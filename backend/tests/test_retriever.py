from app.rag.retriever import retriever


def test_retrieval_for_agriculture():

    query = (
        "What financial assistance is available "
        "for farmers?"
    )

    results = retriever.retrieve(
        query=query,
        top_k=5,
    )

    assert results

    print("\n========================================")
    print("Agriculture Query:")
    print(query)
    print("========================================")

    for index, result in enumerate(results, start=1):

        print(f"\nResult {index}")
        print("----------------------------------------")

        print(
            "Scheme:",
            result.metadata.get(
                "scheme_name",
                "Unknown",
            ),
        )

        print(
            "Section:",
            result.metadata.get(
                "section",
                "Unknown",
            ),
        )

        print(
            "Domain:",
            result.metadata.get(
                "domain",
                "Unknown",
            ),
        )

        print(
            "Distance:",
            result.distance,
        )

        print("Text:")
        print(result.text)


def test_retrieval_for_education():

    query = (
        "What financial assistance is available "
        "for students?"
    )

    results = retriever.retrieve(
        query=query,
        top_k=5,
    )

    assert results

    print("\n========================================")
    print("Education Query:")
    print(query)
    print("========================================")

    for index, result in enumerate(results, start=1):

        print(
            f"{index}. "
            f"{result.metadata.get('scheme_name')} "
            f"→ "
            f"{result.metadata.get('section')}"
        )

    assert any(
        result.metadata.get("domain") == "education"
        for result in results
    )


def test_retrieval_for_healthcare():

    query = (
        "What healthcare assistance is available "
        "in Tamil Nadu?"
    )

    results = retriever.retrieve(
        query=query,
        top_k=5,
    )

    assert results

    print("\n========================================")
    print("Healthcare Query:")
    print(query)
    print("========================================")

    for index, result in enumerate(results, start=1):

        print(
            f"{index}. "
            f"{result.metadata.get('scheme_name')} "
            f"→ "
            f"{result.metadata.get('section')}"
        )

    assert any(
        result.metadata.get("domain") == "healthcare"
        for result in results
    )