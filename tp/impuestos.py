"""Impuestos de una residente fiscal argentina con ETFs de EE.UU.

Detalle donde cambia decisiones (costo por clase de activo); el resto, simplificado.
"""
from tp.config import Impuestos


def tasa_efectiva(retencion_eeuu: float, tasa_ar: float) -> float:
    """Tasa efectiva sobre una renta de EE.UU.: max(retención de EE.UU., tasa argentina).

    Argentina cobra su tasa y descuenta como crédito lo que se retuvo afuera, con
    tope en el impuesto argentino sobre esa renta. Si EE.UU. retiene menos, la
    diferencia se paga acá; si retiene más, el excedente no se recupera.

    Por eso, con 35% en Argentina, los intereses pagan 35% en cualquier caso: tanto
    si EE.UU. no retiene (portfolio interest exemption de los bonos del Tesoro)
    como si retiene 30% (distribuciones de ETFs de bonos no designadas como QII).
    El resultado no depende de cuál de las dos aplique.
    """
    return max(retencion_eeuu, tasa_ar)


def drag_por_clase(rendimientos_renta: dict[str, float], imp: Impuestos) -> dict[str, float]:
    """Costo impositivo anual por clase: renta que distribuye × tasa efectiva.

    Acciones: dividendos. Renta fija: intereses.
    """
    t_div = tasa_efectiva(imp.retencion_eeuu_dividendos, imp.tasa_ar_dividendos)
    t_int = tasa_efectiva(imp.retencion_eeuu_intereses, imp.tasa_ar_intereses)
    return {c: y * (t_div if c.startswith("acciones") else t_int) for c, y in rendimientos_renta.items()}


def drag_ganancias_capital(tasa_retiro: float, renta_cartera: float, rebalanceo: float,
                           fraccion_ganancia: float, tasa: float) -> float:
    """Impuesto anual por ventas, como fracción de la cartera (simplificado).

    Vende lo que falta para el retiro después de cobrar la renta, más el rebalanceo.
    Sobre lo vendido, una fracción es ganancia y paga la tasa.
    """
    ventas = max(0.0, tasa_retiro - renta_cartera) + rebalanceo
    return ventas * fraccion_ganancia * tasa


def tasa_bp(anio: int) -> float:
    """Alícuota de Bienes Personales sobre la cartera (Ley 27.743, tramo máximo).

    La cartera supera con creces el último tramo, así que la tasa efectiva es casi la máxima.
    """
    if anio <= 2025:
        return 0.01
    if anio == 2026:
        return 0.0075
    return 0.0025


def retorno_neto_activo(total: float, renta: float, renta_fija: bool, imp: Impuestos) -> tuple[float, float]:
    """Retorno esperado después de impuestos y tasa efectiva de un activo.

    Renta fija (incluye TIPS): todo el retorno se cobra como interés y paga la tasa de
    intereses (35%). En los TIPS, el ajuste por inflación del capital también es interés.
    Acciones: el dividendo paga la tasa de dividendos (35%, max(retención 30%, Argentina
    35%)); el resto del retorno es ganancia de capital al 15%. Supuesto conservador: la
    ganancia tributa a medida que se genera (no se modela el diferimiento hasta la venta).
    """
    t_int = tasa_efectiva(imp.retencion_eeuu_intereses, imp.tasa_ar_intereses)
    t_div = tasa_efectiva(imp.retencion_eeuu_dividendos, imp.tasa_ar_dividendos)
    if renta_fija:
        impuesto = total * t_int
    else:
        impuesto = renta * t_div + (total - renta) * imp.tasa_ganancia_capital
    return total - impuesto, impuesto / total


def tasa_ganancia_realizada(tasa: float, realizacion: float, g: float) -> float:
    """Tasa efectiva anual sobre la ganancia de precio g cuando el impuesto se paga al vender.

    Cada año se vende la fracción `realizacion` (f) de la posición y se paga `tasa` sobre la ganancia
    acumulada de lo vendido (base de costo promedio). En el estado estacionario, la ganancia sin realizar
    vale g(1−f)/(g+f) del valor y lo realizado por año es f·g(1+g)/(g+f), así que el impuesto equivale a
    t_ef·g con t_ef = t·f(1+g)/(g+f). Con f = 1 (todo se realiza cada año) es la tasa plena; con f → 0,
    el impuesto se difiere sin límite. Si g ≤ 0 no hay diferimiento que valga: tasa plena (quebranto).
    """
    if g <= 0:
        return tasa
    return tasa * realizacion * (1 + g) / (g + realizacion)
