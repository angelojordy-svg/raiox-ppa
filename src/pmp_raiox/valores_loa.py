"""Valores da LOA/empenhos: fixado inicial, empenhado, pago e a pagar."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook

from . import config
from .perfil import PERFIL_2026, PerfilAno
from .texto import codigo, norm, norm_cabecalho, texto


@dataclass
class ValoresPrograma:
    fixado: float | None = None
    empenhado: float | None = None
    pago: float | None = None
    a_pagar: float | None = None
    liquidado_empenhos: float | None = None


@dataclass
class ValoresLOA:
    por_programa: dict[str, ValoresPrograma] = field(default_factory=dict)
    fontes: dict[str, Path] = field(default_factory=dict)
    data_loa: date | None = None
    data_empenhos: date | None = None

    def programa(self, codigo_programa: str) -> ValoresPrograma | None:
        return self.por_programa.get(texto(codigo_programa))

    def contar(self) -> dict[str, int]:
        return {
            "programas": len(self.por_programa),
            "com_fixado": sum(1 for v in self.por_programa.values() if v.fixado is not None),
            "com_empenhado": sum(
                1 for v in self.por_programa.values() if v.empenhado is not None
            ),
        }


def _num(valor: object) -> float:
    if valor is None or valor == "":
        return 0.0
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return float(valor)
    s = texto(valor).replace("R$", "").replace(" ", "").replace("\xa0", "")
    if not s:
        return 0.0
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def _data_arquivo(caminho: Path) -> date:
    return datetime.fromtimestamp(caminho.stat().st_mtime).date()


def _arquivo_loa(ano: int) -> Path | None:
    pasta = config.DADOS / "In Put"
    candidatos = sorted(pasta.glob(f"prog_a*_{ano}.xlsx"))
    return candidatos[-1] if candidatos else None


def _arquivos_empenhos(ano: int) -> list[Path]:
    pasta = config.DADOS / "In Put" / "csv"
    return sorted(pasta.glob(f"empenhos_*_{ano}_atual.csv"))


def _ler_loa(caminho: Path, valores: dict[str, ValoresPrograma]) -> None:
    wb = load_workbook(caminho, read_only=True, data_only=True)
    try:
        ws = wb.active
        cabecalho = [norm_cabecalho(c.value) for c in ws[1]]
        i_prog = cabecalho.index("prog no")
        i_valor = cabecalho.index("valor inicial loa")
        for linha in ws.iter_rows(min_row=2, values_only=True):
            if not linha or not texto(linha[i_prog]):
                continue
            codigo_programa = codigo(linha[i_prog])
            if not codigo_programa:
                continue
            registro = valores.setdefault(codigo_programa, ValoresPrograma())
            registro.fixado = (registro.fixado or 0.0) + _num(linha[i_valor])
    finally:
        wb.close()


def _ler_empenhos(caminho: Path, valores: dict[str, ValoresPrograma]) -> None:
    with caminho.open("r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            programa = codigo(linha.get("Programa de governo", ""))
            if not programa:
                continue
            registro = valores.setdefault(programa, ValoresPrograma())
            registro.empenhado = registro.empenhado or 0.0
            registro.pago = registro.pago or 0.0
            registro.a_pagar = registro.a_pagar or 0.0
            registro.liquidado_empenhos = registro.liquidado_empenhos or 0.0
            sinal = -1.0 if norm(linha.get("Registro", "")).startswith("ANUL") else 1.0
            registro.empenhado += sinal * _num(linha.get("Valor (R$)"))
            registro.pago += sinal * _num(linha.get("Pago (R$)"))
            registro.a_pagar += sinal * _num(linha.get("A pagar (R$)"))
            registro.liquidado_empenhos += sinal * _num(linha.get("Liquidado (R$)"))


def carregar_valores_loa(perfil: PerfilAno | None = None) -> ValoresLOA:
    perfil = perfil or PERFIL_2026
    valores: dict[str, ValoresPrograma] = {}
    fontes: dict[str, Path] = {}
    data_loa = None
    data_empenhos = None

    loa = _arquivo_loa(perfil.ano)
    if loa is not None:
        _ler_loa(loa, valores)
        fontes["loa"] = loa
        data_loa = _data_arquivo(loa)

    empenhos = _arquivos_empenhos(perfil.ano)
    for arquivo in empenhos:
        _ler_empenhos(arquivo, valores)
        fontes[f"empenhos:{arquivo.stem}"] = arquivo
        data_empenhos = _data_arquivo(arquivo) if data_empenhos is None else max(
            data_empenhos, _data_arquivo(arquivo)
        )

    return ValoresLOA(
        por_programa=valores,
        fontes=fontes,
        data_loa=data_loa,
        data_empenhos=data_empenhos,
    )
