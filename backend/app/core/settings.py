from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "PolicyPilot AI"
    APP_VERSION: str = "1.0.0"

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    LLM_MODEL: str = "gpt-4.1-nano"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    DATABASE_URL: str = ""
    CHROMA_DB_PATH: str = "./storage/chroma_db"
    TAVILY_API_KEY: str = ""

    # ==========================================
    # Voice AI (WebSocket Streaming)
    # ==========================================
    VOICE_STT_MODEL: str = "whisper-1"
    VOICE_TTS_MODEL: str = "gpt-4o-mini-tts"
    VOICE_TTS_VOICE: str = "nova"
    # Sentence min chars before TTS starts streaming
    VOICE_TTS_SENTENCE_MIN_CHARS: int = 18

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()