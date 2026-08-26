"""Tests for LLM Reasoning and Orchestration Interface Models."""

from typing import Any, TypeVar

from pydantic import BaseModel

from tathvyn.orchestration.interfaces import LLMReasoningResponse, ReasoningLLM

T = TypeVar("T", bound=BaseModel)


class SampleStructuredOutput(BaseModel):
    summary: str
    confidence: float


class MockReasoningLLM(ReasoningLLM):
    """Mock implementation for ReasoningLLM interface."""

    async def generate_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[T],
        temperature: float = 0.0,
    ) -> tuple[T, LLMReasoningResponse]:
        raw_dict: dict[str, Any] = {"summary": "Mock summary", "confidence": 0.92}
        output = response_schema.model_validate(raw_dict)
        response_meta = LLMReasoningResponse(
            raw_output=output.model_dump_json(),
            tokens_prompt=50,
            tokens_completion=20,
            latency_ms=210,
            cost_usd=0.00045,
        )
        return output, response_meta


async def test_mock_reasoning_llm() -> None:
    """Verify ReasoningLLM mock invocation."""
    llm = MockReasoningLLM()
    output, meta = await llm.generate_structured_response(
        system_prompt="You are a verifier.",
        user_prompt="Verify X.",
        response_schema=SampleStructuredOutput,
    )

    assert output.summary == "Mock summary"
    assert output.confidence == 0.92
    assert meta.latency_ms == 210
    assert meta.cost_usd > 0.0
