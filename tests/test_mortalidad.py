import numpy as np
import pytest

from tp.mortalidad import esperanza_de_vida, muestrear_anios_de_vida, supervivencia


def test_supervivencia_en_cero_es_uno():
    assert supervivencia(35, 0, 93, 9) == pytest.approx(1.0)


def test_supervivencia_decreciente():
    s = supervivencia(35, np.arange(0, 70), 93, 9)
    assert np.all(np.diff(s) < 0)


def test_muestreo_respeta_supervivencia():
    t = muestrear_anios_de_vida(35, 93, 9, 200_000, np.random.default_rng(0))
    for h in (40, 50, 60):
        assert (t > h).mean() == pytest.approx(supervivencia(35, h, 93, 9), abs=0.005)


def test_esperanza_razonable():
    assert 48 < esperanza_de_vida(35, 93, 9) < 56
