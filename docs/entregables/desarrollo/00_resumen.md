# Resumen

Valentina tiene 35 años y USD 15 millones, no tiene ingresos y vive de la cartera. El trabajo responde tres preguntas:

1. qué cartera le conviene;
2. cuánto puede retirar por mes sin riesgo serio de quedarse sin dinero en vida;
3. si le conviene comprar o alquilar su vivienda.

Convención de unidades. Los retornos se informan en dólares nominales. Los montos de gasto, retiro y patrimonio de la simulación se informan en dólares de hoy, porque el sueldo de Valentina sube con la inflación todos los años (inflación de largo plazo de {{nominal.inflacion}}). Cuando una cifra está en términos reales, se aclara.

## La cartera

Tiene 12 posiciones: cuatro fondos de renta fija y un fondo amplio de acciones de EE.UU. con filtro de sustentabilidad, que suman 76,5%, más siete acciones elegidas por análisis fundamental, que suman 23,5%.

| | Liquidez | Tesoro | Bonos ajustados por inflación | Corporativos | Acciones EE.UU. | Acciones Europa |
|---|---|---|---|---|---|---|
| Cartera | 10,0% | 21,5% | 20,0% | 5,0% | 33,5% | 10,0% |
| Benchmark | 5% | 20% | 10% | 15% | 40% | 10% |

- Retorno esperado con las opiniones del equipo: {{cartera.bruto}} anual antes de impuestos y {{cartera.neto_completo}} después de impuestos y de los costos de los fondos. Volatilidad: {{cartera.vol}}.
- Contra el benchmark 50/50 pasivo, con la misma vara (misma covarianza, retornos de largo plazo sin opiniones, mismos impuestos y costos), tiene menos riesgo: {{misma_vara.cartera.vol}} contra {{misma_vara.benchmark_indices.vol}} de volatilidad. En la peor crisis de los últimos 20 años (de pico a valle entre octubre de 2007 y marzo de 2009, con el rebalanceo de la política) habría caído {{misma_vara.caidas_2008.maxima_caida_rebalanceo.cartera}}, contra {{misma_vara.caidas_2008.maxima_caida_rebalanceo.benchmark}} del 50/50.
- El precio es retorno: sin contar las opiniones del equipo, la cartera rinde {{misma_vara.cartera.neto}} contra {{misma_vara.benchmark_indices.neto}} después de impuestos. La diferencia, {{misma_vara.menos_neto_pp}} puntos por año, viene del filtro de sustentabilidad y de tener menos acciones.
- Los pesos salen de un modelo de Black y Litterman, que combina el equilibrio del mercado con siete opiniones del equipo, y de una optimización después de impuestos dentro de los rangos de la política de inversión.

## El retiro

El retiro se arma como un sueldo fijo, el gasto base de la vivienda, más un bono variable que sube y baja con la cartera según reglas fijadas de antemano. Con 10.000 escenarios simulados:

| Escenario | Gasto mensual | Sin plata en vida, gasto fijo | Sin plata en vida, sueldo fijo + bono |
|---|---|---|---|
| Compra, nivel base | USD {{escenarios.A base.gasto}} | {{escenarios.A base.ruina_fijo}} | {{escenarios.A base.ruina_bono}} |
| Compra, nivel lujo | USD {{escenarios.A lujo.gasto}} | {{escenarios.A lujo.ruina_fijo}} | {{escenarios.A lujo.ruina_bono}} |
| Alquila, nivel lujo | USD {{escenarios.B lujo.gasto}} | {{escenarios.B lujo.ruina_fijo}} | {{escenarios.B lujo.ruina_bono}} |

Qué hace la simulación: el 1 de enero de cada año fija el sueldo con las barandas, saca de golpe los 12 sueldos del año (el primer año, 21.700 × 12 = 260.400), descuenta comisión y Bienes Personales, y aplica a lo que queda el rendimiento de ese año, ya neto de impuestos y de los gastos de los fondos.

## La recomendación

Comprar el departamento y vivir con un sueldo fijo de USD {{escenarios.A base.gasto}} por mes más un bono que arranca en USD 6.850.

- La probabilidad de quedarse sin dinero en vida es {{escenarios.A lujo.ruina_bono}}: el dinero alcanza en {{escenarios.A lujo.llegan_bono}} de cada 100 escenarios. Como prueba de estrés, si el primer año repite 2008, alcanza en {{escenarios.A lujo.llegan_estres_bono}} de cada 100.
- Comprar le gana a alquilar porque el alquiler que se ahorra (USD {{nominal.alquiler_implicito_mes}} por mes) rinde {{nominal.depto}} por año en dólares sobre el valor del departamento, contra {{nominal.neto_cartera_1d}} de la cartera después de impuestos y costos, sin contar las opiniones del equipo.
- Invertir es lo que hace posible el plan: con la plata quieta se acabaría a los {{alternativas.a_quieta.edad_central}} años y todo en letras del Tesoro, a los {{alternativas.b_letras.edad_central}}.
- El costo es que en {{escenarios.A lujo.bono_desaparece}} de los escenarios el bono desaparece en algún momento.
- Los costos del servicio son USD {{costos_cliente.A.total_usd}} por año ({{costos_cliente.A.total_pct}} del capital), todo incluido y ya descontado en estas cifras.
