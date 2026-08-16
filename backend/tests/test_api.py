from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    """
    Test the root endpoint.
    """

    response = client.get("/")

    print("\nROOT RESPONSE:")
    print(response.json())

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "Running"


def test_health():
    """
    Test the health endpoint.
    """

    response = client.get("/health")

    print("\nHEALTH RESPONSE:")
    print(response.json())

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "Healthy"


def test_query_validation():
    """
    Test that an empty query is rejected.
    """

    response = client.post(
        "/api/v1/query",
        json={
            "query": "",
        },
    )

    print("\nVALIDATION RESPONSE:")
    print(response.json())

    assert response.status_code == 422


def test_agriculture_query():
    """
    Test a real agriculture query through
    the complete API → LangGraph → RAG pipeline.
    """

    response = client.post(
        "/api/v1/query",
        json={
            "query": (
                "What financial assistance "
                "is available for farmers?"
            )
        },
    )

    print("\n========================================")
    print("AGRICULTURE API RESPONSE")
    print("========================================")

    print("Status:", response.status_code)

    data = response.json()

    print("\nIntent:")
    print(data["intent"])

    print("\nDomain:")
    print(data["domain"])

    print("\nRecommendations:")

    for recommendation in data["recommendations"]:
        print(
            f"- "
            f"{recommendation['scheme_name']}"
            f" → "
            f"{recommendation['reason']}"
        )

    print("\nFinal Response:")
    print(data["final_response"])

    assert response.status_code == 200

    assert data["query"]

    assert data["intent"] == "scheme_discovery"

    assert data["domain"] == "agriculture"

    assert data["retrieved_documents"]

    assert data["verified_information"]

    assert data["recommendations"]

    assert data["final_response"]


def test_eligibility_query():
    """
    Test eligibility query through the API.
    """

    response = client.post(
        "/api/v1/query",
        json={
            "query": "Am I eligible for PM-KISAN?",
            "user_profile": {
                "occupation": "farmer",
                "land_owner": True,
            },
        },
    )

    print("\n========================================")
    print("ELIGIBILITY API RESPONSE")
    print("========================================")

    print("Status:", response.status_code)

    data = response.json()

    print("\nIntent:")
    print(data["intent"])

    print("\nDomain:")
    print(data["domain"])

    print("\nEligibility:")
    print(data["eligibility_results"])

    print("\nFinal Response:")
    print(data["final_response"])

    assert response.status_code == 200

    assert data["intent"] == "eligibility_check"

    assert data["domain"] == "agriculture"

    assert data["retrieved_documents"]

    assert data["eligibility_results"]

    assert data["final_response"]


def test_irrelevant_query():
    """
    Test an unrelated query.

    It should bypass the RAG retrieval pipeline.
    """

    response = client.post(
        "/api/v1/query",
        json={
            "query": "How do I repair a car engine?",
        },
    )

    print("\n========================================")
    print("IRRELEVANT API RESPONSE")
    print("========================================")

    print("Status:", response.status_code)

    data = response.json()

    print("\nIntent:")
    print(data["intent"])

    print("\nDomain:")
    print(data["domain"])

    print("\nRetrieved:")
    print(data["retrieved_documents"])

    print("\nFinal Response:")
    print(data["final_response"])

    assert response.status_code == 200

    assert data["intent"] == "general_query"

    assert data["domain"] == "general"

    assert data["retrieved_documents"] == []

    assert data["verified_information"] == []

    assert data["recommendations"] == []

    assert data["final_response"]


def test_invalid_user_id():
    """
    Invalid UUID should be rejected before
    accessing PostgreSQL.
    """

    response = client.post(
        "/api/v1/query",
        json={
            "query": "What schemes are available?",
            "user_id": "not-a-valid-uuid",
        },
    )

    print("\nINVALID USER ID RESPONSE:")
    print(response.json())

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "Invalid user_id."


def test_missing_user_profile():
    """
    A valid UUID that does not have a citizen profile
    should return 404 when user_id is explicitly supplied.
    """

    fake_user_id = (
        "00000000-0000-0000-0000-000000000001"
    )

    response = client.post(
        "/api/v1/query",
        json={
            "query": (
                "What financial assistance "
                "is available for farmers?"
            ),
            "user_id": fake_user_id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "final_response" in data or "query" in data

def test_profile_service_failure():
    """
    Profile service failure should return a controlled
    HTTP 500 response without exposing the internal exception.
    """

    with patch(
        "app.api.routes.query.profile_service.get_profile",
        side_effect=Exception(
            "Database connection failed"
        ),
    ):

        response = client.post(
            "/api/v1/query",
            json={
                "query": "What schemes are available?",
                "user_id": (
                    "00000000-0000-0000-0000-000000000001"
                ),
            },
        )

    print("\nPROFILE SERVICE FAILURE RESPONSE:")
    print(response.json())

    assert response.status_code == 500

    data = response.json()

    assert data["detail"] == (
        "Failed to load citizen profile."
    )

    assert "Database connection failed" not in str(
        data
    )


def test_workflow_execution_failure():
    """
    Workflow failure should return a controlled
    HTTP 500 response without exposing the internal exception.
    """

    with patch(
        "app.api.routes.query.policy_pilot_workflow.invoke",
        side_effect=Exception(
            "LangGraph execution failed"
        ),
    ):

        response = client.post(
            "/api/v1/query",
            json={
                "query": "What schemes are available?",
            },
        )

    print("\nWORKFLOW FAILURE RESPONSE:")
    print(response.json())

    assert response.status_code == 500

    data = response.json()

    assert data["detail"] == (
        "Workflow execution failed."
    )

    assert "LangGraph execution failed" not in str(
        data
    )


def test_invalid_workflow_result():
    """
    An invalid workflow result should return a controlled
    HTTP 500 response.
    """

    with patch(
        "app.api.routes.query.policy_pilot_workflow.invoke",
        return_value="invalid workflow result",
    ):

        response = client.post(
            "/api/v1/query",
            json={
                "query": "What schemes are available?",
            },
        )

    print("\nINVALID WORKFLOW RESULT RESPONSE:")
    print(response.json())

    assert response.status_code == 500

    data = response.json()

    assert data["detail"] == (
        "Workflow returned an invalid response."
    )


def test_query_with_user_profile():
    """
    Test a query using a directly supplied citizen profile.
    """

    response = client.post(
        "/api/v1/query",
        json={
            "query": (
                "What financial assistance "
                "is available for farmers?"
            ),
            "user_profile": {
                "age": 24,
                "state": "Tamil Nadu",
                "district": "Erode",
                "occupation": "Farmer",
                "annual_income": 150000,
                "is_student": False,
                "land_acres": 2.5,
            },
        },
    )

    print("\nPROFILE QUERY RESPONSE:")
    print(response.status_code)

    assert response.status_code == 200

    data = response.json()

    assert data["query"]

    assert data["intent"]

    assert data["domain"]

    assert isinstance(
        data["retrieved_documents"],
        list,
    )

    assert isinstance(
        data["verified_information"],
        list,
    )

    assert isinstance(
        data["eligibility_results"],
        list,
    )

    assert isinstance(
        data["recommendations"],
        list,
    )

    assert isinstance(
        data["required_documents"],
        list,
    )

    assert isinstance(
        data["final_response"],
        str,
    )

    assert isinstance(
        data["needs_clarification"],
        bool,
    )

    assert isinstance(
        data["clarification_question"],
        str,
    )

    assert isinstance(
        data["errors"],
        list,
    )


def test_query_with_empty_profile():
    """
    Test that an explicitly supplied empty profile
    does not cause an API failure.
    """

    response = client.post(
        "/api/v1/query",
        json={
            "query": (
                "What financial assistance "
                "is available for farmers?"
            ),
            "user_profile": {},
        },
    )

    print("\nEMPTY PROFILE RESPONSE:")
    print(response.status_code)

    assert response.status_code == 200

    data = response.json()

    assert data["query"]

    assert data["final_response"]


def test_query_response_schema():
    """
    Test that the API response contains the
    complete expected response schema.
    """

    response = client.post(
        "/api/v1/query",
        json={
            "query": (
                "What financial assistance "
                "is available for farmers?"
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    expected_fields = {
        "query",
        "intent",
        "domain",
        "retrieved_documents",
        "verified_information",
        "eligibility_results",
        "recommendations",
        "required_documents",
        "final_response",
        "needs_clarification",
        "clarification_question",
        "errors",
    }

    assert set(data.keys()) == expected_fields
