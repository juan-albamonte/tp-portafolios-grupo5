import numpy as np
import pandas as pd

from tp.correr import ventana_comun


def test_ventana_comun_diaria_deja_afuera_los_incompletos():
    idx = pd.bdate_range("2015-01-01", "2026-10-30")
    r = pd.DataFrame({"A": 0.001, "B": 0.002}, index=idx)
    r.loc[:"2020-01-01", "B"] = np.nan
    v = ventana_comun(r, anios=10)
    assert list(v.columns) == ["A"]
    assert v.index[0] > pd.Timestamp("2016-10-28") and v.index[-1] == pd.Timestamp("2026-10-30")


def test_ventana_comun_mensual():
    idx = pd.date_range("2010-01-31", periods=200, freq="ME")
    r = pd.DataFrame({"A": 0.01}, index=idx)
    assert len(ventana_comun(r, anios=10)) == 120


def test_resumen_json_estricto():
    from tp.correr import _limpio
    out = _limpio({"a": float("nan"), "b": np.float64(0.1234567891), 3: [np.int64(2)]})
    assert out == {"a": None, "b": 0.123457, "3": [2]}
