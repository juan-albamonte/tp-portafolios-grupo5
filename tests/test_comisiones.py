import numpy as np
import pytest

from tp.comisiones import comision_anual


@pytest.mark.parametrize("valor, esperado", [
    (14_000_000, 84_000),   # 20.000 + 48.000 + 16.000 = 0,60% efectivo
    (1_000_000, 10_000),
    (2_000_000, 20_000),
    (0, 0),
    (-5, 0),
])
def test_comision_por_tramos(valor, esperado):
    assert float(comision_anual(valor)) == pytest.approx(esperado)


def test_vectorizada():
    out = comision_anual(np.array([1_000_000.0, 14_000_000.0]))
    assert out == pytest.approx([10_000, 84_000])
