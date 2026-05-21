"""
History chart component: time-series line chart of the 3-axis scores across conversation turns.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_history_chart(turn_history: list[dict]) -> None:
    """
    Render a line chart showing score evolution over conversation turns.

    Args:
        turn_history: List of turn dicts, each containing a 'scores' sub-dict with:
            - boundary_violation: int
            - uncontrollability: int
            - anticipated_loss: int
    """
    if len(turn_history) < 1:
        st.caption("スコア履歴がまだありません。")
        return

    rows = []
    for i, turn in enumerate(turn_history, start=1):
        scores = turn.get("scores", {})
        rows.append({
            "ターン": i,
            "境界侵害": scores.get("boundary_violation", 0),
            "制御不能性": scores.get("uncontrollability", 0),
            "予期的喪失": scores.get("anticipated_loss", 0),
        })

    df = pd.DataFrame(rows)

    fig = go.Figure()

    colors = {
        "境界侵害": "#E05C5C",
        "制御不能性": "#F0A030",
        "予期的喪失": "#5080E0",
    }

    for col, color in colors.items():
        fig.add_trace(
            go.Scatter(
                x=df["ターン"],
                y=df[col],
                mode="lines+markers",
                name=col,
                line=dict(color=color, width=2),
                marker=dict(size=6),
            )
        )

    fig.update_layout(
        xaxis=dict(
            title="ターン",
            tickmode="linear",
            tick0=1,
            dtick=1,
            gridcolor="rgba(200,200,200,0.3)",
        ),
        yaxis=dict(
            title="スコア",
            range=[0, 10],
            gridcolor="rgba(200,200,200,0.3)",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=30, b=40, l=40, r=20),
        height=250,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)
