from __future__ import annotations

import pytest

from pmp_raiox import config

SEM_EXECUCAO = {
    "6005",
    "6014",
    "6022",
    "6032",
    "6033",
    "6034-A",
    "6053",
    "6066-A",
    "6072",
    "6074",
    "6083",
    "6084",
    "6085",
}


def test_ppa_basico(bases):
    ppa, _contas = bases
    assert len(ppa.programas) == 87
    assert len(ppa.indicadores) == 247
    assert len(ppa.acoes) == 306
    assert len({p.orgao for p in ppa.programas}) == 48
    assert sum(1 for p in ppa.programas if p.sem_indicador) == 20


def test_contas_basico(bases):
    _ppa, contas = bases
    assert len(contas.ugs) == 35
    assert sum(len(ug.uos) for ug in contas.ugs.values()) == 43
    assert contas.linhas > 38_000
    assert 1_900_000_000 < contas.total.valor_liquido < 2_200_000_000
    assert contas.data_min is not None
    assert contas.data_max is not None


def test_programas_sem_execucao(bases):
    ppa, contas = bases
    sem_execucao = {
        programa.codigo
        for programa in ppa.programas
        if not contas.ugs_do_programa(programa.codigo)
    }
    assert sem_execucao == SEM_EXECUCAO
    assert len(sem_execucao) == 13
    assert len(contas.programa_total) == 75
    assert set(contas.programa_total) - set(ppa.por_codigo) == {"6200"}


def test_ug_004(bases):
    ppa, contas = bases
    ug = contas.ugs["004"]
    assert ug.nome_oficial == "Fundo Municipal de Educação"
    assert len(ug.uos) == 2
    assert {codigo for uo in ug.uos.values() for codigo in uo.codigos} == {"001"}
    assert "FUNDO MUNICIPAL DE EDUCACAO" in ug.uos
    assert "SECRETARIA MUNICIPAL DE EDUCACAO" in ug.uos
    assert ug.uos["FUNDO MUNICIPAL DE EDUCACAO"].nome_oficial == "Fundo Municipal de Educação"
    codigos = {codigo for codigo, codigo_ug in contas.programa_ug if codigo_ug == "004"}
    assert codigos == {"6017", "6018", "6019", "6020", "6021", "6023", "6024", "6025"}
    assert "6022" not in contas.programa_total
    assert contas.total_programa("6024") > 0
    assert contas.ugs_do_programa("6024") == ["004", "016"]


def test_ug_001_uos(bases):
    _ppa, contas = bases
    ug = contas.ugs["001"]
    assert len(ug.uos) == 6
    assert ug.uos["CONTROLADORIA GERAL DO MUNICIPIO"].nome_oficial == (
        "Controladoria Geral do Município"
    )


def test_config_mapas():
    assert config.nome_ug("004") == "Fundo Municipal de Educação"
    assert config.slug_ug("004") == "educacao"
    assert set(config.PROGRAMAS_SEM_UG) == {"6005", "6083", "6084", "6085"}
    assert set(config.PROGRAMAS_EXCLUIDOS) == {"6034-A", "6066-A"}
    assert config.DONOS_COMPARTILHADOS["6013"] == "001"


@pytest.mark.parametrize(
    ("ug", "esperado"),
    [
        ("004", "Fundo Municipal de Educação"),
        ("003", "Fundo Municipal de Saúde"),
        ("016", "FUNDEB"),
        ("041", "Fundo Municipal de Defesa do Consumidor"),
    ],
)
def test_nomes_uo_oficiais(bases, ug, esperado):
    _ppa, contas = bases
    nomes = {uo.nome_oficial for uo in contas.ugs[ug].uos.values()}
    assert esperado in nomes


def test_execucao_acao_natureza(bases):
    _ppa, contas = bases
    execucao = contas.execucao("6024", "004")
    assert execucao.por_acao_natureza
    assert abs(sum(execucao.por_acao_natureza.values()) - execucao.valor_liquido) < 0.01
    assert all(len(chave) == 2 for chave in execucao.por_acao_natureza)
