from app.services.vector_service import vector_service


def test_no_unknown_vectors():

    collection = (
        vector_service.get_or_create_collection()
    )

    result = collection.get(
        include=[
            "metadatas",
            "documents",
        ]
    )

    ids = result.get(
        "ids",
        [],
    )

    metadatas = result.get(
        "metadatas",
        [],
    )

    documents = result.get(
        "documents",
        [],
    )

    invalid_vectors = []

    for index, metadata in enumerate(
        metadatas
    ):

        metadata = metadata or {}

        scheme_name = str(
            metadata.get(
                "scheme_name",
                "",
            )
        ).strip()

        if (
            not scheme_name
            or scheme_name.upper() == "UNKNOWN"
        ):

            invalid_vectors.append(
                {
                    "id": ids[index],
                    "metadata": metadata,
                    "document": documents[index],
                }
            )

    print("\n")
    print("=" * 80)
    print("VECTOR DATABASE VALIDATION")
    print("=" * 80)

    print(
        "\nTotal vectors:",
        len(ids),
    )

    print(
        "Invalid vectors:",
        len(invalid_vectors),
    )

    for index, item in enumerate(
        invalid_vectors,
        start=1,
    ):

        print("\n" + "-" * 80)

        print(
            f"{index}. ID: {item['id']}"
        )

        print(
            "Metadata:",
            item["metadata"],
        )

        print(
            "Document:",
            item["document"][:500],
        )

    print("\n" + "=" * 80)

    assert len(invalid_vectors) == 0