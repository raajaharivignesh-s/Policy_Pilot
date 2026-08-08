from app.graph.workflow import policy_pilot_workflow


def test_agriculture_workflow():
    """
    Test complete scheme-discovery workflow for agriculture.
    """

    state = {
        "query": (
            "What financial assistance is available "
            "for farmers?"
        ),
    }

    result = policy_pilot_workflow.invoke(state)

    print("\n========================================")
    print("AGRICULTURE WORKFLOW")
    print("========================================")

    print("\nQuery:")
    print(result["query"])

    print("\nIntent:")
    print(result["intent"])

    print("\nDomain:")
    print(result["domain"])

    print("\nRetrieved Documents:")
    print(len(result["retrieved_documents"]))

    for document in result["retrieved_documents"]:
        print(
            f"- "
            f"{document['metadata'].get('scheme_name')}"
            f" → "
            f"{document['metadata'].get('section')}"
        )

    print("\nVerified Information:")
    print(result["verified_information"])

    print("\nRecommendations:")
    for recommendation in result["recommendations"]:
        print(
            f"- "
            f"{recommendation['scheme_name']}"
            f" → "
            f"{recommendation['reason']}"
        )

    print("\nFinal Response:")
    print(result["final_response"])

    # Basic workflow validation
    assert result["intent"] == "scheme_discovery"

    assert result["domain"] == "agriculture"

    assert result["retrieved_documents"]

    assert result["verified_information"]

    assert result["recommendations"]

    assert result["eligibility_results"] == []

    assert result["final_response"]

    assert isinstance(
        result["final_response"],
        str,
    )


def test_healthcare_workflow():
    """
    Test complete scheme-discovery workflow for healthcare.
    """

    state = {
        "query": (
            "What healthcare assistance is "
            "available in Tamil Nadu?"
        ),
    }

    result = policy_pilot_workflow.invoke(state)

    print("\n========================================")
    print("HEALTHCARE WORKFLOW")
    print("========================================")

    print("\nQuery:")
    print(result["query"])

    print("\nIntent:")
    print(result["intent"])

    print("\nDomain:")
    print(result["domain"])

    print("\nRetrieved Documents:")
    print(len(result["retrieved_documents"]))

    for document in result["retrieved_documents"]:
        print(
            f"- "
            f"{document['metadata'].get('scheme_name')}"
            f" → "
            f"{document['metadata'].get('section')}"
        )

    print("\nVerified Information:")
    print(result["verified_information"])

    print("\nRecommendations:")
    for recommendation in result["recommendations"]:
        print(
            f"- "
            f"{recommendation['scheme_name']}"
            f" → "
            f"{recommendation['reason']}"
        )

    print("\nFinal Response:")
    print(result["final_response"])

    assert result["intent"] == "scheme_discovery"

    assert result["domain"] == "healthcare"

    assert result["retrieved_documents"]

    assert result["verified_information"]

    assert result["recommendations"]

    assert result["eligibility_results"] == []

    assert result["final_response"]

    assert isinstance(
        result["final_response"],
        str,
    )


def test_education_workflow():
    """
    Test complete scheme-discovery workflow for education.
    """

    state = {
        "query": (
            "What scholarships are available "
            "for students?"
        ),
    }

    result = policy_pilot_workflow.invoke(state)

    print("\n========================================")
    print("EDUCATION WORKFLOW")
    print("========================================")

    print("\nQuery:")
    print(result["query"])

    print("\nIntent:")
    print(result["intent"])

    print("\nDomain:")
    print(result["domain"])

    print("\nRetrieved Documents:")
    print(len(result["retrieved_documents"]))

    for document in result["retrieved_documents"]:
        print(
            f"- "
            f"{document['metadata'].get('scheme_name')}"
            f" → "
            f"{document['metadata'].get('section')}"
        )

    print("\nVerified Information:")
    print(result["verified_information"])

    print("\nRecommendations:")
    for recommendation in result["recommendations"]:
        print(
            f"- "
            f"{recommendation['scheme_name']}"
            f" → "
            f"{recommendation['reason']}"
        )

    print("\nFinal Response:")
    print(result["final_response"])

    assert result["intent"] == "scheme_discovery"

    assert result["domain"] == "education"

    assert result["retrieved_documents"]

    assert result["verified_information"]

    assert result["recommendations"]

    assert result["eligibility_results"] == []

    assert result["final_response"]

    assert isinstance(
        result["final_response"],
        str,
    )


def test_eligibility_workflow():
    """
    Test complete eligibility workflow.
    """

    state = {
        "query": "Am I eligible for PM-KISAN?",
        "user_profile": {
            "occupation": "farmer",
            "land_owner": True,
        },
    }

    result = policy_pilot_workflow.invoke(state)

    print("\n========================================")
    print("ELIGIBILITY WORKFLOW")
    print("========================================")

    print("\nQuery:")
    print(result["query"])

    print("\nIntent:")
    print(result["intent"])

    print("\nDomain:")
    print(result["domain"])

    print("\nRetrieved Documents:")
    print(len(result["retrieved_documents"]))

    for document in result["retrieved_documents"]:
        print(
            f"- "
            f"{document['metadata'].get('scheme_name')}"
            f" → "
            f"{document['metadata'].get('section')}"
        )

    print("\nVerified Information:")
    print(result["verified_information"])

    print("\nEligibility Results:")

    for item in result["eligibility_results"]:
        print(item)

    print("\nFinal Response:")
    print(result["final_response"])

    assert result["intent"] == "eligibility_check"

    assert result["domain"] == "agriculture"

    assert result["retrieved_documents"]

    assert result["verified_information"]

    assert result["eligibility_results"]

    assert result["recommendations"] == []

    assert result["final_response"]

    assert isinstance(
        result["final_response"],
        str,
    )

    for item in result["eligibility_results"]:
        assert item["status"] in {
            "eligible",
            "not_eligible",
            "insufficient_information",
        }


def test_irrelevant_workflow():
    """
    Test a query that is unrelated to government schemes.
    """

    state = {
        "query": "How do I repair a car engine?",
    }

    result = policy_pilot_workflow.invoke(state)

    print("\n========================================")
    print("IRRELEVANT WORKFLOW")
    print("========================================")

    print("\nQuery:")
    print(result["query"])

    print("\nIntent:")
    print(result["intent"])

    print("\nDomain:")
    print(result["domain"])

    print("\nRetrieved Documents:")
    print(len(result["retrieved_documents"]))

    print("\nVerified Information:")
    print(result["verified_information"])

    print("\nRecommendations:")
    print(result["recommendations"])

    print("\nEligibility:")
    print(result["eligibility_results"])

    print("\nFinal Response:")
    print(result["final_response"])

    assert result["intent"] == "general_query"

    assert result["domain"] == "general"

    assert result["retrieved_documents"] == []

    assert result["verified_information"] == []

    assert result["recommendations"] == []

    assert result["eligibility_results"] == []

    assert result["final_response"]

    assert isinstance(
        result["final_response"],
        str,
    )