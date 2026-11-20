"""Etapa 5: Monte Carlo de 2 viviendas × 3 niveles de gasto, estrés 2008 y sensibilidades.

- Retornos: lognormal multivariada por activo. Media = retorno de largo plazo de su clase
  (EIC 3a, compuesto → aritmético con la vol de la clase); no el posterior de Black-Litterman.
  Covarianza = Σ de Ledoit-Wolf diaria anualizada de los 14 activos.
- Todo en USD reales (inflación de largo plazo 2,25%); impuestos sobre el retorno nominal
  de cada activo como en la etapa 4.
- Cartera final de la etapa 4, rebalanceada cada año.
- Gastos de los fondos (expense ratio) descontados del retorno de cada fondo antes de impuestos.
- 10.000 caminos con semilla fija. Las mismas normales y las mismas vidas para los 6
  escenarios, el estrés y las sensibilidades.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from tp import etapa4
from tp.comisiones import comision_anual
from tp.config import (ESCENARIOS, NIVELES, RAIZ, RETORNO_LARGO_PLAZO, Impuestos, Mercado, Simulacion,
                       cargar_presupuesto, gasto_mensual, gastos_fondos)
from tp.escenario import VOL_CLASES, a_aritmetico
from tp.impuestos import tasa_bp
from tp.montecarlo import (RetornoCartera, compuesto_esperado, costos_anuales, normales, retiro_maximo_seguro,
                           retorno_cartera, retornos_lognormales, simular, tasas_impositivas)
from tp.mortalidad import esperanza_de_vida, muestrear_anios_de_vida, supervivencia

SIM = Simulacion()
INF = Mercado.inflacion_largo_plazo
EDADES = (65, 85, 95)
RENTA_FIJA = etapa4.RENTA_FIJA


def mu_por_activo(clase: list[str], desplazamiento: float = 0.0) -> np.ndarray:
    """Media aritmética nominal de cada activo: la de su clase (compuesto + desplazamiento → aritmético)."""
    return np.array([a_aritmetico(RETORNO_LARGO_PLAZO[c] + desplazamiento, VOL_CLASES[c]) for c in clase])


def gasto_simulado(presupuesto: pd.DataFrame, clave: str, nivel: str) -> float:
    """Gasto mensual sin la línea de Bienes Personales del depto: BP se simula aparte, sobre cartera y depto."""
    p = presupuesto[~presupuesto["rubro"].str.startswith("Bienes Personales")]
    return gasto_mensual(p, clave, nivel)


@dataclass
class Caso:
    """Un escenario de vivienda y nivel de gasto."""
    vivienda: str
    nivel: str
    capital: float
    valor_casa: float
    gasto_mes: float
    piso_mes: float  # gasto base de la vivienda: las barandas no recortan debajo de esto

    @property
    def etiqueta(self) -> str:
        return f"{self.vivienda[0]} {self.nivel}"


class Motor:
    """Retornos simulados una sola vez; cada escenario los reusa.

    ins: cualquier objeto con activos, clase, renta y S_lw (los insumos de la etapa 4 o el
    benchmark pasivo). gasto: gasto anual de cada activo; por default, el de data/gastos_fondos.csv.
    imp: alícuotas (la sensibilidad impositiva usa otras).
    """

    def __init__(self, ins, n: int = SIM.n, semilla: int = SIM.semilla, gasto: np.ndarray | None = None,
                 imp: Impuestos = Impuestos(), realizacion: float | None = None):
        self.ins = ins
        g = gastos_fondos()
        self.gasto = np.array([g[a] for a in ins.activos]) if gasto is None else np.asarray(gasto, float)
        self.T = SIM.anios_max
        rng = np.random.default_rng(semilla)
        self.Z = normales(n, self.T, len(ins.activos), rng)
        # Las vidas salen de un generador aparte: no cambian si cambia la cantidad de activos.
        vidas = muestrear_anios_de_vida(SIM.edad, SIM.gompertz_m, SIM.gompertz_b, n,
                                        np.random.default_rng(semilla + 1))
        self.vidas = np.minimum(vidas, self.T)
        # realizacion: fracción de las acciones que se vende por año (la ganancia de capital paga al vender).
        # None: paga 15% todos los años (supuesto conservador de la v2).
        self.realizacion = realizacion
        self.t_r, self.k = tasas_impositivas(np.array([c in RENTA_FIJA for c in ins.clase]), ins.renta.values,
                                             imp, mu=mu_por_activo(ins.clase), realizacion=realizacion)
        self.S = ins.S_lw.values
        self._R: dict[float, np.ndarray] = {}

    def R(self, desplazamiento: float = 0.0) -> np.ndarray:
        if desplazamiento not in self._R:
            self._R[desplazamiento] = retornos_lognormales(self.Z, mu_por_activo(self.ins.clase, desplazamiento),
                                                           self.S)
        return self._R[desplazamiento]

    def rp(self, w: np.ndarray, desplazamiento: float = 0.0, shock: np.ndarray | None = None) -> RetornoCartera:
        """Retorno de la cartera después de impuestos. shock: retornos nominales del primer año por activo."""
        r = retorno_cartera(self.R(desplazamiento), w, self.t_r, self.k, INF, self.gasto)
        if shock is not None:
            r0 = retorno_cartera(shock[None, None, :], w, self.t_r, self.k, INF, self.gasto)
            r.real[:, 0], r.nominal[:, 0] = r0.real[0, 0], r0.nominal[0, 0]
        return r

    def costos(self, caso: Caso, comision=None, bp=tasa_bp):
        """Costos anuales del caso: comisión (por default, la de tramos) y Bienes Personales (bp por año)."""
        comision = comision_anual if comision is None else comision
        casa = caso.valor_casa
        return lambda v, t: costos_anuales(v, t, SIM.anio_inicio,
                                           lambda t: casa * (1 + SIM.valorizacion_real_casa) ** t, bp, comision)

    def correr(self, caso: Caso, rp: RetornoCartera, barandas: bool, vidas=None, retiro_mes: float | None = None,
               comision=None, bp=tasa_bp):
        """comision: función del valor (None = tramos; cero para las alternativas sin asesor). bp: alícuota por año."""
        costos = self.costos(caso, comision, bp)
        retiro = 12 * (caso.gasto_mes if retiro_mes is None else retiro_mes)
        return simular(caso.capital, retiro, rp.real, rp.nominal, self.vidas if vidas is None else vidas, costos,
                       con_barandas=barandas, inflacion=INF, baranda=SIM.baranda, ajuste=SIM.ajuste,
                       piso=12 * caso.piso_mes)

    def horizonte(self, edad: int) -> np.ndarray:
        return np.full(len(self.vidas), float(edad - SIM.edad))

    def retiro_seguro(self, caso: Caso, rp: RetornoCartera, barandas: bool, **kw) -> float:
        """Retiro mensual más alto con ruina ≤ 5% (mortalidad de Gompertz). kw: comision, bp."""
        f = lambda m: self.correr(caso, rp, barandas, retiro_mes=m, **kw).prob_ruina
        return retiro_maximo_seguro(f, SIM.prob_ruina_max, lo=0.0, hi=0.08 * caso.capital / 12, tol=25.0)


def casos() -> list[Caso]:
    pres = cargar_presupuesto()
    return [Caso(e.nombre, nivel, e.capital_inicial, e.valor_casa, gasto_simulado(pres, e.clave_vivienda, nivel),
                 gasto_simulado(pres, e.clave_vivienda, "base"))
            for e in ESCENARIOS for nivel in NIVELES]


def toca_piso(res, caso: Caso) -> float:
    """Probabilidad de que, en vida, las barandas lleven el retiro hasta el gasto base."""
    if caso.gasto_mes <= caso.piso_mes:
        return float("nan")
    T = res.retiro.shape[1]
    vivo = np.arange(T)[None, :] < res.anios_vida[:, None]
    return float(((res.retiro <= 12 * caso.piso_mes * (1 + 1e-9)) & vivo).any(axis=1).mean())


# --------------------------------------------------------------------- impresión

pct = etapa4.pct
titulo = etapa4.titulo


def usd(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".")


def musd(x: float) -> str:
    return f"{x / 1e6:.2f}".replace(".", ",")


def main() -> dict:
    ins = etapa4.insumos()
    r_bl = etapa4.retornos(ins, ins.S_lw)
    w = etapa4.principal(ins, r_bl, ins.S_lw)
    etapa4.controlar(ins, w, "final")
    carteras = {v: etapa4.principal(ins, r_bl, ins.S_lw, vol=v) for v in (0.07, 0.11)}
    for v, x in carteras.items():
        etapa4.controlar(ins, x, f"vol {v:.0%}")
    cs = casos()
    from tp import alternativas as alt_mod
    lujo_a = next(c for c in cs if c.etiqueta == "A lujo")
    real = alt_mod.realizaciones(ins, w.values, lujo_a)
    m = Motor(ins, realizacion=real["cartera"])
    wv = w.values
    base = m.rp(wv)

    titulo("ETAPA 5: MONTE CARLO (2 viviendas × 3 niveles de gasto)")
    print(f"{usd(len(m.vidas))} caminos, semilla {SIM.semilla}, {m.T} años, pasos anuales, USD reales (inflación "
          f"{pct(INF, 2)}). Normales y vidas comunes a todos los escenarios, el estrés y las sensibilidades.")
    print("Orden de cada año: regla de retiro → retiro → comisión por tramos y Bienes Personales "
          f"({pct(tasa_bp(2026), 2)} en 2026, {pct(tasa_bp(2027), 2)} desde 2027; en A también sobre el depto) → "
          "retorno después de impuestos.")
    ev = esperanza_de_vida(SIM.edad, SIM.gompertz_m, SIM.gompertz_b)
    viva = {e: float(supervivencia(SIM.edad, e - SIM.edad, SIM.gompertz_m, SIM.gompertz_b)) for e in (85, 95, 100)}
    print(f"Mortalidad: Gompertz (m = {SIM.gompertz_m:.0f}, b = {SIM.gompertz_b:.0f}) desde los {SIM.edad}. "
          f"Esperanza de vida {SIM.edad + ev:.1f} años; viva a los 85 {pct(viva[85])}, a los 95 {pct(viva[95])}, ".replace(".", ",")
          + f"a los 100 {pct(viva[100])}. En la muestra: edad media de muerte {SIM.edad + m.vidas.mean():.1f}.".replace(".", ",", 1))

    titulo("1. RETORNOS QUE USA LA SIMULACIÓN (largo plazo de 3a por clase, no el posterior BL)")
    mu = mu_por_activo(ins.clase)
    tabla = pd.DataFrame({
        "clase": ins.clase, "peso": w.map(pct),
        "compuesto 3a": [pct(RETORNO_LARGO_PLAZO[c], 2) for c in ins.clase],
        "aritmético": [pct(x, 2) for x in mu], "vol (Σ LW)": [pct(x) for x in np.sqrt(np.diag(m.S))],
        "renta": ins.renta.map(pct), "t sobre r": [pct(x, 0) for x in m.t_r],
    }, index=ins.activos)
    print(tabla[w.values > 0].to_string())
    a_nom = float(wv @ mu)
    vol_nom = float(np.sqrt(wv @ m.S @ wv))
    neto_nom = float(wv @ ((mu - m.gasto) * (1 - m.t_r)) - wv @ m.k)
    neto_nom_sin_gasto = float(wv @ (mu * (1 - m.t_r)) - wv @ m.k)
    gasto_cartera = float(wv @ m.gasto)
    neto_real = (1 + neto_nom) / (1 + INF) - 1
    costo_ini = {c.vivienda: float(comision_anual(c.capital) + tasa_bp(2027) * (c.capital + c.valor_casa)) / c.capital
                 for c in cs}
    print(f"\nCartera: aritmético nominal bruto {pct(a_nom, 2)} | después de impuestos {pct(neto_nom, 2)} | "
          f"real después de impuestos {pct(neto_real, 2)} | vol nominal {pct(vol_nom, 2)}")
    print(f"Gastos de los fondos (expense ratio, data/gastos_fondos.csv): {pct(gasto_cartera, 3)} de la cartera, "
          f"descontados antes de impuestos. Sin ellos, el neto nominal sería {pct(neto_nom_sin_gasto, 2)}.")
    print("Compuesto real después de impuestos, antes de costos y retiros (mediana de los caminos a 70 años): "
          + pct(float(np.median((1 + base.real).prod(axis=1) ** (1 / m.T) - 1)), 2))
    print("Costos fijos desde 2027 (comisión + BP) sobre el capital inicial: "
          + ", ".join(f"{k} {pct(v, 2)}" for k, v in costo_ini.items()))
    print("Impuestos: renta fija 35% sobre todo el retorno nominal; acciones dividendo 35% y resto 15%. Una pérdida "
          "da crédito en el mismo año (quebranto compensado). Retorno de 2008 y de cada año por activo = el de su clase "
          "en el estrés; en el régimen normal, cada activo con su propia vol y correlaciones.")

    titulo("2. RETIRO Y RUINA POR ESCENARIO (ruina = quedarse sin plata estando viva)")
    filas, res_gk, res_fijo = {}, {}, {}
    out = {"escenarios": {}, "retiro_seguro": {}, "sensibilidades": {}}
    for c in cs:
        sin = m.correr(c, base, barandas=False)
        con = m.correr(c, base, barandas=True)
        res_gk[c.etiqueta] = con
        fijos = {e: m.correr(c, base, barandas=False, vidas=m.horizonte(e)).prob_ruina for e in (85, 95, 100)}
        res_fijo[c.etiqueta] = fijos
        out["escenarios"][c.etiqueta] = {
            "gasto_mes": c.gasto_mes, "ruina_sin_barandas": sin.prob_ruina, "ruina_con_barandas": con.prob_ruina,
            "ruina_fija": {str(e): v for e, v in fijos.items()}, "barandas_bajan_al_base": toca_piso(con, c)}
        filas[c.etiqueta] = {
            "capital": usd(c.capital), "gasto/mes": usd(c.gasto_mes), "retiro/capital": pct(12 * c.gasto_mes / c.capital, 2),
            "ruina Gompertz": pct(sin.prob_ruina), "a 85 (fijo)": pct(fijos[85]), "a 95": pct(fijos[95]),
            "a 100": pct(fijos[100]), "con barandas": pct(con.prob_ruina), "GK baja al base": pct(toca_piso(con, c)),
            "GK recorte ≥20%": pct(con.prob_recorte(0.8)),
        }
    print(pd.DataFrame(filas).T.to_string())
    print("Sin barandas: retiro real fijo. Con barandas: Guyton-Klinger 120/80, ±10%, sin ajuste por inflación "
          "después de un año negativo si la tasa supera la inicial, y con piso en el gasto base de la vivienda "
          "(sin piso la regla recorta sin límite y la ruina da 0% por construcción). GK baja al base: el retiro llega "
          "al piso alguna vez en vida. Recorte ≥20%: cae alguna vez debajo del 80% del inicial (o ruina). "
          "El gasto no incluye la línea de BP del depto del presupuesto: el BP se simula aparte.")

    titulo("3. PATRIMONIO DE LA CARTERA (USD millones reales; retiro fijo, viva hasta los 100)")
    filas = {}
    for c in cs:
        v = m.correr(c, base, barandas=False, vidas=m.horizonte(100)).valor
        d = {}
        for e in EDADES:
            x = v[:, e - SIM.edad]
            d[f"mediana {e}"], d[f"p10 {e}"] = musd(np.median(x)), musd(np.percentile(x, 10))
        filas[c.etiqueta] = d
    print(pd.DataFrame(filas).T.to_string())
    casa = ESCENARIOS[0].valor_casa
    print(f"En A, además, el depto: USD {musd(casa)} M hoy; con {pct(SIM.valorizacion_real_casa)} real por año vale "
          + ", ".join(f"{musd(casa * (1 + SIM.valorizacion_real_casa) ** (e - SIM.edad))} M a los {e}" for e in EDADES) + ".")

    titulo("4. RETIRO MÁXIMO SEGURO (sobrevive en el 95% de los caminos, mortalidad de Gompertz)")
    seguro = {}
    for e in ESCENARIOS:
        c0 = next(c for c in cs if c.vivienda == e.nombre)
        seguro[e.nombre] = {b: m.retiro_seguro(c0, base, b) for b in (False, True)}
        out["retiro_seguro"][e.nombre] = {"sin_barandas": seguro[e.nombre][False],
                                         "con_barandas": seguro[e.nombre][True]}
    filas = {}
    for e in ESCENARIOS:
        s = seguro[e.nombre]
        d = {"sin barandas (USD/mes)": usd(s[False]), "% capital": pct(12 * s[False] / e.capital_inicial, 2),
             "con barandas (USD/mes)": usd(s[True]), "% capital ": pct(12 * s[True] / e.capital_inicial, 2)}
        for c in cs:
            if c.vivienda == e.nombre:
                d[f"margen {c.nivel} (sin GK)"] = usd(s[False] - c.gasto_mes)
        filas[e.nombre] = d
    print(pd.DataFrame(filas).T.to_string())
    print("Margen = retiro seguro sin barandas − gasto del nivel (USD/mes). Positivo: el nivel entra con 95% de "
          "confianza sin depender de las barandas. Con barandas: retiro inicial más alto con ruina ≤ 5% si las "
          "barandas pueden recortar hasta el gasto base de la vivienda (A 14.850, B 18.450).")

    titulo("5. ESTRÉS: el primer año repite 2008 (retornos por clase de la etapa 2) y después vuelve al régimen normal")
    r08 = ins.extra["r2008"]
    shock = np.array([r08[c] for c in ins.clase])
    print("2008 por clase (nominal, USD): " + ", ".join(f"{c} {pct(r08[c])}" for c in dict.fromkeys(ins.clase)))
    est = m.rp(wv, shock=shock)
    print(f"Cartera en el año 1: {pct(est.nominal[0, 0])} nominal después de impuestos, {pct(est.real[0, 0])} real.")
    filas = {}
    for c in cs:
        b0, b1 = m.correr(c, base, False), m.correr(c, est, False)
        g0, g1 = res_gk[c.etiqueta], m.correr(c, est, True)
        out["escenarios"][c.etiqueta]["estres_2008"] = {"ruina_sin_barandas": b1.prob_ruina,
                                                        "ruina_con_barandas": g1.prob_ruina}
        filas[c.etiqueta] = {
            "ruina base": pct(b0.prob_ruina), "ruina 2008": pct(b1.prob_ruina),
            "con GK base": pct(g0.prob_ruina), "con GK 2008": pct(g1.prob_ruina),
            "GK baja al base 2008": pct(toca_piso(g1, c)),
            "mediana 65 base": musd(np.median(m.correr(c, base, False, vidas=m.horizonte(100)).valor[:, 30])),
            "mediana 65 2008": musd(np.median(m.correr(c, est, False, vidas=m.horizonte(100)).valor[:, 30])),
        }
    print(pd.DataFrame(filas).T.to_string())
    for e in ESCENARIOS:
        c0 = next(c for c in cs if c.vivienda == e.nombre)
        out["retiro_seguro"][e.nombre]["estres_2008"] = {b: m.retiro_seguro(c0, est, b) for b in (False, True)}
    out["estres_2008_cartera_anio1_real"] = float(est.real[0, 0])
    print("Retiro máximo seguro con 2008 en el año 1 (USD/mes): " + ", ".join(
        f"{e.nombre} sin GK {usd(out['retiro_seguro'][e.nombre]['estres_2008'][False])} "
        f"(normal {usd(seguro[e.nombre][False])}), con GK "
        f"{usd(out['retiro_seguro'][e.nombre]['estres_2008'][True])} "
        f"(normal {usd(seguro[e.nombre][True])})" for e in ESCENARIOS))
    for e in ESCENARIOS:
        r = out["retiro_seguro"][e.nombre]["estres_2008"]
        out["retiro_seguro"][e.nombre]["estres_2008"] = {"sin_barandas": r[False], "con_barandas": r[True]}

    titulo("6. SENSIBILIDADES (ruina con mortalidad de Gompertz, retiro fijo, y retiro máximo seguro sin barandas)")
    sens = {"base (vol 9%)": (wv, 0.0), "retornos +1 pp": (wv, 0.01), "retornos −1 pp": (wv, -0.01),
            "vol 7%": (carteras[0.07].values, 0.0), "vol 11%": (carteras[0.11].values, 0.0)}
    filas, seg = {}, {}
    for k, (x, d) in sens.items():
        rp = m.rp(x, d)
        mu_k = mu_por_activo(ins.clase, d)
        neto_k = (1 + float(x @ ((mu_k - m.gasto) * (1 - m.t_r)) - x @ m.k)) / (1 + INF) - 1
        fila = {"ret. real neto": pct(neto_k, 2), "vol": pct(float(np.sqrt(x @ m.S @ x)), 2)}
        ruinas = {c.etiqueta: m.correr(c, rp, False).prob_ruina for c in cs}
        for et, v in ruinas.items():
            fila[et] = pct(v)
        filas[k] = fila
        seguros = {e.nombre: m.retiro_seguro(next(c for c in cs if c.vivienda == e.nombre), rp, False)
                   for e in ESCENARIOS}
        seg[k] = {n: usd(v) for n, v in seguros.items()}
        out["sensibilidades"][k] = {"retorno_real_neto": neto_k, "ruina_sin_barandas": ruinas,
                                    "retiro_seguro_sin_barandas": seguros}
    print(pd.DataFrame(filas).to_string())
    print("\nRetiro máximo seguro sin barandas (USD/mes):\n" + pd.DataFrame(seg).to_string())
    print("Vol 7% y 11%: carteras de la etapa 4 con las mismas reglas (piso ESGV, mínimo por acción). Retornos ±1 pp: "
          "se mueve el compuesto de largo plazo de las seis clases y se recalcula el aritmético; mismas normales.")
    print("\nPesos por clase de las carteras de vol:\n" + pd.DataFrame(
        {"vol 7%": etapa4.por_clase(ins, carteras[0.07]).map(pct), "vol 9%": etapa4.por_clase(ins, w).map(pct),
         "vol 11%": etapa4.por_clase(ins, carteras[0.11]).map(pct)}).to_string())

    titulo("7. CONTROLES")
    sin_costos = retorno_cartera(m.R(), wv, inflacion=INF)
    v60 = simular(1.0, 0.0, sin_costos.real, sin_costos.nominal, m.horizonte(95), lambda v, t: np.zeros_like(v),
                  con_barandas=False).valor[:, 60]
    g_sim = float(np.median(v60) ** (1 / 60) - 1)
    g_teo = compuesto_esperado((1 + a_nom) / (1 + INF) - 1, vol_nom / (1 + INF))
    print(f"Retiro 0 y sin costos ni impuestos: mediana a 60 años crece {pct(g_sim, 3)} real por año; compuesto "
          f"esperado de la cartera {pct(g_teo, 3)} (diferencia " + f"{abs(g_sim - g_teo) * 1e4:.1f}".replace(".", ",")
          + " pb). Mismo control en tests/test_montecarlo.py.")
    ruina10 = {c.etiqueta: m.correr(c, base, False).prob_ruina for c in cs}
    for n_otro in (20_000,):
        otro = Motor(ins, n=n_otro, semilla=SIM.semilla + 100, realizacion=real["cartera"])
        rp_otro = otro.rp(wv)
        difs = {c.etiqueta: otro.correr(c, rp_otro, False).prob_ruina - ruina10[c.etiqueta] for c in cs}
        maxd = max(abs(v) for v in difs.values()) * 100
        print(f"{usd(n_otro)} caminos (otra semilla) contra 10.000, ruina con Gompertz: "
              + ", ".join(f"{k} {v * 100:+.1f} pp".replace(".", ",") for k, v in difs.items())
              + " → máx. " + f"{maxd:.1f}".replace(".", ",") + " pp"
              + (" (cumple ≤ 1 pp)" if maxd <= 1 else " (NO cumple ≤ 1 pp)"))
        del otro
    se = max(np.sqrt(p * (1 - p) / len(m.vidas)) for p in ruina10.values())
    print("Error estándar binomial de la ruina con 10.000 caminos: ≤ " + f"{se * 100:.2f}".replace(".", ",")
          + " pp (máximo en p = 50%: 0,50 pp). Criterio de convergencia: 20.000 contra 10.000 caminos, ≤ 1 pp.")
    mono = all(f[85] <= f[95] <= f[100] for f in res_fijo.values())
    print(f"Ruina crece con el horizonte (85 ≤ 95 ≤ 100) en los 6 escenarios: {'sí' if mono else 'NO'}.")
    print(f"Comisión sobre USD 14 M: {usd(float(comision_anual(14e6)))} (0,60% efectivo).")
    print(f"TIPS 10 años real: {pct(Mercado.tips_10_real, 2)} (FRED DFII10, 12/11/2026).")
    bil = float(w[[a for a, c in zip(ins.activos, ins.clase) if c == "liquidez"]].sum())
    print("Reserva de 2 años de gasto contra la liquidez: " + ", ".join(
        f"{c.etiqueta} {pct(24 * c.gasto_mes / c.capital)}" for c in cs) + f" vs liquidez {pct(bil)} → "
        + ("entra en todos" if all(24 * c.gasto_mes / c.capital <= bil + 1e-9 for c in cs) else "NO entra en todos"))
    print("Rangos, topes, piso de ESGV y mínimo por acción: la final y las de vol 7% / 11% pasan etapa4.controlar.")
    print("A y B usan la misma matriz de retornos y las mismas vidas (un solo Motor).")

    titulo("8. ¿Y SI NO INVIERTE? (A compra, nivel lujo, sueldo fijo + bono con barandas; mismas vidas)")
    mb = Motor(alt_mod.insumos_benchmark(ins), realizacion=real["benchmark"])
    alt = alt_mod.alternativas(m, mb, lujo_a, wv, SIM.edad, INF)
    nombres = {"a_quieta": "a. plata quieta", "b_letras": "b. letras (BIL)", "c_benchmark": "c. 50/50 pasivo",
               "d_cartera": "d. nuestra cartera", "e_benchmark_comision": "e. 50/50 con comisión"}
    filas = {}
    for k, r in alt.items():
        f = {"ruina": pct(r["ruina"]),
             "edad mediana de ruina": "-" if r["edad_mediana_ruina"] is None else f"{r['edad_mediana_ruina']:.0f}",
             "edad central": f"{r['edad_central']:.0f}" if not np.isnan(r.get("edad_central", np.nan)) else "-",
             "bono desaparece": pct(r["bono_desaparece"]),
             "real compuesto": pct(r["retorno_real_compuesto"], 2)}
        for e in alt_mod.EDADES_PATRIMONIO:
            f[f"{e} real"] = musd(r["patrimonio"]["real"][e])
            f[f"{e} nominal"] = musd(r["patrimonio"]["nominal"][e])
        filas[nombres[k]] = f
    print(pd.DataFrame(filas).T.to_string())
    print("Patrimonio: mediana de la cartera en USD millones (viva hasta los 100), en dólares de hoy y corrientes "
          f"({pct(INF, 2)} de inflación). Edad central: con el retorno compuesto mediano constante. Real compuesto: "
          "después de impuestos y gastos de fondos, antes de comisión y BP. c no paga comisión pero no cumple la "
          "política: más vol y sin filtro ESG.")
    out["alternativas"] = alt
    bw = mb.ins.pesos
    out["alternativas_benchmark_vol"] = float(np.sqrt(bw @ mb.S @ bw))

    titulo("9. SENSIBILIDAD A CAMBIOS DE IMPUESTOS (A lujo con bono)")
    imp = alt_mod.sensibilidad_impuestos(ins, wv, lujo_a, real["cartera"])
    print(pd.DataFrame({k: {"ruina con bono": pct(v["ruina_bono"]), "retiro seguro con bono": usd(v["seguro_bono"])}
                        for k, v in imp.items()}).T.to_string())
    print("bp_fijo: Bienes Personales queda en 0,75% (no baja a 0,25%). alicuotas_altas: intereses y dividendos 40%, "
          "ganancia de capital 20%. ambos: las dos cosas.")
    out["impuestos"] = imp

    out["realizacion"] = real
    out["retorno_real_neto_cartera"] = neto_real
    out["retorno_nominal_neto_cartera"] = neto_nom
    out["retorno_nominal_neto_sin_gasto_fondos"] = neto_nom_sin_gasto
    out["gasto_fondos_cartera"] = gasto_cartera
    out["estres_2008_cartera_anio1_nominal"] = float(est.nominal[0, 0])
    out["convergencia"] = {"error_estandar_max_10000": float(se), "max_dif_20000_vs_10000": maxd / 100}
    return out

if __name__ == "__main__":
    main()
