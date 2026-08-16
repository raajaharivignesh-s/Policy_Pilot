from app.services.vector_service import vector_service


def test_education_vectors():

    collection = vector_service.get_or_create_collection()

    result = collection.get(
        where={
            "domain": "education"
        },
        include=[
            "documents",
            "metadatas",
        ],
    )

    documents = result.get(
        "documents",
        [],
    )

    metadatas = result.get(
        "metadatas",
        [],
    )

    ids = result.get(
        "ids",
        [],
    )

    print("\n")
    print("=" * 80)
    print("EDUCATION VECTOR DATABASE")
    print("=" * 80)

    print(
        f"\nTotal education vectors: {len(ids)}"
    )

    schemes = {}

    for index, vector_id in enumerate(ids):

        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        document = (
            documents[index]
            if index < len(documents)
            else ""
        )

        scheme_name = metadata.get(
            "scheme_name",
            "UNKNOWN",
        )

        schemes.setdefault(
            scheme_name,
            [],
        ).append(
            {
                "id": vector_id,
                "section": metadata.get(
                    "section",
                    "UNKNOWN",
                ),
                "document": document,
            }
        )

    print("\nUnique schemes:")
    print("-" * 80)

    for index, scheme_name in enumerate(
        schemes,
        start=1,
    ):
        print(
            f"{index}. {scheme_name}"
        )

        print(
            f"   Chunks: "
            f"{len(schemes[scheme_name])}"
        )

        sections = [
            item["section"]
            for item in schemes[scheme_name]
        ]

        print(
            f"   Sections: "
            f"{sections}"
        )

    print("\n")
    print("=" * 80)

    expected_schemes = {
        "PUDHUMAI PENN SCHEME",
        "BC / MBC / DNC POST-MATRIC SCHOLARSHIP",
        "TAMIZH PUDHALVAN SCHEME",
        "SCHOLARSHIP FOR DIFFERENTLY ABLED STUDENTS",
        "MINORITY POST-MATRIC SCHOLARSHIP",
    }

    actual_schemes = set(
        schemes.keys()
    )

    print("Expected schemes:")
    for scheme in expected_schemes:
        print(f"  ✓ {scheme}")

    print("\nUnexpected schemes:")
    unexpected = (
        actual_schemes
        - expected_schemes
    )

    if unexpected:
        for scheme in unexpected:
            print(f"  ✗ {scheme}")
    else:
        print("  None")

    print("\n")
    print(
        f"Expected unique schemes: "
        f"{len(expected_schemes)}"
    )

    print(
        f"Actual unique schemes: "
        f"{len(actual_schemes)}"
    )

    print("=" * 80)

    assert expected_schemes.issubset(
        actual_schemes
    )