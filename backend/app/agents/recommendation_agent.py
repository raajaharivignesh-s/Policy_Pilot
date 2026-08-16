from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from app.graph.state import PolicyPilotState
from app.services.source_trust_service import source_trust_service
from app.services.official_source_resolver import OfficialSourceResolver


class RecommendationAgent:
    """
    Creates scheme recommendations from verified information.

    Responsibilities:

    - Uses only verified_information.
    - Removes duplicate schemes.
    - Resolves an official government URL when one is
      not already available.
    - Resolves multiple scheme URLs concurrently.
    - Never invents URLs.
    - Never falls back to a generic URL such as india.gov.in.
    - Works across education, agriculture and healthcare.
    """

    MAX_URL_RESOLUTION_WORKERS = 5

    def __init__(self):
        self.source_resolver = OfficialSourceResolver()

    # ==========================================================
    # Resolve one scheme URL
    # ==========================================================

    def _resolve_scheme_url(
        self,
        scheme_name: str,
        domain: str,
    ) -> tuple[str, dict[str, Any]]:
        """
        Resolve the official government URL for one scheme.

        Returns:

            (
                scheme_name,
                resolver_result
            )

        Any resolver failure is converted into an empty result
        instead of breaking the entire recommendation pipeline.
        """

        try:

            result = self.source_resolver.resolve(
                scheme_name=scheme_name,
                domain=domain,
            )

            if not isinstance(
                result,
                dict,
            ):
                return (
                    scheme_name,
                    {},
                )

            return (
                scheme_name,
                result,
            )

        except Exception as exc:

            print(
                "[RecommendationAgent] "
                f"URL resolution failed for "
                f"{scheme_name}: {exc}"
            )

            return (
                scheme_name,
                {},
            )

    # ==========================================================
    # Resolve multiple URLs concurrently
    # ==========================================================

    def _resolve_missing_urls(
        self,
        schemes: list[tuple[str, str]],
    ) -> dict[str, dict[str, Any]]:
        """
        Resolve missing official URLs concurrently.

        This is important for response time.

        BAD:

            scheme 1 -> wait
            scheme 2 -> wait
            scheme 3 -> wait

        GOOD:

            scheme 1 ─┐
            scheme 2 ─┼─ parallel
            scheme 3 ─┘

        The slowest lookup determines the approximate total
        lookup time rather than the sum of all lookups.
        """

        if not schemes:
            return {}

        results: dict[str, dict[str, Any]] = {}

        max_workers = min(
            self.MAX_URL_RESOLUTION_WORKERS,
            len(schemes),
        )

        with ThreadPoolExecutor(
            max_workers=max_workers,
        ) as executor:

            future_map = {
                executor.submit(
                    self._resolve_scheme_url,
                    scheme_name,
                    domain,
                ): scheme_name
                for scheme_name, domain in schemes
            }

            for future in as_completed(
                future_map
            ):

                scheme_name = future_map[
                    future
                ]

                try:

                    resolved_scheme_name, result = (
                        future.result()
                    )

                    results[
                        resolved_scheme_name
                    ] = result

                except Exception as exc:

                    print(
                        "[RecommendationAgent] "
                        f"Concurrent URL resolution "
                        f"failed for {scheme_name}: "
                        f"{exc}"
                    )

                    results[
                        scheme_name
                    ] = {}

        return results

    # ==========================================================
    # Extract official URL from resolver result
    # ==========================================================

    def _extract_official_url(
        self,
        resolver_result: dict[str, Any],
    ) -> str | None:
        """
        Extract a trusted official URL from the resolver result.

        We do not construct or guess URLs.
        """

        if not isinstance(
            resolver_result,
            dict,
        ):
            return None

        official_url = resolver_result.get(
            "official_url",
        )

        if not isinstance(
            official_url,
            str,
        ):
            return None

        official_url = official_url.strip()

        if not official_url:
            return None

        # ------------------------------------------------------
        # Final safety check.
        #
        # Only expose URLs that our trust service identifies
        # as high-trust government sources.
        # ------------------------------------------------------

        trust_result = (
            source_trust_service.evaluate(
                official_url
            )
        )

        if (
            trust_result.get(
                "trust_level"
            )
            != "high"
        ):
            return None

        if (
            trust_result.get(
                "trusted_source"
            )
            is not True
        ):
            return None

        return official_url

    # ==========================================================
    # Main Method
    # ==========================================================

    def run(
        self,
        state: PolicyPilotState,
    ) -> dict[str, Any]:

        verified_information = state.get(
            "verified_information",
            [],
        )

        if not isinstance(
            verified_information,
            list,
        ):
            verified_information = []

        if not verified_information:
            return {
                "recommendations": []
            }

        # ------------------------------------------------------
        # Get current domain.
        #
        # This comes from the workflow state and can be:
        #
        # education
        # agriculture
        # healthcare
        # ------------------------------------------------------

        domain = str(
            state.get(
                "domain",
                "",
            )
        ).strip().lower()

        recommendations: list[
            dict[str, Any]
        ] = []

        # ------------------------------------------------------
        # Track schemes already added.
        # ------------------------------------------------------

        seen_schemes: set[str] = set()

        # ------------------------------------------------------
        # First collect valid verified schemes.
        # ------------------------------------------------------

        verified_items: list[
            dict[str, Any]
        ] = []

        for item in verified_information:

            if not isinstance(
                item,
                dict,
            ):
                continue

            # --------------------------------------------------
            # Ignore explicitly unsupported evidence.
            # --------------------------------------------------

            if item.get(
                "supported"
            ) is False:
                continue

            scheme_name = str(
                item.get(
                    "scheme_name",
                    "",
                )
            ).strip()

            if not scheme_name:
                continue

            # --------------------------------------------------
            # Normalize duplicate detection.
            scheme_key = scheme_name.casefold()

            if scheme_key in seen_schemes:
                continue

            seen_schemes.add(
                scheme_key
            )

            verified_items.append(
                item
            )

        # --------------------------------------------------
        # Filter irrelevant recommendations if a target scheme is identified.
        # --------------------------------------------------
        
        import difflib

        def normalize_name(n: str) -> str:
            n = n.casefold().replace("tamizh", "tamil").replace("scheme", "").strip()
            return n

        target_schemes = set()
        
        # 1. Try to get target scheme from eligibility results
        elig_results = state.get("eligibility_results", [])
        if isinstance(elig_results, list):
            for res in elig_results:
                if isinstance(res, dict) and res.get("scheme_name"):
                    target_schemes.add(normalize_name(res.get("scheme_name")))
        
        # 2. Try to get target scheme by searching query for known scheme names using fuzzy matching
        query = state.get("query", "").strip().casefold()
        query_norm = query.replace("tamizh", "tamil")
        
        for item in verified_items:
            s_name = item.get("scheme_name", "").strip()
            if s_name:
                norm_s = normalize_name(s_name)
                # If the scheme name is longer than 5 chars, check for substring or fuzzy match
                if len(norm_s) > 5:
                    if norm_s in query_norm:
                        target_schemes.add(norm_s)
                    else:
                        # Split query into n-grams of the same word count as norm_s
                        s_words = norm_s.split()
                        q_words = query_norm.split()
                        if len(s_words) <= len(q_words):
                            for i in range(len(q_words) - len(s_words) + 1):
                                window = " ".join(q_words[i:i+len(s_words)])
                                ratio = difflib.SequenceMatcher(None, norm_s, window).ratio()
                                if ratio > 0.8:  # 80% similarity threshold
                                    target_schemes.add(norm_s)
                                    break

        intent = state.get("intent", "").strip()
        is_specific_intent = intent in ("eligibility_check", "scheme_information", "document_query", "application_process")

        # If we found a target scheme, OR if the intent is strictly specific, we filter.
        if target_schemes:
            verified_items = [
                item for item in verified_items
                if normalize_name(item.get("scheme_name", "")) in target_schemes
            ]
        elif is_specific_intent:
            # If we couldn't resolve the target but intent is specific, keep only top 1
            if verified_items:
                verified_items = [verified_items[0]]
        
        if not verified_items:
            return {
                "recommendations": []
            }

        # ======================================================
        # STEP 1
        #
        # Use existing source URL when available.
        #
        # We do NOT perform a web search in this case.
        # ======================================================

        unresolved_schemes: list[
            tuple[str, str]
        ] = []

        resolved_urls: dict[
            str,
            str | None,
        ] = {}

        for item in verified_items:

            scheme_name = str(
                item.get(
                    "scheme_name",
                    "",
                )
            ).strip()

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

            if official_url:

                resolved_urls[
                    scheme_name.casefold()
                ] = official_url

            else:

                unresolved_schemes.append(
                    (
                        scheme_name,
                        domain,
                    )
                )

        # ======================================================
        # STEP 2
        #
        # Resolve missing URLs concurrently.
        # ======================================================

        if unresolved_schemes:

            resolver_results = (
                self._resolve_missing_urls(
                    unresolved_schemes
                )
            )

            for (
                scheme_name,
                resolver_result,
            ) in resolver_results.items():

                official_url = (
                    self._extract_official_url(
                        resolver_result
                    )
                )

                if official_url:

                    resolved_urls[
                        scheme_name.casefold()
                    ] = official_url

        # ======================================================
        # STEP 3
        #
        # Build recommendations.
        # ======================================================

        for item in verified_items:

            scheme_name = str(
                item.get(
                    "scheme_name",
                    "",
                )
            ).strip()

            section = str(
                item.get(
                    "section",
                    "",
                )
            ).strip()

            reason = str(
                item.get(
                    "reason",
                    "",
                )
            ).strip()

            official_url = resolved_urls.get(
                scheme_name.casefold()
            )

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