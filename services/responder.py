"""
Responder service: generates a structured, policy-driven AI response
based on the AnxietyRiskVector analysis.
"""

from __future__ import annotations

from pathlib import Path

from schemas.anxiety_risk_vector import AnxietyRiskVector

# Load responder system prompt once
_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "responder_prompt.md"


def _load_responder_prompt() -> str:
    try:
        return _PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "あなたは安定性優先のチャットAIです。analysis JSONに基づいて日本語で回答してください。"


def _build_fallback_response(analysis: AnxietyRiskVector) -> str:
    """Template-based fallback response when LLM is unavailable."""
    pattern = analysis.dominant_pattern
    policy = analysis.response_policy
    ni_section = ""

    if policy.should_use_ni and analysis.non_intervention_candidates:
        ni_items = "\n".join(f"  - {c}" for c in analysis.non_intervention_candidates)
        ni_section = f"\n**今日は扱わない（NI）候補：**\n{ni_items}\n"

    controllable_section = ""
    if analysis.controllable_factors:
        cf = "\n".join(f"  - {f}" for f in analysis.controllable_factors)
        controllable_section += f"\n**今日扱えるもの：**\n{cf}"
    if analysis.uncontrollable_factors:
        uf = "\n".join(f"  - {f}" for f in analysis.uncontrollable_factors)
        controllable_section += f"\n**今日は扱わないもの（制御不能）：**\n{uf}"

    safety_section = ""
    if analysis.safety_note:
        safety_section = f"\n---\n⚠️ **重要：** {analysis.safety_note}\n"

    response = f"""**不安の構造：** {analysis.summary}

**主な負荷パターン：** {pattern}

**対応方針：** {policy.primary_strategy}
{controllable_section}
{ni_section}
**今日の最小行動：** {analysis.minimal_action_today}

{analysis.stability_policy}
{safety_section}"""

    return response.strip()


def generate_response(
    user_text: str,
    analysis: AnxietyRiskVector,
    conversation_context: list[dict[str, str]],
    use_llm: bool,
    api_key: str | None,
    model: str,
) -> str:
    """
    Generate a stability-first AI response based on the risk vector analysis.

    Args:
        user_text: The latest user message.
        analysis: Computed AnxietyRiskVector.
        conversation_context: Recent chat history.
        use_llm: Whether to use LLM API.
        api_key: OpenAI API key.
        model: Model name string.

    Returns:
        AI response as a plain string.
    """
    if not use_llm or not api_key:
        return _build_fallback_response(analysis)

    try:
        from services.llm_client import LLMClient, LLMClientError

        client = LLMClient(api_key=api_key, model=model)
        system_prompt = _load_responder_prompt()

        # Serialize analysis for the prompt
        analysis_json = analysis.model_dump_json(indent=2)

        # Recent context (last 6 turns)
        context_lines = []
        for msg in conversation_context[-12:]:
            role = "ユーザー" if msg.get("role") == "user" else "AI"
            context_lines.append(f"{role}: {msg.get('content', '')[:300]}")
        context_str = "\n".join(context_lines) if context_lines else "（会話履歴なし）"

        user_message = (
            f"【直近の会話履歴】\n{context_str}\n\n"
            f"【ユーザーの最新入力】\n{user_text}\n\n"
            f"【分析結果 (AnxietyRiskVector)】\n{analysis_json}"
        )

        messages = [
            {"role": "user", "content": user_message},
        ]

        # Adjust max_tokens based on load level
        max_tokens = 600 if analysis.is_high_load else 1000

        return client.chat(messages, system=system_prompt, temperature=0.4, max_tokens=max_tokens)

    except Exception as e:
        print(f"[Responder] LLM error, using fallback: {e}")
        fallback = _build_fallback_response(analysis)
        return fallback + f"\n\n*（LLMエラーのためテンプレート回答を使用: {e}）*"
