"""Pagina HTML de uma Unidade Gestora."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from . import config
from .dados import Acao, Indicador, Programa
from .html_base import (
    badge,
    barras,
    brl,
    brl_curto,
    direcao,
    e,
    hero,
    kpi,
    layout,
    meta_badge,
    natureza_descricao,
    num,
    pct,
    sec,
    status_badge,
    tabela,
    td,
    topbar,
)
from .crosswalk import LoaRef
from .modelo import (
    Alerta,
    ProgramaUG,
    Relatorio,
    ResumoUG,
    detalhe_execucao_ug,
    insights_ug,
    resumo_indicadores_acao,
)
from .perfil import PerfilAno
from .resultados import ResultadoAcao, ResultadoIndicador, Resultados
from .texto import (
    norm,
    parse_meta_acao,
    percentual,
    percentual_meta,
    tendencia,
)


def _status_indicador(indicador: Indicador, resultado: ResultadoIndicador | None) -> str:
    if resultado and resultado.status:
        return resultado.status
    texto_resultado = resultado.resultado if resultado else ""
    if not texto_resultado or texto_resultado in {"-", "—"}:
        return "Pendente"
    if resultado and resultado.meta_ano:
        valor = percentual(texto_resultado, resultado.meta_ano)
        if valor is not None:
            if valor >= 100:
                return "Atingido"
            if valor >= 70:
                return "Atenção"
            return "Não atingido"
    tend = tendencia(texto_resultado, indicador.ref_atual, indicador.ref_2029)
    if tend == "Favorável":
        return "Favorável"
    if tend == "Desfavorável":
        return "Atenção"
    if tend in {"Estável", "Qualitativo"}:
        return tend
    return "Sem meta anual"


def _status_acao(
    acao: Acao,
    resultado: ResultadoAcao | None,
    meta,
    perfil: PerfilAno,
) -> str:
    if resultado and resultado.status:
        return resultado.status
    texto_resultado = resultado.resultado if resultado else ""
    if not texto_resultado or texto_resultado in {"-", "—"}:
        return "Pendente"
    if meta.tipo in {"nao_definida", "texto"}:
        return "Sem meta anual"
    valor = _pct_acao(resultado, meta, perfil)
    if valor is None:
        if perfil.meta_ano_tipo == "bloco" and not (resultado and resultado.meta_anual):
            return "Sem meta anual"
        if meta.tipo == "percentual_plano":
            return "Sem meta física"
        return "Qualitativo"
    if valor >= 100:
        return "Concluída"
    if valor > 0:
        return "Em andamento"
    return "Não iniciada"


def _pct_acao(
    resultado: ResultadoAcao | None,
    meta,
    perfil: PerfilAno,
) -> float | None:
    if not resultado or not resultado.resultado:
        return None
    return percentual_meta(
        resultado.resultado,
        meta.valor,
        tipo_meta=meta.tipo,
        meta_anual=resultado.meta_anual,
        meta_ano_tipo=perfil.meta_ano_tipo,
    )


def _tendencia(resultado: ResultadoIndicador | None, indicador: Indicador) -> str:
    if not resultado or not resultado.resultado:
        return "A apurar"
    return tendencia(resultado.resultado, indicador.ref_atual, indicador.ref_2029)


def _ficha_programa(programa: Programa) -> str:
    campos = [
        ("Eixo", programa.eixo),
        ("Tipo", programa.tipo),
        ("Natureza", programa.natureza),
        ("Período", programa.periodo),
        ("Órgão no PPA", programa.orgao),
        ("Público-alvo", programa.publico_alvo),
    ]
    itens = "".join(
        f"<div><span>{e(label)}</span><strong>{e(valor or '—')}</strong></div>"
        for label, valor in campos
    )
    return f'<div class="ficha">{itens}</div>'


def _tabela_indicadores(
    programas: list[Programa],
    resultados: Resultados,
    id_tabela: str,
    perfil: PerfilAno,
    *,
    incluir_programa: bool = False,
) -> str:
    if not any(programa.indicadores for programa in programas):
        return (
            '<div class="empty">Programa sem indicador no PPA. A avaliação será pelas ações '
            "e pela análise qualitativa.</div>"
        )
    linhas = []
    for programa in programas:
        for indicador in programa.indicadores:
            resultado = resultados.indicador(programa.codigo, indicador.n)
            texto_resultado = resultado.resultado if resultado else ""
            if texto_resultado:
                resultado_html = f"<strong>{e(texto_resultado)}</strong>"
                if resultado and resultado.unidade:
                    resultado_html += f'<span class="cell-note">{e(resultado.unidade)}</span>'
                if resultado and resultado.data_apuracao:
                    resultado_html += (
                        f'<span class="cell-note">apurado em {e(resultado.data_apuracao)}</span>'
                    )
            else:
                resultado_html = '<span class="pending">Aguardando devolutiva</span>'
            evidencia = '<span class="pending">—</span>'
            if resultado and resultado.evidencia_id:
                ev = resultados.evidencia(resultado.evidencia_id)
                if ev and ev.link:
                    evidencia = f'<a href="{e(ev.link)}">{e(resultado.evidencia_id)}</a>'
                else:
                    evidencia = e(resultado.evidencia_id)
            linha = "<tr>"
            if incluir_programa:
                linha += td(f"<strong>{e(programa.codigo)}</strong>", "nowrap")
            linha += (
                td(f"<strong>{e(indicador.n)}</strong>", "center", indicador.n)
                + td(
                    f'<span class="cell-title">{e(indicador.nome)}</span>'
                    f'<span class="cell-note">{e(indicador.fonte or "Fonte não informada")}</span>'
                )
                + td(e(indicador.ref_atual or "—"), "right")
                + td(resultado_html, "right")
                + td(e(indicador.ref_2029 or "—"), "right")
                + td(e(direcao(indicador.ref_atual, indicador.ref_2029)), "center")
                + td(status_badge(_tendencia(resultado, indicador)), "center")
                + td(status_badge(_status_indicador(indicador, resultado)), "center")
                + td(evidencia, "center")
                + "</tr>"
            )
            linhas.append(linha)
    cabecalhos = [("Programa", "left")] if incluir_programa else []
    cabecalhos += [
        ("Nº", "center"),
        ("Indicador", "left"),
        ("Referência atual", "right"),
        (f"Resultado {perfil.ano}", "right"),
        ("Referência 2029", "right"),
        ("Direção", "center"),
        ("Tendência", "center"),
        ("Status", "center"),
        ("Evidência", "center"),
    ]
    return tabela(
        cabecalhos,
        linhas,
        id_tabela=id_tabela,
        classes="table-compact",
        placeholder="Buscar indicador...",
    )


def _tabela_acoes(
    programas: list[Programa],
    resultados: Resultados,
    id_tabela: str,
    perfil: PerfilAno,
    *,
    incluir_programa: bool = False,
    loa_refs: dict[str, LoaRef] | None = None,
) -> str:
    if not any(programa.acoes for programa in programas):
        return '<div class="empty">Programa sem ação no PPA.</div>'
    loa_refs = loa_refs or {}
    linhas = []
    for programa in programas:
        for acao in programa.acoes:
            resultado = resultados.acao(programa.codigo, acao.num)
            meta = parse_meta_acao(acao.meta_ano, acao.meta_bloco)
            texto_resultado = resultado.resultado if resultado else ""
            if texto_resultado:
                resultado_html = f"<strong>{e(texto_resultado)}</strong>"
                if resultado and resultado.unidade:
                    resultado_html += f'<span class="cell-note">{e(resultado.unidade)}</span>'
            else:
                resultado_html = '<span class="pending">Aguardando devolutiva</span>'
            valor_pct = _pct_acao(resultado, meta, perfil)
            pct_html = (
                f"<strong>{pct(valor_pct)}</strong>"
                if valor_pct is not None
                else '<span class="pending">—</span>'
            )
            evidencia = '<span class="pending">—</span>'
            if resultado and resultado.evidencia_id:
                ev = resultados.evidencia(resultado.evidencia_id)
                if ev and ev.link:
                    evidencia = f'<a href="{e(ev.link)}">{e(resultado.evidencia_id)}</a>'
                else:
                    evidencia = e(resultado.evidencia_id)
            nota = ""
            if resultado and resultado.justificativa:
                nota += f'<span class="cell-note">Justificativa: {e(resultado.justificativa)}</span>'
            if resultado and resultado.proximos_passos:
                nota += (
                    f'<span class="cell-note">Próximos passos: {e(resultado.proximos_passos)}</span>'
                )
            ref = loa_refs.get(acao.num)
            if ref is None:
                nota += '<span class="cell-note">LOA: sem correspondência automática.</span>'
            elif not ref.codigo:
                nota += '<span class="cell-note">LOA: sem vínculo manual.</span>'
            else:
                tom = "ok" if ref.origem == "manual" else ("warn" if ref.origem == "auto-fraco" else "info")
                nota += (
                    f'<span class="cell-note">LOA {e(ref.codigo)} — {e(ref.nome)} '
                    f"({brl_curto(ref.valor)}) {badge(ref.rotulo, tom)}</span>"
                )
            linha = "<tr>"
            if incluir_programa:
                linha += td(f"<strong>{e(programa.codigo)}</strong>", "nowrap")
            linha += (
                td(f"<strong>{e(acao.num)}</strong>", "center", acao.num)
                + td(
                    f'<span class="cell-title">{e(acao.nome)}</span>'
                    f'<span class="cell-note">{e(acao.tipo)} · {e(acao.produto or "Produto não informado")}</span>'
                    + nota
                )
                + td(
                    meta_badge(meta, perfil)
                    + (
                        f'<span class="cell-note">{e(meta.texto)}</span>'
                        if meta.tipo == "texto" and meta.texto
                        else ""
                    ),
                    "right",
                )
            )
            if perfil.meta_bloco_label:
                linha += td(e(acao.meta_bloco or "—"), "right")
            linha += (
                td(resultado_html, "right")
                + td(pct_html, "right", valor_pct if valor_pct is not None else "")
                + td(status_badge(_status_acao(acao, resultado, meta, perfil)), "center")
                + td(evidencia, "center")
                + "</tr>"
            )
            linhas.append(linha)
    cabecalhos = [("Programa", "left")] if incluir_programa else []
    cabecalhos += [
        ("Nº", "center"),
        ("Ação do PPA", "left"),
        (perfil.meta_ano_label, "right"),
    ]
    if perfil.meta_bloco_label:
        cabecalhos.append((perfil.meta_bloco_label, "right"))
    cabecalhos += [
        (f"Resultado {perfil.ano}", "right"),
        ("% da meta", "right"),
        ("Status", "center"),
        ("Evidência", "center"),
    ]
    return tabela(
        cabecalhos,
        linhas,
        id_tabela=id_tabela,
        classes="table-compact",
        placeholder="Buscar ação...",
    )


def _execucao_programa_compacto(
    programa_ug: ProgramaUG,
    resumo: ResumoUG,
    perfil: PerfilAno,
) -> str:
    if programa_ug.sem_execucao:
        return (
            '<div class="note bad" style="margin-top:12px"><strong>Sem execução registrada '
            "em 2026.</strong> O programa está no PPA e deve ser justificado pela UG. "
            "Não há linhas no Consolidado para este programa.</div>"
        )
    execucao = programa_ug.execucao
    share_ug = (
        execucao.valor_liquido / resumo.execucao_total * 100 if resumo.execucao_total else 0.0
    )
    principal_uo = ""
    if execucao.por_uo:
        chave_uo, valor_uo = max(execucao.por_uo.items(), key=lambda kv: kv[1])
        nomes_uo = {uo.chave: uo.nome_oficial for uo in resumo.uos}
        principal_uo = (
            f"Principal UO: {nomes_uo.get(chave_uo, chave_uo)} ({brl_curto(valor_uo)})"
        )
    outras = ""
    if programa_ug.outras_ugs:
        outras = " · Outras UGs: " + "; ".join(
            f"UG {outra.codigo} ({brl_curto(outra.valor)})"
            for outra in programa_ug.outras_ugs
        )
    return (
        '<div class="exec-compact">'
        f"<span>Liquidado <strong>{brl(execucao.valor_liquido)}</strong></span>"
        f"<span>{pct(share_ug)} da UG</span>"
        f"<span>{pct(programa_ug.share_programa)} do programa</span>"
        f"<span>{num(execucao.linhas)} linhas</span>"
        + (f"<span>{e(principal_uo)}</span>" if principal_uo else "")
        + (f"<span>{e(outras)}</span>" if outras else "")
        + f'<a href="#loa-{e(programa_ug.codigo)}">Ver execução LOA</a>'
        "</div>"
    )


def _tabela_execucao_programa(programa_ug: ProgramaUG, detalhes: list) -> str:
    if not detalhes:
        return '<div class="empty">Sem execução LOA detalhada para este programa.</div>'
    grupos: list[list] = []
    atual = None
    for detalhe in detalhes:
        if atual is None or detalhe.acao_loa != atual[0].acao_loa:
            atual = [detalhe]
            grupos.append(atual)
        else:
            atual.append(detalhe)
    linhas = []
    for grupo in grupos:
        primeiro = grupo[0]
        total_acao = primeiro.valor_acao
        pct_programa = sum(item.pct_programa for item in grupo)
        pct_ug = sum(item.pct_ug for item in grupo)
        linhas.append(
            '<tr class="group-row"><td colspan="6">'
            f'<span class="badge muted">Código P/A {e(primeiro.acao_loa)}</span> '
            f"<strong>{e(primeiro.nome_acao_loa)}</strong> · "
            f"total {brl(total_acao)} · {pct(pct_programa)} do programa · "
            f"{pct(pct_ug)} da UG"
            "</td></tr>"
        )
        for detalhe in grupo:
            linhas.append(
                "<tr>"
                + td(
                    f"<strong>{e(detalhe.natureza)}</strong>"
                    f'<span class="cell-note">{e(natureza_descricao(detalhe.natureza))}</span>'
                )
                + td(brl(detalhe.valor), "right", detalhe.valor)
                + td(pct(detalhe.pct_acao), "right", detalhe.pct_acao)
                + td(pct(detalhe.pct_programa), "right", detalhe.pct_programa)
                + td(pct(detalhe.pct_ug), "right", detalhe.pct_ug)
                + td(num(detalhe.linhas), "right", detalhe.linhas)
                + "</tr>"
            )
    return tabela(
        [
            ("Natureza / Elemento", "left"),
            ("Liquidado", "right"),
            ("% da ação", "right"),
            ("% do programa", "right"),
            ("% da UG", "right"),
            ("Linhas", "right"),
        ],
        linhas,
        id_tabela=f"loa-detalhe-{programa_ug.codigo}",
        classes="table-compact",
        placeholder="Buscar natureza ou ação...",
    )


def _valores_programa(programa: Programa, relatorio: Relatorio) -> str:
    valores = relatorio.valores_loa.programa(programa.codigo)
    if valores is None or all(
        valor is None
        for valor in (
            valores.fixado,
            valores.empenhado,
            valores.pago,
            valores.a_pagar,
        )
    ):
        return ""
    liquidado = relatorio.contas.total_programa(programa.codigo)
    celulas = [
        ("Fixado inicial", valores.fixado),
        ("Autorizado", None),
        ("Empenhado", valores.empenhado),
        ("Liquidado", liquidado),
        ("Pago", valores.pago),
        ("A pagar", valores.a_pagar),
    ]
    cabecalho = "".join(f"<th>{e(label)}</th>" for label, _ in celulas)
    corpo = "".join(
        f'<td class="right num">{brl(valor) if valor is not None else "n/d"}</td>'
        for _, valor in celulas
    )
    return (
        '<div class="table-wrap"><table class="table table-compact">'
        f"<thead><tr>{cabecalho}</tr></thead><tbody><tr>{corpo}</tr></tbody></table></div>"
        '<p class="small muted">Fixado inicial: LOA 2026; Empenhado/Pago/A pagar: empenhos '
        "2026 (Prefeitura, Câmara e SAAEP); Liquidado: base de liquidações. Valores totais "
        "do programa; a parte desta UG aparece na execução resumida. Autorizado por programa "
        "e valores após créditos adicionais não estão no export local.</p>"
    )


def _programa_card(
    programa_ug: ProgramaUG,
    resumo: ResumoUG,
    resultados: Resultados,
    detalhes_loa: list,
    perfil: PerfilAno,
    relatorio: Relatorio,
) -> str:
    programa = programa_ug.programa
    status: list[str] = []
    badges: list[str] = []
    if programa_ug.sem_execucao:
        status.append("sem-execucao")
        badges.append(badge("Sem execução", "bad"))
    if programa_ug.sem_indicador:
        status.append("sem-indicador")
        badges.append(badge("Sem indicador", "warn"))
    if programa_ug.compartilhado:
        status.append("compartilhado")
        badges.append(badge("Compartilhado", "info"))
    if not status:
        status.append("com-execucao")
    if programa_ug.vinculo_provisorio:
        badges.append(badge("Vínculo provisório", "warn"))
    resumo_meta = resumo_indicadores_acao(programa)
    chips = [
        badge(f"{resumo_meta['indicadores']} indicador(es)", "muted"),
        badge(f"{resumo_meta['acoes']} ação(ões)", "muted"),
        badge(f"{resumo_meta['meta_percentual']} meta(s) percentual(is)", "info"),
        badge(f"{resumo_meta['meta_quantidade']} meta(s) física(s)", "ok"),
    ]
    if resumo_meta["meta_nao_definida"]:
        chips.append(badge(f"{resumo_meta['meta_nao_definida']} sem meta", "warn"))
    if programa_ug.execucao.por_acao_loa and programa.acoes:
        vinculadas = sum(1 for ref in programa_ug.loa_refs.values() if ref.codigo)
        chips.append(
            badge(
                f"LOA: {vinculadas}/{len(programa.acoes)} ações",
                "info" if vinculadas else "warn",
            )
        )
    valor = programa_ug.execucao.valor_liquido
    share = valor / resumo.execucao_total * 100 if resumo.execucao_total else 0.0
    return (
        f'<details class="programa" id="prog-{e(programa.codigo)}" '
        f'data-codigo="{e(programa.codigo)}" data-status="{" ".join(status)}" '
        f'data-busca="{e(norm(programa.codigo + " " + programa.nome))}">'
        "<summary>"
        f'<span class="prog-id">{e(programa.codigo)}</span>'
        '<span class="prog-heading">'
        f"<h3>{e(programa.nome)}</h3>"
        f'<span class="prog-badges">{"".join(badges)}</span>'
        "</span>"
        '<span class="prog-value">'
        f'<strong class="num">{brl_curto(valor)}</strong>'
        f"<span>{pct(share)} da UG · {num(programa_ug.execucao.linhas)} linhas</span>"
        "</span>"
        '<span class="prog-toggle" aria-hidden="true">⌄</span>'
        "</summary>"
        '<div class="prog-body">'
        f"{_ficha_programa(programa)}"
        f'<div class="objetivo"><strong>Objetivo:</strong> {e(programa.objetivo or "Não informado")}</div>'
        + (
            f'<div class="note info"><strong>Programa compartilhado:</strong> dono provisório '
            f"UG {e(programa_ug.dono)}. Indicadores e metas são do programa; esta UG reporta "
            f"a parte executada ({brl(programa_ug.execucao.valor_liquido)}).</div>"
            if programa_ug.dono and programa_ug.dono != programa_ug.ug
            else ""
        )
        + f'<div class="chips">{"".join(chips)}</div>'
        '<div class="panel"><h4>Indicadores do programa</h4>'
        f"{_tabela_indicadores([programa], resultados, f'ind-{programa.codigo}', perfil)}</div>"
        '<div class="panel"><h4>Ações do programa</h4>'
        f"{_tabela_acoes([programa], resultados, f'acao-{programa.codigo}', perfil, loa_refs=programa_ug.loa_refs)}</div>"
        f"{_execucao_programa_compacto(programa_ug, resumo, perfil)}"
        + (
            '<div class="panel"><h4>Valores LOA do programa</h4>'
            + _valores_programa(programa, relatorio)
            + "</div>"
            if _valores_programa(programa, relatorio)
            else ""
        )
        + '<div class="panel" id="loa-'
        f'{e(programa.codigo)}"><h4>Execução LOA — projeto/atividade e natureza</h4>'
        '<p class="small muted">Código da ação orçamentária (projeto/atividade) e sua '
        "natureza/elemento. O vínculo com a ação do PPA é uma sugestão por similaridade de "
        "nomes (crosswalk provisório), exibida na tabela de ações; confirme no crosswalk manual."
        "</p>"
        f"{_tabela_execucao_programa(programa_ug, detalhes_loa)}</div>"
        "</div></details>"
    )


def _alerta_card(alerta: Alerta, *, link_programa: bool = True) -> str:
    tom = {"alta": "bad", "media": "warn", "baixa": "muted", "info": "info"}.get(
        alerta.severidade, "muted"
    )
    programa = ""
    if alerta.codigo_programa:
        if link_programa:
            programa = (
                f'<a class="badge muted" href="#prog-{e(alerta.codigo_programa)}">'
                f"Programa {e(alerta.codigo_programa)}</a>"
            )
        else:
            programa = badge(f"Programa {alerta.codigo_programa}", "muted")
    return (
        f'<div class="alert {e(alerta.severidade)}">'
        '<div class="alert-head">'
        f'{badge(alerta.severidade.capitalize(), tom)}{programa}'
        f"<strong>{e(alerta.mensagem)}</strong>"
        "</div></div>"
    )


def _alertas_lista(alertas: list[Alerta], *, link_programa: bool = True) -> str:
    if not alertas:
        return '<div class="empty">Nenhum alerta registrado.</div>'
    grupos = [("alta", "Alta"), ("media", "Média"), ("baixa", "Baixa"), ("info", "Informação")]
    partes = []
    for chave, rotulo in grupos:
        itens = [a for a in alertas if a.severidade == chave]
        if not itens:
            continue
        partes.append(f"<h4>{e(rotulo)} · {len(itens)}</h4>")
        partes.extend(_alerta_card(a, link_programa=link_programa) for a in itens)
    return "".join(partes)


def _insights(resumo: ResumoUG, relatorio: Relatorio) -> str:
    itens = "".join(
        f'<div class="insight"><span class="dot"></span><span>{e(texto)}</span></div>'
        for texto in insights_ug(resumo, relatorio)
    )
    return f'<div class="insights">{itens}</div>'


def _resumo_execucao_ug(resumo: ResumoUG) -> str:
    linhas = []
    for programa in resumo.programas:
        share = (
            programa.execucao.valor_liquido / resumo.execucao_total * 100
            if resumo.execucao_total
            else 0.0
        )
        if programa.sem_execucao:
            situacao = badge("Sem execução", "bad")
        elif programa.compartilhado:
            situacao = badge("Compartilhado", "info")
        else:
            situacao = status_badge("Com execução")
        linhas.append(
            "<tr>"
            + td(
                f'<a href="#prog-{e(programa.codigo)}"><strong>{e(programa.codigo)}</strong></a>',
                "nowrap",
            )
            + td(e(programa.nome))
            + td(brl(programa.execucao.valor_liquido), "right", programa.execucao.valor_liquido)
            + td(pct(share), "right", share)
            + td(num(programa.execucao.linhas), "right", programa.execucao.linhas)
            + td(situacao, "center")
            + "</tr>"
        )
    return tabela(
        [
            ("Código", "left"),
            ("Programa", "left"),
            ("Liquidado", "right"),
            ("% da UG", "right"),
            ("Linhas", "right"),
            ("Situação", "center"),
        ],
        linhas,
        id_tabela="tabela-programas-ug",
        placeholder="Buscar programa...",
    )


def _tabela_fontes(resumo: ResumoUG, relatorio: Relatorio) -> str:
    ug_contas = relatorio.contas.ugs[resumo.codigo]
    linhas = []
    total = ug_contas.execucao.valor_liquido
    for codigo, valor in ug_contas.execucao.top(ug_contas.execucao.por_fonte, 30):
        share = valor / total * 100 if total else 0.0
        linhas.append(
            "<tr>"
            + td(
                f"<strong>{e(codigo)}</strong>"
                f'<span class="cell-note">{e(config.FONTES.get(codigo, "Descrição não mapeada"))}</span>'
            )
            + td(brl(valor), "right", valor)
            + td(pct(share), "right", share)
            + "</tr>"
        )
    return tabela(
        [("Fonte de recurso", "left"), ("Liquidado", "right"), ("% da UG", "right")],
        linhas,
        id_tabela="tabela-fontes",
        classes="table-compact",
        placeholder="Buscar fonte...",
    )


def _barras_meses(resumo: ResumoUG, relatorio: Relatorio) -> str:
    execucao = relatorio.contas.ugs[resumo.codigo].execucao
    meses = sorted(execucao.por_mes)
    if not meses:
        return '<div class="empty">Sem série mensal.</div>'
    rotulos = {
        "01": "jan",
        "02": "fev",
        "03": "mar",
        "04": "abr",
        "05": "mai",
        "06": "jun",
        "07": "jul",
        "08": "ago",
        "09": "set",
        "10": "out",
        "11": "nov",
        "12": "dez",
    }
    itens = []
    for mes in meses:
        ano, _, numero = mes.partition("-")
        rotulo = f"{rotulos.get(numero, numero)}/{ano[-2:]}"
        itens.append((rotulo, execucao.por_mes[mes]))
    return barras(itens, formato="brl", limite=24)


def _analise_critica(relatorio: Relatorio, resumo: ResumoUG) -> str:
    sem_execucao = [p for p in resumo.programas_proprios if p.sem_execucao]
    sem_indicador = [p for p in resumo.programas_proprios if p.sem_indicador]
    compartilhados = [p for p in resumo.programas if p.compartilhado]
    dificuldades = []
    if sem_execucao:
        dificuldades.append(
            "Programa(s) sem execução registrada: "
            + ", ".join(f"{p.codigo} — {p.nome}" for p in sem_execucao)
            + "."
        )
    if sem_indicador:
        dificuldades.append(
            "Programa(s) sem indicador no PPA: "
            + ", ".join(f"{p.codigo} — {p.nome}" for p in sem_indicador)
            + "."
        )
    if compartilhados:
        dificuldades.append(
            "Programa(s) compartilhado(s) que exigem rateio e validação de dono: "
            + ", ".join(p.codigo for p in compartilhados)
            + "."
        )
    if resumo.resultados_pendentes:
        dificuldades.append(
            f"{resumo.resultados_pendentes} indicador(es)/ação(ões) sem resultado "
            f"{relatorio.perfil.ano} informado; a análise qualitativa depende da devolutiva da UG."
        )
    riscos = []
    for alerta in resumo.alertas:
        if alerta.severidade in {"alta", "media"}:
            riscos.append(alerta.mensagem)
    if not riscos:
        riscos.append("Nenhum risco alto ou médio registrado na base.")
    recomendacoes = []
    if sem_execucao:
        recomendacoes.append("Cobrar justificativa e evidência dos programas sem execução.")
    if sem_indicador:
        recomendacoes.append("Avaliar os programas sem indicador pelas ações e pela análise qualitativa.")
    if compartilhados:
        recomendacoes.append("Validar dono e rateio dos programas compartilhados antes da coleta.")
    if resumo.n_acoes:
        metas = sum(p.n_acoes_meta_percentual for p in resumo.programas)
        if metas:
            recomendacoes.append(
                "Solicitar a meta física anual (ou o resultado em % do plano) das ações com meta percentual."
            )
    if resumo.resultados_pendentes:
        recomendacoes.append("Priorizar a coleta de resultados, análises e evidências dos itens pendentes.")
    recomendacoes.append("Validar o mapa PPA órgão→UG e os códigos oficiais das UOs.")
    analises = []
    for programa in resumo.programas:
        for indicador in programa.programa.indicadores:
            resultado = relatorio.resultados.indicador(programa.codigo, indicador.n)
            if resultado and resultado.analise:
                analises.append(
                    f"<li><strong>{e(programa.codigo)} · indicador {e(indicador.n)}:</strong> "
                    f"{e(resultado.analise)}</li>"
                )
        for acao in programa.programa.acoes:
            resultado = relatorio.resultados.acao(programa.codigo, acao.num)
            if resultado and resultado.analise:
                analises.append(
                    f"<li><strong>{e(programa.codigo)} · ação {e(acao.num)}:</strong> "
                    f"{e(resultado.analise)}</li>"
                )
    analises_html = (
        "<ul>" + "".join(analises) + "</ul>"
        if analises
        else '<div class="empty">Nenhuma análise qualitativa registrada. '
        "Preencher na devolutiva da UG.</div>"
    )
    return (
        '<div class="grid grid-2">'
        '<div class="card"><h3>Análise qualitativa (a preencher pela UG)</h3>'
        "<p><strong>Destaques:</strong> principais entregas, resultados e boas práticas.</p>"
        "<p><strong>Dificuldades:</strong> restrições, atrasos e causas.</p>"
        "<p><strong>Riscos:</strong> riscos de não atingir a referência de 2029.</p>"
        "<p><strong>Recomendações:</strong> próximos passos, parcerias e correções.</p></div>"
        '<div class="card"><h3>Dificuldades identificadas na base</h3><ul>'
        + (
            "".join(f"<li>{e(item)}</li>" for item in dificuldades)
            or "<li>Nenhuma dificuldade crítica registrada.</li>"
        )
        + "</ul></div>"
        '<div class="card"><h3>Riscos</h3><ul>'
        + "".join(f"<li>{e(item)}</li>" for item in riscos)
        + "</ul></div>"
        '<div class="card"><h3>Recomendações</h3><ul>'
        + "".join(f"<li>{e(item)}</li>" for item in recomendacoes)
        + "</ul></div></div>"
        '<div class="card" style="margin-top:12px"><h3>Análises registradas na camada de resultados</h3>'
        f"{analises_html}</div>"
    )


def _notas_qualidade(relatorio: Relatorio) -> str:
    n_meta = sum(
        1
        for p in relatorio.ppa.programas
        for a in p.acoes
        if parse_meta_acao(a.meta_ano, a.meta_bloco).tipo == "percentual_plano"
    )
    n_itens = len(relatorio.ppa.indicadores) + len(relatorio.ppa.acoes)
    n_resultados = relatorio.n_resultados_indicadores + relatorio.n_resultados_acoes
    return (
        '<div class="grid grid-2">'
        '<div class="note warn"><strong>UO:</strong> o código da unidade orçamentária no '
        "Consolidado não é único. A UG 004, por exemplo, tem duas UOs com código 001. "
        "O raio-x usa o nome normalizado da UO como chave e exibe o código apenas como "
        "referência.</div>"
        f'<div class="note warn"><strong>Meta das ações:</strong> {n_meta} de '
        f"{len(relatorio.ppa.acoes)} ações usam {relatorio.perfil.meta_ano_label} em "
        "percentual do plano/bloco, não em quantidade física. O raio-x classifica a meta e "
        "não calcula execução física contra percentual sem a meta anual informada.</div>"
        f'<div class="note warn"><strong>Execução:</strong> o Consolidado {relatorio.perfil.ano} '
        "é de liquidações (Valor R$), com anulados negativos. Fixado inicial e empenhado/pago "
        "vêm de fontes locais (LOA/empenhos); autorizado por programa não está consolidado. "
        "O raio-x mostra liquidado líquido.</div>"
        f'<div class="note info"><strong>Resultados:</strong> {n_resultados} de {n_itens} '
        f"indicadores/ações têm resultado {relatorio.perfil.ano} na base. O relatório usa "
        "placeholders; a camada de resultados pode ser alimentada por CSV/XLSX.</div>"
        "</div>"
    )


def _metodologia(relatorio: Relatorio, resumo: ResumoUG | None = None) -> str:
    alvo = f" da UG {resumo.codigo}" if resumo else ""
    return (
        '<div class="grid grid-2">'
        '<div class="card"><h3>Fontes e chaves</h3>'
        f"<p><strong>{relatorio.perfil.titulo_ppa}:</strong> abas Programas, Indicadores e Ações. "
        "O código do programa é a chave dos indicadores e das ações.</p>"
        f"<p><strong>Contas {relatorio.perfil.ano}:</strong> <code>{e(relatorio.contas.arquivo.name)}</code>, "
        "aba Consolidado. O vínculo PPA↔contas é o campo <strong>Programa de governo</strong>. "
        "Não há vínculo oficial entre a ação do PPA e a ação da LOA; o raio-x sugere um "
        "crosswalk por similaridade de nomes (provisório) e aceita override em "
        "<code>crosswalk_loa.csv</code>. O código P/A da LOA é exibido na ação do PPA.</p>"
        "<p><strong>UO:</strong> a chave é o nome normalizado da unidade orçamentária; o "
        "código do Consolidado é exibido como referência e pode se repetir.</p></div>"
        '<div class="card"><h3>Regras de leitura</h3>'
        "<p><strong>Execução:</strong> liquidado líquido = valores realizados + anulados "
        "(negativos). Não inclui empenhado ou pago. O detalhamento por ação da LOA "
        "(projeto/atividade) e natureza/elemento está no cartão de cada programa.</p>"
        "<p><strong>Indicadores:</strong> o PPA traz referência atual e referência 2029, sem "
        "meta anual. A direção é inferida pela variação entre as referências; a tendência "
        "compara o resultado com a referência atual.</p>"
        f"<p><strong>Ações:</strong> a {relatorio.perfil.meta_ano_label} pode ser percentual do "
        "plano/bloco ou quantidade. "
        "O % da meta só é calculado quando a meta e o resultado são compatíveis.</p>"
        "<p><strong>Compartilhados:</strong> o dono é provisório (mapa do DEFINICAO do RAM); "
        "cada UG mostra sua parte e o total do programa.</p></div>"
        f'<div class="card"><h3>Escopo desta versão{alvo}</h3>'
        "<p>Protótipo interno, independente do RAM. Não importa o código nem os artefatos do "
        "RAM. A camada de resultados/evidências é opcional e fica em "
        "<code>PMP_DATA_ROOT/Saida/raiox/entrada</code>.</p>"
        "<p>O PDF pode ser gerado pela impressão do HTML no navegador. O raio-x não substitui "
        "o RAM oficial nem o resumo executivo de contas.</p></div>"
        '<div class="card"><h3>Limites e pendências</h3>'
        "<p>Validar o mapa PPA órgão→UG dos programas sem execução; confirmar o dono e o "
        "rateio dos programas compartilhados; obter a fonte de empenhado/pago; definir a meta "
        "física anual das ações com meta percentual; validar os resultados e as evidências "
        "com as UGs.</p></div></div>"
    )


def _uo_programas_tabela(programa_ug: list, uo) -> str:
    linhas = []
    for programa in programa_ug:
        valor = programa.execucao.por_uo.get(uo.chave, 0.0)
        share_uo = valor / uo.valor * 100 if uo.valor else 0.0
        share_programa = (
            valor / programa.execucao_global * 100 if programa.execucao_global else 0.0
        )
        linhas_u = programa.execucao.linhas_por_uo.get(uo.chave, 0)
        linhas.append(
            "<tr>"
            + td(
                f'<a href="#prog-{e(programa.codigo)}"><strong>{e(programa.codigo)}</strong></a>',
                "nowrap",
            )
            + td(e(programa.nome))
            + td(brl(valor), "right", valor)
            + td(pct(share_uo), "right", share_uo)
            + td(pct(share_programa), "right", share_programa)
            + td(num(linhas_u), "right", linhas_u)
            + "</tr>"
        )
    return tabela(
        [
            ("Programa", "left"),
            ("Nome", "left"),
            ("Liquidado na UO", "right"),
            ("% da UO", "right"),
            ("% do programa", "right"),
            ("Linhas", "right"),
        ],
        linhas,
        id_tabela=f"uo-{e(uo.chave)}",
        classes="table-compact",
        busca=False,
    )


def _secao_uos(relatorio: Relatorio, resumo: ResumoUG) -> str:
    cards = []
    for uo in resumo.uos:
        cards.append(
            '<div class="card" style="margin-top:12px">'
            f'<h3>{e(uo.nome_oficial)}</h3>'
            f'<p class="small muted">UO cód. {e(", ".join(uo.codigos))} · '
            f"{num(uo.linhas)} linhas · {len(uo.programas)} programa(s) com execução.</p>"
            '<div class="mini-kpis">'
            f'<div class="mini"><span>Liquidado</span><strong>{brl(uo.valor)}</strong></div>'
            f'<div class="mini"><span>% da UG</span><strong>{pct(uo.share_ug)}</strong></div>'
            f'<div class="mini"><span>Programas</span><strong>{len(uo.programas)}</strong></div>'
            f'<div class="mini"><span>Linhas</span><strong>{num(uo.linhas)}</strong></div>'
            "</div>"
            + _uo_programas_tabela(uo.programas, uo)
            + "</div>"
        )
    sem_exec = [p for p in resumo.programas if p.sem_execucao]
    nota = ""
    if sem_exec:
        nota = (
            '<div class="note warn" style="margin-top:12px"><strong>Programa(s) sem execução '
            "não alocados em UO:</strong> "
            + ", ".join(f"{p.codigo} — {p.nome}" for p in sem_exec)
            + ". A justificativa deve ser pedida na coleta.</div>"
        )
    return (
        '<p class="small muted">A UG tem '
        f"{len(resumo.uos)} UOs. A execução e os programas são mostrados separadamente; "
        "o código da UO no Consolidado é apenas referência, pois não é único.</p>"
        + "".join(cards)
        + nota
    )


def gerar_pagina_ug(relatorio: Relatorio, resumo: ResumoUG) -> str:
    resultados = relatorio.resultados
    hero_html = hero(
        relatorio.perfil.titulo,
        f"UG {resumo.codigo} — {resumo.nome} · diagnóstico de {relatorio.perfil.ano} "
        f"({relatorio.perfil.rotulo_ano} do PPA)",
        f"UG {resumo.codigo}",
        arquivo_contas=relatorio.contas.arquivo.name,
        gerado_em=relatorio.gerado_em,
        perfil=relatorio.perfil,
    )
    links_topo = [
        ("resumo", "Resumo"),
        ("programas", "Programas"),
        ("execucao", "Execução"),
        ("analise", "Análise"),
        ("evidencias", "Evidências"),
        ("alertas", "Alertas"),
        ("metodologia", "Metodologia"),
    ]
    topbar_html = topbar(links_topo)
    n_itens = resumo.n_indicadores + resumo.n_acoes
    detalhes_por_programa = defaultdict(list)
    for detalhe in detalhe_execucao_ug(resumo):
        detalhes_por_programa[detalhe.programa].append(detalhe)
    total_programas = resumo.n_programas_proprios + resumo.n_programas_compartilhados
    if resumo.n_programas_compartilhados:
        hint_programas = (
            f"{resumo.n_programas_proprios} próprio(s) · "
            f"{resumo.n_programas_compartilhados} compartilhado(s)"
        )
    elif resumo.n_compartilhados:
        hint_programas = f"{resumo.n_compartilhados} com execução compartilhada"
    else:
        hint_programas = "sem programa compartilhado"
    kpi_programas = kpi(
        "Programas",
        f"{total_programas}",
        hint_programas,
        "teal",
    )
    kpis = (
        '<div class="kpi-grid">'
        + kpi_programas
        + kpi("Indicadores", f"{resumo.n_indicadores}", "referência atual e 2029; sem meta anual", "teal")
        + kpi("Ações", f"{resumo.n_acoes}", f"{relatorio.perfil.meta_ano_label} do PPA", "teal")
        + kpi(
            f"Liquidado {relatorio.perfil.ano}",
            brl_curto(resumo.execucao_total),
            f"{pct(resumo.share_global)} do total municipal",
            "green",
        )
        + kpi("UOs", f"{len(resumo.uos)}", "subseções por unidade orçamentária")
        + kpi(
            "Resultados",
            f"{resumo.n_resultados}/{n_itens}",
            f"resultados de {relatorio.perfil.ano} informados",
        )
        + kpi("Sem indicador", f"{resumo.n_sem_indicador}", "programa(s) próprio(s)", "amber")
        + kpi("Sem execução", f"{resumo.n_sem_execucao}", "programa(s) próprio(s)", "red")
        + "</div>"
    )
    resumo_secao = sec(
        "resumo",
        "Leitura da UG",
        f"Resumo — {resumo.nome}",
        _insights(resumo, relatorio),
        "Indicadores, ações, execução e alertas da UG. O detalhamento completo está nos "
        "cartões de programa.",
    )
    programas_secao = sec(
        "programas",
        "Diagnóstico",
        "Programas do PPA",
        '<div class="filters no-print">'
        '<input id="busca-programa" type="search" placeholder="Buscar programa, indicador ou ação..." aria-label="Buscar programa">'
        '<button class="chip-btn ativo" type="button" data-filtro-programa="todos">Todos</button>'
        '<button class="chip-btn" type="button" data-filtro-programa="sem-execucao">Sem execução</button>'
        '<button class="chip-btn" type="button" data-filtro-programa="sem-indicador">Sem indicador</button>'
        '<button class="chip-btn" type="button" data-filtro-programa="compartilhado">Compartilhado</button>'
        '<button class="btn ghost" type="button" data-expandir="abrir">Expandir programas</button>'
        '<span class="small muted" id="contador-programas"></span>'
        "</div>"
        + "".join(
            _programa_card(
                p,
                resumo,
                resultados,
                detalhes_por_programa.get(p.codigo, []),
                relatorio.perfil,
                relatorio,
            )
            for p in resumo.programas
        ),
        "Cada programa traz ficha, indicadores, ações do PPA e a execução LOA por "
        "projeto/atividade e natureza.",
    )
    if len(resumo.uos) > 1:
        conteudo_uos = (
            '<div class="card" style="margin-top:12px"><h3>Subseções por UO</h3>'
            + _secao_uos(relatorio, resumo)
            + "</div>"
        )
    elif resumo.uos:
        uo = resumo.uos[0]
        conteudo_uos = (
            '<div class="note" style="margin-top:12px"><strong>UO única:</strong> '
            f"{e(uo.nome_oficial)} · {brl(uo.valor)} ({pct(uo.share_ug)} da UG) · "
            f"{num(uo.linhas)} linhas.</div>"
        )
    else:
        conteudo_uos = ""
    execucao_secao = sec(
        "execucao",
        "Execução orçamentária",
        f"Execução {relatorio.perfil.ano} da UG",
        '<div class="mini-kpis">'
        f'<div class="mini"><span>Liquidado</span><strong>{brl(resumo.execucao_total)}</strong></div>'
        f'<div class="mini"><span>Realizado</span><strong>{brl(resumo.execucao_realizado)}</strong></div>'
        f'<div class="mini"><span>Anulado</span><strong>{brl(resumo.execucao_anulado)}</strong></div>'
        f'<div class="mini"><span>Linhas</span><strong>{num(resumo.linhas)}</strong></div>'
        "</div>"
        '<div class="card" style="margin-top:12px"><h3>Por programa do PPA</h3>'
        + _resumo_execucao_ug(resumo)
        + "</div>"
        + conteudo_uos
        + '<div class="note" style="margin-top:12px"><strong>Detalhamento:</strong> a execução '
        "por ação LOA (projeto/atividade) e natureza/elemento está no cartão de cada programa, "
        "junto às ações do PPA.</div>"
        '<div class="grid grid-2" style="margin-top:12px">'
        '<div class="card"><h3>Evolução mensal</h3>'
        + _barras_meses(resumo, relatorio)
        + "</div>"
        '<div class="card"><h3>Por fonte de recurso</h3>'
        + _tabela_fontes(resumo, relatorio)
        + "</div></div>"
        '<div class="note warn" style="margin-top:12px"><strong>Nota:</strong> a base é de '
        "liquidações. O valor exibido é o liquidado líquido (realizado + anulados negativos). "
        "Fixado/empenhado/pago vêm de fontes locais; autorizado não consolidado por programa."
        "</div>",
        "Visão da UG por programa, UO, fonte e mês. O detalhe por ação LOA/projeto-atividade "
        "e natureza está no cartão do programa.",
    )
    analise_secao = sec(
        "analise",
        "Análise crítica",
        "Destaques, dificuldades, riscos e recomendações",
        _analise_critica(relatorio, resumo),
        "Dificuldades, riscos e recomendações a partir dos alertas da base; a análise "
        "qualitativa é preenchida pela UG na devolutiva.",
    )
    n_evidencias = len(relatorio.resultados.evidencias)
    if relatorio.resultados.evidencias:
        linhas_ev = []
        for ev in relatorio.resultados.evidencias.values():
            link = f'<a href="{e(ev.link)}">{e(ev.id)}</a>' if ev.link else e(ev.id)
            linhas_ev.append(
                "<tr>"
                + td(link, "nowrap")
                + td(e(ev.descricao))
                + td(e(ev.tipo))
                + td(e(ev.data), "center")
                + td(e(ev.responsavel))
                + "</tr>"
            )
        tabela_ev = tabela(
            [("ID", "left"), ("Descrição", "left"), ("Tipo", "left"), ("Data", "center"), ("Responsável", "left")],
            linhas_ev,
            id_tabela="tabela-evidencias",
            classes="table-compact",
            busca=False,
        )
    else:
        tabela_ev = '<div class="empty">Nenhuma evidência registrada.</div>'
    evidencias_secao = sec(
        "evidencias",
        "Qualidade da informação",
        "Resultados e evidências",
        '<div class="grid grid-4">'
        + kpi("Itens", str(n_itens), "indicadores + ações", "teal")
        + kpi(
            "Com resultado",
            str(resumo.n_resultados),
            f"resultados de {relatorio.perfil.ano} informados",
        )
        + kpi("Evidências", str(n_evidencias), "arquivos/links registrados", "green")
        + kpi("Pendentes", str(resumo.resultados_pendentes), "dependem da devolutiva", "amber")
        + "</div>"
        + '<div class="card" style="margin-top:12px"><h3>Orientação</h3>'
        f"<p>Nenhum resultado de {relatorio.perfil.ano} foi informado na base. O relatório mostra "
        "<strong>Aguardando devolutiva</strong> em cada indicador e ação.</p>"
        "<p>Quando a coleta for preenchida, o raio-x aceita resultados, análise, status, "
        "justificativa, próximos passos e IDs de evidência. Evidências obrigatórias para "
        "resultados críticos e metas não atingidas.</p>"
        "<p>Não incluir dados pessoais ou informações sigilosas nas evidências (LGPD).</p>"
        '<p class="small muted">Pasta de entrada: <code>'
        + "PMP_DATA_ROOT/Saida/raiox/entrada"
        + "</code></p></div>"
        + '<div class="card" style="margin-top:12px"><h3>Evidências registradas</h3>'
        + tabela_ev
        + "</div>",
        "A qualidade das evidências só é avaliável depois da devolutiva das UGs. O checklist "
        "completo por programa está na planilha de apoio.",
    )
    alertas_secao = sec(
        "alertas",
        "Exceções e riscos",
        "Alertas da UG",
        '<div class="grid grid-3">'
        + kpi("Alta", str(resumo.contar_alertas("alta")), "exigem justificativa", "red")
        + kpi("Média", str(resumo.contar_alertas("media")), "conferir na validação", "amber")
        + kpi("Info", str(resumo.contar_alertas("info")), "contexto e pendências")
        + "</div>"
        + '<div style="margin-top:12px">'
        + _alertas_lista(resumo.alertas)
        + "</div>",
        "Programas sem execução, sem indicador, compartilhados, metas percentuais, vínculos "
        "provisórios e resultados pendentes.",
    )
    qualidade_secao = sec(
        "qualidade",
        "Notas técnicas",
        "Qualidade dos dados",
        _notas_qualidade(relatorio),
        "Limitações que afetam a leitura e devem ser resolvidas antes da versão final.",
    )
    metodologia_secao = sec(
        "metodologia",
        "Método",
        "Como o raio-x foi calculado",
        _metodologia(relatorio, resumo),
    )
    corpo = (
        kpis
        + resumo_secao
        + programas_secao
        + execucao_secao
        + analise_secao
        + evidencias_secao
        + alertas_secao
        + qualidade_secao
        + metodologia_secao
    )
    return layout(
        f"{relatorio.perfil.titulo} · UG {resumo.codigo} — {resumo.nome}",
        hero_html,
        topbar_html,
        corpo,
        perfil=relatorio.perfil,
    )


def gerar_html_ug(relatorio: Relatorio, codigo_ug: str, destino: Path | str) -> Path:
    resumo = relatorio.ug(codigo_ug)
    if resumo is None:
        raise ValueError(f"UG não encontrada: {codigo_ug}")
    pasta = Path(destino)
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / f"ug_{resumo.codigo}_{resumo.slug}.html"
    arquivo.write_text(gerar_pagina_ug(relatorio, resumo), encoding="utf-8")
    return arquivo
