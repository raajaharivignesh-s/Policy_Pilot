from app.agents.verification_agent import (
    verification_agent,
)


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
                    "source_type": "knowledge_base",
                    "trust_level": "high",
                    "trust_score": 1.0,
                    "trusted_source": True,
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
                    "source_type": "knowledge_base",
                    "trust_level": "high",
                    "trust_score": 1.0,
                    "trusted_source": True,
                },
            },
        ],
    }

    result = verification_agent.run(state)

    print(
        "\n========================================"
    )
    print(
        "VERIFICATION RESULTS"
    )
    print(
        "========================================"
    )

    for item in result[
        "verified_information"
    ]:
        print(item)

    assert result[
        "verified_information"
    ]

    for item in result[
        "verified_information"
    ]:

        assert "scheme_name" in item
        assert "section" in item
        assert "supported" in item
        assert "reason" in item

        assert "evidence" in item
        assert "metadata" in item
        assert "source_type" in item
        assert "source_url" in item
        assert "source_title" in item
        assert "trust_level" in item
        assert "trust_score" in item
        assert "trusted_source" in item


def test_verification_without_documents():

    state = {
        "query": "What assistance is available?",
        "retrieved_documents": [],
    }

    result = verification_agent.run(state)

    assert result[
        "verified_information"
    ] == []


def test_verification_without_query():

    state = {
        "query": "",
        "retrieved_documents": [],
    }

    result = verification_agent.run(state)

    assert result[
        "verified_information"
    ] == []

    assert result["errors"]


def test_low_trust_web_source_cannot_be_verified():

    state = {
        "query": (
            "Is this an official government scheme?"
        ),
        "retrieved_documents": [
            {
                "text": (
                    "This website claims that farmers "
                    "can receive financial assistance "
                    "under a government scheme."
                ),
                "metadata": {
                    "source_type": "web",
                    "title": "Private Scheme Website",
                    "url": "https://example.com/scheme",
                    "domain": "example.com",
                    "scheme_name": (
                        "Example Farmer Scheme"
                    ),
                    "section": "Benefits",
                    "trust_level": "low",
                    "trust_score": 0.4,
                    "trusted_source": False,
                },
            }
        ],
    }

    result = verification_agent.run(state)

    assert result[
        "verified_information"
    ]

    item = result[
        "verified_information"
    ][0]

    assert item["source_type"] == "web"
    assert item["trust_level"] == "low"
    assert item["trust_score"] == 0.4
    assert item["trusted_source"] is False

    assert item["evidence"]

    assert item[
        "source_url"
    ] == "https://example.com/scheme"

    assert item[
        "source_title"
    ] == "Private Scheme Website"

    # Critical safety rule:
    # LOW-trust web sources cannot independently
    # verify an official government scheme.
    assert item["supported"] is False


def test_high_trust_web_source_can_be_verified():

    state = {
        "query": (
            "What agricultural assistance is available "
            "for farmers?"
        ),
        "retrieved_documents": [
            {
                "text": (
                    "Eligible farmers receive financial "
                    "assistance for installing irrigation "
                    "systems."
                ),
                "metadata": {
                    "source_type": "web",
                    "title": (
                        "Agriculture Department Schemes"
                    ),
                    "url": (
                        "https://perambalur.nic.in/"
                        "agriculture-department-schemes"
                    ),
                    "domain": "perambalur.nic.in",
                    "scheme_name": (
                        "Per Drop More Crop"
                    ),
                    "section": "Benefits",
                    "trust_level": "high",
                    "trust_score": 1.0,
                    "trusted_source": True,
                },
            }
        ],
    }

    result = verification_agent.run(state)

    assert result[
        "verified_information"
    ]

    item = result[
        "verified_information"
    ][0]

    assert item["source_type"] == "web"
    assert item["trust_level"] == "high"
    assert item["trust_score"] == 1.0
    assert item["trusted_source"] is True

    assert item["supported"] is True

    assert item["evidence"]

    assert item[
        "source_url"
    ] == (
        "https://perambalur.nic.in/"
        "agriculture-department-schemes"
    )

    assert item[
        "source_title"
    ] == "Agriculture Department Schemes"