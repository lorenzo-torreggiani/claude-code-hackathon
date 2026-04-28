# Churn Rate — Canonical Metric Definition
## Version: 1.0 | Approved: 2026-04-28 | Status: ACTIVE

---

## 1. Definition

**Churn Rate** is the percentage of normalized Monthly Recurring Revenue (nMRR) lost in a calendar month due to voluntary cancellations, involuntary cancellations, and material downgrades, before expansion revenue.

```
Churn Rate (%) = nMRR Lost in Month M / nMRR Active at start of Month M × 100
```

Every result produced by this definition must carry the tag `definition_version: "1.0"`.

---

## 2. Primary Unit

The **headline metric is revenue-based (nMRR)**. Logo churn (customer count) is a secondary metric exposed in the drill-down view and labeled `logo_churn_rate` to avoid confusion with the headline figure.

> **Resolved disagreement:** Anna's logo churn is preserved as a secondary metric. Sarah's, Giulia's, and Marco's revenue-first view drives the headline.

---

## 3. Normalized MRR (nMRR)

All contracts are normalized to a monthly equivalent before any calculation:

- **Monthly contracts**: contract value = nMRR directly.
- **Annual contracts**: nMRR = annual contract value ÷ 12. Churn is distributed across the 12 months of the contract term — it does NOT spike at expiration.
- **Multi-year contracts**: nMRR = total contract value ÷ total months.

**Boundary example — annual contract:**
A customer pays €24,000/year. nMRR = €2,000. If the customer does not renew, churn of €2,000 is recorded in each of the 12 months of the contract term, starting from month 1 of the contract. It does NOT appear as €24,000 in the month of expiration.

> **Resolved disagreement:** Anna's spike-at-expiration approach is replaced by monthly distribution. Aligns with Sarah, Marco, and Giulia.

---

## 4. Canonical Churn Date

The **churn date** is the **contract end date** — the last day the contract was contractually active, regardless of:
- when the cancellation request was submitted
- when the customer last logged in or used the product

Two additional dates are stored as non-canonical fields for operational use:
- `cancellation_request_date`: date the customer or system triggered the cancellation
- `last_active_date`: last day the customer accessed the product (from event log)

**Boundary example:**
Customer submits cancellation on 2026-03-10. Contract end date is 2026-03-31. Last login is 2026-03-25.
→ Churn date = 2026-03-31. Churn is recorded in March.

> **Resolved disagreement:** Marco's "last active day" and Anna's "cancellation event date" are stored but do not drive the headline calculation. Giulia's contract end date is canonical.

---

## 5. Downgrade Treatment

A downgrade is included in churn as **contraction churn** only if it meets **both** of the following conditions:

- The nMRR reduction is **≥ €50**, AND
- The nMRR reduction is **≥ 10%** of the customer's nMRR in the prior month.

If only one condition is met, the event is recorded as a **minor contraction** — tracked but excluded from the headline churn rate.

**Boundary examples:**

| Prior nMRR | New nMRR | Delta | Delta % | Counts as churn? |
|---|---|---|---|---|
| €2,000 | €1,800 | −€200 | −10% | YES (both thresholds met) |
| €2,000 | €1,960 | −€40 | −2% | NO (delta < €50) |
| €600 | €555 | −€45 | −7.5% | NO (delta < €50) |
| €600 | €480 | −€120 | −20% | YES (both thresholds met) |
| €400 | €360 | −€40 | −10% | NO (delta < €50) |

> **Resolved disagreement:** Sarah's "any downgrade counts" and Anna's "no downgrade counts" are both wrong. A dual-threshold rule captures material contractions without noise from minor pricing adjustments.

---

## 6. Customer Segments

Segments are defined by the customer's nMRR at the start of the measurement month:

| Segment | nMRR Range | Included in headline churn rate |
|---|---|---|
| Enterprise | ≥ €5,000 | YES |
| Mid-market | €500 – €4,999 | YES |
| SMB | €200 – €499 | YES |
| Micro | < €200 | NO — tracked in `micro_churn_rate` separately |

The headline churn rate always specifies whether it is **all-segments** or **per-segment**.

> **Resolved disagreement:** Marco's €200 threshold is adopted. Micro-contract churn is tracked but separated to avoid inflating the headline metric with economically non-actionable events.

---

## 7. Customer Return Window (Save vs New Acquisition)

If a customer whose contract ended reactivates within **30 calendar days** of their `churn_date`:

- The original churn event is **reversed** — it is removed from the churn calculation for that month.
- The event is recorded as a **save** with `save_type: "reactivation"`.
- No new customer acquisition is recorded.

If the customer reactivates **after 30 calendar days**, the original churn stands and the reactivation is recorded as a **new customer acquisition**.

**Boundary examples:**

| Churn date | Reactivation date | Days elapsed | Classification |
|---|---|---|---|
| 2026-03-31 | 2026-04-15 | 15 days | SAVE — churn reversed |
| 2026-03-31 | 2026-04-30 | 30 days | SAVE — churn reversed |
| 2026-03-31 | 2026-05-01 | 31 days | CHURN stands + new acquisition |

> **Resolved disagreement:** Anna's double-counting is eliminated. Sarah's and Marco's "save" logic is adopted with an explicit 30-day boundary.

---

## 8. Post-Renewal Grace Period

A cancellation submitted within **14 calendar days** of an automatic renewal — monthly or annual — is classified as a **refund cancellation**:

- It is **excluded** from the churn rate.
- It is recorded in `refund_cancellations` for billing reconciliation.
- The renewal revenue is reversed in the same month.

After 14 calendar days, the cancellation is classified as voluntary churn and included in the headline rate.

**Boundary examples:**

| Renewal date | Cancellation date | Days after renewal | Classification |
|---|---|---|---|
| 2026-04-01 | 2026-04-08 | 7 days | REFUND — excluded from churn |
| 2026-04-01 | 2026-04-15 | 14 days | REFUND — excluded from churn |
| 2026-04-01 | 2026-04-16 | 15 days | VOLUNTARY CHURN — included |

> **Resolved disagreement:** Marco's and Giulia's "refund, not churn" logic is adopted. 14 days applies to both monthly and annual renewals.

---

## 9. Contractual Pause

A customer on a contractual pause is classified as **at-risk**, not active and not churned.

- If the pause duration is **≤ 90 calendar days**: status = `at_risk`. No churn recorded. Excluded from both active base and churn numerator.
- If the pause duration exceeds **90 calendar days** without reactivation: status transitions to **churned** on day 91. Churn is recorded with `churn_type: "pause_expiry"`.

**Boundary example:**
Customer pauses on 2026-02-01. Reactivates on 2026-04-15 (73 days) → no churn, status was at-risk.
Customer pauses on 2026-02-01, no reactivation by 2026-05-03 (91 days) → churn recorded on 2026-05-03.

> **Resolved disagreement:** Anna's "count as active" eliminated. Marco's and Giulia's at-risk state adopted with an explicit 90-day expiry.

---

## 10. Enterprise Partial Seat Cancellations

A partial seat cancellation on an Enterprise contract is classified as:

- **Contraction churn** if the nMRR reduction meets the thresholds in Section 5 (≥ €50 AND ≥ 10%).
- **Minor contraction** otherwise — tracked but excluded from headline.

The parent contract remains active. The remaining seat count and nMRR are updated.

**Boundary example:**
Enterprise customer has 50 seats at €100/seat = €5,000 nMRR. Cancels 8 seats → new nMRR = €4,200. Delta = −€800, −16%. Both thresholds met → contraction churn of €800 recorded.

> **Resolved disagreement:** Anna's "ignore seat cancellations" eliminated. Marco's and Giulia's "track as contraction" adopted.

---

## 11. Churn Types

Every churn event is tagged with one of the following `churn_type` values:

| churn_type | Description | Included in headline rate |
|---|---|---|
| `voluntary` | Customer chose to cancel | YES |
| `involuntary_bankruptcy` | Customer filed insolvency proceedings (CRM evidence required) | YES — financial view; NO — CS-accountable view |
| `involuntary_ma` | Customer acquired by another existing customer (CRM evidence required) | YES — financial view; NO — CS-accountable view |
| `involuntary_fraud` | Account flagged by Trust & Safety team | NO |
| `involuntary_collections` | Cancelled after ≥ 90 days of failed payment attempts | NO |
| `contraction` | Material downgrade meeting Section 5 thresholds | YES |
| `pause_expiry` | Pause exceeded 90 days without reactivation | YES |
| `refund_cancellation` | Cancelled within 14 days of automatic renewal | NO |

**CS-accountable churn** (used for Marco's team performance metric) excludes: `involuntary_bankruptcy`, `involuntary_ma`, `involuntary_fraud`, `involuntary_collections`.

> **Resolved disagreement:** Marco's involuntary exclusions are formalized with explicit evidence requirements. Giulia's financial view includes all types for ARR forecasting.

---

## 12. Trial and Promotional Period Exclusion

Customers are excluded from the headline churn rate until they have completed their **first full-price billing cycle**, defined as:

- First invoice where the applied discount is **< 50% of list price**, AND
- The invoice covers a complete billing period (no pro-rata).

Until that condition is met, the customer has status `trial_or_promo`. Cancellations in this state are recorded in `trial_churn_rate` but excluded from the headline.

**Boundary examples:**

| Invoice | Discount | Status |
|---|---|---|
| €1 (list €99) | 99% discount | trial_or_promo — excluded |
| €49.50 (list €99) | 50% discount | trial_or_promo — excluded (discount = 50%, not < 50%) |
| €59.40 (list €99) | 40% discount | ACTIVE — included in headline from this billing cycle onward |

> **Resolved disagreement:** Giulia's "first full-price renewal" criterion is adopted with a concrete 50% discount threshold.

---

## 13. CS Save Flag

A churn event is flagged `saved_by_cs: true` if:

- A retention activity is logged in the CRM within **30 calendar days before** the `cancellation_request_date`, AND
- The activity type is one of: `retention_call`, `retention_email`, `discount_offered`, `contract_renegotiation`.

The CRM activity log is the **sole source of truth** for this flag. Manual overrides require Finance approval and are audit-logged.

If a save was achieved with a discount, both values are recorded:
- `pre_save_mrr`: nMRR before the retention offer
- `post_save_mrr`: nMRR after the retention offer
- `retention_delta`: pre_save_mrr − post_save_mrr (the revenue cost of the save)

> **Resolved disagreement:** Marco's "save = win" and Giulia's "save with discount = partial loss" are both preserved as separate fields.

---

## 14. Administrative Exclusions

The following cancellations are excluded from all churn metrics (headline and secondary) and recorded in `admin_cancellations`:

- Accounts flagged `involuntary_fraud` by the Trust & Safety team
- Accounts cancelled after ≥ 90 days of failed payment collection (`involuntary_collections`)
- Duplicate records from system migrations (identified by `is_migration_duplicate: true` in the source system)

All exclusions are **automatic** based on CRM tags — no manual blacklist tables. Every exclusion is logged with the tag that triggered it, the timestamp, and the source system field.

> **Resolved disagreement:** Anna's manual blacklist table is replaced by an automated, auditable exclusion rule.

---

## 15. Calculation Windows

The metric is computed on three windows, all exposed via the API:

| Window | Field name | Description |
|---|---|---|
| Monthly fixed | `churn_rate_monthly` | Calendar month M |
| Rolling 30 days | `churn_rate_r30` | Last 30 calendar days from query date |
| Rolling 90 days | `churn_rate_r90` | Last 90 calendar days from query date |

The **headline metric for board reporting** is `churn_rate_monthly`.
The **headline metric for CS operations** is `churn_rate_r90`.

> **Resolved disagreement:** Anna's monthly-only view and Marco's rolling-window preference are both served without conflict.

---

## 16. Dual View: Financial vs Contractual

Every API response includes two parallel figures:

- `financial_view`: MRR lost (revenue-based, accrual, for Finance/board)
- `contractual_view`: contracts lost (logo-based, for legal/ops tracking)

Neither view is hidden or derived from the other. Both are first-class outputs.

---

## 17. Versioning and Audit Trail

Every metric result carries:

```json
{
  "definition_version": "1.0",
  "calculated_at": "2026-04-28T09:00:00Z",
  "calculation_window": "monthly",
  "period": "2026-04",
  "financial_view": { "churn_rate": 2.3, "mrr_lost": 18400 },
  "contractual_view": { "churn_rate": 1.8, "customers_lost": 12 }
}
```

When the definition is updated, the version increments (e.g. `1.1`, `2.0`). Historical data can be recomputed with any prior version. Comparisons between versions are exposed via the `compare_definitions` API endpoint.

---

## 18. Resolved Questions Summary

| # | Question | Resolution |
|---|---|---|
| 1 | Primary unit | nMRR (revenue). Logo churn is secondary. |
| 2 | Downgrade threshold | ≥ €50 AND ≥ 10% of prior nMRR. Both conditions required. |
| 3 | Canonical churn date | Contract end date. |
| 4 | Annual contract allocation | Monthly distribution (÷ 12). No expiration spike. |
| 5 | Return window | 30 calendar days. Reactivation within 30d = save, not churn. |
| 6 | Contractual pause max duration | 90 calendar days. Day 91 = churn recorded. |
| 7 | CS save source of truth | CRM activity log. Activity must be within 30d before cancellation request. |
| 8 | Minimum MRR threshold | €200 nMRR. Below = micro_churn, excluded from headline. |
| 9 | Post-renewal grace period | 14 calendar days. Applies to monthly and annual renewals. |
| 10 | Involuntary churn qualification | Bankruptcy, M&A, fraud, collections — each requires a specific CRM tag. |
| 11 | Trial exclusion boundary | First invoice with discount < 50% of list price (complete billing cycle). |
| 12 | Segment boundaries | Enterprise ≥ €5,000 / Mid-market €500–€4,999 / SMB €200–€499 / Micro < €200. |
