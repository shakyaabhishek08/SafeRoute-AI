from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import math

from app.auth import decode_access_token

from app.database import (
    journeys_collection,
    incidents_collection,
    users_collection
)

from app.services.routing_service import get_routes

from app.services.osm_service import (
    nearby_police,
    street_light_status
)

from app.services.safety_engine import (
    safety_engine
)


router = APIRouter(
    prefix="/api",
    tags=["Routes"]
)


# ==========================================================
# AUTHENTICATION
# ==========================================================

async def get_current_user(
    authorization: Optional[str] = Header(None)
):

    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header"
        )

    token = authorization.split(" ")[1]

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    email = payload.get("email")

    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    user = await users_collection.find_one(
        {
            "email": email
        }
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# ==========================================================
# REQUEST MODELS
# ==========================================================

class Location(BaseModel):
    lat: float
    lng: float


class RouteRequest(BaseModel):
    source: Location
    destination: Location
# ==========================================================
# DISTANCE CALCULATOR
# ==========================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371

    d_lat = math.radians(
        lat2 - lat1
    )

    d_lon = math.radians(
        lon2 - lon1
    )

    a = (

        math.sin(d_lat / 2) ** 2

        +

        math.cos(
            math.radians(lat1)
        )

        *

        math.cos(
            math.radians(lat2)
        )

        *

        math.sin(
            d_lon / 2
        ) ** 2

    )

    c = 2 * math.atan2(

        math.sqrt(a),

        math.sqrt(1 - a)

    )

    return R * c


# ==========================================================
# INCIDENT COUNTER
# ==========================================================

async def get_incident_count(

    lat,
    lng,
    radius_km=1

):

    count = 0

    cursor = incidents_collection.find(

        {
            "status": "active"
        }

    )

    async for incident in cursor:

        location = incident.get(
            "location",
            {}
        )

        incident_lat = location.get("lat")
        incident_lng = location.get("lng")

        if incident_lat is None:
            continue

        if incident_lng is None:
            continue

        distance = calculate_distance(

            lat,

            lng,

            incident_lat,

            incident_lng

        )

        if distance <= radius_km:

            count += 1

    return count
# ==========================================================
# ROUTE ANALYSIS
# ==========================================================

@router.post("/route/analyze")
async def analyze_route(
    request: RouteRequest,
    current_user=Depends(get_current_user)
):

    # ------------------------------------------------------
    # Source & Destination
    # ------------------------------------------------------

    source = {
        "lat": request.source.lat,
        "lng": request.source.lng
    }

    destination = {
        "lat": request.destination.lat,
        "lng": request.destination.lng
    }

    # ------------------------------------------------------
    # Fetch Routes
    # ------------------------------------------------------

    routes = get_routes(
        source,
        destination
    )

    if not routes:

        raise HTTPException(
            status_code=404,
            detail="No routes found."
        )

    analyzed_routes = []

    # ------------------------------------------------------
    # Analyze Each Route
    # ------------------------------------------------------

    for route in routes:

        geometry = route.get("geometry", [])

        if len(geometry) == 0:
            continue

        midpoint = geometry[
            len(geometry) // 2
        ]

        mid_lat = midpoint["lat"]
        mid_lng = midpoint["lng"]

        # ------------------------------------------
        # Nearby Incidents
        # ------------------------------------------

        incident_count = await get_incident_count(
            mid_lat,
            mid_lng
        )

        # ------------------------------------------
        # Police Stations
        # ------------------------------------------

        police = nearby_police(
            mid_lat,
            mid_lng
        )

        if police:

            nearest_police = police[0]

            police_distance = nearest_police.get(
                "distance_km",
                5
            )

        else:

            police_distance = 5

        # ------------------------------------------
        # Street Lighting
        # ------------------------------------------

        lighting = street_light_status(
            mid_lat,
            mid_lng
        )

        lighting_score = lighting.get(
            "lighting_score",
            5
        )

        # ------------------------------------------
        # AI Safety Score
        # ------------------------------------------

        safety = safety_engine.calculate(

            incident_count=incident_count,

            police_distance_km=police_distance,

            lighting_score=lighting_score

        )

        analyzed_routes.append(

            {

                "route_type": route["route_type"],

                "distance_km": route["distance_km"],

                "time_min": route["time_min"],

                "geometry": geometry,

                "safety_score": safety["safety_score"],

                "risk_level": safety["risk_level"],

                "reasons": safety["reasons"],

                "features": {

                    "incident_count": incident_count,

                    "nearest_police_distance_km": police_distance,

                    "lighting_score": lighting_score,

                    "lit_roads": lighting.get(
                        "lit_roads",
                        0
                    ),

                    "unlit_roads": lighting.get(
                        "unlit_roads",
                        0
                    ),

                    "unknown": lighting.get(
                        "unknown",
                        0
                    )

                }

            }

        )

    # ------------------------------------------------------
    # No Route Analysed
    # ------------------------------------------------------

    if len(analyzed_routes) == 0:

        raise HTTPException(

            status_code=404,

            detail="Unable to analyze routes."

        )
    # ------------------------------------------------------
    # Select Best Route
    # ------------------------------------------------------

    best_route = max(
        analyzed_routes,
        key=lambda route: route["safety_score"]
    )

    # ------------------------------------------------------
    # Save Journey
    # ------------------------------------------------------

    journey = {

        # Owner Information

        "user_id": str(current_user["_id"]),

        "user_name": current_user["name"],

        "user_email": current_user["email"],

        # Journey Details

        "source": source,

        "destination": destination,

        "routes": analyzed_routes,

        "recommended_route": best_route["route_type"],

        "best_safety_score": best_route["safety_score"],

        "distance_km": best_route["distance_km"],

        "time_min": best_route["time_min"],

        "created_at": datetime.now(timezone.utc)

    }

    result = await journeys_collection.insert_one(
        journey
    )

    # ------------------------------------------------------
    # Response
    # ------------------------------------------------------

    return {

        "success": True,

        "message": "Route analyzed successfully",

        "journey_id": str(result.inserted_id),

        "recommended": {

            "route_type": best_route["route_type"],

            "distance_km": best_route["distance_km"],

            "time_min": best_route["time_min"],

            "safety_score": best_route["safety_score"],

            "risk_level": best_route["risk_level"],

            "reasons": best_route["reasons"],

            "features": best_route["features"],

            "geometry": best_route["geometry"]

        },

        "routes": analyzed_routes

    }
# ==========================================================
# GET ALL JOURNEY HISTORY
# ==========================================================

@router.get("/history")
async def get_history(

    current_user=Depends(get_current_user)

):

    history = []

    cursor = journeys_collection.find(

        {

            "user_id": str(current_user["_id"])

        }

    ).sort(

        "created_at",

        -1

    )

    async for journey in cursor:

        journey["_id"] = str(journey["_id"])

        history.append(journey)

    return {

        "success": True,

        "count": len(history),

        "history": history

    }


# ==========================================================
# GET SINGLE JOURNEY
# ==========================================================

@router.get("/history/{journey_id}")
async def get_single_history(

    journey_id: str,

    current_user=Depends(get_current_user)

):

    from bson import ObjectId

    try:

        journey = await journeys_collection.find_one(

            {

                "_id": ObjectId(journey_id),

                "user_id": str(current_user["_id"])

            }

        )

    except Exception:

        raise HTTPException(

            status_code=400,

            detail="Invalid Journey ID"

        )

    if journey is None:

        raise HTTPException(

            status_code=404,

            detail="Journey not found"

        )

    journey["_id"] = str(journey["_id"])

    return {

        "success": True,

        "journey": journey

    }


# ==========================================================
# DELETE JOURNEY
# ==========================================================

@router.delete("/history/{journey_id}")
async def delete_journey(

    journey_id: str,

    current_user=Depends(get_current_user)

):

    from bson import ObjectId

    try:

        result = await journeys_collection.delete_one(

            {

                "_id": ObjectId(journey_id),

                "user_id": str(current_user["_id"])

            }

        )

    except Exception:

        raise HTTPException(

            status_code=400,

            detail="Invalid Journey ID"

        )

    if result.deleted_count == 0:

        raise HTTPException(

            status_code=404,

            detail="Journey not found"

        )

    return {

        "success": True,

        "message": "Journey deleted successfully"

    }
# ==========================================================
# JOURNEY STATISTICS
# ==========================================================

@router.get("/history/stats")
async def get_journey_statistics(

    current_user=Depends(get_current_user)

):

    cursor = journeys_collection.find(
        {
            "user_id": str(current_user["_id"])
        }
    )

    total = 0
    safest_score = 0
    safest_route = None
    total_distance = 0
    total_time = 0

    async for journey in cursor:

        total += 1

        score = journey.get(
            "best_safety_score",
            0
        )

        if score > safest_score:

            safest_score = score
            safest_route = journey.get(
                "recommended_route"
            )

        total_distance += journey.get(
            "distance_km",
            0
        )

        total_time += journey.get(
            "time_min",
            0
        )

    return {

        "success": True,

        "statistics": {

            "total_journeys": total,

            "total_distance_km": round(
                total_distance,
                2
            ),

            "total_time_min": round(
                total_time,
                2
            ),

            "average_distance": round(
                total_distance / total,
                2
            ) if total else 0,

            "average_time": round(
                total_time / total,
                2
            ) if total else 0,

            "highest_safety_score": safest_score,

            "best_route": safest_route

        }

    }


# ==========================================================
# LATEST JOURNEY
# ==========================================================

@router.get("/history/latest")
async def latest_journey(

    current_user=Depends(get_current_user)

):

    journey = await journeys_collection.find_one(

        {

            "user_id": str(current_user["_id"])

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

    journey["_id"] = str(journey["_id"])

    return {

        "success": True,

        "journey": journey

    }
# ==========================================================
# ADD / REMOVE FAVORITE ROUTE
# ==========================================================

from bson import ObjectId


@router.put("/history/{journey_id}/favorite")
async def toggle_favorite(

    journey_id: str,

    current_user=Depends(get_current_user)

):

    try:

        journey = await journeys_collection.find_one(

            {

                "_id": ObjectId(journey_id),

                "user_id": str(current_user["_id"])

            }

        )

    except Exception:

        raise HTTPException(

            status_code=400,

            detail="Invalid Journey ID"

        )

    if journey is None:

        raise HTTPException(

            status_code=404,

            detail="Journey not found"

        )

    current_status = journey.get(
        "favorite",
        False
    )

    new_status = not current_status

    await journeys_collection.update_one(

        {

            "_id": ObjectId(journey_id)

        },

        {

            "$set": {

                "favorite": new_status

            }

        }

    )

    return {

        "success": True,

        "favorite": new_status,

        "message": (

            "Journey added to favorites"

            if new_status

            else

            "Journey removed from favorites"

        )

    }


# ==========================================================
# GET FAVORITE ROUTES
# ==========================================================

@router.get("/history/favorites")
async def get_favorites(

    current_user=Depends(get_current_user)

):

    favorites = []

    cursor = journeys_collection.find(

        {

            "user_id": str(current_user["_id"]),

            "favorite": True

        }

    ).sort(

        "created_at",

        -1

    )

    async for item in cursor:

        item["_id"] = str(item["_id"])

        favorites.append(item)

    return {

        "success": True,

        "count": len(favorites),

        "favorites": favorites

    }


# ==========================================================
# SEARCH JOURNEY HISTORY
# ==========================================================

@router.get("/history/search/{keyword}")
async def search_history(

    keyword: str,

    current_user=Depends(get_current_user)

):

    keyword = keyword.lower()

    results = []

    cursor = journeys_collection.find(

        {

            "user_id": str(current_user["_id"])

        }

    )

    async for item in cursor:

        source = str(item.get("source", "")).lower()

        destination = str(item.get("destination", "")).lower()

        recommended = str(

            item.get(

                "recommended_route",

                ""

            )

        ).lower()

        if (

            keyword in source

            or

            keyword in destination

            or

            keyword in recommended

        ):

            item["_id"] = str(item["_id"])

            results.append(item)

    return {

        "success": True,

        "count": len(results),

        "results": results

    }
# ==========================================================
# MONTHLY JOURNEY ANALYTICS
# ==========================================================

@router.get("/history/analytics/monthly")
async def monthly_analytics(

    current_user=Depends(get_current_user)

):

    analytics = {}

    cursor = journeys_collection.find(

        {

            "user_id": str(current_user["_id"])

        }

    )

    async for journey in cursor:

        created_at = journey.get("created_at")

        if created_at is None:
            continue

        month = created_at.strftime("%Y-%m")

        if month not in analytics:

            analytics[month] = {

                "journeys": 0,

                "distance": 0,

                "time": 0

            }

        analytics[month]["journeys"] += 1

        analytics[month]["distance"] += journey.get(
            "distance_km",
            0
        )

        analytics[month]["time"] += journey.get(
            "time_min",
            0
        )

    return {

        "success": True,

        "analytics": analytics

    }


# ==========================================================
# ROUTE USAGE ANALYTICS
# ==========================================================

@router.get("/history/analytics/routes")
async def route_usage(

    current_user=Depends(get_current_user)

):

    usage = {}

    cursor = journeys_collection.find(

        {

            "user_id": str(current_user["_id"])

        }

    )

    async for journey in cursor:

        route = journey.get(

            "recommended_route",

            "Unknown"

        )

        usage[route] = usage.get(route, 0) + 1

    return {

        "success": True,

        "usage": usage

    }


# ==========================================================
# SAFETY SCORE TREND
# ==========================================================

@router.get("/history/analytics/safety")
async def safety_trend(

    current_user=Depends(get_current_user)

):

    trend = []

    cursor = journeys_collection.find(

        {

            "user_id": str(current_user["_id"])

        }

    ).sort(

        "created_at",

        1

    )

    async for journey in cursor:

        trend.append(

            {

                "date": journey.get("created_at"),

                "score": journey.get(

                    "best_safety_score",

                    0

                )

            }

        )

    return {

        "success": True,

        "trend": trend

    }


# ==========================================================
# HEALTH CHECK
# ==========================================================

@router.get("/route/health")
async def route_health():

    return {

        "success": True,

        "service": "Route Service",

        "status": "Healthy",

        "timestamp": datetime.utcnow()

    }