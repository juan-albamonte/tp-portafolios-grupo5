"""Motor del Monte Carlo con los insumos reales (rápido: 2.000 caminos)."""
import numpy as np
import pandas as pd
import pytest

from tp.config import SALIDAS

pytestmark = pytest.mark.skipif(not (SALIDAS / "cartera.csv").exists(),
                                reason="falta outputs/cartera.csv: correr python -m tp.correr")


@pytest.fixture(scope="module")
def ins():
    from tp import etapa4
    return etapa4.insumos()


@pytest.fixture(scope="module")
def w(ins):
    return pd.read_csv(SALIDAS / "cartera.csv").set_index("ticker").loc[ins.activos, "peso"].values


def test_motor_con_gastos_de_fondos_rinde_menos(ins, w):
    from tp.etapa5 import Motor
    con = Motor(ins, n=2000).rp(w).nominal.mean()
    sin = Motor(ins, n=2000, gasto=np.zeros(len(ins.activos))).rp(w).nominal.mean()
    # 0,076% de gasto, descontado antes de impuestos (la renta fija paga 35%, las acciones 15%).
    assert 0.0004 < sin - con < 0.00076


def test_alternativas_ordenadas(ins, w):
    from tp.alternativas import alternativas, insumos_benchmark
    from tp.etapa5 import INF, SIM, Motor, casos
    caso = next(c for c in casos() if c.etiqueta == "A lujo")
    m = Motor(ins, n=2000)
    mb = Motor(insumos_benchmark(ins), n=2000)
    alt = alternativas(m, mb, caso, w, SIM.edad, INF)
    assert alt["a_quieta"]["ruina"] > alt["b_letras"]["ruina"] > alt["d_cartera"]["ruina"]
    assert 35 < alt["a_quieta"]["edad_central"] < 100
    assert alt["d_cartera"]["patrimonio"]["real"][60] > alt["b_letras"]["patrimonio"]["real"][60]


def test_mas_impuestos_mas_ruina(ins, w):
    from tp.alternativas import ALICUOTAS_ALTAS, bp_fijo
    from tp.etapa5 import Motor, casos
    caso = next(c for c in casos() if c.etiqueta == "A lujo")
    base = Motor(ins, n=2000)
    alta = Motor(ins, n=2000, imp=ALICUOTAS_ALTAS)
    r0 = base.correr(caso, base.rp(w), True).prob_ruina
    assert alta.correr(caso, alta.rp(w), True).prob_ruina >= r0
    assert base.correr(caso, base.rp(w), True, bp=bp_fijo).prob_ruina >= r0


def test_misma_vara(ins, w):
    from tp.alternativas import misma_vara
    r = misma_vara(ins, w, rf=0.035)
    assert r["cartera"]["vol"] == pytest.approx(0.09, abs=0.002)  # la Σ conjunta casi no cambia la de la cartera
    assert r["benchmark_indices"]["vol"] < r["neutra_14"]["vol"]  # la neutra lleva Europa en tres acciones
    assert r["neutra_europa_vgk_eeuu_spy"]["vol"] < r["neutra_europa_vgk"]["vol"] < r["neutra_14"]["vol"]


def test_caida_2008_cartera_menor_que_50_50(ins, w):
    from tp.alternativas import caida_2008
    r = caida_2008(ins, w)
    assert r["benchmark"] < r["cartera_por_clase"] < 0
    assert r["fuente"]["SCHP"] == "clase" and r["fuente"]["NVDA"] == "propio"


def test_caidas_2008_consistentes(ins, w):
    from tp.alternativas import caida_2008, caidas_2008
    c = caidas_2008(ins, w)
    assert c["anio_2008_fijos"]["cartera"] == pytest.approx(caida_2008(ins, w)["cartera"], abs=1e-6)
    for k, v in c.items():
        assert v["cartera"] > v["benchmark"], k  # la cartera cae menos con cualquier métrica
