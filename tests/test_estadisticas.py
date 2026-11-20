import numpy as np
import pandas as pd
import pytest

from tp.estadisticas import (correlacion_por_clase, estadisticas_guia, ledoit_wolf_cc, maxima_caida,
                             retorno_anio)


def muestras(T, n=6, rho=0.5, semilla=0):
    rng = np.random.default_rng(semilla)
    vols = np.linspace(0.02, 0.06, n)
    C = np.full((n, n), rho) + (1 - rho) * np.eye(n)
    S = C * np.outer(vols, vols)
    return rng.multivariate_normal(np.zeros(n), S, size=T)


def test_ledoit_wolf_estructura():
    X = muestras(120)
    Sigma, delta, rbar = ledoit_wolf_cc(X, anualizar=1)
    Y = X - X.mean(0)
    S = Y.T @ Y / len(Y)
    assert 0 <= delta <= 1
    np.testing.assert_allclose(np.diag(Sigma), np.diag(S))      # el objetivo conserva las varianzas
    np.testing.assert_allclose(Sigma, Sigma.T)
    assert np.all(np.linalg.eigvalsh(Sigma) > 0)
    sd = np.sqrt(np.diag(S))
    F = rbar * np.outer(sd, sd)
    np.fill_diagonal(F, np.diag(S))
    np.testing.assert_allclose(Sigma, delta * F + (1 - delta) * S)


def test_ledoit_wolf_rbar_es_la_correlacion_media():
    X = muestras(500)
    _, _, rbar = ledoit_wolf_cc(X)
    R = np.corrcoef(X.T)
    n = R.shape[0]
    assert rbar == pytest.approx((R.sum() - n) / (n * (n - 1)))


def muestras_en_bloques(T, semilla=1):
    """Dos bloques (correlación 0,8 adentro, 0,1 entre bloques): el objetivo constante está mal."""
    rng = np.random.default_rng(semilla)
    C = np.full((6, 6), 0.1)
    C[:3, :3] = C[3:, 3:] = 0.8
    np.fill_diagonal(C, 1.0)
    vols = np.linspace(0.02, 0.06, 6)
    return rng.multivariate_normal(np.zeros(6), C * np.outer(vols, vols), size=T)


def test_delta_baja_con_mas_datos():
    _, d_corto, _ = ledoit_wolf_cc(muestras_en_bloques(30))
    _, d_largo, _ = ledoit_wolf_cc(muestras_en_bloques(3000))
    assert d_largo < d_corto
    assert d_largo < 0.05


def test_objetivo_correcto_encoge_mucho():
    _, d, _ = ledoit_wolf_cc(muestras(120, rho=0.3, semilla=1))
    assert d > 0.5


def test_ledoit_wolf_anualiza():
    X = muestras(120)
    s1, d1, _ = ledoit_wolf_cc(X, anualizar=1)
    s12, d12, _ = ledoit_wolf_cc(X, anualizar=12)
    np.testing.assert_allclose(s12, 12 * s1)
    assert d1 == d12


def test_maxima_caida():
    r = pd.Series([0.10, -0.50, 0.20, 0.0])
    caida, pico, valle = maxima_caida(r)
    assert caida == pytest.approx(-0.5)
    assert (pico, valle) == (0, 1)


def test_retorno_anio():
    idx = pd.to_datetime(["2007-12-31", "2008-06-30", "2008-12-31", "2009-06-30"])
    r = pd.DataFrame({"A": [0.5, 0.10, -0.20, 0.3]}, index=idx)
    assert retorno_anio(r, 2008)["A"] == pytest.approx(1.1 * 0.8 - 1)


def test_estadisticas_guia():
    idx = pd.bdate_range("2020-01-01", periods=252)
    r = pd.DataFrame({"A": np.full(252, 0.001), "B": np.r_[np.full(126, 0.002), np.full(126, -0.001)]},
                     index=idx)
    t = estadisticas_guia(r, {"A": 0.5, "B": 0.5}, rf=0.0)
    assert list(t.index) == ["A", "B", "benchmark"]
    assert t.loc["A", "retorno_diario_medio"] == pytest.approx(0.001)
    assert t.loc["A", "retorno_anual"] == pytest.approx(1.001 ** 252 - 1)
    assert t.loc["A", "desvio_diario"] == pytest.approx(0.0, abs=1e-12)
    assert t.loc["benchmark", "retorno_diario_medio"] == pytest.approx(0.5 * 0.001 + 0.5 * 0.0005)
    assert t.loc["B", "maxima_caida"] == pytest.approx(0.999 ** 126 - 1)
    assert t.loc["B", "desvio_anual"] == pytest.approx(r["B"].std() * np.sqrt(252))


def test_correlacion_por_clase():
    R = pd.DataFrame([[1, .8, .1], [.8, 1, .3], [.1, .3, 1]], index=list("abc"), columns=list("abc"))
    m = correlacion_por_clase(R, {"a": "x", "b": "x", "c": "y"})
    assert m.loc["x", "x"] == pytest.approx(0.8)
    assert m.loc["x", "y"] == pytest.approx(0.2)
    assert m.loc["y", "y"] == pytest.approx(1.0)
