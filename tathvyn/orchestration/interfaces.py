"""Abstract Interfaces for Hosted LLM Reasoning Gateways."""

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMReasoningResponse(BaseModel):
    """Normalized response from a reasoning LLM invocation."""

    raw_output: str
    tokens_prompt: int
    tokens_completion: int
    latency_ms: int
    cost_usd: float


class ReasoningLLM(ABC):
    """Abstract Base Class for structured LLM reasoning and planning gateways."""

    @abstractmethod
    async def generate_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[T],
        temperature: float = 0.0,
    ) -> tuple[T, LLMReasoningResponse]:
        """Invoke LLM with strict Pydantic schema validation."""
        pass
