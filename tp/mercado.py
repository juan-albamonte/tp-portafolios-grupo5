"""Foto del mercado desde FRED: tasa corta, TIPS a 10 años e inflación implícita."""
import json
import urllib.request
from collections.abc import Callable
from pathlib import Path

SERIES = {
    "tasa_corta": "DTB3",      # letra del Tesoro a 3 meses
    "tips_10": "DFII10",       # rendimiento real del TIPS a 10 años
    "breakeven_10": "T10YIE",  # inflación implícita a 10 años
}


def bajar_fred(serie: str) -> str:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={serie}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode()


def ultimo_valor(csv: str) -> tuple[str, float]:
    """Último dato disponible (FRED marca los faltantes con '.'), en decimales."""
    for linea in reversed(csv.strip().splitlines()[1:]):
        fecha, valor = linea.split(",")[:2]
        if valor not in (".", ""):
            return fecha, float(valor) / 100
    raise ValueError("serie vacía")


def foto_mercado(archivo: Path, bajador: Callable[[str], str] = bajar_fred) -> dict:
    archivo = Path(archivo)
    if archivo.exists():
        return json.loads(archivo.read_text())
    foto = {}
    for nombre, serie in SERIES.items():
        fecha, valor = ultimo_valor(bajador(serie))
        foto[nombre] = {"serie": serie, "fecha": fecha, "valor": valor}
    archivo.write_text(json.dumps(foto, indent=2))
    return foto
