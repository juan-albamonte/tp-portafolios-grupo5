# TP final de Administración de Portafolios · Grupo 5 · UdeSA, primavera 2026

Cartera para Valentina: 35 años, USD 15 millones, vive de la cartera y tiene restricciones ESG. Este repo tiene el modelo completo y los entregables que se generan desde él.

## Qué hay acá

| Carpeta | Qué tiene |
|---|---|
| `tp/` | El modelo en Python: universo y filtro ESG, Σ de Ledoit-Wolf, Black-Litterman (Meucci, 2010), optimización, HRP, Monte Carlo del retiro (Gompertz, Guyton-Klinger), impuestos, comisiones, monitoreo, gráficos y planilla |
| `data/` | Datos de entrada: precios diarios 2016-2026, notas ESG de S&P Global, views, presupuesto, gastos de los fondos |
| `docs/eic/` | Economía, industria y compañías: el research detrás de las views |
| `docs/entregables/` | Política de inversión, desarrollo, deck y guion (los `.md` y `.js` son la fuente; los `.docx` y `.pptx`, el resultado) |
| `tests/` | Pruebas del modelo y de que las cifras de los entregables coincidan con el modelo |

## Regla importante

Todas las cifras salen de una sola fuente: `outputs/cifras.json`, que arma `tp/cifras.py`. El deck, el guion, el desarrollo, la política y la planilla leen de ahí, y los tests verifican que coincidan.

Para cambiar un número (un supuesto, un peso, el retiro), cambialo en el modelo o en `data/` y regenerá todo. No lo cambies a mano en un entregable: quedaría distinto del resto y los tests lo marcan.

## Cómo correrlo

Requiere Python 3.13 y Node (este último solo para el deck).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m tp.correr                    # regenera outputs/: cartera, Monte Carlo, gráficos, planilla, cifras.json
python docs/entregables/armar_desarrollo.py
cd docs/entregables/deck && npm install && node build_deck.js && cd -
pytest                                 # unos 250 tests
```

La versión para leer y editar el texto está en la carpeta de Google Drive del grupo.
