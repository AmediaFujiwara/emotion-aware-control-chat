"""
Radar chart component: visualizes the 3-axis AnxietyRiskVector as a Plotly radar chart.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from schemas.anxiety_risk_vector import AnxietyRiskVector

AXIS_LABELS = ["境界侵害", "制御不能性", "予期的喪失"]


def render_radar_chart(analysis: AnxietyRiskVector) -> None:
    """Render a Plotly radar chart for the latest analysis."""
    scores = [
        analysis.boundary_violation,
        analysis.uncontrollability,
        analysis.anticipated_loss,
    ]

    # Close the polygon
    values = scores + [scores[0]]
    labels = AXIS_LABELS + [AXIS_LABELS[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=labels,
            fill="toself",
            fillcolor="rgba(220, 80, 80, 0.25)",
            line=dict(color="rgba(220, 80, 80, 0.9)", width=2),
            name="リスクベクトル",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickfont=dict(size=10),
                gridcolor="rgba(200,200,200,0.4)",
            ),
            angularaxis=dict(
                tickfont=dict(size=12),
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        margin=dict(t=20, b=20, l=30, r=30),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)
