from __future__ import annotations

import csv
from pathlib import Path

from pmp_raiox.html import gerar_html_ug
from pmp_raiox.modelo import construir_relatorio
from pmp_raiox.resultados import (
    CABECALHO_ACOES,
    CABECALHO_EVIDENCIAS,
    CABECALHO_INDICADORES,
    carregar_resultados,
    criar_templates,
)


def _csv(caminho: Path, cabecalho: list[str], linhas: list[list[str]]) -> None:
    with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)


def test_templates(tmp_path):
    criados = criar_templates(tmp_path)
    assert (tmp_path / "resultados_indicadores.csv").exists()
    assert (tmp_path / "resultados_acoes.csv").exists()
    assert (tmp_path / "evidencias.csv").exists()
    assert (tmp_path / "LEIAME.txt").exists()
    assert len(criados) >= 3


def test_carrega_resultados(bases, tmp_path):
    ppa, contas = bases
    _csv(
        tmp_path / "resultados_indicadores.csv",
        CABECALHO_INDICADORES,
        [["6018", "1", "50000", "", "alunos", "31/12/2026", "Censo", "Cobertura", "", "E1"]],
    )
    _csv(
        tmp_path / "resultados_acoes.csv",
        CABECALHO_ACOES,
        [["6018", "43", "40000", "50123", "alunos", "31/12/2026", "SEDUC", "Em execução", "", "Parcial", "Ampliar", "E1"]],
    )
    _csv(
        tmp_path / "evidencias.csv",
        CABECALHO_EVIDENCIAS,
        [["E1", "Relatório de atendimento", "documento", "https://example.org/e1", "31/12/2026", "SEMED"]],
    )
    resultados = carregar_resultados(tmp_path)
    assert not resultados.vazio
    assert resultados.indicador("6018", "1") is not None
    assert resultados.acao("6018", "43") is not None
    assert resultados.evidencia("E1") is not None
    relatorio = construir_relatorio(ppa, contas, resultados)
    assert relatorio.n_resultados_indicadores >= 1
    assert relatorio.n_resultados_acoes >= 1
    assert relatorio.n_evidencias == 1
    html = gerar_html_ug(relatorio, "004", tmp_path / "html")
    conteudo = html.read_text(encoding="utf-8")
    assert "50000" in conteudo
    assert "40000" in conteudo
    assert "https://example.org/e1" in conteudo
