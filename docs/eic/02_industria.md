# EIC 2. Industria: sectores y screening

Fecha de corte: 15/11/2026. Parte del escenario base de `01_economia.md`:
- shock de petróleo (Brent USD 92);
- tasas altas por más tiempo (Fed 3,75-4,00%, UST 10 años 5,10%);
- ciclo de inversión en IA;
- Europa casi estancada (1,1-1,2%);
- dólar que se debilita de a poco.

Energía y defensa no son opciones: el filtro ESG las excluye.

## Tesis por sector

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

## Screening

Universo: las 31 acciones de `data/universo.csv`. Los datos de mercado vienen de Yahoo Finance (yfinance) al 15/11/2026 y quedan guardados en `data/fundamentals.csv`. El código está en `tp/screening.py`.

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
- La fuente pública que queda por emisor es el **S&P Global ESG Score**, de 0 a 100 y relativo a la industria. Está en `data/esg.csv`, con el link de cada empresa:
  - 9 páginas leídas en vivo.
  - 18 tomadas de la página indexada por el buscador; las 3 que también leímos en vivo coincidieron con diferencias de ±1 punto.
  - Meta, J&J y Santander: el puntaje vigente solo se publica en canales pagos o no tiene página. Para esas tres usamos el CSA 2024 del documento público de S&P para el rebalanceo del DJSI, marcado.
  - HSBC no tiene puntaje público.
- Como el puntaje se mide contra pares de la misma industria, sirve para rankear dentro del sector, no entre sectores. Los ratings de memoria de `candidatos.csv` (escala MSCI) ya no se usan en el entregable.

### Resultados

**Actualización 3c (15/11):** la política fija un mínimo de 25 en el ESG de S&P. Salen Amazon (21) y J&J (24, CSA 2024), y quedan 29 acciones. Sin J&J, cuatro farmas empatan en 0,54 (LLY, NVO, NVS, SNY): en salud, el screening no decide y la elección va por tesis.

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

## Lista preliminar (9 acciones, 5 europeas)

Las reglas están en `tp/screening.py:preliminar` y la salida en `outputs/preliminar.csv`:
- **Sector favorecido:** entra la mejor de cada sector favorecido, y la segunda solo si queda en la mitad de arriba (puntaje ≥ 0,5).
- **Calidad propia:** de cada sector no favorecido, entra la mejor si su puntaje es ≥ 0,60.
- **Mínimo europeo:** si quedan menos de 4 europeas, se completa con las de mejor puntaje.

Resultado:
- **Sector favorecido:** NVDA, ASML, RELX, V, HSBC, LLY, NVO.
- **Calidad propia:** UL (consumo básico) y META (comunicaciones).
- **Sin cupo:** HD, ahora sola en su sector, queda en 0,50 y no llega al umbral.

En la 3b, antes de la regla ESG, la lista tenía 10 acciones con NVS y HD. La selección final, junto con las consideradas y descartadas, está en `03_companias.md`.
