from app.graph.nodes import initialize_state


def test_initialize_state():

    state = {
        "query": "  What schemes are available for farmers?  ",
    }

    result = initialize_state(state)

    assert result["query"] == (
        "What schemes are available for farmers?"
    )

    assert result["intent"] == ""

    assert result["domain"] == ""

    assert result["retrieved_documents"] == []

    assert result["verified_information"] == []

    assert result["eligibility_results"] == []

    assert result["recommendations"] == []

    assert result["required_documents"] == []

    assert result["final_response"] == ""

    assert result["needs_clarification"] is False

    assert result["clarification_question"] == ""

    assert result["errors"] == []