# EIC 5. Cuánto puede retirar Valentina y dónde conviene que viva

Fecha de corte: 20/11/2026. Sale de `python -m tp.correr --etapa 5` (salida completa en `outputs/checkpoint5.txt`, números en `outputs/resumen.json`). Son 10.000 escenarios simulados en dólares de hoy, con la cartera final, los retornos de largo plazo del escenario base (sin views), impuestos por activo con la ganancia de capital pagada al vender, los costos propios de los fondos, la comisión por tramos y Bienes Personales. Cuántos años vive sale de una tabla de mortalidad (esperanza de vida 88 años). En los dos escenarios de vivienda se usan los mismos mercados y las mismas vidas. Los montos están en dólares de hoy: el sueldo sube con la inflación cada año.

## El retiro como sueldo fijo + bono variable

Valentina cobra todos los meses un **sueldo fijo**: el gasto base de su vivienda, USD {{escenarios.A base.gasto}} si compra y {{escenarios.B base.gasto}} si alquila. Ese monto no se recorta. Encima cobra un **bono variable**, la parte de lujo, que sube cuando la cartera va bien y baja cuando va mal. Así funcionan las barandas de Guyton-Klinger: si el retiro pasa a pesar sobre la cartera más de 20% por encima de la proporción inicial, el retiro total baja 10%, sin perforar nunca el sueldo fijo; si pesa 20% menos, sube 10%. Después de un año negativo, el bono no se ajusta por inflación si la proporción supera la inicial. Para una clienta con poca tolerancia a las caídas, esto cambia la pregunta: en lugar de "¿me puedo quedar sin plata?", pasa a ser "¿cuánto puede bajar mi bono?".

## Probabilidad de quedarse sin plata en vida

| Escenario | Gasto/mes | Sin bono variable (gasto fijo) | Con sueldo fijo + bono | El bono desaparece alguna vez |
|---|---|---|---|---|
| A compra, base | {{escenarios.A base.gasto}} | {{escenarios.A base.ruina_fijo}} | {{escenarios.A base.ruina_bono}} | — |
| A compra, lujo | {{escenarios.A lujo.gasto}} | {{escenarios.A lujo.ruina_fijo}} | **{{escenarios.A lujo.ruina_bono}}** | {{escenarios.A lujo.bono_desaparece}} |
| A compra, alto | {{escenarios.A alto.gasto}} | {{escenarios.A alto.ruina_fijo}} | {{escenarios.A alto.ruina_bono}} | {{escenarios.A alto.bono_desaparece}} |
| B alquila, base | {{escenarios.B base.gasto}} | {{escenarios.B base.ruina_fijo}} | {{escenarios.B base.ruina_bono}} | — |
| B alquila, lujo | {{escenarios.B lujo.gasto}} | {{escenarios.B lujo.ruina_fijo}} | **{{escenarios.B lujo.ruina_bono}}** | {{escenarios.B lujo.bono_desaparece}} |
| B alquila, alto | {{escenarios.B alto.gasto}} | {{escenarios.B alto.ruina_fijo}} | {{escenarios.B alto.ruina_bono}} | {{escenarios.B alto.bono_desaparece}} |

Con gasto fijo, la ruina crece con el horizonte. En A lujo es {{escenarios.A lujo.ruina_85}} a los 85, {{escenarios.A lujo.ruina_95}} a los 95 y {{escenarios.A lujo.ruina_100}} a los 100.

## Retiro máximo seguro (sobrevive en 95 de cada 100 escenarios)

| | Gasto fijo | Sueldo fijo + bono |
|---|---|---|
| A compra (USD {{capital.A}}) | {{retiro_seguro.A: compra.fijo}} por mes | {{retiro_seguro.A: compra.bono}} por mes |
| B alquila (USD {{capital.B}}) | {{retiro_seguro.B: alquila.fijo}} por mes | {{retiro_seguro.B: alquila.bono}} por mes |

Con gasto fijo solo entra el nivel base. El nivel lujo entra con el bono variable en las dos viviendas. El nivel alto no entra en ninguna.

## Prueba de estrés: arrancar con un 2008

Si el primer año repite 2008 (acciones de EE.UU. −37%, Europa −45%, Tesoro +18%), la cartera rinde {{nominal.estres_2008_anio1_nominal}} ese año, en dólares y después de impuestos, y después el mercado vuelve a lo normal. Es una prueba de estrés: el criterio de 5% vale para la simulación base, no para este caso extremo.

| Escenario | Ruina con gasto fijo | Ruina con sueldo fijo + bono | El dinero alcanza |
|---|---|---|---|
| A lujo | {{escenarios.A lujo.ruina_fijo}} → {{escenarios.A lujo.estres_fijo}} | {{escenarios.A lujo.ruina_bono}} → **{{escenarios.A lujo.estres_bono}}** | {{escenarios.A lujo.llegan_estres_bono}} de cada 100 |
| B lujo | {{escenarios.B lujo.ruina_fijo}} → {{escenarios.B lujo.estres_fijo}} | {{escenarios.B lujo.ruina_bono}} → **{{escenarios.B lujo.estres_bono}}** | {{escenarios.B lujo.llegan_estres_bono}} de cada 100 |
| A base | {{escenarios.A base.ruina_fijo}} → {{escenarios.A base.estres_fijo}} | igual | {{escenarios.A base.llegan_estres_bono}} de cada 100 |
| B base | {{escenarios.B base.ruina_fijo}} → {{escenarios.B base.estres_fijo}} | igual | {{escenarios.B base.llegan_estres_bono}} de cada 100 |

Aun arrancando con un 2008, el plan recomendado llega en {{escenarios.A lujo.llegan_estres_bono}} de cada 100 escenarios comprando y en {{escenarios.B lujo.llegan_estres_bono}} alquilando. Comprar sigue ganando.

## Sensibilidades (ruina con gasto fijo)

| | Base | Retornos +1 pp | Retornos −1 pp | Vol 7% | Vol 11% |
|---|---|---|---|---|---|
| Retorno neto, sin views | {{sensibilidades.base (vol 9%).ret_nominal}} | {{sensibilidades.retornos +1 pp.ret_nominal}} | {{sensibilidades.retornos −1 pp.ret_nominal}} | {{sensibilidades.vol 7%.ret_nominal}} | {{sensibilidades.vol 11%.ret_nominal}} |
| A lujo | {{sensibilidades.base (vol 9%).A lujo}} | {{sensibilidades.retornos +1 pp.A lujo}} | {{sensibilidades.retornos −1 pp.A lujo}} | {{sensibilidades.vol 7%.A lujo}} | {{sensibilidades.vol 11%.A lujo}} |
| B lujo | {{sensibilidades.base (vol 9%).B lujo}} | {{sensibilidades.retornos +1 pp.B lujo}} | {{sensibilidades.retornos −1 pp.B lujo}} | {{sensibilidades.vol 7%.B lujo}} | {{sensibilidades.vol 11%.B lujo}} |
| Retiro seguro A (gasto fijo) | {{sensibilidades.base (vol 9%).seguro A: compra}} | {{sensibilidades.retornos +1 pp.seguro A: compra}} | {{sensibilidades.retornos −1 pp.seguro A: compra}} | {{sensibilidades.vol 7%.seguro A: compra}} | {{sensibilidades.vol 11%.seguro A: compra}} |
| Retiro seguro B (gasto fijo) | {{sensibilidades.base (vol 9%).seguro B: alquila}} | {{sensibilidades.retornos +1 pp.seguro B: alquila}} | {{sensibilidades.retornos −1 pp.seguro B: alquila}} | {{sensibilidades.vol 7%.seguro B: alquila}} | {{sensibilidades.vol 11%.seguro B: alquila}} |

Lo que más mueve el resultado son los retornos de largo plazo, no la volatilidad.

## ¿Y si no invierte?

Mismo plan recomendado (compra, nivel lujo, sueldo fijo más bono con las mismas barandas), mismos impuestos, Bienes Personales, mortalidad y escenarios. Cambia solo dónde está la plata y qué costos paga. Patrimonio mediano viva hasta los 100, en millones de dólares de hoy (entre paréntesis, en dólares corrientes).

| | Sin plata en vida | Se acaba la plata (caso central) | A los 60 | A los 75 | A los 90 | El bono desaparece |
|---|---|---|---|---|---|---|
| a. Plata quieta (0% nominal, sin comisión) | {{alternativas.a_quieta.ruina}} | a los {{alternativas.a_quieta.edad_central}} | {{alternativas.a_quieta.patrimonio_60_real}} ({{alternativas.a_quieta.patrimonio_60_nominal}}) | {{alternativas.a_quieta.patrimonio_75_real}} ({{alternativas.a_quieta.patrimonio_75_nominal}}) | {{alternativas.a_quieta.patrimonio_90_real}} ({{alternativas.a_quieta.patrimonio_90_nominal}}) | {{alternativas.a_quieta.bono_desaparece}} |
| b. Todo en letras del Tesoro (sin comisión) | {{alternativas.b_letras.ruina}} | a los {{alternativas.b_letras.edad_central}} | {{alternativas.b_letras.patrimonio_60_real}} ({{alternativas.b_letras.patrimonio_60_nominal}}) | {{alternativas.b_letras.patrimonio_75_real}} ({{alternativas.b_letras.patrimonio_75_nominal}}) | {{alternativas.b_letras.patrimonio_90_real}} ({{alternativas.b_letras.patrimonio_90_nominal}}) | {{alternativas.b_letras.bono_desaparece}} |
| d. Nuestra cartera | {{alternativas.d_cartera.ruina}} | no se acaba | {{alternativas.d_cartera.patrimonio_60_real}} ({{alternativas.d_cartera.patrimonio_60_nominal}}) | {{alternativas.d_cartera.patrimonio_75_real}} ({{alternativas.d_cartera.patrimonio_75_nominal}}) | {{alternativas.d_cartera.patrimonio_90_real}} ({{alternativas.d_cartera.patrimonio_90_nominal}}) | {{alternativas.d_cartera.bono_desaparece}} |

En los escenarios en que la plata se acaba, la edad mediana es {{alternativas.a_quieta.edad_mediana_ruina}} con la plata quieta, {{alternativas.b_letras.edad_mediana_ruina}} en letras y {{alternativas.d_cartera.edad_mediana_ruina}} con la cartera.

![Patrimonio mediano por edad: plata quieta, letras del Tesoro y la cartera](outputs/graficos/k_invertir_vs_no.png){width=100%}

### ¿Y un 50/50 pasivo, sin asesor?

| | Sin plata en vida | A los 90 (USD M de hoy) | El bono desaparece |
|---|---|---|---|
| c. 50/50 de seis índices, sin comisión | {{alternativas.c_benchmark.ruina}} | {{alternativas.c_benchmark.patrimonio_90_real}} | {{alternativas.c_benchmark.bono_desaparece}} |
| e. 50/50 de seis índices, con nuestra comisión | {{alternativas.e_benchmark_comision.ruina}} | {{alternativas.e_benchmark_comision.patrimonio_90_real}} | {{alternativas.e_benchmark_comision.bono_desaparece}} |
| d. Nuestra cartera | {{alternativas.d_cartera.ruina}} | {{alternativas.d_cartera.patrimonio_90_real}} | {{alternativas.d_cartera.bono_desaparece}} |

El 50/50 pasivo sin asesor sale mejor. De c a e se ve el efecto de la comisión; de e a d, el de la asignación (menos acciones, más renta fija que paga 35% sobre todo su retorno, y el filtro de sustentabilidad). Tres razones para presentarlo igual como la vara y no como la alternativa:

- El 50/50 no cumple el mandato de la clienta: SPY y VGK tienen tabaco, petroleras y defensa, que su política excluye. Es la vara contra la que se mide la cartera, no algo que pueda comprar.
- La simulación no le da ningún crédito a las views del equipo: usa los retornos de largo plazo por clase. Por construcción, solo puede mostrar la diferencia de asignación y la comisión. Es conservadora a propósito.
- Lo que paga la comisión no es retorno: es el plan de retiro con barandas, la gestión impositiva, el rebalanceo y la contención en las caídas, que para una clienta de compostura baja es lo que evita vender en el peor momento.

## Si cambian los impuestos

El caso base sigue la ley vigente, incluida la baja de Bienes Personales a 0,25% desde 2027. Nivel lujo comprando, con sueldo fijo más bono:

| Escenario impositivo | Sin plata en vida | Retiro seguro con bono (USD/mes) |
|---|---|---|
| Ley vigente | {{impuestos.base.ruina_bono}} | {{impuestos.base.seguro_bono}} |
| Bienes Personales queda en 0,75% para siempre | {{impuestos.bp_fijo.ruina_bono}} | {{impuestos.bp_fijo.seguro_bono}} |
| Intereses y dividendos 40%, ganancias de capital 20% | {{impuestos.alicuotas_altas.ruina_bono}} | {{impuestos.alicuotas_altas.seguro_bono}} |
| Las dos cosas | {{impuestos.ambos.ruina_bono}} | {{impuestos.ambos.seguro_bono}} |

El riesgo impositivo principal es que un gobierno futuro revierta la baja de Bienes Personales: es el que más mueve el resultado. Es el motivo del seguimiento con el contador: si la ley cambia, el plan se recalcula y se ajusta el bono antes de que la probabilidad pase el 5%.

## Recomendación: comprar (escenario A)

A gana en todas las comparaciones: menos ruina, más retiro seguro con bono variable y mejor resistencia a un 2008. El motivo es el **alquiler implícito**. Comprar le ahorra a Valentina USD {{nominal.alquiler_implicito_mes}} por mes: el alquiler de 4.500 menos ABL (300) y mantenimiento (600), que paga solo la dueña; las expensas las pagan las dos. Son {{nominal.depto_real}} real por año sobre un depto de USD 1 M, {{nominal.depto}} en dólares, que no paga impuesto a las ganancias. La cartera rinde {{nominal.neto_cartera}} en dólares después de impuestos y de los costos de los fondos, sin contar las views, y menos después de la comisión y Bienes Personales. Por eso, poner ese millón en la casa rinde más que invertirlo.

En contra de comprar: el depto concentra riesgo en un solo inmueble, no tiene liquidez y cuesta 7,5% de gastos de compra (USD 75.000, ya descontados del capital de A). Suponemos que mantiene su valor real; no contamos con que se valorice.

**Propuesta a Valentina:** comprar el depto y vivir con un sueldo fijo de USD {{escenarios.A base.gasto}} por mes más un bono variable que arranca en USD 6.850 (nivel lujo, {{escenarios.A lujo.gasto}} en total). La probabilidad de quedarse sin plata en vida es {{escenarios.A lujo.ruina_bono}}; como prueba de estrés, con un 2008 de entrada el dinero alcanza en {{escenarios.A lujo.llegan_estres_bono}} de cada 100 escenarios. A cambio, hay una probabilidad de {{escenarios.A lujo.bono_desaparece}} de que en algún momento el bono desaparezca y viva un tiempo con el sueldo fijo. La decisión es de ella.
