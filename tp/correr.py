"""Programa único del TP: corre las etapas en orden e imprime cada checkpoint.

Uso: python -m tp.correr [--etapa N]   (sin --etapa corre todas las disponibles)
"""
import argparse
import contextlib
import json
import sys

import numpy as np
import pandas as pd

from tp import screening as etapa_screening
from tp import universo as etapa_universo
from tp.config import (BENCHMARK, CLASES, DATA, SALIDAS, FIN_DATOS, INICIO_DATOS, PROXIES, RELLENO,
                       VENTANA_ANIOS)
from tp.datos import a_mensual, cargar_o_bajar, control_relleno, rellenar_hacia_atras, retornos
from tp.estadisticas import (correlacion_por_clase, estadisticas_guia, ledoit_wolf_cc, maxima_caida,
                             retorno_anio)
from tp.mercado import foto_mercado

pd.set_option("display.width", 250)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)


def titulo(texto: str) -> None:
    print(f"\n{'=' * 100}\n{texto}\n{'=' * 100}")


def cargar_universo() -> pd.DataFrame:
    return pd.read_csv(DATA / "universo.csv", keep_default_na=False)


def precios_diarios(universo: pd.DataFrame) -> pd.DataFrame:
    tickers = sorted(set(universo["ticker"]) | set(PROXIES.values()))
    return cargar_o_bajar(DATA / "precios_diarios.csv", tickers, INICIO_DATOS, FIN_DATOS)


def con_relleno(precios: pd.DataFrame) -> pd.DataFrame:
    p = precios.copy()
    for fondo, indice in RELLENO.items():
        p[fondo] = rellenar_hacia_atras(p[fondo], p[indice])
    return p


def ventana_comun(ret: pd.DataFrame, anios: int = VENTANA_ANIOS) -> pd.DataFrame:
    """Últimos 'anios' años (por calendario, sirve para diarios y mensuales).

    Quedan afuera los activos sin historia en toda la ventana.
    """
    desde = ret.index[-1] - pd.DateOffset(years=anios)
    ventana = ret.loc[ret.index > desde]
    completos = ventana.columns[ventana.notna().all()]
    return ventana[completos]


def etapa_datos(universo: pd.DataFrame, imprimir: bool = True) -> dict:
    crudos = precios_diarios(universo)
    precios = con_relleno(crudos)
    activos = list(universo["ticker"])
    clase_de = dict(zip(universo["ticker"], universo["clase"]))

    # Σ principal: retornos diarios de la ventana común, anualizados con 252.
    ret_d = retornos(precios[activos])
    ventana = ventana_comun(ret_d)
    afuera = [a for a in activos if a not in ventana.columns]
    Sigma, delta, rbar = ledoit_wolf_cc(ventana.values, anualizar=252)
    Sigma = pd.DataFrame(Sigma, index=ventana.columns, columns=ventana.columns)
    # Σ mensual: solo para comparar carteras en el checkpoint 4.
    ret_m = retornos(a_mensual(precios[activos]))
    ventana_m = ventana_comun(ret_m)[ventana.columns]
    Sigma_m, delta_m, rbar_m = ledoit_wolf_cc(ventana_m.values, anualizar=12)
    Sigma_m = pd.DataFrame(Sigma_m, index=ventana.columns, columns=ventana.columns)

    # Estadísticas de la guía con los índices de referencia (historia completa, diaria).
    indices = precios[list(PROXIES.values())].dropna()
    ret_idx = retornos(indices).rename(columns={v: k for k, v in PROXIES.items()})
    rf_hist = (1 + ret_idx["liquidez"]).prod() ** (252 / len(ret_idx)) - 1
    guia = estadisticas_guia(ret_idx, BENCHMARK, rf_hist)
    r_bench = sum(w * ret_idx[c] for c, w in BENCHMARK.items())
    caida, pico, valle = maxima_caida(r_bench)
    r2008 = retorno_anio(ret_idx.assign(benchmark=r_bench), 2008)

    controles = {f: control_relleno(crudos[f], crudos[i]) for f, i in RELLENO.items()}
    mercado = foto_mercado(DATA / "mercado.json")

    # Por activo, en la ventana común (los que quedan afuera, con su propia historia).
    filas = []
    for a in activos:
        r = ventana[a] if a in ventana else ret_d[a].dropna()
        filas.append({"ticker": a, "clase": clase_de[a],
                      "desde": r.index[0].strftime("%Y-%m-%d"),
                      "retorno_anual": (1 + r).prod() ** (252 / len(r)) - 1,
                      "vol_anual": r.std() * np.sqrt(252),
                      "maxima_caida": maxima_caida(r)[0]})
    por_activo = pd.DataFrame(filas).set_index("ticker")
    sd = np.sqrt(np.diag(Sigma))
    corr_lw = pd.DataFrame(Sigma.values / np.outer(sd, sd), index=Sigma.index, columns=Sigma.index)
    corr_clases = correlacion_por_clase(corr_lw, clase_de)

    res = dict(precios=precios, ret_mensuales=ret_m, ret_diarios=ret_d, ventana=ventana, Sigma=Sigma,
               delta=delta, rbar=rbar, Sigma_mensual=Sigma_m, delta_mensual=delta_m,
               rbar_mensual=rbar_m, meses=len(ventana_m), guia=guia, caida_benchmark=(caida, pico, valle), r2008=r2008,
               controles=controles, mercado=mercado, por_activo=por_activo,
               corr_clases=corr_clases, afuera=afuera, ret_indices=ret_idx)
    if imprimir:
        imprimir_datos(res)
    return res


def imprimir_datos(r: dict) -> None:
    v = r["ventana"]
    titulo("ETAPA 2: DATOS Y ESTADÍSTICAS")
    print(f"Fuente: Yahoo Finance (yfinance, cierres diarios ajustados por dividendos y splits).")
    print(f"Precios diarios: {r['precios'].index[0].date()} a {r['precios'].index[-1].date()}.")
    print(f"Ventana común (retornos diarios): {v.index[0].date()} a {v.index[-1].date()}, "
          f"{len(v)} días, {v.shape[1]} activos.")
    print(f"Fuera de la ventana (sin historia completa ni relleno aprobado): {', '.join(r['afuera']) or '-'}")

    titulo("RELLENO HACIA ATRÁS: control en el período en que coexisten (retornos diarios)")
    for fondo, c in r["controles"].items():
        print(f"{fondo} vs {RELLENO[fondo]}: {c['desde'].date()} a {c['hasta'].date()} ({c['dias']} días) | "
              f"correlación {c['correlacion_diaria']:.4f} | vol fondo {c['vol_fondo']:.2%} | "
              f"vol índice {c['vol_indice']:.2%} | diferencia {c['dif_vol_anual']:+.2%}")

    titulo("COVARIANZA: Ledoit-Wolf (2004), objetivo de correlación constante")
    print(f"Principal (diaria, ×252): T = {len(v)} días, N = {v.shape[1]}, T/N = {len(v) / v.shape[1]:.0f} | "
          f"r̄ = {r['rbar']:.3f} | δ = {r['delta']:.4f}")
    print(f"Comparación (mensual, ×12): T = {r['meses']} meses, T/N = {r['meses'] / v.shape[1]:.1f} | "
          f"r̄ = {r['rbar_mensual']:.3f} | δ = {r['delta_mensual']:.4f}")

    titulo("POR ACTIVO (ventana común, diarios; retorno anual compuesto, vol anual, máxima caída)")
    pa = r["por_activo"].copy()
    for c in ["retorno_anual", "vol_anual", "maxima_caida"]:
        pa[c] = pa[c].map("{:.2%}".format)
    print(pa.to_string())

    titulo("CORRELACIÓN PROMEDIO POR CLASE (de la Σ de Ledoit-Wolf)")
    print(r["corr_clases"].round(2).to_string())

    titulo(f"ESTADÍSTICAS DE LA GUÍA (índices de referencia, diarios, "
           f"{r['ret_indices'].index[0].date()} a {r['ret_indices'].index[-1].date()})")
    g = r["guia"].copy()
    fmt = {"retorno_diario_medio": "{:.4%}", "desvio_diario": "{:.3%}", "retorno_anual": "{:.2%}",
           "desvio_anual": "{:.2%}", "sharpe": "{:.2f}", "maxima_caida": "{:.2%}"}
    for c, f in fmt.items():
        g[c] = g[c].map(f.format)
    g.index = [f"{i} ({PROXIES[i]})" if i in PROXIES else i for i in g.index]
    print(g.to_string())
    print("Benchmark: pesos fijos de config.BENCHMARK, rebalanceo diario. "
          "Sharpe con la tasa de las letras (BIL) del período.")
    caida, pico, valle = r["caida_benchmark"]
    print(f"Peor caída histórica del benchmark: {caida:.2%} (pico {pico.date()}, valle {valle.date()})")
    print("\nCorrelaciones diarias entre clases (índices de referencia):")
    print(r["ret_indices"].corr().round(2).to_string())
    print("\nRetornos de 2008 por clase (para el estrés):")
    print(r["r2008"].map("{:.2%}".format).to_string())

    titulo("FOTO DEL MERCADO (FRED)")
    for nombre, d in r["mercado"].items():
        print(f"{nombre:13s} {d['serie']:7s} {d['valor']:.2%}  ({d['fecha']})")


class _Copia:
    """Duplica lo que se imprime en un archivo (para outputs/checkpointN.txt)."""

    def __init__(self, archivo):
        self.archivo, self.original = archivo, sys.stdout

    def write(self, texto):
        self.original.write(texto)
        self.archivo.write(texto)

    def flush(self):
        self.original.flush()
        self.archivo.flush()


@contextlib.contextmanager
def a_archivo(nombre: str):
    SALIDAS.mkdir(exist_ok=True)
    with open(SALIDAS / nombre, "w", encoding="utf-8") as f, contextlib.redirect_stdout(_Copia(f)):
        yield


def _limpio(x):
    """JSON estricto: NaN → null, numpy → tipos de Python."""
    if isinstance(x, dict):
        return {str(k): _limpio(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_limpio(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if np.isnan(x) else round(float(x), 6)
    if isinstance(x, np.integer):
        return int(x)
    return x


def guardar_resumen(clave: str, datos: dict) -> None:
    """Agrega o reemplaza una sección de outputs/resumen.json."""
    archivo = SALIDAS / "resumen.json"
    resumen = json.loads(archivo.read_text(encoding="utf-8")) if archivo.exists() else {}
    resumen[clave] = _limpio(datos)
    archivo.write_text(json.dumps(resumen, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--etapa", type=int, default=None)
    etapa = parser.parse_args().etapa
    if etapa in (None, 1):
        etapa_universo.main()
    if etapa in (None, 2):
        etapa_datos(cargar_universo())
    if etapa in (None, 3):
        titulo("ETAPA 3b: INDUSTRIA Y SCREENING")
        etapa_screening.main()
    if etapa in (None, 4):
        from tp import etapa4
        with a_archivo("checkpoint4.txt"):
            guardar_resumen("cartera", etapa4.main())
    if etapa in (None, 5):
        from tp import etapa5
        with a_archivo("checkpoint5.txt"):
            guardar_resumen("retiro", etapa5.main())
    if etapa in (None, 6):
        from tp import graficos
        graficos.main()
        graficos.main(graficos.CARPETA / "deck", deck=True)
    if etapa in (None, 7):
        from tp import cifras, excel
        cifras.main()
        excel.main()


if __name__ == "__main__":
    main()
