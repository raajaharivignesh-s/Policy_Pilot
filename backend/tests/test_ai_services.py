from app.services.llm_service import llm_service
from app.services.embedding_service import embedding_service


def test_llm_service():
    messages = [
        {
            "role": "user",
            "content": "Say exactly: PolicyPilot AI is working."
        }
    ]

    response = llm_service.generate(
        messages=messages,
        temperature=0,
    )

    assert response
    print("\nLLM Response:")
    print(response)


def test_embedding_service():
    text = "Tamil Nadu government schemes for students."

    embedding = embedding_service.generate_embedding(text)

    assert embedding
    assert isinstance(embedding, list)
    assert len(embedding) > 0

    print("\nEmbedding Dimensions:")
    print(len(embedding))