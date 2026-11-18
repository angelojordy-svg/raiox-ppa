# Raio-X Técnico do PPA 2026-2029

Diagnóstico interno por Unidade Gestora (UG), independente do RAM. Reúne programas,
indicadores, ações, execução orçamentária por ação LOA (projeto/atividade) e natureza,
resultados/evidências, análise e alertas.

**Versão completa:** 35 UGs geradas em 2026-11-17.

## Comandos

```bat
scripts\gerar_prototipo.bat
scripts\gerar_tudo.bat
scripts\gerar_ano.bat 2027
scripts\job_diario.bat
scripts\job_publicar.bat
scripts\gerar_pdf.bat
scripts\gerar_pdf.bat 2027
scripts\publicar_site.bat --ano 2027
scripts\verificar.bat
scripts\abrir_prototipo.bat
```

`gerar_prototipo.bat` regenera apenas a UG 004 e um índice de prévia. Para a versão
completa, use `gerar_tudo.bat`. O `gerar_ano.bat <ano>` usa o perfil do ano (2026 a 2029).

`job_diario.bat` e `job_publicar.bat` são os passos automáticos chamados pelo pipeline
diário do motor, depois do dashboard (que gera `despesas_programas`). Eles detectam o ano
mais recente com arquivo de contas (2026-2029).

**Multi-ano:** 2026 fica na raiz de `_dados/Saida/raiox/`; 2027, 2028 e 2029 ficam em
subpastas do ano. O PPA 2026-2029 é o mesmo; em 2027-2029 o PPA só traz o bloco
2027-2029, então a meta anual deve ser informada na coleta (`meta_anual`).

## Saídas

Em `_dados/Saida/raiox/`:

- `index.html` — índice, ranking, mapa das 35 UGs e visões transversais.
- `ug_*.html` — uma página por UG, com o detalhamento do programa → ação LOA
  (projeto/atividade) → natureza/elemento.
- `pdf/` — 35 PDFs por UG + PDF do índice.
- `raiox_apoio_completo.xlsx` — planilha de apoio completa.
- `manifest.json` — fontes, escopo, contagens, PDFs e saídas.
- `entrada/` — modelos CSV de resultados, evidências e `crosswalk_loa.csv`.

## Princípios

- Dados reais de PPA e contas; resultados como placeholders explícitos.
- Execução = liquidação líquida (não há empenhado/pago no Consolidado).
- UO identificada pelo nome normalizado (o código do Consolidado não é único).
- Meta de ação classificada: percentual do plano, quantidade, não definida ou texto.
- Programa compartilhado mostra a parte de cada UG e o total do programa.
- O detalhe LOA fica no cartão do programa, ao lado das ações do PPA.
- O código P/A da LOA é sugerido por similaridade de nomes e pode ser corrigido em
  `crosswalk_loa.csv` (vínculo provisório; validar).

## Repositórios e publicação

- Código: https://github.com/angelojordy-svg/raiox-ppa
- Site: https://angelojordy-svg.github.io/raiox-ppa-site/
- Deploy: repo separado `raiox-ppa-site`, com apenas HTML/PDF gerados.

Definição completa: `docs/DEFINICAO_RAIOX.md`.
