from app.agents.research_agent import research_agent


def test_agriculture_research():

    state = {
        "query": (
            "What financial assistance is available "
            "for farmers?"
        ),
        "intent": "scheme_discovery",
        "domain": "agriculture",
    }

    result = research_agent.run(state)

    print("\n========================================")
    print("AGRICULTURE RESEARCH")
    print("========================================")

    for document in result["retrieved_documents"]:
        print(
            f"\nScheme: "
            f"{document['metadata'].get('scheme_name')}"
        )

        print(
            f"Section: "
            f"{document['metadata'].get('section')}"
        )

        print(
            f"Distance: "
            f"{document.get('distance')}"
        )

    assert result["retrieved_documents"]

    for document in result["retrieved_documents"]:
        assert (
            document["metadata"].get("domain")
            == "agriculture"
        )


def test_education_research():

    state = {
        "query": (
            "What scholarships are available "
            "for students?"
        ),
        "intent": "scheme_discovery",
        "domain": "education",
    }

    result = research_agent.run(state)

    assert result["retrieved_documents"]

    for document in result["retrieved_documents"]:
        assert (
            document["metadata"].get("domain")
            == "education"
        )


def test_healthcare_research():

    state = {
        "query": (
            "What healthcare assistance is "
            "available in Tamil Nadu?"
        ),
        "intent": "scheme_discovery",
        "domain": "healthcare",
    }

    result = research_agent.run(state)

    assert result["retrieved_documents"]

    for document in result["retrieved_documents"]:
        assert (
            document["metadata"].get("domain")
            == "healthcare"
        )


def test_eligibility_research():

    state = {
        "query": (
            "Am I eligible for PM-KISAN?"
        ),
        "intent": "eligibility_check",
        "domain": "agriculture",
    }

    result = research_agent.run(state)

    print("\n========================================")
    print("ELIGIBILITY RESEARCH")
    print("========================================")

    for document in result["retrieved_documents"]:
        print(
            f"\nScheme: "
            f"{document['metadata'].get('scheme_name')}"
        )

        print(
            f"Section: "
            f"{document['metadata'].get('section')}"
        )

    assert result["retrieved_documents"]

    # We specifically want eligibility-related
    # evidence for this intent.
    eligibility_sections = {
        "Eligibility Criteria",
        "Who Is Not Eligible",
    }

    found_eligibility_section = any(
        document["metadata"].get("section")
        in eligibility_sections
        for document in result["retrieved_documents"]
    )

    assert found_eligibility_section

    for document in result["retrieved_documents"]:
        assert (
            document["metadata"].get("domain")
            == "agriculture"
        )


def test_unknown_domain():

    state = {
        "query": "How do I repair a car engine?",
        "intent": "general_query",
        "domain": "general",
    }

    result = research_agent.run(state)

    assert result["retrieved_documents"] == []


def test_empty_query():

    state = {
        "query": "",
        "intent": "scheme_discovery",
        "domain": "agriculture",
    }

    result = research_agent.run(state)

    assert result["retrieved_documents"] == []

    assert result["errors"]