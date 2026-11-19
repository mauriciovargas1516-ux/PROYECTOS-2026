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
  /* === HOJA DE ENTRENAMIENTO MECÁNICO (MODO COPIA / CIEGO + IMPRESIÓN CARTA) === */
  .mec-toolbar {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
    background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px;
  }
  .mec-filters { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
  .flt-btn {
    border: 1px solid #CBD5E1; background: #FFFFFF; color: #334155;
    padding: 4px 10px; border-radius: 14px; font-size: 11.5px; font-weight: 700; cursor: pointer;
  }
  .flt-btn.active { background: #1E293B; color: #FFFFFF; border-color: #1E293B; }
  .pill-score {
    background: #0F172A; color: #FFFFFF; padding: 5px 11px; border-radius: 14px;
    font-size: 12px; font-weight: 700; font-family: Consolas, monospace;
  }
  .mec-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; margin-bottom: 14px; }
  @media (max-width: 780px) { .mec-grid { grid-template-columns: 1fr; } }
  .f-card {
    border: 1px solid #CBD5E1; border-left: 3.5px solid #1E293B; border-radius: 6px;
    background: #FFFFFF; padding: 9px 11px; position: relative; transition: border-color 0.15s ease;
  }
  .f-card.mastered { border-left-color: #15803D; background: #F0FDF4; }
  .f-head { display: flex; justify-content: space-between; align-items: center; gap: 6px; margin-bottom: 5px; }
  .f-title { font-size: 12px; font-weight: 800; color: #0F172A; }
  .f-cat { font-size: 10px; font-weight: 700; color: #475569; background: #E2E8F0; padding: 2px 6px; border-radius: 4px; }
  .chk-btn {
    border: 1px solid #94A3B8; background: #FFFFFF; color: #475569; width: 22px; height: 22px;
    border-radius: 4px; font-size: 12px; font-weight: 800; cursor: pointer; line-height: 1; padding: 0;
  }
  .f-card.mastered .chk-btn { background: #15803D; color: #FFFFFF; border-color: #15803D; }
  .f-body {
    background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 4px; padding: 7px 9px;
    cursor: pointer; min-height: 44px; display: flex; flex-direction: column; justify-content: center;
  }
  .f-eq {
    font-family: "Cambria Math", "Times New Roman", Georgia, serif;
    font-size: 14.5px; font-weight: 700; color: #0F172A; letter-spacing: 0.2px;
    display: flex; align-items: center; flex-wrap: wrap; gap: 4px;
  }
  .f-rule { font-size: 11px; color: #334155; margin-top: 5px; line-height: 1.32; }
  .frac {
    display: inline-flex; flex-direction: column; align-items: center;
    vertical-align: middle; margin: 0 2px; font-size: 0.88em; line-height: 1.1;
  }
  .frac .num { border-bottom: 1.4px solid #0F172A; padding: 0 3px 1px 3px; text-align: center; }
  .frac .den { padding: 1px 3px 0 3px; text-align: center; }
  .blind-cover { display: none; font-size: 11.5px; font-weight: 700; color: #1D4ED8; text-align: center; padding: 4px 0; }
  .blind-mode .f-card:not(.revealed) .f-eq,
  .blind-mode .f-card:not(.revealed) .f-rule { display: none; }
  .blind-mode .f-card:not(.revealed) .blind-cover { display: block; }
  .skel-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
  @media (max-width: 860px) { .skel-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 560px) { .skel-grid { grid-template-columns: 1fr; } }
  .s-card {
    border: 1px solid #CBD5E1; border-radius: 6px; background: #FFFFFF; padding: 8px 9px; cursor: pointer;
  }
  .s-title { font-size: 11.5px; font-weight: 800; color: #0F172A; margin-bottom: 4px; display: flex; justify-content: space-between; }
  .s-sub { font-size: 10.5px; color: #475569; margin-top: 4px; line-height: 1.3; }
  .blind-mode .s-card:not(.revealed) .sk-lbl { opacity: 0; }
  .blind-mode .s-card:not(.revealed) .s-sub { visibility: hidden; }
  .s-card .sk-lbl { transition: opacity 0.15s ease; }

  @media print {
    body { background: #FFFFFF !important; }
    .top-tabs, .mec-toolbar, .mec-filters, .btn-bar, .chk-btn, .note-box { display: none !important; }
    .panel { display: none !important; border: none !important; padding: 0 !important; }
    #panel-mecanica { display: block !important; }
    .sec-title { background: #F1F5F9 !important; color: #000000 !important; border-left: 3px solid #000000 !important; padding: 4px 8px !important; margin-bottom: 6px !important; font-size: 11px !important; }
    .mec-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 6px !important; }
    .f-card { break-inside: avoid; border: 1px solid #94A3B8 !important; border-left: 3px solid #000000 !important; padding: 5px 7px !important; background: #FFFFFF !important; }
    .f-body { border: none !important; background: transparent !important; padding: 2px 0 !important; min-height: auto !important; }
    .f-eq { font-size: 12px !important; }
    .f-rule { font-size: 9.5px !important; }
    .blind-mode .f-card .f-eq, .blind-mode .f-card .f-rule { display: flex !important; }
    .blind-mode .f-card .f-rule { display: block !important; }
    .blind-mode .f-card .blind-cover { display: none !important; }
    .blind-mode .s-card .sk-lbl { opacity: 1 !important; }
    .blind-mode .s-card .s-sub { visibility: visible !important; }
    .skel-grid { grid-template-columns: repeat(3, 1fr) !important; gap: 6px !important; }
    .s-card { break-inside: avoid; border: 1px solid #94A3B8 !important; padding: 5px !important; }
  }
</style>
</head>
<body>
<div class="wrap">
  <div class="top-tabs">
    <button class="tab-btn active" onclick="openTab('transporte', this)">1. Transporte y Externalidades (60 FPS + Flechas)</button>
    <button class="tab-btn" onclick="openTab('leche', this)">2. Mercado de la Leche (Animación O → O' + Flechas)</button>
    <button class="tab-btn" onclick="openTab('elasticidad', this)">3. Elasticidades Extremas (Deformación en Vivo)</button>
    <button class="tab-btn" onclick="openTab('mecanica', this)">4. Hoja de Entrenamiento Mecánico (Plana + Modo Ciego)</button>
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

  <!-- ====================================================================== -->
  <!-- PANEL 4: HOJA DE ENTRENAMIENTO MECÁNICO (FÓRMULAS + ESQUELETOS SVG)    -->
  <!-- ====================================================================== -->
  <div id="panel-mecanica" class="panel">
    <div class="sec-title">
      <span>HOJA DE ENTRENAMIENTO MECÁNICO — EVALUACIÓN INTEGRADA DE PROYECTOS (FDIC26 / SNI 2026)</span>
      <div class="btn-bar">
        <button id="btn-modo-copia" class="act-btn primary" onclick="setModoMec(false)">Modo Copia (Todo Visible)</button>
        <button id="btn-modo-ciego" class="act-btn" onclick="setModoMec(true)">Modo Ciego (Autoevaluación)</button>
        <button class="act-btn" onclick="resetDominadas()">Reiniciar ✓</button>
        <button class="act-btn" onclick="window.print()">Imprimir / Guardar PDF (Carta)</button>
      </div>
    </div>

    <div class="mec-toolbar">
      <div style="font-size:12px;color:#334155;">
        <b>Método de cuaderno:</b> copia cada fórmula y esqueleto a mano varias veces; luego activa <b>Modo Ciego</b>, escríbelos sin mirar y haz clic en cada recuadro para comprobar y marcar <b>✓</b>.
      </div>
      <span id="mec-score" class="pill-score">Dominadas: 0 / 16</span>
    </div>

    <div class="mec-filters">
      <button class="flt-btn active" onclick="filtrarMec('all', this)">Todas (16)</button>
      <button class="flt-btn" onclick="filtrarMec('ps', this)">I. Precios Sociales 2026 (5)</button>
      <button class="flt-btn" onclick="filtrarMec('vsp', this)">II. Microeconomía VSP / Harberger (3)</button>
      <button class="flt-btn" onclick="filtrarMec('eval', this)">III. Privada, VAC/CAE y Jerarquía (5)</button>
      <button class="flt-btn" onclick="filtrarMec('dem', this)">IV. Población, Ambiental y MML (3)</button>
    </div>

    <div id="mec-container">
      <div class="mec-grid" id="mec-formulas-grid"></div>

      <div class="sec-title" style="margin-top:6px;">
        <span>ESQUELETOS DE GRÁFICAS PARA COPIAR A MANO EN CUADERNO (6 DIAGRAMAS CLAVE DE EXAMEN)</span>
        <span style="font-size:11px;font-weight:600;color:#334155;">En Modo Ciego, haz clic en cada gráfico para revelar las etiquetas</span>
      </div>
      <div class="skel-grid" id="mec-skel-grid"></div>
    </div>
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
  if (name === "mecanica") renderMecanica();
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


// ============================================================================
// 4. HOJA DE ENTRENAMIENTO MECÁNICO (16 FÓRMULAS PURAS + 6 ESQUELETOS SVG)
// ============================================================================
const FORMULAS_PROY = [
  { id: 1, cat: "ps", tag: "SNI 2026", title: "1. Tasa Social de Descuento (TSD)",
    eq: `TSD = β·t<sub>p</sub> + φ·q + α·C<sub>mgx</sub> = <b>5,5%</b>`,
    rule: "Pondera ahorro interno (t_p), rentabilidad privada desplazada (q) y costo marginal del ahorro externo (C_mgx)." },
  { id: 2, cat: "ps", tag: "SNI 2026", title: "2. Precio Social Mano de Obra (PSMO)",
    eq: `PSMO = Salario<sub>Bruto</sub> × FCSMO`,
    rule: "MOC = 0,97 · MOSC = 0,95 (choferes/operadores CIUO-08) · MONC = 0,91. Siempre ≤ salario privado." },
  { id: 3, cat: "ps", tag: "SNI 2026", title: "3. Factor Social de la Divisa (FCSD)",
    eq: `FCSD = <span class="frac"><span class="num">θX − μM(1 + t)</span><span class="den">θX − μM</span></span> = <b>1,00</b>`,
    rule: "PSD = TC_obs × FCSD. En maquinaria importada se descuenta IVA (19%) y arancel (6%) por ser transferencias." },
  { id: 4, cat: "ps", tag: "SNI 2026", title: "4. Valor Social del Tiempo (VST Urbano)",
    eq: `VST<sub>urb</sub> = α·VTT + β·VTC + γ·VTO`,
    rule: "α=3,4% trab · β=27,2% commute · γ=69,4% otros. Vehículo (1x) = $3.338/h · Espera/Caminata (2x) = $6.676/h · Recreación = $2.792/h." },
  { id: 5, cat: "ps", tag: "SNI 2026", title: "5. Precio Social de Combustibles",
    eq: `PS<sub>comb</sub> = <span class="frac"><span class="num">PM − (IE<sup>F</sup> + IE<sup>V</sup>)·UTM/1000</span><span class="den">(1 + IVA)(1 + t<sub>a</sub>)</span></span> · FCSD`,
    rule: "Quita impuestos específicos, IVA y arancel. Oficial 2026: Diésel = $805/L · Gas 93 = $737/L · VVE = $2.383.677.600." },

  { id: 6, cat: "vsp", tag: "Fontaine", title: "6. Valor Social de la Producción (VSP)",
    eq: `VSP = AD + LR = VPP + ΔEC + ΔEP`,
    rule: "AD = rectángulo P1·ΔQd + triángulo consumidor; LR = rectángulo P1·ΔQo + triángulo productor. Eficiencia = Agencia." },
  { id: 7, cat: "vsp", tag: "Fontaine", title: "7. Precio Social Unitario y Regla del IVA",
    eq: `P* = <span class="frac"><span class="num">VSP</span><span class="den">Q<sub>proy</sub></span></span> = <span class="frac"><span class="num">P<sub>0</sub> + P<sub>1</sub></span><span class="den">2</span></span>`,
    rule: "Regla de examen: Curva de Demanda INCLUYE IVA; Curva de Oferta es Cmg de producción SIN IVA. Leche (-50): P* = $134/t." },
  { id: 8, cat: "vsp", tag: "Harberger", title: "8. Bienes Transables (Importable / Exportable)",
    eq: `p*<sub>imp</sub> = p<sub>priv</sub><span class="frac"><span class="num">r*</span><span class="den">r(1+t<sub>M</sub>)</span></span> + f &nbsp;|&nbsp; p*<sub>exp</sub> = p<sub>priv</sub><span class="frac"><span class="num">r*</span><span class="den">r(1+s)</span></span> − f`,
    rule: "Importables a precio internacional CIF ajustado + flete interno (sin arancel t_M); Exportables a FOB ajustado − flete." },

  { id: 9, cat: "eval", tag: "1° Prioridad", title: "9. Valor Actual Neto (Criterio Rector)",
    eq: `VAN = −I<sub>0</sub> + ∑<sub>t=1..n</sub> <span class="frac"><span class="num">F<sub>t</sub></span><span class="den">(1 + k)<sup>t</sup></span></span>`,
    rule: "1° prioridad CEPAL/SNI (VAN > 0). Cumple aditividad y separabilidad. VANS descuenta beneficios netos sociales a TSD = 5,5%." },
  { id: 10, cat: "eval", tag: "SNI", title: "10. Costo-Eficiencia: VAC y CAE",
    eq: `VAC = ∑ <span class="frac"><span class="num">C<sub>t</sub></span><span class="den">(1+r)<sup>t</sup></span></span> &nbsp;|&nbsp; CAE = VAC · <span class="frac"><span class="num">r(1+r)<sup>n</sup></span><span class="den">(1+r)<sup>n</sup> − 1</span></span>`,
    rule: "Igual vida útil + beneficios iguales → menor VAC. Distinta vida útil o distinto volumen → menor CAE (o CAE/ton GIRS)." },
  { id: 11, cat: "eval", tag: "Flujo Deuda", title: "11. Cuota Francesa y Escudo Fiscal",
    eq: `Cuota = P · <span class="frac"><span class="num">r(1+r)<sup>n</sup></span><span class="den">(1+r)<sup>n</sup> − 1</span></span> &nbsp;|&nbsp; EF<sub>t</sub> = Int<sub>t</sub>·t<sub>imp</sub>`,
    rule: "Solo los intereses se restan antes de impuestos (escudo fiscal); la amortización se descuenta después en Flujo de Capitales." },
  { id: 12, cat: "eval", tag: "Operación", title: "12. Capital de Trabajo y Costos Hundidos",
    eq: `CT<sub>0</sub> = <span class="frac"><span class="num">C<sub>Anual</sub> · d<sub>desfase</sub></span><span class="den">365</span></span>`,
    rule: "Se inyecta en t=0 y se recupera íntegro en t=n. Costos hundidos pasados (ej. avión US$ 1.000M) son irrecuperables y NO entran." },
  { id: 13, cat: "eval", tag: "Finanzas", title: "13. Tasa Efectiva (TEA), CAPM y Jerarquía",
    eq: `TEA = (1 + TNA·<span class="frac"><span class="num">t</span><span class="den">365</span></span>)<sup>365/t</sup> − 1 &nbsp;|&nbsp; E(R<sub>i</sub>) = R<sub>f</sub> + β[E(R<sub>m</sub>) − R<sub>f</sub>]`,
    rule: "Jerarquía estricta CEPAL: 1° VAN → 2° Tasas (WACC/CAPM/TSD) → 3° TIR (falla en escala) → 4° Riesgo/β → 5° Payback." },

  { id: 14, cat: "dem", tag: "CEPAL 39", title: "14. Proyección Poblacional y Déficit",
    eq: `P<sub>t</sub> = P<sub>0</sub>·(1 + r)<sup>t</sup> &nbsp;|&nbsp; Déficit<sub>t</sub> = Demanda<sub>t</sub> − Oferta<sub>t</sub>`,
    rule: "Embudo SNI: Pob. Referencia ⊃ Pob. Afectada ⊃ Pob. Objetivo. Primero se evalúa la Situación Base Optimizada." },
  { id: 15, cat: "dem", tag: "Terreno", title: "15. Investigación de Campo Poblacional",
    eq: `PHP = V · (P/V)<sub>m</sub> &nbsp;|&nbsp; PT = PHP + PHC`,
    rule: "Viviendas (V) × personas/vivienda muestral = Hogares Particulares (PHP); luego se suman Hogares Colectivos (PHC)." },
  { id: 16, cat: "dem", tag: "RA2 / MML", title: "16. Carbono Equivalente (GEI) y Marco Lógico",
    eq: `CO<sub>2</sub>eq = t<sub>CO2</sub> + 28·t<sub>CH4</sub> + 265·t<sub>N2O</sub> &nbsp;|&nbsp; P<sub>CO2</sub> = $71.801/t`,
    rule: "Problema nunca es 'falta de solución' (caso Macondo). Un único Propósito; Actividades NO llevan supuestos en la MML." }
];

const ESQUELETOS_PROY = [
  {
    title: "1. Mercado del Producto (VSP = AD + LR)",
    sub: "Oferta se desplaza O → O'; baja P0 → P1; bloque izq = LR, bloque der = AD.",
    svg: `<svg viewBox="0 0 260 155">
      <line x1="28" y1="132" x2="245" y2="132" stroke="#0F172A" stroke-width="1.6"/>
      <line x1="28" y1="12" x2="28" y2="132" stroke="#0F172A" stroke-width="1.6"/>
      <text x="16" y="20" font-size="10" font-weight="700" fill="#0F172A">P</text>
      <text x="236" y="146" font-size="10" font-weight="700" fill="#0F172A">Q</text>
      <polygon points="104,132 132,132 132,68 104,88" fill="rgba(37,99,235,0.25)" stroke="#1D4ED8" stroke-width="1"/>
      <polygon points="132,132 166,132 166,88 132,68" fill="rgba(220,38,38,0.25)" stroke="#DC2626" stroke-width="1"/>
      <line x1="45" y1="22" x2="225" y2="122" stroke="#0F172A" stroke-width="2"/>
      <line x1="50" y1="126" x2="188" y2="28" stroke="#1D4ED8" stroke-width="1.8"/>
      <line x1="95" y1="128" x2="230" y2="34" stroke="#15803D" stroke-width="2" stroke-dasharray="5,3"/>
      <line x1="28" y1="68" x2="132" y2="68" stroke="#94A3B8" stroke-dasharray="3,2"/>
      <line x1="28" y1="88" x2="166" y2="88" stroke="#94A3B8" stroke-dasharray="3,2"/>
      <g class="sk-lbl" font-size="9.5" font-weight="700">
        <text x="10" y="71" fill="#0F172A">P0</text><text x="10" y="91" fill="#15803D">P1</text>
        <text x="96" y="145" fill="#1D4ED8">Qo1</text><text x="126" y="145" fill="#0F172A">Q0</text><text x="160" y="145" fill="#DC2626">Q1</text>
        <text x="112" y="114" fill="#1E3A8A">LR</text><text x="142" y="114" fill="#991B1B">AD</text>
        <text x="184" y="25" fill="#1D4ED8">O</text><text x="228" y="34" fill="#15803D">O'</text><text x="224" y="118" fill="#0F172A">D</text>
      </g>
    </svg>`
  },
  {
    title: "2. Extremos VSP = 100% AD (ηd=∞ | ηo=0)",
    sub: "Izq: D horizontal (P0 fijo) → todo es AD. Der: O vertical → todo es AD.",
    svg: `<svg viewBox="0 0 260 155">
      <line x1="18" y1="130" x2="120" y2="130" stroke="#0F172A" stroke-width="1.4"/>
      <line x1="18" y1="18" x2="18" y2="130" stroke="#0F172A" stroke-width="1.4"/>
      <rect x="58" y="66" width="38" height="64" fill="rgba(220,38,38,0.25)" stroke="#DC2626"/>
      <line x1="18" y1="66" x2="115" y2="66" stroke="#0F172A" stroke-width="2.2"/>
      <line x1="25" y1="120" x2="86" y2="24" stroke="#1D4ED8" stroke-width="1.6"/>
      <line x1="63" y1="120" x2="118" y2="30" stroke="#15803D" stroke-width="1.8" stroke-dasharray="4,3"/>
      <line x1="145" y1="130" x2="248" y2="130" stroke="#0F172A" stroke-width="1.4"/>
      <line x1="145" y1="18" x2="145" y2="130" stroke="#0F172A" stroke-width="1.4"/>
      <polygon points="184,130 218,130 218,86 184,60" fill="rgba(220,38,38,0.25)" stroke="#DC2626"/>
      <line x1="184" y1="22" x2="184" y2="130" stroke="#1D4ED8" stroke-width="2"/>
      <line x1="218" y1="22" x2="218" y2="130" stroke="#15803D" stroke-width="2" stroke-dasharray="4,3"/>
      <line x1="152" y1="35" x2="244" y2="106" stroke="#0F172A" stroke-width="2"/>
      <g class="sk-lbl" font-size="9" font-weight="700">
        <text x="68" y="102" fill="#991B1B">AD</text><text x="24" y="14" fill="#0F172A">ηd = ∞ (D horiz.)</text>
        <text x="193" y="108" fill="#991B1B">AD</text><text x="150" y="14" fill="#0F172A">ηo = 0 (O vert.)</text>
        <text x="48" y="144" fill="#0F172A">VSP = AD</text><text x="178" y="144" fill="#0F172A">VSP = AD</text>
      </g>
    </svg>`
  },
  {
    title: "3. Extremos VSP = 100% LR (ηo=∞ | ηd=0)",
    sub: "Izq: O horizontal (P0 fijo) → todo es LR. Der: D vertical → todo es LR.",
    svg: `<svg viewBox="0 0 260 155">
      <line x1="18" y1="130" x2="120" y2="130" stroke="#0F172A" stroke-width="1.4"/>
      <line x1="18" y1="18" x2="18" y2="130" stroke="#0F172A" stroke-width="1.4"/>
      <rect x="44" y="66" width="34" height="64" fill="rgba(37,99,235,0.25)" stroke="#1D4ED8"/>
      <line x1="18" y1="66" x2="115" y2="66" stroke="#1D4ED8" stroke-width="2.2"/>
      <line x1="36" y1="22" x2="108" y2="112" stroke="#0F172A" stroke-width="2"/>
      <line x1="145" y1="130" x2="248" y2="130" stroke="#0F172A" stroke-width="1.4"/>
      <line x1="145" y1="18" x2="145" y2="130" stroke="#0F172A" stroke-width="1.4"/>
      <polygon points="172,130 206,130 206,62 172,92" fill="rgba(37,99,235,0.25)" stroke="#1D4ED8"/>
      <line x1="206" y1="22" x2="206" y2="130" stroke="#0F172A" stroke-width="2.2"/>
      <line x1="150" y1="112" x2="232" y2="38" stroke="#1D4ED8" stroke-width="1.8"/>
      <line x1="176" y1="120" x2="246" y2="56" stroke="#15803D" stroke-width="1.8" stroke-dasharray="4,3"/>
      <g class="sk-lbl" font-size="9" font-weight="700">
        <text x="54" y="102" fill="#1E3A8A">LR</text><text x="24" y="14" fill="#0F172A">ηo = ∞ (O horiz.)</text>
        <text x="183" y="110" fill="#1E3A8A">LR</text><text x="150" y="14" fill="#0F172A">ηd = 0 (D vert.)</text>
        <text x="48" y="144" fill="#0F172A">VSP = LR</text><text x="178" y="144" fill="#0F172A">VSP = LR</text>
      </g>
    </svg>`
  },
  {
    title: "4. Externalidad Negativa (CmgS > CmgP)",
    sub: "El costo social está sobre el privado; la franja es daño a terceros.",
    svg: `<svg viewBox="0 0 260 155">
      <line x1="28" y1="132" x2="245" y2="132" stroke="#0F172A" stroke-width="1.6"/>
      <line x1="28" y1="12" x2="28" y2="132" stroke="#0F172A" stroke-width="1.6"/>
      <rect x="28" y="86" width="144" height="22" fill="rgba(234,88,12,0.30)" stroke="#EA580C"/>
      <polygon points="108,132 172,132 172,62 108,34" fill="rgba(124,58,237,0.18)" stroke="#7C3AED"/>
      <line x1="58" y1="12" x2="236" y2="90" stroke="#0F172A" stroke-width="2"/>
      <line x1="28" y1="86" x2="236" y2="86" stroke="#DC2626" stroke-width="2" stroke-dasharray="5,3"/>
      <line x1="28" y1="108" x2="236" y2="108" stroke="#1D4ED8" stroke-width="2" stroke-dasharray="3,2"/>
      <g class="sk-lbl" font-size="9.2" font-weight="700">
        <text x="180" y="82" fill="#DC2626">CmgS</text><text x="180" y="121" fill="#1D4ED8">CmgP</text>
        <text x="40" y="100" fill="#9A3412">Externalidad</text>
        <text x="100" y="145" fill="#0F172A">X0</text><text x="166" y="145" fill="#7C3AED">X1</text>
      </g>
    </svg>`
  },
  {
    title: "5. Externalidad Positiva en Consumo",
    sub: "UtmgS (punteada arriba) supera a UtmgP; el área social crece al bajar P.",
    svg: `<svg viewBox="0 0 260 155">
      <line x1="28" y1="132" x2="245" y2="132" stroke="#0F172A" stroke-width="1.6"/>
      <line x1="28" y1="12" x2="28" y2="132" stroke="#0F172A" stroke-width="1.6"/>
      <polygon points="122,132 162,132 162,62 122,40" fill="rgba(219,39,119,0.22)" stroke="#BE185D"/>
      <line x1="48" y1="22" x2="225" y2="118" stroke="#0F172A" stroke-width="2"/>
      <line x1="72" y1="12" x2="242" y2="104" stroke="#BE185D" stroke-width="2" stroke-dasharray="5,3"/>
      <line x1="45" y1="125" x2="178" y2="24" stroke="#1D4ED8" stroke-width="1.8"/>
      <line x1="88" y1="125" x2="225" y2="36" stroke="#15803D" stroke-width="1.8" stroke-dasharray="4,3"/>
      <g class="sk-lbl" font-size="9.2" font-weight="700">
        <text x="182" y="66" fill="#BE185D">UtmgS</text><text x="195" y="114" fill="#0F172A">UtmgP</text>
        <text x="166" y="24" fill="#1D4ED8">O</text><text x="220" y="34" fill="#15803D">O'</text>
        <text x="118" y="145" fill="#0F172A">X</text><text x="158" y="145" fill="#BE185D">X'</text>
      </g>
    </svg>`
  },
  {
    title: "6. Insumos Importables (D → D + Ȳ)",
    sub: "Con arancel el mercado paga Pm; el costo social real es Pm* (CIF sin arancel).",
    svg: `<svg viewBox="0 0 260 155">
      <line x1="28" y1="132" x2="245" y2="132" stroke="#0F172A" stroke-width="1.6"/>
      <line x1="28" y1="12" x2="28" y2="132" stroke="#0F172A" stroke-width="1.6"/>
      <rect x="134" y="88" width="44" height="44" fill="rgba(29,78,216,0.22)" stroke="#1D4ED8"/>
      <line x1="28" y1="68" x2="236" y2="68" stroke="#0F172A" stroke-width="1.8"/>
      <line x1="28" y1="88" x2="236" y2="88" stroke="#15803D" stroke-width="1.8" stroke-dasharray="5,3"/>
      <line x1="65" y1="124" x2="155" y2="20" stroke="#475569" stroke-width="1.8"/>
      <line x1="88" y1="18" x2="168" y2="122" stroke="#0F172A" stroke-width="2"/>
      <line x1="132" y1="18" x2="212" y2="122" stroke="#DC2626" stroke-width="2" stroke-dasharray="5,3"/>
      <g class="sk-lbl" font-size="9.2" font-weight="700">
        <text x="6" y="71" fill="#0F172A">Pm</text><text x="4" y="92" fill="#15803D">Pm*</text>
        <text x="148" y="22" fill="#475569">S</text><text x="166" y="118" fill="#0F172A">D</text><text x="206" y="114" fill="#DC2626">D+Ȳ</text>
        <text x="128" y="145" fill="#0F172A">Y0</text><text x="174" y="145" fill="#1D4ED8">Y2</text>
      </g>
    </svg>`
  }
];

let mecBlind = false;
let mecFilter = "all";
let mecMastered = new Set();
let mecBuilt = false;

function renderMecanica() {
  const fGrid = document.getElementById("mec-formulas-grid");
  const sGrid = document.getElementById("mec-skel-grid");
  if (!fGrid || !sGrid) return;

  fGrid.innerHTML = "";
  const visibles = FORMULAS_PROY.filter(f => mecFilter === "all" || f.cat === mecFilter);
  for (const item of visibles) {
    const card = document.createElement("div");
    card.className = "f-card" + (mecMastered.has(item.id) ? " mastered" : "");
    card.innerHTML = `
      <div class="f-head">
        <div><span class="f-cat">${item.tag}</span> <span class="f-title">${item.title}</span></div>
        <button class="chk-btn" title="Marcar dominada en cuaderno" onclick="toggleMastered(${item.id}, event)">✓</button>
      </div>
      <div class="f-body" onclick="this.parentElement.classList.toggle('revealed')">
        <div class="blind-cover">Haz clic para revelar y comprobar tu cuaderno</div>
        <div class="f-eq">${item.eq}</div>
        <div class="f-rule">${item.rule}</div>
      </div>`;
    fGrid.appendChild(card);
  }

  if (!mecBuilt) {
    sGrid.innerHTML = "";
    for (const sk of ESQUELETOS_PROY) {
      const sc = document.createElement("div");
      sc.className = "s-card";
      sc.onclick = function() { this.classList.toggle("revealed"); };
      sc.innerHTML = `<div class="s-title"><span>${sk.title}</span></div>${sk.svg}<div class="s-sub">${sk.sub}</div>`;
      sGrid.appendChild(sc);
    }
    mecBuilt = true;
  }
  actualizarScoreMec();
}
function setModoMec(isBlind) {
  mecBlind = isBlind;
  const cont = document.getElementById("mec-container");
  cont.classList.toggle("blind-mode", isBlind);
  document.getElementById("btn-modo-copia").classList.toggle("primary", !isBlind);
  document.getElementById("btn-modo-ciego").classList.toggle("primary", isBlind);
  cont.querySelectorAll(".f-card, .s-card").forEach(el => el.classList.remove("revealed"));
}
function filtrarMec(cat, btn) {
  mecFilter = cat;
  document.querySelectorAll(".flt-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  renderMecanica();
}
function toggleMastered(id, ev) {
  ev.stopPropagation();
  if (mecMastered.has(id)) mecMastered.delete(id); else mecMastered.add(id);
  renderMecanica();
}
function resetDominadas() {
  mecMastered.clear();
  renderMecanica();
}
function actualizarScoreMec() {
  const sc = document.getElementById("mec-score");
  if (sc) sc.textContent = `Dominadas: ${mecMastered.size} / ${FORMULAS_PROY.length}`;
}

drawTransporte();
renderMecanica();
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
    components.html(HTML_SIMULADOR_FLUIDO, height=860, scrolling=True)
