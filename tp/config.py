"""Supuestos del modelo.

Cada número tiene su justificación en 'Supuestos del equipo - Grupo 5.docx'.
Si un supuesto cambia allá, se cambia acá y en ningún otro lado.
"""
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
SALIDAS = RAIZ / "outputs"

CLASES = ["liquidez", "tesoro", "tips", "corporativos", "acciones_eeuu", "acciones_europa"]

# Serie larga para las estadísticas (todas arrancan antes de la crisis de 2008).
PROXIES = {
    "liquidez": "BIL",
    "tesoro": "IEF",
    "tips": "TIP",
    "corporativos": "LQD",
    "acciones_eeuu": "SPY",
    "acciones_europa": "VGK",
}

# ETF con el que se implementa, con filtro ESG donde existe. VGK no tiene filtro
# ESG: el plan 2 busca una alternativa ESG de Europa domiciliada en EE.UU.
IMPLEMENTACION = {
    "liquidez": "SGOV",
    "tesoro": "IEF",
    "tips": "TIP",
    "corporativos": "SUSC",
    "acciones_eeuu": "ESGU",
    "acciones_europa": "VGK",
}

# Rangos de la política de inversión (mínimo, máximo).
RANGOS = {
    # Reserva de dos años de gasto (Evensky-Horan-Robinson): ~USD 0,5 M, ≈ 4% de la
    # cartera. El máximo anterior (15%) equivalía a ocho años de gasto. Checkpoint 4, 16/11.
    "liquidez": (0.03, 0.10),
    "tesoro": (0.10, 0.30),
    "tips": (0.05, 0.20),
    "corporativos": (0.05, 0.20),
    "acciones_eeuu": (0.25, 0.45),
    # Piso = su peso en el benchmark (10%): la view V2 dice que Europa le gana a EE.UU.;
    # una cartera subponderada en Europa la contradiría. Cierre del motor, 16/11.
    "acciones_europa": (0.10, 0.20),
}

# Benchmark 50/50 (acciones / renta fija). También es el portafolio de
# equilibrio del Black-Litterman.
BENCHMARK = {
    "liquidez": 0.05,
    "tesoro": 0.20,
    "tips": 0.10,
    "corporativos": 0.15,
    "acciones_eeuu": 0.40,
    "acciones_europa": 0.10,
}

# Pisos por activo (checkpoint 4, 16/11): ESGV es el núcleo de la clase de EE.UU. Sin
# piso, las views "X contra ESGV" lo dejaban en 4%.
PISOS_ACTIVO = {"ESGV": 0.20}
# Posición mínima por acción individual: 0 o al menos 2% (una posición menor no mueve
# la cartera y suma una tesis que defender). Se resuelve iterando en optimizacion.con_minimo.
POSICION_MINIMA_ACCION = 0.02

INICIO_DATOS = "2007-06-01"
# Fondos que nacieron después: antes de su lanzamiento se usan los retornos del
# índice de referencia de su clase (decisión del checkpoint 1, declarada en el documento).
RELLENO = {"VCEB": "LQD", "ESGV": "SPY"}
VENTANA_ANIOS = 10  # ventana común para covarianza y estadísticas por activo
FIN_DATOS = "2026-11-01"  # Yahoo excluye el último día: los datos llegan al 31/10/2026

# Views de Black-Litterman: data/views.csv (EIC, compañías). Formato de Meucci (2010,
# ec. 11): v_k = (Pπ)_k + η_k · ESCALA_VIEW · √(PΣP')_kk, con η ∈ {-2, -1, 1, 2}.
# Alcista (η = 1) = +0,25 desvíos de la view; muy alcista (η = 2) = +0,5. Simétrico.
ESCALA_VIEW = 0.25
# Confianza global c de Ω = (1/c)·diag(u)·PΣP'·diag(u) (ec. 13). Dial de sensibilidad.
CONFIANZA_C = 1.0


# Retorno nominal compuesto en USD a 10-15 años por clase (EIC, economía:
# docs/eic/01_economia.md). Lo usa el Monte Carlo (después de impuestos).
RETORNO_LARGO_PLAZO = {
    # Tasa real neutral ~1,2% + inflación 2,25%. Hoy la letra rinde 4,14%, pero la
    # Fed vuelve a ~3,0-3,5% cuando pase el shock de energía.
    "liquidez": 0.035,
    # Rendimiento inicial del UST 7-10 años ~5,0% (FRED DGS10 5,10%); a 10 años, el
    # retorno de un bono de duración parecida converge a su rendimiento inicial.
    # Algo por debajo por si la curva vuelve a empinarse. JPM LTCMA 2027: 4,6%.
    "tesoro": 0.048,
    # Real TIPS 5-10 años 2,64-2,86% (FRED DFII5, DFII10) + inflación 2,25%.
    "tips": 0.049,
    # Tesoro de duración similar (~4,95%) + spread IG 0,89% (FRED BAMLC0A0CM)
    # - pérdidas esperadas por default y downgrades ~0,3%.
    "corporativos": 0.055,
    # Dividendo + recompras ~1,7% + crecimiento real de ganancias ~3% + inflación
    # 2,25% - recorte de múltiplo (P/E forward 17,7 vs 16,4 de promedio de 25 años,
    # FactSet). JPM LTCMA 2027: 7,5%.
    "acciones_eeuu": 0.070,
    # Dividendo 2,7% + recompras ~0,5% + crecimiento real ~1,5% + inflación EUR 2%
    # - múltiplo levemente caro (P/E forward 14,9 vs mediana 14,1, JPM Guide to the
    # Markets 30/09/2026) + depreciación lenta del dólar ~0,5%.
    "acciones_europa": 0.0725,
}


@dataclass(frozen=True)
class Mercado:
    # Exceso aritmético esperado del benchmark 50/50 sobre la tasa corta de largo
    # plazo (w_b'π del equilibrio): tp.escenario.exceso_benchmark sobre
    # RETORNO_LARGO_PLAZO. Implica λ ≈ 3,4 con la vol histórica del benchmark (10,2%).
    exceso_esperado_benchmark: float = 0.0353
    # Inflación de largo plazo: breakeven a 10 años 2,24% y 5y5y 2,18% (FRED, 13/11/2026).
    inflacion_largo_plazo: float = 0.0225
    tau: float = 0.05
    vol_objetivo: float = 0.09
    # Rendimiento real del TIPS a 10 años (FRED DFII10, 12/11/2026). El Word de
    # supuestos dice 2,64% (dato del 22/10, fuente secundaria): corregirlo.
    tips_10_real: float = 0.0286


@dataclass(frozen=True)
class Impuestos:
    tasa_ar_dividendos: float = 0.35
    retencion_eeuu_dividendos: float = 0.30
    tasa_ar_intereses: float = 0.35      # sensibilidad: 0.15
    retencion_eeuu_intereses: float = 0.0  # no cambia el resultado: ver tasa_efectiva
    tasa_ganancia_capital: float = 0.15
    fraccion_ganancia_en_ventas: float = 0.30
    rebalanceo_anual: float = 0.05


@dataclass(frozen=True)
class Simulacion:
    edad: int = 35
    # Gompertz calibrada a una esperanza de vida de ~88 años (mujer de altos
    # ingresos); ~11% llega a los 100. Mismo modelo que Milevsky y Robinson (2005).
    gompertz_m: float = 93.0
    gompertz_b: float = 9.0
    anios_max: int = 70
    n: int = 10_000
    semilla: int = 42
    prob_ruina_max: float = 0.05
    baranda: float = 0.20
    ajuste: float = 0.10
    anio_inicio: int = 2026
    horizontes_fijos: tuple[int, ...] = (85, 95, 100)
    # El depto mantiene su valor real (supuesto neutro acordado el 14/11).
    valorizacion_real_casa: float = 0.0


@dataclass(frozen=True)
class Escenario:
    nombre: str
    capital: float
    valor_casa: float
    clave_vivienda: str  # "compra" o "alquila"
    # Escribanía, sellos y comisión inmobiliaria: ~7-8% del valor en CABA.
    costo_compra: float | None = None

    def __post_init__(self) -> None:
        if self.costo_compra is None:
            object.__setattr__(self, "costo_compra", 0.075 * self.valor_casa)

    @property
    def capital_inicial(self) -> float:
        """Lo que efectivamente se invierte: el capital menos los gastos de la compra."""
        return self.capital - self.costo_compra


ESCENARIOS = (
    Escenario("A: compra", 14_000_000.0, 1_000_000.0, "compra"),
    Escenario("B: alquila", 15_000_000.0, 0.0, "alquila"),
)


def vector(pesos: dict[str, float]) -> np.ndarray:
    """Pasa un dict por clase a un vector en el orden de CLASES."""
    return np.array([pesos[c] for c in CLASES], dtype=float)


def cargar_presupuesto(archivo: Path = DATA / "presupuesto.csv") -> pd.DataFrame:
    return pd.read_csv(archivo)


NIVELES = ("base", "lujo", "alto")


def gasto_mensual(presupuesto: pd.DataFrame, clave_vivienda: str, nivel: str = "lujo") -> float:
    """Gasto mensual en USD de un nivel: rubros comunes más los de la vivienda del escenario."""
    filas = presupuesto["escenario"].isin(["ambos", clave_vivienda])
    if "nivel" in presupuesto:
        filas &= presupuesto["nivel"] == nivel
    return float(presupuesto.loc[filas, "usd_mes"].sum())


def gastos_fondos(archivo: Path = DATA / "gastos_fondos.csv") -> defaultdict:
    """Gasto anual de cada fondo (expense ratio, en fracción). Las acciones no figuran: valen 0."""
    return defaultdict(float, pd.read_csv(archivo).set_index("ticker")["gasto"].to_dict())


def benchmark_pasivo(archivo: Path = DATA / "benchmark_pasivo.csv") -> pd.DataFrame:
    """Los seis fondos índice del benchmark 50/50 (renta y gasto), en el orden de CLASES."""
    return pd.read_csv(archivo).set_index("clase").loc[CLASES].reset_index()
