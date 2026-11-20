"""Del escenario base (EIC, economía) a los números que usa el modelo.

Los retornos de largo plazo de config.RETORNO_LARGO_PLAZO son compuestos
(geométricos), como los publican las gestoras. Black-Litterman y el Monte Carlo
necesitan retornos esperados aritméticos: la conversión es lognormal.
"""
import math

# Vol anual por clase de los índices de referencia (diarios, 06/2007-10/2026,
# checkpoint 2). Solo para pasar de compuesto a aritmético.
VOL_CLASES = {
    "liquidez": 0.0049,
    "tesoro": 0.0697,
    "tips": 0.0628,
    "corporativos": 0.0883,
    "acciones_eeuu": 0.1966,
    "acciones_europa": 0.2349,
}


def a_real(nominal: float, inflacion: float) -> float:
    return (1 + nominal) / (1 + inflacion) - 1


def a_aritmetico(compuesto: float, vol: float) -> float:
    """Retorno esperado aritmético de una lognormal con mediana 1+compuesto y desvío vol.

    Si log(1+R) ~ N(m, s²): 1+g = e^m, 1+E[R] = e^(m+s²/2) y
    s² = log(1 + vol²/(1+E[R])²). Se resuelve por punto fijo (≈ g + vol²/2).
    """
    a = compuesto + vol ** 2 / 2
    for _ in range(50):
        s2 = math.log(1 + vol ** 2 / (1 + a) ** 2)
        a = (1 + compuesto) * math.exp(s2 / 2) - 1
    return a


def exceso_benchmark(retornos: dict[str, float], vols: dict[str, float], pesos: dict[str, float],
                     tasa_corta: float) -> float:
    """Exceso aritmético esperado del benchmark sobre la tasa corta: w_b'π en Black-Litterman."""
    return sum(w * a_aritmetico(retornos[c], vols[c]) for c, w in pesos.items()) - tasa_corta
