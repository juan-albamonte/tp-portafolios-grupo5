"""Filtro ESG: de los candidatos al universo invertible.

Reglas (se acumulan todos los motivos que apliquen):
1. Actividad excluida: armamento, tabaco, petróleo y gas, carbón, minería pesada.
   En los fondos, la actividad es lo que tienen en cartera: un fondo sin filtro
   ESG hereda las actividades de su índice.
2. Fondo de acciones europeas que no es solo Europa: fuera de mandato.
3. Acción con nota ESG por debajo del mínimo de la política: S&P Global ESG Score < 25
   (data/esg.csv). Si el puntaje vigente no es público, se usa el CSA 2024 del documento
   del DJSI. Una acción sin nota verificada queda en el universo marcada "sin puntaje público",
   pero no puede entrar a la cartera.

Fuente ESG: MSCI cerró su buscador público (hoy solo MSCI ONE) y Sustainalytics dejó de
publicar páginas por empresa; S&P Global es la fuente pública por emisor que queda.
Ver docs/eic/nota_esg.md.
"""
import pandas as pd

from tp.config import DATA

ACTIVIDADES_EXCLUIDAS = {"armamento", "tabaco", "petroleo_gas", "carbon", "mineria"}
NOMBRE_ACTIVIDAD = {"armamento": "armamento", "tabaco": "tabaco", "petroleo_gas": "petróleo y gas",
                    "carbon": "carbón", "mineria": "minería pesada"}
ESG_MINIMO = 25
PAISES_EUROPA = {"Europa", "Reino Unido", "Países Bajos", "Alemania", "Dinamarca", "Suiza", "Francia",
                 "España", "Italia", "Suecia", "Irlanda", "Bélgica"}
SOBERANOS = {"liquidez", "tesoro", "tips"}


def motivos_de_exclusion(f: pd.Series) -> list[str]:
    motivos = []
    actividades = [a for a in str(f["actividad"]).split(";") if a]
    if actividades:
        motivos.append("Excluido: " + ", ".join(NOMBRE_ACTIVIDAD[a] for a in actividades))
    if f["tipo"] == "fondo" and f["clase"] == "acciones_europa" and f["pais"] not in PAISES_EUROPA:
        motivos.append(f"Fuera de mandato: no es solo Europa ({f['pais']})")
    if f["tipo"] == "accion" and f["esg_sp"] not in ("", "n/a") and float(f["esg_sp"]) < ESG_MINIMO:
        motivos.append(f"ESG bajo: S&P {float(f['esg_sp']):.0f} < {ESG_MINIMO} ({f['fuente_esg']})")
    return motivos


def por_que_entra(f: pd.Series) -> str:
    if f["tipo"] == "fondo" and f["clase"] in SOBERANOS:
        return "Deuda soberana de EE.UU.: sin exposición a actividades excluidas"
    if f["tipo"] == "fondo":
        return "Fondo con filtro ESG que excluye combustibles fósiles, armas y tabaco (página de Vanguard, 15/11/2026)"
    if f["esg_sp"] == "":
        return "Sin actividades excluidas; ESG sin puntaje público: no puede entrar a la cartera"
    return f"Sin actividades excluidas; ESG S&P {float(f['esg_sp']):.0f} ≥ {ESG_MINIMO}"


def notas_esg(esg: pd.DataFrame) -> pd.DataFrame:
    """ticker, esg_sp (ESG Score vigente o, si no es público, CSA 2024) y fuente_esg."""
    nota = esg["esg"].fillna(esg["csa"])
    fuente = esg["esg"].notna().map({True: "S&P Global ESG Score", False: "CSA 2024, DJSI"})
    return pd.DataFrame({"ticker": esg["ticker"], "esg_sp": nota.map(lambda x: "" if pd.isna(x) else f"{x:.0f}"),
                         "fuente_esg": fuente.where(nota.notna(), "sin puntaje público")})


def filtrar(candidatos: pd.DataFrame, esg: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (universo, excluidos). El universo trae 'seleccionado' vacío: lo llena el EIC."""
    df = candidatos.fillna("").copy()
    if esg is not None:
        df = df.merge(notas_esg(esg), on="ticker", how="left")
    for col in ("esg_sp", "fuente_esg"):
        df[col] = df[col].fillna("") if col in df else ""
    df.loc[(df["tipo"] == "accion") & (df["esg_sp"] == ""), "fuente_esg"] = "sin puntaje público"
    df.loc[df["tipo"] == "fondo", ["esg_sp", "fuente_esg"]] = ["n/a", "n/a"]
    motivos = df.apply(motivos_de_exclusion, axis=1)
    sale = motivos.str.len() > 0

    universo = df[~sale].copy()
    universo["por_que_entra"] = universo.apply(por_que_entra, axis=1)
    universo["seleccionado"] = ""
    universo = universo[["ticker", "nombre", "clase", "tipo", "pais", "sector", "esg_sp", "fuente_esg",
                         "por_que_entra", "seleccionado"]].reset_index(drop=True)

    excluidos = df[sale].copy()
    excluidos["motivo"] = motivos[sale].str.join(" | ")
    excluidos = excluidos[["ticker", "nombre", "clase", "sector", "motivo"]].reset_index(drop=True)
    return universo, excluidos


COLUMNAS_OPERABILIDAD = ["cedear_byma", "mercado_eeuu", "operable_broker_eeuu"]


def agregar_operabilidad(universo: pd.DataFrame, operabilidad: pd.DataFrame) -> pd.DataFrame:
    """Suma si hay CEDEAR en BYMA y dónde cotiza en EE.UU. ('seleccionado' queda al final).

    Fuentes: lista oficial de BYMA "CEDEARs Negociables" (16/09/2026), altas de
    octubre-noviembre 2026 (ninguna de renta fija ni ESG) y mercado de Yahoo Finance.
    """
    op = operabilidad[["ticker"] + COLUMNAS_OPERABILIDAD]
    r = universo.drop(columns=COLUMNAS_OPERABILIDAD, errors="ignore").merge(op, on="ticker", how="left")
    r[COLUMNAS_OPERABILIDAD] = r[COLUMNAS_OPERABILIDAD].fillna("A VERIFICAR")
    columnas = [c for c in r.columns if c != "seleccionado"] + ["seleccionado"]
    return r[columnas]


def marcar_seleccion(universo: pd.DataFrame, seleccion: pd.DataFrame) -> pd.DataFrame:
    """Marca 'seleccionado' = "sí" en los tickers de la cartera final (data/seleccion.csv).

    Una acción sin nota ESG verificada no puede entrar (política de inversión).
    """
    u = universo.copy()
    faltan = set(seleccion["ticker"]) - set(u["ticker"])
    if faltan:
        raise ValueError(f"Seleccionados fuera del universo: {sorted(faltan)}")
    sin_nota = u[u["ticker"].isin(seleccion["ticker"]) & (u["fuente_esg"] == "sin puntaje público")]["ticker"]
    if len(sin_nota):
        raise ValueError(f"Seleccionados con ESG sin puntaje público: {sorted(sin_nota)}")
    u["seleccionado"] = u["ticker"].isin(seleccion["ticker"]).map({True: "sí", False: ""})
    return u


def main() -> None:
    candidatos = pd.read_csv(DATA / "candidatos.csv", keep_default_na=False)
    universo, excluidos = filtrar(candidatos, pd.read_csv(DATA / "esg.csv"))
    if (DATA / "operabilidad.csv").exists():
        universo = agregar_operabilidad(universo, pd.read_csv(DATA / "operabilidad.csv"))
    if (DATA / "seleccion.csv").exists():
        universo = marcar_seleccion(universo, pd.read_csv(DATA / "seleccion.csv"))
    universo.to_csv(DATA / "universo.csv", index=False)
    excluidos.to_csv(DATA / "excluidos.csv", index=False)
    salida = DATA.parent / "outputs"
    salida.mkdir(exist_ok=True)
    universo.to_csv(salida / "universo.csv", index=False)
    excluidos.to_csv(salida / "excluidos.csv", index=False)
    with pd.option_context("display.max_rows", None, "display.width", 250, "display.max_colwidth", 90):
        print(f"UNIVERSO ({len(universo)} de {len(candidatos)} candidatos)")
        print(universo.drop(columns=["seleccionado", "por_que_entra"]).to_string(index=False))
        print(f"\nEXCLUIDOS ({len(excluidos)})")
        print(excluidos.to_string(index=False))


if __name__ == "__main__":
    main()
