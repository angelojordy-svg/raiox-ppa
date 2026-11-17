"""Orquestracao da renderizacao HTML do raio-x."""

from __future__ import annotations

from .html_index import gerar_html_index, gerar_pagina_index
from .html_ug import gerar_html_ug, gerar_pagina_ug

__all__ = [
    "gerar_html_index",
    "gerar_html_ug",
    "gerar_pagina_index",
    "gerar_pagina_ug",
]
