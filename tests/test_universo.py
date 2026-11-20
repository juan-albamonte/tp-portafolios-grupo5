import pytest
import pandas as pd

from tp.config import CLASES, DATA
from tp.universo import ACTIVIDADES_EXCLUIDAS, ESG_MINIMO, filtrar, marcar_seleccion

COLUMNAS = ["ticker", "nombre", "clase", "tipo", "pais", "sector", "actividad", "nota"]


def candidatos_reales() -> pd.DataFrame:
    return pd.read_csv(DATA / "candidatos.csv", keep_default_na=False)


def fila(ticker, clase="acciones_eeuu", tipo="accion", pais="EE.UU.", actividad=""):
    return dict(ticker=ticker, nombre=ticker, clase=clase, tipo=tipo, pais=pais, sector="Tecnología",
                actividad=actividad, nota="")


def esg(filas):
    """filas: (ticker, csa, esg) con None si falta."""
    return pd.DataFrame(filas, columns=["ticker", "csa", "esg"]).astype({"csa": float, "esg": float})


def test_esquema_de_candidatos():
    df = candidatos_reales()
    assert list(df.columns) == COLUMNAS
    assert 50 <= len(df) <= 60
    assert df["ticker"].is_unique
    assert set(df["clase"]) <= set(CLASES)
    assert set(df["tipo"]) <= {"fondo", "accion"}
    tokens = {t for a in df["actividad"] if a for t in a.split(";")}
    assert tokens <= ACTIVIDADES_EXCLUIDAS
    assert not df["nota"].str.contains("MSCI ESG").any()  # nada de ratings de memoria


def test_reglas_del_filtro():
    df = pd.DataFrame([
        fila("OK"),
        fila("PETRO", actividad="petroleo_gas"),
        fila("ARMAS_TABACO", actividad="armamento;tabaco"),
        fila("FONDO_EAFE", clase="acciones_europa", tipo="fondo", pais="Desarrollados ex EE.UU."),
        fila("FONDO_EU", clase="acciones_europa", tipo="fondo", pais="Europa"),
        fila("LAGGARD"),
        fila("VIEJO"),
        fila("SIN_NOTA"),
        fila("BONO", clase="tesoro", tipo="fondo"),
    ])
    notas = esg([("OK", 40, 45), ("LAGGARD", 18, 21), ("VIEJO", 24, None)])
    universo, excluidos = filtrar(df, notas)
    assert set(universo["ticker"]) == {"OK", "FONDO_EU", "BONO", "SIN_NOTA"}
    motivo = excluidos.set_index("ticker")["motivo"]
    assert "petróleo y gas" in motivo["PETRO"]
    assert "armamento" in motivo["ARMAS_TABACO"] and "tabaco" in motivo["ARMAS_TABACO"]
    assert "mandato" in motivo["FONDO_EAFE"]
    assert f"S&P 21 < {ESG_MINIMO}" in motivo["LAGGARD"]
    assert "CSA 2024" in motivo["VIEJO"]  # sin puntaje vigente, cuenta el CSA 2024
    u = universo.set_index("ticker")
    assert u.loc["SIN_NOTA", "fuente_esg"] == "sin puntaje público"
    assert u.loc["BONO", "esg_sp"] == "n/a"
    assert (universo["seleccionado"] == "").all()
    assert universo["por_que_entra"].str.len().gt(0).all()


def test_varios_motivos_se_acumulan():
    df = pd.DataFrame([fila("X", clase="acciones_europa", tipo="fondo", pais="Japón", actividad="carbon")])
    _, excluidos = filtrar(df)
    m = excluidos.loc[0, "motivo"]
    assert "carbón" in m and "mandato" in m


def test_universo_real_cubre_todas_las_clases():
    universo, excluidos = filtrar(candidatos_reales(), pd.read_csv(DATA / "esg.csv"))
    assert len(universo) + len(excluidos) == len(candidatos_reales())
    assert 35 <= len(universo) <= 45
    for clase in ["liquidez", "tesoro", "tips", "corporativos", "acciones_eeuu"]:
        assert ((universo["clase"] == clase) & (universo["tipo"] == "fondo")).any(), clase
    assert ((universo["clase"] == "acciones_europa")).sum() >= 5


def test_agregar_operabilidad_respeta_orden_y_marca_faltantes():
    from tp.universo import agregar_operabilidad
    u = pd.DataFrame({"ticker": ["B", "A"], "seleccionado": ["", ""]})
    op = pd.DataFrame({"ticker": ["A"], "cedear_byma": ["A (2:1)"], "mercado_eeuu": ["NYSE"],
                       "operable_broker_eeuu": ["sí"], "volumen_promedio": [10]})
    r = agregar_operabilidad(u, op)
    assert list(r["ticker"]) == ["B", "A"]
    assert r.loc[1, "cedear_byma"] == "A (2:1)"
    assert r.loc[0, "cedear_byma"] == "A VERIFICAR"
    assert list(r.columns)[-1] == "seleccionado"


def test_marcar_seleccion_y_bloquea_esg_sin_verificar():
    u = pd.DataFrame({"ticker": ["A", "B", "C"], "fuente_esg": ["S&P Global ESG Score", "sin puntaje público", "n/a"],
                      "seleccionado": ["", "", ""]})
    r = marcar_seleccion(u, pd.DataFrame({"ticker": ["A", "C"]}))
    assert list(r["seleccionado"]) == ["sí", "", "sí"]
    with pytest.raises(ValueError, match="sin puntaje público"):
        marcar_seleccion(u, pd.DataFrame({"ticker": ["B"]}))
    with pytest.raises(ValueError, match="fuera del universo"):
        marcar_seleccion(u, pd.DataFrame({"ticker": ["Z"]}))
