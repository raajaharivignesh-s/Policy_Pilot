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
                "evidence": (
                    "Eligible farmer families receive "
                    "financial assistance."
                ),
                "source_type": "knowledge_base",
                "trust_level": "high",
                "trust_score": 1.0,
                "trusted_source": True,
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

    print(
        "\n========================================"
    )
    print("FINAL RESPONSE")
    print(
        "========================================"
    )
    print(
        result["final_response"]
    )

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

    result = final_response_agent.run(
        state
    )

    print(
        "\n========================================"
    )
    print(
        "ELIGIBILITY FINAL RESPONSE"
    )
    print(
        "========================================"
    )
    print(
        result["final_response"]
    )

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

    result = final_response_agent.run(
        state
    )

    print(
        "\n========================================"
    )
    print(
        "EMPTY KNOWLEDGE RESPONSE"
    )
    print(
        "========================================"
    )
    print(
        result["final_response"]
    )

    assert result["final_response"]

    assert (
        "couldn't find sufficiently verified"
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

    result = final_response_agent.run(
        state
    )

    assert result["final_response"]

    assert isinstance(
        result["final_response"],
        str,
    )


def test_unsupported_information_is_not_used():

    state = {
        "query": (
            "What new agricultural schemes were "
            "announced in Tamil Nadu?"
        ),
        "intent": "scheme_discovery",
        "domain": "agriculture",
        "verified_information": [
            {
                "scheme_name": (
                    "Unverified Farmer Scheme 2026"
                ),
                "section": "Benefits",
                "supported": False,
                "reason": (
                    "The scheme was mentioned by "
                    "an unverified web source."
                ),
                "evidence": (
                    "A private website claims this "
                    "scheme exists."
                ),
                "source_type": "web",
                "source_url": (
                    "https://example.com/scheme"
                ),
                "source_title": (
                    "Private Scheme Website"
                ),
                "trust_level": "low",
                "trust_score": 0.4,
                "trusted_source": False,
            },
        ],
        "recommendations": [],
        "eligibility_results": [],
    }

    result = final_response_agent.run(
        state
    )

    print(
        "\n========================================"
    )
    print(
        "UNSUPPORTED INFORMATION RESPONSE"
    )
    print(
        "========================================"
    )
    print(
        result["final_response"]
    )

    response = result[
        "final_response"
    ].lower()

    assert (
        "unverified farmer scheme 2026"
        not in response
    )


def test_low_trust_web_information_is_not_used():

    state = {
        "query": (
            "What financial assistance schemes "
            "are available?"
        ),
        "intent": "scheme_discovery",
        "domain": "agriculture",
        "verified_information": [
            {
                "scheme_name": (
                    "Fake Agriculture Scheme"
                ),
                "section": "Benefits",
                "supported": False,
                "reason": (
                    "Only mentioned by a low-trust "
                    "web source."
                ),
                "evidence": (
                    "This website claims that farmers "
                    "can receive financial assistance."
                ),
                "source_type": "web",
                "source_url": (
                    "https://example.com/fake"
                ),
                "source_title": (
                    "Unknown Agriculture Website"
                ),
                "trust_level": "low",
                "trust_score": 0.4,
                "trusted_source": False,
            },
        ],
        "recommendations": [],
        "eligibility_results": [],
    }

    result = final_response_agent.run(
        state
    )

    response = result[
        "final_response"
    ].lower()

    assert (
        "fake agriculture scheme"
        not in response
    )

    assert (
        "couldn't find sufficiently verified"
        in response
    )