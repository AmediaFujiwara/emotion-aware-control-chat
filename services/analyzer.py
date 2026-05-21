"""
Analyzer service: converts user input into an AnxietyRiskVector.
Uses LLM (OpenAI) when available, falls back to keyword-based rules.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from schemas.anxiety_risk_vector import AnxietyRiskVector
from utils.fallback_rules import analyze_with_fallback

# Load the analyzer system prompt once at import time
_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "analyzer_prompt.md"


def _load_analyzer_prompt() -> str:
    try:
        return _PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "あなたは不安を3軸（境界侵害・制御不能性・予期的喪失）で分析するアナライザーです。JSON形式で返してください。"


def _parse_analysis_json(data: dict[str, Any]) -> AnxietyRiskVector:
    """
    Parse raw dict from LLM into AnxietyRiskVector.
    Raises ValidationError on schema mismatch.
    """
    return AnxietyRiskVector.model_validate(data)


def analyze_user_input(
    user_text: str,
    conversation_context: list[dict[str, str]],
    use_llm: bool,
    api_key: str | None,
    model: str,
) -> AnxietyRiskVector:
    """
    Analyze user input and return a structured AnxietyRiskVector.

    Args:
        user_text: The latest user message.
        conversation_context: Recent chat history as [{"role": ..., "content": ...}].
        use_llm: Whether to use the LLM API.
        api_key: OpenAI API key (may be None).
        model: Model name string.

    Returns:
        AnxietyRiskVector — always returns a valid object (falls back on error).
    """
    if not use_llm or not api_key:
        return analyze_with_fallback(user_text)

    try:
        from services.llm_client import LLMClient, LLMClientError

        client = LLMClient(api_key=api_key, model=model)
        system_prompt = _load_analyzer_prompt()

        # Build recent context string (last 4 turns)
        context_str = _format_context(conversation_context[-8:])

        user_message = (
            f"【直近の会話履歴】\n{context_str}\n\n"
            f"【ユーザーの最新入力】\n{user_text}"
        )

        messages = [
            {"role": "user", "content": user_message},
        ]

        raw_json = client.chat_json(messages, system=system_prompt)
        return _parse_analysis_json(raw_json)

    except ValidationError as e:
        # Schema mismatch → fallback
        print(f"[Analyzer] Pydantic validation error, falling back: {e}")
        return analyze_with_fallback(user_text)

    except Exception as e:
        # LLM error, network error, parse error → fallback
        print(f"[Analyzer] LLM error, falling back: {e}")
        return analyze_with_fallback(user_text)


def _format_context(messages: list[dict[str, str]]) -> str:
    """Format recent messages as a readable string for the prompt."""
    if not messages:
        return "（会話履歴なし）"
    lines = []
    for msg in messages:
        role = "ユーザー" if msg.get("role") == "user" else "AI"
        lines.append(f"{role}: {msg.get('content', '')[:200]}")
    return "\n".join(lines)
