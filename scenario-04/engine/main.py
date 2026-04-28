"""
Churn Rate API — FastAPI application.
Every response carries definition_version so callers always know
which rules produced the number.
"""

from datetime import date
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from .calculator import calculate_churn_rate, ChurnResult
from .data_loader import (
    load_subscriptions,
    load_cancellations,
    load_crm_activity,
    reload_all,
)
from .definition import DEFINITION_METADATA, DEFINITION_VERSION

app = FastAPI(
    title="Churn Rate Engine",
    description="Single source of truth for SaaS churn rate — definition v1.0",
    version=DEFINITION_VERSION,
)


class ChurnResponse(BaseModel):
    definition_version: str
    calculated_at: str
    period_start: date
    period_end: date
    window: str
    segment_filter: str | None
    financial: dict
    contractual: dict
    breakdown: list[dict]
    excluded_events: dict


def _result_to_response(r: ChurnResult) -> ChurnResponse:
    return ChurnResponse(
        definition_version=r.definition_version,
        calculated_at=r.calculated_at,
        period_start=r.period_start,
        period_end=r.period_end,
        window=r.window,
        segment_filter=r.segment_filter,
        financial=r.financial,
        contractual=r.contractual,
        breakdown=r.breakdown,
        excluded_events=r.excluded_events,
    )


@app.get("/churn-rate", response_model=ChurnResponse, tags=["metrics"])
def get_churn_rate(
    period: date = Query(..., description="Reference date. For 'monthly': any day in the target month. For rolling windows: the end date."),
    window: Literal["monthly", "r30", "r90"] = Query("monthly"),
    segment: Literal["Enterprise", "Mid-market", "SMB", "all"] = Query("all"),
    cs_accountable_only: bool = Query(False, description="Exclude involuntary churn types from CS metric"),
):
    """
    Calculate churn rate for a given period, window, and segment.

    Returns both financial view (nMRR-based) and contractual view (logo-based).
    Every response is tagged with the definition version that produced it.
    """
    subs = load_subscriptions()
    cancels = load_cancellations()
    crm = load_crm_activity()

    seg = None if segment == "all" else segment

    try:
        result = calculate_churn_rate(
            subscriptions=subs,
            cancellations=cancels,
            crm_activity=crm,
            period=period,
            window=window,
            segment=seg,
            cs_accountable_only=cs_accountable_only,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return _result_to_response(result)


@app.get("/churn-rate/compare-periods", tags=["metrics"])
def compare_periods(
    period_a: date = Query(..., description="First period reference date"),
    period_b: date = Query(..., description="Second period reference date"),
    window: Literal["monthly", "r30", "r90"] = Query("monthly"),
    segment: Literal["Enterprise", "Mid-market", "SMB", "all"] = Query("all"),
):
    """
    Compare churn rate between two periods.
    Useful for trend analysis and board presentations.
    """
    subs = load_subscriptions()
    cancels = load_cancellations()
    crm = load_crm_activity()
    seg = None if segment == "all" else segment

    result_a = calculate_churn_rate(subs, cancels, crm, period_a, window, seg)
    result_b = calculate_churn_rate(subs, cancels, crm, period_b, window, seg)

    delta_financial = round(
        result_b.financial["churn_rate_pct"] - result_a.financial["churn_rate_pct"], 4
    )
    delta_contractual = round(
        result_b.contractual["churn_rate_pct"] - result_a.contractual["churn_rate_pct"], 4
    )

    return {
        "definition_version": DEFINITION_VERSION,
        "period_a": _result_to_response(result_a),
        "period_b": _result_to_response(result_b),
        "delta": {
            "financial_churn_rate_pct": delta_financial,
            "contractual_churn_rate_pct": delta_contractual,
            "direction": "worse" if delta_financial > 0 else "better" if delta_financial < 0 else "unchanged",
        },
    }


@app.get("/definitions", tags=["semantic-layer"])
def list_definitions():
    """List all available metric definition versions."""
    return {
        "available_versions": [DEFINITION_VERSION],
        "active_version": DEFINITION_VERSION,
    }


@app.get("/definitions/{version}", tags=["semantic-layer"])
def get_definition(version: str):
    """Return the full definition metadata for a given version."""
    if version != DEFINITION_VERSION:
        raise HTTPException(status_code=404, detail=f"Definition version '{version}' not found.")
    return DEFINITION_METADATA


@app.get("/definitions/{version}/explain", tags=["semantic-layer"])
def explain_calculation(version: str):
    """
    Human-readable explanation of how the churn rate is calculated.
    Designed for the NL query layer — returns structured text, not a chart.
    """
    if version != DEFINITION_VERSION:
        raise HTTPException(status_code=404, detail=f"Definition version '{version}' not found.")
    return {
        "definition_version": version,
        "formula": "Churn Rate (%) = nMRR Lost in Period / nMRR Active at Period Start × 100",
        "primary_unit": "Normalized MRR (nMRR). Annual contracts are divided by 12.",
        "canonical_churn_date": "contract_end_date — not cancellation request date, not last login.",
        "inclusions": [
            "voluntary cancellations",
            "involuntary_bankruptcy (financial view only)",
            "involuntary_ma (financial view only)",
            "material downgrades: reduction >= €50 AND >= 10% of prior nMRR",
            "pause_expiry: contractual pause exceeding 90 days",
        ],
        "exclusions": [
            "contracts with nMRR < €200 (tracked separately as micro_churn_rate)",
            "trial/promo customers until first full-price billing cycle",
            "cancellations within 14 days of automatic renewal (refund_cancellation)",
            "involuntary_fraud and involuntary_collections",
            "save reversals: customer reactivated within 30 days of contract end",
            "migration duplicate events (retry storm)",
        ],
        "views": {
            "financial": "nMRR lost / nMRR active — for board and ARR forecast",
            "contractual": "customers lost / customers active — for legal and ops tracking",
        },
        "windows": {
            "monthly": "calendar month — headline for board reporting",
            "r30": "rolling 30 days — trend monitoring",
            "r90": "rolling 90 days — CS operations (full at-risk cycle)",
        },
    }


@app.post("/admin/reload-data", tags=["admin"])
def reload_data():
    """Clear the data cache and reload CSV files from disk."""
    reload_all()
    return {"status": "cache cleared", "message": "Data will be reloaded on next request."}


@app.get("/health", tags=["admin"])
def health():
    return {"status": "ok", "definition_version": DEFINITION_VERSION}
