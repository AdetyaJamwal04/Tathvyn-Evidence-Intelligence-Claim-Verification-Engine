"""Application Configuration Management.

Utilizes pydantic-settings to load, validate, and type-check environment variables
with default fallbacks for local development and testing.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration settings for VeriFact."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="Tathvyn_",
        extra="ignore",
    )

    # Core Application Environment
    environment: Literal["development", "testing", "staging", "production"] = "development"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    app_version: str = "0.1.0"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    # Database (PostgreSQL 16 with pgvector)
    database_url: str = Field(
        default="postgresql+asyncpg://Tathvyn:verifact_secret@localhost:5432/verifact_db",
        description="Async SQLAlchemy database connection URI",
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis (Caching & Task Queues)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for cache and streams",
    )

    # Search Provider Keys (Read with or without Tathvyn_ prefix)
    tavily_api_key: SecretStr = Field(default=SecretStr(""), alias="TAVILY_API_KEY")
    brave_search_api_key: SecretStr = Field(default=SecretStr(""), alias="BRAVE_SEARCH_API_KEY")

    # Hosted LLM Reasoning API Keys
    gemini_api_key: SecretStr = Field(default=SecretStr(""), alias="GEMINI_API_KEY")
    anthropic_api_key: SecretStr = Field(default=SecretStr(""), alias="ANTHROPIC_API_KEY")
    openai_api_key: SecretStr = Field(default=SecretStr(""), alias="OPENAI_API_KEY")
    llm_provider: str = Field(default="gemini", description="'gemini', 'openai', 'anthropic', or 'mock'")
    llm_model_name: str = Field(default="gemini-2.0-flash", description="Model name for reasoning/synthesis")

    # Local ML Model Settings
    device: str = Field(default="cpu", description="'cpu', 'cuda', or 'directml'")
    model_cache_dir: str = "~/.cache/huggingface/hub"
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    nli_model_name: str = "cross-encoder/nli-distilroberta-base"

    # Verification Budget & Latency Default Caps
    default_max_search_queries: int = 12
    default_max_cost_usd: float = 0.05
    max_search_queries_per_claim: int = 12
    max_document_fetch_timeout_seconds: float = 8.0
    max_claim_verification_timeout_seconds: float = 25.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton instance of loaded application settings."""
    return Settings()
