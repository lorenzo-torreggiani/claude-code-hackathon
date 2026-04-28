"""
Tool definitions and handlers for the NL query layer.
Claude calls these tools to answer questions about the semantic layer.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
from datetime import date

from engine.calculator import calculate_churn_rate
from engine.data_loader import load_subscriptions, load_cancellations, load_crm_activity
from engine.definition import DEFINITION_METADATA, DEFINITION_VERSION

# ---------------------------------------------------------------------------
# Tool schemas (passed to Claude API)
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "name": "get_metric",
        "description": (
            "Calculate the churn rate for a given period, window, and segment. "
            "Returns both financial (nMRR) and contractual (logo) views, "
            "plus breakdown by churn type and excluded events. "
            "Every response is tagged with the definition version that produced it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "description": "Reference date in ISO format (YYYY-MM-DD). For monthly window: any day in the target month.",
                },
                "window": {
                    "type": "string",
                    "enum": ["monthly", "r30", "r90"],
                    "description": "Calculation window. monthly=calendar month, r30=rolling 30d, r90=rolling 90d.",
                },
                "segment": {
                    "type": "string",
                    "enum": ["Enterprise", "Mid-market", "SMB", "all"],
                    "description": "Customer segment filter. Use 'all' for no filter.",
                },
                "cs_accountable_only": {
                    "type": "boolean",
                    "description": "If true, exclude involuntary churn types (bankruptcy, M&A, fraud, collections) from the result.",
                },
            },
            "required": ["period"],
        },
    },
    {
        "name": "compare_periods",
        "description": (
            "Compare churn rate between two periods. "
            "Returns the result for each period plus the delta (positive=worse, negative=better)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "period_a": {
                    "type": "string",
                    "description": "First period reference date (ISO format).",
                },
                "period_b": {
                    "type": "string",
                    "description": "Second period reference date (ISO format).",
                },
                "window": {
                    "type": "string",
                    "enum": ["monthly", "r30", "r90"],
                    "description": "Calculation window.",
                },
                "segment": {
                    "type": "string",
                    "enum": ["Enterprise", "Mid-market", "SMB", "all"],
                },
            },
            "required": ["period_a", "period_b"],
        },
    },
    {
        "name": "list_definitions",
        "description": "List all available metric definition versions and which one is currently active.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "explain_calculation",
        "description": (
            "Return a human-readable explanation of how the churn rate is calculated "
            "under a specific definition version, including all thresholds, inclusions, "
            "exclusions, and boundary examples."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "version": {
                    "type": "string",
                    "description": "Definition version (e.g. '1.0').",
                },
            },
            "required": ["version"],
        },
    },
]

# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

def _date(s: str) -> date:
    return date.fromisoformat(s)


def handle_get_metric(inputs: dict) -> dict:
    period = _date(inputs["period"])
    window = inputs.get("window", "monthly")
    seg_raw = inputs.get("segment", "all")
    segment = None if seg_raw == "all" else seg_raw
    cs_only = inputs.get("cs_accountable_only", False)

    subs = load_subscriptions()
    cancels = load_cancellations()
    crm = load_crm_activity()

    r = calculate_churn_rate(subs, cancels, crm, period, window, segment, cs_only)
    return {
        "definition_version": r.definition_version,
        "period_start": str(r.period_start),
        "period_end": str(r.period_end),
        "window": r.window,
        "segment_filter": r.segment_filter,
        "financial": r.financial,
        "contractual": r.contractual,
        "breakdown": r.breakdown,
        "excluded_events": r.excluded_events,
    }


def handle_compare_periods(inputs: dict) -> dict:
    period_a = _date(inputs["period_a"])
    period_b = _date(inputs["period_b"])
    window = inputs.get("window", "monthly")
    seg_raw = inputs.get("segment", "all")
    segment = None if seg_raw == "all" else seg_raw

    subs = load_subscriptions()
    cancels = load_cancellations()
    crm = load_crm_activity()

    ra = calculate_churn_rate(subs, cancels, crm, period_a, window, segment)
    rb = calculate_churn_rate(subs, cancels, crm, period_b, window, segment)

    delta = round(rb.financial["churn_rate_pct"] - ra.financial["churn_rate_pct"], 4)
    return {
        "definition_version": DEFINITION_VERSION,
        "period_a": {"period": str(ra.period_start), "financial": ra.financial, "contractual": ra.contractual},
        "period_b": {"period": str(rb.period_start), "financial": rb.financial, "contractual": rb.contractual},
        "delta_financial_pct": delta,
        "direction": "worse" if delta > 0 else "better" if delta < 0 else "unchanged",
    }


def handle_list_definitions(_: dict) -> dict:
    return {"available_versions": [DEFINITION_VERSION], "active_version": DEFINITION_VERSION}


def handle_explain_calculation(inputs: dict) -> dict:
    version = inputs.get("version", DEFINITION_VERSION)
    if version != DEFINITION_VERSION:
        return {"error": f"Version '{version}' not found. Available: {DEFINITION_VERSION}"}
    return {
        "definition_version": version,
        "formula": "Churn Rate (%) = nMRR Lost in Period / nMRR Active at Period Start × 100",
        "primary_unit": "nMRR. Annual contracts divided by 12 — no spike at expiration.",
        "canonical_churn_date": "contract_end_date (not cancellation request date, not last login).",
        "inclusions": [
            "voluntary cancellations",
            "involuntary_bankruptcy and involuntary_ma (financial view only)",
            "material downgrades: reduction ≥ €50 AND ≥ 10% of prior nMRR",
            "pause_expiry: contractual pause exceeding 90 days",
        ],
        "exclusions": [
            "contracts with nMRR < €200 (tracked in micro_churn_rate)",
            "trial/promo customers until first full-price billing cycle (discount < 50%)",
            "cancellations within 14 days of automatic renewal (refund_cancellation)",
            "involuntary_fraud and involuntary_collections",
            "save reversals: reactivation within 30 days of contract_end_date",
            "migration duplicate events (retry storm — automated exclusion)",
        ],
        "boundary_examples": {
            "downgrade_yes": "€2,000 → €1,800 (−€200, −10%): BOTH thresholds met → contraction churn",
            "downgrade_no": "€600 → €560 (−€40, −6.7%): delta < €50 → NOT churn",
            "save_yes": "Contract ends 2026-03-31, reactivates 2026-04-15 (15 days): SAVE — churn reversed",
            "save_no": "Contract ends 2026-03-31, reactivates 2026-05-15 (45 days): CHURN stands",
            "annual_contract": "€24,000/year not renewed → €2,000/month churn × 12 months (NOT €24,000 spike)",
            "micro": "€19/month subscription cancelled → excluded from headline, tracked in micro_churn_rate",
        },
        "thresholds": DEFINITION_METADATA["thresholds"],
        "note_q2_2025": (
            "The 5.8% figure presented to the board in Q2 2025 was a data quality error: "
            "340 duplicate cancellation events from a CRM migration retry storm were included. "
            "The canonical D4 figure for Q2 2025 is 2.1%. No formal correction has been issued."
        ),
    }


HANDLERS = {
    "get_metric": handle_get_metric,
    "compare_periods": handle_compare_periods,
    "list_definitions": handle_list_definitions,
    "explain_calculation": handle_explain_calculation,
}


def dispatch(tool_name: str, tool_input: dict) -> str:
    handler = HANDLERS.get(tool_name)
    if not handler:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    try:
        result = handler(tool_input)
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})
