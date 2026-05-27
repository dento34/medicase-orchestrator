"""LLM client abstraction.

A small, opinionated surface so the rest of the codebase doesn't depend on
the Anthropic SDK directly, and tests can run without API calls.
"""
from __future__ import annotations

import os
from typing import Protocol, runtime_checkable

from .logging import get_logger

logger = get_logger("llm")


@runtime_checkable
class LLMClient(Protocol):
    def complete(self, *, system: str, user: str) -> str: ...


class AnthropicClient:
    """Real client. Requires ANTHROPIC_API_KEY in env."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int = 1024,
    ):
        # Imported lazily so MockClient doesn't pay the import cost.
        from anthropic import Anthropic

        self._client = Anthropic(api_key=api_key)  # picks up ANTHROPIC_API_KEY if None
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
        self.max_tokens = max_tokens
        logger.info(f"AnthropicClient initialized with model={self.model}")

    def complete(self, *, system: str, user: str) -> str:
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        # We only ever ask for a single text block.
        return resp.content[0].text


class MockClient:
    """Deterministic offline client.

    Looks up canned responses by substring match against the user prompt.
    Used for tests and offline development.
    """

    def __init__(self, fixtures: dict[str, str] | None = None):
        self.fixtures = fixtures or {}
        logger.info(f"MockClient initialized with {len(self.fixtures)} fixtures")

    def complete(self, *, system: str, user: str) -> str:
        for key, value in self.fixtures.items():
            if key == "default":
                continue
            if key in user:
                return value
        if "default" in self.fixtures:
            return self.fixtures["default"]
        raise RuntimeError(
            "MockClient: no fixture matched user prompt and no 'default' set."
        )


def make_client(*, prefer_real: bool = True) -> LLMClient:
    """Factory: returns AnthropicClient if API key set, else MockClient."""
    if prefer_real and os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicClient()
    logger.warning(
        "ANTHROPIC_API_KEY not set — falling back to MockClient. "
        "Real LLM calls will not be made."
    )
    return MockClient()
