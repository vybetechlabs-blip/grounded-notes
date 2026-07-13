"""Claude generation provider (optional upgrade; requires ANTHROPIC_API_KEY).

Install with the extra: ``uv sync --extra cloud``.
"""

import os

from ragkit.generate.prompt import SYSTEM_PROMPT, build_user_message
from ragkit.store.chroma import RetrievedChunk

DEFAULT_MODEL = "claude-opus-4-8"
"""Override with RAGKIT_ANTHROPIC_MODEL (e.g. a smaller model to cut cost)."""


class AnthropicProvider:
    """Answers with Claude via the official Anthropic SDK."""

    def __init__(self, model: str | None = None) -> None:
        self._model = model or os.environ.get("RAGKIT_ANTHROPIC_MODEL", DEFAULT_MODEL)

    @property
    def name(self) -> str:
        return f"anthropic:{self._model}"

    def answer(self, question: str, results: list[RetrievedChunk]) -> str:
        import anthropic

        client = anthropic.Anthropic()
        response = client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_message(question, results)}],
        )
        if response.stop_reason == "refusal":
            return "The model declined to answer this question."
        return "".join(block.text for block in response.content if block.type == "text")
