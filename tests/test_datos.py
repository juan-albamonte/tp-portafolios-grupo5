import numpy as np
import pandas as pd
import pytest

from tp.datos import a_mensual, cargar_o_bajar, control_relleno, rellenar_hacia_atras, retornos


def precios_sinteticos(n=300, semilla=0, inicio="2020-01-01"):
    rng = np.random.default_rng(semilla)
    idx = pd.bdate_range(inicio, periods=n)
    base = 100 * np.cumprod(1 + rng.normal(0.0003, 0.01, n))
    fondo = base * np.cumprod(1 + rng.normal(0, 0.001, n))
    df = pd.DataFrame({"IDX": base, "FONDO": fondo}, index=idx)
    df.iloc[:100, 1] = np.nan  # el fondo arranca después
    return df


def test_cache_no_vuelve_a_bajar(tmp_path):
    llamadas = []

    def bajador(tickers, inicio, fin):
        llamadas.append(list(tickers))
        return precios_sinteticos()[list(tickers)]

    archivo = tmp_path / "p.csv"
    a = cargar_o_bajar(archivo, ["IDX", "FONDO"], "2020-01-01", "2021-01-01", bajador)
    b = cargar_o_bajar(archivo, ["IDX"], "2020-01-01", "2021-01-01", bajador)
    assert len(llamadas) == 1
    pd.testing.assert_series_equal(a["IDX"], b["IDX"], check_freq=False)


def test_cache_baja_si_falta_un_ticker(tmp_path):
    llamadas = []

    def bajador(tickers, inicio, fin):
        llamadas.append(list(tickers))
        return precios_sinteticos()[list(tickers)]

    archivo = tmp_path / "p.csv"
    cargar_o_bajar(archivo, ["IDX"], "2020-01-01", "2021-01-01", bajador)
    cargar_o_bajar(archivo, ["IDX", "FONDO"], "2020-01-01", "2021-01-01", bajador)
    assert len(llamadas) == 2


def test_relleno_usa_los_retornos_del_indice_antes_del_lanzamiento():
    p = precios_sinteticos()
    r = rellenar_hacia_atras(p["FONDO"], p["IDX"])
    assert r.notna().all()
    # Después del lanzamiento, el fondo no cambia.
    pd.testing.assert_series_equal(r.iloc[100:], p["FONDO"].iloc[100:])
    # Antes, sus retornos son los del índice.
    ri = p["IDX"].pct_change().iloc[1:100]
    rf = r.pct_change().iloc[1:100]
    np.testing.assert_allclose(rf.values, ri.values)


def test_control_del_relleno():
    p = precios_sinteticos()
    c = control_relleno(p["FONDO"], p["IDX"])
    assert c["correlacion_diaria"] > 0.95
    assert c["desde"] == p.index[100]
    assert c["dias"] == 199  # 200 precios en común
    assert c["dif_vol_anual"] == pytest.approx(c["vol_fondo"] - c["vol_indice"])


def test_mensual_y_retornos():
    idx = pd.to_datetime(["2020-01-15", "2020-01-31", "2020-02-14", "2020-02-28", "2020-03-31"])
    p = pd.DataFrame({"A": [1.0, 2.0, 2.5, 3.0, 1.5]}, index=idx)
    m = a_mensual(p)
    assert list(m["A"]) == [2.0, 3.0, 1.5]
    r = retornos(m)
    np.testing.assert_allclose(r["A"].values, [0.5, -0.5])
