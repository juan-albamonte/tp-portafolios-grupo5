"""Black-Litterman en la formulación de mercado de Meucci (2010, secc. 3), sin τ.

El prior es el equilibrio: π = λ·Σ·w_b (retornos esperados en exceso de la tasa corta
de largo plazo), con λ calibrado para que la cartera neutra rinda el exceso del
escenario base (w_b'π = Mercado.exceso_esperado_benchmark).

Posterior (ecs. 32-33):
  μ  = π + ΣP'(PΣP' + Ω)⁻¹(v − Pπ)
  Σ_post = Σ − ΣP'(PΣP' + Ω)⁻¹PΣ
La optimización usa μ con la Σ de mercado; Σ_post se reporta solo como dato.
"""
import numpy as np


def calibrar_lambda(Sigma: np.ndarray, w_b: np.ndarray, exceso: float) -> float:
    return exceso / float(w_b @ Sigma @ w_b)


def equilibrio(Sigma: np.ndarray, w_b: np.ndarray, lam: float) -> np.ndarray:
    return lam * Sigma @ w_b


def posterior_mercado(pi: np.ndarray, Sigma: np.ndarray, P: np.ndarray, v: np.ndarray,
                      Omega: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    PS = P @ Sigma
    K = np.linalg.solve(PS @ P.T + Omega, PS).T  # ΣP'(PΣP'+Ω)⁻¹
    mu = pi + K @ (v - P @ pi)
    Sigma_post = Sigma - K @ PS
    return mu, (Sigma_post + Sigma_post.T) / 2
