"""
Load and pre-process raw CSV files into clean DataFrames.
Applies structural fixes only — no business logic here.
"""

import os
from datetime import date
from functools import lru_cache

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _parse_dates(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce").dt.date
    return df


@lru_cache(maxsize=1)
def load_customers() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/customers.csv")
    # Use ground-truth segment, not the potentially mislabeled label
    df["segment"] = df["segment_correct"]
    return df


@lru_cache(maxsize=1)
def load_subscriptions() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/subscriptions.csv")
    df = _parse_dates(df, ["start_date", "end_date"])
    return df


@lru_cache(maxsize=1)
def load_cancellations() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/cancellation_events.csv")
    # Drop retry-storm duplicates — this is the first cleaning step Anna's manual
    # blacklist was approximating; here it's rule-based and auditable.
    df = df[df["is_migration_duplicate"] == False].copy()
    # Use contract_end_date as canonical churn date (definition §4)
    df = _parse_dates(df, ["contract_end_date", "last_active_date"])
    # Drop rows where contract_end_date is missing (gap noise)
    df = df.dropna(subset=["contract_end_date"])
    return df


@lru_cache(maxsize=1)
def load_crm_activity() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/crm_activity_log.csv")
    df = _parse_dates(df, ["activity_date"])
    return df


@lru_cache(maxsize=1)
def load_invoices() -> pd.DataFrame:
    df = pd.read_csv(f"{DATA_DIR}/invoices.csv")
    df = _parse_dates(df, ["invoice_date", "billing_period_start", "billing_period_end"])
    return df


def reload_all() -> None:
    """Clear cache — call after data refresh."""
    load_customers.cache_clear()
    load_subscriptions.cache_clear()
    load_cancellations.cache_clear()
    load_crm_activity.cache_clear()
    load_invoices.cache_clear()
