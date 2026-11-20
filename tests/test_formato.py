import pytest

from tp.formato import pct


@pytest.mark.parametrize("x, d, esperado", [
    (0.0115, 1, "1,2%"),     # mitad hacia arriba, como Excel (Python daría 1,1%)
    (0.0177, 1, "1,8%"),
    (0.0504, 2, "5,04%"),
    (-0.302, 1, "−30,2%"),
    (0.1, 0, "10%"),
])
def test_pct_redondea_como_excel(x, d, esperado):
    assert pct(x, d) == esperado


def test_cero_negativo_sin_signo():
    from tp.formato import pct
    assert pct(-1e-17, 2) == "0,00%"
