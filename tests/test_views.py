import numpy as np
import pandas as pd
import pytest

from tp.config import DATA
from tp.views import COLUMNAS, cargar_views, matriz_P, omega, validar, valores_v

ACTIVOS = ["ESGV", "NVDA", "ASML", "SAP", "IEF", "SCHP"]
CAPS = {"NVDA": 4.0, "ASML": 0.6, "SAP": 0.3}


def views(filas):
    return pd.DataFrame(filas, columns=COLUMNAS)


def fila(id_, largo, corto="ESGV", eta=1, u=1.0, pond="iguales", tipo="relativa"):
    return (id_, tipo, largo, corto, pond, eta, u, "frase", "motivo")


def test_matriz_P_relativa_y_canasta():
    v = views([fila("V1", "NVDA"), fila("V2", "ASML+SAP", pond="cap"), fila("V3", "SCHP", corto="IEF")])
    P = matriz_P(v, ACTIVOS, CAPS)
    assert list(P.columns) == ACTIVOS
    assert P.loc["V1", "NVDA"] == 1 and P.loc["V1", "ESGV"] == -1
    assert P.loc["V2", "ASML"] == pytest.approx(0.6 / 0.9)
    assert P.loc["V2", "SAP"] == pytest.approx(0.3 / 0.9)
    assert P.loc["V3"].sum() == pytest.approx(0.0)  # relativa: suma cero


def test_matriz_P_absoluta():
    v = views([fila("V1", "NVDA", corto="", tipo="absoluta")])
    assert matriz_P(v, ACTIVOS, CAPS).loc["V1"].sum() == pytest.approx(1.0)


def test_valores_v_ecuacion_11_de_meucci():
    v = views([fila("V1", "NVDA", eta=2), fila("V2", "SCHP", corto="IEF", eta=-1)])
    P = matriz_P(v, ACTIVOS, CAPS)
    rng = np.random.default_rng(0)
    A = rng.normal(size=(6, 6))
    Sigma = pd.DataFrame(A @ A.T / 10, index=ACTIVOS, columns=ACTIVOS)
    pi = pd.Series(np.linspace(0.02, 0.07, 6), index=ACTIVOS)
    out = valores_v(v, P, pi, Sigma, escala=0.25)
    sd = np.sqrt(np.diag(P.values @ Sigma.values @ P.values.T))
    esperado = P.values @ pi.values + np.array([2, -1]) * 0.25 * sd
    assert out.values == pytest.approx(esperado)


def test_omega_ecuacion_13_de_meucci():
    v = views([fila("V1", "NVDA", u=2.0), fila("V2", "ASML")])
    P = matriz_P(v, ACTIVOS, CAPS)
    Sigma = pd.DataFrame(np.eye(6) * 0.04, index=ACTIVOS, columns=ACTIVOS)
    O = omega(P, Sigma, v["u"].values, c=0.5)
    PSP = P.values @ Sigma.values @ P.values.T
    D = np.diag([2.0, 1.0])
    assert O == pytest.approx(D @ PSP @ D / 0.5)


def test_validar_rechaza_errores():
    ok = [fila(f"V{i}", "NVDA") for i in range(5)]
    validar(views(ok), ACTIVOS)
    with pytest.raises(ValueError, match="eta"):
        validar(views(ok[:4] + [fila("X", "NVDA", eta=3)]), ACTIVOS)
    with pytest.raises(ValueError, match="entre 5 y 8"):
        validar(views(ok[:3]), ACTIVOS)
    with pytest.raises(ValueError, match="TSLA"):
        validar(views(ok[:4] + [fila("X", "TSLA")]), ACTIVOS)
    with pytest.raises(ValueError, match="u"):
        validar(views(ok[:4] + [fila("X", "NVDA", u=0)]), ACTIVOS)


def test_views_reales_son_validas_y_sobre_la_seleccion():
    seleccion = pd.read_csv(DATA / "seleccion.csv")["ticker"].tolist()
    v = cargar_views(DATA / "views.csv")
    validar(v, seleccion)
    assert (v["tipo"] == "relativa").sum() >= len(v) - 1
    assert v["frase"].str.len().gt(30).all()
