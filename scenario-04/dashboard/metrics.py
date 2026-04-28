"""
Metric computation layer for the dashboard.
Bridges the engine calculator with Streamlit display logic.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
import pandas as pd
import numpy as np

from engine.calculator import calculate_churn_rate, _window_bounds
from engine.data_loader import (
    load_subscriptions, load_cancellations,
    load_crm_activity, load_customers,
)
from engine.definition import DEFINITION_VERSION, MICRO_MRR_THRESHOLD


def get_churn_result(period: date, window: str, segment: str | None, cs_only: bool):
    subs = load_subscriptions()
    cancels = load_cancellations()
    crm = load_crm_activity()
    return calculate_churn_rate(subs, cancels, crm, period, window, segment, cs_only)


def get_trend(months: int, window: str, segment: str | None) -> pd.DataFrame:
    """Return monthly churn results for the last N months."""
    subs = load_subscriptions()
    cancels = load_cancellations()
    crm = load_crm_activity()

    today = date(2026, 3, 1)   # anchor to data range
    rows = []
    for i in range(months - 1, -1, -1):
        month_date = (today.replace(day=1) - timedelta(days=1) * 30 * i).replace(day=1)
        try:
            r = calculate_churn_rate(subs, cancels, crm, month_date, window, segment)
            rows.append({
                "period": month_date,
                "label": month_date.strftime("%b %Y"),
                "financial_rate": r.financial["churn_rate_pct"],
                "contractual_rate": r.contractual["churn_rate_pct"],
                "mrr_lost": r.financial["mrr_lost"],
                "customers_lost": r.contractual["customers_lost"],
            })
        except Exception:
            pass
    return pd.DataFrame(rows)


def get_breakdown(period: date, window: str) -> pd.DataFrame:
    result = get_churn_result(period, window, None, False)
    return pd.DataFrame(result.breakdown)


def get_segment_breakdown(period: date, window: str) -> list[dict]:
    """Real per-segment churn — calls the engine once per segment."""
    rows = []
    for seg in ["Enterprise", "Mid-market", "SMB"]:
        r = get_churn_result(period, window, seg, False)
        rows.append({
            "segment": seg,
            "churn_rate_pct": r.financial["churn_rate_pct"],
            "mrr_lost": r.financial["mrr_lost"],
            "mrr_active": r.financial["mrr_active_start"],
            "customers_lost": r.contractual["customers_lost"],
        })
    return rows


def get_at_risk_contracts(as_of: date, horizon_days: int = 90) -> pd.DataFrame:
    """
    Subscriptions expiring within horizon_days with a risk score.
    Risk: RED = expiry ≤30d AND no login in 30d; YELLOW = one condition; GREEN = neither.
    """
    subs = load_subscriptions()
    customers = load_customers()

    horizon_end = as_of + timedelta(days=horizon_days)
    at_risk = subs[
        subs["end_date"].notna()
        & (subs["end_date"] >= as_of)
        & (subs["end_date"] <= horizon_end)
        & (subs["mrr"] >= MICRO_MRR_THRESHOLD)
        & (subs["status"].isin(["active", "at_risk", "paused"]))
    ].copy()

    at_risk = at_risk.merge(
        customers[["customer_id", "company_name", "segment", "csm_owner"]],
        on="customer_id", how="left"
    )

    # Simulate last_login_days_ago (no event log in dataset)
    np.random.seed(42)
    at_risk["last_login_days"] = np.random.choice(
        [2, 5, 8, 12, 15, 22, 30, 42, 55, 70], size=len(at_risk)
    )

    days_to_expiry = (pd.to_datetime(at_risk["end_date"]) - pd.Timestamp(as_of)).dt.days
    at_risk["days_to_expiry"] = days_to_expiry

    def risk_score(row):
        near_expiry = row["days_to_expiry"] <= 30
        inactive = row["last_login_days"] >= 30
        if near_expiry and inactive:
            return "🔴 Alto"
        elif near_expiry or inactive:
            return "🟡 Medio"
        return "🟢 Basso"

    at_risk["risk"] = at_risk.apply(risk_score, axis=1)

    return at_risk[[
        "company_name", "segment", "mrr", "end_date",
        "days_to_expiry", "last_login_days", "risk", "csm_owner"
    ]].sort_values("days_to_expiry")


HISTORICAL_DATA = [
    {"period": "Q1 2021", "board_rate": 1.8,  "canonical_rate": 2.2, "method": "D0 — Logo churn",     "note": ""},
    {"period": "Q2 2021", "board_rate": 2.1,  "canonical_rate": 2.5, "method": "D0 — Logo churn",     "note": ""},
    {"period": "Q3 2021", "board_rate": 1.9,  "canonical_rate": 2.3, "method": "D0 — Logo churn",     "note": "⚠️ PDF source"},
    {"period": "Q4 2021", "board_rate": 2.4,  "canonical_rate": 2.8, "method": "D0 — Logo churn",     "note": "⚠️ PDF source"},
    {"period": "Q1 2022", "board_rate": 2.2,  "canonical_rate": 2.6, "method": "D0 — Logo churn",     "note": ""},
    {"period": "Q2 2022", "board_rate": 2.0,  "canonical_rate": 2.4, "method": "D0 — Logo churn",     "note": ""},
    {"period": "Q3 2022", "board_rate": 2.3,  "canonical_rate": 2.7, "method": "D0 — Logo churn",     "note": ""},
    {"period": "Q4 2022", "board_rate": 2.6,  "canonical_rate": 3.0, "method": "D0 — Logo churn",     "note": ""},
    {"period": "Q1 2023", "board_rate": 3.1,  "canonical_rate": 3.5, "method": "D0 — Logo churn",     "note": ""},
    {"period": "Q2 2023", "board_rate": 2.8,  "canonical_rate": 3.2, "method": "D1 — Logo+downgrade", "note": "Metodo cambiato"},
    {"period": "Q3 2023", "board_rate": 3.4,  "canonical_rate": 3.8, "method": "D1 — Logo+downgrade", "note": ""},
    {"period": "Q4 2023", "board_rate": 2.9,  "canonical_rate": 3.3, "method": "D1 — Logo+downgrade", "note": ""},
    {"period": "Q1 2024", "board_rate": 2.1,  "canonical_rate": 2.5, "method": "D2 — MRR grezzo",     "note": "⚠️ Cambio CFO = cambio metodo"},
    {"period": "Q2 2024", "board_rate": 1.9,  "canonical_rate": 2.3, "method": "D2 — MRR grezzo",     "note": ""},
    {"period": "Q3 2024", "board_rate": 2.0,  "canonical_rate": 2.4, "method": "D2 — MRR grezzo",     "note": ""},
    {"period": "Q4 2024", "board_rate": 2.2,  "canonical_rate": 2.6, "method": "D2 — MRR grezzo",     "note": ""},
    {"period": "Q1 2025", "board_rate": 1.8,  "canonical_rate": 2.2, "method": "D2 — MRR grezzo",     "note": ""},
    {"period": "Q2 2025", "board_rate": 5.8,  "canonical_rate": 2.1, "method": "D3 — MRR+duplicati",  "note": "❌ Bug: 340 duplicati"},
    {"period": "Q3 2025", "board_rate": 2.3,  "canonical_rate": 2.7, "method": "D2 — MRR grezzo",     "note": ""},
    {"period": "Q4 2025", "board_rate": 2.7,  "canonical_rate": 3.1, "method": "D2 — MRR grezzo",     "note": ""},
]
