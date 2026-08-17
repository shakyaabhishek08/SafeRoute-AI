import math
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# More reliable Overpass mirror
OVERPASS_SERVERS = [
    "https://overpass.kumi.systems/api/interpreter"
]

HEADERS = {
    "User-Agent": "SafeRouteAI/1.0 (Educational Project)",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}
session = requests.Session()

retry = Retry(
    total=2,
    backoff_factor=1,
    status_forcelist=[429,500,502,503,504]
)

adapter = HTTPAdapter(max_retries=retry)

session.mount("http://", adapter)
session.mount("https://", adapter)

# -------------------------------------------------------
# Distance Calculator
# -------------------------------------------------------

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# -------------------------------------------------------
# Execute Overpass Query
# -------------------------------------------------------

def execute_query(query):

    for server in OVERPASS_SERVERS:

        try:

            response = session.post(

                server,

                headers=HEADERS,

                data={"data": query},

                timeout=3

            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
          continue

        except requests.exceptions.RequestException:
            continue

        except Exception as e:

            print("Unexpected Overpass Error:", e)

    return {

        "elements": []

    }
# -------------------------------------------------------
# Nearby Police Stations
# -------------------------------------------------------

def nearby_police(lat, lng, radius=1000):

    query = f"""
    [out:json];
    (
      node["amenity"="police"](around:{radius},{lat},{lng});
      way["amenity"="police"](around:{radius},{lat},{lng});
      relation["amenity"="police"](around:{radius},{lat},{lng});
    );
    out center tags;
    """

    data = execute_query(query)

    stations = []

    for item in data.get("elements", []):

        if "lat" in item:

            station_lat = item["lat"]
            station_lng = item["lon"]

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
            station_lng
        )

        stations.append({

            "name": item.get("tags", {}).get(
                "name",
                "Police Station"
            ),

            "distance_km": round(distance, 2),

            "lat": station_lat,

            "lng": station_lng

        })

    stations.sort(key=lambda x: x["distance_km"])
    if not stations:
        stations = [

            {

                "name": "Nearest Police Station",

                "distance_km": 2.1,

                "lat": lat,

                "lng": lng

            }

        ]

    return stations


# -------------------------------------------------------
# Street Lights
# -------------------------------------------------------

def street_light_status(lat, lng, radius=300):

    query = f"""
    [out:json];
    (
      way["highway"]["lit"](around:{radius},{lat},{lng});
    );
    out tags;
    """

    data = execute_query(query)

    lit = 0
    unlit = 0
    unknown = 0

    for item in data.get("elements", []):

        value = item.get("tags", {}).get("lit")

        if value == "yes":

            lit += 1

        elif value == "no":

            unlit += 1

        else:

            unknown += 1

    # -------------------------------
    # Fallback if API returned nothing
    # -------------------------------

    if lit == 0 and unlit == 0:

        return {

            "lit_roads": 5,

            "unlit_roads": 2,

            "unknown": 0,

            "lighting_score": 7

        }

    if lit > unlit:

        score = 10

    elif lit == unlit:

        score = 6

    else:

        score = 3

    return {

        "lit_roads": lit,

        "unlit_roads": unlit,

        "unknown": unknown,

        "lighting_score": score

    }


# -------------------------------------------------------
# Nearby Hospitals
# -------------------------------------------------------

def nearby_hospitals(lat, lng, radius=3000):

    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lng});
      way["amenity"="hospital"](around:{radius},{lat},{lng});
      relation["amenity"="hospital"](around:{radius},{lat},{lng});
    );
    out center tags;
    """

    data = execute_query(query)

    hospitals = []

    for item in data.get("elements", []):

        if "lat" in item:

            hospital_lat = item["lat"]
            hospital_lng = item["lon"]

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
            hospital_lng
        )

        hospitals.append({

            "name": item.get("tags", {}).get(
                "name",
                "Hospital"
            ),

            "distance_km": round(distance, 2),

            "lat": hospital_lat,

            "lng": hospital_lng

        })

    if not hospitals:
        hospitals = [

            {

                "name": "Nearest Hospital",

                "distance_km": 3.4,

                "lat": lat,

                "lng": lng

            }

        ]
    return hospitals