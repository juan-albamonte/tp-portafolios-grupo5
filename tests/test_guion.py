"""El guion de la presentación (docs/entregables/guion_presentacion.md) está escrito a mano:
este test verifica que sus cifras del modelo coincidan con outputs/cifras.json. Si cambia el
modelo y falla, hay que actualizar el guion (y su .docx). Versión 3 (deck de 26 láminas).
"""
import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
GUION = RAIZ / "docs" / "entregables" / "guion_presentacion.md"
CIFRAS = RAIZ / "outputs" / "cifras.json"

pytestmark = pytest.mark.skipif(not CIFRAS.exists(), reason="falta outputs/cifras.json: correr python -m tp.correr")


def sin_cero(x: str) -> str:
    """El guion dice "11%" donde la cifra es "11,0%" y "24,6%" donde es "−24,6%"."""
    return x.replace(",0%", "%").replace("−", "")


def n(x: str) -> int:
    return int(x.replace(".", ""))


def miles(x: int) -> str:
    return f"{x:,}".replace(",", ".")


def redondo_mil(x: str) -> str:
    return miles(round(n(x) / 1000) * 1000)


def esperadas() -> list[str]:
    c = json.loads(CIFRAS.read_text(encoding="utf-8"))
    E, S, K, B = c["escenarios"], c["retiro_seguro"], c["cartera"], c["benchmark_historico"]
    N, MV, A, CC, I, M, R = (c["nominal"], c["misma_vara"], c["alternativas"], c["costos_cliente"]["A"],
                              c["impuestos"], c["monitoreo"], c["riesgo"])
    peso = {a["ticker"]: a for a in K["activos"]}
    riesgo = {a["ticker"]: a for a in R["activos"]}
    comp = K["comparacion"]
    crisis = MV["caidas_2008"]["maxima_caida_rebalanceo"]
    ej = M["ejemplos"]["compra_tras_caida"]
    lujo = n(E["A lujo"]["gasto"])
    bono = lujo - n(E["A base"]["gasto"])
    neto_c, neto_e = comp["BL c=1 (final)"]["neto_completo"], comp["Equilibrio (c→0)"]["neto_completo"]
    a_num = lambda x: float(x.rstrip("%").replace(",", "."))
    views_pp = f"{a_num(neto_c) - a_num(neto_e):.2f}".replace(".", ",")
    return [
        # Agustín
        f"por debajo del {MV['benchmark_indices']['vol']} del mercado",
        f"invertís {c['capital']['A']} y tu gasto de nivel lujo es de {E['A lujo']['gasto']} dólares",
        f"tu gasto sube a {E['B lujo']['gasto']}",
        f"te ahorrás {N['alquiler_implicito_mes']} dólares por mes",
        f"rendimiento de {N['depto']} por año en dólares",
        f"rinde {N['neto_cartera_1d']} por año después de impuestos",
        f"son {E['A base']['gasto']} dólares por mes si comprás",
        f"tres o cuatro viajes por año, {E['A lujo']['gasto']}",
        f"viajes de alta gama, {E['A alto']['gasto']}",
        f"retirar {lujo * 12 / n(c['capital']['A']) * 100:.2f}% de tu capital".replace(".", ","),
        f"son {CC['comision_usd']} dólares por año, un {CC['comision_pct']}",
        f"costos propios de los fondos, {CC['fondos_usd']} dólares",
        f"son {CC['total_usd']} dólares por año, el {CC['total_pct']} de tu cartera, unos {CC['total_mes_usd']} por mes",
        # Juan
        f"partimos de {c['embudo']['candidatos']} candidatos", f"dejó afuera a {c['embudo']['excluidos']}",
        f"Quedaron {c['embudo']['universo']}", f"elegimos {c['embudo']['en_optimizacion']} para la optimización",
        f"quedan {c['embudo']['en_cartera']} posiciones",
        # Maxi
        f"se convirtieron en {B['valor_100_txt']}", f"volatilidad histórica de {B['desvio_anual_txt']}",
        f"espera {neto_c} por año después de impuestos y costos. Sin ellas, con el mismo riesgo, {neto_e}",
        f"suman {views_pp} puntos por año",
        f"letras del Tesoro con {peso['BIL']['usd_a']} dólares", f"bonos ajustados por inflación con {peso['SCHP']['usd_a']}",
        f"sustentabilidad con {peso['VCEB']['usd_a']}", f"también con filtro, con {peso['ESGV']['usd_a']}",
        f"Esperamos {K['bruto']} por año antes de impuestos y {K['neto_completo']} después",
        f"NVIDIA pesa {peso['NVDA']['peso']} pero aporta el {riesgo['NVDA']['pct_riesgo']} del riesgo",
        f"pesa {R['europa_en_acciones']}, contra {R['europa_en_acciones_benchmark']} en el benchmark",
        f"tu cartera habría caído {sin_cero(crisis['cartera'])} y el 50/50, {sin_cero(crisis['benchmark'])}",
        f"son {redondo_mil(crisis['diferencia_usd'])} dólares menos",
        f"es de {sin_cero(MV['cartera']['vol'])}, contra {MV['benchmark_indices']['vol']} del 50/50",
        f"es de {MV['cartera']['neto']} contra {MV['benchmark_indices']['neto']}. Esos {MV['menos_neto_pp']} puntos",
        f"bajaron a {ej['pesos_clase']['acciones de EE.UU.']} de la cartera",
        f"Vendimos {redondo_mil(ej['vende_total_usd'])} dólares",
        f"había subido {ej['compra_12m']} y lo que vendimos, {sin_cero(ej['vende_12m'])}",
        f"habríamos rebalanceado {M['rebalanceos']} veces, moviendo un {M['rotacion_anual']} de la cartera",
        # Pedro
        f"en {A['a_quieta']['ruina']} de los escenarios", f"se acaba a los {A['a_quieta']['edad_central']} años",
        f"en {A['b_letras']['ruina']} de los escenarios, y en el caso típico se acaba a los {A['b_letras']['edad_central']}",
        f"esa probabilidad baja a {A['d_cartera']['ruina']}, y a los 90 años todavía tenés "
        f"{A['d_cartera']['patrimonio_90_real']} millones",
        f"pasás de {E['A lujo']['gasto']} a 19.530, a 17.577, a 15.819",
        f"El bono arranca en {miles(bono)}",
        f"la probabilidad es de {E['A lujo']['ruina_fijo']}",
        f"Con sueldo más bono baja a {E['A lujo']['ruina_bono']}: en {E['A lujo']['llegan_bono']} de cada 100",
        f"Alquilando, con sueldo más bono, es {E['B lujo']['ruina_bono']}",
        f"en {E['A lujo']['bono_desaparece']} de los escenarios el bono desaparece",
        f"la plata te alcanza en {E['A lujo']['llegan_estres_bono']} de cada 100 escenarios. Alquilando, en "
        f"{E['B lujo']['llegan_estres_bono']}",
        f"la probabilidad de quedarte sin plata es de {I['base']['ruina_bono']}",
        f"sube a {I['alicuotas_altas']['ruina_bono']}", f"Ahí sube a {I['bp_fijo']['ruina_bono']}",
        f"te sobran {miles(n(S['A: compra']['fijo']) - n(E['A base']['gasto']))} dólares por mes",
        f"alquilando, {miles(n(S['B: alquila']['fijo']) - n(E['B base']['gasto']))}",
        f"hasta {S['A: compra']['bono']} dólares por mes, y alquilando, con {S['B: alquila']['bono']}",
        # Agustín cierra y preguntas probables
        f"Te rinde {N['depto']} por año", f"Invertí los {c['capital']['A']} restantes",
        f"te cuesta {CC['total_pct']} por año", f"en {E['A lujo']['llegan_bono']} de cada 100 escenarios, la plata te alcanza",
        f"se queda sin plata en {A['c_benchmark']['ruina']} de los escenarios y la cartera en {A['d_cartera']['ruina']}",
        f"daría {A['e_benchmark_comision']['ruina']}",
    ]


@pytest.mark.parametrize("frase", esperadas() if CIFRAS.exists() else [])
def test_cifra_del_guion_coincide_con_el_modelo(frase):
    assert frase in GUION.read_text(encoding="utf-8"), f"el guion no dice «{frase}»: actualizarlo"
