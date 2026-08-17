from openai import OpenAI
from app.core.settings import settings


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.navigate_client = OpenAI(
            api_key=settings.NAVIGATE_API_KEY or settings.OPENAI_API_KEY,
            base_url=settings.NAVIGATE_BASE_URL or settings.OPENAI_BASE_URL,
        )
 
    def get_chat_model(self):
        return settings.LLM_MODEL

    def get_embedding_model(self):
        return settings.EMBEDDING_MODEL


openai_service = OpenAIService()