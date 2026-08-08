from app.rag.rag_service import rag_service


def test_rag_agriculture_question():

    query = (
        "What financial assistance is available "
        "for farmers?"
    )

    result = rag_service.answer(
        query=query,
        top_k=5,
    )

    print("\n========================================")
    print("RAG QUESTION")
    print("========================================")
    print(query)

    print("\n========================================")
    print("RAG ANSWER")
    print("========================================")
    print(result.answer)

    print("\n========================================")
    print("SOURCES")
    print("========================================")

    for document in result.documents:

        print(
            f"- "
            f"{document.metadata.get('scheme_name')} "
            f"→ "
            f"{document.metadata.get('section')}"
        )

    assert result.has_context is True

    assert result.answer

    assert len(result.documents) > 0


def test_rag_unknown_question():

    query = (
        "How do I repair a car engine?"
    )

    result = rag_service.answer(
        query=query,
        top_k=5,
    )

    print("\n========================================")
    print("UNKNOWN QUESTION")
    print("========================================")
    print(result.answer)

    assert result.has_context is False

    assert result.documents == []

    assert result.answer


def test_rag_empty_question():

    result = rag_service.answer(
        query="",
    )

    assert result.has_context is False

    assert result.documents == []

    assert result.answer