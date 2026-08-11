from typing import Any

from app.graph.state import PolicyPilotState
from app.services.source_trust_service import source_trust_service


class RecommendationAgent:
    """
    Creates scheme recommendations from verified information.

    Important:
    - Uses only verified_information.
    - Does not perform new retrieval.
    - Does not invent scheme details.
    - Does not invent or guess URLs.
    - Removes duplicate schemes.
    - Exposes an official URL only when the original
      source URL belongs to a high-trust government domain.
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

            # --------------------------------------------------
            # Ignore unsupported information.
            # --------------------------------------------------

            if item.get("supported") is False:
                continue

            scheme_name = str(
                item.get("scheme_name", "")
            ).strip()

            if not scheme_name:
                continue

            # --------------------------------------------------
            # Avoid duplicate recommendations.
            # --------------------------------------------------

            if scheme_name in seen_schemes:
                continue

            seen_schemes.add(scheme_name)

            section = str(
                item.get("section", "")
            ).strip()

            reason = str(
                item.get("reason", "")
            ).strip()

            # --------------------------------------------------
            # Official source URL
            # --------------------------------------------------
            #
            # IMPORTANT:
            #
            # The URL must already exist in the retrieved
            # source information.
            #
            # We NEVER construct a URL from the scheme name.
            # We NEVER ask the LLM to generate a URL.
            # We only expose URLs from high-trust government
            # sources.
            # --------------------------------------------------

            source_url = item.get(
                "source_url",
                "",
            )

            if not isinstance(
                source_url,
                str,
            ):
                source_url = ""

            source_url = source_url.strip()

            official_url = None

            if source_url:

                trust_result = (
                    source_trust_service.evaluate(
                        source_url
                    )
                )

                if (
                    trust_result.get(
                        "trust_level"
                    )
                    == "high"
                    and trust_result.get(
                        "trusted_source"
                    )
                    is True
                ):
                    official_url = source_url

            # --------------------------------------------------
            # Build recommendation
            # --------------------------------------------------

            recommendations.append(
                {
                    "scheme_name": scheme_name,
                    "section": section,
                    "reason": reason,
                    "official_url": official_url,
                }
            )

        return {
            "recommendations": recommendations
        }


recommendation_agent = RecommendationAgent()