"""Gráficos del TP (PNG a 200 dpi y SVG) en outputs/graficos/.

Uso: python -m tp.correr --etapa 6   (después de las etapas 4 y 5: lee outputs/resumen.json)

Estilo (skill dataviz, paleta de referencia validada con su script): una paleta categórica
fija por clase de activo en el mismo orden en todos los gráficos; fondo claro, grilla
y ejes en hairline gris, texto en tinta neutra (nunca del color de la serie), etiquetas de
valor visibles porque tres colores claros quedan debajo de 3:1 de contraste. Títulos en
castellano que dicen la conclusión.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from tp.config import BENCHMARK, CLASES, PROXIES, RANGOS, SALIDAS  # noqa: E402
from tp.formato import pct  # noqa: E402

CARPETA = SALIDAS / "graficos"
# Modo deck: sin título ni subtítulo (los pone la lámina) y recortado al contenido.
_DECK = False

# Paleta de referencia de dataviz, slots 1-6 (validada: CVD ΔE 9,1, normal 19,6 entre vecinos).
COLOR_CLASE = {
    "liquidez": "#2a78d6",
    "tesoro": "#eb6834",
    "tips": "#1baf7a",
    "corporativos": "#eda100",
    "acciones_eeuu": "#e87ba4",
    "acciones_europa": "#008300",
}
ETIQUETA_CLASE = {
    "liquidez": "Liquidez",
    "tesoro": "Bonos del Tesoro",
    "tips": "Bonos ajustados por inflación",
    "corporativos": "Bonos corporativos",
    "acciones_eeuu": "Acciones EE.UU.",
    "acciones_europa": "Acciones Europa",
}
# Texto dentro de un relleno: blanco, salvo negro sobre amarillo.
TEXTO_EN = {c: ("#0b0b0b" if c == "corporativos" else "#ffffff") for c in COLOR_CLASE}

SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
APAGADO = "#898781"
GRILLA = "#e1e0d9"
EJE = "#c3c2b7"
AZUL, NARANJA = "#2a78d6", "#eb6834"
AZULES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
DIVERGENTE = LinearSegmentedColormap.from_list("div", ["#184f95", "#6da7ec", "#f0efec", "#ec8a89", "#b52f2f"])


# --------------------------------------------------------------------- datos (funciones puras)

def percentiles_por_edad(valor: np.ndarray, edad_inicial: int, q=(10, 50, 90)) -> pd.DataFrame:
    """Percentiles del valor (n caminos × fechas) por edad."""
    p = np.percentile(valor, q, axis=0).T
    return pd.DataFrame(p, index=range(edad_inicial, edad_inicial + valor.shape[1]), columns=[f"p{x}" for x in q])


def rotacion(w: pd.Series, w_ref: pd.Series) -> float:
    return 0.5 * float(np.abs(w - w_ref).sum())


def pct_coma(x: float, d: int = 1) -> str:
    return pct(x, d)


def miles(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".")


def minuscula(s: str) -> str:
    return s[:1].lower() + s[1:]


def enumerar(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " y " + xs[-1]


# --------------------------------------------------------------------- estilo

def estilo() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
        "text.color": TINTA, "axes.labelcolor": TINTA_2, "xtick.color": APAGADO, "ytick.color": TINTA_2,
        "axes.edgecolor": EJE, "axes.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "grid.color": GRILLA, "grid.linewidth": 0.8, "grid.linestyle": "-",
        "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE,
        "legend.frameon": False, "legend.fontsize": 9, "lines.linewidth": 2, "lines.solid_capstyle": "round",
        "svg.fonttype": "none",
    })


def encabezado(fig, titulo: str, subtitulo: str = "") -> None:
    if _DECK:
        return
    fig.text(0.01, 0.985, titulo, ha="left", va="top", fontsize=13, fontweight="bold", color=TINTA)
    if subtitulo:
        fig.text(0.01, 0.925, subtitulo, ha="left", va="top", fontsize=9.5, color=TINTA_2)


def fuente(fig, texto: str) -> None:
    fig.text(0.01, 0.01, texto, ha="left", va="bottom", fontsize=7.5, color=APAGADO)


def guardar(fig, carpeta: Path, nombre: str) -> None:
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    extra = {"bbox_inches": "tight", "pad_inches": 0.12} if _DECK else {}
    fig.savefig(carpeta / f"{nombre}.png", dpi=200, **extra)
    fig.savefig(carpeta / f"{nombre}.svg", **extra)
    plt.close(fig)


def eje_pct(ax, eje: str = "x", d: int = 0) -> None:
    f = matplotlib.ticker.FuncFormatter(lambda v, _: pct_coma(v, d))
    (ax.xaxis if eje == "x" else ax.yaxis).set_major_formatter(f)


def grilla(ax, eje: str = "x") -> None:
    ax.grid(True, axis=eje, color=GRILLA, linewidth=0.8)
    ax.set_axisbelow(True)


def leyenda_clases(fig, clases=CLASES, y: float = 0.87, ncol: int = 6) -> None:
    from matplotlib.patches import Patch
    fig.legend([Patch(color=COLOR_CLASE[c]) for c in clases], [ETIQUETA_CLASE[c] for c in clases],
               loc="upper left", bbox_to_anchor=(0.01, y), ncol=ncol, handlelength=1, handleheight=1,
               columnspacing=1.4, fontsize=8.5)


def barras_apiladas(ax, filas: dict[str, pd.Series], notas: dict[str, str] | None = None) -> None:
    """Barras horizontales 100% por clase, con hueco de superficie entre segmentos y etiqueta si entra."""
    nombres = list(filas)[::-1]
    for y, k in enumerate(nombres):
        izq = 0.0
        for c in CLASES:
            v = float(filas[k].get(c, 0.0))
            if v <= 0:
                continue
            ax.barh(y, v, left=izq, height=0.6, color=COLOR_CLASE[c], edgecolor=SUPERFICIE, linewidth=1.5)
            if v >= 0.07:
                ax.text(izq + v / 2, y, pct_coma(v, 0) if abs(v * 100 - round(v * 100)) < 0.05 else pct_coma(v),
                        ha="center", va="center", fontsize=8, color=TEXTO_EN[c])
            izq += v
        if notas:
            ax.text(1.01, y, notas[k], ha="left", va="center", fontsize=8.5, color=TINTA_2)
    ax.set_yticks(range(len(nombres)), nombres)
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.spines[["bottom", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)


# --------------------------------------------------------------------- gráficos

def grafico_clases(cartera: pd.Series, bench: pd.Series, rangos: dict, carpeta: Path) -> None:
    """(a) Cartera final por clase contra el benchmark, con el rango de la política como banda."""
    estilo()
    fig, ax = plt.subplots(figsize=(10, 5.2))
    fig.subplots_adjust(left=0.25, right=0.95, top=0.78, bottom=0.12)
    clases = list(cartera.index)[::-1]
    for y, c in enumerate(clases):
        lo, hi = rangos[c]
        ax.barh(y, hi - lo, left=lo, height=0.62, color=GRILLA)
        ax.barh(y, cartera[c], height=0.3, color=AZUL)
        ax.plot([bench[c]] * 2, [y - 0.31, y + 0.31], color=TINTA, linewidth=2)
        ax.text(cartera[c] + 0.006, y + 0.04, pct_coma(cartera[c]), va="center", fontsize=9, color=TINTA)
    ax.set_yticks(range(len(clases)), [ETIQUETA_CLASE[c] for c in clases])
    ax.tick_params(axis="y", length=0)
    eje_pct(ax, "x")
    grilla(ax, "x")
    ax.set_xlim(0, max(max(h for _, h in rangos.values()), cartera.max()) + 0.05)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    fig.legend([Patch(color=AZUL), Line2D([], [], color=TINTA, linewidth=2), Patch(color=GRILLA)],
               ["Cartera final", "Benchmark 50/50", "Rango de la política de inversión"],
               loc="upper left", bbox_to_anchor=(0.01, 0.87), ncol=3)
    sobre = [minuscula(ETIQUETA_CLASE[c]) for c in cartera.index if cartera[c] > bench[c] + 0.02]
    bajo = [minuscula(ETIQUETA_CLASE[c]) for c in cartera.index if cartera[c] < bench[c] - 0.02]
    encabezado(fig, "La cartera final contra el benchmark, por clase de activo",
               f"Más {enumerar(sobre)}; menos {enumerar(bajo)} que el benchmark. Todo dentro de los rangos de la política.")
    fuente(fig, "Fuente: optimización del Grupo 5 (etapa 4). Benchmark: 50% renta fija, 50% acciones.")
    guardar(fig, carpeta, "a_clases")


def grafico_activos(w: pd.Series, clase: dict, nombre: dict, carpeta: Path) -> None:
    """(b) Pesos por activo, coloreados por clase."""
    estilo()
    w = w[w > 1e-6]
    orden = sorted(w.index, key=lambda t: (CLASES.index(clase[t]), -w[t]))[::-1]
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.subplots_adjust(left=0.3, right=0.95, top=0.8, bottom=0.08)
    for y, t in enumerate(orden):
        ax.barh(y, w[t], height=0.62, color=COLOR_CLASE[clase[t]])
        ax.text(w[t] + 0.003, y, pct_coma(w[t]), va="center", fontsize=9, color=TINTA)
    ax.set_yticks(range(len(orden)), [f"{t}  ·  {NOMBRE_FONDO.get(t, nombre[t])}" for t in orden], fontsize=9)
    ax.tick_params(axis="y", length=0)
    eje_pct(ax, "x")
    grilla(ax, "x")
    leyenda_clases(fig, [c for c in CLASES if any(clase[t] == c for t in w.index)], y=0.88, ncol=3)
    fondos = sum(w[t] for t in w.index if t in {"BIL", "IEF", "SCHP", "VCEB", "ESGV"})
    encabezado(fig, f"{len(w)} posiciones: los cinco fondos suman {pct_coma(fondos)} y las acciones, {pct_coma(1 - fondos)}")
    fuente(fig, "Tope de 5% por acción y 30% por fondo; ESGV con al menos 20%; cada acción en 0 o con al menos 2%.")
    guardar(fig, carpeta, "b_activos")


NOMBRE_FONDO = {
    "BIL": "Letras del Tesoro de 1 a 3 meses",
    "IEF": "Bonos del Tesoro de 7 a 10 años",
    "SCHP": "Bonos del Tesoro ajustados por inflación",
    "VCEB": "Bonos corporativos con filtro de sustentabilidad",
    "ESGV": "Acciones de EE.UU. con filtro de sustentabilidad",
}

NOMBRE_CARTERA = {
    "BL c=1 (final)": "Cartera final (con views)",
    "Equilibrio (c→0)": "Equilibrio sin views",
    "HRP ajustado": "Paridad de riesgo jerárquica",
    "Mín. varianza": "Mínima varianza",
    "Neutro (50/50)": "50/50 con nuestros activos",
}


def grafico_frontera(metricas: dict[str, dict], vol_objetivo: float, carpeta: Path) -> None:
    """(c) Las cinco carteras en el plano volatilidad / retorno neto. Énfasis en la final."""
    estilo()
    fig, ax = plt.subplots(figsize=(10, 5.6))
    fig.subplots_adjust(left=0.1, right=0.95, top=0.8, bottom=0.12)
    ax.axvline(vol_objetivo, color=EJE, linewidth=1)
    ax.text(vol_objetivo + 0.0006, ax.get_ylim()[0], "", fontsize=8)
    for k, m in metricas.items():
        final = k == "BL c=1 (final)"
        ax.scatter(m["vol"], m["retorno_neto"], s=110 if final else 70, color=AZUL if final else APAGADO,
                   edgecolor=SUPERFICIE, linewidth=2, zorder=3)
        extra = (f"\nrompe el límite de volatilidad de {pct_coma(vol_objetivo, 0)} de la política"
                 if m["vol"] > vol_objetivo + 1e-4 and k != "Neutro (50/50)" else "")
        ax.annotate(f"{NOMBRE_CARTERA[k]}\n{pct_coma(m['retorno_neto'], 2)} neto · {pct_coma(m['vol'])} vol{extra}",
                    (m["vol"], m["retorno_neto"]), xytext=(-10, 8) if final else (9, -4), textcoords="offset points",
                    fontsize=8.5, color=TINTA if final else TINTA_2, fontweight="bold" if final else "normal",
                    va="bottom" if final else "top", ha="right" if final else "left")
    lo_y = min(m["retorno_neto"] for m in metricas.values()) - 0.004
    hi_y = max(m["retorno_neto"] for m in metricas.values()) + 0.004
    ax.set_ylim(lo_y, hi_y)
    ax.set_xlim(min(m["vol"] for m in metricas.values()) - 0.006, max(m["vol"] for m in metricas.values()) + 0.025)
    ax.text(vol_objetivo, hi_y, "  volatilidad objetivo", fontsize=8, color=APAGADO, va="top")
    eje_pct(ax, "x")
    eje_pct(ax, "y", 1)
    grilla(ax, "both")
    ax.set_xlabel("Volatilidad anual esperada")
    ax.set_ylabel("Retorno esperado después de impuestos")
    f, e = metricas["BL c=1 (final)"], metricas["Equilibrio (c→0)"]
    encabezado(fig, "Mismas reglas, cinco maneras de armar la cartera",
               f"Con el mismo riesgo, las views suman {(f['retorno_neto'] - e['retorno_neto']) * 100:.2f} puntos ".replace(".", ",")
               + "de retorno neto al equilibrio. El 50/50 está armado con nuestros activos (no con los seis índices).")
    fuente(fig, "Retornos del escenario base con views (Black-Litterman), después de impuestos (ganancia de capital al "
                "realizar) y gastos de los fondos. Volatilidad: Ledoit-Wolf, 10 años de retornos diarios.")
    guardar(fig, carpeta, "c_frontera")


def grafico_sensibilidad(por_c: dict, por_vol: dict, carpeta: Path) -> None:
    """(d) Pesos por clase apilados para c y para la vol objetivo. por_x: {etiqueta: (Series por clase, neto)}."""
    estilo()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.2))
    fig.subplots_adjust(left=0.2, right=0.86, top=0.76, bottom=0.06, hspace=0.45)
    barras_apiladas(a1, {k: v[0] for k, v in por_c.items()}, {k: f"neto {pct_coma(v[1], 2)}" for k, v in por_c.items()})
    a1.set_title("Confianza en las views (c más alto = más peso a las views)", loc="left", fontsize=10, color=TINTA_2)
    barras_apiladas(a2, {k: v[0] for k, v in por_vol.items()},
                    {k: f"neto {pct_coma(v[1], 2)}" for k, v in por_vol.items()})
    a2.set_title("Volatilidad objetivo", loc="left", fontsize=10, color=TINTA_2)
    leyenda_clases(fig, y=0.875, ncol=3)
    encabezado(fig, "Las clases casi no se mueven con la confianza en las views; sí con la volatilidad objetivo")
    fuente(fig, "Cada barra es una cartera optimizada con las mismas reglas. Neto: retorno esperado con views, después de "
                "impuestos (ganancia de capital al realizar) y gastos de los fondos.")
    guardar(fig, carpeta, "d_sensibilidad")


DESCRIPCION_VIEW = {
    "V1": "NVIDIA le gana al mercado de EE.UU.",
    "V2": "Europa le gana a EE.UU.",
    "V3": "Salud (Lilly y Novartis) le gana al mercado",
    "V4": "Redes de pago (Visa y Mastercard) le ganan al mercado",
    "V5": "Eaton le gana al mercado",
    "V6": "Bonos ajustados por inflación le ganan al Tesoro",
    "V7": "Corporativos rinden menos que el Tesoro",
}


def grafico_views(rot: dict[str, float], carpeta: Path) -> None:
    """(e) Cuánto cambia la cartera si se saca cada view."""
    estilo()
    items = sorted(((k.replace("sin ", ""), v) for k, v in rot.items()), key=lambda kv: kv[1])
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.subplots_adjust(left=0.42, right=0.95, top=0.8, bottom=0.1)
    for y, (vid, v) in enumerate(items):
        ax.barh(y, v, height=0.6, color=AZUL)
        ax.text(v + 0.002, y, pct_coma(v), va="center", fontsize=9)
    ax.set_yticks(range(len(items)), [f"{vid}  {DESCRIPCION_VIEW.get(vid, '')}" for vid, _ in items], fontsize=9)
    ax.tick_params(axis="y", length=0)
    eje_pct(ax, "x")
    grilla(ax, "x")
    top = items[-1][0]
    encabezado(fig, f"La view que más mueve la cartera es {top}: {minuscula(DESCRIPCION_VIEW.get(top, ''))}",
               "Rotación al sacar una view por vez: la mitad de la suma de los cambios de peso, en % de la cartera.")
    fuente(fig, "Mismas reglas y volatilidad de 9% en todos los casos.")
    guardar(fig, carpeta, "e_views")


def grafico_abanico(paneles: dict[str, tuple[pd.DataFrame, str]], carpeta: Path) -> None:
    """(f) p10 / p50 / p90 del patrimonio real por edad. paneles: {título: (percentiles, nota)}, 4 paneles 2×2."""
    estilo()
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.4), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.8, bottom=0.1, hspace=0.32, wspace=0.08)
    for ax, (tit, (p, nota)) in zip(axs.flat, paneles.items()):
        m = p / 1e6
        ax.fill_between(m.index, m["p10"], m["p90"], color=AZUL, alpha=0.12, linewidth=0)
        ax.plot(m.index, m["p50"], color=AZUL)
        ax.plot(m.index, m["p10"], color=AZUL, linewidth=0.8, alpha=0.6)
        ax.plot(m.index, m["p90"], color=AZUL, linewidth=0.8, alpha=0.6)
        ax.set_title(tit, loc="left", fontsize=10, color=TINTA)
        ax.text(0.02, 0.04, nota, transform=ax.transAxes, ha="left", va="bottom", fontsize=8.5, color=TINTA_2)
        e = m.index[-1]
        ax.text(e, m["p50"].iloc[-1], f" {m['p50'].iloc[-1]:.1f}".replace(".", ","), va="center", fontsize=8)
        grilla(ax, "y")
    for ax in axs[1]:
        ax.set_xlabel("Edad de Valentina")
    for ax in axs[:, 0]:
        ax.set_ylabel("USD millones de hoy")
    encabezado(fig, "El patrimonio de la cartera: con y sin barandas, comprando y alquilando",
               "Línea: mediana. Banda: 8 de cada 10 escenarios (entre el percentil 10 y el 90). En dólares de hoy, "
               "suponiendo que vive hasta los 100.")
    fuente(fig, "Monte Carlo de 10.000 escenarios con impuestos, comisión y Bienes Personales. Barandas: sueldo fijo "
                "(gasto base) más bono variable (Guyton-Klinger 120/80, ±10%).")
    guardar(fig, carpeta, "f_abanico")


ESCENARIOS_ORDEN = ["A base", "A lujo", "A alto", "B base", "B lujo", "B alto"]
NOMBRE_ESC = {"A": "Compra", "B": "Alquila"}


def etiqueta_esc(k: str) -> str:
    v, n = k.split()
    return f"{NOMBRE_ESC[v]} · {n}"


def grafico_ruina(esc: dict, carpeta: Path) -> None:
    """(g) Tabla-calor de la probabilidad de ruina: 6 escenarios × (gasto fijo, sueldo fijo + bono)."""
    estilo()
    filas = ESCENARIOS_ORDEN
    M = np.array([[esc[k]["ruina_sin_barandas"], esc[k]["ruina_con_barandas"]] for k in filas])
    fig, ax = plt.subplots(figsize=(8, 5.6))
    fig.subplots_adjust(left=0.24, right=0.96, top=0.78, bottom=0.08)
    cmap = LinearSegmentedColormap.from_list("azul", AZULES)
    ax.imshow(M, cmap=cmap, vmin=0, vmax=0.7, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, pct_coma(v), ha="center", va="center", fontsize=11.5,
                    color="#ffffff" if v > 0.3 else TINTA, fontweight="bold" if v <= 0.05 else "normal")
    ax.set_xticks([0, 1], ["Gasto fijo", "Sueldo fijo + bono variable"])
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(filas)), [f"{etiqueta_esc(k)}  ({miles(esc[k]['gasto_mes'])}/mes)" for k in filas])
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.axhline(2.5, color=SUPERFICIE, linewidth=4)
    encabezado(fig, "Probabilidad de quedarse sin plata en vida",
               "En negrita, los casos que cumplen el criterio de 5% o menos. Mortalidad de Gompertz (esperanza de vida 88).")
    fuente(fig, "Monte Carlo de 10.000 escenarios. Sueldo fijo = gasto base de la vivienda; el bono variable se ajusta con las barandas.")
    guardar(fig, carpeta, "g_ruina")


def grafico_estres(esc: dict, carpeta: Path) -> None:
    """(h) Ruina en el régimen normal contra un 2008 en el primer año."""
    estilo()
    fig, axs = plt.subplots(1, 2, figsize=(10, 5.6), sharey=True)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.76, bottom=0.1, wspace=0.18)
    filas = ESCENARIOS_ORDEN[::-1]
    for ax, (clave, tit) in zip(axs, [("ruina_sin_barandas", "Gasto fijo"), ("ruina_con_barandas", "Sueldo fijo + bono")]):
        for y, k in enumerate(filas):
            n, s = esc[k][clave], esc[k]["estres_2008"][clave]
            ax.barh(y + 0.18, n, height=0.34, color=AZUL)
            ax.barh(y - 0.18, s, height=0.34, color=NARANJA)
            caja = dict(facecolor=SUPERFICIE, edgecolor="none", pad=0.6)
            ax.text(max(n, 0.05) + 0.012, y + 0.18, pct_coma(n), va="center", fontsize=8, color=TINTA_2, bbox=caja)
            ax.text(max(s, 0.05) + 0.012, y - 0.18, pct_coma(s), va="center", fontsize=8, color=TINTA, bbox=caja)
        ax.axvline(0.05, color=TINTA_2, linewidth=1)
        ax.text(0.052, len(filas) - 0.45, "límite 5%", fontsize=8, color=TINTA_2)
        ax.set_title(tit, loc="left", fontsize=10)
        eje_pct(ax, "x")
        grilla(ax, "x")
        ax.set_xlim(0, 0.98)  # espacio para la etiqueta de la barra más larga
        ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8])  # sin 100%: no se pega con el 0% del panel de al lado
        ax.tick_params(axis="y", length=0)
    axs[0].set_yticks(range(len(filas)), [etiqueta_esc(k) for k in filas])
    from matplotlib.patches import Patch
    fig.legend([Patch(color=AZUL), Patch(color=NARANJA)], ["Mercados normales", "El primer año repite 2008"],
               loc="upper left", bbox_to_anchor=(0.01, 0.875), ncol=2)
    a, b = esc["A lujo"], esc["B lujo"]
    encabezado(fig, "Si arranca con un 2008, solo comprar con sueldo fijo + bono sigue cerca del 5%",
               f"Nivel lujo con barandas: compra {pct_coma(a['estres_2008']['ruina_con_barandas'])}, "
               f"alquila {pct_coma(b['estres_2008']['ruina_con_barandas'])} de probabilidad de quedarse sin plata.")
    fuente(fig, "2008: acciones EE.UU. −37%, Europa −45%, Tesoro +18% (índices de referencia). Después, el mercado vuelve a lo normal.")
    guardar(fig, carpeta, "h_estres")


def grafico_correlaciones(corr: pd.DataFrame, carpeta: Path) -> None:
    """(i) Correlaciones diarias entre los seis índices del benchmark."""
    estilo()
    fig, ax = plt.subplots(figsize=(8.4, 6.6))
    fig.subplots_adjust(left=0.3, right=0.97, top=0.78, bottom=0.05)
    ax.imshow(corr.values, cmap=DIVERGENTE, vmin=-1, vmax=1)
    n = len(corr)
    for i in range(n):
        for j in range(n):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}".replace(".", ","), ha="center", va="center", fontsize=9,
                    color="#ffffff" if abs(v) > 0.6 else TINTA)
    nombres = [f"{ETIQUETA_CLASE[c]} ({PROXIES[c]})" for c in corr.index]
    ax.set_xticks(range(n), [PROXIES[c] for c in corr.index])
    ax.xaxis.tick_top()
    ax.set_yticks(range(n), nombres)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    a = corr.loc["acciones_eeuu", "tesoro"]
    encabezado(fig, "Los bonos del Tesoro son los que más diversifican a las acciones",
               "Correlación diaria entre Tesoro y acciones de EE.UU.: " + f"{a:.2f}".replace(".", ",").replace("-", "−")
               + ". Azul: se mueven en sentidos opuestos; rojo: juntos.")
    fuente(fig, "Retornos diarios de los índices de referencia del benchmark, 2007-2026 (Yahoo Finance).")
    guardar(fig, carpeta, "i_correlaciones")


def grafico_historia(ret: pd.DataFrame, pesos: dict, caida: tuple, carpeta: Path) -> None:
    """(j) USD 100 invertidos en cada índice del benchmark y en el benchmark.

    Sin la caída de 2008-2009 marcada: la que se presenta es la de la lámina 17 (misma regla para la cartera
    y el 50/50); esta, con rebalanceo diario, sería otro número para la misma crisis."""
    estilo()
    bench = sum(w * ret[c] for c, w in pesos.items())
    valor = 100 * (1 + ret).cumprod()
    vb = 100 * (1 + bench).cumprod()
    fig, ax = plt.subplots(figsize=(10, 5.6))
    fig.subplots_adjust(left=0.08, right=0.72, top=0.8, bottom=0.1)
    for c in CLASES:
        ax.plot(valor.index, valor[c], color=COLOR_CLASE[c], linewidth=1.5, label=f"{ETIQUETA_CLASE[c]} ({PROXIES[c]})")
    ax.plot(vb.index, vb, color=TINTA, linewidth=2.2, label="Benchmark 50/50")
    ax.set_yscale("log")
    ticks = [50, 100, 200, 400, 800]
    ax.set_yticks(ticks, [str(t) for t in ticks])
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    grilla(ax, "y")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8.5)
    ax.set_ylabel("Valor de USD 100 invertidos (escala logarítmica)")
    encabezado(fig, f"USD 100 en el benchmark se volvieron {vb.iloc[-1]:.0f}",
               f"{ret.index[0]:%m/%Y} a {ret.index[-1]:%m/%Y}, retornos totales en dólares (con dividendos e intereses).")
    fuente(fig, "Índices de referencia: BIL, IEF, TIP, LQD, SPY y VGK (Yahoo Finance). Benchmark rebalanceado a diario.")
    guardar(fig, carpeta, "j_historia")


# --------------------------------------------------------------------- todo junto

# Alternativas de M2: slots 1-3 de la paleta (validados: CVD ΔE 9,2, normal 27,6; el verde queda
# debajo de 3:1 de contraste, así que las tres líneas llevan etiqueta directa).
COLOR_ALT = {"d_cartera": "#2a78d6", "b_letras": "#eb6834", "a_quieta": "#1baf7a"}
ETIQUETA_ALT = {"d_cartera": "Invertida en nuestra cartera", "b_letras": "Todo en letras del Tesoro",
                "a_quieta": "Plata quieta"}


def grafico_invertir(alt: dict, carpeta: Path, edad0: int = 35) -> None:
    """Patrimonio mediano por edad de tres alternativas, en USD millones de hoy (M2)."""
    fig, ax = plt.subplots(figsize=(9, 5.2))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.80 if not _DECK else 0.97, bottom=0.12)
    tope = 0.0
    for k in ("a_quieta", "b_letras", "d_cartera"):
        y = np.array(alt[k]["mediana_por_edad"]) / 1e6
        x = np.arange(edad0, edad0 + len(y))
        ax.plot(x, y, color=COLOR_ALT[k], linewidth=2.6 if k == "d_cartera" else 2, label=ETIQUETA_ALT[k])
        tope = max(tope, y.max())
        e = alt[k].get("edad_central")
        if e is not None and not np.isnan(e):
            ax.plot([e], [0], "o", markersize=8, color=COLOR_ALT[k], markeredgecolor=SUPERFICIE, markeredgewidth=2,
                    zorder=5)
            ax.annotate(f"se acaba a los {e:.0f}", (e, 0), xytext=(0, -9), textcoords="offset points", va="top",
                        ha="right" if e > 92 else "center", fontsize=9, color=TINTA)
        i = 20  # etiqueta directa a los 55
        ax.annotate(ETIQUETA_ALT[k], (x[i], y[i]), xytext=(0, 7), textcoords="offset points", ha="left",
                    fontsize=9, color=TINTA)
    ax.axhline(0, color=TINTA_2, linewidth=1)
    ax.text(edad0 + 0.5, tope * 0.02, "sin plata", fontsize=8.5, color=TINTA_2, va="bottom")
    ax.set_xlim(edad0, 100)
    ax.set_ylim(-tope * 0.09, tope * 1.08)
    ax.set_xlabel("Edad de Valentina")
    ax.set_ylabel("USD millones de hoy (mediana)")
    grilla(ax, "y")
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[::-1], l[::-1], loc="upper right", ncol=1)  # mismo orden que las líneas, de arriba abajo
    d = alt["d_cartera"]
    encabezado(fig, f"Invertida, tu plata dura toda la vida; quieta, se acaba a los {alt['a_quieta']['edad_central']:.0f}",
               "Patrimonio mediano en USD millones de hoy. Compra del depto, nivel lujo (sueldo fijo + bono).\n"
               f"Probabilidad de quedarse sin plata en vida: quieta {pct_coma(alt['a_quieta']['ruina'])}, letras {pct_coma(alt['b_letras']['ruina'])}, "
               f"nuestra cartera {pct_coma(d['ruina'])}.")
    fuente(fig, "10.000 escenarios con mortalidad de Gompertz; mismos impuestos, Bienes Personales y retiros. "
                "Letras y plata quieta sin comisión de gestión.")
    guardar(fig, carpeta, "k_invertir_vs_no")


def main(carpeta: Path = CARPETA, deck: bool = False) -> list[Path]:
    """deck=True: versión sin títulos para las láminas (outputs/graficos/deck)."""
    global _DECK
    _DECK = deck
    from tp import etapa4, etapa5
    from tp.config import ESCENARIOS, Mercado

    ins = etapa4.insumos()
    base = etapa4.retornos(ins, ins.S_lw)
    w = etapa4.principal(ins, base, ins.S_lw)
    clase = dict(zip(ins.activos, ins.clase))

    grafico_clases(etapa4.por_clase(ins, w), pd.Series(BENCHMARK), RANGOS, carpeta)
    grafico_activos(w, clase, ins.nombre, carpeta)
    carteras, _, _ = etapa4.comparacion(ins, w)
    from tp.alternativas import realizaciones
    lujo_a = next(c for c in etapa5.casos() if c.etiqueta == "A lujo")
    f = realizaciones(ins, w.values, lujo_a)["cartera"]
    real = realizaciones(ins, w.values, lujo_a)
    neto_c = etapa4.neto_completo(ins, base, f)  # con views, impuestos al realizar y gastos de fondos
    neto_b = etapa4.neto_completo(ins, base, real["benchmark"])  # el 50/50 rota como el 50/50
    grafico_frontera({k: etapa4.metricas(ins, x, base)
                      | {"retorno_neto": float(x @ (neto_b if k == "Neutro (50/50)" else neto_c))}
                      for k, x in carteras.items()}, Mercado.vol_objetivo, carpeta)

    def caso(**kw):
        x, _, r = etapa4.sensibilidad(ins, **kw)
        return etapa4.por_clase(ins, x), float(x @ etapa4.neto_completo(ins, r, f))
    por_c = {"c = 0,25": caso(c=0.25), "c = 1 (base)": caso(c=1.0), "c = 5": caso(c=5.0)}
    por_vol = {"7%": caso(vol=0.07), "9% (base)": caso(vol=0.09), "11%": caso(vol=0.11)}
    grafico_sensibilidad(por_c, por_vol, carpeta)
    _, rot = etapa4.leave_one_out(ins, w)
    grafico_views(rot, carpeta)

    resumen = json.loads((SALIDAS / "resumen.json").read_text(encoding="utf-8"))
    esc = resumen["retiro"]["escenarios"]
    m = etapa5.Motor(ins, realizacion=f)
    rp = m.rp(w.values)
    cs = {c.etiqueta: c for c in etapa5.casos()}
    paneles = {}
    for k, b in (("A base", False), ("A lujo", False), ("A lujo", True), ("B lujo", True)):
        nombre = "sueldo fijo + bono" if b else "gasto fijo"
        v = m.correr(cs[k], rp, b, vidas=m.horizonte(100)).valor
        nota = f"sin plata en vida: {pct_coma(esc[k]['ruina_con_barandas' if b else 'ruina_sin_barandas'])}"
        paneles[f"{etiqueta_esc(k)} ({miles(cs[k].gasto_mes)}/mes), {nombre}"] = (
            percentiles_por_edad(v[:, : 100 - 35 + 1], 35), nota)
    grafico_abanico(paneles, carpeta)
    grafico_ruina(esc, carpeta)
    grafico_estres(esc, carpeta)

    grafico_invertir(resumen["retiro"]["alternativas"], carpeta)
    ret = ins.extra["ret_indices"][CLASES]
    grafico_correlaciones(ret.corr(), carpeta)
    grafico_historia(ret, BENCHMARK, ins.extra["caida_benchmark"], carpeta)
    archivos = sorted(Path(carpeta).glob("*.png"))
    print(f"Gráficos en {carpeta}: " + ", ".join(p.stem for p in archivos) + f" ({len(archivos)} PNG + SVG).")
    return archivos


if __name__ == "__main__":
    main()
