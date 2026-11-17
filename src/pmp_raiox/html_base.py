"""Base visual do raio-x: CSS, JS, componentes e formatadores."""

from __future__ import annotations

import html
from datetime import datetime

from . import __version__, config
from .perfil import PerfilAno
from .texto import (
    direcao_indicador,
    formatar_brl,
    formatar_brl_curto,
    formatar_numero,
    formatar_pct,
    norm,
)

CSS = r"""
:root {
  --bg: #eef2f5;
  --surface: #ffffff;
  --surface-2: #f7f9fb;
  --ink: #12263a;
  --muted: #5b6b7c;
  --line: #d7e0e8;
  --navy: #0f2a44;
  --navy-2: #173f63;
  --teal: #0f766e;
  --teal-soft: #e6f4f1;
  --amber: #b45309;
  --amber-soft: #fef3c7;
  --red: #b91c1c;
  --red-soft: #fee2e2;
  --green: #15803d;
  --green-soft: #dcfce7;
  --blue: #1d4ed8;
  --blue-soft: #dbeafe;
  --shadow: 0 10px 30px rgba(15, 42, 68, .08);
  --radius: 14px;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: "Segoe UI", "Inter", Arial, sans-serif;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.48;
  font-size: 15px;
}
a { color: var(--navy-2); }
a:hover { color: var(--teal); }
h1, h2, h3, h4 { line-height: 1.18; margin: 0; }
h1 { font-size: 30px; letter-spacing: -.02em; }
h2 { font-size: 24px; letter-spacing: -.01em; }
h3 { font-size: 18px; }
h4 { font-size: 14px; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); }
p { margin: 0 0 10px; }
ul { margin: 6px 0 10px 18px; padding: 0; }
li { margin: 3px 0; }
code { background: #eef2f6; padding: 1px 5px; border-radius: 5px; font-size: 12px; }
.num { font-variant-numeric: tabular-nums; }
.muted { color: var(--muted); }
.small { font-size: 12.5px; }
.tiny { font-size: 11.5px; }
.right { text-align: right; }
.center { text-align: center; }
.nowrap { white-space: nowrap; }
.wrap { max-width: 1260px; margin: 0 auto; padding: 0 24px; }
.hero {
  background:
    radial-gradient(900px 320px at 12% -10%, rgba(15, 118, 110, .55), transparent 60%),
    linear-gradient(135deg, #0b2239 0%, #123a5a 58%, #0f2a44 100%);
  color: #fff;
  padding: 34px 0 30px;
  border-bottom: 1px solid rgba(255,255,255,.15);
}
.hero-inner { display: flex; flex-wrap: wrap; gap: 22px; align-items: flex-end; justify-content: space-between; }
.hero-brand { display: flex; gap: 18px; align-items: center; min-width: 320px; flex: 1 1 620px; }
.brand-mark {
  width: 58px; height: 58px; border-radius: 16px;
  display: grid; place-items: center;
  background: linear-gradient(145deg, rgba(255,255,255,.22), rgba(255,255,255,.06));
  border: 1px solid rgba(255,255,255,.26);
  font-weight: 800; letter-spacing: .06em; font-size: 17px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.25);
}
.hero .eyebrow { color: #bfe3df; }
.hero h1 { margin: 4px 0 4px; }
.hero-sub { margin: 0; color: #d6e6ef; font-size: 15px; }
.hero-meta { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
.hero-meta .pill {
  border: 1px solid rgba(255,255,255,.22);
  background: rgba(255,255,255,.08);
  color: #eaf3f7;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 11.5px;
}
.hero-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.btn {
  display: inline-flex; align-items: center; gap: 7px;
  border: 1px solid rgba(255,255,255,.28);
  background: rgba(255,255,255,.10);
  color: #fff; text-decoration: none;
  padding: 9px 13px; border-radius: 10px;
  font: inherit; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn:hover { background: rgba(255,255,255,.18); color: #fff; }
.btn.primary { background: #fff; color: var(--navy); border-color: #fff; }
.btn.primary:hover { background: #eaf3f7; color: var(--navy); }
.btn.ghost { background: transparent; color: var(--ink); border-color: var(--line); }
.topbar {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
}
.topbar-inner { display: flex; align-items: center; gap: 14px; min-height: 50px; overflow-x: auto; }
.topbar a {
  color: var(--muted); text-decoration: none; font-size: 12.5px; font-weight: 600;
  padding: 6px 2px; white-space: nowrap;
}
.topbar a:hover { color: var(--navy); }
.topbar .sep { width: 1px; height: 18px; background: var(--line); flex: 0 0 auto; }
main.wrap { padding-top: 26px; padding-bottom: 40px; }
.eyebrow {
  display: block; text-transform: uppercase; letter-spacing: .14em;
  font-size: 10.5px; font-weight: 800; color: var(--teal);
  margin-bottom: 6px;
}
.section { margin: 30px 0 38px; scroll-margin-top: 76px; }
.section-head { margin-bottom: 16px; max-width: 920px; }
.section-head p { color: var(--muted); margin: 6px 0 0; }
.grid { display: grid; gap: 14px; }
.grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.kpi {
  background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 15px 16px; box-shadow: var(--shadow);
  border-top: 3px solid var(--navy-2);
  min-height: 104px;
}
.kpi.teal { border-top-color: var(--teal); }
.kpi.amber { border-top-color: var(--amber); }
.kpi.red { border-top-color: var(--red); }
.kpi.green { border-top-color: var(--green); }
.kpi-label { display: block; color: var(--muted); font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; }
.kpi-value { display: block; font-size: 25px; line-height: 1.12; margin-top: 6px; letter-spacing: -.02em; }
.kpi-hint { display: block; color: var(--muted); font-size: 11.5px; margin-top: 6px; }
.card {
  background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 16px; box-shadow: var(--shadow);
}
.card.flat { box-shadow: none; }
.card h3 { margin-bottom: 8px; }
.card h4 { margin: 14px 0 8px; }
.badge {
  display: inline-flex; align-items: center; gap: 5px;
  border-radius: 999px; padding: 3px 8px;
  font-size: 10.5px; font-weight: 800; letter-spacing: .02em;
  border: 1px solid transparent; white-space: nowrap;
}
.badge.ok { background: var(--green-soft); color: #14532d; border-color: #bbf7d0; }
.badge.warn { background: var(--amber-soft); color: #78350f; border-color: #fde68a; }
.badge.bad { background: var(--red-soft); color: #7f1d1d; border-color: #fecaca; }
.badge.info { background: var(--blue-soft); color: #1e3a8a; border-color: #bfdbfe; }
.badge.muted { background: #eef2f6; color: #475569; border-color: #e2e8f0; }
.badge.accent { background: var(--teal-soft); color: #115e59; border-color: #99f6e4; }
.badge.pending { background: #f1f5f9; color: #64748b; border-color: #e2e8f0; }
.pending { color: #6b7a89; font-style: italic; }
.note {
  background: var(--surface-2); border: 1px solid var(--line); border-left: 4px solid var(--teal);
  border-radius: 10px; padding: 12px 14px; color: #334155; font-size: 13px;
}
.note.warn { border-left-color: var(--amber); background: #fffbeb; }
.note.bad { border-left-color: var(--red); background: #fef2f2; }
.note.info { border-left-color: var(--blue); background: #eff6ff; }
.note strong { color: var(--ink); }
.alert {
  background: var(--surface); border: 1px solid var(--line); border-left: 5px solid var(--muted);
  border-radius: 10px; padding: 11px 13px; margin: 8px 0;
  break-inside: avoid;
}
.alert.alta { border-left-color: var(--red); background: #fffafa; }
.alert.media { border-left-color: var(--amber); background: #fffdf7; }
.alert.baixa { border-left-color: #64748b; }
.alert.info { border-left-color: var(--blue); background: #fbfdff; }
.alert-head { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 4px; }
.alert p { margin: 2px 0 0; font-size: 13px; }
.bars { display: grid; gap: 8px; }
.bar-row { display: grid; grid-template-columns: minmax(150px, 1.25fr) minmax(120px, 2fr) auto; gap: 10px; align-items: center; }
.bar-label { font-size: 12.5px; line-height: 1.2; overflow: visible; text-overflow: clip; white-space: normal; overflow-wrap: anywhere; }
.bar-track { height: 9px; background: #e8eef3; border-radius: 999px; overflow: hidden; }
.bar-fill { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--teal), #2dd4bf); }
.bar-fill.neg { background: linear-gradient(90deg, var(--red), #f87171); }
.bar-value { font-size: 12px; font-weight: 700; text-align: right; white-space: nowrap; }
.stack { display: flex; height: 18px; border-radius: 999px; overflow: hidden; background: #e8eef3; border: 1px solid var(--line); }
.stack span { display: block; height: 100%; }
.stack .s1 { background: #0f766e; }
.stack .s2 { background: #f59e0b; }
.stack .s3 { background: #64748b; }
.stack .s4 { background: #b91c1c; }
.legend { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 8px; font-size: 11.5px; color: var(--muted); }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 5px; vertical-align: -1px; }
.table-block { margin: 12px 0 18px; }
.table-tools { display: flex; gap: 8px; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-bottom: 8px; }
.table-tools input {
  width: min(360px, 100%); border: 1px solid var(--line); border-radius: 9px;
  padding: 8px 10px; font: inherit; font-size: 13px; background: #fff;
}
.table-wrap { width: 100%; overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: #fff; }
table.table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
table.table th {
  text-align: left; background: #f1f5f9; color: #334155; font-size: 10.5px;
  text-transform: uppercase; letter-spacing: .06em; padding: 8px 9px;
  border-bottom: 1px solid var(--line); white-space: nowrap;
}
table.table th[data-sort] { cursor: pointer; user-select: none; }
table.table th[data-sort]:hover { color: var(--teal); }
table.table td { padding: 8px 9px; border-bottom: 1px solid #edf2f6; vertical-align: top; }
table.table tbody tr:last-child td { border-bottom: 0; }
table.table tbody tr:hover { background: #fbfdff; }
table.table td.right, table.table th.right { text-align: right; }
table.table td.center, table.table th.center { text-align: center; }
table.table td.nowrap { white-space: nowrap; }
.cell-title { font-weight: 700; color: var(--ink); }
.cell-note { display: block; color: var(--muted); font-size: 11px; margin-top: 3px; }
.detalhe { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; margin: 12px 0; }
.detalhe > summary { cursor: pointer; padding: 10px 12px; font-weight: 700; color: var(--navy); list-style: none; }
.detalhe > summary::-webkit-details-marker { display: none; }
.detalhe[open] > summary { border-bottom: 1px solid var(--line); }
.detalhe .table-block { margin: 0; padding: 0 12px 12px; }
.empty {
  border: 1px dashed var(--line); border-radius: 10px; padding: 14px;
  color: var(--muted); background: var(--surface-2); font-size: 13px;
}
.programa {
  background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius);
  box-shadow: var(--shadow); margin: 12px 0 18px; overflow: hidden;
  scroll-margin-top: 76px;
}
.programa > summary {
  list-style: none; cursor: pointer; padding: 15px 16px;
  display: grid; grid-template-columns: auto minmax(0, 1fr) auto auto; gap: 12px; align-items: center;
  background: linear-gradient(180deg, #fff, #fbfdff);
  border-bottom: 1px solid transparent;
}
.programa[open] > summary { border-bottom-color: var(--line); }
.programa > summary::-webkit-details-marker { display: none; }
.prog-id {
  font-weight: 800; font-size: 13px; color: #fff; background: var(--navy-2);
  padding: 6px 8px; border-radius: 8px; font-variant-numeric: tabular-nums;
}
.prog-heading h3 { font-size: 17px; margin: 0 0 4px; }
.prog-badges { display: flex; gap: 6px; flex-wrap: wrap; }
.prog-value { text-align: right; min-width: 126px; }
.prog-value strong { display: block; font-size: 17px; }
.prog-value span { color: var(--muted); font-size: 11px; }
.prog-toggle { color: var(--muted); font-size: 20px; width: 26px; text-align: center; transition: transform .15s ease; }
.programa[open] .prog-toggle { transform: rotate(180deg); }
.prog-body { padding: 16px; }
.ficha { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin-bottom: 12px; }
.ficha div { background: var(--surface-2); border: 1px solid var(--line); border-radius: 9px; padding: 9px 10px; }
.ficha span { display: block; color: var(--muted); font-size: 10.5px; text-transform: uppercase; letter-spacing: .06em; }
.ficha strong { display: block; font-size: 12.5px; margin-top: 3px; }
.objetivo { background: var(--surface-2); border: 1px solid var(--line); border-radius: 9px; padding: 11px 12px; margin: 10px 0 12px; font-size: 13px; }
.chips { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0 4px; }
.panel { background: var(--surface-2); border: 1px solid var(--line); border-radius: 10px; padding: 12px; margin-top: 12px; }
.panel h4 { margin-top: 0; }
.mini-kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin: 10px 0; }
.mini { background: #fff; border: 1px solid var(--line); border-radius: 9px; padding: 9px 10px; }
.mini span { display: block; color: var(--muted); font-size: 10.5px; text-transform: uppercase; letter-spacing: .05em; }
.mini strong { display: block; font-size: 15px; margin-top: 3px; }
.exec-compact { display: flex; flex-wrap: wrap; gap: 6px 18px; align-items: center; background: var(--surface-2); border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; margin-top: 12px; font-size: 12.5px; }
.exec-compact strong { color: var(--ink); }
.exec-compact a { margin-left: auto; font-weight: 700; }
table.table tr.group-row td { background: #e8eef3; font-weight: 800; color: var(--navy); border-top: 1px solid var(--line); }
.two-col { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.ug-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
.ug-card {
  display: flex; flex-direction: column; gap: 7px;
  background: var(--surface); border: 1px solid var(--line); border-radius: 12px;
  padding: 12px; color: var(--ink); text-decoration: none; min-height: 150px;
  box-shadow: 0 4px 14px rgba(15,42,68,.04);
}
.ug-card.active { border-color: #5eead4; box-shadow: 0 0 0 1px #5eead4, 0 8px 22px rgba(15,118,110,.12); }
.ug-card.disabled { opacity: .78; }
.ug-card:hover { border-color: var(--teal); }
.ug-card .ug-code { font-size: 11px; font-weight: 800; color: var(--teal); letter-spacing: .08em; }
.ug-card .ug-name { font-weight: 700; font-size: 13px; line-height: 1.25; min-height: 34px; }
.ug-card .ug-value { font-size: 16px; font-weight: 800; }
.ug-card .ug-meta { color: var(--muted); font-size: 11px; }
.ug-card .ug-bar { height: 6px; background: #e8eef3; border-radius: 999px; overflow: hidden; margin-top: auto; }
.ug-card .ug-bar span { display: block; height: 100%; background: var(--teal); }
.ug-card .ug-foot { display: flex; justify-content: space-between; gap: 6px; align-items: center; font-size: 10.5px; color: var(--muted); }
.insights { display: grid; gap: 8px; }
.insight { display: flex; gap: 9px; align-items: flex-start; background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; }
.insight .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--teal); margin-top: 6px; flex: 0 0 auto; }
.toc { display: flex; gap: 6px; flex-wrap: wrap; }
.toc a { background: #fff; border: 1px solid var(--line); border-radius: 999px; padding: 5px 9px; font-size: 11.5px; text-decoration: none; color: var(--muted); }
.toc a:hover { color: var(--teal); border-color: var(--teal); }
.filters { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin: 10px 0 14px; }
.filters input { border: 1px solid var(--line); border-radius: 9px; padding: 9px 11px; font: inherit; font-size: 13px; min-width: 280px; }
.chip-btn { border: 1px solid var(--line); background: #fff; color: var(--muted); border-radius: 999px; padding: 7px 11px; font: inherit; font-size: 12px; font-weight: 700; cursor: pointer; }
.chip-btn.ativo, .chip-btn:hover { color: var(--teal); border-color: var(--teal); background: var(--teal-soft); }
.footer { border-top: 1px solid var(--line); padding: 22px 0 40px; color: var(--muted); font-size: 11.5px; }
.footer strong { color: var(--ink); }
.print-only { display: none; }
@media (max-width: 1040px) {
  .kpi-grid, .ug-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .grid-4, .ficha, .mini-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .grid-3 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 680px) {
  .wrap { padding: 0 14px; }
  h1 { font-size: 24px; }
  h2 { font-size: 20px; }
  .kpi-grid, .ug-grid, .grid-2, .grid-3, .grid-4, .ficha, .mini-kpis, .two-col { grid-template-columns: 1fr; }
  .programa > summary { grid-template-columns: auto minmax(0, 1fr) auto; }
  .prog-value { display: none; }
  .bar-row { grid-template-columns: 1fr; gap: 3px; }
  .bar-value { text-align: left; }
  .filters input { min-width: 100%; }
}
@media print {
  @page { size: A4; margin: 13mm 12mm 14mm; }
  html, body { background: #fff !important; color: #111; font-size: 9.5pt; }
  .no-print, .topbar, .hero-actions, .table-tools, .btn, .filters { display: none !important; }
  .wrap { max-width: none; padding: 0; }
  .hero {
    background: #fff !important; color: #111 !important;
    border-bottom: 2px solid #0f2a44; padding: 0 0 10px;
  }
  .hero .eyebrow { color: #0f766e; }
  .hero-sub { color: #333; }
  .hero-meta .pill { border: 1px solid #aaa; background: #fff; color: #111; }
  .brand-mark { background: #0f2a44; color: #fff; border: 0; }
  .section { margin: 12pt 0; }
  .section-head { margin-bottom: 8pt; }
  .section-head h2 { font-size: 14pt; }
  .kpi-grid { grid-template-columns: repeat(4, 1fr); gap: 6pt; }
  .kpi { box-shadow: none; border: 1px solid #bbb; break-inside: avoid; min-height: 0; }
  .kpi-value { font-size: 16pt; }
  .card, .alert, .note, .insight { box-shadow: none; break-inside: avoid; }
  .programa { border: 1px solid #bbb; box-shadow: none; break-inside: auto; }
  .programa > summary { break-after: avoid; }
  .section-head { break-after: avoid; }
  .programa > summary { cursor: default; }
  .programa .prog-body { display: block !important; }
  details > * { display: block !important; }
  .table-wrap { overflow: visible; border-color: #bbb; }
  table.table { font-size: 7.8pt; }
  table.table th { font-size: 6.8pt; padding: 4pt 5pt; }
  table.table td { padding: 4pt 5pt; }
  thead { display: table-header-group; }
  tr { break-inside: avoid; }
  .bar-fill, .stack span, .badge, .ug-bar span { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  a { color: #111; text-decoration: none; }
  .print-only { display: block; }
  .pagebreak { break-before: page; }
  #execucao, #analise, #evidencias, #alertas { break-before: page; }
  .hide-print { display: none !important; }
}
"""

JS = r"""
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var normalizar = function (s) {
    return (s || '').toString().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  };
  $$('[data-print]').forEach(function (b) {
    b.addEventListener('click', function () { window.print(); });
  });
  var expandir = $('[data-expandir]');
  if (expandir) {
    expandir.addEventListener('click', function () {
      var abrir = expandir.getAttribute('data-expandir') === 'abrir';
      $$('details.programa').forEach(function (d) { d.open = abrir; });
      expandir.setAttribute('data-expandir', abrir ? 'recolher' : 'abrir');
      expandir.textContent = abrir ? 'Recolher programas' : 'Expandir programas';
    });
  }
  var busca = $('#busca-programa');
  var filtros = $$('[data-filtro-programa]');
  function aplicarFiltros() {
    var termo = normalizar(busca ? busca.value : '');
    var ativo = 'todos';
    filtros.forEach(function (b) { if (b.classList.contains('ativo')) ativo = b.getAttribute('data-filtro-programa'); });
    var visiveis = 0;
    $$('details.programa').forEach(function (d) {
      var alvo = normalizar((d.getAttribute('data-busca') || '') + ' ' + d.textContent);
      var status = (d.getAttribute('data-status') || '').split(' ');
      var okTermo = !termo || alvo.indexOf(termo) >= 0;
      var okStatus = ativo === 'todos' || status.indexOf(ativo) >= 0;
      var mostrar = okTermo && okStatus;
      d.hidden = !mostrar;
      if (mostrar) visiveis += 1;
      if (mostrar && termo.length >= 2) d.open = true;
    });
    var contador = $('#contador-programas');
    if (contador) contador.textContent = visiveis + ' programa(s)';
  }
  if (busca) busca.addEventListener('input', aplicarFiltros);
  filtros.forEach(function (b) {
    b.addEventListener('click', function () {
      filtros.forEach(function (x) { x.classList.remove('ativo'); });
      b.classList.add('ativo');
      aplicarFiltros();
    });
  });
  aplicarFiltros();
  $$('input[data-busca-tabela]').forEach(function (input) {
    var tabela = document.getElementById(input.getAttribute('data-busca-tabela'));
    if (!tabela) return;
    input.addEventListener('input', function () {
      var termo = normalizar(input.value);
      $$('tbody tr', tabela).forEach(function (tr) {
        tr.hidden = !!termo && normalizar(tr.textContent).indexOf(termo) < 0;
      });
    });
  });
  $$('table[data-sortable] th[data-sort]').forEach(function (th) {
    th.addEventListener('click', function () {
      var tabela = th.closest('table');
      var tbody = tabela.tBodies[0];
      var idx = Array.prototype.indexOf.call(th.parentNode.children, th);
      var dir = th.getAttribute('data-dir') === 'asc' ? -1 : 1;
      th.setAttribute('data-dir', dir === 1 ? 'asc' : 'desc');
      var linhas = Array.prototype.slice.call(tbody.rows);
      linhas.sort(function (a, b) {
        var ca = a.cells[idx], cb = b.cells[idx];
        var va = ca ? (ca.getAttribute('data-value') || ca.textContent.trim()) : '';
        var vb = cb ? (cb.getAttribute('data-value') || cb.textContent.trim()) : '';
        var na = parseFloat(String(va).replace(/\./g, '').replace(',', '.'));
        var nb = parseFloat(String(vb).replace(/\./g, '').replace(',', '.'));
        if (!isNaN(na) && !isNaN(nb)) return (na - nb) * dir;
        return String(va).localeCompare(String(vb), 'pt-BR') * dir;
      });
      linhas.forEach(function (l) { tbody.appendChild(l); });
    });
  });
  function abrirHash() {
    if (!location.hash) return;
    var el = document.querySelector(location.hash);
    if (el && el.tagName === 'DETAILS') el.open = true;
  }
  window.addEventListener('hashchange', abrirHash);
  abrirHash();
  window.addEventListener('beforeprint', function () {
    $$('details').forEach(function (d) { d.open = true; });
  });
})();
"""


def e(valor: object) -> str:
    return html.escape("" if valor is None else str(valor), quote=True)


def brl(valor: float | None) -> str:
    return formatar_brl(valor)


def brl_curto(valor: float | None) -> str:
    return formatar_brl_curto(valor)


def pct(valor: float | None) -> str:
    return formatar_pct(valor)


def num(valor: float | None) -> str:
    return formatar_numero(valor)


def badge(texto: str, tom: str = "muted") -> str:
    return f'<span class="badge {tom}">{e(texto)}</span>'


def status_badge(status: str) -> str:
    s = norm(status)
    if s in {"CONCLUIDA", "ATINGIDO", "FAVORAVEL", "COM EXECUCAO", "OK"}:
        tom = "ok"
    elif s in {"EM ANDAMENTO", "ESTAVEL", "COMPARTILHADO", "EM EXECUCAO"}:
        tom = "info"
    elif s in {"NAO INICIADA", "NAO ATINGIDO", "DESFAVORAVEL", "ATENCAO", "SEM INDICADOR"}:
        tom = "warn"
    elif s in {"SEM EXECUCAO", "EXECUCAO ANULADA"}:
        tom = "bad"
    elif s == "NAO SE APLICA":
        tom = "muted"
    else:
        tom = "pending"
    return badge(status or "Pendente", tom)


def meta_badge(meta, perfil: PerfilAno) -> str:
    if meta.tipo == "percentual_plano":
        total = ""
        if meta.total_4anos is not None:
            total = f'<span class="cell-note">total 4 anos: {num(meta.total_4anos)}%</span>'
        rotulo = "bloco" if perfil.meta_ano_tipo == "bloco" else "plano"
        return badge(f"{num(meta.valor)}% do {rotulo}", "info") + total
    if meta.tipo == "quantidade":
        total = ""
        if meta.total_4anos is not None:
            unidade = f" {meta.total_unidade}" if meta.total_unidade else ""
            total = f'<span class="cell-note">total 4 anos: {num(meta.total_4anos)}{e(unidade)}</span>'
        return badge(meta.texto or "meta física", "ok") + total
    if meta.tipo == "nao_definida":
        return badge("não definida", "warn")
    return badge("texto", "muted")


def direcao(ref_atual: str, ref_2029: str) -> str:
    valor = direcao_indicador(ref_atual, ref_2029)
    if valor == "aumentar":
        return "↑ Aumentar"
    if valor == "reduzir":
        return "↓ Reduzir"
    if valor == "manter":
        return "→ Manter"
    return "Qualitativo"


def fonte_label(codigo: str) -> str:
    nome = config.FONTES.get(codigo)
    return f"{codigo} — {nome}" if nome else codigo


def natureza_descricao(codigo: str) -> str:
    nome = config.NATUREZAS.get(codigo)
    if nome:
        return nome
    return config.CATEGORIAS_NATUREZA.get(".".join(codigo.split(".")[:2]), "")


def natureza_label(codigo: str) -> str:
    nome = config.NATUREZAS.get(codigo)
    categoria = config.CATEGORIAS_NATUREZA.get(".".join(codigo.split(".")[:2]), "")
    if nome:
        return f"{codigo} — {nome}"
    if categoria:
        return f"{codigo} — {categoria}"
    return codigo


def td(conteudo: str, align: str = "left", valor: object | None = None, classe: str = "") -> str:
    classes = " ".join(c for c in (align, classe) if c)
    attr_valor = f' data-value="{e(valor)}"' if valor is not None else ""
    return f'<td class="{classes}"{attr_valor}>{conteudo}</td>'


def tabela(
    cabecalhos: list[tuple[str, str]],
    linhas: list[str],
    *,
    id_tabela: str = "",
    classes: str = "",
    ordenavel: bool = True,
    busca: bool = True,
    placeholder: str = "Buscar na tabela...",
) -> str:
    id_attr = f' id="{e(id_tabela)}"' if id_tabela else ""
    sort_attr = " data-sortable" if ordenavel else ""
    cab = "".join(
        f'<th class="{e(align)}" data-sort>{e(label)}</th>'
        if ordenavel
        else f'<th class="{e(align)}">{e(label)}</th>'
        for label, align in cabecalhos
    )
    if not linhas:
        linhas = [f'<tr><td colspan="{len(cabecalhos)}" class="center muted">Sem registros.</td></tr>']
    ferramenta = ""
    if busca and id_tabela:
        ferramenta = (
            '<div class="table-tools no-print">'
            f'<input type="search" data-busca-tabela="{e(id_tabela)}" '
            f'placeholder="{e(placeholder)}" aria-label="{e(placeholder)}">'
            "</div>"
        )
    return (
        f'<div class="table-block">{ferramenta}'
        f'<div class="table-wrap"><table class="table {e(classes)}"{id_attr}{sort_attr}>'
        f"<thead><tr>{cab}</tr></thead><tbody>{''.join(linhas)}</tbody></table></div></div>"
    )


def barras(
    itens: list[tuple[str, float]],
    *,
    formato: str = "brl",
    limite: int = 10,
    vazio: str = "Sem dados.",
) -> str:
    itens = [(label, valor) for label, valor in itens if valor]
    itens = sorted(itens, key=lambda kv: (-abs(kv[1]), kv[0]))[:limite]
    if not itens:
        return f'<div class="empty">{e(vazio)}</div>'
    maximo = max(abs(valor) for _, valor in itens) or 1.0
    partes = []
    for label, valor in itens:
        largura = max(0.0, min(100.0, abs(valor) / maximo * 100))
        if formato == "pct":
            valor_txt = pct(valor)
        elif formato == "num":
            valor_txt = num(valor)
        else:
            valor_txt = brl_curto(valor)
        classe = " neg" if valor < 0 else ""
        partes.append(
            '<div class="bar-row">'
            f'<div class="bar-label" title="{e(label)}">{e(label)}</div>'
            '<div class="bar-track">'
            f'<span class="bar-fill{classe}" style="width:{largura:.2f}%"></span>'
            "</div>"
            f'<div class="bar-value num">{e(valor_txt)}</div>'
            "</div>"
        )
    return '<div class="bars">' + "".join(partes) + "</div>"


def kpi(label: str, valor: str, dica: str = "", tom: str = "") -> str:
    classe = f"kpi {tom}".strip()
    return (
        f'<div class="{classe}">'
        f'<span class="kpi-label">{e(label)}</span>'
        f'<strong class="kpi-value num">{valor}</strong>'
        f'<span class="kpi-hint">{e(dica)}</span>'
        "</div>"
    )


def sec(id_secao: str, eyebrow: str, titulo: str, conteudo: str, subtitulo: str = "") -> str:
    sub = f"<p>{subtitulo}</p>" if subtitulo else ""
    return (
        f'<section id="{e(id_secao)}" class="section">'
        '<div class="section-head">'
        f'<span class="eyebrow">{e(eyebrow)}</span>'
        f"<h2>{e(titulo)}</h2>{sub}</div>"
        f"{conteudo}</section>"
    )


def hero(
    titulo: str,
    subtitulo: str,
    marca: str,
    *,
    arquivo_contas: str,
    gerado_em: datetime,
    perfil: PerfilAno,
    acoes: str = "",
    link_indice: bool = True,
) -> str:
    link = '<a class="btn" href="index.html">Índice</a>' if link_indice else ""
    return (
        '<header class="hero"><div class="wrap hero-inner">'
        '<div class="hero-brand">'
        f'<div class="brand-mark">{e(marca)}</div>'
        "<div>"
        '<span class="eyebrow">Prefeitura Municipal de Parauapebas · Planejamento e Controle</span>'
        f"<h1>{e(titulo)}</h1>"
        f'<p class="hero-sub">{e(subtitulo)}</p>'
        '<div class="hero-meta">'
        f'<span class="pill">{e(perfil.titulo_ppa)}</span>'
        f'<span class="pill">Contas: {e(arquivo_contas)}</span>'
        f'<span class="pill">Gerado em {gerado_em:%d/%m/%Y %H:%M}</span>'
        f'<span class="pill">versão {e(__version__)}</span>'
        "</div></div></div>"
        '<div class="hero-actions no-print">'
        f"{link}"
        '<button class="btn primary" type="button" data-print>Imprimir / PDF</button>'
        f"{acoes}</div></div></header>"
    )


def topbar(links: list[tuple[str, str]]) -> str:
    itens = '<span class="sep"></span>'.join(
        f'<a href="#{e(ancora)}">{e(label)}</a>' for ancora, label in links
    )
    return f'<nav class="topbar no-print"><div class="wrap topbar-inner">{itens}</div></nav>'


def layout(
    titulo: str,
    hero_html: str,
    topbar_html: str,
    corpo: str,
    perfil: PerfilAno,
) -> str:
    return (
        "<!DOCTYPE html>"
        '<html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{e(titulo)}</title>"
        f"<style>{CSS}</style></head><body>"
        f'{hero_html}{topbar_html}<main class="wrap">{corpo}</main>'
        '<footer class="footer"><div class="wrap">'
        f"<strong>{e(perfil.titulo)}</strong> · produto interno da equipe técnica. "
        "Não substitui o RAM nem o resumo executivo de contas. "
        f"Gerado por pmp_raiox {e(__version__)}."
        "</div></footer>"
        f"<script>{JS}</script></body></html>"
    )
