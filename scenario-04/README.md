# Team Lorenzo Torreggiani

## Participants
- Lorenzo Torreggiani (PM · Architect · Developer · Tester · Data Engineer)

## Scenario
Scenario 4: **Data Analytics — 40 Dashboards, One Metric, Four Different Answers**

---

## What We Built

A complete SaaS churn rate analytics system built end-to-end with Claude Code, replacing 40 dashboards across 3 BI tools (Tableau, Power BI, Looker) with a single versioned source of truth.

The system spans the full stack: a synthetic noisy dataset, a pure-function calculation engine with 18 unit tests, a Streamlit dashboard with Plotly charts, a natural language eval harness using Claude with tool use, a 5-year historical reconciliation, and a board-ready presentation in both PPTX and HTML (reveal.js).

Every metric result carries a `definition_version` tag — the board always knows what they're looking at.

---

## Challenges Attempted

| # | Challenge | Status | Notes |
|---|---|---|---|
| 1 | Stakeholder interviews (VP, CS, Analyst, Finance) | Done | 4 personas, 12 disagreement points resolved |
| 2 | Synthetic noisy dataset (5 CSV files) | Done | 340 CRM duplicates, timezone mismatch, 15 mislabeled segments |
| 3 | Canonical metric definition v1.0 | Done | 8 rules, all numeric thresholds, approved 28 apr 2026 |
| 4 | Calculation engine + unit tests | Done | FastAPI · Pydantic · 18 tests · 100% pass |
| 5 | Streamlit dashboard | Done | 7 KPI cards, trend, breakdown, at-risk table, export CSV |
| 6 | 5-year reconciliation (D0→D4) | Done | Q2 2025 bug identified: 5.8% → 2.1% (+3.7pp falsi) |
| 7 | NL eval harness | Done | 20/20 pass · accuracy 100% · false confidence 0% |
| — | Board presentation (PPTX + HTML) | Done | 10 slides · reveal.js · dark theme |

---

## Key Decisions

**1. Canonical date = `contract_end_date`**
All four stakeholders used different cancellation signals. We anchored everything to `contract_end_date` — the only signal that is contractually unambiguous and immune to timezone or CRM retry issues.

**2. Dual downgrade threshold (≥€50 AND ≥10%)**
A single-threshold rule created both false positives (small % on large contracts) and false negatives (large absolute drops on tiny contracts). The dual condition was the only formulation that satisfied Finance and CS simultaneously.

**3. Engine as pure functions, no I/O**
`calculator.py` takes DataFrames in, returns a `ChurnResult` dataclass out. No database calls, no side effects. This made the 18 unit tests trivial to write and the engine trivially portable to any runtime.

**4. `definition_version` on every result**
Every `ChurnResult` carries `definition_version: "1.0"`. The dashboard footer, glossary, and CSV export all display it. When the definition changes to v1.1, one constant changes and the entire system updates.

**5. NL eval with tool use, not RAG**
The eval harness uses Claude with 4 structured tools (`get_metric`, `compare_periods`, `list_definitions`, `explain_calculation`) rather than embedding the definition in a prompt. This forces the model to retrieve before answering, which is the correct epistemic behavior for a data assistant.

---

## How to Run It

**Requirements**
```bash
cd scenario-04
pip install -r requirements.txt
```

**Generate synthetic data**
```bash
python generate_data.py
```

**Run unit tests**
```bash
pytest engine/tests/ -v
```

**Launch dashboard**
```bash
streamlit run dashboard/app.py
```

**Run NL eval harness (requires Anthropic API key)**
```bash
python -m eval.runner
# dry run (no API calls):
python -m eval.runner --dry-run
# mock run (no API, simulated answers):
python eval/mock_runner.py
```

**Regenerate presentations**
```bash
python generate_ppt.py   # → churn_rate_board_presentation.pptx
python generate_html.py  # → churn_rate_board_presentation.html
```

---

## If We Had More Time

1. **Connect to a real database** — replace `data_loader.py` CSV reads with warehouse queries (BigQuery / Snowflake). The rest of the engine is already agnostic.
2. **FastAPI HTTP server** — `engine/main.py` is wired but not deployed. A `/churn` endpoint would let any BI tool query the canonical number.
3. **Emit the formal Q2 2025 correction** — the bug is documented in `challenge-06-reconciliation.md`. The board note still needs to be issued.
4. **Definition v1.1 review** — scheduled for April 2027. The `DEFINITION_VERSION` constant in `engine/definition.py` is the single change point.
5. **Docker deploy** — containerize the Streamlit app for internal server access without Python installation.

---

## How We Used Claude Code

**What worked exceptionally well**
- **Stakeholder role-play** — Claude stayed in character through 4 complete interviews, surfacing genuine disagreements that shaped the definition.
- **Test-first engine development** — described the desired behavior in plain language, Claude wrote the pure functions and the 18 unit tests simultaneously.
- **Iterative dashboard feedback loop** — showed screenshots, Claude identified the exact CSS property causing overflow and fixed it without touching unrelated code.
- **Presentation generation** — `generate_ppt.py` and `generate_html.py` produced board-quality output in python-pptx and reveal.js from a single prompt.

**What surprised us**
- Claude correctly refused to answer forecasting and PII questions in the eval harness without explicit prompt instructions — the system prompt rules were enough.
- The `titlefont` bug (deprecated Plotly property) was caught and explained precisely from a one-line error message.

**Where it saved the most time**
- The reconciliation table (`challenge-06-reconciliation.md`) — 5 years of quarterly data with 4 definition columns would have taken days manually. Claude built it from the stakeholder interviews in minutes.
- The entire eval scoring system (`judge.py`, `golden_set.py`, `runner.py`) — 3 files, ~400 lines, zero iterations needed.
