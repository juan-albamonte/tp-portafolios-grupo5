"""Pedido de Juan (21/11): nada semiabierto en los cinco entregables (deck, política, desarrollo, Excel y
guion). Ni "a verificar", ni "pendiente", ni marcas de borrador."""
import re
import zipfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
ENT = RAIZ / "docs" / "entregables"
TEXTOS = ["politica_de_inversion.md", "desarrollo.md", "guion_presentacion.md", "deck/build_deck.js"]
BINARIOS = [ENT / "deck.pptx", ENT / "politica_de_inversion.docx", ENT / "desarrollo.docx",
            ENT / "guion_presentacion.docx", RAIZ / "outputs" / "TP_Grupo5.xlsx"]
# "TODO" y "XX" distinguen mayúsculas: "todo" es castellano.
PROHIBIDO = re.compile(r"(?i:verificar|pendiente|TBD|\[CIFRA|\?\?)|TODO|XX")


def problemas(texto: str) -> list[str]:
    return [texto[max(0, m.start() - 40):m.end() + 40] for m in PROHIBIDO.finditer(texto)]


def test_el_patron_distingue_todo_de_TODO():
    assert not problemas("todo descontado") and problemas("TODO: revisar") and problemas("a verificar")


@pytest.mark.parametrize("archivo", TEXTOS)
def test_textos_sin_pendientes(archivo):
    assert not problemas((ENT / archivo).read_text(encoding="utf-8")), archivo


@pytest.mark.parametrize("archivo", BINARIOS, ids=lambda p: p.name)
def test_archivos_entregados_sin_pendientes(archivo):
    if not archivo.exists():
        pytest.skip(f"falta {archivo.name}")
    with zipfile.ZipFile(archivo) as z:
        xml = " ".join(z.read(n).decode("utf-8", "ignore") for n in z.namelist() if n.endswith(".xml"))
    texto = re.sub(r"<[^>]+>", " ", xml)
    assert not problemas(texto), (archivo.name, problemas(texto)[:3])
