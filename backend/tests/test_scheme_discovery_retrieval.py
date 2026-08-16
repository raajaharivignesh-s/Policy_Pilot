from app.rag.retriever import retriever


def test_scheme_discovery_retrieval():

    query = (
        "What are the scheme for Tamil Nadu students"
    )

    print("\n")
    print("=" * 80)
    print("SCHEME DISCOVERY RETRIEVAL")
    print("=" * 80)

    results = retriever.retrieve(
        query=query,
        top_k=15,
    )

    print(
        f"\nRetrieved results: {len(results)}"
    )

    print("\n")
    print("-" * 80)

    for index, result in enumerate(
        results,
        start=1,
    ):

        metadata = result.metadata

        print(
            f"\n{index}. "
            f"{metadata.get('scheme_name', 'UNKNOWN')}"
        )

        print(
            f"   Section: "
            f"{metadata.get('section', 'UNKNOWN')}"
        )

        print(
            f"   Domain: "
            f"{metadata.get('domain', 'UNKNOWN')}"
        )

        print(
            f"   Distance: "
            f"{result.distance}"
        )

        print(
            f"   Chunk ID: "
            f"{metadata.get('source_file', 'UNKNOWN')}"
        )

    print("\n")
    print("=" * 80)

    unique_schemes = []

    for result in results:

        scheme_name = result.metadata.get(
            "scheme_name"
        )

        if (
            scheme_name
            and scheme_name not in unique_schemes
        ):
            unique_schemes.append(
                scheme_name
            )

    print(
        f"\nUnique schemes retrieved: "
        f"{len(unique_schemes)}"
    )

    for index, scheme in enumerate(
        unique_schemes,
        start=1,
    ):
        print(
            f"{index}. {scheme}"
        )

    print("\n")
    print("=" * 80)

    assert results