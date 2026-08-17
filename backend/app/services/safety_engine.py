from datetime import datetime


class SafetyEngine:
    """
    Calculates safety score based on:

    1. User Reported Incidents
    2. Nearby Police Stations
    3. Street Lighting
    4. Time of Day
    """

    def calculate(
        self,
        incident_count: int,
        police_distance_km: float,
        lighting_score: int,
    ):

        score = 100
        reasons = []

        # ----------------------------------------
        # Incident Score (Maximum -50)
        # ----------------------------------------

        if incident_count == 0:

            reasons.append("No incidents reported nearby")

        elif incident_count <= 2:

            score -= 10
            reasons.append("Few incidents reported nearby")

        elif incident_count <= 5:

            score -= 25
            reasons.append("Moderate number of incidents nearby")

        elif incident_count <= 10:

            score -= 40
            reasons.append("High number of incidents nearby")

        else:

            score -= 50
            reasons.append("Very high crime activity nearby")

        # ----------------------------------------
        # Police Score (Maximum -20)
        # ----------------------------------------

        if police_distance_km <= 0.5:

            reasons.append("Police station is very close")

        elif police_distance_km <= 1:

            score -= 5
            reasons.append("Police station within 1 km")

        elif police_distance_km <= 2:

            score -= 10
            reasons.append("Police station nearby")

        else:

            score -= 20
            reasons.append("Police station is far away")

        # ----------------------------------------
        # Street Lighting (Maximum -20)
        # ----------------------------------------

        if lighting_score >= 8:

            reasons.append("Roads are well lit")

        elif lighting_score >= 5:

            score -= 10
            reasons.append("Average street lighting")

        else:

            score -= 20
            reasons.append("Poor street lighting")

        # ----------------------------------------
        # Time Score (Maximum -10)
        # ----------------------------------------

        hour = datetime.now().hour

        if 6 <= hour <= 18:

            reasons.append("Daytime travel")

        elif 19 <= hour <= 22:

            score -= 5
            reasons.append("Evening travel")

        else:

            score -= 10
            reasons.append("Late night travel")

        # ----------------------------------------
        # Limit Score
        # ----------------------------------------

        score = max(0, min(score, 100))

        # ----------------------------------------
        # Risk Level
        # ----------------------------------------

        if score >= 80:

            risk = "SAFE"

        elif score >= 60:

            risk = "MODERATE"

        else:

            risk = "RISKY"

        return {

            "safety_score": score,

            "risk_level": risk,

            "reasons": reasons

        }


# Singleton Object

safety_engine = SafetyEngine()