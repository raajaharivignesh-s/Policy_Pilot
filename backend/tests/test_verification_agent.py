from app.agents.verification_agent import verification_agent


def test_verification_with_retrieved_documents():

    state = {
        "query": (
            "What financial assistance is available "
            "for farmers?"
        ),
        "retrieved_documents": [
            {
                "text": (
                    "Eligible farmers receive financial "
                    "assistance for installing drip "
                    "irrigation systems."
                ),
                "metadata": {
                    "scheme_name": (
                        "Per Drop More Crop "
                        "(Micro Irrigation)"
                    ),
                    "section": "Benefits",
                    "domain": "agriculture",
                },
            },
            {
                "text": (
                    "Eligible farmers receive financial "
                    "compensation for crop loss due to "
                    "natural disasters."
                ),
                "metadata": {
                    "scheme_name": (
                        "Pradhan Mantri Fasal Bima Yojana "
                        "(PMFBY)"
                    ),
                    "section": "Benefits",
                    "domain": "agriculture",
                },
            },
        ],
    }

    result = verification_agent.run(state)

    print("\n========================================")
    print("VERIFICATION RESULTS")
    print("========================================")

    for item in result["verified_information"]:
        print(item)

    assert result["verified_information"]

    for item in result["verified_information"]:
        assert "scheme_name" in item
        assert "section" in item
        assert "supported" in item
        assert "reason" in item


def test_verification_without_documents():

    state = {
        "query": "What assistance is available?",
        "retrieved_documents": [],
    }

    result = verification_agent.run(state)

    assert result["verified_information"] == []


def test_verification_without_query():

    state = {
        "query": "",
        "retrieved_documents": [],
    }

    result = verification_agent.run(state)

    assert result["verified_information"] == []

    assert result["errors"]