from app.services.official_source_resolver import (
    official_source_resolver,
)


def print_result(
    scheme_name: str,
    result: dict,
) -> None:

    print("\n")
    print("=" * 80)
    print(
        f"SCHEME: {scheme_name}"
    )
    print("=" * 80)

    print(
        "Official URL:",
        result.get(
            "official_url"
        ),
    )

    print(
        "Source Domain:",
        result.get(
            "source_domain"
        ),
    )

    print(
        "Trust Level:",
        result.get(
            "trust_level"
        ),
    )

    print(
        "Trusted:",
        result.get(
            "trusted_source"
        ),
    )

    print(
        "Verified:",
        result.get(
            "verified"
        ),
    )

    print(
        "Source Title:",
        result.get(
            "source_title"
        ),
    )

    print(
        "Relevance Score:",
        result.get(
            "relevance_score"
        ),
    )

    print(
        "Reason:",
        result.get(
            "reason"
        ),
    )


def test_education_sources():

    schemes = [
        "TAMIZH PUDHALVAN SCHEME",
        "PUDHUMAI PENN SCHEME",
        "MINORITY POST-MATRIC SCHOLARSHIP",
    ]

    for scheme in schemes:

        result = (
            official_source_resolver.resolve(
                scheme_name=scheme,
                domain="education",
            )
        )

        print_result(
            scheme,
            result,
        )

        assert (
            result.get(
                "scheme_name"
            )
            == scheme
        )

        if result.get(
            "official_url"
        ):

            assert (
                result.get(
                    "trusted_source"
                )
                is True
            )

            assert (
                result.get(
                    "trust_level"
                )
                == "high"
            )


def test_agriculture_sources():

    schemes = [
        "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "Kalaignarin All Village Integrated Agricultural Development Programme (KAVIADP)",
    ]

    for scheme in schemes:

        result = (
            official_source_resolver.resolve(
                scheme_name=scheme,
                domain="agriculture",
            )
        )

        print_result(
            scheme,
            result,
        )

        assert (
            result.get(
                "scheme_name"
            )
            == scheme
        )

        if result.get(
            "official_url"
        ):

            assert (
                result.get(
                    "trusted_source"
                )
                is True
            )


def test_healthcare_sources():

    schemes = [
        "Chief Minister's Comprehensive Health Insurance Scheme (CMCHIS)",
        "Dr. Muthulakshmi Reddy Maternity Benefit Scheme (MRMBS)",
        "Tamil Nadu Organ Transplant Programme (TNOT)",
    ]

    for scheme in schemes:

        result = (
            official_source_resolver.resolve(
                scheme_name=scheme,
                domain="healthcare",
            )
        )

        print_result(
            scheme,
            result,
        )

        assert (
            result.get(
                "scheme_name"
            )
            == scheme
        )

        if result.get(
            "official_url"
        ):

            assert (
                result.get(
                    "trusted_source"
                )
                is True
            )