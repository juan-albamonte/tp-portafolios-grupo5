"""Monte Carlo de la cartera con retiros: USD reales, pasos anuales, rebalanceo anual.

Retornos: lognormal multivariada por activo, con media aritmética μ y covarianza Σ de los
retornos simples (nominales en USD). Las normales estándar se generan una sola vez y se
reusan en todos los escenarios y sensibilidades (números aleatorios comunes).

Orden de cada año t (t = 0 es 2026):
  1. regla de retiro (Guyton-Klinger, si hay barandas),
  2. retira al principio del año (si está viva),
  3. paga comisión y Bienes Personales,
  4. rinde el retorno de la cartera después de impuestos, en términos reales.
Ruina: estando viva, la cartera no alcanza para el retiro del año.
"""
from dataclasses import dataclass
from typing import Callable

import numpy as np

from tp.config import Impuestos
from tp.impuestos import tasa_efectiva, tasa_ganancia_realizada
from tp.retiro import ajustar_retiro


@dataclass
class ResultadoMC:
    valor: np.ndarray       # (n, T+1) valor real al inicio de cada año
    retiro: np.ndarray      # (n, T) retiro real pagado (0 después de morir)
    anios_vida: np.ndarray  # (n,)
    ruina: np.ndarray       # (n,) True si se quedó sin plata estando viva
    anio_ruina: np.ndarray | None = None  # (n,) año (0 = 2026) en que no alcanzó; NaN si nunca

    @property
    def prob_ruina(self) -> float:
        return float(self.ruina.mean())

    def prob_recorte(self, umbral: float = 0.8) -> float:
        """Probabilidad de que, en vida, el retiro real caiga debajo de umbral × el inicial."""
        T = self.retiro.shape[1]
        vivo = np.arange(T)[None, :] < self.anios_vida[:, None]
        bajo = (self.retiro < umbral * self.retiro[:, [0]]) & vivo
        return float(bajo.any(axis=1).mean())


@dataclass
class RetornoCartera:
    real: np.ndarray     # (n, T) después de impuestos, real
    nominal: np.ndarray  # (n, T) después de impuestos, nominal (lo usa la regla de inflación de Guyton-Klinger)


def normales(n: int, anios: int, k: int, rng: np.random.Generator) -> np.ndarray:
    return rng.standard_normal((n, anios, k))


def parametros_lognormales(mu: np.ndarray, Sigma: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Media y covarianza de log(1+R) para que R tenga media mu y covarianza Sigma."""
    g = 1 + np.asarray(mu, float)
    C = np.log1p(np.asarray(Sigma, float) / np.outer(g, g))
    return np.log(g) - 0.5 * np.diag(C), C


def retornos_lognormales(Z: np.ndarray, mu: np.ndarray, Sigma: np.ndarray) -> np.ndarray:
    """Retornos simples (n, anios, k) a partir de normales estándar Z."""
    m, C = parametros_lognormales(mu, Sigma)
    L = np.linalg.cholesky(C)
    return np.expm1(m + Z @ L.T)


def tasas_impositivas(renta_fija: np.ndarray, renta: np.ndarray, imp: Impuestos, mu: np.ndarray | None = None,
                      realizacion: float | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Impuesto anual de cada activo = t_r · r_nominal + k (lineal en el retorno, como en la etapa 4).

    Renta fija (incluye TIPS): todo el retorno es interés → t_r = 35%, k = 0.
    Acción: dividendo d al 35% y el resto (r − d) al 15% → t_r = 15%, k = (35% − 15%)·d.
    Con retornos negativos el impuesto da negativo: la pérdida compensa ganancias (quebranto).
    Simplificación: se compensa en el mismo año, no en los cinco siguientes.

    Con `realizacion` (fracción de cada acción que se vende por año) y `mu` (retorno esperado nominal),
    la ganancia de capital paga al vender: su tasa efectiva es tasa_ganancia_realizada(15%, f, μ − d).
    Sin `realizacion`, paga 15% todos los años (supuesto conservador de la v2).
    """
    t_int = tasa_efectiva(imp.retencion_eeuu_intereses, imp.tasa_ar_intereses)
    t_div = tasa_efectiva(imp.retencion_eeuu_dividendos, imp.tasa_ar_dividendos)
    rf = np.asarray(renta_fija, bool)
    renta = np.asarray(renta, float)
    if realizacion is None:
        t_g = np.full(len(rf), imp.tasa_ganancia_capital)
    else:
        t_g = np.array([tasa_ganancia_realizada(imp.tasa_ganancia_capital, realizacion, m - d)
                        for m, d in zip(np.asarray(mu, float), renta)])
    t_r = np.where(rf, t_int, t_g)
    k = np.where(rf, 0.0, (t_div - t_g) * renta)
    return t_r, k


def retorno_cartera(R_nominal: np.ndarray, w: np.ndarray, t_r: np.ndarray | None = None,
                    k: np.ndarray | None = None, inflacion: float = 0.0,
                    gasto: np.ndarray | None = None) -> RetornoCartera:
    """Retorno de la cartera rebalanceada cada año, después de impuestos (t_r, k) y en reales.

    Sin t_r ni k, sin impuestos. gasto: gasto anual de cada fondo (expense ratio). Se descuenta
    del retorno nominal del activo antes de impuestos, como en un fondo real: reduce lo que
    distribuye y lo que gana de precio.
    """
    w = np.asarray(w, float)
    t_r = np.zeros_like(w) if t_r is None else t_r
    k = np.zeros_like(w) if k is None else k
    R = R_nominal if gasto is None else R_nominal - np.asarray(gasto, float)
    nominal = R @ (w * (1 - t_r)) - float(w @ k)
    return RetornoCartera(real=(1 + nominal) / (1 + inflacion) - 1, nominal=nominal)


def costos_anuales(v: np.ndarray, t: int, anio_inicio: int, valor_casa: Callable[[int], float],
                   tasa_bp: Callable[[int], float], comision: Callable) -> np.ndarray:
    """Comisión por tramos sobre la cartera + Bienes Personales sobre la cartera y el depto."""
    return comision(v) + tasa_bp(anio_inicio + t) * (v + valor_casa(t))


def simular(capital: float, retiro_anual: float, rp_real: np.ndarray, rp_nominal: np.ndarray,
            anios_vida: np.ndarray, costos: Callable[[np.ndarray, int], np.ndarray], con_barandas: bool = True,
            inflacion: float = 0.0, baranda: float = 0.20, ajuste: float = 0.10, piso: float = 0.0) -> ResultadoMC:
    """piso: retiro real anual mínimo con barandas (el gasto base); sin barandas no se usa."""
    n, T = rp_real.shape
    anios_vida = np.asarray(anios_vida, float)
    valor = np.empty((n, T + 1))
    valor[:, 0] = capital
    pagos = np.zeros((n, T))
    retiro = np.full(n, float(retiro_anual))
    tasa_inicial = retiro_anual / capital
    ruina = np.zeros(n, dtype=bool)
    anio = np.full(n, np.nan)
    for t in range(T):
        v = valor[:, t]
        if t > 0 and con_barandas:
            retiro = ajustar_retiro(retiro, v, tasa_inicial, rp_nominal[:, t - 1], inflacion, baranda, ajuste,
                                    piso=min(piso, retiro_anual))
        vivo = t < anios_vida
        pide = np.where(vivo, retiro, 0.0)
        no_alcanza = vivo & (pide > v + 1e-9 * capital)
        anio = np.where(np.isnan(anio) & no_alcanza, t, anio)
        ruina |= no_alcanza
        pago = np.minimum(pide, v)
        v = v - pago
        v = np.maximum(v - costos(v, t), 0.0)
        valor[:, t + 1] = v * (1 + rp_real[:, t])
        pagos[:, t] = pago
    return ResultadoMC(valor=valor, retiro=pagos, anios_vida=anios_vida, ruina=ruina, anio_ruina=anio)


def retiro_maximo_seguro(prob_ruina_de: Callable[[float], float], objetivo: float, lo: float = 0.0,
                         hi: float = 1.0, tol: float = 1e-4) -> float:
    """Mayor retiro con probabilidad de ruina ≤ objetivo (bisección).

    Usar siempre los mismos retornos y vidas en cada evaluación para que sea monótona.
    """
    while hi - lo > tol:
        medio = (lo + hi) / 2
        if prob_ruina_de(medio) <= objetivo:
            lo = medio
        else:
            hi = medio
    return lo


def aplicar_shock(R: np.ndarray, primer_anio: np.ndarray) -> np.ndarray:
    """Copia de R con el primer año reemplazado por el shock (mismo para todos los caminos)."""
    out = R.copy()
    out[:, 0, :] = primer_anio
    return out


def compuesto_esperado(media: float, vol: float) -> float:
    """Retorno compuesto (mediana anual) de una lognormal con media aritmética `media` y desvío `vol`."""
    s2 = np.log1p(vol ** 2 / (1 + media) ** 2)
    return float((1 + media) * np.exp(-s2 / 2) - 1)
