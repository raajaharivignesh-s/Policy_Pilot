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

    Current/latest queries:
        Tavily first

    Normal queries:
        ChromaDB first

    If ChromaDB results are clearly insufficient or unrelated:
        Tavily fallback

    Important:
        - Web URLs are preserved directly from Tavily.
        - No URL is generated or guessed.
        - Official URLs are validated downstream.
    """

    MAX_CHROMA_DISTANCE = 1.25

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

    # ==========================================================
    # Initialization
    # ==========================================================

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
        Determine whether a URL belongs to an official
        government domain.

        Retained for compatibility with existing tests
        and code.

        Actual web-search trust information comes from
        SearchService / SourceTrustService.
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

        trusted_domains = {
            "gov.in",
            "nic.in",
            "mygov.in",
            "gov",
            "pmkisan.gov.in",
            "pmfby.gov.in",
        }

        for trusted_domain in trusted_domains:

            if (
                hostname == trusted_domain
                or hostname.endswith(
                    "." + trusted_domain
                )
            ):
                return True

        return False

    # ==========================================================
    # Query Helpers
    # ==========================================================

    def _normalize_text(
        self,
        text: str,
    ) -> str:
        """
        Normalize text for lightweight matching.

        Punctuation is converted to spaces.

        This ensures that:

            PM-KISAN
            PM KISAN
            PM-KISAN?

        can all be matched consistently.
        """

        if not text:
            return ""

        punctuation = (
            ".,;:!?\"'()[]{}"
            "/\\-_"
        )

        normalized = text.lower()

        for character in punctuation:
            normalized = normalized.replace(
                character,
                " ",
            )

        return " ".join(
            normalized.split()
        )

    def _extract_specific_scheme_terms(
        self,
        query: str,
    ) -> list[str]:
        """
        Extract terms that are likely to represent a specific
        scheme/entity mentioned by the user.

        Broad queries such as:

            "What scholarships are available for students?"

        should not be treated as specific-scheme queries.

        Specific queries such as:

            "Am I eligible for PM-KISAN?"
            "Am I eligible for Kuruvai Sagupadi scheme?"

        should produce meaningful terms that can be used to
        verify whether retrieved documents actually belong
        to the requested scheme/entity.
        """

        normalized = self._normalize_text(
            query
        )

        words = normalized.split()

        stop_words = {
            "what",
            "is",
            "are",
            "the",
            "a",
            "an",
            "for",
            "to",
            "of",
            "in",
            "on",
            "and",
            "or",
            "with",
            "from",
            "how",
            "can",
            "i",
            "we",
            "you",
            "where",
            "who",
            "which",
            "does",
            "do",
            "tell",
            "me",
            "about",
            "scheme",
            "schemes",
            "government",
            "official",
            "website",
            "portal",
            "information",
            "details",
            "available",
            "assistance",
            "benefits",
            "eligible",
            "eligibility",
            "apply",
            "application",
            "latest",
            "current",
            "recent",
            "recently",
            "new",
            "newly",
            "announced",
            "announcement",
            "launched",
            "launch",
            "year",
            "2026",
            "2025",
            "2024",
        }

        meaningful_terms = []

        for word in words:

            if not word:
                continue

            if word in stop_words:
                continue

            if len(word) < 3:
                continue

            if word not in meaningful_terms:
                meaningful_terms.append(word)

        return meaningful_terms

    def _is_specific_scheme_query(
        self,
        query: str,
        intent: str,
    ) -> bool:
        """
        Determine whether a query appears to ask about one
        specific named scheme/entity.

        Eligibility queries are always treated as specific
        because the user is normally asking eligibility for
        a particular scheme.
        """

        if intent == "eligibility_check":
            return True

        terms = self._extract_specific_scheme_terms(
            query
        )

        normalized = self._normalize_text(
            query
        )

        known_scheme_markers = {
            "pm kisan",
            "pm kis an",
            "pmfby",
            "trusst",
            "trust scholarship",
            "pudhumai penn",
            "tamizh pudhalvan",
            "tamil pudhalvan",
            "per drop more crop",
            "micro irrigation",
        }

        for marker in known_scheme_markers:

            if marker in normalized:
                return True

        if len(terms) == 1:
            return True

        return False

    # ==========================================================
    # Scheme Matching
    # ==========================================================

    def _document_contains_scheme_term(
        self,
        document: dict[str, Any],
        terms: list[str],
    ) -> bool:
        """
        Check whether a document belongs to the specific
        scheme/entity requested by the user.

        All meaningful extracted terms must be present
        somewhere in the document text or metadata.

        Example:

            Query:
                Am I eligible for PM-KISAN?

            Terms:
                ["pm", "kisan"]

            Document:
                Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)

            Result:
                True
        """

        if not terms:
            return False

        # ------------------------------------------------------
        # Document text
        # ------------------------------------------------------

        text = self._normalize_text(
            str(
                document.get(
                    "text",
                    "",
                )
            )
        )

        # ------------------------------------------------------
        # Document metadata
        # ------------------------------------------------------

        metadata = document.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            metadata = {}

        metadata_values = []

        for value in metadata.values():

            if value is None:
                continue

            metadata_values.append(
                str(value)
            )

        metadata_text = self._normalize_text(
            " ".join(
                metadata_values
            )
        )

        searchable_text = (
            f"{text} {metadata_text}"
        )

        # ------------------------------------------------------
        # Normalize requested terms.
        # ------------------------------------------------------

        normalized_terms = []

        for term in terms:

            normalized_term = self._normalize_text(
                term
            )

            if not normalized_term:
                continue

            if normalized_term not in normalized_terms:
                normalized_terms.append(
                    normalized_term
                )

        if not normalized_terms:
            return False

        # ------------------------------------------------------
        # ALL scheme terms must be present.
        #
        # This prevents an unrelated scheme from matching
        # merely because it contains one common word.
        # ------------------------------------------------------

        return all(
            term in searchable_text
            for term in normalized_terms
        )

    # ==========================================================
    # ChromaDB Relevance
    # ==========================================================

    def _chroma_results_are_acceptable(
        self,
        query: str,
        intent: str,
        documents: list[dict[str, Any]],
    ) -> bool:
        """
        Determine whether ChromaDB results are good enough
        to be used without web fallback.

        Eligibility queries require:

            1. Eligibility-related section.
            2. Matching requested scheme/entity.

        Specific scheme queries require a matching scheme.

        Broad queries can use semantic retrieval.
        """

        if not documents:
            return False

        # ------------------------------------------------------
        # Remove results beyond the configured distance.
        # ------------------------------------------------------

        usable_documents = [
            document
            for document in documents
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

        if not usable_documents:
            return False

        # ======================================================
        # Eligibility queries
        # ======================================================

        if intent == "eligibility_check":

            eligibility_sections = {
                "Eligibility Criteria",
                "Who Is Not Eligible",
                "Eligibility",
                "Eligibility Requirements",
            }

            terms = self._extract_specific_scheme_terms(
                query
            )

            for document in usable_documents:

                metadata = document.get(
                    "metadata",
                    {},
                )

                if not isinstance(
                    metadata,
                    dict,
                ):
                    metadata = {}

                section = metadata.get(
                    "section",
                    "",
                )

                if section not in eligibility_sections:
                    continue

                if self._document_contains_scheme_term(
                    document=document,
                    terms=terms,
                ):
                    return True

            return False

        # ======================================================
        # Specific named scheme query
        # ======================================================

        if self._is_specific_scheme_query(
            query=query,
            intent=intent,
        ):

            terms = (
                self._extract_specific_scheme_terms(
                    query
                )
            )

            for document in usable_documents:

                if self._document_contains_scheme_term(
                    document=document,
                    terms=terms,
                ):
                    return True

            return False

        # ======================================================
        # Broad scheme-discovery query
        # ======================================================

        return True

    # ==========================================================
    # Filter ChromaDB Documents
    # ==========================================================

    def _filter_chroma_documents(
        self,
        query: str,
        intent: str,
        documents: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Return only ChromaDB documents relevant to the
        user's request.
        """

        usable_documents = [
            document
            for document in documents
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

        if not usable_documents:
            return []

        # ======================================================
        # Eligibility query
        # ======================================================

        if intent == "eligibility_check":

            eligibility_sections = {
                "Eligibility Criteria",
                "Who Is Not Eligible",
                "Eligibility",
                "Eligibility Requirements",
            }

            terms = self._extract_specific_scheme_terms(
                query
            )

            matching_documents = []

            for document in usable_documents:

                metadata = document.get(
                    "metadata",
                    {},
                )

                if not isinstance(
                    metadata,
                    dict,
                ):
                    metadata = {}

                section = metadata.get(
                    "section",
                    "",
                )

                if section not in eligibility_sections:
                    continue

                if not self._document_contains_scheme_term(
                    document=document,
                    terms=terms,
                ):
                    continue

                matching_documents.append(
                    document
                )

            return matching_documents

        # ======================================================
        # Specific named scheme query
        # ======================================================

        if self._is_specific_scheme_query(
            query=query,
            intent=intent,
        ):

            terms = (
                self._extract_specific_scheme_terms(
                    query
                )
            )

            matching_documents = [
                document
                for document in usable_documents
                if self._document_contains_scheme_term(
                    document=document,
                    terms=terms,
                )
            ]

            return matching_documents

        # ======================================================
        # Broad query
        # ======================================================

        return usable_documents

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

        The URL is taken directly from Tavily.

        No URL is generated or guessed.
        """

        if not self.search_service.is_available():
            return []

        if (
            domain
            and domain != "general"
        ):

            search_query = (
                f"{query} {domain} "
                "official government scheme "
                "scheme portal "
                "scheme application "
                "government notification "
                "site:gov.in OR site:nic.in OR site:tn.gov.in"
            )

        else:

            search_query = (
                f"{query} "
                "official government scheme "
                "scheme portal "
                "scheme application "
                "government notification "
                "site:gov.in OR site:nic.in"
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

            trusted_source = result.get(
                "trusted_source",
                False,
            )

            trust_level = result.get(
                "trust_level",
                "low",
            )

            trust_score = result.get(
                "trust_score",
                0.0,
            )

            source_domain = result.get(
                "source_domain",
                "",
            )

            trust_reason = result.get(
                "trust_reason",
                "",
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
                        "trust_level": trust_level,
                        "trust_score": trust_score,
                        "source_domain": source_domain,
                        "trust_reason": trust_reason,
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

        # ======================================================
        # Official government sources first.
        # ======================================================

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
            No research.

        Current/latest queries:
            Tavily first.

        Normal queries:
            ChromaDB first.

        If ChromaDB is clearly insufficient:
            Tavily fallback.
        """

        query = state.get(
            "query",
            "",
        ).strip()

        intent = state.get(
            "intent",
            "",
        ).strip()

        domain = state.get(
            "domain",
            "",
        ).strip()

        # ======================================================
        # Empty query
        # ======================================================

        if not query:

            return {
                "retrieved_documents": [],
                "errors": [
                    "Cannot perform research without a query."
                ],
            }

        # ======================================================
        # General / unsupported domain
        # ======================================================

        if domain == "general":

            return {
                "retrieved_documents": [],
            }

        # ======================================================
        # Current information → Tavily first
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
        # ChromaDB primary search
        # ======================================================

        where = None

        if (
            domain
            and domain != "general"
        ):

            where = {
                "domain": domain,
            }

        # ------------------------------------------------------
        # Targeted retrieval for eligibility queries.
        # ------------------------------------------------------

        retrieval_query = query

        if intent == "eligibility_check":

            scheme_terms = (
                self._extract_specific_scheme_terms(
                    query
                )
            )

            scheme_name = " ".join(
                scheme_terms
            ).strip()

            if scheme_name:

                retrieval_query = (
                    f"{scheme_name} "
                    "eligibility criteria "
                    "who is not eligible "
                    "eligibility requirements"
                )

            else:

                retrieval_query = (
                    f"{query} "
                    "eligibility criteria "
                    "who is not eligible "
                    "eligibility requirements"
                )

        documents = self.retriever.retrieve(
            query=retrieval_query,
            top_k=15,
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
        # Determine whether ChromaDB is acceptable
        # ======================================================

        if self._chroma_results_are_acceptable(
            query=query,
            intent=intent,
            documents=retrieved_documents,
        ):

            useful_documents = (
                self._filter_chroma_documents(
                    query=query,
                    intent=intent,
                    documents=retrieved_documents,
                )
            )

            if useful_documents:

                return {
                    "retrieved_documents":
                        useful_documents,
                }

        # ======================================================
        # ChromaDB failed / irrelevant
        # → Tavily fallback
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
        # Nothing found
        # ======================================================

        return {
            "retrieved_documents": [],
        }


research_agent = ResearchAgent()