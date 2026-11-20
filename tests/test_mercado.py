import pytest

from tp.mercado import foto_mercado, ultimo_valor

CSV = """observation_date,DTB3
2026-10-28,3.80
2026-10-29,.
2026-10-30,3.75
"""


def test_ultimo_valor_salta_faltantes():
    fecha, valor = ultimo_valor(CSV)
    assert fecha == "2026-10-30" and valor == pytest.approx(0.0375)


def test_foto_usa_cache(tmp_path):
    llamadas = []

    def bajador(serie):
        llamadas.append(serie)
        return CSV.replace("DTB3", serie)

    archivo = tmp_path / "m.json"
    a = foto_mercado(archivo, bajador)
    b = foto_mercado(archivo, bajador)
    assert len(llamadas) == 3 and a == b
    assert a["tasa_corta"]["valor"] == pytest.approx(0.0375)
    assert set(a) == {"tasa_corta", "tips_10", "breakeven_10"}
