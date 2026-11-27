# -*- coding: utf-8 -*-
"""
motor_expansion_ra2_27nov.py — CALENDARIO FDIC26 + EXPANSIÓN RA2 (27 NOV) CON REFUERZO PALABRAL Y TESTEO
Módulo plug-and-play para PROYECTOS-2026 (Evaluación Integrada de Proyectos — ULagos 2026).

Incluye sobre `HTML_SIMULADOR_FLUIDO`:
  1) Cronograma oficial interactivo FDIC26 (2026-2SEM) y etiquetas de fecha por clase.
  2) Zonas Concéntricas 100% MODIFICABLES en Costo de Viaje (edición en vivo de Tasa, CV e Ingreso,
     detección automática de la Paradoja de Ingreso y etiquetas SVG sin superposición).
  3) Refuerzo Pedagógico Palabral-Conceptual profundo en los 4 bloques (MCV, Hedónicos, MVC, Dixon/Barzev):
       - Narrativa conceptual extensa con conectores lógicos destacados (En primer lugar, Porque, Sin embargo,
         En otras palabras, A diferencia de, Por lo tanto).
       - Cuadros comparativos "No confundir X con Y" (Reveladas vs Declaradas, Uso vs No Uso, DAP vs DAA).
       - Guion Oral de Defensa / Certamen (30 segundos) con Modo Ciego para practicar en voz alta.
       - Mini-Test Conceptual Interactivo dentro de CADA bloque (12 preguntas con retroalimentación causal).
  4) Expansión de Modo Practicar (Retos 9, 10, 11 y 12) y del Control de Lectura (+6 preguntas RA2).
"""


CSS_EXPANSION_RA2_27NOV = r"""
<style id="css-expansion-ra2-27nov">
  /* === BARRA CRONOGRAMA OFICIAL FDIC26 === */
  .cal-bar {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-left: 4px solid #0F766E;
    border-radius: 8px;
    padding: 7px 12px;
    margin-bottom: 10px;
    font-size: 11.6px;
  }
  .cal-bar summary {
    cursor: pointer;
    font-weight: 800;
    color: #0F172A;
    list-style: none;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }
  .cal-bar summary::-webkit-details-marker { display: none; }
  .cal-badge-new {
    font-size: 10.2px;
    font-weight: 800;
    color: #FFFFFF;
    background: #059669;
    padding: 2px 8px;
    border-radius: 10px;
  }
  .cal-badge-warn {
    font-size: 10.2px;
    font-weight: 800;
    color: #9A3412;
    background: #FFEDD5;
    border: 1px solid #FDBA74;
    padding: 2px 8px;
    border-radius: 10px;
  }
  .cal-strip {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed #CBD5E1;
  }
  .cal-pill {
    border: 1px solid #CBD5E1;
    background: #F8FAFC;
    color: #1E293B;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.14s ease;
    display: inline-flex;
    align-items: center;
    gap: 5px;
  }
  .cal-pill:hover { border-color: #1D4ED8; background: #EFF6FF; color: #1D4ED8; }
  .cal-pill.cp-eval { border-color: #FDBA74; background: #FFFBEB; color: #9A3412; }
  .cal-pill.cp-new { border-color: #10B981; background: #ECFDF5; color: #065F46; }
  .cal-dt {
    font-family: Consolas, monospace;
    font-size: 10.2px;
    font-weight: 800;
    background: #E2E8F0;
    color: #0F172A;
    padding: 1px 5px;
    border-radius: 4px;
  }
  .cal-pill.cp-eval .cal-dt { background: #FDE68A; color: #78350F; }
  .cal-pill.cp-new .cal-dt { background: #059669; color: #FFFFFF; }

  /* === SUB-SECCIONES DEL MÓDULO 12 (CLASE 27 NOV) === */
  .ra2-sub { display: none; }
  .ra2-sub.active { display: block; }
  .ra2-dual {
    display: grid;
    grid-template-columns: 1.05fr 1.15fr;
    gap: 10px;
    margin: 8px 0;
  }
  @media (max-width: 860px) { .ra2-dual { grid-template-columns: 1fr; } }
  .ra2-card {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 7px;
    padding: 10px 12px;
    font-size: 11.8px;
    line-height: 1.46;
  }
  .ra2-card-tit {
    font-size: 12px;
    font-weight: 800;
    color: #1E3A8A;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
  }
  .ra2-highlight-row td {
    background: #FEF3C7 !important;
    font-weight: 800;
    color: #78350F !important;
  }
  .zn-in {
    width: 68px;
    padding: 3px 5px;
    border: 1.3px solid #94A3B8;
    border-radius: 4px;
    font-family: Consolas, monospace;
    font-size: 11.5px;
    font-weight: 800;
    color: #0F172A;
    background: #FFFFFF;
    text-align: right;
  }
  .zn-in:focus { outline: 2px solid #93C5FD; border-color: #1D4ED8; }
  .zn-diag {
    margin-top: 7px;
    padding: 7px 10px;
    border-radius: 6px;
    font-size: 11.5px;
    line-height: 1.44;
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid #D97706;
    color: #78350F;
  }
  .zn-diag.zn-ok {
    background: #ECFDF5;
    border-color: #A7F3D0;
    border-left-color: #059669;
    color: #065F46;
  }

  /* === TUTOR CONCEPTUAL PALABRAL + CONECTORES + GUION ORAL + MINI-TEST === */
  .tutor-box {
    margin: 10px 0;
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1.5px solid #BFDBFE;
    border-left: 5px solid #1E3A8A;
    border-radius: 8px;
    padding: 11px 14px;
  }
  .tutor-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
    padding-bottom: 7px;
    border-bottom: 1px dashed #CBD5E1;
  }
  .tutor-tit {
    font-size: 12.4px;
    font-weight: 800;
    color: #1E3A8A;
  }
  .tutor-prose {
    font-size: 12.2px;
    line-height: 1.58;
    color: #1E293B;
    margin-bottom: 9px;
  }
  .tutor-prose p { margin: 0 0 7px 0; }
  .tutor-prose p:last-child { margin-bottom: 0; }
  .conn-tag {
    display: inline-block;
    font-weight: 800;
    font-size: 11.1px;
    padding: 0.5px 6px;
    border-radius: 4px;
    margin-right: 3px;
    background: #DBEAFE;
    color: #1E40AF;
  }
  .conn-tag.ct-warn { background: #FEF3C7; color: #92400E; }
  .conn-tag.ct-ok   { background: #DCFCE7; color: #166534; }
  .conn-tag.ct-purp { background: #F3E8FF; color: #6B21A8; }
  .conn-tag.ct-red  { background: #FEE2E2; color: #991B1B; }

  .tutor-cols {
    display: grid;
    grid-template-columns: 1.1fr 1fr;
    gap: 10px;
    margin-top: 8px;
  }
  @media (max-width: 820px) { .tutor-cols { grid-template-columns: 1fr; } }

  .comp-card {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-top: 3px solid #7C3AED;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 11.5px;
    line-height: 1.44;
  }
  .comp-card-tit {
    font-size: 11.2px;
    font-weight: 800;
    color: #6B21A8;
    text-transform: uppercase;
    margin-bottom: 5px;
  }
  .comp-item {
    padding: 4px 0;
    border-bottom: 1px dashed #E2E8F0;
  }
  .comp-item:last-child { border-bottom: none; padding-bottom: 0; }

  .oral-card {
    background: #F0FDF4;
    border: 1px solid #86EFAC;
    border-top: 3px solid #15803D;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 11.6px;
    line-height: 1.48;
    color: #14532D;
  }
  .oral-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 6px;
    margin-bottom: 5px;
  }
  .oral-tit {
    font-size: 11.2px;
    font-weight: 800;
    color: #166534;
    text-transform: uppercase;
  }
  .oral-blur {
    filter: blur(5px);
    user-select: none;
    cursor: pointer;
    transition: filter 0.15s ease;
  }

  /* === MINI-TEST CONCEPTUAL DENTRO DE CADA BLOQUE === */
  .mt-box {
    margin: 10px 0;
    background: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-top: 3.5px solid #0F172A;
    border-radius: 8px;
    padding: 10px 13px;
  }
  .mt-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
  }
  .mt-tit { font-size: 12.2px; font-weight: 800; color: #0F172A; }
  .mt-qcard {
    border: 1px solid #CBD5E1;
    border-left: 4px solid #475569;
    border-radius: 6px;
    background: #F8FAFC;
    padding: 8px 11px;
    margin-bottom: 7px;
  }
  .mt-qcard.ok { border-left-color: #15803D; background: #F0FDF4; }
  .mt-qcard.bad { border-left-color: #DC2626; background: #FEF2F2; }
  .mt-qtxt { font-size: 12px; font-weight: 700; color: #0F172A; margin-bottom: 6px; line-height: 1.42; }
  .mt-opts { display: flex; gap: 6px; flex-wrap: wrap; }
  .mt-btn {
    border: 1px solid #94A3B8;
    background: #FFFFFF;
    color: #0F172A;
    padding: 4px 10px;
    border-radius: 5px;
    font-size: 11.4px;
    font-weight: 700;
    cursor: pointer;
    text-align: left;
  }
  .mt-btn:hover { background: #EFF6FF; border-color: #1D4ED8; color: #1D4ED8; }
  .mt-btn.sel { background: #0F172A; color: #FFFFFF; border-color: #0F172A; }
  .mt-fb {
    display: none;
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px dashed #CBD5E1;
    font-size: 11.6px;
    line-height: 1.46;
    color: #1E293B;
  }
  .mt-qcard.answered .mt-fb { display: block; }

  /* === SELECTOR DIXON & BARZEV === */
  .dix-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
    gap: 7px;
    margin: 8px 0;
  }
  .dix-btn {
    border: 1.5px solid #CBD5E1;
    background: #F8FAFC;
    color: #1E293B;
    padding: 8px 10px;
    border-radius: 7px;
    font-size: 11.6px;
    font-weight: 800;
    cursor: pointer;
    text-align: left;
    transition: all 0.14s ease;
  }
  .dix-btn:hover { border-color: #1D4ED8; background: #EFF6FF; color: #1E3A8A; }
  .dix-btn.active { background: #0F172A; color: #FFFFFF; border-color: #0F172A; }
  .dix-res {
    background: linear-gradient(135deg, #ECFDF5 0%, #F0F9FF 100%);
    border: 1px solid #6EE7B7;
    border-left: 4.5px solid #059669;
    border-radius: 7px;
    padding: 10px 13px;
    margin: 8px 0 10px 0;
    font-size: 12.1px;
    line-height: 1.5;
  }
  .mvc-steps {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 6px;
    margin: 8px 0;
  }
  @media (max-width: 820px) { .mvc-steps { grid-template-columns: 1fr 1fr; } }
  .mvc-st {
    background: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-top: 3px solid #1D4ED8;
    border-radius: 6px;
    padding: 7px 8px;
    font-size: 11.1px;
    line-height: 1.35;
  }
  .mvc-st b { color: #1E3A8A; display: block; margin-bottom: 2px; }
  .enc-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
    margin-top: 8px;
  }
  @media (max-width: 820px) { .enc-grid { grid-template-columns: 1fr; } }
  .enc-box {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-left: 3.5px solid #7C3AED;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 11.4px;
    line-height: 1.4;
  }

  /* Visibilidad inteligente en Modo Aprender: Tutor Palabral SIEMPRE accesible */
  .wrap.mode-aprender.step-1 #panel-ra2_27nov .ra2-dual,
  .wrap.mode-aprender.step-1 #panel-ra2_27nov .dix-wrap,
  .wrap.mode-aprender.step-1 #panel-ra2_27nov .mvc-info-wrap,
  .wrap.mode-aprender.step-1 #panel-ra2_27nov .tutor-box { display: block; }
  .wrap.mode-aprender.step-1 #panel-ra2_27nov .mt-box { display: block; }

  .wrap.mode-aprender.step-2 #panel-ra2_27nov .ra2-dual { display: none; }
  .wrap.mode-aprender.step-2 #panel-ra2_27nov .dix-wrap,
  .wrap.mode-aprender.step-2 #panel-ra2_27nov .tutor-box,
  .wrap.mode-aprender.step-2 #panel-ra2_27nov .mt-box { display: block; }

  .wrap.mode-aprender.step-3 #panel-ra2_27nov .ra2-dual,
  .wrap.mode-aprender.step-3 #panel-ra2_27nov .dix-wrap { display: none; }
  .wrap.mode-aprender.step-3 #panel-ra2_27nov .tutor-box,
  .wrap.mode-aprender.step-3 #panel-ra2_27nov .mt-box { display: block; }
</style>
"""


JS_EXPANSION_RA2_27NOV = r"""
<script id="js-expansion-ra2-27nov">
(function() {
  if (window.__expansionRa2_27NovActiva) return;
  window.__expansionRa2_27NovActiva = true;

  // ==========================================================================
  // 1. CRONOGRAMA OFICIAL FDIC26 (ULAGOS VIRTUAL 2026-2SEM)
  // ==========================================================================
  const CALENDARIO_FDIC26 = [
    { dt: "18 Ago", lbl: "Clase 1 · Flujos y Crédito", tipo: "cls", tab: "horno" },
    { dt: "14 Sep", lbl: "Venc. Descripción Proyecto (12:00)", tipo: "eval", tab: "arboles" },
    { dt: "23 Sep", lbl: "Prueba Proceso 2 · Árboles (16:07)", tipo: "eval", tab: "arboles" },
    { dt: "01 Oct", lbl: "[Defensa] Producto RA1 (16:08)", tipo: "eval", tab: "leche" },
    { dt: "05 Nov", lbl: "Entrega Informe Proyecto (19:00)", tipo: "eval", tab: "waterfall" },
    { dt: "11 Nov", lbl: "Defensa Informe (08:04)", tipo: "eval", tab: "waterfall" },
    { dt: "12 Nov", lbl: "Proceso 1 RA2 [DEFENSA] (16:37)", tipo: "eval", tab: "ambiental" },
    { dt: "16 Nov", lbl: "Clase · Transables y Salmón", tipo: "cls", tab: "clase" },
    { dt: "26 Nov", lbl: "Venc. Última Presentación (23:59)", tipo: "eval", tab: "waterfall" },
    { dt: "27 Nov", lbl: "HOY · RA2: MCV, Hedónicos, MVC y Dixon", tipo: "new", tab: "ra2_27nov" }
  ];

  function montarCalendarioBar() {
    const studioBar = document.querySelector(".studio-bar");
    if (!studioBar || document.getElementById("cal-fdic26-bar")) return;
    const det = document.createElement("details");
    det.id = "cal-fdic26-bar";
    det.className = "cal-bar";
    const pillsHtml = CALENDARIO_FDIC26.map(c => {
      const cls = c.tipo === "new" ? "cp-new" : (c.tipo === "eval" ? "cp-eval" : "");
      return `<button class="cal-pill ${cls}" onclick="jumpToTab('${c.tab}')"><span class="cal-dt">${c.dt}</span><span>${c.lbl}</span></button>`;
    }).join("");
    det.innerHTML = `
      <summary>
        <span>📅 Cronograma Oficial FDIC26 (2026-2SEM) y Fechas por Clase — Clic en cualquier hito para abrir su simulador</span>
        <span style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
          <span class="cal-badge-warn">Aviso Moodle: Venc. Presentación 26 Nov 23:59</span>
          <span class="cal-badge-new">Última clase: 27 Nov · RA2</span>
        </span>
      </summary>
      <div class="cal-strip">${pillsHtml}</div>
    `;
    studioBar.parentNode.insertBefore(det, studioBar.nextSibling);
  }

  // ==========================================================================
  // 2. DATOS DE MINI-TESTS CONCEPTUALES (12 PREGUNTAS EN 4 BLOQUES)
  // ==========================================================================
  const MT_BANK = {
    mcv: [
      {
        id: "mcv1",
        q: "1. ¿Por qué decimos que el Método de Costo de Viaje (MCV) utiliza 'mercados sustitutos' o 'preferencias reveladas'?",
        opts: [
          "Porque aunque la entrada al parque sea gratis ($0), las familias revelan cuánto lo valoran al gastar en traslado y tiempo",
          "Porque se les pregunta por teléfono en una encuesta hipotética cuánto pagarían por el parque",
          "Porque el parque vende entradas en la bolsa de comercio"
        ],
        ans: 0,
        why: "<b>Exacto:</b> en el MCV no inventamos un mercado hipotético (eso es MVC), sino que <b>observamos una conducta real</b>: viajar cuesta combustible, pasajes y tiempo, lo cual actúa como precio sustituto del disfrute recreativo."
      },
      {
        id: "mcv2",
        q: "2. En la tabla zonal de clase, Loc. 3 paga más costo de viaje (US$ 40) que Loc. 2 (US$ 30), pero visita MÁS el parque (80‰ vs. 70‰). ¿Qué demuestra esto?",
        opts: [
          "Que la ley de la demanda no se cumple en los parques nacionales",
          "Que la tasa de visitas no depende solo del costo de viaje, sino también del ingreso promedio (y educación/sustitutos), por lo que debe estimarse con regresión múltiple",
          "Que los habitantes de Loc. 3 cometen un error de cálculo"
        ],
        ans: 1,
        why: "<b>Clave de certamen:</b> Loc. 3 tiene un ingreso promedio mayor (US$ 1.300 vs. US$ 1.100). <b>Por lo tanto</b>, la función debe ser multivariable: <i>v<sub>i</sub> = φ(CV, ingresos, educación, sitios sustitutos)</i>."
      },
      {
        id: "mcv3",
        q: "3. Si un derrame petrolero o el ruido de una carretera degrada el parque y desplaza la demanda de D1 a D2 al mismo costo p*, ¿cuál es la pérdida de bienestar?",
        opts: [
          "Solo el gasto en pasajes multiplicado por las visitas que se perdieron",
          "El área sombreada completa entre las dos curvas de demanda (D1 y D2) por encima del costo p*",
          "Cero, porque el precio de entrada al parque sigue siendo gratis"
        ],
        ans: 1,
        why: "<b>Así es:</b> el bienestar recreativo es el <b>Excedente del Consumidor</b> (área bajo la demanda sobre p*). Al caer la calidad de D<sub>1</sub> a D<sub>2</sub>, el país pierde exactamente el área encerrada entre ambas curvas."
      }
    ],
    hed: [
      {
        id: "hed1",
        q: "1. En la ecuación de pizarra P_i = c + β·terreno_i + φ·río_i + δ·riego_i + ε_i, ¿qué interpreta económicamente el coeficiente φ?",
        opts: [
          "El costo total de construir una casa en el terreno",
          "El precio implícito (prima marginal) que el mercado inmobiliario paga por el atributo ambiental 'acceso a río', manteniendo constantes los demás atributos",
          "La tasa de impuesto territorial (contribuciones) del predio"
        ],
        ans: 1,
        why: "<b>Correcto:</b> en Precios Hedónicos, la derivada parcial <i>∂P/∂río = φ</i> aísla cuánto está dispuesto a pagar el comprador por tener orilla o cercanía al río <b>ceteris paribus</b> (a igual tamaño y riego)."
      },
      {
        id: "hed2",
        q: "2. ¿Qué tipo de preferencia utiliza el Método de Precios Hedónicos (MPH) y cuál es su principal límite?",
        opts: [
          "Usa preferencias reveladas en compraventas reales, pero solo captura atributos percibidos por los compradores de propiedades (no mide valor de existencia de especies lejanas)",
          "Usa encuestas hipotéticas telefónicas y sirve para cualquier especie en peligro de extinción en la Antártica",
          "No necesita datos de precios de terrenos ni viviendas"
        ],
        ans: 0,
        why: "<b>Exacto:</b> al apoyarse en mercados reales de tierras o viviendas, evita el sesgo hipotético; <b>sin embargo</b>, si el mercado no percibe un daño ecológico invisible o no hay transacciones inmobiliarias, el MPH no lo puede medir."
      },
      {
        id: "hed3",
        q: "3. Si se instala un vertedero con malos olores junto a un barrio residencial, ¿qué signo esperarías en el coeficiente de 'cercanía al vertedero' en una ecuación hedónica?",
        opts: [
          "Positivo (+), porque aumenta el valor de las casas",
          "Negativo (−), porque la desamenidad ambiental reduce el precio de mercado de las viviendas cercanas",
          "Siempre exactamente igual a cero"
        ],
        ans: 1,
        why: "<b>Muy bien:</b> los atributos deseables (río limpio, áreas verdes, riego) tienen signo positivo, <b>mientras que</b> las desamenidades (ruido, humo, malos olores) castigan el precio con signo negativo."
      }
    ],
    mvc: [
      {
        id: "mvc1",
        q: "1. ¿Por qué el Método de Valoración Contingente (MVC) es insustituible frente a Costo de Viaje y Precios Hedónicos?",
        opts: [
          "Porque es el único método capaz de medir Valores de No Uso (existencia y legado) cuando no existe mercado real ni mercado sustituto",
          "Porque nunca requiere encuestas a la población",
          "Porque siempre da exactamente el mismo número que el precio de mercado"
        ],
        ans: 0,
        why: "<b>Idea central de prueba:</b> MCV y Hedónicos exigen conducta observable (viajar o comprar tierra). <b>En cambio</b>, el MVC crea un <b>mercado hipotético</b> mediante encuestas para valorar bienes sin mercado (biodiversidad, paisaje, agua/aire)."
      },
      {
        id: "mvc2",
        q: "2. ¿Cuál es la gran ventaja del formato Referéndum (dicotómico: 'Sí' / 'No') introducido por Bishop y Heberlein (1979)?",
        opts: [
          "Obliga a repreguntar 10 veces hasta que el encuestado se canse",
          "Elimina el sesgo inducido por las repreguntas iterativas y reduce el costo de aplicación de la encuesta",
          "Permite saltarse la descripción del problema ambiental"
        ],
        ans: 1,
        why: "<b>Textual de Lámina 10:</b> pedir solo una decisión de 'Sí' o 'No' frente a un monto imita una votación real, <b>por lo tanto</b> elimina el sesgo de punto de partida de las repreguntas y abarata el levantamiento."
      },
      {
        id: "mvc3",
        q: "3. ¿Cuál es la diferencia conceptual entre DAP (Disponibilidad a Pagar) y DAA (Disponibilidad a Aceptar)?",
        opts: [
          "DAP es lo que la persona paga por mejorar o evitar una pérdida ambiental; DAA es la compensación que exige por tolerar un daño o no recibir una mejora",
          "Son sinónimos exactos y siempre dan el mismo valor",
          "DAP solo se usa para empresas y DAA solo para el Estado"
        ],
        ans: 0,
        why: "<b>Exacto (Lámina 12):</b> la DAP pregunta por un pago acotado por el presupuesto familiar; <b>por el contrario</b>, la DAA pregunta por una compensación por perder un derecho ambiental, razón por la cual suele resultar más alta."
      }
    ],
    dix: [
      {
        id: "dix1",
        q: "1. En el Flujograma de Dixon y Sherman (1990), si el proyecto genera cambios en la productividad medibles PERO los precios de mercado están distorsionados, ¿qué corresponde aplicar?",
        opts: [
          "Enfoque de Mercados Sustitutos y Precios Sombra para cambios en la productividad",
          "Usar los precios privados con IVA y subsidios sin corregir nada",
          "Descartar el impacto porque no es medible"
        ],
        ans: 0,
        why: "<b>Ruta exacta de Lámina 14:</b> Productividad medible (SÍ) → Precios no distorsionados (NO) ⇒ <b>Mercados Sustitutos / Precios Sombra</b> (exactamente lo que haces en SNI 2026)."
      },
      {
        id: "dix2",
        q: "2. Según la Matriz de Rado Barzev (1999), si una inundación o proyecto daña puentes, viviendas, carreteras o plantas de tratamiento, ¿qué métodos de valoración se indican?",
        opts: [
          "Solo Valoración Contingente (VC)",
          "Costos de Reposición/Reubicación (CR) y Costos Preventivos o Evitados (CP)",
          "Solo Método del Costo de Viaje (MCV)"
        ],
        ans: 1,
        why: "<b>Exacto (Lámina 15):</b> todo el medio urbano construido (viviendas, puentes, estructura vial, agua, energía, basura) se valora con <b>CR (Reposición)</b> y <b>CP (Preventivos / Evitados)</b>."
      },
      {
        id: "dix3",
        q: "3. Según Dixon (1990) y Barzev (1999), si un proyecto altera el paisaje natural, monumentos históricos o biodiversidad sin uso comercial, ¿qué método corresponde?",
        opts: [
          "Valoración Contingente (VC)",
          "Costos de Salud (CS)",
          "Precios de Mercado (PM)"
        ],
        ans: 0,
        why: "<b>Clave de cierre:</b> los bienes estéticos, culturales, históricos y la biodiversidad son bienes de No Uso sin mercado; <b>en consecuencia</b>, el camino correcto en el flujograma lleva a <b>Valoración Contingente (VC)</b>."
      }
    ]
  };

  const mtUserAns = {};

  function renderMiniTest(blockKey, containerId, titulo) {
    const box = document.getElementById(containerId);
    if (!box) return;
    const qs = MT_BANK[blockKey] || [];
    let okBlock = 0, totalGlobalOk = 0, totalGlobalQ = 0;
    Object.keys(MT_BANK).forEach(bk => {
      MT_BANK[bk].forEach(q => {
        totalGlobalQ++;
        if (mtUserAns[q.id] === q.ans) totalGlobalOk++;
      });
    });

    const cardsHtml = qs.map(q => {
      const u = mtUserAns[q.id];
      const isAns = u !== undefined;
      const isOk = isAns && u === q.ans;
      if (isOk) okBlock++;
      const cls = isAns ? (" answered " + (isOk ? "ok" : "bad")) : "";
      const btns = q.opts.map((op, idx) =>
        `<button class="mt-btn ${u === idx ? 'sel' : ''}" onclick="responderMiniTest('${blockKey}','${q.id}',${idx},'${containerId}','${titulo.replace(/'/g, "\\'")}')">${op}</button>`
      ).join("");
      const stTxt = isAns ? `<span style="font-weight:800;font-size:11.3px;color:${isOk?'#15803D':'#DC2626'};margin-left:6px;">${isOk ? '✓ Correcto' : '✗ Revisa la lógica'}</span>` : "";
      return `
        <div class="mt-qcard${cls}">
          <div class="mt-qtxt">${q.q}${stTxt}</div>
          <div class="mt-opts">${btns}</div>
          <div class="mt-fb">${q.why}</div>
        </div>`;
    }).join("");

    box.innerHTML = `
      <div class="mt-head">
        <span class="mt-tit">🧠 Mini-Test Conceptual en Vivo — ${titulo} (${okBlock}/${qs.length})</span>
        <span class="pill-score" style="font-size:11px;">Puntaje Total Clase 27 Nov: ${totalGlobalOk} / ${totalGlobalQ}</span>
      </div>
      ${cardsHtml}`;
  }

  window.responderMiniTest = function(blockKey, qId, optIdx, containerId, titulo) {
    mtUserAns[qId] = optIdx;
    renderMiniTest(blockKey, containerId, titulo);
  };

  window.toggleOralBlur = function(elId, btn) {
    const node = document.getElementById(elId);
    if (!node) return;
    const blurred = node.classList.toggle("oral-blur");
    if (btn) btn.textContent = blurred ? "Revelar guion 👁" : "Modo Ciego (Practicar oral)";
  };

  // ==========================================================================
  // 3. ESTADO INTERACTIVO DE LAS 4 ZONAS CONCÉNTRICAS (100% MODIFICABLES)
  // ==========================================================================
  window.__mcvZonas = [
    { name: "Loc. 1", rate: 100, cv: 20, inc: 1000 },
    { name: "Loc. 2", rate: 70,  cv: 30, inc: 1100 },
    { name: "Loc. 3", rate: 80,  cv: 40, inc: 1300 },
    { name: "Loc. 4", rate: 60,  cv: 50, inc: 900  }
  ];

  window.presetZonasMcv = function(modo) {
    if (modo === "clase") {
      window.__mcvZonas = [
        { name: "Loc. 1", rate: 100, cv: 20, inc: 1000 },
        { name: "Loc. 2", rate: 70,  cv: 30, inc: 1100 },
        { name: "Loc. 3", rate: 80,  cv: 40, inc: 1300 },
        { name: "Loc. 4", rate: 60,  cv: 50, inc: 900  }
      ];
    } else if (modo === "monotono") {
      window.__mcvZonas = [
        { name: "Loc. 1", rate: 100, cv: 20, inc: 1000 },
        { name: "Loc. 2", rate: 75,  cv: 30, inc: 1000 },
        { name: "Loc. 3", rate: 50,  cv: 40, inc: 1000 },
        { name: "Loc. 4", rate: 25,  cv: 50, inc: 1000 }
      ];
    } else {
      window.__mcvZonas = [
        { name: "Loc. 1", rate: 95,  cv: 20, inc: 950  },
        { name: "Loc. 2", rate: 70,  cv: 30, inc: 1050 },
        { name: "Loc. 3", rate: 55,  cv: 40, inc: 1100 },
        { name: "Loc. 4", rate: 90,  cv: 55, inc: 1850 }
      ];
    }
    buildZonasTable();
    drawRa2Mcv();
  };

  window.updateZonaVal = function(idx, field, rawVal) {
    const v = Math.max(0, parseFloat(rawVal) || 0);
    window.__mcvZonas[idx][field] = v;
    drawRa2Mcv();
  };

  function buildZonasTable() {
    const tbody = document.getElementById("mcv-zonas-tbody");
    if (!tbody) return;
    tbody.innerHTML = window.__mcvZonas.map((z, i) => `
      <tr id="mcv-zrow-${i}">
        <td id="mcv-zname-${i}">${z.name} (Anillo ${i + 1})</td>
        <td><input class="zn-in" type="number" min="0" max="500" step="5" value="${z.rate}" oninput="updateZonaVal(${i},'rate',this.value)" /> <span style="font-size:10px;color:#64748B;">/1000</span></td>
        <td><input class="zn-in" type="number" min="5" max="150" step="5" value="${z.cv}" oninput="updateZonaVal(${i},'cv',this.value)" /></td>
        <td><input class="zn-in" type="number" min="200" max="5000" step="50" value="${z.inc}" oninput="updateZonaVal(${i},'inc',this.value)" /></td>
      </tr>
    `).join("");
  }

  // ==========================================================================
  // 4. HTML DEL PANEL 12 (CLASE 27 NOV — REFUERZO PALABRAL + TESTEO + ZONAS EDITABLES)
  // ==========================================================================
  const PANEL_RA2_27NOV_HTML = `
  <div id="panel-ra2_27nov" class="panel">
    <div class="sec-title">
      <span>[27 Nov · Clase RA2] Valoración Económica Ambiental: MCV Zonal/Bienestar, Precios Hedónicos, MVC y Dixon/Barzev</span>
      <div class="btn-bar">
        <button id="ra2-btn-mcv" class="act-btn primary" onclick="selRa2Sub('mcv', this)">A. Costo de Viaje (Zonas + Pérdida D1→D2)</button>
        <button id="ra2-btn-hed" class="act-btn" onclick="selRa2Sub('hed', this)">B. Precios Hedónicos (Pizarra 27 Nov)</button>
        <button id="ra2-btn-mvc" class="act-btn" onclick="selRa2Sub('mvc', this)">C. Valoración Contingente (DAP/DAA · Referéndum)</button>
        <button id="ra2-btn-dix" class="act-btn" onclick="selRa2Sub('dix', this)">D. Selector Dixon (1990) + Matriz Barzev (1999)</button>
      </div>
    </div>

    <!-- ================= SUB A: MCV ZONAL EDITABLE + PÉRDIDA BIENESTAR ================= -->
    <div id="ra2-sub-mcv" class="ra2-sub active">
      <div id="mcv-hilo" class="hilo-box"></div>
      <div id="mcv-tutor" class="tutor-box"></div>

      <div class="btn-bar" style="margin-bottom:8px;">
        <button class="act-btn primary" onclick="presetMcv27('derrame')">Escenario Clase: Derrame / Ruido Carretera (-40% visitas)</button>
        <button class="act-btn" onclick="presetMcv27('cierre')">Cierre Total del Parque (-100% visitas)</button>
        <button class="act-btn" onclick="presetMcv27('mejora')">Restauración Ecológica (+25% visitas)</button>
      </div>

      <div class="sliders-grid">
        <div class="sl-card"><div class="sl-head"><span>Costo de Viaje Base p* (US$)</span><span id="mcv-p-v" class="sl-val">US$ 20</span></div><input id="mcv-p" type="range" min="5" max="60" step="1" value="20" oninput="drawRa2Mcv()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Precio Estrangulamiento CV_CP (US$)</span><span id="mcv-cp-v" class="sl-val">US$ 80</span></div><input id="mcv-cp" type="range" min="50" max="140" step="5" value="80" oninput="drawRa2Mcv()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Visitas Iniciales v1 (al año)</span><span id="mcv-v1-v" class="sl-val">10.000</span></div><input id="mcv-v1" type="range" min="2000" max="30000" step="500" value="10000" oninput="drawRa2Mcv()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Cambio Calidad Parque (% Visitas)</span><span id="mcv-chg-v" class="sl-val">-40%</span></div><input id="mcv-chg" type="range" min="-100" max="40" step="5" value="-40" oninput="drawRa2Mcv()" /></div>
      </div>

      <div class="kpis">
        <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Excedente Inicial (bajo D1)</div><div id="mcv-k-ec1" class="kpi-val">US$ 300.000</div><div id="mcv-k-ec1s" class="kpi-sub">DAP recreativa anual</div></div>
        <div class="kpi" style="border-left-color:#7C3AED;"><div class="kpi-lbl">Visitas Nuevas (v2)</div><div id="mcv-k-v2" class="kpi-val">6.000 / año</div><div id="mcv-k-dv" class="kpi-sub">ΔVisitas = -4.000</div></div>
        <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Pérdida / Ganancia Bienestar (ΔW)</div><div id="mcv-k-dw" class="kpi-val">-US$ 120.000</div><div id="mcv-k-dws" class="kpi-sub">Área entre D1 y D2</div></div>
        <div class="kpi" style="border-left-color:#059669;"><div class="kpi-lbl">Excedente Remanente (bajo D2)</div><div id="mcv-k-ec2" class="kpi-val">US$ 180.000</div><div class="kpi-sub">Bienestar post-impacto</div></div>
      </div>

      <div id="mcv-fstrip" class="fstrip-grid"></div>

      <div class="ra2-dual">
        <div class="ra2-card">
          <div class="ra2-card-tit">
            <span>1. Zonas Concéntricas Editables (Lámina 4)</span>
            <span style="display:flex;gap:4px;flex-wrap:wrap;">
              <button class="act-btn" style="padding:2px 7px;font-size:10.5px;" onclick="presetZonasMcv('clase')">Clase (Loc. 3)</button>
              <button class="act-btn" style="padding:2px 7px;font-size:10.5px;" onclick="presetZonasMcv('monotono')">Sin Paradoja</button>
              <button class="act-btn" style="padding:2px 7px;font-size:10.5px;" onclick="presetZonasMcv('loc4')">Loc. 4 Rica</button>
            </span>
          </div>
          <svg id="svg-mcv-zonas" viewBox="0 0 430 275"></svg>
          <table class="cl-tbl" style="margin-top:6px;">
            <thead><tr><th>Zona (Edita los números)</th><th>Tasa Vis.</th><th>CV (US$)</th><th>Ingreso (US$)</th></tr></thead>
            <tbody id="mcv-zonas-tbody"></tbody>
          </table>
          <div id="mcv-zonas-diag" class="zn-diag"></div>
        </div>
        <div class="ra2-card">
          <div class="ra2-card-tit"><span>2. Demanda Recreativa (D1 → D2) y Pérdida de Bienestar (Láminas 5–6)</span></div>
          <svg id="svg-mcv-bienestar" viewBox="0 0 540 355"></svg>
        </div>
      </div>

      <div id="mt-mcv" class="mt-box"></div>
      <div id="ped-ra2-mcv" class="ped-grid"></div>
    </div>

    <!-- ================= SUB B: PRECIOS HEDÓNICOS (PIZARRA 27 NOV) ================= -->
    <div id="ra2-sub-hed" class="ra2-sub">
      <div id="hed-hilo" class="hilo-box"></div>
      <div id="hed-tutor" class="tutor-box"></div>

      <div class="sliders-grid">
        <div class="sl-card"><div class="sl-head"><span>Intercepto Base c ($MM)</span><span id="hed-c-v" class="sl-val">$15,0M</span></div><input id="hed-c" type="range" min="5" max="40" step="1" value="15" oninput="drawRa2Hed()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Superficie Terreno (ha)</span><span id="hed-ter-v" class="sl-val">5,0 ha</span></div><input id="hed-ter" type="range" min="1" max="20" step="0.5" value="5" oninput="drawRa2Hed()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Coef. β ($MM / ha)</span><span id="hed-b-v" class="sl-val">$8,0M</span></div><input id="hed-b" type="range" min="2" max="20" step="0.5" value="8" oninput="drawRa2Hed()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Acceso / Orilla Río (φ $MM)</span><span id="hed-phi-v" class="sl-val">$18,0M</span></div><input id="hed-phi" type="range" min="0" max="40" step="1" value="18" oninput="drawRa2Hed()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Acceso Agua / Riego (δ $MM)</span><span id="hed-del-v" class="sl-val">$12,0M</span></div><input id="hed-del" type="range" min="0" max="30" step="1" value="12" oninput="drawRa2Hed()" /></div>
      </div>

      <div class="kpis">
        <div class="kpi" style="border-left-color:#1E293B;"><div class="kpi-lbl">Precio Total Estimado (P_i)</div><div id="hed-k-tot" class="kpi-val">$85,0 MM</div><div class="kpi-sub">Valor de mercado del predio</div></div>
        <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Componente Físico (c + β·ter)</div><div id="hed-k-fis" class="kpi-val">$55,0 MM</div><div id="hed-k-fisp" class="kpi-sub">64,7% del valor</div></div>
        <div class="kpi" style="border-left-color:#059669;"><div class="kpi-lbl">Prima Ambiental Implícita (φ + δ)</div><div id="hed-k-amb" class="kpi-val">$30,0 MM</div><div id="hed-k-ambp" class="kpi-sub">35,3% (Río + Riego/Agua)</div></div>
      </div>

      <div id="hed-fstrip" class="fstrip-grid"></div>
      <div class="svg-box"><svg id="svg-hedonico" viewBox="0 0 940 270"></svg></div>
      <div id="mt-hed" class="mt-box"></div>
      <div id="ped-ra2-hed" class="ped-grid"></div>
    </div>

    <!-- ================= SUB C: VALORACIÓN CONTINGENTE (MVC) ================= -->
    <div id="ra2-sub-mvc" class="ra2-sub">
      <div id="mvc-hilo" class="hilo-box"></div>
      <div id="mvc-tutor" class="tutor-box"></div>

      <div class="btn-bar" style="margin-bottom:8px;">
        <button id="mvc-esc-dap" class="act-btn primary" onclick="setEscenarioMvc('dap')">Escenario A: DAP (Pagar para mejorar / evitar daño)</button>
        <button id="mvc-esc-daa" class="act-btn" onclick="setEscenarioMvc('daa')">Escenario B: DAA (Compensación por aceptar pérdida)</button>
      </div>

      <div class="sliders-grid">
        <div class="sl-card"><div class="sl-head"><span>Monto Ofrecido en Referéndum ($)</span><span id="mvc-bid-v" class="sl-val">$3.500/mes</span></div><input id="mvc-bid" type="range" min="500" max="12000" step="500" value="3500" oninput="drawRa2Mvc()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Valoración Mediana del Hogar ($)</span><span id="mvc-med-v" class="sl-val">$4.000/mes</span></div><input id="mvc-med" type="range" min="1000" max="10000" step="250" value="4000" oninput="drawRa2Mvc()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Hogares Población Objetivo (N)</span><span id="mvc-hog-v" class="sl-val">15.000</span></div><input id="mvc-hog" type="range" min="1000" max="50000" step="1000" value="15000" oninput="drawRa2Mvc()" /></div>
      </div>

      <div class="kpis">
        <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Prob. Responder "SÍ" al Monto</div><div id="mvc-k-prob" class="kpi-val">58,3%</div><div id="mvc-k-esc" class="kpi-sub">Formato Referéndum (Sí/No)</div></div>
        <div class="kpi" style="border-left-color:#7C3AED;"><div class="kpi-lbl">Valor Medio Estimado / Hogar</div><div id="mvc-k-dap" class="kpi-val">$4.250 / mes</div><div class="kpi-sub">Área bajo curva logística</div></div>
        <div class="kpi" style="border-left-color:#059669;"><div class="kpi-lbl">Valor Económico Agregado Anual</div><div id="mvc-k-tot" class="kpi-val">$765,0 MM/año</div><div id="mvc-k-tots" class="kpi-sub">N × Valor medio × 12 meses</div></div>
      </div>

      <div id="mvc-fstrip" class="fstrip-grid"></div>
      <div class="svg-box"><svg id="svg-mvc-ref" viewBox="0 0 940 270"></svg></div>

      <div class="mvc-info-wrap">
        <div class="mvc-steps">
          <div class="mvc-st"><b>Etapa 1</b>Establecer el mercado hipotético</div>
          <div class="mvc-st"><b>Etapa 2</b>Obtener valoraciones (Referéndum Sí/No)</div>
          <div class="mvc-st"><b>Etapa 3</b>Estimar la DAP o DAA media</div>
          <div class="mvc-st"><b>Etapa 4</b>Agregar por N hogares objetivo</div>
          <div class="mvc-st"><b>Etapa 5</b>Validar resultados y controlar sesgos</div>
        </div>
        <div class="enc-grid">
          <div class="enc-box"><b>Sección 1 Encuesta — Descripción del Problema:</b> Información detallada con ayudas visuales (gráficas y fotografías) del bien ambiental (agua, aire o paisaje).</div>
          <div class="enc-box"><b>Sección 2 Encuesta — Escenario DAP / DAA:</b> Modificación concreta del objeto de estudio y pregunta dicotómica de disposición a pagar o aceptar compensación.</div>
          <div class="enc-box"><b>Sección 3 Encuesta — Socioeconómicas:</b> Ingreso, edad, estado civil y nivel de estudios para validar econométricamente la respuesta.</div>
        </div>
      </div>
      <div id="mt-mvc" class="mt-box"></div>
      <div id="ped-ra2-mvc" class="ped-grid"></div>
    </div>

    <!-- ================= SUB D: SELECTOR DIXON (1990) + BARZEV (1999) ================= -->
    <div id="ra2-sub-dix" class="ra2-sub">
      <div id="dix-tutor" class="tutor-box"></div>

      <div class="dix-wrap">
        <div class="dix-grid" id="dix-btns-wrap">
          <button class="dix-btn active" onclick="selDixon('prod_ok', this)">1. Productividad medible (Precios sin distorsión)</button>
          <button class="dix-btn" onclick="selDixon('prod_dist', this)">2. Productividad medible (Precios distorsionados)</button>
          <button class="dix-btn" onclick="selDixon('habitat', this)">3. Calidad Ambiental → Hábitat / Suelo</button>
          <button class="dix-btn" onclick="selDixon('aire_agua', this)">4. Calidad Ambiental → Aire y Agua</button>
          <button class="dix-btn" onclick="selDixon('salud', this)">5. Efectos en la Salud (Morbilidad / Mortalidad)</button>
          <button class="dix-btn" onclick="selDixon('recreacion', this)">6. Recreación y Turismo (Parques / Balnearios)</button>
          <button class="dix-btn" onclick="selDixon('estetico', this)">7. Bienes Estéticos, Biodiversidad y Culturales</button>
        </div>
        <div id="dix-res-box" class="dix-res"></div>
        <div class="cl-tbl-wrap">
          <div class="cl-tbl-tit">Matriz de Indicadores y Métodos de Valoración (Rado Barzev, 1999 — Láminas 15 y 16)</div>
          <div id="dix-barzev-tbl"></div>
        </div>
      </div>
      <div id="mt-dix" class="mt-box"></div>
      <div id="ped-ra2-dix" class="ped-grid"></div>
    </div>
  </div>
  `;

  function montarPanelRa2() {
    const wrap = document.getElementById("app-wrap");
    if (!wrap || document.getElementById("panel-ra2_27nov")) return;
    const pracPanel = document.getElementById("panel-practicar");
    if (pracPanel) {
      pracPanel.insertAdjacentHTML("beforebegin", PANEL_RA2_27NOV_HTML);
    } else {
      wrap.insertAdjacentHTML("beforeend", PANEL_RA2_27NOV_HTML);
    }

    const topTabs = document.querySelector(".top-tabs");
    if (topTabs && !topTabs.querySelector("[data-tab-ra27='1']")) {
      const btn = document.createElement("button");
      btn.className = "tab-btn";
      btn.dataset.tabRa27 = "1";
      btn.setAttribute("onclick", "openTab('ra2_27nov', this)");
      btn.style.borderColor = "#10B981";
      btn.style.color = "#065F46";
      btn.textContent = "12. [27 Nov] RA2: MCV Zonal, Hedónicos, MVC y Dixon/Barzev";
      topTabs.appendChild(btn);
    }

    const dateTags = {
      "'leche'": "[RA1]",
      "'transporte'": "[RA1]",
      "'horno'": "[18 Ago]",
      "'arboles'": "[23 Sep]",
      "'clase'": "[16 Nov]"
    };
    if (topTabs) {
      topTabs.querySelectorAll(".tab-btn").forEach(b => {
        const oc = b.getAttribute("onclick") || "";
        for (const [k, tg] of Object.entries(dateTags)) {
          if (oc.includes(k) && !b.textContent.includes(tg)) {
            b.textContent = b.textContent.replace(" (", " " + tg + " (");
          }
        }
      });
    }
    buildZonasTable();
  }

  // ==========================================================================
  // 5. LÓGICA 60 FPS + REFUERZO PALABRAL DINÁMICO DE LOS 4 BLOQUES
  // ==========================================================================
  window.selRa2Sub = function(subKey, btn) {
    document.querySelectorAll("#panel-ra2_27nov .ra2-sub").forEach(d => d.classList.remove("active"));
    const target = document.getElementById("ra2-sub-" + subKey);
    if (target) target.classList.add("active");
    if (btn && btn.parentElement) {
      btn.parentElement.querySelectorAll(".act-btn").forEach(b => b.classList.remove("primary"));
      btn.classList.add("primary");
    }
    if (subKey === "mcv") drawRa2Mcv();
    if (subKey === "hed") drawRa2Hed();
    if (subKey === "mvc") drawRa2Mvc();
    if (subKey === "dix") selDixon(window.__dixKey || "prod_ok");
  };

  // --- BLOQUE A: MCV ZONAL EDITABLE + PÉRDIDA BIENESTAR ---
  window.presetMcv27 = function(tipo) {
    if (tipo === "derrame") {
      document.getElementById("mcv-p").value = 20;
      document.getElementById("mcv-cp").value = 80;
      document.getElementById("mcv-v1").value = 10000;
      document.getElementById("mcv-chg").value = -40;
    } else if (tipo === "cierre") {
      document.getElementById("mcv-p").value = 20;
      document.getElementById("mcv-cp").value = 80;
      document.getElementById("mcv-v1").value = 10000;
      document.getElementById("mcv-chg").value = -100;
    } else {
      document.getElementById("mcv-p").value = 20;
      document.getElementById("mcv-cp").value = 80;
      document.getElementById("mcv-v1").value = 10000;
      document.getElementById("mcv-chg").value = 25;
    }
    drawRa2Mcv();
  };

  window.drawRa2Mcv = function() {
    const pStar = +document.getElementById("mcv-p").value;
    const cvCp = Math.max(pStar + 10, +document.getElementById("mcv-cp").value);
    const v1 = +document.getElementById("mcv-v1").value;
    const chgPct = +document.getElementById("mcv-chg").value;
    const v2 = Math.max(0, Math.round(v1 * (1 + chgPct / 100)));

    document.getElementById("mcv-p-v").textContent = "US$ " + pStar;
    document.getElementById("mcv-cp-v").textContent = "US$ " + cvCp;
    document.getElementById("mcv-v1-v").textContent = fmtInt(v1);
    document.getElementById("mcv-chg-v").textContent = (chgPct >= 0 ? "+" : "") + chgPct + "%";

    const ec1 = 0.5 * (cvCp - pStar) * v1;
    const ec2 = 0.5 * (cvCp - pStar) * v2;
    const dW = ec2 - ec1;

    document.getElementById("mcv-k-ec1").textContent = "US$ " + fmtInt(ec1);
    document.getElementById("mcv-k-v2").textContent = fmtInt(v2) + " / año";
    document.getElementById("mcv-k-dv").textContent = `ΔVisitas = ${v2 - v1 >= 0 ? "+" : ""}${fmtInt(v2 - v1)}`;
    document.getElementById("mcv-k-dw").textContent = `${dW >= 0 ? "+" : "-"}US$ ${fmtInt(Math.abs(dW))}`;
    document.getElementById("mcv-k-dws").textContent = dW < 0 ? "Pérdida social (D1 → D2)" : (dW > 0 ? "Ganancia por mejora (D1 → D2)" : "Sin cambio de bienestar");
    document.getElementById("mcv-k-ec2").textContent = "US$ " + fmtInt(ec2);

    // Detectar automáticamente paradojas en las 4 zonas editables (mayor CV pero mayor tasa)
    const zSorted = window.__mcvZonas.map((z, origIdx) => ({ ...z, origIdx })).sort((a, b) => a.cv - b.cv);
    const paradoxIdx = new Set();
    let paradoxNotes = [];
    for (let k = 1; k < zSorted.length; k++) {
      if (zSorted[k].rate > zSorted[k - 1].rate && zSorted[k].cv > zSorted[k - 1].cv) {
        paradoxIdx.add(zSorted[k].origIdx);
        const incExplain = zSorted[k].inc > zSorted[k - 1].inc
          ? `porque su ingreso promedio es mayor (<b>US$ ${fmtInt(zSorted[k].inc)}</b> vs. US$ ${fmtInt(zSorted[k - 1].inc)})`
          : `pese a no tener mayor ingreso (sugiere otra variable omitida como nivel educativo o falta de sitios sustitutos)`;
        paradoxNotes.push(`<b>${zSorted[k].name}</b> paga más costo de viaje (US$ ${zSorted[k].cv} &gt; US$ ${zSorted[k - 1].cv}) y, <b>sin embargo</b>, visita más (${zSorted[k].rate}‰ &gt; ${zSorted[k - 1].rate}‰) ${incExplain}.`);
      }
    }

    // Actualizar estilos de filas y diagnóstico verbal de zonas
    window.__mcvZonas.forEach((z, i) => {
      const tr = document.getElementById("mcv-zrow-" + i);
      const tdName = document.getElementById("mcv-zname-" + i);
      const isP = paradoxIdx.has(i);
      if (tr) tr.className = isP ? "ra2-highlight-row" : "";
      if (tdName) tdName.textContent = isP ? `${z.name} (¡Paradoja! ★)` : `${z.name} (Anillo ${i + 1})`;
    });
    const zDiag = document.getElementById("mcv-zonas-diag");
    if (zDiag) {
      if (paradoxNotes.length > 0) {
        zDiag.className = "zn-diag";
        zDiag.innerHTML = `<b>Lectura econométrica en vivo:</b> ${paradoxNotes.join(" ")} <b>Por lo tanto</b>, si graficaras solo CV vs. visitas sin controlar por ingreso, la curva de demanda saldría distorsionada.`;
      } else {
        zDiag.className = "zn-diag zn-ok";
        zDiag.innerHTML = `<b>Relación inversa limpia (sin paradoja):</b> a medida que sube el costo de viaje desde el anillo interno al externo, la tasa de visitas cae de forma estricta. <b>En otras palabras</b>, el efecto precio domina claramente sobre las diferencias de ingreso.`;
      }
    }

    // Hilo conductor vivo
    const hBox = document.getElementById("mcv-hilo");
    if (hBox) {
      hBox.innerHTML = `
        <div class="hilo-head">
          <span class="hilo-title">Hilo Conductor Vivo — Cómo mide el MCV una pérdida o mejora ambiental</span>
          <span class="hilo-sub">Basado en Láminas 2–6 (Clase 27 Nov)</span>
        </div>
        <div class="hilo-steps">
          <div class="hilo-step hs-b"><span class="hilo-conn hc-b">1. Primero, revelamos D1</span>Al observar las visitas desde las 4 zonas concéntricas (controlando por ingreso), obtenemos un excedente recreativo inicial de <b>US$ ${fmtInt(ec1)}/año</b>.</div>
          <div class="hilo-step hs-p"><span class="hilo-conn hc-p">2. Cambia la calidad</span>Ante un impacto ambiental de <b>${chgPct >= 0 ? "+" : ""}${chgPct}%</b>, la demanda pasa de <b>D<sub>1</sub> a D<sub>2</sub></b> y las visitas cambian de <b>${fmtInt(v1)}</b> a <b>${fmtInt(v2)}</b> al mismo costo p* = US$ ${pStar}.</div>
          <div class="hilo-step ${dW < 0 ? 'hs-r' : 'hs-g'}"><span class="hilo-conn ${dW < 0 ? 'hc-r' : 'hc-g'}">3. En consecuencia (ΔW)</span>El área sombreada entre D<sub>1</sub> y D<sub>2</sub> cuantifica exactamente <b>${dW >= 0 ? "+" : "-"}US$ ${fmtInt(Math.abs(dW))}/año</b> de cambio en bienestar social.</div>
        </div>`;
    }

    // Tutor conceptual palabral con conectores lógicos + cuadro comparativo + guion oral
    const tBox = document.getElementById("mcv-tutor");
    if (tBox) {
      const escVerbal = dW < 0
        ? `el parque sufre una degradación (como un derrame o ruido vial), <b>por lo que</b> menos personas desean viajar al mismo costo p* = US$ ${pStar} y el país pierde <b>US$ ${fmtInt(Math.abs(dW))}/año</b> de bienestar.`
        : (dW > 0
          ? `el parque mejora su calidad ecológica, <b>en consecuencia</b> atrae más visitantes al mismo costo p* = US$ ${pStar} y genera una ganancia social de <b>+US$ ${fmtInt(dW)}/año</b>.`
          : `el parque mantiene intacta su calidad, manteniendo un bienestar anual estable de <b>US$ ${fmtInt(ec1)}</b>.`);
      tBox.innerHTML = `
        <div class="tutor-head">
          <span class="tutor-tit">📖 Tutor Conceptual Palabral — Entiende el Costo de Viaje (MCV) con conectores lógicos</span>
          <span class="enun-badge">Preferencias Reveladas · Valor de Uso Recreativo</span>
        </div>
        <div class="tutor-prose">
          <p><span class="conn-tag">En primer lugar</span> los parques naturales suelen tener entrada gratuita ($0); <b>sin embargo</b>, eso <b>NO significa que su valor económico sea cero</b>. <span class="conn-tag ct-ok">En otras palabras</span> las familias revelan cuánto valoran el disfrute recreativo a través del dinero y el tiempo que sacrifican para llegar hasta allí (su <b>costo de viaje</b>).</p>
          <p><span class="conn-tag ct-purp">Ahora bien</span> no basta con mirar la distancia: como ves en las zonas editables de abajo, la tasa de visitación responde a una función multivariable <b>v<sub>i</sub> = φ(CV, ingresos, educación, sitios sustitutos)</b>. <span class="conn-tag ct-warn">Por esa razón</span> si una zona lejana tiene altos ingresos (como Loc. 3), puede visitar más que una zona cercana.</p>
          <p><span class="conn-tag ct-red">Finalmente, en este escenario</span> ${escVerbal}</p>
        </div>
        <div class="tutor-cols">
          <div class="comp-card">
            <div class="comp-card-tit">No confundir en la prueba</div>
            <div class="comp-item"><b>Gasto de viaje ≠ Beneficio social:</b> lo que se gasta en bencina es el <i>costo</i>; el valor social neto es el <b>Excedente del Consumidor</b> (el área del triángulo <i>sobre</i> p* y <i>bajo</i> la demanda).</div>
            <div class="comp-item"><b>MCV vs. MVC:</b> el MCV solo mide <b>Valor de Uso</b> de quienes efectivamente viajan; <b>a diferencia de</b> la Valoración Contingente, no captura el valor que asigna alguien que jamás visitará el parque.</div>
          </div>
          <div class="oral-card">
            <div class="oral-head">
              <span class="oral-tit">🎤 Guion Oral de Defensa (30 seg)</span>
              <button class="act-btn" style="padding:2px 7px;font-size:10.5px;" onclick="toggleOralBlur('oral-mcv-txt', this)">Modo Ciego (Practicar oral)</button>
            </div>
            <div id="oral-mcv-txt">
              "<b>En primer lugar</b>, el Método de Costo de Viaje valora áreas naturales recreativas usando el costo de traslado y tiempo como precio sustituto. <b>Luego</b>, estimamos econométricamente la tasa de visitas por zona controlando por ingreso, educación y sitios sustitutos para construir la curva de demanda del parque. <b>En consecuencia</b>, si un proyecto degrada el parque y desplaza la demanda de D<sub>1</sub> a D<sub>2</sub>, la pérdida de bienestar social equivale exactamente al área entre ambas curvas sobre el costo de viaje."
            </div>
          </div>
        </div>`;
    }

    renderFormulaStrip("mcv-fstrip", [
      {
        step: "PASO 1", lbl: "Función de Visitas por Zona (Lámina 3)", col: "#1D4ED8",
        eq: `v<sub>i</sub> = φ(CV<sub>i</sub>, Ingresos<sub>i</sub>, Educación<sub>i</sub>, Sustitutos<sub>i</sub>)`,
        sub: `Zonas activas: ${window.__mcvZonas.map(z => `${z.name} ($${z.cv} → ${z.rate}‰)`).join(" · ")}`,
        plain: `Puedes editar cualquier número en la tabla de abajo y ver cómo cambian los anillos y el diagnóstico de paradoja.`,
        next: `↳ Con las tasas zonales se construye la demanda agregada D1 del Paso 2.`
      },
      {
        step: "PASO 2", lbl: "Excedente Recreativo Inicial (bajo D1)", col: "#7C3AED",
        eq: `EC<sub>1</sub> = ${mFrac("1", "2")} · (CV<sub>CP</sub> − p*) · v<sub>1</sub>`,
        sub: `EC<sub>1</sub> = 0,5 · ($${cvCp} − $${pStar}) · ${fmtInt(v1)} = ${vChip("US$ "+fmtInt(ec1), "vc-p")}`,
        plain: `Disposición a pagar neta por encima del costo de viaje p* que disfrutan los ${fmtInt(v1)} visitantes al año.`,
        next: `↳ Ahora comparamos contra D2 en el Paso 3 para medir el impacto.`
      },
      {
        step: "PASO 3", lbl: "Pérdida / Ganancia de Bienestar (D1 → D2)", col: dW < 0 ? "#DC2626" : "#059669",
        eq: `ΔW = EC<sub>2</sub> − EC<sub>1</sub> = ${mFrac("1", "2")}·(CV<sub>CP</sub> − p*)·(v<sub>2</sub> − v<sub>1</sub>)`,
        sub: `ΔW = 0,5 · ($${cvCp} − $${pStar}) · (${fmtInt(v2)} − ${fmtInt(v1)}) = ${rChip((dW>=0?"+":"-")+"US$ "+fmtInt(Math.abs(dW)), dW < 0)}`,
        plain: dW < 0 ? `Daño recreativo anual que debe imputarse como costo ambiental en el flujo social.` : `Beneficio recreativo anual atribuible a la restauración o mejora del parque.`,
        next: dW < 0 ? `↳ Este daño entra con signo negativo en el VANS del proyecto contaminante.` : `↳ Este beneficio suma al VANS del proyecto ambiental.`,
        nextCls: dW < 0 ? "nx-bad" : "nx-ok"
      }
    ]);

    // SVG 1: Anillos Concéntricos Dinámicos SIN superposición de etiquetas (4 cuadrantes separados)
    const svgZ = document.getElementById("svg-mcv-zonas");
    if (svgZ) {
      svgZ.innerHTML = "";
      const cx = 215, cy = 142;
      const maxCv = Math.max(50, ...window.__mcvZonas.map(z => z.cv));
      // 4 ángulos bien separados en los 4 cuadrantes (SE, NO, SO, NE)
      const angles = [0.42, -2.35, 2.52, -0.58];
      const pillPos = [
        { x: 325, y: 238, anc: "middle" }, // Loc 1 abajo-derecha
        { x: 108, y: 28,  anc: "middle" }, // Loc 2 arriba-izquierda
        { x: 108, y: 248, anc: "middle" }, // Loc 3 abajo-izquierda
        { x: 325, y: 28,  anc: "middle" }  // Loc 4 arriba-derecha
      ];

      window.__mcvZonas.forEach((z, i) => {
        const rad = 28 + (z.cv / maxCv) * 76;
        const isP = paradoxIdx.has(i);
        el("circle", {
          cx, cy, r: rad, fill: "none",
          stroke: isP ? "#D97706" : "#94A3B8",
          "stroke-width": isP ? "1.8" : "1.2",
          "stroke-dasharray": "4,3"
        }, svgZ);
      });

      el("circle", { cx, cy, r: 15, fill: "#0F172A" }, svgZ);
      const tp = el("text", { x: cx, y: cy + 3.5, fill: "#FFFFFF", "font-size": "7.5", "font-weight": "800", "text-anchor": "middle" }, svgZ);
      tp.textContent = "PARQUE";

      window.__mcvZonas.forEach((z, i) => {
        const rad = 28 + (z.cv / maxCv) * 76;
        const px = cx + Math.cos(angles[i]) * rad;
        const py = cy + Math.sin(angles[i]) * rad;
        const isP = paradoxIdx.has(i);
        const col = isP ? "#D97706" : (i === 0 ? "#1D4ED8" : "#334155");
        const pp = pillPos[i];
        // Línea guía limpia desde el punto del anillo hacia la etiqueta en esquina
        el("line", { x1: px, y1: py, x2: pp.x, y2: pp.y + (pp.y < cy ? 8 : -10), stroke: col, "stroke-width": "1.2", "stroke-dasharray": "2,2" }, svgZ);
        el("circle", { cx: px, cy: py, r: 5.5, fill: col, stroke: "#FFF", "stroke-width": "1.5" }, svgZ);
        drawPill(svgZ, pp.x, pp.y, `${z.name}: $${z.cv} · ${z.rate}‰${isP ? ' ★' : ''}`, col, isP ? "#FFFBEB" : "#FFFFFF", pp.anc, "9.8");
      });
    }

    // SVG 2: Curvas D1 -> D2 y Pérdida de Bienestar
    const svgB = document.getElementById("svg-mcv-bienestar");
    if (svgB) {
      svgB.innerHTML = "";
      addDefs(svgB);
      const M = { l: 60, r: 30, t: 28, b: 48 }, W = 540, H = 355;
      const maxV = Math.max(v1, v2, 10000) * 1.25;
      const maxP = cvCp * 1.18;
      const sx = v => M.l + (v / maxV) * (W - M.l - M.r);
      const sy = p => H - M.b - (p / maxP) * (H - M.t - M.b);

      drawAxesPizarra(svgB, M.l, M.t, W - M.r, H - M.b, "Costo de Viaje (US$)", "Visitas / año");

      const polyPts = `${sx(0)},${sy(cvCp)} ${sx(v1)},${sy(pStar)} ${sx(v2)},${sy(pStar)}`;
      el("polygon", {
        points: polyPts,
        fill: dW < 0 ? "rgba(153, 27, 27, 0.32)" : "rgba(5, 150, 105, 0.28)",
        stroke: dW < 0 ? "#991B1B" : "#059669",
        "stroke-width": "1.6"
      }, svgB);

      const v1Zero = v1 * (cvCp / (cvCp - pStar));
      const v2Zero = v2 * (cvCp / (cvCp - pStar));
      el("line", { x1: sx(0), y1: sy(cvCp), x2: sx(Math.min(maxV, v1Zero)), y2: sy(Math.max(0, cvCp - (cvCp - pStar) * Math.min(maxV, v1Zero) / v1)), stroke: "#1D4ED8", "stroke-width": "2.6" }, svgB);
      if (v2 > 0) {
        el("line", { x1: sx(0), y1: sy(cvCp), x2: sx(Math.min(maxV, v2Zero)), y2: sy(Math.max(0, cvCp - (cvCp - pStar) * Math.min(maxV, v2Zero) / v2)), stroke: dW < 0 ? "#991B1B" : "#059669", "stroke-width": "2.4", "stroke-dasharray": "6,4" }, svgB);
      }

      el("line", { x1: M.l, y1: sy(pStar), x2: sx(Math.max(v1, v2)), y2: sy(pStar), stroke: "#475569", "stroke-dasharray": "4,3" }, svgB);
      el("line", { x1: sx(v1), y1: sy(pStar), x2: sx(v1), y2: H - M.b, stroke: "#1D4ED8", "stroke-dasharray": "4,3" }, svgB);
      el("line", { x1: sx(v2), y1: sy(pStar), x2: sx(v2), y2: H - M.b, stroke: dW < 0 ? "#991B1B" : "#059669", "stroke-dasharray": "4,3" }, svgB);

      const tPs = el("text", { x: M.l - 7, y: sy(pStar) + 4, fill: "#0F172A", "font-size": "10.5", "font-weight": "800", "text-anchor": "end" }, svgB);
      tPs.textContent = "p* $" + pStar;
      const tCp = el("text", { x: M.l - 7, y: sy(cvCp) + 4, fill: "#1E3A8A", "font-size": "10.2", "font-weight": "800", "text-anchor": "end" }, svgB);
      tCp.textContent = "CV_CP $" + cvCp;
      const tv1 = el("text", { x: sx(v1), y: H - M.b + 16, fill: "#1D4ED8", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, svgB);
      tv1.textContent = "v1 (" + fmtInt(v1) + ")";
      const tv2 = el("text", { x: sx(v2), y: H - M.b + 30, fill: dW < 0 ? "#991B1B" : "#059669", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, svgB);
      tv2.textContent = "v2 (" + fmtInt(v2) + ")";

      drawPill(svgB, sx((v1 + v2) * 0.36), sy(pStar + (cvCp - pStar) * 0.42),
        (dW < 0 ? "Pérdida: -US$ " : "Ganancia: +US$ ") + fmtInt(Math.abs(dW)),
        dW < 0 ? "#991B1B" : "#059669", "#FFFFFF", "middle", "10.5");
      drawPill(svgB, sx(v1) + 14, sy(pStar) - 14, "D1", "#1D4ED8", "#EFF6FF", "start", "10.5");
      if (v2 > 0) drawPill(svgB, sx(v2) - 12, sy(pStar) - 24, "D2", dW < 0 ? "#991B1B" : "#059669", "#FFFFFF", "end", "10.5");
      if (Math.abs(v2 - v1) > 400) {
        drawArrow(svgB, sx(v1), sy(pStar) - 6, sx(v2), sy(pStar) - 6, dW < 0 ? "#DC2626" : "#15803D", dW < 0 ? "arr-red" : "arr-green", "", 0, 0);
      }
    }

    renderMiniTest("mcv", "mt-mcv", "Costo de Viaje (MCV)");
    renderPedBox("ped-ra2-mcv",
      `Al desplazarse la demanda recreativa de <b>D<sub>1</sub></b> a <b>D<sub>2</sub></b> (${fmtInt(v1)} → ${fmtInt(v2)} visitas), el bienestar social cambia en <b>${dW >= 0 ? "+" : "-"}US$ ${fmtInt(Math.abs(dW))}/año</b>.`,
      `<b>La Paradoja de Ingreso (Lámina 4):</b> prueba editar arriba el ingreso o la tasa de Loc. 3 y Loc. 4. Verás al instante que cuando una zona lejana es más rica, rompe la caída monótona simple y obliga a controlar econométricamente por ingreso.`,
      `<b>Defensa en prueba RA2:</b> el MCV solo captura <b>Valor de Uso Recreativo</b>. Si un parque protege biodiversidad valorada por personas que nunca viajarán, debes complementarlo con <b>Valoración Contingente (MVC)</b>.`
    );
  };

  // --- BLOQUE B: PRECIOS HEDÓNICOS ---
  window.drawRa2Hed = function() {
    const cVal = +document.getElementById("hed-c").value;
    const ter = +document.getElementById("hed-ter").value;
    const beta = +document.getElementById("hed-b").value;
    const phi = +document.getElementById("hed-phi").value;
    const delta = +document.getElementById("hed-del").value;

    document.getElementById("hed-c-v").textContent = "$" + fmtDec(cVal, 1) + "M";
    document.getElementById("hed-ter-v").textContent = fmtDec(ter, 1) + " ha";
    document.getElementById("hed-b-v").textContent = "$" + fmtDec(beta, 1) + "M";
    document.getElementById("hed-phi-v").textContent = "$" + fmtDec(phi, 1) + "M";
    document.getElementById("hed-del-v").textContent = "$" + fmtDec(delta, 1) + "M";

    const vTer = beta * ter, vFis = cVal + vTer, vAmb = phi + delta, pTot = vFis + vAmb;

    document.getElementById("hed-k-tot").textContent = "$" + fmtDec(pTot, 1) + " MM";
    document.getElementById("hed-k-fis").textContent = "$" + fmtDec(vFis, 1) + " MM";
    document.getElementById("hed-k-fisp").textContent = fmtDec((vFis / pTot) * 100, 1) + "% del precio";
    document.getElementById("hed-k-amb").textContent = "$" + fmtDec(vAmb, 1) + " MM";
    document.getElementById("hed-k-ambp").textContent = fmtDec((vAmb / pTot) * 100, 1) + "% (Río + Riego/Agua)";

    const hBox = document.getElementById("hed-hilo");
    if (hBox) {
      hBox.innerHTML = `
        <div class="hilo-head">
          <span class="hilo-title">Hilo Conductor Vivo — Descomposición Hedónica del Precio del Terreno</span>
          <span class="hilo-sub">Ecuación de pizarra 27 Nov: P_i = c + β·terreno_i + φ·río_i + δ·riego_i + ε_i</span>
        </div>
        <div class="hilo-steps">
          <div class="hilo-step hs-b"><span class="hilo-conn hc-b">1. Atributos físicos</span>Un terreno base ($${fmtDec(cVal,1)}M) de <b>${fmtDec(ter,1)} ha</b> a $${fmtDec(beta,1)}M/ha aporta <b>$${fmtDec(vFis,1)} MM</b> por su tamaño e infraestructura.</div>
          <div class="hilo-step hs-g"><span class="hilo-conn hc-g">2. Atributos ambientales</span>El acceso a río suma <b>+$${fmtDec(phi,1)} MM (φ)</b> y el riego/agua suma <b>+$${fmtDec(delta,1)} MM (δ)</b>: <b>$${fmtDec(vAmb,1)} MM</b> de valor ambiental implícito.</div>
          <div class="hilo-step hs-p"><span class="hilo-conn hc-p">3. Precio de mercado</span>El mercado capitaliza ambos bloques en <b>P<sub>i</sub> = $${fmtDec(pTot,1)} MM</b>; <b>por lo tanto</b>, contaminar el río destruye <b>$${fmtDec(phi,1)} MM</b> por predio.</div>
        </div>`;
    }

    const tBox = document.getElementById("hed-tutor");
    if (tBox) {
      tBox.innerHTML = `
        <div class="tutor-head">
          <span class="tutor-tit">📖 Tutor Conceptual Palabral — Entiende Precios Hedónicos (MPH) paso a paso</span>
          <span class="enun-badge">Preferencias Reveladas · Mercado Inmobiliario / Tierras</span>
        </div>
        <div class="tutor-prose">
          <p><span class="conn-tag">¿Cuál es la idea central?</span> Nadie puede ir al supermercado a comprar "un kilo de vista al río" o "un metro de silencio"; <b>sin embargo</b>, la gente <b>sí compra terrenos y casas</b> que traen esos atributos incluidos en el paquete.</p>
          <p><span class="conn-tag ct-ok">En consecuencia</span> el Método de Precios Hedónicos toma muchas compraventas reales y estima una regresión lineal (<b>P<sub>i</sub> = c + β·terreno<sub>i</sub> + φ·río<sub>i</sub> + δ·riego<sub>i</sub> + ε<sub>i</sub></b>). <span class="conn-tag ct-purp">De este modo</span> al comparar dos terrenos idénticos en hectáreas e infraestructura donde uno tiene río y el otro no, el coeficiente <b>φ = $${fmtDec(phi,1)} MM</b> revela exactamente cuánto valora el mercado ese recurso ambiental.</p>
          <p><span class="conn-tag ct-warn">Cuidado en la prueba</span> este método exige un mercado de tierras competitivo y transparente; <b>además</b>, solo mide atributos ambientales que los compradores realmente conocen y perciben.</p>
        </div>
        <div class="tutor-cols">
          <div class="comp-card">
            <div class="comp-card-tit">No confundir en la prueba</div>
            <div class="comp-item"><b>Atributo físico vs. ambiental:</b> superficie, calidad del suelo y cercanía a transporte son variables de control; <b>río, agua, aire limpio o ruido</b> son los atributos ambientales cuyo precio implícito buscamos aislar.</div>
            <div class="comp-item"><b>Signo del coeficiente:</b> un bien ambiental (río, riego) tiene signo <b>(+)</b>; una desamenidad (olor de vertedero, ruido vial) tiene signo <b>(−)</b>.</div>
          </div>
          <div class="oral-card">
            <div class="oral-head">
              <span class="oral-tit">🎤 Guion Oral de Defensa (30 seg)</span>
              <button class="act-btn" style="padding:2px 7px;font-size:10.5px;" onclick="toggleOralBlur('oral-hed-txt', this)">Modo Ciego (Practicar oral)</button>
            </div>
            <div id="oral-hed-txt">
              "<b>Primero</b>, caracterizamos un bien transado en el mercado —como terrenos o viviendas— por sus atributos físicos y ambientales. <b>Luego</b>, estimamos econométricamente su precio en función de esas características (P<sub>i</sub> = c + β·terreno + φ·río + δ·riego + ε). <b>Por lo tanto</b>, los coeficientes φ y δ miden el precio implícito marginal del atributo ambiental, manteniendo constantes las demás variables."
            </div>
          </div>
        </div>`;
    }

    renderFormulaStrip("hed-fstrip", [
      {
        step: "PASO 1", lbl: "Ecuación Hedónica Lineal (Sala 27 Nov)", col: "#1D4ED8",
        eq: `P<sub>i</sub> = c + β·terreno<sub>i</sub> + <span class="sym-t">φ·río<sub>i</sub></span> + <span class="sym-p">δ·riego<sub>i</sub></span> + ε<sub>i</sub>`,
        sub: `P<sub>i</sub> = $${fmtDec(cVal,1)}M + $${fmtDec(beta,1)}M·(${fmtDec(ter,1)}) + ${vChip("$"+fmtDec(phi,1)+"M","vc-t")} + ${vChip("$"+fmtDec(delta,1)+"M","vc-p")} = ${rChip("$"+fmtDec(pTot,1)+" MM")}`,
        plain: `Cada coeficiente mide cuánto cambia el precio del terreno cuando mejora ese atributo manteniendo lo demás constante.`,
        next: `↳ Los términos verde y morado aíslan el valor económico del río y el agua.`
      },
      {
        step: "PASO 2", lbl: "Precio Implícito Ambiental (Derivada Parcial)", col: "#059669",
        eq: `∂P / ∂río = φ &nbsp;&nbsp;|&nbsp;&nbsp; ∂P / ∂riego = δ`,
        sub: `Prima Ambiental = ${vChip("$"+fmtDec(phi,1)+"M","vc-t")} + ${vChip("$"+fmtDec(delta,1)+"M","vc-p")} = ${rChip("$"+fmtDec(vAmb,1)+" MM ("+fmtDec(vAmb/pTot*100,1)+"%)")}`,
        plain: `Si un proyecto degrada el río o seca el agua de riego, la caída en el valor de los terrenos mide el daño ambiental.`,
        next: `↳ Multiplica esta prima por el N° de predios afectados para llevarlo al VANS.`,
        nextCls: "nx-ok"
      }
    ]);

    const svg = document.getElementById("svg-hedonico");
    if (svg) {
      svg.innerHTML = "";
      const M = { l: 55, r: 30, t: 28, b: 44 }, W = 940, H = 270;
      const items = [
        { lbl: "Base (c)", base: 0, val: cVal, col: "#475569" },
        { lbl: "Superficie (β·ter)", base: cVal, val: vTer, col: "#1D4ED8" },
        { lbl: "Acceso Río (φ)", base: vFis, val: phi, col: "#0D9488" },
        { lbl: "Agua / Riego (δ)", base: vFis + phi, val: delta, col: "#7C3AED" },
        { lbl: "Precio Total (P_i)", base: 0, val: pTot, col: "#0F172A" }
      ];
      const maxY = Math.max(50, pTot * 1.22);
      const sy = v => H - M.b - (v / maxY) * (H - M.t - M.b);
      el("line", { x1: M.l, y1: H - M.b, x2: W - M.r, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);
      const slot = (W - M.l - M.r) / items.length, bw = slot * 0.56;
      items.forEach((it, idx) => {
        const x0 = M.l + idx * slot + (slot - bw) / 2;
        const yT = sy(it.base + it.val), yB = sy(it.base);
        el("rect", { x: x0, y: yT, width: bw, height: Math.max(2, yB - yT), fill: it.col, rx: 4 }, svg);
        const tv = el("text", { x: x0 + bw / 2, y: yT - 6, fill: "#0F172A", "font-size": "11.5", "font-weight": "800", "text-anchor": "middle" }, svg);
        tv.textContent = (idx > 0 && idx < 4 ? "+" : "") + "$" + fmtDec(it.val, 1) + "M";
        const tl = el("text", { x: x0 + bw / 2, y: H - M.b + 18, fill: "#1E293B", "font-size": "11", "font-weight": "700", "text-anchor": "middle" }, svg);
        tl.textContent = it.lbl;
      });
    }

    renderMiniTest("hed", "mt-hed", "Precios Hedónicos (MPH)");
    renderPedBox("ped-ra2-hed",
      `Del precio estimado del predio (<b>$${fmtDec(pTot,1)} MM</b>), un <b>${fmtDec(vAmb/pTot*100,1)}% ($${fmtDec(vAmb,1)} MM)</b> corresponde directamente a atributos ambientales (río + agua/riego).`,
      `<b>Ventaja clave frente a encuestas:</b> Precios Hedónicos usa <b>preferencias reveladas</b> en transacciones reales de compraventa, por lo que no sufre sesgo hipotético; su requisito es contar con datos suficientes de propiedades comparables.`,
      `<b>Pregunta típica de examen:</b> si te piden valorar el impacto de malos olores de un relleno sanitario o ruido de una carretera sobre viviendas cercanas, el método indicado es <b>Precios Hedónicos</b>.`
    );
  };

  // --- BLOQUE C: VALORACIÓN CONTINGENTE (MVC) ---
  window.__mvcEsc = "dap";
  window.setEscenarioMvc = function(esc) {
    window.__mvcEsc = esc;
    document.getElementById("mvc-esc-dap").classList.toggle("primary", esc === "dap");
    document.getElementById("mvc-esc-daa").classList.toggle("primary", esc === "daa");
    if (esc === "daa" && +document.getElementById("mvc-med").value < 5500) {
      document.getElementById("mvc-med").value = 6000;
    } else if (esc === "dap" && +document.getElementById("mvc-med").value > 5500) {
      document.getElementById("mvc-med").value = 4000;
    }
    drawRa2Mvc();
  };

  window.drawRa2Mvc = function() {
    const esc = window.__mvcEsc || "dap";
    const bid = +document.getElementById("mvc-bid").value;
    const med = +document.getElementById("mvc-med").value;
    const hog = +document.getElementById("mvc-hog").value;

    document.getElementById("mvc-bid-v").textContent = "$" + fmtInt(bid) + "/mes";
    document.getElementById("mvc-med-v").textContent = "$" + fmtInt(med) + "/mes";
    document.getElementById("mvc-hog-v").textContent = fmtInt(hog);

    const kSlope = 0.00075;
    const probSi = esc === "dap"
      ? 1 / (1 + Math.exp(kSlope * (bid - med)))
      : 1 / (1 + Math.exp(-kSlope * (bid - med)));
    const valMedio = esc === "dap" ? med * 1.04 : med * 1.12;
    const valAnualMM = (valMedio * 12 * hog) / 1e6;

    document.getElementById("mvc-k-prob").textContent = fmtDec(probSi * 100, 1) + "%";
    document.getElementById("mvc-k-esc").textContent = esc === "dap" ? "P(Sí pagar $" + fmtInt(bid) + ")" : "P(Sí aceptar $" + fmtInt(bid) + ")";
    document.getElementById("mvc-k-dap").textContent = "$" + fmtInt(valMedio) + " / mes";
    document.getElementById("mvc-k-tot").textContent = "$" + fmtDec(valAnualMM, 1) + " MM/año";
    document.getElementById("mvc-k-tots").textContent = `${fmtInt(hog)} hogares × $${fmtInt(valMedio)} × 12`;

    const hBox = document.getElementById("mvc-hilo");
    if (hBox) {
      hBox.innerHTML = `
        <div class="hilo-head">
          <span class="hilo-title">Hilo Conductor Vivo — Valoración Contingente (${esc === "dap" ? "Escenario DAP" : "Escenario DAA"})</span>
          <span class="hilo-sub">Enfoque directo por encuestas (Mercados Hipotéticos · Láminas 7–13)</span>
        </div>
        <div class="hilo-steps">
          <div class="hilo-step hs-b"><span class="hilo-conn hc-b">1. Creamos el escenario</span>Describimos con fotos/gráficas el cambio en agua, aire o paisaje y planteamos un <b>referéndum ("Sí" / "No")</b> por <b>$${fmtInt(bid)}/mes</b>.</div>
          <div class="hilo-step hs-p"><span class="hilo-conn hc-p">2. Estimamos aceptación</span>Al monto consultado, un <b>${fmtDec(probSi*100,1)}%</b> responde "Sí"; integrando la curva logística resulta una ${esc.toUpperCase()} media de <b>$${fmtInt(valMedio)}/mes</b> por hogar.</div>
          <div class="hilo-step hs-g"><span class="hilo-conn hc-g">3. Agregamos al territorio</span>Multiplicando por los <b>${fmtInt(hog)} hogares</b> (× 12 meses), el valor ambiental alcanza <b>$${fmtDec(valAnualMM,1)} MM/año</b>.</div>
        </div>`;
    }

    const tBox = document.getElementById("mvc-tutor");
    if (tBox) {
      tBox.innerHTML = `
        <div class="tutor-head">
          <span class="tutor-tit">📖 Tutor Conceptual Palabral — Entiende Valoración Contingente (MVC) con conectores</span>
          <span class="enun-badge">Preferencias Declaradas · Uso + No Uso (Existencia)</span>
        </div>
        <div class="tutor-prose">
          <p><span class="conn-tag">¿Cuándo se usa?</span> Cuando un bien ambiental <b>no tiene mercado real ni mercado sustituto</b> (por ejemplo: limpiar el aire, proteger un paisaje o salvar una especie nativa). <span class="conn-tag ct-ok">Por ello</span> aplicamos un <b>enfoque directo</b>: mediante encuestas presentamos un <b>mercado hipotético</b> con ayudas visuales y consultamos la valoración de las personas.</p>
          <p><span class="conn-tag ct-purp">Respecto a cómo preguntar</span> antiguamente se hacían experimentos iterativos (repreguntar varias veces subiendo o bajando el monto); <b>sin embargo</b>, eso inducía sesgos y encarecía el estudio. <span class="conn-tag ct-ok">En respuesta a eso</span> <b>Bishop y Heberlein (1979)</b> introdujeron el formato <b>Referéndum (dicotómico: "Sí" o "No")</b>, mucho más limpio y realista.</p>
          <p><span class="conn-tag ct-warn">Ahora en pantalla (${esc.toUpperCase()})</span> ${esc === "dap"
            ? `estás preguntando cuánto está dispuesto a <b>pagar</b> cada hogar para lograr una mejora o evitar un daño ambiental (DAP media = <b>$${fmtInt(valMedio)}/mes</b>).`
            : `estás preguntando qué <b>compensación mínima</b> exige cada hogar para aceptar una reducción de calidad ambiental (DAA media = <b>$${fmtInt(valMedio)}/mes</b>).`}</p>
        </div>
        <div class="tutor-cols">
          <div class="comp-card">
            <div class="comp-card-tit">No confundir en la prueba</div>
            <div class="comp-item"><b>DAP vs. DAA:</b> DAP = pago para mejorar o evitar daño (tope: el ingreso del hogar). DAA = compensación por tolerar un daño o no mejorar (suele ser mayor por aversión a la pérdida).</div>
            <div class="comp-item"><b>Referéndum vs. Iterativo:</b> Referéndum pregunta una sola vez "Sí/No" (elimina sesgo de repregunta y baja costos); el iterativo repregunta hasta que el entrevistado cambia de signo.</div>
          </div>
          <div class="oral-card">
            <div class="oral-head">
              <span class="oral-tit">🎤 Guion Oral de Defensa (30 seg)</span>
              <button class="act-btn" style="padding:2px 7px;font-size:10.5px;" onclick="toggleOralBlur('oral-mvc-txt', this)">Modo Ciego (Practicar oral)</button>
            </div>
            <div id="oral-mvc-txt">
              "<b>A diferencia de</b> Costo de Viaje y Precios Hedónicos, la Valoración Contingente es un método directo de preferencias declaradas que construye un mercado hipotético mediante encuestas, siendo el único capaz de captar Valores de No Uso. <b>Para evitar sesgos</b>, se prefiere el formato Referéndum dicotómico ('Sí' o 'No') de Bishop y Heberlein (1979), siguiendo 5 etapas: definir el escenario con ayudas visuales, levantar la DAP o DAA, estimar la media, agregar por hogares y validar con variables socioeconómicas."
            </div>
          </div>
        </div>`;
    }

    renderFormulaStrip("mvc-fstrip", [
      {
        step: "PASO 1", lbl: `Formato Referéndum (Bishop & Heberlein, 1979)`, col: "#1D4ED8",
        eq: esc === "dap" ? `P(SÍ | Bid) = ${mFrac("1", "1 + e<sup>k(Bid − Med)</sup>")}` : `P(SÍ | Comp) = ${mFrac("1", "1 + e<sup>−k(Comp − Med)</sup>")}`,
        sub: `Para $${fmtInt(bid)}/mes (Mediana $${fmtInt(med)}) ⇒ P(SÍ) = ${rChip(fmtDec(probSi*100,1)+"%")}`,
        plain: `Solo pide responder "Sí" o "No", eliminando el sesgo de punto de partida de las repreguntas iterativas.`,
        next: `↳ El área bajo la curva estima el valor medio por hogar ($${fmtInt(valMedio)}/mes).`
      },
      {
        step: "PASO 2", lbl: `Agregación Territorial (${esc.toUpperCase()} Total Anual)`, col: "#059669",
        eq: `Valor<sub>MVC</sub> = ${esc.toUpperCase()}<sub>media</sub> × 12 × N<sub>hogares</sub>`,
        sub: `Valor<sub>MVC</sub> = $${fmtInt(valMedio)} × 12 × ${fmtInt(hog)} = ${rChip("$"+fmtDec(valAnualMM,1)+" MM/año")}`,
        plain: `Único método capaz de capturar Valores de No Uso (existencia y legado) además del valor de uso.`,
        next: `↳ Recuerda validar econométricamente con ingreso, edad y educación (Sección 3).`,
        nextCls: "nx-ok"
      }
    ]);

    const svg = document.getElementById("svg-mvc-ref");
    if (svg) {
      svg.innerHTML = "";
      addDefs(svg);
      const M = { l: 58, r: 30, t: 26, b: 44 }, W = 940, H = 270;
      const sx = x => M.l + (x / 12500) * (W - M.l - M.r);
      const sy = p => H - M.b - p * (H - M.t - M.b);

      drawAxesPizarra(svg, M.l, M.t, W - M.r, H - M.b, "Probabilidad 'Sí' (%)", esc === "dap" ? "Monto a Pagar (DAP $/mes)" : "Compensación Ofrecida (DAA $/mes)");
      [0.25, 0.5, 0.75, 1.0].forEach(pv => {
        el("line", { x1: M.l, y1: sy(pv), x2: W - M.r, y2: sy(pv), stroke: "#E2E8F0" }, svg);
        const t = el("text", { x: M.l - 7, y: sy(pv) + 4, fill: "#475569", "font-size": "10", "text-anchor": "end" }, svg);
        t.textContent = Math.round(pv * 100) + "%";
      });

      const pts = [];
      for (let x = 0; x <= 12500; x += 250) {
        const pr = esc === "dap" ? 1 / (1 + Math.exp(kSlope * (x - med))) : 1 / (1 + Math.exp(-kSlope * (x - med)));
        pts.push(`${sx(x)},${sy(pr)}`);
      }
      if (esc === "dap") {
        el("polygon", { points: `${sx(0)},${sy(0)} ` + pts.join(" ") + ` ${sx(12500)},${sy(0)}`, fill: "rgba(29,78,216,0.16)" }, svg);
      }
      el("polyline", { points: pts.join(" "), fill: "none", stroke: esc === "dap" ? "#1D4ED8" : "#7C3AED", "stroke-width": "2.8" }, svg);
      el("line", { x1: M.l, y1: sy(probSi), x2: sx(bid), y2: sy(probSi), stroke: "#64748B", "stroke-dasharray": "4,3" }, svg);
      el("line", { x1: sx(bid), y1: sy(probSi), x2: sx(bid), y2: H - M.b, stroke: "#64748B", "stroke-dasharray": "4,3" }, svg);
      el("circle", { cx: sx(bid), cy: sy(probSi), r: 6, fill: "#DC2626", stroke: "#FFF", "stroke-width": "1.6" }, svg);
      drawPill(svg, sx(bid) + 12, sy(probSi) - 12, `$${fmtInt(bid)} → ${fmtDec(probSi*100,1)}% "Sí"`, "#DC2626", "#FEF2F2", "start", "10.5");
    }

    renderMiniTest("mvc", "mt-mvc", "Valoración Contingente (MVC)");
    renderPedBox("ped-ra2-mvc",
      `Bajo el escenario <b>${esc.toUpperCase()}</b> con mediana de $${fmtInt(med)}/mes, el beneficio/daño agregado para ${fmtInt(hog)} hogares es <b>$${fmtDec(valAnualMM,1)} MM/año</b>.`,
      `<b>¿Por qué la DAA suele superar a la DAP?</b> Porque la DAP tiene como techo el presupuesto del hogar, mientras que la DAA por perder un derecho ambiental no tiene techo y activa la aversión a la pérdida.`,
      `<b>Pregunta fija de prueba:</b> Bishop y Heberlein (1979) propusieron el formato <b>Referéndum (dicotómico Sí/No)</b> porque elimina el sesgo de las repreguntas iterativas y reduce costos.`
    );
  };

  // --- BLOQUE D: SELECTOR DIXON (1990) + BARZEV (1999) ---
  const DIXON_MAP = {
    prod_ok: {
      ruta: "Cambios en Productividad Medibles (SÍ) → Precios de mercado NO distorsionados (SÍ)",
      metodos: "Enfoque de Cambios en la Productividad (Precios de Mercado — PM)",
      ejemplos: "Pérdida de cosecha agrícola, baja en captura pesquera o incremento de producción maderera con precios competitivos.",
      logica: "Como el daño o beneficio cambia directamente la producción física de un bien que sí se vende en mercados competitivos, <b>por lo tanto</b> basta multiplicar el cambio físico (ΔQ) por el precio de mercado (PM).",
      barzev: [["Actividad Primaria / Secundaria", "Industria / Agricultura", "PM (Precios de Mercado)"], ["Ingreso Familiar / Inversiones", "Medio Socioeconómico", "PM (Precios de Mercado)"]]
    },
    prod_dist: {
      ruta: "Cambios en Productividad Medibles (SÍ) → Precios de mercado NO distorsionados (NO)",
      metodos: "Mercados Sustitutos y Precios Sombra para Cambios en la Productividad",
      ejemplos: "Producción agrícola o pesquera con subsidios, impuestos o aranceles que distorsionan el precio privado.",
      logica: "Aunque el cambio productivo sea medible, el precio de mercado es 'mentiroso' por impuestos o subsidios; <b>en consecuencia</b>, debemos limpiar distorsiones usando <b>Precios Sombra</b> o mercados sustitutos.",
      barzev: [["Insumos / Bienes Transables", "Distorsión arancel/impuesto", "PM ajustado a Precios Sombra (SNI)"], ["Suelo Productivo", "Pérdida de suelo por erosión", "VC / CO (Costo de Oportunidad)"]]
    },
    habitat: {
      ruta: "Cambios en la Calidad Ambiental → Hábitat",
      metodos: "Costo de Oportunidad (CO) · Costo de Reposición (CR) · Valor de la Tierra (Hedónicos)",
      ejemplos: "Alteración de bosques, humedales, pérdida de suelo por erosión o relocalización de ecosistemas.",
      logica: "Cuando no hay cambio productivo directo pero se altera un hábitat o suelo, <b>entonces</b> valoramos cuánto cuesta reponerlo (CR), a qué uso alternativo renunciamos (CO) o cómo cae el valor de la tierra.",
      barzev: [["Suelo (Físico Inerte)", "Pérdida de suelo por erosión", "VC, CO (Costo de Oportunidad)"], ["Infraestructura / Viviendas / Puentes", "Daños a medio urbano construido", "CR (Reposición), CP (Preventivos)"]]
    },
    aire_agua: {
      ruta: "Cambios en la Calidad Ambiental → Calidad de Aire y Agua",
      metodos: "Costo-Eficiencia de Prevención · Gastos Preventivos (CP) · Costos de Reposición (CR)",
      ejemplos: "Polvo, humo, aserrín, gases, malos olores, ruido, déficit de agua potable o plantas de tratamiento.",
      logica: "Si se deteriora el aire o el agua, <b>en primer lugar</b> observamos cuánto cuesta prevenir el daño (CP) o reponer el suministro (CR); <b>además</b>, para molestias perceptivas (olores, polvo, ruido) Barzev sugiere Valoración Contingente (VC).",
      barzev: [["Aire (Físico Inerte)", "Polvo, humo, aserrín, gases, olores, ruido", "VC (Valoración Contingente)"], ["Agua (Abastecimiento)", "Déficit anual de agua potable", "PM, CR (Reposición)"], ["Plantas Tratamiento Agua / Basura", "Infraestructura sanitaria", "CR, CP (Preventivos / Evitados)"]]
    },
    salud: {
      ruta: "Cambios en la Calidad Ambiental → Efectos en la Salud (Morbilidad / Mortalidad)",
      metodos: "Morbilidad: Pérdida de ingresos/ahorro + Costos Médicos (CS) · Mortalidad: Costo-Eficiencia de Prevención + Capital Humano (VVE)",
      ejemplos: "Contaminación hídrica que provoca enfermedades gastrointestinales o contaminación del aire (MP2,5) con hospitalizaciones.",
      logica: "Cuando el impacto daña la salud humana, Dixon distingue dos ramas: <b>por un lado</b>, enfermedad (morbilidad = gastos médicos + días no trabajados); <b>por otro lado</b>, mortalidad (capital humano / prevención / VVE).",
      barzev: [["Agua (Contaminación)", "Contaminación del agua / costos de salud", "CS (Costos de Salud)"], ["Centros Educ. y Salud", "Centros dañados o sobrecargados", "CR, CP / CS"]]
    },
    recreacion: {
      ruta: "Cambios en la Calidad Ambiental → Recreación",
      metodos: "Método del Costo de Viaje (MCV) · Valoración Contingente (VC)",
      ejemplos: "Parques nacionales, zonas verdes, balnearios de ríos, potencial turístico y esparcimiento familiar.",
      logica: "Como el servicio es recreativo y requiere trasladarse al sitio, <b>en primer lugar</b> se aplica <b>Costo de Viaje (MCV)</b>; <b>sin embargo</b>, si queremos medir mejoras hipotéticas futuras o no visitantes, sumamos <b>Valoración Contingente (VC)</b>.",
      barzev: [["Desarrollo Turístico", "Potencial turístico / Balnearios de ríos", "VC / MCV (Costo de Viaje)"], ["Zonas Verdes y Parques", "Medio físico perceptivo", "MCV / VC"]]
    },
    estetico: {
      ruta: "Cambios en la Calidad Ambiental → Bienes Estéticos, Biodiversidad, Culturales e Históricos",
      metodos: "Valoración Contingente (VC — única capaz de capturar Valor de Existencia / No Uso)",
      ejemplos: "Paisaje natural y urbano, monumentos históricos, especies amenazadas y patrimonio cultural.",
      logica: "Al tratarse de valores intangibles y de No Uso (existencia y legado) sin mercado sustituto observable, <b>en consecuencia</b> el flujograma conduce exclusivamente a la <b>Valoración Contingente (VC)</b>.",
      barzev: [["Paisaje Natural y Urbano", "Medio físico perceptivo", "VC (Valoración Contingente)"], ["Monumentos / Patrimonio", "Medio cultural e histórico", "VC (Valoración Contingente)"]]
    }
  };

  window.selDixon = function(key, btn) {
    window.__dixKey = key;
    const wrap = document.getElementById("dix-btns-wrap");
    if (wrap && btn) {
      wrap.querySelectorAll(".dix-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
    }
    const d = DIXON_MAP[key] || DIXON_MAP.prod_ok;

    const tBox = document.getElementById("dix-tutor");
    if (tBox) {
      tBox.innerHTML = `
        <div class="tutor-head">
          <span class="tutor-tit">📖 Tutor Conceptual Palabral — Cómo elegir el método correcto en un certamen (Dixon 1990 + Barzev 1999)</span>
          <span class="enun-badge">Láminas 14–16 · Mapa de Decisión</span>
        </div>
        <div class="tutor-prose">
          <p><span class="conn-tag">Regla de oro para no equivocarte</span> ante cualquier problema ambiental de prueba, hazte siempre <b>dos preguntas en orden</b>: <b>1)</b> ¿Afecta una producción física vendible (cosecha, pesca, madera)? Si <b>SÍ</b>, usa la rama izquierda (Precios de Mercado o Precios Sombra). <b>2)</b> Si <b>NO</b>, pasa a la rama derecha (Calidad Ambiental) y clasifica el impacto en <i>Hábitat, Aire/Agua, Salud, Recreación o Bienes Estéticos/Biodiversidad</i>.</p>
          <p><span class="conn-tag ct-ok">En la ruta seleccionada ahora</span> ${d.logica}</p>
        </div>
        <div class="tutor-cols">
          <div class="comp-card">
            <div class="comp-card-tit">Glosario Rápido Barzev (1999)</div>
            <div class="comp-item"><b>PM</b> (Precios de Mercado) · <b>CO</b> (Costo de Oportunidad) · <b>CR</b> (Reposición / Reubicación)</div>
            <div class="comp-item"><b>CP</b> (Preventivos / Evitados) · <b>CS</b> (Costos de Salud) · <b>VC</b> (Valoración Contingente)</div>
          </div>
          <div class="oral-card">
            <div class="oral-head">
              <span class="oral-tit">🎤 Guion Oral de Defensa (30 seg)</span>
              <button class="act-btn" style="padding:2px 7px;font-size:10.5px;" onclick="toggleOralBlur('oral-dix-txt', this)">Modo Ciego (Practicar oral)</button>
            </div>
            <div id="oral-dix-txt">
              "<b>Según el flujograma de Dixon y Sherman (1990)</b>, primero verificamos si existen cambios medibles en la productividad: si los precios no están distorsionados usamos precios de mercado, <b>y si están distorsionados</b> aplicamos precios sombra. <b>En cambio</b>, cuando el cambio recae en la calidad ambiental, elegimos el método según el efecto específico: costos de salud para morbilidad, reposición o prevención para infraestructura y aire/agua, costo de viaje para recreación y valoración contingente para paisaje o biodiversidad."
            </div>
          </div>
        </div>`;
    }

    const box = document.getElementById("dix-res-box");
    if (box) {
      box.innerHTML =
        `<div style="font-size:11px;font-weight:800;color:#065F46;text-transform:uppercase;">Ruta Dixon &amp; Sherman (1990)</div>` +
        `<div style="margin:3px 0;"><b>Camino:</b> ${d.ruta}</div>` +
        `<div style="margin:3px 0;"><b>Métodos recomendados:</b> <span style="color:#1E3A8A;font-weight:800;">${d.metodos}</span></div>` +
        `<div><b>Casos de aplicación:</b> ${d.ejemplos}</div>`;
    }
    const tBarz = document.getElementById("dix-barzev-tbl");
    if (tBarz) {
      const rows = d.barzev.map(r => `<tr><td>${r[0]}</td><td style="text-align:left;font-family:inherit;">${r[1]}</td><td style="text-align:center;font-weight:800;color:#1E3A8A;">${r[2]}</td></tr>`).join("");
      tBarz.innerHTML =
        `<table class="cl-tbl"><thead><tr><th>Categoría / Indicador (Barzev 1999)</th><th>Elemento Ambiental Evaluado</th><th>Código Método</th></tr></thead><tbody>${rows}</tbody></table>`;
    }
    renderMiniTest("dix", "mt-dix", "Flujograma Dixon (1990) y Matriz Barzev (1999)");
    renderPedBox("ped-ra2-dix",
      `Para <b>${d.ruta}</b>, la literatura oficial recomienda aplicar <b>${d.metodos}</b>.`,
      `<b>Atajo de memoria:</b> Infraestructura dañada (puentes, viviendas, plantas de agua/basura) → <b>CR / CP</b>. Salud humana → <b>CS</b>. Recreación → <b>MCV</b>. Paisaje, monumentos y biodiversidad → <b>VC</b>.`,
      `Si en un examen te presentan un caso mixto (ej. una carretera que daña un parque y también genera ruido en casas), <b>puedes combinar métodos</b> sin duplicar beneficios: MCV para visitantes + Hedónicos para vecinos.`
    );
  };

  // ==========================================================================
  // 6. INTEGRACIÓN CON STUDIO MODES (APRENDER + PRACTICAR + CONTROL LECTURA)
  // ==========================================================================
  function integrarConStudio() {
    // A) Tema 11 en LEARN_TOPICS con guía palabral reforzada
    if (Array.isArray(LEARN_TOPICS) && !LEARN_TOPICS.some(t => t.id === "t_ra2_27nov")) {
      const mapFechas = {
        t_horno: "7. Unidad II · [18 Ago] Precios Mentirosos (Horno de Pan) y Costos Hundidos",
        t_arboles: "10. Unidad IV · [23 Sep] Árboles Causales (Problemas ↔ Objetivos) y Marco Lógico",
        t_clase1: "4. Unidad II · [16 Nov] Caso Clase: Conversión Social Ítem a Ítem + Perpetuidad",
        t_clase2: "5. Unidad II · [16 Nov] Caso Clase Salmón: Sustitución de Importaciones y Subsidio"
      };
      LEARN_TOPICS.forEach(t => { if (mapFechas[t.id]) t.title = mapFechas[t.id]; });

      LEARN_TOPICS.push({
        id: "t_ra2_27nov",
        tab: "ra2_27nov",
        sub: null,
        retoIdx: 8,
        title: "11. Unidad IV · [27 Nov · NUEVO] Valoración RA2: MCV Zonal, Hedónicos, MVC y Dixon/Barzev",
        s1: "<b>Clase 27 de noviembre (Enfoque Palabral + Visual):</b> Lee el <b>Tutor Conceptual</b> con conectores lógicos en cada bloque y modifica directamente la tabla de las <b>4 zonas concéntricas</b>, los atributos hedónicos, el escenario DAP/DAA y el flujograma de Dixon. Cada bloque trae su propio <b>Mini-Test Conceptual</b> y <b>Guion Oral</b>.",
        s2: "<b>Fórmulas que mandan hoy:</b> En MCV, la pérdida por deterioro ambiental es el área entre D<sub>1</sub> y D<sub>2</sub> (<b>ΔW = ½·(CV<sub>CP</sub>−p*)·(v<sub>2</sub>−v<sub>1</sub>)</b>); en Precios Hedónicos de pizarra, <b>P<sub>i</sub> = c + β·terreno<sub>i</sub> + φ·río<sub>i</sub> + δ·riego<sub>i</sub> + ε<sub>i</sub></b>; en MVC, <b>Valor = DAP<sub>media</sub> × 12 × N<sub>hogares</sub></b>.",
        s3: "<b>Trampas de prueba de esta clase:</b> (1) En MCV zonal, una zona más lejana puede visitar más si tiene mayor ingreso (<b>Paradoja Loc. 3</b>); (2) En MVC, el formato <b>Referéndum (Bishop &amp; Heberlein, 1979)</b> evita el sesgo de repreguntas; (3) Para paisaje, monumentos o biodiversidad (No Uso), el único método válido es <b>Valoración Contingente</b>."
      });

      const sel = document.getElementById("learn-topic-sel");
      if (sel) {
        sel.innerHTML = "";
        LEARN_TOPICS.forEach((t, idx) => {
          const opt = document.createElement("option");
          opt.value = idx;
          opt.textContent = t.title;
          sel.appendChild(opt);
        });
        sel.value = String(learnTopicIdx);
      }
    }

    // B) Sumar 4 Retos en Modo Practicar (Retos 9, 10, 11 y 12 — numéricos + conceptuales)
    if (Array.isArray(PRAC_RETOS) && !PRAC_RETOS.some(r => r.id === "r9")) {
      PRAC_RETOS.push(
        {
          id: "r9", topicIdx: 10, short: "9. MCV 27 Nov",
          title: "Clase 27 Nov — Costo de Viaje (MCV): Paradoja Zonal y Pérdida de Bienestar",
          enun: "Un parque natural tiene costo de viaje base <b>p* = US$ 20</b>, precio de estrangulamiento <b>CV<sub>CP</sub> = US$ 80</b> y recibe <b>v<sub>1</sub> = 10.000 visitas/año</b>. Tras un derrame de petróleo, la demanda cae a <b>v<sub>2</sub> = 6.000 visitas/año</b> (D<sub>1</sub> → D<sub>2</sub>). Además, en la tabla zonal de clase, Loc. 3 paga US$ 40 (más que Loc. 2 a US$ 30) pero registra más visitas (80/1000 vs 70/1000).",
          qs: [
            { lbl: "Excedente recreativo inicial EC1 (US$/año)", type: "num", ans: 300000, tol: 0.02, ph: "ej. 300000" },
            { lbl: "Pérdida anual de bienestar por el derrame (US$/año, valor positivo)", type: "num", ans: 120000, tol: 0.02, ph: "ej. 120000" },
            { lbl: "¿Por qué Loc. 3 visita más que Loc. 2 pese a mayor costo de viaje?", type: "sel", opts: ["Seleccionar...", "Porque tiene un ingreso promedio mayor (US$ 1.300 vs US$ 1.100)", "Porque el MCV no depende del costo de viaje", "Porque tiene menor nivel educativo"], ans: "Porque tiene un ingreso promedio mayor (US$ 1.300 vs US$ 1.100)" }
          ],
          hint: "<b>Pista:</b> EC<sub>1</sub> = 0,5 × (CV<sub>CP</sub> − p*) × v<sub>1</sub>. La pérdida es el área sombreada entre D<sub>1</sub> y D<sub>2</sub>: 0,5 × (80 − 20) × (10.000 − 6.000).",
          sol: "EC1 = 0,5 × (80 − 20) × 10.000 = <b>US$ 300.000</b> | Pérdida = 0,5 × 60 × 4.000 = <b>US$ 120.000/año</b> | Loc. 3 tiene ingreso US$ 1.300 (control econométrico obligatorio en v_i = φ(CV, ingresos, ...))."
        },
        {
          id: "r10", topicIdx: 10, short: "10. Hedón. & MVC",
          title: "Clase 27 Nov — Precios Hedónicos, Referéndum MVC y Flujograma Dixon",
          enun: "En la ecuación de pizarra <b>P<sub>i</sub> = 15 + 8·terreno<sub>i</sub> + 18·río<sub>i</sub> + 12·riego<sub>i</sub></b> (en millones de $), evalúa un predio de <b>5 ha</b> con acceso a río y riego, y responde sobre MVC y Dixon (1990):",
          qs: [
            { lbl: "Precio total estimado del terreno ($ millones)", type: "num", ans: 85, tol: 0.02, ph: "ej. 85" },
            { lbl: "Prima ambiental implícita por río + riego ($ millones)", type: "num", ans: 30, tol: 0.02, ph: "ej. 30" },
            { lbl: "¿Qué ventaja tiene el formato Referéndum (Bishop & Heberlein, 1979)?", type: "sel", opts: ["Seleccionar...", "Elimina el sesgo de repreguntas iterativas y reduce costos", "Reemplaza la necesidad de describir el escenario", "Solo sirve para medir Precios Hedónicos"], ans: "Elimina el sesgo de repreguntas iterativas y reduce costos" },
            { lbl: "Según Dixon (1990), ¿qué método valora bienes estéticos, biodiversidad y patrimonio?", type: "sel", opts: ["Seleccionar...", "Valoración Contingente (VC)", "Solo Precios de Mercado", "Solo Costo de Reposición"], ans: "Valoración Contingente (VC)" }
          ],
          hint: "<b>Pista:</b> P = 15 + 8(5) + 18(1) + 12(1). La prima ambiental es φ + δ = 18 + 12.",
          sol: "P = 15 + 40 + 18 + 12 = <b>$85 MM</b> | Prima ambiental = 18 + 12 = <b>$30 MM</b> | Referéndum (Sí/No) elimina sesgo de repreguntas | Bienes estéticos/biodiversidad/culturales ⇒ <b>Valoración Contingente (VC)</b>."
        },
        {
          id: "r11", topicIdx: 10, short: "11. Casos Dixon",
          title: "Test Conceptual — Elige el Método Ambiental Correcto (Dixon 1990 + Barzev 1999)",
          enun: "En una prueba de desarrollo te presentan 4 situaciones ambientales distintas. Selecciona el <b>método de valoración más apropiado</b> según el Flujograma de Dixon y Sherman (1990) y la Matriz de Barzev (1999):",
          qs: [
            { lbl: "Caso A: Una carretera nueva genera ruido y reduce visitas a un parque natural", type: "sel", opts: ["Seleccionar...", "Método del Costo de Viaje (MCV)", "Solo Precios de Mercado (PM)", "Costo de Reposición (CR)"], ans: "Método del Costo de Viaje (MCV)" },
            { lbl: "Caso B: Malos olores de una planta reducen el precio de las casas vecinas", type: "sel", opts: ["Seleccionar...", "Método de Precios Hedónicos (MPH)", "Método del Costo de Viaje (MCV)", "Capital Humano"], ans: "Método de Precios Hedónicos (MPH)" },
            { lbl: "Caso C: Se quiere valorar la preservación de una especie endémica que casi nadie visita", type: "sel", opts: ["Seleccionar...", "Valoración Contingente (VC — mercado hipotético)", "Costo de Viaje (MCV)", "Precios de Mercado (PM)"], ans: "Valoración Contingente (VC — mercado hipotético)" },
            { lbl: "Caso D: Crecida de río daña un puente, carreteras y una planta de agua potable", type: "sel", opts: ["Seleccionar...", "Costos de Reposición (CR) y Costos Preventivos (CP)", "Valoración Contingente (VC)", "Precios Hedónicos (MPH)"], ans: "Costos de Reposición (CR) y Costos Preventivos (CP)" }
          ],
          hint: "<b>Pista con conectores:</b> Recreación con viajes ⇒ MCV; cambios en precios de viviendas/terrenos ⇒ Precios Hedónicos; bienes de No Uso sin mercado ⇒ VC; infraestructura urbana dañada ⇒ CR/CP.",
          sol: "Caso A ⇒ <b>MCV</b> | Caso B ⇒ <b>Precios Hedónicos</b> | Caso C ⇒ <b>Valoración Contingente</b> | Caso D ⇒ <b>CR y CP (Barzev 1999)</b>."
        },
        {
          id: "r12", topicIdx: 10, short: "12. Trampas RA2",
          title: "Test Conceptual — Trampas Verbales de Certamen (Clase 27 Nov)",
          enun: "Comprueba si detectas las 4 confusiones conceptuales más castigadas en evaluación ambiental RA2:",
          qs: [
            { lbl: "1. ¿Qué tipo de preferencia mide el Costo de Viaje (MCV) y Precios Hedónicos (MPH)?", type: "sel", opts: ["Seleccionar...", "Preferencias reveladas (conducta real observada en mercados sustitutos)", "Preferencias declaradas (mercados hipotéticos por encuesta)"], ans: "Preferencias reveladas (conducta real observada en mercados sustitutos)" },
            { lbl: "2. ¿Qué tipo de preferencia mide la Valoración Contingente (MVC)?", type: "sel", opts: ["Seleccionar...", "Preferencias reveladas (conducta real)", "Preferencias declaradas (mercados hipotéticos por encuesta)"], ans: "Preferencias declaradas (mercados hipotéticos por encuesta)" },
            { lbl: "3. Si preguntamos cuánto exige un vecino como compensación por tolerar humo, ¿qué medimos?", type: "sel", opts: ["Seleccionar...", "DAA (Disponibilidad a Aceptar)", "DAP (Disponibilidad a Pagar)"], ans: "DAA (Disponibilidad a Aceptar)" },
            { lbl: "4. ¿Cuál de las 3 secciones de la encuesta MVC incluye ingreso, edad y nivel de estudios?", type: "sel", opts: ["Seleccionar...", "Sección 3: Características Socioeconómicas (para control econométrico)", "Sección 1: Descripción del problema con fotos", "No se incluyen en encuestas MVC"], ans: "Sección 3: Características Socioeconómicas (para control econométrico)" }
          ],
          hint: "<b>Pista:</b> MCV y MPH observan hechos reales (reveladas); MVC pregunta escenarios (declaradas). Pagar por mejora = DAP; compensación por daño = DAA.",
          sol: "1) <b>Preferencias reveladas</b> | 2) <b>Preferencias declaradas</b> | 3) <b>DAA</b> | 4) <b>Sección 3: Características Socioeconómicas</b>."
        }
      );
      if (typeof saveStudioProg === "function") saveStudioProg();
    }

    // C) Sumar 6 preguntas nuevas de la Clase 27 Nov al Control de Lectura (QUIZ_PROY_DATA)
    if (Array.isArray(QUIZ_PROY_DATA) && !QUIZ_PROY_DATA.some(q => (q.tag || "").includes("27 Nov"))) {
      QUIZ_PROY_DATA.push(
        {
          tag: "27 Nov · MCV",
          q: "En el Método del Costo de Viaje (MCV), cuando se estima la curva de demanda de un parque natural, ¿qué representa el área total debajo de la curva de demanda (sobre el costo de viaje)?",
          opts: ["Solo el costo de combustible gastado por los turistas", "La disposición a pagar (excedente del consumidor) por la experiencia recreativa del parque", "El valor comercial de la madera del parque"],
          ans: 1,
          why: "El gasto de traslado es el precio sustituto; el beneficio neto social de la recreación es el área bajo la curva de demanda (disposición a pagar / excedente del consumidor — Lámina 5)."
        },
        {
          tag: "27 Nov · MCV",
          q: "Al aplicar el MCV por zonas concéntricas, la Loc. 3 tiene un costo de viaje mayor que la Loc. 2 (US$ 40 vs. US$ 30) pero registra una tasa de visitación superior (80/1000 vs. 70/1000). ¿Cuál es la explicación econométrica correcta?",
          opts: ["La tasa de visitación también depende del ingreso promedio (Loc. 3 tiene US$ 1.300 vs. US$ 1.100), educación y sitios sustitutos", "Existe un error aritmético porque el costo de viaje es la única variable explicativa", "Significa que los parques son bienes Giffen"],
          ans: 0,
          why: "En el MCV, v_i = φ(CV, ingresos, nivel educativo, disponibilidad de sustitutos). El mayor ingreso de Loc. 3 desplaza positivamente su tasa de visita (Láminas 3–4)."
        },
        {
          tag: "27 Nov · Hedónicos",
          q: "En la ecuación de Precios Hedónicos de terrenos vista en pizarra (P_i = c + β·terreno_i + φ·río_i + δ·riego_i + ε_i), ¿qué mide el parámetro δ?",
          opts: ["El valor marginal implícito que el mercado asigna al atributo 'riego/acceso a agua', ceteris paribus", "El precio total del terreno incluyendo construcciones", "El error aleatorio del modelo"],
          ans: 0,
          why: "En una forma funcional lineal hedónica, cada coeficiente captura la derivada parcial del precio respecto a ese atributo manteniendo constantes los demás factores."
        },
        {
          tag: "27 Nov · MVC",
          q: "¿Cuál es la principal ventaja del formato Referéndum (dicotómico: 'Sí' o 'No') propuesto por Bishop y Heberlein (1979) en Valoración Contingente?",
          opts: ["Elimina el sesgo inducido por las repreguntas iterativas y tiene un menor costo de aplicación", "No requiere describir el problema ambiental ni usar ayudas visuales", "Reemplaza la necesidad de recolectar datos socioeconómicos"],
          ans: 0,
          why: "El formato referéndum (Sí/No) evita el sesgo de punto de partida de los juegos iterativos y abarata el estudio (Lámina 10)."
        },
        {
          tag: "27 Nov · MVC",
          q: "En un estudio de Valoración Contingente, ¿qué diferencia a la Disponibilidad a Pagar (DAP) de la Disponibilidad a Aceptar (DAA)?",
          opts: ["La DAP mide el pago por lograr mejoras o evitar pérdidas ambientales; la DAA mide la compensación exigida por tolerar pérdidas o no recibir mejoras", "La DAP mide contaminación y la DAA mide solo recreación", "No existe diferencia práctica ni teórica entre ambas"],
          ans: 0,
          why: "Lámina 12: DAP = pago por mejora o evitar deterioro; DAA = compensación por deterioro ambiental o no mejoramiento."
        },
        {
          tag: "27 Nov · Dixon/Barzev",
          q: "Según el Flujograma de Dixon y Sherman (1990) y la Matriz de Barzev (1999), ¿qué combinación de métodos corresponde para valorar (i) contaminación del agua con enfermedades y (ii) pérdida de belleza escénica/monumentos?",
          opts: ["(i) Costos de Salud (CS) / Costos Médicos; y (ii) Valoración Contingente (VC)", "(i) Costo de Viaje; y (ii) Precios de Mercado", "(i) Precios Hedónicos únicamente; y (ii) Costo de Reposición únicamente"],
          ans: 0,
          why: "En Dixon (1990) y Barzev (1999), los efectos de morbilidad se valoran mediante costos médicos/de salud (CS) y pérdida de ingresos, mientras que bienes estéticos, biodiversidad y monumentos se valoran vía Valoración Contingente (VC)."
        }
      );
      if (typeof renderQuizProy === "function") renderQuizProy();
    }

    // D) Envolver openTab y activatePanelClean para renderizar Panel 12 al abrirlo
    const _origOpenTab = window.openTab;
    if (typeof _origOpenTab === "function") {
      window.openTab = function(name, btn) {
        const ret = _origOpenTab.apply(this, arguments);
        if (name === "ra2_27nov") {
          drawRa2Mcv(); drawRa2Hed(); drawRa2Mvc(); selDixon(window.__dixKey || "prod_ok");
        }
        return ret;
      };
    }
    const _origAct = window.activatePanelClean;
    if (typeof _origAct === "function") {
      window.activatePanelClean = function(panelName) {
        const ret = _origAct.apply(this, arguments);
        if (panelName === "ra2_27nov") {
          drawRa2Mcv(); drawRa2Hed(); drawRa2Mvc(); selDixon(window.__dixKey || "prod_ok");
        }
        return ret;
      };
    }
  }

  montarCalendarioBar();
  montarPanelRa2();
  integrarConStudio();
  try { drawRa2Mcv(); } catch (e) {}
  try { drawRa2Hed(); } catch (e) {}
  try { drawRa2Mvc(); } catch (e) {}
  try { selDixon("prod_ok"); } catch (e) {}
})();
</script>
"""


def inyectar_expansion_ra2_27nov(html_base: str) -> str:
    """Inyecta de forma segura el cronograma FDIC26 y el Módulo 12 (Clase 27 Nov RA2) en el HTML 60 FPS."""
    if not html_base or 'id="js-expansion-ra2-27nov"' in html_base:
        return html_base

    html_out = html_base
    if "</head>" in html_out:
        html_out = html_out.replace("</head>", CSS_EXPANSION_RA2_27NOV + "\n</head>", 1)
    else:
        html_out = CSS_EXPANSION_RA2_27NOV + html_out

    idx_body = html_out.rfind("</body>")
    if idx_body != -1:
        html_out = html_out[:idx_body] + JS_EXPANSION_RA2_27NOV + "\n" + html_out[idx_body:]
    else:
        html_out = html_out + JS_EXPANSION_RA2_27NOV

    return html_out
