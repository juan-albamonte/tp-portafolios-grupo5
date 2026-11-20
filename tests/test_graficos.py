import numpy as np
import pandas as pd
import pytest

from tp.graficos import COLOR_CLASE, grafico_clases, pct_coma, percentiles_por_edad, rotacion


def test_percentiles_por_edad():
    # 3 caminos, 4 fechas: el valor de cada camino es su número de fila por la fecha.
    valor = np.array([[1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12]], dtype=float)
    p = percentiles_por_edad(valor, edad_inicial=35, q=(10, 50, 90))
    assert list(p.index) == [35, 36, 37, 38]
    assert list(p.columns) == ["p10", "p50", "p90"]
    assert p.loc[36, "p50"] == pytest.approx(4.0)
    assert (p["p10"] <= p["p50"]).all() and (p["p50"] <= p["p90"]).all()


def test_rotacion():
    w = pd.Series({"a": 0.5, "b": 0.5})
    assert rotacion(pd.Series({"a": 0.7, "b": 0.3}), w) == pytest.approx(0.2)


def test_pct_coma():
    assert pct_coma(0.0504, 1) == "5,0%" and pct_coma(0.1, 0) == "10%"


def test_una_paleta_fija_por_clase():
    assert len(set(COLOR_CLASE.values())) == 6


def test_grafico_clases_escribe_png_y_svg(tmp_path):
    clases = list(COLOR_CLASE)
    cartera = pd.Series([0.1, 0.2, 0.2, 0.05, 0.35, 0.1], index=clases)
    bench = pd.Series([0.05, 0.2, 0.1, 0.15, 0.4, 0.1], index=clases)
    rangos = {c: (0.0, 0.5) for c in clases}
    grafico_clases(cartera, bench, rangos, tmp_path)
    assert (tmp_path / "a_clases.png").stat().st_size > 10_000
    assert (tmp_path / "a_clases.svg").exists()


def test_grafico_invertir(tmp_path):
    from tp.graficos import grafico_invertir
    serie = lambda v: [v] * 66
    alt = {"a_quieta": {"mediana_por_edad": [max(0, 10 - i) * 1e6 for i in range(66)], "edad_central": 45.0, "ruina": 0.8},
           "b_letras": {"mediana_por_edad": serie(5e6), "edad_central": float("nan"), "ruina": 0.1},
           "d_cartera": {"mediana_por_edad": serie(12e6), "ruina": 0.02}}
    grafico_invertir(alt, tmp_path)
    assert (tmp_path / "k_invertir_vs_no.png").stat().st_size > 10_000
