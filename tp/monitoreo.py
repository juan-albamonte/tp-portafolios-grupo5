"""Monitoreo y rebalanceo con historia (M5): backtest ilustrativo de las reglas de la política.

Arranca con los pesos objetivo, deja que los pesos deriven con los retornos diarios y, en la
revisión del último día hábil de cada mes, aplica las reglas de la sección 17 de la política:
  - una clase se aparta más de `banda` de su peso objetivo;
  - una clase sale de su rango;
  - una acción supera el tope.
Si alguna se cumple, vuelve todos los activos a sus pesos objetivo. No modela retiros ni
impuestos: muestra cuándo y cuánto se habría operado, no es evidencia de performance.
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class Monitoreo:
    eventos: list[dict] = field(default_factory=list)
    desvio_max: dict[str, float] = field(default_factory=dict)  # mayor |desvío| por clase en las revisiones
    rotacion_anual: float = 0.0  # ½·Σ|Δw| por año, promedio
    revisiones: int = 0
    anios: float = 0.0
    valores: pd.Series | None = None  # valor diario de la cartera (1 al inicio, sin retiros)

    @property
    def fechas(self) -> list[pd.Timestamp]:
        return [e["fecha"] for e in self.eventos]


def backtest(r: pd.DataFrame, w_obj: pd.Series, clase: dict[str, str], banda: float = 0.03,
             rangos: dict[str, tuple[float, float]] | None = None, tope_accion: float = 0.05,
             tipo: dict[str, str] | None = None) -> Monitoreo:
    """r: retornos diarios (columnas = activos). w_obj: pesos objetivo (suman 1)."""
    activos = list(w_obj.index)
    r = r[activos]
    obj = w_obj.values.astype(float)
    clases = sorted(set(clase[a] for a in activos))
    M = np.array([[clase[a] == c for a in activos] for c in clases], float)  # clase × activo
    obj_c = M @ obj
    acciones = np.array([(tipo or {}).get(a) == "accion" for a in activos])
    fin_de_mes = set(r.groupby(r.index.to_period("M")).tail(1).index)
    w = obj.copy()
    out = Monitoreo(desvio_max={c: 0.0 for c in clases})
    rotacion, valor = 0.0, 1.0
    valores = []
    for fecha, ret in zip(r.index, r.values):
        w = w * (1 + ret)
        valor *= w.sum()
        valores.append(valor)
        w = w / w.sum()
        if fecha not in fin_de_mes:
            continue
        out.revisiones += 1
        desvio = M @ w - obj_c
        for c, d in zip(clases, desvio):
            out.desvio_max[c] = max(out.desvio_max[c], abs(d))
        motivo = []
        if np.any(np.abs(desvio) > banda + 1e-12):
            motivo.append(f"banda de {banda:.0%}")
        if rangos and any(not (rangos[c][0] - 1e-12 <= x <= rangos[c][1] + 1e-12) for c, x in zip(clases, M @ w)):
            motivo.append("fuera de rango")
        if np.any(w[acciones] > tope_accion + 1e-12):
            motivo.append(f"tope de {tope_accion:.0%} por acción")
        if not motivo:
            continue
        dif = w - obj
        # La clase más desviada; ante un empate, la que subió (la que se vende).
        i = max(range(len(clases)), key=lambda j: (round(abs(desvio[j]), 9), desvio[j]))
        out.eventos.append({
            "fecha": fecha, "motivo": ", ".join(motivo), "clase_mas_desviada": clases[i], "desvio": float(desvio[i]),
            "pesos_clase": {c: float(x) for c, x in zip(clases, M @ w)},
            "vende": {a: float(d) for a, d in zip(activos, dif) if d > 1e-9},
            "compra": {a: float(-d) for a, d in zip(activos, dif) if d < -1e-9},
            "rotacion": float(np.abs(dif).sum() / 2),
            "valor": float(valor),  # valor de la cartera ese día (1 al inicio, sin retiros)
        })
        rotacion += np.abs(dif).sum() / 2
        w = obj.copy()
    out.valores = pd.Series(valores, index=r.index)
    out.anios = (r.index[-1] - r.index[0]).days / 365.25
    out.rotacion_anual = rotacion / out.anios if out.anios > 0 else 0.0
    return out


def rendimiento_posterior(r: pd.DataFrame, montos: dict[str, float], desde: pd.Timestamp, meses: int = 12) -> float:
    """Retorno de una canasta comprada en `desde` (montos por activo) y mantenida `meses` meses."""
    tramo = r.loc[(r.index > desde) & (r.index <= pd.Timestamp(desde) + pd.DateOffset(months=meses)), list(montos)]
    w = pd.Series(montos) / sum(montos.values())
    return float((w * (1 + tramo).prod()).sum() - 1)


def realizacion_acciones(mon: Monitoreo, w_obj: pd.Series, clase: dict[str, str]) -> float:
    """Fracción de la parte en acciones que se vende por año al rebalancear (ponderada por peso).

    En cada venta, la fracción vendida de la posición es vende / (objetivo + vende). Es la tasa a la que
    se realiza la ganancia de capital por rebalanceo.
    """
    acc = [a for a in w_obj.index if clase[a].startswith("acciones") and w_obj[a] > 0]
    vendido = {a: 0.0 for a in acc}
    for e in mon.eventos:
        for a, v in e["vende"].items():
            if a in vendido:
                vendido[a] += v / (w_obj[a] + v)
    pesos = w_obj[acc] / w_obj[acc].sum()
    return float(sum(pesos[a] * vendido[a] for a in acc) / mon.anios)


def maxima_caida(valores: pd.Series) -> float:
    """Mayor caída de pico a valle (negativa)."""
    v = np.r_[1.0, valores.values]  # el valor inicial también puede ser el pico
    return float((v / np.maximum.accumulate(v) - 1).min())
