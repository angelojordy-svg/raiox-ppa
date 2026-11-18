"""Planilha de apoio do raio-x."""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from . import __version__, config
from .modelo import Relatorio, detalhe_execucao_ug
from .texto import (
    direcao_indicador,
    formatar_brl,
    parse_meta_acao,
    percentual_meta,
    tendencia,
)

AZUL = "0F2A44"
AZUL_CLARO = "DCE6F1"
CINZA = "F2F5F8"
VERDE = "E2F0D9"
AMARELO = "FFF2CC"
VERMELHO = "FCE4E4"

BORDA = Border(
    left=Side(style="thin", color="D0D7DE"),
    right=Side(style="thin", color="D0D7DE"),
    top=Side(style="thin", color="D0D7DE"),
    bottom=Side(style="thin", color="D0D7DE"),
)


def _cabecalho(ws, colunas: list[tuple[str, int]], linha: int = 1) -> None:
    for i, (titulo, largura) in enumerate(colunas, start=1):
        cel = ws.cell(row=linha, column=i, value=titulo)
        cel.font = Font(bold=True, color="FFFFFF", size=10)
        cel.fill = PatternFill("solid", fgColor=AZUL)
        cel.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cel.border = BORDA
        ws.column_dimensions[get_column_letter(i)].width = largura
    ws.row_dimensions[linha].height = 28


def _linha(ws, valores: list[object], linha: int, *, moeda: set[int] | None = None, pct: set[int] | None = None) -> None:
    for i, valor in enumerate(valores, start=1):
        cel = ws.cell(row=linha, column=i, value=valor)
        cel.border = BORDA
        cel.alignment = Alignment(vertical="top", wrap_text=False)
        if moeda and i in moeda:
            cel.number_format = "#,##0.00"
            cel.alignment = Alignment(horizontal="right", vertical="top")
        if pct and i in pct:
            cel.number_format = "0.0%"
            cel.alignment = Alignment(horizontal="right", vertical="top")
    if linha % 2 == 0:
        for i in range(1, len(valores) + 1):
            ws.cell(row=linha, column=i).fill = PatternFill("solid", fgColor=CINZA)


def _finalizar(ws, n_colunas: int, *, filtro: bool = True) -> None:
    if filtro:
        ws.auto_filter.ref = f"A1:{get_column_letter(n_colunas)}{ws.max_row}"
    ws.freeze_panes = "A2"
    ws.sheet_view.showGridLines = False


def _leia_me(ws, relatorio: Relatorio, escopo: str) -> None:
    ws.sheet_view.showGridLines = False
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 110
    linhas = [
        ("Produto", f"{relatorio.perfil.titulo} — planilha de apoio"),
        ("Versão", __version__),
        ("Gerado em", relatorio.gerado_em.strftime("%d/%m/%Y %H:%M")),
        ("Escopo", escopo),
        ("PPA", str(relatorio.fontes.get("ppa", config.PPA_PADRAO))),
        ("Contas", str(relatorio.fontes.get("contas", relatorio.contas.arquivo))),
        ("Período das contas", f"{relatorio.contas.data_min} a {relatorio.contas.data_max}"),
        ("Programas do PPA", relatorio.n_programas),
        ("Indicadores", relatorio.n_indicadores),
        ("Ações", relatorio.n_acoes),
        ("UGs", len(relatorio.ugs)),
        ("Programas com execução", relatorio.n_programas_com_execucao),
        ("Programas sem execução", relatorio.n_programas_sem_execucao),
        ("Programas sem indicador", relatorio.n_sem_indicador),
        ("Programas compartilhados", relatorio.n_compartilhados),
        ("Liquidado total", formatar_brl(relatorio.total_geral)),
        ("Liquidado no PPA", formatar_brl(relatorio.total_ppa)),
        ("Liquidado fora do PPA", formatar_brl(relatorio.total_fora_ppa)),
        ("Resultados informados", relatorio.n_resultados_indicadores + relatorio.n_resultados_acoes),
        ("Evidências", relatorio.n_evidencias),
    ]
    ws["A1"] = relatorio.perfil.titulo.upper()
    ws["A1"].font = Font(bold=True, size=16, color=AZUL)
    ws["A2"] = "Planilha de apoio — produto interno da equipe técnica"
    ws["A2"].font = Font(italic=True, size=11, color="5B6B7C")
    linha = 4
    for rotulo, valor in linhas:
        ws.cell(row=linha, column=1, value=rotulo).font = Font(bold=True, color=AZUL)
        ws.cell(row=linha, column=2, value=valor)
        ws.cell(row=linha, column=1).border = BORDA
        ws.cell(row=linha, column=2).border = BORDA
        linha += 1
    linha += 1
    notas = [
        "Notas técnicas:",
        "1. A base de contas é de liquidações (Valor R$), com anulados negativos. Não há empenhado/pago no Consolidado.",
        "2. O código da UO no Consolidado não é único; a chave usada é o nome normalizado da UO.",
        f"3. A maior parte das ações tem {relatorio.perfil.meta_ano_label} em percentual do plano/bloco (ex.: 25%), não em quantidade física.",
        "4. Os indicadores têm referência atual e referência 2029, sem meta anual.",
        "5. Programas sem execução usam o mapa provisório do DEFINICAO do RAM; validar.",
        "6. Resultados e evidências estão pendentes; a camada de entrada aceita CSV em _dados/Saida/raiox/entrada.",
        "7. O programa 6200 (emenda parlamentar) está fora do PPA e aparece apenas no anexo de execução.",
        "8. A aba Execucao_Detalhe traz o desdobramento Programa → Ação LOA → Natureza/Elemento.",
        "9. O crosswalk PPA ação ↔ LOA projeto/atividade é provisório; confira a coluna Crosswalk (manual/auto/verificar).",
    ]
    for nota in notas:
        cel = ws.cell(row=linha, column=1, value=nota)
        cel.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=linha, start_column=1, end_row=linha, end_column=2)
        if nota == "Notas técnicas:":
            cel.font = Font(bold=True, color=AZUL)
        linha += 1


def _aba_ugs(ws, relatorio: Relatorio, ugs_geradas: set[str]) -> None:
    colunas = [
        ("Código", 9),
        ("UG", 46),
        ("UOs", 42),
        ("Programas próprios", 12),
        ("Programas compartilhados", 14),
        ("Indicadores", 10),
        ("Ações", 8),
        ("Liquidado (R$)", 16),
        ("% do total", 10),
        ("Sem indicador", 11),
        ("Sem execução", 11),
        ("Alertas altos", 10),
        ("Alertas médios", 10),
        ("Detalhe", 12),
    ]
    _cabecalho(ws, colunas)
    for i, ug in enumerate(relatorio.ranking_ugs, start=2):
        _linha(
            ws,
            [
                ug.codigo,
                ug.nome,
                "; ".join(uo.nome_oficial for uo in ug.uos),
                ug.n_programas_proprios,
                ug.n_programas_compartilhados,
                ug.n_indicadores,
                ug.n_acoes,
                round(ug.execucao_total, 2),
                round(ug.share_global / 100, 6),
                ug.n_sem_indicador,
                ug.n_sem_execucao,
                ug.contar_alertas("alta"),
                ug.contar_alertas("media"),
                "sim" if ug.codigo in ugs_geradas else "não",
            ],
            i,
            moeda={8},
            pct={9},
        )
    _finalizar(ws, len(colunas))


def _situacao_programa(relatorio: Relatorio, codigo: str) -> str:
    item = relatorio.cobertura.get(codigo)
    if item is None:
        return "sem cobertura"
    return {
        "com_execucao": "com execução",
        "sem_execucao": "sem execução (UG provisória)",
        "sem_ug": "sem UG mapeada",
        "excluido": "excluído da revisão",
    }.get(item.status, item.status)


def _aba_programas(ws, relatorio: Relatorio) -> None:
    colunas = [
        ("Código", 9),
        ("Programa", 48),
        ("Eixo", 24),
        ("Órgão no PPA", 42),
        ("Situação", 26),
        ("UG dona", 9),
        ("UGs com execução", 16),
        ("Indicadores", 10),
        ("Ações", 8),
        ("Liquidado total (R$)", 17),
        ("Compartilhado", 12),
        ("Vínculo provisório", 12),
    ]
    _cabecalho(ws, colunas)
    for i, programa in enumerate(relatorio.ppa.programas, start=2):
        item = relatorio.cobertura.get(programa.codigo)
        _linha(
            ws,
            [
                programa.codigo,
                programa.nome,
                programa.eixo,
                programa.orgao,
                _situacao_programa(relatorio, programa.codigo),
                item.dono if item else "",
                ", ".join(item.ugs_execucao) if item else "",
                len(programa.indicadores),
                len(programa.acoes),
                round(item.execucao_total if item else 0.0, 2),
                "sim" if item and len(item.ugs_execucao) > 1 else "não",
                "sim" if item and item.vinculo_provisorio else "não",
            ],
            i,
            moeda={10},
        )
    _finalizar(ws, len(colunas))


def _programas_escopo(relatorio: Relatorio, ugs: set[str]) -> list:
    vistos = set()
    programas = []
    for ug_codigo in ugs:
        resumo = relatorio.ug(ug_codigo)
        if resumo is None:
            continue
        for programa_ug in resumo.programas:
            if programa_ug.codigo in vistos:
                continue
            vistos.add(programa_ug.codigo)
            programas.append(programa_ug.programa)
    return sorted(programas, key=lambda p: p.codigo)


def _aba_indicadores(ws, relatorio: Relatorio, programas: list) -> None:
    colunas = [
        ("Programa", 9),
        ("Indicador", 44),
        ("Nº", 6),
        ("Fonte", 30),
        ("Referência atual", 16),
        (f"Resultado {relatorio.perfil.ano}", 16),
        ("Referência 2029", 16),
        ("Direção", 12),
        ("Tendência", 13),
        ("Status", 15),
        ("Evidência", 12),
    ]
    _cabecalho(ws, colunas)
    linha = 2
    for programa in programas:
        for indicador in programa.indicadores:
            res = relatorio.resultados.indicador(programa.codigo, indicador.n)
            resultado = res.resultado if res else ""
            if not resultado:
                status = "Pendente"
                tend = "A apurar"
            else:
                status = res.status if res and res.status else "Informado"
                tend = tendencia(resultado, indicador.ref_atual, indicador.ref_2029)
            direcao = direcao_indicador(indicador.ref_atual, indicador.ref_2029) or "qualitativo"
            _linha(
                ws,
                [
                    programa.codigo,
                    indicador.nome,
                    indicador.n,
                    indicador.fonte,
                    indicador.ref_atual,
                    resultado,
                    indicador.ref_2029,
                    direcao,
                    tend,
                    status,
                    "",
                ],
                linha,
            )
            linha += 1
    _finalizar(ws, len(colunas))


def _aba_acoes(ws, relatorio: Relatorio, programas: list) -> None:
    colunas = [
        ("Programa", 9),
        ("Ação do PPA", 44),
        ("LOA código", 12),
        ("LOA nome", 40),
        ("LOA liquidado (R$)", 16),
        ("Crosswalk", 12),
        ("Nº", 6),
        ("Tipo", 12),
        ("Produto", 24),
        (relatorio.perfil.meta_ano_label, 14),
        ("Tipo da meta", 18),
        (relatorio.perfil.meta_bloco_label or "Meta do bloco", 14),
        (f"Resultado {relatorio.perfil.ano}", 15),
        ("% da meta", 10),
        ("Status", 14),
        ("Evidência", 12),
        ("Justificativa", 34),
        ("Próximos passos", 34),
    ]
    _cabecalho(ws, colunas)
    linha = 2
    refs_por_programa = {}
    for ug in relatorio.ugs.values():
        for programa_ug in ug.programas:
            if programa_ug.dono == programa_ug.ug or programa_ug.codigo not in refs_por_programa:
                refs_por_programa[programa_ug.codigo] = programa_ug.loa_refs
    for programa in programas:
        for acao in programa.acoes:
            meta = parse_meta_acao(acao.meta_ano, acao.meta_bloco)
            res = relatorio.resultados.acao(programa.codigo, acao.num)
            resultado = res.resultado if res else ""
            pct = percentual_meta(
                resultado,
                meta.valor,
                tipo_meta=meta.tipo,
                meta_anual=res.meta_anual if res else "",
            )
            status = "Pendente" if not resultado else (res.status if res and res.status else "Informado")
            ref = refs_por_programa.get(programa.codigo, {}).get(acao.num)
            total_exec = relatorio.contas.programa_total.get(programa.codigo)
            valor_loa = (
                total_exec.por_acao_loa.get(ref.codigo, 0.0)
                if ref is not None and ref.codigo and total_exec is not None
                else 0.0
            )
            _linha(
                ws,
                [
                    programa.codigo,
                    acao.nome,
                    ref.codigo if ref is not None and ref.codigo else "—",
                    ref.nome if ref is not None and ref.codigo else "—",
                    round(valor_loa, 2) if ref is not None and ref.codigo else "",
                    ref.rotulo if ref is not None else "sem",
                    acao.num,
                    acao.tipo,
                    acao.produto,
                    acao.meta_ano,
                    meta.tipo,
                    acao.meta_bloco,
                    resultado,
                    round(pct / 100, 6) if pct is not None else "",
                    status,
                    "",
                    "",
                    "",
                ],
                linha,
                moeda={5},
                pct={14},
            )
            linha += 1
    _finalizar(ws, len(colunas))


def _aba_execucao_ug(ws, relatorio: Relatorio, ugs: set[str]) -> None:
    colunas = [
        ("UG", 9),
        ("UO", 42),
        ("Programa", 9),
        ("Liquidado (R$)", 16),
        ("Linhas", 8),
        ("% do programa", 12),
        ("% da UG", 10),
    ]
    _cabecalho(ws, colunas)
    linha = 2
    for ug_codigo in sorted(ugs):
        resumo = relatorio.ug(ug_codigo)
        if resumo is None:
            continue
        nomes_uo = {uo.chave: uo.nome_oficial for uo in resumo.uos}
        for programa_ug in resumo.programas:
            programa = programa_ug.programa
            total_programa = programa_ug.execucao_global or 0.0
            for chave_uo, valor in sorted(programa_ug.execucao.por_uo.items()):
                share_programa = valor / total_programa if total_programa else 0.0
                share_ug = valor / resumo.execucao_total if resumo.execucao_total else 0.0
                _linha(
                    ws,
                    [
                        ug_codigo,
                        nomes_uo.get(chave_uo, chave_uo),
                        programa.codigo,
                        round(valor, 2),
                        programa_ug.execucao.linhas_por_uo.get(chave_uo, 0),
                        round(share_programa, 6),
                        round(share_ug, 6),
                    ],
                    linha,
                    moeda={4},
                    pct={6, 7},
                )
                linha += 1
            if programa_ug.sem_execucao:
                _linha(
                    ws,
                    [ug_codigo, "—", programa.codigo, 0.0, 0, 0.0, 0.0],
                    linha,
                    moeda={4},
                    pct={6, 7},
                )
                linha += 1
    _finalizar(ws, len(colunas))


def _aba_execucao_programa(ws, relatorio: Relatorio, programas: list) -> None:
    colunas = [
        ("Programa", 9),
        ("UG", 9),
        ("Liquidado (R$)", 16),
        ("Linhas", 8),
        ("% do programa", 13),
        ("% da UG", 10),
    ]
    _cabecalho(ws, colunas)
    linha = 2
    for programa in programas:
        total = relatorio.contas.total_programa(programa.codigo)
        ugs = relatorio.contas.ugs_do_programa(programa.codigo)
        if not ugs:
            _linha(ws, [programa.codigo, "—", 0.0, 0, 0.0, 0.0], linha, moeda={3}, pct={5, 6})
            linha += 1
            continue
        for ug in ugs:
            valor = relatorio.contas.execucao(programa.codigo, ug).valor_liquido
            linhas = relatorio.contas.execucao(programa.codigo, ug).linhas
            total_ug = relatorio.contas.ugs[ug].execucao.valor_liquido
            _linha(
                ws,
                [
                    programa.codigo,
                    ug,
                    round(valor, 2),
                    linhas,
                    round(valor / total, 6) if total else 0.0,
                    round(valor / total_ug, 6) if total_ug else 0.0,
                ],
                linha,
                moeda={3},
                pct={5, 6},
            )
            linha += 1
    _finalizar(ws, len(colunas))


def _natureza_txt(codigo: str) -> str:
    nome = config.NATUREZAS.get(codigo)
    if nome:
        return f"{codigo} — {nome}"
    categoria = config.CATEGORIAS_NATUREZA.get(".".join(codigo.split(".")[:2]), "")
    return f"{codigo} — {categoria}" if categoria else codigo


def _aba_execucao_detalhe(ws, relatorio: Relatorio, ugs: set[str]) -> None:
    colunas = [
        ("UG", 9),
        ("Programa", 9),
        ("Ação LOA", 34),
        ("Natureza / Elemento", 52),
        ("Liquidado (R$)", 16),
        ("% da ação", 11),
        ("% do programa", 13),
        ("% da UG", 10),
        ("Linhas", 8),
    ]
    _cabecalho(ws, colunas)
    linha = 2
    for ug_codigo in sorted(ugs):
        resumo = relatorio.ug(ug_codigo)
        if resumo is None:
            continue
        for detalhe in detalhe_execucao_ug(resumo):
            acao_txt = (
                f"{detalhe.acao_loa} — {detalhe.nome_acao_loa}"
                if detalhe.acao_loa and detalhe.acao_loa != detalhe.nome_acao_loa
                else (detalhe.nome_acao_loa or "Ação não informada")
            )
            _linha(
                ws,
                [
                    ug_codigo,
                    detalhe.programa,
                    acao_txt,
                    _natureza_txt(detalhe.natureza),
                    round(detalhe.valor, 2),
                    round(detalhe.pct_acao / 100, 6),
                    round(detalhe.pct_programa / 100, 6),
                    round(detalhe.pct_ug / 100, 6),
                    detalhe.linhas,
                ],
                linha,
                moeda={5},
                pct={6, 7, 8},
            )
            linha += 1
    _finalizar(ws, len(colunas))


def _aba_alertas(ws, relatorio: Relatorio, ugs: set[str]) -> None:
    colunas = [
        ("Severidade", 11),
        ("Tipo", 28),
        ("UG", 8),
        ("Programa", 9),
        ("Mensagem", 100),
    ]
    _cabecalho(ws, colunas)
    linha = 2
    alertas = list(relatorio.alertas_globais)
    for ug_codigo in sorted(ugs):
        resumo = relatorio.ug(ug_codigo)
        if resumo:
            alertas.extend(resumo.alertas)
    vistos = set()
    for alerta in alertas:
        chave = (alerta.severidade, alerta.tipo, alerta.codigo_ug, alerta.codigo_programa, alerta.mensagem)
        if chave in vistos:
            continue
        vistos.add(chave)
        _linha(
            ws,
            [
                alerta.severidade,
                alerta.tipo,
                alerta.codigo_ug or "",
                alerta.codigo_programa or "",
                alerta.mensagem,
            ],
            linha,
        )
        linha += 1
    _finalizar(ws, len(colunas))


def _aba_dicionario(ws, relatorio: Relatorio) -> None:
    colunas = [("Campo", 28), ("Descrição", 110)]
    _cabecalho(ws, colunas)
    itens = [
        ("UG", "Unidade gestora (código e nome)."),
        ("UO", "Unidade orçamentária; a chave usada é o nome normalizado."),
        ("Programa", f"Código do programa do {relatorio.perfil.titulo_ppa}."),
        ("Indicador", "Indicador do PPA, com referência atual e referência 2029."),
        ("Ação", "Ação do PPA, com a meta do exercício e a meta do bloco seguinte."),
        ("Meta do exercício", "Meta do PPA para o ano. Pode ser percentual do plano/bloco ou quantidade."),
        ("Tipo da meta", "Classificação: percentual_plano, quantidade, nao_definida ou texto."),
        ("Resultado do exercício", "Resultado informado pela UG; pendente nesta versão."),
        ("% da meta", "Resultado ÷ meta, quando meta e resultado são compatíveis."),
        ("Liquidado (R$)", "Liquidação líquida: realizado + anulados negativos."),
        ("% do programa", "Parcela da UG no total do programa, quando compartilhado."),
        ("% da UG", "Parcela do programa, UO ou item no total liquidado da UG."),
        ("Ação LOA", "Ação orçamentária da LOA; não é a ação do PPA e não há crosswalk."),
        ("Natureza/Elemento", "Código e descrição da natureza da despesa (elemento)."),
        ("Evidência", "ID da evidência vinculada ao resultado."),
        ("Alerta", "Exceção ou pendência de qualidade de dados."),
    ]
    for i, (campo, descricao) in enumerate(itens, start=2):
        _linha(ws, [campo, descricao], i)
    _finalizar(ws, len(colunas), filtro=False)


def gerar_xlsx(
    relatorio: Relatorio,
    destino: Path | str,
    *,
    codigos_ug: set[str] | None = None,
    nome: str = "raiox_apoio.xlsx",
) -> Path:
    todas = codigos_ug is None or set(codigos_ug) == set(relatorio.ugs)
    ugs = codigos_ug if codigos_ug is not None else set(relatorio.ugs)
    programas = list(relatorio.ppa.programas) if todas else _programas_escopo(relatorio, ugs)
    escopo = "todas as UGs" if todas else "UG(s) " + ", ".join(sorted(ugs))
    wb = Workbook()
    ws = wb.active
    ws.title = "Leia-me"
    _leia_me(ws, relatorio, escopo)

    _aba_ugs(wb.create_sheet("UGs"), relatorio, ugs)
    _aba_programas(wb.create_sheet("Programas"), relatorio)
    _aba_indicadores(wb.create_sheet("Indicadores"), relatorio, programas)
    _aba_acoes(wb.create_sheet("Acoes"), relatorio, programas)
    _aba_execucao_ug(wb.create_sheet("Execucao_UG"), relatorio, ugs)
    _aba_execucao_programa(wb.create_sheet("Execucao_Programa"), relatorio, programas)
    _aba_execucao_detalhe(wb.create_sheet("Execucao_Detalhe"), relatorio, ugs)
    _aba_alertas(wb.create_sheet("Alertas"), relatorio, ugs)
    _aba_dicionario(wb.create_sheet("Dicionario"), relatorio)

    wb.properties.title = relatorio.perfil.titulo
    wb.properties.subject = "Planilha de apoio"
    wb.properties.creator = "pmp_raiox"
    wb.properties.description = f"Gerado em {relatorio.gerado_em:%d/%m/%Y %H:%M}"

    pasta = Path(destino)
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / nome
    wb.save(arquivo)
    return arquivo
