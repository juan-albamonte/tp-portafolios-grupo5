import pandas as pd
from openpyxl import load_workbook

from tp.excel import HOJAS, escribir_hoja


def test_escribir_hoja_con_formato_y_formulas(tmp_path):
    from openpyxl import Workbook
    wb = Workbook()
    df = pd.DataFrame({"Activo": ["A", "B"], "Peso": [0.6, 0.4]})
    ws = escribir_hoja(wb, "Prueba", df, nota="Fuente: prueba.", formatos={"Peso": "0.0%"})
    ws.cell(row=ws.max_row + 1, column=2, value="=SUM(B4:B5)")
    archivo = tmp_path / "x.xlsx"
    wb.save(archivo)
    ws2 = load_workbook(archivo)["Prueba"]
    assert ws2["A1"].value == "Prueba"
    assert ws2["A2"].value == "Fuente: prueba."
    assert [c.value for c in ws2[3]] == ["Activo", "Peso"]
    assert ws2["B4"].number_format == "0.0%" and ws2["A3"].font.bold
    assert ws2.freeze_panes == "A4"
    assert ws2["B6"].value == "=SUM(B4:B5)"


def test_diecisiete_hojas():
    assert len(HOJAS) == 17
