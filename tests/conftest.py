from __future__ import annotations

import pytest

from pmp_raiox import config
from pmp_raiox.dados import carregar_contas, carregar_ppa
from pmp_raiox.modelo import construir_relatorio
from pmp_raiox.resultados import Resultados


@pytest.fixture(scope="session")
def bases():
    if not config.PPA_PADRAO.exists():
        pytest.skip("PPA 2026-2029 não encontrado")
    ppa = carregar_ppa()
    try:
        contas = carregar_contas()
    except FileNotFoundError:
        pytest.skip("despesas_programas_2026_*.xlsx não encontrado")
    return ppa, contas


@pytest.fixture(scope="session")
def relatorio(bases):
    ppa, contas = bases
    return construir_relatorio(ppa, contas, Resultados())
