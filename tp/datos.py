"""Precios de Yahoo Finance con caché en data/, relleno hacia atrás y retornos.

Los precios son de cierre ajustados por dividendos y splits (auto_adjust=True):
el retorno incluye la renta que paga cada activo.
"""
from collections.abc import Callable, Sequence
from pathlib import Path

import numpy as np
import pandas as pd

Bajador = Callable[[Sequence[str], str, str], pd.DataFrame]


def bajar_precios(tickers: Sequence[str], inicio: str, fin: str) -> pd.DataFrame:
    """Cierres diarios ajustados. Columnas: tickers. Yahoo excluye el día 'fin'."""
    import yfinance as yf

    datos = yf.download(list(tickers), start=inicio, end=fin, auto_adjust=True, progress=False,
                        threads=True)
    precios = datos["Close"]
    if isinstance(precios, pd.Series):
        precios = precios.to_frame(tickers[0])
    return precios[list(tickers)].sort_index()


def cargar_o_bajar(archivo: Path, tickers: Sequence[str], inicio: str, fin: str,
                   bajador: Bajador = bajar_precios) -> pd.DataFrame:
    """Lee la caché si tiene todos los tickers; si no, baja todo y la reescribe."""
    archivo = Path(archivo)
    if archivo.exists():
        cache = pd.read_csv(archivo, index_col=0, parse_dates=True)
        if set(tickers) <= set(cache.columns):
            return cache[list(tickers)]
        tickers = sorted(set(tickers) | set(cache.columns))
    precios = bajador(tickers, inicio, fin)
    precios.to_csv(archivo)
    return precios


def rellenar_hacia_atras(fondo: pd.Series, indice: pd.Series) -> pd.Series:
    """Antes del lanzamiento del fondo, usa los retornos del índice de referencia.

    Encadena el índice hacia atrás desde el primer precio del fondo, así que
    después del lanzamiento la serie es exactamente la del fondo.
    """
    inicio = fondo.first_valid_index()
    escala = fondo.loc[inicio] / indice.loc[inicio]
    relleno = fondo.copy()
    antes = relleno.index < inicio
    relleno.loc[antes] = indice.loc[antes] * escala
    return relleno


def control_relleno(fondo: pd.Series, indice: pd.Series) -> dict:
    """Correlación diaria y vol anual de fondo e índice en el período en que coexisten."""
    juntos = pd.concat([fondo, indice], axis=1).dropna()
    r = juntos.pct_change(fill_method=None).dropna()
    vol = r.std() * np.sqrt(252)
    return {
        "desde": juntos.index[0],
        "hasta": juntos.index[-1],
        "dias": len(r),
        "correlacion_diaria": float(r.iloc[:, 0].corr(r.iloc[:, 1])),
        "vol_fondo": float(vol.iloc[0]),
        "vol_indice": float(vol.iloc[1]),
        "dif_vol_anual": float(vol.iloc[0] - vol.iloc[1]),
    }


def a_mensual(precios: pd.DataFrame) -> pd.DataFrame:
    """Último precio de cada mes."""
    return precios.resample("ME").last()


def retornos(precios: pd.DataFrame) -> pd.DataFrame:
    """Retornos simples sin rellenar huecos: un activo sin precio queda NaN."""
    return precios.pct_change(fill_method=None).iloc[1:]
