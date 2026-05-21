"""
LLM client wrapper for Anthropic API (claude-sonnet-4-6 etc.)
"""

from __future__ import annotations

import json
from typing import Any

try:
    import anthropic as _anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMClientError(Exception):
    """Raised when the LLM call fails in a recoverable way."""
    pass


class LLMClient:
    """Thin wrapper around the Anthropic Messages API."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        if not ANTHROPIC_AVAILABLE:
            raise LLMClientError("anthropic パッケージがインストールされていません。`uv sync` を実行してください。")
        self.client = _anthropic.Anthropic(api_key=api_key)
        self.model = model

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str:
        """
        Call Anthropic Messages API and return the assistant's text.

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."} dicts.
                      system prompt is passed separately via `system`.
            system: System prompt string.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.

        Returns:
            The assistant's reply as a plain string.

        Raises:
            LLMClientError: On API errors with a human-readable message.
        """
        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": messages,
            }
            if system:
                kwargs["system"] = system

            response = self.client.messages.create(**kwargs)
            return response.content[0].text

        except _anthropic.AuthenticationError:
            raise LLMClientError("APIキーが無効です。サイドバーで正しい Anthropic APIキーを入力してください。")
        except _anthropic.RateLimitError:
            raise LLMClientError("レート制限に達しました。少し待ってから再試行してください。")
        except _anthropic.APIConnectionError:
            raise LLMClientError("Anthropic APIへの接続に失敗しました。ネットワーク接続を確認してください。")
        except Exception as e:
            raise LLMClientError(f"LLM呼び出しエラー: {e}") from e

    def chat_json(
        self,
        messages: list[dict[str, str]],
        system: str = "",
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        """
        Call the API and parse the response as JSON.
        Anthropic doesn't have a dedicated JSON mode, so we rely on the prompt
        instructing the model to return JSON only.

        Returns:
            Parsed dict from the JSON response.

        Raises:
            LLMClientError: On API or parse errors.
        """
        raw = self.chat(messages, system=system, temperature=temperature, max_tokens=max_tokens)

        # Strip accidental markdown code fences (```json ... ```)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            # Remove first and last fence lines
            cleaned = "\n".join(
                line for line in lines
                if not line.strip().startswith("```")
            ).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise LLMClientError(
                f"LLMのJSON出力のパースに失敗しました: {e}\n\nRaw output:\n{raw}"
            ) from e
