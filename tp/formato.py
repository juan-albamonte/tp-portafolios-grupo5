"""Formato de números para todos los entregables: coma decimal y redondeo como Excel.

Python redondea "mitad al par" sobre la representación binaria (0,0115 → 1,1%) y Excel
"mitad hacia arriba" (1,2%). Para que gráficos, textos y planilla muestren lo mismo, todos
los porcentajes pasan por esta función, que redondea el decimal tal como se escribe.
"""
from decimal import ROUND_HALF_UP, Decimal


def redondear(x, d: int) -> Decimal:
    """x (float o Decimal) redondeado a d decimales, mitad hacia arriba."""
    return Decimal(repr(float(x)) if not isinstance(x, Decimal) else x).quantize(Decimal(1).scaleb(-d),
                                                                                  rounding=ROUND_HALF_UP)


def pct(x: float, d: int = 1) -> str:
    v = redondear(Decimal(repr(float(x))) * 100, d)
    if v == 0:
        v = v.copy_abs()  # sin "−0,0%"
    return f"{v:.{d}f}%".replace(".", ",").replace("-", "−")
