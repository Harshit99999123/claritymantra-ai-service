from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str
    app_version: str
    service_name: str
    environment: str
    api_prefix: str
    log_level: str
    ollama_base_url: AnyHttpUrl
    ollama_model: str
    embedding_model: str
    vector_store_path: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
