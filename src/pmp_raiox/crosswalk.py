"""Crosswalk provisório entre ações do PPA e ações da LOA (projeto/atividade)."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from . import config
from .dados import Execucao, Programa
from .texto import norm_cabecalho, similaridade_nomes, texto

CABECALHO = [
    "codigo_programa",
    "n_acao",
    "codigo_projeto_atividade",
    "observacao",
]

MAPA = {
    "codigo programa": "codigo_programa",
    "codigo do programa": "codigo_programa",
    "n acao": "n_acao",
    "no acao": "n_acao",
    "numero da acao": "n_acao",
    "codigo projeto atividade": "codigo_projeto_atividade",
    "codigo p a": "codigo_projeto_atividade",
    "projeto atividade": "codigo_projeto_atividade",
    "observacao": "observacao",
}

LIMIAR_FORTE = 0.90
LIMIAR_FRACO = 0.75


@dataclass(frozen=True)
class LoaRef:
    codigo: str
    nome: str
    valor: float
    score: float
    origem: str
    observacao: str = ""

    @property
    def rotulo(self) -> str:
        return {
            "manual": "manual",
            "auto": "provisório",
            "auto-fraco": "verificar",
            "manual-sem": "sem vínculo",
        }.get(self.origem, self.origem)


@dataclass
class Crosswalk:
    manual: dict[tuple[str, str], LoaRef] = field(default_factory=dict)
    arquivo: Path | None = None

    def contar(self) -> dict[str, int]:
        valores = {"manual": 0, "manual-sem": 0}
        for ref in self.manual.values():
            valores[ref.origem] = valores.get(ref.origem, 0) + 1
        return valores


def _mapa(cabecalho: list[str]) -> dict[str, int]:
    indices: dict[str, int] = {}
    for i, nome_col in enumerate(cabecalho):
        campo = MAPA.get(norm_cabecalho(nome_col))
        if campo:
            indices[campo] = i
    return indices


def carregar_crosswalk(caminho: Path | str | None = None) -> Crosswalk:
    arquivo = Path(caminho) if caminho else config.ENTRADA / "crosswalk_loa.csv"
    if not arquivo.exists():
        return Crosswalk(arquivo=arquivo)
    with arquivo.open("r", encoding="utf-8-sig", newline="") as f:
        amostra = f.read(8192)
        f.seek(0)
        try:
            dialeto = csv.Sniffer().sniff(amostra, delimiters=",;")
        except csv.Error:
            dialeto = csv.excel
        leitor = csv.reader(f, dialeto)
        try:
            cabecalho = next(leitor)
        except StopIteration:
            return Crosswalk(arquivo=arquivo)
        indices = _mapa(cabecalho)
        if "codigo_programa" not in indices or "n_acao" not in indices:
            raise ValueError(
                f"{arquivo.name}: colunas obrigatórias codigo_programa e n_acao"
            )
        manual: dict[tuple[str, str], LoaRef] = {}
        for linha in leitor:
            if not linha or not any(texto(valor) for valor in linha):
                continue
            programa = texto(linha[indices["codigo_programa"]])
            n_acao = texto(linha[indices["n_acao"]])
            if not programa or not n_acao:
                continue
            codigo = (
                texto(linha[indices["codigo_projeto_atividade"]])
                if "codigo_projeto_atividade" in indices
                else ""
            )
            observacao = (
                texto(linha[indices["observacao"]]) if "observacao" in indices else ""
            )
            if codigo.strip() in {"", "-", "—"}:
                manual[(programa, n_acao)] = LoaRef(
                    codigo="",
                    nome="",
                    valor=0.0,
                    score=1.0,
                    origem="manual-sem",
                    observacao=observacao,
                )
                continue
            manual[(programa, n_acao)] = LoaRef(
                codigo=codigo.strip(),
                nome="",
                valor=0.0,
                score=1.0,
                origem="manual",
                observacao=observacao,
            )
    return Crosswalk(manual=manual, arquivo=arquivo)


def refs_para(
    programa: Programa,
    execucao: Execucao,
    crosswalk: Crosswalk | None,
    *,
    limiar_forte: float = LIMIAR_FORTE,
    limiar_fraco: float = LIMIAR_FRACO,
) -> dict[str, LoaRef]:
    crosswalk = crosswalk or Crosswalk()
    loas = execucao.por_acao_loa
    nomes = execucao.nomes_acao_loa
    refs: dict[str, LoaRef] = {}
    for acao in programa.acoes:
        manual = crosswalk.manual.get((programa.codigo, acao.num))
        if manual is not None:
            if not manual.codigo:
                refs[acao.num] = manual
                continue
            refs[acao.num] = LoaRef(
                codigo=manual.codigo,
                nome=nomes.get(manual.codigo, manual.codigo),
                valor=loas.get(manual.codigo, 0.0),
                score=1.0,
                origem="manual",
                observacao=manual.observacao,
            )
            continue
        if not loas:
            continue
        melhor: LoaRef | None = None
        for codigo, valor in loas.items():
            nome_loa = nomes.get(codigo, codigo)
            score = similaridade_nomes(acao.nome, nome_loa)
            if score < limiar_fraco:
                continue
            candidato = LoaRef(
                codigo=codigo,
                nome=nome_loa,
                valor=valor,
                score=score,
                origem="auto" if score >= limiar_forte else "auto-fraco",
            )
            if melhor is None or (candidato.score, candidato.valor) > (
                melhor.score,
                melhor.valor,
            ):
                melhor = candidato
        if melhor is not None:
            refs[acao.num] = melhor
    return refs


def criar_template_crosswalk(pasta: Path | str | None = None) -> list[Path]:
    base = Path(pasta) if pasta else config.ENTRADA
    base.mkdir(parents=True, exist_ok=True)
    criados: list[Path] = []
    caminho = base / "crosswalk_loa.csv"
    if not caminho.exists():
        with caminho.open("w", encoding="utf-8-sig", newline="") as f:
            escritor = csv.writer(f, delimiter=";")
            escritor.writerow(CABECALHO)
        criados.append(caminho)
    leia = base / "LEIAME_CROSSWALK.txt"
    if not leia.exists():
        leia.write_text(
            "Crosswalk PPA ação ↔ LOA projeto/atividade (provisório)\n"
            "\n"
            "Preencha uma linha por ação do PPA que precisa ser vinculada à ação da LOA.\n"
            "Colunas: codigo_programa; n_acao; codigo_projeto_atividade; observacao.\n"
            "Use o código P/A da LOA (ex.: 2.146). Deixe o código em branco ou '-' para\n"
            "marcar uma ação sem vínculo e impedir a sugestão automática.\n"
            "O raio-x sugere automaticamente pelo nome, mas o vínculo oficial deve ser\n"
            "validado pela área técnica.\n",
            encoding="utf-8",
        )
        criados.append(leia)
    return criados


def contar_refs(programas: list) -> dict[str, int]:
    total = 0
    manual = 0
    auto = 0
    auto_fraco = 0
    sem = 0
    sem_vinculo_manual = 0
    for programa_ug in programas:
        if not programa_ug.execucao.por_acao_loa:
            continue
        refs = programa_ug.loa_refs
        for acao in programa_ug.programa.acoes:
            total += 1
            ref = refs.get(acao.num)
            if ref is None:
                sem += 1
            elif ref.origem == "manual":
                manual += 1
            elif ref.origem == "auto":
                auto += 1
            elif ref.origem == "auto-fraco":
                auto_fraco += 1
            elif ref.origem == "manual-sem":
                sem_vinculo_manual += 1
    return {
        "total": total,
        "manual": manual,
        "auto": auto,
        "auto_fraco": auto_fraco,
        "sem": sem,
        "sem_vinculo_manual": sem_vinculo_manual,
    }
