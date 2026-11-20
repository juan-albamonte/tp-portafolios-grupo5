# EIC 4. La cartera final

Fecha de corte: 16/11/2026. Sale de `python -m tp.correr --etapa 4` (salida completa en `outputs/checkpoint4.txt`, pesos y USD en `outputs/cartera.csv`). Retornos: Black-Litterman de mercado (Meucci 2010) con las 7 views de `03_companias.md`, después de impuestos. Riesgo: Σ de Ledoit-Wolf con retornos diarios de 10 años.

## Qué compra Valentina

Máximo retorno después de impuestos con volatilidad de 9%, dentro de los rangos de la política, con estas reglas: 5% como máximo por acción, 30% por fondo, ESGV con al menos 20%, Europa con al menos 10% y acción individual en 0 o con al menos 2%.

| Clase | Activo | Peso | USD en A (compra) | USD en B (alquila) |
|---|---|---|---|---|
| Liquidez | BIL | 10,0% | 1.392.500 | 1.500.000 |
| Tesoro | IEF | 21,5% | 2.992.142 | 3.223.133 |
| TIPS | SCHP | 20,0% | 2.785.000 | 3.000.000 |
| Corporativos | VCEB | 5,0% | 696.250 | 750.000 |
| Acciones EE.UU. | ESGV | 20,0% | 2.785.000 | 3.000.000 |
| | LLY | 5,0% | 696.250 | 750.000 |
| | NVDA | 4,4% | 614.015 | 661.416 |
| | V | 2,1% | 292.843 | 315.451 |
| | ETN | 2,0% | 278.500 | 300.000 |
| Acciones Europa | NVS | 5,0% | 696.250 | 750.000 |
| | ASML | 3,0% | 417.750 | 450.000 |
| | RELX | 2,0% | 278.500 | 300.000 |

En total son 12 posiciones: renta fija 56,5% y acciones 43,5%. El retorno esperado es {{cartera.bruto}} bruto y {{cartera.neto_completo}} neto de impuestos y de los costos de los fondos, con vol de {{cartera.vol}} y tracking error de {{misma_vara.tracking_error}} contra el benchmark de seis índices. MA y PG quedaron en 0 (ver `03_companias.md`).

## Por qué quedó así

La restricción que más manda es la de volatilidad: el 9% está al máximo. Todo lo demás se acomoda alrededor de ella.

- **Liquidez 10%, en el máximo.** BIL casi no tiene volatilidad: cada punto en BIL deja lugar para otro punto en acciones sin pasarse del 9%. Además cubre la reserva de dos años de gasto, que es de 2,6% a 6,0% de la cartera según el escenario.
- **TIPS 20%, en el máximo.** Lo empuja la view V6 (los TIPS le ganan al Tesoro con inflación de 4%). Si se saca esa view, los TIPS bajan a 11% y el Tesoro sube a 30%. Es la view que más mueve la cartera.
- **Corporativos 5%, en el mínimo.** Pesa la view V7 (el spread de 0,89% no paga el riesgo) y también el impuesto: con 35% sobre todo el cupón, el crédito rinde casi lo mismo que el Tesoro después de impuestos y tiene más riesgo.
- **Tesoro 21,5%.** Es lo que sobra de la renta fija y el lastre que permite cumplir el 9%.
- **EE.UU. 33,5%.** ESGV está en el piso de 20%: las views comparan acciones contra ESGV, así que el optimizador lo usa como fuente de fondos. LLY llega al tope de 5% por la view de salud (V3). NVDA tiene la view más fuerte (V1, muy alcista), pero con 50% de volatilidad queda en 4,4%. V y ETN entran con lo justo por sus views (V4 y V5).
- **Europa 10%, en el mínimo.** NVS llega al tope de 5% porque recibe dos views, la de salud (V3) y la de Europa (V2). ASML suma 3% y RELX 2%.

**Qué view mueve qué.** Si se saca una view por vez, la rotación contra la cartera final queda así:
- V6 (TIPS): 8,8%.
- V1 (NVDA): 8,4%.
- V3 (salud): 7,7%.
- V4 (pagos): 4,3%.
- V7 (crédito): 2,1%.
- V5 (ETN): 2,0%.
- V2 (Europa): 1,6%.

Los pesos por clase son robustos. Los pesos por acción no: entre una acción y otra de EE.UU. el optimizador está casi indiferente. Por ejemplo, forzar MA al 2% cuesta 0,004 pp de retorno.

## Contra las alternativas (mismas restricciones)

Todas las carteras se evalúan con el mismo retorno esperado (el posterior de Black-Litterman, con las views), después de impuestos con la ganancia de capital pagada al vender y de los costos de los fondos.

| | Final (con views) | Equilibrio sin views | HRP ajustado | Mínima varianza | 50/50 con nuestros activos |
|---|---|---|---|---|---|
| Retorno neto | {{cartera.comparacion.BL c=1 (final).neto_completo}} | {{cartera.comparacion.Equilibrio (c→0).neto_completo}} | {{cartera.comparacion.HRP ajustado.neto_completo}} | {{cartera.comparacion.Mín. varianza.neto_completo}} | {{cartera.comparacion.Neutro (50/50).neto_completo}} |
| Volatilidad | {{cartera.comparacion.BL c=1 (final).vol}} | {{cartera.comparacion.Equilibrio (c→0).vol}} | {{cartera.comparacion.HRP ajustado.vol}} | {{cartera.comparacion.Mín. varianza.vol}} | {{cartera.comparacion.Neutro (50/50).vol}} |

- **Equilibrio:** el mismo optimizador sin views. Con el mismo riesgo, las views suman la diferencia de retorno neto.
- **HRP ajustado:** rinde más porque toma más riesgo. No usa retornos esperados y, ajustado a los rangos, termina por encima del objetivo de volatilidad. El HRP sin ajustar pone 99,6% en BIL.
- **Mínima varianza:** baja el riesgo a 6,5%, pero el retorno neto no alcanza para el retiro.
- **50/50 con nuestros activos:** la cartera neutra del modelo, con las proporciones del benchmark armadas con los 14 activos: Europa en tres acciones sueltas (ASML 6,1%) y EE.UU. en ESGV más acciones. Por eso tiene {{cartera.comparacion.Neutro (50/50).vol}} de volatilidad, más que el benchmark de seis índices. No es el benchmark de la política: la comparación contra el benchmark va en la sección siguiente.

## Contra el benchmark, con la misma vara

Para comparar con el benchmark de la política (los seis índices) se usa una sola vara para los dos: la covarianza de Ledoit-Wolf estimada en conjunto sobre los 14 activos y los seis índices (2016-2026, retornos diarios), los retornos de largo plazo por clase del escenario económico (sin views), los mismos impuestos y los costos de los fondos.

| | Nuestra cartera | 50/50 de seis índices |
|---|---|---|
| Volatilidad esperada | {{misma_vara.cartera.vol}} | {{misma_vara.benchmark_indices.vol}} |
| Retorno neto esperado, sin views | {{misma_vara.cartera.neto}} | {{misma_vara.benchmark_indices.neto}} |
| Sharpe (bruto) | {{misma_vara.cartera.sharpe}} | {{misma_vara.benchmark_indices.sharpe}} |
| Retorno neto con views (el 50/50 armado con nuestros activos) | {{misma_vara.con_views.cartera}} | {{misma_vara.con_views.benchmark}} |

La crisis de 2007-2009 medida de cuatro formas, con la misma regla para las dos carteras: cada posición con su propio retorno si cotizó todo el período (SCHP y V van con el índice de su clase), nominal, antes de impuestos y sin retiros.

| Crisis 2007-2009 | Nuestra cartera | 50/50 | Diferencia sobre USD {{capital.A}} |
|---|---|---|---|
| Año 2008, pesos fijos | {{misma_vara.caidas_2008.anio_2008_fijos.cartera}} | {{misma_vara.caidas_2008.anio_2008_fijos.benchmark}} | USD {{misma_vara.caidas_2008.anio_2008_fijos.diferencia_usd}} |
| Año 2008, con el rebalanceo de la política | {{misma_vara.caidas_2008.anio_2008_rebalanceo.cartera}} | {{misma_vara.caidas_2008.anio_2008_rebalanceo.benchmark}} | USD {{misma_vara.caidas_2008.anio_2008_rebalanceo.diferencia_usd}} |
| De pico a valle (oct-2007 a mar-2009), pesos fijos | {{misma_vara.caidas_2008.maxima_caida_fijos.cartera}} | {{misma_vara.caidas_2008.maxima_caida_fijos.benchmark}} | USD {{misma_vara.caidas_2008.maxima_caida_fijos.diferencia_usd}} |
| De pico a valle, con el rebalanceo de la política | {{misma_vara.caidas_2008.maxima_caida_rebalanceo.cartera}} | {{misma_vara.caidas_2008.maxima_caida_rebalanceo.benchmark}} | USD {{misma_vara.caidas_2008.maxima_caida_rebalanceo.diferencia_usd}} |

Con rebalanceo, las dos caen más, porque se compran acciones mientras siguen cayendo. La que se presenta es la última, la que haría la política de verdad.

## Aporte de cada posición al riesgo

El aporte de cada activo a la volatilidad es $w_i (\Sigma w)_i / \sigma_p$, con la covarianza de Ledoit-Wolf; los aportes suman la volatilidad de la cartera.

{{tabla_riesgo}}

- NVIDIA es la apuesta más fuerte medida en riesgo, no en peso: con {{riesgo.activos.NVDA.peso}} de la cartera aporta {{riesgo.activos.NVDA.pct_riesgo}} del riesgo. Es la view muy alcista (V1) y una acción con 50% de volatilidad.
- Dentro de las acciones, Europa pesa {{riesgo.europa_en_acciones}} (benchmark {{riesgo.europa_en_acciones_benchmark}}) y EE.UU. {{riesgo.eeuu_en_acciones}} (benchmark {{riesgo.eeuu_en_acciones_benchmark}}).

## Monitoreo y rebalanceo con historia

Un backtest ilustrativo aplica las reglas de la política a la cartera final con los retornos diarios de 2016 a 2026: revisión el último día hábil de cada mes; rebalanceo al objetivo si una clase se aparta más de 3 puntos, si queda más de {{monitoreo.tolerancia_rango_pp}} puntos fuera de su rango o si una acción supera {{monitoreo.tope_accion_disparo}}. No modela retiros ni impuestos y no es evidencia de performance: muestra cuándo y cuánto se habría operado.

- Las reglas sin tolerancia habrían rebalanceado {{monitoreo.literal_rebalanceos}} veces en {{monitoreo.revisiones}} revisiones, con {{monitoreo.literal_rotacion_anual}} de rotación por año. La cartera óptima está en el borde de cuatro rangos (liquidez y TIPS en el máximo, corporativos y Europa en el mínimo) y dos acciones en el tope de 5%: cualquier movimiento dispara una operación. Por eso la política fija tolerancias para disparar.
- Con las tolerancias: {{monitoreo.rebalanceos}} rebalanceos en {{monitoreo.anios}} años y {{monitoreo.rotacion_anual}} de rotación por año. Casi todos los dispara la clase de acciones de EE.UU.
- Mayor desvío de cada clase en una revisión: {{tabla_desvios}}.
- Ejemplo, {{monitoreo.ejemplos.compra_tras_caida.fecha}}: las acciones de EE.UU. habían caído a {{monitoreo.ejemplos.compra_tras_caida.pesos_clase.acciones de EE.UU.}} de la cartera (objetivo 33,5%). Se vendieron USD {{monitoreo.ejemplos.compra_tras_caida.vende_total_usd}} de bonos y de las posiciones que más pesaban y se compraron acciones. En los 12 meses siguientes, lo comprado rindió {{monitoreo.ejemplos.compra_tras_caida.compra_12m}} y lo vendido {{monitoreo.ejemplos.compra_tras_caida.vende_12m}}.
- Contraejemplo, {{monitoreo.ejemplos.primero.fecha}}: el primer rebalanceo vendió acciones porque habían subido, sobre todo NVIDIA. En los 12 meses siguientes, lo vendido rindió {{monitoreo.ejemplos.primero.vende_12m}} y lo comprado {{monitoreo.ejemplos.primero.compra_12m}}. Rebalancear es disciplina de riesgo: mantiene la cartera en el nivel de volatilidad que eligió la clienta. No siempre gana.
