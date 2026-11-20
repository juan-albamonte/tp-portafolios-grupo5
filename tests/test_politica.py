"""La política de inversión (docs/entregables/politica_de_inversion.md) está escrita a mano: sus cifras del
modelo tienen que coincidir con outputs/cifras.json. Si cambia el modelo y falla, actualizar el texto y el .docx."""
import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
POLITICA = RAIZ / "docs" / "entregables" / "politica_de_inversion.md"
CIFRAS = RAIZ / "outputs" / "cifras.json"

pytestmark = pytest.mark.skipif(not CIFRAS.exists(), reason="falta outputs/cifras.json: correr python -m tp.correr")


def esperadas() -> list[str]:
    c = json.loads(CIFRAS.read_text(encoding="utf-8"))
    K, E, A, I, M = c["cartera"], c["escenarios"], c["costos_cliente"]["A"], c["impuestos"], c["monitoreo"]
    return [
        f"{K['bruto']} anual antes de impuestos y {K['neto_completo']} después de impuestos y de los costos de los fondos",
        f"acciones ({K['realizacion']} por año",
        f"sube de {I['base']['ruina_bono']} a {I['bp_fijo']['ruina_bono']}",
        f"Riesgo de quedarse sin dinero en vida: {E['A lujo']['ruina_bono']}",
        f"el dinero alcanza en {E['A lujo']['llegan_estres_bono']} de cada 100 escenarios",
        f"por debajo del {c['misma_vara']['benchmark_indices']['vol']} del benchmark",
        f"Volatilidad esperada: {c['misma_vara']['benchmark_indices']['vol']} anual",
        f"| Total | USD {A['total_usd']} ({A['total_pct']})",
        f"habrían rebalanceado {M['literal_rebalanceos']} veces",
        f"son {M['rebalanceos']} rebalanceos en {M['anios']} años y {M['rotacion_anual']} de rotación",
    ]


@pytest.mark.parametrize("frase", esperadas() if CIFRAS.exists() else [])
def test_cifra_de_la_politica_coincide_con_el_modelo(frase):
    assert frase in POLITICA.read_text(encoding="utf-8"), f"la política no dice «{frase}»: actualizarla"
