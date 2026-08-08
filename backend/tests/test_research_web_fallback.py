from app.agents.research_agent import ResearchAgent


def test_research_web_fallback():

    print("\n========================================")
    print("RESEARCH AGENT → WEB FALLBACK")
    print("========================================")

    agent = ResearchAgent()

    state = {
    "query": (
        "What are the latest government schemes "
        "announced for farmers in Tamil Nadu in 2026?"
    ),
    "domain": "agriculture",
}

    result = agent.run(state)

    documents = result.get(
        "retrieved_documents",
        [],
    )

    print(
        f"\nRetrieved documents: {len(documents)}"
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
            "Source type:",
            metadata.get(
                "source_type"
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

    assert isinstance(
        documents,
        list,
    )