---
title: "Desarrollo del trabajo práctico"
subtitle: "Cartera de Valentina. Family office, Grupo 5"
date: "Noviembre de 2026"
lang: es-AR
toc-title: "Índice"
---

# Índice {.unnumbered}

- [Resumen](#sec-1)
  - [La cartera](#sec-2)
  - [El retiro](#sec-3)
  - [La recomendación](#sec-4)
- [Metodología](#sec-5)
  - [Datos](#sec-6)
  - [Covarianza: Ledoit y Wolf (2004)](#sec-7)
  - [Retornos esperados: Black y Litterman en la versión de Meucci (2010)](#sec-8)
  - [Impuestos por activo](#sec-9)
  - [Optimización](#sec-10)
  - [Carteras de comparación](#sec-11)
  - [Simulación de retiros](#sec-12)
- [Escenario económico](#sec-13)
  - [Dónde estamos](#sec-14)
  - [Escenario base (12-24 meses)](#sec-15)
  - [Del escenario a los retornos de largo plazo (10-15 años)](#sec-16)
  - [Exceso del benchmark y λ (calibración del equilibrio)](#sec-17)
  - [Riesgos: qué rompe el escenario](#sec-18)
  - [Fuentes](#sec-19)
- [Industrias y selección de acciones](#sec-20)
  - [Tesis por sector](#sec-21)
  - [Screening](#sec-22)
  - [Lista preliminar (9 acciones, 5 europeas, con la regla de sustentabilidad)](#sec-23)
- [La calificación de sustentabilidad](#sec-24)
- [Compañías y opiniones de inversión](#sec-25)
  - [La cartera: 14 activos analizados, 12 posiciones finales](#sec-26)
  - [Fondos](#sec-27)
  - [Acciones de EE.UU.](#sec-28)
  - [Acciones de Europa](#sec-29)
  - [Consideradas y descartadas](#sec-30)
  - [Consideradas, el optimizador no las tomó](#sec-31)
  - [Opiniones de inversión (views)](#sec-32)
  - [Cartera neutra (π = λΣw_b)](#sec-33)
- [La cartera final](#sec-34)
  - [Qué compra Valentina](#sec-35)
  - [Por qué quedó así](#sec-36)
  - [Contra las alternativas (mismas restricciones)](#sec-37)
  - [Contra el benchmark, con la misma vara](#sec-38)
  - [Aporte de cada posición al riesgo](#sec-39)
  - [Monitoreo y rebalanceo con historia](#sec-40)
- [Retiro y vivienda](#sec-41)
  - [El retiro como sueldo fijo + bono variable](#sec-42)
  - [Probabilidad de quedarse sin plata en vida](#sec-43)
  - [Retiro máximo seguro (sobrevive en 95 de cada 100 escenarios)](#sec-44)
  - [Prueba de estrés: arrancar con un 2008](#sec-45)
  - [Sensibilidades (ruina con gasto fijo)](#sec-46)
  - [¿Y si no invierte?](#sec-47)
  - [Si cambian los impuestos](#sec-48)
  - [Recomendación: comprar (escenario A)](#sec-49)
- [Limitaciones](#sec-50)
  - [Retornos de largo plazo](#sec-51)
  - [Distribución de los retornos](#sec-52)
  - [Correlación entre bonos y acciones](#sec-53)
  - [Impuestos simplificados](#sec-54)
  - [Pesos por acción](#sec-55)
  - [Historia completada](#sec-56)
  - [Vivienda](#sec-57)
- [Anexos](#sec-58)
  - [Anexo A. Universo de inversión](#sec-59)
  - [Anexo B. Excluidos por el filtro de sustentabilidad](#sec-60)
  - [Anexo C. Screening de acciones](#sec-61)
  - [Anexo D. Opiniones de inversión](#sec-62)
  - [Anexo E. Cartera final en dólares](#sec-63)
  - [Anexo F. Simulación de retiros por escenario](#sec-64)
  - [Anexo G. Código y reproducción](#sec-65)
- [Bibliografía](#sec-66)
  - [Artículos y libros](#sec-67)
  - [Datos y fuentes de mercado](#sec-68)
  - [Normativa](#sec-69)

# Resumen {#sec-1}

Valentina tiene 35 años y USD 15 millones, no tiene ingresos y vive de la cartera. El trabajo responde tres preguntas:

1. qué cartera le conviene;
2. cuánto puede retirar por mes sin riesgo serio de quedarse sin dinero en vida;
3. si le conviene comprar o alquilar su vivienda.

Convención de unidades. Los retornos se informan en dólares nominales. Los montos de gasto, retiro y patrimonio de la simulación se informan en dólares de hoy, porque el sueldo de Valentina sube con la inflación todos los años (inflación de largo plazo de 2,25%). Cuando una cifra está en términos reales, se aclara.

## La cartera {#sec-2}

Tiene 12 posiciones: cuatro fondos de renta fija y un fondo amplio de acciones de EE.UU. con filtro de sustentabilidad, que suman 76,5%, más siete acciones elegidas por análisis fundamental, que suman 23,5%.

| | Liquidez | Tesoro | Bonos ajustados por inflación | Corporativos | Acciones EE.UU. | Acciones Europa |
|---|---|---|---|---|---|---|
| Cartera | 10,0% | 21,5% | 20,0% | 5,0% | 33,5% | 10,0% |
| Benchmark | 5% | 20% | 10% | 15% | 40% | 10% |

- Retorno esperado con las opiniones del equipo: 6,55% anual antes de impuestos y 5,22% después de impuestos y de los costos de los fondos. Volatilidad: 9,0%.
- Contra el benchmark 50/50 pasivo, con la misma vara (misma covarianza, retornos de largo plazo sin opiniones, mismos impuestos y costos), tiene menos riesgo: 9,0% contra 9,5% de volatilidad. En la peor crisis de los últimos 20 años (de pico a valle entre octubre de 2007 y marzo de 2009, con el rebalanceo de la política) habría caído −24,6%, contra −30,5% del 50/50.
- El precio es retorno: sin contar las opiniones del equipo, la cartera rinde 5,12% contra 5,50% después de impuestos. La diferencia, 0,38 puntos por año, viene del filtro de sustentabilidad y de tener menos acciones.
- Los pesos salen de un modelo de Black y Litterman, que combina el equilibrio del mercado con siete opiniones del equipo, y de una optimización después de impuestos dentro de los rangos de la política de inversión.

## El retiro {#sec-3}

El retiro se arma como un sueldo fijo, el gasto base de la vivienda, más un bono variable que sube y baja con la cartera según reglas fijadas de antemano. Con 10.000 escenarios simulados:

| Escenario | Gasto mensual | Sin plata en vida, gasto fijo | Sin plata en vida, sueldo fijo + bono |
|---|---|---|---|
| Compra, nivel base | USD 14.850 | 1,3% | 1,3% |
| Compra, nivel lujo | USD 21.700 | 12,5% | 1,9% |
| Alquila, nivel lujo | USD 25.300 | 17,2% | 4,2% |

Qué hace la simulación: el 1 de enero de cada año fija el sueldo con las barandas, saca de golpe los 12 sueldos del año (el primer año, 21.700 × 12 = 260.400), descuenta comisión y Bienes Personales, y aplica a lo que queda el rendimiento de ese año, ya neto de impuestos y de los gastos de los fondos.

## La recomendación {#sec-4}

Comprar el departamento y vivir con un sueldo fijo de USD 14.850 por mes más un bono que arranca en USD 6.850.

- La probabilidad de quedarse sin dinero en vida es 1,9%: el dinero alcanza en 98 de cada 100 escenarios. Como prueba de estrés, si el primer año repite 2008, alcanza en 95 de cada 100.
- Comprar le gana a alquilar porque el alquiler que se ahorra (USD 3.600 por mes) rinde 6,7% por año en dólares sobre el valor del departamento, contra 5,1% de la cartera después de impuestos y costos, sin contar las opiniones del equipo.
- Invertir es lo que hace posible el plan: con la plata quieta se acabaría a los 77 años y todo en letras del Tesoro, a los 98.
- El costo es que en 43% de los escenarios el bono desaparece en algún momento.
- Los costos del servicio son USD 94.255 por año (0,68% del capital), todo incluido y ya descontado en estas cifras.


# Metodología {#sec-5}

El trabajo es un único programa en Python (`python -m tp.correr`). Corre siete etapas en orden y regenera todas las tablas y gráficos de este documento a partir de los datos:

1. universo y filtro de sustentabilidad;
2. datos y estadísticas;
3. análisis de economía, industrias y compañías;
4. Black y Litterman y optimización;
5. simulación de retiros;
6. gráficos;
7. planilla de cálculo.

El código, con sus pruebas automáticas, se entrega junto con este documento.

## Datos {#sec-6}

- Precios. Cierres diarios ajustados por dividendos y divisiones de acciones, de Yahoo Finance, entre junio de 2007 y octubre de 2026.
- Benchmark. Las estadísticas históricas usan los seis índices de referencia (BIL, IEF, TIP, LQD, SPY y VGK), que tienen historia completa desde antes de la crisis de 2008.
- Covarianza de la cartera. Se estima con los últimos diez años de retornos diarios de los 14 activos finales: 2.514 días, de noviembre de 2016 a octubre de 2026.
- Fondos más nuevos. Dos fondos nacieron después del inicio de la ventana. Antes de su lanzamiento se completaron con el índice de su clase: VCEB con LQD (correlación diaria 0,988 en el período común) y ESGV con SPY (0,992).
- Tasas e inflación. Vienen de FRED (Reserva Federal de St. Louis).

![Valor de USD 100 invertidos en cada índice del benchmark desde 2007](outputs/graficos/j_historia.png){width=100%}

![Correlaciones diarias entre las clases de activo](outputs/graficos/i_correlaciones.png){width=85%}

## Covarianza: Ledoit y Wolf (2004) {#sec-7}

Con 14 activos, la matriz de covarianzas muestral tiene 105 correlaciones estimadas con error, y el optimizador tiende a explotar justamente esos errores. Ledoit y Wolf (2004) proponen achicar la matriz muestral $S$ hacia un objetivo $F$ con todas las correlaciones iguales al promedio:

$$\Sigma = \delta F + (1-\delta) S$$

La intensidad $\delta$ se elige para minimizar el error esperado y sale de los datos: 0,024 con retornos diarios. Con 2.514 días el ruido es bajo y el ajuste es chico. Con retornos mensuales (120 meses) daría 0,22. Esta matriz se usa para la restricción de volatilidad, para el modelo de retornos y para la simulación.

## Retornos esperados: Black y Litterman en la versión de Meucci (2010) {#sec-8}

Black y Litterman (1992) parten del equilibrio. Si el mercado está en equilibrio, los retornos esperados son los que hacen óptima la cartera neutra $w_b$:

$$\pi = \lambda \, \Sigma \, w_b, \qquad \lambda = \frac{e_b}{w_b' \Sigma w_b}$$

donde $e_b$ es el exceso esperado del benchmark sobre la tasa corta de largo plazo.

- Cartera neutra. Respeta los pesos por clase del benchmark 50/50. Dentro de cada clase, la renta fija va en partes iguales, las acciones por capitalización y el fondo amplio de EE.UU. se queda con el resto del mercado.
- Aversión al riesgo. $\lambda$ sale del escenario económico: el benchmark rinde 3,53% por encima de la tasa corta de largo plazo, lo que da $\lambda = 3,06$.

Sobre ese equilibrio se agregan las siete opiniones del equipo. Se usa la formulación de mercado de Meucci (2010, sección 3), que trabaja directamente con la distribución de los retornos y no necesita el parámetro $\tau$ de la versión original:

$$\mu = \pi + \Sigma P'\left(P \Sigma P' + \Omega\right)^{-1}\left(v - P\pi\right)$$

- Las opiniones van en $P$ (qué activos compara cada una) y en $v$ (cuánto espera el equipo).
- Las opiniones son cualitativas (Meucci, ecuación 11). Cada una lleva una intensidad $\eta \in \{-2,-1,+1,+2\}$, de muy bajista a muy alcista, y se traduce a número como $v = P\pi + \eta \cdot 0{,}25 \cdot \sqrt{\mathrm{diag}(P\Sigma P')}$: "alcista" es un cuarto de desvío por encima de lo que dice el equilibrio.
- La incertidumbre de cada opinión es $\Omega = \tfrac{1}{c}\mathrm{diag}(u)\, P\Sigma P' \mathrm{diag}(u)$ (ecuación 13). $u$ marca las opiniones menos seguras (1,5 para las de NVIDIA y los bonos ajustados por inflación) y $c$ es la confianza global. Las pruebas automáticas verifican los dos extremos: con $c \to 0$ el modelo devuelve el equilibrio y con $c \to \infty$ cumple las opiniones exactamente.

## Impuestos por activo {#sec-9}

La optimización usa retornos después de impuestos de una residente fiscal argentina:

- Renta fija, incluidos los bonos ajustados por inflación: todo el retorno se cobra como interés y paga 35% (el ajuste por inflación del capital también es interés).
- Acciones: el dividendo paga 35%, el máximo entre la retención de EE.UU. de 30% y la tasa argentina. La ganancia de capital paga 15%, pero recién al vender.

Para que el impuesto al vender entre en un modelo anual, se lo convierte en una tasa efectiva. Si cada año se vende una fracción $f$ de cada acción (por rebalanceo y para pagar los retiros) y su precio sube $g$ por año, en el estado estacionario la ganancia sin realizar vale $g(1-f)/(g+f)$ del valor y el impuesto equivale a una tasa anual sobre la suba de precio de

$$t_{ef} = 0{,}15 \cdot \frac{f\,(1+g)}{g+f}$$

- Con $f = 1$ (todo se realiza cada año) es 15%; si nunca se vende, tiende a cero. Una prueba automática verifica la fórmula contra una simulación explícita año por año.
- $f$ se mide con las mismas reglas para cada cartera: un backtest de las reglas de rebalanceo de la política sobre 2016-2026, más las ventas que hacen falta para pagar los retiros por encima de la renta cobrada. Da 12,4% por año en la cartera y 7,3% en el 50/50, que rota menos porque no tiene acciones individuales con tope.
- Para el fondo amplio de EE.UU. la tasa efectiva queda cerca de 10%.
- El optimizador usa el supuesto más conservador: 15% todos los años y sin los costos de los fondos. Con el supuesto de realizar, la cartera óptima cambiaría 0,1% (NVIDIA +0,1 punto, Visa −0,1). Los pesos se mantienen, y todas las cifras de retorno y de la simulación usan el supuesto de realizar y descuentan los costos de los fondos.

Por esto la renta fija pierde más de un tercio de su retorno y las acciones de la cartera, entre 16% y 23%.

## Optimización {#sec-10}

Se maximiza el retorno esperado después de impuestos sujeto a:

- volatilidad de 9% como máximo, con la covarianza de Ledoit y Wolf;
- pesos por clase dentro de los rangos de la política;
- 5% como máximo por acción y 30% por fondo;
- el fondo amplio de EE.UU. con al menos 20%;
- sin ventas en corto y sumando 100%.

La regla de "0 o al menos 2% por acción" convierte al problema en uno con variables discretas. Se resuelve en dos pasos:

1. **Iteración.** Se optimiza, las acciones que quedan entre 0 y 2% se fijan en 0 y se vuelve a optimizar.
2. **Reingreso.** Cada acción que salió se prueba forzada al 2% y vuelve si mejora el resultado.

## Carteras de comparación {#sec-11}

- Equilibrio sin opiniones: el mismo optimizador con $\mu = \pi$.
- Mínima varianza.
- Paridad de riesgo jerárquica (López de Prado, 2016):
  - Agrupa los activos por correlación y reparte el riesgo de arriba hacia abajo, sin usar retornos esperados.
  - Sin restricciones, pone 99,6% en letras del Tesoro (la de menor varianza). Por eso se la ajusta a la cartera más cercana que cumple los rangos.
- El 50/50 armado con nuestros activos (la cartera neutra del modelo de Black y Litterman).

## Simulación de retiros {#sec-12}

- Escenarios. 10.000 escenarios anuales en dólares de hoy (inflación de largo plazo 2,25%).
- Retornos. Para la simulación no se usa el posterior de Black y Litterman, que está pensado para elegir pesos, sino los retornos de largo plazo del escenario económico por clase, convertidos a media aritmética. Se simulan con una distribución lognormal multivariada por activo con la covarianza de Ledoit y Wolf. La cartera se rebalancea cada año.
- Costos. Se aplican los impuestos por activo, los gastos propios de cada fondo (0,076% de la cartera, descontados del retorno del fondo antes de impuestos, como en un fondo real), la comisión por tramos y Bienes Personales (0,75% en 2026 y 0,25% desde 2027, sobre la cartera y el departamento).
- Mortalidad. Ley de Gompertz (1825), la misma que usan Milevsky y Robinson (2005). La probabilidad de seguir viva $t$ años desde la edad $x$ es

  $$S(t) = \exp\!\left(e^{(x-m)/b}\left(1 - e^{t/b}\right)\right), \qquad m = 93,\; b = 9$$

  Da una esperanza de vida de 88 años; 11% llega a los 100. También se evalúan horizontes fijos de 85, 95 y 100 años.

- Ruina. Estando viva, la cartera no alcanza para el retiro del año.
- Retiro máximo seguro. El más alto con ruina de 5% o menos, buscado por bisección sobre los mismos escenarios.
- Barandas de Guyton y Klinger (2006). Si el retiro pasa a pesar más de 20% por encima de su proporción inicial sobre la cartera, baja 10%. Si pesa 20% menos, sube 10%. Después de un año negativo no se ajusta por inflación, si la proporción supera la inicial. Se agrega un piso: el retiro nunca baja del gasto base de la vivienda. Sin piso, la regla recorta indefinidamente y la ruina sería cero por construcción.
- Estrés. El primer año repite los retornos de 2008 de cada clase y después el mercado vuelve a lo normal. Es una prueba de estrés, no se compara contra el criterio de 5%, que vale para la simulación base.
- Controles. Sin retiros ni costos, la mediana del valor a 60 años crece al retorno compuesto teórico de la cartera (diferencia de 0,8 puntos básicos). Con 20.000 escenarios la probabilidad de ruina cambia menos de 1 punto contra 10.000 (error estándar de 0,5 puntos como máximo).

Ejemplo de las barandas con años malos seguidos, en dólares de hoy: 21.700 → 19.530 → 17.577 → 15.819 → 14.850 (piso). Hacen falta cuatro recortes para que pierda el bono entero. Cuando la cartera se recupera y el retiro vuelve a pesar más de 20% menos que su proporción inicial sobre la cartera, sube de a 10%.


# Escenario económico {#sec-13}

Fecha de corte: 15/11/2026. Mercado al 12-13/11/2026.

## Dónde estamos {#sec-14}

| Indicador | EE.UU. | Zona euro | Fuente |
|---|---|---|---|
| Tasa de política | Fed funds 3,75-4,00% (suba en septiembre; mantuvo el 28/10 con un voto por subir) | Depósito BCE 2,50% (subas en junio y septiembre) | Fed, BCE, FRED (DFEDTARU, ECBDFR) |
| Inflación general (interanual) | IPC 4,1% (oct) | HICP 3,75% (sep) | FRED (CPIAUCSL, CP0000EZ19M086NEST) |
| Inflación subyacente | IPC core 2,9% (oct); PCE core 3,1% (sep) | sin energía ni alimentos: 2,5% proyectado 2026 | FRED (CPILFESL, PCEPILFE), BCE |
| Crecimiento 2026 / 2027 (FMI) | 2,3% / 2,3% | 1,1% / 1,2% | FMI, WEO oct-2026 |
| Inflación 2026 / 2027 (FMI) | 3,6% / 2,8% | 3,1% / 2,8% | FMI, WEO oct-2026 |
| PIB último trimestre | 3,4% anualizado (T3) | n/d | FRED (A191RL1Q225SBEA) |
| Desempleo | 4,1% (oct) | n/d | FRED (UNRATE) |
| Letra 3m / UST 2a / UST 10a | 4,14% / 4,86% / 5,10% | | FRED (DTB3, DGS2, DGS10) |
| TIPS 10a real / breakeven 10a / 5y5y | 2,86% / 2,24% / 2,18% | | FRED (DFII10, T10YIE, T5YIFR) |
| Spread IG / HY | 0,89% / 3,20% | | FRED (BAMLC0A0CM, BAMLH0A0HYM2) |
| Brent | USD 92 (+44% interanual) | | FRED (DCOILBRENTEU) |
| EUR/USD | 1,115 | | FRED (DEXUSEU) |
| P/E forward acciones | S&P 500 17,7 (prom. 25 años 16,4) | Europa ex-UK 14,9 (mediana 14,1) | FactSet (05/11); JPM Guide to the Markets (30/09) |

**Lectura.** El shock de energía por la guerra en Medio Oriente subió la inflación general en los dos lados del Atlántico, y la Fed y el BCE volvieron a subir tasas. La subyacente aumentó menos y las expectativas de largo plazo siguen ancladas: el 5y5y está en 2,18%. El crecimiento resiste en EE.UU., empujado por la inversión en IA y por ganancias corporativas que suben 33% en 2026 (FactSet). Europa crece poco más de 1%.

## Escenario base (12-24 meses) {#sec-15}

- **Inflación:** baja de a poco a medida que el petróleo converge a la curva de futuros (USD 78-79 para 2027, FMI). En EE.UU. pasa de 3,6% en 2026 a 2,8% en 2027. En la zona euro, de 3,1% a 2,8%.
- **Tasas:** la Fed sostiene 3,75-4,00% o sube una vez más, y no baja antes de fines de 2027. El BCE se queda en 2,50%. El UST a 10 años se mueve entre 4,75% y 5,25%, y la prima por plazo se mantiene alta (JPM: "rebuilt term premia").
- **Crecimiento:** EE.UU. crece 2,3% por año sin recesión. La zona euro crece 1,1-1,2%, con más gasto público en 2027.
- **Dólar:** se deprecia de a poco, a ~0,5% por año (supuesto de JPM LTCMA 2027 para el retorno de mercados no estadounidenses).
- **Acciones:** el múltiplo de EE.UU. ya bajó a su menor nivel en tres años porque las ganancias crecieron más que los precios. Para 2027 se espera que las ganancias sigan creciendo (+16% de consenso), pero no queda margen para que suba el múltiplo. Europa es más barata y paga más dividendo, pero crece menos.

## Del escenario a los retornos de largo plazo (10-15 años) {#sec-16}

Inflación de largo plazo: **2,25%**, la del breakeven a 10 años (2,24%), coherente con el 5y5y. Estos retornos alimentan el Monte Carlo después de impuestos. El posterior de Black-Litterman se usa solo para optimizar. Con las views elegimos la cartera, pero para ver si le alcanza la plata no contamos con que acertemos.

| Clase | Nominal (compuesto, USD) | Real | Aritmético* | Lógica |
|---|---|---|---|---|
| Liquidez | 3,50% | 1,22% | 3,50% | Tasa real neutral ~1,2% + inflación. Hoy rinde 4,14%, pero la tasa vuelve a la neutral cuando pasa el shock. |
| Tesoro (7-10 años) | 4,80% | 2,49% | 5,03% | A 10 años, un bono de duración parecida rinde lo que paga al entrar (~5,0%). Le resto algo por si la curva se empina. JPM: 4,6%. |
| TIPS | 4,90% | 2,59% | 5,09% | Tasa real 5-10 años 2,64-2,86% + inflación 2,25%. |
| Corporativos IG | 5,50% | 3,18% | 5,87% | Tesoro de duración similar (~4,95%) + spread 0,89% − pérdidas esperadas por default y downgrades ~0,3%. El spread está ajustado: no supongo que se achique. |
| Acciones EE.UU. | 7,00% | 4,65% | 8,73% | Dividendo + recompras ~1,7% + crecimiento real de ganancias ~3% + inflación − ~0,5%/año porque el múltiplo vuelve a su promedio. JPM: 7,5%. |
| Acciones Europa (en USD) | 7,25% | 4,89% | 9,68% | Dividendo 2,7% + recompras ~0,5% + crecimiento real ~1,5% + inflación EUR 2% − múltiplo levemente caro + dólar más débil ~0,5%. |

\* Aritmético = compuesto más la corrección lognormal con la vol histórica de cada clase (≈ σ²/2). Es la media que usan Black-Litterman y el Monte Carlo.

### Contra las gestoras: estamos en rango

Retornos nominales anuales en USD, compuestos. La comparación sirve para ver si estamos en rango; los números de arriba no se tocan.

| Clase | Nosotros (10-15 años) | J.P. Morgan LTCMA 2027 (10-15 años) | Vanguard VCMM (10 años, mediana) | BlackRock CMA (10 años) |
|---|---|---|---|---|
| Liquidez | 3,50% | n/d en lo público | 3,7% | 3,7% |
| Tesoro (7-10 años) | 4,80% | 4,6% (intermedios) | 4,8% (intermedios) | 4,8% (todos los plazos) |
| TIPS | 4,90% | n/d en lo público | 4,4% (1-10 años) | 5,2% |
| Corporativos IG | 5,50% | 6,1% | 5,5% (crédito) | 5,4% (crédito) |
| Acciones EE.UU. | 7,00% | 7,5% (gran capitalización) | 5,8% | 9,0% (MSCI USA) |
| Acciones Europa (USD) | 7,25% | ~7,5%* | 6,3% (desarrollados ex-EE.UU.) | 7,4% (MSCI Europe) |

\* J.P. Morgan publica 7,0% para la zona euro en EUR. Le sumamos ~0,5% por año de dólar más débil, el supuesto de la propia LTCMA. Es una estimación nuestra; el dato en USD está en la matriz, que requiere registro.

Fuentes: J.P. Morgan, comunicado del 19/10/2026 y Guide to the Markets Europe (datos al 05/11/2026). Vanguard, VCMM corrido al 30/09/2026 (tabla de la página "Vanguard Capital Markets Model forecasts", 21/10/2026). BlackRock Investment Institute, planilla de Capital Market Assumptions de agosto 2026 (datos al 30/06/2026).

Las tres casas difieren más entre sí que nosotros de cualquiera. En acciones de EE.UU. van de 5,8% (Vanguard, que ubica la valuación en el percentil 99) a 9,0% (BlackRock, que apuesta a la productividad por IA). Nuestro 7,0% queda en el medio. En renta fija, las cuatro fuentes caen dentro de medio punto en Tesoro y crédito. La mayor diferencia está en TIPS (4,4% en Vanguard contra 5,2% en BlackRock), y nuestro 4,9% sale de la tasa real de mercado más el breakeven.

### Por qué Europa (7,25%) queda arriba de EE.UU. (7,0%)

Europa no queda arriba porque crezca más: crece menos (1,5% real de ganancias contra 3% en EE.UU.). La diferencia sale de tres cosas:

1. **Dividendo.** El índice europeo (VGK) paga 2,95% en efectivo y el S&P 500 (SPY) 1,0%, según Yahoo Finance al 15/11/2026. EE.UU. compensa una parte con recompras, pero el punto de partida en caja es casi 2 puntos mayor en Europa.
2. **Múltiplo.** EE.UU. cotiza a 17,7 veces las ganancias esperadas, contra un promedio de 16,4 en 25 años, y Vanguard ubica su valuación en el percentil 99. Europa ex-Reino Unido cotiza a 14,9 contra una mediana de 14,1. Le restamos ~0,5 puntos por año a EE.UU. porque el múltiplo vuelve hacia su promedio, y casi nada a Europa.
3. **Dólar.** Medimos todo en USD y el escenario base tiene un dólar que se deprecia ~0,5% por año (J.P. Morgan; Vanguard, −0,6%). Eso suma directo al retorno de un activo europeo.

Sumando los bloques: EE.UU. da ~6,5% y Europa ~7,2%. Usamos 7,0% y 7,25%: la suma por bloques llevada hacia lo que proyectan las gestoras (J.P. Morgan 7,5% para EE.UU.; BlackRock 7,4% para Europa). Ese medio punto en EE.UU. es un ajuste de criterio, no sale de un bloque. Las casas no coinciden en el orden. Vanguard pone ex-EE.UU. arriba (6,3% contra 5,8%), J.P. Morgan queda prácticamente igual (7,5% contra ~7,5%) y BlackRock pone EE.UU. arriba (9,0% contra 7,4%). Por eso la diferencia que dejamos es chica: un cuarto de punto. Además, el IPS ya limita Europa a un rango de 10% a 20% porque el riesgo de estancamiento es real.

**Prima por riesgo de acciones sobre el Tesoro: ~2,2 puntos.** Es angosta. Con el Tesoro pagando 5% y las acciones en valuaciones exigentes, la renta fija vuelve a pagar por sí sola, y eso sostiene un benchmark 50/50 para alguien que vive de la cartera.

## Exceso del benchmark y λ (calibración del equilibrio) {#sec-17}

- **Benchmark 50/50:** 6,0% compuesto, 7,0% aritmético.
- **Exceso aritmético sobre la tasa corta de largo plazo:** 7,03% − 3,50% = **3,53%**. Este es el w_b'π del equilibrio.
- **λ implícito:** con la vol histórica del benchmark (10,2%) sería 3,53% / 10,2%² ≈ 3,4. Con la covarianza de Ledoit-Wolf de los 14 activos finales, la cartera neutra tiene 10,7% de vol y λ = **3,06**, que es el que usa el modelo. Los dos están dentro del rango habitual de aversión al riesgo (2-4).
- **Cartera neutra (w_b) a nivel activo**:
  - El 50/50 fija el peso de cada clase.
  - En renta fija, el peso de la clase se reparte en partes iguales entre sus fondos.
  - En acciones de EE.UU., cada acción suelta pesa lo que pesa en el mercado: su capitalización sobre la del universo de ESGV. Esa capitalización total sale implícita de las mayores posiciones del fondo. ESGV se queda con el resto.
  - En Europa, el peso va por capitalización entre las elegidas.

  Así la cartera neutra es el mercado y no una apuesta a 4-6 nombres.

## Riesgos: qué rompe el escenario {#sec-18}

| Riesgo | Señal a mirar | Efecto en la cartera |
|---|---|---|
| Escalada en Medio Oriente: Brent > USD 110 | Brent, breakeven 5 años | Inflación de segunda vuelta, más subas, y acciones y bonos que caen juntos (como en 2022). Los TIPS y la liquidez amortiguan. |
| Se desinfla la expectativa de IA (lo marca el FMI) | Revisiones de ganancias en tecnología, capex de hiperescaladores | Corrección del S&P 500, que está concentrado en tecnología. Pega más en acciones de EE.UU. que en Europa. |
| Fiscal de EE.UU. y prima por plazo (déficit estructural ~4% del PIB, FMI) | UST 10a > 5,5%, subastas | Pérdida en el Tesoro largo. La duración moderada (7-10 años) limita el golpe. |
| Estancamiento europeo | PMI, crédito, HICP core | Retorno más bajo de las acciones europeas (de ahí el rango chico en el IPS). |
| Spreads de crédito ajustados (IG 0,89%) | OAS IG > 1,5% | Corporativos peor que el Tesoro. Por eso no suponemos que el spread se achique. |
| A favor: el petróleo vuelve a USD 78 y la inflación cede antes | Futuros de Brent, IPC core | La Fed baja antes y los bonos suben por precio: el escenario mejora. |

## Fuentes {#sec-19}

- FRED, Federal Reserve Bank of St. Louis: series citadas en la tabla, bajadas el 15/11/2026.
- Federal Reserve, comunicado del FOMC del 28/10/2026.
- BCE, decisiones de política monetaria del 11/06/2026 y del 10/09/2026, con las proyecciones del staff de septiembre (HICP 3,0% / 2,5% / 2,1% y PIB 0,9% / 1,4% / 1,5% para 2026-2028).
- FMI, World Economic Outlook, octubre 2026, y DataMapper (crecimiento e inflación por país). WEO Update de julio 2026 para el supuesto de petróleo.
- J.P. Morgan Asset Management, 2027 Long-Term Capital Market Assumptions, comunicado del 19/10/2026. Guide to the Markets Europe, datos al 30/09/2026.
- FactSet, Earnings Insight, 05-13/11/2026: P/E forward del S&P 500 17,7; ganancias +33% en 2026 y +16% esperado en 2027.
- Vanguard, "Vanguard Capital Markets Model forecasts" (21/10/2026, simulaciones al 30/09/2026) y "Where to find value in the U.S. markets" (21/10/2026).
- BlackRock Investment Institute, Capital Market Assumptions, planilla de agosto 2026 (datos al 30/06/2026).
- Yahoo Finance: rendimiento por dividendo de SPY y VGK, 15/11/2026.


# Industrias y selección de acciones {#sec-20}

Fecha de corte: 15/11/2026. Parte del escenario base del capítulo de escenario económico:

- shock de petróleo (Brent USD 92);
- tasas altas por más tiempo (Fed 3,75-4,00%, UST 10 años 5,10%);
- ciclo de inversión en IA;
- Europa casi estancada (1,1-1,2%);
- dólar que se debilita de a poco.

Energía y defensa no son opciones: el filtro ESG las excluye.

## Tesis por sector {#sec-21}

| Sector | Postura | Por qué | Qué lo rompe |
|---|---|---|---|
| Salud (farma) | Favorecido | La demanda no depende del ciclo ni del petróleo, tiene poder de precio y una cartera de productos fuerte (obesidad, oncología). La farma europea cotiza barata (P/E 9-16) y vende en todo el mundo, así que no depende de la economía europea. | Control de precios de medicamentos en EE.UU. o aranceles a la farma. Vencimientos de patentes. Guerra de precios en GLP-1 (la expectativa de ganancias de Novo ya cae −3%). |
| Tecnología (IA con ganancias reales) | Favorecido | Las ganancias del S&P 500 suben 33% en 2026, empujadas por la inversión de las grandes plataformas en IA. Nos quedamos con las que tienen caja neta y márgenes altos: los semiconductores y los equipos para fabricarlos son lo que la inversión en IA compra. | La inversión en IA se frena (el riesgo que marca el FMI). Tasas más altas que comprimen múltiplos. Restricciones de exportación de chips. |
| Financiero | Favorecido | Las tasas altas por más tiempo sostienen el margen de interés de los bancos, y el BCE ya subió a 2,50%. Visa y Mastercard cobran sobre el gasto nominal: la inflación les suma volumen sin riesgo de crédito. | Recesión con pérdidas de crédito. Curva invertida que aprieta el margen. Regulación de comisiones de tarjeta. |
| Industria (electrificación, información profesional) | Favorecido | Los centros de datos y la red eléctrica necesitan equipos (Eaton). Los servicios de información con suscripción, como RELX, tienen ingresos recurrentes que acompañan la inflación. | Que el ciclo de inversión en IA y en la red se dé vuelta. Que la IA generativa le quite valor a los datos propietarios de RELX. |
| Comunicaciones | Neutral | Las dos (Alphabet y Meta) cobran publicidad con IA, pero gastan fortunas en inversión y están expuestas a la regulación. | — |
| Consumo discrecional | Penalizado | El shock de petróleo le come ingreso real al consumidor, y las tasas altas frenan la vivienda (Home Depot). | El petróleo vuelve a USD 78 y la Fed baja antes. |
| Consumo básico | Penalizado | Los costos de energía y envases suben y los volúmenes no crecen. El mercado lo valúa como un bono, y con tasas al 5% compite contra el Tesoro. | Recesión: ahí lo defensivo gana. Además, el dólar débil ayuda a las europeas que venden en todo el mundo (Unilever). |
| Servicios públicos | Penalizado | Es el sector más sensible a la tasa (NextEra tiene deuda neta de 8 veces el EBITDA) y necesita mucho capital justo cuando el capital es caro. | La demanda eléctrica de los centros de datos supera lo esperado y las tasas bajan. |

Lectura cruzada:

- **Dólar débil:** favorece a las europeas que venden en todo el mundo (ASML, SAP, farma, RELX, Unilever) frente a las que dependen de la economía local.
- **Estancamiento europeo:** pesa sobre los bancos domésticos (ING) más que sobre Santander o HSBC, que tienen negocio en América Latina y Asia.

## Screening {#sec-22}

Universo: las 31 acciones que pasaron el filtro de exclusiones (anexo A). Los datos de mercado vienen de Yahoo Finance al 15/11/2026.

Métricas (entre paréntesis, qué valor es mejor):

- P/E forward (menor).
- Crecimiento esperado de ganancias del próximo ejercicio, según el consenso de analistas (mayor).
- Margen operativo (mayor).
- Deuda neta / EBITDA (menor; no aplica a bancos).
- ROE (mayor).
- Dividendo + recompras sobre capitalización (mayor).
- ESG (mayor).

**Ranking dentro de cada sector.** Cada métrica se convierte en un percentil dentro del sector, y el puntaje es el promedio de esos percentiles. Así un sector favorecido no se come la lista: una farma barata compite contra otras farmas, no contra Nvidia.

**Nota ESG: verificada en la web, con un cambio de fuente.**

- MSCI cerró su buscador público y hoy lo ofrece solo a clientes por MSCI ONE (verificado el 15/11/2026).
- Las páginas por empresa de Sustainalytics redirigen a un formulario.
- La fuente pública que queda por emisor es el **S&P Global ESG Score**, de 0 a 100 y relativo a la industria. Cada puntaje quedó registrado con el link de su empresa:
  - 9 páginas leídas en vivo.
  - 18 tomadas de la página indexada por el buscador; las 3 que también leímos en vivo coincidieron con diferencias de ±1 punto.
  - Meta, J&J y Santander: el puntaje vigente solo se publica en canales pagos o no tiene página. Para esas tres usamos el CSA 2024 del documento público de S&P para el rebalanceo del DJSI, marcado.
  - HSBC no tiene puntaje público.
- Como el puntaje se mide contra pares de la misma industria, sirve para rankear dentro del sector, no entre sectores.

### Resultados

**Regla de sustentabilidad:** la política fija un mínimo de 25 en el ESG de S&P. Salen Amazon (21) y J&J (24, CSA 2024), y quedan 29 acciones. Sin J&J, cuatro farmas empatan en 0,54 (LLY, NVO, NVS, SNY): en salud, el screening no decide y la elección va por tesis.

Div. + recompras = rendimiento por dividendo más recompras del último ejercicio sobre capitalización. Puntaje = promedio de percentiles dentro del sector (0,5 = mitad del sector).

| Sector | Acción | P/E fwd | Crec. ganancias | Margen op. | Deuda neta/EBITDA | ROE | Div. + recompras | ESG S&P | Puntaje | Puesto | Preliminar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Comunicaciones | META | 18,0 | 17% | 38% | 0,3 | 32% | 1,9% | 30 | 0,61 | 1 | calidad propia |
| Comunicaciones | GOOGL | 19,2 | -23% | 33% | -0,6 | 44% | 1,6% | 29 | 0,39 | 2 |  |
| Consumo básico | UL | 17,1 | 7% | 20% | 2,4 | 32% | 4,3% | 50 | 0,61 | 1 | calidad propia |
| Consumo básico | KO | 28,1 | 6% | 32% | 1,5 | 41% | 2,3% | 42 | 0,56 | 2 |  |
| Consumo básico | PG | 23,0 | 6% | 25% | 0,9 | 30% | 3,8% | 37 | 0,50 | 3 |  |
| Consumo básico | DEO | 14,4 | 5% | 29% | 3,2 | 15% | 2,0% | 57 | 0,44 | 4 |  |
| Consumo básico | COST | 44,2 | 10% | 4% | -0,8 | 28% | 0,7% | 41 | 0,39 | 5 |  |
| Consumo discrecional | HD | 21,9 | 6% | 12% | 2,5 | 104% | 2,7% | 39 | 0,50 | 1 |  |
| Financiero | V | 24,8 | 14% | 66% | 0,3 | 64% | 3,3% | 58 | 0,61 | 1 | sector favorecido |
| Financiero | HSBC | 9,6 | 10% | 49% | n/d | 14% | 6,4% | n/d | 0,55 | 2 | sector favorecido |
| Financiero | SAN | 8,7 | 11% | 42% | n/d | 13% | 4,9% | 73 | 0,53 | 3 |  |
| Financiero | MA | 28,5 | 15% | 60% | 0,6 | 231% | 2,6% | 58 | 0,51 | 4 |  |
| Financiero | ING | 10,8 | 9% | 52% | n/d | 18% | 4,0% | 47 | 0,42 | 5 |  |
| Financiero | JPM | 13,5 | 7% | 45% | n/d | 18% | 5,7% | 29 | 0,36 | 6 |  |
| Industria | RELX | 18,9 | 13% | 32% | 2,6 | 132% | 5,1% | 58 | 0,68 | 1 | sector favorecido |
| Industria | ETN | 21,5 | 19% | 18% | 2,8 | 20% | 2,6% | 50 | 0,32 | 2 |  |
| Salud | LLY | 28,5 | 43% | 51% | 1,0 | 86% | 0,8% | 38 | 0,54 | 1 | sector favorecido |
| Salud | NVO | 12,1 | -3% | 51% | 0,5 | 58% | 4,4% | 33 | 0,54 | 2 | sector favorecido |
| Salud | NVS | 16,2 | 10% | 34% | 1,6 | 24% | 6,0% | 58 | 0,54 | 3 |  |
| Salud | SNY | 8,9 | 7% | 22% | 0,9 | 6% | 9,8% | 52 | 0,54 | 4 |  |
| Salud | GSK | 10,2 | 4% | 31% | 1,8 | 28% | 5,4% | 68 | 0,52 | 5 |  |
| Salud | AZN | 16,3 | 12% | 26% | 1,2 | 23% | 1,7% | 69 | 0,48 | 6 |  |
| Salud | UNH | 17,5 | 14% | 6% | 1,6 | 16% | 3,8% | 39 | 0,34 | 7 |  |
| Servicios públicos | NEE | 19,5 | 9% | 30% | 8,1 | 14% | 2,9% | 38 | 0,50 | 1 |  |
| Tecnología | NVDA | 10,3 | 70% | 65% | -0,1 | 117% | 1,6% | 61 | 0,76 | 1 | sector favorecido |
| Tecnología | ASML | 23,6 | 36% | 39% | -0,7 | 66% | 1,8% | 58 | 0,60 | 2 | sector favorecido |
| Tecnología | SAP | 24,6 | 18% | 29% | -0,0 | 18% | 2,0% | 58 | 0,40 | 3 |  |
| Tecnología | MSFT | 21,7 | 21% | 47% | 0,3 | 34% | 1,3% | 46 | 0,39 | 4 |  |
| Tecnología | AAPL | 33,7 | 12% | 33% | 0,2 | 142% | 2,0% | 32 | 0,36 | 5 |  |

Datos que hay que leer con cuidado:

- **NVDA:** el P/E forward de 10,3 usa la ganancia esperada del ejercicio fiscal que cierra en enero de 2028, que crece +70%. Sobre la ganancia de los últimos 12 meses, el P/E es 20,6.
- **GOOGL (y AMZN, ya excluida):** el crecimiento negativo sale de una base 2026 inflada (+81% y +79% contra 2025). La causa más probable es la revaluación de participaciones en otras empresas, no un deterioro del negocio. Las penaliza injustamente en esa métrica.
- **ROE de MA, AAPL, RELX y HD (>100%):** las recompras achicaron el patrimonio, así que el ROE dice poco en estas empresas.
- **Sectores de dos acciones** (Comunicaciones, Consumo discrecional, Industria): el percentil es 0,25 o 0,75 por métrica, así que el ranking ahí es "la mejor de dos".

## Lista preliminar (9 acciones, 5 europeas, con la regla de sustentabilidad) {#sec-23}

Las reglas son:

- **Sector favorecido:** entra la mejor de cada sector favorecido, y la segunda solo si queda en la mitad de arriba (puntaje ≥ 0,5).
- **Calidad propia:** de cada sector no favorecido, entra la mejor si su puntaje es ≥ 0,60.
- **Mínimo europeo:** si quedan menos de 4 europeas, se completa con las de mejor puntaje.

Resultado:

- **Sector favorecido:** NVDA, ASML, RELX, V, HSBC, LLY, NVO.
- **Calidad propia:** UL (consumo básico) y META (comunicaciones).
- **Sin cupo:** HD, ahora sola en su sector, queda en 0,50 y no llega al umbral.

Antes de fijar la regla de sustentabilidad, la lista tenía 10 acciones (6 europeas), con NVS y HD. La selección final, junto con las consideradas y descartadas, está en el capítulo de compañías.


# La calificación de sustentabilidad {#sec-24}

**Qué cambió.** El plan era calificar a cada empresa con el rating de MSCI (escala AAA a CCC) y controlarlo con Sustainalytics. El 15/11/2026 comprobamos que ninguna de las dos fuentes sigue siendo pública:

- **MSCI** cerró su buscador público (*ESG Ratings & Climate Search Tool*). La página ahora dice que los clientes acceden a los datos por la plataforma MSCI ONE.
- **Sustainalytics** redirige las páginas por empresa a un formulario comercial, y Yahoo Finance ya no muestra sus puntajes.

**Fuente que usamos.** El *S&P Global ESG Score*, de 0 a 100. Es la única calificación por emisor que sigue siendo pública. El puntaje se calcula contra empresas de la misma industria, así que compara bien dentro de un sector y mal entre sectores. Cada valor quedó registrado con el link a la página de la empresa.

**Cómo se obtuvo.**

- 9 páginas se leyeron en vivo.
- 18 se tomaron de la página indexada por el buscador. Las 3 que también leímos en vivo coincidieron con diferencias de ±1 punto.
- Meta, Johnson & Johnson y Santander: el puntaje vigente se vende en canales pagos o no tiene página. Para ellas usamos el CSA 2024, publicado por S&P en el documento del rebalanceo del índice de sustentabilidad Dow Jones (DJSI), y lo marcamos.
- HSBC no tiene puntaje público.

**Regla de la política de inversión.**

- Una acción solo puede estar en la cartera si su ESG de S&P es de al menos **25**.
- Si el puntaje vigente no es público, cuenta el último publicado (CSA 2024).
- Una acción sin nota verificada no puede entrar.
- Hoy la regla excluye a Amazon (21) y a Johnson & Johnson (24, CSA 2024). HSBC queda en el universo sin puntaje público y no puede entrar a la cartera.
- El programa no permite seleccionar una acción sin nota verificada.

**Fondos.** No se califican con este puntaje. Se exige que su índice excluya combustibles fósiles, armamento y tabaco, y lo verificamos el 15/11/2026 en las páginas de Vanguard:

- **ESGV** excluye entretenimiento para adultos, alcohol, tabaco, cannabis, juego, armas (controvertidas, nucleares, convencionales y civiles), energía nuclear, y carbón, petróleo y gas.
- **VCEB** aplica las mismas exclusiones a los bonos corporativos.
- Los fondos de Tesoro y TIPS son deuda soberana de EE.UU.


# Compañías y opiniones de inversión {#sec-25}

Fecha de corte: 15/11/2026. Sale del escenario del capítulo de escenario económico y de los sectores y el screening del capítulo de industrias. La nota ESG es el puntaje de S&P Global, con mínimo 25 (ver el capítulo de calificación de sustentabilidad). Los números de cada acción vienen del screening (Yahoo Finance, 15/11). La volatilidad es la anual de retornos diarios en 10 años (2016-2026).

## La cartera: 14 activos analizados, 12 posiciones finales {#sec-26}

Los 14 activos de abajo son los que pasaron a la optimización. Con las reglas de la política de inversión (piso de 20% en ESGV, piso de 10% en Europa, liquidez 3-10%, acción individual 0 o al menos 2%), el optimizador deja 12 posiciones: los 5 fondos más NVDA, V, LLY, ETN, ASML, NVS y RELX. MA y PG quedan en 0 (ver «Consideradas, el optimizador no las tomó»).

**Estructura:**

- 4 fondos de renta fija, uno por clase.
- ESGV como núcleo de acciones de EE.UU.
- 6 acciones de EE.UU. y 3 de Europa.
- Como máximo 2 acciones por sector, contando EE.UU. y Europa juntas.

| Activo | Clase | Sector | Una línea | Veredicto |
|---|---|---|---|---|
| BIL | Liquidez | — | Letras de 1 a 3 meses: la reserva de gasto | — |
| IEF | Tesoro | — | Tesoro de 7 a 10 años, la duración de la clase | — |
| SCHP | TIPS | — | Replica lo mismo que TIP, con comisión de 0,03% contra 0,18% | — |
| VCEB | Corporativos | — | El único fondo de corporativos que pasa el filtro ESG | — |
| ESGV | Acciones EE.UU. | Amplio | El mercado de EE.UU. con filtro ESG | — |
| NVDA | Acciones EE.UU. | Tecnología | El proveedor central de la inversión en IA | Muy alcista |
| ASML | Acciones Europa | Tecnología | Monopolio de la litografía EUV | Alcista |
| V | Acciones EE.UU. | Financiero | Cobra un peaje sobre el gasto nominal | Alcista |
| MA | Acciones EE.UU. | Financiero | La otra red de pagos: mismo peaje, ESG 58 | Alcista |
| LLY | Acciones EE.UU. | Salud | Líder en obesidad, ganancias que crecen 43% | Alcista |
| NVS | Acciones Europa | Salud | Farma barata, de baja volatilidad y con 6% de retorno al accionista | Alcista |
| ETN | Acciones EE.UU. | Industria | Electrificación de centros de datos y de la red | Alcista |
| RELX | Acciones Europa | Industria | Información por suscripción; la mejor de su sector en el screening | Alcista |
| PG | Acciones EE.UU. | Consumo básico | Cobertura deliberada contra el riesgo de IA | Neutral |

Por sector: tecnología 2, financiero 2, salud 2, industria 2 y consumo básico 1. Quedan en cero los tres sectores sin tesis a favor (servicios públicos, consumo discrecional y comunicaciones).

**Veredictos y views.** Muy alcista equivale a η = +2 en la view (+0,5 desvíos) y alcista a η = +1 (+0,25 desvíos). Neutral significa que la acción no lleva view propia y entra a su peso de equilibrio (solo PG). Una acción alcista puede expresarse dentro de una view de canasta en lugar de tener una propia (ASML y RELX van por la view de Europa, LLY por la de salud).

## Fondos {#sec-27}

| Fondo | Comisión anual | Activos | Por qué este y no otro |
|---|---|---|---|
| BIL | 0,135% | USD 48.500 M | Letras de 1 a 3 meses, con historia desde 2007. Se descartó SGOV, que tiene historia corta. |
| IEF | 0,15% | USD 43.500 M | Su plazo de 7 a 10 años es la definición de la clase y del benchmark. IEI (3 a 7 años) tiene menos duración que la que pide la clase. |
| SCHP | 0,03% | USD 17.500 M | Replica los TIPS de todos los plazos, igual que TIP, y cuesta 0,15 puntos menos por año. VTIP (0 a 5 años) es más corto que la clase. |
| VCEB | 0,12% | USD 1.200 M | Es el único fondo de bonos corporativos con exclusión de fósiles y armas (LQD, VCIT y SUSC no pasan el filtro). Opera poco volumen, así que se compra con órdenes límite. |
| ESGV | 0,09% | USD 13.000 M | Mercado de EE.UU. con exclusiones verificadas (el capítulo de calificación de sustentabilidad). ESGU tiene CEDEAR, pero no pasa el filtro de petróleo. |

Comisiones y activos: Yahoo Finance al 15/11/2026.

## Acciones de EE.UU. {#sec-28}

### NVIDIA (NVDA): muy alcista

**Qué hace.** Diseña los procesadores (GPU) y el equipamiento de red con que se entrenan y corren los modelos de IA, más el software que los programa.

**Por qué gana con el escenario.** La inversión en IA de las grandes plataformas empuja buena parte del +33% de ganancias del S&P 500 en 2026, y Nvidia cobra esa inversión. Tecnología es un sector favorecido, y Nvidia es su primera en el screening (puntaje 0,76).

**Números.**

- P/E forward 10,3, sobre el ejercicio que cierra en enero de 2028; 20,6 sobre los últimos 12 meses.
- Crecimiento esperado +70%, margen operativo 65%, caja neta y ROE 117%.
- ESG 61, el más alto de las acciones de EE.UU. elegidas.
- Volatilidad 50%.

**Qué la saca.** Que las grandes plataformas recorten inversión dos trimestres seguidos, o que la guía de crecimiento caiga debajo de 20%. Las restricciones de exportación de chips son el otro riesgo. Con 50% de volatilidad, el tope de 5% por acción es lo que limita el daño.

**View V1:** NVDA contra ESGV, η = +2, con u = 1,5 (menos confianza) porque el freno de la IA es el riesgo número 1 del escenario.

### Visa (V): alcista

**Qué hace.** Opera la red de tarjetas: cobra una comisión por cada transacción. El crédito lo dan los bancos, así que Visa no carga ese riesgo.

**Por qué gana.** Con inflación de 3% a 4% (IPC de 4,1% en octubre), el gasto nominal crece solo y Visa cobra un porcentaje de ese gasto. Las tasas altas no la afectan como a un banco. Es la primera del sector financiero en el screening.

**Números.** P/E forward 24,8, crecimiento 14%, margen 66%, ROE 64%, deuda neta 0,3 veces el EBITDA, retorno al accionista 3,3%, ESG 58 y volatilidad 25%.

**Qué la saca.** Una regulación que ponga techo a las comisiones de tarjeta, o que los pagos instantáneos entre cuentas le saquen volumen.

**View V4:** V contra ESGV, η = +1.

### Mastercard (MA): alcista

**Por qué Mastercard y no JPMorgan.** JPMorgan tiene ESG 29: pasa el mínimo de 25, pero es el mayor financiador de combustibles fósiles y la clienta rechaza las industrias altamente contaminantes. Mastercard tiene ESG 58, verificado en S&P Global (actualizado el 18/03/2026).

**Qué hace.** Opera la segunda red global de tarjetas. Como Visa, cobra por transacción y no presta.

**Por qué gana.** La misma tesis que Visa: un peaje sobre el gasto nominal con inflación de 3% a 4%.

**Números.** P/E forward 28,5, crecimiento 15%, margen 60%, deuda neta 0,6 veces el EBITDA, retorno al accionista 2,6%, ESG 58 y volatilidad 27%.

**El costo, dicho explícitamente.** Financiero queda con dos redes de pago, que son casi el mismo negocio, y la cartera pierde la exposición al margen de interés de los bancos. Aceptamos esa concentración a cambio de cumplir el mandato ESG de la clienta. Las dos pesan como máximo 5% cada una.

**Qué la saca.** Una regulación que ponga techo a las comisiones de tarjeta, o pagos instantáneos entre cuentas que le saquen volumen. Es el mismo riesgo que Visa, así que las dos caen juntas.

**Va en la view V4** (V+MA contra ESGV).

### Eli Lilly (LLY): alcista

**Qué hace.** Es una farmacéutica con el tratamiento líder para obesidad y diabetes (tirzepatida), además de oncología e inmunología.

**Por qué gana.** Salud es un sector favorecido: la demanda no depende del ciclo ni del petróleo. Lilly tiene el mayor crecimiento del sector.

**Números.** P/E forward 28,5, crecimiento esperado 43%, margen 51%, ROE 86%, deuda neta 1,0 veces el EBITDA, retorno al accionista 0,8%, ESG 38 y volatilidad 31%.

**Qué la saca.**

- Una guerra de precios en los medicamentos para obesidad: la ganancia esperada de Novo ya cae 3%.
- Un control de precios de medicamentos en EE.UU.
- El múltiplo es exigente, así que no hay margen para fallar en crecimiento.

**View V3:** LLY y NVS contra ESGV, η = +1.

### Eaton (ETN): alcista

**Qué hace.** Fabrica equipos de distribución y control eléctrico para centros de datos, redes eléctricas, edificios y la industria. Tiene sede legal en Irlanda y opera y cotiza en EE.UU.

**Por qué gana.** Los centros de datos y la modernización de la red necesitan sus equipos. Es la forma de tener la inversión en IA desde la electricidad, no desde el chip.

**Números.** P/E forward 21,5, crecimiento esperado 19% (el mayor de su sector), margen 18%, deuda neta 2,8 veces el EBITDA, retorno al accionista 2,6%, ESG 50 y volatilidad 31%.

En el screening pierde contra RELX (0,32) por margen y deuda. Entra por tesis, y lo decimos.

**Qué la saca.** Que se dé vuelta el ciclo de inversión en centros de datos y en la red. Además, su correlación con ESGV es 0,70: comparte el riesgo de IA con NVDA.

**View V5:** ETN contra ESGV, η = +1.

### Procter & Gamble (PG): neutral

**Qué hace.** Vende productos de consumo masivo: limpieza, higiene y cuidado personal.

**Por qué está, a pesar de un sector penalizado.** Es una cobertura deliberada. NVDA, ASML y ETN dependen de que siga la inversión en IA. PG es la segunda acción de menor volatilidad de las 29 elegibles (19%, detrás de KO con 18,5%) y tiene baja correlación con el mercado (0,41 con ESGV, contra 0,70-0,72 de NVDA, ASML y ETN). Si se desinfla la IA, el riesgo 2 del escenario, PG sostiene.

**Números.** P/E forward 23,0, crecimiento 6%, margen 25%, deuda neta 0,9 veces el EBITDA, retorno al accionista 3,8%, ESG 37.

La elegimos sobre KO (P/E 28,1, retorno 2,3%) y UL (1ª del sector, pero los cupos europeos ya estaban).

**Qué la saca.**

- Que los costos de insumos ligados al petróleo aprieten el margen más de lo que puede trasladar a precios.
- Que se cotice como un bono con el Tesoro al 5% y se estanque.

**Sin view:** está para bajar el riesgo, no para ganarle al mercado.

## Acciones de Europa {#sec-29}

### ASML (Países Bajos): alcista

**Qué hace.** Es el único fabricante de las máquinas de litografía EUV, sin las cuales no se fabrican los chips de vanguardia.

**Por qué gana.** La inversión en IA compra chips, y los chips de vanguardia necesitan sus máquinas. Además vende en todo el mundo y la medimos en dólares, así que el dólar débil le suma. Es la segunda de tecnología en el screening (0,60).

**Números.** P/E forward 23,6, crecimiento esperado 36%, margen 39%, caja neta (deuda neta de −0,7 veces el EBITDA), ROE 66%, retorno al accionista 1,8%, ESG 58 y volatilidad 40%.

**Qué la saca.** Que se amplíen los controles de exportación a China, o que caiga el ciclo de inversión de los fabricantes de chips. Con NVDA concentra la apuesta de semiconductores: por eso tecnología se queda en dos.

**Va en la view V2** (Europa contra EE.UU.).

### Novartis (NVS, Suiza): alcista

**Qué hace.** Es una farmacéutica de medicamentos innovadores (cardiología, oncología, inmunología), concentrada en ese negocio desde que escindió sus genéricos.

**Por qué gana.** Salud es un sector favorecido. Vende en todo el mundo, así que no depende del estancamiento europeo, y cotiza barata. Tiene la menor volatilidad de las farmacéuticas elegibles.

**Números.** P/E forward 16,2, crecimiento 10%, margen 34%, deuda neta 1,6 veces el EBITDA, retorno al accionista 6,0%, ESG 58 (actualizado en diciembre de 2025), volatilidad 20% y correlación de 0,41 con ESGV.

La elegimos entre las farmacéuticas europeas:

- **AstraZeneca:** mismo P/E y mejor ESG (69), pero devuelve 1,7% y tiene volatilidad de 25%.
- **Novo:** se superpone con LLY en obesidad, su ganancia esperada cae 3% y tiene ESG 33 en revisión.

**Qué la saca.** Que vencen patentes de productos grandes, o un control de precios en EE.UU.

**Va en las views V2** (Europa) **y V3** (salud).

### RELX (Reino Unido): alcista

**Qué hace.** Vende información y análisis por suscripción: bases jurídicas, revistas científicas y análisis de riesgo para bancos y aseguradoras.

**Por qué gana.** Sus ingresos son recurrentes y siguen a la inflación, y vende en todo el mundo con un dólar que se debilita. Tiene el segundo puntaje del screening entre las 29 acciones elegibles (0,68, detrás de NVIDIA) y el mejor de su sector.

**Números.** P/E forward 18,9, crecimiento 13%, margen 32%, deuda neta 2,6 veces el EBITDA, retorno al accionista 5,1%, ESG 58 y volatilidad 23%.

**Qué la saca.** Que la IA generativa le quite valor a sus datos propietarios: es el riesgo que el mercado ya mira en esta acción.

**Va en la view V2.**

## Consideradas y descartadas {#sec-30}

| Acción | Por qué no |
|---|---|
| Home Depot (HD) | Contradice el escenario: depende de la vivienda, que sufre con tasas al 5%. Con la regla ESG queda sola en su sector, con puntaje 0,50. |
| Meta (META) | ESG 30, y es un CSA 2024 porque el puntaje vigente no es público. Volatilidad de 40% y controversias regulatorias: no cuadra con una clienta de compostura baja. |
| Microsoft (MSFT) | Tecnología tiene dos cupos y van para NVDA (0,76) y ASML (0,60); MSFT sale 0,39. Igual la tiene a través de ESGV, donde pesa 6,4%. |
| Amazon (AMZN), J&J (JNJ) | Excluidas por la regla ESG (21 y 24). |
| Novo Nordisk (NVO) | Se superpone con LLY en obesidad, su ganancia esperada cae 3% y su ESG (33) está en revisión. |
| AstraZeneca (AZN), GSK | Las dos tienen el mejor ESG del universo (69 y 68). AZN es la alternativa a NVS si pesa más el ESG. GSK crece 4%. |
| UnitedHealth (UNH) | Margen de 6%, puntaje 0,34 y riesgo regulatorio en la medicina prepaga de EE.UU. |
| Santander (SAN) | P/E 8,7 y CSA 2024 de 73, pero volatilidad de 35%, banco expuesto a Europa y ESG no vigente. Es la alternativa a RELX si se quiere un banco europeo. |
| HSBC | Sin puntaje ESG público: por política no puede entrar. |
| JPMorgan (JPM) | Descartada por criterio de sustentabilidad: ESG 29 y mayor financiador de combustibles fósiles, contra el mandato de la clienta. |
| Unilever (UL), Coca-Cola (KO) | UL es la mejor del sector, pero los tres cupos europeos ya estaban. KO cotiza a 28 veces. |
| Alphabet (GOOGL) | Sumaría una cuarta apuesta a la IA, con ESG 29. Su crecimiento esperado sale negativo por una base 2026 inflada. |

## Consideradas, el optimizador no las tomó {#sec-31}

Pasaron el filtro ESG, el screening y la tesis, y entraron a la optimización. Con el piso de 20% en ESGV y la vol de 9% al máximo, el espacio para acciones individuales de EE.UU. se achica y el optimizador las deja en 0. No salieron por la regla del 2%: quedan en 0 aun sin esa regla.

| Acción | Por qué el optimizador no la toma |
|---|---|
| Mastercard (MA) | La tesis de pagos sigue en la cartera a través de Visa (2,1%). V y MA tienen correlación 0,88, y la view V4 es sobre la canasta de las dos. Con una correlación tan alta, el optimizador elige una sola: Visa tiene menos volatilidad (24,6% contra 27,0%). Forzar MA al 2% cuesta 0,004 pp de retorno neto: el optimizador está casi indiferente. |
| Procter & Gamble (PG) | Es la acción con menor retorno neto esperado de la cartera (4,1%), porque su beta baja le da poco retorno de equilibrio y no tiene view. La cobertura contra el riesgo de IA que buscábamos con PG ya la dan los bonos: IEF, SCHP y BIL suman 51,5%. |

RELX estuvo en esta lista hasta que el piso de Europa pasó a 10%: ahora entra con 2%. MA y PG se mantienen en la lista de seguimiento. Si en la revisión anual cambia la tesis o se relaja el piso de ESGV, son las primeras candidatas.

## Opiniones de inversión (views) {#sec-32}

Formato de Meucci (2010, ec. 11): v = Pπ + η · 0,25 · √(PΣP'). Ω = (1/c) · diag(u) · PΣP' · diag(u) (ec. 13), con c = 1 por defecto.

| View | Largo | Corto | η | u | Frase |
|---|---|---|---|---|---|
| V1 | NVDA | ESGV | +2 | 1,5 | Nvidia cobra la inversión en IA: crece 70% y cotiza a 10 veces la ganancia esperada. Le gana con holgura al mercado de EE.UU. |
| V2 | ASML+NVS+RELX (por capitalización) | ESGV | +1 | 1,0 | En dólares, Europa le gana a EE.UU.: paga casi el triple de dividendo, cotiza más barata y el dólar se debilita. |
| V3 | LLY+NVS (partes iguales) | ESGV | +1 | 1,0 | La salud le gana al mercado: su demanda no depende del ciclo ni del petróleo y tiene poder de precio. |
| V4 | V+MA (partes iguales) | ESGV | +1 | 1,0 | Las redes de pago cobran un peaje sobre el gasto nominal: con inflación de 3% a 4%, Visa y Mastercard le ganan al mercado sin tomar riesgo de crédito. |
| V5 | ETN | ESGV | +1 | 1,0 | Los centros de datos y la red eléctrica necesitan los equipos de Eaton: le gana al mercado de EE.UU. |
| V6 | SCHP | IEF | +1 | 1,5 | Con inflación de 4% y un shock de petróleo que puede escalar, los TIPS le ganan al Tesoro nominal en los próximos dos años. |
| V7 | VCEB | IEF | −1 | 1,0 | Con el spread de crédito en 0,89%, los corporativos no pagan su riesgo: rinden menos que el Tesoro de lo que el equilibrio supone. |

Las 7 views son relativas. Cinco van contra ESGV, así que son apuestas a acciones o canastas dentro de la renta variable, no a la cantidad total de acciones. Dos están en renta fija (TIPS contra Tesoro y crédito contra Tesoro). PG no tiene view: es neutral a propósito.

## Cartera neutra (π = λΣw_b) {#sec-33}

Se calcula con el criterio descripto en la metodología. La capitalización total implícita del universo de ESGV es de USD 61,5 billones.

| BIL | IEF | SCHP | VCEB | ESGV | NVDA | V | MA | LLY | ETN | PG | ASML | NVS | RELX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5,0% | 20,0% | 10,0% | 15,0% | 35,4% | 2,6% | 0,5% | 0,4% | 0,8% | 0,1% | 0,3% | 6,1% | 3,2% | 0,7% |

ESGV conserva 88% de la clase de EE.UU. En Europa, la capitalización le da a ASML 61% de la clase: 6,1% de la cartera, por encima del tope de 5%. No hay contradicción. El neutro solo fija el punto de partida de los retornos (π), y el tope de 5% por acción lo aplica el optimizador.


# La cartera final {#sec-34}

Fecha de corte: 16/11/2026. Retornos: Black-Litterman de mercado (Meucci 2010) con las 7 views del capítulo de compañías, después de impuestos. Riesgo: Σ de Ledoit-Wolf con retornos diarios de 10 años.

## Qué compra Valentina {#sec-35}

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

En total son 12 posiciones: renta fija 56,5% y acciones 43,5%. El retorno esperado es 6,55% bruto y 5,22% neto de impuestos y de los costos de los fondos, con vol de 9,0% y tracking error de 3,2% contra el benchmark de seis índices. MA y PG quedaron en 0 (ver el capítulo de compañías).

![Cartera final contra el benchmark, por clase de activo](outputs/graficos/a_clases.png){width=100%}

![Las 12 posiciones de la cartera final](outputs/graficos/b_activos.png){width=100%}

## Por qué quedó así {#sec-36}

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

![Las cinco carteras en el plano volatilidad y retorno](outputs/graficos/c_frontera.png){width=100%}

## Contra las alternativas (mismas restricciones) {#sec-37}

Todas las carteras se evalúan con el mismo retorno esperado (el posterior de Black-Litterman, con las views), después de impuestos con la ganancia de capital pagada al vender y de los costos de los fondos.

| | Final (con views) | Equilibrio sin views | HRP ajustado | Mínima varianza | 50/50 con nuestros activos |
|---|---|---|---|---|---|
| Retorno neto | 5,22% | 4,95% | 6,11% | 3,76% | 5,47% |
| Volatilidad | 9,0% | 9,0% | 11,6% | 6,5% | 10,7% |

- **Equilibrio:** el mismo optimizador sin views. Con el mismo riesgo, las views suman la diferencia de retorno neto.
- **HRP ajustado:** rinde más porque toma más riesgo. No usa retornos esperados y, ajustado a los rangos, termina por encima del objetivo de volatilidad. El HRP sin ajustar pone 99,6% en BIL.
- **Mínima varianza:** baja el riesgo a 6,5%, pero el retorno neto no alcanza para el retiro.
- **50/50 con nuestros activos:** la cartera neutra del modelo, con las proporciones del benchmark armadas con los 14 activos: Europa en tres acciones sueltas (ASML 6,1%) y EE.UU. en ESGV más acciones. Por eso tiene 10,7% de volatilidad, más que el benchmark de seis índices. No es el benchmark de la política: la comparación contra el benchmark va en la sección siguiente.

![Sensibilidad de los pesos por clase](outputs/graficos/d_sensibilidad.png){width=100%}

![Cuánto mueve la cartera cada opinión de inversión](outputs/graficos/e_views.png){width=100%}

## Contra el benchmark, con la misma vara {#sec-38}

Para comparar con el benchmark de la política (los seis índices) se usa una sola vara para los dos: la covarianza de Ledoit-Wolf estimada en conjunto sobre los 14 activos y los seis índices (2016-2026, retornos diarios), los retornos de largo plazo por clase del escenario económico (sin views), los mismos impuestos y los costos de los fondos.

| | Nuestra cartera | 50/50 de seis índices |
|---|---|---|
| Volatilidad esperada | 9,0% | 9,5% |
| Retorno neto esperado, sin views | 5,12% | 5,50% |
| Sharpe (bruto) | 0,35 | 0,37 |
| Retorno neto con views (el 50/50 armado con nuestros activos) | 5,22% | 5,47% |

La crisis de 2007-2009 medida de cuatro formas, con la misma regla para las dos carteras: cada posición con su propio retorno si cotizó todo el período (SCHP y V van con el índice de su clase), nominal, antes de impuestos y sin retiros.

| Crisis 2007-2009 | Nuestra cartera | 50/50 | Diferencia sobre USD 13.925.000 |
|---|---|---|---|
| Año 2008, pesos fijos | −11,7% | −15,2% | USD 474.104 |
| Año 2008, con el rebalanceo de la política | −14,5% | −16,9% | USD 329.466 |
| De pico a valle (oct-2007 a mar-2009), pesos fijos | −19,7% | −25,6% | USD 817.439 |
| De pico a valle, con el rebalanceo de la política | −24,6% | −30,5% | USD 812.830 |

Con rebalanceo, las dos caen más, porque se compran acciones mientras siguen cayendo. La que se presenta es la última, la que haría la política de verdad.

## Aporte de cada posición al riesgo {#sec-39}

El aporte de cada activo a la volatilidad es $w_i (\Sigma w)_i / \sigma_p$, con la covarianza de Ledoit-Wolf; los aportes suman la volatilidad de la cartera.

| Posición | Peso | Aporte (puntos de vol) | % del riesgo |
|---|---|---|---|
| ESGV | 20,0% | 3,41 | 37,9% |
| NVDA | 4,4% | 1,61 | 17,9% |
| ASML | 3,0% | 0,86 | 9,6% |
| LLY | 5,0% | 0,74 | 8,3% |
| NVS | 5,0% | 0,51 | 5,7% |
| SCHP | 20,0% | 0,39 | 4,3% |
| ETN | 2,0% | 0,39 | 4,3% |
| V | 2,1% | 0,34 | 3,7% |
| IEF | 21,5% | 0,31 | 3,5% |
| RELX | 2,0% | 0,25 | 2,7% |
| VCEB | 5,0% | 0,20 | 2,2% |
| BIL | 10,0% | 0,00 | 0,0% |
| Total | 100% | 9,0 | 100% |

- NVIDIA es la apuesta más fuerte medida en riesgo, no en peso: con 4,4% de la cartera aporta 17,9% del riesgo. Es la view muy alcista (V1) y una acción con 50% de volatilidad.
- Dentro de las acciones, Europa pesa 23% (benchmark 20%) y EE.UU. 77% (benchmark 80%).

## Monitoreo y rebalanceo con historia {#sec-40}

Un backtest ilustrativo aplica las reglas de la política a la cartera final con los retornos diarios de 2016 a 2026: revisión el último día hábil de cada mes; rebalanceo al objetivo si una clase se aparta más de 3 puntos, si queda más de 2 puntos fuera de su rango o si una acción supera 7%. No modela retiros ni impuestos y no es evidencia de performance: muestra cuándo y cuánto se habría operado.

- Las reglas sin tolerancia habrían rebalanceado 120 veces en 121 revisiones, con 17% de rotación por año. La cartera óptima está en el borde de cuatro rangos (liquidez y TIPS en el máximo, corporativos y Europa en el mínimo) y dos acciones en el tope de 5%: cualquier movimiento dispara una operación. Por eso la política fija tolerancias para disparar.
- Con las tolerancias: 15 rebalanceos en 10 años y 7% de rotación por año. Casi todos los dispara la clase de acciones de EE.UU.
- Mayor desvío de cada clase en una revisión: acciones de EE.UU. 4,7%, acciones de Europa 3,7%, corporativos 0,5%, liquidez 1,4%, Tesoro 2,4%, bonos ajustados por inflación 2,3%.
- Ejemplo, 31/12/2018: las acciones de EE.UU. habían caído a 30,1% de la cartera (objetivo 33,5%). Se vendieron USD 809.076 de bonos y de las posiciones que más pesaban y se compraron acciones. En los 12 meses siguientes, lo comprado rindió 60,6% y lo vendido 11,0%.
- Contraejemplo, 31/01/2017: el primer rebalanceo vendió acciones porque habían subido, sobre todo NVIDIA. En los 12 meses siguientes, lo vendido rindió 93,2% y lo comprado 2,4%. Rebalancear es disciplina de riesgo: mantiene la cartera en el nivel de volatilidad que eligió la clienta. No siempre gana.


# Retiro y vivienda {#sec-41}

Fecha de corte: 20/11/2026. Son 10.000 escenarios simulados en dólares de hoy, con la cartera final, los retornos de largo plazo del escenario base (sin views), impuestos por activo con la ganancia de capital pagada al vender, los costos propios de los fondos, la comisión por tramos y Bienes Personales. Cuántos años vive sale de una tabla de mortalidad (esperanza de vida 88 años). En los dos escenarios de vivienda se usan los mismos mercados y las mismas vidas. Los montos están en dólares de hoy: el sueldo sube con la inflación cada año.

## El retiro como sueldo fijo + bono variable {#sec-42}

Valentina cobra todos los meses un **sueldo fijo**: el gasto base de su vivienda, USD 14.850 si compra y 18.450 si alquila. Ese monto no se recorta. Encima cobra un **bono variable**, la parte de lujo, que sube cuando la cartera va bien y baja cuando va mal. Así funcionan las barandas de Guyton-Klinger: si el retiro pasa a pesar sobre la cartera más de 20% por encima de la proporción inicial, el retiro total baja 10%, sin perforar nunca el sueldo fijo; si pesa 20% menos, sube 10%. Después de un año negativo, el bono no se ajusta por inflación si la proporción supera la inicial. Para una clienta con poca tolerancia a las caídas, esto cambia la pregunta: en lugar de "¿me puedo quedar sin plata?", pasa a ser "¿cuánto puede bajar mi bono?".

## Probabilidad de quedarse sin plata en vida {#sec-43}

| Escenario | Gasto/mes | Sin bono variable (gasto fijo) | Con sueldo fijo + bono | El bono desaparece alguna vez |
|---|---|---|---|---|
| A compra, base | 14.850 | 1,3% | 1,3% | — |
| A compra, lujo | 21.700 | 12,5% | **1,9%** | 43% |
| A compra, alto | 31.550 | 50,4% | 5,3% | 46% |
| B alquila, base | 18.450 | 2,8% | 2,8% | — |
| B alquila, lujo | 25.300 | 17,2% | **4,2%** | 53% |
| B alquila, alto | 37.650 | 61,8% | 11,5% | 58% |

Con gasto fijo, la ruina crece con el horizonte. En A lujo es 8,0% a los 85, 17,4% a los 95 y 22,6% a los 100.

![Probabilidad de quedarse sin dinero en vida](outputs/graficos/g_ruina.png){width=100%}

![Patrimonio de la cartera por edad](outputs/graficos/f_abanico.png){width=100%}

## Retiro máximo seguro (sobrevive en 95 de cada 100 escenarios) {#sec-44}

| | Gasto fijo | Sueldo fijo + bono |
|---|---|---|
| A compra (USD 13.925.000) | 18.358 por mes | 30.824 por mes |
| B alquila (USD 15.000.000) | 20.093 por mes | 27.832 por mes |

Con gasto fijo solo entra el nivel base. El nivel lujo entra con el bono variable en las dos viviendas. El nivel alto no entra en ninguna.

## Prueba de estrés: arrancar con un 2008 {#sec-45}

Si el primer año repite 2008 (acciones de EE.UU. −37%, Europa −45%, Tesoro +18%), la cartera rinde −12,6% ese año, en dólares y después de impuestos, y después el mercado vuelve a lo normal. Es una prueba de estrés: el criterio de 5% vale para la simulación base, no para este caso extremo.

| Escenario | Ruina con gasto fijo | Ruina con sueldo fijo + bono | El dinero alcanza |
|---|---|---|---|
| A lujo | 12,5% → 27,8% | 1,9% → **5,2%** | 95 de cada 100 |
| B lujo | 17,2% → 35,1% | 4,2% → **10,2%** | 90 de cada 100 |
| A base | 1,3% → 4,0% | igual | 96 de cada 100 |
| B base | 2,8% → 8,6% | igual | 91 de cada 100 |

Aun arrancando con un 2008, el plan recomendado llega en 95 de cada 100 escenarios comprando y en 90 alquilando. Comprar sigue ganando.

![Estrés: el primer año repite 2008](outputs/graficos/h_estres.png){width=100%}

## Sensibilidades (ruina con gasto fijo) {#sec-46}

| | Base | Retornos +1 pp | Retornos −1 pp | Vol 7% | Vol 11% |
|---|---|---|---|---|---|
| Retorno neto, sin views | 5,12% | 5,87% | 4,36% | 4,72% | 5,52% |
| A lujo | 12,5% | 3,9% | 28,7% | 11,7% | 13,7% |
| B lujo | 17,2% | 5,9% | 35,0% | 17,5% | 17,4% |
| Retiro seguro A (gasto fijo) | 18.358 | 22.528 | 14.687 | 19.174 | 17.565 |
| Retiro seguro B (gasto fijo) | 20.093 | 24.585 | 16.113 | 20.947 | 19.214 |

Lo que más mueve el resultado son los retornos de largo plazo, no la volatilidad.

## ¿Y si no invierte? {#sec-47}

Mismo plan recomendado (compra, nivel lujo, sueldo fijo más bono con las mismas barandas), mismos impuestos, Bienes Personales, mortalidad y escenarios. Cambia solo dónde está la plata y qué costos paga. Patrimonio mediano viva hasta los 100, en millones de dólares de hoy (entre paréntesis, en dólares corrientes).

| | Sin plata en vida | Se acaba la plata (caso central) | A los 60 | A los 75 | A los 90 | El bono desaparece |
|---|---|---|---|---|---|---|
| a. Plata quieta (0% nominal, sin comisión) | 84,6% | a los 77 | 3,8 (6,6) | 0,4 (0,9) | 0,0 (0,0) | 100% |
| b. Todo en letras del Tesoro (sin comisión) | 16,5% | a los 98 | 7,5 (13,0) | 4,5 (10,9) | 1,6 (5,5) | 98% |
| d. Nuestra cartera | 1,9% | no se acaba | 12,9 (22,5) | 12,3 (30,0) | 11,7 (39,8) | 43% |

En los escenarios en que la plata se acaba, la edad mediana es 77 con la plata quieta, 98 en letras y 89 con la cartera.

![Patrimonio mediano por edad: plata quieta, letras del Tesoro y la cartera](outputs/graficos/k_invertir_vs_no.png){width=100%}

### ¿Y un 50/50 pasivo, sin asesor?

| | Sin plata en vida | A los 90 (USD M de hoy) | El bono desaparece |
|---|---|---|---|
| c. 50/50 de seis índices, sin comisión | 0,2% | 20,9 | 18% |
| e. 50/50 de seis índices, con nuestra comisión | 1,5% | 14,5 | 34% |
| d. Nuestra cartera | 1,9% | 11,7 | 43% |

El 50/50 pasivo sin asesor sale mejor. De c a e se ve el efecto de la comisión; de e a d, el de la asignación (menos acciones, más renta fija que paga 35% sobre todo su retorno, y el filtro de sustentabilidad). Tres razones para presentarlo igual como la vara y no como la alternativa:

- El 50/50 no cumple el mandato de la clienta: SPY y VGK tienen tabaco, petroleras y defensa, que su política excluye. Es la vara contra la que se mide la cartera, no algo que pueda comprar.
- La simulación no le da ningún crédito a las views del equipo: usa los retornos de largo plazo por clase. Por construcción, solo puede mostrar la diferencia de asignación y la comisión. Es conservadora a propósito.
- Lo que paga la comisión no es retorno: es el plan de retiro con barandas, la gestión impositiva, el rebalanceo y la contención en las caídas, que para una clienta de compostura baja es lo que evita vender en el peor momento.

## Si cambian los impuestos {#sec-48}

El caso base sigue la ley vigente, incluida la baja de Bienes Personales a 0,25% desde 2027. Nivel lujo comprando, con sueldo fijo más bono:

| Escenario impositivo | Sin plata en vida | Retiro seguro con bono (USD/mes) |
|---|---|---|
| Ley vigente | 1,9% | 30.824 |
| Bienes Personales queda en 0,75% para siempre | 5,8% | 19.695 |
| Intereses y dividendos 40%, ganancias de capital 20% | 2,7% | 27.900 |
| Las dos cosas | 8,0% | 14.573 |

El riesgo impositivo principal es que un gobierno futuro revierta la baja de Bienes Personales: es el que más mueve el resultado. Es el motivo del seguimiento con el contador: si la ley cambia, el plan se recalcula y se ajusta el bono antes de que la probabilidad pase el 5%.

## Recomendación: comprar (escenario A) {#sec-49}

A gana en todas las comparaciones: menos ruina, más retiro seguro con bono variable y mejor resistencia a un 2008. El motivo es el **alquiler implícito**. Comprar le ahorra a Valentina USD 3.600 por mes: el alquiler de 4.500 menos ABL (300) y mantenimiento (600), que paga solo la dueña; las expensas las pagan las dos. Son 4,32% real por año sobre un depto de USD 1 M, 6,7% en dólares, que no paga impuesto a las ganancias. La cartera rinde 5,12% en dólares después de impuestos y de los costos de los fondos, sin contar las views, y menos después de la comisión y Bienes Personales. Por eso, poner ese millón en la casa rinde más que invertirlo.

En contra de comprar: el depto concentra riesgo en un solo inmueble, no tiene liquidez y cuesta 7,5% de gastos de compra (USD 75.000, ya descontados del capital de A). Suponemos que mantiene su valor real; no contamos con que se valorice.

**Propuesta a Valentina:** comprar el depto y vivir con un sueldo fijo de USD 14.850 por mes más un bono variable que arranca en USD 6.850 (nivel lujo, 21.700 en total). La probabilidad de quedarse sin plata en vida es 1,9%; como prueba de estrés, con un 2008 de entrada el dinero alcanza en 95 de cada 100 escenarios. A cambio, hay una probabilidad de 43% de que en algún momento el bono desaparezca y viva un tiempo con el sueldo fijo. La decisión es de ella.


# Limitaciones {#sec-50}

## Retornos de largo plazo {#sec-51}

Son la variable que más pesa en el resultado. Con 1 punto menos por año en todas las clases:

- la probabilidad de quedarse sin dinero en el nivel lujo con gasto fijo sube de 12,5% a 28,7% si compra y de 17,2% a 35,0% si alquila;
- el retiro seguro sin barandas baja de USD 18.358 a 14.687 por mes.

Los supuestos están en rango con los de J.P. Morgan, Vanguard y BlackRock, pero cada año se revisan contra el mercado.

## Distribución de los retornos {#sec-52}

La simulación usa una lognormal con correlaciones fijas. No reproduce colas más gruesas ni el aumento de las correlaciones en las crisis. El escenario de estrés de 2008 cubre parte de ese riesgo, no todo.

## Correlación entre bonos y acciones {#sec-53}

En 2007-2026 fue negativa para el Tesoro (−0,29). En los últimos diez años fue positiva por la suba de tasas de 2022. Si se repite un episodio de inflación con tasas en alza, los bonos diversifican menos de lo que supone la covarianza.

## Impuestos simplificados {#sec-54}


- La ganancia de capital paga al vender, con una tasa efectiva calibrada a la rotación del backtest 2016-2026 (12,4% de las acciones por año). Es un estado estacionario: no captura la venta total cuando la plata se acaba ni la ganancia que queda sin realizar al final del horizonte. Si la rotación real fuera mayor, el impuesto se acercaría al 15% anual, el supuesto conservador de la versión anterior.
- El optimizador usa el supuesto de 15% todos los años. Con el de realizar, la cartera óptima cambiaría 0,1%.
- Las pérdidas compensan ganancias en el mismo año; la norma permite trasladarlas cinco años.
- Las tasas son las vigentes: dividendos e intereses del exterior, 35% (alícuota marginal máxima de la escala del artículo 94 de la Ley de Impuesto a las Ganancias, la que corresponde a este patrimonio); venta de acciones del exterior, 15% (artículo 94, segundo párrafo); Bienes Personales, 0,75% en 2026 y 0,25% desde 2027 (Ley 27.743, alícuota máxima).
- La Ley 27.743 exime la casa habitación hasta ARS 350.000.000 (monto que se actualiza cada año) y lleva el mínimo no imponible general a ARS 100.000.000. El modelo grava el departamento completo y la cartera sin mínimo: es conservador.

## Pesos por acción {#sec-55}

Los pesos por clase son estables ante cambios en la confianza en las opiniones, en las opiniones mismas y en la volatilidad objetivo. Los pesos entre acciones de EE.UU. no lo son: el optimizador está casi indiferente entre Visa, Mastercard, Eaton y ASML (forzar Mastercard al 2% cuesta 0,004 puntos de retorno). Las acciones individuales expresan una tesis; su peso exacto no es una predicción.

## Historia completada {#sec-56}

VCEB y ESGV tienen historia corta y se completaron con índices muy correlacionados (0,988 y 0,992). La volatilidad de VCEB puede estar sobrestimada en 1,7 puntos, lo que también es conservador.

## Vivienda {#sec-57}

Se supone que el departamento mantiene su valor real y que el alquiler sigue a la inflación. El análisis no incluye el riesgo de concentrar USD 1 millón en un solo inmueble ni la falta de liquidez del departamento.


# Anexos {#sec-58}

## Anexo A. Universo de inversión {#sec-59}

Candidatos que pasaron el filtro de exclusiones y la nota mínima de sustentabilidad. «En cartera» marca los 14 activos que entraron a la optimización.

| Activo | Nombre | Clase | Tipo | País | Sector | ESG S&P | En cartera |
|---|---|---|---|---|---|---|---|
| BIL | SPDR Bloomberg 1-3 Month T-Bill ETF | Liquidez | fondo | EE.UU. | Soberano | n/a | sí |
| SGOV | iShares 0-3 Month Treasury Bond ETF | Liquidez | fondo | EE.UU. | Soberano | n/a |  |
| IEF | iShares 7-10 Year Treasury Bond ETF | Tesoro | fondo | EE.UU. | Soberano | n/a | sí |
| IEI | iShares 3-7 Year Treasury Bond ETF | Tesoro | fondo | EE.UU. | Soberano | n/a |  |
| TIP | iShares TIPS Bond ETF | Ajustados por inflación | fondo | EE.UU. | Soberano | n/a |  |
| SCHP | Schwab U.S. TIPS ETF | Ajustados por inflación | fondo | EE.UU. | Soberano | n/a | sí |
| VTIP | Vanguard Short-Term Inflation-Protected Securities ETF | Ajustados por inflación | fondo | EE.UU. | Soberano | n/a |  |
| VCEB | Vanguard ESG U.S. Corporate Bond ETF | Corporativos | fondo | EE.UU. | Corporativo | n/a | sí |
| ESGV | Vanguard ESG U.S. Stock ETF | Acciones EE.UU. | fondo | EE.UU. | Amplio | n/a | sí |
| AAPL | Apple | Acciones EE.UU. | accion | EE.UU. | Tecnología | 32 |  |
| MSFT | Microsoft | Acciones EE.UU. | accion | EE.UU. | Tecnología | 46 |  |
| NVDA | NVIDIA | Acciones EE.UU. | accion | EE.UU. | Tecnología | 61 | sí |
| GOOGL | Alphabet | Acciones EE.UU. | accion | EE.UU. | Comunicaciones | 29 |  |
| META | Meta Platforms | Acciones EE.UU. | accion | EE.UU. | Comunicaciones | 30 |  |
| HD | Home Depot | Acciones EE.UU. | accion | EE.UU. | Consumo discrecional | 39 |  |
| JPM | JPMorgan Chase | Acciones EE.UU. | accion | EE.UU. | Financiero | 29 |  |
| V | Visa | Acciones EE.UU. | accion | EE.UU. | Financiero | 58 | sí |
| MA | Mastercard | Acciones EE.UU. | accion | EE.UU. | Financiero | 58 | sí |
| UNH | UnitedHealth Group | Acciones EE.UU. | accion | EE.UU. | Salud | 39 |  |
| LLY | Eli Lilly | Acciones EE.UU. | accion | EE.UU. | Salud | 38 | sí |
| PG | Procter & Gamble | Acciones EE.UU. | accion | EE.UU. | Consumo básico | 37 | sí |
| KO | Coca-Cola | Acciones EE.UU. | accion | EE.UU. | Consumo básico | 42 |  |
| COST | Costco | Acciones EE.UU. | accion | EE.UU. | Consumo básico | 41 |  |
| NEE | NextEra Energy | Acciones EE.UU. | accion | EE.UU. | Servicios públicos | 38 |  |
| ETN | Eaton | Acciones EE.UU. | accion | EE.UU. | Industria | 50 | sí |
| ASML | ASML Holding | Acciones Europa | accion | Países Bajos | Tecnología | 58 | sí |
| SAP | SAP | Acciones Europa | accion | Alemania | Tecnología | 58 |  |
| NVO | Novo Nordisk | Acciones Europa | accion | Dinamarca | Salud | 33 |  |
| AZN | AstraZeneca | Acciones Europa | accion | Reino Unido | Salud | 69 |  |
| NVS | Novartis | Acciones Europa | accion | Suiza | Salud | 58 | sí |
| SNY | Sanofi | Acciones Europa | accion | Francia | Salud | 52 |  |
| GSK | GSK | Acciones Europa | accion | Reino Unido | Salud | 68 |  |
| UL | Unilever | Acciones Europa | accion | Reino Unido | Consumo básico | 50 |  |
| DEO | Diageo | Acciones Europa | accion | Reino Unido | Consumo básico | 57 |  |
| RELX | RELX | Acciones Europa | accion | Reino Unido | Industria | 58 | sí |
| HSBC | HSBC Holdings | Acciones Europa | accion | Reino Unido | Financiero |  |  |
| ING | ING Groep | Acciones Europa | accion | Países Bajos | Financiero | 47 |  |
| SAN | Banco Santander | Acciones Europa | accion | España | Financiero | 73 |  |


## Anexo B. Excluidos por el filtro de sustentabilidad {#sec-60}

| Activo | Nombre | Clase | Motivo |
|---|---|---|---|
| LQD | iShares iBoxx $ Investment Grade Corporate Bond ETF | Corporativos | Excluido: petróleo y gas, armamento, tabaco |
| VCIT | Vanguard Intermediate-Term Corporate Bond ETF | Corporativos | Excluido: petróleo y gas, armamento, tabaco |
| SUSC | iShares ESG Aware USD Corporate Bond ETF | Corporativos | Excluido: petróleo y gas |
| SPY | SPDR S&P 500 ETF Trust | Acciones EE.UU. | Excluido: petróleo y gas, armamento, tabaco |
| ESGU | iShares ESG Aware MSCI USA ETF | Acciones EE.UU. | Excluido: petróleo y gas |
| VGK | Vanguard FTSE Europe ETF | Acciones Europa | Excluido: petróleo y gas, armamento, tabaco |
| ESGD | iShares ESG Aware MSCI EAFE ETF | Acciones Europa | Excluido: petróleo y gas / Fuera de mandato: no es solo Europa (Desarrollados ex EE.UU.) |
| AMZN | Amazon | Acciones EE.UU. | ESG bajo: S&P 21 < 25 (S&P Global ESG Score) |
| JNJ | Johnson & Johnson | Acciones EE.UU. | ESG bajo: S&P 24 < 25 (CSA 2024, DJSI) |
| XOM | Exxon Mobil | Acciones EE.UU. | Excluido: petróleo y gas |
| CVX | Chevron | Acciones EE.UU. | Excluido: petróleo y gas |
| LMT | Lockheed Martin | Acciones EE.UU. | Excluido: armamento |
| RTX | RTX (Raytheon) | Acciones EE.UU. | Excluido: armamento |
| MO | Altria | Acciones EE.UU. | Excluido: tabaco |
| PM | Philip Morris International | Acciones EE.UU. | Excluido: tabaco |
| FCX | Freeport-McMoRan | Acciones EE.UU. | Excluido: minería pesada |
| TTE | TotalEnergies | Acciones Europa | Excluido: petróleo y gas |
| SHEL | Shell | Acciones Europa | Excluido: petróleo y gas |
| BP | BP | Acciones Europa | Excluido: petróleo y gas |
| RIO | Rio Tinto | Acciones Europa | Excluido: minería pesada |
| BTI | British American Tobacco | Acciones Europa | Excluido: tabaco |


## Anexo C. Screening de acciones {#sec-61}

Puntaje = promedio de los percentiles de cada métrica dentro de su sector (0,5 = mitad del sector). Datos de Yahoo Finance al 15/11/2026.

| Sector | Acción | P/E forward | Crec. ganancias | Margen operativo | Deuda neta / EBITDA | ROE | Dividendo + recompras | ESG S&P | Puntaje |
|---|---|---|---|---|---|---|---|---|---|
| Comunicaciones | META | 18,0 | 17% | 38% | 0,3 | 32% | 1,9% | 30 | 0,61 |
| Comunicaciones | GOOGL | 19,2 | -23% | 33% | -0,6 | 44% | 1,6% | 29 | 0,39 |
| Consumo básico | UL | 17,1 | 7% | 20% | 2,4 | 32% | 4,3% | 50 | 0,61 |
| Consumo básico | KO | 28,1 | 6% | 32% | 1,5 | 41% | 2,3% | 42 | 0,56 |
| Consumo básico | PG | 23,0 | 6% | 25% | 0,9 | 30% | 3,8% | 37 | 0,50 |
| Consumo básico | DEO | 14,4 | 5% | 29% | 3,2 | 15% | 2,0% | 57 | 0,44 |
| Consumo básico | COST | 44,2 | 10% | 4% | -0,8 | 28% | 0,7% | 41 | 0,39 |
| Consumo discrecional | HD | 21,9 | 6% | 12% | 2,5 | 104% | 2,7% | 39 | 0,50 |
| Financiero | V | 24,8 | 14% | 66% | 0,3 | 64% | 3,3% | 58 | 0,61 |
| Financiero | HSBC | 9,6 | 10% | 49% |  | 14% | 6,4% |  | 0,55 |
| Financiero | SAN | 8,7 | 11% | 42% |  | 13% | 4,9% | 73 | 0,53 |
| Financiero | MA | 28,5 | 15% | 60% | 0,6 | 231% | 2,6% | 58 | 0,51 |
| Financiero | ING | 10,8 | 9% | 52% |  | 18% | 4,0% | 47 | 0,43 |
| Financiero | JPM | 13,5 | 7% | 45% |  | 18% | 5,7% | 29 | 0,36 |
| Industria | RELX | 18,9 | 13% | 32% | 2,6 | 132% | 5,1% | 58 | 0,68 |
| Industria | ETN | 21,5 | 19% | 18% | 2,8 | 20% | 2,6% | 50 | 0,32 |
| Salud | LLY | 28,5 | 43% | 51% | 1,0 | 86% | 0,8% | 38 | 0,54 |
| Salud | NVO | 12,1 | -3% | 51% | 0,5 | 58% | 4,4% | 33 | 0,54 |
| Salud | NVS | 16,2 | 10% | 34% | 1,6 | 24% | 6,0% | 58 | 0,54 |
| Salud | SNY | 8,9 | 7% | 22% | 0,9 | 6% | 9,8% | 52 | 0,54 |
| Salud | GSK | 10,2 | 4% | 31% | 1,8 | 28% | 5,4% | 68 | 0,52 |
| Salud | AZN | 16,3 | 12% | 26% | 1,2 | 23% | 1,7% | 69 | 0,48 |
| Salud | UNH | 17,5 | 14% | 6% | 1,6 | 16% | 3,8% | 39 | 0,34 |
| Servicios públicos | NEE | 19,5 | 9% | 30% | 8,1 | 14% | 2,9% | 38 | 0,50 |
| Tecnología | NVDA | 10,3 | 70% | 65% | -0,1 | 117% | 1,6% | 61 | 0,76 |
| Tecnología | ASML | 23,6 | 36% | 39% | -0,7 | 66% | 1,8% | 58 | 0,60 |
| Tecnología | SAP | 24,6 | 18% | 29% | -0,0 | 18% | 2,0% | 58 | 0,40 |
| Tecnología | MSFT | 21,7 | 21% | 47% | 0,3 | 34% | 1,3% | 46 | 0,39 |
| Tecnología | AAPL | 33,7 | 12% | 33% | 0,2 | 142% | 2,0% | 32 | 0,36 |


## Anexo D. Opiniones de inversión {#sec-62}

η: intensidad (+1 alcista, +2 muy alcista, −1 bajista). u: incertidumbre relativa (1,5 = menos segura).

| Opinión | Largo | Contra | η | u | Frase |
|---|---|---|---|---|---|
| V1 | NVDA | ESGV | +2 | 1,5 | Nvidia cobra la inversión en IA: crece 70% y cotiza a 10 veces la ganancia esperada. Le gana con holgura al mercado de EE.UU. |
| V2 | ASML+NVS+RELX | ESGV | +1 | 1,0 | En dólares, Europa le gana a EE.UU.: paga casi el triple de dividendo, cotiza más barata y el dólar se debilita. |
| V3 | LLY+NVS | ESGV | +1 | 1,0 | La salud le gana al mercado: su demanda no depende del ciclo ni del petróleo y tiene poder de precio. |
| V4 | V+MA | ESGV | +1 | 1,0 | Las redes de pago cobran un peaje sobre el gasto nominal: con inflación de 3% a 4%, Visa y Mastercard le ganan al mercado sin tomar riesgo de crédito. |
| V5 | ETN | ESGV | +1 | 1,0 | Los centros de datos y la red eléctrica necesitan los equipos de Eaton: le gana al mercado de EE.UU. |
| V6 | SCHP | IEF | +1 | 1,5 | Con inflación de 4% y un shock de petróleo que puede escalar, los TIPS le ganan al Tesoro nominal en los próximos dos años. |
| V7 | VCEB | IEF | −1 | 1,0 | Con el spread de crédito en 0,89%, los corporativos no pagan su riesgo: rinden menos que el Tesoro de lo que el equilibrio supone. |


## Anexo E. Cartera final en dólares {#sec-63}

| Clase | Activo | Nombre | Peso | USD si compra | USD si alquila |
|---|---|---|---|---|---|
| Liquidez | BIL | SPDR Bloomberg 1-3 Month T-Bill ETF | 10,0% | 1.392.500 | 1.500.000 |
| Tesoro | IEF | iShares 7-10 Year Treasury Bond ETF | 21,5% | 2.992.142 | 3.223.133 |
| Ajustados por inflación | SCHP | Schwab U.S. TIPS ETF | 20,0% | 2.785.000 | 3.000.000 |
| Corporativos | VCEB | Vanguard ESG U.S. Corporate Bond ETF | 5,0% | 696.250 | 750.000 |
| Acciones EE.UU. | ESGV | Vanguard ESG U.S. Stock ETF | 20,0% | 2.785.000 | 3.000.000 |
| Acciones EE.UU. | NVDA | NVIDIA | 4,4% | 614.015 | 661.416 |
| Acciones EE.UU. | V | Visa | 2,1% | 292.843 | 315.451 |
| Acciones EE.UU. | MA | Mastercard | 0,0% | 0 | 0 |
| Acciones EE.UU. | LLY | Eli Lilly | 5,0% | 696.250 | 750.000 |
| Acciones EE.UU. | ETN | Eaton | 2,0% | 278.500 | 300.000 |
| Acciones EE.UU. | PG | Procter & Gamble | 0,0% | 0 | 0 |
| Acciones Europa | ASML | ASML Holding | 3,0% | 417.750 | 450.000 |
| Acciones Europa | NVS | Novartis | 5,0% | 696.250 | 750.000 |
| Acciones Europa | RELX | RELX | 2,0% | 278.500 | 300.000 |


## Anexo F. Simulación de retiros por escenario {#sec-64}

Probabilidad de quedarse sin dinero en vida. Gasto fijo: retiro real constante. Con bono: sueldo fijo (gasto base) más bono variable.

| Escenario | Gasto mensual (USD) | Gasto fijo | Horizonte 85 | Horizonte 95 | Horizonte 100 | Con bono | 2008, gasto fijo | 2008, con bono |
|---|---|---|---|---|---|---|---|---|
| Compra, base | 14.850 | 1,3% | 0,5% | 1,8% | 2,7% | 1,3% | 4,0% | 4,0% |
| Compra, lujo | 21.700 | 12,5% | 8,0% | 17,4% | 22,6% | 1,9% | 27,8% | 5,2% |
| Compra, alto | 31.550 | 50,4% | 46,3% | 62,8% | 68,2% | 5,3% | 72,6% | 11,5% |
| Alquila, base | 18.450 | 2,8% | 1,2% | 4,1% | 6,5% | 2,8% | 8,6% | 8,6% |
| Alquila, lujo | 25.300 | 17,2% | 11,6% | 23,7% | 29,6% | 4,2% | 35,1% | 10,2% |
| Alquila, alto | 37.650 | 61,8% | 60,3% | 74,4% | 79,0% | 11,5% | 81,6% | 21,9% |


Retiro máximo seguro (USD por mes, ruina de 5% o menos):


| Vivienda | Gasto fijo | Con bono | Gasto fijo, 2008 | Con bono, 2008 |
|---|---|---|---|---|
| A: compra | 18.358 | 30.824 | 15.457 | 21.259 |
| B: alquila | 20.093 | 27.832 | 16.943 | 16.943 |


Sensibilidades (ruina con gasto fijo):


| Caso | Retorno real neto | Compra, base | Compra, lujo | Compra, alto | Alquila, base | Alquila, lujo | Alquila, alto |
|---|---|---|---|---|---|---|---|
| base (vol 9%) | 2,80% | 1,3% | 12,5% | 50,4% | 2,8% | 17,2% | 61,8% |
| retornos +1 pp | 3,54% | 0,3% | 3,9% | 29,7% | 0,6% | 5,9% | 40,9% |
| retornos −1 pp | 2,07% | 5,3% | 28,7% | 69,2% | 10,2% | 35,0% | 77,7% |
| vol 7% | 2,41% | 0,5% | 11,7% | 59,3% | 1,7% | 17,5% | 71,7% |
| vol 11% | 3,19% | 2,1% | 13,7% | 44,8% | 4,0% | 17,4% | 55,0% |


## Anexo G. Código y reproducción {#sec-65}

Todo el análisis se reproduce con `python -m tp.correr` (Python 3.13; dependencias en `requirements.txt`). Las pruebas automáticas se corren con `pytest -q`. Módulos principales:

- `tp/universo.py`: candidatos, exclusiones y nota mínima de sustentabilidad.
- `tp/datos.py`, `tp/estadisticas.py`: precios, estadísticas del benchmark y covarianza de Ledoit y Wolf.
- `tp/screening.py`: ranking de acciones por sector.
- `tp/equilibrio.py`, `tp/views.py`, `tp/black_litterman.py`: cartera neutra, opiniones y modelo de Black y Litterman.
- `tp/optimizacion.py`, `tp/hrp.py`: optimización con reglas y paridad de riesgo jerárquica.
- `tp/impuestos.py`, `tp/comisiones.py`, `tp/mortalidad.py`, `tp/retiro.py`, `tp/montecarlo.py`: impuestos, comisión, mortalidad, barandas y simulación.
- `tp/etapa4.py`, `tp/etapa5.py`, `tp/graficos.py`: salidas de cada etapa.


# Bibliografía {#sec-66}

## Artículos y libros {#sec-67}

- Black, F. y Litterman, R. (1992). Global Portfolio Optimization. *Financial Analysts Journal*, 48(5), 28-43. <https://doi.org/10.2469/faj.v48.n5.28>
- Bodie, Z., Kane, A. y Marcus, A. *Investments*. McGraw-Hill. Capítulo 27, el modelo de Black y Litterman (bibliografía del curso).
- CFA Institute. *CFA Program Curriculum, Level III: Private Wealth Pathway*, volumen 2, módulo 5 (planificación de retiros y tasas de retiro sostenibles).
- Chhabra, A. B. (2005). Beyond Markowitz: A Comprehensive Wealth Allocation Framework for Individual Investors. *The Journal of Wealth Management*, 7(4), 8-34. <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=925138>
- Evensky, H., Horan, S. M. y Robinson, T. R. (2011). *The New Wealth Management: The Financial Advisor's Guide to Managing and Investing Client Assets*. Wiley, CFA Institute Investment Series.
- Gompertz, B. (1825). On the Nature of the Function Expressive of the Law of Human Mortality. *Philosophical Transactions of the Royal Society of London*, 115, 513-583. <https://doi.org/10.1098/rstl.1825.0026>
- Guyton, J. T. y Klinger, W. J. (2006). Decision Rules and Maximum Initial Withdrawal Rates. *Journal of Financial Planning*, 19(3), marzo. <https://www.financialplanningassociation.org/article/journal/MAR06-decision-rules-and-maximum-initial-withdrawal-rates>
- Ledoit, O. y Wolf, M. (2004). Honey, I Shrunk the Sample Covariance Matrix. *The Journal of Portfolio Management*, 30(4), 110-119. <https://doi.org/10.3905/jpm.2004.110>
- López de Prado, M. (2016). Building Diversified Portfolios that Outperform Out of Sample. *The Journal of Portfolio Management*, 42(4), 59-69. <https://doi.org/10.3905/jpm.2016.42.4.059>
- Meucci, A. (2010). The Black-Litterman Approach: Original Model and Extensions. En *The Encyclopedia of Quantitative Finance*, Wiley. Versión extendida: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1117574>
- Milevsky, M. A. y Robinson, C. (2005). A Sustainable Spending Rate without Simulation. *Financial Analysts Journal*, 61(6), 89-100. <https://rpc.cfainstitute.org/research/financial-analysts-journal/2005/a-sustainable-spending-rate-without-simulation>
- Reilly, F. K. y Brown, K. C. *Investment Analysis and Portfolio Management*. Cengage. Enfoque de tres pasos economía, industria y compañía (bibliografía del curso).
- Schwager, J. D. (1992). *The New Market Wizards: Conversations with America's Top Traders*. HarperBusiness.

## Datos y fuentes de mercado {#sec-68}

- Yahoo Finance: precios diarios ajustados, fundamentos de las compañías, rendimientos por dividendo y comisiones de los fondos, al 15/11/2026. <https://finance.yahoo.com>
- Federal Reserve Bank of St. Louis, FRED: tasas del Tesoro (DTB3, DGS10), rendimiento real de los bonos ajustados por inflación (DFII5, DFII10), inflación implícita (T10YIE) y diferencial de crédito (BAMLC0A0CM). <https://fred.stlouisfed.org>
- S&P Global, ESG Scores por emisor y Corporate Sustainability Assessment 2024 (rebalanceo del índice Dow Jones de Sustentabilidad). <https://www.spglobal.com/sustainable1/en/scores/>
- J.P. Morgan Asset Management, 2027 Long-Term Capital Market Assumptions (19/10/2026) y Guide to the Markets Europe (datos al 30/09/2026).
- Vanguard, Vanguard Capital Markets Model forecasts (21/10/2026).
- BlackRock Investment Institute, Capital Market Assumptions (agosto de 2026).
- FactSet, Earnings Insight (noviembre de 2026).
- Fondo Monetario Internacional, World Economic Outlook (octubre de 2026).
- Reserva Federal, comunicado del Comité Federal de Mercado Abierto del 28/10/2026. Banco Central Europeo, decisiones de política monetaria y proyecciones de septiembre de 2026.
- BYMA, lista oficial de certificados de depósito argentinos (CEDEAR) del 16/09/2026.

## Normativa {#sec-69}

- Ley 27.743 (2024), Título sobre el Impuesto sobre los Bienes Personales: reducción de alícuotas hasta 0,25% en 2027. Boletín Oficial, 08/07/2024: <https://www.boletinoficial.gob.ar/detalleAviso/primera/310191/20240708>
- Ley de Impuesto a las Ganancias, texto ordenado 2019 (InfoLEG), artículo 94: escala de personas humanas (alícuota marginal máxima 35%) y alícuota de 15% para la venta de acciones del exterior.
- Deloitte Argentina, «Medidas Fiscales Paliativas y Relevantes – Ley 27.743». <https://www.deloitte.com/latam/es/services/tax/perspectives/ley-de-medidas-fiscales.html>
- Estudio O'Farrell, «Ley 27.743 – Paquete Fiscal».
- Errepar, «Dividendos y venta de acciones de EE.UU.: claves del tratamiento en Ganancias para personas humanas residentes» (mayo de 2025).
- Internal Revenue Service (EE.UU.), retención a no residentes y exención de intereses de cartera. <https://www.irs.gov/individuals/international-taxpayers/federal-income-tax-withholding-and-reporting-on-other-kinds-of-us-source-income-paid-to-nonresident-aliens>
