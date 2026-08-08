from app.services.embedding_service import embedding_service
from app.services.vector_service import vector_service


def test_vector_storage_and_search():
    documents = [
        "Students from eligible families can receive educational financial assistance.",
        "Farmers may receive financial support through eligible agriculture schemes.",
        "Eligible citizens can receive healthcare assistance under government schemes.",
    ]

    metadatas = [
        {
            "domain": "education",
            "source": "test",
        },
        {
            "domain": "agriculture",
            "source": "test",
        },
        {
            "domain": "healthcare",
            "source": "test",
        },
    ]

    ids = [
        "test_education_001",
        "test_agriculture_001",
        "test_healthcare_001",
    ]

    embeddings = embedding_service.generate_embeddings(documents)

    assert len(embeddings) == len(documents)
    assert len(embeddings[0]) == 1536

    vector_service.add_documents(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    assert vector_service.count() >= 3

    query = "What government assistance is available for students?"

    query_embedding = embedding_service.generate_embedding(query)

    results = vector_service.search(
        query_embedding=query_embedding,
        n_results=2,
    )

    assert results["documents"]
    assert len(results["documents"][0]) > 0

    print("\nQuery:")
    print(query)

    print("\nRetrieved documents:")

    for document in results["documents"][0]:
        print("-", document)