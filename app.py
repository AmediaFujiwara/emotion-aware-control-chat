"""
Emotion-Aware Control Chat
不安3軸モデルによる安定性優先チャット

Entry point for Streamlit app.
Run: uv run streamlit run app.py
"""

from __future__ import annotations

import os
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from schemas.anxiety_risk_vector import AnxietyRiskVector
from services.analyzer import analyze_user_input
from services.responder import generate_response
from components.radar_chart import render_radar_chart
from components.score_panel import render_score_panel
from components.history_chart import render_history_chart
from utils.storage import session_to_json, build_turn_record

# --- Load .env ---
load_dotenv()

# ─────────────────────────────────────────
# Page config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Emotion-Aware Control Chat",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# Session state initialization
# ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages: list[dict] = []  # {"role": ..., "content": ...}

if "turn_history" not in st.session_state:
    st.session_state.turn_history: list[dict] = []  # full turn records with analysis

if "latest_analysis" not in st.session_state:
    st.session_state.latest_analysis: AnxietyRiskVector | None = None

# ─────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    st.title("🧭 Emotion-Aware\nControl Chat")
    st.caption("不安3軸モデルによる安定性優先チャット")

    st.divider()

    # --- API Key ---
    st.subheader("設定")

    env_key = os.getenv("ANTHROPIC_API_KEY", "")
    api_key_input = st.text_input(
        "Anthropic APIキー",
        value=env_key,
        type="password",
        placeholder="sk-ant-...",
        help=".envファイルに ANTHROPIC_API_KEY=sk-ant-... を設定することもできます。",
    )
    api_key = api_key_input.strip() or env_key.strip() or None

    # --- LLM / Demo mode ---
    use_llm = st.toggle(
        "LLMを使用する（APIキー必要）",
        value=bool(api_key),
        help="オフにするとキーワードベースのデモ分析が動きます。",
    )

    if use_llm and not api_key:
        st.warning("APIキーを入力してください。未入力の場合はデモモードで動作します。")
        use_llm = False

    mode_label = "LLMモード（Anthropic）" if use_llm else "デモモード（キーワードベース）"
    st.caption(f"現在: {mode_label}")

    # --- Model ---
    model = st.text_input(
        "モデル名",
        value="claude-sonnet-4-6",
        help="例: claude-sonnet-4-6, claude-haiku-4-5-20251001",
    )

    st.divider()

    # --- Reset ---
    if st.button("🗑️ スコア履歴をリセット", use_container_width=True):
        st.session_state.messages = []
        st.session_state.turn_history = []
        st.session_state.latest_analysis = None
        st.rerun()

    # --- Export ---
    if st.session_state.turn_history:
        export_json = session_to_json(st.session_state.turn_history)
        st.download_button(
            label="📥 セッションをJSONでエクスポート",
            data=export_json,
            file_name=f"emotion_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()

    # --- Disclaimer ---
    st.caption(
        "⚠️ このアプリは医療診断・治療ではありません。"
        "自己整理・メタ認知・意思決定支援のための実験的ツールです。"
        "精神的な危機・緊急事態は専門機関にご相談ください。"
    )

# ─────────────────────────────────────────
# Main area
# ─────────────────────────────────────────
st.title("Emotion-Aware Control Chat")
st.caption("不安3軸モデルによる安定性優先チャット")

st.markdown(
    """
このチャットは、不安を以下の **3軸** で構造化し、AIの応答方針を変化させます。

| 軸 | 説明 |
|---|---|
| **境界侵害** | 生活・回復・責任範囲への他者・仕事・義務の侵入 |
| **制御不能性** | 他者・組織・市場・未来など自分で制御できない要素への依存 |
| **予期的喪失** | 評価・健康・生活・関係性など将来失われるかもしれないものへの不安 |
"""
)

st.divider()

# ─────────────────────────────────────────
# Chat history display
# ─────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─────────────────────────────────────────
# Chat input
# ─────────────────────────────────────────
user_input = st.chat_input("不安・悩み・出来事を入力してください...")

if user_input and user_input.strip():
    user_text = user_input.strip()

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_text)

    # Add to message history
    st.session_state.messages.append({"role": "user", "content": user_text})

    # ── Step 1: Analyze ──
    with st.spinner("分析中..."):
        analysis: AnxietyRiskVector = analyze_user_input(
            user_text=user_text,
            conversation_context=st.session_state.messages[:-1],  # exclude current
            use_llm=use_llm,
            api_key=api_key,
            model=model,
        )

    # ── Step 2: Generate response ──
    with st.spinner("回答を生成中..."):
        ai_response: str = generate_response(
            user_text=user_text,
            analysis=analysis,
            conversation_context=st.session_state.messages[:-1],
            use_llm=use_llm,
            api_key=api_key,
            model=model,
        )

    # ── Step 3: Display assistant response ──
    with st.chat_message("assistant"):
        st.markdown(ai_response)

    # Add to message history
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # ── Step 4: Save to turn history ──
    turn_record = build_turn_record(
        user_text=user_text,
        ai_response=ai_response,
        analysis_dict=analysis.model_dump(),
    )
    st.session_state.turn_history.append(turn_record)
    st.session_state.latest_analysis = analysis

# ─────────────────────────────────────────
# Visualization (shown after at least one turn)
# ─────────────────────────────────────────
if st.session_state.latest_analysis is not None:
    analysis = st.session_state.latest_analysis

    st.divider()
    st.subheader("分析結果")

    col_radar, col_panel = st.columns([1, 2])

    with col_radar:
        st.markdown("**リスクベクトル（最新ターン）**")
        render_radar_chart(analysis)

    with col_panel:
        render_score_panel(analysis)

    if len(st.session_state.turn_history) >= 2:
        st.divider()
        st.subheader("スコア推移")
        render_history_chart(st.session_state.turn_history)
