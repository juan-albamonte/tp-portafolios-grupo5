import pandas as pd
import pytest

from tp.monitoreo import backtest

IDX = pd.bdate_range("2020-01-01", periods=60)
W = pd.Series({"A": 0.5, "B": 0.5})
CLASE = {"A": "x", "B": "y"}


def test_sin_movimiento_no_rebalancea():
    r = pd.DataFrame(0.0, index=IDX, columns=["A", "B"])
    out = backtest(r, W, CLASE, banda=0.03)
    assert out.eventos == [] and out.revisiones == 3


def test_dispara_cuando_una_clase_se_aparta_mas_de_la_banda():
    r = pd.DataFrame(0.0, index=IDX, columns=["A", "B"])
    r.iloc[5, 0] = 0.20  # A sube 20%: pesa 0,6 / 1,1 = 54,5%, 4,5 puntos arriba del objetivo
    out = backtest(r, W, CLASE, banda=0.03)
    assert len(out.eventos) == 1
    ev = out.eventos[0]
    assert ev["fecha"] == IDX[IDX.month == 1][-1]  # se ve en la revisión de fin de mes
    assert ev["clase_mas_desviada"] == "x" and ev["desvio"] == pytest.approx(0.0455, abs=1e-3)
    assert ev["vende"]["A"] == pytest.approx(0.0455, abs=1e-3)
    assert ev["compra"]["B"] == pytest.approx(0.0455, abs=1e-3)
    assert out.desvio_max["x"] == pytest.approx(0.0455, abs=1e-3)


def test_movimiento_dentro_de_la_banda_no_dispara():
    r = pd.DataFrame(0.0, index=IDX, columns=["A", "B"])
    r.iloc[5, 0] = 0.10  # 0,55 / 1,05 = 52,4%: 2,4 puntos
    assert backtest(r, W, CLASE, banda=0.03).eventos == []


def test_tope_por_accion():
    r = pd.DataFrame(0.0, index=IDX, columns=["A", "B", "C"])
    r.iloc[5, 2] = 0.30  # C pasa de 4,5% a ~5,8%
    w = pd.Series({"A": 0.5, "B": 0.455, "C": 0.045})
    out = backtest(r, w, {"A": "x", "B": "y", "C": "x"}, banda=0.10, tipo={"C": "accion"}, tope_accion=0.05)
    assert len(out.eventos) == 1 and "tope" in out.eventos[0]["motivo"]


def test_rendimiento_posterior_de_una_canasta():
    from tp.monitoreo import rendimiento_posterior
    idx = pd.bdate_range("2020-01-01", periods=300)
    r = pd.DataFrame({"A": 0.001, "B": 0.0}, index=idx)
    g = rendimiento_posterior(r, {"A": 3.0, "B": 1.0}, idx[0], meses=12)
    dias = ((idx > idx[0]) & (idx <= idx[0] + pd.DateOffset(months=12))).sum()
    assert g == pytest.approx(0.75 * (1.001 ** dias - 1))


def test_realizacion_por_rebalanceo():
    from tp.monitoreo import Monitoreo, realizacion_acciones
    m = Monitoreo(eventos=[{"vende": {"A": 0.10}}, {"vende": {"A": 0.05, "B": 0.02}}], anios=2.0)
    w = pd.Series({"A": 0.40, "B": 0.60})
    # A: vende 0,10 de 0,50 y 0,05 de 0,45 → (0,2 + 0,111) / 2 años. B no es acción.
    assert realizacion_acciones(m, w, {"A": "acciones_eeuu", "B": "tesoro"}) == pytest.approx((0.2 + 0.05 / 0.45) / 2)


def test_valores_y_maxima_caida():
    from tp.monitoreo import maxima_caida
    r = pd.DataFrame({"A": [0.10, -0.50, 0.20], "B": [0.0, 0.0, 0.0]}, index=IDX[:3])
    out = backtest(r, pd.Series({"A": 1.0, "B": 0.0}), CLASE, banda=1.0)
    assert out.valores.tolist() == pytest.approx([1.1, 0.55, 0.66])
    assert maxima_caida(out.valores) == pytest.approx(-0.5)
