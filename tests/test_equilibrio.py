import pandas as pd
import pytest

from tp.config import BENCHMARK
from tp.equilibrio import cap_total_implicita, pesos_neutros


def seleccion(filas):
    return pd.DataFrame(filas, columns=["ticker", "clase", "tipo"])


BASE = [("BIL", "liquidez", "fondo"), ("IEF", "tesoro", "fondo"), ("TIP", "tips", "fondo"),
        ("VCEB", "corporativos", "fondo"), ("ESGV", "acciones_eeuu", "fondo"),
        ("MSFT", "acciones_eeuu", "accion"), ("NVDA", "acciones_eeuu", "accion"),
        ("ASML", "acciones_europa", "accion"), ("SAP", "acciones_europa", "accion")]
CAPS = {"MSFT": 4.0, "NVDA": 5.0, "ASML": 0.6, "SAP": 0.3}  # billones de USD


def test_suma_uno_y_respeta_el_benchmark_por_clase():
    w = pesos_neutros(seleccion(BASE), BENCHMARK, CAPS, cap_total_eeuu=50.0)
    assert w.sum() == pytest.approx(1.0)
    clase = dict((t, c) for t, c, _ in BASE)
    for c, peso in BENCHMARK.items():
        assert w[[t for t in w.index if clase[t] == c]].sum() == pytest.approx(peso)


def test_renta_fija_en_partes_iguales_dentro_de_la_clase():
    filas = BASE + [("IEI", "tesoro", "fondo")]
    w = pesos_neutros(seleccion(filas), BENCHMARK, CAPS, cap_total_eeuu=50.0)
    assert w["IEF"] == pytest.approx(BENCHMARK["tesoro"] / 2)
    assert w["IEI"] == pytest.approx(BENCHMARK["tesoro"] / 2)


def test_acciones_eeuu_por_su_peso_en_el_mercado_y_el_fondo_con_el_resto():
    w = pesos_neutros(seleccion(BASE), BENCHMARK, CAPS, cap_total_eeuu=50.0)
    eeuu = BENCHMARK["acciones_eeuu"]
    assert w["MSFT"] == pytest.approx(eeuu * 4.0 / 50.0)
    assert w["NVDA"] == pytest.approx(eeuu * 5.0 / 50.0)
    assert w["ESGV"] == pytest.approx(eeuu * (1 - 9.0 / 50.0))


def test_acciones_europa_por_capitalizacion_entre_las_elegidas():
    w = pesos_neutros(seleccion(BASE), BENCHMARK, CAPS, cap_total_eeuu=50.0)
    eur = BENCHMARK["acciones_europa"]
    assert w["ASML"] == pytest.approx(eur * 0.6 / 0.9)
    assert w["SAP"] == pytest.approx(eur * 0.3 / 0.9)


def test_clase_sin_activos_es_error():
    sin_tips = [f for f in BASE if f[1] != "tips"]
    with pytest.raises(ValueError, match="tips"):
        pesos_neutros(seleccion(sin_tips), BENCHMARK, CAPS, cap_total_eeuu=50.0)


def test_acciones_que_superan_el_mercado_es_error():
    with pytest.raises(ValueError, match="acciones_eeuu"):
        pesos_neutros(seleccion(BASE), BENCHMARK, CAPS, cap_total_eeuu=8.0)


def test_cap_total_implicita_es_la_mediana_de_cap_sobre_peso():
    top = {"NVDA": 0.10, "AAPL": 0.08, "MSFT": 0.07}
    caps = {"NVDA": 5.0, "AAPL": 4.4, "MSFT": 3.85}  # implican 50, 55 y 55
    assert cap_total_implicita(top, caps) == pytest.approx(55.0)


def test_con_la_seleccion_real_esgv_no_queda_cerca_de_cero():
    from tp.config import DATA
    sel = pd.read_csv(DATA / "seleccion.csv")
    caps = pd.read_csv(DATA / "fundamentals.csv").set_index("ticker")["market_cap"].to_dict()
    top = pd.read_csv(DATA / "esgv_top.csv").set_index("ticker")["peso"].to_dict()
    total = cap_total_implicita(top, caps)
    w = pesos_neutros(sel, BENCHMARK, caps, cap_total_eeuu=total)
    eeuu = BENCHMARK["acciones_eeuu"]
    assert w["ESGV"] / eeuu > 0.6          # el fondo sigue siendo el núcleo de la clase
    eeuu_acc = sel.loc[(sel["tipo"] == "accion") & (sel["clase"] == "acciones_eeuu"), "ticker"]
    assert (w[eeuu_acc] <= 0.05).all()     # en EE.UU. las acciones sueltas pesan poco en el neutro
    # En Europa, por capitalización ASML se lleva ~60% de la clase y pasa el tope de 5%.
    # El neutro solo fija π; los topes se aplican en la optimización, no acá.
    assert w["ASML"] > 0.05
    assert w.sum() == pytest.approx(1.0)
