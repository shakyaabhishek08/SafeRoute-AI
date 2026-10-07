import os
import math
import requests
from dotenv import load_dotenv

load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

BASE_URL = "https://api.geoapify.com/v2/places"

session = requests.Session()


def calculate_distance_km(lat1, lng1, lat2, lng2):
    """
    Calculate distance between two coordinates using Haversine formula.
    """

    R = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(dlng / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def _nearby_places(lat, lng, category, radius_m=3000, limit=20):
    """
    Generic Geoapify nearby-place search.
    """

    if not GEOAPIFY_API_KEY:
        return {
            "available": False,
            "source": "geoapify",
            "error": "GEOAPIFY_API_KEY not configured",
            "places": [],
            "nearest": None,
        }

    params = {
        "categories": category,
        "filter": f"circle:{lng},{lat},{radius_m}",
        "limit": limit,
        "apiKey": GEOAPIFY_API_KEY,
    }

    try:
        response = session.get(
            BASE_URL,
            params=params,
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()

        features = data.get("features", [])

        places = []

        for feature in features:
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})

            coordinates = geometry.get("coordinates", [])

            if len(coordinates) < 2:
                continue

            place_lng = coordinates[0]
            place_lat = coordinates[1]

            distance_km = calculate_distance_km(
                lat,
                lng,
                place_lat,
                place_lng,
            )

            places.append(
                {
                    "name": properties.get("name")
                    or properties.get("address_line1")
                    or "Unnamed place",

                    "lat": place_lat,
                    "lng": place_lng,

                    "distance_km": round(distance_km, 3),

                    "address": properties.get("formatted")
                    or properties.get("address_line2")
                    or "",
                }
            )

        places.sort(key=lambda x: x["distance_km"])

        nearest = places[0] if places else None

        return {
            "available": True,
            "source": "geoapify",
            "error": None,
            "places": places,
            "nearest": nearest,
        }

    except requests.exceptions.Timeout:
        return {
            "available": False,
            "source": "geoapify",
            "error": "Geoapify request timed out",
            "places": [],
            "nearest": None,
        }

    except requests.exceptions.RequestException as e:
        return {
            "available": False,
            "source": "geoapify",
            "error": f"Geoapify request failed: {str(e)}",
            "places": [],
            "nearest": None,
        }

    except Exception as e:
        return {
            "available": False,
            "source": "geoapify",
            "error": f"Unexpected error: {str(e)}",
            "places": [],
            "nearest": None,
        }


def nearby_police(lat, lng, radius_m=3000):
    """
    Find nearby police stations.
    """

    result = _nearby_places(
        lat=lat,
        lng=lng,
        category="service.police",
        radius_m=radius_m,
    )

    return {
        "available": result["available"],
        "source": result["source"],
        "error": result["error"],
        "stations": result["places"],
        "nearest": result["nearest"],
    }


def nearby_hospitals(lat, lng, radius_m=5000):
    """
    Find nearby hospitals.
    """

    result = _nearby_places(
        lat=lat,
        lng=lng,
        category="healthcare.hospital",
        radius_m=radius_m,
    )

    return {
        "available": result["available"],
        "source": result["source"],
        "error": result["error"],
        "hospitals": result["places"],
        "nearest": result["nearest"],
    }