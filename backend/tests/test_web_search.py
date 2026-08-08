from app.services.search_service import search_service


def test_live_tavily_search():

    print("\n========================================")
    print("TAVILY LIVE WEB SEARCH")
    print("========================================")

    assert search_service.is_available(), (
        "Tavily is not configured."
    )

    results = search_service.search(
        query="Tamil Nadu government schemes for farmers",
        max_results=5,
    )

    print(f"\nResults found: {len(results)}\n")

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(f"RESULT {index}")
        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Score:", result["score"])
        print("Content:", result["content"][:500])
        print("-" * 60)

    assert len(results) > 0

    for result in results:
        assert result["title"]
        assert result["url"]
        assert result["content"]