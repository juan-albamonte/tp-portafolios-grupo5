"""Convierte un .md de docs/entregables a .docx con pandoc y el documento de referencia.

Antes normaliza el Markdown para que pandoc no junte listas con el párrafo anterior:
agrega una línea en blanco antes de cada lista que sigue a un párrafo.

Uso: python docs/entregables/md_a_docx.py docs/entregables/politica_de_inversion.md [--toc]
"""
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ITEM = re.compile(r"^\s*(?:[-*+]|\d+\.)\s")


def normalizar(texto: str) -> str:
    """Línea en blanco antes de cada lista que arranca justo después de un párrafo (fuera de tablas)."""
    out: list[str] = []
    for linea in texto.split("\n"):
        previa = out[-1] if out else ""
        if (ITEM.match(linea) and previa.strip() and not ITEM.match(previa)
                and not previa.lstrip().startswith(("|", "#")) and not previa.startswith("  ")):
            out.append("")
        out.append(linea)
    return "\n".join(out)


def convertir(md: Path, toc: bool = False) -> Path:
    md = Path(md).resolve()
    texto = normalizar(md.read_text(encoding="utf-8"))
    md.write_text(texto, encoding="utf-8")
    salida = md.with_suffix(".docx")
    cmd = ["pandoc", str(md), "--reference-doc", str(AQUI / "referencia.docx"), "-o", str(salida),
           "--resource-path", f"{md.parent}:{AQUI.parent.parent}"]
    if toc:
        cmd += ["--toc", "--toc-depth=2"]
    subprocess.run(cmd, check=True)
    subprocess.run(["zip", "-qd", str(salida), "*/"], check=False, capture_output=True)
    declarar_png(salida)
    return salida


def declarar_png(docx: Path) -> None:
    """Agrega <Default Extension="png"> a [Content_Types].xml (pandoc usa Override por imagen; algunos lectores piden Default)."""
    import shutil
    import tempfile
    import zipfile
    with zipfile.ZipFile(docx) as z:
        tipos = z.read("[Content_Types].xml").decode("utf-8")
        if 'Extension="png"' in tipos or not any(n.endswith(".png") for n in z.namelist()):
            return
        tipos = tipos.replace('<Default Extension="xml"', '<Default Extension="png" ContentType="image/png" /><Default Extension="xml"', 1)
        tmp = Path(tempfile.mkstemp(suffix=".docx")[1])
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
            for item in z.infolist():
                out.writestr(item, tipos if item.filename == "[Content_Types].xml" else z.read(item.filename))
    shutil.move(tmp, docx)


if __name__ == "__main__":
    print(convertir(Path(sys.argv[1]), toc="--toc" in sys.argv))
