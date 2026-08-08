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