"""Estadísticas de la guía, covarianza con shrinkage y correlaciones."""
import numpy as np
import pandas as pd

DIAS = 252


def ledoit_wolf_cc(X, anualizar: int = 12) -> tuple[np.ndarray, float, float]:
    """Covarianza de Ledoit y Wolf (2004), "Honey, I Shrunk the Sample Covariance Matrix".

    Encoge la covarianza muestral S hacia un objetivo F de correlación constante:
    F conserva las varianzas de S y reemplaza cada correlación por la promedio r̄.
    Σ = δF + (1−δ)S, con la intensidad óptima δ = max(0, min(1, κ/T)) y
    κ = (π̂ − ρ̂)/γ̂: π̂ es el ruido de estimación de S, ρ̂ el de F (que comparte
    las varianzas) y γ̂ cuán lejos está F de S. Misma fórmula que el covCor.m de
    los autores. X: T×N sin faltantes. Devuelve (Σ anualizada, δ, r̄).
    """
    X = np.asarray(X, dtype=float)
    T, n = X.shape
    Y = X - X.mean(axis=0)
    S = Y.T @ Y / T
    var = np.diag(S)
    sd = np.sqrt(var)
    R = S / np.outer(sd, sd)
    rbar = (R.sum() - n) / (n * (n - 1))
    F = rbar * np.outer(sd, sd)
    np.fill_diagonal(F, var)

    Y2 = Y ** 2
    pi_mat = Y2.T @ Y2 / T - S ** 2
    pi_hat = pi_mat.sum()

    theta = (Y ** 3).T @ Y / T - var[:, None] * S   # ϑ_ii,ij
    np.fill_diagonal(theta, 0.0)
    rho_hat = np.trace(pi_mat) + rbar * (np.outer(1 / sd, sd) * theta).sum()

    gamma_hat = ((F - S) ** 2).sum()
    kappa = (pi_hat - rho_hat) / gamma_hat
    delta = float(max(0.0, min(1.0, kappa / T)))
    return anualizar * (delta * F + (1 - delta) * S), delta, float(rbar)


def maxima_caida(r: pd.Series) -> tuple[float, object, object]:
    """Peor caída desde un máximo: (caída, fecha del pico, fecha del valle)."""
    valor = (1 + r).cumprod()
    pico_corrido = np.maximum.accumulate(np.r_[1.0, valor.values])[1:]
    caidas = pd.Series(valor.values / pico_corrido - 1, index=r.index)
    valle = caidas.idxmin()
    hasta_valle = valor.loc[:valle]
    pico = hasta_valle.idxmax() if hasta_valle.max() >= 1 else r.index[0]
    return float(caidas.min()), pico, valle


def retorno_anio(r: pd.DataFrame, anio: int) -> pd.Series:
    """Retorno compuesto de un año calendario."""
    return (1 + r.loc[str(anio)]).prod() - 1


def estadisticas_guia(r_diarios: pd.DataFrame, pesos_benchmark: dict[str, float],
                      rf: float) -> pd.DataFrame:
    """Lo que pide la guía, por serie y para el benchmark (pesos fijos, rebalanceo diario).

    Retorno anual: compuesto (geométrico). Desvío anual: diario × √252.
    Sharpe: (retorno anual − rf) / desvío anual.
    """
    r = r_diarios.copy()
    r["benchmark"] = sum(w * r[c] for c, w in pesos_benchmark.items())
    filas = {}
    for c in r:
        x = r[c].dropna()
        anual = (1 + x).prod() ** (DIAS / len(x)) - 1
        desvio_anual = x.std() * np.sqrt(DIAS)
        filas[c] = {
            "retorno_diario_medio": x.mean(),
            "desvio_diario": x.std(),
            "retorno_anual": anual,
            "desvio_anual": desvio_anual,
            "sharpe": (anual - rf) / desvio_anual if desvio_anual > 0 else np.nan,
            "maxima_caida": maxima_caida(x)[0],
        }
    return pd.DataFrame(filas).T


def correlacion_por_clase(R: pd.DataFrame, clase_de: dict[str, str]) -> pd.DataFrame:
    """Correlación promedio entre los activos de cada par de clases (sin la diagonal)."""
    clases = list(dict.fromkeys(clase_de[a] for a in R.index))
    out = pd.DataFrame(index=clases, columns=clases, dtype=float)
    for a in clases:
        for b in clases:
            ia = [x for x in R.index if clase_de[x] == a]
            ib = [x for x in R.index if clase_de[x] == b]
            bloque = R.loc[ia, ib].values
            if a == b:
                k = len(ia)
                out.loc[a, b] = 1.0 if k == 1 else (bloque.sum() - k) / (k * (k - 1))
            else:
                out.loc[a, b] = bloque.mean()
    return out
