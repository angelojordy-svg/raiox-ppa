# Raio-X Técnico do PPA 2026-2029

Diagnóstico interno por Unidade Gestora (UG), independente do RAM. Reúne programas,
indicadores, ações, execução orçamentária por ação LOA (projeto/atividade) e natureza,
resultados/evidências, análise e alertas.

**Versão completa:** 35 UGs geradas em 2026-11-17.

## Comandos

```bat
scripts\gerar_prototipo.bat
scripts\gerar_tudo.bat
scripts\gerar_pdf.bat
scripts\verificar.bat
scripts\abrir_prototipo.bat
```

`gerar_prototipo.bat` regenera apenas a UG 004 e um índice de prévia. Para a versão
completa, use `gerar_tudo.bat`.

## Saídas

Em `_dados/Saida/raiox/`:

- `index.html` — índice, ranking, mapa das 35 UGs e visões transversais.
- `ug_*.html` — uma página por UG, com o detalhamento do programa → ação LOA
  (projeto/atividade) → natureza/elemento.
- `pdf/` — 35 PDFs por UG + PDF do índice.
- `raiox_apoio_completo.xlsx` — planilha de apoio completa.
- `manifest.json` — fontes, escopo, contagens, PDFs e saídas.
- `entrada/` — modelos CSV de resultados e evidências.

## Princípios

- Dados reais de PPA e contas; resultados como placeholders explícitos.
- Execução = liquidação líquida (não há empenhado/pago no Consolidado).
- UO identificada pelo nome normalizado (o código do Consolidado não é único).
- Meta de ação classificada: percentual do plano, quantidade, não definida ou texto.
- Programa compartilhado mostra a parte de cada UG e o total do programa.
- O detalhe LOA fica no cartão do programa, ao lado das ações do PPA.

Definição completa: `docs/DEFINICAO_RAIOX.md`.
