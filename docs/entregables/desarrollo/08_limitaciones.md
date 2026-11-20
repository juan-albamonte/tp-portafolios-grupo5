# Limitaciones

## Retornos de largo plazo

Son la variable que más pesa en el resultado. Con 1 punto menos por año en todas las clases:

- la probabilidad de quedarse sin dinero en el nivel lujo con gasto fijo sube de {{sensibilidades.base (vol 9%).A lujo}} a {{sensibilidades.retornos −1 pp.A lujo}} si compra y de {{sensibilidades.base (vol 9%).B lujo}} a {{sensibilidades.retornos −1 pp.B lujo}} si alquila;
- el retiro seguro sin barandas baja de USD {{sensibilidades.base (vol 9%).seguro A: compra}} a {{sensibilidades.retornos −1 pp.seguro A: compra}} por mes.

Los supuestos están en rango con los de J.P. Morgan, Vanguard y BlackRock, pero cada año se revisan contra el mercado.

## Distribución de los retornos

La simulación usa una lognormal con correlaciones fijas. No reproduce colas más gruesas ni el aumento de las correlaciones en las crisis. El escenario de estrés de 2008 cubre parte de ese riesgo, no todo.

## Correlación entre bonos y acciones

En 2007-2026 fue negativa para el Tesoro (−0,29). En los últimos diez años fue positiva por la suba de tasas de 2022. Si se repite un episodio de inflación con tasas en alza, los bonos diversifican menos de lo que supone la covarianza.

## Impuestos simplificados


- La ganancia de capital paga al vender, con una tasa efectiva calibrada a la rotación del backtest 2016-2026 ({{cartera.realizacion}} de las acciones por año). Es un estado estacionario: no captura la venta total cuando la plata se acaba ni la ganancia que queda sin realizar al final del horizonte. Si la rotación real fuera mayor, el impuesto se acercaría al 15% anual, el supuesto conservador de la versión anterior.
- El optimizador usa el supuesto de 15% todos los años. Con el de realizar, la cartera óptima cambiaría 0,1%.
- Las pérdidas compensan ganancias en el mismo año; la norma permite trasladarlas cinco años.
- Las tasas son las vigentes: dividendos e intereses del exterior, 35% (alícuota marginal máxima de la escala del artículo 94 de la Ley de Impuesto a las Ganancias, la que corresponde a este patrimonio); venta de acciones del exterior, 15% (artículo 94, segundo párrafo); Bienes Personales, 0,75% en 2026 y 0,25% desde 2027 (Ley 27.743, alícuota máxima).
- La Ley 27.743 exime la casa habitación hasta ARS 350.000.000 (monto que se actualiza cada año) y lleva el mínimo no imponible general a ARS 100.000.000. El modelo grava el departamento completo y la cartera sin mínimo: es conservador.

## Pesos por acción

Los pesos por clase son estables ante cambios en la confianza en las opiniones, en las opiniones mismas y en la volatilidad objetivo. Los pesos entre acciones de EE.UU. no lo son: el optimizador está casi indiferente entre Visa, Mastercard, Eaton y ASML (forzar Mastercard al 2% cuesta 0,004 puntos de retorno). Las acciones individuales expresan una tesis; su peso exacto no es una predicción.

## Historia completada

VCEB y ESGV tienen historia corta y se completaron con índices muy correlacionados (0,988 y 0,992). La volatilidad de VCEB puede estar sobrestimada en 1,7 puntos, lo que también es conservador.

## Vivienda

Se supone que el departamento mantiene su valor real y que el alquiler sigue a la inflación. El análisis no incluye el riesgo de concentrar USD 1 millón en un solo inmueble ni la falta de liquidez del departamento.
