from app.graph.workflow import policy_pilot_workflow


def test_full_workflow_with_web_search():

    print("\n========================================")
    print("FULL WORKFLOW → WEB SEARCH")
    print("========================================")

    state = {
        "query": (
            "What are the latest government schemes "
            "announced for farmers in Tamil Nadu in 2026?"
        ),
        "user_profile": {},
    }

    result = policy_pilot_workflow.invoke(
        state
    )

    print("\nIntent:")
    print(
        result.get(
            "intent",
            "",
        )
    )

    print("\nDomain:")
    print(
        result.get(
            "domain",
            "",
        )
    )

    documents = result.get(
        "retrieved_documents",
        [],
    )

    print(
        f"\nRetrieved Documents: {len(documents)}"
    )

    for index, document in enumerate(
        documents,
        start=1,
    ):
        metadata = document.get(
            "metadata",
            {},
        )

        print(f"\nDOCUMENT {index}")

        print(
            "Source Type:",
            metadata.get(
                "source_type",
                "",
            ),
        )

        print(
            "Title:",
            metadata.get(
                "title",
                metadata.get(
                    "scheme_name",
                    "",
                ),
            ),
        )

        print(
            "URL:",
            metadata.get(
                "url",
                "",
            ),
        )

        print(
            "Trusted:",
            metadata.get(
                "trusted_source",
                False,
            ),
        )

    print("\nVerified Information:")
    print(
        result.get(
            "verified_information",
            [],
        )
    )

    print("\nRecommendations:")
    print(
        result.get(
            "recommendations",
            [],
        )
    )

    print("\nFinal Response:")
    print(
        result.get(
            "final_response",
            "",
        )
    )

    print("\nErrors:")
    print(
        result.get(
            "errors",
            [],
        )
    )

    assert result.get(
        "intent"
    )

    assert result.get(
        "domain"
    )

    assert len(documents) > 0

    web_documents = [
        document
        for document in documents
        if document.get(
            "metadata",
            {},
        ).get(
            "source_type"
        ) == "web"
    ]

    assert len(web_documents) > 0