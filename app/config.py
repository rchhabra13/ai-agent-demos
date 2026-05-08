from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:8000/auth/github/callback"

    # Redis
    redis_url: str = "redis://redis:6379"

    # Session
    session_secret_key: str = "dev-secret-key-change-in-production"
    session_ttl_seconds: int = 3600

    # LLM (OpenAI-compatible)
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o"

    # Rate limiting
    rate_limit_requests: int = 500
    rate_limit_window_seconds: int = 60

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/app.db"


settings = Settings()
