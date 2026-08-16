from typing import Any
from urllib.parse import urlparse

from app.graph.state import PolicyPilotState
from app.rag.retriever import retriever
from app.services.search_service import search_service
from app.services.llm_service import llm_service


class ResearchAgent:
    """
    Retrieves government-scheme information.

    Knowledge strategy
    ------------------

    1. ChromaDB is the primary knowledge source.
    2. Domain filtering is applied whenever a domain is known.
    3. Broad scheme-discovery queries retrieve multiple chunks.
    4. Retrieved chunks are diversified by scheme so that one
       scheme cannot consume the entire retrieval window.
    5. Specific scheme queries use targeted retrieval.
    6. Current/latest queries use web search first.
    7. ChromaDB falls back to web search when its evidence is
       insufficient.
    8. Web URLs are preserved exactly as returned by the search
       service.
    9. No URL is generated or guessed.
    """

    MAX_CHROMA_DISTANCE = 1.25

    # Number of chunks retrieved from ChromaDB before applying
    # scheme-level diversification.
    BROAD_RETRIEVAL_TOP_K = 25

    # Number of chunks retained from one scheme for a broad
    # discovery query.
    #
    # Keeping more than one chunk is important because different
    # sections may contain:
    #
    #   - identity
    #   - eligibility
    #   - benefits
    #   - documents
    #   - application process
    #
    MAX_CHUNKS_PER_SCHEME = 3

    # Maximum number of unique schemes to retain during broad
    # discovery.
    MAX_DISCOVERY_SCHEMES = 5

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
        self.llm_service = llm_service

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
    # Query Normalization
    # ==========================================================

    def _normalize_text(
        self,
        text: str,
    ) -> str:
        """
        Normalize text for lightweight matching.

        Examples:

            PM-KISAN
            PM KISAN
            PM-KISAN?

        become comparable.
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

    # ==========================================================
    # Specific Scheme Extraction
    # ==========================================================

    def _extract_specific_scheme_terms(
        self,
        query: str,
    ) -> list[str]:
        """
        Extract meaningful terms that may identify a specific
        scheme/entity.

        This method is intentionally lightweight.

        Broad words such as:

            students
            farmers
            healthcare
            assistance

        should not by themselves make a broad discovery query
        behave like a named-scheme query.
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
            "support",
            "help",
            "program",
            "programs",
            "programme",
            "programmes",
            "student",
            "students",
            "farmer",
            "farmers",
            "agriculture",
            "agricultural",
            "healthcare",
            "health",
            "medical",
            "education",
            "educational",
            "tamil",
            "nadu",
            "india",
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
            "whether",
            "qualify",
            "qualified",
            "entitled",
            "please",
            "my",
            "am",
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
                meaningful_terms.append(
                    word
                )

        return meaningful_terms

    # ==========================================================
    # Specific Scheme Detection
    # ==========================================================

    def _is_specific_scheme_query(
        self,
        query: str,
        intent: str,
    ) -> bool:
        """
        Determine whether a query asks about a specific
        named scheme/entity.

        Important:

        Broad discovery intents must NEVER be converted into
        specific scheme retrieval merely because the query
        contains two or more ordinary words.

        Examples:

            "What schemes are available for students?"
                -> False

            "What schemes are available for farmers?"
                -> False

            "What healthcare schemes are available?"
                -> False

            "Am I eligible for PM-KISAN?"
                -> True

            "Tell me about Pudhumai Penn Scheme"
                -> True
        """

        if intent == "scheme_discovery":
            return False

        if intent == "eligibility_check":
            return True

        if intent in {
            "document_query",
            "application_process",
        }:
            return True

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
            "vetri laptop",
            "vetri laptop scheme",
            "per drop more crop",
            "micro irrigation",
            "kuruvai sagupadi",
            "kuruvai",
        }

        for marker in known_scheme_markers:

            if marker in normalized:
                return True

        # ------------------------------------------------------
        # Do not use "two meaningful words" as a generic
        # specific-scheme detector.
        #
        # That caused broad queries such as:
        #
        #   "Tamil Nadu students"
        #
        # to behave like named schemes.
        # ------------------------------------------------------

        return False

    # ==========================================================
    # Scheme Phrase Extraction
    # ==========================================================

    def _extract_scheme_phrase(
        self,
        query: str,
    ) -> str:
        """
        Extract a compact scheme/entity phrase from a query.
        """

        terms = (
            self._extract_specific_scheme_terms(
                query
            )
        )

        return " ".join(
            terms
        ).strip()

    # ==========================================================
    # Document Scheme Matching
    # ==========================================================

    def _document_contains_scheme_term(
        self,
        document: dict[str, Any],
        terms: list[str],
    ) -> bool:
        """
        Determine whether a retrieved document actually
        belongs to the requested scheme/entity.

        ALL meaningful scheme terms must be present somewhere
        in the document text or metadata.
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
        # Metadata
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
        # Normalize terms
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
        # Every requested term must occur.
        # ------------------------------------------------------

        return all(
            term in searchable_text
            for term in normalized_terms
        )

    # ==========================================================
    # ChromaDB Acceptance
    # ==========================================================

    def _chroma_results_are_acceptable(
        self,
        query: str,
        intent: str,
        documents: list[dict[str, Any]],
    ) -> bool:
        """
        Determine whether ChromaDB returned sufficiently
        relevant information.
        """

        if not documents:
            return False

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
        # Eligibility
        # ======================================================

        if intent == "eligibility_check":

            eligibility_sections = {
                "Eligibility Criteria",
                "Who Is Not Eligible",
                "Eligibility",
                "Eligibility Requirements",
            }

            terms = (
                self._extract_specific_scheme_terms(
                    query
                )
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
        # Specific named scheme
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

            return any(
                self._document_contains_scheme_term(
                    document=document,
                    terms=terms,
                )
                for document in usable_documents
            )

        # ======================================================
        # Broad query
        # ======================================================

        return True

    # ==========================================================
    # ChromaDB Filtering
    # ==========================================================

    def _filter_chroma_documents(
        self,
        query: str,
        intent: str,
        documents: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Filter ChromaDB results to only documents that are
        relevant to the requested scheme.
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
        # Eligibility
        # ======================================================

        if intent == "eligibility_check":

            eligibility_sections = {
                "Eligibility Criteria",
                "Who Is Not Eligible",
                "Eligibility",
                "Eligibility Requirements",
            }

            terms = (
                self._extract_specific_scheme_terms(
                    query
                )
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
        # Specific named scheme
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

            return [
                document
                for document in usable_documents
                if self._document_contains_scheme_term(
                    document=document,
                    terms=terms,
                )
            ]

        # ======================================================
        # Broad query
        # ======================================================

        return usable_documents

    # ==========================================================
    # Scheme-Level Diversification
    # ==========================================================

    def _diversify_scheme_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Diversify broad retrieval results by scheme.

        ChromaDB retrieves chunks, not schemes.

        Without diversification:

            Scheme A - chunk 1
            Scheme A - chunk 2
            Scheme A - chunk 3
            Scheme A - chunk 4
            Scheme B - chunk 1

        could consume most of the retrieval window.

        This method keeps a limited number of high-ranked chunks
        from each unique scheme.

        The logic is domain-independent and works for:

            agriculture
            education
            healthcare
            future domains
        """

        if not documents:
            return []

        scheme_counts: dict[str, int] = {}
        unique_schemes: set[str] = set()

        diversified_documents = []

        for document in documents:

            metadata = document.get(
                "metadata",
                {},
            )

            if not isinstance(
                metadata,
                dict,
            ):
                metadata = {}

            scheme_name = str(
                metadata.get(
                    "scheme_name",
                    "",
                )
            ).strip()

            # --------------------------------------------------
            # Web documents or documents without scheme metadata
            # --------------------------------------------------

            if not scheme_name:

                # Preserve non-scheme evidence only if we have
                # not exceeded the overall discovery capacity.
                diversified_documents.append(
                    document
                )

                continue

            # --------------------------------------------------
            # New scheme
            # --------------------------------------------------

            if scheme_name not in unique_schemes:

                if (
                    len(unique_schemes)
                    >= self.MAX_DISCOVERY_SCHEMES
                ):
                    continue

                unique_schemes.add(
                    scheme_name
                )

                scheme_counts[
                    scheme_name
                ] = 0

            # --------------------------------------------------
            # Per-scheme chunk limit
            # --------------------------------------------------

            current_count = scheme_counts.get(
                scheme_name,
                0,
            )

            if (
                current_count
                >= self.MAX_CHUNKS_PER_SCHEME
            ):
                continue

            diversified_documents.append(
                document
            )

            scheme_counts[
                scheme_name
            ] = current_count + 1

        return diversified_documents

    # ==========================================================
    # Web Search
    # ==========================================================

    def _web_search(
        self,
        query: str,
        domain: str,
    ) -> list[dict[str, Any]]:
        """
        Search Tavily and convert web results into the same
        structure used by ChromaDB.

        URLs are taken directly from Tavily.

        No URL is generated or guessed.
        """

        if not self.search_service.is_available():
            return []

        # ------------------------------------------------------
        # Build search query.
        # ------------------------------------------------------

        if (
            domain
            and domain != "general"
        ):

            search_query = (
                f"{query} "
                f"{domain} "
                "official government scheme "
                "government portal "
                "government notification "
                "eligibility "
                "site:gov.in OR site:nic.in "
                "OR site:tn.gov.in"
            )

        else:

            search_query = (
                f"{query} "
                "official government scheme "
                "government portal "
                "government notification "
                "site:gov.in OR site:nic.in"
            )

        # ------------------------------------------------------
        # For eligibility queries, make the search explicitly
        # eligibility-oriented.
        # ------------------------------------------------------

        if (
            "eligible"
            in query.lower()
            or "eligibility"
            in query.lower()
            or "qualify"
            in query.lower()
        ):

            search_query = (
                f"{query} "
                "eligibility criteria "
                "who is eligible "
                "who is not eligible "
                "official government notification "
                "official government portal "
                "site:gov.in OR site:nic.in "
                "OR site:tn.gov.in"
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

        # ------------------------------------------------------
        # Official sources first.
        # ------------------------------------------------------

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

        Scheme discovery:
            ChromaDB first with domain filtering and
            scheme-level diversification.

        Specific scheme queries:
            Targeted retrieval.

        If ChromaDB is insufficient:
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

        conversation_history = state.get(
            "conversation_history",
            [],
        )

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
        # Query Rewriting for Context
        # ======================================================
        # If the user gives a follow-up answer (e.g. "yes, I am a student")
        # or references a numbered scheme ("5th scheme"), the raw query
        # will fail in semantic search. We use a fast LLM call to rewrite it.

        if conversation_history and intent in ("eligibility_check", "scheme_information", "document_query", "application_process"):
            history_lines = []
            for msg in conversation_history[-6:]:
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "").strip()
                if content:
                    history_lines.append(f"{role}: {content}")
            history_text = "\n".join(history_lines)

            rewrite_prompt = f"""
You are a helpful assistant that rewrites a user's follow-up message into a standalone search query.
If the user's message is an answer to previous questions (e.g., "Yes, I am a student"), rewrite it to include the NAME of the scheme they are applying for based on the history.
If the user refers to a scheme by a number (e.g., "5th scheme"), find the exact name of that scheme from the history and replace it.
If the query already contains the specific scheme name, just return the query as is.
Return ONLY the rewritten query text. Do not include quotes or explanations.

CONVERSATION HISTORY:
{history_text}

USER'S CURRENT MESSAGE:
{query}
            """.strip()

            try:
                rewritten_query = self.llm_service.generate(
                    messages=[{"role": "user", "content": rewrite_prompt}],
                    temperature=0.0,
                ).strip()
                print("DEBUG Rewrite prompt:", rewrite_prompt)
                print("DEBUG Rewritten query:", rewritten_query)
                if rewritten_query and len(rewritten_query) < 200:
                    query = rewritten_query
            except Exception as e:
                print("DEBUG Rewrite exception:", e)
                pass


        # ======================================================
        # General domain
        # ======================================================

        if domain == "general":

            return {
                "retrieved_documents": [],
                "query": query,
            }

        # ======================================================
        # Current/latest information
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
                    "query": query,
                }

        # ======================================================
        # ChromaDB domain filter
        # ======================================================

        where = None

        if (
            domain
            and domain != "general"
        ):

            where = {
                "domain": domain,
            }

        # ======================================================
        # Determine retrieval type
        # ======================================================

        is_specific = (
            self._is_specific_scheme_query(
                query=query,
                intent=intent,
            )
        )

        is_discovery = (
            intent == "scheme_discovery"
        )

        # ======================================================
        # Build retrieval query
        # ======================================================

        retrieval_query = query

        if is_specific:

            scheme_phrase = (
                self._extract_scheme_phrase(
                    query
                )
            )

            if intent == "eligibility_check":

                if scheme_phrase:

                    retrieval_query = (
                        f"{scheme_phrase} "
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

            elif intent == "document_query":

                retrieval_query = (
                    f"{scheme_phrase} "
                    "required documents "
                    "documents required "
                    "supporting documents"
                )

            elif intent == "application_process":

                retrieval_query = (
                    f"{scheme_phrase} "
                    "application process "
                    "how to apply "
                    "where to apply"
                )

            else:

                retrieval_query = (
                    f"{scheme_phrase} "
                    "scheme information "
                    "benefits "
                    "eligibility "
                    "application"
                )

        # ======================================================
        # Retrieval size
        # ======================================================

        if is_discovery:

            retrieval_top_k = (
                self.BROAD_RETRIEVAL_TOP_K
            )

        else:

            retrieval_top_k = 15

        # ======================================================
        # Retrieve from ChromaDB
        # ======================================================

        documents = self.retriever.retrieve(
            query=retrieval_query,
            top_k=retrieval_top_k,
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
        # Check ChromaDB relevance
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

            # --------------------------------------------------
            # Scheme discovery
            # --------------------------------------------------

            if is_discovery:

                useful_documents = (
                    self._diversify_scheme_documents(
                        useful_documents
                    )
                )

            if useful_documents:

                return {
                    "retrieved_documents":
                        useful_documents,
                    "query": query,
                }

        # ======================================================
        # Tavily fallback
        # ======================================================

        web_documents = self._web_search(
            query=query,
            domain=domain,
        )

        if web_documents:

            return {
                "retrieved_documents":
                    web_documents,
                "query": query,
            }

        # ======================================================
        # Nothing found
        # ======================================================

        return {
            "retrieved_documents": [],
            "query": query,
        }

research_agent = ResearchAgent()