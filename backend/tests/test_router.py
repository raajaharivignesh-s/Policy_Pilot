from app.graph.router import route_after_verification


def test_eligibility_route():

    state = {
        "intent": "eligibility_check",
    }

    result = route_after_verification(state)

    assert result == "eligibility_agent"


def test_scheme_discovery_route():

    state = {
        "intent": "scheme_discovery",
    }

    result = route_after_verification(state)

    assert result == "recommendation_agent"


def test_general_query_route():

    state = {
        "intent": "general_query",
    }

    result = route_after_verification(state)

    assert result == "final_response_agent"