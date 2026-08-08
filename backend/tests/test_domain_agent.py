from app.agents.domain_agent import domain_agent


def test_agriculture_domain():

    domain = domain_agent.classify(
        "What financial assistance is available for farmers?"
    )

    print("\nDomain:", domain)

    assert domain == "agriculture"


def test_education_domain():

    domain = domain_agent.classify(
        "What scholarships are available for students?"
    )

    print("\nDomain:", domain)

    assert domain == "education"


def test_healthcare_domain():

    domain = domain_agent.classify(
        "What health insurance schemes are available?"
    )

    print("\nDomain:", domain)

    assert domain == "healthcare"


def test_general_domain():

    domain = domain_agent.classify(
        "How do I repair a car engine?"
    )

    print("\nDomain:", domain)

    assert domain == "general"


def test_empty_query():

    domain = domain_agent.classify("")

    assert domain == "general"