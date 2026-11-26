// Deck v3 del TP (30 minutos: 26 láminas + anexo). Desde la raíz del proyecto, después de `python -m tp.correr`:
//   node docs/entregables/deck/build_deck.js
// Todo hablado a Valentina, en segunda persona; retornos en dólares nominales; la comisión, como lo que le cuesta.
// Todas las cifras salen de outputs/cifras.json (mismo redondeo que gráficos, textos y planilla) y los gráficos de
// outputs/graficos/deck (sin título: lo pone la lámina). Si cambia el modelo, se regenera sin tocar este archivo.
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const RAIZ = path.resolve(__dirname, "..", "..", "..");
const C = JSON.parse(fs.readFileSync(path.join(RAIZ, "outputs", "cifras.json"), "utf8"));
const G = (f) => path.join(RAIZ, "outputs", "graficos", "deck", f);
const SALIDA = path.join(__dirname, "..", "deck.pptx");

const NAVY = "1F3A5F", TINTA = "1B1B1B", GRIS = "52514E", APAGADO = "898781", CLARO = "EEF1F5", LINEA = "C9CED6";
const AZUL = "2A78D6", NARANJA = "EB6834", BLANCO = "FFFFFF", SUAVE = "CADCFC", ROSADO = "FDEEE7";
const TIT = "Cambria", CUERPO = "Calibri";

const ROL = {
  asesor: "Agustín · Asesor", research: "Juan · Research", gestor: "Maxi · Gestor de cartera", riesgo: "Pedro · Riesgos",
  anexo: "Anexo",
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Una cartera para vivir de ella toda la vida";
pres.author = "Grupo 5";
pres.theme = { headFontFace: TIT, bodyFontFace: CUERPO };

pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: BLANCO },
  objects: [
    { text: { text: "Grupo 5 · Administración de Portafolios · UdeSA", options: {
      x: 0.6, y: 7.0, w: 7, h: 0.3, fontFace: CUERPO, fontSize: 10, color: APAGADO, margin: 0 } } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.3, w: 10.1, h: 1.15, fontFace: TIT,
      fontSize: 28, bold: true, color: NAVY, valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontFace: CUERPO, fontSize: 10, color: APAGADO, align: "right" },
});
pres.defineSlideMaster({
  title: "OSCURO",
  background: { color: NAVY },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 0.8, w: 11.7, h: 1.9, fontFace: TIT,
      fontSize: 38, bold: true, color: BLANCO, valign: "bottom", margin: 0 }, text: "" } },
  ],
});

// --------------------------------------------------------------------- ayudas

function lamina(rol, titulo, nota) {
  const s = pres.addSlide({ masterName: "CONTENIDO" });
  s.addText(titulo, { placeholder: "title" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 10.85, y: 0.6, w: 1.9, h: 0.42, fill: { color: CLARO },
    line: { color: CLARO }, rectRadius: 0.21, objectName: "Quién habla" });
  s.addText(ROL[rol], { x: 10.85, y: 0.6, w: 1.9, h: 0.42, fontFace: CUERPO, fontSize: 11, bold: true, color: NAVY,
    align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addNotes(nota);
  return s;
}

function oscura(titulo, nota) {
  const s = pres.addSlide({ masterName: "OSCURO" });
  s.addText(titulo, { placeholder: "title" });
  s.addNotes(nota);
  return s;
}

function texto(s, t, x, y, w, h, o = {}) {
  s.addText(t, { x, y, w, h, fontFace: CUERPO, fontSize: 16, color: TINTA, valign: "top", margin: 0, isTextBox: true,
    ...o });
}

function dato(s, x, y, w, grande, rotulo, o = {}) {
  texto(s, grande, x, y, w, 0.8, { fontFace: TIT, fontSize: o.size || 36, bold: true, color: o.color || NAVY,
    valign: "bottom" });
  texto(s, rotulo, x, y + 0.85, w, o.h || 0.75, { fontSize: o.rotulo || 14, color: o.ink || GRIS });
}

function caja(s, x, y, w, h, fill) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill || CLARO }, line: { color: fill || CLARO },
    rectRadius: 0.08 });
}

function tarjeta(s, x, y, w, h, titulo, lineas, o = {}) {
  caja(s, x, y, w, h, o.fill);
  texto(s, titulo, x + 0.25, y + 0.18, w - 0.5, 0.45, { fontSize: o.tsize || 17, bold: true, color: o.color || NAVY });
  if (lineas.length) {
    s.addText(lineas.map((l, i) => ({ text: l, options: { bullet: o.bullet !== false, breakLine: i < lineas.length - 1 } })),
      { x: x + 0.25, y: y + 0.7, w: w - 0.5, h: h - 0.85, fontFace: CUERPO, fontSize: o.size || 14, color: o.ink || TINTA,
        valign: "top", margin: 0, paraSpaceAfter: 5, isTextBox: true });
  }
}

// Recuadro chico con el nombre técnico y una línea de qué hace.
function tecnico(s, x, y, w, nombre, que) {
  caja(s, x, y, w, 0.62, "F6F6F4");
  s.addText([{ text: `${nombre}: `, options: { bold: true, color: NAVY } }, { text: que, options: { color: GRIS } }],
    { x: x + 0.18, y, w: w - 0.36, h: 0.62, fontFace: CUERPO, fontSize: 12, valign: "middle", margin: 0, isTextBox: true });
}

function pngTam(f) {
  const b = fs.readFileSync(f);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

function grafico(s, archivo, x, y, maxW, maxH, alt) {
  const f = G(archivo);
  const t = pngTam(f);
  let w = maxW, h = (maxW * t.h) / t.w;
  if (h > maxH) { h = maxH; w = (maxH * t.w) / t.h; }
  s.addImage({ path: f, x: x + (maxW - w) / 2, y, w, h, altText: alt });
}

function tabla(s, filas, x, y, w, colW, o = {}) {
  const rows = filas.map((f, i) => f.map((c, j) => ({ text: String(c), options: {
    ...(i === 0 ? { bold: true, color: NAVY, fill: { color: CLARO } } : { color: TINTA }),
    ...(o.destacar && i > 0 && o.destacar(i, j) ? { bold: true, color: AZUL } : {}),
    align: j === 0 || (o.izq || []).includes(j) ? "left" : "center" } })));
  s.addTable(rows, { x, y, w, colW, fontFace: CUERPO, fontSize: o.size || 14, border: { type: "solid", pt: 0.75, color: LINEA },
    valign: "middle", margin: 0.06, rowH: o.rowH || 0.42 });
}

const num = (t) => parseFloat(String(t).replace(/\./g, "").replace(",", ".").replace("−", "-"));
const miles = (x) => Math.round(x).toLocaleString("es-AR");

const E = C.escenarios, S = C.retiro_seguro, K = C.cartera, B = C.benchmark_historico, N = C.nominal;
const MV = C.misma_vara, ALT = C.alternativas, CC = C.costos_cliente.A, MON = C.monitoreo, R = C.riesgo;
const lujoA = E["A lujo"], lujoB = E["B lujo"];
const fijo = num(E["A base"].gasto), lujo = num(lujoA.gasto), bono = lujo - fijo;
const peso = Object.fromEntries(K.activos.map((a) => [a.ticker, a]));
const riesgo = Object.fromEntries(R.activos.map((a) => [a.ticker, a]));
const ej = MON.ejemplos.compra_tras_caida;
const MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
  "noviembre", "diciembre"];
const mesAnio = (iso) => { const [y, m] = iso.split("-"); return `${MESES[+m - 1]} de ${y}`; };
const mayus = (t) => t[0].toUpperCase() + t.slice(1);

// --------------------------------------------------------------------- 1-7: Agustín (asesor)

{
  const s = oscura("El caso: Valentina, 35 años, USD 15 millones y ningún otro ingreso",
    "Agustín, para los profesores: el caso en una lámina y el equipo. Desde la próxima le hablamos a Valentina.");
  [["35 años, recién divorciada", "Sin hijos; no trabaja y no piensa volver a hacerlo"],
    ["USD 15 millones", "Todo su patrimonio, en efectivo; vive de la cartera"],
    ["Residente argentina", "Opera desde un bróker de EE.UU., en dólares"],
    ["Valores claros", "Nada de armas, tabaco ni contaminantes; le gusta la vida de lujo"]].forEach(([t, d], i) => {
    texto(s, t, 0.8 + i * 3.0, 3.2, 2.8, 0.45, { fontSize: 18, bold: true, color: BLANCO });
    texto(s, d, 0.8 + i * 3.0, 3.7, 2.8, 0.9, { fontSize: 14, color: SUAVE });
  });
  [["Agustín", "Asesor"], ["Juan", "Research"], ["Maxi", "Gestor de cartera"], ["Pedro", "Riesgos"]].forEach(([n, r], i) => {
    texto(s, n, 0.8 + i * 3.0, 5.1, 2.8, 0.4, { fontSize: 17, bold: true, color: BLANCO });
    texto(s, r, 0.8 + i * 3.0, 5.48, 2.8, 0.35, { fontSize: 13, color: SUAVE });
  });
  texto(s, "A partir de acá le hablamos a Valentina.", 0.8, 6.3, 11.7, 0.5,
    { fontFace: TIT, fontSize: 22, bold: true, italic: true, color: BLANCO });
}

{
  const s = lamina("asesor", "Valentina, esto es lo que entendimos de vos",
    "Perfil en segunda persona: tolerancia moderada, compostura baja, capacidad alta; manda la compostura y por eso el techo de 9%.");
  [["Tolerancia al riesgo", "Moderada", "Aceptás que tu cartera se mueva si eso protege tu poder de compra."],
    ["Compostura", "Baja", "Las caídas te inquietan: por eso te mostramos todo sin sustos y tu sueldo no depende del mes."],
    ["Capacidad", "Alta", "Tu patrimonio es grande frente a tu gasto y tenés más de 50 años por delante."]].forEach(([d, n, q], i) => {
    const y = 1.75 + i * 1.4;
    caja(s, 0.6, y, 12.15, 1.22);
    texto(s, d, 0.85, y + 0.17, 2.6, 0.4, { fontSize: 14, color: GRIS });
    texto(s, n, 0.85, y + 0.52, 2.6, 0.55, { fontFace: TIT, fontSize: 26, bold: true, color: i === 1 ? NARANJA : NAVY });
    texto(s, q, 3.6, y + 0.2, 8.9, 0.85, { fontSize: 17, valign: "middle" });
  });
  texto(s, "9%", 0.6, 5.95, 2.2, 0.75, { fontFace: TIT, fontSize: 36, bold: true, color: AZUL, valign: "middle" });
  texto(s, `Es el techo de volatilidad de tu cartera: por debajo del ${MV.benchmark_indices.vol} del mercado. Manda tu compostura, no tu capacidad.`,
    2.4, 5.95, 10.35, 0.75, { fontSize: 17, valign: "middle" });
}

{
  const s = lamina("asesor", "Lo que querés lograr y lo que no negociás",
    "Objetivos y restricciones; los impuestos con las alícuotas de hoy y el contador que sigue cada cambio.");
  tarjeta(s, 0.6, 1.7, 5.9, 3.3, "Lo que querés lograr", [
    "Un sueldo mensual que reemplace un ingreso",
    "Que tu plata no pierda poder de compra",
    "No quedarte nunca sin plata: que alcance en 95 de cada 100 escenarios"], { size: 16 });
  tarjeta(s, 6.85, 1.7, 5.9, 3.3, "Lo que no negociás", [
    "Sin armas, tabaco ni contaminantes (nota ESG de 25 o más)",
    "Solo mercados regulados de EE.UU. y Europa",
    "Liquidez todos los meses y dos años de gasto de reserva",
    "Entender qué hacemos con tu plata"], { size: 16 });
  tarjeta(s, 0.6, 5.2, 12.15, 1.6, "Impuestos: las alícuotas de hoy, y nosotros encima de cada cambio", [
    "Renta (intereses y dividendos) 35%; ganancias por venta 15%; Bienes Personales 0,75% en 2026 y 0,25% desde 2027.",
    "Si una ley cambia, nuestro contador lo ve antes y ajustamos el plan."],
  { fill: ROSADO, color: NARANJA, size: 14 });
}

{
  const s = lamina("asesor", "Tu casa: comprar te deja más que alquilar",
    "Comprar el depto rinde más que invertir ese millón: el alquiler que te ahorrás contra lo que rinde la cartera, en nominal.");
  tarjeta(s, 0.6, 1.7, 5.9, 2.2, "Si comprás (USD 1 M)", [`Invertís USD ${C.capital.A}`, `Gasto de nivel lujo: USD ${lujoA.gasto} por mes`],
    { size: 15 });
  tarjeta(s, 6.85, 1.7, 5.9, 2.2, "Si alquilás", [`Invertís USD ${C.capital.B}`, `Gasto de nivel lujo: USD ${lujoB.gasto} por mes (con el alquiler)`],
    { size: 15 });
  dato(s, 0.6, 4.2, 3.8, `USD ${N.alquiler_implicito_mes}`, "por mes te ahorrás si comprás (alquiler menos ABL y mantenimiento)");
  dato(s, 4.75, 4.2, 3.8, N.depto, "por año rinde tu depto, en dólares, sin impuesto a las ganancias", { color: AZUL });
  dato(s, 8.9, 4.2, 3.85, N.neto_cartera_1d, "por año rinde la cartera sin contar nuestras opiniones, después de impuestos y costos", { color: GRIS });
  texto(s, "Comprar cuesta 7,5% de gastos (USD 75.000, ya descontados) y concentra en un inmueble; suponemos que el depto solo mantiene su valor.",
    0.6, 6.25, 12.15, 0.5, { fontSize: 13, color: APAGADO });
}

{
  const s = lamina("asesor", "Tres niveles de vida para elegir",
    "El presupuesto por rubro en tres niveles, en dólares de hoy por mes; la diferencia entre comprar y alquilar es el alquiler.");
  tabla(s, [["Nivel", "Si comprás (USD/mes)", "Si alquilás (USD/mes)", "Qué cambia"],
    ["Base", E["A base"].gasto, E["B base"].gasto, "Una empleada, sin chofer, viajes moderados"],
    ["Lujo", lujoA.gasto, lujoB.gasto, "Dos empleadas y chofer, 3 o 4 viajes por año"],
    ["Alto", E["A alto"].gasto, E["B alto"].gasto, "Personal full time, tres autos, viajes de alta gama"]],
  0.6, 1.85, 12.15, [1.6, 2.5, 2.5, 5.55], { size: 17, rowH: 0.66, izq: [3] });
  texto(s, "Montos en dólares de hoy: cada año suben con la inflación. Sin el Bienes Personales, que calculamos aparte.",
    0.6, 4.75, 12.15, 0.4, { fontSize: 13, color: APAGADO });
  dato(s, 0.6, 5.1, 6, `${(lujo * 12 / num(C.capital.A) * 100).toFixed(2).replace(".", ",")}% de tu capital`,
    "retirás por año en el nivel lujo si comprás", { color: AZUL, size: 32 });
}

{
  const s = lamina("asesor", "Las reglas de tu cartera",
    "La política en una lámina: benchmark, techo de riesgo, rangos, reglas por activo, revisión y rebalanceo.");
  [["Contra qué te medimos", ["Benchmark 50/50: seis índices pasivos", `Volatilidad esperada del mercado: ${MV.benchmark_indices.vol}`]],
    ["Cuánto riesgo", ["Volatilidad máxima de 9%", "Liquidez 3-10%, acciones de EE.UU. 25-45%, Europa 10-20%"]],
    ["Reglas por activo", ["Hasta 5% por acción y 30% por fondo", "Fondo amplio de EE.UU. con filtro ESG: al menos 20%"]],
    ["Cada cuánto miramos", ["Todos los meses, con vos", "Cada trimestre, el comité; cada año, la política"]],
    ["Cuándo rebalanceamos", [`Clase a más de 3 puntos de su objetivo, o ${MON.tolerancia_rango_pp} fuera de su rango`,
      `Acción por encima de ${MON.tope_accion_disparo}; los retiros salen de lo que sobra`]],
    ["Qué no hacemos", ["Sin apalancamiento ni derivados", "Sin monedas fuera del dólar y el euro"]],
  ].forEach(([t, l], i) => tarjeta(s, 0.6 + (i % 3) * 4.1, 1.7 + Math.floor(i / 3) * 2.6, 3.85, 2.4, t, l));
}

{
  const s = lamina("asesor", "Tu servicio y lo que te cuesta",
    "Qué recibís y cuánto te cuesta por año, en USD; todo ya está descontado en los números que te mostramos.");
  tarjeta(s, 0.6, 1.7, 6.3, 5.1, "Qué recibís", [
    "Un equipo de cuatro: asesor, research, gestor y riesgos",
    "Reunión mensual con vos, con un tema para aprender",
    "Informe mensual por baldes, sin sustos: liquidez, renta, crecimiento",
    "Comité de inversiones cada trimestre",
    "Informe anual con todo lo impositivo",
    "Contador coordinado por nosotros",
    "Te llamamos si el mercado cae más de 10%, antes de que preguntes"], { size: 15 });
  caja(s, 7.15, 1.7, 5.6, 5.1);
  texto(s, "Lo que te cuesta por año", 7.4, 1.88, 5.1, 0.45, { fontSize: 17, bold: true, color: NAVY });
  const tr = C.costos_cliente.tramos;
  tabla(s, [["Patrimonio (USD)", "Comisión"], ...tr.map((t) => [t.hasta ? `De ${t.desde} a ${t.hasta}` : `Más de ${t.desde}`, t.tasa])],
    7.4, 2.4, 5.1, [3.4, 1.7], { size: 13, rowH: 0.36 });
  tabla(s, [["Concepto", "USD por año", "%"],
    ["Comisión de gestión", CC.comision_usd, CC.comision_pct], ["Costos de los fondos", CC.fondos_usd, CC.fondos_pct],
    ["Total", CC.total_usd, CC.total_pct]], 7.4, 4.0, 5.1, [2.4, 1.6, 1.1],
  { size: 13, rowH: 0.36, destacar: (i) => i === 3 });
  texto(s, `≈ USD ${CC.total_mes_usd} por mes. Sin retrocesiones de terceros. Todo esto ya está descontado en los números que te mostramos.`,
    7.4, 5.65, 5.1, 1.0, { fontSize: 13, color: GRIS });
}

// --------------------------------------------------------------------- 8-13: Juan (research)

{
  const s = lamina("research", "El mundo en el que vas a invertir",
    "Juan. El escenario base con sus supuestos explícitos y lo que lo rompe.");
  [["USD 92 → 78", "Brent hoy y en 2027 (curva de futuros)"], ["4,1% → 2,25%", "Inflación de EE.UU. hoy y a largo plazo"],
    ["3,75-4,00%", "Tasa de la Fed, sin bajas hasta fines de 2027"], ["2,3%", "Crecimiento de EE.UU. por año, sin recesión"]]
    .forEach(([g, r], i) => dato(s, 0.6 + i * 3.1, 1.7, 2.9, g, r, { size: 30 }));
  tarjeta(s, 0.6, 4.1, 12.15, 2.7, "Qué rompe el escenario, y qué vigilamos", [
    "Brent arriba de USD 110: acciones y bonos caen juntos, como en 2022",
    "La IA decepciona: corrige un mercado de EE.UU. concentrado en tecnología",
    "Déficit de EE.UU.: Tesoro a 10 años arriba de 5,5%",
    "A favor: el petróleo baja antes, la inflación cede y los bonos suben"], { size: 15 });
}

{
  const s = lamina("research", "Qué esperamos que rinda cada parte de tu cartera",
    "Retornos de largo plazo por clase, en dólares nominales, en el rango de las grandes gestoras.");
  const lp = Object.fromEntries(K.clases.map((c) => [c.clase, c.lp]));
  tabla(s, [["Clase", "Nosotros", "J.P. Morgan", "Vanguard", "BlackRock"],
    ["Liquidez", lp["Liquidez"], "n/d", "3,7%", "3,7%"], ["Tesoro 7-10 años", lp["Tesoro"], "4,6%", "4,8%", "4,8%"],
    ["Bonos ajustados por inflación", lp["Bonos ajustados por inflación"], "n/d", "4,4%", "5,2%"],
    ["Corporativos", lp["Corporativos"], "6,1%", "5,5%", "5,4%"],
    ["Acciones de EE.UU.", lp["Acciones EE.UU."], "7,5%", "5,8%", "9,0%"],
    ["Acciones de Europa (en USD)", lp["Acciones Europa"], "~7,5%", "6,3%", "7,4%"]],
  0.6, 1.75, 12.15, [4.15, 2, 2, 2, 2], { size: 16, rowH: 0.55, destacar: (i, j) => j === 1 });
  texto(s, "Retornos compuestos anuales en USD a 10-15 años. J.P. Morgan LTCMA 2027; Vanguard VCMM (30/09/2026); BlackRock CMA (agosto de 2026).",
    0.6, 5.85, 12.15, 0.4, { fontSize: 12, color: APAGADO });
  texto(s, "Armado en bloques: rendimientos - dividendos - ganancias - precio",
    0.6, 6.3, 12.15, 0.45, { fontSize: 15, bold: true, color: NAVY });
}

{
  const s = lamina("research", "Dónde ponemos tu plata y por qué",
    "Sectores favorecidos y penalizados por el escenario; energía y defensa quedan fuera por tus valores.");
  tarjeta(s, 0.6, 1.7, 3.9, 4.25, "Favorecemos", ["Salud: demanda que no depende del ciclo", "Tecnología con ganancias reales de IA",
    "Pagos: cobran sobre el gasto nominal", "Industria: electrificación e información"], { size: 15 });
  tarjeta(s, 4.73, 1.7, 3.9, 4.25, "Neutral", ["Comunicaciones: publicidad con IA, pero mucha inversión y regulación"], { size: 15 });
  tarjeta(s, 8.85, 1.7, 3.9, 4.25, "Penalizamos", ["Consumo discrecional: el petróleo come ingreso real",
    "Consumo básico: costos en alza, volumen estancado", "Servicios públicos: los más sensibles a la tasa"],
  { color: NARANJA, size: 15 });
}

{
  const s = lamina("research", "Solo empresas que cumplen tus valores",
    "El embudo: de los candidatos líquidos al filtro ESG, al screening y a la cartera.");
  const em = C.embudo;
  [[em.candidatos, "candidatos líquidos de EE.UU. y Europa"], [em.excluidos, "afuera por tus valores (filtro ESG)"],
    [em.universo, `cumplen (${em.acciones} acciones y ${em.fondos} fondos)`], [em.en_optimizacion, "elegidos por screening y tesis"],
    [em.en_cartera, "en tu cartera"]].forEach(([n, t], i) => {
    const w = 12.15 - i * 1.6, x = 0.6 + i * 0.8, y = 1.75 + i * 0.98;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.82, fill: { color: i === 1 ? ROSADO : i === 4 ? NAVY : CLARO },
      line: { color: BLANCO }, rectRadius: 0.08 });
    texto(s, String(n), x + 0.3, y + 0.1, 1.2, 0.62, { fontFace: TIT, fontSize: 28, bold: true,
      color: i === 4 ? BLANCO : i === 1 ? NARANJA : NAVY, valign: "middle" });
    texto(s, t, x + 1.6, y + 0.1, w - 1.9, 0.62, { fontSize: 17, color: i === 4 ? BLANCO : TINTA, valign: "middle" });
  });
}

{
  const s = lamina("research", "Siete empresas, una tesis cada una",
    "Las siete acciones con su tesis; Mastercard repite la de Visa y Procter queda en lista de espera.");
  tabla(s, [["Empresa", "Sector", "Por qué está en tu cartera", "Peso"],
    ["NVIDIA", "Tecnología", "Cobra la inversión en IA: crece rápido y cotiza barata para lo que crece", peso.NVDA.peso],
    ["Eli Lilly", "Salud", "Líder en tratamientos para obesidad y diabetes", peso.LLY.peso],
    ["Visa", "Pagos", "Un peaje sobre el gasto en dólares, sin riesgo de crédito", peso.V.peso],
    ["Eaton", "Industria", "La IA desde la electricidad: equipos para centros de datos y redes", peso.ETN.peso],
    ["Novartis", "Salud", "Farma global, barata y la menos volátil del sector", peso.NVS.peso],
    ["ASML", "Tecnología", "Único fabricante de las máquinas para los chips de vanguardia", peso.ASML.peso],
    ["RELX", "Industria", "Información por suscripción; la mejor de su sector en el screening", peso.RELX.peso]],
  0.6, 1.7, 12.15, [1.8, 1.7, 7.45, 1.2], { size: 15, rowH: 0.52, izq: [2] });
}

{
  const s = lamina("research", "Nuestras opiniones, con su grado de confianza",
    "Las siete views relativas con intensidad y confianza; Black-Litterman las combina con el equilibrio del mercado.");
  tabla(s, [["", "Opinión", "Intensidad", "Confianza"],
    ["1", "NVIDIA le gana al mercado de EE.UU.", "Muy alcista", "Menor"],
    ["2", "Europa (ASML, Novartis, RELX) le gana a EE.UU.", "Alcista", "Normal"],
    ["3", "Salud (Lilly y Novartis) le gana al mercado", "Alcista", "Normal"],
    ["4", "Pagos (Visa y Mastercard) le ganan al mercado", "Alcista", "Normal"],
    ["5", "Eaton le gana al mercado", "Alcista", "Normal"],
    ["6", "Bonos ajustados por inflación le ganan al Tesoro", "Alcista", "Menor"],
    ["7", "Corporativos no compensan su riesgo frente al Tesoro", "Bajista", "Normal"]],
  0.6, 1.7, 12.15, [0.6, 7.55, 2.0, 2.0], { size: 15, rowH: 0.5, izq: [1] });
  tecnico(s, 0.6, 5.95, 12.15, "Black-Litterman (Meucci, 2010)",
    "parte de lo que el mercado ya espera y lo corrige con cada opinión según su confianza; ninguna opinión manda sola.");
}

// --------------------------------------------------------------------- 14-18: Maxi (gestor)

{
  const s = lamina("gestor", "La vara contra la que te rendimos cuentas",
    "Maxi. El benchmark 50/50 de seis índices: su historia desde 2007 y su riesgo esperado.");
  grafico(s, "j_historia.png", 0.4, 1.55, 9.0, 5.3, "Valor de USD 100 en los índices del benchmark desde 2007");
  dato(s, 9.8, 1.7, 3.0, `USD ${B.valor_100_txt}`, "valen hoy USD 100 invertidos en 2007", { size: 30 });
  dato(s, 9.8, 3.3, 3.0, B.retorno_anual_txt, "por año, en dólares", { size: 30 });
  dato(s, 9.8, 4.9, 3.0, B.desvio_anual_txt, "de volatilidad histórica (2007-2026)", { size: 30 });
}

{
  const s = lamina("gestor", "Cómo convertimos nuestras opiniones en tu cartera",
    "Cuatro pasos: equilibrio, opiniones, retornos corregidos y optimización con las reglas; Ledoit-Wolf para medir el riesgo.");
  [["1. Lo que espera el mercado", "Los retornos que hacen óptimo al 50/50"],
    ["2. Nuestras opiniones", "Siete views, cada una con su confianza"],
    ["3. Retornos corregidos", "El mercado ajustado por las opiniones, después de impuestos"],
    ["4. Tu cartera", "Máximo retorno con volatilidad de 9% y las reglas de tu política"]].forEach(([t, d], i) => {
    const x = 0.6 + i * 3.1;
    caja(s, x, 1.75, 2.8, 2.45, i === 3 ? NAVY : CLARO);
    texto(s, t, x + 0.22, 1.95, 2.4, 0.75, { fontSize: 17, bold: true, color: i === 3 ? BLANCO : NAVY });
    texto(s, d, x + 0.22, 2.75, 2.4, 1.3, { fontSize: 14, color: i === 3 ? BLANCO : TINTA });
    if (i < 3) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.83, y: 2.8, w: 0.24, h: 0.3,
      fill: { color: APAGADO }, line: { color: APAGADO } });
  });
  dato(s, 0.6, 4.45, 7, `${K.comparacion["BL c=1 (final)"].neto_completo} contra ${K.comparacion["Equilibrio (c→0)"].neto_completo}`,
    "retorno esperado con todo descontado (impuestos y costos de los fondos): tu cartera contra la armada sin nuestras opiniones, con el mismo riesgo", { size: 32 });
  tecnico(s, 0.6, 6.15, 12.15, "Ledoit y Wolf (2004)",
    "mide cómo se mueven juntos tus activos con 10 años de datos diarios, sin dejarse engañar por el ruido de la muestra.");
}

{
  const s = lamina("gestor", `Tu cartera: ${K.posiciones} posiciones`,
    "Las doce posiciones en USD con su aporte al riesgo: NVIDIA es la apuesta más grande medida en riesgo, no en peso.");
  const orden = ["BIL", "IEF", "SCHP", "VCEB", "ESGV", "NVDA", "LLY", "V", "ETN", "ASML", "NVS", "RELX"];
  const nombre = { BIL: "Letras del Tesoro (BIL)", IEF: "Tesoro 7-10 años (IEF)", SCHP: "Bonos ajustados por inflación (SCHP)",
    VCEB: "Corporativos ESG (VCEB)", ESGV: "Acciones de EE.UU. ESG (ESGV)", NVDA: "NVIDIA", LLY: "Eli Lilly", V: "Visa",
    ETN: "Eaton", ASML: "ASML", NVS: "Novartis", RELX: "RELX" };
  const filas = orden.filter((t) => peso[t]);
  tabla(s, [["Posición", "Peso", "USD", "% del riesgo"],
    ...filas.map((t) => [nombre[t], peso[t].peso, peso[t].usd_a, riesgo[t] ? riesgo[t].pct_riesgo : "0,0%"])],
  0.6, 1.6, 7.9, [3.7, 1.2, 1.6, 1.4], { size: 13, rowH: 0.385,
    destacar: (i, j) => filas[i - 1] === "NVDA" && j === 3 });
  dato(s, 8.95, 1.6, 3.8, `${K.bruto} · ${K.neto_completo}`, "retorno esperado en dólares: bruto, y después de impuestos y costos de los fondos", { size: 28 });
  dato(s, 8.95, 3.25, 3.8, `${riesgo.NVDA.pct_riesgo} del riesgo`, `con ${peso.NVDA.peso} de tu plata: NVIDIA es nuestra apuesta más fuerte`,
    { size: 28, color: AZUL });
  dato(s, 8.95, 4.9, 3.8, `${R.europa_en_acciones} en Europa`, `de tus acciones, contra ${R.europa_en_acciones_benchmark} del benchmark`,
    { size: 28 });
}

{
  const s = lamina("gestor", "Menos riesgo que el mercado y fiel a tus valores",
    `Tu cartera contra el 50/50 con la misma vara: en la peor crisis perdés menos; resignás ${MV.menos_neto_pp} puntos por el filtro ESG y menos acciones.`);
  const c08 = MV.caidas_2008.maxima_caida_rebalanceo;
  const fila = (y, titulo, tuyo, mercado, nota, color) => {
    caja(s, 0.6, y, 12.15, 1.45);
    texto(s, titulo, 0.85, y + 0.15, 3.6, 1.15, { fontSize: 17, bold: true, color: NAVY, valign: "middle" });
    texto(s, tuyo, 4.5, y + 0.12, 2.3, 0.75, { fontFace: TIT, fontSize: 30, bold: true, color: color || AZUL, align: "center", valign: "bottom" });
    texto(s, "tu cartera", 4.5, y + 0.9, 2.3, 0.4, { fontSize: 13, color: GRIS, align: "center" });
    texto(s, mercado, 6.9, y + 0.12, 2.3, 0.75, { fontFace: TIT, fontSize: 30, bold: true, color: GRIS, align: "center", valign: "bottom" });
    texto(s, "el 50/50", 6.9, y + 0.9, 2.3, 0.4, { fontSize: 13, color: GRIS, align: "center" });
    texto(s, nota, 9.4, y + 0.15, 3.15, 1.15, { fontSize: 14, valign: "middle" });
  };
  fila(1.6, "Cuánto perdés en la peor crisis de los últimos 20 años", c08.cartera, c08.benchmark,
    `Perdés USD ${miles(Math.round(num(c08.diferencia_usd) / 1000) * 1000)} menos que con el 50/50`);
  fila(3.2, "Volatilidad esperada", MV.cartera.vol, MV.benchmark_indices.vol, "Menos sustos en el camino");
  fila(4.8, "Retorno esperado sin contar nuestras opiniones, después de impuestos", MV.cartera.neto, MV.benchmark_indices.neto,
    `${MV.menos_neto_pp} puntos: el precio de tu filtro ESG y de tener menos acciones`, NAVY);
  texto(s, "Crisis: caída de pico a valle entre octubre de 2007 y marzo de 2009, con el rebalanceo de tu política; nominal, antes de impuestos. " +
    "Volatilidad y retorno: misma vara para los dos (10 años de datos diarios, retornos de largo plazo, mismos impuestos y costos).",
    0.6, 6.35, 12.15, 0.55, { fontSize: 11, color: APAGADO });
}

{
  const s = lamina("gestor", "Cómo cuidamos tu cartera",
    `Qué miramos, cada cuánto y qué hacemos; el ejemplo de ${mesAnio(ej.fecha)}. Rebalancear es disciplina de riesgo: no siempre gana (en 2017 vender acciones salió peor).`);
  tabla(s, [["Qué miramos", "Cada cuánto", "Cuándo actuamos", "Qué hacemos"],
    ["Peso de cada clase", "Mensual", "Más de 3 puntos del objetivo", "Volvemos al objetivo"],
    ["Rangos de la política", "Mensual", `${MON.tolerancia_rango_pp} puntos fuera del rango`, "Corregimos en 5 días hábiles"],
    ["Cada acción", "Mensual", `Por encima de ${MON.tope_accion_disparo}`, "Recortamos a su peso"],
    ["Tus retiros", "Mensual", "Siempre", "Salen de la liquidez; se repone con lo que sobra"],
    ["El mercado", "Diario", "Cae más de 10%", "Te llamamos antes del informe"]],
  0.6, 1.6, 7.6, [2.2, 1.3, 2.1, 2.0], { size: 12, rowH: 0.5, izq: [3] });
  tarjeta(s, 8.45, 1.6, 4.3, 3.0, `${mayus(mesAnio(ej.fecha))}: el mercado cayó`, [
    `Tus acciones de EE.UU. bajaron a ${ej.pesos_clase["acciones de EE.UU."]} (objetivo ${K.clases.find((c) => c.clase === "Acciones EE.UU.").peso})`,
    `Vendimos USD ${miles(Math.round(num(ej.vende_total_usd) / 1000) * 1000)} de bonos y otras posiciones y compramos acciones`,
    `12 meses después, lo comprado rindió ${ej.compra_12m}; lo vendido, ${ej.vende_12m}`], { size: 14 });
  dato(s, 0.6, 4.75, 3.6, String(MON.rebalanceos), `rebalanceos en ${MON.anios} años con estas reglas (2016-2026)`, { size: 32 });
  dato(s, 4.4, 4.75, 3.8, MON.rotacion_anual, "de la cartera se mueve por año: pocos costos e impuestos", { size: 32 });
  texto(s, "Ilustrativo, con los datos diarios de tus activos desde 2016; no es una promesa de rendimiento.",
    8.45, 4.85, 4.3, 0.8, { fontSize: 12, color: APAGADO });
}

// --------------------------------------------------------------------- 19-24: Pedro (riesgos)

{
  const s = lamina("riesgo", "¿Y si no invertís?",
    `Pedro. Mismo plan y mismos impuestos: con la plata quieta se acaba a los ${ALT.a_quieta.edad_central}; en letras, a los ${ALT.b_letras.edad_central}; invertida, te dura.`);
  grafico(s, "k_invertir_vs_no.png", 0.4, 1.55, 8.9, 5.3, "Patrimonio mediano por edad: plata quieta, letras del Tesoro y la cartera");
  dato(s, 9.65, 1.6, 3.1, ALT.a_quieta.ruina, `de quedarte sin plata con la plata quieta (se acaba a los ${ALT.a_quieta.edad_central})`,
    { size: 30, color: GRIS, h: 0.8 });
  dato(s, 9.65, 3.3, 3.1, ALT.b_letras.ruina, `todo en letras del Tesoro (se acaba a los ${ALT.b_letras.edad_central})`,
    { size: 30, color: GRIS, h: 0.8 });
  dato(s, 9.65, 5.0, 3.1, ALT.d_cartera.ruina, `invertida en tu cartera; a los 90 te quedan USD ${ALT.d_cartera.patrimonio_90_real} M de hoy`,
    { size: 30, color: AZUL, h: 0.8 });
}

{
  const s = lamina("riesgo", "10.000 vidas posibles para tu plata",
    "Monte Carlo: 10.000 escenarios con impuestos, costos y una tabla de mortalidad; tu sueldo sube con la inflación todos los años.");
  grafico(s, "f_abanico.png", 0.6, 1.5, 12.15, 4.65, "Patrimonio de la cartera por edad en cuatro casos");
  tecnico(s, 0.6, 6.25, 12.15, "Monte Carlo",
    "simulamos 10.000 vidas posibles de mercado y de edad; los montos están en dólares de hoy porque tu sueldo sube con la inflación cada año.");
}

{
  const s = lamina("riesgo", "Tu ingreso: un sueldo que no se toca y un bono",
    "Sueldo fijo más bono con barandas de Guyton y Klinger; ejemplo de recortes hasta el piso, en dólares de hoy.");
  const alto = 4.4, base = 6.5, hF = (fijo / lujo) * alto;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: base - hF, w: 2.3, h: hF, fill: { color: NAVY }, line: { color: BLANCO, width: 2 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: base - alto, w: 2.3, h: alto - hF, fill: { color: AZUL }, line: { color: BLANCO, width: 2 } });
  texto(s, `Sueldo fijo\nUSD ${E["A base"].gasto}`, 0.8, base - hF / 2 - 0.4, 2.3, 0.8, { fontSize: 16, bold: true, color: BLANCO, align: "center", valign: "middle" });
  texto(s, `Bono\nUSD ${miles(bono)}`, 0.8, base - alto + (alto - hF) / 2 - 0.4, 2.3, 0.8, { fontSize: 16, bold: true, color: BLANCO, align: "center", valign: "middle" });
  [["Si la cartera va bien", "el bono sube 10%"], ["Si la cartera va mal", "el bono baja 10%"],
    ["Pase lo que pase", "el sueldo fijo no se toca y sube con la inflación"]].forEach(([a, b], i) => {
    texto(s, a, 3.6, 1.8 + i * 0.85, 4.0, 0.38, { fontSize: 16, bold: true, color: NAVY });
    texto(s, b, 3.6, 2.17 + i * 0.85, 9.0, 0.4, { fontSize: 15 });
  });
  const pasos = [lujo];
  while (pasos[pasos.length - 1] > fijo) pasos.push(Math.max(pasos[pasos.length - 1] * 0.9, fijo));
  caja(s, 3.6, 4.45, 9.15, 1.3);
  texto(s, "Si vienen años malos seguidos (USD por mes, en dólares de hoy)", 3.85, 4.55, 8.7, 0.4, { fontSize: 14, bold: true, color: NAVY });
  texto(s, pasos.map(miles).join("  →  ") + "  (piso)", 3.85, 4.98, 8.7, 0.6, { fontFace: TIT, fontSize: 20, bold: true, color: AZUL });
  texto(s, `Hacen falta ${pasos.length - 1} recortes para perder el bono entero; cuando la cartera se recupera, vuelve a subir de a 10%.`,
    3.6, 5.85, 9.15, 0.45, { fontSize: 14 });
  tecnico(s, 3.6, 6.3, 9.15, "Barandas de Guyton y Klinger (2006)", "recortan o suben el retiro cuando su peso sobre la cartera se aleja 20%.");
}

{
  const s = lamina("riesgo", "Podés vivir con nivel de lujo si una parte es variable",
    "Probabilidad de quedarte sin plata en vida: con sueldo fijo más bono, el nivel lujo entra en el criterio de 5%.");
  const f = (k) => [E[k].ruina_fijo, E[k].ruina_bono];
  tabla(s, [["Nivel de vida", "Si comprás: gasto fijo", "Si comprás: sueldo + bono", "Si alquilás: gasto fijo", "Si alquilás: sueldo + bono"],
    ["Base", ...f("A base"), ...f("B base")], ["Lujo", ...f("A lujo"), ...f("B lujo")], ["Alto", ...f("A alto"), ...f("B alto")]],
  0.6, 1.8, 12.15, [2.15, 2.5, 2.5, 2.5, 2.5], { size: 17, rowH: 0.7, destacar: (i, j) => i === 2 && j === 2 });
  texto(s, "Probabilidad de quedarte sin plata en vida, en 10.000 escenarios. Criterio de la política: 5% o menos.",
    0.6, 4.75, 12.15, 0.4, { fontSize: 13, color: APAGADO });
  dato(s, 0.6, 5.0, 6, `${lujoA.llegan_bono} de cada 100`, "escenarios te alcanza la plata toda la vida con nivel lujo, comprando", { size: 32, color: AZUL });
  dato(s, 6.85, 5.0, 5.9, lujoA.bono_desaparece, "de los escenarios el bono desaparece en algún momento: vivís un tiempo con el sueldo fijo", { size: 32, color: NARANJA });
}

{
  const s = lamina("riesgo", "Qué puede salir mal y cómo lo cubrimos",
    "Prueba de estrés con 2008 de entrada y sensibilidad a cambios de impuestos; el caso base sigue la ley vigente.");
  tarjeta(s, 0.6, 1.7, 5.9, 5.1, "Si arrancás con un 2008", []);
  dato(s, 0.85, 2.35, 5.4, `${lujoA.llegan_estres_bono} de cada 100`, "escenarios llegan comprando, aun con un 2008 el primer año", { size: 32, color: AZUL });
  dato(s, 0.85, 4.0, 5.4, `${lujoB.llegan_estres_bono} de cada 100`, "alquilando: comprar sigue ganando", { size: 32 });
  texto(s, "El primer año repite 2008 y el bono absorbe el golpe; después el mercado vuelve a lo normal.", 0.85, 5.75, 5.4, 0.9, { fontSize: 14 });
  const I = C.impuestos;
  caja(s, 6.85, 1.7, 5.9, 5.1);
  texto(s, "Si cambian los impuestos (nivel lujo, comprando)", 7.1, 1.88, 5.4, 0.45, { fontSize: 17, bold: true, color: NAVY });
  tabla(s, [["Escenario", "Sin plata en vida"], ["Ley vigente", I.base.ruina_bono], ["Bienes Personales no baja a 0,25%", I.bp_fijo.ruina_bono],
    ["Renta 40% y ganancias 20%", I.alicuotas_altas.ruina_bono], ["Las dos cosas", I.ambos.ruina_bono]],
  7.1, 2.45, 5.4, [3.7, 1.7], { size: 14, rowH: 0.42 });
  texto(s, "El riesgo principal es que un gobierno revierta la baja de Bienes Personales. Nuestro contador lo sigue y, si pasa, ajustamos el bono.",
    7.1, 4.75, 5.4, 1.2, { fontSize: 14 });
}

{
  const s = lamina("riesgo", "Comprar gana en todas las comparaciones",
    "Retiro máximo seguro, el que alcanza en 95 de cada 100 escenarios: comprar deja más margen y un bono inicial más alto.");
  const col = (x, t, k, base, a) => {
    tarjeta(s, x, 1.7, 5.9, 5.1, t, []);
    dato(s, x + 0.3, 2.3, 5.3, `+USD ${miles(num(S[k].fijo) - num(base))}`, `por mes de margen sobre tu gasto base (USD ${base}) con gasto fijo`, { size: 32 });
    dato(s, x + 0.3, 3.95, 5.3, `USD ${S[k].bono}`, "por mes podés arrancar con sueldo fijo más bono", { size: 32, color: AZUL });
    texto(s, `Nivel lujo con bono: ${a.llegan_bono} de cada 100 escenarios te alcanza (${a.llegan_estres_bono} con un 2008)`,
      x + 0.3, 5.7, 5.3, 0.8, { fontSize: 14, color: GRIS });
  };
  col(0.6, "Si comprás", "A: compra", E["A base"].gasto, lujoA);
  col(6.85, "Si alquilás", "B: alquila", E["B base"].gasto, lujoB);
}

// --------------------------------------------------------------------- 25-26: Agustín cierra

{
  const s = oscura("Nuestra recomendación: comprá el depto y cobrá un sueldo fijo más un bono",
    `Agustín cierra arrancando por lo que gana: nivel lujo, sueldo que no se toca y la plata que alcanza en ${lujoA.llegan_bono} de cada 100 escenarios. La decisión es de ella.`);
  [[`USD ${E["A base"].gasto}`, "sueldo fijo por mes, que sube con la inflación"], [`USD ${miles(bono)}`, "bono inicial por mes: nivel lujo completo"],
    [`${lujoA.llegan_bono} de cada 100`, "escenarios te alcanza la plata toda la vida"]].forEach(([g, r], i) => {
    texto(s, g, 0.8 + i * 4.1, 3.4, 3.8, 0.9, { fontFace: TIT, fontSize: 38, bold: true, color: BLANCO, valign: "bottom" });
    texto(s, r, 0.8 + i * 4.1, 4.35, 3.8, 0.8, { fontSize: 16, color: SUAVE });
  });
  texto(s, `Tu casa rinde ${N.depto} por año, tu cartera tiene menos riesgo que el mercado y te cuesta ${CC.total_pct} por año, todo incluido.`,
    0.8, 5.6, 11.7, 0.6, { fontSize: 17, color: BLANCO });
  texto(s, "La decisión es tuya.", 0.8, 6.3, 11.7, 0.5, { fontFace: TIT, fontSize: 22, bold: true, italic: true, color: BLANCO });
}

{
  const s = lamina("asesor", "Próximos pasos y nuestro compromiso",
    "Los cuatro pasos para arrancar y los compromisos de servicio; después, preguntas.");
  [["1", "Firmar tu política", "Rangos, reglas y el esquema de sueldo y bono"],
    ["2", "Abrir tu cuenta", "En un bróker regulado de EE.UU., a tu nombre"],
    ["3", "Comprar e invertir", `Depto de USD 1 M; USD ${C.capital.A} según tu cartera`],
    ["4", "Primera reunión", "Informe por baldes y el primer tema para aprender"]].forEach(([n, t, d], i) => {
    const x = 0.6 + i * 3.1;
    s.addShape(pres.shapes.OVAL, { x, y: 1.75, w: 0.75, h: 0.75, fill: { color: NAVY }, line: { color: NAVY } });
    texto(s, n, x, 1.75, 0.75, 0.75, { fontFace: TIT, fontSize: 22, bold: true, color: BLANCO, align: "center", valign: "middle" });
    texto(s, t, x, 2.65, 2.85, 0.45, { fontSize: 18, bold: true, color: NAVY });
    texto(s, d, x, 3.15, 2.85, 1.0, { fontSize: 14 });
  });
  tarjeta(s, 0.6, 4.4, 12.15, 1.75, "Nuestro compromiso", [
    "Te vemos todos los meses y te llamamos si el mercado cae más de 10%",
    "Tu sueldo llega todos los meses, pase lo que pase en el mercado",
    "Te avisamos antes de cualquier cambio de impuestos y ajustamos el plan con el contador"], { size: 15 });
}

// --------------------------------------------------------------------- Anexo (no se presenta)

oscura("Anexo", "Láminas para las preguntas; no se presentan.");

{
  const s = lamina("anexo", "A1. Sensibilidades del modelo de cartera",
    "Confianza, volatilidad objetivo y cuánto mueve cada view (leave-one-out).");
  grafico(s, "d_sensibilidad.png", 0.4, 1.5, 6.6, 5.2, "Pesos por clase según la confianza y la volatilidad objetivo");
  grafico(s, "e_views.png", 7.1, 1.5, 5.8, 5.2, "Rotación de la cartera al sacar cada view");
}

{
  const s = lamina("anexo", "A2. Qué restricción manda en cada clase",
    "La volatilidad está al máximo; liquidez y TIPS en el máximo; corporativos y Europa en el mínimo; ESGV en su piso.");
  grafico(s, "a_clases.png", 0.4, 1.5, 8.4, 5.3, "Cartera contra benchmark por clase, con los rangos de la política");
  tarjeta(s, 9.15, 1.7, 3.6, 5.0, "Restricciones activas", [
    "Volatilidad de 9%, al máximo", "Liquidez y bonos ajustados por inflación, en el máximo",
    "Corporativos y Europa, en el mínimo", "ESGV, en su piso de 20%", "Lilly y Novartis, en el tope de 5%"], { size: 14 });
}

{
  const s = lamina("anexo", "A3. De dónde sale cada número",
    "Tabla cifra → fuente para las preguntas.");
  tabla(s, [["Cifra", "Fuente"],
    ["Escenario (Brent, IPC, Fed, Tesoro)", "FMI WEO oct-2026; FRED (DGS10, DFII10, T10YIE, T5YIFR); Fed; BLS"],
    ["Retornos de largo plazo por clase", "Bloques: rendimiento inicial, dividendo, crecimiento, valuación; contra J.P. Morgan, Vanguard y BlackRock"],
    ["Precios y covarianzas", "Yahoo Finance, 10 años diarios; Ledoit y Wolf (2004)"],
    ["Notas ESG", "S&P Global ESG Score (consulta pública, noviembre de 2026)"],
    ["Impuestos", "Ley 27.743 (Bienes Personales); Ley de Ganancias; retención de EE.UU. 30% sin tratado"],
    ["Mortalidad", "Gompertz (m = 93, b = 9), como Milevsky y Robinson (2005): esperanza de vida 88 años"],
    ["Comisión y costos de fondos", "Tramos de la política; expense ratios de SSGA, iShares, Schwab y Vanguard"],
    ["Alquiler y presupuesto", "Avisos de Zonaprop 2026 (Puerto Madero y Libertador); estimación propia por rubro"]],
  0.6, 1.6, 12.15, [3.8, 8.35], { size: 13, rowH: 0.56, izq: [1] });
}

{
  const s = lamina("anexo", "A4. Supuestos impositivos y su fuente",
    "Las alícuotas vigentes, todas verificadas, con su fuente.");
  tabla(s, [["Impuesto", "Supuesto", "Fuente", "Estado"],
    ["Dividendos de EE.UU.", "35%, marginal máxima (EE.UU. retiene 30%)", "LIG art. 94 (t.o. 2019); Errepar", "Vigente"],
    ["Intereses (incluye el ajuste de los TIPS)", "35%, alícuota marginal máxima", "LIG art. 94 (t.o. 2019); Errepar", "Vigente"],
    ["Ganancia por venta de acciones del exterior", "15% sobre la ganancia realizada (tasa efectiva por rotación)", "LIG art. 94, 2.º párrafo; Errepar", "Vigente"],
    ["Bienes Personales", "0,75% en 2026; 0,25% desde 2027 (alícuota máxima)", "Ley 27.743; Deloitte; O'Farrell", "Vigente"],
    ["Mínimo exento del depto", "Exento hasta ARS 350 M; gravamos todo el depto", "Ley 27.743; Deloitte; O'Farrell", "Vigente"],
  ],
  0.6, 1.6, 12.15, [3.3, 4.2, 2.6, 2.05], { size: 13, rowH: 0.62, izq: [1, 2] });
  texto(s, "Un contador matriculado revisa cada supuesto antes de implementar y en cada cambio de ley.",
    0.6, 6.2, 12.15, 0.45, { fontSize: 14, color: GRIS });
}

{
  const s = lamina("anexo", "A5. Otras formas de armar la cartera",
    "Equilibrio sin views, paridad de riesgo jerárquica y mínima varianza con las mismas reglas.");
  grafico(s, "c_frontera.png", 0.6, 1.5, 12.15, 5.3, "Cinco carteras en el plano volatilidad y retorno neto");
}

{
  const s = lamina("anexo", "A6. Sensibilidades del retiro",
    "Ruina con gasto fijo y retiro seguro según retornos ±1 punto y volatilidad 7% / 11%.");
  const nombres = { "base (vol 9%)": "Base (vol 9%)", "retornos +1 pp": "Retornos +1 punto", "retornos −1 pp": "Retornos −1 punto",
    "vol 7%": "Volatilidad 7%", "vol 11%": "Volatilidad 11%" };
  tabla(s, [["Caso", "Retorno neto sin opiniones", "Lujo, compra", "Lujo, alquila", "Retiro seguro, compra", "Retiro seguro, alquila"],
    ...Object.entries(C.sensibilidades).map(([k, v]) => [nombres[k] || k, v.ret_nominal, v["A lujo"], v["B lujo"],
      v["seguro A: compra"], v["seguro B: alquila"]])],
  0.6, 1.7, 12.15, [2.4, 2.0, 1.75, 1.75, 2.15, 2.1], { size: 14, rowH: 0.55 });
  texto(s, "Probabilidad de quedarse sin plata con gasto fijo (sin barandas) y retiro máximo seguro en USD por mes.",
    0.6, 5.25, 12.15, 0.4, { fontSize: 13, color: APAGADO });
}

{
  const s = lamina("anexo", "A7. ¿Y un 50/50 pasivo, sin asesor?",
    "La respuesta honesta: cuánto es asignación y cuánto comisión, con y sin views, y por qué igual te conviene la cartera.");
  tabla(s, [["Nivel lujo, comprando, con bono", "Sin plata en vida", "A los 90 (USD M de hoy)", "Bono desaparece"],
    ["50/50 de seis índices, sin comisión", ALT.c_benchmark.ruina, ALT.c_benchmark.patrimonio_90_real, ALT.c_benchmark.bono_desaparece],
    ["50/50 de seis índices, con nuestra comisión", ALT.e_benchmark_comision.ruina, ALT.e_benchmark_comision.patrimonio_90_real, ALT.e_benchmark_comision.bono_desaparece],
    ["Tu cartera", ALT.d_cartera.ruina, ALT.d_cartera.patrimonio_90_real, ALT.d_cartera.bono_desaparece]],
  0.6, 1.55, 7.6, [3.7, 1.3, 1.4, 1.2], { size: 12, rowH: 0.48 });
  tabla(s, [["Retorno neto esperado", "Tu cartera", "50/50"],
    ["Sin views, 50/50 de seis índices", MV.cartera.neto, MV.benchmark_indices.neto],
    ["Con views, 50/50 con nuestros activos", MV.con_views.cartera, MV.con_views.benchmark],
    ["Sharpe (sin views)", MV.cartera.sharpe, MV.benchmark_indices.sharpe]],
  8.45, 1.55, 4.3, [2.3, 1.0, 1.0], { size: 12, rowH: 0.48 });
  const CR = MV.caidas_2008;
  tabla(s, [["Crisis 2007-2009", "Tu cartera", "50/50"],
    ["Año 2008, pesos fijos", CR.anio_2008_fijos.cartera, CR.anio_2008_fijos.benchmark],
    ["Año 2008, con rebalanceo", CR.anio_2008_rebalanceo.cartera, CR.anio_2008_rebalanceo.benchmark],
    ["Pico a valle, pesos fijos", CR.maxima_caida_fijos.cartera, CR.maxima_caida_fijos.benchmark],
    ["Pico a valle, con rebalanceo", CR.maxima_caida_rebalanceo.cartera, CR.maxima_caida_rebalanceo.benchmark]],
  8.45, 3.75, 4.3, [2.3, 1.0, 1.0], { size: 12, rowH: 0.48, destacar: (i) => i === 4 });
  texto(s, "Misma regla para las dos; nominal, antes de impuestos, sin retiros.", 8.45, 6.25, 4.3, 0.5, { fontSize: 11, color: APAGADO });
  tarjeta(s, 0.6, 3.75, 7.6, 3.05, "Por qué igual te conviene tu cartera", [
    "El 50/50 no cumple tu mandato: tiene tabaco, petroleras y defensa. Es la vara contra la que te medimos, no algo que puedas comprar.",
    "La simulación no le da ningún crédito a nuestras opiniones: usa los retornos de largo plazo por clase. Solo muestra la asignación (menos acciones, más renta fija que paga 35%) y la comisión. Es conservadora a propósito.",
    "Lo que pagás no es retorno: es el plan de sueldo y bono, la gestión impositiva, el rebalanceo y estar con vos en las caídas."],
  { size: 12 });
}

pres.writeFile({ fileName: SALIDA }).then((f) => console.log(f));
