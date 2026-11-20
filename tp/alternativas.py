"""Invertir contra no invertir (M2) y sensibilidad a cambios de impuestos (M3).

Mismo plan recomendado en todas las alternativas: escenario A (compra), nivel lujo, sueldo fijo
(gasto base) más bono con las barandas de Guyton y Klinger, mortalidad de Gompertz, 10.000
caminos con la semilla de siempre. Cambia solo dónde está la plata y qué costos paga.

    a. Plata quieta: 0% nominal, pierde la inflación. Sin comisión; paga Bienes Personales.
    b. Todo en letras del Tesoro (BIL): interés al 35% y el gasto del fondo; sin comisión.
    c. Benchmark 50/50 pasivo, sin asesor: los seis fondos índice con su gasto; sin comisión.
       No cumple la política (más vol, sin filtro ESG): es la comparación honesta.
    d. Nuestra cartera, con todos sus costos.
    e. El 50/50 pasivo pagando nuestra comisión: separa el efecto de la asignación del de la comisión.

misma_vara: cartera contra el 50/50 de índices con la misma Σ (Ledoit-Wolf diaria conjunta de los
14 activos y los 6 índices, ventana 2016-2026), los mismos retornos de largo plazo por clase y los
mismos impuestos y gastos de fondos.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from tp.config import BENCHMARK, Impuestos, benchmark_pasivo
from tp.estadisticas import ledoit_wolf_cc
from tp.montecarlo import RetornoCartera, simular

EDADES_PATRIMONIO = (60, 75, 90)
SIN_COMISION = lambda v: np.zeros_like(np.asarray(v, float))

# M3: escenarios impositivos.
ALICUOTAS_ALTAS = Impuestos(tasa_ar_dividendos=0.40, tasa_ar_intereses=0.40, tasa_ganancia_capital=0.20)


def bp_fijo(anio: int) -> float:
    """Bienes Personales que no baja: 0,75% para siempre (en vez de 0,25% desde 2027)."""
    return 0.01 if anio <= 2025 else 0.0075


def rp_quieta(n: int, T: int, inflacion: float) -> RetornoCartera:
    """Plata quieta: 0% nominal; en reales pierde la inflación todos los años."""
    return RetornoCartera(real=np.full((n, T), 1 / (1 + inflacion) - 1), nominal=np.zeros((n, T)))


def edad_central(capital: float, retiro: float, piso: float, r_real: float, r_nominal: float, costos,
                 T: int, edad0: int, barandas: bool = False, inflacion: float = 0.0) -> float:
    """Edad a la que se acaba la plata con un retorno constante (el caso central). NaN si no se acaba."""
    rr, rn = np.full((1, T), r_real), np.full((1, T), r_nominal)
    res = simular(capital, retiro, rr, rn, np.array([float(T)]), costos, con_barandas=barandas,
                  inflacion=inflacion, piso=piso)
    return edad0 + float(res.anio_ruina[0])


def patrimonio(valor: np.ndarray, edades=EDADES_PATRIMONIO, edad0: int = 35, inflacion: float = 0.0) -> dict:
    """Mediana del valor real a cada edad y su equivalente en dólares corrientes."""
    real = {e: float(np.median(valor[:, e - edad0])) for e in edades}
    return {"real": real, "nominal": {e: v * (1 + inflacion) ** (e - edad0) for e, v in real.items()}}


def compuesto_mediano(r: np.ndarray) -> float:
    """Retorno anual compuesto del camino mediano."""
    return float(np.median((1 + r).prod(axis=1) ** (1 / r.shape[1]) - 1))


@dataclass
class InsumosBenchmark:
    """Lo que el Motor necesita para simular el benchmark pasivo."""
    activos: list[str]
    clase: list[str]
    renta: pd.Series
    S_lw: pd.DataFrame
    pesos: np.ndarray


def insumos_benchmark(ins) -> InsumosBenchmark:
    """Los seis fondos índice: Σ de Ledoit-Wolf diaria en la misma ventana que la cartera."""
    b = benchmark_pasivo()
    ventana = ins.extra["ventana"]
    r = ins.extra["ret_indices"].loc[ventana.index[0]:ventana.index[-1], b["clase"]]
    S, _, _ = ledoit_wolf_cc(r.values, anualizar=252)
    act = b["ticker"].tolist()
    return InsumosBenchmark(act, b["clase"].tolist(), pd.Series(b["renta"].values, index=act),
                            pd.DataFrame(S, index=act, columns=act),
                            np.array([BENCHMARK[c] for c in b["clase"]]))


def metricas(m, caso, rp: RetornoCartera, comision, edad0: int, inflacion: float, central: bool) -> dict:
    """Ruina, edades, patrimonio y bono para una alternativa (con barandas, el plan recomendado)."""
    from tp.etapa5 import toca_piso
    res = m.correr(caso, rp, True, comision=comision)
    a100 = m.correr(caso, rp, True, vidas=m.horizonte(100), comision=comision)
    arruinados = res.anio_ruina[res.ruina]
    out = {
        "ruina": res.prob_ruina,
        "edad_mediana_ruina": edad0 + float(np.median(arruinados)) if len(arruinados) else None,
        "patrimonio": patrimonio(a100.valor, edad0=edad0, inflacion=inflacion),
        "mediana_por_edad": [float(x) for x in np.median(a100.valor[:, :100 - edad0 + 1], axis=0)],
        "bono_desaparece": toca_piso(res, caso),
        "retorno_real_compuesto": compuesto_mediano(rp.real),
    }
    if central:
        rr, rn = compuesto_mediano(rp.real), compuesto_mediano(rp.nominal)
        out["edad_central"] = edad_central(caso.capital, 12 * caso.gasto_mes, 12 * caso.piso_mes, rr, rn,
                                           m.costos(caso, comision), m.T, edad0, barandas=True,
                                           inflacion=inflacion)
    return out


def alternativas(m, mb, caso, w: np.ndarray, edad0: int, inflacion: float) -> dict:
    """Las cuatro alternativas de M2. m: Motor de la cartera; mb: Motor del benchmark pasivo."""
    n = len(m.vidas)
    e_bil = np.array([a == "BIL" for a in m.ins.activos], float)
    return {
        "a_quieta": metricas(m, caso, rp_quieta(n, m.T, inflacion), SIN_COMISION, edad0, inflacion, True),
        "b_letras": metricas(m, caso, m.rp(e_bil), SIN_COMISION, edad0, inflacion, True),
        "c_benchmark": metricas(mb, caso, mb.rp(mb.ins.pesos), SIN_COMISION, edad0, inflacion, False),
        "d_cartera": metricas(m, caso, m.rp(w), None, edad0, inflacion, False),
        "e_benchmark_comision": metricas(mb, caso, mb.rp(mb.ins.pesos), None, edad0, inflacion, False),
    }


def misma_vara(ins, w: np.ndarray, rf: float, real: dict | None = None) -> dict:
    """Cartera, 50/50 de índices y cartera neutra (el 50/50 armado con los 14 activos) con la misma vara.

    Devuelve vol, retorno bruto y neto (después de impuestos y gastos de fondos), Sharpe (bruto − rf)/vol
    y tracking error contra el 50/50 de índices. También la descomposición de la vol de la neutra:
    Europa con VGK y después EE.UU. con SPY.
    """
    from tp.config import gastos_fondos
    from tp.etapa4 import RENTA_FIJA
    from tp.etapa5 import mu_por_activo
    from tp.montecarlo import tasas_impositivas
    b = benchmark_pasivo()
    ventana = ins.extra["ventana"]
    idx = ins.extra["ret_indices"].loc[ventana.index[0]:ventana.index[-1], b["clase"]]
    idx.columns = [f"{t}_idx" for t in b["ticker"]]
    X = pd.concat([ventana[ins.activos], idx], axis=1).dropna()
    S, delta, _ = ledoit_wolf_cc(X.values, anualizar=252)
    S = pd.DataFrame(S, index=X.columns, columns=X.columns)
    g = gastos_fondos()
    clase = dict(zip(ins.activos, ins.clase)) | {f"{t}_idx": c for t, c in zip(b["ticker"], b["clase"])}
    renta = dict(zip(ins.activos, ins.renta.values)) | {f"{t}_idx": r for t, r in zip(b["ticker"], b["renta"])}

    real = real or {}

    def medir(pesos: dict, f: float | None) -> dict:
        act = [a for a in X.columns if pesos.get(a, 0) > 0]
        x = np.array([pesos[a] for a in act])
        cls = [clase[a] for a in act]
        mu = mu_por_activo(cls)
        t_r, k = tasas_impositivas(np.array([c in RENTA_FIJA for c in cls]), np.array([renta[a] for a in act]),
                                   Impuestos(), mu=mu, realizacion=f)
        gasto = np.array([g[a.removesuffix("_idx")] for a in act])
        xs = pd.Series(pesos).reindex(X.columns).fillna(0).values
        vol = float(np.sqrt(xs @ S.values @ xs))
        bruto = float(x @ mu)
        return {"vol": vol, "bruto": bruto, "neto": float(x @ ((mu - gasto) * (1 - t_r)) - x @ k),
                "sharpe": (bruto - rf) / vol}

    wc = dict(zip(ins.activos, w))
    wi = {f"{t}_idx": BENCHMARK[c] for t, c in zip(b["ticker"], b["clase"])}
    wn = ins.w_b.to_dict()
    europa = ("ASML", "NVS", "RELX")
    eeuu = ("ESGV", "NVDA", "V", "MA", "LLY", "ETN", "PG")
    wn_vgk = {k: v for k, v in wn.items() if k not in europa} | {"VGK_idx": BENCHMARK["acciones_europa"]}
    wn_spy = {k: v for k, v in wn_vgk.items() if k not in eeuu} | {"SPY_idx": BENCHMARK["acciones_eeuu"]}
    dif = pd.Series(wc).reindex(X.columns).fillna(0).values - pd.Series(wi).reindex(X.columns).fillna(0).values
    fc, fb = real.get("cartera"), real.get("benchmark")
    return {"cartera": medir(wc, fc), "benchmark_indices": medir(wi, fb), "neutra_14": medir(wn, fb),
            "neutra_europa_vgk": medir(wn_vgk, fb), "neutra_europa_vgk_eeuu_spy": medir(wn_spy, fb),
            "tracking_error": float(np.sqrt(dif @ S.values @ dif)), "delta": float(delta), "dias": len(X),
            "desde": f"{X.index[0]:%Y-%m-%d}", "hasta": f"{X.index[-1]:%Y-%m-%d}"}


def sensibilidad_impuestos(ins, w: np.ndarray, caso, realizacion: float | None = None) -> dict:
    """M3: ruina y retiro seguro con bono de un caso, con Bienes Personales fijo y alícuotas más altas."""
    from tp.etapa5 import Motor
    base, alta = Motor(ins, realizacion=realizacion), Motor(ins, imp=ALICUOTAS_ALTAS, realizacion=realizacion)
    casos = {"base": (base, None), "bp_fijo": (base, bp_fijo), "alicuotas_altas": (alta, None),
             "ambos": (alta, bp_fijo)}
    out = {}
    for k, (m, bp) in casos.items():
        rp = m.rp(w)
        kw = {} if bp is None else {"bp": bp}
        out[k] = {"ruina_bono": m.correr(caso, rp, True, **kw).prob_ruina,
                  "seguro_bono": m.retiro_seguro(caso, rp, True, **kw)}
    assert all(out[k]["ruina_bono"] >= out["base"]["ruina_bono"] for k in out), "más impuestos no puede bajar la ruina"
    return out


def retorno_anio_activo(precios: pd.Series, anio: int) -> float | None:
    """Retorno total del año calendario (cierre del último día del año anterior al último del año), o None."""
    antes = precios.loc[:f"{anio - 1}-12-31"].dropna()
    durante = precios.loc[f"{anio}-01-01":f"{anio}-12-31"].dropna()
    if antes.empty or durante.empty or durante.index[-1] < pd.Timestamp(f"{anio}-12-24"):
        return None
    return float(durante.iloc[-1] / antes.iloc[-1] - 1)


def caida_2008(ins, w: np.ndarray) -> dict:
    """Cuánto cae en 2008 (nominal, antes de impuestos, pesos fijos todo el año) la cartera y el 50/50.

    Misma regla para los dos: cada posición con su propio retorno de 2008 si cotizó todo el año (los
    fondos rellenados usan su índice), si no el de su clase. El 50/50 son los índices mismos. También la
    versión solo por clase, la que usa el estrés del Monte Carlo.
    """
    r08 = ins.extra["r2008"]
    precios = ins.extra["precios"]
    por_activo, fuente = {}, {}
    for a, c in zip(ins.activos, ins.clase):
        r = retorno_anio_activo(precios[a], 2008)
        por_activo[a], fuente[a] = (r, "propio") if r is not None else (r08[c], "clase")
    cartera = float(sum(x * por_activo[a] for a, x in zip(ins.activos, w)))
    cartera_clase = float(sum(x * r08[c] for c, x in zip(ins.clase, w)))
    bench = float(sum(BENCHMARK[c] * r08[c] for c in BENCHMARK))
    return {"cartera": cartera, "cartera_por_clase": cartera_clase, "benchmark": bench,
            "por_activo": por_activo, "fuente": fuente}


def con_views(ins, w: np.ndarray, total_bl: pd.Series, real: dict | None = None) -> dict:
    """Retorno neto con el posterior de Black-Litterman (gastos de fondos e impuestos con la misma regla
    de realización) de la cartera y del 50/50 armado con nuestros 14 activos (la cartera neutra), que es
    como el modelo ve el benchmark: no hay views sobre los seis índices."""
    from tp.config import gastos_fondos
    from tp.etapa4 import RENTA_FIJA
    from tp.montecarlo import tasas_impositivas
    real = real or {}
    g = gastos_fondos()
    gasto = np.array([g[a] for a in ins.activos])
    rf = np.array([c in RENTA_FIJA for c in ins.clase])
    mu = total_bl.values

    def neto(x: np.ndarray, f: float | None) -> float:
        t_r, k = tasas_impositivas(rf, ins.renta.values, Impuestos(), mu=mu, realizacion=f)
        return float(x @ ((mu - gasto) * (1 - t_r)) - x @ k)

    return {"cartera": neto(np.asarray(w), real.get("cartera")), "benchmark": neto(ins.w_b.values, real.get("benchmark"))}

def realizaciones(ins, w: np.ndarray, caso) -> dict:
    """Fracción de las acciones que se vende por año (realiza ganancia), para la cartera y el 50/50.

    Suma dos partes, medidas con las mismas reglas para las dos carteras:
      - rebalanceo: backtest 2016-2026 con las reglas de la política (banda de 3 puntos, rango ± 2,
        acción > 7%), fracción vendida de cada acción, ponderada por peso;
      - retiros: lo que el retiro y los costos piden por encima de la renta cobrada (intereses y
        dividendos después de impuestos), como fracción de la cartera, vendido a prorrata.
    """
    from tp.comisiones import comision_anual
    from tp.etapa4 import RANGOS, TOLERANCIA_RANGO, TOPE_ACCION_DISPARO
    from tp.impuestos import tasa_bp
    from tp.monitoreo import backtest, realizacion_acciones
    holgura = {c: (lo - TOLERANCIA_RANGO, hi + TOLERANCIA_RANGO) for c, (lo, hi) in RANGOS.items()}
    ventana = ins.extra["ventana"]
    wc = pd.Series(w, index=ins.activos)
    clase = dict(zip(ins.activos, ins.clase))
    mon = backtest(ventana[ins.activos], wc, clase, 0.03, holgura, TOPE_ACCION_DISPARO, dict(zip(ins.activos, ins.tipo)))
    b = insumos_benchmark(ins)
    idx = ins.extra["ret_indices"].loc[ventana.index[0]:ventana.index[-1], b.clase]
    idx.columns = b.activos
    wb = pd.Series(b.pesos, index=b.activos)
    clase_b = dict(zip(b.activos, b.clase))
    mon_b = backtest(idx, wb, clase_b, 0.03, holgura, TOPE_ACCION_DISPARO)
    costos = (float(comision_anual(caso.capital)) + tasa_bp(2027) * (caso.capital + caso.valor_casa)) / caso.capital
    pide = 12 * caso.gasto_mes / caso.capital + costos

    def retiros(renta: np.ndarray, pesos: np.ndarray) -> float:
        return max(0.0, pide - float(pesos @ renta) * (1 - 0.35))

    rc = realizacion_acciones(mon, wc, clase)
    rb = realizacion_acciones(mon_b, wb, clase_b)
    vc, vb = retiros(ins.renta.values, np.asarray(w)), retiros(b.renta.values, b.pesos)
    return {"cartera": rc + vc, "benchmark": rb + vb, "rebalanceo_cartera": rc, "rebalanceo_benchmark": rb,
            "retiros_cartera": vc, "retiros_benchmark": vb}


def retornos_diarios_historicos(ins, desde: str, hasta: str) -> pd.DataFrame:
    """Retornos diarios de los 14 activos: los propios si cotizaron toda la ventana (fondos rellenados con su
    índice); si no, el índice de su clase en toda la ventana (SCHP, que nace en 2010; V, que sale a bolsa en
    marzo de 2008). Es la misma regla que caida_2008."""
    precios = ins.extra["precios"].loc[:hasta]
    idx = ins.extra["ret_indices"]
    fechas = idx.loc[desde:hasta].index
    out = {}
    for a, c in zip(ins.activos, ins.clase):
        propio = precios[a].pct_change(fill_method=None).reindex(fechas)
        out[a] = propio if propio.notna().all() else idx[c].reindex(fechas)
    return pd.DataFrame(out, index=fechas)


def caidas_2008(ins, w: np.ndarray) -> dict:
    """Cuatro métricas de la crisis, con la misma regla para la cartera y el 50/50 de índices.

    - Año 2008 (31/12/2007 a 31/12/2008) con pesos fijos y con el rebalanceo de la política (revisión
      mensual, banda de 3 puntos, rango ± 2, acción > 7%).
    - Máxima caída de pico a valle entre octubre de 2007 y marzo de 2009, con pesos fijos y con rebalanceo.
    Nominal, antes de impuestos, sin retiros.
    """
    from tp.etapa4 import RANGOS, TOLERANCIA_RANGO, TOPE_ACCION_DISPARO
    from tp.monitoreo import backtest, maxima_caida
    holgura = {c: (lo - TOLERANCIA_RANGO, hi + TOLERANCIA_RANGO) for c, (lo, hi) in RANGOS.items()}
    wc = pd.Series(w, index=ins.activos)
    clase = dict(zip(ins.activos, ins.clase))
    tipo = dict(zip(ins.activos, ins.tipo))
    b = insumos_benchmark(ins)
    wb = pd.Series(b.pesos, index=b.activos)
    clase_b = dict(zip(b.activos, b.clase))

    def correr(desde, hasta, rebalancea):
        rc = retornos_diarios_historicos(ins, desde, hasta)
        rb = ins.extra["ret_indices"].loc[desde:hasta, b.clase]
        rb.columns = b.activos
        kw = dict(banda=0.03, rangos=holgura, tope_accion=TOPE_ACCION_DISPARO) if rebalancea else \
            dict(banda=10.0, rangos=None, tope_accion=10.0)
        return (backtest(rc, wc, clase, tipo=tipo, **kw), backtest(rb, wb, clase_b, **kw))

    out = {}
    for nombre, reb in (("fijos", False), ("rebalanceo", True)):
        c, bb = correr("2008-01-01", "2008-12-31", reb)
        out[f"anio_2008_{nombre}"] = {"cartera": float(c.valores.iloc[-1] - 1), "benchmark": float(bb.valores.iloc[-1] - 1),
                                      "rebalanceos": [len(c.eventos), len(bb.eventos)]}
        c, bb = correr("2007-10-01", "2009-03-31", reb)
        out[f"maxima_caida_{nombre}"] = {"cartera": maxima_caida(c.valores), "benchmark": maxima_caida(bb.valores),
                                         "rebalanceos": [len(c.eventos), len(bb.eventos)]}
    return out
