import pandas as pd
import pytest

from tp.config import (BENCHMARK, CLASES, ESCENARIOS, IMPLEMENTACION, PROXIES, RANGOS,
                       cargar_presupuesto, gasto_mensual)


def test_costo_de_compra():
    a, b = ESCENARIOS
    assert a.costo_compra == pytest.approx(75_000)
    assert a.capital_inicial == pytest.approx(13_925_000)
    assert b.costo_compra == 0 and b.capital_inicial == 15_000_000


def test_todas_las_clases_definidas():
    for d in (PROXIES, IMPLEMENTACION, RANGOS, BENCHMARK):
        assert set(d) == set(CLASES)


def test_rangos_factibles():
    assert sum(a for a, _ in RANGOS.values()) <= 1 <= sum(b for _, b in RANGOS.values())


def test_benchmark_suma_uno_y_cae_dentro_de_rangos():
    assert abs(sum(BENCHMARK.values()) - 1) < 1e-12
    for clase, w in BENCHMARK.items():
        lo, hi = RANGOS[clase]
        assert lo <= w <= hi


def test_gasto_por_escenario_y_nivel():
    df = pd.DataFrame({"rubro": ["a", "b", "c"] * 2, "usd_mes": [100.0, 50.0, 30.0, 60.0, 50.0, 30.0],
                       "escenario": ["ambos", "compra", "alquila"] * 2,
                       "nivel": ["lujo"] * 3 + ["base"] * 3, "fuente": ["x"] * 6})
    assert gasto_mensual(df, "compra") == 150
    assert gasto_mensual(df, "alquila", "lujo") == 130
    assert gasto_mensual(df, "compra", "base") == 110


def test_presupuesto_real():
    df = cargar_presupuesto()
    assert set(df["escenario"]) <= {"ambos", "compra", "alquila"}
    assert set(df["nivel"]) == {"base", "lujo", "alto"}
    assert (df["usd_mes"] > 0).all()
    esperado = {("compra", "lujo"): 21_900, ("alquila", "lujo"): 25_300,
                ("compra", "base"): 15_050, ("alquila", "base"): 18_450,
                ("compra", "alto"): 31_750, ("alquila", "alto"): 37_650}
    for (viv, nivel), monto in esperado.items():
        assert gasto_mensual(df, viv, nivel) == monto, (viv, nivel)


def test_cada_rubro_en_los_tres_niveles():
    df = cargar_presupuesto()
    conteo = df.groupby(["rubro", "escenario"])["nivel"].nunique()
    assert (conteo == 3).all()


def test_gastos_de_fondos_ponderados_dan_0076():
    from tp.config import gastos_fondos
    g = gastos_fondos()
    w = {"BIL": 0.10, "IEF": 0.215, "SCHP": 0.20, "VCEB": 0.05, "ESGV": 0.20}
    assert sum(w[t] * g[t] for t in w) == pytest.approx(0.00076, abs=0.00002)
    assert g["NVDA"] == 0.0  # acciones: sin gasto de fondo


def test_benchmark_pasivo_tiene_una_fila_por_clase():
    from tp.config import benchmark_pasivo
    b = benchmark_pasivo()
    assert list(b["clase"]) == CLASES
    assert set(b.columns) >= {"ticker", "clase", "renta", "gasto", "fuente"}
    assert list(b["ticker"]) == [PROXIES[c] for c in CLASES]
