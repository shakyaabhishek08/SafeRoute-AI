import math
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================
# OVERPASS SERVERS
# ============================================================

OVERPASS_SERVERS = [
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]


# ============================================================
# HTTP CONFIGURATION
# ============================================================

HEADERS = {
    "User-Agent": "SafeRouteAI/1.0 (Educational Project)",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}


session = requests.Session()

# Do NOT repeatedly retry slow public Overpass servers.
retry = Retry(
    total=0,
    connect=0,
    read=0,
    backoff_factor=0,
    status_forcelist=[],
    allowed_methods=["POST"],
)

adapter = HTTPAdapter(max_retries=retry)

session.mount("http://", adapter)
session.mount("https://", adapter)


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula.

    Returns:
        Distance in kilometers.
    """

    R = 6371.0

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# ============================================================
# OVERPASS QUERY EXECUTION
# ============================================================

def execute_query(query):
    """
    Execute an Overpass API query.

    Tries each configured server once.

    Returns:
        {
            "success": True/False,
            "data": {...} or None,
            "error": "..."/None
        }
    """

    last_error = None

    for server in OVERPASS_SERVERS:
        try:
            response = session.post(
                server,
                headers=HEADERS,
                data={"data": query},
                timeout=3,
            )

            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "data": data,
                "error": None,
            }

        except requests.exceptions.Timeout:
            last_error = f"Overpass server timed out: {server}"
            print("Overpass timeout:", server)
            continue

        except requests.exceptions.RequestException as e:
            last_error = f"Overpass request failed: {server}"
            print("Overpass request failed:", server, e)
            continue

        except ValueError:
            last_error = f"Invalid JSON returned by: {server}"
            print("Overpass returned invalid JSON:", server)
            continue

        except Exception as e:
            last_error = f"Unexpected Overpass error: {server}"
            print("Unexpected Overpass error:", server, e)
            continue

    print("All Overpass servers unavailable.")

    return {
        "success": False,
        "data": None,
        "error": last_error,
    }

# ============================================================
# NEARBY POLICE STATIONS
# ============================================================

def nearby_police(lat, lng, radius=1000):
    """
    Find police stations near a coordinate.

    radius:
        Search radius in meters.

    Returns:
        Dictionary containing available stations and nearest station.
    """

    query = f"""
    [out:json][timeout:5];

    (
        node["amenity"="police"](around:{radius},{lat},{lng});

        way["amenity"="police"](around:{radius},{lat},{lng});

        relation["amenity"="police"](around:{radius},{lat},{lng});
    );

    out center tags;
    """

    result = execute_query(query)

    if not result["success"]:

        return {
            "available": False,
            "source": "openstreetmap",
            "error": result["error"],
            "stations": [],
            "nearest": None,
        }

    data = result["data"]

    stations = []

    for item in data.get("elements", []):

        # ----------------------------------------------------
        # NODE
        # ----------------------------------------------------

        if "lat" in item and "lon" in item:

            station_lat = item["lat"]
            station_lng = item["lon"]

        # ----------------------------------------------------
        # WAY / RELATION
        # ----------------------------------------------------

        else:

            center = item.get("center", {})

            station_lat = center.get("lat")
            station_lng = center.get("lon")

        if station_lat is None or station_lng is None:
            continue

        distance = calculate_distance(
            lat,
            lng,
            station_lat,
            station_lng,
        )

        tags = item.get("tags", {})

        station_name = tags.get(
            "name",
            "Unnamed Police Station"
        )

        stations.append({
            "name": station_name,
            "distance_km": round(distance, 2),
            "lat": station_lat,
            "lng": station_lng,
        })

    # Sort by nearest distance
    stations.sort(
        key=lambda station: station["distance_km"]
    )

    nearest = stations[0] if stations else None

    return {
        "available": True,
        "source": "openstreetmap",
        "error": None,
        "stations": stations,
        "nearest": nearest,
    }


# ============================================================
# STREET LIGHTING
# ============================================================

def street_light_status(lat, lng, radius=300):
    """
    Check mapped street-lighting information around a location.

    Important:
    OpenStreetMap does NOT contain complete street-light
    information everywhere.

    Therefore this function NEVER invents lighting values.
    """

    query = f"""
    [out:json][timeout:5];

    (
        way["highway"]["lit"](around:{radius},{lat},{lng});
    );

    out tags;
    """

    result = execute_query(query)

    if not result["success"]:

        return {
            "available": False,
            "source": "openstreetmap",
            "error": result["error"],
            "lit_roads": 0,
            "unlit_roads": 0,
            "unknown_roads": 0,
            "lighting_score": None,
        }

    data = result["data"]

    lit = 0
    unlit = 0
    unknown = 0

    for item in data.get("elements", []):

        tags = item.get("tags", {})

        value = tags.get("lit")

        if value == "yes":

            lit += 1

        elif value == "no":

            unlit += 1

        else:

            unknown += 1

    # --------------------------------------------------------
    # No mapped lighting information
    # --------------------------------------------------------

    if lit == 0 and unlit == 0:

        return {
            "available": True,
            "source": "openstreetmap",
            "error": None,
            "lit_roads": 0,
            "unlit_roads": 0,
            "unknown_roads": unknown,
            "lighting_score": None,
        }

    # --------------------------------------------------------
    # Calculate score ONLY from actual mapped data
    # --------------------------------------------------------

    total_known = lit + unlit

    lighting_ratio = lit / total_known

    lighting_score = round(
        lighting_ratio * 10
    )

    return {
        "available": True,
        "source": "openstreetmap",
        "error": None,
        "lit_roads": lit,
        "unlit_roads": unlit,
        "unknown_roads": unknown,
        "lighting_score": lighting_score,
    }


# ============================================================
# NEARBY HOSPITALS
# ============================================================

def nearby_hospitals(lat, lng, radius=3000):
    """
    Find hospitals near a coordinate.

    radius:
        Search radius in meters.
    """

    query = f"""
    [out:json][timeout:5];

    (
        node["amenity"="hospital"](around:{radius},{lat},{lng});

        way["amenity"="hospital"](around:{radius},{lat},{lng});

        relation["amenity"="hospital"](around:{radius},{lat},{lng});
    );

    out center tags;
    """

    result = execute_query(query)

    if not result["success"]:

        return {
            "available": False,
            "source": "openstreetmap",
            "error": result["error"],
            "hospitals": [],
            "nearest": None,
        }

    data = result["data"]

    hospitals = []

    for item in data.get("elements", []):

        # ----------------------------------------------------
        # NODE
        # ----------------------------------------------------

        if "lat" in item and "lon" in item:

            hospital_lat = item["lat"]
            hospital_lng = item["lon"]

        # ----------------------------------------------------
        # WAY / RELATION
        # ----------------------------------------------------

        else:

            center = item.get("center", {})

            hospital_lat = center.get("lat")
            hospital_lng = center.get("lon")

        if hospital_lat is None or hospital_lng is None:
            continue

        distance = calculate_distance(
            lat,
            lng,
            hospital_lat,
            hospital_lng,
        )

        tags = item.get("tags", {})

        hospital_name = tags.get(
            "name",
            "Unnamed Hospital"
        )

        hospitals.append({
            "name": hospital_name,
            "distance_km": round(distance, 2),
            "lat": hospital_lat,
            "lng": hospital_lng,
        })

    # Sort nearest first
    hospitals.sort(
        key=lambda hospital: hospital["distance_km"]
    )

    nearest = hospitals[0] if hospitals else None

    return {
        "available": True,
        "source": "openstreetmap",
        "error": None,
        "hospitals": hospitals,
        "nearest": nearest,
    }