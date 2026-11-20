# Nota: fuente de la calificación ESG

**Qué cambió.** El plan era calificar a cada empresa con el rating de MSCI (escala AAA a CCC) y controlarlo con Sustainalytics. El 15/11/2026 comprobamos que ninguna de las dos fuentes sigue siendo pública:
- **MSCI** cerró su buscador público (*ESG Ratings & Climate Search Tool*). La página ahora dice que los clientes acceden a los datos por la plataforma MSCI ONE.
- **Sustainalytics** redirige las páginas por empresa a un formulario comercial, y Yahoo Finance ya no muestra sus puntajes.

**Fuente que usamos.** El *S&P Global ESG Score*, de 0 a 100. Es la única calificación por emisor que sigue siendo pública. El puntaje se calcula contra empresas de la misma industria, así que compara bien dentro de un sector y mal entre sectores. Cada valor está en `data/esg.csv`, con el link a la página de la empresa.

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
- La regla está en `tp/universo.py`, que además se niega a marcar como seleccionada una acción sin nota verificada.

**Fondos.** No se califican con este puntaje. Se exige que su índice excluya combustibles fósiles, armamento y tabaco, y lo verificamos el 15/11/2026 en las páginas de Vanguard:
- **ESGV** excluye entretenimiento para adultos, alcohol, tabaco, cannabis, juego, armas (controvertidas, nucleares, convencionales y civiles), energía nuclear, y carbón, petróleo y gas.
- **VCEB** aplica las mismas exclusiones a los bonos corporativos.
- Los fondos de Tesoro y TIPS son deuda soberana de EE.UU.
