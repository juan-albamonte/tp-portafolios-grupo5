import json

import pytest

from tp.config import SALIDAS
from tp.cifras import a_nominal, alquiler_implicito

skip_sin_outputs = pytest.mark.skipif(not (SALIDAS / "cifras.json").exists(), reason="falta outputs/cifras.json")


def test_nominal_desde_real():
    assert a_nominal(0.0268, 0.0225) == pytest.approx(1.0268 * 1.0225 - 1)


def test_alquiler_implicito_neto_de_abl_y_mantenimiento():
    import pandas as pd
    pres = pd.DataFrame({"rubro": ["Alquiler del departamento", "ABL", "Mantenimiento del departamento", "Expensas"],
                         "usd_mes": [4500, 300, 600, 1500], "escenario": ["alquila", "compra", "compra", "ambos"],
                         "nivel": ["lujo"] * 4})
    assert alquiler_implicito(pres, "lujo") == 3600


@skip_sin_outputs
def test_cifras_v3_tiene_las_secciones_nuevas():
    c = json.loads((SALIDAS / "cifras.json").read_text(encoding="utf-8"))
    for k in ("nominal", "alternativas", "impuestos", "riesgo", "monitoreo", "costos_cliente"):
        assert k in c, k
    assert c["nominal"]["depto"].endswith("%")


def test_de_cada_100_redondea_como_excel():
    from tp.cifras import de_cada_100
    assert de_cada_100(0.052) == "95" and de_cada_100(0.042) == "96" and de_cada_100(0.019) == "98"
    assert de_cada_100(0.025) == "98"  # 97,5 → 98 (mitad hacia arriba)
