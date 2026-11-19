# -*- coding: utf-8 -*-
"""
motor_fluidez_vectores_sni.py — EXTENSIÓN DE GRÁFICOS FLUIDOS A 60 FPS CON FLECHAS VECTORIALES
Módulo independiente para PROYECTOS-2026 (ULagos).
Renderiza en el navegador (HTML5 SVG + JavaScript) simuladores microeconómicos sin lag de servidor:
  1) Externalidades y Costo Social en Transporte (CmgP vs. CmgS, Elasticidad Ed, Flechas de dirección).
  2) Mercado de la Leche (VSP = AD + LR, Desplazamiento animado O -> O', Flechas de ΔP, AD y LR).
  3) Laboratorio de los 4 Casos Extremos de Elasticidad (Morfología continua a 60 FPS).
Incluye Rastro Fantasma (Ghost Trail) para comparar en vivo la posición anterior vs. actual.
"""

import streamlit as st
import streamlit.components.v1 as components


HTML_SIMULADOR_FLUIDO = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<style>
  * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }
  body { margin: 0; padding: 0; background: #F8FAFC; color: #0F172A; }
  .wrap { max-width: 1200px; margin: 0 auto; padding: 6px 4px 12px 4px; }
  .top-tabs { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
  .tab-btn {
    border: 1px solid #CBD5E1; background: #FFFFFF; color: #334155;
    padding: 8px 14px; border-radius: 6px; font-weight: 700; font-size: 13px;
    cursor: pointer; transition: all 0.15s ease;
  }
  .tab-btn:hover { border-color: #1D4ED8; color: #1D4ED8; background: #EFF6FF; }
  .tab-btn.active { background: #0F172A; color: #FFFFFF; border-color: #0F172A; }
  .panel { display: none; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 16px; }
  .panel.active { display: block; }
  .sec-title {
    font-size: 13.5px; font-weight: 700; color: #1E3A8A;
    background: #DBEAFE; border-left: 4px solid #1D4ED8;
    padding: 7px 12px; border-radius: 4px; margin-bottom: 12px;
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
  }
  .btn-bar { display: flex; gap: 8px; flex-wrap: wrap; }
  .act-btn {
    border: 1px solid #94A3B8; background: #FFFFFF; color: #0F172A;
    padding: 5px 10px; border-radius: 5px; font-size: 12px; font-weight: 700; cursor: pointer;
  }
  .act-btn:hover { background: #EFF6FF; border-color: #1D4ED8; color: #1D4ED8; }
  .act-btn.primary { background: #1D4ED8; color: #FFFFFF; border-color: #1D4ED8; }
  .act-btn.primary:hover { background: #1E40AF; }
  .sliders-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(195px, 1fr)); gap: 12px; margin-bottom: 12px; }
  .sl-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px 10px; }
  .sl-head { display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: #1E293B; margin-bottom: 4px; }
  .sl-val { color: #1D4ED8; font-family: Consolas, monospace; }
  .sl-delta { font-size: 11px; font-weight: 700; margin-left: 4px; }
  .d-up { color: #15803D; }
  .d-down { color: #DC2626; }
  .d-eq { color: #64748B; }
  input[type="range"] { width: 100%; accent-color: #1D4ED8; cursor: pointer; margin: 2px 0; }
  .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(165px, 1fr)); gap: 8px; margin-bottom: 10px; }
  .kpi { background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 3px solid #0F172A; border-radius: 5px; padding: 7px 10px; }
  .kpi-lbl { font-size: 11px; color: #475569; font-weight: 600; }
  .kpi-val { font-size: 15px; font-weight: 800; color: #0F172A; font-family: Consolas, monospace; margin-top: 2px; }
  .kpi-sub { font-size: 11px; color: #334155; margin-top: 1px; }
  .svg-box { width: 100%; border: 1px solid #E2E8F0; border-radius: 6px; background: #FFFFFF; overflow: hidden; }
  svg { width: 100%; height: auto; display: block; }
  .legend-bar {
    display: flex; gap: 14px; flex-wrap: wrap; font-size: 11.5px; color: #334155;
    margin-top: 8px; padding: 6px 10px; background: #F8FAFC; border-radius: 5px; border: 1px solid #E2E8F0;
  }
  .leg-item { display: inline-flex; align-items: center; gap: 5px; font-weight: 600; }
  .sw { width: 12px; height: 12px; border-radius: 2px; display: inline-block; }
  .sw-line { width: 16px; height: 3px; display: inline-block; }
  .note-box {
    margin-top: 8px; padding: 8px 12px; border-radius: 5px; font-size: 12.5px; line-height: 1.4;
    background: #EFF6FF; border-left: 4px solid #1D4ED8; color: #1E293B;
  }
</style>
</head>
<body>
<div class="wrap">
  <div class="top-tabs">
    <button class="tab-btn active" onclick="openTab('transporte', this)">1. Transporte y Externalidades (60 FPS + Flechas)</button>
    <button class="tab-btn" onclick="openTab('leche', this)">2. Mercado de la Leche (Animación O → O' + Flechas)</button>
    <button class="tab-btn" onclick="openTab('elasticidad', this)">3. Elasticidades Extremas (Deformación en Vivo)</button>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 1: TRANSPORTE Y EXTERNALIDADES                                   -->
  <!-- ====================================================================== -->
  <div id="panel-transporte" class="panel active">
    <div class="sec-title">
      <span>SIMULADOR FLUIDO: EXTERNALIDADES Y COSTO SOCIAL EN TRANSPORTE (APUNTES PÁGS. 13–14)</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarTransporte()">Reproducir Expansión</button>
        <button class="act-btn" onclick="fijarGhostTransporte()">Fijar Fantasma Aquí</button>
        <button class="act-btn" onclick="resetTransporte()">Restaurar Caso Apuntes</button>
      </div>
    </div>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>Pasajes Iniciales X0</span><span><span id="tr-x0-v" class="sl-val">70.000</span><span id="tr-x0-d" class="sl-delta d-eq"></span></span></div>
        <input id="tr-x0" type="range" min="30000" max="90000" step="500" value="70000" oninput="drawTransporte()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Pasajes Con Proyecto X1</span><span><span id="tr-x1-v" class="sl-val">100.030</span><span id="tr-x1-d" class="sl-delta d-eq"></span></span></div>
        <input id="tr-x1" type="range" min="72000" max="122000" step="250" value="100030" oninput="drawTransporte()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Costo Marg. Privado CmgP</span><span><span id="tr-cp-v" class="sl-val">$1.300</span><span id="tr-cp-d" class="sl-delta d-eq"></span></span></div>
        <input id="tr-cp" type="range" min="400" max="2400" step="50" value="1300" oninput="drawTransporte()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Costo Marg. Social CmgS</span><span><span id="tr-cs-v" class="sl-val">$1.700</span><span id="tr-cs-d" class="sl-delta d-eq"></span></span></div>
        <input id="tr-cs" type="range" min="400" max="3200" step="50" value="1700" oninput="drawTransporte()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Elasticidad Demanda (Ed)</div><div id="tr-k-ed" class="kpi-val">-1,43</div><div id="tr-k-dx" class="kpi-sub">ΔX = +30.030 pasajes</div></div>
      <div class="kpi" style="border-left-color:#7C3AED;"><div class="kpi-lbl">Beneficio Bruto Demanda</div><div id="tr-k-ben" class="kpi-val">$127.627.500</div><div class="kpi-sub">Área bajo curva D (X0 → X1)</div></div>
      <div class="kpi" style="border-left-color:#EA580C;"><div class="kpi-lbl">Externalidad (CmgS - CmgP)</div><div id="tr-k-ext" class="kpi-val">$40.012.000</div><div id="tr-k-brecha" class="kpi-sub">Brecha = $400 / pasaje</div></div>
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Movimiento vs. Fantasma</div><div id="tr-k-mov" class="kpi-val">Base (Sin cambios)</div><div id="tr-k-mov2" class="kpi-sub">Mueve un slider para ver flechas</div></div>
    </div>

    <div class="svg-box"><svg id="svg-transporte" viewBox="0 0 960 400"></svg></div>
    <div class="legend-bar">
      <span class="leg-item"><span class="sw" style="background:rgba(124,58,237,0.25);border:1px solid #7C3AED;"></span>Beneficio Bruto Demanda</span>
      <span class="leg-item"><span class="sw" style="background:rgba(234,88,12,0.35);border:1px solid #EA580C;"></span>Banda Externalidad (CmgS vs CmgP)</span>
      <span class="leg-item"><span class="sw-line" style="border-top:2px dashed #94A3B8;"></span>Rastro Fantasma (Referencia anterior)</span>
      <span class="leg-item"><span class="sw-line" style="background:#DC2626;"></span>Flecha Vectorial de Movimiento</span>
    </div>
    <div id="tr-note" class="note-box">Arrastra cualquier deslizador: el gráfico responde instantáneamente a 60 FPS y dibuja flechas rojas/verdes indicando hacia dónde se movió el área respecto de tu referencia fantasma.</div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 2: MERCADO DE LA LECHE                                           -->
  <!-- ====================================================================== -->
  <div id="panel-leche" class="panel">
    <div class="sec-title">
      <span>PIZARRA FLUIDA A 60 FPS: MERCADO DE LA LECHE (VSP = AD + LR)</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarLeche()">Reproducir 0% → 100%</button>
        <button class="act-btn" onclick="presetLeche(-50)">Apuntes (-50)</button>
        <button class="act-btn" onclick="presetLeche(50)">Variante (+50)</button>
        <button class="act-btn" onclick="fijarGhostLeche()">Fijar Fantasma Aquí</button>
      </div>
    </div>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>Intercepto Demanda (A)</span><span id="lc-a-v" class="sl-val">300</span></div>
        <input id="lc-a" type="range" min="180" max="500" step="5" value="300" oninput="drawLeche()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Pendiente Demanda (B)</span><span id="lc-b-v" class="sl-val">0,0205</span></div>
        <input id="lc-b" type="range" min="0.008" max="0.050" step="0.0005" value="0.0205" oninput="drawLeche()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Intercepto Oferta (C)</span><span id="lc-c-v" class="sl-val">-50</span></div>
        <input id="lc-c" type="range" min="-120" max="120" step="5" value="-50" oninput="drawLeche()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Pendiente Oferta (D)</span><span id="lc-d-v" class="sl-val">0,0250</span></div>
        <input id="lc-d" type="range" min="0.008" max="0.050" step="0.0005" value="0.0250" oninput="drawLeche()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Producción Proyecto (Q_proy)</span><span id="lc-q-v" class="sl-val">1.470 t</span></div>
        <input id="lc-q" type="range" min="0" max="3200" step="10" value="1470" oninput="drawLeche()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Equilibrio Inicial (E0)</div><div id="lc-k-e0" class="kpi-val">7.692 t | $142,3</div><div class="kpi-sub">Sin proyecto</div></div>
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Nuevo Equilibrio (E1)</div><div id="lc-k-e1" class="kpi-val">8.500 t | $125,8</div><div id="lc-k-dp" class="kpi-sub">Caída precio ΔP = -$16,6</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Aumento Disponibilidad (AD)</div><div id="lc-k-ad" class="kpi-val">$108.282</div><div id="lc-k-adp" class="kpi-sub">55,0% del VSP</div></div>
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Liberación Recursos (LR)</div><div id="lc-k-lr" class="kpi-val">$88.742</div><div id="lc-k-lrp" class="kpi-sub">45,0% del VSP</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">VSP Total y Precio Social P*</div><div id="lc-k-vsp" class="kpi-val">$197.024</div><div id="lc-k-ps" class="kpi-sub">P* = $134,03 / ton</div></div>
    </div>

    <div class="svg-box"><svg id="svg-leche" viewBox="0 0 960 410"></svg></div>
    <div class="legend-bar">
      <span class="leg-item"><span class="sw" style="background:rgba(37,99,235,0.28);border:1px solid #1D4ED8;"></span>Liberación de Recursos (LR: Qo1 ← Q0)</span>
      <span class="leg-item"><span class="sw" style="background:rgba(220,38,38,0.28);border:1px solid #DC2626;"></span>Aumento en Disponibilidad (AD: Q0 → Q1)</span>
      <span class="leg-item"><span class="sw-line" style="background:#15803D;"></span>Flecha Verde: Desplazamiento Oferta O → O'</span>
      <span class="leg-item"><span class="sw-line" style="border-top:2px dashed #94A3B8;"></span>Rastro Fantasma (Referencia anterior)</span>
    </div>
    <div id="lc-note" class="note-box">Tip: presiona <b>Reproducir 0% → 100%</b> o arrastra <b>Q_proy</b> para ver en movimiento continuo cómo la flecha de oferta empuja el precio hacia abajo y abre simultáneamente el bloque azul (LR) y el rojo (AD).</div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 3: ELASTICIDADES EXTREMAS                                        -->
  <!-- ====================================================================== -->
  <div id="panel-elasticidad" class="panel">
    <div class="sec-title">
      <span>LABORATORIO FLUIDO DE ELASTICIDADES EXTREMAS (PESO % AD VS. % LR)</span>
      <div class="btn-bar">
        <button class="act-btn" onclick="setElast(0, 55)">ηd = ∞ (100% AD)</button>
        <button class="act-btn" onclick="setElast(55, 0)">ηo = ∞ (100% LR)</button>
        <button class="act-btn" onclick="setElast(100, 45)">ηd = 0 (100% LR)</button>
        <button class="act-btn" onclick="setElast(45, 100)">ηo = 0 (100% AD)</button>
      </div>
    </div>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>Rigidez Demanda (0=Horiz, 100=Vert)</span><span id="el-rd-v" class="sl-val">50</span></div>
        <input id="el-rd" type="range" min="0" max="100" step="1" value="50" oninput="drawElast()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Rigidez Oferta (0=Horiz, 100=Vert)</span><span id="el-ro-v" class="sl-val">50</span></div>
        <input id="el-ro" type="range" min="0" max="100" step="1" value="50" oninput="drawElast()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Tamaño Proyecto (ΔQ)</span><span id="el-dq-v" class="sl-val">300</span></div>
        <input id="el-dq" type="range" min="50" max="500" step="10" value="300" oninput="drawElast()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Participación AD</div><div id="el-k-ad" class="kpi-val">50,0%</div><div class="kpi-sub">Mayor consumo neto (→)</div></div>
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Participación LR</div><div id="el-k-lr" class="kpi-val">50,0%</div><div class="kpi-sub">Recursos liberados (←)</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Efecto en Precio (P0 → P1)</div><div id="el-k-p" class="kpi-val">$100 → $82,0</div><div id="el-k-dp" class="kpi-sub">Caída ΔP = -$18,0</div></div>
    </div>

    <div class="svg-box"><svg id="svg-elast" viewBox="0 0 960 390"></svg></div>
    <div id="el-note" class="note-box">Mueve las rigideces suavemente: observa cómo las flechas horizontales <b>← LR</b> y <b>→ AD</b> cambian de tamaño al instante hasta volverse 100% una u otra en los 4 casos extremos de examen.</div>
  </div>
</div>

<script>
const NS = "http://www.w3.org/2000/svg";
function fmtInt(n) { return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, "."); }
function fmtDec(n, d=1) {
  const s = Number(n).toFixed(d).split(".");
  return s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (d > 0 ? "," + s[1] : "");
}
function el(tag, attrs, parent) {
  const node = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs || {})) node.setAttribute(k, v);
  if (parent) parent.appendChild(node);
  return node;
}
function addDefs(svg) {
  const defs = el("defs", {}, svg);
  const colors = [
    ["arr-red", "#DC2626"], ["arr-blue", "#1D4ED8"], ["arr-green", "#15803D"],
    ["arr-orange", "#EA580C"], ["arr-dark", "#0F172A"]
  ];
  for (const [id, col] of colors) {
    const m = el("marker", { id, viewBox: "0 0 10 10", refX: "8", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" }, defs);
    el("path", { d: "M 0 1 L 10 5 L 0 9 z", fill: col }, m);
  }
}
function drawArrow(svg, x1, y1, x2, y2, color, markerId, label, lx, ly, anchor="middle") {
  const dist = Math.hypot(x2 - x1, y2 - y1);
  if (dist < 6) return;
  el("line", { x1, y1, x2, y2, stroke: color, "stroke-width": "2.6", "marker-end": `url(#${markerId})` }, svg);
  if (label) {
    const bgW = Math.max(54, label.length * 6.8 + 10);
    const rx = anchor === "middle" ? lx - bgW / 2 : (anchor === "start" ? lx - 4 : lx - bgW + 4);
    el("rect", { x: rx, y: ly - 12, width: bgW, height: 17, rx: 4, fill: "rgba(255,255,255,0.92)", stroke: color, "stroke-width": "1" }, svg);
    const t = el("text", { x: lx, y: ly, fill: color, "font-size": "11", "font-weight": "700", "text-anchor": anchor }, svg);
    t.textContent = label;
  }
}
function setDeltaBadge(id, diff, unit="", isMoney=false) {
  const node = document.getElementById(id);
  if (Math.abs(diff) < 1e-6) { node.textContent = ""; node.className = "sl-delta d-eq"; return; }
  const sign = diff > 0 ? "↑ +" : "↓ -";
  const valTxt = isMoney ? "$" + fmtInt(Math.abs(diff)) : fmtInt(Math.abs(diff)) + unit;
  node.textContent = `(${sign}${valTxt})`;
  node.className = "sl-delta " + (diff > 0 ? "d-up" : "d-down");
}

function openTab(name, btn) {
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.getElementById("panel-" + name).classList.add("active");
  btn.classList.add("active");
  if (name === "transporte") drawTransporte();
  if (name === "leche") drawLeche();
  if (name === "elasticidad") drawElast();
}

// ============================================================================
// 1. SIMULADOR TRANSPORTE Y EXTERNALIDADES
// ============================================================================
let ghostTr = { x0: 70000, x1: 100030, cp: 1300, cs: 1700 };
let animTrId = null;

function fijarGhostTransporte() {
  ghostTr = {
    x0: +document.getElementById("tr-x0").value,
    x1: +document.getElementById("tr-x1").value,
    cp: +document.getElementById("tr-cp").value,
    cs: +document.getElementById("tr-cs").value,
  };
  drawTransporte();
}
function resetTransporte() {
  if (animTrId) cancelAnimationFrame(animTrId);
  document.getElementById("tr-x0").value = 70000;
  document.getElementById("tr-x1").value = 100030;
  document.getElementById("tr-cp").value = 1300;
  document.getElementById("tr-cs").value = 1700;
  ghostTr = { x0: 70000, x1: 100030, cp: 1300, cs: 1700 };
  drawTransporte();
}
function animarTransporte() {
  if (animTrId) cancelAnimationFrame(animTrId);
  const x0 = +document.getElementById("tr-x0").value;
  const targetX1 = 100030;
  const startX1 = Math.max(72000, x0 + 2000);
  ghostTr = { x0, x1: startX1, cp: +document.getElementById("tr-cp").value, cs: +document.getElementById("tr-cs").value };
  const t0 = performance.now();
  const dur = 1600;
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    const ease = 1 - Math.pow(1 - u, 3);
    document.getElementById("tr-x1").value = Math.round(startX1 + (targetX1 - startX1) * ease);
    drawTransporte();
    if (u < 1) animTrId = requestAnimationFrame(step);
  }
  animTrId = requestAnimationFrame(step);
}
function drawTransporte() {
  const x0 = +document.getElementById("tr-x0").value;
  let x1 = +document.getElementById("tr-x1").value;
  if (x1 <= x0 + 1500) { x1 = x0 + 1500; document.getElementById("tr-x1").value = x1; }
  const cp = +document.getElementById("tr-cp").value;
  const cs = +document.getElementById("tr-cs").value;

  document.getElementById("tr-x0-v").textContent = fmtInt(x0);
  document.getElementById("tr-x1-v").textContent = fmtInt(x1);
  document.getElementById("tr-cp-v").textContent = "$" + fmtInt(cp);
  document.getElementById("tr-cs-v").textContent = "$" + fmtInt(cs);
  setDeltaBadge("tr-x0-d", x0 - ghostTr.x0);
  setDeltaBadge("tr-x1-d", x1 - ghostTr.x1);
  setDeltaBadge("tr-cp-d", cp - ghostTr.cp, "", true);
  setDeltaBadge("tr-cs-d", cs - ghostTr.cs, "", true);

  const p0 = 5000, p1 = 3500;
  const dx = x1 - x0;
  const ed = ((x1 - x0) / x0) / ((p1 - p0) / p0);
  const ben = 0.5 * (p0 + p1) * dx;
  const brecha = cs - cp;
  const ext = brecha * x1;

  document.getElementById("tr-k-ed").textContent = fmtDec(ed, 2);
  document.getElementById("tr-k-dx").textContent = `ΔX = +${fmtInt(dx)} pasajes`;
  document.getElementById("tr-k-ben").textContent = "$" + fmtInt(ben);
  document.getElementById("tr-k-ext").textContent = (ext < 0 ? "-$" : "$") + fmtInt(Math.abs(ext));
  document.getElementById("tr-k-brecha").textContent = `Brecha = ${brecha >= 0 ? "+" : "-"}$${fmtInt(Math.abs(brecha))} / pasaje`;

  const dX1 = x1 - ghostTr.x1;
  const dCs = cs - ghostTr.cs;
  if (Math.abs(dX1) >= 250) {
    document.getElementById("tr-k-mov").textContent = dX1 > 0 ? `→ +${fmtInt(dX1)} pasajes` : `← -${fmtInt(Math.abs(dX1))} pasajes`;
    document.getElementById("tr-k-mov2").textContent = dX1 > 0 ? "Área de demanda se expandió" : "Área de demanda se contrajo";
  } else if (Math.abs(dCs) >= 50) {
    document.getElementById("tr-k-mov").textContent = dCs > 0 ? `↑ CmgS +$${fmtInt(dCs)}` : `↓ CmgS -$${fmtInt(Math.abs(dCs))}`;
    document.getElementById("tr-k-mov2").textContent = "Cambio en costo marginal social";
  } else {
    document.getElementById("tr-k-mov").textContent = "En referencia fantasma";
    document.getElementById("tr-k-mov2").textContent = "Mueve un slider para ver flechas";
  }

  const svg = document.getElementById("svg-transporte");
  svg.innerHTML = "";
  addDefs(svg);

  const M = { l: 72, r: 30, t: 28, b: 46 };
  const W = 960, H = 400;
  const maxX = 130000, maxY = 6200;
  const sx = v => M.l + (v / maxX) * (W - M.l - M.r);
  const sy = v => H - M.b - (v / maxY) * (H - M.t - M.b);

  // Grilla y ejes
  for (let y = 0; y <= 6000; y += 1000) {
    el("line", { x1: M.l, y1: sy(y), x2: W - M.r, y2: sy(y), stroke: "#E2E8F0", "stroke-width": "1" }, svg);
    const t = el("text", { x: M.l - 8, y: sy(y) + 4, fill: "#475569", "font-size": "11", "text-anchor": "end" }, svg);
    t.textContent = "$" + fmtInt(y);
  }
  for (let x = 0; x <= 120000; x += 20000) {
    el("line", { x1: sx(x), y1: M.t, x2: sx(x), y2: H - M.b, stroke: "#F1F5F9", "stroke-width": "1" }, svg);
    const t = el("text", { x: sx(x), y: H - M.b + 16, fill: "#475569", "font-size": "11", "text-anchor": "middle" }, svg);
    t.textContent = x === 0 ? "0" : (x / 1000) + "k";
  }
  el("line", { x1: M.l, y1: H - M.b, x2: W - M.r, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);
  el("line", { x1: M.l, y1: M.t, x2: M.l, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);

  // Rastro fantasma del área de demanda anterior
  if (Math.abs(x1 - ghostTr.x1) >= 250 || Math.abs(x0 - ghostTr.x0) >= 250) {
    const gPts = `${sx(ghostTr.x0)},${sy(0)} ${sx(ghostTr.x1)},${sy(0)} ${sx(ghostTr.x1)},${sy(p1)} ${sx(ghostTr.x0)},${sy(p0)}`;
    el("polygon", { points: gPts, fill: "rgba(148,163,184,0.12)", stroke: "#94A3B8", "stroke-width": "1.6", "stroke-dasharray": "5,4" }, svg);
  }
  if (Math.abs(cs - ghostTr.cs) >= 50) {
    el("line", { x1: M.l, y1: sy(ghostTr.cs), x2: W - M.r, y2: sy(ghostTr.cs), stroke: "#94A3B8", "stroke-width": "1.4", "stroke-dasharray": "4,4" }, svg);
  }

  // Área actual Beneficio Bruto Demanda
  const dPts = `${sx(x0)},${sy(0)} ${sx(x1)},${sy(0)} ${sx(x1)},${sy(p1)} ${sx(x0)},${sy(p0)}`;
  el("polygon", { points: dPts, fill: "rgba(124,58,237,0.22)", stroke: "#7C3AED", "stroke-width": "1.8" }, svg);

  // Banda Externalidad Negativa (o Positiva)
  const yTopExt = Math.max(cp, cs), yBotExt = Math.min(cp, cs);
  el("rect", {
    x: sx(0), y: sy(yTopExt), width: sx(x1) - sx(0), height: Math.max(1, sy(yBotExt) - sy(yTopExt)),
    fill: brecha >= 0 ? "rgba(234,88,12,0.34)" : "rgba(22,163,74,0.28)",
    stroke: brecha >= 0 ? "#EA580C" : "#16A34A", "stroke-width": "1.5"
  }, svg);

  // Rectas CmgS y CmgP
  el("line", { x1: M.l, y1: sy(cs), x2: W - M.r, y2: sy(cs), stroke: "#DC2626", "stroke-width": "2", "stroke-dasharray": "6,4" }, svg);
  el("line", { x1: M.l, y1: sy(cp), x2: W - M.r, y2: sy(cp), stroke: "#1D4ED8", "stroke-width": "2", "stroke-dasharray": "3,3" }, svg);
  const tCs = el("text", { x: W - M.r - 4, y: sy(cs) - 5, fill: "#DC2626", "font-size": "11", "font-weight": "700", "text-anchor": "end" }, svg);
  tCs.textContent = `CmgS = $${fmtInt(cs)}`;
  const tCp = el("text", { x: W - M.r - 4, y: sy(cp) + 13, fill: "#1D4ED8", "font-size": "11", "font-weight": "700", "text-anchor": "end" }, svg);
  tCp.textContent = `CmgP = $${fmtInt(cp)}`;

  // Curva de Demanda
  const pend = (p0 - p1) / dx;
  const xDemIni = Math.max(0, x0 - (maxY - p0) / pend);
  const xDemFin = Math.min(maxX, x1 + p1 / pend);
  const yDemIni = p0 + pend * (x0 - xDemIni);
  const yDemFin = p1 - pend * (xDemFin - x1);
  el("line", { x1: sx(xDemIni), y1: sy(yDemIni), x2: sx(xDemFin), y2: sy(yDemFin), stroke: "#0F172A", "stroke-width": "2.6" }, svg);

  // Puntos clave
  el("circle", { cx: sx(x0), cy: sy(p0), r: 5, fill: "#0F172A" }, svg);
  el("circle", { cx: sx(x1), cy: sy(p1), r: 5.5, fill: "#7C3AED", stroke: "#FFFFFF", "stroke-width": "1.5" }, svg);

  // FLECHA VECTORIAL DE DIRECCIÓN DE MOVIMIENTO EN X1 (vs Fantasma)
  if (Math.abs(x1 - ghostTr.x1) >= 250) {
    const colArr = x1 > ghostTr.x1 ? "#15803D" : "#DC2626";
    const mk = x1 > ghostTr.x1 ? "arr-green" : "arr-red";
    const lbl = x1 > ghostTr.x1 ? `→ +${fmtInt(x1 - ghostTr.x1)}` : `← -${fmtInt(ghostTr.x1 - x1)}`;
    drawArrow(svg, sx(ghostTr.x1), sy(p1) - 24, sx(x1), sy(p1) - 24, colArr, mk, lbl, (sx(ghostTr.x1) + sx(x1)) / 2, sy(p1) - 32);
  }
  // FLECHA VECTORIAL DE EXPANSIÓN X0 -> X1
  drawArrow(svg, sx(x0) + 4, sy(350), sx(x1) - 4, sy(350), "#0F172A", "arr-dark", `ΔX = +${fmtInt(dx)}`, (sx(x0) + sx(x1)) / 2, sy(650));

  // FLECHA VECTORIAL VERTICAL EN BRECHA EXTERNALIDAD (CmgP -> CmgS)
  if (Math.abs(brecha) >= 150) {
    const xBre = sx(25000);
    drawArrow(svg, xBre, sy(cp), xBre, sy(cs), brecha > 0 ? "#EA580C" : "#15803D", brecha > 0 ? "arr-orange" : "arr-green",
      `Externalidad $${fmtInt(Math.abs(brecha))}`, xBre + 8, (sy(cp) + sy(cs)) / 2 + 4, "start");
  }
}

// ============================================================================
// 2. SIMULADOR MERCADO DE LA LECHE (60 FPS + ANIMACIÓN + FLECHAS)
// ============================================================================
let ghostLc = { A: 300, B: 0.0205, C: -50, D: 0.025, Q: 1470 };
let animLcId = null;

function fijarGhostLeche() {
  ghostLc = {
    A: +document.getElementById("lc-a").value,
    B: +document.getElementById("lc-b").value,
    C: +document.getElementById("lc-c").value,
    D: +document.getElementById("lc-d").value,
    Q: +document.getElementById("lc-q").value,
  };
  drawLeche();
}
function presetLeche(cVal) {
  if (animLcId) cancelAnimationFrame(animLcId);
  document.getElementById("lc-a").value = 300;
  document.getElementById("lc-b").value = 0.0205;
  document.getElementById("lc-c").value = cVal;
  document.getElementById("lc-d").value = 0.025;
  document.getElementById("lc-q").value = 1470;
  drawLeche();
}
function animarLeche() {
  if (animLcId) cancelAnimationFrame(animLcId);
  const targetQ = Math.max(400, +document.getElementById("lc-q").value || 1470);
  ghostLc = {
    A: +document.getElementById("lc-a").value,
    B: +document.getElementById("lc-b").value,
    C: +document.getElementById("lc-c").value,
    D: +document.getElementById("lc-d").value,
    Q: 0,
  };
  const t0 = performance.now();
  const dur = 1800;
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    const ease = 1 - Math.pow(1 - u, 3);
    document.getElementById("lc-q").value = Math.round(targetQ * ease);
    drawLeche();
    if (u < 1) animLcId = requestAnimationFrame(step);
  }
  animLcId = requestAnimationFrame(step);
}
function drawLeche() {
  const A = +document.getElementById("lc-a").value;
  const B = +document.getElementById("lc-b").value;
  const C = +document.getElementById("lc-c").value;
  const D = +document.getElementById("lc-d").value;
  const Qp = +document.getElementById("lc-q").value;

  document.getElementById("lc-a-v").textContent = fmtInt(A);
  document.getElementById("lc-b-v").textContent = fmtDec(B, 4);
  document.getElementById("lc-c-v").textContent = fmtInt(C);
  document.getElementById("lc-d-v").textContent = fmtDec(D, 4);
  document.getElementById("lc-q-v").textContent = fmtInt(Qp) + " t";

  const q0 = (A - C) / (B + D);
  const p0 = A - B * q0;
  const q1 = (A - C + D * Qp) / (B + D);
  const p1 = A - B * q1;
  const qo1 = q1 - Qp;

  const ad = 0.5 * (p0 + p1) * (q1 - q0);
  const lr = 0.5 * (p0 + p1) * (q0 - qo1);
  const vsp = ad + lr;
  const pSoc = Qp > 0 ? vsp / Qp : p0;

  document.getElementById("lc-k-e0").textContent = `${fmtInt(q0)} t | $${fmtDec(p0, 1)}`;
  document.getElementById("lc-k-e1").textContent = `${fmtInt(q1)} t | $${fmtDec(p1, 1)}`;
  document.getElementById("lc-k-dp").textContent = `Caída ΔP = -$${fmtDec(Math.abs(p0 - p1), 2)}/t`;
  document.getElementById("lc-k-ad").textContent = "$" + fmtInt(ad);
  document.getElementById("lc-k-adp").textContent = `${vsp > 0 ? fmtDec(ad / vsp * 100, 1) : "0,0"}% del VSP`;
  document.getElementById("lc-k-lr").textContent = "$" + fmtInt(lr);
  document.getElementById("lc-k-lrp").textContent = `${vsp > 0 ? fmtDec(lr / vsp * 100, 1) : "0,0"}% del VSP`;
  document.getElementById("lc-k-vsp").textContent = "$" + fmtInt(vsp);
  document.getElementById("lc-k-ps").textContent = `P* = $${fmtDec(pSoc, 2)} / ton`;

  const svg = document.getElementById("svg-leche");
  svg.innerHTML = "";
  addDefs(svg);

  const M = { l: 64, r: 30, t: 28, b: 48 };
  const W = 960, H = 410;
  const minX = 2000, maxX = 12500, maxY = 320;
  const sx = v => M.l + ((v - minX) / (maxX - minX)) * (W - M.l - M.r);
  const sy = v => H - M.b - (v / maxY) * (H - M.t - M.b);

  for (let y = 0; y <= 300; y += 50) {
    el("line", { x1: M.l, y1: sy(y), x2: W - M.r, y2: sy(y), stroke: "#E2E8F0", "stroke-width": "1" }, svg);
    const t = el("text", { x: M.l - 8, y: sy(y) + 4, fill: "#475569", "font-size": "11", "text-anchor": "end" }, svg);
    t.textContent = "$" + y;
  }
  for (let x = 2000; x <= 12000; x += 2000) {
    el("line", { x1: sx(x), y1: M.t, x2: sx(x), y2: H - M.b, stroke: "#F1F5F9", "stroke-width": "1" }, svg);
    const t = el("text", { x: sx(x), y: H - M.b + 16, fill: "#475569", "font-size": "11", "text-anchor": "middle" }, svg);
    t.textContent = (x / 1000) + "k";
  }
  el("line", { x1: M.l, y1: H - M.b, x2: W - M.r, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);
  el("line", { x1: M.l, y1: M.t, x2: M.l, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);

  // Rastro fantasma del equilibrio anterior
  const gq1 = (ghostLc.A - ghostLc.C + ghostLc.D * ghostLc.Q) / (ghostLc.B + ghostLc.D);
  const gp1 = ghostLc.A - ghostLc.B * gq1;
  if (Math.abs(Qp - ghostLc.Q) >= 30 || Math.abs(C - ghostLc.C) >= 5) {
    el("line", { x1: sx(minX), y1: sy(ghostLc.C + ghostLc.D * (minX - ghostLc.Q)), x2: sx(maxX), y2: sy(ghostLc.C + ghostLc.D * (maxX - ghostLc.Q)), stroke: "#94A3B8", "stroke-width": "1.5", "stroke-dasharray": "4,4" }, svg);
    el("circle", { cx: sx(gq1), cy: sy(gp1), r: 4, fill: "#94A3B8" }, svg);
  }

  // Polígonos LR y AD
  if (Qp > 5) {
    const lrPts = `${sx(qo1)},${sy(0)} ${sx(q0)},${sy(0)} ${sx(q0)},${sy(p0)} ${sx(qo1)},${sy(p1)}`;
    el("polygon", { points: lrPts, fill: "rgba(37,99,235,0.28)", stroke: "#1D4ED8", "stroke-width": "1.6" }, svg);
    const adPts = `${sx(q0)},${sy(0)} ${sx(q1)},${sy(0)} ${sx(q1)},${sy(p1)} ${sx(q0)},${sy(p0)}`;
    el("polygon", { points: adPts, fill: "rgba(220,38,38,0.28)", stroke: "#DC2626", "stroke-width": "1.6" }, svg);
  }

  // Curvas D, O y O'
  el("line", { x1: sx(minX), y1: sy(A - B * minX), x2: sx(maxX), y2: sy(A - B * maxX), stroke: "#0F172A", "stroke-width": "2.6" }, svg);
  el("line", { x1: sx(minX), y1: sy(C + D * minX), x2: sx(maxX), y2: sy(C + D * maxX), stroke: "#1D4ED8", "stroke-width": "2.4" }, svg);
  if (Qp > 5) {
    el("line", { x1: sx(minX), y1: sy(C + D * (minX - Qp)), x2: sx(maxX), y2: sy(C + D * (maxX - Qp)), stroke: "#15803D", "stroke-width": "2.6", "stroke-dasharray": "7,4" }, svg);
  }

  // Líneas punteadas hacia el eje Y
  el("line", { x1: M.l, y1: sy(p0), x2: sx(q0), y2: sy(p0), stroke: "#94A3B8", "stroke-dasharray": "3,3" }, svg);
  if (Qp > 5) el("line", { x1: M.l, y1: sy(p1), x2: sx(q1), y2: sy(p1), stroke: "#15803D", "stroke-dasharray": "3,3" }, svg);

  // Puntos E0 y E1
  el("circle", { cx: sx(q0), cy: sy(p0), r: 5.5, fill: "#0F172A" }, svg);
  const tE0 = el("text", { x: sx(q0), y: sy(p0) - 10, fill: "#0F172A", "font-size": "11", "font-weight": "700", "text-anchor": "middle" }, svg);
  tE0.textContent = `E0 (${fmtInt(q0)}; $${fmtDec(p0, 0)})`;

  if (Qp > 5) {
    el("circle", { cx: sx(q1), cy: sy(p1), r: 5.5, fill: "#15803D", stroke: "#FFFFFF", "stroke-width": "1.5" }, svg);
    // FLECHA VERDE DESPLAZAMIENTO OFERTA O -> O'
    const yArrO = Math.min(275, p0 + 75);
    const xO0 = (yArrO - C) / D;
    const xO1 = xO0 + Qp;
    if (xO0 > minX + 200 && xO1 < maxX - 200) {
      drawArrow(svg, sx(xO0), sy(yArrO), sx(xO1), sy(yArrO), "#15803D", "arr-green", `O → O' (+${fmtInt(Qp)} t)`, (sx(xO0) + sx(xO1)) / 2, sy(yArrO) - 10);
    }
    // FLECHA VERTICAL CAÍDA DE PRECIO P0 -> P1
    drawArrow(svg, M.l + 26, sy(p0), M.l + 26, sy(p1), "#DC2626", "arr-red", `↓ -$${fmtDec(p0 - p1, 1)}`, M.l + 34, (sy(p0) + sy(p1)) / 2 + 4, "start");
    // FLECHAS HORIZONTALES LR Y AD
    drawArrow(svg, sx(q0) - 2, sy(22), sx(qo1) + 2, sy(22), "#1D4ED8", "arr-blue", `← LR`, (sx(q0) + sx(qo1)) / 2, sy(42));
    drawArrow(svg, sx(q0) + 2, sy(22), sx(q1) - 2, sy(22), "#DC2626", "arr-red", `AD →`, (sx(q0) + sx(q1)) / 2, sy(42));
  }
}

// ============================================================================
// 3. SIMULADOR ELASTICIDADES EXTREMAS (60 FPS + FLECHAS EN VIVO)
// ============================================================================
function setElast(rd, ro) {
  document.getElementById("el-rd").value = rd;
  document.getElementById("el-ro").value = ro;
  drawElast();
}
function slopeFromRig(r) {
  if (r <= 0) return 1e-5;
  if (r >= 100) return 1e5;
  return Math.tan((r / 100) * 85 * Math.PI / 180) * 0.12;
}
function drawElast() {
  const rd = +document.getElementById("el-rd").value;
  const ro = +document.getElementById("el-ro").value;
  const dq = +document.getElementById("el-dq").value;
  document.getElementById("el-rd-v").textContent = rd;
  document.getElementById("el-ro-v").textContent = ro;
  document.getElementById("el-dq-v").textContent = dq;

  const bd = slopeFromRig(rd), d_o = slopeFromRig(ro);
  const q0 = 1000, p0 = 100;
  const fracAD = d_o / (bd + d_o);
  const fracLR = bd / (bd + d_o);
  const q1 = q0 + fracAD * dq;
  const qo1 = q0 - fracLR * dq;
  const p1 = Math.max(8, p0 - (bd * d_o / (bd + d_o)) * dq);

  document.getElementById("el-k-ad").textContent = fmtDec(fracAD * 100, 1) + "%";
  document.getElementById("el-k-lr").textContent = fmtDec(fracLR * 100, 1) + "%";
  document.getElementById("el-k-p").textContent = `$${p0} → $${fmtDec(p1, 1)}`;
  document.getElementById("el-k-dp").textContent = `Caída ΔP = -$${fmtDec(p0 - p1, 1)}`;

  const svg = document.getElementById("svg-elast");
  svg.innerHTML = "";
  addDefs(svg);

  const M = { l: 64, r: 170, t: 24, b: 44 };
  const W = 960, H = 390;
  const minX = 300, maxX = 1700, maxY = 195;
  const sx = v => M.l + ((v - minX) / (maxX - minX)) * (W - M.l - M.r);
  const sy = v => H - M.b - (v / maxY) * (H - M.t - M.b);

  el("line", { x1: M.l, y1: H - M.b, x2: W - M.r, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);
  el("line", { x1: M.l, y1: M.t, x2: M.l, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);

  if (q0 - qo1 > 2) {
    el("polygon", { points: `${sx(qo1)},${sy(0)} ${sx(q0)},${sy(0)} ${sx(q0)},${sy(p0)} ${sx(qo1)},${sy(p1)}`, fill: "rgba(37,99,235,0.30)", stroke: "#1D4ED8", "stroke-width": "1.5" }, svg);
  }
  if (q1 - q0 > 2) {
    el("polygon", { points: `${sx(q0)},${sy(0)} ${sx(q1)},${sy(0)} ${sx(q1)},${sy(p1)} ${sx(q0)},${sy(p0)}`, fill: "rgba(220,38,38,0.30)", stroke: "#DC2626", "stroke-width": "1.5" }, svg);
  }

  // Demanda
  if (rd >= 99) {
    el("line", { x1: sx(q0), y1: sy(0), x2: sx(q0), y2: sy(190), stroke: "#0F172A", "stroke-width": "3" }, svg);
  } else {
    el("line", { x1: sx(minX), y1: sy(p0 - bd * (minX - q0)), x2: sx(maxX), y2: sy(p0 - bd * (maxX - q0)), stroke: "#0F172A", "stroke-width": "2.8" }, svg);
  }
  // Oferta O y O'
  if (ro >= 99) {
    el("line", { x1: sx(q0), y1: sy(0), x2: sx(q0), y2: sy(190), stroke: "#1D4ED8", "stroke-width": "2.6" }, svg);
    el("line", { x1: sx(q0 + dq), y1: sy(0), x2: sx(q0 + dq), y2: sy(190), stroke: "#15803D", "stroke-width": "2.6", "stroke-dasharray": "6,4" }, svg);
  } else {
    el("line", { x1: sx(minX), y1: sy(p0 + d_o * (minX - q0)), x2: sx(maxX), y2: sy(p0 + d_o * (maxX - q0)), stroke: "#1D4ED8", "stroke-width": "2.6" }, svg);
    el("line", { x1: sx(minX), y1: sy(p0 + d_o * (minX - q0 - dq)), x2: sx(maxX), y2: sy(p0 + d_o * (maxX - q0 - dq)), stroke: "#15803D", "stroke-width": "2.6", "stroke-dasharray": "6,4" }, svg);
  }

  // Flechas LR, AD y ΔP
  if (q0 - qo1 > 12) drawArrow(svg, sx(q0) - 2, sy(18), sx(qo1) + 2, sy(18), "#1D4ED8", "arr-blue", `← LR`, (sx(q0) + sx(qo1)) / 2, sy(35));
  if (q1 - q0 > 12) drawArrow(svg, sx(q0) + 2, sy(18), sx(q1) - 2, sy(18), "#DC2626", "arr-red", `AD →`, (sx(q0) + sx(q1)) / 2, sy(35));
  if (p0 - p1 > 3) drawArrow(svg, M.l + 22, sy(p0), M.l + 22, sy(p1), "#0F172A", "arr-dark", `↓ -$${fmtDec(p0 - p1, 0)}`, M.l + 30, (sy(p0) + sy(p1)) / 2 + 4, "start");

  // Barra lateral apilada en tiempo real (% AD vs % LR)
  const bx = W - 125, bw = 82, bh = H - M.t - M.b;
  const hAD = bh * fracAD, hLR = bh * fracLR;
  el("rect", { x: bx, y: M.t, width: bw, height: hAD, fill: "#DC2626", rx: 2 }, svg);
  el("rect", { x: bx, y: M.t + hAD, width: bw, height: hLR, fill: "#1D4ED8", rx: 2 }, svg);
  if (fracAD > 0.12) {
    const t1 = el("text", { x: bx + bw / 2, y: M.t + hAD / 2 + 4, fill: "#FFFFFF", "font-size": "12", "font-weight": "800", "text-anchor": "middle" }, svg);
    t1.textContent = `${fmtDec(fracAD * 100, 0)}% AD`;
  }
  if (fracLR > 0.12) {
    const t2 = el("text", { x: bx + bw / 2, y: M.t + hAD + hLR / 2 + 4, fill: "#FFFFFF", "font-size": "12", "font-weight": "800", "text-anchor": "middle" }, svg);
    t2.textContent = `${fmtDec(fracLR * 100, 0)}% LR`;
  }
  const tTit = el("text", { x: bx + bw / 2, y: M.t - 8, fill: "#0F172A", "font-size": "11.5", "font-weight": "700", "text-anchor": "middle" }, svg);
  tTit.textContent = "Peso VSP";
}

drawTransporte();
</script>
</body>
</html>
"""


def renderizar_simuladores_fluidos_60fps():
    """Renderiza el motor interactivo a 60 FPS en el navegador sin recargar Streamlit."""
    st.markdown(
        "<div class='sec-header'>MOTOR FLUIDO A 60 FPS (SIN RECARGA DE SERVIDOR) — FLECHAS VECTORIALES Y RASTRO FANTASMA</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Mueve cualquier deslizador con fluidez instantánea: el gráfico deja una silueta punteada gris de tu referencia anterior "
        "y dibuja flechas vectoriales indicando hacia dónde y cuánto se desplazó cada curva o área."
    )
    components.html(HTML_SIMULADOR_FLUIDO, height=740, scrolling=True)
