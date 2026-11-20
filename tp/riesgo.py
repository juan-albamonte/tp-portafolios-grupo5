"""Aporte de cada posición al riesgo de la cartera (M4)."""
import numpy as np
import pandas as pd


def aporte_al_riesgo(w: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Aporte de cada activo a la volatilidad: w_i·(Σw)_i / σ_p. Los aportes suman σ_p."""
    w = np.asarray(w, float)
    sw = np.asarray(S, float) @ w
    return w * sw / np.sqrt(w @ sw)


def regiones_en_acciones(w: pd.Series, clase: dict[str, str]) -> dict[str, float]:
    """Peso de EE.UU. y de Europa dentro de la parte en acciones."""
    acc = {a: x for a, x in w.items() if clase[a].startswith("acciones")}
    total = sum(acc.values())
    return {r: sum(x for a, x in acc.items() if clase[a] == r) / total for r in ("acciones_eeuu", "acciones_europa")}
