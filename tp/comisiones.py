"""Comisión del asesor: tasa marginal por tramo (1% / 0,6% / 0,4%)."""
import numpy as np

TRAMOS = ((2_000_000.0, 0.010), (10_000_000.0, 0.006), (float("inf"), 0.004))


def comision_anual(valor, tramos=TRAMOS) -> np.ndarray:
    """Comisión anual en USD. Cada tramo cobra su tasa solo sobre la parte que cae en él."""
    v = np.asarray(valor, dtype=float)
    total = np.zeros_like(v)
    piso = 0.0
    for techo, tasa in tramos:
        total = total + np.clip(v - piso, 0.0, techo - piso) * tasa
        piso = techo
    return total
