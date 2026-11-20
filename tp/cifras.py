"""Cifras ya formateadas para los entregables (deck y textos): outputs/cifras.json.

Una sola fuente: resumen.json y los CSV de outputs/, con el redondeo de tp.formato (mitad
hacia arriba, como Excel). Así el deck, los gráficos y la planilla muestran el mismo número.

El guion de la presentación (docs/entregables/guion_presentacion.md) está escrito a mano;
tests/test_guion.py verifica que sus cifras clave coincidan con este archivo.
"""
import json

import pandas as pd

from tp.comisiones import TRAMOS, comision_anual
from tp.config import BENCHMARK, CLASES, DATA, ESCENARIOS, RANGOS, RETORNO_LARGO_PLAZO, SALIDAS, Mercado
from tp.formato import pct, redondear

ETIQUETA = {"liquidez": "Liquidez", "tesoro": "Tesoro", "tips": "Bonos ajustados por inflación",
            "corporativos": "Corporativos", "acciones_eeuu": "Acciones EE.UU.", "acciones_europa": "Acciones Europa"}


def miles(x: float) -> str:
    return f"{int(redondear(x, 0)):,}".replace(",", ".")


def millones(x: float, d: int = 1) -> str:
    return f"{redondear(x / 1e6, d):.{d}f}".replace(".", ",")


INF = Mercado.inflacion_largo_plazo
NOMBRE_CLASE = {"liquidez": "liquidez", "tesoro": "Tesoro", "tips": "bonos ajustados por inflación",
                "corporativos": "corporativos", "acciones_eeuu": "acciones de EE.UU.",
                "acciones_europa": "acciones de Europa"}


def de_cada_100(ruina: float) -> str:
    """Cuántos de cada 100 escenarios llegan con plata: 100 − ruina, redondeado como Excel."""
    return str(int(redondear(100 * (1 - ruina), 0)))


def a_nominal(r_real: float, inflacion: float = INF) -> float:
    """Retorno nominal en USD equivalente a uno real: (1+r)(1+π) − 1."""
    return (1 + r_real) * (1 + inflacion) - 1


def alquiler_implicito(pres: pd.DataFrame, nivel: str = "lujo") -> float:
    """Lo que comprar le ahorra por mes: alquiler menos ABL y mantenimiento (las expensas las pagan las dos)."""
    p = pres[pres["nivel"] == nivel].set_index("rubro")["usd_mes"]
    return float(p["Alquiler del departamento"] - p["ABL"] - p["Mantenimiento del departamento"])


def m1(x: float) -> str:
    """USD millones con un decimal."""
    return millones(x, 1)


def secciones_v3(res: dict, pres: pd.DataFrame) -> dict:
    """M1-M6: nominal, costos para la clienta, alternativas, impuestos, riesgo y monitoreo."""
    car, ret = res["cartera"], res["retiro"]
    a = ESCENARIOS[0]
    ahorro = alquiler_implicito(pres)
    depto_real = 12 * ahorro / a.valor_casa
    neto_mc = ret["retorno_nominal_neto_cartera"]
    nominal = {
        "neto_cartera": pct(neto_mc, 2), "neto_cartera_1d": pct(neto_mc, 1),
        "neto_sin_gasto_fondos": pct(ret["retorno_nominal_neto_sin_gasto_fondos"], 2),
        "neto_optimizador": pct(car["retorno_neto"], 2), "bruto_optimizador": pct(car["retorno_bruto"], 2),
        "diferencia_optimizador_pp": f"{redondear((car['retorno_neto'] - neto_mc) * 100, 2)}".replace(".", ","),
        "explicacion": ("El optimizador usa el posterior de Black-Litterman (con views); el Monte Carlo, los retornos "
                        "de largo plazo por clase y los gastos de los fondos."),
        "real_neto": pct(ret["retorno_real_neto_cartera"], 2), "inflacion": pct(INF, 2),
        "alquiler_implicito_mes": miles(ahorro), "depto_real": pct(depto_real, 2), "depto": pct(a_nominal(depto_real), 1),
        "estres_2008_anio1_nominal": pct(ret["estres_2008_cartera_anio1_nominal"]),
        "estres_2008_anio1_real": pct(ret["estres_2008_cartera_anio1_real"]),
    }
    costos = {}
    for e in ESCENARIOS:
        com = float(comision_anual(e.capital_inicial))
        fon = ret["gasto_fondos_cartera"] * e.capital_inicial
        costos[e.nombre[0]] = {"capital": miles(e.capital_inicial), "comision_usd": miles(com),
                               "comision_pct": pct(com / e.capital_inicial, 2), "fondos_usd": miles(fon),
                               "fondos_pct": pct(ret["gasto_fondos_cartera"], 3), "total_usd": miles(com + fon),
                               "total_pct": pct((com + fon) / e.capital_inicial, 2),
                               "total_mes_usd": miles((com + fon) / 12)}
    piso = 0.0
    tramos = []
    for techo, tasa in TRAMOS:
        tramos.append({"desde": miles(piso), "hasta": "" if techo == float("inf") else miles(techo), "tasa": pct(tasa, 2)})
        piso = techo
    costos["tramos"] = tramos
    alt = {}
    for k, v in ret["alternativas"].items():
        alt[k] = {"ruina": pct(v["ruina"]),
                  "edad_mediana_ruina": "" if v["edad_mediana_ruina"] is None else f"{v['edad_mediana_ruina']:.0f}",
                  "edad_central": f"{v['edad_central']:.0f}" if v.get("edad_central") is not None else "",
                  "bono_desaparece": pct(v["bono_desaparece"], 0),
                  "real_compuesto": pct(v["retorno_real_compuesto"], 2),
                  "nominal_compuesto": pct(a_nominal(v["retorno_real_compuesto"]), 2),
                  **{f"patrimonio_{e}_real": m1(x) for e, x in v["patrimonio"]["real"].items()},
                  **{f"patrimonio_{e}_nominal": m1(x) for e, x in v["patrimonio"]["nominal"].items()}}
    alt["vol_benchmark"] = pct(ret["alternativas_benchmark_vol"])
    imp = {k: {"ruina_bono": pct(v["ruina_bono"]), "seguro_bono": miles(v["seguro_bono"])}
           for k, v in ret["impuestos"].items()}
    r = car["riesgo"]
    riesgo = {"activos": [{"ticker": t, "peso": pct(car["pesos"][t]), "aporte_pp": f"{redondear(x * 100, 2)}".replace(".", ","),
                           "pct_riesgo": pct(r["pct"][t])}
                          for t, x in sorted(r["aporte"].items(), key=lambda kv: -kv[1])],
              "mayor_accion": r["mayor_accion"], "vol": pct(r["vol"], 1),
              "europa_en_acciones": pct(r["regiones"]["acciones_europa"], 0),
              "eeuu_en_acciones": pct(r["regiones"]["acciones_eeuu"], 0),
              "europa_en_acciones_benchmark": pct(r["regiones_benchmark"]["acciones_europa"], 0),
              "eeuu_en_acciones_benchmark": pct(r["regiones_benchmark"]["acciones_eeuu"], 0)}
    mo = car["monitoreo"]
    ej = {}
    for k, e in mo["ejemplos"].items():
        ej[k] = {"fecha": e["fecha"], "motivo": e["motivo"], "clase": NOMBRE_CLASE[e["clase_mas_desviada"]],
                 "desvio": pct(e["desvio"]), "capital_usd": miles(e["capital_usd"]),
                 "pesos_clase": {NOMBRE_CLASE[c]: pct(x) for c, x in e["pesos_clase"].items()},
                 "vende_usd": {t: miles(x * e["capital_usd"]) for t, x in e["vende"].items()},
                 "compra_usd": {t: miles(x * e["capital_usd"]) for t, x in e["compra"].items()},
                 "vende_total_usd": miles(sum(e["vende"].values()) * e["capital_usd"]),
                 "compra_12m": pct(e["compra_12m"]), "vende_12m": pct(e["vende_12m"])}
    monitoreo = {"rebalanceos": mo["rebalanceos"], "revisiones": mo["revisiones"], "anios": f"{mo['anios']:.0f}",
                 "rotacion_anual": pct(mo["rotacion_anual"], 0), "literal_rebalanceos": mo["literal"]["rebalanceos"],
                 "literal_rotacion_anual": pct(mo["literal"]["rotacion_anual"], 0),
                 "tolerancia_rango_pp": f"{mo['tolerancia_rango'] * 100:.0f}",
                 "tope_accion_disparo": pct(mo["tope_accion_disparo"], 0),
                 "fechas": mo["fechas"] if "fechas" in mo else [e["fecha"] for e in mo["eventos"]],
                 "desvio_max": {NOMBRE_CLASE[c]: pct(x) for c, x in mo["desvio_max"].items()}, "ejemplos": ej}
    mv = car["misma_vara"]
    misma = {k: {"vol": pct(v["vol"], 1), "bruto": pct(v["bruto"], 2), "neto": pct(v["neto"], 2),
                 "sharpe": f"{redondear(v['sharpe'], 2)}".replace(".", ",")}
             for k, v in mv.items() if isinstance(v, dict) and "vol" in v}
    misma["tracking_error"] = pct(mv["tracking_error"], 1)
    c08 = mv["caida_2008"]
    capA = ESCENARIOS[0].capital_inicial
    misma["caida_2008"] = {"cartera": pct(c08["cartera"]), "cartera_por_clase": pct(c08["cartera_por_clase"]),
                           "benchmark": pct(c08["benchmark"]), "cartera_usd": miles(-c08["cartera"] * capA),
                           "benchmark_usd": miles(-c08["benchmark"] * capA),
                           "diferencia_usd": miles((c08["cartera"] - c08["benchmark"]) * capA)}
    misma["con_views"] = {k: pct(v, 2) for k, v in mv["con_views"].items()}
    misma["caidas_2008"] = {k: {"cartera": pct(v["cartera"]), "benchmark": pct(v["benchmark"]),
                                "diferencia_usd": miles((v["cartera"] - v["benchmark"]) * capA),
                                "cartera_usd": miles(-v["cartera"] * capA), "benchmark_usd": miles(-v["benchmark"] * capA)}
                            for k, v in mv["caidas_2008"].items()}
    misma["menos_vol_pp"] = f"{redondear((mv['benchmark_indices']['vol'] - mv['cartera']['vol']) * 100, 1)}".replace(".", ",")
    misma["menos_neto_pp"] = f"{redondear((mv['benchmark_indices']['neto'] - mv['cartera']['neto']) * 100, 2)}".replace(".", ",")
    return {"misma_vara": misma, "nominal": nominal, "costos_cliente": costos, "alternativas": alt, "impuestos": imp, "riesgo": riesgo,
            "monitoreo": monitoreo}


def armar() -> dict:
    res = json.loads((SALIDAS / "resumen.json").read_text(encoding="utf-8"))
    car, ret = res["cartera"], res["retiro"]
    ca = pd.read_csv(SALIDAS / "cartera.csv")
    pres = pd.read_csv(DATA / "presupuesto.csv")
    u = pd.read_csv(SALIDAS / "universo.csv")
    ex = pd.read_csv(SALIDAS / "excluidos.csv")
    cand = pd.read_csv(DATA / "candidatos.csv", sep=None, engine="python")

    activos = [{"ticker": r.ticker, "clase": r.clase, "peso": pct(r.peso), "peso_num": r.peso,
                "usd_a": miles(r.usd_compra), "usd_b": miles(r.usd_alquila)} for r in ca.itertuples() if r.peso > 1e-6]
    clases = [{"clase": ETIQUETA[c], "peso": pct(car["pesos_por_clase"][c]), "benchmark": pct(BENCHMARK[c], 0),
               "rango": f"{pct(RANGOS[c][0], 0)} a {pct(RANGOS[c][1], 0)}", "lp": pct(RETORNO_LARGO_PLAZO[c], 2)}
              for c in CLASES]
    esc = {}
    for k, e in ret["escenarios"].items():
        esc[k] = {"gasto": miles(e["gasto_mes"]), "ruina_fijo": pct(e["ruina_sin_barandas"]),
                  "ruina_bono": pct(e["ruina_con_barandas"]),
                  "bono_desaparece": pct(e["barandas_bajan_al_base"], 0) if e["barandas_bajan_al_base"] is not None else "",
                  "ruina_85": pct(e["ruina_fija"]["85"]), "ruina_95": pct(e["ruina_fija"]["95"]),
                  "ruina_100": pct(e["ruina_fija"]["100"]),
                  "estres_fijo": pct(e["estres_2008"]["ruina_sin_barandas"]),
                  "estres_bono": pct(e["estres_2008"]["ruina_con_barandas"]),
                  # "N de cada 100 escenarios llegan": 100 − ruina, con el redondeo único.
                  "llegan_fijo": de_cada_100(e["ruina_sin_barandas"]), "llegan_bono": de_cada_100(e["ruina_con_barandas"]),
                  "llegan_estres_bono": de_cada_100(e["estres_2008"]["ruina_con_barandas"])}
    seguro = {k: {"fijo": miles(v["sin_barandas"]), "bono": miles(v["con_barandas"]),
                  "fijo_2008": miles(v["estres_2008"]["sin_barandas"]), "bono_2008": miles(v["estres_2008"]["con_barandas"])}
              for k, v in ret["retiro_seguro"].items()}
    sens = {k: {"ret": pct(v["retorno_real_neto"], 2), "ret_nominal": pct(a_nominal(v["retorno_real_neto"]), 2), **{e: pct(x) for e, x in v["ruina_sin_barandas"].items()},
                **{f"seguro {e}": miles(x) for e, x in v["retiro_seguro_sin_barandas"].items()}}
            for k, v in ret["sensibilidades"].items()}
    comp = {k: {"neto_completo": pct(v["retorno_neto_completo"], 2), "neto": pct(v["retorno_neto"], 2), "vol": pct(v["vol"]), "sharpe": f"{redondear(v['sharpe'], 2)}".replace(".", ",")}
            for k, v in car["comparacion"].items()}
    gastos = {}
    for e in ESCENARIOS:
        for nivel in ("base", "lujo", "alto"):
            filas = pres["escenario"].isin(["ambos", e.clave_vivienda]) & (pres["nivel"] == nivel)
            gastos[f"{e.nombre[0]} {nivel}"] = miles(pres.loc[filas, "usd_mes"].sum())
    v3 = secciones_v3(res, pres)
    return {
        **v3,
        "cartera": {"activos": activos, "clases": clases, "bruto": pct(car["retorno_bruto"], 2),
                    "neto": pct(car["retorno_neto"], 2), "neto_completo": pct(car["retorno_neto_completo"], 2),
                    "realizacion": pct(car["realizacion"]["cartera"], 1),
                    "realizacion_benchmark": pct(car["realizacion"]["benchmark"], 1), "vol": pct(car["vol"], 1),
                    "sharpe": f"{redondear(car['sharpe'], 2)}".replace(".", ","), "te": pct(car["tracking_error"], 1),
                    "posiciones": car["posiciones"], "comparacion": comp},
        "capital": {"A": miles(ESCENARIOS[0].capital_inicial), "B": miles(ESCENARIOS[1].capital_inicial),
                    "A_m": millones(ESCENARIOS[0].capital_inicial, 3), "B_m": millones(ESCENARIOS[1].capital_inicial, 1)},
        "escenarios": esc, "retiro_seguro": seguro, "sensibilidades": sens, "presupuesto": gastos,
        "benchmark_historico": {**car["benchmark_historico"],
                                "retorno_anual_txt": pct(car["benchmark_historico"]["retorno_anual"], 2),
                                "desvio_anual_txt": pct(car["benchmark_historico"]["desvio_anual"], 1),
                                "peor_caida_txt": pct(car["benchmark_historico"]["peor_caida"], 1),
                                "valor_100_txt": miles(car["benchmark_historico"]["valor_100"])},
        "retorno_real_neto": pct(ret["retorno_real_neto_cartera"]),
        "estres_anio1_real": pct(ret["estres_2008_cartera_anio1_real"]),
        "embudo": {"candidatos": len(cand), "excluidos": len(ex), "universo": len(u),
                   "acciones": int((u["tipo"] == "accion").sum()), "fondos": int((u["tipo"] == "fondo").sum()),
                   "en_optimizacion": int((u["seleccionado"] == "sí").sum()), "en_cartera": len(activos)},
    }


def main() -> dict:
    c = armar()
    (SALIDAS / "cifras.json").write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
    return c


if __name__ == "__main__":
    main()
