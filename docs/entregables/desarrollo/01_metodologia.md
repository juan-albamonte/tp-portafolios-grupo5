# Metodología

El trabajo es un único programa en Python (`python -m tp.correr`). Corre siete etapas en orden y regenera todas las tablas y gráficos de este documento a partir de los datos:

1. universo y filtro de sustentabilidad;
2. datos y estadísticas;
3. análisis de economía, industrias y compañías;
4. Black y Litterman y optimización;
5. simulación de retiros;
6. gráficos;
7. planilla de cálculo.

El código, con sus pruebas automáticas, se entrega junto con este documento.

## Datos

- Precios. Cierres diarios ajustados por dividendos y divisiones de acciones, de Yahoo Finance, entre junio de 2007 y octubre de 2026.
- Benchmark. Las estadísticas históricas usan los seis índices de referencia (BIL, IEF, TIP, LQD, SPY y VGK), que tienen historia completa desde antes de la crisis de 2008.
- Covarianza de la cartera. Se estima con los últimos diez años de retornos diarios de los 14 activos finales: 2.514 días, de noviembre de 2016 a octubre de 2026.
- Fondos más nuevos. Dos fondos nacieron después del inicio de la ventana. Antes de su lanzamiento se completaron con el índice de su clase: VCEB con LQD (correlación diaria 0,988 en el período común) y ESGV con SPY (0,992).
- Tasas e inflación. Vienen de FRED (Reserva Federal de St. Louis).

![Valor de USD 100 invertidos en cada índice del benchmark desde 2007](outputs/graficos/j_historia.png){width=100%}

![Correlaciones diarias entre las clases de activo](outputs/graficos/i_correlaciones.png){width=85%}

## Covarianza: Ledoit y Wolf (2004)

Con 14 activos, la matriz de covarianzas muestral tiene 105 correlaciones estimadas con error, y el optimizador tiende a explotar justamente esos errores. Ledoit y Wolf (2004) proponen achicar la matriz muestral $S$ hacia un objetivo $F$ con todas las correlaciones iguales al promedio:

$$\Sigma = \delta F + (1-\delta) S$$

La intensidad $\delta$ se elige para minimizar el error esperado y sale de los datos: 0,024 con retornos diarios. Con 2.514 días el ruido es bajo y el ajuste es chico. Con retornos mensuales (120 meses) daría 0,22. Esta matriz se usa para la restricción de volatilidad, para el modelo de retornos y para la simulación.

## Retornos esperados: Black y Litterman en la versión de Meucci (2010)

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

## Impuestos por activo

La optimización usa retornos después de impuestos de una residente fiscal argentina:

- Renta fija, incluidos los bonos ajustados por inflación: todo el retorno se cobra como interés y paga 35% (el ajuste por inflación del capital también es interés).
- Acciones: el dividendo paga 35%, el máximo entre la retención de EE.UU. de 30% y la tasa argentina. La ganancia de capital paga 15%, pero recién al vender.

Para que el impuesto al vender entre en un modelo anual, se lo convierte en una tasa efectiva. Si cada año se vende una fracción $f$ de cada acción (por rebalanceo y para pagar los retiros) y su precio sube $g$ por año, en el estado estacionario la ganancia sin realizar vale $g(1-f)/(g+f)$ del valor y el impuesto equivale a una tasa anual sobre la suba de precio de

$$t_{ef} = 0{,}15 \cdot \frac{f\,(1+g)}{g+f}$$

- Con $f = 1$ (todo se realiza cada año) es 15%; si nunca se vende, tiende a cero. Una prueba automática verifica la fórmula contra una simulación explícita año por año.
- $f$ se mide con las mismas reglas para cada cartera: un backtest de las reglas de rebalanceo de la política sobre 2016-2026, más las ventas que hacen falta para pagar los retiros por encima de la renta cobrada. Da {{cartera.realizacion}} por año en la cartera y {{cartera.realizacion_benchmark}} en el 50/50, que rota menos porque no tiene acciones individuales con tope.
- Para el fondo amplio de EE.UU. la tasa efectiva queda cerca de 10%.
- El optimizador usa el supuesto más conservador: 15% todos los años y sin los costos de los fondos. Con el supuesto de realizar, la cartera óptima cambiaría 0,1% (NVIDIA +0,1 punto, Visa −0,1). Los pesos se mantienen, y todas las cifras de retorno y de la simulación usan el supuesto de realizar y descuentan los costos de los fondos.

Por esto la renta fija pierde más de un tercio de su retorno y las acciones de la cartera, entre 16% y 23%.

## Optimización

Se maximiza el retorno esperado después de impuestos sujeto a:

- volatilidad de 9% como máximo, con la covarianza de Ledoit y Wolf;
- pesos por clase dentro de los rangos de la política;
- 5% como máximo por acción y 30% por fondo;
- el fondo amplio de EE.UU. con al menos 20%;
- sin ventas en corto y sumando 100%.

La regla de "0 o al menos 2% por acción" convierte al problema en uno con variables discretas. Se resuelve en dos pasos:

1. **Iteración.** Se optimiza, las acciones que quedan entre 0 y 2% se fijan en 0 y se vuelve a optimizar.
2. **Reingreso.** Cada acción que salió se prueba forzada al 2% y vuelve si mejora el resultado.

## Carteras de comparación

- Equilibrio sin opiniones: el mismo optimizador con $\mu = \pi$.
- Mínima varianza.
- Paridad de riesgo jerárquica (López de Prado, 2016):
  - Agrupa los activos por correlación y reparte el riesgo de arriba hacia abajo, sin usar retornos esperados.
  - Sin restricciones, pone 99,6% en letras del Tesoro (la de menor varianza). Por eso se la ajusta a la cartera más cercana que cumple los rangos.
- El 50/50 armado con nuestros activos (la cartera neutra del modelo de Black y Litterman).

## Simulación de retiros

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
