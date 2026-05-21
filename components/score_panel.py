"""
Score panel component: displays key fields from the AnxietyRiskVector in a readable format.
"""

from __future__ import annotations

import streamlit as st

from schemas.anxiety_risk_vector import AnxietyRiskVector


def _score_bar(score: int, max_score: int = 10) -> str:
    """Return a simple ASCII-style bar for quick visual scanning."""
    filled = round(score / max_score * 10)
    return "█" * filled + "░" * (10 - filled)


def render_score_panel(analysis: AnxietyRiskVector) -> None:
    """Render the 3-axis scores and policy summary in a compact panel."""
    st.markdown("#### 不安3軸スコア")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("境界侵害", f"{analysis.boundary_violation} / 10")
        st.caption(_score_bar(analysis.boundary_violation))
    with col2:
        st.metric("制御不能性", f"{analysis.uncontrollability} / 10")
        st.caption(_score_bar(analysis.uncontrollability))
    with col3:
        st.metric("予期的喪失", f"{analysis.anticipated_loss} / 10")
        st.caption(_score_bar(analysis.anticipated_loss))

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**支配軸:** {analysis.dominant_axis}")
        st.markdown(f"**パターン:** {analysis.dominant_pattern}")
    with col_b:
        ni_label = "⚠️ NI推奨" if analysis.response_policy.should_use_ni else "介入OK"
        st.markdown(f"**NI方針:** {ni_label}")
        st.markdown(f"**総負荷:** {analysis.total_load} / 30")

    st.divider()
    st.markdown(f"**主方針:** {analysis.response_policy.primary_strategy}")
    st.markdown(f"**今日の最小行動:** {analysis.minimal_action_today}")

    if analysis.response_policy.should_use_ni and analysis.response_policy.ni_reason:
        st.info(f"NI理由: {analysis.response_policy.ni_reason}")

    if analysis.safety_note:
        st.error(f"⚠️ {analysis.safety_note}")
