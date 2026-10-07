import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================
# OSRM CONFIGURATION
# ============================================================

OSRM_URL = "https://router.project-osrm.org/route/v1/driving"


# ============================================================
# HTTP SESSION
# ============================================================

session = requests.Session()

retry = Retry(
    total=2,
    connect=2,
    read=2,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)

adapter = HTTPAdapter(max_retries=retry)

session.mount("http://", adapter)
session.mount("https://", adapter)


HEADERS = {
    "User-Agent": "SafeRouteAI/1.0 (Educational Project)",
    "Accept": "application/json",
}


# ============================================================
# COORDINATE VALIDATION
# ============================================================

def validate_coordinates(
    lat: float,
    lng: float
):
    """
    Validate latitude and longitude.
    """

    if not (-90 <= lat <= 90):
        raise ValueError(
            f"Invalid latitude: {lat}"
        )

    if not (-180 <= lng <= 180):
        raise ValueError(
            f"Invalid longitude: {lng}"
        )


# ============================================================
# GET ROUTES FROM OSRM
# ============================================================

def get_routes(
    source_lat: float,
    source_lng: float,
    destination_lat: float,
    destination_lng: float
):
    """
    Get alternative driving routes from OSRM.

    IMPORTANT:
    OSRM expects coordinates in:

        longitude,latitude

    while the rest of our application uses:

        latitude,longitude
    """

    # --------------------------------------------------------
    # Validate coordinates
    # --------------------------------------------------------

    validate_coordinates(
        source_lat,
        source_lng
    )

    validate_coordinates(
        destination_lat,
        destination_lng
    )

    # --------------------------------------------------------
    # Prevent identical locations
    # --------------------------------------------------------

    if (
        source_lat == destination_lat
        and source_lng == destination_lng
    ):
        raise ValueError(
            "Source and destination cannot be identical"
        )

    # --------------------------------------------------------
    # OSRM coordinate format
    # --------------------------------------------------------

    coordinates = (
        f"{source_lng},{source_lat};"
        f"{destination_lng},{destination_lat}"
    )

    url = f"{OSRM_URL}/{coordinates}"

    params = {
        "alternatives": "true",
        "steps": "true",
        "overview": "full",
        "geometries": "geojson",
    }

    # --------------------------------------------------------
    # Call OSRM
    # --------------------------------------------------------

    try:

        response = session.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

    except requests.exceptions.Timeout as e:

        print(
            "OSRM timeout:",
            e
        )

        raise RuntimeError(
            "OSRM routing service timed out"
        )

    except requests.exceptions.RequestException as e:

        print(
            "OSRM request failed:",
            e
        )

        raise RuntimeError(
            f"OSRM routing service unavailable: {str(e)}"
        )

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        data = response.json()

    except ValueError:

        print(
            "OSRM returned invalid JSON"
        )

        raise RuntimeError(
            "OSRM returned an invalid response"
        )

    # --------------------------------------------------------
    # Check OSRM response
    # --------------------------------------------------------

    if data.get("code") != "Ok":

        message = data.get(
            "message",
            "Unknown OSRM error"
        )

        print(
            "OSRM error:",
            message
        )

        raise RuntimeError(
            f"OSRM could not calculate route: {message}"
        )

    raw_routes = data.get(
        "routes",
        []
    )

    if not raw_routes:

        raise RuntimeError(
            "OSRM returned no routes"
        )

    # ========================================================
    # CLEAN ROUTES
    # ========================================================

    routes = []

    for route_index, route in enumerate(raw_routes):

        # ----------------------------------------------------
        # Geometry
        # ----------------------------------------------------

        geometry = []

        geojson = route.get(
            "geometry",
            {}
        )

        coordinates_list = geojson.get(
            "coordinates",
            []
        )

        for coordinate in coordinates_list:

            if len(coordinate) < 2:
                continue

            # OSRM GeoJSON:
            # [longitude, latitude]

            lng = coordinate[0]
            lat = coordinate[1]

            geometry.append({
                "lat": lat,
                "lng": lng
            })

        # ----------------------------------------------------
        # Skip route without geometry
        # ----------------------------------------------------

        if not geometry:
            continue

        # ----------------------------------------------------
        # Distance
        # ----------------------------------------------------

        distance_meters = route.get(
            "distance",
            0
        )

        distance_km = round(
            distance_meters / 1000,
            2
        )

        # ----------------------------------------------------
        # Duration
        # ----------------------------------------------------

        duration_seconds = route.get(
            "duration",
            0
        )

        duration_minutes = round(
            duration_seconds / 60,
            1
        )

        # ----------------------------------------------------
        # Steps
        # ----------------------------------------------------

        steps = []

        for leg in route.get(
            "legs",
            []
        ):

            for step in leg.get(
                "steps",
                []
            ):

                maneuver = step.get(
                    "maneuver",
                    {}
                )

                location = maneuver.get(
                    "location",
                    []
                )

                step_lng = None
                step_lat = None

                if len(location) >= 2:

                    step_lng = location[0]
                    step_lat = location[1]

                steps.append({
                    "instruction": step.get(
                        "name",
                        "Continue"
                    ),

                    "name": step.get(
                        "name",
                        ""
                    ),

                    "distance_m": round(
                        step.get(
                            "distance",
                            0
                        ),
                        1
                    ),

                    "duration_seconds": round(
                        step.get(
                            "duration",
                            0
                        ),
                        1
                    ),

                    "mode": step.get(
                        "mode",
                        "driving"
                    ),

                    "maneuver": maneuver.get(
                        "type"
                    ),

                    "modifier": maneuver.get(
                        "modifier"
                    ),

                    "lat": step_lat,

                    "lng": step_lng,
                })

        # ----------------------------------------------------
        # Add cleaned route
        # ----------------------------------------------------

        routes.append({
            "route_id": route_index,

            "distance_km": distance_km,

            "duration_minutes": duration_minutes,

            "geometry": geometry,

            "steps": steps,
        })

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    if not routes:

        raise RuntimeError(
            "OSRM returned routes but no usable route geometry"
        )

    return routes