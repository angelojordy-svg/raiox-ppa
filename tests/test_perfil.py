from __future__ import annotations

from pmp_raiox.dados import carregar_ppa
from pmp_raiox.html import gerar_html_ug
from pmp_raiox.modelo import construir_relatorio
from pmp_raiox.perfil import PERFIL_2026, PERFIL_2027, perfil_por_ano
from pmp_raiox.resultados import Resultados


def test_perfis_basicos():
    assert PERFIL_2026.ano == 2026
    assert PERFIL_2026.meta_ano_label == "Meta 2026"
    assert PERFIL_2026.meta_ano_tipo == "anual"
    assert PERFIL_2027.ano == 2027
    assert PERFIL_2027.contas_glob == "despesas_programas_2027_*.xlsx"
    assert PERFIL_2027.meta_ano_label == "Meta 2027-2029 (bloco)"
    assert PERFIL_2027.meta_ano_tipo == "bloco"
    assert PERFIL_2027.meta_bloco_col == ""
    assert perfil_por_ano("2027") is PERFIL_2027


def test_ppa_2027_usa_bloco(bases):
    ppa = carregar_ppa(perfil=PERFIL_2027)
    acao = ppa.programa("6024").acoes[0]
    assert acao.meta_ano == "75 %"
    assert acao.meta_bloco == ""
    assert acao.meta_ano_label == "Meta 2027-2029 (bloco)"
    assert acao.meta_ano_tipo == "bloco"


def test_html_2027_rotulos(bases, tmp_path):
    _ppa, contas = bases
    ppa = carregar_ppa(perfil=PERFIL_2027)
    relatorio = construir_relatorio(ppa, contas, Resultados(), perfil=PERFIL_2027)
    assert relatorio.perfil.ano == 2027
    arquivo = gerar_html_ug(relatorio, "004", tmp_path)
    html = arquivo.read_text(encoding="utf-8")
    assert "Resultado 2027" in html
    assert "Meta 2027-2029 (bloco)" in html
    assert "75% do bloco" in html
    assert "Resultado 2026" not in html
    assert "Meta 2026" not in html
    assert "diagnóstico de 2027" in html
