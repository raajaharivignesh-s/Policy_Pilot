from app.services.search_service import search_service


def test_search_service_configuration():

    print("\n========================================")
    print("TAVILY SEARCH SERVICE")
    print("========================================")

    print(
        "Configured:",
        search_service.is_available(),
    )

    assert search_service is not None