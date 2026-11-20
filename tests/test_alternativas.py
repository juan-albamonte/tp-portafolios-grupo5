import numpy as np
import pytest

from tp.alternativas import edad_central, patrimonio, rp_quieta

SIN_COSTOS = lambda v, t: np.zeros_like(v)


def test_plata_quieta_pierde_la_inflacion():
    rp = rp_quieta(3, 5, 0.0225)
    assert np.allclose(rp.nominal, 0) and np.allclose(rp.real, 1 / 1.0225 - 1)


def test_edad_central_deterministica():
    # 100 de capital, retira 10 por año, rinde 0: hace 10 retiros (35 a 44) y a los 45 no alcanza.
    assert edad_central(100.0, 10.0, 0.0, 0.0, 0.0, SIN_COSTOS, T=30, edad0=35) == 45


def test_edad_central_sin_ruina_es_nan():
    assert np.isnan(edad_central(100.0, 1.0, 0.0, 0.05, 0.05, SIN_COSTOS, T=30, edad0=35))


def test_patrimonio_en_reales_y_nominales():
    valor = np.ones((4, 61))
    p = patrimonio(valor, edades=(60,), edad0=35, inflacion=0.0225)
    assert p["real"][60] == 1.0
    assert p["nominal"][60] == pytest.approx(1.0225 ** 25)


def test_retorno_anio_activo():
    import pandas as pd
    from tp.alternativas import retorno_anio_activo
    idx = pd.bdate_range("2007-12-01", "2008-12-31")
    s = pd.Series(100.0, index=idx)
    s.loc["2008-01-01":] = 80.0
    assert retorno_anio_activo(s, 2008) == pytest.approx(-0.2)
    assert retorno_anio_activo(s.loc["2008-03-01":], 2008) is None  # no cotizó todo el año
