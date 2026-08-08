from app.agents.eligibility_agent import eligibility_agent


def test_eligibility_with_sufficient_information():

    state = {
        "query": "Am I eligible for PM-KISAN?",
        "user_profile": {
            "occupation": "farmer",
            "land_owner": True,
        },
        "verified_information": [
            {
                "scheme_name": "PM-KISAN",
                "section": "Eligibility Criteria",
                "supported": True,
                "reason": (
                    "Eligible farmer families who satisfy "
                    "the scheme conditions may receive "
                    "financial assistance."
                ),
            }
        ],
    }

    result = eligibility_agent.run(state)

    print("\n========================================")
    print("ELIGIBILITY RESULT")
    print("========================================")

    for item in result["eligibility_results"]:
        print(item)

    assert result["eligibility_results"]

    result_item = result["eligibility_results"][0]

    assert result_item["scheme_name"] == "PM-KISAN"

    assert result_item["status"] in {
        "eligible",
        "not_eligible",
        "insufficient_information",
    }

    assert "matched_rules" in result_item
    assert "failed_rules" in result_item
    assert "missing_information" in result_item
    assert "reason" in result_item


def test_insufficient_information():

    state = {
        "query": "Am I eligible for PM-KISAN?",
        "user_profile": {
            "occupation": "farmer",
        },
        "verified_information": [
            {
                "scheme_name": "PM-KISAN",
                "section": "Eligibility Criteria",
                "supported": True,
                "reason": (
                    "The farmer must satisfy the scheme "
                    "eligibility conditions."
                ),
            }
        ],
    }

    result = eligibility_agent.run(state)

    print("\n========================================")
    print("INSUFFICIENT INFORMATION")
    print("========================================")

    for item in result["eligibility_results"]:
        print(item)

    assert result["eligibility_results"]

    result_item = result["eligibility_results"][0]

    assert result_item["status"] in {
        "eligible",
        "not_eligible",
        "insufficient_information",
    }


def test_no_verified_information():

    state = {
        "query": "Am I eligible for PM-KISAN?",
        "user_profile": {
            "occupation": "farmer",
        },
        "verified_information": [],
    }

    result = eligibility_agent.run(state)

    assert result["eligibility_results"] == []


def test_invalid_profile():

    state = {
        "query": "Am I eligible?",
        "user_profile": {},
        "verified_information": [
            {
                "scheme_name": "Test Scheme",
                "section": "Eligibility Criteria",
                "supported": True,
                "reason": (
                    "Applicants must satisfy the eligibility "
                    "conditions."
                ),
            }
        ],
    }

    result = eligibility_agent.run(state)

    assert result["eligibility_results"]

    result_item = result["eligibility_results"][0]

    assert result_item["status"] == (
        "insufficient_information"
    )