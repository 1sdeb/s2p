"""Provider-agnostic LLM interface.

Both Claude and OpenAI are reached through the same `LLMClient.complete()`
call so the rest of the engine never needs to know which provider is in use.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ..config import LLMConfig


class LLMClient(Protocol):
    """Minimal contract the conversion engine relies on."""

    model: str

    def complete(self, system: str, user: str, *, max_tokens: int = 8192) -> str:
        """Return the assistant's text for a single-turn system+user prompt."""
        ...


def get_client(llm: "LLMConfig") -> LLMClient:
    """Build a client from resolved LLMConfig (provider, model, api key)."""
    provider = (llm.provider or "anthropic").lower()

    if provider in ("anthropic", "claude"):
        from .anthropic_client import AnthropicClient

        return AnthropicClient(model=llm.model, api_key=llm.anthropic_api_key)
    if provider in ("openai", "gpt"):
        from .openai_client import OpenAIClient

        return OpenAIClient(
            model=llm.model or llm.openai_model, api_key=llm.openai_api_key
        )
    raise ValueError(f"Unknown provider: {provider!r} (use 'anthropic' or 'openai')")
