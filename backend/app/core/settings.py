from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "PolicyPilot AI"
    APP_VERSION: str = "1.0.0"

    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str

    LLM_MODEL: str = "gpt-4.1-nano"

    EMBEDDING_MODEL: str = "text-embedding-3-small"

    DATABASE_URL: str = ""

    CHROMA_DB_PATH: str = "./storage/chroma_db"

    TAVILY_API_KEY: str = ""

    JWT_SECRET_KEY: str = "super_secret_key_change_me_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()