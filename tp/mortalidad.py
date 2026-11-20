"""Ley de mortalidad de Gompertz (la que usan Milevsky y Robinson, 2005).

m: edad modal de muerte. b: dispersión. Probabilidad de seguir viva t años más
a partir de la edad x: S(t) = exp(exp((x - m) / b) * (1 - exp(t / b))).
"""
import numpy as np


def supervivencia(edad: float, t, m: float, b: float) -> np.ndarray:
    return np.exp(np.exp((edad - m) / b) * (1 - np.exp(np.asarray(t, dtype=float) / b)))


def muestrear_anios_de_vida(edad: float, m: float, b: float, n: int,
                            rng: np.random.Generator) -> np.ndarray:
    """Años de vida restantes por inversión de S(t) = u, con u uniforme."""
    u = rng.uniform(size=n)
    return b * np.log(1 - np.log(u) / np.exp((edad - m) / b))


def esperanza_de_vida(edad: float, m: float, b: float) -> float:
    """Años de vida esperados: integral de S(t)."""
    t = np.linspace(0, 120, 12_001)
    return float(np.trapezoid(supervivencia(edad, t, m, b), t))
