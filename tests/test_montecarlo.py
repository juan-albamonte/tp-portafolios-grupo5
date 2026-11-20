import numpy as np
import pytest

from tp.config import Impuestos
from tp.montecarlo import (ResultadoMC, aplicar_shock, compuesto_esperado, costos_anuales, normales,
                           retiro_maximo_seguro, retorno_cartera, retornos_lognormales, simular,
                           tasas_impositivas)

SIN_COSTOS = lambda v, t: np.zeros_like(v)


def test_lognormal_respeta_media_y_covarianza():
    mu = np.array([0.05, 0.08])
    S = np.array([[0.01, 0.002], [0.002, 0.04]])
    Z = normales(200_000, 2, 2, np.random.default_rng(1))
    R = retornos_lognormales(Z, mu, S).reshape(-1, 2)
    assert R.mean(axis=0) == pytest.approx(mu, abs=2e-3)
    assert np.cov(R.T) == pytest.approx(S, abs=2e-3)


def test_impuestos_por_activo_como_en_la_etapa_4():
    imp = Impuestos()
    t_r, k = tasas_impositivas(np.array([True, False]), np.array([0.04, 0.02]), imp)
    R = np.array([[[0.05, 0.08]]])  # un camino, un año, renta fija y acción
    # Renta fija: 5% × 0,65. Acción: 8% − 2%·35% − 6%·15%.
    neto_rf = retorno_cartera(R, np.array([1.0, 0.0]), t_r, k, inflacion=0.0)
    neto_acc = retorno_cartera(R, np.array([0.0, 1.0]), t_r, k, inflacion=0.0)
    assert neto_rf.real[0, 0] == pytest.approx(0.05 * 0.65)
    assert neto_acc.real[0, 0] == pytest.approx(0.08 - 0.02 * 0.35 - 0.06 * 0.15)


def test_retorno_real_descuenta_inflacion_y_paga_impuesto_sobre_el_nominal():
    t_r, k = tasas_impositivas(np.array([True]), np.array([0.0]), Impuestos())
    r = retorno_cartera(np.array([[[0.0225]]]), np.array([1.0]), t_r, k, inflacion=0.0225)
    # Un bono que rinde justo la inflación pierde en términos reales lo que paga de impuesto.
    assert r.nominal[0, 0] == pytest.approx(0.0225 * 0.65)
    assert r.real[0, 0] == pytest.approx((1 + 0.0225 * 0.65) / 1.0225 - 1)
    assert r.real[0, 0] < 0


def test_ruina_deterministica():
    rp = np.zeros((2, 30))
    res = simular(100.0, 5.0, rp, rp, np.array([20.0, 21.0]), SIN_COSTOS, con_barandas=False)
    assert res.ruina.tolist() == [False, True]
    assert np.all(res.retiro[0, 20:] == 0)  # muerta no retira


def test_costos_reducen_el_valor():
    rp = np.zeros((1, 1))
    costos = lambda v, t: costos_anuales(v, t, anio_inicio=2026, valor_casa=lambda t: 50.0,
                                         tasa_bp=lambda a: 0.01, comision=lambda v: 0.01 * v)
    res = simular(100.0, 0.0, rp, rp, np.array([5.0]), costos, con_barandas=False)
    assert res.valor[0, 1] == pytest.approx(100 - 1 - 0.01 * 150)  # comisión + BP sobre cartera y depto


def test_barandas_recortan_despues_de_una_caida():
    rp = np.array([[-0.40, 0.0, 0.0]])
    res = simular(100.0, 4.0, rp, rp, np.array([3.0]), SIN_COSTOS, con_barandas=True, inflacion=0.0)
    assert res.retiro[0, 0] == pytest.approx(4.0)
    assert res.retiro[0, 1] == pytest.approx(3.6)  # 4 / 57,6 = 6,9% > 4%·1,2 → recorta 10%


def test_prob_recorte():
    res = ResultadoMC(valor=np.zeros((2, 4)), retiro=np.array([[10.0, 10.0, 7.0], [10.0, 9.0, 0.0]]),
                      anios_vida=np.array([3.0, 2.0]), ruina=np.array([False, False]))
    assert res.prob_recorte(0.8) == pytest.approx(0.5)


def test_retiro_maximo_seguro_biseccion():
    # Ruina = retiro / 1.000 (monótona): el máximo con ruina ≤ 5% es 50.
    assert retiro_maximo_seguro(lambda x: x / 1000, 0.05, hi=200.0, tol=0.01) == pytest.approx(50, abs=0.02)


def test_shock_solo_cambia_el_primer_anio():
    R = np.zeros((3, 4, 2))
    out = aplicar_shock(R, np.array([-0.3, 0.05]))
    assert out[:, 0, :].tolist() == [[-0.3, 0.05]] * 3
    assert np.all(out[:, 1:, :] == 0) and np.all(R == 0)


def test_mediana_a_60_anios_es_el_compuesto_esperado():
    """Control del checkpoint 5: sin retiro y sin costos, la mediana del valor a 60 años
    crece al retorno compuesto esperado de la cartera."""
    mu = np.array([0.04, 0.09])
    S = np.array([[0.004, 0.001], [0.001, 0.04]])
    w = np.array([0.5, 0.5])
    R = retornos_lognormales(normales(20_000, 60, 2, np.random.default_rng(7)), mu, S)
    rp = R @ w
    res = simular(1.0, 0.0, rp, rp, np.full(20_000, 60.0), SIN_COSTOS, con_barandas=False)
    g_sim = np.median(res.valor[:, 60]) ** (1 / 60) - 1
    assert g_sim == pytest.approx(compuesto_esperado(w @ mu, np.sqrt(w @ S @ w)), abs=1e-3)


def test_barandas_con_piso_pueden_arruinar():
    # Con −3% por año, las barandas recortan hasta estabilizar la tasa y nunca hay ruina;
    # con un piso de 3, el retiro deja de bajar y la cartera se agota antes de 40 años.
    rp = np.full((1, 40), -0.03)
    sin_piso = simular(100.0, 4.0, rp, rp, np.array([40.0]), SIN_COSTOS, con_barandas=True, inflacion=0.0)
    con_piso = simular(100.0, 4.0, rp, rp, np.array([40.0]), SIN_COSTOS, con_barandas=True, inflacion=0.0, piso=3.0)
    assert not sin_piso.ruina[0] and con_piso.ruina[0]
    pagados = con_piso.retiro[0][con_piso.valor[0, :-1] > 3.0]
    assert pagados.min() >= 3.0 - 1e-9


def test_anio_de_ruina():
    rp = np.zeros((2, 30))
    res = simular(100.0, 5.0, rp, rp, np.array([20.0, 25.0]), SIN_COSTOS, con_barandas=False)
    # 100 / 5 = 20 retiros completos (años 0-19); en el año 20 ya no alcanza.
    assert np.isnan(res.anio_ruina[0])
    assert res.anio_ruina[1] == 20


def test_gasto_de_fondo_se_descuenta_antes_de_impuestos():
    t_r, k = tasas_impositivas(np.array([True]), np.array([0.0]), Impuestos())
    r = retorno_cartera(np.array([[[0.05]]]), np.array([1.0]), t_r, k, inflacion=0.0, gasto=np.array([0.001]))
    assert r.nominal[0, 0] == pytest.approx((0.05 - 0.001) * 0.65)


def test_tasas_con_ganancia_realizada():
    from tp.impuestos import tasa_ganancia_realizada
    imp = Impuestos()
    t_r, k = tasas_impositivas(np.array([True, False]), np.array([0.04, 0.02]), imp,
                               mu=np.array([0.05, 0.09]), realizacion=0.12)
    t_g = tasa_ganancia_realizada(0.15, 0.12, 0.09 - 0.02)
    assert t_r[0] == 0.35 and t_r[1] == pytest.approx(t_g)
    assert k[1] == pytest.approx((0.35 - t_g) * 0.02)  # el dividendo sigue pagando 35%
