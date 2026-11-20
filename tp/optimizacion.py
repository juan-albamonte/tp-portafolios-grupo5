"""Optimización con las restricciones de la política de inversión.

- Sin cortos; suma 100%.
- Rangos por clase del IPS (config.RANGOS).
- Topes por activo según el tipo: acción 5%, fondo 30%.
- Pisos por activo opcionales (núcleo en ESGV) y posición mínima por acción (2% o 0),
  resuelta iterando: las acciones que quedan entre 0 y el mínimo se fijan en 0 y se reoptimiza.
- Cartera principal: máximo retorno esperado después de impuestos s.a. vol ≤ objetivo,
  con la Σ de Ledoit-Wolf diaria.
"""
import numpy as np
from scipy.optimize import minimize

TOPES = {"accion": 0.05, "fondo": 0.30}
TOL = 1e-6


def _restricciones(clase: list[str], rangos: dict) -> list[dict]:
    clase = np.asarray(clase)
    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1, "jac": lambda w: np.ones_like(w)}]
    for c, (lo, hi) in rangos.items():
        a = (clase == c).astype(float)
        cons.append({"type": "ineq", "fun": lambda w, a=a, lo=lo: a @ w - lo, "jac": lambda w, a=a: a})
        cons.append({"type": "ineq", "fun": lambda w, a=a, hi=hi: hi - a @ w, "jac": lambda w, a=a: -a})
    return cons


def _cotas(tipo: list[str], topes: dict, pisos: dict | None = None,
           excluidos: set | None = None) -> list[tuple[float, float]]:
    pisos, excluidos = pisos or {}, excluidos or set()
    return [(0.0, 0.0) if i in excluidos else (pisos.get(i, 0.0), topes[t]) for i, t in enumerate(tipo)]


def _inicio(clase, tipo, rangos, topes) -> np.ndarray:
    """Punto factible: centro de cada rango, repartido dentro de la clase respetando topes."""
    return mas_cercana(np.full(len(clase), 1 / len(clase)), clase, tipo, rangos, topes)


def _resolver(f, jac, x0, clase, tipo, rangos, topes, extra=(), pisos=None, excluidos=None) -> np.ndarray:
    cotas = _cotas(tipo, topes, pisos, excluidos)
    x0 = np.clip(x0, [lo for lo, _ in cotas], [hi for _, hi in cotas])
    r = minimize(f, x0, jac=jac, method="SLSQP", bounds=cotas,
                 constraints=_restricciones(clase, rangos) + list(extra),
                 options={"maxiter": 1000, "ftol": 1e-12})
    if not r.success:
        raise RuntimeError(f"El optimizador no convergió: {r.message}")
    w = np.clip(r.x, 0, None)
    return w / w.sum()


def mas_cercana(w_obj: np.ndarray, clase, tipo, rangos, topes=TOPES, pisos: dict | None = None,
                excluidos: set | None = None) -> np.ndarray:
    """La cartera factible más cercana (distancia euclídea) a w_obj. Sirve para ajustar HRP."""
    w_obj = np.asarray(w_obj, float)
    x0 = np.clip(w_obj, 0, [topes[t] for t in tipo])
    x0 = x0 / x0.sum()
    return _resolver(lambda w: ((w - w_obj) ** 2).sum(), lambda w: 2 * (w - w_obj), x0, clase, tipo, rangos, topes,
                     pisos=pisos, excluidos=excluidos)


def optimizar(mu: np.ndarray, Sigma: np.ndarray, clase, tipo, rangos, vol_max: float, topes=TOPES,
              desempate: float = 0.0, pisos: dict | None = None, excluidos: set | None = None) -> np.ndarray:
    """Máximo w'μ s.a. w'Σw ≤ vol_max². `desempate` suma una penalización mínima a la varianza.

    pisos: {índice del activo: peso mínimo} (p. ej., un núcleo mínimo en el fondo amplio).
    excluidos: índices que quedan en 0.
    """
    vol_c = {"type": "ineq", "fun": lambda w: vol_max ** 2 - w @ Sigma @ w, "jac": lambda w: -2 * Sigma @ w}
    f = lambda w: -mu @ w + desempate * w @ Sigma @ w
    jac = lambda w: -mu + 2 * desempate * Sigma @ w
    x0 = minima_varianza(Sigma, clase, tipo, rangos, topes, pisos, excluidos)
    if np.sqrt(x0 @ Sigma @ x0) > vol_max + TOL:
        raise ValueError(f"No hay cartera factible con vol ≤ {vol_max:.1%} (mínimo {np.sqrt(x0 @ Sigma @ x0):.2%})")
    return _resolver(f, jac, x0, clase, tipo, rangos, topes, extra=[vol_c], pisos=pisos, excluidos=excluidos)


def minima_varianza(Sigma: np.ndarray, clase, tipo, rangos, topes=TOPES, pisos: dict | None = None,
                    excluidos: set | None = None) -> np.ndarray:
    x0 = _inicio(clase, tipo, rangos, topes)
    return _resolver(lambda w: w @ Sigma @ w, lambda w: 2 * Sigma @ w, x0, clase, tipo, rangos, topes, pisos=pisos,
                     excluidos=excluidos)


def con_minimo(resolver, tipo, minimo: float, valor=None, tol: float = 1e-6) -> tuple[np.ndarray, list[int]]:
    """Posición mínima por acción: 0 o al menos `minimo`.

    resolver(excluidos, forzados) devuelve una cartera con las acciones `excluidos` en 0 y las
    `forzados` en al menos `minimo`.
    1. Iteración: se optimiza, las acciones con peso entre 0 y el mínimo se fijan en 0 y se
       reoptimiza, hasta que no quede ninguna en ese rango.
    2. Reingreso (si se pasa `valor`, la función objetivo a maximizar): cada acción que salió se
       prueba forzada al mínimo y vuelve si el objetivo mejora. Corrige la elección codiciosa del
       paso 1 cuando el objetivo es casi plano. No es el óptimo entero exacto (eso pide
       programación entera), pero no puede quedar peor que la iteración sola.
    Devuelve la cartera y los índices que quedaron afuera.
    """
    def iterar(excluidos: list[int], forzados: set[int]) -> tuple[np.ndarray, list[int]]:
        excluidos = list(excluidos)
        while True:
            w = resolver(set(excluidos), set(forzados))
            chicas = [i for i, t in enumerate(tipo) if t == "accion" and tol < w[i] < minimo - tol
                      and i not in forzados]
            if not chicas:
                w = np.where(w < tol, 0.0, w)
                return w / w.sum(), excluidos
            excluidos += chicas

    forzados: set[int] = set()
    w, fuera = iterar([], forzados)
    if valor is None:
        return w, fuera
    mejoro = True
    while mejoro:
        mejoro = False
        for i in list(fuera):
            try:
                w2, fuera2 = iterar([j for j in fuera if j != i], forzados | {i})
            except (ValueError, RuntimeError):
                continue
            if valor(w2) > valor(w) + 1e-9:
                w, fuera, forzados, mejoro = w2, fuera2, forzados | {i}, True
                break
    return w, fuera


def optimizar_con_minimo(mu, Sigma, clase, tipo, rangos, vol_max: float, minimo: float, topes=TOPES,
                         pisos: dict | None = None) -> tuple[np.ndarray, list[int]]:
    pisos = pisos or {}
    return con_minimo(lambda ex, fz: optimizar(mu, Sigma, clase, tipo, rangos, vol_max, topes,
                                               pisos={**pisos, **{i: minimo for i in fz}}, excluidos=ex),
                      tipo, minimo, valor=lambda w: mu @ w)


def violaciones(w: np.ndarray, clase, tipo, rangos, topes=TOPES, tol: float = TOL) -> list[str]:
    clase, tipo = np.asarray(clase), np.asarray(tipo)
    v = []
    if abs(w.sum() - 1) > tol:
        v.append(f"suma {w.sum():.6f}")
    if (w < -tol).any():
        v.append("pesos negativos")
    for i, t in enumerate(tipo):
        if w[i] > topes[t] + tol:
            v.append(f"activo {i} pasa el tope de {t}")
    for c, (lo, hi) in rangos.items():
        s = w[clase == c].sum()
        if s < lo - tol or s > hi + tol:
            v.append(f"{c} fuera de rango ({s:.4f})")
    return v


def restricciones_activas(w, Sigma, clase, tipo, rangos, vol_max=None, topes=TOPES, nombres=None,
                          tol: float = 1e-4) -> list[str]:
    nombres = nombres or [str(i) for i in range(len(w))]
    clase, tipo = np.asarray(clase), np.asarray(tipo)
    a = []
    if vol_max is not None and abs(np.sqrt(w @ Sigma @ w) - vol_max) < tol:
        a.append(f"vol al máximo ({vol_max:.0%})")
    for c, (lo, hi) in rangos.items():
        s = w[clase == c].sum()
        if abs(s - lo) < tol:
            a.append(f"{c} en el mínimo ({lo:.0%})")
        elif abs(s - hi) < tol:
            a.append(f"{c} en el máximo ({hi:.0%})")
    for i, t in enumerate(tipo):
        if abs(w[i] - topes[t]) < tol:
            a.append(f"tope {nombres[i]} ({topes[t]:.0%})")
    return a
