from __future__ import annotations

from openpyxl import load_workbook

from pmp_raiox.xlsx import gerar_xlsx


def test_planilha_apoio(relatorio, tmp_path):
    arquivo = gerar_xlsx(relatorio, tmp_path, codigos_ug={"004"}, nome="apoio.xlsx")
    assert arquivo.exists()
    assert arquivo.stat().st_size > 20_000
    wb = load_workbook(arquivo, read_only=True, data_only=True)
    try:
        assert wb.sheetnames == [
            "Leia-me",
            "UGs",
            "Programas",
            "Indicadores",
            "Acoes",
            "Execucao_UG",
            "Execucao_Programa",
            "Execucao_Detalhe",
            "Alertas",
            "Dicionario",
        ]
        ugs = wb["UGs"]
        assert ugs.max_row == 36
        programas = wb["Programas"]
        assert programas.max_row == 88
        indicadores = wb["Indicadores"]
        assert indicadores.max_row >= 17
        acoes = wb["Acoes"]
        assert acoes.max_row >= 35
        cabecalho = [c.value for c in next(acoes.iter_rows(min_row=1, max_row=1))]
        assert "LOA código" in cabecalho
        assert "Crosswalk" in cabecalho
        detalhe = wb["Execucao_Detalhe"]
        assert detalhe.max_row >= 50
        leia = wb["Leia-me"]
        texto = " ".join(str(c.value) for row in leia.iter_rows() for c in row if c.value)
        assert "RAIO-X" in texto
        assert "Notas técnicas" in texto
        assert "liquidações" in texto
    finally:
        wb.close()


def test_planilha_completa(relatorio, tmp_path):
    arquivo = gerar_xlsx(relatorio, tmp_path, codigos_ug=None, nome="completo.xlsx")
    wb = load_workbook(arquivo, read_only=True, data_only=True)
    try:
        assert wb["Indicadores"].max_row == 248
        assert wb["Acoes"].max_row == 307
    finally:
        wb.close()
