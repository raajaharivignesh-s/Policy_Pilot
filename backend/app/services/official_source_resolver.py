from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import re
import requests

from app.core.settings import settings
from app.services.source_trust_service import (
    source_trust_service,
)


@dataclass
class SourceCandidate:
    """
    Represents one candidate source returned by Tavily.
    """

    url: str
    title: str
    content: str

    domain: str = ""
    trust_level: str = "low"
    trusted_source: bool = False

    relevance_score: float = 0.0

    page_title: str = ""
    page_content: str = ""


class OfficialSourceResolver:
    """
    Resolves the best official government source
    for a government scheme.

    Architecture:

        Scheme
          ↓
        ONE targeted Tavily search
          ↓
        Multiple search candidates
          ↓
        Government trust filtering
          ↓
        Candidate ranking
          ↓
        Top candidates selected
          ↓
        HTTP validation
          ↓
        Final ranking
          ↓
        Best official source
    """

    TAVILY_ENDPOINT = (
        "https://api.tavily.com/search"
    )

    # ==========================================================
    # PERFORMANCE SETTINGS
    # ==========================================================

    RESULTS_PER_QUERY = 5

    REQUEST_TIMEOUT = 6

    # Validate only the strongest candidates.
    MAX_VALIDATION_CANDIDATES = 3

    # ==========================================================
    # GENERIC GOVERNMENT PORTALS
    # ==========================================================

    GENERIC_PORTAL_DOMAINS = {
        "scholarships.gov.in",
        "services.india.gov.in",
        "india.gov.in",
        "digitalindia.gov.in",
        "myscheme.gov.in",
    }

    # ==========================================================
    # NON HTML FILES
    # ==========================================================

    NON_HTML_EXTENSIONS = {
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".zip",
        ".rar",
    }

    # ==========================================================
    # GENERIC / SECONDARY PAGE KEYWORDS
    # ==========================================================

    GENERIC_PATH_PENALTIES = {
        "evaluation": 12.0,
        "evaluations": 12.0,
        "report": 10.0,
        "reports": 10.0,
        "study": 9.0,
        "assessment": 9.0,
        "statistics": 8.0,
        "statistic": 8.0,
        "survey": 8.0,
        "research": 8.0,
        "budget": 8.0,
        "news": 6.0,
        "notice": 6.0,
        "notices": 6.0,
        "announcement": 6.0,
        "press-release": 7.0,
        "pressrelease": 7.0,
        "publication": 6.0,
        "publications": 6.0,
    }

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self):

        self.api_key = settings.TAVILY_API_KEY

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "PolicyPilot/1.0 "
                    "(Government Scheme Verification)"
                )
            }
        )

    # ==========================================================
    # PUBLIC RESOLVE
    # ==========================================================

    def resolve(
        self,
        scheme_name: str,
        domain: str = "",
    ) -> dict[str, Any]:
        """
        Resolve the best official government source.

        Only ONE Tavily search is performed.

        Multiple candidates returned by that search
        are ranked and the strongest candidates are
        independently validated.
        """

        scheme_name = (
            scheme_name or ""
        ).strip()

        domain = (
            domain or ""
        ).strip()

        # ------------------------------------------------------
        # Validate input
        # ------------------------------------------------------

        if not scheme_name:

            return self._empty_result(
                scheme_name="",
                reason=(
                    "Scheme name was not provided."
                ),
            )

        # ------------------------------------------------------
        # Check API key
        # ------------------------------------------------------

        if not self.api_key:

            return self._empty_result(
                scheme_name=scheme_name,
                reason=(
                    "TAVILY_API_KEY is not configured."
                ),
            )

        print(
            "\n[OfficialSourceResolver] "
            f"Searching for: {scheme_name}"
        )

        # ------------------------------------------------------
        # ONE TARGETED QUERY
        # ------------------------------------------------------

        query = self._build_targeted_query(
            scheme_name=scheme_name,
            domain=domain,
        )

        print(
            "[OfficialSourceResolver] "
            f"Query: {query}"
        )

        # ------------------------------------------------------
        # ONE Tavily search
        # ------------------------------------------------------

        candidates = self._search(
            query=query,
        )

        print(
            "[OfficialSourceResolver] "
            f"Search results: {len(candidates)}"
        )

        if not candidates:

            return self._empty_result(
                scheme_name=scheme_name,
                reason=(
                    "No search results were found."
                ),
            )

        # ------------------------------------------------------
        # TRUST FILTER
        # ------------------------------------------------------

        trusted_candidates = []

        for candidate in candidates:

            # --------------------------------------------------
            # Ignore downloadable files.
            # --------------------------------------------------

            if self._is_non_html_url(
                candidate.url
            ):
                continue

            # --------------------------------------------------
            # Evaluate source trust.
            # --------------------------------------------------

            trust_result = (
                source_trust_service.evaluate(
                    candidate.url
                )
            )

            if (
                trust_result.get(
                    "trusted_source"
                )
                is not True
            ):
                continue

            candidate.domain = str(
                trust_result.get(
                    "domain",
                    "",
                )
            )

            candidate.trust_level = str(
                trust_result.get(
                    "trust_level",
                    "low",
                )
            )

            candidate.trusted_source = True

            # --------------------------------------------------
            # Calculate ranking score.
            # --------------------------------------------------

            candidate.relevance_score = (
                self._candidate_score(
                    candidate=candidate,
                    scheme_name=scheme_name,
                    domain=domain,
                )
            )

            if candidate.relevance_score <= 0:
                continue

            trusted_candidates.append(
                candidate
            )

        print(
            "[OfficialSourceResolver] "
            f"Trusted candidates: "
            f"{len(trusted_candidates)}"
        )

        if not trusted_candidates:

            return self._empty_result(
                scheme_name=scheme_name,
                reason=(
                    "No trusted government page "
                    "relevant to this scheme was found."
                ),
            )

        # ------------------------------------------------------
        # Rank ALL trusted candidates.
        # ------------------------------------------------------

        trusted_candidates.sort(
            key=lambda candidate: (
                candidate.relevance_score
            ),
            reverse=True,
        )

        # ------------------------------------------------------
        # Display ranking.
        # ------------------------------------------------------

        print(
            "\n[OfficialSourceResolver] "
            "Candidate ranking:"
        )

        for index, candidate in enumerate(
            trusted_candidates,
            start=1,
        ):

            print(
                f"  {index}. "
                f"{candidate.url}"
            )

            print(
                f"     Title: "
                f"{candidate.title}"
            )

            print(
                f"     Score: "
                f"{candidate.relevance_score}"
            )

        # ------------------------------------------------------
        # IMPORTANT:
        #
        # Do NOT blindly validate only #1.
        #
        # A generic evaluation/report page can rank highly
        # because it contains the scheme name many times.
        #
        # We therefore validate the top 3.
        # ------------------------------------------------------

        validation_candidates = (
            trusted_candidates[
                : self.MAX_VALIDATION_CANDIDATES
            ]
        )

        print(
            "\n[OfficialSourceResolver] "
            f"Validating top "
            f"{len(validation_candidates)} "
            "candidate(s)"
        )

        # ------------------------------------------------------
        # Validate candidates concurrently.
        # ------------------------------------------------------

        validated_candidates = (
            self._validate_candidates(
                candidates=validation_candidates,
                scheme_name=scheme_name,
                domain=domain,
            )
        )

        if not validated_candidates:

            return self._empty_result(
                scheme_name=scheme_name,
                reason=(
                    "Trusted government candidates "
                    "were found, but none could be "
                    "independently validated."
                ),
            )

        # ------------------------------------------------------
        # FINAL RANKING
        # ------------------------------------------------------

        validated_candidates.sort(
            key=lambda candidate: (
                candidate.relevance_score
            ),
            reverse=True,
        )

        best_candidate = (
            validated_candidates[0]
        )

        print(
            "\n[OfficialSourceResolver] "
            "Final selected source:"
        )

        print(
            f"  URL: "
            f"{best_candidate.url}"
        )

        print(
            f"  Title: "
            f"{best_candidate.page_title or best_candidate.title}"
        )

        print(
            f"  Score: "
            f"{best_candidate.relevance_score}"
        )

        # ------------------------------------------------------
        # Build result
        # ------------------------------------------------------

        return self._build_result(
            scheme_name=scheme_name,
            candidate=best_candidate,
            title=(
                best_candidate.page_title
                or best_candidate.title
            ),
            score=best_candidate.relevance_score,
        )

    # ==========================================================
    # TARGETED SEARCH QUERY
    # ==========================================================

    def _build_targeted_query(
        self,
        scheme_name: str,
        domain: str,
    ) -> str:
        """
        Build one domain-aware search query.
        """

        clean_name = (
            scheme_name.strip()
        )

        if domain == "education":

            return (
                f'"{clean_name}" '
                f'"Tamil Nadu" '
                f'official government scheme '
                f'education site:gov.in'
            )

        if domain == "agriculture":

            return (
                f'"{clean_name}" '
                f'"Tamil Nadu" '
                f'official government scheme '
                f'agriculture site:gov.in'
            )

        if domain == "healthcare":

            return (
                f'"{clean_name}" '
                f'"Tamil Nadu" '
                f'official government scheme '
                f'health site:gov.in'
            )

        return (
            f'"{clean_name}" '
            f'"Tamil Nadu" '
            f'official government scheme '
            f'site:gov.in'
        )

    # ==========================================================
    # TAVILY SEARCH
    # ==========================================================

    def _search(
        self,
        query: str,
    ) -> list[SourceCandidate]:
        """
        Perform exactly ONE Tavily search request.

        One request can return multiple candidate URLs.
        """

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": self.RESULTS_PER_QUERY,
            "include_answer": False,
            "include_raw_content": False,
        }

        try:

            response = requests.post(
                self.TAVILY_ENDPOINT,
                json=payload,
                timeout=self.REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()

        except Exception as exc:

            print(
                "[OfficialSourceResolver] "
                "Tavily search failed:",
                exc,
            )

            return []

        if not isinstance(
            data,
            dict,
        ):
            return []

        raw_results = data.get(
            "results",
            [],
        )

        if not isinstance(
            raw_results,
            list,
        ):
            return []

        candidates = []

        seen_urls = set()

        for item in raw_results:

            if not isinstance(
                item,
                dict,
            ):
                continue

            url = str(
                item.get(
                    "url",
                    "",
                )
            ).strip()

            if not url:
                continue

            normalized_url = (
                self._normalize_url(
                    url
                )
            )

            if (
                normalized_url
                in seen_urls
            ):
                continue

            seen_urls.add(
                normalized_url
            )

            title = str(
                item.get(
                    "title",
                    "",
                )
            ).strip()

            content = str(
                item.get(
                    "content",
                    "",
                )
            ).strip()

            candidates.append(
                SourceCandidate(
                    url=url,
                    title=title,
                    content=content,
                )
            )

        return candidates

    # ==========================================================
    # CANDIDATE SCORE
    # ==========================================================

  # ------------------------------------------------------

        score += self._domain_relevance_bonus(
            candidate.domain,
            domain,
        )

        # ------------------------------------------------------
        # Generic page penalty
        # ------------------------------------------------------

    def _candidate_score(
        self,
        candidate: SourceCandidate,
        scheme_name: str,
        domain: str,
    ) -> float:
        """
        Calculate the initial source ranking score.

        Source quality is intentionally weighted more heavily
        than raw text frequency.

        Priority:

            1. Dedicated scheme page
            2. Official department relevance
            3. Government domain
            4. Scheme relevance
            5. Generic-page penalties
        """

        # ------------------------------------------------------
        # Base relevance
        # ------------------------------------------------------

        relevance_score = self._calculate_relevance(
            scheme_name=scheme_name,
            title=candidate.title,
            content=candidate.content,
        )

        # ------------------------------------------------------
        # Official government domain
        # ------------------------------------------------------

        government_score = (
            self._official_domain_bonus(
                candidate.domain
            )
        )

        # ------------------------------------------------------
        # Dedicated scheme-page quality
        #
        # This is deliberately given a large weight.
        # ------------------------------------------------------

        dedicated_score = (
            self._dedicated_page_bonus(
                url=candidate.url,
                title=candidate.title,
                scheme_name=scheme_name,
            )
        )

        # ------------------------------------------------------
        # Requested-domain relevance
        #
        # Works for:
        # education
        # agriculture
        # healthcare
        # ------------------------------------------------------

        domain_score = (
            self._domain_relevance_bonus(
                candidate.domain,
                domain,
            )
        )

        # ------------------------------------------------------
        # Generic-page penalty
        # ------------------------------------------------------

        generic_penalty = (
            self._generic_page_penalty(
                url=candidate.url,
                title=candidate.title,
                scheme_name=scheme_name,
            )
        )

        # ------------------------------------------------------
        # Final score
        #
        # Dedicated-page quality is the strongest factor.
        # ------------------------------------------------------

        score = (
            dedicated_score * 2.5
            + relevance_score
            + government_score
            + domain_score
            - generic_penalty
        )

        return round(
            max(
                score,
                0.0,
            ),
            4,
        )

    # ==========================================================
    # DEDICATED PAGE BONUS
    # ==========================================================

    def _dedicated_page_bonus(
        self,
        url: str,
        title: str,
        scheme_name: str,
    ) -> float:
        """
        Determine how strongly a page appears to be
        specifically dedicated to the requested scheme.

        Higher score = more scheme-specific.

        The function intentionally distinguishes:

            Dedicated scheme page
            >
            Generic department page
            >
            Evaluation/report page
        """

        parsed = urlparse(url)

        path = (
            parsed.path
            or ""
        ).lower()

        normalized_path = self._normalize(
            path
        )

        normalized_title = self._normalize(
            title
        )

        normalized_scheme = self._normalize(
            scheme_name
        )

        aliases = self._get_aliases(
            scheme_name
        )

        normalized_aliases = [
            self._normalize(alias)
            for alias in aliases
            if alias
        ]

        score = 0.0

        # ======================================================
        # 1. EXACT SCHEME NAME IN TITLE
        # ======================================================

        if (
            normalized_scheme
            and normalized_scheme in normalized_title
        ):
            score += 8.0

        # ======================================================
        # 2. ALIAS IN TITLE
        # ======================================================

        for alias in normalized_aliases:

            if not alias:
                continue

            if alias in normalized_title:
                score += 5.0

        # ======================================================
        # 3. EXACT SCHEME NAME IN URL
        # ======================================================

        if (
            normalized_scheme
            and normalized_scheme in normalized_path
        ):
            score += 10.0

        # ======================================================
        # 4. ALIAS IN URL
        # ======================================================

        for alias in normalized_aliases:

            if not alias:
                continue

            if alias in normalized_path:
                score += 7.0

        # ======================================================
        # 5. IMPORTANT SCHEME-SPECIFIC URL TERMS
        # ======================================================

        dedicated_keywords = {
            "scheme",
            "scholarship",
            "programme",
            "program",
            "insurance",
            "maternity",
            "transplant",
            "welfare",
            "benefit",
            "eligibility",
            "application",
        }

        for keyword in dedicated_keywords:

            if keyword in normalized_path:
                score += 1.0

        # ======================================================
        # 6. TITLE INDICATES A DEDICATED SCHEME PAGE
        # ======================================================

        title_scheme_keywords = {
            "scheme",
            "scholarship",
            "programme",
            "program",
            "insurance",
            "benefit",
            "maternity",
            "transplant",
        }

        for keyword in title_scheme_keywords:

            if keyword in normalized_title:
                score += 1.5

        # ======================================================
        # 7. EXACT TITLE + URL MATCH
        #
        # Strong signal of a dedicated page.
        # ======================================================

        title_match = (
            normalized_scheme
            and normalized_scheme in normalized_title
        )

        url_match = (
            normalized_scheme
            and normalized_scheme in normalized_path
        )

        if title_match and url_match:
            score += 12.0

        # ======================================================
        # 8. EVALUATION / REPORT / RESEARCH PAGES
        #
        # These can contain the scheme name many times,
        # so they must be strongly downgraded.
        # ======================================================

        secondary_keywords = {
            "evaluation",
            "evaluations",
            "report",
            "reports",
            "research",
            "study",
            "assessment",
            "statistics",
            "statistic",
            "survey",
            "publication",
            "publications",
            "impact",
        }

        for keyword in secondary_keywords:

            if keyword in normalized_path:
                score -= 15.0

            if keyword in normalized_title:
                score -= 12.0

        # ======================================================
        # 9. PRESS RELEASE / NEWS
        # ======================================================

        press_keywords = {
            "press",
            "pressrelease",
            "press-release",
            "news",
            "announcement",
            "notice",
        }

        for keyword in press_keywords:

            if keyword in normalized_path:
                score -= 7.0

            if keyword in normalized_title:
                score -= 5.0

        # ======================================================
        # 10. GENERIC DEPARTMENT PAGE
        # ======================================================

        generic_department_titles = {
            "home",
            "homepage",
            "department of agriculture",
            "department of horticulture",
            "department of health",
            "department of education",
            "directorate of collegiate education",
            "directorate of technical education",
            "government of tamil nadu",
        }

        if normalized_title in generic_department_titles:
            score -= 8.0

        return max(
            score,
            0.0,
        )

    # ==========================================================
    # GENERIC PAGE PENALTY
    # ==========================================================

    def _generic_page_penalty(
        self,
        url: str,
        title: str,
        scheme_name: str,
    ) -> float:
        """
        Penalize generic pages.

        Examples:

            evaluation pages
            annual reports
            statistics
            department homepages
            news pages
            generic scheme listings
        """

        parsed = urlparse(
            url
        )

        domain = (
            parsed.hostname
            or ""
        ).lower()

        path = (
            parsed.path
            or "/"
        ).lower()

        normalized_path = self._normalize(
            path
        )

        normalized_title = self._normalize(
            title
        )

        normalized_scheme = self._normalize(
            scheme_name
        )

        penalty = 0.0

        # ------------------------------------------------------
        # Generic portals
        # ------------------------------------------------------

        if (
            domain
            in self.GENERIC_PORTAL_DOMAINS
        ):
            penalty += 3.0

        # ------------------------------------------------------
        # Homepage
        # ------------------------------------------------------

        clean_path = path.rstrip("/")

        if clean_path in {
            "",
            "/",
            "/home",
            "/index",
            "/index.html",
            "/home.html",
        }:
            penalty += 10.0

        # ------------------------------------------------------
        # Generic path keywords
        # ------------------------------------------------------

        for (
            keyword,
            value,
        ) in self.GENERIC_PATH_PENALTIES.items():

            if keyword in normalized_path:

                penalty += value

        # ------------------------------------------------------
        # Generic titles
        # ------------------------------------------------------

        generic_titles = {
            "home",
            "homepage",
            "department of horticulture",
            "department of agriculture",
            "department of health",
            "department of education",
            "annual report",
            "evaluation",
            "statistics",
            "good practices",
            "government services",
            "india portal",
        }

        if normalized_title in generic_titles:

            penalty += 10.0

        # ------------------------------------------------------
        # Title does not mention scheme
        # ------------------------------------------------------

        aliases = self._get_aliases(
            scheme_name
        )

        title_contains_scheme = (
            normalized_scheme
            and normalized_scheme
            in normalized_title
        )

        title_contains_alias = any(
            self._normalize(alias)
            and self._normalize(alias)
            in normalized_title
            for alias in aliases
        )

        if (
            not title_contains_scheme
            and not title_contains_alias
        ):

            penalty += 3.0

        return penalty

    # ==========================================================
    # VALIDATE MULTIPLE CANDIDATES
    # ==========================================================

    def _validate_candidates(
        self,
        candidates: list[SourceCandidate],
        scheme_name: str,
        domain: str,
    ) -> list[SourceCandidate]:
        """
        Validate the strongest candidates concurrently.

        This is the fallback mechanism.

        If candidate #1 is a generic page or fails,
        candidates #2/#3 can still win.
        """

        if not candidates:
            return []

        def validate(
            candidate: SourceCandidate,
        ) -> SourceCandidate | None:

            print(
                "\n[OfficialSourceResolver] "
                f"Validating: {candidate.url}"
            )

            page_title, page_content = (
                self._fetch_page(
                    candidate.url
                )
            )

            # --------------------------------------------------
            # Failed HTTP validation.
            #
            # IMPORTANT:
            # Do not mark it verified.
            # --------------------------------------------------

            if (
                not page_title
                and not page_content
            ):

                print(
                    "[OfficialSourceResolver] "
                    "Validation failed."
                )

                return None

            candidate.page_title = (
                page_title
            )

            candidate.page_content = (
                page_content
            )

            final_title = (
                page_title
                or candidate.title
            )

            final_content = (
                page_content
                or candidate.content
            )

            # --------------------------------------------------
            # Recalculate relevance using real page content.
            # --------------------------------------------------

            score = (
                self._calculate_relevance(
                    scheme_name=scheme_name,
                    title=final_title,
                    content=final_content,
                )
            )

            score += (
                self._official_domain_bonus(
                    candidate.domain
                )
            )

            score += (
                self._dedicated_page_bonus(
                    url=candidate.url,
                    title=final_title,
                    scheme_name=scheme_name,
                )
            )

            score += (
                self._domain_relevance_bonus(
                    candidate.domain,
                    domain,
                )
            )

            score -= (
                self._generic_page_penalty(
                    url=candidate.url,
                    title=final_title,
                    scheme_name=scheme_name,
                )
            )

            score = round(
                max(
                    score,
                    0.0,
                ),
                4,
            )

            if score <= 0:

                print(
                    "[OfficialSourceResolver] "
                    "Candidate rejected after validation."
                )

                return None

            candidate.relevance_score = (
                score
            )

            print(
                "[OfficialSourceResolver] "
                f"Validated score: {score}"
            )

            return candidate

        validated = []

        # ------------------------------------------------------
        # Validate top candidates concurrently.
        # ------------------------------------------------------

        with ThreadPoolExecutor(
            max_workers=min(
                len(candidates),
                self.MAX_VALIDATION_CANDIDATES,
            )
        ) as executor:

            futures = [
                executor.submit(
                    validate,
                    candidate,
                )
                for candidate in candidates
            ]

            for future in as_completed(
                futures
            ):

                try:

                    result = future.result()

                    if result is not None:

                        validated.append(
                            result
                        )

                except Exception as exc:

                    print(
                        "[OfficialSourceResolver] "
                        "Candidate validation error:",
                        exc,
                    )

        return validated

    # ==========================================================
    # FETCH PAGE
    # ==========================================================

    def _fetch_page(
        self,
        url: str,
    ) -> tuple[str, str]:
        """
        Fetch and extract text from an HTML page.
        """

        if self._is_non_html_url(
            url
        ):
            return "", ""

        try:

            response = self.session.get(
                url,
                timeout=self.REQUEST_TIMEOUT,
                allow_redirects=True,
            )

            response.raise_for_status()

            content_type = (
                response.headers.get(
                    "Content-Type",
                    "",
                )
                .lower()
            )

            # --------------------------------------------------
            # Only validate HTML pages.
            # --------------------------------------------------

            if (
                "text/html"
                not in content_type
            ):
                return "", ""

            html = response.text

            # --------------------------------------------------
            # Extract page title.
            # --------------------------------------------------

            title_match = re.search(
                r"<title[^>]*>(.*?)</title>",
                html,
                flags=(
                    re.IGNORECASE
                    | re.DOTALL
                ),
            )

            page_title = ""

            if title_match:

                page_title = (
                    self._clean_html_text(
                        title_match.group(1)
                    )
                )

            # --------------------------------------------------
            # Remove scripts.
            # --------------------------------------------------

            text = re.sub(
                r"<script\b[^>]*>.*?</script>",
                " ",
                html,
                flags=(
                    re.IGNORECASE
                    | re.DOTALL
                ),
            )

            # --------------------------------------------------
            # Remove styles.
            # --------------------------------------------------

            text = re.sub(
                r"<style\b[^>]*>.*?</style>",
                " ",
                text,
                flags=(
                    re.IGNORECASE
                    | re.DOTALL
                ),
            )

            # --------------------------------------------------
            # Remove noscript.
            # --------------------------------------------------

            text = re.sub(
                r"<noscript\b[^>]*>.*?</noscript>",
                " ",
                text,
                flags=(
                    re.IGNORECASE
                    | re.DOTALL
                ),
            )

            text = self._clean_html_text(
                text
            )

            # Keep validation lightweight.
            text = text[:20000]

            return (
                page_title,
                text,
            )

        except Exception as exc:

            print(
                "[OfficialSourceResolver] "
                f"Page fetch failed for {url}:",
                exc,
            )

            return "", ""

    # ==========================================================
    # RELEVANCE CALCULATION
    # ==========================================================

    def _calculate_relevance(
        self,
        scheme_name: str,
        title: str,
        content: str,
    ) -> float:
        """
        Calculate deterministic scheme relevance.
        """

        normalized_scheme = (
            self._normalize(
                scheme_name
            )
        )

        normalized_title = (
            self._normalize(
                title
            )
        )

        normalized_content = (
            self._normalize(
                content
            )
        )

        if not normalized_scheme:
            return 0.0

        score = 0.0

        # ------------------------------------------------------
        # Exact scheme in title
        # ------------------------------------------------------

        if (
            normalized_scheme
            in normalized_title
        ):

            score += 5.0

        # ------------------------------------------------------
        # Exact scheme in content
        # ------------------------------------------------------

        if (
            normalized_scheme
            in normalized_content
        ):

            score += 2.0

        # ------------------------------------------------------
        # Alias matches
        # ------------------------------------------------------

        aliases = self._get_aliases(
            scheme_name
        )

        for alias in aliases:

            normalized_alias = (
                self._normalize(
                    alias
                )
            )

            if not normalized_alias:
                continue

            if (
                normalized_alias
                in normalized_title
            ):

                score += 3.0

            elif (
                normalized_alias
                in normalized_content
            ):

                score += 1.0

        # ------------------------------------------------------
        # Token overlap
        # ------------------------------------------------------

        scheme_tokens = {
            token
            for token
            in normalized_scheme.split()
            if len(token) >= 3
        }

        result_tokens = set(
            (
                normalized_title
                + " "
                + normalized_content
            ).split()
        )

        if scheme_tokens:

            overlap = (
                len(
                    scheme_tokens
                    & result_tokens
                )
                / len(
                    scheme_tokens
                )
            )

            score += (
                overlap * 1.5
            )

        # ------------------------------------------------------
        # Tamil Nadu relevance
        # ------------------------------------------------------

        if (
            "tamil nadu"
            in normalized_title
        ):

            score += 0.5

        if (
            "tamil nadu"
            in normalized_content
        ):

            score += 0.3

        return score

    # ==========================================================
    # SCHEME ALIASES
    # ==========================================================

    def _get_aliases(
        self,
        scheme_name: str,
    ) -> list[str]:
        """
        Known aliases for schemes in the current
        PolicyPilot knowledge base.
        """

        normalized = self._normalize(
            scheme_name
        )

        aliases: list[str] = []

        # ------------------------------------------------------
        # TAMIZH PUDHALVAN
        # ------------------------------------------------------

        if (
            "tamizh pudhalvan"
            in normalized
            or "tamil pudhalvan"
            in normalized
        ):

            aliases.extend(
                [
                    "Tamizh Pudhalvan",
                    "Tamil Pudhalvan",
                    "Tamil Pudhalvan Scheme",
                ]
            )

        # ------------------------------------------------------
        # PUDHUMAI PENN
        # ------------------------------------------------------

        if (
            "pudhumai penn"
            in normalized
        ):

            aliases.extend(
                [
                    "Pudhumai Penn",
                    "Pudhumai Penn Scheme",
                    (
                        "Moovalur Ramamirtham "
                        "Ammaiyar Higher Education "
                        "Assurance Scheme"
                    ),
                ]
            )

        # ------------------------------------------------------
        # MINORITY SCHOLARSHIP
        # ------------------------------------------------------

        if (
            "minority"
            in normalized
            and "post matric"
            in normalized
        ):

            aliases.extend(
                [
                    "Minority Post-Matric Scholarship",
                    "Post Matric Scholarship for Minorities",
                    (
                        "Post-Matric Scholarship "
                        "Scheme for Minorities"
                    ),
                ]
            )

        # ------------------------------------------------------
        # BC MBC DNC
        # ------------------------------------------------------

        if (
            "bc"
            in normalized
            and "mbc"
            in normalized
        ):

            aliases.extend(
                [
                    "BC MBC DNC Post-Matric Scholarship",
                    "Post Matric Scholarship BC MBC DNC",
                    "BC MBC DNC Scholarship",
                ]
            )

        # ------------------------------------------------------
        # DIFFERENTLY ABLED
        # ------------------------------------------------------

        if (
            "differently abled"
            in normalized
        ):

            aliases.extend(
                [
                    (
                        "Scholarship for "
                        "Differently Abled Students"
                    ),
                    (
                        "Differently Abled "
                        "Students Scholarship"
                    ),
                ]
            )

        # ------------------------------------------------------
        # PM KISAN
        # ------------------------------------------------------

        if (
            "pm kisan"
            in normalized
            or "kisan samman nidhi"
            in normalized
        ):

            aliases.extend(
                [
                    "PM-KISAN",
                    "PM KISAN",
                    "Pradhan Mantri Kisan Samman Nidhi",
                ]
            )

        # ------------------------------------------------------
        # PMFBY
        # ------------------------------------------------------

        if (
            "fasal bima"
            in normalized
            or "pmfby"
            in normalized
        ):

            aliases.extend(
                [
                    "PMFBY",
                    "PM Fasal Bima Yojana",
                    "Pradhan Mantri Fasal Bima Yojana",
                ]
            )

        # ------------------------------------------------------
        # KAVIADP
        # ------------------------------------------------------

        if (
            "kaviadp"
            in normalized
            or "all village"
            in normalized
        ):

            aliases.extend(
                [
                    "KAVIADP",
                    (
                        "Kalaignarin All Village "
                        "Integrated Agricultural "
                        "Development Programme"
                    ),
                    (
                        "Kalaignar All Villages "
                        "Integrated Agricultural "
                        "Development Programme"
                    ),
                ]
            )

        # ------------------------------------------------------
        # CMCHIS
        # ------------------------------------------------------

        if (
            "cmchis"
            in normalized
            or "comprehensive health insurance"
            in normalized
        ):

            aliases.extend(
                [
                    "CMCHIS",
                    (
                        "Chief Minister's "
                        "Comprehensive Health "
                        "Insurance Scheme"
                    ),
                    (
                        "Chief Minister "
                        "Comprehensive Health "
                        "Insurance Scheme"
                    ),
                ]
            )

        # ------------------------------------------------------
        # MRMBS
        # ------------------------------------------------------

        if (
            "muthulakshmi reddy"
            in normalized
        ):

            aliases.extend(
                [
                    "MRMBS",
                    (
                        "Dr Muthulakshmi Reddy "
                        "Maternity Benefit Scheme"
                    ),
                    (
                        "Muthulakshmi Reddy "
                        "Maternity Benefit Scheme"
                    ),
                ]
            )

        # ------------------------------------------------------
        # TNOT
        # ------------------------------------------------------

        if (
            "organ transplant"
            in normalized
            or "tnot"
            in normalized
        ):

            aliases.extend(
                [
                    "TNOT",
                    (
                        "Tamil Nadu Organ "
                        "Transplant Programme"
                    ),
                    (
                        "Tamil Nadu Organ "
                        "Transplant Program"
                    ),
                    "TRANSTAN",
                ]
            )

        return aliases

    # ==========================================================
    # OFFICIAL DOMAIN BONUS
    # ==========================================================

    def _official_domain_bonus(
        self,
        domain: str,
    ) -> float:
        """
        Prefer official government domains.
        """

        normalized_domain = (
            domain.lower().strip()
        )

        if not normalized_domain:
            return 0.0

        # Tamil Nadu government.
        if (
            normalized_domain.endswith(
                ".tn.gov.in"
            )
        ):
            return 2.0

        # NIC government.
        if (
            normalized_domain.endswith(
                ".nic.in"
            )
        ):
            return 1.5

        # Indian government.
        if (
            normalized_domain.endswith(
                ".gov.in"
            )
            or normalized_domain == "gov.in"
        ):
            return 1.0

        return 0.3

    # ==========================================================
    # DOMAIN-SPECIFIC BONUS
    # ==========================================================

    def _domain_relevance_bonus(
        self,
        candidate_domain: str,
        requested_domain: str,
    ) -> float:
        """
        Prefer departments related to the requested domain.

        Works across:

            education
            agriculture
            healthcare
        """

        if not requested_domain:
            return 0.0

        candidate = (
            candidate_domain.lower()
        )

        domain = (
            requested_domain.lower()
        )

        domain_keywords = {

            "education": {
                "education",
                "school",
                "college",
                "dte",
                "scholarship",
                "socialwelfare",
                "highereducation",
            },

            "agriculture": {
                "agri",
                "agriculture",
                "horticulture",
                "farmer",
                "farm",
                "tnagrisnet",
            },

            "healthcare": {
                "health",
                "medical",
                "hospital",
                "healthcare",
                "transtan",
                "tnhealth",
                "nhm",
            },
        }

        keywords = domain_keywords.get(
            domain,
            set(),
        )

        for keyword in keywords:

            if keyword in candidate:
                return 1.0

        return 0.0

    # ==========================================================
    # URL HELPERS
    # ==========================================================

    def _is_non_html_url(
        self,
        url: str,
    ) -> bool:
        """
        Detect downloadable documents.
        """

        parsed = urlparse(
            url
        )

        path = (
            parsed.path
            or ""
        ).lower()

        return any(
            path.endswith(
                extension
            )
            for extension
            in self.NON_HTML_EXTENSIONS
        )

    @staticmethod
    def _normalize_url(
        url: str,
    ) -> str:
        """
        Normalize URL for duplicate detection.
        """

        if not url:
            return ""

        parsed = urlparse(
            url.strip()
        )

        hostname = (
            parsed.hostname
            or ""
        ).lower()

        path = (
            parsed.path
            or "/"
        ).rstrip("/")

        return (
            f"{hostname}{path}"
        ).lower()

    # ==========================================================
    # HTML CLEANING
    # ==========================================================

    @staticmethod
    def _clean_html_text(
        value: str,
    ) -> str:
        """
        Convert HTML into plain text.
        """

        value = re.sub(
            r"<[^>]+>",
            " ",
            value,
        )

        value = (
            value
            .replace(
                "&nbsp;",
                " ",
            )
            .replace(
                "&amp;",
                "&",
            )
            .replace(
                "&quot;",
                '"',
            )
            .replace(
                "&#39;",
                "'",
            )
            .replace(
                "&lt;",
                "<",
            )
            .replace(
                "&gt;",
                ">",
            )
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    # ==========================================================
    # TEXT NORMALIZATION
    # ==========================================================

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:
        """
        Normalize text for deterministic comparison.
        """

        return (
            " ".join(
                str(value)
                .lower()
                .replace(
                    "-",
                    " ",
                )
                .replace(
                    "/",
                    " ",
                )
                .replace(
                    "'",
                    " ",
                )
                .replace(
                    ",",
                    " ",
                )
                .replace(
                    ".",
                    " ",
                )
                .split()
            )
        )

    # ==========================================================
    # RESULT BUILDER
    # ==========================================================

    @staticmethod
    def _build_result(
        scheme_name: str,
        candidate: SourceCandidate,
        title: str,
        score: float,
    ) -> dict[str, Any]:
        """
        Build final structured result.
        """

        return {
            "scheme_name": scheme_name,

            "official_url": (
                candidate.url
            ),

            "source_domain": (
                candidate.domain
            ),

            "trust_level": (
                candidate.trust_level
            ),

            "trusted_source": (
                candidate.trusted_source
            ),

            "source_title": title,

            "source_type": (
                "official_government"
            ),

            "verified": True,

            "relevance_score": (
                round(
                    score,
                    4,
                )
            ),

            "reason": (
                "Official government page "
                "was matched and validated "
                "against the requested scheme."
            ),
        }

    # ==========================================================
    # EMPTY RESULT
    # ==========================================================

    @staticmethod
    def _empty_result(
        scheme_name: str,
        reason: str,
    ) -> dict[str, Any]:
        """
        Safe result when no verified official
        government URL is available.
        """

        return {
            "scheme_name": scheme_name,

            "official_url": None,

            "source_domain": "",

            "trust_level": "low",

            "trusted_source": False,

            "source_title": "",

            "source_type": "",

            "verified": False,

            "relevance_score": 0.0,

            "reason": reason,
        }


official_source_resolver = (
    OfficialSourceResolver()
)