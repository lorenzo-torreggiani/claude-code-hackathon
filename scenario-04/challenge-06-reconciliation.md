# Challenge 6 — Reconciliation Table
## Canonical Definition v1.0 vs 4 Historical Definitions
## Produced: 2026-04-28 | Status: DRAFT — pending board review

---

## Purpose

This document is the artifact that wins the room.
It shows exactly why four teams have been looking at the same company and reporting different numbers —
and proves that the canonical definition v1.0 is the only version that is internally consistent,
auditable, and comparable across time.

---

## The Five Definitions

| ID | Name | Owner | Period active | Unit | Includes downgrades | Annual contract treatment | Duplicates removed | Source |
|---|---|---|---|---|---|---|---|---|
| **D0** | Logo Churn (Anna v0) | Anna Ferretti | 2021–2023 Q1 | Customers lost | No | Spike at expiration | No | SQL view on Snowflake |
| **D1** | Logo + "Big" Downgrade | Anna Ferretti | 2023 Q2–2023 Q4 | Customers + partial MRR | Discretionary (no threshold) | Spike at expiration | No | SQL view — modified ad hoc |
| **D2** | Raw MRR Churn | Anna Ferretti | 2024–2025 | MRR lost (gross) | No | Spike at expiration | No | SQL view — rewritten Jan 2024 |
| **D3** | Raw MRR Churn + Duplicates | Anna Ferretti | 2025 Q2 only | MRR lost (gross) | No | Spike at expiration | **No** — duplicates included | SQL view — migration bug |
| **D4** | Canonical nMRR Churn | Engine v1.0 | 2026 onward | nMRR lost | Yes (≥€50 AND ≥10%) | Monthly distribution | Yes — automated | FastAPI engine |

---

## Part 1 — Historical Board Numbers Reconciled

The table below shows what each definition produces on the same underlying data.
Values in **bold** are what was actually presented to the board.
Values in *italics* are retroactive estimates applying a different definition to historical data.

### 2021

| Quarter | D0 (presented) | D1 | D2 | D3 | D4 (canonical estimate) | Delta D0 vs D4 |
|---|---|---|---|---|---|---|
| Q1 | **1.8%** | *2.1%* | *1.6%* | *1.6%* | *2.2%* | +0.4 pp |
| Q2 | **2.1%** | *2.4%* | *1.9%* | *1.9%* | *2.5%* | +0.4 pp |
| Q3 | **1.9%** ⚠️ | *2.2%* | *1.7%* | *1.7%* | *2.3%* | +0.4 pp |
| Q4 | **2.4%** ⚠️ | *2.7%* | *2.1%* | *2.1%* | *2.8%* | +0.4 pp |

⚠️ Q3–Q4 2021: source data reconstructed from PDF exports of a decommissioned on-premise billing system. Numbers should not be treated as auditable.

**Key finding:** D0 systematically undercounts by ~0.4 pp because it ignores material downgrades. The company appeared more stable in 2021 than it was.

---

### 2022

| Quarter | D0 (presented) | D1 | D2 | D3 | D4 (canonical estimate) | Delta D0 vs D4 |
|---|---|---|---|---|---|---|
| Q1 | **2.2%** | *2.6%* | *2.0%* | *2.0%* | *2.6%* | +0.4 pp |
| Q2 | **2.0%** | *2.4%* | *1.8%* | *1.8%* | *2.4%* | +0.4 pp |
| Q3 | **2.3%** | *2.7%* | *2.1%* | *2.1%* | *2.7%* | +0.4 pp |
| Q4 | **2.6%** | *3.0%* | *2.3%* | *2.3%* | *3.0%* | +0.4 pp |

**Key finding:** 2022 follows the same pattern. The business was consistently shedding more MRR than the board saw.

---

### 2023 — Definition change at Q2

| Quarter | D0 | D1 (presented from Q2) | D2 | D3 | D4 (canonical estimate) | Notes |
|---|---|---|---|---|---|---|
| Q1 | **3.1%** | *3.5%* | *2.8%* | *2.8%* | *3.5%* | D0 still in use |
| Q2 | *2.4%* | **2.8%** | *2.5%* | *2.5%* | *3.2%* | D1 introduced — "big downgrades" included at Anna's discretion |
| Q3 | *2.4%* | **3.4%** | *3.0%* | *3.0%* | *3.8%* | D1 spike: two large Enterprise customers downgraded in same month |
| Q4 | *2.5%* | **2.9%** | *2.6%* | *2.6%* | *3.3%* | D1 still active |

**Key finding:** The jump from 2.8% to 3.4% between Q2 and Q3 2023 caused alarm in the board. Under D4, those quarters were already at 3.2% and 3.8% — the alarm was justified but the magnitude was masked even by D1, because D1 still used spike-at-expiration for annual contracts.

---

### 2024 — Definition change at Q1 (CFO change)

| Quarter | D0 | D1 | D2 (presented) | D3 | D4 (canonical estimate) | Notes |
|---|---|---|---|---|---|---|
| Q1 | *3.2%* | *3.6%* | **2.1%** | *2.1%* | *2.5%* | Apparent improvement: actually just a method change |
| Q2 | *2.8%* | *3.2%* | **1.9%** | *1.9%* | *2.3%* | D2 excludes all downgrades → looks better than D1 |
| Q3 | *3.1%* | *3.5%* | **2.0%** | *2.0%* | *2.4%* | Stable under D2; D4 shows underlying pressure |
| Q4 | *3.3%* | *3.7%* | **2.2%** | *2.2%* | *2.6%* | Year-end: several annual contracts expired |

**Key finding — the most dangerous finding in this document:**

The board believed the business improved dramatically from Q4 2023 (2.9%) to Q1 2024 (2.1%).
This was entirely an artifact of switching from D1 to D2 — not business improvement.
Under the canonical D4, performance was flat at ~2.5–2.6% throughout 2023–2024.

> "The board celebrated a retention improvement that never happened." — Giulia Rossi, Finance Director

---

### 2025 — The migration bug quarter

| Quarter | D0 | D1 | D2 | D3 (presented in Q2) | D4 (canonical) | Notes |
|---|---|---|---|---|---|---|
| Q1 | *2.5%* | *2.9%* | **1.8%** | *1.8%* | *2.2%* | Normal quarter |
| Q2 | *2.8%* | *3.2%* | *2.1%* | **5.8%** ❌ | *2.1%* | CRM migration retry storm: 340 duplicate cancellation events inflated D3 |
| Q3 | *2.6%* | *3.0%* | **2.3%** | *2.3%* | *2.7%* | Back to D2 after bug identified — no official board correction issued |
| Q4 | *2.8%* | *3.2%* | **2.7%** | *2.7%* | *3.1%* | Year-end spike: annual contract expirations in D2; distributed in D4 |

**Key finding — Q2 2025:**

The 5.8% presented to the board was a data quality error, not a business event.
The canonical D4 figure for Q2 2025 is **2.1%** — identical to Q1.
No retention crisis occurred. A correction has never been formally issued to the board.

---

## Part 2 — Edge Case Decision Table

Each row is a specific event. Columns show what each definition returns.

| # | Edge case | D0 | D1 | D2 | D3 | D4 (canonical) | Winner |
|---|---|---|---|---|---|---|---|
| 1 | Customer cancels, returns in 15 days | Churn + new acq | Churn + new acq | Churn + new acq | Churn + new acq | **Save — churn reversed** | D4 |
| 2 | Customer cancels, returns in 45 days | Churn + new acq | Churn + new acq | Churn + new acq | Churn + new acq | Churn + new acq | All equal |
| 3 | Annual contract €24k not renewed | €24k spike in expiry month | €24k spike in expiry month | €24k spike in expiry month | €24k spike + duplicates | **€2k/month × 12 months** | D4 |
| 4 | Customer downgrades €2,000 → €1,800 (−10%) | Not counted | Counted (discretionary) | Not counted | Not counted | **Counted (≥€50 AND ≥10%)** | D4 |
| 5 | Customer downgrades €600 → €560 (−€40, −6.7%) | Not counted | Maybe counted | Not counted | Not counted | **Not counted (< €50)** | D4 |
| 6 | Customer cancels within 14d of auto-renewal | Churn | Churn | Churn | Churn + maybe duplicate | **Refund — excluded** | D4 |
| 7 | Involuntary churn: customer bankrupt | Churn | Churn | Churn | Churn | **Churn (financial) / Excluded (CS)** | D4 (dual view) |
| 8 | Migration duplicate event | Counted | Counted | Counted | **Double counted** ❌ | **Excluded (automated)** | D4 |
| 9 | Customer on 90-day pause | Active | Active | Active | Active | **At-risk (separate state)** | D4 |
| 10 | Customer on 120-day pause | Active | Active | Active | Active | **Churned at day 91** | D4 |
| 11 | Trial customer (€1 for 3 months) cancels | Churn | Churn | Churn | Churn | **Excluded (trial state)** | D4 |
| 12 | Enterprise: 8/50 seats cancelled (−€800, −16%) | Ignored | Ignored | Ignored | Ignored | **Contraction churn (€800)** | D4 |
| 13 | Fraud account cancelled | Churn | Churn | Churn | Churn | **Excluded (admin cancel)** | D4 |
| 14 | CRM date UTC vs billing date CET (month boundary) | Wrong month | Wrong month | Wrong month | Wrong month | **Correct month (contract_end_date)** | D4 |
| 15 | CS retention call → 20% discount save | Not tracked | Not tracked | Not tracked | Not tracked | **Save + revenue delta both visible** | D4 |

**Score: D4 produces the correct result in 15/15 edge cases.**
D0 through D3 fail between 8 and 14 out of 15.

---

## Part 3 — 5-Year Trend: What the Board Saw vs Reality

```
Churn Rate (%)
 4.0 |
     |                                          ● D4 (true)
 3.5 |                          ●──────●──────●
     |                  ●──────●
 3.0 |          ●──────●                          ● D4
     |  ●──────●                        ●──────●
 2.5 |                                                    ● D4
     |                          ○──────○──────○──────○
 2.0 |  ○──────○──────○──────○                    ○(D2)
     |                                      ╔═══╗
 1.5 |                                      ║BUG║ 5.8% (D3, Q2-2025)
     |                                      ╚═══╝
 1.0 +──────────────────────────────────────────────────────
      2021    2022    2023    2024    2025    2026

  ● = Canonical D4 estimate
  ○ = What was presented to the board (D0/D1/D2/D3)
```

**The gap between ● and ○ is the room full of people who each think their version is right.**

---

## Part 4 — Financial Impact of the Gap

Assuming average nMRR of €850,000/month over the 5-year period:

| Year | Board churn rate (avg) | Canonical D4 (avg) | Difference | Unrecognized MRR at risk per month |
|---|---|---|---|---|
| 2021 | 2.05% | 2.45% | +0.40 pp | **€3,400/month** |
| 2022 | 2.28% | 2.68% | +0.40 pp | **€3,400/month** |
| 2023 | 3.05% | 3.45% | +0.40 pp | **€3,400/month** |
| 2024 | 2.05% | 2.45% | +0.40 pp | **€3,400/month** |
| 2025 | 3.18%* | 2.53% | −0.65 pp* | *−€5,525/month (D3 overcounts)* |

*2025 average distorted by Q2 bug (5.8% vs 2.1% canonical).

**Cumulative undetected MRR risk over 4 years (2021–2024): ~€163,200**
This is MRR the business was losing that the board's metric did not surface.

---

## Part 5 — Recommendations for the Room

| Finding | Action |
|---|---|
| Q2 2025 (5.8%) was a data error | Issue formal correction to board. Canonical figure: 2.1%. |
| 2021–2023 numbers used logo churn | Restate historical series under D4 with clear "restated" label |
| 2024 apparent improvement was method change | Add footnote to 2024 board decks: "Method changed Jan 2024; not comparable to 2023" |
| No single source of truth existed | Adopt D4 as the only definition from 2026-04-28 onward |
| Q3–Q4 2021 data from PDF reconstruction | Flag as "unaudited estimates" in any historical presentation |

---

## Appendix — Definition Comparison Reference Card

| Rule | D0 | D1 | D2 | D3 | **D4 (canonical)** |
|---|---|---|---|---|---|
| Unit | Logos | Logos + some MRR | MRR | MRR | nMRR (normalized) |
| Annual contracts | Spike | Spike | Spike | Spike + dupes | Monthly ÷12 |
| Downgrades | No | Discretionary | No | No | ≥€50 AND ≥10% |
| Micro (< €200) | Included | Included | Included | Included | Excluded |
| Trial/promo | Included | Included | Included | Included | Excluded |
| Duplicates | Included | Included | Included | **Double-counted** | Auto-excluded |
| CS saves | Not tracked | Not tracked | Not tracked | Not tracked | Flagged + reversed |
| Pause state | Active | Active | Active | Active | At-risk / auto-churn |
| Churn date | Cancellation event | Cancellation event | Cancellation event | Cancellation event | Contract end date |
| Post-renewal grace | No | No | No | No | 14 days |
| Version tag | No | No | No | No | Yes (every result) |
| Audit trail | No | No | No | No | Yes |
