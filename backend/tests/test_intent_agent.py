from app.agents.intent_agent import intent_agent


def test_scheme_discovery_intent():

    intent = intent_agent.classify(
        "What government schemes are available for farmers?"
    )

    print("\nIntent:", intent)

    assert intent == "scheme_discovery"


def test_eligibility_intent():

    intent = intent_agent.classify(
        "Am I eligible for PM-KISAN?"
    )

    print("\nIntent:", intent)

    assert intent == "eligibility_check"


def test_document_intent():

    intent = intent_agent.classify(
        "What documents are required for CMCHIS?"
    )

    print("\nIntent:", intent)

    assert intent == "document_query"


def test_application_intent():

    intent = intent_agent.classify(
        "How can I apply for PMFBY?"
    )

    print("\nIntent:", intent)

    assert intent == "application_process"


def test_scheme_information_intent():

    intent = intent_agent.classify(
        "What is the PM-KISAN scheme?"
    )

    print("\nIntent:", intent)

    assert intent == "scheme_information"


def test_general_query():

    intent = intent_agent.classify(
        "Hello"
    )

    print("\nIntent:", intent)

    assert intent == "general_query"


def test_empty_query():

    intent = intent_agent.classify("")

    assert intent == "general_query"