"""
Challenge 2 — Raw data generation for SaaS Churn scenario.
Injects realistic noise: timezone mismatch, retry-storm duplicates,
mislabeled segments, gaps, and edge cases from the canonical definition.
"""

import random
import os
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from faker import Faker

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker("it_IT")
fake.seed_instance(SEED)

OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT_DIR, exist_ok=True)

UTC = ZoneInfo("UTC")
CET = ZoneInfo("Europe/Rome")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

N_CUSTOMERS = 500
PERIOD_START = date(2025, 1, 1)
PERIOD_END = date(2026, 3, 31)

PLANS = {
    "Micro Free":      {"mrr": 19,    "segment": "Micro"},
    "Micro Plus":      {"mrr": 99,    "segment": "Micro"},
    "SMB Starter":     {"mrr": 249,   "segment": "SMB"},
    "SMB Pro":         {"mrr": 399,   "segment": "SMB"},
    "Mid Growth":      {"mrr": 799,   "segment": "Mid-market"},
    "Mid Scale":       {"mrr": 1_999, "segment": "Mid-market"},
    "Enterprise Core": {"mrr": 5_500, "segment": "Enterprise"},
    "Enterprise Plus": {"mrr": 12_000,"segment": "Enterprise"},
}

INDUSTRIES = ["SaaS", "E-commerce", "Fintech", "Healthcare", "Logistics",
              "Manufacturing", "Media", "Consulting", "Education", "Retail"]

CSM_POOL = ["giulia.ferrari", "marco.ricci", "sara.conti",
            "luca.marino", "elena.russo"]

CHURN_TYPES = ["voluntary", "involuntary_bankruptcy", "involuntary_ma",
               "involuntary_fraud", "involuntary_collections",
               "contraction", "pause_expiry"]


def rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def to_utc_str(d: date) -> str:
    dt = datetime(d.year, d.month, d.day, random.randint(0, 23),
                  random.randint(0, 59), tzinfo=UTC)
    return dt.isoformat()


def to_cet_str(d: date) -> str:
    """Billing system records in CET — source of timezone noise."""
    dt = datetime(d.year, d.month, d.day, random.randint(0, 23),
                  random.randint(0, 59), tzinfo=CET)
    return dt.isoformat()


# ---------------------------------------------------------------------------
# 1. Customers
# ---------------------------------------------------------------------------

def build_customers() -> pd.DataFrame:
    rows = []
    for i in range(1, N_CUSTOMERS + 1):
        plan_name = random.choice(list(PLANS.keys()))
        plan = PLANS[plan_name]
        segment = plan["segment"]

        # Noise: ~4% of customers have wrong segment label (mislabeled)
        if random.random() < 0.04:
            wrong_segments = [s for s in ["SMB", "Mid-market", "Enterprise", "Micro"]
                              if s != segment]
            segment_label = random.choice(wrong_segments)
            is_mislabeled = True
        else:
            segment_label = segment
            is_mislabeled = False

        rows.append({
            "customer_id":    f"CUST-{i:04d}",
            "company_name":   fake.company(),
            "industry":       random.choice(INDUSTRIES),
            "country":        random.choice(["IT", "DE", "FR", "ES", "NL", "UK", "PL"]),
            "segment":        segment_label,       # may be wrong
            "segment_correct": plan["segment"],    # ground truth
            "is_mislabeled":  is_mislabeled,
            "csm_owner":      random.choice(CSM_POOL),
            "created_at":     rand_date(date(2020, 1, 1), PERIOD_START).isoformat(),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. Subscriptions
# ---------------------------------------------------------------------------

def build_subscriptions(customers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    sub_id = 1
    for _, c in customers.iterrows():
        cid = c["customer_id"]
        plan_name = random.choice(list(PLANS.keys()))
        plan = PLANS[plan_name]
        mrr = plan["mrr"]

        # Billing cycle: Enterprise mostly annual, others mixed
        if plan["segment"] == "Enterprise":
            billing_cycle = random.choices(["annual", "monthly"], weights=[75, 25])[0]
        else:
            billing_cycle = random.choices(["annual", "monthly"], weights=[30, 70])[0]

        contract_value = mrr * 12 if billing_cycle == "annual" else mrr

        start = rand_date(date(2023, 1, 1), PERIOD_START)

        # Determine status
        r = random.random()
        if r < 0.72:
            status = "active"
            end = None
        elif r < 0.82:
            status = "cancelled"
            end = rand_date(PERIOD_START, PERIOD_END)
        elif r < 0.88:
            status = "paused"
            end = None
        elif r < 0.92:
            status = "trial_or_promo"
            end = None
        else:
            status = "at_risk"
            end = None

        # Seats (Enterprise only)
        seats = random.randint(10, 200) if plan["segment"] == "Enterprise" else None

        rows.append({
            "subscription_id":  f"SUB-{sub_id:05d}",
            "customer_id":      cid,
            "plan_name":        plan_name,
            "billing_cycle":    billing_cycle,
            "mrr":              mrr,
            "contract_value":   contract_value,
            "start_date":       start.isoformat(),
            "end_date":         end.isoformat() if end else None,
            "status":           status,
            "seats":            seats,
        })
        sub_id += 1

        # ~8% of customers have a second (upgrade) subscription
        if random.random() < 0.08:
            plan2_name = random.choice(list(PLANS.keys()))
            plan2 = PLANS[plan2_name]
            start2 = end if end else rand_date(PERIOD_START, PERIOD_END)
            rows.append({
                "subscription_id":  f"SUB-{sub_id:05d}",
                "customer_id":      cid,
                "plan_name":        plan2_name,
                "billing_cycle":    "monthly",
                "mrr":              plan2["mrr"],
                "contract_value":   plan2["mrr"],
                "start_date":       start2.isoformat() if start2 else start.isoformat(),
                "end_date":         None,
                "status":           "active",
                "seats":            None,
            })
            sub_id += 1

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 3. Cancellation events  (with injected noise)
# ---------------------------------------------------------------------------

def build_cancellation_events(subscriptions: pd.DataFrame) -> pd.DataFrame:
    cancelled = subscriptions[subscriptions["status"] == "cancelled"].copy()
    rows = []
    event_id = 1

    for _, sub in cancelled.iterrows():
        end_date = date.fromisoformat(sub["end_date"])
        cancel_req = end_date - timedelta(days=random.randint(1, 45))
        last_active = end_date - timedelta(days=random.randint(0, 10))

        churn_type = random.choices(
            ["voluntary", "involuntary_bankruptcy", "involuntary_ma",
             "involuntary_fraud", "involuntary_collections", "pause_expiry"],
            weights=[70, 5, 5, 5, 10, 5]
        )[0]

        # Noise 1 — timezone mismatch: billing (CET) vs CRM (UTC)
        # At month boundaries this shifts the event to the wrong month
        cancel_req_utc = to_utc_str(cancel_req)   # CRM
        cancel_req_cet = to_cet_str(cancel_req)   # Billing — may differ by 1–2h → different day

        rows.append({
            "event_id":                  f"EVT-{event_id:05d}",
            "subscription_id":           sub["subscription_id"],
            "customer_id":               sub["customer_id"],
            "cancellation_request_date_utc":  cancel_req_utc,
            "cancellation_request_date_cet":  cancel_req_cet,
            "contract_end_date":         end_date.isoformat(),
            "last_active_date":          last_active.isoformat(),
            "churn_type":                churn_type,
            "is_migration_duplicate":    False,
            "source_system":             random.choice(["CRM", "billing"]),
        })
        event_id += 1

    # Noise 2 — retry storm: inject ~340 duplicate cancellation events
    # from the November 2025 CRM migration (as described by Anna)
    migration_window_start = date(2025, 11, 1)
    migration_window_end   = date(2025, 11, 30)
    migration_candidates = [
        r for r in rows
        if migration_window_start.isoformat() <= r["contract_end_date"] <= migration_window_end.isoformat()
    ]

    n_dupes = 340
    base_pool = migration_candidates if migration_candidates else rows[:50]
    for _ in range(n_dupes):
        original = random.choice(base_pool).copy()
        original["event_id"]              = f"EVT-{event_id:05d}"
        original["is_migration_duplicate"] = True
        original["source_system"]         = "billing"
        # Slight timestamp variation to make duplicates non-obvious
        base_dt = datetime.fromisoformat(original["cancellation_request_date_utc"])
        jitter   = timedelta(seconds=random.randint(1, 300))
        original["cancellation_request_date_utc"] = (base_dt + jitter).isoformat()
        rows.append(original)
        event_id += 1

    # Noise 3 — gaps: ~3% of records are missing contract_end_date
    df = pd.DataFrame(rows)
    gap_idx = df.sample(frac=0.03, random_state=SEED).index
    df.loc[gap_idx, "contract_end_date"] = None

    # Noise 4 — mislabeled churn_type: ~2% labeled "voluntary" when they are collections
    mis_idx = df[df["churn_type"] == "involuntary_collections"].sample(
        frac=0.02, random_state=SEED
    ).index
    df.loc[mis_idx, "churn_type"] = "voluntary"

    return df


# ---------------------------------------------------------------------------
# 4. CRM activity log  (CS retention actions)
# ---------------------------------------------------------------------------

def build_crm_activity_log(cancellation_events: pd.DataFrame) -> pd.DataFrame:
    clean = cancellation_events[~cancellation_events["is_migration_duplicate"]]
    voluntary = clean[clean["churn_type"] == "voluntary"]
    sampled = voluntary.sample(frac=0.35, random_state=SEED)

    rows = []
    for act_id, (_, evt) in enumerate(sampled.iterrows(), start=1):
        cancel_req = evt["cancellation_request_date_utc"]
        try:
            cancel_dt = datetime.fromisoformat(cancel_req)
        except Exception:
            continue

        activity_dt = cancel_dt - timedelta(days=random.randint(1, 30))
        activity_type = random.choice(
            ["retention_call", "retention_email", "discount_offered",
             "contract_renegotiation"]
        )
        outcome = random.choices(["saved", "churned"], weights=[40, 60])[0]

        pre_mrr = None
        post_mrr = None
        if activity_type == "discount_offered" and outcome == "saved":
            # Noise: some saved records are missing post_save_mrr (incomplete CRM entry)
            if random.random() > 0.15:
                pre_mrr = random.choice([249, 399, 799, 1999, 5500])
                post_mrr = round(pre_mrr * random.uniform(0.6, 0.9), 2)

        rows.append({
            "activity_id":    f"ACT-{act_id:05d}",
            "customer_id":    evt["customer_id"],
            "subscription_id": evt["subscription_id"],
            "activity_type":  activity_type,
            "activity_date":  activity_dt.isoformat(),
            "outcome":        outcome,
            "pre_save_mrr":   pre_mrr,
            "post_save_mrr":  post_mrr,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 5. Invoices
# ---------------------------------------------------------------------------

def build_invoices(subscriptions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    inv_id = 1
    for _, sub in subscriptions.iterrows():
        start = date.fromisoformat(sub["start_date"])
        end = date.fromisoformat(sub["end_date"]) if sub["end_date"] else PERIOD_END
        mrr = sub["mrr"]
        cycle = sub["billing_cycle"]
        step = 365 if cycle == "annual" else 30
        amount = sub["contract_value"]

        current = start
        invoice_num = 0
        while current <= end:
            period_end = current + timedelta(days=step - 1)
            invoice_num += 1

            # First invoice for trial/promo customers: apply heavy discount
            if sub["status"] == "trial_or_promo" and invoice_num == 1:
                discount_pct = random.choice([50, 75, 90, 99])
                billed = round(amount * (1 - discount_pct / 100), 2)
            elif invoice_num == 2 and sub["status"] == "trial_or_promo":
                discount_pct = random.choice([0, 20, 40])
                billed = round(amount * (1 - discount_pct / 100), 2)
            else:
                discount_pct = 0
                billed = amount

            # Noise: ~2% of invoices have failed payment status
            status = random.choices(
                ["paid", "failed", "refunded"],
                weights=[94, 4, 2]
            )[0]

            # Noise: ~1% missing invoice_date (data gap)
            inv_date = current.isoformat() if random.random() > 0.01 else None

            is_renewal = invoice_num > 1

            rows.append({
                "invoice_id":           f"INV-{inv_id:06d}",
                "subscription_id":      sub["subscription_id"],
                "customer_id":          sub["customer_id"],
                "invoice_date":         inv_date,
                "billing_period_start": current.isoformat(),
                "billing_period_end":   period_end.isoformat(),
                "list_price":           amount,
                "discount_pct":         discount_pct,
                "amount_billed":        billed,
                "status":               status,
                "is_renewal":           is_renewal,
            })
            inv_id += 1
            current += timedelta(days=step)

            # Limit invoices per subscription to keep dataset manageable
            if invoice_num >= 24:
                break

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Generating customers...")
    customers = build_customers()
    customers.to_csv(f"{OUT_DIR}/customers.csv", index=False)
    print(f"  {len(customers)} rows -> customers.csv")

    print("Generating subscriptions...")
    subscriptions = build_subscriptions(customers)
    subscriptions.to_csv(f"{OUT_DIR}/subscriptions.csv", index=False)
    print(f"  {len(subscriptions)} rows -> subscriptions.csv")

    print("Generating cancellation events (with noise)...")
    cancellations = build_cancellation_events(subscriptions)
    cancellations.to_csv(f"{OUT_DIR}/cancellation_events.csv", index=False)
    clean = cancellations[~cancellations["is_migration_duplicate"]]
    dupes = cancellations[cancellations["is_migration_duplicate"]]
    gaps  = cancellations[cancellations["contract_end_date"].isna()]
    print(f"  {len(cancellations)} rows -> cancellation_events.csv")
    print(f"    clean events:      {len(clean)}")
    print(f"    migration dupes:   {len(dupes)}")
    print(f"    missing end_date:  {len(gaps)}")

    print("Generating CRM activity log...")
    activity_log = build_crm_activity_log(cancellations)
    activity_log.to_csv(f"{OUT_DIR}/crm_activity_log.csv", index=False)
    print(f"  {len(activity_log)} rows -> crm_activity_log.csv")

    print("Generating invoices...")
    invoices = build_invoices(subscriptions)
    invoices.to_csv(f"{OUT_DIR}/invoices.csv", index=False)
    print(f"  {len(invoices)} rows -> invoices.csv")

    print("\nNoise summary:")
    mislabeled = customers[customers["is_mislabeled"]].shape[0]
    print(f"  Mislabeled segments:        {mislabeled} customers")
    print(f"  Timezone-split events:      all cancellation_events have dual UTC/CET timestamps")
    print(f"  Retry-storm duplicates:     {len(dupes)} events (is_migration_duplicate=True)")
    print(f"  Missing contract_end_date:  {len(gaps)} events")
    failed_inv = invoices[invoices["status"] == "failed"].shape[0]
    print(f"  Failed invoices:            {failed_inv}")
    missing_inv_date = invoices[invoices["invoice_date"].isna()].shape[0]
    print(f"  Missing invoice_date:       {missing_inv_date}")

    print("\nDone. Files written to:", OUT_DIR)


if __name__ == "__main__":
    main()
