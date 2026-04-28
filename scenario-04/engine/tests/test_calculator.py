"""
Unit tests for the churn rate calculator — definition v1.0.
Each test corresponds to a specific rule in challenge-03-metric-definition.md.
"""

from datetime import date

import pandas as pd
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from engine.calculator import (
    calculate_churn_rate,
    _window_bounds,
    _active_subscriptions,
    _churn_events_in_window,
    _nMRR_active,
    _nMRR_lost,
)
from engine.definition import (
    DEFINITION_VERSION,
    MICRO_MRR_THRESHOLD,
    SAVE_WINDOW_DAYS,
    RENEWAL_GRACE_DAYS,
    HEADLINE_CHURN_TYPES,
    EXCLUDED_CHURN_TYPES,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_sub(sub_id, customer_id, mrr, start, end=None, status="active", billing_cycle="monthly"):
    return {
        "subscription_id": sub_id,
        "customer_id": customer_id,
        "mrr": mrr,
        "start_date": date.fromisoformat(start),
        "end_date": date.fromisoformat(end) if end else None,
        "status": status,
        "billing_cycle": billing_cycle,
    }


def make_event(event_id, sub_id, customer_id, end_date, churn_type="voluntary", is_dupe=False):
    return {
        "event_id": event_id,
        "subscription_id": sub_id,
        "customer_id": customer_id,
        "contract_end_date": date.fromisoformat(end_date),
        "churn_type": churn_type,
        "is_migration_duplicate": is_dupe,
    }


def make_activity(act_id, customer_id, sub_id, activity_date, outcome="saved"):
    return {
        "activity_id": act_id,
        "customer_id": customer_id,
        "subscription_id": sub_id,
        "activity_type": "retention_call",
        "activity_date": date.fromisoformat(activity_date),
        "outcome": outcome,
        "pre_save_mrr": None,
        "post_save_mrr": None,
    }


def subs_df(rows): return pd.DataFrame(rows)
def events_df(rows): return pd.DataFrame(rows)
def crm_df(rows): return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# §2 — Window bounds
# ---------------------------------------------------------------------------

def test_monthly_window_bounds():
    start, end = _window_bounds(date(2026, 4, 15), "monthly")
    assert start == date(2026, 4, 1)
    assert end == date(2026, 4, 30)


def test_monthly_window_february():
    start, end = _window_bounds(date(2026, 2, 10), "monthly")
    assert start == date(2026, 2, 1)
    assert end == date(2026, 2, 28)


def test_r30_window_bounds():
    start, end = _window_bounds(date(2026, 4, 30), "r30")
    assert start == date(2026, 4, 1)
    assert end == date(2026, 4, 30)


def test_r90_window_bounds():
    start, end = _window_bounds(date(2026, 4, 30), "r90")
    assert start == date(2026, 1, 31)
    assert end == date(2026, 4, 30)


# ---------------------------------------------------------------------------
# §6 — Micro contract exclusion
# ---------------------------------------------------------------------------

def test_micro_contracts_excluded_from_active_base():
    subs = subs_df([
        make_sub("S1", "C1", 199, "2025-01-01"),   # micro — excluded
        make_sub("S2", "C2", 200, "2025-01-01"),   # SMB threshold — included
        make_sub("S3", "C3", 500, "2025-01-01"),   # mid-market — included
    ])
    active = _active_subscriptions(subs, date(2026, 4, 1), segment=None)
    assert "S1" not in active["subscription_id"].values
    assert "S2" in active["subscription_id"].values
    assert "S3" in active["subscription_id"].values


def test_micro_contract_boundary_exactly_200():
    subs = subs_df([make_sub("S1", "C1", 200, "2025-01-01")])
    active = _active_subscriptions(subs, date(2026, 4, 1), segment=None)
    assert len(active) == 1


def test_micro_contract_boundary_199():
    subs = subs_df([make_sub("S1", "C1", 199, "2025-01-01")])
    active = _active_subscriptions(subs, date(2026, 4, 1), segment=None)
    assert len(active) == 0


# ---------------------------------------------------------------------------
# §2 — Trial/promo exclusion from active base
# ---------------------------------------------------------------------------

def test_trial_subs_excluded_from_active():
    subs = subs_df([
        make_sub("S1", "C1", 500, "2025-01-01", status="trial_or_promo"),
        make_sub("S2", "C2", 500, "2025-01-01", status="active"),
    ])
    active = _active_subscriptions(subs, date(2026, 4, 1), segment=None)
    assert "S1" not in active["subscription_id"].values
    assert "S2" in active["subscription_id"].values


# ---------------------------------------------------------------------------
# §11 — Churn type exclusions
# ---------------------------------------------------------------------------

def test_excluded_churn_types_not_in_headline():
    events = events_df([
        make_event("E1", "S1", "C1", "2026-04-15", churn_type="voluntary"),
        make_event("E2", "S2", "C2", "2026-04-15", churn_type="involuntary_fraud"),
        make_event("E3", "S3", "C3", "2026-04-15", churn_type="involuntary_collections"),
        make_event("E4", "S4", "C4", "2026-04-15", churn_type="refund_cancellation"),
    ])
    filtered = _churn_events_in_window(events, date(2026, 4, 1), date(2026, 4, 30))
    assert "E1" in filtered["event_id"].values
    assert "E2" not in filtered["event_id"].values
    assert "E3" not in filtered["event_id"].values
    assert "E4" not in filtered["event_id"].values


def test_involuntary_bankruptcy_included_in_financial():
    events = events_df([
        make_event("E1", "S1", "C1", "2026-04-15", churn_type="involuntary_bankruptcy"),
    ])
    filtered = _churn_events_in_window(events, date(2026, 4, 1), date(2026, 4, 30), cs_accountable_only=False)
    assert "E1" in filtered["event_id"].values


def test_involuntary_bankruptcy_excluded_from_cs_metric():
    events = events_df([
        make_event("E1", "S1", "C1", "2026-04-15", churn_type="involuntary_bankruptcy"),
        make_event("E2", "S2", "C2", "2026-04-15", churn_type="voluntary"),
    ])
    filtered = _churn_events_in_window(events, date(2026, 4, 1), date(2026, 4, 30), cs_accountable_only=True)
    assert "E1" not in filtered["event_id"].values
    assert "E2" in filtered["event_id"].values


# ---------------------------------------------------------------------------
# §7 — Save reversal (return within 30 days)
# ---------------------------------------------------------------------------

def test_save_reversal_removes_churn_event():
    subs = subs_df([make_sub("S1", "C1", 500, "2025-01-01", end="2026-04-15", status="cancelled")])
    events = events_df([make_event("E1", "S1", "C1", "2026-04-15")])
    crm = crm_df([make_activity("A1", "C1", "S1", "2026-04-01", outcome="saved")])

    result = calculate_churn_rate(subs, events, crm, date(2026, 4, 1), "monthly")
    assert "E1" in result.excluded_events["reversed_event_ids"]
    assert result.financial["churned_events"] == 0


def test_no_save_reversal_without_crm_activity():
    subs = subs_df([make_sub("S1", "C1", 500, "2025-01-01", end="2026-04-15", status="cancelled")])
    events = events_df([make_event("E1", "S1", "C1", "2026-04-15")])
    crm = crm_df([])

    result = calculate_churn_rate(subs, events, crm, date(2026, 4, 1), "monthly")
    assert result.financial["churned_events"] == 1


# ---------------------------------------------------------------------------
# §3 — nMRR calculation
# ---------------------------------------------------------------------------

def test_nmrr_active_sum():
    subs = subs_df([
        make_sub("S1", "C1", 500, "2025-01-01"),
        make_sub("S2", "C2", 1000, "2025-01-01"),
        make_sub("S3", "C3", 199, "2025-01-01"),  # micro — excluded
    ])
    active = _active_subscriptions(subs, date(2026, 4, 1), None)
    assert _nMRR_active(active) == 1500.0


def test_nmrr_lost():
    subs = subs_df([make_sub("S1", "C1", 750, "2025-01-01", end="2026-04-20", status="cancelled")])
    events = events_df([make_event("E1", "S1", "C1", "2026-04-20")])
    assert _nMRR_lost(events, subs) == 750.0


# ---------------------------------------------------------------------------
# §1 — Result carries definition version
# ---------------------------------------------------------------------------

def test_result_carries_definition_version():
    subs = subs_df([make_sub("S1", "C1", 500, "2025-01-01")])
    result = calculate_churn_rate(subs, events_df([]), crm_df([]), date(2026, 4, 1), "monthly")
    assert result.definition_version == DEFINITION_VERSION


# ---------------------------------------------------------------------------
# §16 — Both financial and contractual views present
# ---------------------------------------------------------------------------

def test_result_has_both_views():
    subs = subs_df([make_sub("S1", "C1", 500, "2025-01-01")])
    result = calculate_churn_rate(subs, events_df([]), crm_df([]), date(2026, 4, 1), "monthly")
    assert "churn_rate_pct" in result.financial
    assert "churn_rate_pct" in result.contractual
    assert "mrr_lost" in result.financial
    assert "customers_lost" in result.contractual


# ---------------------------------------------------------------------------
# Zero-division guard
# ---------------------------------------------------------------------------

def test_zero_active_subscriptions_returns_zero_rate():
    subs = subs_df([make_sub("S1", "C1", 199, "2025-01-01")])  # all micro
    result = calculate_churn_rate(subs, events_df([]), crm_df([]), date(2026, 4, 1), "monthly")
    assert result.financial["churn_rate_pct"] == 0.0
    assert result.contractual["churn_rate_pct"] == 0.0
