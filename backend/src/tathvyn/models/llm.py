"""Unified LLM Client Interface and Provider Implementations.

Supports Google Gemini (via google-genai), OpenAI, and deterministic Mock client
for offline testing and development.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

from tathvyn.common.config import Settings, get_settings
from tathvyn.common.exceptions import ProviderError
from tathvyn.common.logging import get_logger

logger = get_logger("llm_client")

T = TypeVar("T", bound=BaseModel)


class BaseLLMClient(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.0,
    ) -> str:
        """Generate unstructured text response from LLM."""
        ...

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        temperature: float = 0.0,
    ) -> T:
        """Generate structured Pydantic response from LLM."""
        ...


class GeminiLLMClient(BaseLLMClient):
    """Google Gemini LLM client using official google-genai SDK."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash",
    ) -> None:
        self.api_key = api_key
        self.model_name = model_name
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from google import genai

                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error("failed_to_initialize_gemini_client", error=str(e))
                raise ProviderError("gemini", f"Failed to initialize Gemini client: {e}") from e
        return self._client

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.0,
    ) -> str:
        client = self._get_client()
        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction,
            )
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            return str(response.text or "").strip()
        except Exception as e:
            logger.error("gemini_text_generation_failed", error=str(e), model=self.model_name)
            raise ProviderError("gemini", f"Gemini generation error: {e}") from e

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        temperature: float = 0.0,
    ) -> T:
        client = self._get_client()
        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=response_schema,
            )
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            raw_json = response.text or "{}"
            parsed_data = json.loads(raw_json)
            return response_schema.model_validate(parsed_data)
        except Exception as e:
            logger.error(
                "gemini_structured_generation_failed",
                error=str(e),
                schema=response_schema.__name__,
            )
            raise ProviderError("gemini", f"Gemini structured output error: {e}") from e


class MockLLMClient(BaseLLMClient):
    """Deterministic Mock LLM client for testing and offline development."""

    def __init__(self, model_name: str = "mock-llm") -> None:
        self.model_name = model_name

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.0,
    ) -> str:
        return f"Mock response for prompt: {prompt[:50]}..."

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
        temperature: float = 0.0,
    ) -> T:
        # Generate default instance for schema
        try:
            return response_schema.model_validate({})
        except Exception:
            # Fallback with dummy values if fields are required
            fields = response_schema.model_fields
            dummy_data: dict[str, Any] = {}
            for k, field_info in fields.items():
                annotation = str(field_info.annotation)
                if "list" in annotation.lower():
                    dummy_data[k] = []
                elif "int" in annotation.lower():
                    dummy_data[k] = 0
                elif "float" in annotation.lower():
                    dummy_data[k] = 0.0
                elif "bool" in annotation.lower():
                    dummy_data[k] = False
                else:
                    dummy_data[k] = "mock_value"
            return response_schema.model_validate(dummy_data)


def get_llm_client(settings: Settings | None = None) -> BaseLLMClient:
    """Factory creating appropriate LLM client based on application configuration."""
    cfg = settings or get_settings()

    gemini_key = cfg.gemini_api_key.get_secret_value()

    if (cfg.llm_provider == "gemini" or not cfg.llm_provider) and gemini_key:
        return GeminiLLMClient(
            api_key=gemini_key,
            model_name=cfg.llm_model_name if "gemini" in cfg.llm_model_name else "gemini-2.0-flash",
        )

    if gemini_key:
        return GeminiLLMClient(api_key=gemini_key, model_name="gemini-2.0-flash")

    logger.debug("no_hosted_llm_key_found_using_mock_client")
    return MockLLMClient()
