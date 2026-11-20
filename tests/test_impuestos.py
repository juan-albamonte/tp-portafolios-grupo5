import pytest

from tp.config import Impuestos
from tp.impuestos import drag_ganancias_capital, drag_por_clase, tasa_bp, tasa_efectiva


@pytest.mark.parametrize("ret, ar, esperado", [(0.30, 0.35, 0.35), (0.30, 0.15, 0.30), (0.0, 0.35, 0.35)])
def test_tasa_efectiva_toma_la_mayor(ret, ar, esperado):
    assert tasa_efectiva(ret, ar) == esperado


def test_drag_por_clase():
    d = drag_por_clase({"acciones_eeuu": 0.012, "tesoro": 0.04}, Impuestos())
    assert d["acciones_eeuu"] == pytest.approx(0.012 * 0.35)
    assert d["tesoro"] == pytest.approx(0.04 * 0.35)


def test_drag_ganancias_capital_con_ventas_para_el_retiro():
    # vende 0,5% para completar el retiro + 5% de rebalanceo
    assert drag_ganancias_capital(0.025, 0.02, 0.05, 0.30, 0.15) == pytest.approx(0.055 * 0.30 * 0.15)


def test_drag_ganancias_capital_retiro_cubierto_por_renta():
    assert drag_ganancias_capital(0.02, 0.03, 0.05, 0.30, 0.15) == pytest.approx(0.05 * 0.30 * 0.15)


@pytest.mark.parametrize("anio, tasa", [(2025, 0.01), (2026, 0.0075), (2027, 0.0025), (2040, 0.0025)])
def test_tasa_bp(anio, tasa):
    assert tasa_bp(anio) == tasa


def test_ganancia_realizada_cada_anio_es_la_tasa_plena():
    from tp.impuestos import tasa_ganancia_realizada
    assert tasa_ganancia_realizada(0.15, 1.0, 0.07) == pytest.approx(0.15)


def test_ganancia_diferida_paga_menos():
    from tp.impuestos import tasa_ganancia_realizada
    t = tasa_ganancia_realizada(0.15, 0.10, 0.08)
    assert t == pytest.approx(0.15 * 0.10 * 1.08 / 0.18)
    assert tasa_ganancia_realizada(0.15, 0.0, 0.08) == 0.0


def test_ganancia_diferida_es_el_estado_estacionario():
    """Simulación explícita: cada año sube g, se vende la fracción f y se paga t sobre la ganancia realizada."""
    from tp.impuestos import tasa_ganancia_realizada
    t, f, g = 0.15, 0.12, 0.07
    valor, base, impuesto = 1.0, 1.0, 0.0
    for _ in range(400):
        valor *= 1 + g
        ganancia = f * (valor - base)
        base = base * (1 - f) + f * valor  # se vende f y se recompra al precio de hoy
        impuesto = t * ganancia / (valor / (1 + g))  # impuesto del año sobre el valor de inicio
    assert impuesto == pytest.approx(tasa_ganancia_realizada(t, f, g) * g, rel=1e-3)
