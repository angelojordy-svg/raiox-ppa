"""Leitura do PPA 2026-2029 e da execucao orcamentaria de 2026."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from . import config
from .texto import codigo, norm, norm_cabecalho, norm_uo, nome, texto


@dataclass(frozen=True)
class Indicador:
    codigo_programa: str
    n: str
    nome: str
    fonte: str
    ref_atual: str
    ref_2029: str


@dataclass(frozen=True)
class Acao:
    codigo_programa: str
    num: str
    nome: str
    tipo: str
    produto: str
    meta_2026: str
    meta_2027_2029: str
    objetivo: str
    obs_emenda: str
    pagina: int | str


@dataclass
class Programa:
    codigo: str
    nome: str
    eixo: str
    orgao: str
    periodo: str
    publico_alvo: str
    tipo: str
    natureza: str
    objetivo: str
    indicadores: list[Indicador] = field(default_factory=list)
    acoes: list[Acao] = field(default_factory=list)

    @property
    def sem_indicador(self) -> bool:
        return not self.indicadores

    @property
    def sem_acao(self) -> bool:
        return not self.acoes


@dataclass
class PPA:
    programas: list[Programa]
    por_codigo: dict[str, Programa] = field(init=False)

    def __post_init__(self) -> None:
        self.por_codigo = {p.codigo: p for p in self.programas}

    @property
    def indicadores(self) -> list[Indicador]:
        return [i for p in self.programas for i in p.indicadores]

    @property
    def acoes(self) -> list[Acao]:
        return [a for p in self.programas for a in p.acoes]

    def programa(self, codigo_programa: str) -> Programa | None:
        return self.por_codigo.get(texto(codigo_programa))

    def indicadores_de(self, codigo_programa: str) -> list[Indicador]:
        p = self.programa(codigo_programa)
        return list(p.indicadores) if p else []

    def acoes_de(self, codigo_programa: str) -> list[Acao]:
        p = self.programa(codigo_programa)
        return list(p.acoes) if p else []


@dataclass
class Execucao:
    valor_liquido: float = 0.0
    valor_realizado: float = 0.0
    valor_anulado: float = 0.0
    linhas: int = 0
    por_uo: dict[str, float] = field(default_factory=dict)
    linhas_por_uo: dict[str, int] = field(default_factory=dict)
    por_natureza: dict[str, float] = field(default_factory=dict)
    por_fonte: dict[str, float] = field(default_factory=dict)
    por_mes: dict[str, float] = field(default_factory=dict)
    por_acao_loa: dict[str, float] = field(default_factory=dict)
    por_acao_natureza: dict[tuple[str, str], float] = field(default_factory=dict)
    linhas_acao_natureza: dict[tuple[str, str], int] = field(default_factory=dict)
    nomes_acao_loa: dict[str, str] = field(default_factory=dict)
    por_entidade: dict[str, float] = field(default_factory=dict)

    @property
    def vazia(self) -> bool:
        return self.linhas == 0 and not self.valor_liquido

    def adicionar(
        self,
        valor: float,
        *,
        uo: str = "",
        natureza: str = "",
        fonte: str = "",
        mes: str = "",
        acao_loa: str = "",
        nome_acao_loa: str = "",
        entidade: str = "",
    ) -> None:
        sinal = -1.0 if valor < 0 else 1.0
        liquido = abs(valor) * sinal
        self.valor_liquido += liquido
        if liquido >= 0:
            self.valor_realizado += liquido
        else:
            self.valor_anulado += liquido
        self.linhas += 1
        if uo:
            self.por_uo[uo] = self.por_uo.get(uo, 0.0) + liquido
            self.linhas_por_uo[uo] = self.linhas_por_uo.get(uo, 0) + 1
        chave_natureza = natureza or "SEM NATUREZA"
        chave_acao = acao_loa or "SEM AÇÃO"
        self.por_natureza[chave_natureza] = (
            self.por_natureza.get(chave_natureza, 0.0) + liquido
        )
        if fonte:
            self.por_fonte[fonte] = self.por_fonte.get(fonte, 0.0) + liquido
        if mes:
            self.por_mes[mes] = self.por_mes.get(mes, 0.0) + liquido
        self.por_acao_loa[chave_acao] = self.por_acao_loa.get(chave_acao, 0.0) + liquido
        self.nomes_acao_loa.setdefault(
            chave_acao,
            nome_acao_loa or "Ação não informada",
        )
        chave_an = (chave_acao, chave_natureza)
        self.por_acao_natureza[chave_an] = (
            self.por_acao_natureza.get(chave_an, 0.0) + liquido
        )
        self.linhas_acao_natureza[chave_an] = self.linhas_acao_natureza.get(chave_an, 0) + 1
        if entidade:
            self.por_entidade[entidade] = self.por_entidade.get(entidade, 0.0) + liquido

    def mesclar(self, outra: "Execucao") -> None:
        self.valor_liquido += outra.valor_liquido
        self.valor_realizado += outra.valor_realizado
        self.valor_anulado += outra.valor_anulado
        self.linhas += outra.linhas
        for chave, valor in outra.linhas_por_uo.items():
            self.linhas_por_uo[chave] = self.linhas_por_uo.get(chave, 0) + valor
        for chave, valor in outra.por_acao_natureza.items():
            self.por_acao_natureza[chave] = self.por_acao_natureza.get(chave, 0.0) + valor
        for chave, valor in outra.linhas_acao_natureza.items():
            self.linhas_acao_natureza[chave] = self.linhas_acao_natureza.get(chave, 0) + valor
        for destino, origem in (
            (self.por_uo, outra.por_uo),
            (self.por_natureza, outra.por_natureza),
            (self.por_fonte, outra.por_fonte),
            (self.por_mes, outra.por_mes),
            (self.por_acao_loa, outra.por_acao_loa),
            (self.por_entidade, outra.por_entidade),
        ):
            for chave, valor in origem.items():
                destino[chave] = destino.get(chave, 0.0) + valor
        for chave, valor in outra.nomes_acao_loa.items():
            self.nomes_acao_loa.setdefault(chave, valor)

    def top(self, dicionario: dict[str, float], limite: int = 10) -> list[tuple[str, float]]:
        return sorted(dicionario.items(), key=lambda kv: (-kv[1], kv[0]))[:limite]


@dataclass
class UOExecucao:
    nome: str
    nome_oficial: str
    codigos: set[str] = field(default_factory=set)
    execucao: Execucao = field(default_factory=Execucao)
    programas: set[str] = field(default_factory=set)


@dataclass
class UGExecucao:
    codigo: str
    nome_contas: str
    nome_oficial: str
    execucao: Execucao = field(default_factory=Execucao)
    uos: dict[str, UOExecucao] = field(default_factory=dict)
    programas: set[str] = field(default_factory=set)


@dataclass
class Contas:
    arquivo: Path
    ugs: dict[str, UGExecucao]
    programa_ug: dict[tuple[str, str], Execucao]
    programa_total: dict[str, Execucao]
    programa_nome: dict[str, str]
    total: Execucao
    data_min: date | None
    data_max: date | None
    registros: dict[str, int]
    linhas: int

    def execucao(self, codigo_programa: str, ug: str) -> Execucao:
        return self.programa_ug.get((codigo_programa, ug), Execucao())

    def total_programa(self, codigo_programa: str) -> float:
        execucao = self.programa_total.get(codigo_programa)
        return execucao.valor_liquido if execucao else 0.0

    def ugs_do_programa(self, codigo_programa: str) -> list[str]:
        return sorted(
            ug for (codigo, ug) in self.programa_ug if codigo == codigo_programa
        )


def _arquivo_contas_mais_recente(pasta: Path | None = None) -> Path:
    base = pasta or (config.DADOS / "Saida")
    candidatos = sorted(
        base.glob("despesas_programas_2026_*.xlsx"),
        key=lambda p: (p.stat().st_mtime, p.name),
    )
    if not candidatos:
        raise FileNotFoundError(f"Nenhum despesas_programas_2026_*.xlsx encontrado em {base}")
    return candidatos[-1]


def _indice_cabecalho(ws) -> dict[str, int]:
    cabecalho = [texto(c.value) for c in ws[1]]
    return {norm_cabecalho(nome_col): i for i, nome_col in enumerate(cabecalho) if nome_col}


def _exigir(indices: dict[str, int], chaves: list[tuple[str, str]], aba: str) -> None:
    faltando = [rotulo for chave, rotulo in chaves if chave not in indices]
    if faltando:
        raise ValueError(f"Colunas ausentes na aba {aba}: {faltando}")


MAPA_PROGRAMAS = {
    "codigo": "codigo",
    "eixo": "eixo",
    "programa": "nome",
    "orgao responsavel": "orgao",
    "periodo": "periodo",
    "publico alvo": "publico_alvo",
    "tipo": "tipo",
    "natureza": "natureza",
    "no indicadores": "n_indicadores",
    "no acoes": "n_acoes",
    "objetivo do programa": "objetivo",
}


def carregar_ppa(caminho: Path | str | None = None) -> PPA:
    arquivo = Path(caminho) if caminho else config.PPA_PADRAO
    if not arquivo.exists():
        raise FileNotFoundError(f"PPA não encontrado: {arquivo}")
    wb = load_workbook(arquivo, read_only=True, data_only=True)
    try:
        indices = _indice_cabecalho(wb["Programas"])
        _exigir(
            indices,
            [
                ("codigo", "Código"),
                ("eixo", "Eixo"),
                ("programa", "Programa"),
                ("orgao responsavel", "Órgão Responsável"),
                ("periodo", "Período"),
                ("publico alvo", "Público Alvo"),
                ("tipo", "Tipo"),
                ("natureza", "Natureza"),
                ("no indicadores", "Nº Indicadores"),
                ("no acoes", "Nº Ações"),
                ("objetivo do programa", "Objetivo do Programa"),
            ],
            "Programas",
        )
        programas: list[Programa] = []
        for linha in wb["Programas"].iter_rows(min_row=2, values_only=True):
            if not linha or not texto(linha[indices["codigo"]]):
                continue
            programas.append(
                Programa(
                    codigo=codigo(linha[indices["codigo"]]),
                    nome=texto(linha[indices["programa"]]),
                    eixo=texto(linha[indices["eixo"]]),
                    orgao=texto(linha[indices["orgao responsavel"]]),
                    periodo=texto(linha[indices["periodo"]]),
                    publico_alvo=texto(linha[indices["publico alvo"]]),
                    tipo=texto(linha[indices["tipo"]]),
                    natureza=texto(linha[indices["natureza"]]),
                    objetivo=texto(linha[indices["objetivo do programa"]]),
                )
            )
        por_codigo = {p.codigo: p for p in programas}

        ind = _indice_cabecalho(wb["Indicadores"])
        _exigir(
            ind,
            [
                ("codigo programa", "Código Programa"),
                ("no", "Nº"),
                ("indicador", "Indicador"),
                ("fonte do indicador", "Fonte do Indicador"),
                ("referencia atual", "Referência Atual"),
                ("referencia esperada 2029", "Referência Esperada (2029)"),
            ],
            "Indicadores",
        )
        for linha in wb["Indicadores"].iter_rows(min_row=2, values_only=True):
            if not linha or not texto(linha[ind["codigo programa"]]):
                continue
            codigo_programa = codigo(linha[ind["codigo programa"]])
            programa = por_codigo.get(codigo_programa)
            if programa is None:
                continue
            programa.indicadores.append(
                Indicador(
                    codigo_programa=codigo_programa,
                    n=texto(linha[ind["no"]]),
                    nome=texto(linha[ind["indicador"]]),
                    fonte=texto(linha[ind["fonte do indicador"]]),
                    ref_atual=texto(linha[ind["referencia atual"]]),
                    ref_2029=texto(linha[ind["referencia esperada 2029"]]),
                )
            )

        acoes = _indice_cabecalho(wb["Ações"])
        _exigir(
            acoes,
            [
                ("codigo programa", "Código Programa"),
                ("no acao", "Nº Ação"),
                ("nome da acao", "Nome da Ação"),
                ("tipo a p", "Tipo (A/P)"),
                ("produto esperado", "Produto Esperado"),
                ("meta 2026", "Meta 2026"),
                ("meta 2027 2029", "Meta 2027-2029"),
                ("objetivo da acao", "Objetivo da Ação"),
                ("obs emenda", "Obs. Emenda"),
                ("pagina", "Página"),
            ],
            "Ações",
        )
        for linha in wb["Ações"].iter_rows(min_row=2, values_only=True):
            if not linha or not texto(linha[acoes["codigo programa"]]):
                continue
            codigo_programa = codigo(linha[acoes["codigo programa"]])
            programa = por_codigo.get(codigo_programa)
            if programa is None:
                continue
            pagina = linha[acoes["pagina"]]
            if isinstance(pagina, float) and pagina.is_integer():
                pagina = int(pagina)
            programa.acoes.append(
                Acao(
                    codigo_programa=codigo_programa,
                    num=texto(linha[acoes["no acao"]]),
                    nome=texto(linha[acoes["nome da acao"]]),
                    tipo=texto(linha[acoes["tipo a p"]]),
                    produto=texto(linha[acoes["produto esperado"]]),
                    meta_2026=texto(linha[acoes["meta 2026"]]),
                    meta_2027_2029=texto(linha[acoes["meta 2027 2029"]]),
                    objetivo=texto(linha[acoes["objetivo da acao"]]),
                    obs_emenda=texto(linha[acoes["obs emenda"]]),
                    pagina=pagina if pagina is not None else "",
                )
            )
        return PPA(programas=programas)
    finally:
        wb.close()


def _valor_numerico(valor: Any) -> float:
    if valor is None or valor == "":
        return 0.0
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return float(valor)
    t = texto(valor).replace("R$", "").replace("\xa0", "").replace(" ", "")
    if not t:
        return 0.0
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return 0.0


def _mes(valor: Any) -> str:
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m")
    if isinstance(valor, date):
        return valor.strftime("%Y-%m")
    t = texto(valor)
    return t[:7] if len(t) >= 7 else ""


def _data(valor: Any) -> date | None:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    t = texto(valor)
    try:
        return datetime.strptime(t[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def carregar_contas(caminho: Path | str | None = None) -> Contas:
    arquivo = Path(caminho) if caminho else _arquivo_contas_mais_recente()
    wb = load_workbook(arquivo, read_only=True, data_only=True)
    ws = wb["Consolidado"]
    try:
        indices = _indice_cabecalho(ws)
        _exigir(
            indices,
            [
                ("unidade gestora", "Unidade gestora"),
                ("unidade orcamentaria", "Unidade orçamentária"),
                ("programa de governo", "Programa de governo"),
                ("valor r", "Valor (R$)"),
                ("registro", "Registro"),
                ("data", "Data"),
                ("natureza da despesa", "Natureza da despesa"),
                ("fonte de recurso", "Fonte de recurso"),
                ("acao", "Ação"),
                ("entidade", "Entidade"),
            ],
            "Consolidado",
        )
        i_ug = indices["unidade gestora"]
        i_uo = indices["unidade orcamentaria"]
        i_pg = indices["programa de governo"]
        i_valor = indices["valor r"]
        i_reg = indices["registro"]
        i_data = indices["data"]
        i_nat = indices["natureza da despesa"]
        i_fonte = indices["fonte de recurso"]
        i_acao = indices["acao"]
        i_proj = indices.get("projeto atividade")
        i_ent = indices["entidade"]

        ugs: dict[str, UGExecucao] = {}
        programa_ug: dict[tuple[str, str], Execucao] = {}
        programa_total: dict[str, Execucao] = {}
        programa_nome: dict[str, str] = {}
        total = Execucao()
        data_min: date | None = None
        data_max: date | None = None
        registros: dict[str, int] = defaultdict(int)
        linhas = 0

        for linha in ws.iter_rows(min_row=2, values_only=True):
            ug_raw = texto(linha[i_ug])
            if not ug_raw:
                continue
            ug_cod = codigo(ug_raw)
            ug_nome_contas = nome(ug_raw)
            uo_raw = texto(linha[i_uo])
            uo_norm = norm_uo(uo_raw)
            uo_nome = nome(uo_raw)
            pg_raw = texto(linha[i_pg])
            pg_cod = codigo(pg_raw) if pg_raw and norm(pg_raw) != "SEM PROGRAMA" else ""
            pg_nome = nome(pg_raw) if pg_cod else ""
            valor_bruto = _valor_numerico(linha[i_valor])
            registro = texto(linha[i_reg])
            registro_norm = norm(registro)
            negativo = valor_bruto < 0 or "ANULADO" in registro_norm
            valor = -abs(valor_bruto) if negativo else abs(valor_bruto)
            natureza = codigo(linha[i_nat])
            fonte = codigo(linha[i_fonte])
            acao_raw = texto(linha[i_acao])
            projeto_raw = texto(linha[i_proj]) if i_proj is not None else ""
            acao_loa = codigo(projeto_raw) or codigo(acao_raw)
            nome_acao_loa = nome(projeto_raw) or nome(acao_raw)
            mes = _mes(linha[i_data])
            entidade = texto(linha[i_ent])
            data_valor = _data(linha[i_data])
            if data_valor:
                data_min = data_valor if data_min is None or data_valor < data_min else data_min
                data_max = data_valor if data_max is None or data_valor > data_max else data_max
            registros[registro or "SEM REGISTRO"] += 1
            linhas += 1

            ug = ugs.get(ug_cod)
            if ug is None:
                ug = UGExecucao(
                    codigo=ug_cod,
                    nome_contas=ug_nome_contas,
                    nome_oficial=config.nome_ug(ug_cod),
                )
                ugs[ug_cod] = ug
            uo = ug.uos.get(uo_norm)
            if uo is None:
                uo = UOExecucao(
                    nome=uo_nome,
                    nome_oficial=config.nome_uo(ug_cod, uo_norm, uo_nome),
                )
                ug.uos[uo_norm] = uo
            if codigo(uo_raw):
                uo.codigos.add(codigo(uo_raw))

            ug.execucao.adicionar(
                valor,
                uo=uo_norm,
                natureza=natureza,
                fonte=fonte,
                mes=mes,
                acao_loa=acao_loa,
                nome_acao_loa=nome_acao_loa,
                entidade=entidade,
            )
            uo.execucao.adicionar(
                valor,
                natureza=natureza,
                fonte=fonte,
                mes=mes,
                acao_loa=acao_loa,
                nome_acao_loa=nome_acao_loa,
                entidade=entidade,
            )
            total.adicionar(
                valor,
                uo=f"{ug_cod}|{uo_norm}",
                natureza=natureza,
                fonte=fonte,
                mes=mes,
                acao_loa=acao_loa,
                nome_acao_loa=nome_acao_loa,
                entidade=entidade,
            )
            if pg_cod:
                programa_nome.setdefault(pg_cod, pg_nome)
                ug.programas.add(pg_cod)
                uo.programas.add(pg_cod)
                chave = (pg_cod, ug_cod)
                exec_pg = programa_ug.get(chave)
                if exec_pg is None:
                    exec_pg = Execucao()
                    programa_ug[chave] = exec_pg
                exec_pg.adicionar(
                    valor,
                    uo=uo_norm,
                    natureza=natureza,
                    fonte=fonte,
                    mes=mes,
                    acao_loa=acao_loa,
                    nome_acao_loa=nome_acao_loa,
                    entidade=entidade,
                )
                exec_total = programa_total.get(pg_cod)
                if exec_total is None:
                    exec_total = Execucao()
                    programa_total[pg_cod] = exec_total
                exec_total.adicionar(
                    valor,
                    uo=uo_norm,
                    natureza=natureza,
                    fonte=fonte,
                    mes=mes,
                    acao_loa=acao_loa,
                    nome_acao_loa=nome_acao_loa,
                    entidade=entidade,
                )

        return Contas(
            arquivo=arquivo,
            ugs=ugs,
            programa_ug=programa_ug,
            programa_total=programa_total,
            programa_nome=programa_nome,
            total=total,
            data_min=data_min,
            data_max=data_max,
            registros=dict(registros),
            linhas=linhas,
        )
    finally:
        wb.close()
