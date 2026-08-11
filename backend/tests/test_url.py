from app.agents.recommendation_agent import recommendation_agent

result = recommendation_agent.run(
    {
        "verified_information": [
            {
                "scheme_name": "PM-KISAN",
                "section": "Benefits",
                "supported": True,
                "reason": "Financial assistance for eligible farmers.",
                "source_url": "https://pmkisan.gov.in/",
            }
        ]
    }
)

print(result)