from typing import Any

from tavily import TavilyClient

from app.core.settings import settings
from app.services.source_trust_service import (
    source_trust_service,
)


class SearchService:
    """
    Service responsible for searching the web using Tavily.

    The service also evaluates the trust level of each
    returned web source before passing the result downstream.
    """

    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY

        self.client = None

        if self.api_key:
            self.client = TavilyClient(
                api_key=self.api_key
            )

    def is_available(self) -> bool:
        """
        Check whether Tavily web search is configured.
        """

        return self.client is not None

    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
    ) -> list[dict[str, Any]]:
        """
        Search the web using Tavily.

        Each result is normalized and enriched with
        source trust information.
        """

        # --------------------------------------------------
        # Validate query
        # --------------------------------------------------

        if not query or not query.strip():
            return []

        if max_results <= 0:
            return []

        if not self.is_available():
            return []

        # --------------------------------------------------
        # Tavily search
        # --------------------------------------------------

        try:
            response = self.client.search(
                query=query.strip(),
                search_depth=search_depth,
                max_results=max_results,
                include_answer=False,
                include_raw_content=False,
            )

        except Exception:
            return []

        # --------------------------------------------------
        # Validate response
        # --------------------------------------------------

        results = response.get(
            "results",
            [],
        )

        if not isinstance(
            results,
            list,
        ):
            return []

        # --------------------------------------------------
        # Normalize and evaluate sources
        # --------------------------------------------------

        normalized_results = []

        for result in results:

            if not isinstance(
                result,
                dict,
            ):
                continue

            title = result.get(
                "title",
                "",
            )

            url = result.get(
                "url",
                "",
            )

            content = result.get(
                "content",
                "",
            )

            score = result.get(
                "score",
                None,
            )

            # --------------------------------------------------
            # Evaluate source trust
            # --------------------------------------------------

            trust = source_trust_service.evaluate(
                url
            )

            normalized_results.append(
                {
                    "title": title,
                    "url": url,
                    "content": content,
                    "score": score,

                    # Source trust information
                    "trust_level": trust.get(
                        "trust_level",
                        "low",
                    ),
                    "trust_score": trust.get(
                        "trust_score",
                        0.0,
                    ),
                    "trusted_source": trust.get(
                        "trusted_source",
                        False,
                    ),
                    "source_domain": trust.get(
                        "domain",
                        "",
                    ),
                    "trust_reason": trust.get(
                        "reason",
                        "",
                    ),
                }
            )

        return normalized_results


search_service = SearchService()