"""Copia HTML/PDF gerados para o repo de site, preservando o .git."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def _workspace() -> Path:
    projeto = Path(__file__).resolve().parents[1]
    return projeto.parents[1]


def _origem_padrao(ano: int) -> Path:
    projeto = Path(__file__).resolve().parents[1]
    dados = projeto.parents[1] / "_dados"
    base = dados / "Saida" / "raiox"
    return base if ano == 2026 else base / str(ano)


def _site_padrao() -> Path:
    return _workspace() / "_publico" / "raiox-ppa-site"


def _prefixo_padrao(ano: int) -> str:
    return "" if ano == 2026 else str(ano)


def _injetar(html: str, *, indice: bool, pdf_nome: str = "") -> str:
    if indice:
        if 'href="pdf/index.html"' not in html:
            html = html.replace(
                '<a class="btn" href="#ugs">Mapa de UGs</a>',
                '<a class="btn" href="#ugs">Mapa de UGs</a>'
                '<a class="btn" href="pdf/index.html">PDFs</a>',
            )
        return html
    if pdf_nome and f'href="pdf/{pdf_nome}"' not in html:
        html = html.replace(
            '<button class="btn primary" type="button" data-print>Imprimir / PDF</button>',
            '<button class="btn primary" type="button" data-print>Imprimir / PDF</button>'
            f'<a class="btn" href="pdf/{pdf_nome}">Baixar PDF</a>',
        )
    return html


def _pdf_index(pasta: Path) -> None:
    pdfs = sorted(pasta.glob("*.pdf"))
    links = "".join(f'<li><a href="{p.name}">{p.stem}</a></li>' for p in pdfs)
    (pasta / "index.html").write_text(
        f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PDFs - Raio-X PPA</title>
<style>body{{font-family:"Segoe UI",Arial,sans-serif;background:#eef2f5;color:#12263a;margin:0;padding:32px}}main{{max-width:900px;margin:auto;background:#fff;border:1px solid #d7e0e8;border-radius:14px;padding:24px}}h1{{margin-top:0}}a{{color:#0f766e}}li{{margin:6px 0}}</style>
</head><body><main><h1>PDFs do Raio-X Técnico do PPA</h1>
<p><a href="../index.html">Voltar ao índice</a></p><ul>{links}</ul>
<p class="small">Produto interno; não é o RAM oficial.</p></main></body></html>""",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publica o raio-x no repo de site.")
    parser.add_argument("--ano", type=int, default=2026, choices=[2026, 2027, 2028, 2029])
    parser.add_argument("--origem", type=Path, default=None)
    parser.add_argument("--site", type=Path, default=None)
    parser.add_argument("--prefixo", default=None)
    parser.add_argument("--publicar", action="store_true", help="commit e push no repo do site")
    args = parser.parse_args(argv)

    origem = Path(args.origem) if args.origem else _origem_padrao(args.ano)
    site = Path(args.site) if args.site else _site_padrao()
    prefixo = args.prefixo if args.prefixo is not None else _prefixo_padrao(args.ano)
    destino = site / prefixo if prefixo else site
    if not origem.is_dir():
        raise SystemExit(f"Pasta de origem não encontrada: {origem}")
    if not (origem / "index.html").exists():
        raise SystemExit(f"index.html não encontrado em {origem}")

    destino.mkdir(parents=True, exist_ok=True)
    for antigo in destino.glob("ug_*.html"):
        antigo.unlink()
    for html in sorted(origem.glob("*.html")):
        conteudo = html.read_text(encoding="utf-8")
        pdf_nome = f"{html.stem}.pdf" if html.name != "index.html" else ""
        conteudo = _injetar(conteudo, indice=html.name == "index.html", pdf_nome=pdf_nome)
        (destino / html.name).write_text(conteudo, encoding="utf-8")

    pdf_destino = destino / "pdf"
    if pdf_destino.exists():
        shutil.rmtree(pdf_destino)
    shutil.copytree(origem / "pdf", pdf_destino)
    _pdf_index(pdf_destino)

    status = {
        "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "versao": datetime.now().strftime("%Y%m%d"),
        "ano": args.ano,
    }
    (destino / "status.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if destino != site:
        status_raiz = {**status, "path": f"/{prefixo}/"}
        (site / "status.json").write_text(
            json.dumps(status_raiz, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    (site / ".nojekyll").write_text("", encoding="utf-8")
    fonte = ""
    manifesto = origem / "manifest.json"
    if manifesto.exists():
        try:
            dados = json.loads(manifesto.read_text(encoding="utf-8"))
            fonte = Path(dados.get("fontes", {}).get("contas", "")).name
        except (OSError, json.JSONDecodeError):
            fonte = ""
    (destino / "README.md").write_text(
        f"""# Raio-X Técnico do PPA — {args.ano}

Versão publicada em {datetime.now():%d/%m/%Y} a partir de dados públicos do PPA
2026-2029 e das contas {args.ano}{f" (`{fonte}`)" if fonte else ""}.

- `index.html` — índice, ranking e mapa das 35 UGs.
- `ug_*.html` — 35 páginas por UG, com o detalhamento
  programa → ação LOA (projeto/atividade) → natureza.
- `pdf/` — 35 PDFs por UG + PDF do índice.

Código: https://github.com/angelojordy-svg/raiox-ppa

Produto interno de diagnóstico; não é o RAM oficial nem o resumo executivo de contas.
""",
        encoding="utf-8",
    )
    print(f"Site atualizado em {destino}")
    if args.publicar:
        alteracoes = subprocess.run(
            ["git", "-C", str(site), "status", "--porcelain"],
            capture_output=True,
            text=True,
        )
        if not alteracoes.stdout.strip():
            print("Nada novo para publicar.")
            return 0
        passos = [
            ["git", "-C", str(site), "add", "-A"],
            [
                "git",
                "-C",
                str(site),
                "commit",
                "-m",
                f"site: atualiza raio-x {args.ano} {status['gerado_em']}",
            ],
            ["git", "-C", str(site), "push"],
        ]
        for comando in passos:
            resultado = subprocess.run(comando, capture_output=True, text=True)
            if resultado.returncode != 0:
                print(resultado.stdout.strip())
                print(resultado.stderr.strip())
                return resultado.returncode
        print("Site publicado no GitHub.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
