from app.agents.research_agent import research_agent


def print_results(
    title: str,
    result: dict,
) -> None:

    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)

    documents = result.get(
        "retrieved_documents",
        [],
    )

    print(
        f"\nRetrieved chunks: {len(documents)}"
    )

    print("\n" + "-" * 80)

    schemes = []

    for index, document in enumerate(
        documents,
        start=1,
    ):

        metadata = document.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            metadata = {}

        scheme_name = metadata.get(
            "scheme_name",
            "UNKNOWN",
        )

        section = metadata.get(
            "section",
            "UNKNOWN",
        )

        domain = metadata.get(
            "domain",
            "UNKNOWN",
        )

        distance = document.get(
            "distance",
            None,
        )

        print(
            f"\n{index}. {scheme_name}"
        )

        print(
            f"   Domain: {domain}"
        )

        print(
            f"   Section: {section}"
        )

        print(
            f"   Distance: {distance}"
        )

        if (
            scheme_name
            not in schemes
            and scheme_name != "UNKNOWN"
        ):
            schemes.append(
                scheme_name
            )

    print("\n")
    print("-" * 80)

    print(
        f"\nUnique schemes: {len(schemes)}"
    )

    for index, scheme in enumerate(
        schemes,
        start=1,
    ):

        print(
            f"{index}. {scheme}"
        )

    print("\n")
    print("=" * 80)


def run_research_test(
    query: str,
    intent: str,
    domain: str,
) -> dict:

    state = {
        "query": query,
        "intent": intent,
        "domain": domain,
    }

    return research_agent.run(
        state
    )


# ==========================================================
# EDUCATION
# ==========================================================


def test_education_scheme_discovery():

    result = run_research_test(
        query=(
            "What are the schemes "
            "for Tamil Nadu students?"
        ),
        intent="scheme_discovery",
        domain="education",
    )

    print_results(
        "EDUCATION SCHEME DISCOVERY",
        result,
    )

    documents = result.get(
        "retrieved_documents",
        [],
    )

    assert documents

    schemes = {
        document.get(
            "metadata",
            {},
        ).get(
            "scheme_name",
            "",
        )
        for document in documents
    }

    schemes.discard("")

    assert len(schemes) >= 3

    assert all(
        document.get(
            "metadata",
            {},
        ).get(
            "domain"
        )
        == "education"
        for document in documents
    )


# ==========================================================
# AGRICULTURE
# ==========================================================


def test_agriculture_scheme_discovery():

    result = run_research_test(
        query=(
            "What are the schemes "
            "available for farmers?"
        ),
        intent="scheme_discovery",
        domain="agriculture",
    )

    print_results(
        "AGRICULTURE SCHEME DISCOVERY",
        result,
    )

    documents = result.get(
        "retrieved_documents",
        [],
    )

    assert documents

    schemes = {
        document.get(
            "metadata",
            {},
        ).get(
            "scheme_name",
            "",
        )
        for document in documents
    }

    schemes.discard("")

    assert len(schemes) >= 3

    assert all(
        document.get(
            "metadata",
            {},
        ).get(
            "domain"
        )
        == "agriculture"
        for document in documents
    )


# ==========================================================
# HEALTHCARE
# ==========================================================


def test_healthcare_scheme_discovery():

    result = run_research_test(
        query=(
            "What healthcare schemes "
            "are available in Tamil Nadu?"
        ),
        intent="scheme_discovery",
        domain="healthcare",
    )

    print_results(
        "HEALTHCARE SCHEME DISCOVERY",
        result,
    )

    documents = result.get(
        "retrieved_documents",
        [],
    )

    assert documents

    schemes = {
        document.get(
            "metadata",
            {},
        ).get(
            "scheme_name",
            "",
        )
        for document in documents
    }

    schemes.discard("")

    assert len(schemes) >= 3

    assert all(
        document.get(
            "metadata",
            {},
        ).get(
            "domain"
        )
        == "healthcare"
        for document in documents
    )