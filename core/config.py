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
    ollama_keep_alive: str
    chat_temperature: float
    chat_max_tokens: int
    insight_model: str
    insight_max_tokens: int
    enable_source_quote_formatting: bool
    source_quote_format_model: str
    source_quote_format_max_tokens: int
    source_quote_format_cache_path: str
    enable_query_rewrite: bool
    query_rewrite_model: str
    query_rewrite_max_tokens: int
    embedding_provider: str
    embedding_model: str
    vector_store_provider: str
    active_book_slug: str
    retrieval_top_k: int
    retrieval_context_token_limit: int
    retrieval_candidate_pool: int
    vector_store_path: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
