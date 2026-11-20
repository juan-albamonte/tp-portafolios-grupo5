"""Cartera neutra para la ingeniería inversa del equilibrio: π = λ·Σ·w_b.

Criterio (aprobado en el checkpoint 3a):
- El benchmark 50/50 fija el peso de cada clase.
- Renta fija: partes iguales entre los fondos elegidos de la clase (hoy, uno por clase).
- Acciones de EE.UU.: cada acción suelta pesa lo que pesa en el mercado de EE.UU.
  (su capitalización sobre la capitalización total), y el fondo amplio (ESGV) se queda
  con el resto. Así la clase replica el mercado: el fondo ya contiene esas acciones, y
  separarlas no cambia la exposición neutra.
- Acciones de Europa: por capitalización entre las elegidas (no hay fondo europeo que
  pase el filtro ESG).

Por qué no "ESGV por capitalización contra las acciones": la capitalización de un fondo
no existe como tal (sus activos bajo gestión, ~USD 10.000 millones, no son comparables con
los USD 4 billones de Microsoft). Con ese criterio el fondo quedaría con peso casi nulo y la
cartera neutra sería una apuesta concentrada en 4-6 acciones, que no es el mercado.

La capitalización total de EE.UU. sale implícita de las mayores posiciones de ESGV
(capitalización de la empresa / su peso en el fondo), así que el "mercado" es el
universo ESG que sigue el fondo, el mismo que puede comprar la clienta.
"""
import statistics

import pandas as pd

RENTA_FIJA = ("liquidez", "tesoro", "tips", "corporativos")


def cap_total_implicita(top: dict[str, float], caps: dict[str, float]) -> float:
    """Capitalización total del índice del fondo: mediana de cap_i / peso_i en sus mayores posiciones."""
    return statistics.median(caps[t] / w for t, w in top.items() if t in caps)


def pesos_neutros(seleccion: pd.DataFrame, benchmark: dict[str, float], caps: dict[str, float],
                  cap_total_eeuu: float) -> pd.Series:
    """Pesos neutros por activo (suman 1). seleccion: columnas ticker, clase, tipo."""
    pesos = {}
    for clase, peso_clase in benchmark.items():
        activos = seleccion[seleccion["clase"] == clase]
        if activos.empty:
            raise ValueError(f"No hay activos elegidos en la clase {clase}")
        if clase in RENTA_FIJA:
            for t in activos["ticker"]:
                pesos[t] = peso_clase / len(activos)
            continue
        acciones = activos[activos["tipo"] == "accion"]["ticker"].tolist()
        fondos = activos[activos["tipo"] == "fondo"]["ticker"].tolist()
        if clase == "acciones_eeuu" and fondos:
            cuotas = {t: caps[t] / cap_total_eeuu for t in acciones}
            resto = 1 - sum(cuotas.values())
            if resto <= 0:
                raise ValueError(f"En acciones_eeuu las acciones elegidas suman más que el mercado ({1 - resto:.0%})")
            for t in fondos:
                cuotas[t] = resto / len(fondos)
        else:
            if fondos:
                raise ValueError(f"Fondo en {clase} sin criterio de peso neutro definido")
            total = sum(caps[t] for t in acciones)
            cuotas = {t: caps[t] / total for t in acciones}
        for t, q in cuotas.items():
            pesos[t] = peso_clase * q
    return pd.Series(pesos, name="peso_neutro")
