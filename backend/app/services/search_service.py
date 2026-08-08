from typing import Any

from tavily import TavilyClient

from app.core.settings import settings


class SearchService:
    """
    Service responsible for searching the web using Tavily.

    This service is intentionally kept separate from the
    Research Agent so the agent does not depend directly
    on the Tavily SDK.
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
        search_depth: str = "advanced",
    ) -> list[dict[str, Any]]:
        """
        Search the web using Tavily.

        Returns a normalized list of search results.
        """

        if not query or not query.strip():
            return []

        if max_results <= 0:
            return []

        if not self.is_available():
            return []

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

        results = response.get(
            "results",
            [],
        )

        if not isinstance(
            results,
            list,
        ):
            return []

        normalized_results = []

        for result in results:

            if not isinstance(
                result,
                dict,
            ):
                continue

            normalized_results.append(
                {
                    "title": result.get(
                        "title",
                        "",
                    ),
                    "url": result.get(
                        "url",
                        "",
                    ),
                    "content": result.get(
                        "content",
                        "",
                    ),
                    "score": result.get(
                        "score",
                        None,
                    ),
                }
            )

        return normalized_results


search_service = SearchService()