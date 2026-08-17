import requests

OSRM_BASE_URL = "https://router.project-osrm.org/route/v1/driving"


def get_routes(source: dict, destination: dict):
    """
    Fetch alternative routes from OSRM.
    """

    src_lat = source["lat"]
    src_lng = source["lng"]

    dst_lat = destination["lat"]
    dst_lng = destination["lng"]

    url = (
        f"{OSRM_BASE_URL}/"
        f"{src_lng},{src_lat};{dst_lng},{dst_lat}"
        "?alternatives=true"
        "&steps=true"
        "&overview=full"
        "&geometries=geojson"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        routes = []

        names = [
            "Recommended",
            "Alternative 1",
            "Alternative 2"
        ]

        for index, route in enumerate(data.get("routes", [])):

            coordinates = []

            for lng, lat in route["geometry"]["coordinates"]:

                coordinates.append({
                    "lat": lat,
                    "lng": lng
                })

            routes.append({

                "id": index,

                "route_type": names[index]
                if index < len(names)
                else f"Route {index + 1}",

                "distance_km": round(
                    route["distance"] / 1000,
                    2
                ),

                "time_min": round(
                    route["duration"] / 60
                ),

                "geometry": coordinates,

                "steps": route.get("legs", [])[0].get("steps", [])
                if route.get("legs") else []

            })

        return routes

    except requests.exceptions.RequestException as e:

        print("OSRM Error:", e)

        return []

    except Exception as e:

        print("Routing Service Error:", e)

        return []
    analyzed_routes.append({

    "route_type": route["route_type"],

    "distance_km": route["distance_km"],

    "time_min": route["time_min"],

    "geometry": geometry,

    "steps": route.get("steps", []),

    "safety_score": safety["safety_score"],

    "risk_level": safety["risk_level"],

    "reasons": safety["reasons"],

    "features": {
        ...
    }

})