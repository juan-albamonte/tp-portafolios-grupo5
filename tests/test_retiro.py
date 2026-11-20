import numpy as np
import pytest

from tp.retiro import ajustar_retiro


def caso(valor, ret_ant=0.05):
    return float(ajustar_retiro(np.array([25.0]), np.array([valor]), 0.025, np.array([ret_ant]), 0.025)[0])


def test_dentro_de_banda_no_cambia():
    assert caso(1000.0) == pytest.approx(25.0)


def test_recorte_si_la_tasa_pasa_la_baranda_de_arriba():
    assert caso(800.0) == pytest.approx(22.5)    # 3,125% > 3%


def test_suba_si_la_tasa_cae_debajo_de_la_baranda():
    assert caso(1300.0) == pytest.approx(27.5)   # 1,92% < 2%


def test_anio_negativo_con_tasa_arriba_de_la_inicial_no_ajusta_por_inflacion():
    # 25 / 900 = 2,78% > 2,5% inicial (pero < 3%, no recorta): se congela el ajuste.
    assert caso(900.0, ret_ant=-0.05) == pytest.approx(25.0 / 1.025)


def test_anio_negativo_con_tasa_debajo_de_la_inicial_si_ajusta():
    # Guyton y Klinger (2006): el congelamiento solo aplica si la tasa actual supera la inicial.
    assert caso(1100.0, ret_ant=-0.05) == pytest.approx(25.0)


def test_valor_cero_recorta():
    assert caso(0.0) == pytest.approx(22.5)


def test_piso_no_deja_recortar_debajo():
    r = ajustar_retiro(np.array([25.0]), np.array([800.0]), 0.025, np.array([0.05]), 0.025, piso=24.0)
    assert float(r[0]) == pytest.approx(24.0)  # recortaría a 22,5
