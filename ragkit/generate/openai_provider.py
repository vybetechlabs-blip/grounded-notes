"""OpenAI generation provider (optional upgrade; requires OPENAI_API_KEY).

Install with the extra: ``uv sync --extra cloud``.
"""

import os

from ragkit.generate.prompt import SYSTEM_PROMPT, build_user_message
from ragkit.store.chroma import RetrievedChunk

DEFAULT_MODEL = "gpt-4o-mini"
"""Override with RAGKIT_OPENAI_MODEL."""


class OpenAIProvider:
    """Answers with an OpenAI chat model via the official SDK."""

    def __init__(self, model: str | None = None) -> None:
        self._model = model or os.environ.get("RAGKIT_OPENAI_MODEL", DEFAULT_MODEL)

    @property
    def name(self) -> str:
        return f"openai:{self._model}"

    def answer(self, question: str, results: list[RetrievedChunk]) -> str:
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model=self._model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_message(question, results)},
            ],
        )
        return response.choices[0].message.content or ""
