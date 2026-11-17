"""Pagina HTML de indice e visoes transversais do raio-x."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from .html_base import (
    badge,
    barras,
    brl,
    brl_curto,
    e,
    hero,
    kpi,
    layout,
    num,
    pct,
    sec,
    status_badge,
    tabela,
    td,
    topbar,
)
from .html_ug import _alertas_lista, _metodologia
from .modelo import CoberturaPrograma, Relatorio
from .texto import parse_meta_acao, percentual, percentual_meta


def _execucao_por_eixo(relatorio: Relatorio) -> list[tuple[str, float, int]]:
    valores: dict[str, float] = defaultdict(float)
    contagem: Counter[str] = Counter()
    for programa in relatorio.ppa.programas:
        contagem[programa.eixo] += 1
        execucao = relatorio.contas.programa_total.get(programa.codigo)
        if execucao:
            valores[programa.eixo] += execucao.valor_liquido
    return sorted(
        ((eixo, valores.get(eixo, 0.0), contagem[eixo]) for eixo in contagem),
        key=lambda item: (-item[1], item[0]),
    )


def _tabela_cobertura(relatorio: Relatorio) -> str:
    linhas = [
        ("Com execução registrada", relatorio.n_programas_com_execucao, "ok", "Programas com linhas no Consolidado."),
        (
            "Sem execução — UG provisória",
            relatorio.n_programas_sem_execucao_mapeado,
            "warn",
            "Mapeados pelo DEFINICAO do RAM; validar.",
        ),
        ("Sem UG mapeada", relatorio.n_sem_ug, "bad", "Programas do PPA sem UG de execução."),
        ("Excluídos da revisão", relatorio.n_excluidos, "muted", "6034-A e 6066-A."),
    ]
    total = sum(item[1] for item in linhas) or 1
    corpo = []
    for rotulo, quantidade, tom, nota in linhas:
        corpo.append(
            "<tr>"
            + td(badge(rotulo, tom))
            + td(num(quantidade), "right", quantidade)
            + td(pct(quantidade / total * 100), "right", quantidade / total * 100)
            + td(e(nota))
            + "</tr>"
        )
    return tabela(
        [("Situação", "left"), ("Programas", "right"), ("% do PPA", "right"), ("Observação", "left")],
        corpo,
        id_tabela="tabela-cobertura",
        classes="table-compact",
        busca=False,
    )


def _stack_cobertura(relatorio: Relatorio) -> str:
    total = relatorio.n_programas or 1
    partes = [
        ("s1", relatorio.n_programas_com_execucao, "Com execução"),
        ("s2", relatorio.n_programas_sem_execucao_mapeado, "Sem execução (UG provisória)"),
        ("s3", relatorio.n_sem_ug, "Sem UG mapeada"),
        ("s4", relatorio.n_excluidos, "Excluídos"),
    ]
    barras_html = "".join(
        f'<span class="{classe}" style="width:{quantidade / total * 100:.2f}%" '
        f'title="{e(rotulo)}: {quantidade}"></span>'
        for classe, quantidade, rotulo in partes
        if quantidade
    )
    legenda = "".join(
        f'<span><i class="{classe}" style="background:{cor}"></i>{e(rotulo)}: '
        f"<strong>{quantidade}</strong></span>"
        for (classe, quantidade, rotulo), cor in zip(
            partes,
            ["#0f766e", "#f59e0b", "#64748b", "#b91c1c"],
            strict=False,
        )
        if quantidade
    )
    return f'<div class="stack">{barras_html}</div><div class="legend">{legenda}</div>'


def _tabela_eixos(relatorio: Relatorio) -> str:
    linhas = []
    for eixo, valor, quantidade in _execucao_por_eixo(relatorio):
        share = valor / relatorio.total_ppa * 100 if relatorio.total_ppa else 0.0
        linhas.append(
            "<tr>"
            + td(f"<strong>{e(eixo)}</strong>")
            + td(num(quantidade), "center", quantidade)
            + td(brl(valor), "right", valor)
            + td(pct(share), "right", share)
            + "</tr>"
        )
    return tabela(
        [("Eixo", "left"), ("Programas", "center"), ("Liquidado", "right"), ("% do PPA", "right")],
        linhas,
        id_tabela="tabela-eixos",
        classes="table-compact",
        busca=False,
    )


def _ug_cards(relatorio: Relatorio, ugs_geradas: set[str]) -> str:
    maximo = max((ug.execucao_total for ug in relatorio.ugs.values()), default=1.0) or 1.0
    cards = []
    for ug in relatorio.ranking_ugs:
        link = f"ug_{ug.codigo}_{ug.slug}.html" if ug.codigo in ugs_geradas else ""
        classe = "ug-card active" if link else "ug-card disabled"
        tag = "a" if link else "div"
        href = f' href="{e(link)}"' if link else ""
        situacao = badge("Abrir relatório", "accent") if link else badge("Não gerado", "muted")
        largura = ug.execucao_total / maximo * 100
        cards.append(
            f'<{tag} class="{classe}"{href}>'
            f'<span class="ug-code">UG {e(ug.codigo)}</span>'
            f'<span class="ug-name">{e(ug.nome)}</span>'
            f'<span class="ug-value num">{brl_curto(ug.execucao_total)}</span>'
            f'<span class="ug-meta">{ug.n_programas_proprios} próprio(s) · '
            f"{ug.n_programas_compartilhados} compartilhado(s) · "
            f"{num(ug.n_indicadores)} ind. · {num(ug.n_acoes)} ações</span>"
            f'<span class="ug-bar"><span style="width:{largura:.1f}%"></span></span>'
            f'<span class="ug-foot"><span>{pct(ug.share_global)} do total</span>{situacao}</span>'
            f"</{tag}>"
        )
    return '<div class="ug-grid">' + "".join(cards) + "</div>"


def _cobertura_dono(item: CoberturaPrograma) -> str:
    if item.status == "excluido":
        return badge("Excluído", "muted")
    if item.status == "sem_ug":
        return badge("Sem UG", "bad")
    if item.dono:
        return f"UG {e(item.dono)}"
    return "—"


def _tabela_sem_indicador(relatorio: Relatorio) -> str:
    linhas = []
    for programa in relatorio.ppa.programas:
        if not programa.sem_indicador:
            continue
        item = relatorio.cobertura.get(programa.codigo)
        linhas.append(
            "<tr>"
            + td(f"<strong>{e(programa.codigo)}</strong>", "nowrap")
            + td(e(programa.nome))
            + td(e(programa.orgao))
            + td(_cobertura_dono(item) if item else "—")
            + td(num(len(programa.acoes)), "center", len(programa.acoes))
            + td(status_badge("Sem indicador"), "center")
            + "</tr>"
        )
    return tabela(
        [
            ("Código", "left"),
            ("Programa", "left"),
            ("Órgão no PPA", "left"),
            ("UG", "left"),
            ("Ações", "center"),
            ("Situação", "center"),
        ],
        linhas,
        id_tabela="tabela-sem-indicador",
        classes="table-compact",
        placeholder="Buscar programa...",
    )


def _tabela_sem_execucao(relatorio: Relatorio) -> str:
    linhas = []
    for programa in relatorio.ppa.programas:
        item = relatorio.cobertura.get(programa.codigo)
        if not item or item.status == "com_execucao":
            continue
        if item.status == "sem_execucao":
            situacao = badge("Sem execução (UG provisória)", "warn")
        elif item.status == "sem_ug":
            situacao = badge("Sem UG mapeada", "bad")
        else:
            situacao = badge("Excluído da revisão", "muted")
        linhas.append(
            "<tr>"
            + td(f"<strong>{e(programa.codigo)}</strong>", "nowrap")
            + td(e(programa.nome))
            + td(e(programa.orgao))
            + td(_cobertura_dono(item))
            + td(num(len(programa.indicadores)), "center", len(programa.indicadores))
            + td(num(len(programa.acoes)), "center", len(programa.acoes))
            + td(situacao, "center")
            + "</tr>"
        )
    return tabela(
        [
            ("Código", "left"),
            ("Programa", "left"),
            ("Órgão no PPA", "left"),
            ("UG", "left"),
            ("Indicadores", "center"),
            ("Ações", "center"),
            ("Situação", "center"),
        ],
        linhas,
        id_tabela="tabela-sem-execucao",
        classes="table-compact",
        placeholder="Buscar programa...",
    )


def _tabela_compartilhados(relatorio: Relatorio) -> str:
    linhas = []
    codigos = [
        codigo
        for codigo, item in relatorio.cobertura.items()
        if item.status == "com_execucao" and len(item.ugs_execucao) > 1
    ]
    for codigo in sorted(codigos):
        programa = relatorio.ppa.programa(codigo)
        if programa is None:
            continue
        item = relatorio.cobertura[codigo]
        total = item.execucao_total
        for ug in item.ugs_execucao:
            valor = relatorio.contas.execucao(codigo, ug).valor_liquido
            share = valor / total * 100 if total else 0.0
            linhas.append(
                "<tr>"
                + td(f"<strong>{e(codigo)}</strong>", "nowrap")
                + td(e(programa.nome))
                + td(f"UG {e(item.dono)}", "nowrap")
                + td(f"UG {e(ug)}", "nowrap")
                + td(brl(valor), "right", valor)
                + td(pct(share), "right", share)
                + "</tr>"
            )
    return tabela(
        [
            ("Programa", "left"),
            ("Nome", "left"),
            ("Dono", "left"),
            ("UG executora", "left"),
            ("Liquidado", "right"),
            ("% do programa", "right"),
        ],
        linhas,
        id_tabela="tabela-compartilhados",
        classes="table-compact",
        placeholder="Buscar programa...",
    )


def _tabela_fora_ppa(relatorio: Relatorio) -> str:
    linhas = []
    for item in relatorio.fora_ppa:
        for ug in item.ugs:
            linhas.append(
                "<tr>"
                + td(f"<strong>{e(item.codigo)}</strong>", "nowrap")
                + td(e(item.nome))
                + td(f"UG {e(ug.codigo)}")
                + td(brl(ug.valor), "right", ug.valor)
                + td(pct(ug.share), "right", ug.share)
                + "</tr>"
            )
    return tabela(
        [
            ("Programa", "left"),
            ("Nome", "left"),
            ("UG", "left"),
            ("Liquidado", "right"),
            ("% do programa", "right"),
        ],
        linhas,
        id_tabela="tabela-fora-ppa",
        classes="table-compact",
        busca=False,
    )


def _tabela_excluidos(relatorio: Relatorio) -> str:
    linhas = []
    for item in relatorio.excluidos:
        programa = item.programa
        linhas.append(
            "<tr>"
            + td(f"<strong>{e(programa.codigo)}</strong>", "nowrap")
            + td(e(programa.nome))
            + td(e(programa.orgao))
            + td(num(len(programa.indicadores)), "center", len(programa.indicadores))
            + td(num(len(programa.acoes)), "center", len(programa.acoes))
            + td(badge("Excluído", "muted"), "center")
            + "</tr>"
        )
    return tabela(
        [
            ("Código", "left"),
            ("Programa", "left"),
            ("Órgão no PPA", "left"),
            ("Indicadores", "center"),
            ("Ações", "center"),
            ("Situação", "center"),
        ],
        linhas,
        id_tabela="tabela-excluidos",
        classes="table-compact",
        busca=False,
    )


def _metas_nao_atingidas(relatorio: Relatorio) -> list[dict[str, str]]:
    itens: list[dict[str, str]] = []
    for programa in relatorio.ppa.programas:
        for indicador in programa.indicadores:
            res = relatorio.resultados.indicador(programa.codigo, indicador.n)
            if not res or not res.resultado:
                continue
            meta = res.meta_2026 or indicador.ref_2029
            valor = percentual(res.resultado, meta)
            if valor is None or valor >= 100:
                continue
            itens.append(
                {
                    "programa": programa.codigo,
                    "nome": programa.nome,
                    "item": f"Indicador {indicador.n}",
                    "descricao": indicador.nome,
                    "resultado": res.resultado,
                    "meta": meta,
                    "percentual": valor,
                    "situacao": "Não atingido",
                }
            )
        for acao in programa.acoes:
            res = relatorio.resultados.acao(programa.codigo, acao.num)
            if not res or not res.resultado:
                continue
            meta = parse_meta_acao(acao.meta_2026, acao.meta_2027_2029)
            valor = percentual_meta(
                res.resultado,
                meta.valor,
                tipo_meta=meta.tipo,
                meta_anual=res.meta_anual,
            )
            if valor is None or valor >= 100:
                continue
            itens.append(
                {
                    "programa": programa.codigo,
                    "nome": programa.nome,
                    "item": f"Ação {acao.num}",
                    "descricao": acao.nome,
                    "resultado": res.resultado,
                    "meta": acao.meta_2026 or res.meta_anual or "—",
                    "percentual": valor,
                    "situacao": "Não atingida",
                }
            )
    return itens


def _tabela_metas_nao_atingidas(relatorio: Relatorio) -> str:
    itens = _metas_nao_atingidas(relatorio)
    if not itens:
        return (
            '<div class="empty">Nenhuma meta não atingida registrada. '
            "A lista será preenchida quando os resultados de 2026 forem informados.</div>"
        )
    linhas = []
    for item in itens:
        linhas.append(
            "<tr>"
            + td(f"<strong>{e(item['programa'])}</strong>", "nowrap")
            + td(e(item["nome"]))
            + td(e(item["item"]))
            + td(e(item["descricao"]))
            + td(e(item["resultado"]), "right")
            + td(e(item["meta"]), "right")
            + td(pct(item["percentual"]), "right", item["percentual"])
            + td(badge(item["situacao"], "warn"), "center")
            + "</tr>"
        )
    return tabela(
        [
            ("Programa", "left"),
            ("Nome", "left"),
            ("Item", "left"),
            ("Indicador/ação", "left"),
            ("Resultado", "right"),
            ("Meta", "right"),
            ("% da meta", "right"),
            ("Situação", "center"),
        ],
        linhas,
        id_tabela="tabela-metas-nao-atingidas",
        classes="table-compact",
        placeholder="Buscar item...",
    )


def _qualidade_evidencias(relatorio: Relatorio) -> str:
    n_itens = relatorio.n_indicadores + relatorio.n_acoes
    n_resultados = relatorio.n_resultados_indicadores + relatorio.n_resultados_acoes
    n_evidencias = relatorio.n_evidencias
    return (
        '<div class="grid grid-4">'
        + kpi("Itens avaliáveis", str(n_itens), "indicadores + ações", "teal")
        + kpi("Com resultado", str(n_resultados), "resultados 2026 informados")
        + kpi("Evidências", str(n_evidencias), "arquivos/links registrados", "green")
        + kpi(
            "Pendentes",
            str(max(0, n_itens - n_resultados)),
            "dependem da devolutiva das UGs",
            "amber",
        )
        + "</div>"
        + '<div class="note info" style="margin-top:12px"><strong>Qualidade:</strong> '
        "só é avaliável depois que a UG informar resultado, análise e evidência. "
        "Nesta versão, o checklist por programa está na página de cada UG.</div>"
    )


def _qualidade_index(relatorio: Relatorio) -> str:
    n_meta = sum(
        1
        for programa in relatorio.ppa.programas
        for acao in programa.acoes
        if parse_meta_acao(acao.meta_2026, acao.meta_2027_2029).tipo == "percentual_plano"
    )
    return (
        '<div class="grid grid-2">'
        '<div class="note warn"><strong>UO:</strong> o código da UO no Consolidado não é único. '
        "A UG 004 tem duas UOs com código 001. O raio-x usa o nome normalizado da UO como "
        "chave.</div>"
        f'<div class="note warn"><strong>Metas:</strong> {n_meta} de '
        f"{len(relatorio.ppa.acoes)} ações têm meta 2026 em percentual do plano, não em "
        "quantidade física.</div>"
        '<div class="note warn"><strong>Execução:</strong> a base é de liquidações; não há '
        "empenhado/pago no Consolidado.</div>"
        '<div class="note info"><strong>Resultados:</strong> a base não tem resultados de 2026; '
        "o protótipo usa placeholders.</div>"
        f'<div class="note info"><strong>Cobertura:</strong> '
        f"{relatorio.n_programas_com_execucao} de {relatorio.n_programas} programas com "
        f"execução; {relatorio.n_programas_sem_execucao} sem execução "
        f"({relatorio.n_programas_sem_execucao_mapeado} com UG provisória, "
        f"{relatorio.n_sem_ug} sem UG, {relatorio.n_excluidos} excluídos).</div>"
        f'<div class="note info"><strong>Compartilhados:</strong> '
        f"{relatorio.n_compartilhados} programas aparecem em mais de uma UG.</div>"
        "</div>"
    )


def gerar_pagina_index(relatorio: Relatorio, ugs_geradas: set[str]) -> str:
    total_ugs = len(relatorio.ugs)
    kpis = (
        '<div class="kpi-grid">'
        + kpi("Programas do PPA", str(relatorio.n_programas), "2026-2029", "teal")
        + kpi("Indicadores", str(relatorio.n_indicadores), "referência atual e 2029", "teal")
        + kpi("Ações", str(relatorio.n_acoes), "meta 2026", "teal")
        + kpi("UGs", str(total_ugs), "unidades gestoras com execução", "teal")
        + kpi(
            "Liquidado 2026",
            brl_curto(relatorio.total_geral),
            f"{brl_curto(relatorio.total_fora_ppa)} fora do PPA",
            "green",
        )
        + kpi(
            "Com execução",
            f"{relatorio.n_programas_com_execucao}/{relatorio.n_programas}",
            "programas com linhas no Consolidado",
        )
        + kpi("Sem indicador", str(relatorio.n_sem_indicador), "programas do PPA", "amber")
        + kpi(
            "Sem execução",
            str(relatorio.n_programas_sem_execucao),
            f"{relatorio.n_programas_sem_execucao_mapeado} com UG provisória",
            "red",
        )
        + "</div>"
    )
    panorama = sec(
        "panorama",
        "Panorama",
        "O PPA no primeiro ano de execução",
        f'<div class="grid grid-2"><div class="card"><h3>Cobertura do PPA nas contas</h3>'
        f"{_stack_cobertura(relatorio)}"
        f'<p class="small muted">O programa 6200 (emenda parlamentar) está fora do PPA e '
        f"aparece apenas no anexo de execução. Total liquidado: {brl(relatorio.total_geral)}; "
        f"PPA: {brl(relatorio.total_ppa)}.</p></div>"
        f'<div class="card"><h3>Programas por situação</h3>{_tabela_cobertura(relatorio)}</div>'
        "</div>",
        "87 programas, 247 indicadores e 306 ações. 74 programas têm execução; 13 não têm. "
        "O elo é o campo Programa de governo.",
    )
    cobertura = sec(
        "cobertura",
        "Cobertura",
        "Onde o PPA encontra a execução",
        '<div class="grid grid-2">'
        '<div class="card"><h3>Execução por eixo</h3>'
        + barras([(eixo, valor) for eixo, valor, _ in _execucao_por_eixo(relatorio)], limite=8)
        + "</div>"
        '<div class="card"><h3>Programas por eixo</h3>'
        + _tabela_eixos(relatorio)
        + "</div></div>",
        "A execução por eixo usa o total do programa uma única vez, mesmo quando ele é "
        "compartilhado entre UGs.",
    )
    ranking = sec(
        "ranking",
        "Ranking",
        "Execução liquidada por UG",
        '<div class="card"><h3>Top 10</h3>'
        + barras(
            [(f"UG {ug.codigo} — {ug.nome}", ug.execucao_total) for ug in relatorio.ranking_ugs[:10]],
            limite=10,
        )
        + "</div>",
        "A lista completa das 35 UGs está no mapa abaixo. Todas as UGs estão detalhadas "
        "nesta versão.",
    )
    ugs = sec(
        "ugs",
        "Mapa de UGs",
        f"{total_ugs} unidades gestoras",
        _ug_cards(relatorio, ugs_geradas),
        "Cada cartão resume programas, indicadores, ações e execução. O detalhe completo é "
        "gerado por UG.",
    )
    transversais = sec(
        "transversais",
        "Visões transversais",
        "Exceções, lacunas e compartilhamentos",
        '<details class="programa" open><summary><span class="prog-id">20</span>'
        '<span class="prog-heading"><h3>Programas sem indicador</h3>'
        '<span class="prog-badges">'
        + badge("Avaliar por ações e análise qualitativa", "warn")
        + "</span></span><span></span><span></span></summary>"
        '<div class="prog-body">'
        + _tabela_sem_indicador(relatorio)
        + "</div></details>"
        '<details class="programa" open><summary><span class="prog-id">13</span>'
        '<span class="prog-heading"><h3>Programas sem execução</h3>'
        '<span class="prog-badges">'
        + badge("7 com UG provisória", "warn")
        + badge("4 sem UG", "bad")
        + badge("2 excluídos", "muted")
        + "</span></span><span></span><span></span></summary>"
        '<div class="prog-body">'
        + _tabela_sem_execucao(relatorio)
        + "</div></details>"
        '<details class="programa" open><summary><span class="prog-id">4</span>'
        '<span class="prog-heading"><h3>Programas compartilhados</h3>'
        '<span class="prog-badges">'
        + badge("Dono provisório", "info")
        + "</span></span><span></span><span></span></summary>"
        '<div class="prog-body">'
        + _tabela_compartilhados(relatorio)
        + "</div></details>"
        '<details class="programa" open><summary><span class="prog-id">6200</span>'
        '<span class="prog-heading"><h3>Fora do PPA</h3>'
        '<span class="prog-badges">'
        + badge("Anexo de execução", "muted")
        + "</span></span><span></span><span></span></summary>"
        '<div class="prog-body">'
        + _tabela_fora_ppa(relatorio)
        + "</div></details>"
        '<details class="programa"><summary><span class="prog-id">2</span>'
        '<span class="prog-heading"><h3>Excluídos da revisão do PPA</h3>'
        '<span class="prog-badges">'
        + badge("Não avaliar", "muted")
        + "</span></span><span></span><span></span></summary>"
        '<div class="prog-body">'
        + _tabela_excluidos(relatorio)
        + "</div></details>"
        '<details class="programa" open><summary><span class="prog-id">0</span>'
        '<span class="prog-heading"><h3>Metas não atingidas</h3>'
        '<span class="prog-badges">'
        + badge("Aguardando resultados", "muted")
        + "</span></span><span></span><span></span></summary>"
        '<div class="prog-body">'
        + _tabela_metas_nao_atingidas(relatorio)
        + "</div></details>"
        '<div style="margin-top:14px">'
        + _qualidade_evidencias(relatorio)
        + "</div>",
        "As listas usam o mapa provisório do DEFINICAO do RAM. Validar antes de gerar as 35 UGs.",
    )
    qualidade = sec(
        "qualidade",
        "Notas técnicas",
        "Qualidade dos dados",
        _qualidade_index(relatorio)
        + '<div style="margin-top:14px">'
        + _alertas_lista(relatorio.alertas_globais, link_programa=False)
        + "</div>",
        "Limitações da base atual e alertas globais.",
    )
    metodologia = sec(
        "metodologia",
        "Método",
        "Como o raio-x foi calculado",
        _metodologia(relatorio),
    )
    hero_html = hero(
        "Raio-X Técnico do PPA 2026-2029",
        "Panorama, cobertura e mapa das 35 UGs · versão completa",
        "RX",
        arquivo_contas=relatorio.contas.arquivo.name,
        gerado_em=relatorio.gerado_em,
        acoes='<a class="btn" href="#ugs">Mapa de UGs</a>',
        link_indice=False,
    )
    topbar_html = topbar(
        [
            ("panorama", "Panorama"),
            ("cobertura", "Cobertura"),
            ("ranking", "Ranking"),
            ("ugs", "Mapa de UGs"),
            ("transversais", "Transversais"),
            ("qualidade", "Qualidade"),
            ("metodologia", "Metodologia"),
        ]
    )
    corpo = kpis + panorama + cobertura + ranking + ugs + transversais + qualidade + metodologia
    return layout(
        "Raio-X Técnico do PPA 2026-2029",
        hero_html,
        topbar_html,
        corpo,
    )


def gerar_html_index(
    relatorio: Relatorio,
    destino: Path | str,
    ugs_geradas: set[str] | None = None,
) -> Path:
    pasta = Path(destino)
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / "index.html"
    arquivo.write_text(
        gerar_pagina_index(relatorio, ugs_geradas or set()),
        encoding="utf-8",
    )
    return arquivo
