from urllib.parse import urlparse


class SourceTrustService:
    """
    Determines the trust level of a web source.

    Trust levels:

        high
            Official government domains and government
            institutional portals.

        medium
            Reputable news organizations and academic/
            educational institutions.

        low
            Private websites, aggregators, blogs,
            social media, video platforms, and unknown
            sources.
    """

    HIGH_TRUST_DOMAINS = {
        ".gov.in",
        ".nic.in",
        ".gov",
    }

    MEDIUM_TRUST_DOMAINS = {
        ".ac.in",
        ".edu",
        "reuters.com",
        "thehindu.com",
        "indianexpress.com",
        "timesofindia.indiatimes.com",
        "hindustantimes.com",
        "ndtv.com",
    }

    LOW_TRUST_DOMAINS = {
        "youtube.com",
        "youtu.be",
        "facebook.com",
        "instagram.com",
        "x.com",
        "twitter.com",
    }

    def get_domain(
        self,
        url: str,
    ) -> str:
        """
        Extract the hostname from a URL.
        """

        if not url:
            return ""

        try:
            parsed = urlparse(
                url.strip()
            )

            hostname = (
                parsed.hostname or ""
            )

            return hostname.lower().rstrip(".")

        except Exception:
            return ""

    def is_high_trust_domain(
        self,
        domain: str,
    ) -> bool:
        """
        Check whether a domain is an official
        government domain.

        Examples accepted:

            tn.gov.in
            www.tn.gov.in
            scholarship.tn.gov.in
            nic.in
            example.nic.in

        The check is boundary-aware so that a domain such as
        notgov.in is not accidentally accepted.
        """

        if not domain:
            return False

        domain = domain.lower().rstrip(".")

        for trusted_domain in self.HIGH_TRUST_DOMAINS:

            trusted_domain = (
                trusted_domain.lower()
            )

            if trusted_domain.startswith("."):

                if domain.endswith(
                    trusted_domain
                ):
                    return True

            else:

                if (
                    domain == trusted_domain
                    or domain.endswith(
                        "." + trusted_domain
                    )
                ):
                    return True

        return False

    def is_medium_trust_domain(
        self,
        domain: str,
    ) -> bool:
        """
        Check whether a domain belongs to a
        reputable secondary or academic source.
        """

        if not domain:
            return False

        domain = domain.lower().rstrip(".")

        for trusted_domain in self.MEDIUM_TRUST_DOMAINS:

            trusted_domain = (
                trusted_domain.lower()
            )

            if (
                domain == trusted_domain
                or domain.endswith(
                    "." + trusted_domain
                )
            ):
                return True

        return False

    def is_low_trust_domain(
        self,
        domain: str,
    ) -> bool:
        """
        Identify known low-trust distribution
        platforms.
        """

        if not domain:
            return False

        domain = domain.lower().rstrip(".")

        for low_trust_domain in self.LOW_TRUST_DOMAINS:

            low_trust_domain = (
                low_trust_domain.lower()
            )

            if (
                domain == low_trust_domain
                or domain.endswith(
                    "." + low_trust_domain
                )
            ):
                return True

        return False

    def evaluate(
        self,
        url: str,
    ) -> dict[str, object]:
        """
        Evaluate a source and return structured
        trust information.
        """

        domain = self.get_domain(url)

        # --------------------------------------------------
        # HIGH TRUST
        # --------------------------------------------------

        if self.is_high_trust_domain(
            domain
        ):
            return {
                "trust_level": "high",
                "trust_score": 1.0,
                "trusted_source": True,
                "domain": domain,
                "reason": (
                    "Official government domain."
                ),
            }

        # --------------------------------------------------
        # MEDIUM TRUST
        # --------------------------------------------------

        if self.is_medium_trust_domain(
            domain
        ):
            return {
                "trust_level": "medium",
                "trust_score": 0.7,
                "trusted_source": False,
                "domain": domain,
                "reason": (
                    "Reputable secondary or "
                    "academic source."
                ),
            }

        # --------------------------------------------------
        # KNOWN LOW TRUST
        # --------------------------------------------------

        if self.is_low_trust_domain(
            domain
        ):
            return {
                "trust_level": "low",
                "trust_score": 0.2,
                "trusted_source": False,
                "domain": domain,
                "reason": (
                    "Social media or user-generated "
                    "content platform."
                ),
            }

        # --------------------------------------------------
        # UNKNOWN / PRIVATE SOURCE
        # --------------------------------------------------

        return {
            "trust_level": "low",
            "trust_score": 0.4,
            "trusted_source": False,
            "domain": domain,
            "reason": (
                "Source is not recognized as an "
                "official government domain."
            ),
        }


source_trust_service = SourceTrustService()