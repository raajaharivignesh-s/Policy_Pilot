from app.services.vector_service import vector_service


TEST_VECTOR_IDS = [
    "test_education_001",
    "test_agriculture_001",
    "test_healthcare_001",
]


def test_remove_test_vectors():

    collection = (
        vector_service.get_or_create_collection()
    )

    # --------------------------------------------------
    # Check which test vectors actually exist
    # --------------------------------------------------

    existing = collection.get(
        ids=TEST_VECTOR_IDS,
        include=[
            "metadatas",
        ],
    )

    existing_ids = existing.get(
        "ids",
        [],
    )

    print("\n")
    print("=" * 80)
    print("TEST VECTOR CLEANUP")
    print("=" * 80)

    print(
        "\nExisting test vectors:",
        len(existing_ids),
    )

    for vector_id in existing_ids:
        print(
            f" - {vector_id}"
        )

    # --------------------------------------------------
    # Delete ONLY the known test vectors
    # --------------------------------------------------

    if existing_ids:

        collection.delete(
            ids=existing_ids
        )

    # --------------------------------------------------
    # Verify deletion
    # --------------------------------------------------

    remaining = collection.get(
        ids=TEST_VECTOR_IDS,
        include=[
            "metadatas",
        ],
    )

    remaining_ids = remaining.get(
        "ids",
        [],
    )

    print(
        "\nRemaining test vectors:",
        len(remaining_ids),
    )

    print(
        "\nTotal vectors after cleanup:",
        collection.count(),
    )

    print("\n" + "=" * 80)

    assert remaining_ids == []