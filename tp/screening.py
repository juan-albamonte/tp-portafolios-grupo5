"""Screening de las acciones del universo: fundamentales de Yahoo Finance + nota ESG.

El ranking es DENTRO de cada sector (percentil por métrica, promedio de percentiles),
para que los sectores favorecidos por el escenario no se coman toda la lista: la
preferencia por sector entra después, en `preliminar`.

Métricas (y sentido):
- pe_forward (menor es mejor): precio / ganancia esperada 12 meses (Yahoo).
- crecimiento_ganancias (mayor): ganancia esperada del próximo ejercicio vs. el actual
  (consenso de analistas, Yahoo "earnings estimate +1y").
- margen_operativo (mayor), roe (mayor).
- deuda_neta_ebitda (menor): (deuda total − caja) / EBITDA. No aplica a bancos.
- retorno_accionista (mayor): dividendo + recompras de los últimos 12 meses / capitalización.
- esg (mayor): S&P Global ESG Score (0-100, relativo a la industria). Ver data/esg.csv.
"""
import math

import numpy as np
import pandas as pd

from tp.config import DATA, RAIZ

SALIDA = RAIZ / "outputs"

METRICAS = {
    "pe_forward": False,
    "crecimiento_ganancias": True,
    "margen_operativo": True,
    "deuda_neta_ebitda": False,
    "roe": True,
    "retorno_accionista": True,
    "esg": True,
}

# Tesis de 02_industria.md (escenario base de 01_economia.md).
FAVORECIDOS = {"Salud", "Tecnología", "Financiero", "Industria"}
PENALIZADOS = {"Consumo discrecional", "Consumo básico", "Servicios públicos"}


def _num(x) -> float:
    return float("nan") if x is None else float(x)


def fundamentales_de(info: dict, recompras: float, crecimiento: float, fx: float) -> dict:
    """Métricas de una empresa a partir del `info` de Yahoo.

    recompras: recompra de acciones de los últimos 12 meses en la moneda de los estados
    contables (negativa, como sale del flujo de fondos); fx: esa moneda en USD.
    Yahoo da el dividendo en porcentaje (1,5 = 1,5%).
    """
    ebitda = _num(info.get("ebitda"))
    deuda_neta = _num(info.get("totalDebt")) - _num(info.get("totalCash"))
    cap = _num(info.get("marketCap"))
    dividendo = _num(info.get("dividendYield")) / 100 if info.get("dividendYield") is not None else 0.0
    recompra = -_num(recompras) * fx / cap if not math.isnan(_num(recompras)) else 0.0
    return {
        "pe_forward": _num(info.get("forwardPE")),
        "crecimiento_ganancias": _num(crecimiento),
        "margen_operativo": _num(info.get("operatingMargins")),
        "deuda_neta_ebitda": deuda_neta / ebitda if ebitda and ebitda > 0 else float("nan"),
        "roe": _num(info.get("returnOnEquity")),
        "retorno_accionista": dividendo + recompra,
    }


def percentil_en_sector(s: pd.Series, mayor_es_mejor: bool) -> pd.Series:
    """Percentil por rango medio: (puesto − 0,5) / n. Una sola empresa queda en 0,5."""
    r = s.rank(ascending=mayor_es_mejor, method="average")
    return (r - 0.5) / s.notna().sum()


def ranking_por_sector(df: pd.DataFrame) -> pd.DataFrame:
    r = df.copy()
    for m, mayor in METRICAS.items():
        r[f"p_{m}"] = r.groupby("sector")[m].transform(lambda s: percentil_en_sector(s, mayor))
    r["puntaje"] = r[[f"p_{m}" for m in METRICAS]].mean(axis=1, skipna=True)
    r["puesto_en_sector"] = r.groupby("sector")["puntaje"].rank(ascending=False, method="first").astype(int)
    return r.sort_values(["sector", "puesto_en_sector"]).reset_index(drop=True)


def preliminar(r: pd.DataFrame, favorecidos: set[str], por_sector: int, umbral_calidad: float,
               min_europa: int) -> pd.DataFrame:
    """Lista preliminar con el motivo de entrada de cada acción.

    1. Sector favorecido: la mejor de cada sector favorecido y, hasta `por_sector`, las
       siguientes que estén en la mitad de arriba (puntaje ≥ 0,5). Sin esa condición, en un
       sector de dos acciones entrarían las dos aunque una pierda en casi todo.
    2. Calidad propia: la mejor de cada sector no favorecido si su puntaje ≥ umbral.
    3. Completa Europa: si faltan europeas, las de mejor puntaje que no entraron.
    """
    elegidas = []
    for sector, g in r.groupby("sector"):
        if sector in favorecidos:
            top = g.nsmallest(por_sector, "puesto_en_sector")
            top = top[(top["puesto_en_sector"] == 1) | (top["puntaje"] >= 0.5)]
            elegidas += [(t, "sector favorecido") for t in top["ticker"]]
        else:
            mejor = g.nsmallest(1, "puesto_en_sector").iloc[0]
            if mejor["puntaje"] >= umbral_calidad:
                elegidas.append((mejor["ticker"], "calidad propia"))
    p = pd.DataFrame(elegidas, columns=["ticker", "motivo"]).merge(r, on="ticker")
    faltan = min_europa - int(p["europa"].sum())
    if faltan > 0:
        resto = r[r["europa"] & ~r["ticker"].isin(p["ticker"])].nlargest(faltan, "puntaje")
        p = pd.concat([p, resto.assign(motivo="completa Europa")], ignore_index=True)
    return p.sort_values("puntaje", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------- datos (I/O)

def bajar_fundamentales(tickers: list[str]) -> pd.DataFrame:
    """Yahoo Finance: info, recompras del último ejercicio y crecimiento esperado."""
    import yfinance as yf

    filas = []
    fx_cache: dict[str, float] = {}
    for t in tickers:
        tk = yf.Ticker(t)
        info = tk.info
        try:
            cf = tk.cashflow
            recompras = cf.loc["Repurchase Of Capital Stock"].iloc[0] if "Repurchase Of Capital Stock" in cf.index else 0.0
        except Exception:
            recompras = float("nan")
        try:
            crecimiento = tk.earnings_estimate.loc["+1y", "growth"]
        except Exception:
            crecimiento = float("nan")
        moneda = info.get("financialCurrency") or "USD"
        if moneda not in fx_cache:
            fx_cache[moneda] = 1.0 if moneda == "USD" else float(yf.Ticker(f"{moneda}USD=X").fast_info["last_price"])
        filas.append({"ticker": t, "moneda_contable": moneda, "fx": fx_cache[moneda],
                      "market_cap": info.get("marketCap"), "volumen_promedio": info.get("averageVolume"),
                      "dividendo": info.get("dividendYield"), "recompras": recompras,
                      **fundamentales_de(info, recompras, crecimiento, fx_cache[moneda])})
    return pd.DataFrame(filas)


def cargar_o_bajar_fundamentales(tickers: list[str], archivo=DATA / "fundamentals.csv") -> pd.DataFrame:
    if archivo.exists():
        df = pd.read_csv(archivo)
        if set(tickers) <= set(df["ticker"]):
            return df[df["ticker"].isin(tickers)].reset_index(drop=True)
    df = bajar_fundamentales(tickers)
    df.to_csv(archivo, index=False)
    return df


def nota_esg(esg: pd.DataFrame) -> pd.Series:
    """ESG Score vigente; si no es público, el CSA 2024 del documento DJSI (marcado en data/esg.csv)."""
    return esg["esg"].fillna(esg["csa"])


def tabla_screening(universo: pd.DataFrame, fundamentales: pd.DataFrame, esg: pd.DataFrame) -> pd.DataFrame:
    acciones = universo[universo["tipo"] == "accion"][["ticker", "nombre", "clase", "pais", "sector"]]
    e = esg.assign(esg_nota=nota_esg(esg))[["ticker", "esg_nota", "fuente"]].rename(columns={"fuente": "fuente_esg"})
    t = acciones.merge(fundamentales, on="ticker", how="left").merge(e, on="ticker", how="left")
    t["esg"] = t.pop("esg_nota")
    t["europa"] = t["clase"] == "acciones_europa"
    t["tesis_sector"] = np.where(t["sector"].isin(FAVORECIDOS), "favorecido",
                                 np.where(t["sector"].isin(PENALIZADOS), "penalizado", "neutral"))
    return t


def main() -> None:
    universo = pd.read_csv(DATA / "universo.csv", keep_default_na=False)
    tickers = universo.loc[universo["tipo"] == "accion", "ticker"].tolist()
    fundamentales = cargar_o_bajar_fundamentales(tickers)
    esg = pd.read_csv(DATA / "esg.csv")
    r = ranking_por_sector(tabla_screening(universo, fundamentales, esg))
    SALIDA.mkdir(exist_ok=True)
    r.to_csv(SALIDA / "screening.csv", index=False)
    p = preliminar(r, FAVORECIDOS, por_sector=2, umbral_calidad=0.60, min_europa=4)
    p.to_csv(SALIDA / "preliminar.csv", index=False)
    imprimir(r, p)


def imprimir(r: pd.DataFrame, p: pd.DataFrame) -> None:
    cols = ["ticker", "sector", "tesis_sector", "pe_forward", "crecimiento_ganancias", "margen_operativo",
            "deuda_neta_ebitda", "roe", "retorno_accionista", "esg", "puntaje", "puesto_en_sector"]
    fmt = {"pe_forward": "{:.1f}", "crecimiento_ganancias": "{:.0%}", "margen_operativo": "{:.0%}",
           "deuda_neta_ebitda": "{:.1f}", "roe": "{:.0%}", "retorno_accionista": "{:.1%}", "esg": "{:.0f}",
           "puntaje": "{:.2f}"}
    with pd.option_context("display.width", 250, "display.max_rows", None):
        print("SCREENING (ranking dentro de cada sector)")
        print(r[cols].to_string(index=False, formatters={k: v.format for k, v in fmt.items()}, na_rep="n/a"))
        print(f"\nPRELIMINAR ({len(p)} acciones, {int(p['europa'].sum())} europeas)")
        print(p[["ticker", "sector", "motivo", "puntaje"]].to_string(index=False, formatters={"puntaje": "{:.2f}".format}))


if __name__ == "__main__":
    main()
