from typing import Any
from urllib.parse import urlparse

from app.graph.state import PolicyPilotState
from app.rag.retriever import retriever
from app.services.search_service import search_service


class ResearchAgent:
    """
    Retrieves government-scheme information.

    Primary knowledge source:
        ChromaDB

    Web source:
        Tavily

    Current/latest queries are routed to Tavily because
    ChromaDB contains the project's stored knowledge and
    may not contain the latest information.
    """

    MAX_CHROMA_DISTANCE = 1.25

    TRUSTED_DOMAINS = {
        "gov.in",
        "nic.in",
        "mygov.in",
        "tn.gov.in",
        "pmkisan.gov.in",
        "pmfby.gov.in",
    }

    CURRENT_KEYWORDS = {
        "latest",
        "current",
        "today",
        "now",
        "recent",
        "recently",
        "new",
        "newly",
        "updated",
        "update",
        "this month",
        "this year",
        "this week",
        "2026",
        "2025-26",
        "recently launched",
        "newly announced",
        "latest announcement",
    }

    def __init__(self):
        self.retriever = retriever
        self.search_service = search_service

    # ==========================================================
    # Current Query Detection
    # ==========================================================

    def _requires_web_search(
        self,
        query: str,
    ) -> bool:
        """
        Determine whether the query explicitly asks for
        current or recently updated information.
        """

        normalized_query = query.lower().strip()

        return any(
            keyword in normalized_query
            for keyword in self.CURRENT_KEYWORDS
        )

    # ==========================================================
    # Trusted Source Detection
    # ==========================================================

    def _is_trusted_source(
        self,
        url: str,
    ) -> bool:
        """
        Determine whether a URL belongs to a preferred
        government domain.
        """

        if not url:
            return False

        try:
            hostname = urlparse(url).hostname

        except Exception:
            return False

        if not hostname:
            return False

        hostname = hostname.lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        for trusted_domain in self.TRUSTED_DOMAINS:

            if (
                hostname == trusted_domain
                or hostname.endswith(
                    "." + trusted_domain
                )
            ):
                return True

        return False

    # ==========================================================
    # Tavily Search
    # ==========================================================

    def _web_search(
        self,
        query: str,
        domain: str,
    ) -> list[dict[str, Any]]:
        """
        Search Tavily and convert web results into the same
        structure used by ChromaDB.
        """

        if not self.search_service.is_available():
            return []

        search_query = query

        if domain and domain != "general":
            search_query = (
                f"{query} {domain} "
                "government official scheme"
            )

        results = self.search_service.search(
            query=search_query,
            max_results=5,
        )

        web_documents = []

        for result in results:

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

            if not content:
                continue

            trusted_source = (
                self._is_trusted_source(
                    url
                )
            )

            web_documents.append(
                {
                    "text": content,
                    "metadata": {
                        "source_type": "web",
                        "title": title,
                        "url": url,
                        "domain": (
                            domain
                            or "general"
                        ),
                        "trusted_source": (
                            trusted_source
                        ),
                    },
                    "distance": (
                        1.0 - score
                        if isinstance(
                            score,
                            (int, float),
                        )
                        else None
                    ),
                }
            )

        # Prefer official government sources.
        web_documents.sort(
            key=lambda document: (
                not document[
                    "metadata"
                ].get(
                    "trusted_source",
                    False,
                ),
                -(
                    1.0
                    - document["distance"]
                    if document["distance"]
                    is not None
                    else 0.0
                ),
            )
        )

        return web_documents

    # ==========================================================
    # Main Research
    # ==========================================================

    def run(
        self,
        state: PolicyPilotState,
    ) -> dict[str, Any]:
        """
        Main research operation.

        General queries:
            No research is performed.

        Current-information query:
            Tavily first.

        Normal policy query:
            ChromaDB first.

        If ChromaDB has no useful results:
            Tavily fallback.
        """

        query = state.get(
            "query",
            "",
        ).strip()

        domain = state.get(
            "domain",
            "",
        ).strip()

        if not query:
            return {
                "retrieved_documents": [],
                "errors": [
                    "Cannot perform research without a query."
                ],
            }

        # ======================================================
        # GENERAL / UNSUPPORTED DOMAIN
        # ======================================================

        if domain == "general":
            return {
                "retrieved_documents": [],
            }

        # ======================================================
        # CURRENT INFORMATION → TAVILY FIRST
        # ======================================================

        if self._requires_web_search(
            query
        ):

            web_documents = self._web_search(
                query=query,
                domain=domain,
            )

            if web_documents:
                return {
                    "retrieved_documents":
                        web_documents,
                }

        # ======================================================
        # CHROMADB PRIMARY SEARCH
        # ======================================================

        where = None

        if domain and domain != "general":
            where = {
                "domain": domain,
            }

        documents = self.retriever.retrieve(
            query=query,
            top_k=5,
            where=where,
        )

        retrieved_documents = []

        for document in documents:

            retrieved_documents.append(
                {
                    "text": document.text,
                    "metadata": document.metadata,
                    "distance": document.distance,
                }
            )

        # ======================================================
        # CHECK CHROMADB RESULTS
        # ======================================================

        useful_documents = [
            document
            for document in retrieved_documents
            if (
                document.get(
                    "distance"
                ) is None
                or document.get(
                    "distance"
                )
                <= self.MAX_CHROMA_DISTANCE
            )
        ]

        if useful_documents:
            return {
                "retrieved_documents":
                    useful_documents,
            }

        # ======================================================
        # CHROMADB FAILED → TAVILY FALLBACK
        # ======================================================

        web_documents = self._web_search(
            query=query,
            domain=domain,
        )

        if web_documents:
            return {
                "retrieved_documents":
                    web_documents,
            }

        # ======================================================
        # NOTHING FOUND
        # ======================================================

        return {
            "retrieved_documents": [],
        }


research_agent = ResearchAgent()