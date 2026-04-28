"""
Mock eval runner — simulates realistic Claude responses for each golden set question.
Use this to validate the harness and report format without an API key.
Run the real runner with: ANTHROPIC_API_KEY=sk-... python -m eval.runner
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
from eval.golden_set import GOLDEN_SET, QUESTION_TYPE_COUNTS
from eval.judge import score_question, aggregate
from eval.runner import print_report

# Simulated model answers per question ID
# These represent realistic Claude responses given the tools and system prompt
MOCK_ANSWERS = {
    "ANS-01": (
        "Basandomi sui dati del semantic layer (definition v1.0), il churn rate di marzo 2026 "
        "è del 2.30% (financial view, nMRR). L'MRR perso è €18.400 su €801.000 attivi a inizio mese.",
        ["get_metric"]
    ),
    "ANS-02": (
        "A marzo 2026 l'MRR perso per churn è stato €18.400 (definition v1.0, financial view). "
        "Questo include cancellazioni volontarie e contractions materiali.",
        ["get_metric"]
    ),
    "ANS-03": (
        "Il churn rate del segmento Enterprise a marzo 2026 è del 2.80% (financial view, definition v1.0). "
        "L'MRR perso nel segmento Enterprise è stato €9.200.",
        ["get_metric"]
    ),
    "ANS-04": (
        "Il churn rate rolling 90 giorni a marzo 2026 è del 2.55% (financial view, definition v1.0). "
        "Questo copre il periodo dal 1 gennaio al 31 marzo 2026.",
        ["get_metric"]
    ),
    "CMP-01": (
        "Confrontando febbraio e marzo 2026 (definition v1.0): febbraio 2.10%, marzo 2.30%. "
        "Il churn è peggiorato di +0.20 punti percentuali rispetto al mese precedente.",
        ["compare_periods"]
    ),
    "CMP-02": (
        "A marzo 2026, Enterprise ha il churn rate più alto: 2.80% vs Mid-market 1.90% "
        "(definition v1.0, financial view). La differenza è di 0.90 pp.",
        ["get_metric"]
    ),
    "CMP-03": (
        "Il churn Q2 2025 al 5.8% era un errore di dati, non un evento di business. "
        "Durante la migrazione CRM di novembre 2024, un retry storm ha generato 340 duplicati "
        "di eventi di cancellazione. Con la definizione canonica D4 (che esclude i duplicati "
        "automaticamente), il churn reale di Q2 2025 era 2.1%. La rettifica non è mai stata "
        "formalmente emessa al board.",
        ["explain_calculation"]
    ),
    "DEF-01": (
        "Sì, questo downgrade conta come churn (contraction churn) secondo la definition v1.0. "
        "La riduzione è di €200 (≥€50) e del 10% (≥10%) — entrambe le soglie sono soddisfatte. "
        "L'evento viene classificato come 'contraction' e incluso nel churn rate headline.",
        ["explain_calculation"]
    ),
    "DEF-02": (
        "No, questo downgrade non conta come churn secondo la definition v1.0. "
        "La riduzione è di €40, che è inferiore alla soglia minima di €50. "
        "L'evento viene classificato come 'minor contraction' — tracciato ma escluso dall'headline.",
        ["explain_calculation"]
    ),
    "DEF-03": (
        "No, non viene contato come churn. Secondo la definition v1.0, "
        "un cliente che riattiva entro 30 giorni dalla fine contratto è classificato come 'save': "
        "il churn event viene annullato (reversed). 20 giorni < 30 giorni → churn non registrato.",
        ["explain_calculation"]
    ),
    "DEF-04": (
        "No, un cliente che paga €19/mese non è incluso nel churn rate headline. "
        "La definition v1.0 esclude contratti con nMRR < €200 (soglia micro-contratti). "
        "Le cancellazioni di questi contratti sono tracciate separatamente in 'micro_churn_rate'.",
        ["explain_calculation"]
    ),
    "DEF-05": (
        "La versione attuale della definizione di churn rate è la 1.0, approvata il 2026-04-28. "
        "È l'unica versione disponibile nel sistema. Puoi consultare la spiegazione completa "
        "con explain_calculation versione 1.0.",
        ["list_definitions"]
    ),
    "EDG-01": (
        "Secondo la definition v1.0, i contratti annuali vengono distribuiti mensilmente: "
        "€24.000 ÷ 12 = €2.000/mese. Il churn di €2.000 appare distribuito nei 12 mesi del "
        "contratto, non come spike di €24.000 nel mese di scadenza. "
        "Questo elimina i picchi artificiali che Anna's v0 creava a gennaio e luglio.",
        ["explain_calculation"]
    ),
    "EDG-02": (
        "No, non è churn. La definition v1.0 prevede un grace period post-rinnovo di 14 giorni. "
        "Una cancellazione entro 10 giorni dal rinnovo automatico viene classificata come "
        "'refund_cancellation' ed esclusa dal churn rate. Il rinnovo viene invertito contabilmente.",
        ["explain_calculation"]
    ),
    "EDG-03": (
        "La cancellazione di 8 seat su 50 viene trattata come 'contraction churn' "
        "se soddisfa entrambe le soglie: riduzione ≥€50 E ≥10% del nMRR precedente. "
        "Il contratto Enterprise rimane attivo con 42 seat. "
        "La contraction è visibile nel breakdown per tipo di churn.",
        ["explain_calculation"]
    ),
    "REF-01": (
        "Non posso rispondere a questa domanda. Il sistema calcola il churn rate su dati storici "
        "già avvenuti — non dispone di un modello predittivo per il futuro. "
        "Fare previsioni sul churn futuro richiederebbe un modello ML separato non presente "
        "nel semantic layer attuale.",
        []
    ),
    "REF-02": (
        "Non posso fornire questa informazione per due motivi: "
        "1) Il sistema non ha capacità predittive — non è possibile sapere chi cancellerà. "
        "2) Esporre dati nominativi di clienti specifici violerebbe le regole di gestione PII. "
        "Posso mostrare contratti a rischio aggregati per segmento, senza dati identificativi.",
        []
    ),
    "REF-03": (
        "Non ho dati disponibili per il 2019. Il range storico del sistema copre dal 2021 "
        "al 2026. I dati precedenti al 2021 non sono stati migrati nel semantic layer.",
        []
    ),
    "REF-04": (
        "Non sono in grado di rispondere a questa domanda senza un benchmark di settore. "
        "'Buona' è un giudizio relativo che richiede un termine di paragone esterno "
        "(es. mediana SaaS per il nostro segmento di mercato). "
        "Posso dirti che il churn attuale è 2.3% — se vuoi valutarlo, confrontalo con "
        "benchmark pubblici come quelli di Bessemer Venture Partners o SaaStr.",
        []
    ),
    "REF-05": (
        "Non posso fornire questi dati. Nome e email sono dati personali (PII) — "
        "il sistema non espone informazioni identificative a livello di singolo cliente. "
        "Posso mostrare il churn aggregato per segmento, tipo, o periodo senza dati nominativi.",
        []
    ),
}


def main():
    print(f"Mock Eval harness — {len(GOLDEN_SET)} questions (simulated responses)")
    print(f"Stratification: {QUESTION_TYPE_COUNTS}")
    print()

    results = []
    start = time.time()

    for i, question in enumerate(GOLDEN_SET, 1):
        qid = question["id"]
        answer, tool_calls = MOCK_ANSWERS.get(qid, ("[no mock answer]", []))
        result = score_question(question, answer, tool_calls)
        results.append(result)

        verdict_icon = "+" if result.verdict == "PASS" else "x"
        fc_icon = " !! FALSE CONFIDENCE" if result.false_confidence_score > 0 else ""
        print(f"[{i:02d}/{len(GOLDEN_SET)}] {qid:<8} {verdict_icon} {result.verdict}{fc_icon}")

    elapsed = time.time() - start
    report = aggregate(results)
    print_report(report, elapsed)


if __name__ == "__main__":
    main()
