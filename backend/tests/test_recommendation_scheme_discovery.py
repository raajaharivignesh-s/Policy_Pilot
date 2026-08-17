from app.agents.research_agent import research_agent
from app.agents.verification_agent import verification_agent
from app.agents.recommendation_agent import recommendation_agent


def test_education_scheme_recommendations():

    query = (
        "What are the schemes "
        "for Tamil Nadu students?"
    )

    # --------------------------------------------------
    # 1. Research
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 2. Verification
    # --------------------------------------------------

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

    verified_information = (
        verification_result.get(
            "verified_information",
            [],
        )
    )

    assert verified_information

    # --------------------------------------------------
    # 3. Recommendation
    # --------------------------------------------------

    recommendation_state = {
        "query": query,
        "intent": "scheme_discovery",
        "domain": "education",
        "retrieved_documents": (
            retrieved_documents
        ),
        "verified_information": (
            verified_information
        ),
    }

    recommendation_result = (
        recommendation_agent.run(
            recommendation_state
        )
    )

    recommendations = (
        recommendation_result.get(
            "recommendations",
            [],
        )
    )

    # --------------------------------------------------
    # Print results
    # --------------------------------------------------

    print("\n")
    print("=" * 80)
    print("RECOMMENDATION SCHEME DISCOVERY")
    print("=" * 80)

    print(
        f"\nRecommendations: "
        f"{len(recommendations)}"
    )

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):

        print(
            f"\n{index}. "
            f"{recommendation.get('scheme_name', '')}"
        )

        print(
            f"   Section: "
            f"{recommendation.get('section', '')}"
        )

        print(
            f"   Reason: "
            f"{recommendation.get('reason', '')}"
        )

        print(
            f"   Official URL: "
            f"{recommendation.get('official_url')}"
        )

    print("\n")
    print("=" * 80)

    # --------------------------------------------------
    # Validate recommendations
    # --------------------------------------------------

    scheme_names = {
        recommendation.get(
            "scheme_name",
            "",
        )
        for recommendation in recommendations
    }

    scheme_names.discard("")

    print(
        "\nUnique recommended schemes:",
        len(scheme_names),
    )

    for scheme in sorted(
        scheme_names
    ):
        print(
            f" - {scheme}"
        )

    # --------------------------------------------------
    # Assertions
    # --------------------------------------------------

    assert len(recommendations) >= 3

    assert len(scheme_names) >= 3

    # Every recommendation must have
    # a valid scheme name.
    for recommendation in recommendations:

        assert recommendation.get(
            "scheme_name"
        )

        # The current RAG metadata does not yet
        # contain URLs, so we only verify that the
        # field exists. URL provenance will be handled
        # in the next stage.
        assert (
            "official_url"
            in recommendation
        )