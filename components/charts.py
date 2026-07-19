"""Plotly chart helpers."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def price_chart(prices: list[float]) -> go.Figure:
    """Create a historical price chart."""

    frame = pd.DataFrame({"period": list(range(1, len(prices) + 1)), "price": prices})
    fig = px.line(frame, x="period", y="price", markers=True, template="plotly_dark")
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=24, b=10))
    return fig


def allocation_chart(labels: list[str], values: list[float]) -> go.Figure:
    """Create an investment allocation chart."""

    fig = px.bar(x=labels, y=values, template="plotly_dark", labels={"x": "Bucket", "y": "Allocation"})
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=24, b=10))
    return fig


def radar_chart(scores: dict[str, float]) -> go.Figure:
    """Create a radar score chart."""

    labels = list(scores.keys())
    values = list(scores.values())
    fig = go.Figure(
        data=[go.Scatterpolar(r=values + values[:1], theta=labels + labels[:1], fill="toself", line_color="#38c7e8")]
    )
    fig.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=340)
    return fig


def gauge_chart(value: float, title: str, *, maximum: float = 100.0) -> go.Figure:
    """Create a compact gauge indicator."""

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "" if maximum != 100 else ""},
            title={"text": title},
            gauge={
                "axis": {"range": [0, maximum]},
                "bar": {"color": "#38c7e8"},
                "steps": [
                    {"range": [0, maximum * 0.45], "color": "rgba(240, 103, 125, 0.28)"},
                    {"range": [maximum * 0.45, maximum * 0.75], "color": "rgba(240, 182, 74, 0.24)"},
                    {"range": [maximum * 0.75, maximum], "color": "rgba(77, 213, 138, 0.22)"},
                ],
            },
        )
    )
    fig.update_layout(template="plotly_dark", height=250, margin=dict(l=10, r=10, t=35, b=5))
    return fig


def metric_bar_chart(values: dict[str, float], title: str = "") -> go.Figure:
    """Create a horizontal metric bar chart."""

    frame = pd.DataFrame({"metric": list(values.keys()), "value": list(values.values())})
    fig = px.bar(
        frame,
        x="value",
        y="metric",
        orientation="h",
        template="plotly_dark",
        color="value",
        color_continuous_scale=["#f0677d", "#f0b64a", "#4dd58a"],
        title=title,
    )
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=42 if title else 10, b=10), coloraxis_showscale=False)
    return fig


def cashflow_chart(cash_flows: Sequence[float]) -> go.Figure:
    """Create a cash-flow bar chart with positive/negative coloring."""

    frame = pd.DataFrame(
        {
            "period": [f"Y{idx}" for idx in range(len(cash_flows))],
            "cash_flow": list(cash_flows),
            "type": ["Inflow" if value >= 0 else "Outflow" for value in cash_flows],
        }
    )
    fig = px.bar(
        frame,
        x="period",
        y="cash_flow",
        color="type",
        template="plotly_dark",
        color_discrete_map={"Inflow": "#4dd58a", "Outflow": "#f0677d"},
    )
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=24, b=10))
    return fig


def donut_chart(values: dict[str, float], title: str = "") -> go.Figure:
    """Create a donut chart."""

    fig = px.pie(
        names=list(values.keys()),
        values=list(values.values()),
        hole=0.62,
        template="plotly_dark",
        title=title,
        color_discrete_sequence=["#38c7e8", "#4dd58a", "#f0b64a", "#f0677d", "#8f7cff"],
    )
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=42 if title else 10, b=10))
    return fig


def scatter_value_chart(frame: pd.DataFrame, x: str, y: str, size: str | None = None, title: str = "") -> go.Figure:
    """Create a polished scatter chart for property comparison."""

    fig = px.scatter(
        frame,
        x=x,
        y=y,
        size=size,
        template="plotly_dark",
        title=title,
        color_discrete_sequence=["#38c7e8"],
    )
    fig.update_traces(marker={"line": {"width": 1, "color": "rgba(255,255,255,0.55)"}})
    fig.update_layout(height=330, margin=dict(l=10, r=10, t=42 if title else 10, b=10))
    return fig
