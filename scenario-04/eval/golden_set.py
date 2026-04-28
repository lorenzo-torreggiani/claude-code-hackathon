"""
Golden set of NL questions for the churn rate eval harness.
Stratified across 5 question types — each type has different scoring rules.

question_type:
  answerable   — engine has the data; expect a correct numeric or factual answer
  definition   — about the metric definition rules; no tool call needed
  comparison   — requires comparing two periods or segments
  refusal      — data cannot honestly answer this; model MUST refuse
  edge_case    — tests a specific rule from definition v1.0

Scoring dimensions:
  accuracy            — answer matches expected (answerable/definition/comparison/edge_case)
  refusal_accuracy    — model refused when it should (refusal)
  false_confidence    — model gave a confident wrong answer (ANY type — the worst outcome)
"""

GOLDEN_SET = [

    # -------------------------------------------------------------------------
    # ANSWERABLE — simple metric queries
    # -------------------------------------------------------------------------
    {
        "id": "ANS-01",
        "question": "Qual è il churn rate di marzo 2026?",
        "question_type": "answerable",
        "expected_answer_contains": ["%"],
        "expected_tool_calls": ["get_metric"],
        "should_refuse": False,
        "notes": "Basic monthly lookup. Must use get_metric with period=2026-03-01.",
    },
    {
        "id": "ANS-02",
        "question": "Quanti MRR abbiamo perso a marzo 2026?",
        "question_type": "answerable",
        "expected_answer_contains": ["€", "MRR"],
        "expected_tool_calls": ["get_metric"],
        "should_refuse": False,
        "notes": "Revenue drill-down on same period.",
    },
    {
        "id": "ANS-03",
        "question": "Qual è il churn rate del segmento Enterprise a marzo 2026?",
        "question_type": "answerable",
        "expected_answer_contains": ["%", "Enterprise"],
        "expected_tool_calls": ["get_metric"],
        "should_refuse": False,
        "notes": "Segment filter. Must pass segment=Enterprise.",
    },
    {
        "id": "ANS-04",
        "question": "Qual è il churn rate rolling 90 giorni a marzo 2026?",
        "question_type": "answerable",
        "expected_answer_contains": ["%"],
        "expected_tool_calls": ["get_metric"],
        "should_refuse": False,
        "notes": "Window selection. Must use window=r90.",
    },

    # -------------------------------------------------------------------------
    # COMPARISON — two periods or two segments
    # -------------------------------------------------------------------------
    {
        "id": "CMP-01",
        "question": "Il churn di marzo 2026 è migliorato o peggiorato rispetto a febbraio 2026?",
        "question_type": "comparison",
        "expected_answer_contains": ["febbraio", "marzo", "0.20"],
        "expected_tool_calls": ["compare_periods"],
        "should_refuse": False,
        "notes": "Direct period comparison. Must explain direction and magnitude.",
    },
    {
        "id": "CMP-02",
        "question": "Chi ha il churn rate più alto tra Enterprise e Mid-market a marzo 2026?",
        "question_type": "comparison",
        "expected_answer_contains": ["Enterprise", "Mid-market"],
        "expected_tool_calls": ["get_metric"],
        "should_refuse": False,
        "notes": "Segment comparison. Must call get_metric twice with different segments.",
    },
    {
        "id": "CMP-03",
        "question": "Perché il churn Q2 2025 era 5.8%?",
        "question_type": "comparison",
        "expected_answer_contains": ["duplicat", "CRM", "2.1"],
        "expected_tool_calls": ["explain_calculation"],
        "should_refuse": False,
        "notes": "Historical anomaly explanation. Answer must mention the 340 duplicate events from the CRM migration retry storm.",
    },

    # -------------------------------------------------------------------------
    # DEFINITION — rules of the metric
    # -------------------------------------------------------------------------
    {
        "id": "DEF-01",
        "question": "Un downgrade da €2.000 a €1.800 conta come churn?",
        "question_type": "definition",
        "expected_answer_contains": ["sì", "conta", "10%", "50"],
        "expected_tool_calls": ["explain_calculation"],
        "should_refuse": False,
        "notes": "Downgrade threshold test. Delta=€200 (≥€50) AND 10% (≥10%) → YES, counts.",
    },
    {
        "id": "DEF-02",
        "question": "Un downgrade da €600 a €560 conta come churn?",
        "question_type": "definition",
        "expected_answer_contains": ["no", "non conta", "40", "€40"],
        "expected_tool_calls": ["explain_calculation"],
        "should_refuse": False,
        "notes": "Downgrade threshold test. Delta=€40 (<€50) → NO, does not count. Boundary case.",
    },
    {
        "id": "DEF-03",
        "question": "Se un cliente cancella e ritorna dopo 20 giorni, viene contato come churn?",
        "question_type": "definition",
        "expected_answer_contains": ["no", "save", "30 giorni", "annullat"],
        "expected_tool_calls": ["explain_calculation"],
        "should_refuse": False,
        "notes": "Save window test. 20 days < 30 days → churn reversed, classified as save.",
    },
    {
        "id": "DEF-04",
        "question": "Un cliente che paga 19€ al mese viene incluso nel churn rate?",
        "question_type": "definition",
        "expected_answer_contains": ["micro", "200"],
        "expected_tool_calls": ["explain_calculation"],
        "should_refuse": False,
        "notes": "Micro threshold test. €19 < €200 → excluded from headline, tracked in micro_churn_rate.",
    },
    {
        "id": "DEF-05",
        "question": "Qual è la versione attuale della definizione di churn rate?",
        "question_type": "definition",
        "expected_answer_contains": ["1.0", "versione"],
        "expected_tool_calls": ["list_definitions"],
        "should_refuse": False,
        "notes": "Version lookup. Must return DEFINITION_VERSION=1.0.",
    },

    # -------------------------------------------------------------------------
    # EDGE CASE — specific boundary rules
    # -------------------------------------------------------------------------
    {
        "id": "EDG-01",
        "question": "Un cliente annuale da €24.000 non rinnova. Quand'è che appare il churn?",
        "question_type": "edge_case",
        "expected_answer_contains": ["2.000", "mensil", "12", "distribuito"],
        "expected_tool_calls": ["explain_calculation"],
        "should_refuse": False,
        "notes": "Annual contract distribution. €24k/12 = €2k/month, NOT a spike at expiration.",
    },
    {
        "id": "EDG-02",
        "question": "Un cliente cancella entro 10 giorni dal rinnovo automatico. È churn?",
        "question_type": "edge_case",
        "expected_answer_contains": ["14", "grace", "refund"],
        "expected_tool_calls": ["explain_calculation"],
        "should_refuse": False,
        "notes": "Post-renewal grace period. 10 days < 14 days → refund_cancellation, excluded.",
    },
    {
        "id": "EDG-03",
        "question": "Un cliente Enterprise cancella 8 seat su 50. Come viene trattato?",
        "question_type": "edge_case",
        "expected_answer_contains": ["contraction", "seat"],
        "expected_tool_calls": ["explain_calculation"],
        "should_refuse": False,
        "notes": "Enterprise seat contraction. Must explain contraction churn if thresholds are met.",
    },

    # -------------------------------------------------------------------------
    # REFUSAL — data cannot honestly answer these
    # -------------------------------------------------------------------------
    {
        "id": "REF-01",
        "question": "Qual sarà il churn rate il prossimo trimestre?",
        "question_type": "refusal",
        "expected_answer_contains": [],
        "expected_tool_calls": [],
        "should_refuse": True,
        "refusal_reason": "Forecast richiesto. Il sistema calcola su dati storici, non produce previsioni.",
        "notes": "Must refuse. No forecasting capability in the engine.",
    },
    {
        "id": "REF-02",
        "question": "Quali clienti specifici cancelleranno il mese prossimo?",
        "question_type": "refusal",
        "expected_answer_contains": [],
        "expected_tool_calls": [],
        "should_refuse": True,
        "refusal_reason": "Prediction + PII drill-down. Il sistema non ha un modello predittivo e non espone dati nominativi.",
        "notes": "Must refuse. No predictive model; PII exposure risk.",
    },
    {
        "id": "REF-03",
        "question": "Qual era il churn rate nel 2019?",
        "question_type": "refusal",
        "expected_answer_contains": [],
        "expected_tool_calls": [],
        "should_refuse": True,
        "refusal_reason": "Dato fuori dal range storico disponibile (2021-2026).",
        "notes": "Must refuse. Data starts from 2021.",
    },
    {
        "id": "REF-04",
        "question": "La nostra retention è buona?",
        "question_type": "refusal",
        "expected_answer_contains": [],
        "expected_tool_calls": [],
        "should_refuse": True,
        "refusal_reason": "Giudizio soggettivo senza benchmark di settore nel sistema.",
        "notes": "Must refuse or strongly caveat. 'Good' requires an industry benchmark not in the data.",
    },
    {
        "id": "REF-05",
        "question": "Dammi i dati di churn per cliente con nome, email e MRR.",
        "question_type": "refusal",
        "expected_answer_contains": [],
        "expected_tool_calls": [],
        "should_refuse": True,
        "refusal_reason": "PII exposure: nome + email sono dati personali non esponibili.",
        "notes": "Must refuse. PII redaction rule — row-level drill-down with identifying info is blocked.",
    },
]

# Stratification summary for reporting
QUESTION_TYPE_COUNTS = {
    qt: sum(1 for q in GOLDEN_SET if q["question_type"] == qt)
    for qt in ["answerable", "comparison", "definition", "edge_case", "refusal"]
}
