"""Pedido de Juan (21/11): el impuesto a la herencia de EE.UU. no va en ningún entregable."""
import re
import zipfile
from pathlib import Path

import pytest

ENT = Path(__file__).resolve().parent.parent / "docs" / "entregables"
TEXTOS = ["politica_de_inversion.md", "desarrollo.md", "guion_presentacion.md", "deck/build_deck.js",
          "desarrollo/00_resumen.md", "desarrollo/01_metodologia.md", "desarrollo/08_limitaciones.md"]
BINARIOS = ["deck.pptx", "politica_de_inversion.docx", "desarrollo.docx", "guion_presentacion.docx"]
PROHIBIDO = re.compile(r"herencia|herederos|sucesori", re.IGNORECASE)


@pytest.mark.parametrize("archivo", TEXTOS)
def test_sin_herencia_en_los_textos(archivo):
    assert not PROHIBIDO.search((ENT / archivo).read_text(encoding="utf-8")), archivo


@pytest.mark.parametrize("archivo", BINARIOS)
def test_sin_herencia_en_los_archivos_entregados(archivo):
    with zipfile.ZipFile(ENT / archivo) as z:
        xml = " ".join(z.read(n).decode("utf-8", "ignore") for n in z.namelist() if n.endswith(".xml"))
    texto = re.sub(r"<[^>]+>", "", xml)
    assert not PROHIBIDO.search(texto), archivo
