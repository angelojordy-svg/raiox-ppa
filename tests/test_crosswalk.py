from __future__ import annotations

from pathlib import Path

from pmp_raiox.crosswalk import (
    carregar_crosswalk,
    criar_template_crosswalk,
    refs_para,
)
from pmp_raiox.modelo import construir_relatorio
from pmp_raiox.resultados import Resultados
from pmp_raiox.texto import similaridade_nomes


def test_similaridade():
    assert similaridade_nomes(
        "Remuneração do Magistério do Ensino Fundamental",
        "Remuneração do Magistério do Ensino Fundamental",
    ) == 1.0
    assert 0.0 < similaridade_nomes("Dívida Fundada Interna", "Dívida Fundada Externa") < 1.0
    assert similaridade_nomes("", "qualquer") == 0.0


def test_template(tmp_path):
    criados = criar_template_crosswalk(tmp_path)
    assert (tmp_path / "crosswalk_loa.csv").exists()
    assert (tmp_path / "LEIAME_CROSSWALK.txt").exists()
    assert len(criados) == 2
    assert "codigo_programa" in (tmp_path / "crosswalk_loa.csv").read_text(encoding="utf-8-sig")


def test_automatico_e_manual(bases, tmp_path: Path):
    ppa, contas = bases
    programa = ppa.programa("6024")
    execucao = contas.execucao("6024", "004")

    refs = refs_para(programa, execucao, carregar_crosswalk(tmp_path / "ausente.csv"))
    assert refs["60"].codigo
    assert refs["60"].origem == "auto"
    assert refs["60"].valor > 0

    manual = tmp_path / "crosswalk_loa.csv"
    manual.write_text(
        "codigo_programa;n_acao;codigo_projeto_atividade;observacao\n"
        "6024;60;9.999;teste manual\n",
        encoding="utf-8",
    )
    refs2 = refs_para(programa, execucao, carregar_crosswalk(manual))
    assert refs2["60"].codigo == "9.999"
    assert refs2["60"].origem == "manual"


def test_relatorio_crosswalk(bases):
    ppa, contas = bases
    relatorio = construir_relatorio(ppa, contas, Resultados())
    ug = relatorio.ug("004")
    programa = next(p for p in ug.programas if p.codigo == "6024")
    assert programa.loa_refs["60"].codigo
    assert relatorio.crosswalk_resumo["total"] > 0
    assert any(a.tipo == "crosswalk_loa" for a in relatorio.alertas_globais)
