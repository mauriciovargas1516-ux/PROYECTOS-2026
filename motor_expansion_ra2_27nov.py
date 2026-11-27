# -*- coding: utf-8 -*-
"""
motor_expansion_ra2_27nov.py — CALENDARIO OFICIAL FDIC26 + EXPANSIÓN CLASE 27 NOV (RA2) A 60 FPS
Módulo plug-and-play para PROYECTOS-2026 (Evaluación Integrada de Proyectos — ULagos 2026).

Agrega sobre `HTML_SIMULADOR_FLUIDO`:
  1) Línea de tiempo interactiva con fechas oficiales de ULagos Virtual (FDIC26 · 2026-2SEM)
     y etiquetas de fecha por clase en los temas y pestañas.
  2) Módulo 12 interactivo a 60 FPS ("Clase 27 Nov · Valoración Ambiental RA2 Avanzada"):
       A. Costo de Viaje (MCV) Zonal (anillos Loc. 1–4 + Paradoja Loc. 3) y Pérdida de Bienestar (D1 -> D2).
       B. Precios Hedónicos (MPH): ecuación lineal de pizarra P_i = c + β·terreno + φ·río + δ·riego + ε_i.
       C. Valoración Contingente (MVC): DAP vs. DAA, Referéndum Dicotómico (Bishop & Heberlein 1979),
          curva de aceptación 60 FPS, 5 etapas y 3 secciones de encuesta.
       D. Selector Interactivo de Método Ambiental: Flujograma Dixon & Sherman (1990) + Matriz Barzev (1999).
  3) Integración total en Modo Aprender (Tema 11), Modo Practicar (Retos 9 y 10) y Laboratorio Completo (Tab 12).
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
  .cal-pill:hover {
    border-color: #1D4ED8;
    background: #EFF6FF;
    color: #1D4ED8;
  }
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
    grid-template-columns: 1fr 1.25fr;
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
  }
  .ra2-highlight-row td {
    background: #FEF3C7 !important;
    font-weight: 800;
    color: #78350F !important;
  }
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

  /* Compatibilidad con Modo Aprender Paso 1/2/3 dentro de Panel 12 */
  .wrap.mode-aprender.step-1 #panel-ra2_27nov .ra2-dual,
  .wrap.mode-aprender.step-1 #panel-ra2_27nov .dix-wrap,
  .wrap.mode-aprender.step-1 #panel-ra2_27nov .mvc-info-wrap { display: block; }
  .wrap.mode-aprender.step-2 #panel-ra2_27nov .ra2-dual,
  .wrap.mode-aprender.step-3 #panel-ra2_27nov .ra2-dual,
  .wrap.mode-aprender.step-3 #panel-ra2_27nov .dix-wrap { display: none; }
  .wrap.mode-aprender.step-2 #panel-ra2_27nov .dix-wrap { display: block; }
</style>
"""


JS_EXPANSION_RA2_27NOV = r"""
<script id="js-expansion-ra2-27nov">
(function() {
  if (window.__expansionRa2_27NovActiva) return;
  window.__expansionRa2_27NovActiva = true;

  // ==========================================================================
  // 1. CALENDARIO OFICIAL FDIC26 (ULAGOS VIRTUAL 2026-2SEM) + FECHAS POR CLASE
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
        <span>📅 Cronograma Oficial FDIC26 (2026-2SEM) y Fechas por Clase — Haz clic en un hito para abrir su simulador</span>
        <span style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
          <span class="cal-badge-warn">Aviso Moodle: Venc. Presentación fue 26 Nov 23:59</span>
          <span class="cal-badge-new">Última clase: 27 Nov · RA2</span>
        </span>
      </summary>
      <div class="cal-strip">${pillsHtml}</div>
    `;
    studioBar.parentNode.insertBefore(det, studioBar.nextSibling);
  }

  // ==========================================================================
  // 2. MONTAJE DEL PANEL 12 (CLASE 27 NOV — VALORACIÓN AMBIENTAL RA2 AVANZADA)
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

    <!-- ================= SUB A: MCV ZONAL + PÉRDIDA BIENESTAR ================= -->
    <div id="ra2-sub-mcv" class="ra2-sub active">
      <details class="enun-box" open>
        <summary>
          <span>Método de Costo de Viaje (MCV) — Zonas Concéntricas y Pérdida de Bienestar (Láminas 2–6 · 27 Nov)</span>
          <span class="enun-badge">v_i = φ(CV, ingresos, educación, sustitutos)</span>
        </summary>
        <div class="enun-body">
          El MCV valora áreas naturales con función recreativa observando cómo varían las visitas ante cambios en el costo de traslado.
          <b>Curiosidad de clase (Lámina 4):</b> la <b>Loc. 3</b> paga más costo de viaje (US$ 40) que la <b>Loc. 2</b> (US$ 30), pero registra <b>más visitas</b> (80/1000 vs 70/1000) porque su ingreso promedio es mayor (US$ 1.300 vs US$ 1.100).
          Cuando baja la calidad del parque (derrame petrolero o ruido de carretera), la curva de demanda se desplaza de <b>D<sub>1</sub> a D<sub>2</sub></b> y la pérdida de bienestar es el <b>área sombreada entre ambas curvas</b>.
        </div>
      </details>

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

      <div id="mcv-hilo" class="hilo-box"></div>
      <div id="mcv-fstrip" class="fstrip-grid"></div>

      <div class="ra2-dual">
        <div class="ra2-card">
          <div class="ra2-card-tit">1. Zonas Concéntricas del Parque (Ejemplo Oficial Lámina 4)</div>
          <svg id="svg-mcv-zonas" viewBox="0 0 380 235"></svg>
          <table class="cl-tbl" style="margin-top:6px;">
            <thead><tr><th>Zona</th><th>Tasa Visitación</th><th>CV (US$)</th><th>Ingreso Prom.</th></tr></thead>
            <tbody>
              <tr><td>Loc. 1 (Anillo 1)</td><td>100 / 1.000</td><td>US$ 20</td><td>US$ 1.000</td></tr>
              <tr><td>Loc. 2 (Anillo 2)</td><td>70 / 1.000</td><td>US$ 30</td><td>US$ 1.100</td></tr>
              <tr class="ra2-highlight-row"><td>Loc. 3 (¡Paradoja!)</td><td>80 / 1.000 ▲</td><td>US$ 40 ▲</td><td>US$ 1.300 ★</td></tr>
              <tr><td>Loc. 4 (Anillo 4)</td><td>60 / 1.000</td><td>US$ 50</td><td>US$ 900</td></tr>
            </tbody>
          </table>
        </div>
        <div class="ra2-card">
          <div class="ra2-card-tit">2. Demanda Recreativa (D1 → D2) y Pérdida de Bienestar (Láminas 5–6)</div>
          <svg id="svg-mcv-bienestar" viewBox="0 0 540 340"></svg>
        </div>
      </div>
      <div id="ped-ra2-mcv" class="ped-grid"></div>
      <details class="teo-box">
        <summary>
          <span>Marco Teórico MCV (Guía Metodológica 2002 · Clase 27 Nov)</span>
          <span class="enun-badge">Desplegar teoría de apoyo</span>
        </summary>
        <div class="teo-body">
          <ul>
            <li><b>Principio de mercado sustituto:</b> aunque entrar al parque sea gratis ($0), el visitante revela su valoración mediante el costo de viaje (transporte + costo de oportunidad del tiempo).</li>
            <li><b>Control econométrico obligatorio:</b> la tasa de visitación depende de <b>v<sub>i</sub> = φ(CV, ingresos, nivel educativo, sitios sustitutos)</b>. Por eso Loc. 3 visita más que Loc. 2 pese a estar más lejos: su mayor ingreso desplaza su disposición a viajar.</li>
            <li><b>Pérdida por degradación ambiental:</b> si un derrame o carretera degrada el sitio, la curva rota/cae de D<sub>1</sub> a D<sub>2</sub> al mismo costo p*; la pérdida social exacta es el área entre D<sub>1</sub> y D<sub>2</sub> sobre p*.</li>
          </ul>
        </div>
      </details>
    </div>

    <!-- ================= SUB B: PRECIOS HEDÓNICOS (PIZARRA 27 NOV) ================= -->
    <div id="ra2-sub-hed" class="ra2-sub">
      <details class="enun-box" open>
        <summary>
          <span>Método de Precios Hedónicos (MPH) — Ecuación Lineal de Terrenos (Sala 27 Nov)</span>
          <span class="enun-badge">P_i = c + β·terreno_i + φ·río_i + δ·riego_i + ε_i</span>
        </summary>
        <div class="enun-body">
          Caracteriza un bien de mercado (terreno o vivienda) por sus atributos físicos (superficie, calidad del suelo, infraestructura, transporte) y sus atributos ambientales (acceso a agua, cercanía a río, aire limpio).
          Al estimar la regresión lineal <b>P<sub>i</sub> = c + β·terreno<sub>i</sub> + φ·río<sub>i</sub> + δ·riego<sub>i</sub> + ε<sub>i</sub></b>, los coeficientes <b>φ</b> y <b>δ</b> revelan el <b>precio implícito</b> que el mercado paga por el atributo ambiental.
        </div>
      </details>

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

      <div id="hed-hilo" class="hilo-box"></div>
      <div id="hed-fstrip" class="fstrip-grid"></div>
      <div class="svg-box"><svg id="svg-hedonico" viewBox="0 0 940 270"></svg></div>
      <div id="ped-ra2-hed" class="ped-grid"></div>
      <details class="teo-box">
        <summary>
          <span>Etapas de Aplicación de Precios Hedónicos (Diapositiva 27 Nov)</span>
          <span class="enun-badge">Desplegar teoría de apoyo</span>
        </summary>
        <div class="teo-body">
          <ul>
            <li><b>Etapa 1 — Caracterizar el objeto de estudio:</b> definir valor del terreno, unidades equivalentes de medida, calidad (alta/baja), infraestructura, acceso al agua y cercanía a transporte.</li>
            <li><b>Etapa 2 — Especificar y estimar la ecuación:</b> bajo forma funcional lineal <b>P<sub>i</sub> = c + β·terreno<sub>i</sub> + φ·río<sub>i</sub> + δ·riego<sub>i</sub> + ε<sub>i</sub></b>, la derivada parcial <b>∂P/∂río = φ</b> entrega la disposición marginal a pagar por el atributo ambiental sin necesidad de encuestas hipotéticas.</li>
          </ul>
        </div>
      </details>
    </div>

    <!-- ================= SUB C: VALORACIÓN CONTINGENTE (MVC) ================= -->
    <div id="ra2-sub-mvc" class="ra2-sub">
      <details class="enun-box" open>
        <summary>
          <span>Método de Valoración Contingente (MVC) — DAP vs. DAA y Formato Referéndum (Láminas 7–13 · 27 Nov)</span>
          <span class="enun-badge">Bishop &amp; Heberlein (1979) · Mercados Hipotéticos</span>
        </summary>
        <div class="enun-body">
          Es un <b>enfoque directo</b> basado en encuestas que construye un <b>mercado hipotético</b> cuando no existe precio de mercado ni sustituto (calidad de agua, calidad de aire, paisaje, biodiversidad).
          El formato <b>Referéndum (dicotómico: "Sí" o "No")</b> de Bishop y Heberlein (1979) supera a las repreguntas iterativas porque elimina el sesgo del entrevistador y reduce costos.
        </div>
      </details>

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

      <div id="mvc-hilo" class="hilo-box"></div>
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
      <div id="ped-ra2-mvc" class="ped-grid"></div>
    </div>

    <!-- ================= SUB D: SELECTOR DIXON (1990) + BARZEV (1999) ================= -->
    <div id="ra2-sub-dix" class="ra2-sub">
      <details class="enun-box" open>
        <summary>
          <span>Flujograma de Decisión Ambiental (Dixon &amp; Sherman, 1990) y Matriz de Indicadores (Barzev, 1999)</span>
          <span class="enun-badge">Láminas 14–16 · 27 Nov</span>
        </summary>
        <div class="enun-body">
          En un caso de certamen, ¿cómo saber qué método elegir? Selecciona el tipo de impacto ambiental abajo y el flujograma te indicará el método exacto según <b>Dixon &amp; Sherman (1990)</b> y los indicadores aplicables según <b>Rado Barzev (1999)</b>.
        </div>
      </details>

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

    // Agregar botón 12 a .top-tabs
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

    // Agregar etiquetas de fecha a las pestañas existentes en Modo Lab
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
  }

  // ==========================================================================
  // 3. LÓGICA 60 FPS DE LOS 4 BLOQUES DE LA CLASE DEL 27 DE NOVIEMBRE
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

  // --- BLOQUE A: MCV ZONAL + PÉRDIDA DE BIENESTAR ---
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

    // Excedente del consumidor sobre p*: triángulo = 0.5 * (CV_CP - p*) * v
    const ec1 = 0.5 * (cvCp - pStar) * v1;
    const ec2 = 0.5 * (cvCp - pStar) * v2;
    const dW = ec2 - ec1; // negativo si hay pérdida de bienestar

    document.getElementById("mcv-k-ec1").textContent = "US$ " + fmtInt(ec1);
    document.getElementById("mcv-k-v2").textContent = fmtInt(v2) + " / año";
    document.getElementById("mcv-k-dv").textContent = `ΔVisitas = ${v2 - v1 >= 0 ? "+" : ""}${fmtInt(v2 - v1)}`;
    document.getElementById("mcv-k-dw").textContent = `${dW >= 0 ? "+" : "-"}US$ ${fmtInt(Math.abs(dW))}`;
    document.getElementById("mcv-k-dws").textContent = dW < 0 ? "Pérdida social (D1 → D2)" : (dW > 0 ? "Ganancia por mejora (D1 → D2)" : "Sin cambio de bienestar");
    document.getElementById("mcv-k-ec2").textContent = "US$ " + fmtInt(ec2);

    // Hilo conductor vivo
    const hBox = document.getElementById("mcv-hilo");
    if (hBox) {
      hBox.innerHTML = `
        <div class="hilo-head">
          <span class="hilo-title">Hilo Conductor Vivo — Cómo mide el MCV una pérdida o mejora ambiental</span>
          <span class="hilo-sub">Basado en Láminas 4, 5 y 6 (Clase 27 Nov)</span>
        </div>
        <div class="hilo-steps">
          <div class="hilo-step hs-b"><span class="hilo-conn hc-b">1. Primero, estimamos D1</span>Al observar las visitas desde las 4 zonas concéntricas (controlando por ingreso), obtenemos un excedente recreativo inicial de <b>US$ ${fmtInt(ec1)}/año</b>.</div>
          <div class="hilo-step hs-p"><span class="hilo-conn hc-p">2. Cambia la calidad</span>Ante un impacto ambiental de <b>${chgPct >= 0 ? "+" : ""}${chgPct}%</b>, la demanda pasa de <b>D<sub>1</sub> a D<sub>2</sub></b> y las visitas cambian de <b>${fmtInt(v1)}</b> a <b>${fmtInt(v2)}</b> al mismo costo p* = US$ ${pStar}.</div>
          <div class="hilo-step ${dW < 0 ? 'hs-r' : 'hs-g'}"><span class="hilo-conn ${dW < 0 ? 'hc-r' : 'hc-g'}">3. En consecuencia (ΔW)</span>El área sombreada entre D<sub>1</sub> y D<sub>2</sub> cuantifica exactamente <b>${dW >= 0 ? "+" : "-"}US$ ${fmtInt(Math.abs(dW))}/año</b> de cambio en bienestar social.</div>
        </div>`;
    }

    renderFormulaStrip("mcv-fstrip", [
      {
        step: "PASO 1", lbl: "Función de Visitas por Zona (Lámina 3)", col: "#1D4ED8",
        eq: `v<sub>i</sub> = φ(CV<sub>i</sub>, Ingresos<sub>i</sub>, Educación<sub>i</sub>, Sustitutos<sub>i</sub>)`,
        sub: `Loc. 3: CV = ${vChip("US$ 40", "vc-o")} &gt; Loc. 2 ($30), pero visita ${vChip("80/1000", "vc-g")} por Ingreso = ${vChip("US$ 1.300", "vc-b")}`,
        plain: `Por eso el MCV siempre usa regresión múltiple: si no controlas por ingreso, confundes riqueza con cercanía.`,
        next: `↳ Con las tasas zonales se construye la demanda agregada D1 del Paso 2.`
      },
      {
        step: "PASO 2", lbl: "Excedente Recreativo Inicial (bajo D1)", col: "#7C3AED",
        eq: `EC<sub>1</sub> = ${mFrac("1", "2")} · (CV<sub>CP</sub> − p*) · v<sub>1</sub>`,
        sub: `EC<sub>1</sub> = 0,5 · ($${cvCp} − $${pStar}) · ${fmtInt(v1)} = ${vChip("US$ "+fmtInt(ec1), "vc-p")}`,
        plain: `Mide la disposición a pagar neta por encima del costo de viaje p* que disfrutan los ${fmtInt(v1)} visitantes al año.`,
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

    // SVG 1: Anillos Concéntricos (Lámina 4)
    const svgZ = document.getElementById("svg-mcv-zonas");
    if (svgZ) {
      svgZ.innerHTML = "";
      const cx = 190, cy = 118;
      [34, 60, 86, 110].forEach(rad => {
        el("circle", { cx, cy, r: rad, fill: "none", stroke: "#64748B", "stroke-width": "1.2", "stroke-dasharray": "4,3" }, svgZ);
      });
      el("circle", { cx, cy, r: 15, fill: "#0F172A" }, svgZ);
      const tp = el("text", { x: cx, y: cy - 20, fill: "#0F172A", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, svgZ);
      tp.textContent = "PARQUE";
      const locs = [
        { x: cx + 28, y: cy + 20, lbl: "Loc. 1 ($20 · 100‰)", col: "#1D4ED8" },
        { x: cx - 18, y: cy - 58, lbl: "Loc. 2 ($30 · 70‰)", col: "#475569" },
        { x: cx - 78, y: cy + 36, lbl: "Loc. 3 ($40 · 80‰ ★)", col: "#D97706" },
        { x: cx + 88, y: cy - 66, lbl: "Loc. 4 ($50 · 60‰)", col: "#475569" }
      ];
      locs.forEach(l => {
        el("circle", { cx: l.x, cy: l.y, r: 5.5, fill: l.col, stroke: "#FFF", "stroke-width": "1.4" }, svgZ);
        drawPill(svgZ, l.x, l.y - 12, l.lbl, l.col, "#FFFFFF", "middle", "9.5");
      });
    }

    // SVG 2: Curvas D1 -> D2 y Pérdida de Bienestar (Lámina 6)
    const svgB = document.getElementById("svg-mcv-bienestar");
    if (svgB) {
      svgB.innerHTML = "";
      addDefs(svgB);
      const M = { l: 58, r: 28, t: 26, b: 44 }, W = 540, H = 340;
      const maxV = Math.max(v1, v2, 10000) * 1.25;
      const maxP = cvCp * 1.18;
      const sx = v => M.l + (v / maxV) * (W - M.l - M.r);
      const sy = p => H - M.b - (p / maxP) * (H - M.t - M.b);

      drawAxesPizarra(svgB, M.l, M.t, W - M.r, H - M.b, "Costo de Viaje (US$)", "Visitas / año");

      // Sombreado pérdida/ganancia de bienestar entre D1 y D2 sobre p*
      const polyPts = `${sx(0)},${sy(cvCp)} ${sx(v1)},${sy(pStar)} ${sx(v2)},${sy(pStar)}`;
      el("polygon", {
        points: polyPts,
        fill: dW < 0 ? "rgba(153, 27, 27, 0.34)" : "rgba(5, 150, 105, 0.28)",
        stroke: dW < 0 ? "#991B1B" : "#059669",
        "stroke-width": "1.6"
      }, svgB);

      // Curvas D1 y D2 extendidas hasta el eje X
      const v1Zero = v1 * (cvCp / (cvCp - pStar));
      const v2Zero = v2 * (cvCp / (cvCp - pStar));
      el("line", { x1: sx(0), y1: sy(cvCp), x2: sx(Math.min(maxV, v1Zero)), y2: sy(Math.max(0, cvCp - (cvCp - pStar) * Math.min(maxV, v1Zero) / v1)), stroke: "#1D4ED8", "stroke-width": "2.6" }, svgB);
      if (v2 > 0) {
        el("line", { x1: sx(0), y1: sy(cvCp), x2: sx(Math.min(maxV, v2Zero)), y2: sy(Math.max(0, cvCp - (cvCp - pStar) * Math.min(maxV, v2Zero) / v2)), stroke: dW < 0 ? "#991B1B" : "#059669", "stroke-width": "2.4", "stroke-dasharray": "6,4" }, svgB);
      }

      // Líneas punteadas p*, v1, v2
      el("line", { x1: M.l, y1: sy(pStar), x2: sx(Math.max(v1, v2)), y2: sy(pStar), stroke: "#475569", "stroke-dasharray": "4,3" }, svgB);
      el("line", { x1: sx(v1), y1: sy(pStar), x2: sx(v1), y2: H - M.b, stroke: "#1D4ED8", "stroke-dasharray": "4,3" }, svgB);
      el("line", { x1: sx(v2), y1: sy(pStar), x2: sx(v2), y2: H - M.b, stroke: dW < 0 ? "#991B1B" : "#059669", "stroke-dasharray": "4,3" }, svgB);

      const tPs = el("text", { x: M.l - 7, y: sy(pStar) + 4, fill: "#0F172A", "font-size": "10.5", "font-weight": "800", "text-anchor": "end" }, svgB);
      tPs.textContent = "p* $" + pStar;
      const tCp = el("text", { x: M.l - 7, y: sy(cvCp) + 4, fill: "#1E3A8A", "font-size": "10.2", "font-weight": "800", "text-anchor": "end" }, svgB);
      tCp.textContent = "CV_CP $" + cvCp;
      const tv1 = el("text", { x: sx(v1), y: H - M.b + 16, fill: "#1D4ED8", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, svgB);
      tv1.textContent = "v1 (" + fmtInt(v1) + ")";
      const tv2 = el("text", { x: sx(v2), y: H - M.b + 29, fill: dW < 0 ? "#991B1B" : "#059669", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, svgB);
      tv2.textContent = "v2 (" + fmtInt(v2) + ")";

      drawPill(svgB, sx((v1 + v2) * 0.36), sy(pStar + (cvCp - pStar) * 0.42),
        (dW < 0 ? "Pérdida: -US$ " : "Ganancia: +US$ ") + fmtInt(Math.abs(dW)),
        dW < 0 ? "#991B1B" : "#059669", "#FFFFFF", "middle", "10.5");
      drawPill(svgB, sx(v1) + 18, sy(pStar) - 14, "D1", "#1D4ED8", "#EFF6FF", "start", "10.5");
      if (v2 > 0) drawPill(svgB, sx(v2) - 14, sy(pStar) - 24, "D2", dW < 0 ? "#991B1B" : "#059669", "#FFFFFF", "end", "10.5");

      if (Math.abs(v2 - v1) > 400) {
        drawArrow(svgB, sx(v1), sy(pStar) - 6, sx(v2), sy(pStar) - 6, dW < 0 ? "#DC2626" : "#15803D", dW < 0 ? "arr-red" : "arr-green", "", 0, 0);
      }
    }

    renderPedBox("ped-ra2-mcv",
      `Al desplazarse la demanda recreativa de <b>D<sub>1</sub></b> a <b>D<sub>2</sub></b> (${fmtInt(v1)} → ${fmtInt(v2)} visitas), el bienestar social cambia en <b>${dW >= 0 ? "+" : "-"}US$ ${fmtInt(Math.abs(dW))}/año</b>.`,
      `<b>La Paradoja de Loc. 3 (Lámina 4):</b> aunque está más lejos que Loc. 2 (US$ 40 vs US$ 30), registra más visitas (80‰ vs 70‰) porque su ingreso promedio es US$ 1.300. Si omites el ingreso en la regresión, obtendrías una pendiente errada de la demanda.`,
      `<b>Defensa en prueba RA2:</b> recuerda que el MCV solo captura <b>Valor de Uso Recreativo</b> (visitantes reales). Si un parque tiene especies endémicas valoradas por gente que nunca irá, necesitas complementarlo con <b>Valoración Contingente (MVC)</b>.`
    );
  };

  // --- BLOQUE B: PRECIOS HEDÓNICOS (ECUACIÓN DE PIZARRA 27 NOV) ---
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

    const vTer = beta * ter;
    const vFis = cVal + vTer;
    const vAmb = phi + delta;
    const pTot = vFis + vAmb;

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
          <div class="hilo-step hs-g"><span class="hilo-conn hc-g">2. Atributos ambientales</span>El acceso/orilla a río suma <b>+$${fmtDec(phi,1)} MM (φ)</b> y el acceso a agua/riego suma <b>+$${fmtDec(delta,1)} MM (δ)</b>: <b>$${fmtDec(vAmb,1)} MM</b> de valor ambiental implícito.</div>
          <div class="hilo-step hs-p"><span class="hilo-conn hc-p">3. Precio de mercado</span>El mercado capitaliza ambos bloques en <b>P<sub>i</sub> = $${fmtDec(pTot,1)} MM</b>; si se contamina el río (φ → 0), el predio pierde al instante <b>$${fmtDec(phi,1)} MM</b>.</div>
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

    renderPedBox("ped-ra2-hed",
      `Del precio estimado del predio (<b>$${fmtDec(pTot,1)} MM</b>), un <b>${fmtDec(vAmb/pTot*100,1)}% ($${fmtDec(vAmb,1)} MM)</b> corresponde directamente a atributos ambientales (río + agua/riego).`,
      `<b>Ventaja clave frente a encuestas:</b> Precios Hedónicos usa <b>preferencias reveladas</b> en transacciones reales de compraventa, por lo que no sufre sesgo hipotético; su requisito es contar con una base de datos robusta de propiedades comparables.`,
      `<b>Pregunta típica de examen:</b> si te piden valorar el impacto de malos olores de un relleno sanitario o ruido de una carretera sobre viviendas cercanas, el método de mercado sustituto indicado es <b>Precios Hedónicos</b>.`
    );
  };

  // --- BLOQUE C: VALORACIÓN CONTINGENTE (MVC — DAP VS DAA + REFERÉNDUM) ---
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

    // Curva logística de Referéndum (Bishop & Heberlein 1979)
    // En DAP: mayor monto -> menor prob de decir "Sí"; en DAA: mayor compensación -> mayor prob de aceptar "Sí"
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

    renderPedBox("ped-ra2-mvc",
      `Bajo el escenario <b>${esc.toUpperCase()}</b> con mediana de $${fmtInt(med)}/mes, el beneficio/daño agregado para ${fmtInt(hog)} hogares es <b>$${fmtDec(valAnualMM,1)} MM/año</b>.`,
      `<b>¿Por qué la DAA suele ser mayor que la DAP?</b> Porque la DAP está acotada por el ingreso del hogar (no puedes pagar más de lo que tienes), mientras que la DAA por perder un bien ambiental (ej. un río limpio) no tiene techo presupuestario y sufre aversión a la pérdida.`,
      `<b>Pregunta fija de prueba:</b> ¿Por qué Bishop y Heberlein (1979) propusieron el formato <b>Referéndum (dicotómico Sí/No)</b>? Porque elimina el sesgo de las repreguntas iterativas y reduce el costo de aplicación de la encuesta.`
    );
  };

  // --- BLOQUE D: SELECTOR DIXON & SHERMAN (1990) + MATRIZ BARZEV (1999) ---
  const DIXON_MAP = {
    prod_ok: {
      ruta: "Cambios en Productividad Medibles (SÍ) → Precios de mercado NO distorsionados (SÍ)",
      metodos: "Enfoque de Cambios en la Productividad (Precios de Mercado — PM)",
      ejemplos: "Pérdida de cosecha agrícola, baja en captura pesquera o incremento de producción maderera con precios competitivos.",
      barzev: [["Actividad Primaria / Secundaria", "Industria / Agricultura", "PM (Precios de Mercado)"], ["Ingreso Familiar / Inversiones", "Medio Socioeconómico", "PM (Precios de Mercado)"]]
    },
    prod_dist: {
      ruta: "Cambios en Productividad Medibles (SÍ) → Precios de mercado NO distorsionados (NO)",
      metodos: "Mercados Sustitutos y Precios Sombra para Cambios en la Productividad",
      ejemplos: "Producción agrícola o pesquera con subsidios, impuestos o aranceles que distorsionan el precio privado.",
      barzev: [["Insumos / Bienes Transables", "Distorsión arancel/impuesto", "PM ajustado a Precios Sombra (SNI)"], ["Suelo Productivo", "Pérdida de suelo por erosión", "VC / CO (Costo de Oportunidad)"]]
    },
    habitat: {
      ruta: "Cambios en la Calidad Ambiental → Hábitat",
      metodos: "Costo de Oportunidad (CO) · Costo de Reposición (CR) · Valor de la Tierra (Hedónicos)",
      ejemplos: "Alteración de bosques, humedales, pérdida de suelo por erosión o relocalización de ecosistemas.",
      barzev: [["Suelo (Físico Inerte)", "Pérdida de suelo por erosión", "VC, CO (Costo de Oportunidad)"], ["Infraestructura / Viviendas / Puentes", "Daños a medio urbano construido", "CR (Reposición), CP (Preventivos)"]]
    },
    aire_agua: {
      ruta: "Cambios en la Calidad Ambiental → Calidad de Aire y Agua",
      metodos: "Costo-Eficiencia de Prevención · Gastos Preventivos (CP) · Costos de Reposición (CR)",
      ejemplos: "Polvo, humo, aserrín, gases, malos olores, ruido, déficit de agua potable o plantas de tratamiento.",
      barzev: [["Aire (Físico Inerte)", "Polvo, humo, aserrín, gases, olores, ruido", "VC (Valoración Contingente)"], ["Agua (Abastecimiento)", "Déficit anual de agua potable", "PM, CR (Reposición)"], ["Plantas Tratamiento Agua / Basura", "Infraestructura sanitaria", "CR, CP (Preventivos / Evitados)"]]
    },
    salud: {
      ruta: "Cambios en la Calidad Ambiental → Efectos en la Salud (Morbilidad / Mortalidad)",
      metodos: "Morbilidad: Pérdida de ingresos/ahorro + Costos Médicos (CS) · Mortalidad: Costo-Eficiencia de Prevención + Capital Humano (VVE)",
      ejemplos: "Contaminación hídrica que provoca enfermedades gastrointestinales o contaminación del aire (MP2,5) con hospitalizaciones.",
      barzev: [["Agua (Contaminación)", "Contaminación del agua / costos de salud", "CS (Costos de Salud)"], ["Centros Educ. y Salud", "Centros dañados o sobrecargados", "CR, CP / CS"]]
    },
    recreacion: {
      ruta: "Cambios en la Calidad Ambiental → Recreación",
      metodos: "Método del Costo de Viaje (MCV) · Valoración Contingente (VC)",
      ejemplos: "Parques nacionales, zonas verdes, balnearios de ríos, potencial turístico y esparcimiento familiar.",
      barzev: [["Desarrollo Turístico", "Potencial turístico / Balnearios de ríos", "VC / MCV (Costo de Viaje)"], ["Zonas Verdes y Parques", "Medio físico perceptivo", "MCV / VC"]]
    },
    estetico: {
      ruta: "Cambios en la Calidad Ambiental → Bienes Estéticos, Biodiversidad, Culturales e Históricos",
      metodos: "Valoración Contingente (VC — única capaz de capturar Valor de Existencia / No Uso)",
      ejemplos: "Paisaje natural y urbano, monumentos históricos, especies amenazadas y patrimonio cultural.",
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
    const box = document.getElementById("dix-res-box");
    if (box) {
      box.innerHTML =
        `<div style="font-size:11px;font-weight:800;color:#065F46;text-transform:uppercase;">Ruta Dixon &amp; Sherman (1990)</div>` +
        `<div style="margin:3px 0;"><b>Camino:</b> ${d.ruta}</div>` +
        `<div style="margin:3px 0;"><b>Métodos recomendados:</b> <span style="color:#1E3A8A;font-weight:800;">${d.metodos}</span></div>` +
        `<div><b>Casos de aplicación:</b> ${d.ejemplos}</div>`;
    }
    const tBox = document.getElementById("dix-barzev-tbl");
    if (tBox) {
      const rows = d.barzev.map(r => `<tr><td>${r[0]}</td><td style="text-align:left;font-family:inherit;">${r[1]}</td><td style="text-align:center;font-weight:800;color:#1E3A8A;">${r[2]}</td></tr>`).join("");
      tBox.innerHTML =
        `<table class="cl-tbl"><thead><tr><th>Categoría / Indicador (Barzev 1999)</th><th>Elemento Ambiental Evaluado</th><th>Código Método</th></tr></thead><tbody>${rows}</tbody></table>` +
        `<div style="font-size:10.8px;color:#475569;margin-top:6px;"><b>Siglas Barzev:</b> <b>VC</b>=Valoración Contingente · <b>CO</b>=Costo Oportunidad · <b>CR</b>=Costo Reposición/Reubicación · <b>CS</b>=Costos de Salud · <b>PM</b>=Precios de Mercado · <b>CP</b>=Costos Preventivos y Evitados.</div>`;
    }
    renderPedBox("ped-ra2-dix",
      `Para <b>${d.ruta}</b>, la literatura oficial de clase recomienda aplicar <b>${d.metodos}</b>.`,
      `<b>Regla mnemotécnica del Flujograma Dixon (1990):</b> pregunta primero si el impacto altera la producción física vendible (izq. del árbol). Si NO, pasa a la derecha (calidad ambiental) y busca el casillero exacto: Salud → CS/Capital Humano; Recreación → MCV; Paisaje/Biodiversidad → solo VC.`,
      `En la matriz de Barzev (1999), toda infraestructura dañada (viviendas, puentes, carreteras, plantas de agua/basura) se valora vía <b>CR (Reposición)</b> o <b>CP (Preventivos/Evitados)</b>.`
    );
  };

  // ==========================================================================
  // 4. INTEGRACIÓN CON STUDIO MODES (APRENDER + PRACTICAR + LAB)
  // ==========================================================================
  function integrarConStudio() {
    // A) Sumar Tema 11 a LEARN_TOPICS y actualizar el dropdown
    if (Array.isArray(LEARN_TOPICS) && !LEARN_TOPICS.some(t => t.id === "t_ra2_27nov")) {
      // Agregar etiquetas de fecha a temas clave existentes
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
        s1: "<b>Clase 27 de noviembre:</b> Explora los 4 bloques de valoración ambiental con sus gráficos a 60 FPS: <b>A)</b> Anillos zonales y pérdida de bienestar (D<sub>1</sub>→D<sub>2</sub>) en Costo de Viaje; <b>B)</b> Ecuación de Precios Hedónicos de terrenos; <b>C)</b> Curva Referéndum DAP/DAA en Valoración Contingente; <b>D)</b> Flujograma de Dixon (1990) + Matriz Barzev (1999).",
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

    // B) Sumar 2 nuevos Retos Activos (Reto 9 y Reto 10) a PRAC_RETOS
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
        }
      );
      if (typeof saveStudioProg === "function") saveStudioProg();
    }

    // C) Envolver openTab y activatePanelClean para renderizar Panel 12 al abrirlo
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
