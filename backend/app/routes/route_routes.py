from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime
import asyncio
import math

from app.database import journeys_collection, incidents_collection
from app.dependencies import get_current_user
from app.services.routing_service import get_routes
from app.services.osm_service import nearby_police, street_light_status
from app.services.safety_engine import safety_engine


router = APIRouter(prefix="/api")


# ============================================================
# PYDANTIC MODELS
# ============================================================

class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class RouteRequest(BaseModel):
    source: Location
    destination: Location


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def haversine_distance(
    lat1: float,
    lng1: float,
    lat2: float,
    lng2: float
) -> float:
    """
    Calculate straight-line distance between two coordinates.

    Used only for checking whether reported incidents are
    close to a route checkpoint.

    Route distance itself comes from OSRM.
    """

    R = 6371.0

    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)

    a = (
        math.sin(d_lat / 2) ** 2
        +
        math.cos(math.radians(lat1))
        *
        math.cos(math.radians(lat2))
        *
        math.sin(d_lng / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# ============================================================
# ROUTE CHECKPOINTS
# ============================================================

def get_route_checkpoints(
    geometry: list,
    max_checkpoints: int = 3
) -> list:
    """
    Select evenly distributed checkpoints from route geometry.

    The route geometry is expected to contain dictionaries:

        {
            "lat": ...,
            "lng": ...
        }

    We use a small number of checkpoints so that external
    OSM requests remain manageable.
    """

    if not geometry:
        return []

    if len(geometry) <= max_checkpoints:
        return geometry

    checkpoints = []

    for i in range(max_checkpoints):

        index = round(
            i * (len(geometry) - 1)
            / (max_checkpoints - 1)
        )

        checkpoints.append(
            geometry[index]
        )

    return checkpoints


# ============================================================
# INCIDENT COUNT
# ============================================================

async def get_incident_count(
    lat: float,
    lng: float,
    radius_km: float = 1.0
) -> int:
    """
    Count active user-reported incidents within the
    specified radius of a checkpoint.

    This uses MongoDB incident data.

    It does NOT use fake/demo values.
    """

    incidents = incidents_collection.find({
        "status": "active"
    })

    count = 0

    async for incident in incidents:

        incident_lat = incident.get("lat")
        incident_lng = incident.get("lng")

        if incident_lat is None or incident_lng is None:
            continue

        distance = haversine_distance(
            lat,
            lng,
            incident_lat,
            incident_lng
        )

        if distance <= radius_km:
            count += 1

    return count


# ============================================================
# CHECKPOINT ANALYSIS
# ============================================================

async def analyze_checkpoint(point: dict):
    """
    Analyze one route checkpoint.

    Safety indicators:

    1. User-reported incidents
    2. Nearby police station from OSM
    3. Street-lighting information from OSM
    4. Time of day handled by safety_engine

    OSM is optional.

    If OSM is unavailable, we pass None to the safety engine
    instead of inventing a value.
    """

    lat = point["lat"]
    lng = point["lng"]

    # --------------------------------------------------------
    # MongoDB incident analysis
    # --------------------------------------------------------

    incident_count = await get_incident_count(
        lat,
        lng,
        radius_km=1.0
    )

    # --------------------------------------------------------
    # Run OSM requests concurrently
    # --------------------------------------------------------

    police_task = asyncio.to_thread(
        nearby_police,
        lat,
        lng
    )

    lighting_task = asyncio.to_thread(
        street_light_status,
        lat,
        lng
    )

    try:

        police_data, lighting = await asyncio.wait_for(
            asyncio.gather(
                police_task,
                lighting_task
            ),
            timeout=7
        )

    except asyncio.TimeoutError:

        police_data = {
            "available": False,
            "source": "openstreetmap",
            "error": "OSM request timed out",
            "stations": [],
            "nearest": None
        }

        lighting = {
            "available": False,
            "source": "openstreetmap",
            "error": "OSM request timed out",
            "lit_roads": 0,
            "unlit_roads": 0,
            "unknown_roads": 0,
            "lighting_score": None
        }

    except Exception as e:

        print(
            "Checkpoint OSM analysis error:",
            e
        )

        police_data = {
            "available": False,
            "source": "openstreetmap",
            "error": "Police data unavailable",
            "stations": [],
            "nearest": None
        }

        lighting = {
            "available": False,
            "source": "openstreetmap",
            "error": "Lighting data unavailable",
            "lit_roads": 0,
            "unlit_roads": 0,
            "unknown_roads": 0,
            "lighting_score": None
        }

    # --------------------------------------------------------
    # Police information
    # --------------------------------------------------------

    nearest_police = police_data.get("nearest")

    police_distance = None
    police_name = None

    if nearest_police is not None:

        police_distance = nearest_police.get(
            "distance_km"
        )

        police_name = nearest_police.get(
            "name"
        )

    # --------------------------------------------------------
    # Lighting information
    # --------------------------------------------------------

    lighting_score = lighting.get(
        "lighting_score"
    )

    # --------------------------------------------------------
    # Safety engine
    # --------------------------------------------------------

    safety = safety_engine.calculate(
        incident_count=incident_count,
        police_distance_km=police_distance,
        lighting_score=lighting_score
    )

    # --------------------------------------------------------
    # Return checkpoint result
    # --------------------------------------------------------

    return {
        "lat": lat,
        "lng": lng,

        "incident_count": incident_count,

        "police_station": police_name,
        "police_distance_km": police_distance,

        "police_data_available": police_data.get(
            "available",
            False
        ),

        "police_data": police_data,

        "lighting": lighting,

        "safety_score": safety.get(
            "safety_score",
            0
        ),

        "risk_level": safety.get(
            "risk_level",
            "UNKNOWN"
        ),

        "reasons": safety.get(
            "reasons",
            []
        ),

        "indicators_used": safety.get(
            "indicators_used",
            []
        ),

        "indicators_unavailable": safety.get(
            "indicators_unavailable",
            []
        ),

        "data_coverage": safety.get(
            "data_coverage",
            0
        ),

        "confidence": safety.get(
            "confidence",
            "LOW"
        ),

        "data_message": safety.get(
            "data_message",
            ""
        )
    }


# ============================================================
# AGGREGATE CHECKPOINT RESULTS
# ============================================================

def aggregate_checkpoint_results(
    checkpoint_results: list
) -> dict:
    """
    Convert multiple checkpoint results into one route-level
    safety result.
    """

    if not checkpoint_results:

        return {
            "safety_score": 0,
            "risk_level": "UNKNOWN",
            "incident_count": 0,
            "police_station": None,
            "police_distance_km": None,
            "average_lighting_score": None,
            "reasons": [
                "No checkpoint safety data available"
            ],
            "indicators_used": [],
            "indicators_unavailable": [],
            "data_coverage": 0,
            "confidence": "LOW",
            "data_message": "Insufficient safety data",
            "checkpoints": []
        }

    # --------------------------------------------------------
    # Safety scores
    # --------------------------------------------------------

    scores = [
        result.get("safety_score", 0)
        for result in checkpoint_results
    ]

    average_score = sum(scores) / len(scores)

    # --------------------------------------------------------
    # Penalize route if one checkpoint is substantially worse
    # --------------------------------------------------------

    lowest_score = min(scores)

    if lowest_score < 50:
        average_score -= 10

    elif lowest_score < 60:
        average_score -= 5

    average_score = max(
        0,
        min(
            round(average_score),
            100
        )
    )

    # --------------------------------------------------------
    # Route risk level
    # --------------------------------------------------------

    if average_score >= 80:

        risk_level = "LOWER_RISK"

    elif average_score >= 60:

        risk_level = "MODERATE_RISK"

    else:

        risk_level = "HIGHER_RISK"

    # --------------------------------------------------------
    # Total incidents
    # --------------------------------------------------------

    incident_count = sum(
        result.get("incident_count", 0)
        for result in checkpoint_results
    )

    # --------------------------------------------------------
    # Find nearest police station along the route
    # --------------------------------------------------------

    police_results = [
        result
        for result in checkpoint_results
        if result.get("police_distance_km") is not None
    ]

    nearest_route_police = None

    if police_results:

        nearest_route_police = min(
            police_results,
            key=lambda result: result.get(
                "police_distance_km",
                float("inf")
            )
        )

    police_station = None
    police_distance = None

    if nearest_route_police:

        police_station = nearest_route_police.get(
            "police_station"
        )

        police_distance = nearest_route_police.get(
            "police_distance_km"
        )

    # --------------------------------------------------------
    # Average lighting score
    # --------------------------------------------------------

    lighting_scores = [
        result["lighting"].get("lighting_score")
        for result in checkpoint_results
        if result.get("lighting", {}).get(
            "lighting_score"
        ) is not None
    ]

    if lighting_scores:

        average_lighting_score = round(
            sum(lighting_scores) / len(lighting_scores),
            1
        )

    else:

        average_lighting_score = None

    # --------------------------------------------------------
    # Collect reasons
    # --------------------------------------------------------

    reasons = []

    for result in checkpoint_results:

        for reason in result.get(
            "reasons",
            []
        ):

            if reason not in reasons:
                reasons.append(reason)

    # --------------------------------------------------------
    # Indicators used
    # --------------------------------------------------------

    indicators_used = []

    for result in checkpoint_results:

        for indicator in result.get(
            "indicators_used",
            []
        ):

            if indicator not in indicators_used:
                indicators_used.append(indicator)

    # --------------------------------------------------------
    # Indicators unavailable
    # --------------------------------------------------------

    indicators_unavailable = []

    for result in checkpoint_results:

        for indicator in result.get(
            "indicators_unavailable",
            []
        ):

            if indicator not in indicators_unavailable:
                indicators_unavailable.append(indicator)

    # --------------------------------------------------------
    # Average data coverage
    # --------------------------------------------------------

    coverage_values = [
        result.get("data_coverage", 0)
        for result in checkpoint_results
    ]

    data_coverage = round(
        sum(coverage_values)
        / len(coverage_values)
    )

    # --------------------------------------------------------
    # Route confidence
    # --------------------------------------------------------

    if data_coverage >= 75:

        confidence = "HIGH"

    elif data_coverage >= 50:

        confidence = "MEDIUM"

    else:

        confidence = "LOW"

    # --------------------------------------------------------
    # Data message
    # --------------------------------------------------------

    if indicators_unavailable:

        data_message = (
            "Route recommendation is based on available "
            "safety indicators. Some data was unavailable: "
            + ", ".join(indicators_unavailable)
        )

    else:

        data_message = (
            "Route recommendation is based on the available "
            "safety indicators."
        )

    return {
        "safety_score": average_score,

        "risk_level": risk_level,

        "incident_count": incident_count,

        "police_station": police_station,

        "police_distance_km": police_distance,

        "average_lighting_score": average_lighting_score,

        "reasons": reasons,

        "indicators_used": indicators_used,

        "indicators_unavailable": indicators_unavailable,

        "data_coverage": data_coverage,

        "confidence": confidence,

        "data_message": data_message,

        "checkpoints": checkpoint_results
    }


# ============================================================
# ROUTE ANALYSIS
# ============================================================

@router.post("/route/analyze")
async def analyze_route(
    request: RouteRequest,
    current_user=Depends(get_current_user)
):
    """
    Calculate routes between source and destination and
    analyze their safety.

    OSRM provides route distance, duration and geometry.

    Safety is calculated from available indicators.
    """

    # --------------------------------------------------------
    # Validate source/destination
    # --------------------------------------------------------

    source = request.source
    destination = request.destination

    if (
        source.lat == destination.lat
        and source.lng == destination.lng
    ):

        raise HTTPException(
            status_code=400,
            detail="Source and destination cannot be identical"
        )

    # --------------------------------------------------------
    # Get routes from OSRM
    # --------------------------------------------------------

    try:

        routes = await asyncio.to_thread(
            get_routes,
            source.lat,
            source.lng,
            destination.lat,
            destination.lng
        )

    except Exception as e:

        print(
            "Routing service error:",
            e
        )

        raise HTTPException(
            status_code=502,
            detail="Unable to calculate route"
        )

    if not routes:

        raise HTTPException(
            status_code=404,
            detail="No routes found between the selected locations"
        )

    # --------------------------------------------------------
    # Analyze every route
    # --------------------------------------------------------

    analyzed_routes = []

    for route_index, route in enumerate(routes):

        geometry = route.get(
            "geometry",
            []
        )

        if not geometry:

            continue

        # ----------------------------------------------------
        # Use only 3 checkpoints
        # ----------------------------------------------------

        checkpoints = get_route_checkpoints(
            geometry,
            max_checkpoints=3
        )

        # ----------------------------------------------------
        # Analyze ALL checkpoints concurrently
        # ----------------------------------------------------

        checkpoint_tasks = [
            analyze_checkpoint(point)
            for point in checkpoints
        ]

        checkpoint_results = await asyncio.gather(
    *[
        analyze_checkpoint(point)
        for point in checkpoints
    ]
)

        # ----------------------------------------------------
        # Aggregate checkpoint safety
        # ----------------------------------------------------

        route_safety = aggregate_checkpoint_results(
            checkpoint_results
        )

        # ----------------------------------------------------
        # Build route response
        # ----------------------------------------------------

        analyzed_routes.append({
            "route_id": route_index,

            "distance_km": route.get(
                "distance_km"
            ),

            "duration_minutes": route.get(
                "duration_minutes"
            ),

            "geometry": geometry,

            "steps": route.get(
                "steps",
                []
            ),

            "safety_score": route_safety.get(
                "safety_score",
                0
            ),

            "risk_level": route_safety.get(
                "risk_level",
                "UNKNOWN"
            ),

            "reasons": route_safety.get(
                "reasons",
                []
            ),

            "features": {
                "incident_count": route_safety.get(
                    "incident_count",
                    0
                ),

                "police_station": route_safety.get(
                    "police_station"
                ),

                "police_distance_km": route_safety.get(
                    "police_distance_km"
                ),

                "average_lighting_score": route_safety.get(
                    "average_lighting_score"
                ),

                "data_coverage": route_safety.get(
                    "data_coverage",
                    0
                ),

                "confidence": route_safety.get(
                    "confidence",
                    "LOW"
                ),

                "indicators_used": route_safety.get(
                    "indicators_used",
                    []
                ),

                "indicators_unavailable": route_safety.get(
                    "indicators_unavailable",
                    []
                ),

                "data_message": route_safety.get(
                    "data_message",
                    ""
                ),

                "checkpoints": route_safety.get(
                    "checkpoints",
                    []
                )
            }
        })

    if not analyzed_routes:

        raise HTTPException(
            status_code=404,
            detail="Routes were found but contained no usable geometry"
        )

    # ========================================================
    # RECOMMENDED ROUTE
    # ========================================================

    recommended_route = max(
        analyzed_routes,
        key=lambda route: (
            route.get(
                "safety_score",
                0
            ),

            route.get(
                "features",
                {}
            ).get(
                "data_coverage",
                0
            )
        )
    )

    # --------------------------------------------------------
    # Mark recommended route
    # --------------------------------------------------------

    for route in analyzed_routes:

        route["is_recommended"] = (
            route["route_id"]
            == recommended_route["route_id"]
        )

    # ========================================================
    # SAVE JOURNEY HISTORY
    # ========================================================

    journey_document = {
        "user_id": str(
            current_user["_id"]
        ),

        "user_email": current_user.get(
            "email"
        ),

        "source": {
            "lat": source.lat,
            "lng": source.lng
        },

        "destination": {
            "lat": destination.lat,
            "lng": destination.lng
        },

        "routes": analyzed_routes,

        "recommended_route_id": recommended_route[
            "route_id"
        ],

        "created_at": datetime.utcnow(),

        "favorite": False
    }

    try:

        insert_result = await journeys_collection.insert_one(
            journey_document
        )

        journey_id = str(
            insert_result.inserted_id
        )

    except Exception as e:

        print(
            "Journey history save error:",
            e
        )

        journey_id = None

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "success": True,

        "journey_id": journey_id,

        "source": {
            "lat": source.lat,
            "lng": source.lng
        },

        "destination": {
            "lat": destination.lat,
            "lng": destination.lng
        },

        "recommended_route": recommended_route,

        "routes": analyzed_routes,

        "message": (
            "Route analysis completed. "
            "The recommendation is based on "
            "available safety indicators."
        )
    }


# ============================================================
# JOURNEY HISTORY
# ============================================================

@router.get("/history")
async def get_history(
    current_user=Depends(get_current_user)
):
    """
    Return journey history belonging only to the
    currently authenticated user.
    """

    user_id = str(
        current_user["_id"]
    )

    cursor = journeys_collection.find(
        {
            "user_id": user_id
        }
    ).sort(
        "created_at",
        -1
    )

    journeys = []

    async for journey in cursor:

        journey["_id"] = str(
            journey["_id"]
        )

        journeys.append(journey)

    return {
        "success": True,
        "journeys": journeys
    }


# ============================================================
# HISTORY STATS
# ============================================================

@router.get("/history/stats")
async def history_stats(
    current_user=Depends(get_current_user)
):
    """
    Basic statistics for the current user's journeys.
    """

    user_id = str(
        current_user["_id"]
    )

    journeys = []

    cursor = journeys_collection.find({
        "user_id": user_id
    })

    async for journey in cursor:
        journeys.append(journey)

    total_journeys = len(journeys)

    if total_journeys == 0:

        return {
            "success": True,
            "total_journeys": 0,
            "average_safety_score": 0,
            "favorite_count": 0
        }

    scores = []

    favorite_count = 0

    for journey in journeys:

        recommended_id = journey.get(
            "recommended_route_id"
        )

        for route in journey.get(
            "routes",
            []
        ):

            if route.get("route_id") == recommended_id:

                score = route.get(
                    "safety_score"
                )

                if score is not None:
                    scores.append(score)

                break

        if journey.get(
            "favorite",
            False
        ):
            favorite_count += 1

    average_safety_score = (
        round(
            sum(scores) / len(scores),
            2
        )
        if scores
        else 0
    )

    return {
        "success": True,
        "total_journeys": total_journeys,
        "average_safety_score": average_safety_score,
        "favorite_count": favorite_count
    }


# ============================================================
# LATEST JOURNEY
# ============================================================

@router.get("/history/latest")
async def latest_history(
    current_user=Depends(get_current_user)
):
    """
    Return the most recent journey for the current user.
    """

    user_id = str(
        current_user["_id"]
    )

    journey = await journeys_collection.find_one(
        {
            "user_id": user_id
        },
        sort=[
            ("created_at", -1)
        ]
    )

    if journey is None:

        return {
            "success": True,
            "journey": None
        }

    journey["_id"] = str(
        journey["_id"]
    )

    return {
        "success": True,
        "journey": journey
    }


# ============================================================
# FAVORITE JOURNEYS
# ============================================================

@router.get("/history/favorites")
async def favorite_history(
    current_user=Depends(get_current_user)
):
    """
    Return favorite journeys for current user.
    """

    user_id = str(
        current_user["_id"]
    )

    cursor = journeys_collection.find({
        "user_id": user_id,
        "favorite": True
    }).sort(
        "created_at",
        -1
    )

    journeys = []

    async for journey in cursor:

        journey["_id"] = str(
            journey["_id"]
        )

        journeys.append(journey)

    return {
        "success": True,
        "journeys": journeys
    }


# ============================================================
# SEARCH HISTORY
# ============================================================

@router.get("/history/search/{keyword}")
async def search_history(
    keyword: str,
    current_user=Depends(get_current_user)
):
    """
    Search current user's journey history.

    Searches coordinate values converted to strings,
    because source/destination names are not necessarily
    stored by the current backend.
    """

    user_id = str(
        current_user["_id"]
    )

    cursor = journeys_collection.find({
        "user_id": user_id
    }).sort(
        "created_at",
        -1
    )

    journeys = []

    keyword_lower = keyword.lower()

    async for journey in cursor:

        source = journey.get(
            "source",
            {}
        )

        destination = journey.get(
            "destination",
            {}
        )

        searchable_text = (
            f"{source.get('lat', '')} "
            f"{source.get('lng', '')} "
            f"{destination.get('lat', '')} "
            f"{destination.get('lng', '')}"
        ).lower()

        if keyword_lower in searchable_text:

            journey["_id"] = str(
                journey["_id"]
            )

            journeys.append(journey)

    return {
        "success": True,
        "journeys": journeys
    }


# ============================================================
# GET SINGLE JOURNEY
# ============================================================

@router.get("/history/{journey_id}")
async def get_single_history(
    journey_id: str,
    current_user=Depends(get_current_user)
):
    """
    Get one journey only if it belongs to the current user.
    """

    if not ObjectId.is_valid(journey_id):

        raise HTTPException(
            status_code=400,
            detail="Invalid journey ID"
        )

    user_id = str(
        current_user["_id"]
    )

    journey = await journeys_collection.find_one({
        "_id": ObjectId(journey_id),
        "user_id": user_id
    })

    if journey is None:

        raise HTTPException(
            status_code=404,
            detail="Journey not found"
        )

    journey["_id"] = str(
        journey["_id"]
    )

    return {
        "success": True,
        "journey": journey
    }


# ============================================================
# DELETE JOURNEY
# ============================================================

@router.delete("/history/{journey_id}")
async def delete_history(
    journey_id: str,
    current_user=Depends(get_current_user)
):
    """
    Delete a journey only if it belongs to the current user.
    """

    if not ObjectId.is_valid(journey_id):

        raise HTTPException(
            status_code=400,
            detail="Invalid journey ID"
        )

    user_id = str(
        current_user["_id"]
    )

    result = await journeys_collection.delete_one({
        "_id": ObjectId(journey_id),
        "user_id": user_id
    })

    if result.deleted_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Journey not found"
        )

    return {
        "success": True,
        "message": "Journey deleted successfully"
    }


# ============================================================
# FAVORITE / UNFAVORITE JOURNEY
# ============================================================

@router.put("/history/{journey_id}/favorite")
async def toggle_favorite(
    journey_id: str,
    current_user=Depends(get_current_user)
):
    """
    Toggle favorite status of a user's journey.
    """

    if not ObjectId.is_valid(journey_id):

        raise HTTPException(
            status_code=400,
            detail="Invalid journey ID"
        )

    user_id = str(
        current_user["_id"]
    )

    journey = await journeys_collection.find_one({
        "_id": ObjectId(journey_id),
        "user_id": user_id
    })

    if journey is None:

        raise HTTPException(
            status_code=404,
            detail="Journey not found"
        )

    new_favorite_status = not journey.get(
        "favorite",
        False
    )

    await journeys_collection.update_one(
        {
            "_id": ObjectId(journey_id),
            "user_id": user_id
        },
        {
            "$set": {
                "favorite": new_favorite_status
            }
        }
    )

    return {
        "success": True,
        "favorite": new_favorite_status
    }


# ============================================================
# MONTHLY ANALYTICS
# ============================================================

@router.get("/history/analytics/monthly")
async def monthly_analytics(
    current_user=Depends(get_current_user)
):
    """
    Return journey counts grouped by month.
    """

    user_id = str(
        current_user["_id"]
    )

    cursor = journeys_collection.find({
        "user_id": user_id
    })

    monthly = {}

    async for journey in cursor:

        created_at = journey.get(
            "created_at"
        )

        if not created_at:
            continue

        month_key = created_at.strftime(
            "%Y-%m"
        )

        monthly[month_key] = (
            monthly.get(month_key, 0)
            + 1
        )

    return {
        "success": True,
        "monthly": monthly
    }


# ============================================================
# ROUTE USAGE ANALYTICS
# ============================================================

@router.get("/history/analytics/routes")
async def route_usage(
    current_user=Depends(get_current_user)
):
    """
    Return basic route usage statistics.
    """

    user_id = str(
        current_user["_id"]
    )

    cursor = journeys_collection.find({
        "user_id": user_id
    })

    total_routes = 0

    recommended_routes = 0

    async for journey in cursor:

        routes = journey.get(
            "routes",
            []
        )

        total_routes += len(routes)

        if journey.get(
            "recommended_route_id"
        ) is not None:

            recommended_routes += 1

    return {
        "success": True,
        "total_routes_analyzed": total_routes,
        "recommended_routes": recommended_routes
    }


# ============================================================
# SAFETY TREND
# ============================================================

@router.get("/history/analytics/safety-trend")
async def safety_trend(
    current_user=Depends(get_current_user)
):
    """
    Return safety scores of recommended routes over time.
    """

    user_id = str(
        current_user["_id"]
    )

    cursor = journeys_collection.find({
        "user_id": user_id
    }).sort(
        "created_at",
        1
    )

    trend = []

    async for journey in cursor:

        recommended_id = journey.get(
            "recommended_route_id"
        )

        for route in journey.get(
            "routes",
            []
        ):

            if route.get(
                "route_id"
            ) == recommended_id:

                trend.append({
                    "date": (
                        journey.get(
                            "created_at"
                        ).isoformat()
                        if journey.get(
                            "created_at"
                        )
                        else None
                    ),

                    "safety_score": route.get(
                        "safety_score"
                    ),

                    "risk_level": route.get(
                        "risk_level"
                    )
                })

                break

    return {
        "success": True,
        "trend": trend
    }


# ============================================================
# ROUTE HEALTH CHECK
# ============================================================

@router.get("/history/health")
async def history_health():
    """
    Basic health endpoint for the route/history service.
    """

    try:

        await journeys_collection.find_one(
            {},
            {
                "_id": 1
            }
        )

        return {
            "success": True,
            "status": "healthy"
        }

    except Exception as e:

        print(
            "History health check error:",
            e
        )

        return {
            "success": False,
            "status": "unhealthy"
        }