# Challenge 1 — Stakeholder Requirements
## Domain: SaaS Subscription | Metric: Churn Rate
## Version: 1.0 | Date: 2026-04-28

---

## Stakeholder Interviews Summary

### 1. Sarah Chen — VP of Revenue

**Perspective:** Board-level, revenue-first.

**Definition of Churn Rate:**
> Percentage of MRR lost each month due to cancellations and downgrades, excluding expansions.
> Formula: (MRR lost from cancellations + MRR lost from downgrades) / MRR at start of month

**Requirements:**
- Revenue churn (MRR-based), NOT logo churn (customer count-based)
- Expansions reported separately — must NOT offset churn in the main metric
- Granularity: monthly for board, weekly for internal monitoring
- Drill-down by segment: Enterprise, Mid-market, SMB
- Audience: monthly → board + CEO; weekly → VP + CS team; raw → Anna + Marco

**Edge cases raised:**
- Customer cancels and returns within 30 days → should NOT count as churn
- Annual contracts: churn at expiration date or distributed monthly?
- Downgrade below a threshold → not all downgrades should count as churn
- Needs a defined numeric threshold for "material" downgrade

---

### 2. Anna Ferretti — Senior Analyst

**Perspective:** Technical, data-first. Built the existing dashboards 3 years ago on requirements from the previous CFO.

**Definition of Churn Rate:**
> Number of customers (logos) with an active contract at start of month that no longer have one at end of month, divided by total active customers at start of month.
> Formula: cancelled_customers / active_customers_start_of_month

**Requirements:**
- Logo churn, NOT revenue churn
- Calculated on monthly fixed windows
- Source: SQL view on Snowflake, dbt job, nightly refresh

**Known issues (open, unresolved):**
1. **Timezone mismatch**: CRM cancellation data in UTC, billing system in CET → 8–12 records/month fall in the wrong month
2. **Duplicate records**: ~340 duplicate cancellation events from a CRM migration retry storm in November → manually filtered via hardcoded blacklist table
3. **Enterprise seat cancellations**: partial seat cancellations on Enterprise contracts have no defined rule → currently ignored

**Edge cases raised:**
- Customers on contractual pause → counted as active (no rule for at-risk state)
- Customers who return within 30 days → counted as churn out + new customer in (double-counted)
- Downgrades → NOT counted at all (only full cancellations count)
- Annual contracts → churn recorded entirely in the month of expiration (creates artificial spikes in January and July)

**Technical debt:**
- No versioning of the SQL logic
- No automated tests
- Blacklist table updated manually
- No audit trail on calculation changes

---

### 3. Marco Bianchi — Head of Customer Success

**Perspective:** Operational, team-performance-first. Personally measured on churn rate.

**Definition of Churn Rate:**
> Preventable revenue lost, net of CS retention actions, over a 90-day rolling window.
> Distinguishes: voluntary vs involuntary churn, preventable vs unpreventable.

**Requirements:**
- Must distinguish `churn_type`: voluntary / involuntary / contraction
- Must flag `saved_by_cs`: true if a retention activity occurred in the 30 days before cancellation or reactivation
- Customers returning within 30 days → classified as **save**, NOT churn + new customer
- Customers on contractual pause → classified as **at-risk**, NOT active
- Partial seat cancellations on Enterprise → tracked as **contraction**, NOT ignored
- Rolling windows: 30 / 60 / 90 days — not only monthly fixed

**Additional definitions proposed:**
- **Churn date**: last day of active service (not the cancellation signature date)
- **Minimum contract threshold**: contracts < 200€ MRR tracked but excluded from the main churn rate (not economically actionable)
- **Post-renewal grace period**: cancellations within 14 days of automatic renewal → classified as **refund**, not churn

**Edge cases raised:**
- Involuntary churn (customer bankruptcy, M&A) → must be excluded from CS-accountable churn
- CS saves with discount → revenue impact visible separately (Marco's win, Giulia's partial loss)
- Micro-cancellations (< 200€ MRR) → tracked but not included in headline rate

---

### 4. Giulia Rossi — Finance Director

**Perspective:** Financial reporting, forecast accuracy, audit compliance.

**Definition of Churn Rate:**
> MRR normalized churn: contracted recurring revenue lost in a period, calculated on accrual basis (date of contract end, not cash received), distributed monthly for annual contracts.

**Requirements:**
- MRR normalized: annual contracts split into monthly installments (€12,000/year = €1,000/month churn when not renewed)
- Accrual basis: use **contract end date**, not last day of active service, not cancellation request date
- CS saves with discount → show both the save (operational) and the revenue delta (financial) — never merge them
- Export: structured CSV by day 3 of each month, fixed schema, importable directly into ARR forecast model
- Versioned history: ability to reproject historical data with new definition AND compare old vs new definition side by side
- Audit trail: every metric value must carry → definition version, calculation timestamp, approver
- Automatic alerts: notify Finance if MRR churn rate exceeds a configurable threshold (proposed: 1.8%/month) before board review

**Additional requirements:**
- Auto-reconciliation against Stripe: expose discrepancies (pro-rata refunds, mid-cycle upgrades, applied credits) explicitly instead of hiding them
- Two parallel views: **contractual view** (contracts lost) vs **financial view** (MRR lost) — togglable, not a forced choice
- 90-day forward projection: contracts expiring in 90 days + risk indicator (e.g. no login in last 30 days = high risk)
- Glossary embedded in dashboard: every metric shows definition version, formula, exclusions, approval date — eliminates "how was this calculated?" questions in review meetings
- Exclude **administrative cancellations**: fraudulent accounts, non-payers after 90-day collections, migration duplicates → auto-excluded with audit log, not manual filter
- Exclude customers in **trial or promotional period** (e.g. €1 for 3 months) from headline churn until first full-price renewal

---

## Explicit Disagreements Matrix

| Topic | Sarah (VP) | Anna (Analyst) | Marco (CS) | Giulia (Finance) |
|---|---|---|---|---|
| **Unit of measure** | Revenue (MRR) | Logos (customers) | Revenue, preventable only | Revenue, normalized MRR |
| **Downgrade treatment** | Counts as churn | Does NOT count | Counts as contraction | Counts as partial revenue churn |
| **Annual contract** | Distribute monthly | Spike at expiration | Distribute monthly | Distribute monthly (accrual) |
| **Customer returns in 30 days** | NOT churn | Churn + new customer | Save (not churn) | Not churn (refund or save) |
| **Churn date** | Not specified | Cancellation event date | Last active service day | Contract end date |
| **Contractual pause** | Not specified | Active | At-risk (separate state) | At-risk (separate state) |
| **Enterprise seat cancellation** | Not specified | Ignored | Contraction (tracked) | Contraction (tracked) |
| **Involuntary churn** | Included | Included | Excluded from CS metric | Included in financial metric |
| **Micro-contracts < 200€ MRR** | Not specified | Included | Excluded from headline | Excluded from headline |
| **Post-renewal cancellation (≤14d)** | Not specified | Counted as churn | Refund, not churn | Refund, not churn |
| **Trial/promo period customers** | Not specified | Included | Not specified | Excluded until first full-price renewal |
| **Calculation window** | Monthly + weekly | Monthly fixed | 30 / 60 / 90d rolling | Monthly (accrual) |
| **CS saves with discount** | Not specified | Not tracked | Victory (save flagged) | Partial revenue loss (both shown) |

---

## Open Questions to Resolve in Metric Definition (Challenge 3)

1. **Primary unit**: is the headline churn rate revenue-based or logo-based? (Sarah vs Anna)
2. **Downgrade threshold**: at what € delta does a downgrade become "material" churn? (no one defined a number)
3. **Canonical churn date**: cancellation event / last active day / contract end date?
4. **Annual contract allocation**: spike at expiration vs monthly distribution?
5. **Return window**: what is the exact day threshold to classify a return as a save vs a new acquisition?
6. **Contractual pause**: maximum duration before it becomes churn? Who decides?
7. **CS save flag**: who maintains the retention activity log? Is it source-of-truth?
8. **Minimum MRR threshold**: confirm 200€ as the boundary for headline inclusion?
9. **Post-renewal grace period**: confirm 14 days? Does it apply to both monthly and annual renewals?
10. **Involuntary churn**: which specific event types qualify? (bankruptcy, M&A, fraud, collections)
11. **Trial exclusion boundary**: first full-price renewal or first invoice above X€?
12. **Segment definitions**: exact MRR ranges for Enterprise / Mid-market / SMB?

---

## Agreed Points (no disagreement across stakeholders)

- Expansions must NOT offset churn in the headline metric
- Administrative cancellations (fraud, non-payers, migration duplicates) should be excluded with an audit log
- The metric must carry a definition version tag on every result
- Historical recalculation must be possible when the definition changes
- A single dashboard must replace the existing fragmented views
- Natural-language querying is a desired capability
