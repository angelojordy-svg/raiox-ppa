"""Camada opcional de resultados, analises e evidencias informados pelas UGs."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from . import config
from .texto import norm_cabecalho, texto

CABECALHO_INDICADORES = [
    "codigo_programa",
    "n_indicador",
    "resultado",
    "meta_2026",
    "unidade",
    "data_apuracao",
    "fonte_resultado",
    "analise",
    "status",
    "evidencia_id",
]
CABECALHO_ACOES = [
    "codigo_programa",
    "n_acao",
    "resultado",
    "meta_anual",
    "unidade",
    "data_apuracao",
    "fonte_resultado",
    "analise",
    "status",
    "justificativa",
    "proximos_passos",
    "evidencia_id",
]
CABECALHO_EVIDENCIAS = [
    "id",
    "descricao",
    "tipo",
    "link",
    "data",
    "responsavel",
]

MAPA_INDICADORES = {
    "codigo programa": "codigo_programa",
    "codigo do programa": "codigo_programa",
    "n indicador": "n_indicador",
    "no indicador": "n_indicador",
    "numero do indicador": "n_indicador",
    "resultado": "resultado",
    "resultado 2026": "resultado",
    "meta 2026": "meta_2026",
    "unidade": "unidade",
    "data apuracao": "data_apuracao",
    "data de apuracao": "data_apuracao",
    "fonte resultado": "fonte_resultado",
    "fonte do resultado": "fonte_resultado",
    "analise": "analise",
    "status": "status",
    "evidencia id": "evidencia_id",
    "id evidencia": "evidencia_id",
}

MAPA_ACOES = {
    "codigo programa": "codigo_programa",
    "codigo do programa": "codigo_programa",
    "n acao": "n_acao",
    "no acao": "n_acao",
    "numero da acao": "n_acao",
    "resultado": "resultado",
    "resultado 2026": "resultado",
    "meta anual": "meta_anual",
    "meta anual 2026": "meta_anual",
    "unidade": "unidade",
    "data apuracao": "data_apuracao",
    "data de apuracao": "data_apuracao",
    "fonte resultado": "fonte_resultado",
    "fonte do resultado": "fonte_resultado",
    "analise": "analise",
    "status": "status",
    "justificativa": "justificativa",
    "proximos passos": "proximos_passos",
    "evidencia id": "evidencia_id",
    "id evidencia": "evidencia_id",
}

MAPA_EVIDENCIAS = {
    "id": "id",
    "descricao": "descricao",
    "tipo": "tipo",
    "link": "link",
    "data": "data",
    "responsavel": "responsavel",
}


@dataclass(frozen=True)
class ResultadoIndicador:
    codigo_programa: str
    n: str
    resultado: str = ""
    meta_2026: str = ""
    unidade: str = ""
    data_apuracao: str = ""
    fonte_resultado: str = ""
    analise: str = ""
    status: str = ""
    evidencia_id: str = ""


@dataclass(frozen=True)
class ResultadoAcao:
    codigo_programa: str
    num: str
    resultado: str = ""
    meta_anual: str = ""
    unidade: str = ""
    data_apuracao: str = ""
    fonte_resultado: str = ""
    analise: str = ""
    status: str = ""
    justificativa: str = ""
    proximos_passos: str = ""
    evidencia_id: str = ""


@dataclass(frozen=True)
class Evidencia:
    id: str
    descricao: str = ""
    tipo: str = ""
    link: str = ""
    data: str = ""
    responsavel: str = ""


@dataclass
class Resultados:
    indicadores: dict[tuple[str, str], ResultadoIndicador] = field(default_factory=dict)
    acoes: dict[tuple[str, str], ResultadoAcao] = field(default_factory=dict)
    evidencias: dict[str, Evidencia] = field(default_factory=dict)
    arquivos: dict[str, Path] = field(default_factory=dict)

    @property
    def vazio(self) -> bool:
        return not self.indicadores and not self.acoes and not self.evidencias

    def indicador(self, codigo_programa: str, n: str) -> ResultadoIndicador | None:
        return self.indicadores.get((texto(codigo_programa), texto(n)))

    def acao(self, codigo_programa: str, num: str) -> ResultadoAcao | None:
        return self.acoes.get((texto(codigo_programa), texto(num)))

    def evidencia(self, identificador: str) -> Evidencia | None:
        return self.evidencias.get(texto(identificador))


def _mapa(cabecalho: list[str], mapa: dict[str, str]) -> dict[str, int]:
    indices: dict[str, int] = {}
    for i, nome_col in enumerate(cabecalho):
        chave = norm_cabecalho(nome_col)
        campo = mapa.get(chave)
        if campo:
            indices[campo] = i
    return indices


def _ler_csv(caminho: Path, mapa: dict[str, str], obrigatorios: list[str]) -> list[dict[str, str]]:
    with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
        amostra = arquivo.read(8192)
        arquivo.seek(0)
        try:
            dialeto = csv.Sniffer().sniff(amostra, delimiters=",;")
        except csv.Error:
            dialeto = csv.excel
        leitor = csv.reader(arquivo, dialeto)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            return []
        indices = _mapa(cabecalho, mapa)
        faltando = [campo for campo in obrigatorios if campo not in indices]
        if faltando:
            raise ValueError(f"{caminho.name}: colunas ausentes {faltando}")
        linhas: list[dict[str, str]] = []
        for numero_linha, linha in enumerate(leitor, start=2):
            if not linha or not any(texto(valor) for valor in linha):
                continue
            registro = {
                campo: texto(linha[i]) if i < len(linha) else ""
                for campo, i in indices.items()
            }
            if not registro.get(obrigatorios[0]):
                continue
            registro["_linha"] = str(numero_linha)
            linhas.append(registro)
    return linhas


def carregar_resultados(pasta: Path | str | None = None) -> Resultados:
    base = Path(pasta) if pasta else config.ENTRADA
    resultados = Resultados()
    if not base.exists():
        return resultados

    caminho_ind = base / "resultados_indicadores.csv"
    if caminho_ind.exists():
        for linha in _ler_csv(caminho_ind, MAPA_INDICADORES, ["codigo_programa", "n_indicador"]):
            chave = (linha["codigo_programa"], linha["n_indicador"])
            resultados.indicadores[chave] = ResultadoIndicador(
                codigo_programa=linha["codigo_programa"],
                n=linha["n_indicador"],
                resultado=linha.get("resultado", ""),
                meta_2026=linha.get("meta_2026", ""),
                unidade=linha.get("unidade", ""),
                data_apuracao=linha.get("data_apuracao", ""),
                fonte_resultado=linha.get("fonte_resultado", ""),
                analise=linha.get("analise", ""),
                status=linha.get("status", ""),
                evidencia_id=linha.get("evidencia_id", ""),
            )
        resultados.arquivos["indicadores"] = caminho_ind

    caminho_acoes = base / "resultados_acoes.csv"
    if caminho_acoes.exists():
        for linha in _ler_csv(caminho_acoes, MAPA_ACOES, ["codigo_programa", "n_acao"]):
            chave = (linha["codigo_programa"], linha["n_acao"])
            resultados.acoes[chave] = ResultadoAcao(
                codigo_programa=linha["codigo_programa"],
                num=linha["n_acao"],
                resultado=linha.get("resultado", ""),
                meta_anual=linha.get("meta_anual", ""),
                unidade=linha.get("unidade", ""),
                data_apuracao=linha.get("data_apuracao", ""),
                fonte_resultado=linha.get("fonte_resultado", ""),
                analise=linha.get("analise", ""),
                status=linha.get("status", ""),
                justificativa=linha.get("justificativa", ""),
                proximos_passos=linha.get("proximos_passos", ""),
                evidencia_id=linha.get("evidencia_id", ""),
            )
        resultados.arquivos["acoes"] = caminho_acoes

    caminho_evid = base / "evidencias.csv"
    if caminho_evid.exists():
        for linha in _ler_csv(caminho_evid, MAPA_EVIDENCIAS, ["id"]):
            resultados.evidencias[linha["id"]] = Evidencia(
                id=linha["id"],
                descricao=linha.get("descricao", ""),
                tipo=linha.get("tipo", ""),
                link=linha.get("link", ""),
                data=linha.get("data", ""),
                responsavel=linha.get("responsavel", ""),
            )
        resultados.arquivos["evidencias"] = caminho_evid

    return resultados


def _criar_csv(caminho: Path, cabecalho: list[str]) -> bool:
    if caminho.exists():
        return False
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(cabecalho)
    return True


def criar_templates(pasta: Path | str | None = None) -> list[Path]:
    base = Path(pasta) if pasta else config.ENTRADA
    base.mkdir(parents=True, exist_ok=True)
    criados: list[Path] = []
    for nome, cabecalho in (
        ("resultados_indicadores.csv", CABECALHO_INDICADORES),
        ("resultados_acoes.csv", CABECALHO_ACOES),
        ("evidencias.csv", CABECALHO_EVIDENCIAS),
    ):
        caminho = base / nome
        if _criar_csv(caminho, cabecalho):
            criados.append(caminho)
    leia = base / "LEIAME.txt"
    if not leia.exists():
        leia.write_text(
            "Resultados do Raio-X 2026\n"
            "\n"
            "Preencha uma linha por indicador e por acao do PPA. Use os mesmos\n"
            "codigos do PPA (codigo do programa e numero do indicador/acao).\n"
            "O arquivo usa separador ponto e virgula (;), compativel com Excel pt-BR.\n"
            "O campo 'meta_anual' da acao e a meta fisica de 2026; quando o PPA\n"
            "trouxer apenas percentual do plano (ex.: 25%), informe a meta anual\n"
            "em quantidade ou deixe em branco e explique na analise.\n"
            "As evidencias sao referenciadas pelo campo 'evidencia_id'.\n",
            encoding="utf-8",
        )
        criados.append(leia)
    return criados
