import pytest

from tp.config import BENCHMARK, CLASES, RETORNO_LARGO_PLAZO, Mercado
from tp.escenario import a_aritmetico, a_real, exceso_benchmark


def test_retornos_definidos_para_todas_las_clases():
    assert set(RETORNO_LARGO_PLAZO) == set(CLASES)
    assert all(0 < r < 0.15 for r in RETORNO_LARGO_PLAZO.values())


def test_a_real():
    assert a_real(0.0475, 0.0225) == pytest.approx(1.0475 / 1.0225 - 1)


def test_a_aritmetico_lognormal():
    # Si log(1+R) ~ N(m, s²): 1+g = e^m y 1+E[R] = e^(m + s²/2).
    g, vol = 0.07, 0.20
    a = a_aritmetico(g, vol)
    s2 = __import__("math").log(1 + vol ** 2 / (1 + a) ** 2)
    assert (1 + a) == pytest.approx((1 + g) * __import__("math").exp(s2 / 2), rel=1e-9)
    assert a_aritmetico(0.03, 0.0) == pytest.approx(0.03)


def test_exceso_benchmark():
    ret = {c: 0.05 for c in CLASES} | {"liquidez": 0.03}
    vols = {c: 0.0 for c in CLASES}
    assert exceso_benchmark(ret, vols, BENCHMARK, tasa_corta=0.03) == pytest.approx(0.95 * 0.02)


def test_exceso_en_config_es_coherente():
    from tp.escenario import VOL_CLASES
    calculado = exceso_benchmark(RETORNO_LARGO_PLAZO, VOL_CLASES, BENCHMARK,
                                 tasa_corta=RETORNO_LARGO_PLAZO["liquidez"])
    assert Mercado().exceso_esperado_benchmark == pytest.approx(round(calculado, 4))
