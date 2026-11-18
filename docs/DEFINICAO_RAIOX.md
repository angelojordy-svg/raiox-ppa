# Raio-X Técnico do PPA 2026-2029 — Definição do Projeto

**Status:** definição + versão completa de 2026 + perfis multi-ano 2026-2029; aguardando validação final
**Data:** 2026-11-18
**Projeto:** `laboratorio/raiox` (promover para `planejamento/raiox` quando houver recorrência)
**Produto:** diagnóstico técnico interno por Unidade Gestora (UG), independente do RAM
**Público:** equipe técnica de planejamento/controle, analistas de eixo e alta gestão
**Fonte de contas da versão completa:** `_dados/Saida/despesas_programas_2026_0101-1811.xlsx`

---

## 1. Contexto e problema

O PPA 2026-2029 está no primeiro ano de execução. O resumo executivo de contas entrega a
visão agregada para a alta gestão; o RAM é o relatório oficial/anual da Câmara. Falta um
produto **técnico, completo e interno**, que permita à equipe de planejamento/controle
olhar cada UG e responder, com evidência:

- quais programas, indicadores e ações do PPA estão sob a UG;
- o que foi executado fisicamente e o que ainda depende de devolutiva;
- quanto foi liquidado, por programa, UO, natureza, fonte e mês;
- quais programas são compartilhados, estão sem execução ou sem indicador;
- quais metas, resultados, análises e evidências precisam ser cobrados.

O raio-x não substitui o RAM nem o resumo executivo. Ele é a **versão técnica completa** que
alimenta a validação, a cobrança e a consolidação dos dois.

## 2. Objetivo

Produzir um diagnóstico por UG, com dados reais de PPA e contas, que:

1. organize todos os programas, indicadores e ações da UG;
2. mostre a execução orçamentária de 2026 como contexto;
3. explicite lacunas, exceções e riscos de qualidade de dados;
4. receba resultados, análises e evidências das UGs;
5. gere HTML interativo, prévia de impressão/PDF por UG e planilha de apoio.

O protótipo da **UG 004 — Fundo Municipal de Educação** foi validado e a versão completa das
35 UGs foi gerada em 2026-11-17.

## 3. Público e uso

| Público | Uso |
|---|---|
| Equipe técnica | Validar dados, cobrar devolutivas, analisar e consolidar. |
| Analistas de eixo | Revisar indicadores, ações e análise qualitativa. |
| Alta gestão | Consultar o resumo da UG e os alertas. |
| UGs | Conferir a base antes de preencher resultados e evidências. |
| Câmara / controle social | Não é o produto principal; o RAM oficial é a referência. |

## 4. Escopo

**Dentro do escopo**

- PPA 2026-2029: programas, indicadores, ações e metas.
- Contas 2026: liquidações por UG, UO, programa do PPA, natureza, fonte e mês.
- Programas sem execução, sem indicador e compartilhados.
- Resultados, análises, justificativas e evidências informados pelas UGs.
- Visões transversais, ranking, alertas e qualidade de dados.
- HTML, impressão/PDF e planilha de apoio.

**Fora do escopo**

- Substituir o RAM oficial ou o resumo executivo de contas.
- Refazer a execução orçamentária ou conciliar empenhado/pago sem nova fonte.
- Criar indicadores, metas ou programas fora do PPA.
- Fazer crosswalk automático PPA ação ↔ LOA ação nesta fase.
- Avaliação individual de servidores.
- Dados pessoais ou informações sigilosas nas evidências.

## 5. Fontes e bases

| Insumo | Caminho | Situação |
|---|---|---|
| PPA 2026-2029 | `_dados/Saida/ppa_2026_2029.xlsx` (abas Programas, Indicadores, Ações, Resumo) | Estruturado |
| Contas 2026 | `_dados/Saida/despesas_programas_2026_*.xlsx` (aba Consolidado) | Atualização diária; usar o mais recente |
| Resultados/evidências | `_dados/Saida/raiox/entrada/*.csv` | Opcional; placeholders no protótipo |
| Referência conceitual | `laboratorio/ram/docs/DEFINICAO.md` | Consulta; não importar `pmp_ram` |
| Saídas | `_dados/Saida/raiox/` | Protótipo |

O manifesto `manifest.json` registra o arquivo de contas usado, o período, as contagens e as
saídas geradas.

## 6. O que a base mostra (18/11/2026)

- **PPA:** 87 programas, 247 indicadores, 306 ações e 48 órgãos/entidades.
- **20 programas sem indicador.** Nesses casos, a avaliação é pelas ações e pela análise
  qualitativa, não uma falha automática.
- **Indicadores:** referência atual e referência esperada para 2029, **sem meta anual**.
- **Ações:** meta 2026 preenchida em 305 de 306 ações. Em **277 ações (90,5%)** a meta é um
  percentual do plano (ex.: 25%), não uma quantidade física. Há 28 metas de quantidade
  (Unid, Pc, kWp) e 1 ação sem meta.
- **Contas:** 35 UGs, **43 UOs por nome** e 39.901 linhas. O código da UO no Consolidado
  **não é único**: a UG 004 tem duas UOs com código 001. O raio-x usa o nome normalizado da
  UO como chave e exibe o código como referência.
- **Execução:** R$ 2.057.509.936,33 liquidados (líquido de anulações). Desse total,
  R$ 2.055.288.553,97 estão em programas do PPA e R$ 2.221.382,36 no programa 6200, fora do
  PPA.
- **Cobertura:** 74 dos 87 programas do PPA têm execução; 13 não têm. Dos 13: 7 têm UG
  provisória, 4 não têm UG mapeada (6005, 6083, 6084, 6085) e 2 são excluídos da revisão
  (6034-A, 6066-A).
- **Programas compartilhados (4):** 6013 (UG 001/041), 6023, 6024 e 6025 (UG 004/016).
- **Fora do PPA:** 6200 — Emenda Parlamentar Impositiva Individual — LIVRE, nas UGs 020,
  021 e 022. Entra apenas no anexo de execução.
- **Resultados:** a base de contas não traz resultados de 2026. O protótipo usa placeholders
  explícitos (“Aguardando devolutiva”), sem números inventados.
- **UG 004 (protótipo):** 9 programas próprios, 16 indicadores, 34 ações, 2 UOs e
  R$ 288.307.407,68 liquidados (14,2% do total municipal). Três programas são compartilhados
  com a UG 016; 6022 não tem execução; 6020 não tem indicador.
- **Crosswalk LOA:** 280 ações em programas com execução têm sugestão/código P/A:
  154 sugestões fortes, 21 a verificar e 105 sem correspondência automática. O override
  manual fica em `entrada/crosswalk_loa.csv`.

### 6.1 Limitações que o produto deve explicitar

1. **UO:** o código não é chave confiável; usar o nome normalizado.
2. **Execução:** o Consolidado é de **liquidações**. Não há empenhado/pago. O valor é
   liquidado líquido (realizado + anulados negativos).
3. **Meta da ação:** percentual do plano não é meta física anual. O % da meta só pode ser
   calculado quando meta e resultado são compatíveis.
4. **Indicador:** sem meta anual, a leitura é por referência 2029 e tendência, não por
   “meta atingida”.
5. **Vínculo PPA ↔ LOA:** o elo disponível é o campo **Programa de governo**. Não há
   vínculo oficial PPA ação ↔ LOA ação. O raio-x sugere um **crosswalk provisório por
   similaridade de nomes** e aceita override manual em `crosswalk_loa.csv`; validar.
6. **Mapa PPA órgão → UG:** provisório para os programas sem execução; validar.
7. **Resultados/evidências:** pendentes de coleta; a camada é opcional e independente.

## 7. Estrutura do produto

### 7.1 Índice (`index.html`)

- Capa e metadados: PPA, arquivo de contas, data de geração, versão.
- KPIs: programas, indicadores, ações, UGs, liquidado, cobertura, sem indicador, sem execução.
- Cobertura do PPA nas contas (com execução, sem execução com UG provisória, sem UG,
  excluídos) e o programa 6200 fora do PPA.
- Execução e programas por eixo.
- Ranking de UGs por execução liquidada.
- Mapa de 35 UGs com resumo e link para todas as páginas geradas.
- Visões transversais: sem indicador, sem execução, compartilhados, fora do PPA, excluídos,
  metas não atingidas e qualidade de evidências.
- Qualidade dos dados e metodologia.

### 7.2 Página por UG (`ug_<código>_<slug>.html`)

1. **Resumo:** KPIs e insights automáticos, sem gráficos repetidos.
2. **Programas:** cartão por programa com ficha, objetivo, indicadores, ações do PPA (com
   o **código P/A da LOA sugerido**), uma linha de execução resumida e a **execução LOA
   por ação (projeto/atividade) e natureza/elemento**. Filtros por busca, sem execução, sem indicador e compartilhado.
3. **Execução:** visão da UG por programa, UO, fonte e mês. O detalhamento completo por
   ação LOA (projeto/atividade) e natureza/elemento fica no cartão do programa, junto às
   ações do PPA. As subseções por UO ficam nesta seção quando a UG tem mais de uma UO.
4. **Análise crítica:** dificuldades, riscos, recomendações e análises registradas na camada
   de resultados; campos qualitativos a preencher pela UG.
5. **Evidências:** KPIs, orientação e evidências registradas.
6. **Alertas:** alta, média, baixa e informação, com os alertas agregados por UG.
7. **Qualidade dos dados:** notas técnicas essenciais.
8. **Metodologia:** fontes, chaves, regras e limites.

As antigas tabelas consolidadas de indicadores e ações foram removidas para eliminar a
redundância com os cartões de programa. O checklist completo por programa fica na planilha.

Cada programa tem âncora própria (`#prog-<código>`). Na tela, os cartões começam recolhidos e
o botão “Expandir programas” abre todos; a impressão abre o conteúdo. O detalhamento
Programa → Ação LOA → Natureza/Elemento fica em um bloco expansível e entra na impressão.
Quando a UG tem mais de uma UO, a seção de execução mostra o desdobramento por unidade.

### 7.3 Visões transversais

- Ranking de execução por UG.
- Programas sem indicador.
- Programas sem execução (com UG provisória, sem UG ou excluídos).
- Programas compartilhados e a parte de cada UG.
- Programa 6200 fora do PPA.
- Metas não atingidas (quando houver resultados).
- Qualidade/ausência de evidências.
- Exceções de qualidade de dados.

### 7.4 Multi-ano

O código usa **perfis anuais** (`perfil.py`):

| Ano | Contas | Saída | Meta no PPA |
|---|---|---|---|
| 2026 | `despesas_programas_2026_*.xlsx` | `Saida/raiox/` | Meta 2026 + bloco 2027-2029 |
| 2027 | `despesas_programas_2027_*.xlsx` | `Saida/raiox/2027/` | Bloco 2027-2029 (sem meta anual explícita) |
| 2028 | `despesas_programas_2028_*.xlsx` | `Saida/raiox/2028/` | Bloco 2027-2029 |
| 2029 | `despesas_programas_2029_*.xlsx` | `Saida/raiox/2029/` | Bloco 2027-2029 |

O PPA é o mesmo 2026-2029. Para 2027-2029, a coleta deve informar a **meta anual**
(`meta_anual`) da ação; sem ela, o relatório mostra o bloco e não calcula o % da meta.
Comandos: `scripts\gerar_ano.bat 2027`, `scripts\gerar_pdf.bat 2027` e
`scripts\publicar_site.bat --ano 2027` (o site recebe o ano em subpasta).

### 7.5 Publicação

- **Código:** https://github.com/angelojordy-svg/raiox-ppa (público; somente código, docs,
  testes e scripts).
- **Site:** https://angelojordy-svg.github.io/raiox-ppa-site/ (repo separado, público, com
  apenas HTML/PDF gerados).
- O site não recebe `_dados`, o `manifest.json` com caminhos absolutos nem caches.
- Atualização do site: gerar HTML/PDF, copiar `index.html`, `ug_*.html` e `pdf/` para o repo
  de deploy e commitar.

### 7.6 Job automático

O raio-x é um passo do pipeline diário existente, **depois** do dashboard PMP (que gera
`despesas_programas_*.xlsx`). Não duplica a coleta de dados.

| Passo | O que faz | Depende de |
|---|---|---|
| `raiox` | gera HTML/XLSX e PDFs por UG | `dashboard` |
| `publicar_raiox` | copia HTML/PDF para o repo do site e faz commit/push | `raiox` |

- Tarefa: `Orcamento Publico diario` (já existente), sem nova tarefa.
- Ano: o job detecta o ano mais recente com `despesas_programas_<ano>_*.xlsx` (2026-2029).
- Falha: o passo fica `erro`, mas o pipeline continua; o site permanece na última versão boa.
- Em 2027-2029, usa o perfil do ano e a meta do bloco; a meta anual deve ser informada na coleta.
- A alteração do pipeline (`pipeline_diario.py`) e o card no `mapa_projetos.html` foram feitos
  no motor local; o commit do motor deve ser feito junto com as demais alterações pendentes.

### 7.7 Formatos de saída

- **HTML interativo** com filtros, busca, ordenação de tabelas, navegação e impressão.
- **PDF/print por UG** pela impressão do HTML no navegador (CSS `@media print`) ou por
  `scripts\gerar_pdf.bat` (Edge/Chrome headless).
- **Planilha de apoio XLSX** com abas de UGs, programas, indicadores, ações, execução,
  execução detalhada (programa → ação LOA → natureza), alertas e dicionário.
- **Manifesto JSON** com fontes, escopo, contagens e saídas.

## 8. Modelo de dados

### 8.1 Entidades principais

| Entidade | Campos essenciais |
|---|---|
| Programa | código, nome, eixo, órgão, período, público-alvo, tipo, natureza, objetivo. |
| Indicador | programa, nº, nome, fonte, referência atual, referência 2029. |
| Ação | programa, nº, nome, tipo, produto, meta 2026, meta 2027-2029, objetivo. |
| Execução | UG, UO, programa, natureza, fonte, mês, ação LOA (projeto/atividade), valor realizado/anulado/líquido, linhas, ação × natureza (elemento). |
| ProgramaUG | programa, UG, dono, execução da UG, execução total, outras UGs, situação. |
| ResumoUG | programas próprios/compartilhados, UOs, indicadores, ações, execução, alertas. |
| ResultadoIndicador | programa, nº, resultado, meta 2026, unidade, data, fonte, análise, status, evidência. |
| ResultadoAcao | programa, nº, resultado, meta anual, unidade, data, fonte, análise, status, justificativa, próximos passos, evidência. |
| Evidência | ID, descrição, tipo, link, data, responsável. |
| Alerta | severidade, tipo, UG, programa, mensagem. |

### 8.2 Chaves e regras de junção

- **PPA ↔ contas:** `Programa de governo` (código do programa) → código do PPA.
- **Indicador:** `(código do programa, nº do indicador)`.
- **Ação:** `(código do programa, nº da ação)`.
- **UG:** código de 3 dígitos do Consolidado.
- **UO:** nome normalizado (maiúsculas, sem acentos/pontuação) dentro da UG. O código é
  exibido, mas não é chave.
- **Programa por UG:** a execução define as UGs; o dono vem do mapa provisório quando o
  programa é compartilhado.
- **Programa sem execução:** usa o mapa provisório do `DEFINICAO.md`; se não houver, entra
  em “sem UG mapeada”.
- **Ação LOA:** código da coluna **Projeto/Atividade** (fallback: coluna Ação). O nome e o
  código são exibidos juntos no cartão do programa.
- **6200:** não é programa do PPA; não entra nas contagens de programas, apenas no anexo.

### 8.3 Camada de resultados e evidências

Arquivos CSV em `_dados/Saida/raiox/entrada/`:

- `resultados_indicadores.csv`
- `resultados_acoes.csv`
- `evidencias.csv`
- `crosswalk_loa.csv` — override manual do vínculo PPA ação ↔ LOA projeto/atividade.

Colunas mínimas:

- **Indicadores:** código do programa, nº do indicador, resultado, meta 2026, unidade, data
  de apuração, fonte do resultado, análise, status, evidência.
- **Ações:** código do programa, nº da ação, resultado, meta anual, unidade, data, fonte,
  análise, status, justificativa, próximos passos, evidência.
- **Evidências:** ID, descrição, tipo, link, data, responsável.

O raio-x é independente do RAM. Se as devolutivas do RAM existirem, elas podem ser
convertidas para esse formato; não há importação de código do RAM.

## 9. Regras de análise

### 9.1 Execução

- `liquidado_líquido = realizado + anulados` (anulados negativos).
- `% da UG = valor do programa/UO ÷ liquidado da UG`.
- `% do programa = valor da UG ÷ total do programa` (para compartilhados).
- Programa sem linhas no Consolidado = **sem execução registrada**.
- Programa com linhas e líquido ≤ 0 = **execução anulada** (alerta alto).
- Não há empenhado/pago nesta base; a tela e a planilha dizem isso explicitamente.

### 9.2 Indicadores

- Sem meta anual, a referência é a trajetória entre a referência atual e a de 2029.
- Direção inferida: se 2029 > atual → “aumentar”; se 2029 < atual → “reduzir”; se igual →
  “manter”.
- Tendência: compara o resultado com a referência atual, respeitando a direção.
- Valores não numéricos (ex.: “Diamante”, “7 Urbanas e 2 Campo”) ficam como qualitativos.
- Status: usa a meta 2026 informada pela UG, quando existir; caso contrário, “sem meta anual”
  ou “pendente”.

### 9.3 Ações

- Classificação da meta 2026:
  - `percentual_plano`: “25%”, “28%”, etc. (percentual do plano, não quantidade física).
  - `quantidade`: “50.123 Unid”, “12 Pc”, “25 kWp”, etc.
  - `nao_definida`: sem meta.
  - `texto`: meta não numérica.
- `% da meta` só é calculado quando meta e resultado são compatíveis. Para meta percentual,
  o resultado deve ser informado como % do plano; para quantidade, como quantidade.
- Se a UG informar `meta_anual` na camada de resultados, ela prevalece sobre o percentual do
  PPA.
- Status: Concluída (≥100%), Em andamento (>0), Não iniciada (0), ou o status informado.
- **Crosswalk LOA:** o código P/A exibido na ação do PPA é uma sugestão por similaridade de
  nomes (provisório) ou um override manual; não é vínculo oficial.
- Justificativa e próximos passos são obrigatórios quando o resultado fica abaixo da meta ou
  a ação não foi iniciada.

### 9.4 Programas compartilhados

- Dono provisório: 6013 → UG 001; 6023/6024/6025 → UG 004.
- Cada UG mostra sua parte e o total do programa.
- O raio-x não rateia metas/indicadores entre UGs nesta fase; a UG dona responde pelo
  programa e a outra reporta a parte executada. Validar o rateio antes da coleta.

### 9.5 Programas sem indicador

- Não são tratados como falha automática.
- A avaliação é pelas ações + análise qualitativa (objetivo, público, entregas,
  dificuldades, riscos e recomendações).

### 9.6 Qualidade de evidências

- Evidência obrigatória para resultados críticos e metas não atingidas.
- Evidência obrigatória para ação não iniciada ou sem execução.
- Evidências não podem conter dados pessoais ou informações sigilosas (LGPD).
- No protótipo, a qualidade é “não avaliável” porque não há resultados.

### 9.7 Severidade dos alertas

| Severidade | Exemplos |
|---|---|
| Alta | Programa sem execução; execução anulada; UG sem execução. |
| Média | Programa sem indicador; ação sem meta; vínculo provisório; código de UO duplicado; programas sem UG. |
| Baixa | Indicador sem referência atual. |
| Info | Programa compartilhado; resultado pendente; evidência pendente; 6200 fora do PPA; excluídos. |

## 10. Arquivos e nomenclatura

Saída em `_dados/Saida/raiox/`:

- `index.html` — índice e visões transversais, com as 35 UGs ativas.
- `ug_<código>_<slug>.html` — uma página por UG (35 arquivos).
- `raiox_apoio_completo.xlsx` — planilha de apoio completa.
- `pdf/` — 35 PDFs por UG + PDF do índice (36 arquivos).
- `manifest.json` — fontes, escopo, contagens, PDFs e saídas.
- `entrada/` — modelos CSV de resultados e evidências.

Comandos:

- `scripts\gerar_tudo.bat` — gera HTML, XLSX e manifesto das 35 UGs.
- `scripts\gerar_pdf.bat` — gera os PDFs pela impressão headless do Edge/Chrome.
- `scripts\verificar.bat` — testes e `ruff`.

## 11. Critérios de aceite

**Protótipo (UG 004)** — concluído e validado para escalar

- [x] Dados reais de PPA e contas; resultados como placeholders explícitos.
- [x] 9 programas, 16 indicadores, 34 ações, 2 UOs e 3 programas compartilhados.
- [x] 6022 sem execução e 6020 sem indicador destacados.
- [x] Execução por programa, UO, natureza, fonte, mês e ação da LOA.
- [x] HTML interativo + prévia de impressão + XLSX + manifesto.
- [x] Testes e `ruff` sem erros.
- [x] Validação do visual/escopo pelo usuário.

**Versão completa (35 UGs)**

- [x] 35 UGs cobertas, com todos os programas, indicadores e ações.
- [x] Execução conciliada com o Consolidado (soma do detalhamento = total do PPA).
- [x] Código P/A da LOA sugerido por ação do PPA, com override manual e marcação provisória.
- [x] Exceções e compartilhados tratados.
- [ ] Resultados, análises e evidências das UGs (pendente de coleta).
- [x] Visões transversais e alertas.
- [x] HTML + impressão/PDF + XLSX + manifesto.
- [x] `scripts\verificar.bat` sem erros.

## 12. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Contas atualizam diariamente | Usar o arquivo mais recente e registrar no manifesto. |
| Código de UO duplicado | Chave pelo nome normalizado; exibir o código como referência. |
| Meta de ação percentual | Classificar a meta e exigir meta física anual ou resultado em % do plano. |
| Indicador sem meta anual | Comparar com a referência 2029 e sinalizar tendência. |
| Programa sem execução | Mapa provisório + validação com a área técnica. |
| Programa compartilhado | Dono provisório + parte executada por UG; validar rateio. |
| Sem empenhado/pago | Declarar a limitação; buscar fonte complementar. |
| Sem resultados/evidências | Placeholders e camada CSV; cobrar devolutivas. |
| Volume de 35 UGs | Geração automatizada; validar a versão completa antes de publicar. |
| Impressão longa | CSS de impressão, cartões abertos, quebras de página por seção. |
| LGPD | Orientação e checagem de evidências. |

## 13. Decisões confirmadas e pendências de validação

| Tema | Decisão |
|---|---|
| Nome/local | Manter `laboratorio/raiox`; promover para `planejamento/raiox` só quando virar recorrente. |
| Visual | Claro/institucional técnico, legível em tela e impressão. Confirmado. |
| Saída | `index.html` + uma página por UG + impressão/PDF por UG + XLSX. Confirmado. |
| Execução | Por programa do PPA + ações da LOA como contexto; sem crosswalk PPA ação ↔ LOA ação. Confirmado. |
| Evidências | Independentes, com placeholders; camada CSV opcional. Confirmado. |
| Escopo do protótipo | UG 004 — Educação. Confirmado e validado. |
| Geração completa | 35 UGs geradas em 2026-11-17 (HTML + PDF + XLSX + manifesto). Confirmada. |
| Crosswalk LOA | Provisório por similaridade + override manual; validar com a área técnica. |
| Validação final | Pendente — revisão da versão completa. |
| Prazo | A definir. |

## 14. Pendências

- Validar o mapa PPA órgão→UG dos 13 programas sem execução, especialmente 6005, 6053,
  6083, 6084 e 6085.
- Confirmar dono e rateio dos 4 programas compartilhados.
- Validar o crosswalk PPA ação ↔ LOA projeto/atividade (sugestões e overrides).
- Obter fonte de empenhado/pago, se necessária.
- Definir a meta física anual das ações com meta percentual.
- Confirmar os códigos oficiais das UOs (o Consolidado não é confiável).
- Definir prazo/prioridade e responsável pela coleta.
- Definir o canal de devolução e o formato de assinatura.
- Confirmar o prazo legal do RAM.

## 15. Próximos passos

1. Revisar a versão completa das 35 UGs.
2. Validar o mapa PPA↔UG e os compartilhados.
3. Receber resultados/evidências e reprocessar.
4. Congelar a versão do raio-x para a consolidação do RAM.

---

## Anexo A — Programas sem execução (13)

| Programa | Órgão no PPA | Indicadores | Ações | UG provisória | Situação |
|---|---|---:|---:|---|---|
| 6005 | Fundo Especial de Promoção dos Direitos Indígenas — FEPPI | 0 | 2 | — | Sem UG mapeada |
| 6014 | Fundo Municipal de Defesa do Consumidor | 1 | 1 | 041 | Provisória |
| 6022 | Fundo Municipal de Educação — FNDE | 1 | 1 | 004 | Provisória |
| 6032 | Secretaria Municipal de Assistência Social | 0 | 1 | 005 | Provisória |
| 6033 | Secretaria Municipal de Assistência Social | 1 | 2 | 005 | Provisória |
| 6034-A | Excluídos da revisão do PPA | 0 | 1 | — | Excluído |
| 6053 | Secretaria Municipal da Mulher | 1 | 2 | 011 | Provisória |
| 6066-A | Excluídos da revisão do PPA | 5 | 1 | — | Excluído |
| 6072 | Secretaria de Mineração, Energia, Ciência e Tecnologia | 3 | 3 | 030 | Provisória |
| 6074 | Secretaria Municipal do Meio Ambiente | 9 | 5 | 025 | Provisória |
| 6083 | FUMINEC | 4 | 2 | — | Sem UG mapeada |
| 6084 | Fundo de Incentivo às Ações de Ensino Superior | 4 | 2 | — | Sem UG mapeada |
| 6085 | Fundo de Incentivo às Ações de Ensino Superior | 3 | 3 | — | Sem UG mapeada |

## Anexo B — Programas compartilhados (4)

| Programa | Dono provisório | UGs com execução | Regra proposta |
|---|---|---|---|
| 6013 — Gestão Estratégica e Operacional da PGM | 001 | 001, 041 | UG 001 responde pelo programa; UG 041 reporta a parte executada. |
| 6023 — Gestão da Educação Infantil | 004 | 004, 016 | UG 004 responde; UG 016 reporta a parte do FUNDEB. |
| 6024 — Gestão do Ensino Fundamental | 004 | 004, 016 | UG 004 responde; UG 016 reporta a parte do FUNDEB. |
| 6025 — Gestão da Educação de Jovens e Adultos | 004 | 004, 016 | UG 004 responde; UG 016 reporta a parte do FUNDEB. |

## Anexo C — Dicionário resumido

| Campo | Descrição |
|---|---|
| UG | Unidade gestora (código e nome). |
| UO | Unidade orçamentária; chave pelo nome normalizado. |
| Programa | Código e nome do programa do PPA. |
| Indicador | Indicador do PPA; referência atual e 2029. |
| Ação | Ação do PPA; meta 2026 e meta 2027-2029. |
| Tipo da meta | percentual_plano, quantidade, nao_definida ou texto. |
| Resultado 2026 | Resultado informado pela UG (pendente no protótipo). |
| % da meta | Resultado ÷ meta, quando compatíveis. |
| Liquidado | Liquidação líquida (realizado + anulados negativos). |
| % da UG | Participação do programa/UO no liquidado da UG. |
| % do programa | Participação da UG no total do programa compartilhado. |
| Evidência | ID da evidência vinculada ao resultado. |
| Alerta | Exceção ou pendência de qualidade de dados. |

## Anexo D — Versão completa gerada

- `_dados/Saida/raiox/index.html` — índice com as 35 UGs ativas.
- `_dados/Saida/raiox/ug_*.html` — 35 páginas por UG.
- `_dados/Saida/raiox/raiox_apoio_completo.xlsx` — planilha de apoio completa.
- `_dados/Saida/raiox/pdf/` — 35 PDFs por UG + PDF do índice.
- `_dados/Saida/raiox/manifest.json` — fontes, escopo, contagens e PDFs.
- `_dados/Saida/raiox/entrada/` — modelos CSV.
- Perfis 2027-2029: subpastas `2027/`, `2028/`, `2029/` com o mesmo layout.
- Código: https://github.com/angelojordy-svg/raiox-ppa
- Site: https://angelojordy-svg.github.io/raiox-ppa-site/

Verificação: 62 testes passaram; `ruff check src tests` sem erros. A UG 004 tem 34 páginas
no PDF; o detalhamento completo por programa → ação LOA (projeto/atividade) → natureza
está nos cartões de programa.
