"""CLI do raio-x: gera HTML, planilha de apoio e manifesto."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .dados import carregar_contas, carregar_ppa
from .html import gerar_html_index, gerar_html_ug
from .modelo import construir_relatorio
from .perfil import perfil_por_ano
from .resultados import carregar_resultados, criar_templates
from .texto import texto
from .xlsx import gerar_xlsx


def _codigos_ug(valores: list[str]) -> set[str]:
    codigos: set[str] = set()
    for valor in valores:
        for parte in texto(valor).replace(";", ",").split(","):
            parte = parte.strip()
            if parte:
                codigos.add(parte.zfill(3))
    return codigos


def _nome_xlsx(codigos: set[str], todas: bool, perfil) -> str:
    if todas or len(codigos) == len(perfil.ug_nomes):
        return "raiox_apoio_completo.xlsx"
    if len(codigos) == 1:
        return f"raiox_apoio_ug{next(iter(codigos))}.xlsx"
    return "raiox_apoio_selecao.xlsx"


def _manifesto(
    relatorio,
    *,
    codigos: set[str],
    todas: bool,
    saidas: list[Path],
    entrada: Path,
    resultados: Path | None,
) -> dict:
    return {
        "produto": relatorio.perfil.titulo,
        "ano": relatorio.perfil.ano,
        "ppa_periodo": relatorio.perfil.ppa_periodo,
        "meta_ano_label": relatorio.perfil.meta_ano_label,
        "versao": __version__,
        "gerado_em": relatorio.gerado_em.isoformat(timespec="seconds"),
        "fontes": {
            "ppa": str(relatorio.fontes.get("ppa", relatorio.perfil.ppa_path)),
            "contas": str(relatorio.fontes.get("contas", relatorio.contas.arquivo)),
            "periodo_contas": {
                "inicio": str(relatorio.contas.data_min),
                "fim": str(relatorio.contas.data_max),
            },
            "resultados": str(resultados) if resultados else str(entrada),
        },
        "escopo": {
            "todas": todas,
            "ugs": sorted(codigos),
            "n_ugs": len(codigos),
        },
        "contagens": {
            "programas": relatorio.n_programas,
            "indicadores": relatorio.n_indicadores,
            "acoes": relatorio.n_acoes,
            "ugs": len(relatorio.ugs),
            "programas_com_execucao": relatorio.n_programas_com_execucao,
            "programas_sem_execucao": relatorio.n_programas_sem_execucao,
            "programas_sem_execucao_mapeado": relatorio.n_programas_sem_execucao_mapeado,
            "programas_sem_ug": relatorio.n_sem_ug,
            "programas_excluidos": relatorio.n_excluidos,
            "programas_sem_indicador": relatorio.n_sem_indicador,
            "programas_compartilhados": relatorio.n_compartilhados,
            "resultados_indicadores": relatorio.n_resultados_indicadores,
            "resultados_acoes": relatorio.n_resultados_acoes,
            "evidencias": relatorio.n_evidencias,
        },
        "execucao": {
            "total_geral": round(relatorio.total_geral, 2),
            "total_ppa": round(relatorio.total_ppa, 2),
            "total_fora_ppa": round(relatorio.total_fora_ppa, 2),
            "liquidacao": True,
            "empenhado_pago_disponivel": False,
        },
        "alertas_globais": [
            {
                "severidade": alerta.severidade,
                "tipo": alerta.tipo,
                "mensagem": alerta.mensagem,
            }
            for alerta in relatorio.alertas_globais
        ],
        "saidas": [str(saida) for saida in saidas],
        "entrada": str(entrada),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gera o Raio-X Técnico do PPA por UG e por ano."
    )
    parser.add_argument(
        "--ano",
        default="2026",
        choices=["2026", "2027", "2028", "2029"],
        help="Ano do exercício. Padrão: 2026.",
    )
    parser.add_argument(
        "--ug",
        action="append",
        default=[],
        help="Código(s) da UG para gerar. Pode repetir ou separar por vírgula. Padrão: 004.",
    )
    parser.add_argument(
        "--todas",
        action="store_true",
        help="Gera todas as 35 UGs (usar somente após validar o protótipo).",
    )
    parser.add_argument("--ppa", type=Path, default=None, help="Caminho do PPA.")
    parser.add_argument("--contas", type=Path, default=None, help="Caminho do Consolidado do ano.")
    parser.add_argument(
        "--resultados",
        type=Path,
        default=None,
        help="Pasta com resultados_indicadores.csv, resultados_acoes.csv e evidencias.csv.",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=None,
        help="Pasta de saída. Padrão: a pasta do perfil do ano.",
    )
    parser.add_argument(
        "--sem-xlsx",
        action="store_true",
        help="Não gera a planilha de apoio.",
    )
    parser.add_argument(
        "--sem-html",
        action="store_true",
        help="Não gera HTML.",
    )
    args = parser.parse_args(argv)
    perfil = perfil_por_ano(args.ano)

    codigos = set(perfil.ug_nomes) if args.todas else (_codigos_ug(args.ug) or {"004"})
    desconhecidas = sorted(codigos - set(perfil.ug_nomes))
    if desconhecidas:
        parser.error(f"UG(s) desconhecida(s): {', '.join(desconhecidas)}")

    ppa = carregar_ppa(args.ppa, perfil)
    contas = carregar_contas(args.contas, perfil)
    pasta_resultados = args.resultados or perfil.entrada_dir
    resultados = carregar_resultados(pasta_resultados, perfil)
    relatorio = construir_relatorio(
        ppa,
        contas,
        resultados,
        fontes={
            "ppa": Path(args.ppa) if args.ppa else perfil.ppa_path,
            "contas": Path(args.contas) if args.contas else contas.arquivo,
        },
        perfil=perfil,
    )

    destino = Path(args.saida) if args.saida else perfil.saida_dir
    destino.mkdir(parents=True, exist_ok=True)
    entrada = Path(pasta_resultados)
    entrada.mkdir(parents=True, exist_ok=True)
    templates = criar_templates(entrada, perfil)

    saidas: list[Path] = []
    if not args.sem_html:
        for codigo in sorted(codigos):
            saidas.append(gerar_html_ug(relatorio, codigo, destino))
        saidas.append(gerar_html_index(relatorio, destino, codigos))

    if not args.sem_xlsx:
        saidas.append(
            gerar_xlsx(
                relatorio,
                destino,
                codigos_ug=codigos,
                nome=_nome_xlsx(codigos, args.todas, perfil),
            )
        )

    manifesto = _manifesto(
        relatorio,
        codigos=codigos,
        todas=args.todas,
        saidas=saidas,
        entrada=entrada,
        resultados=args.resultados,
    )
    caminho_manifesto = destino / "manifest.json"
    caminho_manifesto.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    saidas.append(caminho_manifesto)

    print("Raio-X gerado:")
    for saida in saidas:
        print(f"  {saida}")
    if templates:
        print("Modelos de entrada criados:")
        for template in templates:
            print(f"  {template}")
    print(
        f"Ano: {relatorio.perfil.ano} | Contas: {contas.arquivo.name} | "
        f"{contas.linhas} linhas | "
        f"liquidado {relatorio.total_geral:,.2f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
