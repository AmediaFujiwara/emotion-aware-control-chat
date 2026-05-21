"""
Session storage utilities: serialize chat history to JSON for export.
"""

import json
from datetime import datetime
from typing import Any


def session_to_json(chat_history: list[dict[str, Any]]) -> str:
    """
    Convert chat history (list of turn dicts) to a formatted JSON string.

    Each turn dict should have:
    - timestamp: str
    - role: "user" | "assistant"
    - content: str
    - analysis: dict (AnxietyRiskVector fields) — present on assistant turns
    """
    export = {
        "exported_at": datetime.now().isoformat(),
        "app": "emotion-aware-control-chat",
        "version": "0.1.0",
        "turns": chat_history,
    }
    return json.dumps(export, ensure_ascii=False, indent=2)


def build_turn_record(
    user_text: str,
    ai_response: str,
    analysis_dict: dict[str, Any],
) -> dict[str, Any]:
    """Build a single turn record for storage."""
    return {
        "timestamp": datetime.now().isoformat(),
        "user_text": user_text,
        "ai_response": ai_response,
        "analysis": analysis_dict,
        "scores": {
            "boundary_violation": analysis_dict.get("boundary_violation", 0),
            "uncontrollability": analysis_dict.get("uncontrollability", 0),
            "anticipated_loss": analysis_dict.get("anticipated_loss", 0),
        },
    }
