"""
Generates the final board presentation for Scenario 04.
Output: scenario-04/churn_rate_board_presentation.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import os

# ── Palette ────────────────────────────────────────────────────────────────
BLUE       = RGBColor(0x1F, 0x77, 0xB4)
DARK       = RGBColor(0x1A, 0x1A, 0x2E)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xF5, 0xF5, 0xF5)
MID_GRAY   = RGBColor(0x88, 0x88, 0x88)
RED        = RGBColor(0xD6, 0x27, 0x28)
GREEN      = RGBColor(0x2C, 0xA0, 0x2C)
ORANGE     = RGBColor(0xFF, 0x7F, 0x0E)
ACCENT     = RGBColor(0x00, 0xB4, 0xD8)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


# ── Helpers ─────────────────────────────────────────────────────────────────
def new_prs() -> Presentation:
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank_slide(prs: Presentation):
    blank_layout = prs.slide_layouts[6]
    return prs.slides.add_slide(blank_layout)


def bg(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def box(slide, l, t, w, h, text, font_size=18, bold=False, color=WHITE,
        bg_color=None, align=PP_ALIGN.LEFT, italic=False, wrap=True):
    txBox = slide.shapes.add_textbox(l, t, w, h)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    if bg_color:
        txBox.fill.solid()
        txBox.fill.fore_color.rgb = bg_color
    return txBox


def rect(slide, l, t, w, h, fill_color: RGBColor, line_color=None):
    shape = slide.shapes.add_shape(1, l, t, w, h)  # MSO_SHAPE_TYPE.RECTANGLE
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
    else:
        shape.line.fill.background()
    return shape


def hline(slide, t, color=MID_GRAY):
    ln = slide.shapes.add_shape(1, Inches(0.5), t, Inches(12.33), Pt(1))
    ln.fill.solid()
    ln.fill.fore_color.rgb = color
    ln.line.fill.background()


def kpi_card(slide, l, t, w, h, label, value, value_color=BLUE, sub=None):
    rect(slide, l, t, w, h, LIGHT_GRAY)
    box(slide, l + Inches(0.15), t + Inches(0.12), w - Inches(0.3), Inches(0.4),
        label, font_size=9, color=MID_GRAY)
    box(slide, l + Inches(0.15), t + Inches(0.42), w - Inches(0.3), Inches(0.55),
        value, font_size=22, bold=True, color=value_color)
    if sub:
        box(slide, l + Inches(0.15), t + Inches(0.92), w - Inches(0.3), Inches(0.3),
            sub, font_size=9, color=MID_GRAY)


def bullet(slide, l, t, w, text, color=DARK, size=14, indent=0):
    prefix = "  " * indent + ("• " if indent == 0 else "– ")
    box(slide, l, t, w, Inches(0.35), prefix + text, font_size=size, color=color)


# ── Slides ───────────────────────────────────────────────────────────────────

def slide_01_title(prs):
    """Cover"""
    s = blank_slide(prs)
    bg(s, DARK)
    rect(s, Inches(0), Inches(0), Inches(4.5), SLIDE_H, BLUE)
    box(s, Inches(0.3), Inches(2.2), Inches(3.9), Inches(0.6),
        "CHURN RATE", font_size=13, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    box(s, Inches(0.3), Inches(2.75), Inches(3.9), Inches(1.6),
        "One Metric.\nOne Definition.\nOne Dashboard.", font_size=24, bold=True,
        color=WHITE, align=PP_ALIGN.LEFT)
    box(s, Inches(0.3), Inches(4.6), Inches(3.9), Inches(0.4),
        "Board Presentation  |  Definition v1.0", font_size=11,
        color=RGBColor(0xCC, 0xDD, 0xEE), align=PP_ALIGN.LEFT)
    box(s, Inches(0.3), Inches(5.1), Inches(3.9), Inches(0.35),
        "Approvata: 28 aprile 2026", font_size=10,
        color=RGBColor(0xAA, 0xBB, 0xCC), align=PP_ALIGN.LEFT)

    box(s, Inches(5.0), Inches(1.5), Inches(7.8), Inches(0.7),
        "Il problema", font_size=13, bold=True, color=ACCENT)
    box(s, Inches(5.0), Inches(2.1), Inches(7.8), Inches(0.45),
        "40 dashboard  ·  3 BI tools  ·  4 risposte diverse per la stessa domanda",
        font_size=14, color=WHITE)
    hline(s, Inches(2.7))
    box(s, Inches(5.0), Inches(2.85), Inches(7.8), Inches(0.7),
        "La soluzione", font_size=13, bold=True, color=ACCENT)
    box(s, Inches(5.0), Inches(3.45), Inches(7.8), Inches(1.4),
        "Una definizione canonica versioned, un motore di calcolo auditabile\n"
        "e un'unica dashboard come source of truth per VP, CS, Finance e Board.",
        font_size=14, color=WHITE)
    hline(s, Inches(5.0))
    box(s, Inches(5.0), Inches(5.15), Inches(2.3), Inches(0.35),
        "Scenario 04  |  Hackathon", font_size=10, color=MID_GRAY)


def slide_02_problem(prs):
    """Il problema — 4 risposte diverse"""
    s = blank_slide(prs)
    bg(s, WHITE)
    rect(s, Inches(0), Inches(0), SLIDE_W, Inches(1.0), DARK)
    box(s, Inches(0.5), Inches(0.2), Inches(12), Inches(0.6),
        "IL PROBLEMA", font_size=11, bold=True, color=ACCENT)
    box(s, Inches(0.5), Inches(0.5), Inches(12), Inches(0.6),
        "Stessa domanda, 4 risposte: «qual è il churn rate di Q2 2025?»",
        font_size=20, bold=True, color=WHITE)

    cw = Inches(2.9)
    gap = Inches(0.2)
    tops = [
        ("VP Sales", "3.1%", "Logo churn\n(senza downgrade)", ORANGE),
        ("CS Head", "2.4%", "CS-accountable\n(escluse bankruptcies)", BLUE),
        ("Finance", "5.8%", "nMRR grezzo\n(con 340 duplicati CRM)", RED),
        ("Analyst", "2.1%", "nMRR canonical\n(D4, senza duplicati)", GREEN),
    ]
    for i, (role, val, method, col) in enumerate(tops):
        lft = Inches(0.5) + i * (cw + gap)
        rect(s, lft, Inches(1.3), cw, Inches(4.2), LIGHT_GRAY)
        rect(s, lft, Inches(1.3), cw, Inches(0.08), col)
        box(s, lft + Inches(0.15), Inches(1.5), cw - Inches(0.3), Inches(0.5),
            role, font_size=13, bold=True, color=DARK)
        box(s, lft + Inches(0.15), Inches(2.1), cw - Inches(0.3), Inches(0.8),
            val, font_size=36, bold=True, color=col)
        box(s, lft + Inches(0.15), Inches(2.9), cw - Inches(0.3), Inches(0.8),
            method, font_size=11, color=MID_GRAY)

    rect(s, Inches(0.5), Inches(5.7), Inches(12.33), Inches(0.9),
         RGBColor(0xFF, 0xF3, 0xCD))
    box(s, Inches(0.7), Inches(5.8), Inches(12), Inches(0.6),
        "⚠  Il 5.8% presentato al board in Q2 2025 era un bug: 340 eventi duplicati da una retry storm "
        "del CRM. Il valore corretto (canonical D4) era 2.1%. La rettifica non è mai stata emessa.",
        font_size=11, color=RGBColor(0x85, 0x53, 0x00))


def slide_03_stakeholders(prs):
    """Stakeholder requirements"""
    s = blank_slide(prs)
    bg(s, WHITE)
    rect(s, Inches(0), Inches(0), SLIDE_W, Inches(1.0), DARK)
    box(s, Inches(0.5), Inches(0.2), Inches(12), Inches(0.35),
        "REQUISITI", font_size=11, bold=True, color=ACCENT)
    box(s, Inches(0.5), Inches(0.5), Inches(12), Inches(0.5),
        "Cosa voleva ogni stakeholder — e dove si contraddicevano",
        font_size=20, bold=True, color=WHITE)

    rows = [
        ("VP Sales & Marketing",    ORANGE, "Churn rate logocentrico (clienti persi, non €). Vuole il toggle CS-accountable."),
        ("CS Head",                  BLUE,   "Escludere bankruptcies e M&A dal suo KPI. Save reversal entro 30gg = non churn."),
        ("Finance Director",         GREEN,  "nMRR normalizzato (annuali ÷12). Micro-contratti <€200/m esclusi dall'headline."),
        ("Data Analyst",             ACCENT, "Definizione versionata, auditabile, con boundary cases espliciti e test automatici."),
    ]
    for i, (name, col, desc) in enumerate(rows):
        t = Inches(1.3) + i * Inches(1.35)
        rect(s, Inches(0.5), t, Inches(0.06), Inches(1.1), col)
        box(s, Inches(0.75), t + Inches(0.05), Inches(11.5), Inches(0.4),
            name, font_size=13, bold=True, color=DARK)
        box(s, Inches(0.75), t + Inches(0.42), Inches(11.5), Inches(0.55),
            desc, font_size=12, color=RGBColor(0x44, 0x44, 0x44))

    hline(s, Inches(6.8))
    box(s, Inches(0.5), Inches(6.9), Inches(12), Inches(0.4),
        "12 punti di disaccordo risolti → 1 documento di definizione approvato da tutti e 4  |  v1.0 — 28 apr 2026",
        font_size=10, color=MID_GRAY)


def slide_04_definition(prs):
    """Definizione canonica v1.0"""
    s = blank_slide(prs)
    bg(s, WHITE)
    rect(s, Inches(0), Inches(0), SLIDE_W, Inches(1.0), DARK)
    box(s, Inches(0.5), Inches(0.2), Inches(12), Inches(0.35),
        "DEFINIZIONE CANONICA  v1.0", font_size=11, bold=True, color=ACCENT)
    box(s, Inches(0.5), Inches(0.5), Inches(12), Inches(0.5),
        "Ogni soglia è numerica. Nessun termine vago.",
        font_size=20, bold=True, color=WHITE)

    rules = [
        ("Formula headline",      "nMRR Lost  ÷  nMRR Active (inizio periodo)  × 100",         BLUE),
        ("Data canonica",         "contract_end_date  — non cancellation_date, non last_login", BLUE),
        ("nMRR normalizzazione",  "Contratti annuali ÷ 12  — nessun picco a scadenza",          BLUE),
        ("Micro-contratti",       "< €200/mese  → esclusi dall'headline, tracciati in micro_churn_rate", ORANGE),
        ("Contraction/downgrade", "Conta se delta ≥ €50  E  ≥ 10% del nMRR precedente (doppia soglia)", ORANGE),
        ("Save reversal",         "Riattivazione entro 30 giorni da contract_end_date  → churn annullato", GREEN),
        ("Grace post-rinnovo",    "Cancellazione entro 14 giorni da rinnovo automatico  → refund, non churn", GREEN),
        ("Pausa contrattuale",    "At-risk fino a 90 giorni. Dopo → churn automatico (pause_expiry)", RED),
    ]
    for i, (label, rule, col) in enumerate(rules):
        t = Inches(1.2) + i * Inches(0.72)
        rect(s, Inches(0.5), t + Inches(0.1), Inches(0.04), Inches(0.45), col)
        box(s, Inches(0.7), t + Inches(0.05), Inches(3.0), Inches(0.4),
            label, font_size=10, bold=True, color=DARK)
        box(s, Inches(3.8), t + Inches(0.05), Inches(9.0), Inches(0.4),
            rule, font_size=10, color=RGBColor(0x33, 0x33, 0x33))
        hline(s, t + Inches(0.62), color=RGBColor(0xE0, 0xE0, 0xE0))


def slide_05_architecture(prs):
    """Architettura della soluzione"""
    s = blank_slide(prs)
    bg(s, WHITE)
    rect(s, Inches(0), Inches(0), SLIDE_W, Inches(1.0), DARK)
    box(s, Inches(0.5), Inches(0.2), Inches(12), Inches(0.35),
        "ARCHITETTURA", font_size=11, bold=True, color=ACCENT)
    box(s, Inches(0.5), Inches(0.5), Inches(12), Inches(0.5),
        "Tre layer indipendenti — dati, calcolo, presentazione",
        font_size=20, bold=True, color=WHITE)

    layers = [
        (Inches(0.5),  "DATA LAYER",       "5 CSV sintetici con noise iniettato\n340 duplicati CRM · timezone mismatch · segment errors",  ORANGE),
        (Inches(4.6),  "ENGINE",            "FastAPI + Pydantic  |  calculator.py\n18 unit test · ogni risultato tagged definition_version", BLUE),
        (Inches(8.7),  "PRESENTATION",      "Streamlit dashboard  +  NL eval harness\nPlotly charts · Claude tool use · 20 golden questions", GREEN),
    ]
    for lft, title, desc, col in layers:
        rect(s, lft, Inches(1.5), Inches(3.8), Inches(3.5), LIGHT_GRAY)
        rect(s, lft, Inches(1.5), Inches(3.8), Inches(0.06), col)
        box(s, lft + Inches(0.2), Inches(1.7), Inches(3.4), Inches(0.5),
            title, font_size=13, bold=True, color=col)
        box(s, lft + Inches(0.2), Inches(2.3), Inches(3.4), Inches(1.0),
            desc, font_size=11, color=DARK)

    # arrows
    for ax in [Inches(4.3), Inches(8.4)]:
        rect(s, ax, Inches(3.1), Inches(0.35), Inches(0.25),
             RGBColor(0xCC, 0xCC, 0xCC))

    box(s, Inches(0.5), Inches(5.3), Inches(12.3), Inches(0.4),
        "Ogni ChurnResult porta: definition_version · period_start · period_end · window · segment_filter",
        font_size=10, color=MID_GRAY, align=PP_ALIGN.CENTER)

    kpis = [
        ("Unit test",         "18 / 18", GREEN),
        ("Golden questions",  "20 / 20", GREEN),
        ("Accuracy",          "100%",    GREEN),
        ("Refusal accuracy",  "100%",    GREEN),
        ("False confidence",  "0%",      GREEN),
    ]
    kw = Inches(2.3)
    for i, (lbl, val, col) in enumerate(kpis):
        lft = Inches(0.5) + i * (kw + Inches(0.08))
        kpi_card(s, lft, Inches(5.8), kw, Inches(1.3), lbl, val, col)


def slide_06_reconciliation(prs):
    """Riconciliazione storica"""
    s = blank_slide(prs)
    bg(s, WHITE)
    rect(s, Inches(0), Inches(0), SLIDE_W, Inches(1.0), DARK)
    box(s, Inches(0.5), Inches(0.2), Inches(12), Inches(0.35),
        "RICONCILIAZIONE STORICA", font_size=11, bold=True, color=ACCENT)
    box(s, Inches(0.5), Inches(0.5), Inches(12), Inches(0.5),
        "5 anni · 4 definizioni · 1 verità canonica",
        font_size=20, bold=True, color=WHITE)

    defs = [
        ("D0  2021–2023",   "Logo churn puro",          BLUE,   "Underestimates revenue impact"),
        ("D1  Q2–Q4 2023",  "Logo + downgrade",          ORANGE, "Metodo cambiato con nuovo CFO"),
        ("D2  2024–Q1 2025","nMRR grezzo",               GREEN,  "Miglioramento reale, ma senza normalizzazione"),
        ("D3  Q2 2025",     "nMRR + duplicati CRM",      RED,    "BUG: 5.8% invece di 2.1% — +3.7pp falsi"),
        ("D4  v1.0 canonica","nMRR normalizzato, clean", ACCENT, "Definizione approvata — retroattiva su 5 anni"),
    ]
    for i, (period, name, col, note) in enumerate(defs):
        t = Inches(1.3) + i * Inches(1.05)
        rect(s, Inches(0.5), t, Inches(0.06), Inches(0.85), col)
        box(s, Inches(0.75), t + Inches(0.02), Inches(2.5), Inches(0.38),
            period, font_size=10, bold=True, color=DARK)
        box(s, Inches(3.3), t + Inches(0.02), Inches(3.5), Inches(0.38),
            name, font_size=11, color=DARK)
        box(s, Inches(7.0), t + Inches(0.02), Inches(6.0), Inches(0.38),
            note, font_size=10, color=MID_GRAY, italic=True)
        hline(s, t + Inches(0.95), color=RGBColor(0xE8, 0xE8, 0xE8))

    rect(s, Inches(0.5), Inches(6.6), Inches(12.3), Inches(0.65),
         RGBColor(0xFF, 0xE8, 0xE8))
    box(s, Inches(0.7), Inches(6.68), Inches(12), Inches(0.5),
        "❌  Q2 2025: il board ha visto 5.8%.  Il valore corretto era 2.1%.  "
        "Delta: +3.7pp.  Causa: 340 eventi duplicati da retry storm CRM.  "
        "Rettifica formale da emettere.",
        font_size=10, color=RED)


def slide_07_dashboard(prs):
    """Dashboard — screenshot e KPI"""
    s = blank_slide(prs)
    bg(s, WHITE)
    rect(s, Inches(0), Inches(0), SLIDE_W, Inches(1.0), DARK)
    box(s, Inches(0.5), Inches(0.2), Inches(12), Inches(0.35),
        "LA DASHBOARD", font_size=11, bold=True, color=ACCENT)
    box(s, Inches(0.5), Inches(0.5), Inches(12), Inches(0.5),
        "Single source of truth — sostituisce 40 dashboard su 3 BI tool",
        font_size=20, bold=True, color=WHITE)

    kpis = [
        ("nMRR Churn Rate",   "0.19%",      BLUE),
        ("MRR Lost",          "€2.446",     BLUE),
        ("MRR Active",        "€1.313.020", BLUE),
        ("Logo Churn Rate",   "0.31%",      BLUE),
        ("CS Saves",          "0",          MID_GRAY),
        ("nMRR rischio 🔴",   "€0",         GREEN),
    ]
    kw = Inches(2.0)
    for i, (lbl, val, col) in enumerate(kpis):
        lft = Inches(0.4) + i * (kw + Inches(0.08))
        kpi_card(s, lft, Inches(1.2), kw, Inches(1.1), lbl, val, col)

    features = [
        ("Vista Financial / Contractual", "Toggle tra nMRR e logo churn"),
        ("Window: Monthly · R30 · R90",   "Flessibilità temporale senza ricalcolo manuale"),
        ("Filtro segmento",               "Enterprise · Mid-market · SMB"),
        ("Toggle CS-accountable",         "Esclude bankruptcies e M&A dal KPI CS"),
        ("Contratti a rischio",           "Scadenza ≤90gg con risk score e CSM owner"),
        ("Export CSV",                    "Tutti i periodi del trend con definition_version"),
        ("Glossario inline",              "Definizione v1.0 sempre visibile, con data approvazione"),
        ("Storico 5 anni",                "Confronto D0→D4 con annotazioni sui cambi di metodo"),
    ]
    for i, (feat, desc) in enumerate(features):
        col_idx = i % 2
        row_idx = i // 2
        lft = Inches(0.5) + col_idx * Inches(6.3)
        t   = Inches(2.6) + row_idx * Inches(0.85)
        rect(s, lft, t, Inches(0.06), Inches(0.6), BLUE)
        box(s, lft + Inches(0.2), t, Inches(2.8), Inches(0.38),
            feat, font_size=11, bold=True, color=DARK)
        box(s, lft + Inches(0.2), t + Inches(0.35), Inches(5.8), Inches(0.38),
            desc, font_size=10, color=MID_GRAY)


def slide_08_eval(prs):
    """Eval harness — risultati"""
    s = blank_slide(prs)
    bg(s, WHITE)
    rect(s, Inches(0), Inches(0), SLIDE_W, Inches(1.0), DARK)
    box(s, Inches(0.5), Inches(0.2), Inches(12), Inches(0.35),
        "NL EVAL HARNESS", font_size=11, bold=True, color=ACCENT)
    box(s, Inches(0.5), Inches(0.5), Inches(12), Inches(0.5),
        "Claude risponde a domande sul churn rate con tool use — 20 golden questions",
        font_size=20, bold=True, color=WHITE)

    kpis = [
        ("Accuracy",         "100%",   "> 80%",  GREEN),
        ("Refusal accuracy", "100%",   "> 90%",  GREEN),
        ("False confidence", "0%",     "< 5%",   GREEN),
        ("Overall pass",     "100%",   "> 80%",  GREEN),
    ]
    kw = Inches(2.9)
    for i, (lbl, val, target, col) in enumerate(kpis):
        lft = Inches(0.5) + i * (kw + Inches(0.15))
        kpi_card(s, lft, Inches(1.3), kw, Inches(1.3), lbl, val, col,
                 sub=f"Target: {target}")

    types = [
        ("answerable",  4,  "Lookup metriche con get_metric"),
        ("comparison",  3,  "Confronto periodi e segmenti"),
        ("definition",  5,  "Regole e soglie della definizione"),
        ("edge_case",   3,  "Boundary cases (grace period, micro, save)"),
        ("refusal",     5,  "Rifiuto corretto (forecast, PII, out-of-range)"),
    ]
    box(s, Inches(0.5), Inches(2.8), Inches(12), Inches(0.4),
        "Distribuzione per tipo  (20 domande totali)", font_size=12,
        bold=True, color=DARK)
    for i, (qtype, count, desc) in enumerate(types):
        t = Inches(3.25) + i * Inches(0.72)
        bw = Inches(count * 1.8)
        rect(s, Inches(0.5), t, bw, Inches(0.5), BLUE)
        box(s, Inches(0.5) + bw + Inches(0.1), t + Inches(0.06),
            Inches(9.0), Inches(0.38),
            f"{qtype}  ({count})  —  {desc}", font_size=11, color=DARK)

    hline(s, Inches(7.0))
    box(s, Inches(0.5), Inches(7.1), Inches(12), Inches(0.35),
        "Tool use: get_metric · compare_periods · list_definitions · explain_calculation  "
        "|  Prompt caching sul system prompt  |  Agentic loop max 5 turns",
        font_size=9, color=MID_GRAY)


def slide_09_next(prs):
    """Next steps"""
    s = blank_slide(prs)
    bg(s, WHITE)
    rect(s, Inches(0), Inches(0), SLIDE_W, Inches(1.0), DARK)
    box(s, Inches(0.5), Inches(0.2), Inches(12), Inches(0.35),
        "NEXT STEPS", font_size=11, bold=True, color=ACCENT)
    box(s, Inches(0.5), Inches(0.5), Inches(12), Inches(0.5),
        "Dalla demo alla produzione",
        font_size=20, bold=True, color=WHITE)

    steps = [
        ("1", "Rettifica formale Q2 2025",
         "Emettere la nota al board: churn reale 2.1%, non 5.8%. Aggiornare i verbali.",
         RED, "Immediato"),
        ("2", "Deploy su server interno",
         "Containerizzare con Docker, deploy su infrastruttura aziendale. "
         "Accesso via browser, nessuna installazione per il CFO.",
         ORANGE, "2 settimane"),
        ("3", "Connessione DB di produzione",
         "Sostituire i CSV con lettura diretta dal warehouse. "
         "Mantenere data_loader.py come unico punto di accesso ai dati.",
         BLUE, "1 mese"),
        ("4", "Definizione v1.1",
         "Revisione annuale: aggiornare DEFINITION_VERSION nel codice. "
         "Footer e glossario si aggiornano automaticamente.",
         GREEN, "Apr 2027"),
        ("5", "Deprecazione dashboard legacy",
         "Dopo 30 giorni di run parallelo, disattivare i 40 dashboard esistenti. "
         "Comunicare a tutti i team il nuovo URL unico.",
         ACCENT, "3 mesi"),
    ]

    for i, (num, title, desc, col, timing) in enumerate(steps):
        t = Inches(1.2) + i * Inches(1.1)
        rect(s, Inches(0.5), t + Inches(0.1), Inches(0.5), Inches(0.5), col)
        box(s, Inches(0.5), t + Inches(0.12), Inches(0.5), Inches(0.4),
            num, font_size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        box(s, Inches(1.2), t + Inches(0.05), Inches(3.5), Inches(0.4),
            title, font_size=13, bold=True, color=DARK)
        box(s, Inches(1.2), t + Inches(0.45), Inches(9.0), Inches(0.45),
            desc, font_size=10, color=MID_GRAY)
        rect(s, Inches(11.5), t + Inches(0.15), Inches(1.5), Inches(0.35), col)
        box(s, Inches(11.5), t + Inches(0.18), Inches(1.5), Inches(0.3),
            timing, font_size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    prs = new_prs()
    slide_01_title(prs)
    slide_02_problem(prs)
    slide_03_stakeholders(prs)
    slide_04_definition(prs)
    slide_05_architecture(prs)
    slide_06_reconciliation(prs)
    slide_07_dashboard(prs)
    slide_08_eval(prs)
    slide_09_next(prs)

    out = os.path.join(os.path.dirname(__file__), "churn_rate_board_presentation.pptx")
    prs.save(out)
    print(f"Saved: {out}  ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
