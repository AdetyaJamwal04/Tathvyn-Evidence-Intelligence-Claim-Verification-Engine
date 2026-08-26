"""Tests for Application Configuration and Logging Setup."""

from pydantic import SecretStr

from tathvyn.common.config import Settings, get_settings
from tathvyn.common.logging import get_logger, setup_logging


def test_default_settings() -> None:
    """Verify default configuration values."""
    settings = Settings()
    assert settings.environment == "development"
    assert settings.port == 8000
    assert "postgresql+asyncpg" in settings.database_url
    assert "redis://" in settings.redis_url
    assert settings.default_max_search_queries == 12
    assert settings.default_max_cost_usd == 0.05


def test_settings_singleton() -> None:
    """Verify get_settings returns identical cached instance."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_secret_str_handling() -> None:
    """Verify API keys are wrapped in SecretStr to prevent leak."""
    settings = Settings(TAVILY_API_KEY=SecretStr("super-secret-key"))
    assert settings.tavily_api_key.get_secret_value() == "super-secret-key"
    assert "super-secret-key" not in str(settings.tavily_api_key)


def test_logging_setup() -> None:
    """Verify logging setup initializes without error."""
    setup_logging(log_level="DEBUG", json_output=True)
    logger = get_logger("test_component")
    assert logger is not None
