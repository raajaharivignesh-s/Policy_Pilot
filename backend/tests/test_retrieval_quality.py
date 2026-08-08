from app.rag.retriever import retriever


def print_results(title: str, results):
    print(f"\n{'=' * 60}")
    print(title)
    print(f"{'=' * 60}")

    for index, result in enumerate(results, start=1):
        print(
            f"\n{index}. "
            f"{result.metadata.get('scheme_name', 'Unknown')}"
        )
        print(
            f"   Domain: "
            f"{result.metadata.get('domain', 'Unknown')}"
        )
        print(
            f"   Section: "
            f"{result.metadata.get('section', 'Unknown')}"
        )
        print(
            f"   Distance: {result.distance}"
        )


def test_agriculture_retrieval_quality():

    query = "What financial assistance is available for farmers?"

    results = retriever.retrieve(
        query=query,
        top_k=5,
    )

    assert results

    print_results(
        "AGRICULTURE RETRIEVAL",
        results,
    )

    agriculture_results = [
        result
        for result in results
        if result.metadata.get("domain") == "agriculture"
    ]

    assert agriculture_results


def test_education_retrieval_quality():

    query = "What scholarships and financial assistance are available for students?"

    results = retriever.retrieve(
        query=query,
        top_k=5,
    )

    assert results

    print_results(
        "EDUCATION RETRIEVAL",
        results,
    )

    education_results = [
        result
        for result in results
        if result.metadata.get("domain") == "education"
    ]

    assert education_results


def test_healthcare_retrieval_quality():

    query = "What healthcare assistance is available in Tamil Nadu?"

    results = retriever.retrieve(
        query=query,
        top_k=5,
    )

    assert results

    print_results(
        "HEALTHCARE RETRIEVAL",
        results,
    )

    healthcare_results = [
        result
        for result in results
        if result.metadata.get("domain") == "healthcare"
    ]

    assert healthcare_results


def test_unrelated_query():

    query = "How do I repair a car engine?"

    results = retriever.retrieve(
        query=query,
        top_k=5,
    )

    print_results(
        "UNRELATED QUERY",
        results,
    )

    assert results == []