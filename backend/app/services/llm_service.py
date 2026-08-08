from typing import Any

from app.services.openai_service import openai_service


class LLMService:
    """
    Service responsible for text generation using
    the configured LLM.
    """

    def __init__(self):
        self.client = openai_service.client
        self.model = openai_service.get_chat_model()

    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        **kwargs: Any,
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            **kwargs,
        )

        return response.choices[0].message.content or ""


llm_service = LLMService()