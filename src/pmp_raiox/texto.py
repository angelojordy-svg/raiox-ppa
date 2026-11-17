"""Normalizacao, leitura de numeros e formatacao pt-BR."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from datetime import date, datetime
from typing import Any


def texto(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    return " ".join(str(valor).split())


def codigo(valor: Any) -> str:
    return texto(valor).split(" - ", 1)[0].strip()


def nome(valor: Any) -> str:
    partes = texto(valor).split(" - ", 1)
    return partes[1].strip() if len(partes) > 1 else partes[0].strip()


@lru_cache(maxsize=8192)
def norm(valor: Any) -> str:
    t = unicodedata.normalize("NFKD", texto(valor))
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(t.split()).upper()


def norm_cabecalho(valor: Any) -> str:
    t = norm(valor).lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


@lru_cache(maxsize=8192)
def norm_uo(valor: Any) -> str:
    t = re.sub(r"^\d{1,4}\s*-\s*", "", texto(valor))
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^A-Za-z0-9]+", " ", t)
    return " ".join(t.split()).upper()


def _num_br(trecho: str) -> float:
    t = trecho.strip()
    if not t:
        return 0.0
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    else:
        partes = t.split(".")
        if len(partes) > 2:
            t = "".join(partes)
        elif len(partes) == 2 and len(partes[1]) == 3 and partes[0]:
            t = "".join(partes)
    return float(t)


@dataclass(frozen=True)
class Numero:
    valor: float
    unidade: str = ""
    tipo: str = "nivel"
    sufixo: str = ""
    direcao: str = ""
    original: str = ""

    @property
    def numerico(self) -> bool:
        return self.tipo in {"nivel", "quantidade", "percentual", "minimo", "limite"}

    @property
    def comparavel(self) -> bool:
        return self.tipo in {"nivel", "quantidade", "percentual"}


def parse_numero(valor: Any) -> Numero | None:
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return Numero(float(valor), "", "nivel", "", "", str(valor))
    s = texto(valor)
    if not s or s in {"-", "—", "N/A", "NA", "NÃO SE APLICA"}:
        return None

    sem_parenteses = re.sub(r"\([^)]*\)", "", s).strip()
    baixo = norm(sem_parenteses)

    m = re.match(r"^AUMENTAR EM\s+([\d.,]+)\s*%?\b", baixo)
    if m:
        return Numero(_num_br(m.group(1)), "%", "variacao", "", "aumentar", s)

    m = re.match(r"^REDU(?:CAO|ÇÃO) DE\s+([\d.,]+)\s*%?\b", baixo)
    if m:
        return Numero(_num_br(m.group(1)), "%", "variacao", "", "reduzir", s)

    m = re.match(r"^MINIMO\s+([\d.,]+)\b", baixo)
    if m:
        return Numero(_num_br(m.group(1)), "", "minimo", "", "", s)

    m = re.match(r"^ATE\s+([\d.,]+)\s*%?\b", baixo)
    if m:
        unidade = "%" if "%" in sem_parenteses else ""
        return Numero(_num_br(m.group(1)), unidade, "limite", "", "", s)

    numeros = re.findall(r"(?<![\w])\d[\d.,]*(?![\w])", sem_parenteses)
    if len(numeros) != 1:
        return None
    trecho = numeros[0]
    try:
        numero = _num_br(trecho)
    except ValueError:
        return None

    resto = sem_parenteses.replace(trecho, "", 1)
    unidade = ""
    tipo = "nivel"
    if re.search(r"%", resto):
        unidade = "%"
        tipo = "percentual"
        sufixo = resto.split("%", 1)[1].strip(" -–—")
    else:
        m_unidade = re.search(
            r"\b(Unid(?:ade|ades)?|UND|und|Pc|kWp|metros?|min|horas?|dias?|"
            r"alunos?|fam[ií]lias?|pessoas?|toneladas?|m[²2]|km|ha)\b",
            resto,
            re.IGNORECASE,
        )
        if m_unidade:
            unidade = m_unidade.group(1)
            tipo = "quantidade"
            sufixo = resto.strip(" -–—")
        elif re.search(r"/ano\b", resto, re.IGNORECASE):
            unidade = "/ano"
            tipo = "quantidade"
            sufixo = resto.strip(" -–—")
        else:
            sufixo = resto.strip(" -–—")
    return Numero(numero, unidade, tipo, sufixo, "", s)


@dataclass(frozen=True)
class MetaAcao:
    texto: str
    tipo: str
    valor: float | None = None
    unidade: str = ""
    meta_2027_2029: str = ""
    valor_2027_2029: float | None = None
    total_4anos: float | None = None
    total_unidade: str = ""


def parse_meta_acao(valor: Any, meta_2027_2029: Any = "") -> MetaAcao:
    s = texto(valor)
    s2 = texto(meta_2027_2029)
    if not s:
        n2 = parse_numero(s2)
        return MetaAcao(
            texto="",
            tipo="nao_definida",
            meta_2027_2029=s2,
            valor_2027_2029=n2.valor if n2 else None,
            total_unidade=n2.unidade if n2 else "",
        )
    n = parse_numero(s)
    if n is None:
        return MetaAcao(texto=s, tipo="texto", meta_2027_2029=s2)
    if n.tipo == "percentual" and n.unidade == "%":
        n2 = parse_numero(s2)
        total = None
        if n2 and n2.unidade == "%":
            total = n.valor + n2.valor
        return MetaAcao(
            texto=s,
            tipo="percentual_plano",
            valor=n.valor,
            unidade="%",
            meta_2027_2029=s2,
            valor_2027_2029=n2.valor if n2 else None,
            total_4anos=total,
            total_unidade="%",
        )
    if n.tipo in {"nivel", "quantidade"}:
        n2 = parse_numero(s2)
        total = None
        if n2 and n2.tipo in {"nivel", "quantidade"} and (
            not n.unidade or not n2.unidade or n.unidade == n2.unidade
        ):
            total = n.valor + n2.valor
        return MetaAcao(
            texto=s,
            tipo="quantidade",
            valor=n.valor,
            unidade=n.unidade,
            meta_2027_2029=s2,
            valor_2027_2029=n2.valor if n2 else None,
            total_4anos=total,
            total_unidade=n.unidade or (n2.unidade if n2 else ""),
        )
    return MetaAcao(texto=s, tipo="texto", valor=n.valor, unidade=n.unidade, meta_2027_2029=s2)


def direcao_indicador(ref_atual: Any, ref_2029: Any) -> str | None:
    a = parse_numero(ref_atual)
    b = parse_numero(ref_2029)
    if a is None or b is None or not a.comparavel or not b.comparavel:
        return None
    if not _unidades_compativeis(a, b):
        return None
    if b.valor > a.valor:
        return "aumentar"
    if b.valor < a.valor:
        return "reduzir"
    return "manter"


def _unidades_compativeis(a: Numero, b: Numero) -> bool:
    if a.unidade == b.unidade:
        return True
    if a.unidade == "%" or b.unidade == "%":
        return False
    return not a.unidade or not b.unidade


def tendencia(resultado: Any, ref_atual: Any, ref_2029: Any) -> str:
    r = parse_numero(resultado)
    if r is None:
        return "A apurar"
    direcao = direcao_indicador(ref_atual, ref_2029)
    if direcao is None:
        return "Qualitativo"
    a = parse_numero(ref_atual)
    if a is None or not _unidades_compativeis(r, a):
        return "Qualitativo"
    if direcao == "aumentar":
        if r.valor > a.valor:
            return "Favorável"
        if r.valor < a.valor:
            return "Desfavorável"
        return "Estável"
    if direcao == "reduzir":
        if r.valor < a.valor:
            return "Favorável"
        if r.valor > a.valor:
            return "Desfavorável"
        return "Estável"
    if r.valor > a.valor * 1.01:
        return "Favorável"
    if r.valor < a.valor * 0.99:
        return "Desfavorável"
    return "Estável"


def percentual(resultado: Any, meta: Any) -> float | None:
    r = parse_numero(resultado)
    m = parse_numero(meta)
    if r is None or m is None or not m.valor:
        return None
    return r.valor / m.valor * 100


def percentual_meta(
    resultado: Any,
    meta_valor: Any,
    *,
    tipo_meta: str = "",
    meta_anual: Any = "",
) -> float | None:
    if not texto(resultado) or not texto(meta_valor):
        return None
    if tipo_meta in {"nao_definida", "texto"} and not texto(meta_anual):
        return None
    if tipo_meta == "percentual_plano" and not texto(meta_anual):
        numero = parse_numero(resultado)
        if numero is None:
            return None
        if numero.unidade and numero.unidade != "%":
            return None
        if not numero.unidade and numero.valor > 100:
            return None
    return percentual(resultado, meta_anual or meta_valor)


def formatar_brl(valor: float | None, decimais: int = 2) -> str:
    if valor is None:
        return "—"
    t = f"{valor:,.{decimais}f}"
    return "R$ " + t.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_brl_curto(valor: float | None) -> str:
    if valor is None:
        return "—"
    absoluto = abs(valor)
    sinal = "-" if valor < 0 else ""
    if absoluto >= 1_000_000_000:
        return f"{sinal}R$ {absoluto / 1_000_000_000:,.2f} bi".replace(".", ",")
    if absoluto >= 1_000_000:
        return f"{sinal}R$ {absoluto / 1_000_000:,.2f} mi".replace(".", ",")
    if absoluto >= 1_000:
        return f"{sinal}R$ {absoluto / 1_000:,.1f} mil".replace(".", ",")
    return formatar_brl(valor)


def formatar_numero(valor: float | None, decimais: int = 0) -> str:
    if valor is None:
        return "—"
    t = f"{valor:,.{decimais}f}"
    return t.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_pct(valor: float | None, decimais: int = 1) -> str:
    if valor is None:
        return "—"
    return f"{valor:,.{decimais}f}%".replace(".", ",")


def formatar_data(valor: date | datetime | str | None) -> str:
    if valor is None or valor == "":
        return "—"
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    s = texto(valor)
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"
    return s
