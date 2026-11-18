from __future__ import annotations

from pmp_raiox.html import gerar_html_index, gerar_html_ug


def test_gera_pagina_ug(relatorio, tmp_path):
    arquivo = gerar_html_ug(relatorio, "004", tmp_path)
    assert arquivo.exists()
    html = arquivo.read_text(encoding="utf-8")
    assert len(html) > 100_000
    assert "Fundo Municipal de Educação" in html
    assert "6022" in html
    assert "6024" in html
    assert "Aguardando devolutiva" in html
    assert 'id="loa-6024"' in html
    assert "loa-detalhe-6024" in html
    assert "Execução LOA" in html
    assert "Código P/A" in html
    assert "Ação do PPA" in html
    assert "LOA 2." in html
    assert "provisório" in html
    assert "projeto/atividade" in html
    assert "Imprimir / PDF" in html
    assert "Expandir programas" in html
    assert "data-print" in html
    assert "25% do plano" in html
    assert "Subseções por UO" in html
    assert 'id="analise"' in html
    assert "Análise qualitativa" in html
    assert "Sem execução" in html
    assert "Compartilhado" in html
    assert html.count("<html") == 1


def test_gera_pagina_ug_compartilhada(relatorio, tmp_path):
    arquivo = gerar_html_ug(relatorio, "016", tmp_path)
    html = arquivo.read_text(encoding="utf-8")
    assert "FUNDEB" in html
    assert "6023" in html
    assert "6024" in html
    assert "6025" in html
    assert "compartilhado" in html.lower()


def test_gera_index(relatorio, tmp_path):
    arquivo = gerar_html_index(relatorio, tmp_path, {"004"})
    assert arquivo.exists()
    html = arquivo.read_text(encoding="utf-8")
    assert len(html) > 60_000
    assert "35 unidades gestoras" in html
    assert "87" in html
    assert "6200" in html
    assert "ug_004_educacao.html" in html
    assert "Abrir relatório" in html
    assert "Programas sem indicador" in html
    assert "Programas sem execução" in html
    assert "Programas compartilhados" in html
    assert "Metas não atingidas" in html
    assert "Itens avaliáveis" in html
    assert html.count("<html") == 1


def test_index_sem_ug_gerada(relatorio, tmp_path):
    arquivo = gerar_html_index(relatorio, tmp_path, set())
    html = arquivo.read_text(encoding="utf-8")
    assert "ug_004_educacao.html" not in html
    assert "Não gerado" in html
