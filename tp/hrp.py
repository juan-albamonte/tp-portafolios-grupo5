"""Hierarchical Risk Parity (López de Prado, 2016).

1. Distancia d = √(0,5·(1 − ρ)) y clustering jerárquico single-linkage.
2. Cuasi-diagonalización: ordenar los activos según las hojas del árbol.
3. Bisección recursiva: cada mitad recibe peso en proporción inversa a su varianza
   (calculada con pesos de varianza inversa dentro de la mitad).
No usa retornos esperados. El ajuste a rangos y topes está en optimizacion.mas_cercana.
"""
import numpy as np
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform


def _var_cluster(S: np.ndarray, idx: list[int]) -> float:
    s = S[np.ix_(idx, idx)]
    ivp = 1 / np.diag(s)
    ivp /= ivp.sum()
    return float(ivp @ s @ ivp)


def hrp(Sigma: np.ndarray) -> np.ndarray:
    n = Sigma.shape[0]
    sd = np.sqrt(np.diag(Sigma))
    rho = np.clip(Sigma / np.outer(sd, sd), -1, 1)
    if n == 1:
        return np.ones(1)
    d = np.sqrt(np.clip(0.5 * (1 - rho), 0, None))
    np.fill_diagonal(d, 0)
    orden = list(leaves_list(linkage(squareform(d, checks=False), method="single")))
    w = np.ones(n)
    grupos = [orden]
    while grupos:
        nuevos = []
        for g in grupos:
            if len(g) < 2:
                continue
            a, b = g[: len(g) // 2], g[len(g) // 2:]
            va, vb = _var_cluster(Sigma, a), _var_cluster(Sigma, b)
            alfa = 1 - va / (va + vb)
            w[a] *= alfa
            w[b] *= 1 - alfa
            nuevos += [a, b]
        grupos = nuevos
    return w / w.sum()
