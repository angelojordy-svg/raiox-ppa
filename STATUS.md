# Status — Raio-X Técnico do PPA 2026-2029

**Versão completa 2026 publicada; perfis multi-ano 2026-2029 preparados; aguardando validação final.**

- Escopo: diagnóstico por UG do PPA 2026-2029.
- Entradas: PPA 2026-2029; contas 2026 (`despesas_programas_2026_0101-1711.xlsx`).
- Saídas: `_dados/Saida/raiox/` com `index.html`, 35 páginas `ug_*.html`,
  `raiox_apoio_completo.xlsx`, 36 PDFs em `pdf/`, `manifest.json` e modelos CSV.
- Job: integrado ao pipeline diário do motor (`dashboard` → `raiox` → `publicar_raiox`), na tarefa existente `Orcamento Publico diario`; o raio-x detecta o ano mais recente (2026-2029).
- Testes: `scripts\verificar.bat` — 57 passed; `ruff check src tests` sem erros.
- Números: 87 programas, 247 indicadores, 306 ações, 35 UGs; 74 programas com execução;
  20 sem indicador; R$ 2.031.195.913,51 liquidados.
  UG 004: R$ 288.013.097,89; 9 programas; 16 indicadores; 34 ações; 3 compartilhados;
  6022 sem execução; 6020 sem indicador.
- Decisões confirmadas: visual claro institucional; HTML + PDF por UG + XLSX; programa PPA +
  ações LOA (projeto/atividade) + natureza; evidências independentes com placeholders;
  manter `laboratorio/raiox`.
- Pendências: validação final; resultados/evidências; validar mapa PPA↔UG dos 13 sem
  execução; confirmar dono/rateio dos compartilhados; obter empenhado/pago se necessário;
  definir meta física anual das ações com meta percentual.
- Publicação: código em https://github.com/angelojordy-svg/raiox-ppa e site em
  https://angelojordy-svg.github.io/raiox-ppa-site/.
- Multi-ano: perfis 2026-2029; 2027 usa `despesas_programas_2027_*.xlsx` e o bloco de meta 2027-2029 (sem meta anual explícita).
- Próximos passos: revisar as 35 UGs; carregar resultados/evidências; reprocessar.
