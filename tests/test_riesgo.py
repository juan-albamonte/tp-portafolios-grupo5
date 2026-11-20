import numpy as np
import pandas as pd
import pytest

from tp.riesgo import aporte_al_riesgo, regiones_en_acciones


def test_aportes_suman_la_vol():
    S = np.array([[0.04, 0.01], [0.01, 0.09]])
    w = np.array([0.6, 0.4])
    assert aporte_al_riesgo(w, S).sum() == pytest.approx(np.sqrt(w @ S @ w))


def test_activo_sin_peso_no_aporta():
    S = np.array([[0.04, 0.01], [0.01, 0.09]])
    assert aporte_al_riesgo(np.array([1.0, 0.0]), S)[1] == 0


def test_regiones_en_acciones():
    w = pd.Series({"ESGV": 0.20, "NVDA": 0.135, "ASML": 0.10, "IEF": 0.565})
    clase = {"ESGV": "acciones_eeuu", "NVDA": "acciones_eeuu", "ASML": "acciones_europa", "IEF": "tesoro"}
    r = regiones_en_acciones(w, clase)
    assert r["acciones_europa"] == pytest.approx(0.10 / 0.435)
    assert r["acciones_eeuu"] + r["acciones_europa"] == pytest.approx(1)
