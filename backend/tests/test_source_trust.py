from app.services.source_trust_service import (
    source_trust_service,
)


def test_official_government_domain():

    result = source_trust_service.evaluate(
        "https://www.india.gov.in/"
    )

    assert result["trust_level"] == "high"
    assert result["trust_score"] == 1.0
    assert result["trusted_source"] is True


def test_tamil_nadu_government_domain():

    result = source_trust_service.evaluate(
        "https://agriculture.tn.gov.in/"
    )

    assert result["trust_level"] == "high"
    assert result["trust_score"] == 1.0
    assert result["trusted_source"] is True


def test_nic_subdomain():

    result = source_trust_service.evaluate(
        "https://perambalur.nic.in/"
    )

    assert result["trust_level"] == "high"
    assert result["trust_score"] == 1.0
    assert result["trusted_source"] is True


def test_government_subdomain():

    result = source_trust_service.evaluate(
        "https://example.gov.in/schemes"
    )

    assert result["trust_level"] == "high"
    assert result["trusted_source"] is True


def test_government_lookalike_domain_is_not_trusted():

    result = source_trust_service.evaluate(
        "https://gov.in.example.com/scheme"
    )

    assert result["trust_level"] == "low"
    assert result["trusted_source"] is False


def test_nic_lookalike_domain_is_not_trusted():

    result = source_trust_service.evaluate(
        "https://nic.in.example.com/"
    )

    assert result["trust_level"] == "low"
    assert result["trusted_source"] is False


def test_private_domain_is_low_trust():

    result = source_trust_service.evaluate(
        "https://example.com/scheme"
    )

    assert result["trust_level"] == "low"
    assert result["trust_score"] == 0.4
    assert result["trusted_source"] is False


def test_reuters_is_medium_trust():

    result = source_trust_service.evaluate(
        "https://www.reuters.com/world/india/"
    )

    assert result["trust_level"] == "medium"
    assert result["trust_score"] == 0.7
    assert result["trusted_source"] is False


def test_news_subdomain_is_medium_trust():

    result = source_trust_service.evaluate(
        "https://india.thehindu.com/"
    )

    assert result["trust_level"] == "medium"
    assert result["trust_score"] == 0.7
    assert result["trusted_source"] is False


def test_academic_domain_is_medium_trust():

    result = source_trust_service.evaluate(
        "https://university.ac.in/"
    )

    assert result["trust_level"] == "medium"
    assert result["trust_score"] == 0.7
    assert result["trusted_source"] is False


def test_edu_domain_is_medium_trust():

    result = source_trust_service.evaluate(
        "https://example.edu/"
    )

    assert result["trust_level"] == "medium"
    assert result["trust_score"] == 0.7
    assert result["trusted_source"] is False


def test_youtube_is_low_trust():

    result = source_trust_service.evaluate(
        "https://www.youtube.com/watch?v=test"
    )

    assert result["trust_level"] == "low"
    assert result["trust_score"] == 0.2
    assert result["trusted_source"] is False


def test_facebook_is_low_trust():

    result = source_trust_service.evaluate(
        "https://www.facebook.com/example"
    )

    assert result["trust_level"] == "low"
    assert result["trust_score"] == 0.2
    assert result["trusted_source"] is False


def test_empty_url():

    result = source_trust_service.evaluate("")

    assert result["domain"] == ""
    assert result["trust_level"] == "low"
    assert result["trusted_source"] is False


def test_invalid_url():

    result = source_trust_service.evaluate(
        "not-a-valid-url"
    )

    assert result["domain"] == ""
    assert result["trust_level"] == "low"
    assert result["trusted_source"] is False


def test_domain_extraction():

    domain = source_trust_service.get_domain(
        "https://www.perambalur.nic.in/agriculture"
    )

    assert domain == "www.perambalur.nic.in"