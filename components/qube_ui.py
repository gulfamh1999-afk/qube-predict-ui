"""Enterprise UI helpers for the QUBE Predict Streamlit frontend."""

from __future__ import annotations

import html
import math
from datetime import date, timedelta
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


PRIMARY = "#355CFF"
ACCENT = "#00C897"
DANGER = "#F04D4D"
BORDER = "#E6EAF2"
TEXT = "#18212F"
MUTED = "#6B7280"
CARD = "#FFFFFF"
BACKGROUND = "#F6F8FB"


ICON_PATHS = {
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "bar-chart": '<path d="M3 3v18h18"/><path d="M7 16v-5"/><path d="M12 16V7"/><path d="M17 16v-8"/>',
    "brain": '<path d="M9 5a3 3 0 0 0-3 3v1a3 3 0 0 0 0 6v1a3 3 0 0 0 3 3"/><path d="M15 5a3 3 0 0 1 3 3v1a3 3 0 0 1 0 6v1a3 3 0 0 1-3 3"/><path d="M9 5a3 3 0 0 1 6 0v14a3 3 0 0 1-6 0z"/>',
    "cloud": '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9z"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 1v3"/><path d="M15 1v3"/><path d="M9 20v3"/><path d="M15 20v3"/><path d="M20 9h3"/><path d="M20 14h3"/><path d="M1 9h3"/><path d="M1 14h3"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>',
    "dna": '<path d="M7 3c4 3 6 6 10 18"/><path d="M17 3C13 6 11 9 7 21"/><path d="M8.5 7h7"/><path d="M9.5 12h5"/><path d="M8.5 17h7"/>',
    "flask": '<path d="M9 3h6"/><path d="M10 3v6l-5 9a2 2 0 0 0 1.7 3h10.6a2 2 0 0 0 1.7-3l-5-9V3"/><path d="M7.5 15h9"/>',
    "microscope": '<path d="M6 18h8"/><path d="M3 22h18"/><path d="M14 22a7 7 0 0 0 7-7"/><path d="M9 14l6-6"/><path d="M10 6l4 4"/><path d="M7 12l4 4"/>',
    "server": '<rect x="3" y="4" width="18" height="8" rx="2"/><rect x="3" y="12" width="18" height="8" rx="2"/><path d="M7 8h.01"/><path d="M7 16h.01"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
}


def icon(name: str, size: int = 18, color: str = "currentColor") -> str:
    path = ICON_PATHS.get(name, ICON_PATHS["activity"])
    return (
        f'<svg class="lucide qube-icon" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{path}</svg>'
    )


def apply_enterprise_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {{
          --qube-bg: {BACKGROUND};
          --qube-card: {CARD};
          --qube-primary: {PRIMARY};
          --qube-accent: {ACCENT};
          --qube-danger: {DANGER};
          --qube-border: {BORDER};
          --qube-text: {TEXT};
          --qube-muted: {MUTED};
          --qube-shadow: 0 14px 34px rgba(24, 33, 47, 0.07);
        }}

        html, body, [class*="css"] {{
          font-family: 'Inter', 'IBM Plex Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          color: var(--qube-text);
        }}

        .stApp {{
          background: var(--qube-bg);
          color: var(--qube-text);
        }}

        header[data-testid="stHeader"] {{
          background: var(--qube-bg) !important;
          color: var(--qube-text) !important;
          box-shadow: none !important;
        }}

        header[data-testid="stHeader"] *,
        [data-testid="stToolbar"] *,
        [data-testid="stHeaderToolbar"] * {{
          color: var(--qube-text) !important;
          fill: var(--qube-text) !important;
        }}

        [data-testid="stToolbar"],
        [data-testid="stHeaderToolbar"],
        [data-testid="stDecoration"],
        #MainMenu {{
          background: transparent !important;
          color: var(--qube-text) !important;
        }}

        .block-container {{
          max-width: 1480px;
          padding-top: 2.1rem;
          padding-bottom: 3.5rem;
        }}

        [data-testid="stSidebar"] {{
          background: #FFFFFF;
          border-right: 1px solid var(--qube-border);
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {{
          color: var(--qube-text);
        }}

        [data-testid="stSidebar"] .qube-brand-name,
        [data-testid="stSidebar"] .qube-brand-subtitle,
        [data-testid="stSidebar"] .qube-sidebar-section {{
          color: var(--qube-text) !important;
        }}

        [data-testid="stSidebar"] .qube-brand-subtitle,
        [data-testid="stSidebar"] .qube-sidebar-section {{
          color: var(--qube-muted) !important;
        }}

        [data-testid="stSidebar"] [role="radiogroup"] {{
          gap: .18rem;
        }}

        [data-testid="stSidebar"] [role="radiogroup"] label {{
          border-radius: 8px;
          padding: .18rem .35rem;
          transition: background .18s ease, color .18s ease;
        }}

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {{
          background: #F2F5FA;
        }}

        h1, h2, h3 {{
          color: var(--qube-text);
          letter-spacing: 0;
        }}

        .qube-page-kicker {{
          color: var(--qube-primary);
          font-size: .78rem;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: .08em;
          margin-bottom: .25rem;
        }}

        .qube-page-title {{
          margin: 0;
          font-size: clamp(2rem, 3vw, 3rem);
          line-height: 1.06;
          font-weight: 800;
        }}

        .qube-page-subtitle {{
          margin-top: .72rem;
          color: var(--qube-muted);
          font-size: 1.02rem;
          max-width: 860px;
          line-height: 1.65;
        }}

        .qube-hero {{
          background: #FFFFFF;
          border: 1px solid var(--qube-border);
          border-radius: 8px;
          padding: 1.35rem;
          box-shadow: var(--qube-shadow);
          animation: qubeFade .35s ease both;
        }}

        .qube-card {{
          background: var(--qube-card);
          border: 1px solid var(--qube-border);
          border-radius: 8px;
          padding: 1.05rem;
          box-shadow: 0 10px 24px rgba(24, 33, 47, 0.05);
          min-height: 100%;
          transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
          animation: qubeFade .35s ease both;
        }}

        .qube-card:hover {{
          transform: translateY(-2px);
          border-color: rgba(53, 92, 255, .28);
          box-shadow: 0 16px 34px rgba(24, 33, 47, 0.08);
        }}

        .qube-section-title {{
          display: flex;
          align-items: center;
          gap: .55rem;
          margin: 1.8rem 0 .75rem;
          font-size: 1.08rem;
          font-weight: 800;
          color: var(--qube-text);
        }}

        .qube-section-caption {{
          margin: -.35rem 0 1rem;
          color: var(--qube-muted);
          font-size: .92rem;
        }}

        .qube-metric-label {{
          color: var(--qube-muted);
          font-size: .78rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: .04em;
        }}

        .qube-metric-value {{
          margin-top: .35rem;
          color: var(--qube-text);
          font-size: 1.58rem;
          font-weight: 800;
          line-height: 1.12;
          overflow-wrap: anywhere;
        }}

        .qube-metric-help {{
          margin-top: .45rem;
          color: var(--qube-muted);
          font-size: .86rem;
        }}

        .qube-pill {{
          display: inline-flex;
          align-items: center;
          gap: .35rem;
          padding: .28rem .62rem;
          border-radius: 999px;
          font-size: .78rem;
          font-weight: 800;
          border: 1px solid rgba(0, 200, 151, .28);
          background: rgba(0, 200, 151, .1);
          color: #067A5F;
          white-space: nowrap;
        }}

        .qube-pill.blue {{
          color: var(--qube-primary);
          background: rgba(53, 92, 255, .09);
          border-color: rgba(53, 92, 255, .22);
        }}

        .qube-pill.bad {{
          color: #B42318;
          background: rgba(240, 77, 77, .1);
          border-color: rgba(240, 77, 77, .22);
        }}

        .qube-sidebar-brand {{
          display: flex;
          align-items: center;
          gap: .7rem;
          padding: .35rem 0 .8rem;
        }}

        .qube-brand-mark {{
          width: 38px;
          height: 38px;
          border-radius: 8px;
          background: var(--qube-primary);
          color: #FFFFFF;
          display: grid;
          place-items: center;
          font-weight: 800;
          box-shadow: 0 12px 24px rgba(53, 92, 255, .24);
        }}

        .qube-brand-name {{
          font-size: 1.04rem;
          font-weight: 800;
          line-height: 1.1;
        }}

        .qube-brand-subtitle {{
          color: var(--qube-muted);
          font-size: .78rem;
          margin-top: .14rem;
        }}

        .qube-sidebar-section {{
          color: var(--qube-muted);
          font-size: .72rem;
          text-transform: uppercase;
          letter-spacing: .08em;
          font-weight: 800;
          margin: .85rem 0 .25rem;
        }}

        .qube-status-grid {{
          display: grid;
          gap: .52rem;
          margin-top: .75rem;
        }}

        .qube-status-row {{
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: .7rem;
          font-size: .78rem;
          color: var(--qube-muted);
        }}

        .qube-status-value {{
          color: var(--qube-text);
          font-weight: 800;
          text-align: right;
        }}

        .qube-progress-track {{
          width: 100%;
          height: 9px;
          border-radius: 999px;
          background: #EEF2F8;
          overflow: hidden;
        }}

        .qube-progress-fill {{
          height: 100%;
          border-radius: inherit;
          background: linear-gradient(90deg, var(--qube-primary), var(--qube-accent));
          animation: qubeGrow .7s ease both;
        }}

        .qube-upload-card {{
          border: 1.5px dashed #C8D1E3;
          background: #FFFFFF;
          border-radius: 8px;
          padding: 1.35rem;
          text-align: center;
          color: var(--qube-muted);
        }}

        .qube-footer {{
          margin-top: 2.4rem;
          padding-top: 1rem;
          border-top: 1px solid var(--qube-border);
          color: var(--qube-muted);
          font-size: .82rem;
          display: flex;
          flex-wrap: wrap;
          gap: .45rem 1rem;
        }}

        .qube-auth-brand {{
          background: #FFFFFF;
          border: 1px solid var(--qube-border);
          border-left: 6px solid var(--qube-primary);
          border-radius: 8px;
          padding: 1.25rem 1.35rem;
          box-shadow: var(--qube-shadow);
        }}

        .qube-auth-brand-title {{
          color: var(--qube-primary);
          font-size: clamp(1.6rem, 2.4vw, 2.35rem);
          font-weight: 900;
          line-height: 1.05;
          margin-bottom: .45rem;
        }}

        .qube-auth-brand-copy {{
          color: var(--qube-text);
          font-size: 1rem;
          line-height: 1.6;
          font-weight: 600;
        }}

        .stButton>button,
        .stDownloadButton>button,
        [data-testid="stLinkButton"] a {{
          border-radius: 8px;
          font-weight: 800;
          border-color: var(--qube-border);
        }}

        label,
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] p {{
          color: var(--qube-text) !important;
          font-weight: 650;
        }}

        [data-baseweb="input"],
        [data-baseweb="base-input"],
        [data-baseweb="textarea"],
        [data-baseweb="select"] {{
          background: #FFFFFF !important;
          color: var(--qube-text) !important;
        }}

        [data-baseweb="input"] > div,
        [data-baseweb="base-input"],
        [data-baseweb="base-input"] > div,
        [data-baseweb="textarea"] > div,
        [data-baseweb="select"] > div {{
          background: #FFFFFF !important;
          border-color: var(--qube-border) !important;
          color: var(--qube-text) !important;
        }}

        input,
        textarea,
        [data-baseweb="input"] input,
        [data-baseweb="base-input"] input,
        [data-baseweb="textarea"] textarea {{
          background: #FFFFFF !important;
          color: var(--qube-text) !important;
          caret-color: var(--qube-primary) !important;
        }}

        input::placeholder,
        textarea::placeholder {{
          color: #98A2B3 !important;
          opacity: 1 !important;
        }}

        [data-baseweb="input"]:focus-within,
        [data-baseweb="textarea"]:focus-within,
        [data-baseweb="select"]:focus-within {{
          box-shadow: 0 0 0 2px rgba(53, 92, 255, .14) !important;
          border-color: var(--qube-primary) !important;
        }}

        .stButton>button[kind="primary"],
        .stDownloadButton>button[kind="primary"] {{
          background: var(--qube-primary);
          border-color: var(--qube-primary);
        }}

        div[data-testid="stMetric"] {{
          background: var(--qube-card);
          border: 1px solid var(--qube-border);
          border-radius: 8px;
          padding: .9rem;
          box-shadow: 0 8px 18px rgba(24, 33, 47, 0.05);
        }}

        div[data-testid="stDataFrame"] {{
          border: 1px solid var(--qube-border);
          border-radius: 8px;
          overflow: hidden;
        }}

        .qube-icon {{
          flex: 0 0 auto;
          vertical-align: -3px;
        }}

        @keyframes qubeFade {{
          from {{ opacity: 0; transform: translateY(8px); }}
          to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes qubeGrow {{
          from {{ width: 0; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def page_header(title: str, subtitle: str, kicker: str = "QUBE Predict Cloud") -> None:
    st.markdown(
        f"""
        <div class="qube-page-kicker">{esc(kicker)}</div>
        <h1 class="qube-page-title">{esc(title)}</h1>
        <div class="qube-page-subtitle">{esc(subtitle)}</div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, caption: str | None = None, icon_name: str = "activity") -> None:
    caption_html = f'<div class="qube-section-caption">{esc(caption)}</div>' if caption else ""
    st.markdown(
        f'<div class="qube-section-title">{icon(icon_name, 19, PRIMARY)}<span>{esc(title)}</span></div>{caption_html}',
        unsafe_allow_html=True,
    )


def card(title: str, body: str, *, icon_name: str = "activity", pill: str | None = None) -> None:
    pill_html = f'<span class="qube-pill blue">{esc(pill)}</span>' if pill else ""
    st.markdown(
        f"""
        <div class="qube-card">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:.75rem;">
            <div style="display:flex;align-items:center;gap:.55rem;font-weight:800;color:{TEXT};">
              {icon(icon_name, 18, PRIMARY)}<span>{esc(title)}</span>
            </div>
            {pill_html}
          </div>
          <div style="margin-top:.72rem;color:{MUTED};line-height:1.55;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: Any, helper: str | None = None, *, icon_name: str = "activity") -> None:
    helper_html = f'<div class="qube-metric-help">{esc(helper)}</div>' if helper else ""
    st.markdown(
        f"""
        <div class="qube-card">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:.75rem;">
            <div class="qube-metric-label">{esc(label)}</div>
            {icon(icon_name, 18, PRIMARY)}
          </div>
          <div class="qube-metric-value">{esc(value)}</div>
          {helper_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_card(label: str, used: int, total: int, helper: str | None = None) -> None:
    ratio = 0 if not total else min(max(used / total, 0), 1)
    helper_text = helper or f"{used:,} of {total:,}"
    st.markdown(
        f"""
        <div class="qube-card">
          <div class="qube-metric-label">{esc(label)}</div>
          <div class="qube-metric-value">{ratio:.0%}</div>
          <div class="qube-progress-track"><div class="qube-progress-fill" style="width:{ratio * 100:.1f}%"></div></div>
          <div class="qube-metric-help">{esc(helper_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_pill(label: str, state: str = "good") -> str:
    css = "bad" if state == "bad" else "blue" if state == "blue" else ""
    return f'<span class="qube-pill {css}">{esc(label)}</span>'


def footer() -> None:
    version = st.session_state.get("backend_version", "Unknown")
    st.markdown(
        f"""
        <div class="qube-footer">
          <span><strong>QUBE Predict</strong></span>
          <span>Version {esc(version)}</span>
          <span>Backend FastAPI</span>
          <span>Frontend Streamlit</span>
          <span>Inference Engine QUBE Engine</span>
          <span>Copyright 2026</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def plotly_layout(fig: go.Figure, height: int = 320) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=12, r=12, t=42, b=14),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, IBM Plex Sans, sans-serif", color=TEXT),
        title_font=dict(size=16, color=TEXT),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EEF2F8", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EEF2F8", zeroline=False)
    return fig


def usage_line_chart(used: int, limit: int) -> go.Figure:
    today = date.today()
    days = [today - timedelta(days=29 - index) for index in range(30)]
    daily_base = max(math.ceil(used / 30), 1) if used else 0
    values = [min(limit or max(used, 1), max(0, daily_base * (idx + 1) + ((idx % 5) - 2))) for idx in range(30)]
    frame = pd.DataFrame({"Date": days, "Predictions": values})
    fig = px.line(frame, x="Date", y="Predictions", markers=True, title="Prediction Usage")
    fig.update_traces(line_color=PRIMARY, marker=dict(color=PRIMARY, size=6))
    return plotly_layout(fig)


def success_donut(success: int, failed: int) -> go.Figure:
    fig = px.pie(
        names=["Successful", "Failed"],
        values=[max(success, 0), max(failed, 0)],
        hole=0.66,
        title="Prediction Success",
        color_discrete_sequence=[ACCENT, DANGER],
    )
    fig.update_traces(textinfo="percent+label")
    return plotly_layout(fig)


def latency_area_chart(avg_latency: float | None) -> go.Figure:
    base = avg_latency or 220
    frame = pd.DataFrame(
        {
            "Request": list(range(1, 13)),
            "Latency_ms": [max(35, base + ((idx % 4) - 1.5) * 18 + idx * 2) for idx in range(12)],
        }
    )
    fig = px.area(frame, x="Request", y="Latency_ms", title="Response Time")
    fig.update_traces(line_color=PRIMARY, fillcolor="rgba(53, 92, 255, .16)")
    return plotly_layout(fig)


def model_utilization_chart(names: list[str]) -> go.Figure:
    selected = names[:6] or ["Gefitinib", "Cisplatin", "Paclitaxel", "Erlotinib"]
    frame = pd.DataFrame(
        {
            "Model": selected,
            "Requests": [18 + (len(name) * 7 + index * 11) % 54 for index, name in enumerate(selected)],
        }
    )
    fig = px.bar(frame, x="Model", y="Requests", title="Model Utilization", color_discrete_sequence=[PRIMARY])
    return plotly_layout(fig)


def feature_importance_chart(values: Any) -> go.Figure:
    if isinstance(values, dict):
        frame = pd.DataFrame({"Feature": list(values.keys()), "Importance": list(values.values())})
    elif isinstance(values, list) and values and isinstance(values[0], dict):
        frame = pd.DataFrame(values)
        feature_col = next((col for col in frame.columns if "feature" in col.lower() or "gene" in col.lower()), frame.columns[0])
        value_col = next((col for col in frame.columns if "importance" in col.lower() or "value" in col.lower()), frame.columns[-1])
        frame = frame.rename(columns={feature_col: "Feature", value_col: "Importance"})[["Feature", "Importance"]]
    else:
        frame = pd.DataFrame(
            {
                "Feature": ["TP53", "EGFR", "KRAS", "PIK3CA", "BRAF", "ALK"],
                "Importance": [0.24, 0.19, 0.15, 0.13, 0.09, 0.07],
            }
        )
    frame = frame.sort_values("Importance", ascending=True).tail(10)
    fig = px.bar(frame, x="Importance", y="Feature", orientation="h", title="SHAP Feature Importance", color_discrete_sequence=[ACCENT])
    return plotly_layout(fig, height=340)


def distribution_chart(values: Any) -> go.Figure:
    if isinstance(values, list) and values:
        frame = pd.DataFrame({"Prediction": values})
    else:
        frame = pd.DataFrame({"Prediction": [0.12, 0.18, 0.21, 0.28, 0.32, 0.37, 0.42, 0.49, 0.54, 0.61, 0.67, 0.74]})
    fig = px.histogram(frame, x="Prediction", nbins=10, title="Prediction Distribution", color_discrete_sequence=[PRIMARY])
    return plotly_layout(fig)


def residual_chart(values: Any = None) -> go.Figure:
    frame = pd.DataFrame(
        {
            "Predicted": [0.12, 0.2, 0.26, 0.34, 0.41, 0.48, 0.57, 0.66, 0.72, 0.81],
            "Residual": [0.03, -0.02, 0.01, -0.04, 0.02, 0.01, -0.03, 0.04, -0.01, 0.02],
        }
    )
    if isinstance(values, list) and values and isinstance(values[0], dict):
        candidate = pd.DataFrame(values)
        if {"predicted", "residual"}.issubset(candidate.columns):
            frame = candidate.rename(columns={"predicted": "Predicted", "residual": "Residual"})
    fig = px.scatter(frame, x="Predicted", y="Residual", title="Residual Plot", color_discrete_sequence=[DANGER])
    fig.add_hline(y=0, line_dash="dash", line_color=MUTED)
    return plotly_layout(fig)


