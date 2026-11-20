"""Planilla del TP: outputs/TP_Grupo5.xlsx, una hoja por tabla.

Uso: python -m tp.correr --etapa 7   (después de las etapas 1 a 5)

Convenciones: Arial; fila 1 título, fila 2 fuente, fila 3 encabezados, datos desde la fila 4,
panel inmovilizado. Los resultados del modelo van como valores (salen de Python y su fuente
está anotada en la fila 2). Lo que se deriva de ellos va como fórmula de Excel, y sus
supuestos en celdas azules: USD por activo, totales, pesos por clase, retornos reales y
presupuestos por nivel.
"""
import json

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from tp.config import (BENCHMARK, CLASES, DATA, ESCENARIOS, PROXIES, RANGOS, RETORNO_LARGO_PLAZO, SALIDAS,
                       Mercado)
from tp.escenario import VOL_CLASES, a_aritmetico

ARCHIVO = SALIDAS / "TP_Grupo5.xlsx"
HOJAS = ["Universo", "Excluidos", "Screening", "Benchmark histórico", "Correlaciones", "Retornos largo plazo",
         "Cartera final", "Comparación", "Misma vara", "Aporte al riesgo", "Monitoreo", "Sensibilidades",
         "Monte Carlo", "Invertir o no", "Impuestos", "Costos", "Presupuestos"]

FUENTE = "Arial"
AZUL = Font(name=FUENTE, size=10, color="0000FF")
NORMAL = Font(name=FUENTE, size=10)
NEGRITA = Font(name=FUENTE, size=10, bold=True)
ENCABEZADO = PatternFill("solid", fgColor="EEF1F5")
SUPUESTO = PatternFill("solid", fgColor="FFFF00")
LINEA = Border(bottom=Side(style="thin", color="C9CED6"))
PCT1, PCT2, USD, DEC2, DEC3 = "0.0%", "0.00%", "#,##0", "0.00", "0.000"

CLASE = {"liquidez": "Liquidez", "tesoro": "Tesoro", "tips": "Bonos ajustados por inflación",
         "corporativos": "Corporativos", "acciones_eeuu": "Acciones EE.UU.", "acciones_europa": "Acciones Europa"}


# --------------------------------------------------------------------- escritura

def escribir_hoja(wb: Workbook, nombre: str, df: pd.DataFrame, nota: str = "", formatos: dict | None = None,
                  anchos: dict | None = None):
    """Título (fila 1), nota de fuente (fila 2), encabezados (fila 3) y datos desde la fila 4."""
    ws = wb.create_sheet(nombre)
    formatos, anchos = formatos or {}, anchos or {}
    ws["A1"] = nombre
    ws["A1"].font = Font(name=FUENTE, size=13, bold=True, color="1F3A5F")
    ws["A2"] = nota
    ws["A2"].font = Font(name=FUENTE, size=9, italic=True, color="52514E")
    for j, col in enumerate(df.columns, start=1):
        c = ws.cell(row=3, column=j, value=str(col))
        c.font, c.fill, c.border = NEGRITA, ENCABEZADO, LINEA
        c.alignment = Alignment(wrap_text=True, vertical="bottom")
    for i, fila in enumerate(df.itertuples(index=False), start=4):
        for j, (col, v) in enumerate(zip(df.columns, fila), start=1):
            if isinstance(v, (np.floating, float)) and np.isnan(v):
                v = None
            elif isinstance(v, np.generic):
                v = v.item()
            c = ws.cell(row=i, column=j, value=v)
            c.font = NORMAL
            if col in formatos:
                c.number_format = formatos[col]
    for j, col in enumerate(df.columns, start=1):
        largo = max([len(str(col))] + [len(str(v)) for v in df[col].head(200)]) if len(df) else len(str(col))
        ws.column_dimensions[get_column_letter(j)].width = anchos.get(col, min(max(10, largo + 2), 60))
    ws.row_dimensions[3].height = 30
    ws.freeze_panes = "A4"
    return ws


def etiqueta(ws, celda: str, texto: str, negrita: bool = True) -> None:
    ws[celda] = texto
    ws[celda].font = NEGRITA if negrita else NORMAL


def supuesto(ws, celda: str, valor, formato: str) -> None:
    ws[celda] = valor
    ws[celda].font, ws[celda].fill, ws[celda].number_format = AZUL, SUPUESTO, formato


def formula(ws, celda: str, f: str, formato: str, negrita: bool = False) -> None:
    ws[celda] = f
    ws[celda].font = NEGRITA if negrita else NORMAL
    ws[celda].number_format = formato


# --------------------------------------------------------------------- hojas

def hoja_universo(wb, u: pd.DataFrame) -> None:
    df = pd.DataFrame({"Activo": u["ticker"], "Nombre": u["nombre"], "Clase": u["clase"].map(CLASE), "Tipo": u["tipo"],
                       "País": u["pais"], "Sector": u["sector"], "ESG S&P Global": u["esg_sp"],
                       "Fuente ESG": u["fuente_esg"], "Por qué entra": u["por_que_entra"],
                       "CEDEAR en BYMA": u["cedear_byma"], "En cartera": u["seleccionado"]})
    escribir_hoja(wb, "Universo", df, "Candidatos que pasaron el filtro de exclusiones y la nota mínima de 25 en el "
                  "S&P Global ESG Score. Fuentes: S&P Global ESG Score (CSA 2024 del DJSI donde no hay puntaje público), "
                  "exclusiones publicadas por cada fondo (Vanguard), Yahoo Finance y lista de CEDEAR de BYMA. Noviembre de 2026.",
                  anchos={"Por qué entra": 60})


def hoja_excluidos(wb, ex: pd.DataFrame) -> None:
    df = pd.DataFrame({"Activo": ex["ticker"], "Nombre": ex["nombre"], "Clase": ex["clase"].map(CLASE),
                       "Sector": ex["sector"], "Motivo": ex["motivo"]})
    escribir_hoja(wb, "Excluidos", df, "Candidatos excluidos por actividad (armamento, tabaco, combustibles fósiles) "
                  "o por nota ESG menor a 25.", anchos={"Motivo": 60})


def hoja_screening(wb, sc: pd.DataFrame) -> None:
    sc = sc.sort_values(["sector", "puntaje"], ascending=[True, False])
    df = pd.DataFrame({"Sector": sc["sector"], "Acción": sc["ticker"], "Nombre": sc["nombre"], "País": sc["pais"],
                       "Tesis del sector": sc["tesis_sector"], "P/E forward": sc["pe_forward"],
                       "Crecimiento de ganancias": sc["crecimiento_ganancias"], "Margen operativo": sc["margen_operativo"],
                       "Deuda neta / EBITDA": sc["deuda_neta_ebitda"], "ROE": sc["roe"],
                       "Dividendo + recompras": sc["retorno_accionista"], "ESG S&P Global": sc["esg"],
                       "Puntaje": sc["puntaje"], "Puesto en el sector": sc["puesto_en_sector"]})
    escribir_hoja(wb, "Screening", df, "Puntaje = promedio de los percentiles de cada métrica dentro del sector "
                  "(0,5 = mitad del sector). Fuente: Yahoo Finance al 15/11/2026; ESG de S&P Global.",
                  {"P/E forward": "0.0", "Crecimiento de ganancias": PCT1, "Margen operativo": PCT1,
                   "Deuda neta / EBITDA": "0.0", "ROE": PCT1, "Dividendo + recompras": PCT1, "ESG S&P Global": "0",
                   "Puntaje": DEC2, "Puesto en el sector": "0"})


def hoja_benchmark(wb, guia: pd.DataFrame, caida: tuple) -> None:
    nombres = {c: f"{CLASE[c]} ({PROXIES[c]})" for c in CLASES} | {"benchmark": "Benchmark 50/50"}
    g = guia.loc[CLASES + ["benchmark"]]
    df = pd.DataFrame({"Serie": [nombres[i] for i in g.index],
                       "Peso en el benchmark": [BENCHMARK.get(i, 1.0) for i in g.index],
                       "Rendimiento diario medio": g["retorno_diario_medio"].values, "Desvío diario": g["desvio_diario"].values,
                       "Rendimiento anual": g["retorno_anual"].values, "Desvío anual": g["desvio_anual"].values,
                       "Ratio de Sharpe": g["sharpe"].values, "Peor caída": g["maxima_caida"].values})
    ws = escribir_hoja(wb, "Benchmark histórico", df, "Retornos diarios 06/2007-10/2026 (Yahoo Finance). Rendimiento "
                       "anual compuesto; desvío anual = diario × √252; Sharpe con la tasa de las letras del período. "
                       "Benchmark rebalanceado a diario.",
                       {"Peso en el benchmark": "0%", "Rendimiento diario medio": "0.000%", "Desvío diario": PCT2,
                        "Rendimiento anual": PCT2, "Desvío anual": PCT2, "Ratio de Sharpe": DEC2, "Peor caída": PCT1})
    n = 4 + len(df)
    etiqueta(ws, f"A{n + 1}", "Suma de pesos del benchmark")
    formula(ws, f"B{n + 1}", f"=SUM(B4:B{n - 2})", "0%", True)
    etiqueta(ws, f"A{n + 2}", f"Peor caída del benchmark: del {caida[1]:%d/%m/%Y} al {caida[2]:%d/%m/%Y}", False)
    exp_comp = sum(w * RETORNO_LARGO_PLAZO[c] for c, w in BENCHMARK.items())
    exp_arit = sum(w * a_aritmetico(RETORNO_LARGO_PLAZO[c], VOL_CLASES[c]) for c, w in BENCHMARK.items())
    etiqueta(ws, f"A{n + 4}", "Esperado (escenario base, 10-15 años)")
    for k, (txt, v, fmt) in enumerate([("Rendimiento anual compuesto", exp_comp, PCT2),
                                       ("Rendimiento anual aritmético", exp_arit, PCT2)], start=5):
        etiqueta(ws, f"A{n + k}", txt, False)
        ws[f"B{n + k}"], ws[f"B{n + k}"].number_format, ws[f"B{n + k}"].font = v, fmt, NORMAL
    etiqueta(ws, f"A{n + 7}", "Rendimiento diario esperado (aritmético / 252)", False)
    formula(ws, f"B{n + 7}", f"=B{n + 6}/252", "0.000%")


def hoja_correlaciones(wb, corr: pd.DataFrame, corr_activos: pd.DataFrame) -> None:
    df = corr.copy()
    df.index = [f"{CLASE[c]} ({PROXIES[c]})" for c in df.index]
    df.columns = [PROXIES[c] for c in corr.columns]
    df = df.reset_index().rename(columns={"index": "Clase (índice)"})
    ws = escribir_hoja(wb, "Correlaciones", df, "Arriba: correlaciones diarias de los índices del benchmark "
                       "(06/2007-10/2026). Abajo: matriz de los 14 activos de la cartera, de la covarianza de "
                       "Ledoit-Wolf (10 años de retornos diarios).", {c: DEC2 for c in df.columns[1:]})
    r0 = 4 + len(df) + 2
    etiqueta(ws, f"A{r0}", "Activo")
    for j, a in enumerate(corr_activos.columns, start=2):
        c = ws.cell(row=r0, column=j, value=a)
        c.font, c.fill = NEGRITA, ENCABEZADO
    for i, a in enumerate(corr_activos.index, start=r0 + 1):
        ws.cell(row=i, column=1, value=a).font = NEGRITA
        for j, b in enumerate(corr_activos.columns, start=2):
            c = ws.cell(row=i, column=j, value=float(corr_activos.loc[a, b]))
            c.font, c.number_format = NORMAL, DEC2


def hoja_retornos(wb) -> None:
    df = pd.DataFrame({"Clase": [CLASE[c] for c in CLASES], "Índice": [PROXIES[c] for c in CLASES],
                       "Compuesto nominal": [RETORNO_LARGO_PLAZO[c] for c in CLASES],
                       "Volatilidad de la clase": [VOL_CLASES[c] for c in CLASES],
                       "Aritmético nominal": [a_aritmetico(RETORNO_LARGO_PLAZO[c], VOL_CLASES[c]) for c in CLASES],
                       "Compuesto real": [None] * 6, "Peso en el benchmark": [BENCHMARK[c] for c in CLASES]})
    ws = escribir_hoja(wb, "Retornos largo plazo", df, "Retornos nominales en USD a 10-15 años del escenario base "
                       "(EIC, economía). Aritmético = media de una lognormal con esa mediana y esa volatilidad.",
                       {"Compuesto nominal": PCT2, "Volatilidad de la clase": PCT2, "Aritmético nominal": PCT2,
                        "Compuesto real": PCT2, "Peso en el benchmark": "0%"})
    for i in range(4, 10):
        ws[f"C{i}"].font = AZUL
        formula(ws, f"F{i}", f"=(1+C{i})/(1+$B$12)-1", PCT2)
    etiqueta(ws, "A12", "Inflación de largo plazo (supuesto)")
    supuesto(ws, "B12", Mercado.inflacion_largo_plazo, PCT2)
    etiqueta(ws, "A13", "Benchmark: compuesto nominal (promedio ponderado)")
    formula(ws, "B13", "=SUMPRODUCT(C4:C9,G4:G9)", PCT2, True)
    etiqueta(ws, "A14", "Benchmark: aritmético nominal (promedio ponderado)")
    formula(ws, "B14", "=SUMPRODUCT(E4:E9,G4:G9)", PCT2, True)
    etiqueta(ws, "A15", "Tasa corta de largo plazo (liquidez)")
    formula(ws, "B15", "=C4", PCT2)
    etiqueta(ws, "A16", "Exceso aritmético del benchmark sobre la tasa corta")
    formula(ws, "B16", "=B14-B15", PCT2, True)


def hoja_cartera(wb, ca: pd.DataFrame) -> None:
    n = len(ca)
    df = pd.DataFrame({"Clase": ca["clase"].map(CLASE), "Activo": ca["ticker"], "Nombre": ca["nombre"],
                       "Tipo": ca["tipo"], "Peso": ca["peso"], "USD si compra (A)": [None] * n,
                       "USD si alquila (B)": [None] * n})
    ws = escribir_hoja(wb, "Cartera final", df, "Black-Litterman de mercado (Meucci, 2010) y optimización después de "
                       "impuestos con volatilidad ≤ 9%, rangos de la política, tope 5% por acción y 30% por fondo, "
                       "ESGV ≥ 20%, cada acción 0 o ≥ 2%. Los USD son fórmulas sobre el capital de cada escenario.",
                       {"Peso": PCT1, "USD si compra (A)": USD, "USD si alquila (B)": USD})
    ult = 3 + n
    cap = ult + 3
    etiqueta(ws, f"A{cap}", "Capital invertido, escenario A (compra), USD")
    supuesto(ws, f"B{cap}", ESCENARIOS[0].capital_inicial, USD)
    etiqueta(ws, f"A{cap + 1}", "Capital invertido, escenario B (alquila), USD")
    supuesto(ws, f"B{cap + 1}", ESCENARIOS[1].capital_inicial, USD)
    for i in range(4, ult + 1):
        ws[f"E{i}"].font = AZUL
        formula(ws, f"F{i}", f"=E{i}*$B${cap}", USD)
        formula(ws, f"G{i}", f"=E{i}*$B${cap + 1}", USD)
    etiqueta(ws, f"A{ult + 1}", "Total")
    for col, fmt in (("E", PCT1), ("F", USD), ("G", USD)):
        formula(ws, f"{col}{ult + 1}", f"=SUM({col}4:{col}{ult})", fmt, True)
    r = cap + 3
    for j, t in enumerate(["Clase", "Peso", "Benchmark", "Mínimo", "Máximo", "USD si compra (A)", "USD si alquila (B)"], 1):
        c = ws.cell(row=r, column=j, value=t)
        c.font, c.fill, c.border = NEGRITA, ENCABEZADO, LINEA
    for k, cl in enumerate(CLASES, start=r + 1):
        ws[f"A{k}"] = CLASE[cl]
        ws[f"A{k}"].font = NORMAL
        formula(ws, f"B{k}", f"=SUMIF($A$4:$A${ult},A{k},$E$4:$E${ult})", PCT1)
        for col, v in (("C", BENCHMARK[cl]), ("D", RANGOS[cl][0]), ("E", RANGOS[cl][1])):
            supuesto(ws, f"{col}{k}", v, "0%")
        formula(ws, f"F{k}", f"=SUMIF($A$4:$A${ult},A{k},$F$4:$F${ult})", USD)
        formula(ws, f"G{k}", f"=SUMIF($A$4:$A${ult},A{k},$G$4:$G${ult})", USD)


def hoja_comparacion(wb, carteras: dict, metricas: dict, ins) -> None:
    nombres = {"BL c=1 (final)": "Final (con views)", "Equilibrio (c→0)": "Equilibrio sin views",
               "HRP ajustado": "Paridad de riesgo jerárquica", "Mín. varianza": "Mínima varianza",
               "Neutro (50/50)": "50/50 con nuestros activos (neutra)"}
    df = pd.DataFrame({"Activo": ins.activos, "Clase": [CLASE[c] for c in ins.clase]})
    for k, w in carteras.items():
        df[nombres[k]] = w.values
    ws = escribir_hoja(wb, "Comparación", df, "Mismas reglas que la cartera final. Métricas evaluadas con los retornos "
                       "con views (c = 1). Neto: después de impuestos (ganancia de capital al realizar) y de los costos "
                       "de los fondos. Volatilidad con la covarianza de Ledoit-Wolf.",
                       {nombres[k]: PCT1 for k in carteras})
    r = 4 + len(df) + 1
    filas = [("Retorno esperado bruto", "retorno_bruto", PCT2), ("Retorno esperado neto", "retorno_neto_completo", PCT2),
             ("Volatilidad", "vol", PCT2), ("Ratio de Sharpe", "sharpe", DEC2),
             ("Tracking error contra la neutra", "tracking_error", PCT2), ("Herfindahl", "herfindahl", DEC3)]
    for k, (txt, clave, fmt) in enumerate(filas):
        etiqueta(ws, f"A{r + k}", txt)
        for j, nombre in enumerate(carteras, start=3):
            c = ws.cell(row=r + k, column=j, value=float(metricas[nombre][clave]))
            c.font, c.number_format = NORMAL, fmt


def hoja_sensibilidades(wb, filas_bl: list[dict], resumen: dict) -> None:
    df = pd.DataFrame(filas_bl)
    ws = escribir_hoja(wb, "Sensibilidades", df, "Arriba: pesos por clase de la cartera optimizada en cada caso; retorno "
                       "neto con views, después de impuestos (ganancia de capital al realizar) y costos de los fondos. "
                       "Abajo: simulación de retiros (probabilidad de quedarse sin dinero en vida con gasto fijo y "
                       "retiro máximo seguro en USD por mes).",
                       {c: PCT1 for c in df.columns if c not in ("Caso", "Rotación contra la final")} |
                       {"Rotación contra la final": PCT1})
    sens = resumen["retiro"]["sensibilidades"]
    esc = list(next(iter(sens.values()))["ruina_sin_barandas"])
    r = 4 + len(df) + 2
    cab = ["Caso de la simulación", "Retorno real neto"] + [f"Ruina {e}" for e in esc] + \
          [f"Retiro seguro {v}" for v in next(iter(sens.values()))["retiro_seguro_sin_barandas"]]
    for j, t in enumerate(cab, 1):
        c = ws.cell(row=r, column=j, value=t)
        c.font, c.fill, c.alignment = NEGRITA, ENCABEZADO, Alignment(wrap_text=True)
    for i, (k, v) in enumerate(sens.items(), start=r + 1):
        vals = [k, v["retorno_real_neto"]] + [v["ruina_sin_barandas"][e] for e in esc] + \
               list(v["retiro_seguro_sin_barandas"].values())
        fmts = ["@", PCT2] + [PCT1] * len(esc) + [USD] * len(v["retiro_seguro_sin_barandas"])
        for j, (x, f) in enumerate(zip(vals, fmts), 1):
            c = ws.cell(row=i, column=j, value=x)
            c.font, c.number_format = NORMAL, f


def hoja_montecarlo(wb, resumen: dict) -> None:
    r = resumen["retiro"]
    capital = {"A": ESCENARIOS[0].capital_inicial, "B": ESCENARIOS[1].capital_inicial}
    filas = []
    for k, e in r["escenarios"].items():
        filas.append({"Escenario": k, "Vivienda": "Compra" if k.startswith("A") else "Alquila", "Nivel": k.split()[1],
                      "Capital (USD)": capital[k[0]], "Gasto mensual (USD)": e["gasto_mes"], "Retiro / capital": None,
                      "Ruina, gasto fijo": e["ruina_sin_barandas"], "Ruina a 85": e["ruina_fija"]["85"],
                      "Ruina a 95": e["ruina_fija"]["95"], "Ruina a 100": e["ruina_fija"]["100"],
                      "Ruina, sueldo fijo + bono": e["ruina_con_barandas"],
                      "El bono desaparece alguna vez": e["barandas_bajan_al_base"],
                      "Ruina 2008, gasto fijo": e["estres_2008"]["ruina_sin_barandas"],
                      "Ruina 2008, sueldo fijo + bono": e["estres_2008"]["ruina_con_barandas"]})
    df = pd.DataFrame(filas)
    pct = [c for c in df.columns if c.startswith("Ruina") or c.startswith("El bono") or c == "Retiro / capital"]
    ws = escribir_hoja(wb, "Monte Carlo", df, "10.000 escenarios anuales en USD reales, mortalidad de Gompertz "
                       "(m = 93, b = 9), impuestos por activo (ganancia de capital al realizar), costos de los fondos, comisión "
                       "por tramos y Bienes Personales. Ruina = "
                       "quedarse sin dinero estando viva. Sueldo fijo = gasto base; bono = barandas de Guyton-Klinger.",
                       {"Capital (USD)": USD, "Gasto mensual (USD)": USD} | {c: PCT1 for c in pct})
    for i in range(4, 4 + len(df)):
        formula(ws, f"F{i}", f"=E{i}*12/D{i}", PCT2)
    s = 4 + len(df) + 2
    for j, t in enumerate(["Vivienda", "Retiro seguro, gasto fijo", "Retiro seguro, sueldo fijo + bono",
                           "Gasto fijo, con 2008", "Sueldo fijo + bono, con 2008"], 1):
        c = ws.cell(row=s, column=j, value=t)
        c.font, c.fill, c.alignment = NEGRITA, ENCABEZADO, Alignment(wrap_text=True)
    for i, (k, v) in enumerate(r["retiro_seguro"].items(), start=s + 1):
        for j, x in enumerate([k, v["sin_barandas"], v["con_barandas"], v["estres_2008"]["sin_barandas"],
                               v["estres_2008"]["con_barandas"]], 1):
            c = ws.cell(row=i, column=j, value=x)
            c.font, c.number_format = NORMAL, USD if j > 1 else "@"
    etiqueta(ws, f"A{s + 4}", "Retiro seguro = el retiro mensual más alto (USD) con ruina de 5% o menos.", False)


def tabla_simple(ws, fila: int, encabezados: list[str], filas: list[list], formatos: list[str]) -> int:
    """Una tabla debajo de otra en la misma hoja. Devuelve la fila siguiente a la tabla."""
    for j, t in enumerate(encabezados, 1):
        c = ws.cell(row=fila, column=j, value=t)
        c.font, c.fill, c.alignment = NEGRITA, ENCABEZADO, Alignment(wrap_text=True)
    for i, f in enumerate(filas, start=fila + 1):
        for j, (x, fmt) in enumerate(zip(f, formatos), 1):
            c = ws.cell(row=i, column=j, value=x)
            c.font, c.number_format = NORMAL, fmt
    return fila + len(filas) + 2


NOMBRE_ALT = {"a_quieta": "a. Plata quieta (0% nominal, sin comisión)", "b_letras": "b. Todo en letras del Tesoro (BIL)",
              "c_benchmark": "c. 50/50 de seis índices, sin comisión", "d_cartera": "d. Nuestra cartera",
              "e_benchmark_comision": "e. 50/50 de seis índices, con nuestra comisión"}


def hoja_misma_vara(wb, mv: dict) -> None:
    nombres = {"cartera": "Nuestra cartera", "benchmark_indices": "50/50 (seis índices)",
               "neutra_14": "50/50 con nuestros activos (neutra)", "neutra_europa_vgk": "Neutra con Europa en VGK",
               "neutra_europa_vgk_eeuu_spy": "Neutra con Europa en VGK y EE.UU. en SPY"}
    df = pd.DataFrame([{"Cartera": nombres[k], "Volatilidad": v["vol"], "Retorno bruto": v["bruto"],
                        "Retorno neto": v["neto"], "Sharpe": v["sharpe"]} for k, v in mv.items() if k in nombres])
    ws = escribir_hoja(wb, "Misma vara", df, "Misma covarianza (Ledoit-Wolf diaria conjunta de los 14 activos y los 6 "
                       f"índices, {mv['desde']} a {mv['hasta']}), retornos de largo plazo por clase sin views, mismos "
                       "impuestos (ganancia de capital al realizar) y costos de los fondos.",
                       {"Volatilidad": PCT2, "Retorno bruto": PCT2, "Retorno neto": PCT2, "Sharpe": DEC2})
    r = 4 + len(df) + 1
    etiqueta(ws, f"A{r}", "Tracking error de la cartera contra el 50/50")
    ws[f"B{r}"], ws[f"B{r}"].number_format = mv["tracking_error"], PCT2
    r = tabla_simple(ws, r + 2, ["Con views (posterior de Black-Litterman)", "Nuestra cartera", "50/50 con nuestros activos"],
                     [["Retorno neto (impuestos y costos de fondos)", mv["con_views"]["cartera"], mv["con_views"]["benchmark"]]],
                     ["@", PCT2, PCT2])
    nombres_c = {"anio_2008_fijos": "Año 2008, pesos fijos", "anio_2008_rebalanceo": "Año 2008, con el rebalanceo de la política",
                 "maxima_caida_fijos": "Pico a valle oct-2007 a mar-2009, pesos fijos",
                 "maxima_caida_rebalanceo": "Pico a valle oct-2007 a mar-2009, con rebalanceo"}
    cap = ESCENARIOS[0].capital_inicial
    supuesto(ws, f"B{r}", cap, USD)
    etiqueta(ws, f"A{r}", "Capital del escenario A (USD)")
    filas = [[nombres_c[k], v["cartera"], v["benchmark"], None] for k, v in mv["caidas_2008"].items()]
    inicio = r + 2
    tabla_simple(ws, inicio, ["Crisis 2007-2009 (nominal, antes de impuestos, sin retiros)", "Nuestra cartera", "50/50",
                              "Diferencia en USD"], filas, ["@", PCT1, PCT1, USD])
    for i in range(inicio + 1, inicio + 1 + len(filas)):
        formula(ws, f"D{i}", f"=(B{i}-C{i})*$B${r}", USD)


def hoja_riesgo(wb, riesgo: dict, pesos: dict) -> None:
    activos = list(riesgo["aporte"])
    df = pd.DataFrame({"Activo": activos, "Peso": [pesos[a] for a in activos],
                       "Aporte a la vol": [riesgo["aporte"][a] for a in activos], "% del riesgo": None,
                       "Riesgo / peso": None})
    ws = escribir_hoja(wb, "Aporte al riesgo", df, "Aporte de cada posición a la volatilidad: w_i·(Σw)_i/σ_p, con la "
                       "covarianza de Ledoit-Wolf diaria. Los aportes suman la volatilidad de la cartera.",
                       {"Peso": PCT1, "Aporte a la vol": PCT2, "% del riesgo": PCT1, "Riesgo / peso": DEC2})
    ult = 3 + len(df)
    for i in range(4, ult + 1):
        formula(ws, f"D{i}", f"=C{i}/$C${ult + 1}", PCT1)
        formula(ws, f"E{i}", f"=IF(B{i}=0,0,D{i}/B{i})", DEC2)
    etiqueta(ws, f"A{ult + 1}", "Total (vol de la cartera)")
    formula(ws, f"B{ult + 1}", f"=SUM(B4:B{ult})", PCT1, True)
    formula(ws, f"C{ult + 1}", f"=SUM(C4:C{ult})", PCT2, True)
    r = ult + 3
    tabla_simple(ws, r, ["Dentro de las acciones", "Cartera", "Benchmark"],
                 [["EE.UU.", riesgo["regiones"]["acciones_eeuu"], riesgo["regiones_benchmark"]["acciones_eeuu"]],
                  ["Europa", riesgo["regiones"]["acciones_europa"], riesgo["regiones_benchmark"]["acciones_europa"]]],
                 ["@", PCT1, PCT1])


def hoja_monitoreo(wb, mon: dict) -> None:
    filas = []
    for e in mon["eventos"]:
        filas.append({"Fecha": e["fecha"], "Motivo": e["motivo"], "Clase más desviada": CLASE[e["clase_mas_desviada"]],
                      "Desvío": e["desvio"], "Rotación": e["rotacion"],
                      "Vende": ", ".join(f"{a} {x:.1%}" for a, x in e["vende"].items()),
                      "Compra": ", ".join(f"{a} {x:.1%}" for a, x in e["compra"].items())})
    df = pd.DataFrame(filas)
    ws = escribir_hoja(wb, "Monitoreo", df, "Backtest ilustrativo 2016-2026 de las reglas de la política: revisión "
                       f"mensual, banda de 3 puntos por clase, rango ± {mon['tolerancia_rango'] * 100:.0f} puntos, acción "
                       f"> {mon['tope_accion_disparo']:.0%}. Sin retiros ni impuestos; no es evidencia de performance. "
                       "Vende y compra: fracción de la cartera.",
                       {"Desvío": PCT1, "Rotación": PCT1}, {"Vende": 60, "Compra": 60, "Motivo": 34})
    r = 4 + len(df) + 1
    etiqueta(ws, f"A{r}", "Rotación anual promedio")
    formula(ws, f"B{r}", f"=SUM(E4:E{3 + len(df)})/{mon['anios']:.4f}", PCT1, True)
    etiqueta(ws, f"A{r + 1}", "Reglas sin tolerancia: rebalanceos / revisiones")
    ws[f"B{r + 1}"] = f"{mon['literal']['rebalanceos']} / {mon['literal']['revisiones']}"
    r += 3
    tabla_simple(ws, r, ["Clase", "Mayor desvío en una revisión"],
                 [[CLASE[c], x] for c, x in mon["desvio_max"].items()], ["@", PCT1])


def hoja_invertir(wb, alt: dict) -> None:
    filas = []
    for k in ("a_quieta", "b_letras", "d_cartera", "c_benchmark", "e_benchmark_comision"):
        v = alt[k]
        filas.append({"Alternativa": NOMBRE_ALT[k], "Sin plata en vida": v["ruina"],
                      "Edad mediana al quedarse sin plata": v["edad_mediana_ruina"], "Se acaba (caso central)": v.get("edad_central"),
                      "A los 60 (USD M de hoy)": v["patrimonio"]["real"]["60"] / 1e6,
                      "A los 75": v["patrimonio"]["real"]["75"] / 1e6, "A los 90": v["patrimonio"]["real"]["90"] / 1e6,
                      "A los 90 (USD M corrientes)": v["patrimonio"]["nominal"]["90"] / 1e6,
                      "El bono desaparece": v["bono_desaparece"], "Retorno real compuesto": v["retorno_real_compuesto"]})
    df = pd.DataFrame(filas)
    escribir_hoja(wb, "Invertir o no", df, "Escenario A (compra), nivel lujo, sueldo fijo + bono con barandas, mortalidad "
                  "de Gompertz, 10.000 escenarios. Mismos impuestos y Bienes Personales. Patrimonio mediano viva hasta "
                  "los 100. c no cumple la política (sin filtro ESG): es la vara.",
                  {"Sin plata en vida": PCT1, "El bono desaparece": PCT1, "Retorno real compuesto": PCT2,
                   "Edad mediana al quedarse sin plata": "0", "Se acaba (caso central)": "0"} |
                  {c: "0.0" for c in df.columns if c.startswith("A los")})


def hoja_impuestos(wb, imp: dict, real: dict) -> None:
    nombres = {"base": "Ley vigente", "bp_fijo": "Bienes Personales queda en 0,75%",
               "alicuotas_altas": "Intereses y dividendos 40%, ganancias 20%", "ambos": "Las dos cosas"}
    df = pd.DataFrame([{"Escenario impositivo": nombres[k], "Sin plata en vida (lujo, compra, con bono)": v["ruina_bono"],
                        "Retiro seguro con bono (USD/mes)": v["seguro_bono"]} for k, v in imp.items()])
    ws = escribir_hoja(wb, "Impuestos", df, "Sensibilidad a cambios de impuestos. El caso base sigue la ley vigente "
                       "(Bienes Personales baja a 0,25% desde 2027).",
                       {"Sin plata en vida (lujo, compra, con bono)": PCT1, "Retiro seguro con bono (USD/mes)": USD})
    r = 4 + len(df) + 2
    etiqueta(ws, f"A{r}", "Ganancia de capital al realizar: tasa efectiva = t·f(1+g)/(g+f)")
    etiqueta(ws, f"A{r + 1}", "Tasa sobre la ganancia realizada (t)", False)
    supuesto(ws, f"B{r + 1}", 0.15, PCT1)
    etiqueta(ws, f"A{r + 2}", "Fracción vendida por año, cartera (f)", False)
    supuesto(ws, f"B{r + 2}", real["cartera"], PCT1)
    etiqueta(ws, f"A{r + 3}", "  de la que: rebalanceo / retiros", False)
    ws[f"B{r + 3}"] = f"{real['rebalanceo_cartera']:.1%} / {real['retiros_cartera']:.1%}"
    etiqueta(ws, f"A{r + 4}", "Fracción vendida por año, 50/50", False)
    supuesto(ws, f"B{r + 4}", real["benchmark"], PCT1)
    g = a_aritmetico(RETORNO_LARGO_PLAZO["acciones_eeuu"], VOL_CLASES["acciones_eeuu"]) - 0.009
    etiqueta(ws, f"A{r + 5}", "Suba de precio esperada, ESGV (g = μ − dividendo)", False)
    supuesto(ws, f"B{r + 5}", g, PCT2)
    etiqueta(ws, f"A{r + 6}", "Tasa efectiva para ESGV en la cartera")
    formula(ws, f"B{r + 6}", f"=B{r + 1}*B{r + 2}*(1+B{r + 5})/(B{r + 5}+B{r + 2})", PCT2, True)
    etiqueta(ws, f"A{r + 7}", "Con f = 100% (todo se realiza cada año)", False)
    formula(ws, f"B{r + 7}", f"=B{r + 1}*1*(1+B{r + 5})/(B{r + 5}+1)", PCT2)


def hoja_costos(wb, gasto_fondos: float) -> None:
    df = pd.DataFrame({"Desde (USD)": [0, 2_000_000, 10_000_000], "Hasta (USD)": [2_000_000, 10_000_000, None],
                       "Tasa marginal": [0.01, 0.006, 0.004]})
    ws = escribir_hoja(wb, "Costos", df, "Costos para la clienta por año: comisión de gestión por tramos (sin "
                       "retrocesiones) y costos propios de los fondos (expense ratio ponderado por pesos).",
                       {"Desde (USD)": USD, "Hasta (USD)": USD, "Tasa marginal": PCT2})
    r = 9
    for j, t in enumerate(["Concepto", "A: compra", "B: alquila"], 1):
        c = ws.cell(row=r, column=j, value=t)
        c.font, c.fill = NEGRITA, ENCABEZADO
    etiqueta(ws, f"A{r + 1}", "Capital invertido (USD)", False)
    supuesto(ws, f"B{r + 1}", ESCENARIOS[0].capital_inicial, USD)
    supuesto(ws, f"C{r + 1}", ESCENARIOS[1].capital_inicial, USD)
    etiqueta(ws, f"A{r + 2}", "Costo de los fondos (% de la cartera)", False)
    supuesto(ws, f"B{r + 2}", gasto_fondos, "0.000%")
    formula(ws, f"C{r + 2}", f"=B{r + 2}", "0.000%")
    etiqueta(ws, f"A{r + 3}", "Comisión de gestión (USD)", False)
    etiqueta(ws, f"A{r + 4}", "Costos de los fondos (USD)", False)
    etiqueta(ws, f"A{r + 5}", "Total por año (USD)")
    etiqueta(ws, f"A{r + 6}", "Total (% del capital)")
    etiqueta(ws, f"A{r + 7}", "Total por mes (USD)", False)
    for col in ("B", "C"):
        k = f"{col}{r + 1}"
        formula(ws, f"{col}{r + 3}", f"=MIN({k},$B$5)*$C$4+MAX(0,MIN({k},$B$6)-$A$5)*$C$5+MAX(0,{k}-$A$6)*$C$6", USD)
        formula(ws, f"{col}{r + 4}", f"={k}*{col}{r + 2}", USD)
        formula(ws, f"{col}{r + 5}", f"={col}{r + 3}+{col}{r + 4}", USD, True)
        formula(ws, f"{col}{r + 6}", f"={col}{r + 5}/{k}", PCT2, True)
        formula(ws, f"{col}{r + 7}", f"={col}{r + 5}/12", USD)


def hoja_presupuestos(wb, pres: pd.DataFrame) -> None:
    df = pd.DataFrame({"Rubro": pres["rubro"], "USD por mes": pres["usd_mes"], "Escenario": pres["escenario"],
                       "Nivel": pres["nivel"], "Descripción y fuente": pres["fuente"]})
    ws = escribir_hoja(wb, "Presupuestos", df, "Gasto mensual en USD por rubro. Escenario: ambos, compra (A) o "
                       "alquila (B). Los totales son fórmulas. La simulación no incluye la línea de Bienes Personales "
                       "del departamento porque ese impuesto se simula aparte.", {"USD por mes": USD},
                       anchos={"Rubro": 55, "Descripción y fuente": 60})
    ult = 3 + len(df)
    for i in range(4, ult + 1):
        ws[f"B{i}"].font = AZUL
    r = ult + 3
    for j, t in enumerate(["Vivienda", "Nivel", "Total mensual (USD)", "Usado en la simulación (USD)"], 1):
        c = ws.cell(row=r, column=j, value=t)
        c.font, c.fill, c.border = NEGRITA, ENCABEZADO, LINEA
    rng = lambda col: f"${col}$4:${col}${ult}"
    k = r + 1
    for viv, clave in (("Compra (A)", "compra"), ("Alquila (B)", "alquila")):
        for nivel in ("base", "lujo", "alto"):
            ws[f"A{k}"], ws[f"B{k}"] = viv, nivel
            ws[f"A{k}"].font = ws[f"B{k}"].font = NORMAL
            total = (f'SUMIFS({rng("B")},{rng("D")},B{k},{rng("C")},"ambos")'
                     f'+SUMIFS({rng("B")},{rng("D")},B{k},{rng("C")},"{clave}")')
            formula(ws, f"C{k}", "=" + total, USD, True)
            formula(ws, f"D{k}", f'=C{k}-SUMIFS({rng("B")},{rng("D")},B{k},{rng("C")},"{clave}",'
                                 f'{rng("A")},"Bienes Personales*")', USD)
            k += 1


# --------------------------------------------------------------------- todo junto

def main() -> None:
    from tp import etapa4
    from tp.config import cargar_presupuesto

    ins = etapa4.insumos()
    base = etapa4.retornos(ins, ins.S_lw)
    w = etapa4.principal(ins, base, ins.S_lw)
    carteras, _, _ = etapa4.comparacion(ins, w)
    resumen = json.loads((SALIDAS / "resumen.json").read_text(encoding="utf-8"))
    car = resumen["cartera"]
    metricas = {k: etapa4.metricas(ins, x, base) | {"retorno_neto_completo": car["comparacion"][k]["retorno_neto_completo"]}
                for k, x in carteras.items()}
    f_real = car["realizacion"]["cartera"]
    filas_bl = []

    def fila(caso: str, x: pd.Series, m: dict, rot: float | None = None) -> dict:
        d = {"Caso": caso, **{CLASE[c]: float(v) for c, v in etapa4.por_clase(ins, x).items()},
             "Retorno neto": m["retorno_neto_completo"], "Volatilidad": m["vol"]}
        if rot is not None:
            d["Rotación contra la final"] = rot
        return d

    def completo(x, m, r):
        return m | {"retorno_neto_completo": float(x @ etapa4.neto_completo(ins, r, f_real))}

    for c in (0.25, 1.0, 5.0):
        x, m, r = etapa4.sensibilidad(ins, c=c)
        filas_bl.append(fila(f"Confianza c = {c:g}".replace(".", ","), x, completo(x, m, r)))
    for v in (0.07, 0.09, 0.11):
        x, m, r = etapa4.sensibilidad(ins, vol=v)
        filas_bl.append(fila(f"Volatilidad objetivo {v:.0%}", x, completo(x, m, r)))
    loo, rot = etapa4.leave_one_out(ins, w, f_real)
    for k, (x, m) in loo.items():
        filas_bl.append(fila(f"Sin la view {k.replace('sin ', '')}", x, m, rot[k]))
    sd = np.sqrt(np.diag(ins.S_lw.values))
    corr_activos = pd.DataFrame(ins.S_lw.values / np.outer(sd, sd), index=ins.activos, columns=ins.activos)

    wb = Workbook()
    wb.remove(wb.active)
    hoja_universo(wb, pd.read_csv(SALIDAS / "universo.csv", keep_default_na=False))
    hoja_excluidos(wb, pd.read_csv(SALIDAS / "excluidos.csv", keep_default_na=False))
    hoja_screening(wb, pd.read_csv(SALIDAS / "screening.csv"))
    hoja_benchmark(wb, ins.extra["guia"], ins.extra["caida_benchmark"])
    hoja_correlaciones(wb, ins.extra["ret_indices"][CLASES].corr(), corr_activos)
    hoja_retornos(wb)
    hoja_cartera(wb, pd.read_csv(SALIDAS / "cartera.csv"))
    hoja_comparacion(wb, carteras, metricas, ins)
    hoja_misma_vara(wb, car["misma_vara"])
    hoja_riesgo(wb, car["riesgo"], car["pesos"])
    hoja_monitoreo(wb, car["monitoreo"])
    hoja_sensibilidades(wb, filas_bl, resumen)
    hoja_montecarlo(wb, resumen)
    hoja_invertir(wb, resumen["retiro"]["alternativas"])
    hoja_impuestos(wb, resumen["retiro"]["impuestos"], resumen["retiro"]["realizacion"])
    hoja_costos(wb, resumen["retiro"]["gasto_fondos_cartera"])
    hoja_presupuestos(wb, cargar_presupuesto(DATA / "presupuesto.csv"))
    assert wb.sheetnames == HOJAS, wb.sheetnames
    wb.save(ARCHIVO)
    print(f"Planilla en {ARCHIVO} ({len(HOJAS)} hojas).")


if __name__ == "__main__":
    main()
