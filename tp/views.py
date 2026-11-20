"""Views del EIC en el formato de Meucci (2010), formulación de mercado.

data/views.csv, una fila por view:
- tipo: relativa (largo contra corto) o absoluta (solo largo).
- largo / corto: tickers separados por "+" (canasta). Vacío el corto si es absoluta.
- ponderacion: "iguales" o "cap" (por capitalización) dentro de cada pata.
- eta ∈ {-2, -1, 1, 2}: muy bajista, bajista, alcista, muy alcista.
- u > 0: incertidumbre propia de la view (1 = estándar; más alto = menos confianza).
- frase: la view dicha como la diría un analista. motivo: el dato que la sostiene.

Ec. 11: v_k = (Pπ)_k + η_k · escala · √(PΣP')_kk.
Ec. 13: Ω = (1/c) · diag(u) · PΣP' · diag(u).
"""
import numpy as np
import pandas as pd

COLUMNAS = ["id", "tipo", "largo", "corto", "ponderacion", "eta", "u", "frase", "motivo"]
ETAS = {-2, -1, 1, 2}


def _patas(texto) -> list[str]:
    return [t for t in str(texto).split("+") if t and t != "nan"]


def cargar_views(archivo) -> pd.DataFrame:
    v = pd.read_csv(archivo, keep_default_na=False)
    v["eta"] = v["eta"].astype(int)
    v["u"] = v["u"].astype(float)
    return v[COLUMNAS]


def validar(v: pd.DataFrame, activos: list[str]) -> None:
    if not 5 <= len(v) <= 8:
        raise ValueError(f"Tiene que haber entre 5 y 8 views (hay {len(v)})")
    if not set(v["eta"]) <= ETAS:
        raise ValueError(f"eta fuera de {sorted(ETAS)}: {sorted(set(v['eta']) - ETAS)}")
    if (v["u"] <= 0).any():
        raise ValueError("u tiene que ser positivo")
    for _, f in v.iterrows():
        tickers = _patas(f["largo"]) + _patas(f["corto"])
        fuera = [t for t in tickers if t not in activos]
        if fuera:
            raise ValueError(f"View {f['id']}: activos fuera de la cartera {fuera}")
        if (f["tipo"] == "relativa") != bool(_patas(f["corto"])):
            raise ValueError(f"View {f['id']}: una relativa necesita pata corta y una absoluta no")


def _pesos_pata(tickers: list[str], ponderacion: str, caps: dict[str, float]) -> dict[str, float]:
    if len(tickers) == 1:
        return {tickers[0]: 1.0}
    if ponderacion == "cap":
        total = sum(caps[t] for t in tickers)
        return {t: caps[t] / total for t in tickers}
    return {t: 1 / len(tickers) for t in tickers}


def matriz_P(v: pd.DataFrame, activos: list[str], caps: dict[str, float]) -> pd.DataFrame:
    P = pd.DataFrame(0.0, index=v["id"], columns=activos)
    for _, f in v.iterrows():
        for t, w in _pesos_pata(_patas(f["largo"]), f["ponderacion"], caps).items():
            P.loc[f["id"], t] += w
        for t, w in _pesos_pata(_patas(f["corto"]), f["ponderacion"], caps).items():
            P.loc[f["id"], t] -= w
    return P


def valores_v(v: pd.DataFrame, P: pd.DataFrame, pi: pd.Series, Sigma: pd.DataFrame, escala: float) -> pd.Series:
    Pm = P.values
    S = Sigma.loc[P.columns, P.columns].values
    sd = np.sqrt(np.diag(Pm @ S @ Pm.T))
    return pd.Series(Pm @ pi[P.columns].values + v["eta"].values * escala * sd, index=P.index, name="v")


def omega(P: pd.DataFrame, Sigma: pd.DataFrame, u: np.ndarray, c: float) -> np.ndarray:
    Pm = P.values
    S = Sigma.loc[P.columns, P.columns].values
    D = np.diag(u)
    return D @ (Pm @ S @ Pm.T) @ D / c
