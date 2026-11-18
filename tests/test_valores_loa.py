from __future__ import annotations

from pmp_raiox.html import gerar_html_ug
from pmp_raiox.modelo import construir_relatorio
from pmp_raiox.perfil import PERFIL_2026
from pmp_raiox.resultados import Resultados
from pmp_raiox.valores_loa import carregar_valores_loa
from pmp_raiox.xlsx import gerar_xlsx


def test_carrega_valores(bases):
    _ppa, _contas = bases
    valores = carregar_valores_loa(PERFIL_2026)
    programa = valores.programa("6024")
    assert programa is not None
    assert programa.fixado and programa.fixado > 0
    assert programa.empenhado and programa.empenhado > 0
    assert programa.pago and programa.pago > 0
    assert programa.a_pagar is not None
    assert valores.contar()["programas"] > 0


def test_relatorio_e_html_com_valores(bases, tmp_path):
    ppa, contas = bases
    valores = carregar_valores_loa(PERFIL_2026)
    relatorio = construir_relatorio(
        ppa, contas, Resultados(), perfil=PERFIL_2026, valores_loa=valores
    )
    ug = relatorio.ug("004")
    programa = next(p for p in ug.programas if p.codigo == "6024")
    assert programa is not None
    arquivo = gerar_html_ug(relatorio, "004", tmp_path)
    html = arquivo.read_text(encoding="utf-8")
    assert "Valores LOA do programa" in html
    assert "Fixado inicial" in html
    assert "Autorizado" in html
    assert "n/d" in html


def test_xlsx_programas_com_valores(bases, tmp_path):
    ppa, contas = bases
    valores = carregar_valores_loa(PERFIL_2026)
    relatorio = construir_relatorio(
        ppa, contas, Resultados(), perfil=PERFIL_2026, valores_loa=valores
    )
    arquivo = gerar_xlsx(relatorio, tmp_path, codigos_ug={"004"}, nome="valores.xlsx")
    from openpyxl import load_workbook

    wb = load_workbook(arquivo, read_only=True, data_only=True)
    try:
        cabecalho = [c.value for c in next(wb["Programas"].iter_rows(min_row=1, max_row=1))]
        assert "Fixado inicial (R$)" in cabecalho
        assert "Empenhado (R$)" in cabecalho
        assert "Pago (R$)" in cabecalho
        assert "Autorizado (R$)" in cabecalho
    finally:
        wb.close()
