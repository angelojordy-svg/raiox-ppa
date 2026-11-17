"""Gera PDFs por UG pela impressão headless do Edge/Chrome."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BROWSERS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
]


def _browser() -> Path | None:
    for caminho in BROWSERS:
        if caminho.is_file():
            return caminho
    for nome in ("msedge", "chrome", "google-chrome", "chromium"):
        achado = shutil.which(nome)
        if achado:
            return Path(achado)
    return None


def _saida_padrao() -> Path:
    projeto = Path(__file__).resolve().parents[1]
    dados = Path(os.environ.get("PMP_DATA_ROOT", projeto.parents[1] / "_dados"))
    return dados / "Saida" / "raiox"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gera PDFs do raio-x pelo navegador.")
    parser.add_argument("--saida", type=Path, default=None, help="Pasta com os HTMLs.")
    parser.add_argument("--pdf", type=Path, default=None, help="Pasta de destino dos PDFs.")
    args = parser.parse_args(argv)

    base = Path(args.saida) if args.saida else _saida_padrao()
    destino = Path(args.pdf) if args.pdf else base / "pdf"
    if not base.is_dir():
        raise SystemExit(f"Pasta de saída não encontrada: {base}")

    navegador = _browser()
    if navegador is None:
        raise SystemExit("Edge/Chrome não encontrado. Use a impressão do HTML no navegador.")

    htmls = sorted(base.glob("*.html"))
    if not htmls:
        raise SystemExit(f"Nenhum HTML encontrado em {base}")

    destino.mkdir(parents=True, exist_ok=True)
    gerados: list[Path] = []
    for html in htmls:
        pdf = destino / f"{html.stem}.pdf"
        comando = [
            str(navegador),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf}",
            html.as_uri(),
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        if resultado.returncode != 0 or not pdf.exists():
            print(f"FALHOU: {html.name}")
            if resultado.stderr:
                print(resultado.stderr.strip()[:500])
            continue
        gerados.append(pdf)
        print(pdf)

    paginas: dict[str, int] = {}
    try:
        from pypdf import PdfReader

        for pdf in gerados:
            paginas[pdf.name] = len(PdfReader(str(pdf)).pages)
    except Exception:
        paginas = {}

    manifesto_path = base / "manifest.json"
    if manifesto_path.exists():
        try:
            manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
            manifesto["pdf"] = {
                "dir": str(destino),
                "n_arquivos": len(gerados),
                "gerado_em": datetime.now().isoformat(timespec="seconds"),
                "navegador": str(navegador),
                "arquivos": [
                    {"arquivo": pdf.name, "paginas": paginas.get(pdf.name)}
                    for pdf in gerados
                ],
            }
            manifesto_path.write_text(
                json.dumps(manifesto, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except (OSError, json.JSONDecodeError):
            pass

    print(f"{len(gerados)} PDF(s) gerados em {destino}")
    return 0 if len(gerados) == len(htmls) else 1


if __name__ == "__main__":
    raise SystemExit(main())
