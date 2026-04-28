"""
Challenge 5 — The One Dashboard.
Replaces 40 dashboards across 3 BI tools with a single source of truth.
Every number carries definition_version so the board always knows what they're looking at.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date
import pandas as pd
import streamlit as st

from engine.data_loader import load_subscriptions, load_customers
from engine.definition import DEFINITION_VERSION, DEFINITION_METADATA, DEFINITION_DATE
from dashboard.metrics import (
    get_churn_result, get_trend, get_breakdown,
    get_at_risk_contracts, get_segment_breakdown, HISTORICAL_DATA,
)
from dashboard.charts import (
    trend_chart, segment_bar, churn_type_bar, historical_chart,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Churn Rate Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .metric-card {
        background: #f8f9fa; border-radius: 8px;
        padding: 1rem; border-left: 4px solid #1f77b4;
    }
    .metric-label { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #111; }
    .metric-delta-pos { font-size: 0.85rem; color: #d62728; }
    .metric-delta-neg { font-size: 0.85rem; color: #2ca02c; }
    .section-title { font-size: 0.9rem; font-weight: 600; color: #444;
                     text-transform: uppercase; letter-spacing: 0.05em;
                     margin-bottom: 0.5rem; margin-top: 0.5rem; }
    .footer-bar { background: #f0f2f6; border-radius: 6px; padding: 0.5rem 1rem;
                  font-size: 0.75rem; color: #555; margin-top: 1rem; }
    .risk-red { color: #d62728; font-weight: 600; }
    .risk-yellow { color: #ff7f0e; }
    .risk-green { color: #2ca02c; }
    div[data-testid="stMetricDelta"] { font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 1 — Header + controls
# ---------------------------------------------------------------------------

col_title, col_ver = st.columns([5, 1])
with col_title:
    st.markdown("## Churn Rate Dashboard")
with col_ver:
    st.markdown(
        f"<div style='text-align:right; padding-top:1rem; font-size:0.75rem; color:#888'>"
        f"definition <b>v{DEFINITION_VERSION}</b><br>{date.today().strftime('%d %b %Y')}</div>",
        unsafe_allow_html=True,
    )

ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = st.columns([2, 2, 2, 2, 2])
with ctrl1:
    view = st.radio("Vista", ["Financial", "Contractual"], horizontal=True)
with ctrl2:
    window = st.selectbox("Window", ["monthly", "r30", "r90"],
                          format_func=lambda x: {"monthly": "Monthly", "r30": "Rolling 30d", "r90": "Rolling 90d"}[x])
with ctrl3:
    segment_opt = st.selectbox("Segmento", ["Tutti", "Enterprise", "Mid-market", "SMB"])
    segment = None if segment_opt == "Tutti" else segment_opt
with ctrl4:
    cs_only = st.toggle("Solo CS-accountable", value=False)
with ctrl5:
    period = st.date_input("Periodo", value=date(2026, 3, 1))

st.divider()

# ---------------------------------------------------------------------------
# 2 — Compute current + previous period
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300)
def cached_result(p, w, s, cs):
    return get_churn_result(p, w, s, cs)

@st.cache_data(ttl=300)
def cached_trend(w, s):
    return get_trend(12, w, s)

@st.cache_data(ttl=300)
def cached_breakdown(p, w):
    return get_breakdown(p, w)

@st.cache_data(ttl=300)
def cached_segment_breakdown(p, w):
    return get_segment_breakdown(p, w)

result = cached_result(period, window, segment, cs_only)

from datetime import timedelta
prev_period = (period.replace(day=1) - timedelta(days=1)).replace(day=1)
prev_result = cached_result(prev_period, window, segment, cs_only)

fin = result.financial
con = result.contractual
prev_fin = prev_result.financial
prev_con = prev_result.contractual

delta_rate = round(fin["churn_rate_pct"] - prev_fin["churn_rate_pct"], 2)
delta_mrr  = round(fin["mrr_lost"] - prev_fin["mrr_lost"], 0)
delta_logo = round(con["churn_rate_pct"] - prev_con["churn_rate_pct"], 2)

# ---------------------------------------------------------------------------
# 3 — KPI cards row 1
# ---------------------------------------------------------------------------

st.markdown('<div class="section-title">Headline KPIs</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5, k6 = st.columns(6)

rate_val = fin["churn_rate_pct"] if view == "Financial" else con["churn_rate_pct"]
rate_delta = delta_rate if view == "Financial" else delta_logo
rate_label = "nMRR Churn Rate" if view == "Financial" else "Logo Churn Rate"

with k1:
    st.metric(
        label=rate_label,
        value=f"{rate_val:.2f}%",
        delta=f"{rate_delta:+.2f}pp vs M-1",
        delta_color="inverse",
    )
with k2:
    st.metric(
        label="MRR Lost",
        value=f"€{fin['mrr_lost']:,.0f}",
        delta=f"€{delta_mrr:+,.0f} vs M-1",
        delta_color="inverse",
    )
with k3:
    st.metric(
        label="MRR Active (start)",
        value=f"€{fin['mrr_active_start']:,.0f}",
    )
with k4:
    st.metric(
        label="Logo Churn Rate",
        value=f"{con['churn_rate_pct']:.2f}%",
        delta=f"{delta_logo:+.2f}pp vs M-1",
        delta_color="inverse",
        help="Secondary metric (customer count). Not the headline.",
    )
with k5:
    crm = load_customers()
    saves = result.excluded_events.get("save_reversals", 0)
    st.metric(label="CS Saves", value=f"{saves}", help="Churn events reversed by CS retention activity")
with k6:
    excl = result.excluded_events.get("admin_cancellations", 0) + result.excluded_events.get("micro_contracts", 0)
    st.metric(
        label="Excluded Events",
        value=f"{excl}",
        help=f"Admin cancellations: {result.excluded_events.get('admin_cancellations',0)} | Micro contracts: {result.excluded_events.get('micro_contracts',0)}",
    )

st.divider()

# ---------------------------------------------------------------------------
# 4 — Trend chart
# ---------------------------------------------------------------------------

st.markdown('<div class="section-title">Trend — ultimi 12 mesi</div>', unsafe_allow_html=True)

trend_df = cached_trend(window, segment)
if not trend_df.empty:
    st.plotly_chart(trend_chart(trend_df, view), use_container_width=True)
else:
    st.info("Dati insufficienti per il trend nel range selezionato.")

st.divider()

# ---------------------------------------------------------------------------
# 5 — Breakdown: segment + churn type
# ---------------------------------------------------------------------------

st.markdown('<div class="section-title">Breakdown</div>', unsafe_allow_html=True)

b1, b2 = st.columns(2)
breakdown_df = cached_breakdown(period, window)
seg_data = cached_segment_breakdown(period, window)   # Fix 1 — real data per segment

with b1:
    st.markdown("**Per segmento**")
    st.plotly_chart(segment_bar(seg_data), use_container_width=True)

with b2:
    st.markdown("**Per tipo di churn**")
    st.plotly_chart(churn_type_bar(breakdown_df), use_container_width=True)
    n_events = int(breakdown_df["count"].sum()) if not breakdown_df.empty and "count" in breakdown_df.columns else 0
    st.caption(f"Basato su {n_events} eventi nel periodo selezionato (definition v{DEFINITION_VERSION})")

st.divider()

# ---------------------------------------------------------------------------
# 6 — At-risk contracts
# ---------------------------------------------------------------------------

st.markdown('<div class="section-title">Contratti a rischio — prossimi 90 giorni</div>', unsafe_allow_html=True)

at_risk_df = get_at_risk_contracts(period)

if at_risk_df.empty:
    st.success("Nessun contratto a rischio nei prossimi 90 giorni.")
else:
    total_at_risk_mrr = at_risk_df["mrr"].sum()
    high_risk_mrr = at_risk_df.loc[at_risk_df["risk"].str.startswith("🔴"), "mrr"].sum()
    ar1, ar2, ar3 = st.columns(3)
    with ar1:
        st.metric("Totale nMRR a rischio", f"€{total_at_risk_mrr:,.0f}")
    with ar2:
        st.metric("nMRR rischio alto 🔴", f"€{high_risk_mrr:,.0f}")
    with ar3:
        st.metric("Contratti a rischio", len(at_risk_df))

    show_all = st.toggle("Mostra tutti", value=False)
    display_df = at_risk_df if show_all else at_risk_df.head(10)

    # Fix 5 — CSM in default view, before Risk column
    display_df = display_df.rename(columns={
        "company_name": "Cliente",
        "segment": "Segmento",
        "mrr": "nMRR (€)",
        "end_date": "Scadenza",
        "days_to_expiry": "Giorni alla scadenza",
        "last_login_days": "Ultimo login (gg fa)",
        "risk": "Risk",
        "csm_owner": "CSM",
    })
    # Reorder: CSM before Risk
    ordered_cols = ["Cliente", "Segmento", "nMRR (€)", "Scadenza",
                    "Giorni alla scadenza", "Ultimo login (gg fa)", "CSM", "Risk"]
    display_df = display_df[[c for c in ordered_cols if c in display_df.columns]]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "nMRR (€)": st.column_config.NumberColumn(format="€%.0f"),
            "Scadenza": st.column_config.DateColumn(),
        }
    )
    st.caption(f"Mostrati {len(display_df)} di {len(at_risk_df)} contratti a rischio.")

st.divider()

# ---------------------------------------------------------------------------
# 7 — Historical comparison (Finance view)
# ---------------------------------------------------------------------------

with st.expander("Storico 5 anni — Confronto definizioni (Finance view)", expanded=False):
    st.markdown("""
    Ogni trimestre mostra il numero presentato al board con la definizione in uso in quel momento
    e la stima retroattiva con la definizione canonica **v1.0**.
    Le colonne non sono comparabili tra loro — il metodo è cambiato 3 volte.
    """)

    st.plotly_chart(historical_chart(HISTORICAL_DATA), use_container_width=True)

    hist_df = pd.DataFrame(HISTORICAL_DATA)
    hist_df["delta_pp"] = (hist_df["canonical_rate"] - hist_df["board_rate"]).round(2)
    hist_df = hist_df.rename(columns={
        "period": "Trimestre",
        "board_rate": "Presentato al board (%)",
        "canonical_rate": "Canonical D4 (%)",
        "method": "Metodo usato",
        "delta_pp": "Delta (pp)",
        "note": "Note",
    })

    st.dataframe(
        hist_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Delta (pp)": st.column_config.NumberColumn(format="%.2f"),
        }
    )
    st.caption("⚠️ Q3–Q4 2021: sorgente PDF — dati non auditabili. ❌ Q2 2025: bug duplicati CRM — rettifica non ancora emessa.")

st.divider()

# ---------------------------------------------------------------------------
# 8 — Glossary inline
# ---------------------------------------------------------------------------

with st.expander("Glossario — definizione v1.0", expanded=False):
    thresholds = DEFINITION_METADATA["thresholds"]
    # Fix 6 — show approval date prominently
    st.caption(f"Versione **{DEFINITION_VERSION}** — approvata il **{DEFINITION_DATE}**")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
**Churn Rate (headline)**
`nMRR Lost / nMRR Active × 100`
Vista primaria: Financial (nMRR). Vista secondaria: Contractual (logo).

**nMRR**
Contratti mensili: valore diretto.
Contratti annuali: valore ÷ 12.

**Data canonica di churn**
`contract_end_date` — non la data di cancellazione, non l'ultimo login.

**Contraction churn (downgrade)**
Conta se riduzione >= €{thresholds['downgrade_delta_min_eur']} **E** >= {int(thresholds['downgrade_delta_min_pct']*100)}% del nMRR precedente.
        """)
    with col_b:
        st.markdown(f"""
**Soglia micro-contratti**
Contratti < €{thresholds['micro_mrr_threshold_eur']}/mese esclusi dall'headline.
Tracciati in `micro_churn_rate` separato.

**Save reversal**
Riattivazione entro {thresholds['save_window_days']} giorni dalla fine contratto = churn annullato.

**Grace period post-rinnovo**
Cancellazione entro {thresholds['renewal_grace_days']} giorni da rinnovo automatico = rimborso, non churn.

**Pausa contrattuale**
At-risk fino a {thresholds['pause_max_days']} giorni. Dopo = churn automatico (`pause_expiry`).
        """)

# ---------------------------------------------------------------------------
# 9 — Footer
# ---------------------------------------------------------------------------

st.markdown(
    f"""<div class="footer-bar">
    <b>definition v{result.definition_version}</b> &nbsp;|&nbsp;
    calcolato: {result.calculated_at} &nbsp;|&nbsp;
    periodo: {result.period_start} → {result.period_end} &nbsp;|&nbsp;
    window: {result.window} &nbsp;|&nbsp;
    segmento: {result.segment_filter or 'tutti'}
    </div>""",
    unsafe_allow_html=True,
)

col_exp1, col_exp2, _ = st.columns([1, 1, 4])
with col_exp1:
    # Fix 2 — full ChurnResult export including breakdown and excluded_events
    export_rows = []
    for r_period in (cached_trend(window, segment)["period"].tolist() if not trend_df.empty else []):
        r = cached_result(r_period, window, segment, cs_only)
        base = {
            "definition_version": r.definition_version,
            "period_start": r.period_start,
            "period_end": r.period_end,
            "window": r.window,
            "segment_filter": r.segment_filter or "all",
            **{f"financial_{k}": v for k, v in r.financial.items()},
            **{f"contractual_{k}": v for k, v in r.contractual.items()},
            "excluded_admin": r.excluded_events.get("admin_cancellations", 0),
            "excluded_micro": r.excluded_events.get("micro_contracts", 0),
            "save_reversals": r.excluded_events.get("save_reversals", 0),
        }
        export_rows.append(base)
    if not export_rows:
        # Fallback: export at least the current period result
        export_rows = [{
            "definition_version": result.definition_version,
            "period_start": result.period_start,
            "period_end": result.period_end,
            "window": result.window,
            "segment_filter": result.segment_filter or "all",
            **{f"financial_{k}": v for k, v in result.financial.items()},
            **{f"contractual_{k}": v for k, v in result.contractual.items()},
            "excluded_admin": result.excluded_events.get("admin_cancellations", 0),
            "excluded_micro": result.excluded_events.get("micro_contracts", 0),
            "save_reversals": result.excluded_events.get("save_reversals", 0),
        }]
    full_csv = pd.DataFrame(export_rows).to_csv(index=False)
    st.download_button("Esporta CSV forecast", full_csv, "churn_full_export.csv", "text/csv")
with col_exp2:
    reconciliation_path = os.path.join(
        os.path.dirname(__file__), "..", "challenge-06-reconciliation.md"
    )
    if os.path.exists(reconciliation_path):
        with open(reconciliation_path, "r", encoding="utf-8") as f:
            st.download_button("Scarica riconciliazione", f.read(),
                               "reconciliation.md", "text/markdown")
