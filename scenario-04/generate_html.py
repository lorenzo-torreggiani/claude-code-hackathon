"""
Generates churn_rate_board_presentation.html
Self-contained reveal.js presentation (CDN) — 9 slides, dark theme.
Run: python scenario-04/generate_html.py
"""

import os

HTML = r"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Churn Rate Analytics — Board Presentation</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.1/reveal.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.1/theme/black.min.css">
<style>
  :root {
    --bg:       #0d1b2a;
    --surface:  #162b40;
    --surface2: #1c354d;
    --cyan:     #00c2cb;
    --cyan-dim: #007a82;
    --white:    #ffffff;
    --gray1:    #c8d8e8;
    --gray2:    #6e8ca8;
    --red:      #ff4d6d;
    --orange:   #ff9f1c;
    --green:    #06d6a0;
    --purple:   #9b5de5;
  }

  .reveal-viewport { background: var(--bg); }
  .reveal .slides   { text-align: left; }
  .reveal           { font-family: 'Segoe UI', system-ui, sans-serif; }

  /* ── typography ── */
  .reveal h1,.reveal h2,.reveal h3 { text-transform: none; letter-spacing: -0.02em; }
  .tag   { font-size:.6em; font-weight:700; text-transform:uppercase;
           letter-spacing:.12em; color:var(--cyan); }
  .muted { color:var(--gray2); font-size:.7em; }

  /* ── layout utils ── */
  .cols2  { display:grid; grid-template-columns:1fr 1fr;    gap:1.2rem; }
  .cols3  { display:grid; grid-template-columns:1fr 1fr 1fr; gap:1.2rem; }
  .cols4  { display:grid; grid-template-columns:repeat(4,1fr); gap:.8rem; }
  .cols6  { display:grid; grid-template-columns:repeat(6,1fr); gap:.6rem; }

  /* ── card ── */
  .card {
    background: var(--surface);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    position: relative;
    overflow: hidden;
  }
  .card::before {
    content:''; position:absolute; top:0; left:0;
    width:100%; height:4px;
  }
  .card.cyan::before   { background:var(--cyan);   }
  .card.orange::before { background:var(--orange); }
  .card.green::before  { background:var(--green);  }
  .card.red::before    { background:var(--red);    }
  .card.purple::before { background:var(--purple); }
  .card.gray::before   { background:var(--gray2);  }
  .card-label { font-size:.55em; font-weight:700; text-transform:uppercase;
                letter-spacing:.1em; color:var(--gray2); margin-bottom:.3rem; }
  .card-value { font-size:1.8em; font-weight:800; line-height:1; }
  .card-sub   { font-size:.55em; color:var(--gray2); margin-top:.4rem; }

  /* ── kpi hero ── */
  .kpi-hero { font-size:3em; font-weight:900; line-height:1; }

  /* ── row card ── */
  .row-card {
    background: var(--surface);
    border-radius: 8px;
    padding:.7rem 1rem;
    display:grid;
    grid-template-columns: 2.5rem 1fr auto;
    align-items:center;
    gap:1rem;
    margin-bottom:.5rem;
  }
  .row-card .num {
    width:2.2rem; height:2.2rem; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-weight:800; font-size:.9em; color:var(--bg); flex-shrink:0;
  }
  .row-card .timing {
    font-size:.6em; font-weight:700; padding:.25rem .7rem;
    border-radius:20px; white-space:nowrap; color:var(--bg);
  }

  /* ── accent bar ── */
  .accent-bar {
    height:3px; background:var(--cyan);
    border-radius:2px; margin:1rem 0;
  }

  /* ── def rule ── */
  .def-rule {
    background:var(--surface); border-radius:8px;
    padding:.6rem 1rem; margin-bottom:.5rem;
    border-left:3px solid;
  }
  .def-rule .rule-label { font-size:.6em; font-weight:700;
    text-transform:uppercase; letter-spacing:.08em; }
  .def-rule .rule-text  { font-size:.75em; color:var(--gray1); margin-top:.15rem; }

  /* ── timeline row ── */
  .timeline-row {
    display:grid;
    grid-template-columns: 2.8rem 5.5rem 1fr 1fr;
    align-items:center; gap:.8rem;
    background:var(--surface); border-radius:8px;
    padding:.5rem .8rem; margin-bottom:.4rem;
    border-left:4px solid;
  }
  .badge {
    display:inline-block; padding:.15rem .5rem;
    border-radius:20px; font-size:.55em; font-weight:700;
    color:var(--bg); white-space:nowrap;
  }

  /* ── warning box ── */
  .warn-box {
    background:#2a1015; border-left:4px solid var(--red);
    border-radius:8px; padding:.7rem 1rem; font-size:.7em; color:var(--gray1);
  }
  .warn-box strong { color:var(--red); }

  /* ── section slide header ── */
  .slide-header { margin-bottom:1.2rem; }
  .slide-header h2 { font-size:1.25em; font-weight:800; margin:.3rem 0 .1rem; }
  .slide-header .sub { font-size:.65em; color:var(--gray2); }

  /* ── feature row ── */
  .feat-row {
    display:grid; grid-template-columns:3px 1fr;
    gap:.8rem; align-items:center;
    background:var(--surface); border-radius:8px;
    padding:.5rem .8rem; margin-bottom:.4rem; overflow:hidden;
  }
  .feat-row .bar { width:3px; height:2rem; border-radius:2px; }
  .feat-title  { font-size:.75em; font-weight:700; color:var(--white); }
  .feat-desc   { font-size:.6em;  color:var(--gray2); }

  /* ── progress bar (eval) ── */
  .prog-row { display:flex; align-items:center; gap:.8rem; margin-bottom:.5rem; }
  .prog-label { font-size:.65em; min-width:7rem; color:var(--gray1); }
  .prog-track { flex:1; background:var(--surface2); border-radius:4px; height:.55rem; }
  .prog-fill  { height:100%; border-radius:4px; }
  .prog-count { font-size:.6em; color:var(--gray2); min-width:2rem; text-align:right; }

  /* ── cover ── */
  .cover-left-bar {
    position:absolute; left:0; top:0; bottom:0; width:6px;
    background:var(--cyan); border-radius:0;
  }
  .cover-stat-grid { display:grid; grid-template-columns:1fr; gap:.7rem; }

  /* ── slide numbering ── */
  .reveal .slide-number { background:transparent; color:var(--gray2);
    font-size:.6em; bottom:.8rem; right:1rem; }

  /* ── override reveal defaults ── */
  .reveal .slides section { padding: 1.8rem 2.5rem; box-sizing:border-box; height:100%; }
  .reveal p, .reveal li   { font-size:.8em; line-height:1.5; }
  .reveal ul { list-style:none; padding:0; margin:0; }
  .reveal ul li::before   { content:"· "; color:var(--cyan); font-weight:700; }

  /* ── tool pill ── */
  .pill {
    display:inline-block; background:var(--surface2);
    color:var(--cyan); border-radius:20px; padding:.2rem .8rem;
    font-size:.6em; font-weight:700; margin:.2rem;
  }
</style>
</head>
<body>
<div class="reveal">
<div class="slides">

<!-- ═══════════════════════════════════════════════════════════════
     SLIDE 01 — COVER
════════════════════════════════════════════════════════════════ -->
<section>
  <div class="cover-left-bar"></div>
  <div style="display:grid;grid-template-columns:1fr 220px;gap:2rem;height:100%;align-items:center;">
    <div>
      <div class="tag" style="margin-bottom:.6rem;">Churn Rate Analytics</div>
      <h1 style="font-size:2.4em;font-weight:900;line-height:1.1;color:var(--white);margin:0 0 .8rem;">
        One Metric.<br>One Definition.<br>One Dashboard.
      </h1>
      <div class="accent-bar" style="width:60px;margin:.8rem 0;"></div>
      <p style="font-size:.85em;color:var(--gray1);margin:.4rem 0;">
        Sostituisce 40 dashboard su 3 BI tool con una sola fonte di verità.
      </p>
      <p class="muted" style="margin-top:.6rem;">
        Definizione canonica v1.0 &nbsp;·&nbsp; Approvata 28 aprile 2026 &nbsp;·&nbsp; Scenario 04
      </p>
    </div>
    <div class="cover-stat-grid" style="margin-top:2rem;">
      <div class="card cyan">
        <div class="card-label">Dashboard eliminati</div>
        <div class="card-value" style="color:var(--cyan);">40</div>
      </div>
      <div class="card cyan">
        <div class="card-label">Stakeholder allineati</div>
        <div class="card-value" style="color:var(--cyan);">4</div>
      </div>
      <div class="card cyan">
        <div class="card-label">Fonte di verità</div>
        <div class="card-value" style="color:var(--cyan);">1</div>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════
     SLIDE 02 — IL PROBLEMA
════════════════════════════════════════════════════════════════ -->
<section>
  <div class="slide-header">
    <div class="tag">01 — Il Problema</div>
    <h2>Stessa domanda, 4 risposte diverse</h2>
    <div class="sub" style="font-style:italic;color:var(--cyan);">
      &laquo; Qual è il churn rate di Q2 2025? &raquo;
    </div>
  </div>

  <div class="cols4" style="margin-bottom:1rem;">
    <div class="card orange">
      <div class="card-label">VP Sales</div>
      <div class="card-value" style="color:var(--orange);">3.1%</div>
      <div class="card-sub">Logo churn<br>senza downgrade</div>
    </div>
    <div class="card purple">
      <div class="card-label">CS Head</div>
      <div class="card-value" style="color:var(--purple);">2.4%</div>
      <div class="card-sub">CS-accountable<br>escluse bankruptcies</div>
    </div>
    <div class="card red">
      <div class="card-label">Finance</div>
      <div class="card-value" style="color:var(--red);">5.8%</div>
      <div class="card-sub">nMRR grezzo<br>+ 340 duplicati CRM</div>
    </div>
    <div class="card green">
      <div class="card-label">Analyst</div>
      <div class="card-value" style="color:var(--green);">2.1%</div>
      <div class="card-sub">nMRR canonical D4<br>clean</div>
    </div>
  </div>

  <div class="warn-box">
    <strong>BUG CONFERMATO — Q2 2025</strong><br>
    Il 5.8% presentato al board era causato da 340 eventi duplicati (CRM retry storm).
    Valore corretto: <strong style="color:var(--green);">2.1%</strong>.
    Delta: <strong>+3.7pp falsi</strong>. Rettifica formale ancora da emettere.
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════
     SLIDE 03 — STAKEHOLDER REQUIREMENTS
════════════════════════════════════════════════════════════════ -->
<section>
  <div class="slide-header">
    <div class="tag">02 — Requisiti</div>
    <h2>Cosa voleva ogni stakeholder</h2>
    <div class="sub">12 punti di disaccordo → 1 definizione approvata da tutti · v1.0 · 28 apr 2026</div>
  </div>

  <div style="display:grid;gap:.5rem;">
    <div class="card" style="border-left:4px solid var(--orange);border-radius:8px;padding:.7rem 1rem;">
      <div style="display:grid;grid-template-columns:auto 1fr;gap:1rem;align-items:center;">
        <span class="badge" style="background:var(--orange);">VP Sales</span>
        <div>
          <div style="font-size:.8em;font-weight:700;color:var(--white);">Vista logocentrica</div>
          <div style="font-size:.65em;color:var(--gray1);">Churn = clienti persi. Toggle CS-accountable separato dal KPI finanziario.</div>
        </div>
      </div>
    </div>
    <div class="card" style="border-left:4px solid var(--purple);border-radius:8px;padding:.7rem 1rem;">
      <div style="display:grid;grid-template-columns:auto 1fr;gap:1rem;align-items:center;">
        <span class="badge" style="background:var(--purple);">CS Head</span>
        <div>
          <div style="font-size:.8em;font-weight:700;color:var(--white);">Esclusioni strutturali</div>
          <div style="font-size:.65em;color:var(--gray1);">Bankruptcies e M&A fuori dal KPI. Save reversal entro 30gg = churn annullato.</div>
        </div>
      </div>
    </div>
    <div class="card" style="border-left:4px solid var(--green);border-radius:8px;padding:.7rem 1rem;">
      <div style="display:grid;grid-template-columns:auto 1fr;gap:1rem;align-items:center;">
        <span class="badge" style="background:var(--green);">Finance</span>
        <div>
          <div style="font-size:.8em;font-weight:700;color:var(--white);">nMRR normalizzato</div>
          <div style="font-size:.65em;color:var(--gray1);">Annuali ÷ 12. Micro &lt; €200/m esclusi dall'headline. Versioning obbligatorio.</div>
        </div>
      </div>
    </div>
    <div class="card" style="border-left:4px solid var(--cyan);border-radius:8px;padding:.7rem 1rem;">
      <div style="display:grid;grid-template-columns:auto 1fr;gap:1rem;align-items:center;">
        <span class="badge" style="background:var(--cyan);">Analyst</span>
        <div>
          <div style="font-size:.8em;font-weight:700;color:var(--white);">Audit trail completo</div>
          <div style="font-size:.65em;color:var(--gray1);">Soglie numeriche esplicite, boundary cases, 18 unit test automatici, export CSV versionato.</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════
     SLIDE 04 — DEFINIZIONE v1.0
════════════════════════════════════════════════════════════════ -->
<section>
  <div class="slide-header">
    <div class="tag">03 — Definizione Canonica v1.0</div>
    <h2>Ogni soglia è numerica. Nessun termine vago.</h2>
    <div class="sub">Approvata da VP · CS · Finance · Analyst &nbsp;—&nbsp; 28 apr 2026</div>
  </div>

  <div class="cols2">
    <div>
      <div class="def-rule" style="border-color:var(--cyan);">
        <div class="rule-label" style="color:var(--cyan);">Formula headline</div>
        <div class="rule-text">nMRR Lost ÷ nMRR Active (inizio periodo) × 100</div>
      </div>
      <div class="def-rule" style="border-color:var(--cyan);">
        <div class="rule-label" style="color:var(--cyan);">Data canonica</div>
        <div class="rule-text">contract_end_date — non la data di cancellazione</div>
      </div>
      <div class="def-rule" style="border-color:var(--cyan);">
        <div class="rule-label" style="color:var(--cyan);">nMRR</div>
        <div class="rule-text">Annuali ÷ 12 — nessun picco artificiale a scadenza</div>
      </div>
      <div class="def-rule" style="border-color:var(--orange);">
        <div class="rule-label" style="color:var(--orange);">Micro-contratti</div>
        <div class="rule-text">&lt; €200/mese → esclusi dall'headline, tracciati separatamente</div>
      </div>
    </div>
    <div>
      <div class="def-rule" style="border-color:var(--orange);">
        <div class="rule-label" style="color:var(--orange);">Downgrade / Contraction</div>
        <div class="rule-text">Conta se delta ≥ €50 <strong>E</strong> ≥ 10% del nMRR precedente (doppia soglia)</div>
      </div>
      <div class="def-rule" style="border-color:var(--green);">
        <div class="rule-label" style="color:var(--green);">Save reversal</div>
        <div class="rule-text">Riattivazione entro 30 giorni da contract_end_date → churn annullato</div>
      </div>
      <div class="def-rule" style="border-color:var(--green);">
        <div class="rule-label" style="color:var(--green);">Grace post-rinnovo</div>
        <div class="rule-text">Cancellazione entro 14gg da rinnovo automatico → rimborso, non churn</div>
      </div>
      <div class="def-rule" style="border-color:var(--red);">
        <div class="rule-label" style="color:var(--red);">Pausa contrattuale</div>
        <div class="rule-text">At-risk ≤ 90 giorni · oltre = churn automatico (pause_expiry)</div>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════
     SLIDE 05 — ARCHITETTURA
════════════════════════════════════════════════════════════════ -->
<section>
  <div class="slide-header">
    <div class="tag">04 — Architettura</div>
    <h2>Tre layer indipendenti — testati, versionati, auditabili</h2>
  </div>

  <div class="cols3" style="margin-bottom:.8rem;">
    <div class="card orange" style="padding:1rem 1.2rem;">
      <div style="font-size:1em;font-weight:800;color:var(--orange);margin-bottom:.4rem;">DATA</div>
      <div class="muted" style="margin-bottom:.6rem;">5 CSV con noise iniettato</div>
      <ul style="font-size:.65em;color:var(--gray1);">
        <li>340 duplicati CRM</li>
        <li>Timezone mismatch UTC/CET</li>
        <li>15 segmenti errati</li>
        <li>12 end_date mancanti</li>
      </ul>
    </div>
    <div class="card cyan" style="padding:1rem 1.2rem;">
      <div style="font-size:1em;font-weight:800;color:var(--cyan);margin-bottom:.4rem;">ENGINE</div>
      <div class="muted" style="margin-bottom:.6rem;">FastAPI · Pydantic · Python</div>
      <ul style="font-size:.65em;color:var(--gray1);">
        <li>calculator.py — pure functions</li>
        <li>18 unit test · 100% pass</li>
        <li>definition_version su ogni risultato</li>
        <li>save reversals · micro filter</li>
      </ul>
    </div>
    <div class="card green" style="padding:1rem 1.2rem;">
      <div style="font-size:1em;font-weight:800;color:var(--green);margin-bottom:.4rem;">DASHBOARD</div>
      <div class="muted" style="margin-bottom:.6rem;">Streamlit · Plotly · Claude</div>
      <ul style="font-size:.65em;color:var(--gray1);">
        <li>KPI cards · trend · breakdown</li>
        <li>At-risk con risk score e CSM</li>
        <li>NL eval harness — 20/20 pass</li>
        <li>Export CSV versionato</li>
      </ul>
    </div>
  </div>

  <div class="cols4">
    <div class="card green"><div class="card-label">Unit test</div><div class="card-value" style="color:var(--green);font-size:1.6em;">18 / 18</div></div>
    <div class="card green"><div class="card-label">Golden questions</div><div class="card-value" style="color:var(--green);font-size:1.6em;">20 / 20</div></div>
    <div class="card green"><div class="card-label">Accuracy</div><div class="card-value" style="color:var(--green);font-size:1.6em;">100%</div></div>
    <div class="card green"><div class="card-label">False confidence</div><div class="card-value" style="color:var(--green);font-size:1.6em;">0%</div></div>
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════
     SLIDE 06 — RICONCILIAZIONE STORICA
════════════════════════════════════════════════════════════════ -->
<section>
  <div class="slide-header">
    <div class="tag">05 — Riconciliazione Storica</div>
    <h2>5 anni · 4 definizioni · 1 verità canonica</h2>
    <div class="sub">Ogni trimestre storico ricalcolato con D4 — le colonne precedenti non sono comparabili</div>
  </div>

  <div>
    <div class="timeline-row" style="border-color:var(--gray2);">
      <span class="badge" style="background:var(--gray2);">D0</span>
      <span style="font-size:.65em;color:var(--gray2);">2021 – Q1 2023</span>
      <span style="font-size:.75em;font-weight:700;color:var(--white);">Logo churn puro</span>
      <span style="font-size:.65em;color:var(--gray1);">Misura clienti persi. Non cattura la perdita di fatturato.</span>
    </div>
    <div class="timeline-row" style="border-color:var(--orange);">
      <span class="badge" style="background:var(--orange);">D1</span>
      <span style="font-size:.65em;color:var(--gray2);">Q2 – Q4 2023</span>
      <span style="font-size:.75em;font-weight:700;color:var(--white);">Logo + downgrade</span>
      <span style="font-size:.65em;color:var(--gray1);">Cambiato con il nuovo CFO. Include contrazioni ma senza soglia chiara.</span>
    </div>
    <div class="timeline-row" style="border-color:var(--cyan);">
      <span class="badge" style="background:var(--cyan);">D2</span>
      <span style="font-size:.65em;color:var(--gray2);">2024 – Q1 2025</span>
      <span style="font-size:.75em;font-weight:700;color:var(--white);">nMRR grezzo</span>
      <span style="font-size:.65em;color:var(--gray1);">Migliora la misura revenue ma manca la normalizzazione annuali ÷ 12.</span>
    </div>
    <div class="timeline-row" style="border-color:var(--red);background:#2a1015;">
      <span class="badge" style="background:var(--red);">D3</span>
      <span style="font-size:.65em;color:var(--gray2);">Q2 2025</span>
      <span style="font-size:.75em;font-weight:700;color:var(--red);">nMRR + duplicati CRM</span>
      <span style="font-size:.65em;color:var(--gray1);">BUG: 340 eventi duplicati portano il rate da 2.1% a 5.8% (+3.7pp falsi).</span>
    </div>
    <div class="timeline-row" style="border-color:var(--green);background:var(--surface2);">
      <span class="badge" style="background:var(--green);">D4</span>
      <span style="font-size:.65em;color:var(--gray2);">v1.0 canonica</span>
      <span style="font-size:.75em;font-weight:700;color:var(--green);">nMRR normalizzato · clean</span>
      <span style="font-size:.65em;color:var(--green);">Definizione approvata. Retroattiva su 5 anni. Questo è il numero corretto. ✓</span>
    </div>
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════
     SLIDE 07 — LA DASHBOARD
════════════════════════════════════════════════════════════════ -->
<section>
  <div class="slide-header">
    <div class="tag">06 — La Dashboard</div>
    <h2>Single source of truth — sostituisce 40 dashboard su 3 BI tool</h2>
  </div>

  <div class="cols6" style="margin-bottom:.8rem;">
    <div class="card cyan"><div class="card-label">nMRR Churn Rate</div><div class="card-value" style="color:var(--cyan);font-size:1.4em;">0.19%</div></div>
    <div class="card cyan"><div class="card-label">MRR Lost</div><div class="card-value" style="color:var(--cyan);font-size:1.4em;">€2.446</div></div>
    <div class="card gray"><div class="card-label">MRR Active</div><div class="card-value" style="color:var(--gray1);font-size:1.4em;">€1.3M</div></div>
    <div class="card cyan"><div class="card-label">Logo Churn</div><div class="card-value" style="color:var(--cyan);font-size:1.4em;">0.31%</div></div>
    <div class="card gray"><div class="card-label">CS Saves</div><div class="card-value" style="color:var(--gray2);font-size:1.4em;">0</div></div>
    <div class="card green"><div class="card-label">nMRR rischio 🔴</div><div class="card-value" style="color:var(--green);font-size:1.4em;">€0</div></div>
  </div>

  <div class="cols2">
    <div>
      <div class="feat-row"><div class="bar" style="background:var(--cyan);"></div><div><div class="feat-title">Vista Financial / Contractual</div><div class="feat-desc">Toggle nMRR ↔ logo churn</div></div></div>
      <div class="feat-row"><div class="bar" style="background:var(--orange);"></div><div><div class="feat-title">Window: Monthly · R30 · R90</div><div class="feat-desc">Flessibilità temporale on-the-fly</div></div></div>
      <div class="feat-row"><div class="bar" style="background:var(--purple);"></div><div><div class="feat-title">Filtro segmento</div><div class="feat-desc">Enterprise · Mid-market · SMB</div></div></div>
      <div class="feat-row"><div class="bar" style="background:var(--cyan);"></div><div><div class="feat-title">Toggle CS-accountable</div><div class="feat-desc">Separa KPI CS da quello finanziario</div></div></div>
    </div>
    <div>
      <div class="feat-row"><div class="bar" style="background:var(--green);"></div><div><div class="feat-title">Contratti a rischio</div><div class="feat-desc">Scadenza ≤90gg · risk score · CSM owner</div></div></div>
      <div class="feat-row"><div class="bar" style="background:var(--green);"></div><div><div class="feat-title">Export CSV versionato</div><div class="feat-desc">Tutti i periodi con definition_version</div></div></div>
      <div class="feat-row"><div class="bar" style="background:var(--orange);"></div><div><div class="feat-title">Glossario inline</div><div class="feat-desc">Definizione v1.0 sempre visibile</div></div></div>
      <div class="feat-row"><div class="bar" style="background:var(--purple);"></div><div><div class="feat-title">Storico 5 anni</div><div class="feat-desc">Confronto D0→D4 con annotazioni metodo</div></div></div>
    </div>
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════
     SLIDE 08 — NL EVAL HARNESS
════════════════════════════════════════════════════════════════ -->
<section>
  <div class="slide-header">
    <div class="tag">07 — NL Eval Harness</div>
    <h2>Claude risponde a domande sul churn con tool use</h2>
    <div class="sub">20 golden questions stratificate · prompt caching · agentic loop ≤ 5 turns</div>
  </div>

  <div class="cols2">
    <div>
      <div class="cols2" style="margin-bottom:.8rem;">
        <div class="card green"><div class="card-label">Accuracy</div><div class="card-value" style="color:var(--green);">100%</div><div class="card-sub">Target &gt; 80%</div></div>
        <div class="card green"><div class="card-label">Refusal accuracy</div><div class="card-value" style="color:var(--green);">100%</div><div class="card-sub">Target &gt; 90%</div></div>
        <div class="card green"><div class="card-label">False confidence</div><div class="card-value" style="color:var(--green);">0%</div><div class="card-sub">Target &lt; 5%</div></div>
        <div class="card green"><div class="card-label">Pass rate</div><div class="card-value" style="color:var(--green);">100%</div><div class="card-sub">Target &gt; 80%</div></div>
      </div>

      <div class="prog-row"><span class="prog-label">answerable (4)</span><div class="prog-track"><div class="prog-fill" style="width:80%;background:var(--cyan);"></div></div><span class="prog-count">4/4</span></div>
      <div class="prog-row"><span class="prog-label">comparison (3)</span><div class="prog-track"><div class="prog-fill" style="width:60%;background:var(--orange);"></div></div><span class="prog-count">3/3</span></div>
      <div class="prog-row"><span class="prog-label">definition (5)</span><div class="prog-track"><div class="prog-fill" style="width:100%;background:var(--purple);"></div></div><span class="prog-count">5/5</span></div>
      <div class="prog-row"><span class="prog-label">edge_case (3)</span><div class="prog-track"><div class="prog-fill" style="width:60%;background:var(--green);"></div></div><span class="prog-count">3/3</span></div>
      <div class="prog-row"><span class="prog-label">refusal (5)</span><div class="prog-track"><div class="prog-fill" style="width:100%;background:var(--red);"></div></div><span class="prog-count">5/5</span></div>
    </div>

    <div class="card" style="padding:1rem;">
      <div class="tag" style="margin-bottom:.6rem;">Tool use</div>
      <div style="margin-bottom:.8rem;">
        <span class="pill">get_metric</span>
        <span class="pill">compare_periods</span>
        <span class="pill">list_definitions</span>
        <span class="pill">explain_calculation</span>
      </div>
      <div class="accent-bar"></div>
      <div class="tag" style="margin-bottom:.4rem;">Regole critiche</div>
      <ul style="font-size:.65em;color:var(--gray1);">
        <li>Usare sempre un tool prima di rispondere a domande quantitative</li>
        <li>Includere definition_version in ogni risposta</li>
        <li>Rifiutare forecast, PII, dati fuori range 2021–2026</li>
        <li>False confidence = worst outcome</li>
      </ul>
    </div>
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════
     SLIDE 09 — NEXT STEPS
════════════════════════════════════════════════════════════════ -->
<section>
  <div class="slide-header">
    <div class="tag">08 — Next Steps</div>
    <h2>Dalla demo alla produzione</h2>
  </div>

  <div>
    <div class="row-card">
      <div class="num" style="background:var(--red);">1</div>
      <div>
        <div style="font-size:.8em;font-weight:700;color:var(--white);">Rettifica formale Q2 2025</div>
        <div style="font-size:.62em;color:var(--gray1);">Emettere la nota al board: churn reale 2.1%, non 5.8%. Aggiornare i verbali.</div>
      </div>
      <span class="timing" style="background:var(--red);">Immediato</span>
    </div>
    <div class="row-card">
      <div class="num" style="background:var(--orange);">2</div>
      <div>
        <div style="font-size:.8em;font-weight:700;color:var(--white);">Deploy su server interno</div>
        <div style="font-size:.62em;color:var(--gray1);">Docker container su infrastruttura aziendale. Accesso via browser, nessuna installazione.</div>
      </div>
      <span class="timing" style="background:var(--orange);">2 settimane</span>
    </div>
    <div class="row-card">
      <div class="num" style="background:var(--cyan);">3</div>
      <div>
        <div style="font-size:.8em;font-weight:700;color:var(--white);">Connessione DB di produzione</div>
        <div style="font-size:.62em;color:var(--gray1);">Sostituire i CSV con lettura dal warehouse. data_loader.py resta l'unico punto di accesso.</div>
      </div>
      <span class="timing" style="background:var(--cyan);">1 mese</span>
    </div>
    <div class="row-card">
      <div class="num" style="background:var(--green);">4</div>
      <div>
        <div style="font-size:.8em;font-weight:700;color:var(--white);">Deprecazione dashboard legacy</div>
        <div style="font-size:.62em;color:var(--gray1);">30 giorni di run parallelo, poi dismissione dei 40 dashboard. Comunicare il nuovo URL unico.</div>
      </div>
      <span class="timing" style="background:var(--green);">3 mesi</span>
    </div>
    <div class="row-card">
      <div class="num" style="background:var(--purple);">5</div>
      <div>
        <div style="font-size:.8em;font-weight:700;color:var(--white);">Definizione v1.1</div>
        <div style="font-size:.62em;color:var(--gray1);">Revisione annuale. Aggiornare DEFINITION_VERSION — footer e glossario si aggiornano in automatico.</div>
      </div>
      <span class="timing" style="background:var(--purple);">Apr 2027</span>
    </div>
  </div>
</section>

</div><!-- /slides -->
</div><!-- /reveal -->

<script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.1/reveal.min.js"></script>
<script>
Reveal.initialize({
  hash: true,
  slideNumber: 'c/t',
  transition: 'fade',
  transitionSpeed: 'fast',
  backgroundTransition: 'fade',
  controls: true,
  progress: true,
  center: false,
  width: 1280,
  height: 720,
  margin: 0,
  minScale: 0.2,
  maxScale: 2.0,
});
</script>
</body>
</html>
"""

def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "churn_rate_board_presentation.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(HTML)
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()
