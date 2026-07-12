from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from backend.metrics import drug_library_frame, prediction_distribution


TEMPLATE = "plotly_white"


def accuracy_chart() -> go.Figure:
    df = drug_library_frame()
    fig = px.bar(df, x="Drug", y="Accuracy", color="ROC-AUC", template=TEMPLATE)
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=30, b=10))
    return fig


def roc_chart() -> go.Figure:
    df = drug_library_frame()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Drug"], y=df["ROC-AUC"], mode="lines+markers", name="ROC-AUC"))
    fig.add_trace(go.Scatter(x=df["Drug"], y=df["Accuracy"], mode="lines+markers", name="Accuracy"))
    fig.update_layout(template=TEMPLATE, height=360, margin=dict(l=10, r=10, t=30, b=10))
    return fig


def distribution_chart(predictions: pd.DataFrame | None) -> go.Figure:
    df = prediction_distribution(predictions)
    fig = px.histogram(df, x="probability_responsive", nbins=24, template=TEMPLATE)
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=10))
    return fig


def gauge(value: float, title: str) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(value) * 100.0,
            number={"suffix": "%"},
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2bd4ff"},
                "steps": [
                    {"range": [0, 45], "color": "rgba(255,92,122,.25)"},
                    {"range": [45, 70], "color": "rgba(255,210,92,.22)"},
                    {"range": [70, 100], "color": "rgba(56,217,150,.25)"},
                ],
            },
        )
    )
    fig.update_layout(template=TEMPLATE, height=260, margin=dict(l=10, r=10, t=20, b=10))
    return fig
