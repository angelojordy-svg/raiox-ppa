"""Perfis anuais do raio-x.

Cada perfil define o ano, o período do PPA, o arquivo de contas esperado, a pasta de
saída, as colunas de meta e os mapas de referência. O PPA 2026-2029 é o mesmo para
2026 a 2029; o que muda é a LOA/contas e a meta disponível no PPA.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import config


@dataclass(frozen=True)
class PerfilAno:
    ano: int
    ppa_periodo: str
    ano_ppa: int
    rotulo_ano: str
    ppa_path: Path
    contas_glob: str
    saida_dir: Path
    entrada_dir: Path
    meta_ano_col: str
    meta_bloco_col: str
    meta_ano_label: str
    meta_bloco_label: str
    meta_ano_tipo: str
    ug_nomes: dict[str, str]
    ug_slugs: dict[str, str]
    uo_nomes: dict[tuple[str, str], str]
    programas_sem_execucao: dict[str, tuple[str, str]]
    programas_sem_ug: dict[str, str]
    programas_excluidos: dict[str, str]
    donos_compartilhados: dict[str, str]

    def nome_ug(self, codigo: str) -> str:
        return self.ug_nomes.get(codigo, codigo)

    def slug_ug(self, codigo: str) -> str:
        return self.ug_slugs.get(codigo, f"ug_{codigo}")

    def nome_uo(self, codigo_ug: str, nome_normalizado: str, nome_contas: str = "") -> str:
        return self.uo_nomes.get(
            (codigo_ug, nome_normalizado),
            nome_contas or nome_normalizado.title(),
        )

    @property
    def titulo_ppa(self) -> str:
        return f"PPA {self.ppa_periodo}"

    @property
    def titulo(self) -> str:
        return f"Raio-X Técnico do {self.titulo_ppa}"

    @property
    def usa_meta_bloco(self) -> bool:
        return bool(self.meta_bloco_col and self.meta_bloco_label)


PERFIL_2026 = PerfilAno(
    ano=2026,
    ppa_periodo="2026-2029",
    ano_ppa=1,
    rotulo_ano="1º ano",
    ppa_path=config.PPA_PADRAO,
    contas_glob="despesas_programas_2026_*.xlsx",
    saida_dir=config.SAIDA,
    entrada_dir=config.ENTRADA,
    meta_ano_col="meta 2026",
    meta_bloco_col="meta 2027 2029",
    meta_ano_label="Meta 2026",
    meta_bloco_label="Meta 2027-2029",
    meta_ano_tipo="anual",
    ug_nomes=config.UG_NOMES,
    ug_slugs=config.UG_SLUGS,
    uo_nomes=config.UO_NOMES_OFICIAIS,
    programas_sem_execucao=config.PROGRAMAS_SEM_EXECUCAO,
    programas_sem_ug=config.PROGRAMAS_SEM_UG,
    programas_excluidos=config.PROGRAMAS_EXCLUIDOS,
    donos_compartilhados=config.DONOS_COMPARTILHADOS,
)

PERFIL_2027 = PerfilAno(
    ano=2027,
    ppa_periodo="2026-2029",
    ano_ppa=2,
    rotulo_ano="2º ano",
    ppa_path=config.PPA_PADRAO,
    contas_glob="despesas_programas_2027_*.xlsx",
    saida_dir=config.SAIDA / "2027",
    entrada_dir=config.SAIDA / "2027" / "entrada",
    meta_ano_col="meta 2027 2029",
    meta_bloco_col="",
    meta_ano_label="Meta 2027-2029 (bloco)",
    meta_bloco_label="",
    meta_ano_tipo="bloco",
    ug_nomes=config.UG_NOMES,
    ug_slugs=config.UG_SLUGS,
    uo_nomes=config.UO_NOMES_OFICIAIS,
    programas_sem_execucao=config.PROGRAMAS_SEM_EXECUCAO,
    programas_sem_ug=config.PROGRAMAS_SEM_UG,
    programas_excluidos=config.PROGRAMAS_EXCLUIDOS,
    donos_compartilhados=config.DONOS_COMPARTILHADOS,
)

PERFIL_2028 = PerfilAno(
    ano=2028,
    ppa_periodo="2026-2029",
    ano_ppa=3,
    rotulo_ano="3º ano",
    ppa_path=config.PPA_PADRAO,
    contas_glob="despesas_programas_2028_*.xlsx",
    saida_dir=config.SAIDA / "2028",
    entrada_dir=config.SAIDA / "2028" / "entrada",
    meta_ano_col="meta 2027 2029",
    meta_bloco_col="",
    meta_ano_label="Meta 2027-2029 (bloco)",
    meta_bloco_label="",
    meta_ano_tipo="bloco",
    ug_nomes=config.UG_NOMES,
    ug_slugs=config.UG_SLUGS,
    uo_nomes=config.UO_NOMES_OFICIAIS,
    programas_sem_execucao=config.PROGRAMAS_SEM_EXECUCAO,
    programas_sem_ug=config.PROGRAMAS_SEM_UG,
    programas_excluidos=config.PROGRAMAS_EXCLUIDOS,
    donos_compartilhados=config.DONOS_COMPARTILHADOS,
)

PERFIL_2029 = PerfilAno(
    ano=2029,
    ppa_periodo="2026-2029",
    ano_ppa=4,
    rotulo_ano="4º ano",
    ppa_path=config.PPA_PADRAO,
    contas_glob="despesas_programas_2029_*.xlsx",
    saida_dir=config.SAIDA / "2029",
    entrada_dir=config.SAIDA / "2029" / "entrada",
    meta_ano_col="meta 2027 2029",
    meta_bloco_col="",
    meta_ano_label="Meta 2027-2029 (bloco)",
    meta_bloco_label="",
    meta_ano_tipo="bloco",
    ug_nomes=config.UG_NOMES,
    ug_slugs=config.UG_SLUGS,
    uo_nomes=config.UO_NOMES_OFICIAIS,
    programas_sem_execucao=config.PROGRAMAS_SEM_EXECUCAO,
    programas_sem_ug=config.PROGRAMAS_SEM_UG,
    programas_excluidos=config.PROGRAMAS_EXCLUIDOS,
    donos_compartilhados=config.DONOS_COMPARTILHADOS,
)

PERFIS = {
    "2026": PERFIL_2026,
    "2027": PERFIL_2027,
    "2028": PERFIL_2028,
    "2029": PERFIL_2029,
}


def perfil_por_ano(ano: int | str) -> PerfilAno:
    chave = str(ano)
    if chave not in PERFIS:
        raise ValueError(f"Ano sem perfil: {ano}. Perfis disponíveis: {', '.join(PERFIS)}")
    return PERFIS[chave]
