"""
Canonical metric definition constants — version 1.0.
Every threshold lives here. Bumping a value = new version.
"""

DEFINITION_VERSION = "1.0"
DEFINITION_DATE = "2026-04-28"

# Segment MRR boundaries (nMRR at start of period)
SEGMENT_ENTERPRISE_MIN = 5_000      # >= 5000
SEGMENT_MID_MARKET_MIN = 500        # 500 – 4999
SEGMENT_SMB_MIN = 200               # 200 – 499
MICRO_MRR_THRESHOLD = 200           # < 200 → excluded from headline

# Downgrade counts as contraction churn only if BOTH conditions are met
DOWNGRADE_DELTA_MIN_EUR = 50        # absolute MRR reduction >= €50
DOWNGRADE_DELTA_MIN_PCT = 0.10      # relative MRR reduction >= 10%

# Customer return window: reactivation within N days = save (churn reversed)
SAVE_WINDOW_DAYS = 30

# Post-renewal grace period: cancellation within N days of renewal = refund
RENEWAL_GRACE_DAYS = 14

# Contractual pause max duration before auto-churn
PAUSE_MAX_DAYS = 90

# CS save: retention activity must be logged within N days before cancellation request
CS_SAVE_LOOKBACK_DAYS = 30

# Trial/promo exclusion: customer excluded until first invoice with discount < this threshold
PROMO_DISCOUNT_THRESHOLD_PCT = 50   # discount >= 50% → still trial

# Churn types included in headline rate
HEADLINE_CHURN_TYPES = {
    "voluntary",
    "involuntary_bankruptcy",
    "involuntary_ma",
    "contraction",
    "pause_expiry",
}

# Churn types excluded from headline (administrative / non-business)
EXCLUDED_CHURN_TYPES = {
    "involuntary_fraud",
    "involuntary_collections",
    "refund_cancellation",
}

# Churn types excluded from CS-accountable metric only
CS_EXCLUDED_CHURN_TYPES = {
    "involuntary_bankruptcy",
    "involuntary_ma",
    "involuntary_fraud",
    "involuntary_collections",
}

DEFINITION_METADATA = {
    "version": DEFINITION_VERSION,
    "approved_date": DEFINITION_DATE,
    "primary_unit": "nMRR",
    "canonical_churn_date_field": "contract_end_date",
    "annual_contract_treatment": "monthly_distribution",
    "thresholds": {
        "micro_mrr_threshold_eur": MICRO_MRR_THRESHOLD,
        "downgrade_delta_min_eur": DOWNGRADE_DELTA_MIN_EUR,
        "downgrade_delta_min_pct": DOWNGRADE_DELTA_MIN_PCT,
        "save_window_days": SAVE_WINDOW_DAYS,
        "renewal_grace_days": RENEWAL_GRACE_DAYS,
        "pause_max_days": PAUSE_MAX_DAYS,
        "cs_save_lookback_days": CS_SAVE_LOOKBACK_DAYS,
        "promo_discount_threshold_pct": PROMO_DISCOUNT_THRESHOLD_PCT,
    },
}
