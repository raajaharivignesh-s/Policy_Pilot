from typing import Any

from app.graph.state import PolicyPilotState


class RecommendationAgent:
    """
    Creates scheme recommendations from verified information.

    Important:
    - Uses only verified_information.
    - Does not perform new retrieval.
    - Does not invent scheme details.
    - Removes duplicate schemes.
    """

    def run(
        self,
        state: PolicyPilotState,
    ) -> dict[str, Any]:
        verified_information = state.get(
            "verified_information",
            []
        )

        if not verified_information:
            return {
                "recommendations": []
            }

        recommendations: list[dict[str, Any]] = []

        # Keep track of schemes already added.
        seen_schemes: set[str] = set()

        for item in verified_information:

            # Ignore unsupported information.
            if item.get("supported") is False:
                continue

            scheme_name = str(
                item.get("scheme_name", "")
            ).strip()

            if not scheme_name:
                continue

            # Avoid duplicate recommendations.
            if scheme_name in seen_schemes:
                continue

            seen_schemes.add(scheme_name)

            section = str(
                item.get("section", "")
            ).strip()

            reason = str(
                item.get("reason", "")
            ).strip()

            recommendations.append(
                {
                    "scheme_name": scheme_name,
                    "section": section,
                    "reason": reason,
                }
            )

        return {
            "recommendations": recommendations
        }


recommendation_agent = RecommendationAgent()