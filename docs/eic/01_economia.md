# EIC 1. Economía: escenario base a 12-24 meses

Fecha de corte: 15/11/2026. Mercado al 12-13/11/2026.

## Dónde estamos

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

## Escenario base (12-24 meses)

- **Inflación:** baja de a poco a medida que el petróleo converge a la curva de futuros (USD 78-79 para 2027, FMI). En EE.UU. pasa de 3,6% en 2026 a 2,8% en 2027. En la zona euro, de 3,1% a 2,8%.
- **Tasas:** la Fed sostiene 3,75-4,00% o sube una vez más, y no baja antes de fines de 2027. El BCE se queda en 2,50%. El UST a 10 años se mueve entre 4,75% y 5,25%, y la prima por plazo se mantiene alta (JPM: "rebuilt term premia").
- **Crecimiento:** EE.UU. crece 2,3% por año sin recesión. La zona euro crece 1,1-1,2%, con más gasto público en 2027.
- **Dólar:** se deprecia de a poco, a ~0,5% por año (supuesto de JPM LTCMA 2027 para el retorno de mercados no estadounidenses).
- **Acciones:** el múltiplo de EE.UU. ya bajó a su menor nivel en tres años porque las ganancias crecieron más que los precios. Para 2027 se espera que las ganancias sigan creciendo (+16% de consenso), pero no queda margen para que suba el múltiplo. Europa es más barata y paga más dividendo, pero crece menos.

## Del escenario a los retornos de largo plazo (10-15 años)

Inflación de largo plazo: **2,25%**, la del breakeven a 10 años (2,24%), coherente con el 5y5y. Estos retornos alimentan el Monte Carlo después de impuestos. El posterior de Black-Litterman se usa solo para optimizar. Con las views elegimos la cartera, pero para ver si le alcanza la plata no contamos con que acertemos.

| Clase | Nominal (compuesto, USD) | Real | Aritmético* | Lógica |
|---|---|---|---|---|
| Liquidez | 3,50% | 1,22% | 3,50% | Tasa real neutral ~1,2% + inflación. Hoy rinde 4,14%, pero la tasa vuelve a la neutral cuando pasa el shock. |
| Tesoro (7-10 años) | 4,80% | 2,49% | 5,03% | A 10 años, un bono de duración parecida rinde lo que paga al entrar (~5,0%). Le resto algo por si la curva se empina. JPM: 4,6%. |
| TIPS | 4,90% | 2,59% | 5,09% | Tasa real 5-10 años 2,64-2,86% + inflación 2,25%. |
| Corporativos IG | 5,50% | 3,18% | 5,87% | Tesoro de duración similar (~4,95%) + spread 0,89% − pérdidas esperadas por default y downgrades ~0,3%. El spread está ajustado: no supongo que se achique. |
| Acciones EE.UU. | 7,00% | 4,65% | 8,73% | Dividendo + recompras ~1,7% + crecimiento real de ganancias ~3% + inflación − ~0,5%/año porque el múltiplo vuelve a su promedio. JPM: 7,5%. |
| Acciones Europa (en USD) | 7,25% | 4,89% | 9,68% | Dividendo 2,7% + recompras ~0,5% + crecimiento real ~1,5% + inflación EUR 2% − múltiplo levemente caro + dólar más débil ~0,5%. |

\* Aritmético = compuesto más la corrección lognormal con la vol histórica de cada clase (≈ σ²/2). Es la media que usan Black-Litterman y el Monte Carlo (`tp/escenario.py`).

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

Sumando los bloques: EE.UU. da ~6,5% y Europa ~7,2%. Las casas no coinciden en el orden. Vanguard pone ex-EE.UU. arriba (6,3% contra 5,8%), J.P. Morgan queda prácticamente igual (7,5% contra ~7,5%) y BlackRock pone EE.UU. arriba (9,0% contra 7,4%). Por eso la diferencia que dejamos es chica: un cuarto de punto. Además, el IPS ya limita Europa a un rango de 5% a 20% porque el riesgo de estancamiento es real.

**Prima por riesgo de acciones sobre el Tesoro: ~2,2 puntos.** Es angosta. Con el Tesoro pagando 5% y las acciones en valuaciones exigentes, la renta fija vuelve a pagar por sí sola, y eso sostiene un benchmark 50/50 para alguien que vive de la cartera.

## Exceso del benchmark y λ (calibración del equilibrio)

- **Benchmark 50/50:** 6,0% compuesto, 7,0% aritmético.
- **Exceso aritmético sobre la tasa corta de largo plazo:** 7,03% − 3,50% = **3,53%** (`Mercado.exceso_esperado_benchmark`). Este es el w_b'π del equilibrio.
- **λ implícito:** con la vol histórica del benchmark (10,2%) sería 3,53% / 10,2%² ≈ 3,4. Con la covarianza de Ledoit-Wolf de los 14 activos finales, la cartera neutra tiene 10,7% de vol y λ = **3,06**, que es el que usa el modelo. Los dos están dentro del rango habitual de aversión al riesgo (2-4).
- **Cartera neutra (w_b) a nivel activo** (`tp/equilibrio.py`):
  - El 50/50 fija el peso de cada clase.
  - En renta fija, el peso de la clase se reparte en partes iguales entre sus fondos.
  - En acciones de EE.UU., cada acción suelta pesa lo que pesa en el mercado: su capitalización sobre la del universo de ESGV. Esa capitalización total sale implícita de las mayores posiciones del fondo. ESGV se queda con el resto.
  - En Europa, el peso va por capitalización entre las elegidas.

  Así la cartera neutra es el mercado y no una apuesta a 4-6 nombres.

## Riesgos: qué rompe el escenario

| Riesgo | Señal a mirar | Efecto en la cartera |
|---|---|---|
| Escalada en Medio Oriente: Brent > USD 110 | Brent, breakeven 5 años | Inflación de segunda vuelta, más subas, y acciones y bonos que caen juntos (como en 2022). Los TIPS y la liquidez amortiguan. |
| Se desinfla la expectativa de IA (lo marca el FMI) | Revisiones de ganancias en tecnología, capex de hiperescaladores | Corrección del S&P 500, que está concentrado en tecnología. Pega más en acciones de EE.UU. que en Europa. |
| Fiscal de EE.UU. y prima por plazo (déficit estructural ~4% del PIB, FMI) | UST 10a > 5,5%, subastas | Pérdida en el Tesoro largo. La duración moderada (7-10 años) limita el golpe. |
| Estancamiento europeo | PMI, crédito, HICP core | Retorno más bajo de las acciones europeas (de ahí el rango chico en el IPS). |
| Spreads de crédito ajustados (IG 0,89%) | OAS IG > 1,5% | Corporativos peor que el Tesoro. Por eso no suponemos que el spread se achique. |
| A favor: el petróleo vuelve a USD 78 y la inflación cede antes | Futuros de Brent, IPC core | La Fed baja antes y los bonos suben por precio: el escenario mejora. |

## Fuentes

- FRED, Federal Reserve Bank of St. Louis: series citadas en la tabla, bajadas el 15/11/2026 (`tp/mercado.py`).
- Federal Reserve, comunicado del FOMC del 28/10/2026.
- BCE, decisiones de política monetaria del 11/06/2026 y del 10/09/2026, con las proyecciones del staff de septiembre (HICP 3,0% / 2,5% / 2,1% y PIB 0,9% / 1,4% / 1,5% para 2026-2028).
- FMI, World Economic Outlook, octubre 2026, y DataMapper (crecimiento e inflación por país). WEO Update de julio 2026 para el supuesto de petróleo.
- J.P. Morgan Asset Management, 2027 Long-Term Capital Market Assumptions, comunicado del 19/10/2026. Guide to the Markets Europe, datos al 30/09/2026.
- FactSet, Earnings Insight, 05-13/11/2026: P/E forward del S&P 500 17,7; ganancias +33% en 2026 y +16% esperado en 2027.
- Vanguard, "Vanguard Capital Markets Model forecasts" (21/10/2026, simulaciones al 30/09/2026) y "Where to find value in the U.S. markets" (21/10/2026).
- BlackRock Investment Institute, Capital Market Assumptions, planilla de agosto 2026 (datos al 30/06/2026).
- Yahoo Finance: rendimiento por dividendo de SPY y VGK, 15/11/2026.
