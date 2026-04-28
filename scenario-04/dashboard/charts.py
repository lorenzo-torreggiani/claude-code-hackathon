"""
Chart builders — all return plotly figures.
One color = one meaning: red=problem, yellow=warning, green=ok.
No pie charts. No animations.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

ALERT_THRESHOLD = 1.8
COLOR_FINANCIAL = "#1f77b4"
COLOR_CONTRACTUAL = "#aec7e8"
COLOR_ALERT = "#d62728"
COLOR_GRID = "#e0e0e0"


def trend_chart(df: pd.DataFrame, view: str, alert_threshold: float = ALERT_THRESHOLD) -> go.Figure:
    rate_col = "financial_rate" if view == "Financial" else "contractual_rate"
    mrr_col  = "mrr_lost"
    unit_label = "nMRR Churn Rate (%)" if view == "Financial" else "Logo Churn Rate (%)"
    color = COLOR_FINANCIAL if view == "Financial" else COLOR_CONTRACTUAL

    fig = go.Figure()

    # Primary line — churn rate
    fig.add_trace(go.Scatter(
        x=df["label"], y=df[rate_col],
        mode="lines+markers+text",
        name=unit_label,
        line=dict(color=color, width=2),
        marker=dict(size=7),
        text=df[rate_col].apply(lambda v: f"{v:.2f}%"),
        textposition="top center",
        textfont=dict(size=10, color="#111111"),
        yaxis="y1",
        hovertemplate="<b>%{x}</b><br>Churn rate: %{y:.2f}%<extra></extra>",
    ))

    # Secondary bars — MRR lost (only in financial view)
    if view == "Financial" and mrr_col in df.columns:
        fig.add_trace(go.Bar(
            x=df["label"], y=df[mrr_col],
            name="MRR Lost (€)",
            marker_color="rgba(31,119,180,0.15)",
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>MRR lost: €%{y:,.0f}<extra></extra>",
        ))

    # Alert threshold line
    fig.add_hline(
        y=alert_threshold,
        line_dash="dash",
        line_color=COLOR_ALERT,
        annotation_text=f"Alert {alert_threshold}%",
        annotation_position="top right",
        annotation_font_color=COLOR_ALERT,
        annotation_font_size=11,
    )

    fig.update_layout(
        height=280,
        margin=dict(l=0, r=60, t=10, b=50),
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(
            gridcolor=COLOR_GRID,
            title=dict(text="Churn rate (%)", font=dict(color=color)),
            tickfont=dict(color="#111111"),
        ),
        yaxis2=dict(
            title=dict(text="MRR lost (€)", font=dict(color="#555555", size=11)),
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="#555555", size=10),
        ),
        xaxis=dict(
            gridcolor=COLOR_GRID,
            title=dict(text="Periodo", font=dict(color="#111111")),
            tickmode="array",
            tickvals=df["label"].iloc[::2].tolist(),
            tickangle=-45,
            tickfont=dict(size=9, color="#111111"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            font=dict(size=11, color="#111111"),
        ),
        font=dict(size=12, color="#111111"),
        barmode="overlay",
    )
    return fig


def segment_bar(segment_data: list[dict]) -> go.Figure:
    """Fix 1 — accepts real per-segment data from the engine, not estimates."""
    if not segment_data:
        fig = go.Figure()
        fig.update_layout(height=220, annotations=[dict(text="No data", showarrow=False)])
        return fig

    df = pd.DataFrame(segment_data)
    total_mrr = df["mrr_lost"].sum()
    df["pct"] = (df["mrr_lost"] / total_mrr * 100).round(1) if total_mrr > 0 else 0.0

    colors = {"Enterprise": "#1f77b4", "Mid-market": "#ff7f0e", "SMB": "#2ca02c"}
    fig = go.Figure(go.Bar(
        x=df["segment"],
        y=df["churn_rate_pct"],
        marker_color=[colors.get(s, "#7f7f7f") for s in df["segment"]],
        text=df["churn_rate_pct"].apply(lambda v: f"{v:.2f}%"),
        textposition="outside",
        textfont=dict(color="#111111", size=11),
        customdata=df[["mrr_lost", "mrr_active"]].values,
        hovertemplate=(
            "%{x}<br>Churn rate: %{y:.2f}%<br>"
            "MRR lost: €%{customdata[0]:,.0f}<br>"
            "MRR active: €%{customdata[1]:,.0f}<extra></extra>"
        ),
    ))
    fig.update_layout(
        height=220, margin=dict(l=0, r=0, t=20, b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor=COLOR_GRID, title="Churn rate (%)", tickfont=dict(color="#111111")),
        xaxis=dict(gridcolor=COLOR_GRID, title="Segmento", tickfont=dict(color="#111111")),
        font=dict(color="#111111"),
        showlegend=False,
    )
    return fig


def churn_type_bar(df_breakdown: pd.DataFrame) -> go.Figure:
    if df_breakdown.empty or "churn_type" not in df_breakdown.columns:
        fig = go.Figure()
        fig.update_layout(height=220, annotations=[dict(text="No data", showarrow=False)])
        return fig

    total = df_breakdown["count"].sum() if "count" in df_breakdown.columns else 1
    df_breakdown = df_breakdown.copy()
    df_breakdown["pct"] = (df_breakdown.get("count", 1) / total * 100).round(1)

    type_colors = {
        "voluntary":              "#1f77b4",
        "involuntary_bankruptcy": "#ff7f0e",
        "involuntary_ma":         "#9467bd",
        "contraction":            "#e377c2",
        "pause_expiry":           "#bcbd22",
    }
    colors = [type_colors.get(t, "#7f7f7f") for t in df_breakdown["churn_type"]]

    fig = go.Figure(go.Bar(
        x=df_breakdown["churn_type"].str.replace("_", " ").str.title(),
        y=df_breakdown["pct"],
        marker_color=colors,
        text=df_breakdown["pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        textfont=dict(color="#111111", size=11),
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        height=220, margin=dict(l=0, r=0, t=20, b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor=COLOR_GRID, title="% eventi", tickfont=dict(color="#111111")),
        xaxis=dict(gridcolor=COLOR_GRID, title="Tipo di churn", tickfont=dict(color="#111111")),
        font=dict(color="#111111"),
        showlegend=False,
    )
    return fig


def historical_chart(historical_data: list[dict]) -> go.Figure:
    df = pd.DataFrame(historical_data)

    fig = go.Figure()

    bug_mask = df["board_rate"] > 4
    normal_mask = ~bug_mask

    fig.add_trace(go.Scatter(
        x=df.loc[normal_mask, "period"],
        y=df.loc[normal_mask, "board_rate"],
        mode="lines+markers",
        name="Presentato al board",
        line=dict(color="#aec7e8", width=2, dash="dot"),
        marker=dict(size=6, symbol="circle-open"),
    ))

    if bug_mask.any():
        fig.add_trace(go.Scatter(
            x=df.loc[bug_mask, "period"],
            y=df.loc[bug_mask, "board_rate"],
            mode="markers",
            name="Bug (D3 duplicati)",
            marker=dict(size=12, color=COLOR_ALERT, symbol="x"),
        ))

    fig.add_trace(go.Scatter(
        x=df["period"], y=df["canonical_rate"],
        mode="lines+markers",
        name="Canonical D4 (reale)",
        line=dict(color=COLOR_FINANCIAL, width=2),
        marker=dict(size=7),
    ))

    # Fix 4 — explicit method change annotations with full labels
    fig.add_vrect(
        x0="Q1 2021", x1="Q1 2023", fillcolor="#aec7e8",
        opacity=0.07, line_width=0,
        annotation_text="D0: Logo churn", annotation_position="top left",
        annotation_font_size=10, annotation_font_color="#111111",
    )
    fig.add_vrect(
        x0="Q2 2023", x1="Q4 2023", fillcolor="orange",
        opacity=0.08, line_width=0,
        annotation_text="D1: Logo+downgrade", annotation_position="top left",
        annotation_font_size=10, annotation_font_color="#111111",
    )
    fig.add_vrect(
        x0="Q1 2024", x1="Q1 2025", fillcolor="#2ca02c",
        opacity=0.05, line_width=0,
        annotation_text="D2: MRR grezzo", annotation_position="top left",
        annotation_font_size=10, annotation_font_color="#111111",
    )
    fig.add_vrect(
        x0="Q2 2025", x1="Q4 2025", fillcolor="#d62728",
        opacity=0.05, line_width=0,
        annotation_text="D3: MRR+duplicati", annotation_position="top left",
        annotation_font_size=10, annotation_font_color="#111111",
    )

    fig.update_layout(
        height=300, margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor=COLOR_GRID, title="Churn Rate (%)", tickfont=dict(color="#111111")),
        xaxis=dict(gridcolor=COLOR_GRID, tickangle=-45, tickfont=dict(size=10, color="#111111")),
        legend=dict(
            orientation="h",
            yanchor="top", y=-0.15,
            xanchor="left", x=0,
            font=dict(color="#111111", size=11),
        ),
        font=dict(size=11, color="#111111"),
    )
    return fig
