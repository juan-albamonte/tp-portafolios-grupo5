import math

import pandas as pd
import pytest

from tp.screening import METRICAS, fundamentales_de, percentil_en_sector, preliminar, ranking_por_sector


def info(**k):
    base = {"marketCap": 1000.0, "forwardPE": 20.0, "operatingMargins": 0.30, "returnOnEquity": 0.25,
            "totalDebt": 300.0, "totalCash": 100.0, "ebitda": 400.0, "dividendYield": 1.5,
            "financialCurrency": "USD", "currency": "USD"}
    return base | k


def test_fundamentales_de_una_empresa():
    f = fundamentales_de(info(), recompras=-20.0, crecimiento=0.12, fx=1.0)
    assert f["pe_forward"] == 20.0
    assert f["crecimiento_ganancias"] == 0.12
    assert f["margen_operativo"] == 0.30
    assert f["deuda_neta_ebitda"] == pytest.approx((300 - 100) / 400)
    assert f["roe"] == 0.25
    # Yahoo da el dividendo en %: 1,5 → 0,015. Recompras: 20 sobre 1000 de capitalización.
    assert f["retorno_accionista"] == pytest.approx(0.015 + 0.02)


def test_recompras_en_otra_moneda_se_pasan_a_dolares():
    f = fundamentales_de(info(financialCurrency="EUR", dividendYield=0.0), recompras=-10.0, crecimiento=0.1, fx=1.1)
    assert f["retorno_accionista"] == pytest.approx(11.0 / 1000.0)


def test_bancos_sin_ebitda_quedan_sin_deuda_neta_ebitda():
    f = fundamentales_de(info(ebitda=None), recompras=0.0, crecimiento=0.05, fx=1.0)
    assert math.isnan(f["deuda_neta_ebitda"])


def test_percentil_en_sector_usa_el_rango_medio():
    s = pd.Series([1.0, 2.0, 3.0, 4.0])
    assert list(percentil_en_sector(s, mayor_es_mejor=True)) == [0.125, 0.375, 0.625, 0.875]
    assert list(percentil_en_sector(s, mayor_es_mejor=False)) == [0.875, 0.625, 0.375, 0.125]
    assert percentil_en_sector(pd.Series([7.0]), mayor_es_mejor=True).iloc[0] == 0.5


def tabla():
    filas = [
        # ticker, sector, pe, crec, margen, deuda/ebitda, roe, retorno, esg, europa
        ("A", "Salud", 12, 0.15, 0.35, 0.5, 0.30, 0.05, 60, True),
        ("B", "Salud", 30, 0.05, 0.15, 2.5, 0.10, 0.01, 30, False),
        ("C", "Tecnología", 25, 0.20, 0.40, -0.5, 0.40, 0.03, 55, True),
        ("D", "Tecnología", 40, 0.10, 0.20, 1.0, 0.15, 0.01, 40, False),
        ("E", "Servicios públicos", 18, 0.08, 0.30, 5.0, 0.11, 0.03, 38, False),
    ]
    cols = ["ticker", "sector"] + list(METRICAS) + ["europa"]
    return pd.DataFrame(filas, columns=cols)


def test_ranking_es_dentro_de_cada_sector():
    r = ranking_por_sector(tabla())
    assert r.loc[r.ticker == "A", "puesto_en_sector"].item() == 1
    assert r.loc[r.ticker == "C", "puesto_en_sector"].item() == 1
    assert r.loc[r.ticker == "E", "puesto_en_sector"].item() == 1
    # A le gana a B en todas las métricas: percentil 0,75 en cada una.
    assert r.loc[r.ticker == "A", "puntaje"].item() == pytest.approx(0.75)
    # Un sector de una sola empresa queda neutro.
    assert r.loc[r.ticker == "E", "puntaje"].item() == pytest.approx(0.5)


def test_ranking_ignora_metricas_faltantes():
    t = tabla()
    t.loc[t.ticker == "B", "deuda_neta_ebitda"] = float("nan")
    r = ranking_por_sector(t)
    # B promedia sus 6 métricas con dato (pierde en todas); A queda sola en la que falta: neutra.
    assert r.loc[r.ticker == "B", "puntaje"].item() == pytest.approx(0.25)
    assert r.loc[r.ticker == "A", "puntaje"].item() == pytest.approx((6 * 0.75 + 0.5) / 7)


def test_preliminar_marca_el_motivo():
    r = ranking_por_sector(tabla())
    p = preliminar(r, favorecidos={"Salud", "Tecnología"}, por_sector=1, umbral_calidad=0.6, min_europa=0)
    assert set(p.ticker) == {"A", "C"}
    assert set(p.motivo) == {"sector favorecido"}
    p2 = preliminar(r, favorecidos={"Salud"}, por_sector=1, umbral_calidad=0.6, min_europa=0)
    assert set(p2.ticker) == {"A", "C"}
    assert p2.loc[p2.ticker == "C", "motivo"].item() == "calidad propia"


def test_preliminar_en_sector_favorecido_la_segunda_entra_solo_si_esta_en_la_mitad_de_arriba():
    r = ranking_por_sector(tabla())
    p = preliminar(r, favorecidos={"Salud"}, por_sector=2, umbral_calidad=0.99, min_europa=0)
    assert set(p.ticker) == {"A"}  # B pierde en todo (puntaje 0,25)


def test_preliminar_completa_europeas():
    r = ranking_por_sector(tabla())
    p = preliminar(r, favorecidos={"Tecnología"}, por_sector=1, umbral_calidad=0.99, min_europa=2)
    assert set(p.ticker) == {"C", "A"}
    assert p.loc[p.ticker == "A", "motivo"].item() == "completa Europa"
