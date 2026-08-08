from app.agents.final_response_agent import (
    final_response_agent,
)


def test_scheme_discovery_response():

    state = {
        "query": (
            "What financial assistance is available "
            "for farmers?"
        ),
        "intent": "scheme_discovery",
        "domain": "agriculture",
        "verified_information": [
            {
                "scheme_name": "PM-KISAN",
                "section": "Benefits",
                "supported": True,
                "reason": (
                    "Provides financial assistance "
                    "to eligible farmer families."
                ),
            },
        ],
        "recommendations": [
            {
                "scheme_name": "PM-KISAN",
                "section": "Benefits",
                "reason": (
                    "Provides financial assistance "
                    "to eligible farmer families."
                ),
            },
        ],
        "eligibility_results": [],
    }

    result = final_response_agent.run(state)

    print("\n========================================")
    print("FINAL RESPONSE")
    print("========================================")
    print(result["final_response"])

    assert result["final_response"]

    assert isinstance(
        result["final_response"],
        str,
    )


def test_eligibility_response():

    state = {
        "query": "Am I eligible for PM-KISAN?",
        "intent": "eligibility_check",
        "domain": "agriculture",
        "verified_information": [
            {
                "scheme_name": "PM-KISAN",
                "section": "Eligibility Criteria",
                "supported": True,
                "reason": (
                    "The scheme contains eligibility "
                    "conditions for farmers."
                ),
            },
        ],
        "recommendations": [],
        "eligibility_results": [
            {
                "scheme_name": "PM-KISAN",
                "status": "insufficient_information",
                "matched_rules": [],
                "failed_rules": [],
                "missing_information": [
                    "land ownership details",
                ],
                "reason": (
                    "More information is required "
                    "to determine eligibility."
                ),
            },
        ],
    }

    result = final_response_agent.run(state)

    print("\n========================================")
    print("ELIGIBILITY FINAL RESPONSE")
    print("========================================")
    print(result["final_response"])

    assert result["final_response"]

    assert isinstance(
        result["final_response"],
        str,
    )


def test_empty_information():

    state = {
        "query": "How do I repair a car engine?",
        "intent": "general_query",
        "domain": "general",
        "verified_information": [],
        "recommendations": [],
        "eligibility_results": [],
    }

    result = final_response_agent.run(state)

    print("\n========================================")
    print("EMPTY KNOWLEDGE RESPONSE")
    print("========================================")
    print(result["final_response"])

    assert result["final_response"]

    assert (
        "couldn't find relevant government"
        in result["final_response"].lower()
    )


def test_insufficient_eligibility_response():

    state = {
        "query": "Am I eligible for PM-KISAN?",
        "intent": "eligibility_check",
        "domain": "agriculture",
        "verified_information": [
            {
                "scheme_name": "PM-KISAN",
                "section": "Eligibility Criteria",
                "supported": True,
                "reason": (
                    "Eligibility conditions are "
                    "available."
                ),
            },
        ],
        "eligibility_results": [
            {
                "scheme_name": "PM-KISAN",
                "status": "insufficient_information",
                "matched_rules": [],
                "failed_rules": [],
                "missing_information": [
                    "income",
                ],
                "reason": (
                    "The available information is "
                    "not sufficient."
                ),
            },
        ],
        "recommendations": [],
    }

    result = final_response_agent.run(state)

    assert result["final_response"]

    assert isinstance(
        result["final_response"],
        str,
    )