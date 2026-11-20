import numpy as np
import pytest

from tp.hrp import hrp
from tp.impuestos import retorno_neto_activo
from tp.config import Impuestos
from tp.optimizacion import (TOPES, mas_cercana, minima_varianza, optimizar, restricciones_activas,
                             violaciones)

CLASE = ["liquidez", "tesoro", "tips", "corporativos", "acciones_eeuu", "acciones_eeuu", "acciones_eeuu",
         "acciones_europa", "acciones_europa"]
TIPO = ["fondo"] * 5 + ["accion"] * 4
RANGOS = {"liquidez": (0.05, 0.15), "tesoro": (0.10, 0.30), "tips": (0.05, 0.20), "corporativos": (0.05, 0.20),
          "acciones_eeuu": (0.25, 0.45), "acciones_europa": (0.05, 0.20)}
VOLS = np.array([0.005, 0.07, 0.06, 0.08, 0.18, 0.35, 0.30, 0.25, 0.22])


def sigma():
    n = len(VOLS)
    R = np.full((n, n), 0.3)
    R[:4, 4:] = R[4:, :4] = 0.0
    np.fill_diagonal(R, 1.0)
    return R * np.outer(VOLS, VOLS)


def test_optimizar_respeta_vol_rangos_y_topes():
    mu = np.array([0.035, 0.05, 0.05, 0.055, 0.08, 0.15, 0.14, 0.12, 0.11])
    S = sigma()
    w = optimizar(mu, S, CLASE, TIPO, RANGOS, vol_max=0.09)
    assert np.sqrt(w @ S @ w) <= 0.09 + 1e-6
    assert violaciones(w, CLASE, TIPO, RANGOS) == []
    assert w[5:].max() <= TOPES["accion"] + 1e-8  # las acciones, que rinden más, quedan al tope
    activas = restricciones_activas(w, S, CLASE, TIPO, RANGOS, vol_max=0.09)
    assert any("tope" in a for a in activas)


def test_con_mu_igual_elige_menos_riesgo():
    S = sigma()
    mu = np.full(len(VOLS), 0.05)
    w_mv = minima_varianza(S, CLASE, TIPO, RANGOS)
    w = optimizar(mu, S, CLASE, TIPO, RANGOS, vol_max=0.20, desempate=1e-3)
    assert np.sqrt(w @ S @ w) == pytest.approx(np.sqrt(w_mv @ S @ w_mv), abs=2e-3)


def test_un_fondo_nunca_pasa_30():
    mu = np.array([0.01, 0.01, 0.01, 0.01, 0.30, 0.01, 0.01, 0.01, 0.01])
    w = optimizar(mu, sigma(), CLASE, TIPO, RANGOS, vol_max=0.30)
    assert w[4] <= TOPES["fondo"] + 1e-8


def test_hrp_dos_activos_es_varianza_inversa():
    S = np.diag([0.04, 0.01])
    w = hrp(S)
    assert w == pytest.approx([0.2, 0.8])


def test_hrp_suma_uno_y_no_negativa_y_ajuste_cumple():
    S = sigma()
    w = hrp(S)
    assert w.sum() == pytest.approx(1.0) and (w >= 0).all()
    w_aj = mas_cercana(w, CLASE, TIPO, RANGOS)
    assert violaciones(w_aj, CLASE, TIPO, RANGOS) == []


def test_retorno_neto_por_tipo():
    imp = Impuestos()
    # Renta fija: todo el retorno es interés (35%).
    neto, tasa = retorno_neto_activo(0.05, renta=0.04, renta_fija=True, imp=imp)
    assert tasa == pytest.approx(0.35) and neto == pytest.approx(0.05 * 0.65)
    # Acción: dividendo 2% al 35%, el resto (6%) ganancia de capital al 15%.
    neto, tasa = retorno_neto_activo(0.08, renta=0.02, renta_fija=False, imp=imp)
    assert neto == pytest.approx(0.08 - 0.02 * 0.35 - 0.06 * 0.15)
    assert tasa == pytest.approx((0.007 + 0.009) / 0.08)


def test_piso_por_activo():
    mu = np.array([0.035, 0.05, 0.05, 0.055, 0.06, 0.15, 0.14, 0.12, 0.11])
    w = optimizar(mu, sigma(), CLASE, TIPO, RANGOS, vol_max=0.09, pisos={4: 0.15})
    assert w[4] >= 0.15 - 1e-8
    assert violaciones(w, CLASE, TIPO, RANGOS) == []


def test_minimo_por_accion_deja_cero_o_mas_de_2():
    from tp.optimizacion import optimizar_con_minimo
    # Sin mínimo, la acción 8 queda en 0,4%: la regla la saca y reoptimiza.
    mu = np.array([0.035, 0.05, 0.05, 0.055, 0.06, 0.15, 0.14, 0.12, 0.05])
    w0 = optimizar(mu, sigma(), CLASE, TIPO, RANGOS, vol_max=0.09)
    assert 0 < w0[8] < 0.02
    w, fuera = optimizar_con_minimo(mu, sigma(), CLASE, TIPO, RANGOS, vol_max=0.09, minimo=0.02)
    acc = w[5:]
    assert fuera == [8] and w[8] == 0
    assert ((acc < 1e-8) | (acc >= 0.02 - 1e-8)).all()
    assert violaciones(w, CLASE, TIPO, RANGOS) == []
    assert np.sqrt(w @ sigma() @ w) <= 0.09 + 1e-6


def test_minimo_respeta_pisos_y_no_toca_fondos():
    from tp.optimizacion import optimizar_con_minimo
    mu = np.array([0.035, 0.05, 0.05, 0.055, 0.06, 0.15, 0.14, 0.12, 0.11])
    w, _ = optimizar_con_minimo(mu, sigma(), CLASE, TIPO, RANGOS, vol_max=0.09, minimo=0.02, pisos={4: 0.15})
    assert w[4] >= 0.15 - 1e-8


def test_excluidos_quedan_en_cero():
    w = optimizar(np.array([0.035, 0.05, 0.05, 0.055, 0.08, 0.15, 0.14, 0.12, 0.11]), sigma(), CLASE, TIPO,
                  RANGOS, vol_max=0.09, excluidos={5})
    assert w[5] == pytest.approx(0, abs=1e-10)


def test_reingreso_vuelve_a_entrar_si_mejora():
    from tp.optimizacion import con_minimo
    tipo = ["fondo", "accion", "accion"]
    # Resolver de juguete: sin restricciones, la acción 2 queda en 1% (la iteración la saca);
    # forzada al 2% el objetivo sube. Sacarla de entrada fue la elección codiciosa equivocada.
    def resolver(excluidos, forzados):
        if 2 in forzados:
            return np.array([0.93, 0.05, 0.02])
        if 2 in excluidos:
            return np.array([0.95, 0.05, 0.0])
        return np.array([0.94, 0.05, 0.01])
    valor = lambda w: {0.0: 1.0, 0.01: 1.5, 0.02: 2.0}[round(w[2], 2)]
    w, fuera = con_minimo(resolver, tipo, 0.02, valor=valor)
    assert w[2] == pytest.approx(0.02) and fuera == []


def test_reingreso_no_entra_si_empeora():
    from tp.optimizacion import con_minimo
    tipo = ["fondo", "accion", "accion"]
    def resolver(excluidos, forzados):
        if 2 in forzados:
            return np.array([0.93, 0.05, 0.02])
        if 2 in excluidos:
            return np.array([0.95, 0.05, 0.0])
        return np.array([0.94, 0.05, 0.01])
    valor = lambda w: -w[2]
    w, fuera = con_minimo(resolver, tipo, 0.02, valor=valor)
    assert w[2] == 0 and fuera == [2]
