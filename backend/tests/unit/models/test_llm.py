"""Unit Tests for Unified LLM Client and Google Gemini Integration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, SecretStr

from tathvyn.common.config import Settings
from tathvyn.common.exceptions import ProviderError
from tathvyn.models.llm import (
    BaseLLMClient,
    GeminiLLMClient,
    MockLLMClient,
    get_llm_client,
)


class SampleStructuredOutput(BaseModel):
    summary: str
    key_points: list[str]
    confidence: float


@pytest.mark.asyncio
async def test_mock_llm_client_text_and_structured() -> None:
    client = MockLLMClient()
    assert isinstance(client, BaseLLMClient)

    text = await client.generate_text("Verify this claim")
    assert "Mock response" in text

    structured = await client.generate_structured("Verify this claim", SampleStructuredOutput)
    assert isinstance(structured, SampleStructuredOutput)
    assert isinstance(structured.key_points, list)


def test_get_llm_client_factory_gemini_default() -> None:
    settings = Settings(
        GEMINI_API_KEY=SecretStr("test_gemini_key"),
        llm_provider="gemini",
        llm_model_name="gemini-2.0-flash",
    )
    client = get_llm_client(settings)
    assert isinstance(client, GeminiLLMClient)
    assert client.api_key == "test_gemini_key"
    assert client.model_name == "gemini-2.0-flash"


def test_get_llm_client_fallback_to_mock_when_no_keys() -> None:
    settings = Settings(
        GEMINI_API_KEY=SecretStr(""),
        OPENAI_API_KEY=SecretStr(""),
        ANTHROPIC_API_KEY=SecretStr(""),
    )
    client = get_llm_client(settings)
    assert isinstance(client, MockLLMClient)


@pytest.mark.asyncio
async def test_gemini_client_generate_text_mocked() -> None:
    client = GeminiLLMClient(api_key="fake_key", model_name="gemini-2.0-flash")

    mock_response = MagicMock()
    mock_response.text = "This is verified factual text from Gemini."

    mock_genai_client = MagicMock()
    mock_genai_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch.object(client, "_get_client", return_value=mock_genai_client):
        result = await client.generate_text("Is the sky blue?", temperature=0.2)
        assert result == "This is verified factual text from Gemini."


@pytest.mark.asyncio
async def test_gemini_client_generate_structured_mocked() -> None:
    client = GeminiLLMClient(api_key="fake_key", model_name="gemini-2.0-flash")

    mock_response = MagicMock()
    mock_response.text = '{"summary": "Accurate claim", "key_points": ["point 1", "point 2"], "confidence": 0.95}'

    mock_genai_client = MagicMock()
    mock_genai_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with patch.object(client, "_get_client", return_value=mock_genai_client):
        result = await client.generate_structured(
            "Analyze claim",
            SampleStructuredOutput,
        )
        assert isinstance(result, SampleStructuredOutput)
        assert result.summary == "Accurate claim"
        assert len(result.key_points) == 2
        assert result.confidence == 0.95


@pytest.mark.asyncio
async def test_gemini_client_error_handling() -> None:
    client = GeminiLLMClient(api_key="fake_key", model_name="gemini-2.0-flash")

    mock_genai_client = MagicMock()
    mock_genai_client.aio.models.generate_content = AsyncMock(side_effect=RuntimeError("Quota limit"))

    with (
        patch.object(client, "_get_client", return_value=mock_genai_client),
        pytest.raises(ProviderError, match="Gemini generation error"),
    ):
        await client.generate_text("Prompt that causes quota error")
