from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"
    database_url: str = "sqlite:///./app/data/resume_screener.db"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_frontend_origins() -> list[str]:
    return [
        origin.strip()
        for origin in get_settings().frontend_origins.split(",")
        if origin.strip()
    ]
