"""Etapa 4: Black-Litterman + optimización + comparaciones + sensibilidades.

Retornos esperados: totales anuales en USD = tasa corta de largo plazo (3,5%) + exceso.
π y μ son excesos sobre esa tasa (Meucci); las tablas muestran el total.
La vol reportada es siempre la de la Σ de Ledoit-Wolf con retornos diarios (×252).
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from tp.black_litterman import calibrar_lambda, equilibrio, posterior_mercado
from tp.config import (BENCHMARK, CLASES, CONFIANZA_C, DATA, ESCALA_VIEW, ESCENARIOS, PISOS_ACTIVO,
                       POSICION_MINIMA_ACCION, RAIZ, RANGOS, RETORNO_LARGO_PLAZO, Impuestos, Mercado)
from tp.equilibrio import cap_total_implicita, pesos_neutros
from tp.estadisticas import ledoit_wolf_cc
from tp import formato
from tp.hrp import hrp
from tp.impuestos import retorno_neto_activo
from tp.optimizacion import (TOPES, con_minimo, mas_cercana, minima_varianza, optimizar, restricciones_activas,
                             violaciones)
from tp.views import cargar_views, matriz_P, omega, validar, valores_v

RF = RETORNO_LARGO_PLAZO["liquidez"]
RENTA_FIJA = {"liquidez", "tesoro", "tips", "corporativos"}


@dataclass
class Insumos:
    activos: list[str]
    clase: list[str]
    tipo: list[str]
    nombre: dict
    S_lw: pd.DataFrame
    S_mensual: pd.DataFrame
    S_muestral: pd.DataFrame
    delta: float
    delta_mensual: float
    w_b: pd.Series
    caps: dict
    renta: pd.Series
    views: pd.DataFrame
    dias: int = 0
    meses: int = 0
    extra: dict = field(default_factory=dict)


def insumos() -> Insumos:
    from tp.correr import cargar_universo, etapa_datos, ventana_comun

    universo = cargar_universo()
    d = etapa_datos(universo, imprimir=False)
    sel = pd.read_csv(DATA / "seleccion.csv")
    act = sel["ticker"].tolist()
    X = d["ventana"][act].values
    S_lw, delta, _ = ledoit_wolf_cc(X, anualizar=252)
    Xm = ventana_comun(d["ret_mensuales"])[act].values
    S_m, delta_m, _ = ledoit_wolf_cc(Xm, anualizar=12)
    Y = X - X.mean(axis=0)
    S_s = Y.T @ Y / len(Y) * 252
    caps = pd.read_csv(DATA / "fundamentals.csv").set_index("ticker")["market_cap"].to_dict()
    top = pd.read_csv(DATA / "esgv_top.csv").set_index("ticker")["peso"].to_dict()
    w_b = pesos_neutros(sel, BENCHMARK, caps, cap_total_implicita(top, caps))[act]
    views = cargar_views(DATA / "views.csv")
    validar(views, act)
    df = lambda S: pd.DataFrame(S, index=act, columns=act)
    nombre = universo.set_index("ticker")["nombre"].to_dict()
    renta = pd.read_csv(DATA / "rendimientos.csv").set_index("ticker")["renta"][act]
    return Insumos(act, sel["clase"].tolist(), sel["tipo"].tolist(), nombre, df(S_lw), df(S_m), df(S_s),
                   delta, delta_m, w_b, caps, renta, views, dias=len(X), meses=len(Xm),
                   extra={"r2008": d["r2008"], "ret_indices": d["ret_indices"], "ventana": d["ventana"], "precios": d["precios"], "guia": d["guia"],
                          "caida_benchmark": d["caida_benchmark"]})


def retornos(ins: Insumos, S: pd.DataFrame, c: float = CONFIANZA_C, escala: float = ESCALA_VIEW,
             views: pd.DataFrame | None = None) -> dict:
    """λ, π, μ posterior, Σ_post y retornos totales y netos por activo para una Σ dada."""
    v = ins.views if views is None else views
    lam = calibrar_lambda(S.values, ins.w_b.values, Mercado.exceso_esperado_benchmark)
    pi = pd.Series(equilibrio(S.values, ins.w_b.values, lam), index=ins.activos)
    if c == 0 or v.empty:
        mu, Sp = pi.copy(), S.values
    else:
        P = matriz_P(v, ins.activos, ins.caps)
        q = valores_v(v, P, pi, S, escala)
        mu_a, Sp = posterior_mercado(pi.values, S.values, P.values, q.values, omega(P, S, v["u"].values, c))
        mu = pd.Series(mu_a, index=ins.activos)
    total = RF + mu
    imp = Impuestos()
    netos = [retorno_neto_activo(total[a], ins.renta[a], cl in RENTA_FIJA, imp) for a, cl in zip(ins.activos, ins.clase)]
    neto = pd.Series([n for n, _ in netos], index=ins.activos)
    tasa = pd.Series([t for _, t in netos], index=ins.activos)
    return dict(lam=lam, pi=pi, mu=mu, Sigma_post=pd.DataFrame(Sp, index=ins.activos, columns=ins.activos),
                total=total, neto=neto, tasa=tasa)


def pisos(ins: Insumos) -> dict[int, float]:
    return {ins.activos.index(t): p for t, p in PISOS_ACTIVO.items() if t in ins.activos}


def con_reglas(ins: Insumos, resolver, valor) -> tuple[pd.Series, list[str]]:
    """Aplica la posición mínima por acción. resolver(excluidos, pisos) arma la cartera con esos pisos
    (los de config más las acciones forzadas al mínimo); valor(w) es el objetivo a maximizar."""
    base = pisos(ins)
    w, fuera = con_minimo(lambda ex, fz: resolver(ex, {**base, **{i: POSICION_MINIMA_ACCION for i in fz}}),
                          ins.tipo, POSICION_MINIMA_ACCION, valor=valor)
    return pd.Series(w, index=ins.activos), [ins.activos[i] for i in fuera]


def cartera(ins: Insumos, r: dict, S: pd.DataFrame, vol: float = Mercado.vol_objetivo) -> tuple[pd.Series, list[str]]:
    """Máximo retorno neto s.a. vol, rangos, topes, piso de ESGV y mínimo de 2% por acción."""
    mu = r["neto"].values
    return con_reglas(ins, lambda ex, ps: optimizar(mu, S.values, ins.clase, ins.tipo, RANGOS, vol, pisos=ps,
                                                    excluidos=ex), valor=lambda w: mu @ w)


def principal(ins: Insumos, r: dict, S: pd.DataFrame, vol: float = Mercado.vol_objetivo) -> pd.Series:
    return cartera(ins, r, S, vol)[0]


def hrp_ajustado(ins: Insumos, w_crudo: pd.Series) -> tuple[pd.Series, list[str]]:
    obj = w_crudo.values
    return con_reglas(ins, lambda ex, ps: mas_cercana(obj, ins.clase, ins.tipo, RANGOS, pisos=ps, excluidos=ex),
                      valor=lambda w: -((w - obj) ** 2).sum())


def min_var(ins: Insumos) -> tuple[pd.Series, list[str]]:
    S = ins.S_lw.values
    return con_reglas(ins, lambda ex, ps: minima_varianza(S, ins.clase, ins.tipo, RANGOS, pisos=ps, excluidos=ex),
                      valor=lambda w: -w @ S @ w)


def neto_completo(ins: Insumos, r: dict, f: float) -> pd.Series:
    """Retorno neto por activo con el posterior de Black-Litterman, con todo descontado: impuestos (la
    ganancia de capital paga al vender, fracción f de las acciones por año) y gastos de los fondos. Es la
    misma base que alternativas.con_views. El optimizador sigue con el supuesto de la v2 (15% todos los
    años, sin gastos): con el de realizar, la cartera óptima rota 0,1% (se informa en la etapa 4)."""
    from tp.config import gastos_fondos
    from tp.montecarlo import tasas_impositivas
    rf = np.array([c in RENTA_FIJA for c in ins.clase])
    g = gastos_fondos()
    gasto = np.array([g[a] for a in ins.activos])
    t_r, k = tasas_impositivas(rf, ins.renta.values, Impuestos(), mu=r["total"].values, realizacion=f)
    return pd.Series((r["total"].values - gasto) * (1 - t_r) - k, index=ins.activos)


def metricas(ins: Insumos, w: pd.Series, r: dict) -> dict:
    S = ins.S_lw.values
    bruto, neto = float(w @ r["total"]), float(w @ r["neto"])
    vol = float(np.sqrt(w @ S @ w))
    a = w - ins.w_b
    return {"retorno_bruto": bruto, "retorno_neto": neto, "vol": vol,
            "vol_sigma_post": float(np.sqrt(w @ r["Sigma_post"].values @ w)),
            "sharpe": (bruto - RF) / vol, "tracking_error": float(np.sqrt(a @ S @ a)),
            "herfindahl": float((w ** 2).sum())}


def por_clase(ins: Insumos, w: pd.Series) -> pd.Series:
    return w.groupby(pd.Series(ins.clase, index=ins.activos)).sum().reindex(CLASES)


def controlar(ins: Insumos, w: pd.Series, nombre: str) -> None:
    v = violaciones(w.values, ins.clase, ins.tipo, RANGOS)
    v += [f"{t} debajo de su piso" for t, p in PISOS_ACTIVO.items() if t in w and w[t] < p - 1e-6]
    v += [f"{t} entre 0 y el mínimo" for t, x, tp in zip(ins.activos, w, ins.tipo)
          if tp == "accion" and 1e-6 < x < POSICION_MINIMA_ACCION - 1e-6]
    if v:
        raise AssertionError(f"{nombre} viola restricciones: {v}")


def comparacion(ins: Insumos, w: pd.Series) -> tuple[dict[str, pd.Series], pd.Series, tuple]:
    """Las 5 carteras de la comparación (mismas reglas), el HRP crudo y lo que salió por el mínimo en cada una."""
    eq = retornos(ins, ins.S_lw, c=0)
    w_eq, f_eq = cartera(ins, eq, ins.S_lw)
    w_hrp_crudo = pd.Series(hrp(ins.S_lw.values), index=ins.activos)
    w_hrp, f_hrp = hrp_ajustado(ins, w_hrp_crudo)
    w_mv, f_mv = min_var(ins)
    carteras = {"BL c=1 (final)": w, "Equilibrio (c→0)": w_eq, "HRP ajustado": w_hrp, "Mín. varianza": w_mv,
                "Neutro (50/50)": ins.w_b}
    for k, x in carteras.items():
        if k != "Neutro (50/50)":
            controlar(ins, x, k)
    return carteras, w_hrp_crudo, (f_eq, f_hrp, f_mv)


def sensibilidad(ins: Insumos, S: pd.DataFrame | None = None, c: float = CONFIANZA_C, escala: float = ESCALA_VIEW,
                 vol: float = Mercado.vol_objetivo, views: pd.DataFrame | None = None):
    """Cartera con las reglas para un caso. Devuelve (pesos, métricas, retornos) o (None, error, retornos)."""
    S = ins.S_lw if S is None else S
    r = retornos(ins, S, c=c, escala=escala, views=views)
    try:
        x, _ = cartera(ins, r, S, vol)
    except (ValueError, RuntimeError) as e:
        return None, str(e), r
    controlar(ins, x, "sensibilidad")
    return x, metricas(ins, x, r), r


def leave_one_out(ins: Insumos, w: pd.Series, f: float | None = None) -> tuple[dict, dict]:
    """Saca una view por vez: {etiqueta: (pesos, métricas)} y {etiqueta: rotación = ½·Σ|x − w|}.

    Con f (fracción de las acciones vendida por año), las métricas suman retorno_neto_completo: el neto
    con todo descontado (impuestos al realizar y gastos de fondos), con el posterior de ese caso."""
    filas, rot = {}, {}
    for i, vid in enumerate(ins.views["id"]):
        x, mm, r = sensibilidad(ins, views=ins.views.drop(index=i).reset_index(drop=True))
        if f is not None and x is not None:
            mm = mm | {"retorno_neto_completo": float(x @ neto_completo(ins, r, f))}
        filas[f"sin {vid}"] = (x, mm)
        rot[f"sin {vid}"] = 0.5 * float(np.abs(x - w).sum()) if x is not None else np.nan
    return filas, rot


# --------------------------------------------------------------------- impresión

def pct(x, d=1):
    return "" if pd.isna(x) else formato.pct(x, d).replace("−", "-")


def titulo(t: str) -> None:
    print(f"\n{'=' * 100}\n{t}\n{'=' * 100}")


def tabla_clases(ins, filas: dict[str, tuple[pd.Series, dict]]) -> str:
    """filas: etiqueta → (pesos, métricas). Pesos por clase + vol + retorno neto."""
    d = {}
    for k, (w, m) in filas.items():
        if w is None:
            d[k] = {"nota": m}
            continue
        d[k] = {**{c: pct(x) for c, x in por_clase(ins, w).items()}, "vol": pct(m["vol"], 2),
                "ret. neto": pct(m["retorno_neto"], 2), "ret. bruto": pct(m["retorno_bruto"], 2)}
    return pd.DataFrame(d).T.fillna("").to_string()


def main(completo: bool = False) -> dict:
    """completo=True agrega las sensibilidades del primer checkpoint 4 (escala, Σ mensual/muestral, piso de ESGV)."""
    ins = insumos()
    base = retornos(ins, ins.S_lw)
    w, fuera = cartera(ins, base, ins.S_lw)
    controlar(ins, w, "principal")
    m = metricas(ins, w, base)
    from tp.alternativas import realizaciones
    from tp.etapa5 import casos
    real = realizaciones(ins, w.values, next(c for c in casos() if c.etiqueta == "A lujo"))
    neto_r = neto_completo(ins, base, real["cartera"])
    m["retorno_neto_completo"] = float(w @ neto_r)
    sd = np.sqrt(np.diag(ins.S_lw.values))
    a, b = ESCENARIOS

    titulo("ETAPA 4: BLACK-LITTERMAN (Meucci 2010, formulación de mercado) Y OPTIMIZACIÓN")
    print(f"Σ: Ledoit-Wolf (correlación constante) sobre los 14 activos, retornos diarios, {ins.dias} días, "
          f"δ = {ins.delta:.4f}. Mensual: {ins.meses} meses, δ = {ins.delta_mensual:.4f}.")
    print(f"λ = {base['lam']:.2f} (w_b'π = {Mercado.exceso_esperado_benchmark:.2%} sobre la tasa corta de largo plazo "
          f"{RF:.1%}). Views: {len(ins.views)}, escala {ESCALA_VIEW}σ por unidad de η, c = {CONFIANZA_C}.")
    print("Ajustes del checkpoint 4 (16/11): piso ESGV " + ", ".join(f"{t} ≥ {p:.0%}" for t, p in PISOS_ACTIVO.items())
          + f"; liquidez {RANGOS['liquidez'][0]:.0%}-{RANGOS['liquidez'][1]:.0%} (benchmark {BENCHMARK['liquidez']:.0%}); "
          f"acción individual 0 o ≥ {POSICION_MINIMA_ACCION:.0%} (iterativo).")

    titulo("1. POR ACTIVO: neutro, equilibrio, posterior e impuestos (retornos totales anuales en USD)")
    t = pd.DataFrame({
        "clase": ins.clase, "w_b": ins.w_b.map(pct), "π": (RF + base["pi"]).map(pct),
        "μ post": base["total"].map(pct), "μ−π": (base["mu"] - base["pi"]).map(lambda x: pct(x, 2)),
        "vol": pd.Series(sd, index=ins.activos).map(pct), "renta": ins.renta.map(pct),
        "tasa ef.": base["tasa"].map(pct), "μ neto": base["neto"].map(pct),
    }, index=ins.activos)
    print(t.to_string())
    print("Impuestos: renta fija (incluye TIPS) → todo el retorno es interés, 35%. Acciones → dividendo al 35% "
          "(máx. entre retención de EE.UU. 30% y Argentina 35%) y el resto ganancia de capital al 15%, "
          "devengada cada año (conservador). Renta = rendimiento de distribución / dividendo de Yahoo, 15/11/2026.")

    titulo("2. CARTERA FINAL: máx. retorno neto s.a. vol ≤ 9% (Σ LW diaria), rangos IPS, 5% acción, 30% fondo, "
           "piso ESGV, mínimo 2% por acción")
    tw = pd.DataFrame({"clase": ins.clase, "tipo": ins.tipo, "peso": w.map(pct), "neutro": ins.w_b.map(pct),
                       "activo−neutro": (w - ins.w_b).map(pct),
                       "USD A (compra)": (w * a.capital_inicial).map("{:,.0f}".format),
                       "USD B (alquila)": (w * b.capital_inicial).map("{:,.0f}".format)}, index=ins.activos)
    print(tw.to_string())
    pc = pd.DataFrame({"peso": por_clase(ins, w).map(pct), "benchmark": pd.Series(BENCHMARK).map(pct),
                       "rango": pd.Series({c: f"{lo:.0%}-{hi:.0%}" for c, (lo, hi) in RANGOS.items()}),
                       "USD A": (por_clase(ins, w) * a.capital_inicial).map("{:,.0f}".format),
                       "USD B": (por_clase(ins, w) * b.capital_inicial).map("{:,.0f}".format)})
    print("\n" + pc.to_string())
    print(f"\nPosiciones: {int((w > 1e-6).sum())}. Quedaron en 0 por el mínimo de 2% (iteración + reingreso): {', '.join(fuera) or 'ninguna'}.")
    print(f"Ganancia de capital al realizar (fracción vendida por año: cartera {pct(real['cartera'])}, 50/50 "
          f"{pct(real['benchmark'])}): neto con todo descontado (impuestos y gastos de fondos) {pct(m['retorno_neto_completo'], 2)} con los mismos pesos. "
          "El optimizador usa 15% todos los años; con el supuesto de realizar, la óptima rota 0,1% (NVDA +0,1, V −0,1).")
    print(f"Retorno esperado bruto {pct(m['retorno_bruto'], 2)} | neto {pct(m['retorno_neto'], 2)} | "
          f"vol {pct(m['vol'], 2)} | vol con Σ_post (informativa) {pct(m['vol_sigma_post'], 2)} | "
          f"Sharpe {m['sharpe']:.2f}".replace(".", ",") + f" | tracking error vs. neutro {pct(m['tracking_error'], 2)}")
    act = restricciones_activas(w.values, ins.S_lw.values, ins.clase, ins.tipo, RANGOS, Mercado.vol_objetivo,
                                nombres=ins.activos)
    act += [f"piso {t} ({p:.0%})" for t, p in PISOS_ACTIVO.items() if abs(w[t] - p) < 1e-4]
    act += [f"{t} fijada en 0 por el mínimo" for t in fuera]
    print("Restricciones activas: " + "; ".join(act))
    print(f"Capital: A USD {a.capital_inicial:,.0f} (14 M menos gastos de compra del depto); B USD {b.capital_inicial:,.0f}.")

    titulo("3. COMPARACIÓN (mismas restricciones: rangos, topes, piso ESGV y mínimo por acción)")
    carteras, w_hrp_crudo, (f_eq, f_hrp, f_mv) = comparacion(ins, w)
    comp = pd.DataFrame({k: x.map(pct) for k, x in carteras.items()})
    comp.insert(0, "HRP crudo", w_hrp_crudo.map(pct))
    print(comp.to_string())
    # El 50/50 con nuestros activos rota como el 50/50 (su propia realización); el resto, como la cartera.
    neto_b = neto_completo(ins, base, real["benchmark"])
    ms = {k: metricas(ins, x, base) | {"retorno_neto_completo": float(x @ (neto_b if k == "Neutro (50/50)" else neto_r))}
          for k, x in carteras.items()}
    mt = pd.DataFrame({k: {"ret. bruto": pct(v["retorno_bruto"], 2), "ret. neto": pct(v["retorno_neto"], 2),
                           "vol (Σ LW)": pct(v["vol"], 2), "Sharpe": f"{v['sharpe']:.2f}".replace(".", ","),
                           "TE vs neutro": pct(v["tracking_error"], 2),
                           "Herfindahl": f"{v['herfindahl']:.3f}".replace(".", ","),
                           "posiciones": str(int((carteras[k] > 1e-6).sum()))}
                       for k, v in ms.items()})
    print("\n" + mt.to_string())
    print("Métricas de las 5 carteras evaluadas con los retornos del posterior BL (c=1). El neutro pone ASML en 6,1% "
          "(no cumple el tope; es solo la referencia). Salieron por el mínimo: "
          f"equilibrio {', '.join(f_eq) or '-'}; HRP {', '.join(f_hrp) or '-'}; mín. varianza {', '.join(f_mv) or '-'}.")
    print("\nPor clase:\n" + pd.DataFrame({k: por_clase(ins, x).map(pct) for k, x in carteras.items()}).to_string())

    titulo("4. SENSIBILIDADES (con los ajustes; pesos por clase, vol con Σ LW diaria, retorno neto con el posterior "
           "de cada caso)")

    caso = lambda **kw: sensibilidad(ins, **kw)

    def con_activos(filas: dict) -> str:
        return pd.DataFrame({k: v[0].map(pct) for k, v in filas.items() if v[0] is not None}).to_string()

    print("\n4a. Confianza global c")
    filas = {f"c = {c}": caso(c=c)[:2] for c in (0.25, 1, 5)}
    print(tabla_clases(ins, filas).replace(".", ",").replace("ret, ", "ret. "))
    print("Por activo:\n" + con_activos(filas))
    print("\n4b. Vol objetivo")
    filas = {f"vol ≤ {v:.0%}": caso(vol=v)[:2] for v in (0.07, 0.09, 0.11)}
    print(tabla_clases(ins, filas))
    print("Por activo:\n" + con_activos(filas))
    print("\n4c. Leave-one-out: sacando una view por vez (rotación = ½·Σ|w − w_final|)")
    filas, rot = leave_one_out(ins, w)
    print(tabla_clases(ins, filas))
    print("Rotación contra la final: " + ", ".join(f"{k} {pct(v)}" for k, v in
                                                     sorted(rot.items(), key=lambda kv: -kv[1])))
    detalle = pd.DataFrame({k: v[0].map(pct) for k, v in filas.items() if v[0] is not None})
    detalle.insert(0, "final", w.map(pct))
    print("\nPesos por activo en el leave-one-out:\n" + detalle.to_string())

    if completo:
        print("\n4d. Escala de las views (alcista / muy alcista, en desvíos de la view)")
        print(tabla_clases(ins, {f"{e:.2f} / {2 * e:.2f}": caso(escala=e)[:2] for e in (0.15, 0.25, 0.35)}))
        print("\n4e. Σ: LW diaria / LW mensual / muestral diaria (la vol de la tabla es con Σ LW diaria)")
        print(tabla_clases(ins, {k: caso(S=S)[:2] for k, S in {"LW diaria": ins.S_lw, "LW mensual": ins.S_mensual,
                                                                "Muestral diaria": ins.S_muestral}.items()}))

    titulo("5. CONTROLES")
    print("Topes, rangos, piso de ESGV y mínimo por acción: todas las carteras optimizadas de las secciones 2 a 4 "
          "pasan `controlar` (si alguna fallara, la etapa se corta).")
    print(f"Vol de la final con Σ LW diaria: {pct(m['vol'], 2)} ≤ {pct(Mercado.vol_objetivo)}.")
    lim0 = retornos(ins, ins.S_lw, c=1e-10)
    print(f"c → 0: máx |μ − π| = {np.abs(lim0['mu'] - lim0['pi']).max():.1e}.")
    P = matriz_P(ins.views, ins.activos, ins.caps)
    q = valores_v(ins.views, P, base["pi"], ins.S_lw, ESCALA_VIEW)
    liminf = retornos(ins, ins.S_lw, c=1e10)
    print(f"c → ∞: máx |Pμ − v| = {np.abs(P.values @ liminf['mu'].values - q.values).max():.1e}.")
    print("Los mismos límites están en tests/test_black_litterman.py.")

    riesgo_out = imprimir_riesgo(ins, w)
    monitoreo_out = imprimir_monitoreo(ins, w)
    vara_out = imprimir_misma_vara(ins, w)

    out = pd.DataFrame({"clase": ins.clase, "ticker": ins.activos, "nombre": [ins.nombre[t] for t in ins.activos],
                        "tipo": ins.tipo, "peso": w.round(4).values,
                        "usd_compra": (w * a.capital_inicial).round(0).values,
                        "usd_alquila": (w * b.capital_inicial).round(0).values})
    (RAIZ / "outputs").mkdir(exist_ok=True)
    out.to_csv(RAIZ / "outputs" / "cartera.csv", index=False)
    print(f"\nCartera guardada en outputs/cartera.csv (A: USD {a.capital_inicial:,.0f}; B: USD {b.capital_inicial:,.0f}).")
    return {"pesos": {t: round(float(x), 4) for t, x in w.items()},
            "pesos_por_clase": {c: round(float(x), 4) for c, x in por_clase(ins, w).items()},
            "posiciones": int((w > 1e-6).sum()),
            **{k: round(v, 4) for k, v in m.items() if k != "herfindahl"},
            "realizacion": real,
            "comparacion": {k: {"retorno_neto": round(v["retorno_neto"], 4), "vol": round(v["vol"], 4),
                                "retorno_neto_completo": round(v["retorno_neto_completo"], 4),
                                "sharpe": round(v["sharpe"], 3)} for k, v in ms.items()},
            "benchmark_historico": benchmark_historico(ins), "riesgo": riesgo_out,
            "monitoreo": monitoreo_out, "misma_vara": vara_out}


def imprimir_misma_vara(ins: Insumos, w: pd.Series) -> dict:
    """Cartera contra el 50/50 de índices con la misma Σ, ventana, retornos de largo plazo e impuestos."""
    from tp.alternativas import misma_vara, realizaciones
    from tp.etapa5 import casos
    real = realizaciones(ins, w.values, next(c for c in casos() if c.etiqueta == "A lujo"))
    r = misma_vara(ins, w.values, RF, real)
    r["realizacion"] = real
    titulo("8. CARTERA CONTRA EL 50/50 CON LA MISMA VARA (Σ LW diaria conjunta 14 + 6 índices, "
           f"{r['desde']} a {r['hasta']}, retornos de largo plazo por clase, impuestos y gastos de fondos)")
    nombres = {"cartera": "Nuestra cartera", "benchmark_indices": "50/50 (seis índices)",
               "neutra_14": "Neutra (50/50 con los 14 activos)", "neutra_europa_vgk": "Neutra con Europa en VGK",
               "neutra_europa_vgk_eeuu_spy": "Neutra con Europa en VGK y EE.UU. en SPY"}
    print(pd.DataFrame({nombres[k]: {"vol": pct(v["vol"], 2), "bruto": pct(v["bruto"], 2), "neto": pct(v["neto"], 2),
                                     "Sharpe": f"{v['sharpe']:.2f}".replace(".", ",")}
                        for k, v in r.items() if k in nombres}).T.to_string())
    print(f"Tracking error de la cartera contra el 50/50 de índices: {pct(r['tracking_error'], 2)}. δ = {r['delta']:.3f}, "
          f"{r['dias']} días. El 10,7% de la v2 era la cartera neutra: Europa en tres acciones (ASML 6,1%) y EE.UU. "
          "en ESGV más acciones; el benchmark de la política son los seis índices.")
    from tp.alternativas import caida_2008, con_views
    c08 = caida_2008(ins, w.values)
    cv = con_views(ins, w.values, retornos(ins, ins.S_lw)["total"], real)
    print(f"2008 (nominal, antes de impuestos, pesos fijos todo el año; cada posición con su retorno si cotizó todo "
          f"2008, si no el de su clase): cartera {pct(c08['cartera'])} (solo por clase {pct(c08['cartera_por_clase'])}), "
          f"50/50 {pct(c08['benchmark'])}. Con clase: " + ", ".join(a for a, f in c08["fuente"].items() if f == "clase") + ".")
    print(f"Con views (posterior de Black-Litterman, gastos de fondos; el 50/50 armado con los 14 activos): cartera "
          f"{pct(cv['cartera'], 2)}, 50/50 {pct(cv['benchmark'], 2)}. Sin views (arriba): {pct(r['cartera']['neto'], 2)} "
          f"y {pct(r['benchmark_indices']['neto'], 2)}.")
    r["caida_2008"] = c08
    from tp.alternativas import caidas_2008
    r["caidas_2008"] = caidas_2008(ins, w.values)
    print("Crisis (misma regla para los dos; nominal, antes de impuestos, sin retiros): " + "; ".join(
        f"{k} cartera {pct(v['cartera'])} y 50/50 {pct(v['benchmark'])}" for k, v in r["caidas_2008"].items()) + ".")
    r["con_views"] = cv
    return r


# M5: tolerancias para disparar el rebalanceo (propuesta a la política; el recorte vuelve al objetivo).
TOLERANCIA_RANGO = 0.02
TOPE_ACCION_DISPARO = 0.07


def imprimir_monitoreo(ins: Insumos, w: pd.Series) -> dict:
    """M5: backtest ilustrativo de las reglas de rebalanceo con los retornos diarios de la ventana.

    Dos versiones: las reglas literales de la política (la cartera óptima está en el borde de varios
    rangos y en el tope de 5% de dos acciones, así que casi cualquier movimiento dispara) y la propuesta
    con tolerancias para disparar (rango ± 2 puntos, acción > 7%), que se recorta igual al objetivo.
    """
    from tp.monitoreo import backtest, rendimiento_posterior
    r = ins.extra["ventana"][ins.activos]
    clase = dict(zip(ins.activos, ins.clase))
    tipo = dict(zip(ins.activos, ins.tipo))
    literal = backtest(r, w, clase, banda=0.03, rangos=RANGOS, tope_accion=0.05, tipo=tipo)
    holgura = {c: (lo - TOLERANCIA_RANGO, hi + TOLERANCIA_RANGO) for c, (lo, hi) in RANGOS.items()}
    mon = backtest(r, w, clase, banda=0.03, rangos=holgura, tope_accion=TOPE_ACCION_DISPARO, tipo=tipo)
    titulo(f"7. MONITOREO Y REBALANCEO CON HISTORIA ({r.index[0]:%d/%m/%Y} a {r.index[-1]:%d/%m/%Y}; ilustrativo)")
    print("Revisión el último día hábil de cada mes; si una regla se activa, se vuelve a los pesos objetivo. "
          "Sin retiros ni impuestos. No es evidencia de performance.")
    print(f"Reglas literales (banda 3 puntos, rangos, tope 5%): {len(literal.eventos)} rebalanceos en "
          f"{literal.revisiones} revisiones, rotación {pct(literal.rotacion_anual)} por año. La cartera está en el "
          "borde de cuatro rangos (liquidez 10%, TIPS 20%, corporativos 5%, Europa 10%) y LLY y NVS en el tope de 5%: "
          "cualquier movimiento dispara.")
    print(f"Propuesta (banda 3 puntos; rango ± {TOLERANCIA_RANGO * 100:.0f} puntos; acción > "
          f"{TOPE_ACCION_DISPARO:.0%}): {len(mon.eventos)} rebalanceos, rotación {pct(mon.rotacion_anual)} por año.")
    print("\n" + pd.DataFrame([{"fecha": f"{e['fecha']:%d/%m/%Y}", "motivo": e["motivo"],
                                "clase más desviada": e["clase_mas_desviada"], "desvío": pct(e["desvio"]),
                                "rotación": pct(e["rotacion"])} for e in mon.eventos]).to_string(index=False))
    print("\nMayor desvío de cada clase en una revisión: " + ", ".join(f"{c} {pct(d)}" for c, d in mon.desvio_max.items()))
    a = ESCENARIOS[0].capital_inicial
    ejemplos = {}
    if mon.eventos:
        ejemplos["primero"] = mon.eventos[0]
        caida = [e for e in mon.eventos if e["pesos_clase"]["acciones_eeuu"] + e["pesos_clase"]["acciones_europa"]
                 < sum(por_clase(ins, w)[["acciones_eeuu", "acciones_europa"]])]
        if caida:
            ejemplos["compra_tras_caida"] = caida[0]
    obj = por_clase(ins, w)
    for nombre, e in ejemplos.items():
        capital = a * e["valor"]
        print(f"\nEjemplo «{nombre}» ({e['fecha']:%d/%m/%Y}, {e['motivo']}). Con los USD {a:,.0f} de A, la cartera "
              f"valía ese día USD {capital:,.0f} (sin retiros).")
        print(pd.DataFrame({"peso": pd.Series(e["pesos_clase"]).map(pct), "objetivo": obj.map(pct)}).to_string())
        print("Vende: " + ", ".join(f"{x} {pct(v)} (USD {v * capital:,.0f})" for x, v in e["vende"].items()))
        print("Compra: " + ", ".join(f"{x} {pct(v)} (USD {v * capital:,.0f})" for x, v in e["compra"].items()))
        e["compra_12m"] = rendimiento_posterior(r, e["compra"], e["fecha"])
        e["vende_12m"] = rendimiento_posterior(r, e["vende"], e["fecha"])
        print(f"12 meses después: lo comprado rindió {pct(e['compra_12m'])} y lo vendido {pct(e['vende_12m'])}.")
    fmt = lambda e: {**e, "fecha": f"{e['fecha']:%Y-%m-%d}", "capital_usd": a * e["valor"]}
    return {"literal": {"rebalanceos": len(literal.eventos), "revisiones": literal.revisiones,
                        "rotacion_anual": literal.rotacion_anual},
            "tolerancia_rango": TOLERANCIA_RANGO, "tope_accion_disparo": TOPE_ACCION_DISPARO,
            "revisiones": mon.revisiones, "rebalanceos": len(mon.eventos), "anios": mon.anios,
            "rotacion_anual": mon.rotacion_anual, "desvio_max": mon.desvio_max,
            "eventos": [fmt(e) for e in mon.eventos], "ejemplos": {k: fmt(e) for k, e in ejemplos.items()}}

def imprimir_riesgo(ins: Insumos, w: pd.Series) -> dict:
    """M4: aporte de cada posición a la vol (Σ LW diaria) y peso de cada región dentro de las acciones."""
    from tp.riesgo import aporte_al_riesgo, regiones_en_acciones
    titulo("6. APORTE DE CADA POSICIÓN AL RIESGO (w_i·(Σw)_i/σ_p, Σ LW diaria)")
    ap = pd.Series(aporte_al_riesgo(w.values, ins.S_lw.values), index=ins.activos)
    vol = float(ap.sum())
    activos = w[w > 1e-6].index
    tabla = pd.DataFrame({"clase": pd.Series(dict(zip(ins.activos, ins.clase)))[activos], "peso": w[activos].map(pct),
                          "aporte (pp de vol)": (ap[activos] * 100).map(lambda x: f"{x:.2f}".replace(".", ",")),
                          "% del riesgo": (ap[activos] / vol).map(pct),
                          "riesgo / peso": (ap[activos] / vol / w[activos]).map(lambda x: f"{x:.2f}".replace(".", ","))})
    print(tabla.sort_values("% del riesgo", key=lambda s: s.str.replace(",", ".").str.rstrip("%").astype(float),
                            ascending=False).to_string())
    clase = dict(zip(ins.activos, ins.clase))
    acciones = [a for a in activos if ins.tipo[ins.activos.index(a)] == "accion"]
    mayor = max(acciones, key=lambda a: ap[a])
    reg = regiones_en_acciones(w, clase)
    reg_b = {r: BENCHMARK[r] / (BENCHMARK["acciones_eeuu"] + BENCHMARK["acciones_europa"])
             for r in ("acciones_eeuu", "acciones_europa")}
    print(f"\nVol total {pct(vol, 2)}. Acción que más riesgo aporta: {mayor} ({pct(ap[mayor] / vol)} del riesgo con "
          f"{pct(w[mayor])} del peso).")
    print(f"Dentro de las acciones: EE.UU. {pct(reg['acciones_eeuu'])} y Europa {pct(reg['acciones_europa'])} "
          f"(benchmark {pct(reg_b['acciones_eeuu'])} y {pct(reg_b['acciones_europa'])}).")
    return {"vol": vol, "aporte": {a: float(ap[a]) for a in activos},
            "pct": {a: float(ap[a] / vol) for a in activos}, "mayor_accion": mayor,
            "regiones": reg, "regiones_benchmark": reg_b}


def benchmark_historico(ins: Insumos) -> dict:
    """Números de la etapa 2 del benchmark 50/50 (índices de referencia, retornos diarios)."""
    g = ins.extra["guia"].loc["benchmark"]
    r = ins.extra["ret_indices"]
    valor = float((1 + sum(w * r[c] for c, w in BENCHMARK.items())).prod() * 100)
    caida, pico, valle = ins.extra["caida_benchmark"]
    return {"desde": f"{r.index[0]:%m/%Y}", "hasta": f"{r.index[-1]:%m/%Y}", "retorno_anual": float(g["retorno_anual"]),
            "desvio_anual": float(g["desvio_anual"]), "desvio_diario": float(g["desvio_diario"]),
            "sharpe": float(g["sharpe"]), "peor_caida": float(caida), "pico": f"{pico:%m/%Y}", "valle": f"{valle:%m/%Y}",
            "valor_100": valor}


if __name__ == "__main__":
    main()
