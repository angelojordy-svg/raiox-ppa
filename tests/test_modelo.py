from __future__ import annotations

import pytest

from pmp_raiox.modelo import detalhe_execucao_programa, detalhe_execucao_ug, insights_ug, resumo_indicadores_acao


def test_cobertura(relatorio):
    assert relatorio.n_programas == 87
    assert relatorio.n_indicadores == 247
    assert relatorio.n_acoes == 306
    assert relatorio.n_programas_com_execucao == 74
    assert relatorio.n_programas_sem_execucao == 13
    assert relatorio.n_programas_sem_execucao_mapeado == 7
    assert relatorio.n_sem_ug == 4
    assert relatorio.n_excluidos == 2
    assert relatorio.n_sem_indicador == 20
    assert relatorio.n_compartilhados == 4
    assert relatorio.n_programas_com_execucao + relatorio.n_programas_sem_execucao == 87


def test_totais(relatorio):
    assert relatorio.total_ppa > 1_900_000_000
    assert relatorio.total_fora_ppa > 0
    assert relatorio.total_ppa + relatorio.total_fora_ppa == pytest.approx(
        relatorio.total_geral, rel=1e-6
    )


def test_ug_004(relatorio):
    ug = relatorio.ug("004")
    assert ug is not None
    assert ug.nome == "Fundo Municipal de Educação"
    assert ug.n_programas_proprios == 9
    assert ug.n_programas_compartilhados == 0
    assert ug.n_sem_indicador == 1
    assert ug.n_sem_execucao == 1
    assert ug.n_compartilhados == 3
    codigos = {p.codigo for p in ug.programas}
    assert "6022" in codigos
    assert "6020" in codigos
    assert "6024" in codigos
    assert ug.n_indicadores == 16
    assert ug.n_acoes == 34
    assert len(ug.uos) == 2
    assert ug.execucao_total > 0
    assert any(a.tipo == "programa_sem_execucao" for a in ug.alertas)
    assert any(a.tipo == "programa_sem_indicador" for a in ug.alertas)
    assert any(a.tipo == "uo_codigo_duplicado" for a in ug.alertas)


def test_ug_016_compartilhada(relatorio):
    ug = relatorio.ug("016")
    assert ug is not None
    assert ug.n_programas_proprios == 0
    assert ug.n_programas_compartilhados == 3
    assert ug.n_compartilhados == 3
    assert {p.codigo for p in ug.programas} == {"6023", "6024", "6025"}
    assert all(p.dono == "004" for p in ug.programas)


def test_cobertura_excecoes(relatorio):
    assert relatorio.cobertura["6022"].status == "sem_execucao"
    assert relatorio.cobertura["6022"].dono == "004"
    assert relatorio.cobertura["6022"].vinculo_provisorio is True
    assert relatorio.cobertura["6005"].status == "sem_ug"
    assert relatorio.cobertura["6034-A"].status == "excluido"
    assert relatorio.cobertura["6013"].ugs_execucao == ["001", "041"]
    assert relatorio.cobertura["6013"].dono == "001"
    assert {item.codigo for item in relatorio.sem_ug} == {"6005", "6083", "6084", "6085"}
    assert {item.codigo for item in relatorio.excluidos} == {"6034-A", "6066-A"}
    assert [item.codigo for item in relatorio.fora_ppa] == ["6200"]


def test_ranking(relatorio):
    valores = [ug.execucao_total for ug in relatorio.ranking_ugs]
    assert valores == sorted(valores, reverse=True)
    assert len(relatorio.ranking_ugs) == 35


def test_insights(relatorio):
    ug = relatorio.ug("004")
    assert ug is not None
    textos = insights_ug(ug, relatorio)
    assert len(textos) >= 5
    assert any("6024" in texto for texto in textos)
    assert any("6022" in texto for texto in textos)
    assert any("6020" in texto for texto in textos)


def test_meta_resumo(relatorio):
    programa = relatorio.ppa.programa("6024")
    assert programa is not None
    resumo = resumo_indicadores_acao(programa)
    assert resumo["indicadores"] == 4
    assert resumo["acoes"] == 10
    assert resumo["meta_percentual"] == 10


def test_alertas_globais(relatorio):
    tipos = {alerta.tipo for alerta in relatorio.alertas_globais}
    assert "fora_ppa" in tipos
    assert "programas_sem_ug" in tipos
    assert "programas_excluidos" in tipos
    assert "acoes_meta_percentual" in tipos
    assert "execucao_liquidacao" in tipos


def test_detalhe_execucao_ug(relatorio):
    ug = relatorio.ug("004")
    detalhes = detalhe_execucao_ug(ug)
    assert len(detalhes) >= 50
    assert abs(sum(item.valor for item in detalhes) - ug.execucao_total) < 0.01
    assert all(item.acao_loa and item.natureza for item in detalhes)
    assert all(0 <= item.pct_acao <= 100.001 for item in detalhes)


def test_detalhe_execucao_programa(relatorio):
    ug = relatorio.ug("004")
    programa = next(p for p in ug.programas if p.codigo == "6024")
    detalhes = detalhe_execucao_programa(programa, ug.execucao_total)
    assert detalhes
    assert all(item.programa == "6024" for item in detalhes)
    assert abs(sum(item.valor for item in detalhes) - programa.execucao.valor_liquido) < 0.01
    assert all(item.acao_loa for item in detalhes)
