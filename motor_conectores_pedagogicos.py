# -*- coding: utf-8 -*-
"""
motor_conectores_pedagogicos.py — CAPA DE FLUIDEZ NARRATIVA Y CONECTORES VIVOS (60 FPS)
Módulo plug-and-play para PROYECTOS-2026 (ULagos FDIC26).
Inyecta sobre `HTML_SIMULADOR_FLUIDO` (sin alterar los cálculos base):
  1) Franja de "Hilo Conductor Vivo" (3 pasos con conectores causales dinámicos) en los simuladores clave:
     Casos de Clase (Ej. 1 y Ej. 2), Mercado de la Leche, Transporte/Externalidades,
     Elasticidades Extremas, Puente VAN->VANS, Horno de Pan, Agua 10 Años y Ambiental RA2.
  2) Badges PASO 1 -> PASO 2 -> PASO 3, traducción "En simple" y micro-conectores al pie.
  3) Cableado visual por color heredado y puente explícito de partidas en Casos de Clase.
"""


CSS_CONECTORES_PEDAGOGICOS = r"""
<style id="css-conectores-pedagogicos">
  .hilo-box {
    background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
    border: 1px solid #BFDBFE;
    border-left: 4.5px solid #1D4ED8;
    border-radius: 8px;
    padding: 10px 13px;
    margin: 10px 0 8px 0;
  }
  .hilo-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    flex-wrap: wrap;
  }
  .hilo-title {
    font-size: 11.4px;
    font-weight: 800;
    color: #1E3A8A;
    text-transform: uppercase;
    letter-spacing: 0.35px;
  }
  .hilo-sub {
    font-size: 11px;
    color: #475569;
    font-weight: 600;
  }
  .hilo-steps {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
  }
  @media (max-width: 860px) {
    .hilo-steps { grid-template-columns: 1fr; }
  }
  .hilo-step {
    background: #FFFFFF;
    border: 1px solid #DBEAFE;
    border-top: 3px solid #1D4ED8;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 11.8px;
    line-height: 1.46;
    color: #1E293B;
    position: relative;
  }
  .hilo-step.hs-p { border-top-color: #7C3AED; }
  .hilo-step.hs-g { border-top-color: #059669; }
  .hilo-step.hs-b { border-top-color: #1D4ED8; }
  .hilo-step.hs-r { border-top-color: #DC2626; }
  .hilo-step.hs-o { border-top-color: #EA580C; }
  .hilo-conn {
    display: inline-block;
    font-size: 10.2px;
    font-weight: 800;
    padding: 1.5px 7px;
    border-radius: 10px;
    margin-right: 5px;
    margin-bottom: 3px;
    vertical-align: middle;
  }
  .hc-p { background: #F3E8FF; color: #6B21A8; }
  .hc-g { background: #DCFCE7; color: #166534; }
  .hc-b { background: #DBEAFE; color: #1E40AF; }
  .hc-r { background: #FEE2E2; color: #991B1B; }
  .hc-o { background: #FFEDD5; color: #9A3412; }

  .step-badge {
    display: inline-block;
    font-size: 9.8px;
    font-weight: 800;
    color: #FFFFFF;
    background: #1E3A8A;
    padding: 2px 7px;
    border-radius: 10px;
    margin-right: 6px;
    letter-spacing: 0.3px;
    vertical-align: middle;
  }
  .fstrip-plain {
    margin-top: 7px;
    padding: 5px 8px;
    background: #F8FAFC;
    border-left: 2.5px solid #94A3B8;
    border-radius: 0 4px 4px 0;
    font-size: 11.4px;
    line-height: 1.4;
    color: #334155;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
  }
  .fstrip-next {
    margin-top: 7px;
    padding-top: 6px;
    border-top: 1px dashed #CBD5E1;
    font-size: 11.3px;
    font-weight: 700;
    line-height: 1.38;
    color: #1E3A8A;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
  }
  .fstrip-next.nx-ok { color: #15803D; }
  .fstrip-next.nx-warn { color: #B45309; }
  .fstrip-next.nx-bad { color: #B91C1C; }

  /* Integración limpia con Modo Aprender (visible en Paso 1, Paso 2 y Laboratorio Completo) */
  .wrap.mode-aprender .panel .hilo-box { display: block; }
  .wrap.mode-aprender.step-3 .panel .hilo-box { display: none; }
</style>
"""


JS_CONECTORES_PEDAGOGICOS = r"""
<script id="js-conectores-pedagogicos">
(function() {
  if (window.__conectoresPedagogicosActivos) return;
  window.__conectoresPedagogicosActivos = true;

  let _suppressFstripId = null;

  function ensureHiloBox(hiloId, beforeId) {
    let box = document.getElementById(hiloId);
    if (box) return box;
    const ref = document.getElementById(beforeId);
    if (!ref || !ref.parentNode) return null;
    box = document.createElement("div");
    box.id = hiloId;
    box.className = "hilo-box";
    ref.parentNode.insertBefore(box, ref);
    return box;
  }

  function renderHilo(hiloId, beforeId, titulo, subtitulo, steps) {
    const box = ensureHiloBox(hiloId, beforeId);
    if (!box) return;
    const stepsHtml = steps.map(s => `
      <div class="hilo-step ${s.cls || 'hs-b'}">
        <span class="hilo-conn ${s.cCls || 'hc-b'}">${s.conn}</span>${s.html}
      </div>
    `).join("");
    box.innerHTML = `
      <div class="hilo-head">
        <span class="hilo-title">${titulo}</span>
        <span class="hilo-sub">${subtitulo}</span>
      </div>
      <div class="hilo-steps">${stepsHtml}</div>
    `;
  }

  // Enriquecer renderFormulaStrip con badges PASO N, "En simple" y micro-conector inferior
  window.renderFormulaStrip = function(id, cards) {
    if (_suppressFstripId && id === _suppressFstripId) return;
    const box = document.getElementById(id);
    if (!box) return;
    box.innerHTML = cards.map((c, idx) => {
      const k = `${id}_${idx}`;
      const isOn = !!fstripXrayState[k];
      const col = c.col || "#1E3A8A";
      const badgeHtml = c.step ? `<span class="step-badge" style="background:${col};">${c.step}</span>` : "";
      const plainHtml = c.plain ? `<div class="fstrip-plain"><b>En simple:</b> ${c.plain}</div>` : "";
      const noteHtml = c.note ? `<div class="fstrip-note">${c.note}</div>` : "";
      const nextHtml = c.next ? `<div class="fstrip-next ${c.nextCls || ''}">${c.next}</div>` : "";
      return `
        <div class="fstrip-card${isOn ? ' xray-on' : ''}" style="border-left-color:${col};">
          <div class="fstrip-head" onclick="toggleXrayCard('${k}', this)" title="Clic aquí para alternar Modo Rayos X">
            <span class="fstrip-lbl" style="color:${col};">${badgeHtml}${c.lbl}</span>
            <span class="xray-pill">${isOn ? "Rayos X: ON ⇄" : "f(x) → 123"}</span>
          </div>
          <div class="fstrip-eq">${c.eq}</div>
          <div class="fstrip-sub">${c.sub || ""}</div>
          ${plainHtml}
          ${noteHtml}
          ${nextHtml}
        </div>`;
    }).join("");
  };

  // ==========================================================================
  // 1. CASO DE CLASE EJERCICIO 1 — TABLA SOCIAL + PERPETUIDAD ($503,3M)
  // ==========================================================================
  const _origDrawCl1 = window.drawClaseEj1;
  if (typeof _origDrawCl1 === "function") {
    window.drawClaseEj1 = function(...args) {
      _suppressFstripId = "cl1-fstrip";
      let ret;
      try { ret = _origDrawCl1.apply(this, args); } finally { _suppressFstripId = null; }

      const ipMM = +document.getElementById("cl1-ip").value;
      const cpU = +document.getElementById("cl1-cp").value;
      const rPct = +document.getElementById("cl1-r").value, r = rPct / 100;
      const fcsd = +document.getElementById("cl1-div").value;
      const arPct = +document.getElementById("cl1-ar").value, ar = arPct / 100;
      const iva = 0.19, ip = ipMM * 1e6;

      const fImp = fcsd / ((1 + iva) * (1 + ar));
      const fNac = 1 / (1 + iva);
      const fInt = cl1State.intSocial ? fNac : 0.0;

      const isTot = ip * (
        0.07 * cl1State.moc + 0.09 * cl1State.mosc + 0.17 * cl1State.monc +
        0.25 * fImp + (0.15 + 0.12) * fNac + 0.05 * fInt
      );
      const csImpU = cpU * 0.47 * fImp;
      const csMoU  = cpU * (0.08 * cl1State.moc + 0.10 * cl1State.mosc + 0.05 * cl1State.monc);
      const csNacU = cpU * ((0.15 + 0.07) * fNac + 0.03 * fInt);
      const csUnit = csImpU + csMoU + csNacU;

      const q0 = 100000, q1 = 250000, p0 = 2000, p1 = 100;
      const ad = (q1 - q0) * (p0 + p1) / 2;
      const lr = q0 * csUnit;
      const vsp = ad + lr;
      const vpVsp = vsp / r;
      const vans = -isTot + vpVsp;

      const isStr = "$" + fmtDec(isTot / 1e6, 2) + "M";
      const csStr = "$" + fmtDec(csUnit, 2) + "/u";
      const vspStr = "$" + fmtDec(vsp / 1e6, 2) + "M/año";
      const vansStr = (vans >= 0 ? "+" : "-") + "$" + fmtDec(Math.abs(vans) / 1e6, 2) + "M";

      renderHilo(
        "cl1-hilo", "cl1-fstrip",
        "Hilo Conductor Vivo — Lee el ejercicio en 3 pasos conectados",
        "Los colores de cada resultado se heredan hacia la siguiente fórmula",
        [
          {
            cls: "hs-p", cCls: "hc-p", conn: "1. Primero, limpiamos precios",
            html: `Como el Estado excluye IVA, arancel y depreciación ($0), la inversión cae de <b>$${fmtInt(ipMM)}M</b> a ${vChip(isStr, "vc-b")} y el costo operativo baja de <b>$${fmtInt(cpU)}</b> a ${vChip(csStr, "vc-p")}.`
          },
          {
            cls: "hs-g", cCls: "hc-g", conn: "2. Con ese costo social",
            html: `Valoramos lo que gana el país cada año: los 150k usuarios nuevos aportan <b>$${fmtDec(ad/1e6,2)}M</b> (AD), <b>mientras que</b> producir más barato los 100k antiguos libera <b>$${fmtDec(lr/1e6,2)}M</b> (LR), sumando ${vChip(vspStr, "vc-g")}.`
          },
          {
            cls: vans >= 0 ? "hs-b" : "hs-r", cCls: vans >= 0 ? "hc-b" : "hc-r",
            conn: vans >= 0 ? "3. En consecuencia" : "3. Sin embargo",
            html: vans >= 0
              ? `Al descontar ${vChip(vspStr, "vc-g")} en perpetuidad al <b>${fmtDec(rPct,1)}%</b> ($${fmtDec(vpVsp/1e6,2)}M) y restar ${vChip(isStr, "vc-b")}, obtenemos <b>VANS = ${vansStr}</b>: conviene ejecutarlo.`
              : `Al descontar ${vChip(vspStr, "vc-g")} al <b>${fmtDec(rPct,1)}%</b> ($${fmtDec(vpVsp/1e6,2)}M), el beneficio ya no cubre ${vChip(isStr, "vc-b")} (<b>VANS = ${vansStr}</b>): la sociedad perdería riqueza.`
          }
        ]
      );

      renderFormulaStrip("cl1-fstrip", [
        {
          step: "PASO 1", lbl: "Limpiar Precios (Importados + Ponderado)", col: "#7C3AED",
          eq: `F<sub>imp</sub> = ${mFrac('<span class="sym-p">R* / R</span>', '(1 + IVA)(1 + <span class="sym-o">t<sub>a</sub></span>)')} &nbsp;⇒&nbsp; CS = ∑(w<sub>i</sub>·CP·FC<sub>i</sub>)`,
          sub: `F<sub>imp</sub> = ${mFrac(eChip(fmtDec(fcsd,2),fcsd,"cl1_div","0.01","vc-p","Factor Divisa R*/R"), "1,19·(1+" + eChip(fmtDec(arPct,1)+"%",arPct,"cl1_ar","1","vc-o","Arancel (%)") + ")")} = <b>${fmtDec(fImp,4)}</b> ⇒ CS = ${vChip(csStr, "vc-p", "Costo Social Unitario ponderado")}`,
          plain: `Sobre ${eChip("$"+fmtInt(cpU),cpU,"cl1_cp","50","vc-b","Costo Privado Unitario")}/u sumamos: Importados 47% ($${fmtDec(csImpU,2)}) + MO 23% ($${fmtDec(csMoU,2)}) + Nac./Otros ($${fmtDec(csNacU,2)}) + Dep. 5% ($0) = <b>$${fmtDec(csUnit,2)}/u</b>.`,
          next: `↳ Con este Costo Social (${csStr}) pasamos al Paso 2 para valorar los recursos liberados (LR).`
        },
        {
          step: "PASO 2", lbl: "Medir Beneficio Anual (VSP = AD + LR)", col: "#059669",
          eq: `VSP = (q<sub>1</sub>−q<sub>0</sub>)·${mFrac("P<sub>0</sub>+P<sub>1</sub>","2")} + q<sub>0</sub>·<span class="sym-p">CS</span>`,
          sub: `VSP = 150k·$1.050 + 100k·${vChip("$"+fmtDec(csUnit,2), "vc-p", "Heredado del Paso 1")} = ${rChip(vspStr)}`,
          plain: `Suma lo que valoran los 150k nuevos viajes (<b>AD = $${fmtDec(ad/1e6,2)}M</b>) <b>más</b> los recursos ahorrados en los 100k antiguos (<b>LR = $${fmtDec(lr/1e6,2)}M</b>).`,
          next: `↳ Estos ${vspStr} suben ahora al numerador del Paso 3 como flujo perpetuo.`
        },
        {
          step: "PASO 3", lbl: "Evaluar Conveniencia (VANS Perpetuo)", col: "#1D4ED8",
          eq: `VANS = −<span class="sym-b">I<sub>S</sub></span> + ${mFrac('<span class="sym-t">VSP</span>', '<span class="sym-r">r</span>')}`,
          sub: `VANS = −${vChip(isStr, "vc-b", "Inversión Social corregida")} + ${mFrac(vChip("$"+fmtDec(vsp/1e6,2)+"M", "vc-g", "Heredado del Paso 2"), eChip(fmtDec(rPct,1)+"%",rPct,"cl1_r","0.5","vc-r","Tasa de descuento r (%)"))} = ${rChip(vansStr, vans < 0)}`,
          plain: `Valor hoy de recibir $${fmtDec(vsp/1e6,2)}M todos los años ($${fmtDec(vpVsp/1e6,2)}M) <b>menos</b> el sacrificio inicial de inversión (${isStr} desde IP ${eChip("$"+fmtInt(ipMM)+"M",ipMM,"cl1_ip","100","vc-b","Inversión Privada IP")}).`,
          next: vans >= 0
            ? `↳ Por lo tanto, al ser positivo (${vansStr}), el proyecto crea riqueza neta para el país.`
            : `↳ Sin embargo, al ser negativo (${vansStr}), conviene rechazar o revisar costos/tasa.`,
          nextCls: vans >= 0 ? "nx-ok" : "nx-bad"
        }
      ]);
      return ret;
    };
  }

  // ==========================================================================
  // 2. CASO DE CLASE EJERCICIO 2 — SALMÓN (SUSTITUCIÓN IMPORTACIONES + SUBSIDIO)
  // ==========================================================================
  const _origDrawCl2 = window.drawClaseEj2;
  if (typeof _origDrawCl2 === "function") {
    window.drawClaseEj2 = function(...args) {
      _suppressFstripId = "cl2-fstrip";
      let ret;
      try { ret = _origDrawCl2.apply(this, args); } finally { _suppressFstripId = null; }

      const pCif = +document.getElementById("cl2-cif").value;
      const pInt = +document.getElementById("cl2-pin").value;
      const qTon = +document.getElementById("cl2-q").value, qKg = qTon * 1000;
      const arPct = +document.getElementById("cl2-ar").value, ar = arPct / 100;
      const rpPct = +document.getElementById("cl2-rp").value, rp = rpPct / 100;
      const tsd = 0.055, n = 40, iva = 0.19, moc = 0.97, monc = 0.91, fcsd = 1.00;

      const invAfSoc = 1000000 / ((1 + iva) * (1 + ar)) * fcsd;
      const isTot = invAfSoc + 400000 * moc;
      const csImp = 100 / ((1 + iva) * (1 + ar)) * fcsd;
      const csKg = (100 / (1 + iva)) + csImp + (50 * moc) + (150 * monc);
      const vspAnual = qKg * pCif * fcsd;
      const csAnual = qKg * csKg;
      const bnSoc = vspAnual - csAnual;
      const pvBnSoc = bnSoc * ((1 - Math.pow(1 + tsd, -n)) / tsd);
      const vans = -isTot + pvBnSoc;

      const invAfPrivNeto = 1000000 / (1 + iva);
      const invPrivNeto = invAfPrivNeto + 400000;
      const depAnual = invAfPrivNeto / n;
      const uaiPriv = qKg * ((pInt / (1 + iva)) - ((200 / (1 + iva)) + 200)) - depAnual;
      const fcPrivAnual = (uaiPriv - (uaiPriv > 0 ? uaiPriv * 0.27 : 0)) + depAnual;
      const vanPriv = -invPrivNeto + fcPrivAnual * ((1 - Math.pow(1 + rp, -n)) / rp);

      const isStr = "US$ " + fmtInt(isTot);
      const csKgStr = "US$ " + fmtDec(csKg, 2) + "/kg";
      const bnStr = (bnSoc >= 0 ? "" : "-") + "US$ " + fmtInt(Math.abs(bnSoc)) + "/año";
      const vansStr = (vans >= 0 ? "+" : "-") + "US$ " + fmtInt(Math.abs(vans));
      const vpStr = (vanPriv >= 0 ? "+" : "-") + "US$ " + fmtInt(Math.abs(vanPriv));

      let paso3Conn = "3. En consecuencia (Subsidio)";
      let paso3Cls = "hs-g", paso3cCls = "hc-g", paso3Txt = "";
      if (vanPriv >= 0 && vans > 0) {
        paso3Txt = `Traer ${vChip(bnStr, "vc-p")} por 40 años al 5,5% y restar ${vChip(isStr, "vc-b")} da <b>VANS = ${vansStr}</b>; <b>sin embargo</b>, como el privado ya gana <b>${vpStr}</b> (Cuadrante I), el Estado aporta <b>US$ 0</b>.`;
      } else if (vanPriv < 0 && vans > 0) {
        paso3Conn = "3. Por ello (Subsidio SÍ)";
        paso3Cls = "hs-o"; paso3cCls = "hc-o";
        paso3Txt = `Aunque el país gana <b>VANS = ${vansStr}</b>, el privado pierde <b>${vpStr}</b> (Cuadrante II); <b>en consecuencia</b>, el Estado SÍ justifica subsidiar mínimo <b>US$ ${fmtInt(Math.abs(vanPriv))}</b> (tope VANS).`;
      } else {
        paso3Conn = "3. Por el contrario (Rechazar)";
        paso3Cls = "hs-r"; paso3cCls = "hc-r";
        paso3Txt = `Al descontar 40 años al 5,5% y restar ${vChip(isStr, "vc-b")}, resulta <b>VANS = ${vansStr}</b>; <b>por lo tanto</b>, el proyecto destruye valor social y no debe financiarse.`;
      }

      renderHilo(
        "cl2-hilo", "cl2-fstrip",
        "Hilo Conductor Vivo — Sustitución de Importaciones y Decisión de Subsidio (SNI 2026)",
        "Sigue el paso a paso antes de responder si el Estado debe aportar dinero",
        [
          {
            cls: "hs-b", cCls: "hc-b", conn: "1. Primero, precios SNI 2026",
            html: `Limpiamos IVA (19%) y arancel (<b>${fmtDec(arPct,1)}%</b>) y aplicamos MOC 0,97 / MONC 0,91: la inversión pasa a ${vChip(isStr, "vc-b")} y cada kilo producido cuesta socialmente ${vChip(csKgStr, "vc-t")}.`
          },
          {
            cls: "hs-p", cCls: "hc-p", conn: "2. Luego, ahorro de divisas",
            html: `Como ${fmtDec(qTon,1)} ton ≤ 10 ton importadas, cada kilo ahorra <b>US$ ${fmtInt(pCif)} CIF</b> (VSP = US$ ${fmtInt(vspAnual)}/año), <b>dejando un beneficio neto anual</b> de ${vChip(bnStr, "vc-p")}.`
          },
          { cls: paso3Cls, cCls: paso3cCls, conn: paso3Conn, html: paso3Txt }
        ]
      );

      renderFormulaStrip("cl2-fstrip", [
        {
          step: "PASO 1", lbl: "Inversión y Costo Social SNI 2026", col: "#1D4ED8",
          eq: `I<sub>S</sub> = ${mFrac("1.000.000", '(1,19)(1+<span class="sym-o">t<sub>a</sub></span>)')} + 400.000·0,97`,
          sub: `I<sub>S</sub> = ${mFrac("1.000.000", "1,19·(1+" + eChip(fmtDec(arPct,1)+"%",arPct,"cl2_ar","0.5","vc-o","Arancel efectivo (%)") + ")")} + $388.000 = ${vChip(isStr, "vc-b")}`,
          plain: `Y cada kilo operado suma: Nac. $84,03 + Imp. $${fmtDec(csImp,2)} + MOC $48,50 + MONC $136,50 = ${vChip(csKgStr, "vc-t")}.`,
          next: `↳ Con ${csKgStr} vamos al Paso 2 para restarlo al ahorro de divisas CIF.`
        },
        {
          step: "PASO 2", lbl: "Margen Social Anual (BN = VSP − CS)", col: "#7C3AED",
          eq: `BN = <span class="sym-t">Q</span> · (<span class="sym-b">P<sub>CIF</sub></span> − <span class="sym-p">CS<sub>kg</sub></span>)`,
          sub: `BN = ${eChip(fmtDec(qTon,1)+"t",qTon,"cl2_q","0.5","vc-t","Producción anual (ton)")} · (${eChip("$"+fmtInt(pCif),pCif,"cl2_cif","10","vc-b","Precio CIF (US$/kg)")} − ${vChip("$"+fmtDec(csKg,2), "vc-t", "Heredado del Paso 1")}) = ${vChip(bnStr, "vc-p")}`,
          plain: `Ahorramos <b>US$ ${fmtInt(vspAnual)}/año</b> en divisas de importación <b>menos</b> <b>US$ ${fmtInt(csAnual)}/año</b> de recursos locales usados.`,
          next: `↳ Este flujo anual (${bnStr}) se actualiza por 40 años al 5,5% en el Paso 3.`
        },
        {
          step: "PASO 3", lbl: "VANS (40a · 5,5%) vs. Subsidio Estatal", col: "#15803D",
          eq: `VANS = −<span class="sym-b">I<sub>S</sub></span> + <span class="sym-p">BN</span> · ${mFrac("1 − (1,055)<sup>−40</sup>", "0,055")}`,
          sub: `VANS = −${vChip(isStr, "vc-b", "Heredado del Paso 1")} + ${vChip("$"+fmtInt(pvBnSoc), "vc-p", "Valor actual 40a de BN")} = ${rChip(vansStr, vans < 0)}`,
          plain: `Comparamos contra el privado (P<sub>int</sub>=${eChip("$"+fmtInt(pInt),pInt,"cl2_pin","5","vc-o","Precio venta interno")} · r<sub>p</sub>=${eChip(fmtDec(rpPct,0)+"%",rpPct,"cl2_rp","1","vc-r","Tasa privada")} ⇒ <b>VAN<sub>P</sub> = ${vpStr}</b>).`,
          next: vanPriv >= 0 && vans > 0
            ? `↳ En consecuencia (Cuadrante I): el privado invierte solo ⇒ Aporte Estatal = US$ 0.`
            : (vanPriv < 0 && vans > 0
              ? `↳ Por lo tanto (Cuadrante II): conviene subsidiar al menos US$ ${fmtInt(Math.abs(vanPriv))} (tope VANS).`
              : `↳ En consecuencia: VANS ≤ 0, rechazar financiamiento público.`),
          nextCls: vanPriv >= 0 && vans > 0 ? "nx-ok" : (vanPriv < 0 && vans > 0 ? "nx-warn" : "nx-bad")
        }
      ]);
      return ret;
    };
  }

  // ==========================================================================
  // 3. MERCADO DE LA LECHE (VSP = AD + LR)
  // ==========================================================================
  const _origDrawLeche = window.drawLeche;
  if (typeof _origDrawLeche === "function") {
    window.drawLeche = function(...args) {
      const ret = _origDrawLeche.apply(this, args);
      const { A, B, C, D, Q: Qp } = stateLc;
      const q0 = (A - C) / (B + D), p0 = A - B * q0;
      const q1 = (A - C + D * Qp) / (B + D), p1 = A - B * q1, qo1 = q1 - Qp;
      const ad = 0.5 * (p0 + p1) * (q1 - q0), lr = 0.5 * (p0 + p1) * (q0 - qo1);
      const vsp = ad + lr, pSoc = Qp > 0 ? vsp / Qp : p0, vpp = p1 * Qp;

      renderHilo(
        "lc-hilo", "lc-fstrip",
        "Hilo Conductor Vivo — Cómo nace el Valor Social de la Producción (Fontaine)",
        "Desde el equilibrio inicial hasta la comparación con el ingreso privado",
        [
          {
            cls: "hs-b", cCls: "hc-b", conn: "1. Primero, sin proyecto",
            html: `Al igualar oferta y demanda, el mercado parte en <b>Q<sub>0</sub> = ${fmtInt(q0)}</b> a un precio de <b>P<sub>0</sub> = $${fmtDec(p0,2)}</b>.`
          },
          {
            cls: "hs-g", cCls: "hc-g", conn: "2. Al sumar el proyecto",
            html: `La oferta se desplaza en <b>+${fmtInt(Qp)}</b>; <b>por ello</b> el precio cae a <b>P<sub>1</sub> = $${fmtDec(p1,2)}</b>, el consumo sube a <b>${fmtInt(q1)}</b> y los antiguos oferentes bajan a <b>${fmtInt(qo1)}</b>.`
          },
          {
            cls: "hs-p", cCls: "hc-p", conn: "3. En consecuencia (VSP)",
            html: `El país gana <b>AD ($${fmtInt(ad)})</b> + <b>LR ($${fmtInt(lr)})</b> = <b>$${fmtInt(vsp)}</b> (<b>P* = $${fmtDec(pSoc,2)}</b>), superando al ingreso privado (VPP = $${fmtInt(vpp)}).`
          }
        ]
      );
      return ret;
    };
  }

  // ==========================================================================
  // 4. TRANSPORTE Y EXTERNALIDADES
  // ==========================================================================
  const _origDrawTr = window.drawTransporte;
  if (typeof _origDrawTr === "function") {
    window.drawTransporte = function(...args) {
      const ret = _origDrawTr.apply(this, args);
      const x0 = +document.getElementById("tr-x0").value;
      const x1 = +document.getElementById("tr-x1").value;
      const cp = +document.getElementById("tr-cp").value;
      const cs = +document.getElementById("tr-cs").value;
      const p0 = Math.max(500, +document.getElementById("tr-p0-in").value || 5000);
      let p1 = Math.max(100, +document.getElementById("tr-p1-in").value || 3500);
      if (p1 >= p0 - 100) p1 = Math.max(100, p0 - 200);
      const dx = x1 - x0;
      const ben = 0.5 * (p0 + p1) * dx;
      const brecha = cs - cp;
      const ext = brecha * x1;

      renderHilo(
        "tr-hilo", "tr-fstrip",
        "Hilo Conductor Vivo — Beneficio de Demanda frente a Externalidad",
        "Por qué el costo marginal social corrige la mirada privada",
        [
          {
            cls: "hs-b", cCls: "hc-b", conn: "1. Primero, el incentivo",
            html: `Al bajar la tarifa de <b>$${fmtInt(p0)}</b> a <b>$${fmtInt(p1)}</b>, se generan <b>+${fmtInt(dx)} viajes</b> nuevos en el corredor.`
          },
          {
            cls: "hs-g", cCls: "hc-g", conn: "2. Luego, el beneficio bruto",
            html: `Valorando esos viajes bajo la demanda (regla del trapecio), la disposición a pagar alcanza <b>$${fmtDec(ben/1e6,2)}M</b>.`
          },
          {
            cls: brecha > 0 ? "hs-r" : "hs-g", cCls: brecha > 0 ? "hc-r" : "hc-g",
            conn: brecha > 0 ? "3. Sin embargo (Externalidad)" : "3. Además (Ahorro externo)",
            html: brecha > 0
              ? `Cada viaje impone <b>+$${fmtInt(brecha)}</b> de congestión/emisiones a terceros (<b>$${fmtDec(ext/1e6,2)}M</b> en total), <b>por lo que</b> debe evaluarse usando CmgS = $${fmtInt(cs)}.`
              : `Al ser CmgS ≤ CmgP, el proyecto no genera daño externo neto sino un ahorro de <b>$${fmtDec(Math.abs(ext)/1e6,2)}M</b> para terceros.`
          }
        ]
      );
      return ret;
    };
  }

  // ==========================================================================
  // 5. ELASTICIDADES EXTREMAS
  // ==========================================================================
  const _origDrawEl = window.drawElast;
  if (typeof _origDrawEl === "function") {
    window.drawElast = function(...args) {
      const ret = _origDrawEl.apply(this, args);
      const rd = +document.getElementById("el-rd").value;
      const ro = +document.getElementById("el-ro").value;
      const dq = +document.getElementById("el-dq").value;
      const bd = slopeFromRig(rd), d_o = slopeFromRig(ro);
      const pctAD = (d_o / (bd + d_o)) * 100;
      const pctLR = (bd / (bd + d_o)) * 100;
      const dom = pctAD > 95 ? "100% AD (todo va a mayor consumo)" : (pctLR > 95 ? "100% LR (todo sustituye oferta antigua)" : `${fmtDec(pctAD,1)}% AD y ${fmtDec(pctLR,1)}% LR`);

      renderHilo(
        "el-hilo", "el-fstrip",
        "Hilo Conductor Vivo — Quién absorbe el ajuste del mercado",
        "No memorices las 4 reglas: mira qué lado puede reaccionar al precio",
        [
          {
            cls: "hs-b", cCls: "hc-b", conn: "1. Entra nueva oferta",
            html: `El proyecto inyecta <b>ΔQ = ${fmtInt(dq)} u</b> sobre un mercado que parte en equilibrio (Q<sub>0</sub> = 1.000; P<sub>0</sub> = $100).`
          },
          {
            cls: "hs-p", cCls: "hc-p", conn: "2. Comparamos rigideces",
            html: `La demanda tiene rigidez <b>${rd}/100</b> y la oferta <b>${ro}/100</b>; <b>por eso</b> el lado más elástico (menos rígido) absorbe la mayor parte del cambio.`
          },
          {
            cls: "hs-g", cCls: "hc-g", conn: "3. En consecuencia",
            html: `El Valor Social de la Producción se reparte en <b>${dom}</b>.`
          }
        ]
      );
      return ret;
    };
  }

  // ==========================================================================
  // 6. PUENTE VAN PRIVADO -> VANS SOCIAL (WATERFALL)
  // ==========================================================================
  const _origDrawWf = window.drawWaterfall;
  if (typeof _origDrawWf === "function") {
    window.drawWaterfall = function(...args) {
      const ret = _origDrawWf.apply(this, args);
      const cap = +document.getElementById("wf-cap").value;
      const vol = Math.max(5, +document.getElementById("wf-vol").value * (1 + (+document.getElementById("rd-vol").value) / 100));
      const mar = Math.max(10000, +document.getElementById("wf-mar").value * (1 + (+document.getElementById("rd-pre").value) / 100));
      const wacc = +document.getElementById("wf-wacc").value;
      const mo = Math.max(5, +document.getElementById("wf-mo").value * (1 + (+document.getElementById("rd-cos").value) / 100));
      const ch4 = +document.getElementById("wf-ch4").value;
      const r = calcWaterfall(cap, vol, mar, wacc, mo, ch4);
      const brecha = r.vanSoc - r.vanPriv;

      renderHilo(
        "wf-hilo", "wf-fstrip",
        "Hilo Conductor Vivo — Puente del VAN Privado al VANS Social SNI 2026",
        "Cada peldaño suma una corrección normativa exacta",
        [
          {
            cls: "hs-b", cCls: "hc-b", conn: "1. Punto de partida",
            html: `Con capital privado al <b>${fmtDec(wacc,1)}%</b> y pagando 25% de renta, el dueño obtiene <b>VAN Privado = $${fmtDec(r.vanPriv,1)}M</b>.`
          },
          {
            cls: "hs-p", cCls: "hc-p", conn: "2. Aplicamos SNI 2026",
            html: `Al pasar a <b>TSD 5,5%</b> (${r.dTsd>=0?"+":""}$${fmtDec(r.dTsd,1)}M), quitar impuestos (+$${fmtDec(r.dImp,1)}M), corregir MO (+$${fmtDec(r.dMo,1)}M) y sumar carbono/GIRS (+$${fmtDec(r.dCarb,1)}M), el valor salta <b>${brecha>=0?"+":""}$${fmtDec(brecha,1)}M</b>.`
          },
          {
            cls: r.vanSoc >= 0 ? "hs-g" : "hs-r", cCls: r.vanSoc >= 0 ? "hc-g" : "hc-r",
            conn: "3. En consecuencia",
            html: r.vanPriv >= 0 && r.vanSoc >= 0
              ? `Resulta <b>VANS = $${fmtDec(r.vanSoc,1)}M</b> (Cuadrante I): rentable privada y socialmente sin subsidio.`
              : (r.vanPriv < 0 && r.vanSoc >= 0
                ? `Aunque el privado pierde, <b>VANS = $${fmtDec(r.vanSoc,1)}M</b> (Cuadrante II): justifica aporte estatal hasta el monto del VANS.`
                : `Con <b>VANS = $${fmtDec(r.vanSoc,1)}M</b>, el proyecto no crea riqueza social bajo este nivel de estrés.`)
          }
        ]
      );
      return ret;
    };
  }

  // ==========================================================================
  // 7. HORNO DE PAN (PRECIOS MENTIROSOS)
  // ==========================================================================
  const _origDrawHn = window.drawHorno;
  if (typeof _origDrawHn === "function") {
    window.drawHorno = function(...args) {
      const ret = _origDrawHn.apply(this, args);
      const pb = +document.getElementById("hn-pb").value;
      const pe = +document.getElementById("hn-pe").value;
      const ce = +document.getElementById("hn-ce").value;
      const sub = +document.getElementById("hn-sub").value;
      const epBase = pb - 100, esBase = epBase - sub;
      const epEnv = pe - (100 + ce), esEnv = epEnv - sub;

      renderHilo(
        "hn-hilo", "hn-fstrip",
        "Hilo Conductor Vivo — Por qué un Precio Mentiroso engaña al privado",
        "Diferencia clave entre rentabilidad privada y bienestar país (Fontaine Cap. I)",
        [
          {
            cls: "hs-b", cCls: "hc-b", conn: "1. Mirada privada",
            html: `Con costo base $100 y precio $${pb}, Juan gana <b>${epBase>=0?"+":""}$${epBase}</b>; si agrega envasado (+$${ce} costo para vender a $${pe}), su ganancia cambia a <b>${epEnv>=0?"+":""}$${epEnv}</b>.`
          },
          {
            cls: "hs-o", cCls: "hc-o", conn: "2. Destapamos el subsidio",
            html: `Un insumo tiene un subsidio estatal oculto de <b>$${sub}</b>; <b>es decir</b>, el país paga en realidad $${100+sub} por producir el pan base.`
          },
          {
            cls: esBase < 0 ? "hs-r" : "hs-g", cCls: esBase < 0 ? "hc-r" : "hc-g",
            conn: esBase < 0 ? "3. En consecuencia (Trampa)" : "3. En consecuencia",
            html: esBase < 0
              ? `El Excedente Social cae a <b>$${esBase}</b> (y <b>$${esEnv}</b> envasado): <b>aunque Juan gane</b>, el negocio destruye riqueza nacional.`
              : `El Excedente Social se mantiene positivo (<b>+$${esBase}</b> base / <b>${esEnv>=0?"+":""}$${esEnv}</b> envasado), alineado con el interés país.`
          }
        ]
      );
      return ret;
    };
  }

  // ==========================================================================
  // 8. AGUA 10 AÑOS (DÉFICIT HÍDRICO CEPAL)
  // ==========================================================================
  const _origDrawAg = window.drawAgua;
  if (typeof _origDrawAg === "function") {
    window.drawAgua = function(...args) {
      const ret = _origDrawAg.apply(this, args);
      const p0 = +document.getElementById("ag-p0").value;
      const rPct = +document.getElementById("ag-r").value, r = rPct / 100;
      const dot = +document.getElementById("ag-dot").value;
      const ofe = +document.getElementById("ag-ofe").value;
      const p10 = p0 * Math.pow(1 + r, 9);
      const d10 = (p10 * dot) / 1000;
      const def10 = d10 - ofe;

      renderHilo(
        "ag-hilo", "ag-fstrip",
        "Hilo Conductor Vivo — Cómo se dimensiona un proyecto por déficit (CEPAL N° 39)",
        "Población geométrica → Demanda física → Brecha a cubrir",
        [
          {
            cls: "hs-b", cCls: "hc-b", conn: "1. Proyectamos población",
            html: `Partiendo en <b>${fmtInt(p0)} hab.</b> al <b>${fmtDec(rPct,1)}% anual</b> compuesto, al Año 10 (t=9) llegamos a <b>${fmtInt(p10)} hab.</b>`
          },
          {
            cls: "hs-p", cCls: "hc-p", conn: "2. Convertimos a demanda",
            html: `Multiplicando por <b>${dot} L/día</b> (÷ 1.000), la ciudad necesitará <b>${fmtInt(d10)} m³/día</b> de agua potable.`
          },
          {
            cls: def10 > 0 ? "hs-r" : "hs-g", cCls: def10 > 0 ? "hc-r" : "hc-g",
            conn: "3. Restamos oferta actual",
            html: def10 > 0
              ? `Frente a la planta fija de <b>${fmtInt(ofe)} m³/día</b>, surge un déficit de <b>${fmtInt(def10)} m³/día</b> que justifica la ampliación.`
              : `La planta actual (<b>${fmtInt(ofe)} m³/día</b>) todavía cubre toda la demanda del Año 10 sin déficit.`
          }
        ]
      );
      return ret;
    };
  }

  // ==========================================================================
  // 9. AMBIENTAL RA2 (MCV + CARBONO IPCC 2026)
  // ==========================================================================
  const _origDrawAmb = window.drawAmbiental;
  if (typeof _origDrawAmb === "function") {
    window.drawAmbiental = function(...args) {
      const ret = _origDrawAmb.apply(this, args);
      const vis = +document.getElementById("amb-vis").value;
      const hrs = +document.getElementById("amb-hrs").value;
      const gas = +document.getElementById("amb-gas").value;
      const co2 = +document.getElementById("amb-co2").value;
      const ch4 = +document.getElementById("amb-ch4").value;
      const n2o = +document.getElementById("amb-n2o").value;
      const valRec = vis * (hrs * 2792 + gas);
      const co2Eq = co2 + 28 * ch4 + 265 * n2o;
      const valGei = co2Eq * 71801;
      const valTot = valRec + valGei;

      renderHilo(
        "amb-hilo", "amb-fstrip",
        "Hilo Conductor Vivo — Cómo monetizar servicios ambientales para el VANS (RA2)",
        "Recreación (Barzev MCV) + Gases de Efecto Invernadero (SNI 2026)",
        [
          {
            cls: "hs-b", cCls: "hc-b", conn: "1. Valor recreativo (MCV)",
            html: `<b>${fmtInt(vis)} visitas</b> × (${fmtDec(hrs,2)}h a VST $2.792 + $${fmtInt(gas)} gasto) revelan un beneficio de <b>$${fmtDec(valRec/1e6,2)}M/año</b>.`
          },
          {
            cls: "hs-g", cCls: "hc-g", conn: "2. Homologamos gases IPCC",
            html: `Convertimos CH<sub>4</sub> (×28) y N<sub>2</sub>O (×265) a <b>${fmtDec(co2Eq,1)} t CO<sub>2</sub>eq</b>, que a $71.801/t valen <b>$${fmtDec(valGei/1e6,2)}M/año</b>.`
          },
          {
            cls: "hs-p", cCls: "hc-p", conn: "3. Sumamos al flujo social",
            html: `En total, el ecosistema aporta <b>$${fmtDec(valTot/1e6,2)} MM/año</b> de beneficio ambiental cuantificable para descontar al 5,5%.`
          }
        ]
      );
      return ret;
    };
  }

  // Disparo inicial para pintar todos los hilos al cargar
  ["drawLeche","drawTransporte","drawElast","drawWaterfall","drawHorno","drawAgua","drawAmbiental","drawClaseEj1","drawClaseEj2"].forEach(fn => {
    try { if (typeof window[fn] === "function") window[fn](); } catch (e) {}
  });
})();
</script>
"""


def inyectar_conectores_pedagogicos(html_base: str) -> str:
    """Inyecta de forma no destructiva el CSS y el motor de conectores vivos en el HTML 60 FPS."""
    if not html_base or 'id="js-conectores-pedagogicos"' in html_base:
        return html_base

    html_out = html_base
    if "</head>" in html_out:
        html_out = html_out.replace("</head>", CSS_CONECTORES_PEDAGOGICOS + "\n</head>", 1)
    else:
        html_out = CSS_CONECTORES_PEDAGOGICOS + html_out

    idx_body = html_out.rfind("</body>")
    if idx_body != -1:
        html_out = html_out[:idx_body] + JS_CONECTORES_PEDAGOGICOS + "\n" + html_out[idx_body:]
    else:
        html_out = html_out + JS_CONECTORES_PEDAGOGICOS

    return html_out
