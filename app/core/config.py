"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration with safe development defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Betting Platform", min_length=1)
    app_env: str = Field(default="development", min_length=1)
    log_level: str = Field(default="INFO", min_length=1)
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://betting:betting@localhost:5432/betting"
    redis_url: str = "redis://localhost:6379/0"
    odds_api_key: str | None = None
    telegram_bot_token: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide configuration snapshot."""

    return Settings()
