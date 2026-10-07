from datetime import datetime


class SafetyEngine:
    """
    Rule-based safety scoring engine.

    Safety indicators:
    1. User-reported incidents
    2. Nearby police station
    3. Street lighting
    4. Time of day

    Missing data is NOT treated as safe or unsafe.
    """

    def calculate(
        self,
        incident_count=None,
        police_distance_km=None,
        lighting_score=None,
        current_hour=None,
    ):
        score = 100

        reasons = []
        indicators_used = []
        indicators_unavailable = []

        # -------------------------------------------------
        # 1. USER-REPORTED INCIDENTS
        # -------------------------------------------------

        if incident_count is None:

            indicators_unavailable.append(
                "incident data"
            )

        else:

            indicators_used.append(
                "reported incidents"
            )

            if incident_count == 0:

                reasons.append(
                    "No user-reported incidents nearby"
                )

            elif incident_count <= 2:

                score -= 10

                reasons.append(
                    "Few user-reported incidents nearby"
                )

            elif incident_count <= 5:

                score -= 25

                reasons.append(
                    "Several user-reported incidents nearby"
                )

            elif incident_count <= 10:

                score -= 40

                reasons.append(
                    "Many user-reported incidents nearby"
                )

            else:

                score -= 50

                reasons.append(
                    "A high number of user-reported incidents nearby"
                )

        # -------------------------------------------------
        # 2. NEAREST POLICE STATION
        # -------------------------------------------------

        if police_distance_km is None:

            indicators_unavailable.append(
                "nearby police station data"
            )

        else:

            indicators_used.append(
                "nearby police station"
            )

            if police_distance_km <= 0.5:

                reasons.append(
                    "Police station is very close"
                )

            elif police_distance_km <= 1:

                score -= 5

                reasons.append(
                    "Police station is within 1 km"
                )

            elif police_distance_km <= 2:

                score -= 10

                reasons.append(
                    "Nearest mapped police station is nearby"
                )

            else:

                score -= 20

                reasons.append(
                    "Nearest mapped police station is more than 2 km away"
                )

        # -------------------------------------------------
        # 3. STREET LIGHTING
        # -------------------------------------------------

        if lighting_score is None:

            indicators_unavailable.append(
                "street lighting data"
            )

        else:

            indicators_used.append(
                "street lighting"
            )

            if lighting_score >= 8:

                reasons.append(
                    "Mapped road lighting indicators are good"
                )

            elif lighting_score >= 5:

                score -= 10

                reasons.append(
                    "Mapped road lighting indicators are moderate"
                )

            else:

                score -= 20

                reasons.append(
                    "Mapped road lighting indicators are poor"
                )

        # -------------------------------------------------
        # 4. TIME OF DAY
        # -------------------------------------------------

        # IMPORTANT:
        # Do not automatically use the backend machine's
        # clock. The frontend will eventually provide the
        # user's local hour.

        if current_hour is None:

            indicators_unavailable.append(
                "time of day"
            )

        else:

            indicators_used.append(
                "time of day"
            )

            if 6 <= current_hour <= 18:

                reasons.append(
                    "Daytime travel"
                )

            elif 19 <= current_hour <= 22:

                score -= 5

                reasons.append(
                    "Evening travel"
                )

            else:

                score -= 10

                reasons.append(
                    "Late-night travel"
                )

        # -------------------------------------------------
        # FINAL SCORE
        # -------------------------------------------------

        score = max(
            0,
            min(round(score), 100)
        )

        # -------------------------------------------------
        # RISK LEVEL
        # -------------------------------------------------

        if score >= 80:

            risk_level = "LOWER_RISK"

        elif score >= 60:

            risk_level = "MODERATE_RISK"

        else:

            risk_level = "HIGHER_RISK"

        # -------------------------------------------------
        # DATA COVERAGE
        # -------------------------------------------------

        total_possible_indicators = 4

        data_available_count = len(
            indicators_used
        )

        data_coverage = round(
            (
                data_available_count
                / total_possible_indicators
            ) * 100
        )

        # -------------------------------------------------
        # CONFIDENCE
        # -------------------------------------------------

        if data_coverage >= 75:

            confidence = "HIGH"

        elif data_coverage >= 50:

            confidence = "MEDIUM"

        else:

            confidence = "LOW"

        # -------------------------------------------------
        # DATA MESSAGE
        # -------------------------------------------------

        if indicators_unavailable:

            data_message = (
                "Some safety indicators were unavailable: "
                + ", ".join(indicators_unavailable)
                + "."
            )

        else:

            data_message = (
                "All configured safety indicators were available."
            )

        # -------------------------------------------------
        # RETURN RESULT
        # -------------------------------------------------

        return {
            "safety_score": score,
            "risk_level": risk_level,
            "reasons": reasons,
            "indicators_used": indicators_used,
            "indicators_unavailable": indicators_unavailable,
            "data_coverage": data_coverage,
            "confidence": confidence,
            "data_message": data_message,
        }


safety_engine = SafetyEngine()