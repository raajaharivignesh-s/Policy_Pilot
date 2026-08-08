from app.graph.state import PolicyPilotState


def test_policy_pilot_state():

    state: PolicyPilotState = {
        "query": "What schemes are available for farmers?",
        "user_profile": {
            "age": 45,
            "occupation": "farmer",
            "income": 200000,
            "district": "Erode",
        },
        "intent": "scheme_discovery",
        "domain": "agriculture",
        "retrieved_documents": [],
        "verified_information": [],
        "eligibility_results": [],
        "recommendations": [],
        "required_documents": [],
        "final_response": "",
        "needs_clarification": False,
        "clarification_question": "",
        "errors": [],
    }

    assert state["query"]

    assert state["domain"] == "agriculture"

    assert state["user_profile"]["occupation"] == "farmer"

    assert state["retrieved_documents"] == []

    assert state["eligibility_results"] == []

    assert state["recommendations"] == []

    assert state["needs_clarification"] is False