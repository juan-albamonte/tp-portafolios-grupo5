"""Arma docs/entregables/desarrollo.md (y .docx) a partir de los textos del EIC, las partes
propias del desarrollo, los gráficos de outputs/graficos y anexos generados desde los datos.

Uso (desde la raíz del proyecto, después de `python -m tp.correr`):
    .venv/bin/python docs/entregables/armar_desarrollo.py

Los textos de docs/eic/ son documentos de trabajo: acá se les sacan las notas internas del
proceso (fechas de checkpoints, rutas de salida) y se renombran los títulos. Cada reemplazo se
verifica: si el texto de origen cambia y un reemplazo deja de aplicar, el armado se corta.

Las cifras del modelo no se escriben a mano: los textos llevan marcadores {{ruta.en.cifras}} que se
reemplazan con outputs/cifras.json (mismo redondeo que el deck y la planilla). Un marcador que no
existe corta el armado.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
EIC = RAIZ / "docs" / "eic"
PARTES = AQUI / "desarrollo"
SALIDAS = RAIZ / "outputs"
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ))
from md_a_docx import convertir  # noqa: E402

CAPITULO = {
    "01_economia.md": "el capítulo de escenario económico",
    "02_industria.md": "el capítulo de industrias",
    "03_companias.md": "el capítulo de compañías",
    "04_cartera.md": "el capítulo de la cartera final",
    "05_retiro.md": "el capítulo de retiro y vivienda",
    "nota_esg.md": "el capítulo de calificación de sustentabilidad",
}

# (archivo, título nuevo, reemplazos exactos [(viejo, nuevo)], gráficos [(después de este encabezado, png, pie)])
EIC_ORDEN = [
    ("01_economia.md", "Escenario económico", [
        (" (`tp/mercado.py`)", ""),
        (" (`tp/escenario.py`)", ""),
        (" (`Mercado.exceso_esperado_benchmark`)", ""),
        (" (`tp/equilibrio.py`)", ""),
    ], []),
    ("02_industria.md", "Industrias y selección de acciones", [
        (" Los ratings de memoria de `candidatos.csv` (escala MSCI) ya no se usan en el entregable.", ""),
        ("**Actualización 3c (15/11):** la política fija", "**Regla de sustentabilidad:** la política fija"),
        ("En la 3b, antes de la regla ESG, la lista tenía 10 acciones con NVS y HD.",
         "Antes de fijar la regla de sustentabilidad, la lista tenía 10 acciones (6 europeas), con NVS y HD."),
        ("## Lista preliminar (9 acciones, 5 europeas)", "## Lista preliminar (9 acciones, 5 europeas, con la regla de sustentabilidad)"),
        ("Universo: las 31 acciones de `data/universo.csv`. Los datos de mercado vienen de Yahoo Finance (yfinance) al "
         "15/11/2026 y quedan guardados en `data/fundamentals.csv`. El código está en `tp/screening.py`.",
         "Universo: las 31 acciones que pasaron el filtro de exclusiones (anexo A). Los datos de mercado vienen de Yahoo "
         "Finance al 15/11/2026."),
        ("Está en `data/esg.csv`, con el link de cada empresa:", "Cada puntaje quedó registrado con el link de su empresa:"),
        ("Las reglas están en `tp/screening.py:preliminar` y la salida en `outputs/preliminar.csv`:", "Las reglas son:"),
    ], []),
    ("nota_esg.md", "La calificación de sustentabilidad", [
        ("Cada valor está en `data/esg.csv`, con el link a la página de la empresa.",
         "Cada valor quedó registrado con el link a la página de la empresa."),
        ("- La regla está en `tp/universo.py`, que además se niega a marcar como seleccionada una acción sin nota verificada.",
         "- El programa no permite seleccionar una acción sin nota verificada."),
    ], []),
    ("03_companias.md", "Compañías y opiniones de inversión", [
        ("Con las reglas del checkpoint 4 y del cierre (", "Con las reglas de la política de inversión ("),
        (", que tiene historia corta (checkpoint 2).", ", que tiene historia corta."),
        ("### Mastercard (MA): alcista (reemplaza a JPM, 16/11)", "### Mastercard (MA): alcista"),
        ("**Por qué el cambio.** JPMorgan tenía ESG 29: pasaba el mínimo de 25, pero es el mayor financiador",
         "**Por qué Mastercard y no JPMorgan.** JPMorgan tiene ESG 29: pasa el mínimo de 25, pero es el mayor financiador"),
        ("Mastercard tiene ESG 58, verificado en vivo en S&P Global", "Mastercard tiene ESG 58, verificado en S&P Global"),
        ("## Views (`data/views.csv`)", "## Opiniones de inversión (views)"),
        (" La escala (0,25) y c están en `tp/config.py`.", ""),
        ("Se calcula con el criterio de `tp/equilibrio.py`. ", "Se calcula con el criterio descripto en la metodología. "),
        ("## Consideradas, el optimizador no las tomó (checkpoint 4, 16/11)", "## Consideradas, el optimizador no las tomó"),
        ("Reemplazada por MA el 16/11:", "Descartada por criterio de sustentabilidad:"),
    ], []),
    ("04_cartera.md", "La cartera final", [
        ("Sale de `python -m tp.correr --etapa 4` (salida completa en `outputs/checkpoint4.txt`, pesos y USD en "
         "`outputs/cartera.csv`). ", ""),
    ], [
        ("## Por qué quedó así", "a_clases.png", "Cartera final contra el benchmark, por clase de activo"),
        ("## Por qué quedó así", "b_activos.png", "Las 12 posiciones de la cartera final"),
        ("## Contra las alternativas (mismas restricciones)", "c_frontera.png", "Las cinco carteras en el plano volatilidad y retorno"),
        ("## Contra el benchmark, con la misma vara", "d_sensibilidad.png", "Sensibilidad de los pesos por clase"),
        ("## Contra el benchmark, con la misma vara", "e_views.png", "Cuánto mueve la cartera cada opinión de inversión"),
    ]),
    ("05_retiro.md", "Retiro y vivienda", [
        ("Sale de `python -m tp.correr --etapa 5` (salida completa en `outputs/checkpoint5.txt`, números en "
         "`outputs/resumen.json`). ", ""),
    ], [
        ("## Retiro máximo seguro (sobrevive en 95 de cada 100 escenarios)", "g_ruina.png", "Probabilidad de quedarse sin dinero en vida"),
        ("## Retiro máximo seguro (sobrevive en 95 de cada 100 escenarios)", "f_abanico.png", "Patrimonio de la cartera por edad"),
        ("## Sensibilidades (ruina con gasto fijo)", "h_estres.png", "Estrés: el primer año repite 2008"),
    ]),
]


def figura(png: str, pie: str) -> str:
    return f"![{pie}](outputs/graficos/{png}){{width=100%}}\n"


def preparar_eic(archivo: str, titulo: str, reemplazos, graficos) -> str:
    s = (EIC / archivo).read_text(encoding="utf-8")
    for viejo, nuevo in reemplazos:
        if viejo not in s:
            raise ValueError(f"{archivo}: no encontré «{viejo[:60]}»")
        s = s.replace(viejo, nuevo)
    s = re.sub(r"\A# .*\n", f"# {titulo}\n", s, count=1)
    for nombre, cap in CAPITULO.items():
        s = s.replace(f"de `{nombre}`", "del " + cap.removeprefix("el "))  # "de el capítulo" → "del capítulo"
        s = s.replace(f"`{nombre}`", cap)
    # Gráficos antes del encabezado indicado (al final de la sección anterior).
    for encabezado, png, pie in graficos:
        if encabezado not in s:
            raise ValueError(f"{archivo}: no encontré el encabezado «{encabezado}»")
        s = s.replace(encabezado, figura(png, pie) + "\n" + encabezado, 1)
    return s.strip() + "\n"


# --------------------------------------------------------------------- anexos

def num(x, d=1, pct=False) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)) or x == "":
        return ""
    if isinstance(x, str):
        return x
    from decimal import Decimal
    from tp.formato import redondear  # mitad hacia arriba, como el resto de los entregables
    v = redondear(Decimal(repr(float(x))) * (100 if pct else 1), d)
    return (f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")) + ("%" if pct else "")


def tabla(df: pd.DataFrame) -> str:
    cab = "| " + " | ".join(df.columns) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    filas = ["| " + " | ".join(str(v).replace("|", "/") for v in fila) + " |" for fila in df.itertuples(index=False)]
    return "\n".join([cab, sep, *filas]) + "\n"


CLASE = {"liquidez": "Liquidez", "tesoro": "Tesoro", "tips": "Ajustados por inflación", "corporativos": "Corporativos",
         "acciones_eeuu": "Acciones EE.UU.", "acciones_europa": "Acciones Europa"}


def anexos() -> str:
    u = pd.read_csv(SALIDAS / "universo.csv", keep_default_na=False)
    ex = pd.read_csv(SALIDAS / "excluidos.csv", keep_default_na=False)
    sc = pd.read_csv(SALIDAS / "screening.csv")
    vw = pd.read_csv(RAIZ / "data" / "views.csv")
    ca = pd.read_csv(SALIDAS / "cartera.csv")
    res = json.loads((SALIDAS / "resumen.json").read_text(encoding="utf-8"))
    partes = ["# Anexos\n"]

    partes.append("## Anexo A. Universo de inversión\n\nCandidatos que pasaron el filtro de exclusiones y la nota mínima de "
                  "sustentabilidad. «En cartera» marca los 14 activos que entraron a la optimización.\n")
    a = pd.DataFrame({"Activo": u["ticker"], "Nombre": u["nombre"], "Clase": u["clase"].map(CLASE), "Tipo": u["tipo"],
                      "País": u["pais"], "Sector": u["sector"], "ESG S&P": u["esg_sp"], "En cartera": u["seleccionado"]})
    partes.append(tabla(a))

    partes.append("\n## Anexo B. Excluidos por el filtro de sustentabilidad\n")
    partes.append(tabla(pd.DataFrame({"Activo": ex["ticker"], "Nombre": ex["nombre"], "Clase": ex["clase"].map(CLASE),
                                      "Motivo": ex["motivo"]})))

    partes.append("\n## Anexo C. Screening de acciones\n\nPuntaje = promedio de los percentiles de cada métrica dentro de su "
                  "sector (0,5 = mitad del sector). Datos de Yahoo Finance al 15/11/2026.\n")
    sc = sc.sort_values(["sector", "puntaje"], ascending=[True, False])
    partes.append(tabla(pd.DataFrame({
        "Sector": sc["sector"], "Acción": sc["ticker"], "P/E forward": sc["pe_forward"].map(lambda x: num(x, 1)),
        "Crec. ganancias": sc["crecimiento_ganancias"].map(lambda x: num(x, 0, True)),
        "Margen operativo": sc["margen_operativo"].map(lambda x: num(x, 0, True)),
        "Deuda neta / EBITDA": sc["deuda_neta_ebitda"].map(lambda x: num(x, 1)),
        "ROE": sc["roe"].map(lambda x: num(x, 0, True)),
        "Dividendo + recompras": sc["retorno_accionista"].map(lambda x: num(x, 1, True)),
        "ESG S&P": sc["esg"].map(lambda x: num(x, 0)), "Puntaje": sc["puntaje"].map(lambda x: num(x, 2))})))

    partes.append("\n## Anexo D. Opiniones de inversión\n\nη: intensidad (+1 alcista, +2 muy alcista, −1 bajista). "
                  "u: incertidumbre relativa (1,5 = menos segura).\n")
    partes.append(tabla(pd.DataFrame({"Opinión": vw["id"], "Largo": vw["largo"], "Contra": vw["corto"],
                                      "η": vw["eta"].map(lambda x: f"{x:+d}".replace("-", "−")),
                                      "u": vw["u"].map(lambda x: num(x, 1)), "Frase": vw["frase"]})))

    partes.append("\n## Anexo E. Cartera final en dólares\n")
    partes.append(tabla(pd.DataFrame({"Clase": ca["clase"].map(CLASE), "Activo": ca["ticker"], "Nombre": ca["nombre"],
                                      "Peso": ca["peso"].map(lambda x: num(x, 1, True)),
                                      "USD si compra": ca["usd_compra"].map(lambda x: num(x, 0)),
                                      "USD si alquila": ca["usd_alquila"].map(lambda x: num(x, 0))})))

    r = res["retiro"]
    partes.append("\n## Anexo F. Simulación de retiros por escenario\n\nProbabilidad de quedarse sin dinero en vida. "
                  "Gasto fijo: retiro real constante. Con bono: sueldo fijo (gasto base) más bono variable.\n")
    filas = []
    for k, e in r["escenarios"].items():
        filas.append({"Escenario": k.replace("A ", "Compra, ").replace("B ", "Alquila, "),
                      "Gasto mensual (USD)": num(e["gasto_mes"], 0),
                      "Gasto fijo": num(e["ruina_sin_barandas"], 1, True),
                      "Horizonte 85": num(e["ruina_fija"]["85"], 1, True),
                      "Horizonte 95": num(e["ruina_fija"]["95"], 1, True),
                      "Horizonte 100": num(e["ruina_fija"]["100"], 1, True),
                      "Con bono": num(e["ruina_con_barandas"], 1, True),
                      "2008, gasto fijo": num(e["estres_2008"]["ruina_sin_barandas"], 1, True),
                      "2008, con bono": num(e["estres_2008"]["ruina_con_barandas"], 1, True)})
    partes.append(tabla(pd.DataFrame(filas)))
    partes.append("\nRetiro máximo seguro (USD por mes, ruina de 5% o menos):\n\n")
    partes.append(tabla(pd.DataFrame([{
        "Vivienda": k, "Gasto fijo": num(v["sin_barandas"], 0), "Con bono": num(v["con_barandas"], 0),
        "Gasto fijo, 2008": num(v["estres_2008"]["sin_barandas"], 0),
        "Con bono, 2008": num(v["estres_2008"]["con_barandas"], 0)} for k, v in r["retiro_seguro"].items()])))
    partes.append("\nSensibilidades (ruina con gasto fijo):\n\n")
    sens = r["sensibilidades"]
    esc = list(next(iter(sens.values()))["ruina_sin_barandas"])
    partes.append(tabla(pd.DataFrame([{"Caso": k, "Retorno real neto": num(v["retorno_real_neto"], 2, True),
                                       **{e.replace("A ", "Compra, ").replace("B ", "Alquila, "):
                                          num(v["ruina_sin_barandas"][e], 1, True) for e in esc}}
                                      for k, v in sens.items()])))

    partes.append("\n## Anexo G. Código y reproducción\n\n"
                  "Todo el análisis se reproduce con `python -m tp.correr` (Python 3.13; dependencias en "
                  "`requirements.txt`). Las pruebas automáticas se corren con `pytest -q`. Módulos principales:\n\n"
                  "- `tp/universo.py`: candidatos, exclusiones y nota mínima de sustentabilidad.\n"
                  "- `tp/datos.py`, `tp/estadisticas.py`: precios, estadísticas del benchmark y covarianza de Ledoit y Wolf.\n"
                  "- `tp/screening.py`: ranking de acciones por sector.\n"
                  "- `tp/equilibrio.py`, `tp/views.py`, `tp/black_litterman.py`: cartera neutra, opiniones y modelo de "
                  "Black y Litterman.\n"
                  "- `tp/optimizacion.py`, `tp/hrp.py`: optimización con reglas y paridad de riesgo jerárquica.\n"
                  "- `tp/impuestos.py`, `tp/comisiones.py`, `tp/mortalidad.py`, `tp/retiro.py`, `tp/montecarlo.py`: "
                  "impuestos, comisión, mortalidad, barandas y simulación.\n"
                  "- `tp/etapa4.py`, `tp/etapa5.py`, `tp/graficos.py`: salidas de cada etapa.\n")
    return "\n".join(partes)


def contexto_cifras() -> dict:
    """cifras.json más algunas vistas derivadas que los textos usan como marcadores."""
    c = json.loads((SALIDAS / "cifras.json").read_text(encoding="utf-8"))
    r = c["riesgo"]
    filas = ["| Posición | Peso | Aporte (puntos de vol) | % del riesgo |", "|---|---|---|---|"]
    filas += [f"| {a['ticker']} | {a['peso']} | {a['aporte_pp']} | {a['pct_riesgo']} |" for a in r["activos"]]
    filas.append(f"| Total | 100% | {r['vol'].rstrip('%')} | 100% |")
    c["tabla_riesgo"] = "\n".join(filas)
    r["activos"] = {a["ticker"]: a for a in r["activos"]}
    m = c["monitoreo"]
    c["tabla_desvios"] = ", ".join(f"{k} {v}" for k, v in m["desvio_max"].items())
    for e in m["ejemplos"].values():
        a, mes, d = e["fecha"].split("-")
        e["fecha"] = f"{d}/{mes}/{a}"
    return c


def buscar(c, ruta: str):
    """Sigue la ruta en el árbol; las claves pueden tener puntos (p. ej. "Mín. varianza")."""
    if ruta == "":
        return c
    if not isinstance(c, dict):
        raise KeyError(ruta)
    for k in sorted(c, key=len, reverse=True):
        if ruta == k or ruta.startswith(k + "."):
            try:
                return buscar(c[k], ruta[len(k) + 1:])
            except KeyError:
                continue
    raise KeyError(ruta)


def rellenar(texto: str, c: dict) -> str:
    """Reemplaza cada {{ruta}} por su valor en cifras.json; si alguna no existe, corta."""
    def valor(m):
        try:
            v = buscar(c, m.group(1))
        except KeyError:
            raise KeyError(f"marcador sin cifra: {{{{{m.group(1)}}}}}") from None
        if isinstance(v, (dict, list)) or v in ("", None):
            raise KeyError(f"marcador sin valor simple: {{{{{m.group(1)}}}}}")
        return str(v)
    return re.sub(r"\{\{([^{}]+)\}\}", valor, texto)


def indice_estatico(cuerpo: str) -> tuple[str, str]:
    """Índice ya escrito, con vínculos a cada título de nivel 1 y 2.

    El campo de índice de Word (pandoc --toc) queda vacío en los visores que no recalculan
    campos (Google Docs, vistas previas). Por eso cada título recibe un identificador propio
    y el índice es una lista de vínculos. No lleva números de página.
    """
    lineas, indice, n = [], [], 0
    for linea in cuerpo.split("\n"):
        m = re.match(r"^(#{1,2}) (.+?)\s*$", linea)
        if m:
            n += 1
            nivel, titulo = len(m.group(1)), m.group(2)
            linea = f"{m.group(1)} {titulo} {{#sec-{n}}}"
            indice.append(("" if nivel == 1 else "  ") + f"- [{titulo}](#sec-{n})")
        lineas.append(linea)
    return "# Índice {.unnumbered}\n\n" + "\n".join(indice) + "\n", "\n".join(lineas)


def main() -> Path:
    frente = ('---\ntitle: "Desarrollo del trabajo práctico"\nsubtitle: "Cartera de Valentina. Family office, Grupo 5"\n'
              'date: "Noviembre de 2026"\nlang: es-AR\ntoc-title: "Índice"\n---\n')
    bloques = [(PARTES / "00_resumen.md").read_text(encoding="utf-8"),
               (PARTES / "01_metodologia.md").read_text(encoding="utf-8")]
    bloques += [preparar_eic(*e) for e in EIC_ORDEN]
    bloques += [(PARTES / "08_limitaciones.md").read_text(encoding="utf-8"), anexos(),
                (PARTES / "99_bibliografia.md").read_text(encoding="utf-8")]
    texto = rellenar("\n\n".join(b.strip() + "\n" for b in bloques), contexto_cifras())
    indice, cuerpo = indice_estatico(texto)
    md = AQUI / "desarrollo.md"
    md.write_text(frente + "\n" + indice + "\n" + cuerpo, encoding="utf-8")
    return convertir(md, toc=False)


if __name__ == "__main__":
    print(main())
