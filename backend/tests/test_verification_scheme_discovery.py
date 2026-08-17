from app.agents.research_agent import research_agent
from app.agents.verification_agent import verification_agent


def print_verification_results(
    result: dict,
) -> None:

    print("\n")
    print("=" * 80)
    print("VERIFICATION SCHEME DISCOVERY")
    print("=" * 80)

    verified_information = result.get(
        "verified_information",
        [],
    )

    print(
        f"\nVerification entries: "
        f"{len(verified_information)}"
    )

    print("\n" + "-" * 80)

    schemes = set()

    for index, item in enumerate(
        verified_information,
        start=1,
    ):

        print(
            f"\n{index}. "
            f"Scheme: "
            f"{item.get('scheme_name', '')}"
        )

        print(
            f"   Supported: "
            f"{item.get('supported', False)}"
        )

        print(
            f"   Section: "
            f"{item.get('section', '')}"
        )

        print(
            f"   Source Type: "
            f"{item.get('source_type', '')}"
        )

        print(
            f"   Trust Level: "
            f"{item.get('trust_level', '')}"
        )

        print(
            f"   Source URL: "
            f"{item.get('source_url', '')}"
        )

        print(
            f"   Reason: "
            f"{item.get('reason', '')}"
        )

        if (
            item.get("supported") is True
            and item.get("scheme_name")
        ):
            schemes.add(
                item["scheme_name"]
            )

    print("\n")
    print("=" * 80)

    print(
        f"\nUnique supported schemes: "
        f"{len(schemes)}"
    )

    for index, scheme in enumerate(
        sorted(schemes),
        start=1,
    ):
        print(
            f"{index}. {scheme}"
        )

    print("\n")
    print("=" * 80)


def test_education_scheme_verification():

    query = (
        "What are the schemes "
        "for Tamil Nadu students?"
    )

    research_state = {
        "query": query,
        "intent": "scheme_discovery",
        "domain": "education",
    }

    research_result = research_agent.run(
        research_state
    )

    retrieved_documents = (
        research_result.get(
            "retrieved_documents",
            [],
        )
    )

    assert retrieved_documents

    print("\n")
    print("=" * 80)
    print("RESEARCH → VERIFICATION")
    print("=" * 80)

    print(
        f"\nRetrieved documents: "
        f"{len(retrieved_documents)}"
    )

    verification_state = {
        "query": query,
        "intent": "scheme_discovery",
        "domain": "education",
        "retrieved_documents": (
            retrieved_documents
        ),
    }

    verification_result = (
        verification_agent.run(
            verification_state
        )
    )

    print_verification_results(
        verification_result
    )

    verified_information = (
        verification_result.get(
            "verified_information",
            [],
        )
    )

    assert verified_information

    supported_schemes = {
        item.get(
            "scheme_name",
            "",
        )
        for item in verified_information
        if (
            item.get("supported") is True
            and item.get("scheme_name")
        )
    }

    print(
        "\nSupported schemes found:",
        len(supported_schemes),
    )

    # The discovery query should verify
    # multiple schemes, not just one.
    assert len(supported_schemes) >= 3

    # All supported RAG documents should remain
    # associated with the education domain.
    for item in verified_information:

        if item.get("supported") is not True:
            continue

        metadata = item.get(
            "metadata",
            {},
        )

        assert metadata.get(
            "domain"
        ) == "education"