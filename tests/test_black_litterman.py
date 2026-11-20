import numpy as np
import pandas as pd
import pytest

from tp.black_litterman import calibrar_lambda, equilibrio, posterior_mercado
from tp.views import COLUMNAS, matriz_P, omega, valores_v

ACT = ["A", "B", "C", "D"]


def datos():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(500, 4)) @ np.array([[1, .3, .2, 0], [0, 1, .4, .1], [0, 0, 1, .5], [0, 0, 0, 1]]) * 0.01
    Sigma = pd.DataFrame(np.cov(X.T) * 252, index=ACT, columns=ACT)
    w_b = pd.Series([0.4, 0.3, 0.2, 0.1], index=ACT)
    v = pd.DataFrame([("V1", "relativa", "A", "B", "iguales", 1, 1.0, "f", "m"),
                      ("V2", "relativa", "C+D", "B", "iguales", -2, 1.0, "f", "m")], columns=COLUMNAS)
    return Sigma, w_b, v


def test_lambda_reproduce_el_exceso_del_benchmark():
    Sigma, w_b, _ = datos()
    lam = calibrar_lambda(Sigma.values, w_b.values, 0.0353)
    pi = equilibrio(Sigma.values, w_b.values, lam)
    assert w_b.values @ pi == pytest.approx(0.0353)


def _posterior(c):
    Sigma, w_b, v = datos()
    pi = pd.Series(equilibrio(Sigma.values, w_b.values, 3.0), index=ACT)
    P = matriz_P(v, ACT, {})
    q = valores_v(v, P, pi, Sigma, escala=0.25)
    O = omega(P, Sigma, v["u"].values, c=c)
    mu, Sp = posterior_mercado(pi.values, Sigma.values, P.values, q.values, O)
    return pi.values, Sigma.values, P.values, q.values, mu, Sp


def test_c_tiende_a_cero_reproduce_el_equilibrio():
    pi, Sigma, _, _, mu, Sp = _posterior(1e-10)
    assert mu == pytest.approx(pi, abs=1e-8)
    assert Sp == pytest.approx(Sigma, abs=1e-8)


def test_c_tiende_a_infinito_cumple_las_views_exactas():
    _, _, P, q, mu, _ = _posterior(1e10)
    assert P @ mu == pytest.approx(q, abs=1e-8)


def test_c_intermedio_queda_entre_equilibrio_y_views():
    pi, _, P, q, mu, _ = _posterior(1.0)
    d = P @ mu - P @ pi
    assert np.all(np.sign(d) == np.sign(q - P @ pi))
    assert np.all(np.abs(d) < np.abs(q - P @ pi))


def test_sigma_posterior_simetrica_y_menor():
    _, Sigma, _, _, _, Sp = _posterior(1.0)
    assert Sp == pytest.approx(Sp.T)
    assert np.all(np.linalg.eigvalsh(Sigma - Sp) > -1e-12)
