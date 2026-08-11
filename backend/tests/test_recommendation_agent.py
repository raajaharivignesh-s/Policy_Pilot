from app.agents.recommendation_agent import recommendation_agent


def test_recommendations_from_verified_information():

    state = {
        "query": (
            "What financial assistance is available "
            "for farmers?"
        ),
        "intent": "scheme_discovery",
        "domain": "agriculture",
        "verified_information": [
            {
                "scheme_name": (
                    "Per Drop More Crop "
                    "(Micro Irrigation)"
                ),
                "section": "Benefits",
                "supported": True,
                "reason": (
                    "Provides financial assistance "
                    "for farmers installing "
                    "micro irrigation systems."
                ),
            },
            {
                "scheme_name": (
                    "Pradhan Mantri Fasal Bima "
                    "Yojana (PMFBY)"
                ),
                "section": "Benefits",
                "supported": True,
                "reason": (
                    "Offers financial compensation "
                    "for crop loss."
                ),
            },
        ],
    }

    result = recommendation_agent.run(state)

    print("\n========================================")
    print("RECOMMENDATIONS")
    print("========================================")

    for recommendation in result["recommendations"]:
        print(recommendation)

    assert result["recommendations"]

    assert len(result["recommendations"]) == 2

    assert (
        result["recommendations"][0]["scheme_name"]
        == "Per Drop More Crop (Micro Irrigation)"
    )

    assert (
        result["recommendations"][1]["scheme_name"]
        == "Pradhan Mantri Fasal Bima Yojana (PMFBY)"
    )


def test_duplicate_schemes_are_removed():

    state = {
        "verified_information": [
            {
                "scheme_name": "PM-KISAN",
                "section": "Benefits",
                "supported": True,
                "reason": "Provides financial assistance.",
            },
            {
                "scheme_name": "PM-KISAN",
                "section": "Objective",
                "supported": True,
                "reason": "Supports eligible farmers.",
            },
        ]
    }

    result = recommendation_agent.run(state)

    assert len(result["recommendations"]) == 1

    assert (
        result["recommendations"][0]["scheme_name"]
        == "PM-KISAN"
    )


def test_unsupported_information_is_ignored():

    state = {
        "verified_information": [
            {
                "scheme_name": "Unsupported Scheme",
                "section": "Benefits",
                "supported": False,
                "reason": "Not supported by evidence.",
            },
            {
                "scheme_name": "PM-KISAN",
                "section": "Benefits",
                "supported": True,
                "reason": "Provides financial assistance.",
            },
        ]
    }

    result = recommendation_agent.run(state)

    assert len(result["recommendations"]) == 1

    assert (
        result["recommendations"][0]["scheme_name"]
        == "PM-KISAN"
    )


def test_empty_verified_information():

    state = {
        "verified_information": []
    }

    result = recommendation_agent.run(state)

    assert result["recommendations"] == []


# ==========================================================
# OFFICIAL URL TESTS
# ==========================================================


def test_official_government_url_is_included():

    state = {
        "verified_information": [
            {
                "scheme_name": "PM-KISAN",
                "section": "Benefits",
                "supported": True,
                "reason": (
                    "Provides financial assistance "
                    "to eligible farmers."
                ),
                "source_url": (
                    "https://pmkisan.gov.in/"
                ),
            }
        ]
    }

    result = recommendation_agent.run(state)

    print("\n========================================")
    print("OFFICIAL URL TEST")
    print("========================================")
    print(result["recommendations"])

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert (
        recommendation["scheme_name"]
        == "PM-KISAN"
    )

    assert (
        recommendation["official_url"]
        == "https://pmkisan.gov.in/"
    )


def test_non_government_url_is_not_exposed_as_official():

    state = {
        "verified_information": [
            {
                "scheme_name": "PM-KISAN",
                "section": "Benefits",
                "supported": True,
                "reason": (
                    "Provides financial assistance "
                    "to eligible farmers."
                ),
                "source_url": (
                    "https://indianexpress.com/"
                ),
            }
        ]
    }

    result = recommendation_agent.run(state)

    print("\n========================================")
    print("NON-GOVERNMENT URL TEST")
    print("========================================")
    print(result["recommendations"])

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert (
        recommendation["scheme_name"]
        == "PM-KISAN"
    )

    assert (
        recommendation["official_url"]
        is None
    )