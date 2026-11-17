"""Modelo analitico do raio-x: cobertura, programas por UG, alertas e resumos."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .perfil import PERFIL_2026, PerfilAno
from .dados import Contas, Execucao, PPA, Programa
from .resultados import Resultados
from .texto import (
    formatar_brl_curto,
    formatar_pct,
    parse_meta_acao,
    texto,
)

SEVERIDADES = {"alta": 0, "media": 1, "baixa": 2, "info": 3}


@dataclass
class Alerta:
    severidade: str
    tipo: str
    mensagem: str
    codigo_programa: str = ""
    codigo_ug: str = ""
    acao: str = ""

    @property
    def ordem(self) -> int:
        return SEVERIDADES.get(self.severidade, 9)


@dataclass
class UGRef:
    codigo: str
    nome: str
    valor: float
    share: float


@dataclass
class ProgramaUG:
    programa: Programa
    ug: str
    dono: str
    execucao: Execucao
    execucao_global: float
    outras_ugs: list[UGRef]
    compartilhado: bool
    vinculo_provisorio: bool
    sem_execucao: bool
    sem_indicador: bool
    alertas: list[Alerta] = field(default_factory=list)
    n_acoes_meta_percentual: int = 0
    n_acoes_sem_meta: int = 0
    n_indicadores_sem_ref: int = 0
    n_resultados_indicadores: int = 0
    n_resultados_acoes: int = 0

    @property
    def codigo(self) -> str:
        return self.programa.codigo

    @property
    def nome(self) -> str:
        return self.programa.nome

    @property
    def n_indicadores(self) -> int:
        return len(self.programa.indicadores)

    @property
    def n_acoes(self) -> int:
        return len(self.programa.acoes)

    @property
    def share_ug(self) -> float:
        return 0.0

    @property
    def share_programa(self) -> float:
        if not self.execucao_global:
            return 0.0
        return self.execucao.valor_liquido / self.execucao_global * 100

    @property
    def resultados_pendentes(self) -> int:
        return (
            self.n_indicadores
            + self.n_acoes
            - self.n_resultados_indicadores
            - self.n_resultados_acoes
        )


@dataclass
class ResumoUO:
    chave: str
    nome: str
    nome_oficial: str
    codigos: list[str]
    valor: float
    share_ug: float
    linhas: int
    programas: list[ProgramaUG] = field(default_factory=list)


@dataclass
class ResumoUG:
    codigo: str
    nome: str
    slug: str
    uos: list[ResumoUO]
    programas_proprios: list[ProgramaUG]
    programas_compartilhados: list[ProgramaUG]
    execucao_total: float
    execucao_realizado: float
    execucao_anulado: float
    linhas: int
    share_global: float
    n_indicadores_proprios: int
    n_indicadores_compartilhados: int
    n_acoes_proprios: int
    n_acoes_compartilhados: int
    n_sem_indicador: int
    n_sem_execucao: int
    n_compartilhados: int
    n_resultados_indicadores: int
    n_resultados_acoes: int
    alertas: list[Alerta] = field(default_factory=list)

    @property
    def programas(self) -> list[ProgramaUG]:
        return self.programas_proprios + self.programas_compartilhados

    @property
    def n_programas_proprios(self) -> int:
        return len(self.programas_proprios)

    @property
    def n_programas_compartilhados(self) -> int:
        return len(self.programas_compartilhados)

    @property
    def n_indicadores(self) -> int:
        return self.n_indicadores_proprios + self.n_indicadores_compartilhados

    @property
    def n_acoes(self) -> int:
        return self.n_acoes_proprios + self.n_acoes_compartilhados

    @property
    def n_resultados(self) -> int:
        return self.n_resultados_indicadores + self.n_resultados_acoes

    @property
    def resultados_pendentes(self) -> int:
        return self.n_indicadores + self.n_acoes - self.n_resultados

    def contar_alertas(self, severidade: str) -> int:
        return sum(1 for alerta in self.alertas if alerta.severidade == severidade)


@dataclass
class LinhaExecucaoDetalhe:
    programa: str
    nome_programa: str
    acao_loa: str
    nome_acao_loa: str
    natureza: str
    valor: float
    valor_acao: float
    pct_acao: float
    pct_programa: float
    pct_ug: float
    linhas: int


@dataclass
class CoberturaPrograma:
    programa: Programa
    ugs_execucao: list[str]
    dono: str
    status: str
    vinculo_provisorio: bool
    execucao_total: float

    @property
    def codigo(self) -> str:
        return self.programa.codigo

    @property
    def nome(self) -> str:
        return self.programa.nome


@dataclass
class ForaPPA:
    codigo: str
    nome: str
    ugs: list[UGRef]
    valor: float
    linhas: int


@dataclass
class Relatorio:
    ppa: PPA
    contas: Contas
    perfil: PerfilAno
    resultados: Resultados
    ugs: dict[str, ResumoUG]
    cobertura: dict[str, CoberturaPrograma]
    sem_ug: list[CoberturaPrograma]
    excluidos: list[CoberturaPrograma]
    fora_ppa: list[ForaPPA]
    alertas_globais: list[Alerta]
    gerado_em: datetime
    fontes: dict[str, Path] = field(default_factory=dict)

    @property
    def n_programas(self) -> int:
        return len(self.ppa.programas)

    @property
    def n_indicadores(self) -> int:
        return len(self.ppa.indicadores)

    @property
    def n_acoes(self) -> int:
        return len(self.ppa.acoes)

    @property
    def n_programas_com_execucao(self) -> int:
        return sum(1 for c in self.cobertura.values() if c.status == "com_execucao")

    @property
    def n_programas_sem_execucao_mapeado(self) -> int:
        return sum(1 for c in self.cobertura.values() if c.status == "sem_execucao")

    @property
    def n_programas_sem_execucao(self) -> int:
        return sum(1 for c in self.cobertura.values() if c.status != "com_execucao")

    @property
    def n_sem_ug(self) -> int:
        return sum(1 for c in self.cobertura.values() if c.status == "sem_ug")

    @property
    def n_excluidos(self) -> int:
        return sum(1 for c in self.cobertura.values() if c.status == "excluido")

    @property
    def n_sem_indicador(self) -> int:
        return sum(1 for p in self.ppa.programas if p.sem_indicador)

    @property
    def n_compartilhados(self) -> int:
        return sum(1 for c in self.cobertura.values() if len(c.ugs_execucao) > 1)

    @property
    def total_ppa(self) -> float:
        return sum(
            self.contas.programa_total[codigo].valor_liquido
            for codigo in self.ppa.por_codigo
            if codigo in self.contas.programa_total
        )

    @property
    def total_fora_ppa(self) -> float:
        return sum(item.valor for item in self.fora_ppa)

    @property
    def total_geral(self) -> float:
        return self.contas.total.valor_liquido

    @property
    def ranking_ugs(self) -> list[ResumoUG]:
        return sorted(
            self.ugs.values(),
            key=lambda ug: (-ug.execucao_total, ug.codigo),
        )

    @property
    def n_resultados_indicadores(self) -> int:
        return sum(
            1
            for programa in self.ppa.programas
            for indicador in programa.indicadores
            if self.resultados.indicador(programa.codigo, indicador.n)
            and _resultado_preenchido(
                self.resultados.indicador(programa.codigo, indicador.n).resultado
            )
        )

    @property
    def n_resultados_acoes(self) -> int:
        return sum(
            1
            for programa in self.ppa.programas
            for acao in programa.acoes
            if self.resultados.acao(programa.codigo, acao.num)
            and _resultado_preenchido(self.resultados.acao(programa.codigo, acao.num).resultado)
        )

    @property
    def n_evidencias(self) -> int:
        return len(self.resultados.evidencias)

    def ug(self, codigo_ug: str) -> ResumoUG | None:
        return self.ugs.get(texto(codigo_ug).zfill(3))


def _resultado_preenchido(valor: str) -> bool:
    return bool(texto(valor)) and texto(valor) not in {"-", "—", "PENDENTE", "NÃO INFORMADO"}


def _alertas_programa(
    programa: Programa,
    ug: str,
    execucao: Execucao,
    outras_ugs: list[UGRef],
    execucao_global: float,
    vinculo_provisorio: bool,
    resultados: Resultados,
    perfil: PerfilAno,
) -> list[Alerta]:
    alertas: list[Alerta] = []
    if execucao.linhas == 0:
        alertas.append(
            Alerta(
                "alta",
                "programa_sem_execucao",
                f"Programa sem execução registrada no Consolidado {perfil.ano}.",
                codigo_programa=programa.codigo,
                codigo_ug=ug,
            )
        )
    elif execucao.valor_liquido <= 0:
        alertas.append(
            Alerta(
                "alta",
                "execucao_anulada",
                "Programa com execução líquida nula ou negativa; conferir anulações.",
                codigo_programa=programa.codigo,
                codigo_ug=ug,
            )
        )
    if programa.sem_indicador:
        alertas.append(
            Alerta(
                "media",
                "programa_sem_indicador",
                "Programa sem indicador no PPA; avaliar pelas ações e pela análise qualitativa.",
                codigo_programa=programa.codigo,
                codigo_ug=ug,
            )
        )
    if outras_ugs:
        partes = ", ".join(
            f"UG {outra.codigo} ({formatar_brl_curto(outra.valor)}, {formatar_pct(outra.share)})"
            for outra in outras_ugs
        )
        alertas.append(
            Alerta(
                "info",
                "programa_compartilhado",
                f"Programa compartilhado. Execução total {formatar_brl_curto(execucao_global)}; "
                f"outras UGs: {partes}.",
                codigo_programa=programa.codigo,
                codigo_ug=ug,
            )
        )
    if vinculo_provisorio:
        alertas.append(
            Alerta(
                "media",
                "vinculo_provisorio",
                "Vínculo PPA↔UG provisório (mapa do DEFINICAO do RAM); validar com a área técnica.",
                codigo_programa=programa.codigo,
                codigo_ug=ug,
            )
        )
    sem_meta = [a.num for a in programa.acoes if not texto(a.meta_ano)]
    if sem_meta:
        alertas.append(
            Alerta(
                "media",
                "acao_sem_meta",
                f"Ação(ões) sem {perfil.meta_ano_label}: " + ", ".join(sem_meta) + ".",
                codigo_programa=programa.codigo,
                codigo_ug=ug,
            )
        )
    metas_percentuais = [
        a
        for a in programa.acoes
        if parse_meta_acao(a.meta_ano, a.meta_bloco).tipo == "percentual_plano"
    ]
    if metas_percentuais:
        alertas.append(
            Alerta(
                "info",
                "meta_percentual",
                f"{len(metas_percentuais)} de {len(programa.acoes)} ações usam meta "
                f"{perfil.meta_ano_label} em percentual, não meta física anual. A coleta deve "
                "informar a meta anual em quantidade ou o resultado em % do plano/bloco.",
                codigo_programa=programa.codigo,
                codigo_ug=ug,
            )
        )
    sem_ref = [i for i in programa.indicadores if not texto(i.ref_atual) or i.ref_atual == "-"]
    if sem_ref:
        alertas.append(
            Alerta(
                "baixa",
                "indicador_sem_referencia",
                f"{len(sem_ref)} indicador(es) sem referência atual no PPA.",
                codigo_programa=programa.codigo,
                codigo_ug=ug,
            )
        )
    total_itens = len(programa.indicadores) + len(programa.acoes)
    preenchidos = sum(
        1
        for i in programa.indicadores
        if resultados.indicador(programa.codigo, i.n)
        and _resultado_preenchido(resultados.indicador(programa.codigo, i.n).resultado)
    ) + sum(
        1
        for a in programa.acoes
        if resultados.acao(programa.codigo, a.num)
        and _resultado_preenchido(resultados.acao(programa.codigo, a.num).resultado)
    )
    if total_itens and preenchidos < total_itens:
        alertas.append(
            Alerta(
                "info",
                "resultado_pendente",
                f"{total_itens - preenchidos} de {total_itens} indicadores/ações sem resultado "
                f"{perfil.ano} informado.",
                codigo_programa=programa.codigo,
                codigo_ug=ug,
            )
        )
    return alertas


def _programa_ug(
    programa: Programa,
    ug: str,
    dono: str,
    exec_ugs: list[str],
    contas: Contas,
    resultados: Resultados,
    vinculo_provisorio: bool,
    perfil: PerfilAno,
) -> ProgramaUG:
    execucao = contas.execucao(programa.codigo, ug)
    execucao_global = contas.total_programa(programa.codigo)
    outras: list[UGRef] = []
    for outra in exec_ugs:
        if outra == ug:
            continue
        valor = contas.execucao(programa.codigo, outra).valor_liquido
        share = valor / execucao_global * 100 if execucao_global else 0.0
        outras.append(UGRef(outra, perfil.nome_ug(outra), valor, share))
    alertas = _alertas_programa(
        programa,
        ug,
        execucao,
        outras,
        execucao_global,
        vinculo_provisorio,
        resultados,
        perfil,
    )
    meta_percentual = sum(
        1
        for a in programa.acoes
        if parse_meta_acao(a.meta_ano, a.meta_bloco).tipo == "percentual_plano"
    )
    sem_meta = sum(1 for a in programa.acoes if not texto(a.meta_ano))
    sem_ref = sum(
        1 for i in programa.indicadores if not texto(i.ref_atual) or i.ref_atual == "-"
    )
    resultados_ind = sum(
        1
        for i in programa.indicadores
        if resultados.indicador(programa.codigo, i.n)
        and _resultado_preenchido(resultados.indicador(programa.codigo, i.n).resultado)
    )
    resultados_acao = sum(
        1
        for a in programa.acoes
        if resultados.acao(programa.codigo, a.num)
        and _resultado_preenchido(resultados.acao(programa.codigo, a.num).resultado)
    )
    return ProgramaUG(
        programa=programa,
        ug=ug,
        dono=dono,
        execucao=execucao,
        execucao_global=execucao_global,
        outras_ugs=outras,
        compartilhado=len(exec_ugs) > 1,
        vinculo_provisorio=vinculo_provisorio,
        sem_execucao=execucao.linhas == 0,
        sem_indicador=programa.sem_indicador,
        alertas=alertas,
        n_acoes_meta_percentual=meta_percentual,
        n_acoes_sem_meta=sem_meta,
        n_indicadores_sem_ref=sem_ref,
        n_resultados_indicadores=resultados_ind,
        n_resultados_acoes=resultados_acao,
    )


def _resumo_uo(
    ug: str,
    chave: str,
    uo,
    programas: list[ProgramaUG],
    total_ug: float,
) -> ResumoUO:
    programas_uo = [p for p in programas if p.execucao.por_uo.get(chave, 0.0)]
    programas_uo.sort(key=lambda p: (-p.execucao.por_uo.get(chave, 0.0), p.codigo))
    valor = uo.execucao.valor_liquido
    return ResumoUO(
        chave=chave,
        nome=uo.nome,
        nome_oficial=uo.nome_oficial,
        codigos=sorted(uo.codigos),
        valor=valor,
        share_ug=valor / total_ug * 100 if total_ug else 0.0,
        linhas=uo.execucao.linhas,
        programas=programas_uo,
    )


def _alertas_ug(
    ug: str,
    nome: str,
    uos: list[ResumoUO],
    programas: list[ProgramaUG],
    total: float,
    resultados: Resultados,
    perfil: PerfilAno,
) -> list[Alerta]:
    alertas: list[Alerta] = []
    codigos_uo: dict[str, list[str]] = defaultdict(list)
    for uo in uos:
        for cod in uo.codigos:
            codigos_uo[cod].append(uo.nome_oficial)
    duplicados = {cod: nomes for cod, nomes in codigos_uo.items() if len(nomes) > 1}
    if duplicados:
        detalhes = "; ".join(
            f"cód. {cod}: {', '.join(nomes)}" for cod, nomes in sorted(duplicados.items())
        )
        alertas.append(
            Alerta(
                "media",
                "uo_codigo_duplicado",
                "O código de UO no Consolidado não é único; a chave usada é o nome da UO. "
                f"Casos: {detalhes}.",
                codigo_ug=ug,
            )
        )
    if total <= 0:
        alertas.append(
            Alerta(
                "alta",
                "ug_sem_execucao",
                f"UG sem execução líquida registrada em {perfil.ano}.",
                codigo_ug=ug,
            )
        )
    n_resultados = sum(p.n_resultados_indicadores + p.n_resultados_acoes for p in programas)
    n_itens = sum(p.n_indicadores + p.n_acoes for p in programas)
    n_pendentes = max(0, n_itens - n_resultados)
    if n_itens and n_pendentes:
        mensagem = (
            f"Nenhum resultado de indicador ou ação foi informado para esta UG em {perfil.ano}; "
            "o raio-x está em modo de prévia."
            if n_resultados == 0
            else f"{n_pendentes} de {n_itens} indicadores/ações sem resultado {perfil.ano} informado."
        )
        alertas.append(Alerta("info", "resultado_pendente", mensagem, codigo_ug=ug))
    if not resultados.evidencias:
        alertas.append(
            Alerta(
                "info",
                "evidencias_pendentes_ug",
                "Nenhuma evidência registrada para esta UG.",
                codigo_ug=ug,
            )
        )
    compartilhados = [p for p in programas if p.compartilhado]
    if compartilhados:
        detalhes = "; ".join(
            f"{p.codigo} (outras UGs: "
            + ", ".join(f"UG {outra.codigo}" for outra in p.outras_ugs)
            + ")"
            for p in compartilhados
        )
        alertas.append(
            Alerta(
                "info",
                "programa_compartilhado",
                f"Programas compartilhados: {detalhes}. A parte de cada UG está na seção "
                "Execução.",
                codigo_ug=ug,
            )
        )
    metas = sum(p.n_acoes_meta_percentual for p in programas)
    n_acoes = sum(p.n_acoes for p in programas)
    if metas:
        alertas.append(
            Alerta(
                "info",
                "meta_percentual",
                f"{metas} de {n_acoes} ações usam meta {perfil.meta_ano_label} em percentual, "
                "não meta física anual. A coleta deve informar a meta anual ou o resultado em "
                "% do plano/bloco.",
                codigo_ug=ug,
            )
        )
    tipos_agregados = {"meta_percentual", "resultado_pendente", "programa_compartilhado"}
    for programa in programas:
        alertas.extend(
            alerta for alerta in programa.alertas if alerta.tipo not in tipos_agregados
        )
    vistos = set()
    unicos: list[Alerta] = []
    for alerta in alertas:
        chave = (alerta.severidade, alerta.tipo, alerta.codigo_programa, alerta.codigo_ug, alerta.mensagem)
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(alerta)
    return sorted(unicos, key=lambda a: (a.ordem, a.codigo_programa, a.mensagem))


def construir_relatorio(
    ppa: PPA,
    contas: Contas,
    resultados: Resultados | None = None,
    fontes: dict[str, Path] | None = None,
    perfil: PerfilAno | None = None,
) -> Relatorio:
    perfil = perfil or PERFIL_2026
    resultados = resultados if resultados is not None else Resultados()
    cobertura: dict[str, CoberturaPrograma] = {}
    programas_por_ug: dict[str, list[ProgramaUG]] = defaultdict(list)
    sem_ug: list[CoberturaPrograma] = []
    excluidos: list[CoberturaPrograma] = []

    for programa in ppa.programas:
        codigo = programa.codigo
        if codigo in perfil.programas_excluidos:
            item = CoberturaPrograma(
                programa=programa,
                ugs_execucao=[],
                dono="",
                status="excluido",
                vinculo_provisorio=False,
                execucao_total=0.0,
            )
            cobertura[codigo] = item
            excluidos.append(item)
            continue

        exec_ugs = contas.ugs_do_programa(codigo)
        provisorio = perfil.programas_sem_execucao.get(codigo)
        if exec_ugs:
            dono = perfil.donos_compartilhados.get(codigo)
            vinculo_provisorio = False
            if dono is None:
                dono = provisorio[0] if provisorio else min(exec_ugs)
                vinculo_provisorio = bool(provisorio)
            if dono not in exec_ugs:
                dono = min(exec_ugs)
                vinculo_provisorio = True
            for ug in exec_ugs:
                programas_por_ug[ug].append(
                    _programa_ug(
                        programa,
                        ug,
                        dono,
                        exec_ugs,
                        contas,
                        resultados,
                        vinculo_provisorio,
                        perfil,
                    )
                )
            cobertura[codigo] = CoberturaPrograma(
                programa=programa,
                ugs_execucao=exec_ugs,
                dono=dono,
                status="com_execucao",
                vinculo_provisorio=vinculo_provisorio,
                execucao_total=contas.total_programa(codigo),
            )
            continue

        if codigo in perfil.programas_sem_ug:
            item = CoberturaPrograma(
                programa=programa,
                ugs_execucao=[],
                dono="",
                status="sem_ug",
                vinculo_provisorio=False,
                execucao_total=0.0,
            )
            cobertura[codigo] = item
            sem_ug.append(item)
            continue

        if provisorio:
            dono = provisorio[0]
            programas_por_ug[dono].append(
                _programa_ug(
                    programa,
                    dono,
                    dono,
                    [],
                    contas,
                    resultados,
                    True,
                    perfil,
                )
            )
            cobertura[codigo] = CoberturaPrograma(
                programa=programa,
                ugs_execucao=[],
                dono=dono,
                status="sem_execucao",
                vinculo_provisorio=True,
                execucao_total=0.0,
            )
            continue

        item = CoberturaPrograma(
            programa=programa,
            ugs_execucao=[],
            dono="",
            status="sem_ug",
            vinculo_provisorio=False,
            execucao_total=0.0,
        )
        cobertura[codigo] = item
        sem_ug.append(item)

    ugs: dict[str, ResumoUG] = {}
    for codigo_ug, ug_contas in contas.ugs.items():
        todos = programas_por_ug.get(codigo_ug, [])
        proprios = [p for p in todos if p.dono == codigo_ug]
        compartilhados = [p for p in todos if p.dono != codigo_ug]
        proprios.sort(key=lambda p: (p.sem_execucao, -p.execucao.valor_liquido, p.codigo))
        compartilhados.sort(key=lambda p: (-p.execucao.valor_liquido, p.codigo))
        total = ug_contas.execucao.valor_liquido
        uos = [
            _resumo_uo(codigo_ug, chave, uo, proprios + compartilhados, total)
            for chave, uo in ug_contas.uos.items()
        ]
        uos.sort(key=lambda uo: (-uo.valor, uo.nome_oficial))
        n_ind_proprios = sum(p.n_indicadores for p in proprios)
        n_ind_compartilhados = sum(p.n_indicadores for p in compartilhados)
        n_acoes_proprios = sum(p.n_acoes for p in proprios)
        n_acoes_compartilhados = sum(p.n_acoes for p in compartilhados)
        n_resultados_ind = sum(p.n_resultados_indicadores for p in proprios + compartilhados)
        n_resultados_acoes = sum(p.n_resultados_acoes for p in proprios + compartilhados)
        alertas = _alertas_ug(
            codigo_ug,
            perfil.nome_ug(codigo_ug),
            uos,
            proprios + compartilhados,
            total,
            resultados,
            perfil,
        )
        ugs[codigo_ug] = ResumoUG(
            codigo=codigo_ug,
            nome=perfil.nome_ug(codigo_ug),
            slug=perfil.slug_ug(codigo_ug),
            uos=uos,
            programas_proprios=proprios,
            programas_compartilhados=compartilhados,
            execucao_total=total,
            execucao_realizado=ug_contas.execucao.valor_realizado,
            execucao_anulado=ug_contas.execucao.valor_anulado,
            linhas=ug_contas.execucao.linhas,
            share_global=total / contas.total.valor_liquido * 100 if contas.total.valor_liquido else 0.0,
            n_indicadores_proprios=n_ind_proprios,
            n_indicadores_compartilhados=n_ind_compartilhados,
            n_acoes_proprios=n_acoes_proprios,
            n_acoes_compartilhados=n_acoes_compartilhados,
            n_sem_indicador=sum(1 for p in proprios if p.sem_indicador),
            n_sem_execucao=sum(1 for p in proprios if p.sem_execucao),
            n_compartilhados=sum(1 for p in proprios + compartilhados if p.compartilhado),
            n_resultados_indicadores=n_resultados_ind,
            n_resultados_acoes=n_resultados_acoes,
            alertas=alertas,
        )

    fora_ppa: list[ForaPPA] = []
    for codigo, exec_total in contas.programa_total.items():
        if codigo in ppa.por_codigo:
            continue
        ugs_ref: list[UGRef] = []
        for ug in contas.ugs_do_programa(codigo):
            valor = contas.execucao(codigo, ug).valor_liquido
            share = valor / exec_total.valor_liquido * 100 if exec_total.valor_liquido else 0.0
            ugs_ref.append(UGRef(ug, perfil.nome_ug(ug), valor, share))
        ugs_ref.sort(key=lambda u: -u.valor)
        fora_ppa.append(
            ForaPPA(
                codigo=codigo,
                nome=contas.programa_nome.get(codigo, codigo),
                ugs=ugs_ref,
                valor=exec_total.valor_liquido,
                linhas=exec_total.linhas,
            )
        )
    fora_ppa.sort(key=lambda f: -f.valor)

    alertas_globais: list[Alerta] = []
    if fora_ppa:
        nomes = ", ".join(f"{f.codigo} — {f.nome}" for f in fora_ppa)
        alertas_globais.append(
            Alerta(
                "info",
                "fora_ppa",
                f"Programa(s) com execução fora do PPA: {nomes}. Incluir apenas no anexo de execução.",
            )
        )
    if sem_ug:
        nomes = ", ".join(f"{i.codigo}" for i in sem_ug)
        alertas_globais.append(
            Alerta(
                "media",
                "programas_sem_ug",
                f"{len(sem_ug)} programa(s) do PPA sem UG mapeada: {nomes}.",
            )
        )
    if excluidos:
        nomes = ", ".join(f"{i.codigo}" for i in excluidos)
        alertas_globais.append(
            Alerta(
                "info",
                "programas_excluidos",
                f"{len(excluidos)} programa(s) excluído(s) da revisão do PPA: {nomes}.",
            )
        )
    n_sem_exec = sum(1 for c in cobertura.values() if c.status == "sem_execucao")
    if n_sem_exec:
        alertas_globais.append(
            Alerta(
                "media",
                "programas_sem_execucao_mapeados",
                f"{n_sem_exec} programa(s) sem execução com UG provisória. Validar o mapa PPA↔UG.",
            )
        )
    n_meta_percentual = sum(
        1
        for p in ppa.programas
        for a in p.acoes
        if parse_meta_acao(a.meta_ano, a.meta_bloco).tipo == "percentual_plano"
    )
    if n_meta_percentual:
        alertas_globais.append(
            Alerta(
                "media",
                "acoes_meta_percentual",
                f"{n_meta_percentual} de {len(ppa.acoes)} ações têm meta "
                f"{perfil.meta_ano_label} em percentual do plano/bloco. Não é possível calcular "
                "execução física contra a meta anual sem a meta física informada pela UG.",
            )
        )
    n_sem_ref = sum(
        1
        for p in ppa.programas
        for i in p.indicadores
        if not texto(i.ref_atual) or i.ref_atual == "-"
    )
    if n_sem_ref:
        alertas_globais.append(
            Alerta(
                "baixa",
                "indicadores_sem_referencia",
                f"{n_sem_ref} indicador(es) sem referência atual no PPA.",
            )
        )
    alertas_globais.append(
        Alerta(
            "media",
            "execucao_liquidacao",
            "A base de contas disponível é de liquidações (Valor R$), com anulados negativos. "
            "Empenhado e pago não estão no Consolidado; o raio-x mostra liquidado líquido.",
        )
    )
    alertas_globais.append(
        Alerta(
            "info",
            "resultados_pendentes",
            f"A base não contém resultados de {perfil.ano}. O relatório usa placeholders e "
            "será alimentado pela camada de resultados/evidências.",
        )
    )

    return Relatorio(
        ppa=ppa,
        contas=contas,
        perfil=perfil,
        resultados=resultados,
        ugs=ugs,
        cobertura=cobertura,
        sem_ug=sem_ug,
        excluidos=excluidos,
        fora_ppa=fora_ppa,
        alertas_globais=sorted(alertas_globais, key=lambda a: (a.ordem, a.tipo)),
        gerado_em=datetime.now(),
        fontes=fontes or {"ppa": perfil.ppa_path, "contas": contas.arquivo},
    )


def detalhe_execucao_programa(
    programa_ug: ProgramaUG,
    total_ug: float,
) -> list[LinhaExecucaoDetalhe]:
    execucao = programa_ug.execucao
    if not execucao.linhas:
        return []
    total_programa = programa_ug.execucao_global
    linhas: list[LinhaExecucaoDetalhe] = []
    for (acao, natureza), valor in execucao.por_acao_natureza.items():
        total_acao = execucao.por_acao_loa.get(acao, 0.0)
        linhas.append(
            LinhaExecucaoDetalhe(
                programa=programa_ug.codigo,
                nome_programa=programa_ug.nome,
                acao_loa=acao,
                nome_acao_loa=execucao.nomes_acao_loa.get(acao, acao),
                natureza=natureza,
                valor=valor,
                valor_acao=total_acao,
                pct_acao=valor / total_acao * 100 if total_acao else 0.0,
                pct_programa=valor / total_programa * 100 if total_programa else 0.0,
                pct_ug=valor / total_ug * 100 if total_ug else 0.0,
                linhas=execucao.linhas_acao_natureza.get((acao, natureza), 0),
            )
        )
    linhas.sort(key=lambda linha: (-linha.valor_acao, linha.acao_loa, -linha.valor, linha.natureza))
    return linhas


def detalhe_execucao_ug(resumo: ResumoUG) -> list[LinhaExecucaoDetalhe]:
    linhas: list[LinhaExecucaoDetalhe] = []
    for programa_ug in resumo.programas:
        linhas.extend(detalhe_execucao_programa(programa_ug, resumo.execucao_total))
    return linhas


def insights_ug(resumo: ResumoUG, relatorio: Relatorio) -> list[str]:
    insights: list[str] = []
    com_execucao = [p for p in resumo.programas if not p.sem_execucao]
    if com_execucao:
        maior = max(com_execucao, key=lambda p: p.execucao.valor_liquido)
        share = (
            maior.execucao.valor_liquido / resumo.execucao_total * 100
            if resumo.execucao_total
            else 0.0
        )
        insights.append(
            f"O programa {maior.codigo} — {maior.nome} concentra "
            f"{formatar_brl_curto(maior.execucao.valor_liquido)} ({formatar_pct(share)} da UG)."
        )
    if resumo.uos:
        maior_uo = max(resumo.uos, key=lambda uo: uo.valor)
        insights.append(
            f"A UO {maior_uo.nome_oficial} responde por "
            f"{formatar_brl_curto(maior_uo.valor)} ({formatar_pct(maior_uo.share_ug)} da UG)."
        )
    compartilhados = [p for p in resumo.programas if p.compartilhado]
    if compartilhados:
        partes = []
        for p in compartilhados[:3]:
            outras = ", ".join(f"UG {u.codigo}" for u in p.outras_ugs)
            partes.append(
                f"{p.codigo} ({formatar_brl_curto(p.execucao.valor_liquido)}; outras UGs: {outras})"
            )
        insights.append("Programas compartilhados: " + "; ".join(partes) + ".")
    sem_execucao = [p for p in resumo.programas_proprios if p.sem_execucao]
    if sem_execucao:
        insights.append(
            "Sem execução registrada: "
            + ", ".join(f"{p.codigo} — {p.nome}" for p in sem_execucao)
            + "."
        )
    sem_indicador = [p for p in resumo.programas_proprios if p.sem_indicador]
    if sem_indicador:
        insights.append(
            "Sem indicador no PPA: "
            + ", ".join(f"{p.codigo} — {p.nome}" for p in sem_indicador)
            + "."
        )
    if resumo.n_indicadores + resumo.n_acoes:
        insights.append(
            f"Resultados {relatorio.perfil.ano}: {resumo.n_resultados} de "
            f"{resumo.n_indicadores + resumo.n_acoes} indicadores/ações informados "
            f"({formatar_pct(resumo.n_resultados / (resumo.n_indicadores + resumo.n_acoes) * 100)})."
        )
    if resumo.n_acoes:
        metas = sum(p.n_acoes_meta_percentual for p in resumo.programas)
        if metas:
            insights.append(
                f"Metas de ação: {metas} de {resumo.n_acoes} usam percentual do plano/bloco, "
                "não meta física anual."
            )
    insights.append(
        f"Participação no total liquidado do município: {formatar_pct(resumo.share_global)} "
        f"({formatar_brl_curto(resumo.execucao_total)} de {formatar_brl_curto(relatorio.total_geral)})."
    )
    return insights


def resumo_indicadores_acao(programa: Programa) -> dict[str, int]:
    metas = [parse_meta_acao(a.meta_ano, a.meta_bloco) for a in programa.acoes]
    return {
        "indicadores": len(programa.indicadores),
        "acoes": len(programa.acoes),
        "meta_percentual": sum(1 for m in metas if m.tipo == "percentual_plano"),
        "meta_quantidade": sum(1 for m in metas if m.tipo == "quantidade"),
        "meta_nao_definida": sum(1 for m in metas if m.tipo == "nao_definida"),
        "meta_texto": sum(1 for m in metas if m.tipo == "texto"),
    }
