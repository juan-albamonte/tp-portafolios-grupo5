"""Regla de retiro con barandas de Guyton y Klinger (2006). Todo en USD reales."""
import numpy as np


def ajustar_retiro(retiro, valor, tasa_inicial: float, retorno_anterior_nominal, inflacion: float,
                   baranda: float = 0.20, ajuste: float = 0.10, piso: float = 0.0) -> np.ndarray:
    """Aplica un año de la regla, vectorizado sobre las simulaciones.

    1. Si el año anterior la cartera rindió negativo y la tasa actual (retiro / valor) supera
       la inicial, no se ajusta por inflación: en términos reales, el retiro cae lo que subió
       la inflación. Con la tasa en o debajo de la inicial, se ajusta igual (Guyton y Klinger,
       2006; la versión de Guyton 2004 congelaba siempre).
    2. Si la tasa actual (retiro / valor) supera la inicial en más de baranda (20%), recorta ajuste (10%).
    3. Si queda más de baranda por debajo de la inicial, sube ajuste.
    4. El retiro nunca baja de `piso` (USD reales por año): el gasto base que no se recorta.
       Sin piso, la regla recorta hasta que el retiro entra y la ruina es imposible.
    """
    r = np.asarray(retiro, dtype=float)
    v = np.asarray(valor, dtype=float)
    tasa = np.divide(r, v, out=np.full_like(r, np.inf), where=v > 0)
    congela = (np.asarray(retorno_anterior_nominal) < 0) & (tasa > tasa_inicial)
    r = np.where(congela, r / (1 + inflacion), r)
    tasa = np.divide(r, v, out=np.full_like(r, np.inf), where=v > 0)
    r = np.where(tasa > tasa_inicial * (1 + baranda), r * (1 - ajuste), r)
    r = np.where(tasa < tasa_inicial * (1 - baranda), r * (1 + ajuste), r)
    return np.maximum(r, piso)
