# AGENTS.md — Raio-X Técnico do PPA 2026-2029

**Dono:** equipe técnica de planejamento/controle (a definir).
**Produto:** diagnóstico completo por UG do PPA 2026-2029, interno e independente do RAM.
**Unidade:** UG (35), com subseções por UO quando a UG tiver mais de uma UO.
**Status:** versão completa de 2026 publicada; perfis multi-ano 2026-2029 preparados; aguardando validação final.

## Onde está o quê

- Definição: `docs/DEFINICAO_RAIOX.md`
- Código: `src/pmp_raiox/`
- PPA: `_dados/Saida/ppa_2026_2029.xlsx`
- Contas: `_dados/Saida/despesas_programas_2026_*.xlsx` (usar o mais recente)
- Resultados/evidências: `_dados/Saida/raiox/entrada/*.csv`
- Saídas: `_dados/Saida/raiox/` (`index.html`, `ug_*.html`, `raiox_apoio_completo.xlsx`, `pdf/`)
- Kernel compartilhado: `pmp_kernel` (`..\..\_kernel`), se necessário
- Gerar protótipo (UG 004): `scripts\gerar_prototipo.bat`
- Gerar as 35 UGs: `scripts\gerar_tudo.bat` (2026) ou `scripts\gerar_ano.bat 2027`
- Gerar PDFs: `scripts\gerar_pdf.bat` (2026) ou `scripts\gerar_pdf.bat 2027`
- Publicar site: `scripts\publicar_site.bat --ano 2027`
- Testes + lint: `scripts\verificar.bat`
- Abrir protótipo: `scripts\abrir_prototipo.bat`
- Código: https://github.com/angelojordy-svg/raiox-ppa
- Site: https://angelojordy-svg.github.io/raiox-ppa-site/
- Deploy do site: repo separado `_publico/raiox-ppa-site` (somente HTML/PDF gerados)

## Regras

1. Produto interno; **não é o RAM** e não importa `pmp_ram`.
2. Contexto importa `_kernel`; contexto nunca importa outro contexto.
3. Dados fora do repo; saídas em `PMP_DATA_ROOT/Saida/raiox/`.
4. Não pedir/aceitar senhas ou credenciais; usar dados locais/export.
5. Preservar os placeholders de resultados até a devolutiva das UGs.
6. Marcar como provisório o mapa PPA órgão→UG dos programas sem execução.
7. `scripts\verificar.bat` antes de considerar pronto.
8. Projeto no laboratório até ter produto recorrente; depois promover para `planejamento/raiox`.
