from __future__ import annotations

import pytest

from pmp_raiox.texto import (
    direcao_indicador,
    formatar_brl,
    formatar_brl_curto,
    norm_cabecalho,
    norm_uo,
    parse_meta_acao,
    parse_numero,
    percentual_meta,
    similaridade_nomes,
    tendencia,
)


@pytest.mark.parametrize(
    ("texto", "valor", "unidade", "tipo"),
    [
        ("49.630", 49630, "", "nivel"),
        ("1.527", 1527, "", "nivel"),
        ("80%", 80, "%", "percentual"),
        ("45% (2024)", 45, "%", "percentual"),
        ("0,10% dos servidores ativos", 0.1, "%", "percentual"),
        ("05 unidades", 5, "unidades", "quantidade"),
        ("100/ano", 100, "/ano", "quantidade"),
        ("Aumentar em 50%", 50, "%", "variacao"),
        ("Redução de 20%", 20, "%", "variacao"),
        ("Mínimo 10", 10, "", "minimo"),
        ("Até 100 %", 100, "%", "limite"),
    ],
)
def test_parse_numero(texto, valor, unidade, tipo):
    numero = parse_numero(texto)
    assert numero is not None
    assert numero.valor == pytest.approx(valor)
    assert numero.unidade == unidade
    assert numero.tipo == tipo


@pytest.mark.parametrize(
    "texto",
    ["7 Urbanas e 2 Campo", "Diamante", "N/A (Programa em implantação)", "-", ""],
)
def test_parse_numero_nao_numerico(texto):
    assert parse_numero(texto) is None


def test_meta_percentual():
    meta = parse_meta_acao("25 %", "75 %")
    assert meta.tipo == "percentual_plano"
    assert meta.valor == 25
    assert meta.total_4anos == 100


def test_meta_quantidade():
    meta = parse_meta_acao("50123 Unid", "150369 Unid")
    assert meta.tipo == "quantidade"
    assert meta.valor == 50123
    assert meta.total_4anos == 200492


def test_meta_nao_definida():
    meta = parse_meta_acao("", "25 %")
    assert meta.tipo == "nao_definida"


def test_direcao_e_tendencia():
    assert direcao_indicador("10", "40") == "aumentar"
    assert direcao_indicador("40", "10") == "reduzir"
    assert direcao_indicador("5", "5") == "manter"
    assert direcao_indicador("Diamante", "Diamante") is None
    assert tendencia("20", "10", "40") == "Favorável"
    assert tendencia("5", "10", "40") == "Desfavorável"
    assert tendencia("10", "10", "10") == "Estável"
    assert tendencia("12", "10", "10") == "Favorável"
    assert tendencia("8", "10", "10") == "Desfavorável"


def test_normalizacao():
    assert norm_uo("001 - Fundo Municipal de Educação") == "FUNDO MUNICIPAL DE EDUCACAO"
    assert norm_cabecalho("Valor (R$)") == "valor r"
    assert norm_cabecalho("Nº Ações") == "no acoes"


def test_formatacao():
    assert formatar_brl(1234.5) == "R$ 1.234,50"
    assert "bi" in formatar_brl_curto(2_028_324_527.54)
    assert "mi" in formatar_brl_curto(2_028_324.54)


def test_percentual_meta():
    assert percentual_meta("30", 25, tipo_meta="percentual_plano") == 120
    assert percentual_meta("120%", 25, tipo_meta="percentual_plano") == 480
    assert percentual_meta("50000", 25, tipo_meta="percentual_plano") is None
    assert percentual_meta("50000 Unid", 25, tipo_meta="percentual_plano") is None
    assert percentual_meta("40000", 50123, tipo_meta="quantidade") == pytest.approx(79.8036, rel=1e-3)
    assert percentual_meta("30", 25, tipo_meta="percentual_plano", meta_anual="50") == 60


def test_percentual_meta_bloco():
    assert percentual_meta("50", 75, tipo_meta="percentual_plano", meta_ano_tipo="bloco") is None
    assert percentual_meta(
        "50", 75, tipo_meta="percentual_plano", meta_ano_tipo="bloco", meta_anual="100"
    ) == 50


def test_similaridade_nomes():
    assert similaridade_nomes("Manutenção do Transporte Escolar", "Manutenção do Transporte Escolar") == 1.0
    assert similaridade_nomes("Dívida Interna", "Dívida Externa") < 1.0
    assert similaridade_nomes("", "x") == 0.0
