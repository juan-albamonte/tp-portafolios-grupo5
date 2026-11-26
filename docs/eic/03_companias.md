# EIC 3. Compañías: cartera final y views

Fecha de corte: 15/11/2026. Sale del escenario de `01_economia.md` y de los sectores y el screening de `02_industria.md`. La nota ESG es el puntaje de S&P Global, con mínimo 25 (ver `nota_esg.md`). Los números de cada acción vienen del screening (Yahoo Finance, 15/11). La volatilidad es la anual de retornos diarios en 10 años (2016-2026).

## La cartera: 14 activos analizados, 12 posiciones finales

Los 14 activos de abajo son los que pasaron a la optimización. Con las reglas del checkpoint 4 y del cierre (piso de 20% en ESGV, piso de 10% en Europa, liquidez 3-10%, acción individual 0 o al menos 2%), el optimizador deja 12 posiciones: los 5 fondos más NVDA, V, LLY, ETN, ASML, NVS y RELX. MA y PG quedan en 0 (ver «Consideradas, el optimizador no las tomó»).

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

## Fondos

| Fondo | Comisión anual | Activos | Por qué este y no otro |
|---|---|---|---|
| BIL | 0,135% | USD 48.500 M | Letras de 1 a 3 meses, con historia desde 2007. Se descartó SGOV, que tiene historia corta (checkpoint 2). |
| IEF | 0,15% | USD 43.500 M | Su plazo de 7 a 10 años es la definición de la clase y del benchmark. IEI (3 a 7 años) tiene menos duración que la que pide la clase. |
| SCHP | 0,03% | USD 17.500 M | Replica los TIPS de todos los plazos, igual que TIP, y cuesta 0,15 puntos menos por año. VTIP (0 a 5 años) es más corto que la clase. |
| VCEB | 0,12% | USD 1.200 M | Es el único fondo de bonos corporativos con exclusión de fósiles y armas (LQD, VCIT y SUSC no pasan el filtro). Opera poco volumen, así que se compra con órdenes límite. |
| ESGV | 0,09% | USD 13.000 M | Mercado de EE.UU. con exclusiones verificadas (`nota_esg.md`). ESGU tiene CEDEAR, pero no pasa el filtro de petróleo. |

Comisiones y activos: Yahoo Finance al 15/11/2026.

## Acciones de EE.UU.

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

### Mastercard (MA): alcista (reemplaza a JPM, 16/11)

**Por qué el cambio.** JPMorgan tenía ESG 29: pasaba el mínimo de 25, pero es el mayor financiador de combustibles fósiles y la clienta rechaza las industrias altamente contaminantes. Mastercard tiene ESG 58, verificado en vivo en S&P Global (actualizado el 18/03/2026).

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

## Acciones de Europa

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

## Consideradas y descartadas

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
| JPMorgan (JPM) | Reemplazada por MA el 16/11: ESG 29 y mayor financiador de combustibles fósiles, contra el mandato de la clienta. |
| Unilever (UL), Coca-Cola (KO) | UL es la mejor del sector, pero los tres cupos europeos ya estaban. KO cotiza a 28 veces. |
| Alphabet (GOOGL) | Sumaría una cuarta apuesta a la IA, con ESG 29. Su crecimiento esperado sale negativo por una base 2026 inflada. |

## Consideradas, el optimizador no las tomó (checkpoint 4, 16/11)

Pasaron el filtro ESG, el screening y la tesis, y entraron a la optimización. Con el piso de 20% en ESGV y la vol de 9% al máximo, el espacio para acciones individuales de EE.UU. se achica y el optimizador las deja en 0. No salieron por la regla del 2%: quedan en 0 aun sin esa regla.

| Acción | Por qué el optimizador no la toma |
|---|---|
| Mastercard (MA) | La tesis de pagos sigue en la cartera a través de Visa (2,1%). V y MA tienen correlación 0,88, y la view V4 es sobre la canasta de las dos. Con una correlación tan alta, el optimizador elige una sola: Visa tiene menos volatilidad (24,6% contra 27,0%). Forzar MA al 2% cuesta 0,004 pp de retorno neto: el optimizador está casi indiferente. |
| Procter & Gamble (PG) | Es la acción con menor retorno neto esperado de la cartera (4,1%), porque su beta baja le da poco retorno de equilibrio y no tiene view. La cobertura contra el riesgo de IA que buscábamos con PG ya la dan los bonos: IEF, SCHP y BIL suman 51,5%. |

RELX estuvo en esta lista hasta que el piso de Europa pasó a 10%: ahora entra con 2%. MA y PG se mantienen en la lista de seguimiento. Si en la revisión anual cambia la tesis o se relaja el piso de ESGV, son las primeras candidatas.

## Views (`data/views.csv`)

Formato de Meucci (2010, ec. 11): v = Pπ + η · 0,25 · √(PΣP'). Ω = (1/c) · diag(u) · PΣP' · diag(u) (ec. 13), con c = 1 por defecto. La escala (0,25) y c están en `tp/config.py`.

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

## Cartera neutra (π = λΣw_b)

Se calcula con el criterio de `tp/equilibrio.py`. La capitalización total implícita del universo de ESGV es de USD 61,5 billones.

| BIL | IEF | SCHP | VCEB | ESGV | NVDA | V | MA | LLY | ETN | PG | ASML | NVS | RELX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5,0% | 20,0% | 10,0% | 15,0% | 35,4% | 2,6% | 0,5% | 0,4% | 0,8% | 0,1% | 0,3% | 6,1% | 3,2% | 0,7% |

ESGV conserva 88% de la clase de EE.UU. En Europa, la capitalización le da a ASML 61% de la clase: 6,1% de la cartera, por encima del tope de 5%. No hay contradicción. El neutro solo fija el punto de partida de los retornos (π), y el tope de 5% por acción lo aplica el optimizador.
