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
  .top-tabs {
    display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap;
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px;
  }
  .tab-btn {
    border: 1px solid #CBD5E1; background: #F8FAFC; color: #334155;
    padding: 6px 11px; border-radius: 6px; font-weight: 700; font-size: 12px;
    cursor: pointer; transition: all 0.14s ease;
  }
  .tab-btn:hover { border-color: #1D4ED8; color: #1D4ED8; background: #EFF6FF; }
  .tab-btn.active { background: #0F172A; color: #FFFFFF; border-color: #0F172A; }
  /* === MATRIZ DE LEOPOLD 60 FPS === */
  .leo-table { width: 100%; border-collapse: collapse; font-size: 11.5px; margin-top: 6px; }
  .leo-table th { background: #1E293B; color: #FFFFFF; padding: 7px 6px; border: 1px solid #CBD5E1; text-align: center; }
  .leo-table td { border: 1px solid #CBD5E1; padding: 6px; text-align: center; vertical-align: middle; }
  .leo-table td:first-child { text-align: left; font-weight: 700; background: #F8FAFC; color: #0F172A; width: 21%; }
  .leo-cell-score { font-family: Consolas, monospace; font-weight: 800; font-size: 13px; margin-bottom: 3px; }
  .leo-mini-lbl { font-size: 10px; color: #334155; display: flex; justify-content: space-between; }
  .leo-mini-rng { width: 100%; height: 12px; margin: 1px 0; cursor: pointer; }
  /* === ENTRENADOR V/F 60 FPS === */
  .vf-card {
    border: 1px solid #CBD5E1; border-left: 4px solid #334155; border-radius: 6px;
    background: #FFFFFF; padding: 9px 12px; margin-bottom: 8px;
  }
  .vf-card.ok { border-left-color: #15803D; background: #F0FDF4; }
  .vf-card.bad { border-left-color: #DC2626; background: #FEF2F2; }
  .vf-q { font-size: 12.2px; font-weight: 700; color: #0F172A; margin-bottom: 6px; line-height: 1.4; }
  .vf-btns { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
  .vf-btn {
    border: 1px solid #94A3B8; background: #FFFFFF; color: #0F172A;
    padding: 4px 12px; border-radius: 5px; font-size: 11.5px; font-weight: 800; cursor: pointer;
  }
  .vf-btn:hover { background: #EFF6FF; border-color: #1D4ED8; }
  .vf-fb { font-size: 11.5px; color: #1E293B; margin-top: 6px; line-height: 1.38; display: none; }
  .vf-card.answered .vf-fb { display: block; }
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
  /* === ENUNCIADO REDACTADO + EDITOR DE ECUACIONES + SOLUCIONARIO VIVO === */
  .enun-box {
    background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 4px solid #0F172A;
    border-radius: 6px; padding: 10px 13px; margin-bottom: 10px; font-size: 12.2px; line-height: 1.48; color: #1E293B;
  }
  .enun-box summary {
    cursor: pointer; font-weight: 800; color: #0F172A; font-size: 12.5px; list-style: none;
    display: flex; justify-content: space-between; align-items: center;
  }
  .enun-box summary::-webkit-details-marker { display: none; }
  .enun-badge {
    font-size: 10.5px; font-weight: 700; color: #1E3A8A; background: #DBEAFE;
    padding: 2px 8px; border-radius: 10px;
  }
  .enun-body { margin-top: 8px; border-top: 1px dashed #CBD5E1; padding-top: 8px; }
  .enun-list { margin: 5px 0 0 18px; padding: 0; }
  .enun-list li { margin-bottom: 2px; }
  .eq-editor-bar {
    display: grid; grid-template-columns: 1.3fr 1.3fr 0.75fr auto; gap: 8px; align-items: end;
    background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 9px 11px; margin-bottom: 10px;
  }
  @media (max-width: 820px) { .eq-editor-bar { grid-template-columns: 1fr; } }
  .eq-field label { display: block; font-size: 11px; font-weight: 700; color: #1E293B; margin-bottom: 3px; }
  .eq-input {
    width: 100%; padding: 6px 9px; border: 1px solid #94A3B8; border-radius: 5px;
    font-family: Consolas, monospace; font-size: 12.5px; font-weight: 700; color: #0F172A; background: #FFFFFF;
  }
  .eq-input:focus { outline: 2px solid #1D4ED8; border-color: #1D4ED8; }
  .eq-err { font-size: 11px; font-weight: 700; color: #DC2626; margin-top: 4px; display: none; }
  .sol-box {
    margin-top: 8px; background: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #15803D;
    border-radius: 6px; padding: 9px 12px; font-size: 12px; line-height: 1.48; color: #0F172A;
    font-family: Consolas, monospace;
  }
  .sol-box b { color: #1E3A8A; }

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
    display: block; line-height: 1.65;
  }
  .f-eq sup, .fstrip-eq sup, .fstrip-sub sup { font-size: 0.72em; vertical-align: super; line-height: 0; }
  .f-eq sub, .fstrip-eq sub, .fstrip-sub sub { font-size: 0.72em; vertical-align: sub; line-height: 0; }
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

  /* === MAPA TEÓRICO Y LECTURA VIVA (PESTAÑA 10) === */
  .map-detail-card {
    margin-top: 9px; background: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #1D4ED8;
    border-radius: 6px; padding: 10px 13px; font-size: 12.2px; line-height: 1.48; color: #0F172A;
  }
  .map-detail-head {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
    margin-bottom: 6px; padding-bottom: 6px; border-bottom: 1px dashed #CBD5E1;
  }
  .map-detail-title { font-size: 13px; font-weight: 800; color: #1E3A8A; }
  .jump-btn {
    border: 1px solid #1D4ED8; background: #EFF6FF; color: #1E3A8A;
    padding: 4px 9px; border-radius: 5px; font-size: 11px; font-weight: 700; cursor: pointer;
  }
  .jump-btn:hover { background: #1D4ED8; color: #FFFFFF; }
  .lec-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 12px; }
  @media (max-width: 820px) { .lec-grid { grid-template-columns: 1fr; } }
  .lec-card {
    border: 1px solid #CBD5E1; border-top: 3.5px solid #1E3A8A; border-radius: 6px;
    background: #FFFFFF; padding: 10px 12px; display: flex; flex-direction: column; gap: 6px;
  }
  .lec-meta { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 4px; }
  .lec-unit { font-size: 10px; font-weight: 800; color: #FFFFFF; background: #1E293B; padding: 2px 7px; border-radius: 4px; }
  .lec-src { font-size: 10.5px; font-weight: 600; color: #475569; font-family: Consolas, monospace; }
  .lec-title { font-size: 12.6px; font-weight: 800; color: #0F172A; }
  .lec-layer {
    font-size: 11.8px; line-height: 1.44; color: #1E293B; padding: 6px 9px; border-radius: 5px;
    background: #F8FAFC; border-left: 3px solid #94A3B8;
  }
  .lec-layer.l-core { border-left-color: #1D4ED8; background: #EFF6FF; }
  .lec-layer.l-bridge { border-left-color: #059669; background: #ECFDF5; }
  .lec-layer.l-trap { border-left-color: #DC2626; background: #FEF2F2; }
  .lec-layer b { color: #0F172A; }
  .qz-card {
    border: 1px solid #CBD5E1; border-left: 4px solid #334155; border-radius: 6px;
    background: #FFFFFF; padding: 9px 12px; margin-bottom: 8px;
  }
  .qz-card.ok { border-left-color: #15803D; background: #F0FDF4; }
  .qz-card.bad { border-left-color: #DC2626; background: #FEF2F2; }
  .qz-tag { font-size: 10px; font-weight: 800; color: #1E3A8A; background: #DBEAFE; padding: 2px 7px; border-radius: 4px; margin-right: 6px; }
  .qz-q { font-size: 12.2px; font-weight: 700; color: #0F172A; margin: 4px 0 7px 0; line-height: 1.42; }
  .qz-opts { display: flex; gap: 7px; flex-wrap: wrap; align-items: center; }
  .qz-btn {
    border: 1px solid #94A3B8; background: #FFFFFF; color: #0F172A;
    padding: 4px 10px; border-radius: 5px; font-size: 11.4px; font-weight: 700; cursor: pointer;
  }
  .qz-btn:hover { background: #EFF6FF; border-color: #1D4ED8; }
  .qz-btn.sel { background: #0F172A; color: #FFFFFF; border-color: #0F172A; }
  .qz-fb { font-size: 11.5px; color: #1E293B; margin-top: 7px; line-height: 1.42; display: none; border-top: 1px dashed #CBD5E1; padding-top: 6px; }
  .qz-card.answered .qz-fb { display: block; }
  /* === CÁPSULAS PEDAGÓGICAS VIVAS DENTRO DE CADA INTERACTIVO === */
  .ped-grid {
    display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: 10px;
  }
  @media (max-width: 860px) { .ped-grid { grid-template-columns: 1fr; } }
  .ped-card {
    background: #F8FAFC; border: 1px solid #CBD5E1; border-top: 3.5px solid #1D4ED8;
    border-radius: 6px; padding: 9px 11px; font-size: 11.7px; line-height: 1.46; color: #1E293B;
  }
  .ped-card.p-cur { border-top-color: #7C3AED; background: #FAF5FF; }
  .ped-card.p-def { border-top-color: #059669; background: #F0FDF4; }
  .ped-hd {
    font-size: 10.6px; font-weight: 800; letter-spacing: 0.3px; text-transform: uppercase;
    margin-bottom: 5px; color: #1E3A8A;
  }
  .ped-card.p-cur .ped-hd { color: #6D28D9; }
  .ped-card.p-def .ped-hd { color: #065F46; }
  .ped-card b { color: #0F172A; }
  .s-card .sk-lbl { transition: opacity 0.15s ease; }
  /* === TARJETAS DE FÓRMULAS VIVAS (GRANDE + EDITABLE IN-PLACE + RAYOS X) === */
  .fstrip-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
    gap: 10px; margin: 10px 0 12px 0;
  }
  .fstrip-card {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid #CBD5E1; border-left: 4px solid #1E3A8A;
    border-radius: 8px; padding: 11px 14px;
    transition: box-shadow 0.16s ease, border-color 0.16s ease;
    position: relative;
  }
  .fstrip-card:hover {
    border-color: #93C5FD; box-shadow: 0 3px 12px rgba(29, 78, 216, 0.09);
  }
  .fstrip-card.xray-on {
    background: linear-gradient(180deg, #F0F9FF 0%, #FFFFFF 100%);
    border-color: #3B82F6;
    box-shadow: 0 4px 14px rgba(29, 78, 216, 0.14);
  }
  .fstrip-head {
    display: flex; justify-content: space-between; align-items: center; gap: 8px;
    margin-bottom: 7px; cursor: pointer;
  }
  .fstrip-lbl { font-size: 12px; font-weight: 800; color: #1E3A8A; letter-spacing: 0.1px; }
  .xray-pill {
    font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 12px;
    border: 1px solid #BFDBFE; background: #EFF6FF; color: #1D4ED8;
    white-space: nowrap; transition: all 0.15s ease; cursor: pointer;
  }
  .xray-pill:hover { background: #DBEAFE; }
  .fstrip-card.xray-on .xray-pill {
    background: #0F172A; color: #FFFFFF; border-color: #0F172A;
  }
  .fstrip-eq {
    font-family: "Cambria Math", "Times New Roman", Georgia, serif;
    font-size: 16.5px; font-weight: 700; color: #0F172A;
    display: block; line-height: 1.75;
  }
  .fstrip-sub {
    font-family: "Cambria Math", "Times New Roman", Georgia, serif;
    font-size: 15.2px; font-weight: 700; color: #0F172A;
    margin-top: 8px; padding-top: 8px; border-top: 1px dashed #CBD5E1;
    display: block; line-height: 1.95;
  }
  .fstrip-card.xray-on .fstrip-eq { display: none; }
  .fstrip-card.xray-on .fstrip-sub {
    margin-top: 4px; padding-top: 2px; border-top: none; font-size: 17.5px; line-height: 2.05;
  }
  .fstrip-card .frac {
    font-size: 0.96em; margin: 0 3px; line-height: 1.25;
  }
  .fstrip-card .frac .num {
    border-bottom: 1.7px solid #0F172A; padding: 0 5px 2px 5px;
  }
  .fstrip-card .frac .den {
    padding: 2px 5px 0 5px;
  }
  .fstrip-note {
    font-size: 11.4px; color: #475569; margin-top: 6px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    display: flex; flex-wrap: wrap; gap: 5px; align-items: center; line-height: 1.4;
  }
  .v-chip {
    display: inline-block; padding: 1px 7px; border-radius: 5px;
    font-family: Consolas, monospace; font-size: 0.94em; font-weight: 800;
    border: 1.3px solid transparent; line-height: 1.35; vertical-align: baseline;
    transition: transform 0.14s ease, box-shadow 0.14s ease;
  }
  .v-chip.editable {
    cursor: text; border-style: dashed;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
  }
  .v-chip.editable:hover {
    transform: translateY(-1px) scale(1.04);
    border-style: solid;
    box-shadow: 0 0 0 2.5px rgba(29, 78, 216, 0.22);
  }
  .chip-inline-in {
    font-family: Consolas, monospace; font-size: 0.96em; font-weight: 800;
    color: #0F172A; background: #FFFFFF; border: 2px solid #1D4ED8;
    border-radius: 5px; padding: 1px 5px; text-align: center;
    outline: none; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.20);
    vertical-align: baseline;
  }
  .vc-b { background: #DBEAFE; color: #1E40AF; border-color: #60A5FA; }
  .vc-t { background: #CCFBF1; color: #0F766E; border-color: #2DD4BF; }
  .vc-p { background: #F3E8FF; color: #6B21A8; border-color: #C084FC; }
  .vc-o { background: #FFEDD5; color: #9A3412; border-color: #FB923C; }
  .vc-r { background: #FEE2E2; color: #991B1B; border-color: #F87171; }
  .vc-g { background: #DCFCE7; color: #166534; border-color: #4ADE80; }
  .vc-res {
    background: #15803D; color: #FFFFFF; border-color: #166534;
    padding: 2px 8px; border-radius: 6px; font-family: Consolas, monospace;
    font-size: 0.98em; font-weight: 800; display: inline-block; line-height: 1.35;
  }
  .vc-res.neg { background: #DC2626; border-color: #991B1B; }
  @keyframes chipPop {
    0% { transform: scale(1); }
    45% { transform: scale(1.09); filter: brightness(1.05); }
    100% { transform: scale(1); }
  }
  .v-pop { animation: chipPop 0.25s ease-out; }
  .sym-b { color: #1D4ED8; }
  .sym-t { color: #0F766E; }
  .sym-p { color: #7C3AED; }
  .sym-o { color: #C2410C; }
  .sym-r { color: #DC2626; }
  .teo-box {
    margin-top: 10px; background: #FFFFFF; border: 1px solid #CBD5E1;
    border-left: 4px solid #334155; border-radius: 6px; padding: 8px 12px;
    font-size: 11.9px; line-height: 1.48; color: #1E293B;
  }
  .teo-box summary {
    cursor: pointer; font-weight: 800; color: #0F172A; font-size: 12px; list-style: none;
    display: flex; justify-content: space-between; align-items: center;
  }
  .teo-box summary::-webkit-details-marker { display: none; }
  .teo-body { margin-top: 7px; border-top: 1px dashed #CBD5E1; padding-top: 7px; }
  .teo-body ul { margin: 4px 0 0 18px; padding: 0; }
  .teo-body li { margin-bottom: 4px; }

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
    <button class="tab-btn active" onclick="openTab('leche', this)">1. Valor Social de la Producción: Leche (RA1)</button>
    <button class="tab-btn" onclick="openTab('transporte', this)">2. Transporte, Distorsiones y Externalidades (RA1)</button>
    <button class="tab-btn" onclick="openTab('elasticidad', this)">3. Elasticidades Extremas: AD vs. LR (RA1)</button>
    <button class="tab-btn" onclick="openTab('waterfall', this)">4. Puente VAN Privado → VANS y Sensibilidad (SNI 2026)</button>
    <button class="tab-btn" onclick="openTab('horno', this)">5. Precios Mentirosos (Horno) y Costos Hundidos (RA1)</button>
    <button class="tab-btn" onclick="openTab('agua', this)">6. Proyección de Agua 10 Años, TEA y CAPM</button>
    <button class="tab-btn" onclick="openTab('ambiental', this)">7. Valoración Ambiental: Leopold, Viaje y GEI (RA2)</button>
    <button class="tab-btn" onclick="openTab('arboles', this)">8. Árboles Causales, Población SNI y Quiz V/F</button>
    <button class="tab-btn" onclick="openTab('mecanica', this)">9. Formulario de Fórmulas y Gráficos (Modo Ciego)</button>
    <button class="tab-btn" onclick="openTab('lectura', this)">10. Mapa Teórico Integrado y Control de Lectura</button>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 1: TRANSPORTE Y EXTERNALIDADES (ENUNCIADO + ECUACIONES + 60 FPS) -->
  <!-- ====================================================================== -->
  <div id="panel-transporte" class="panel">
    <div class="sec-title">
      <span>Externalidades y Costo Social en Transporte Urbano (Apuntes de Cátedra, págs. 13–14)</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarTransporte()">Reproducir Expansión</button>
        <button class="act-btn" onclick="fijarGhostTransporte()">Fijar Fantasma Aquí</button>
        <button class="act-btn" onclick="resetTransporte()">Restaurar Caso Apuntes</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento del Ejercicio (Transporte Urbano, Elasticidad y Externalidad Negativa)</span>
        <span class="enun-badge">Enunciado sincronizado en vivo</span>
      </summary>
      <div class="enun-body" id="tr-enunciado"></div>
    </details>

    <div class="eq-editor-bar" style="grid-template-columns: 1fr 1fr 1.2fr auto;">
      <div class="eq-field">
        <label>Tarifa Inicial P0 ($/pasaje):</label>
        <input id="tr-p0-in" class="eq-input" type="number" value="5000" step="100" min="500" oninput="drawTransporte()" />
      </div>
      <div class="eq-field">
        <label>Tarifa Con Proyecto P1 ($/pasaje):</label>
        <input id="tr-p1-in" class="eq-input" type="number" value="3500" step="100" min="200" oninput="drawTransporte()" />
      </div>
      <div class="eq-field">
        <label>Ecuación Demanda Implícita (Editable por P0, P1, X0, X1):</label>
        <input id="tr-eq-display" class="eq-input" type="text" readonly style="background:#E2E8F0;color:#1E293B;" />
      </div>
      <button class="act-btn primary" onclick="presetTransporteExt()">Cargar Variante CmgP=$500 / CmgS=$700</button>
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
        <input id="tr-cp" type="range" min="300" max="2400" step="50" value="1300" oninput="drawTransporte()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Costo Marg. Social CmgS</span><span><span id="tr-cs-v" class="sl-val">$1.700</span><span id="tr-cs-d" class="sl-delta d-eq"></span></span></div>
        <input id="tr-cs" type="range" min="300" max="3200" step="50" value="1700" oninput="drawTransporte()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Elasticidad Demanda (Ed)</div><div id="tr-k-ed" class="kpi-val">-1,43</div><div id="tr-k-dx" class="kpi-sub">ΔX = +30.030 pasajes</div></div>
      <div class="kpi" style="border-left-color:#7C3AED;"><div class="kpi-lbl">Beneficio Bruto Demanda</div><div id="tr-k-ben" class="kpi-val">$127.627.500</div><div id="tr-k-ben2" class="kpi-sub">Área bajo curva D (X0 → X1)</div></div>
      <div class="kpi" style="border-left-color:#EA580C;"><div class="kpi-lbl">Externalidad (CmgS - CmgP)</div><div id="tr-k-ext" class="kpi-val">$40.012.000</div><div id="tr-k-brecha" class="kpi-sub">Brecha = $400 / pasaje</div></div>
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Movimiento vs. Fantasma</div><div id="tr-k-mov" class="kpi-val">Base (Sin cambios)</div><div id="tr-k-mov2" class="kpi-sub">Mueve un slider para ver flechas</div></div>
    </div>

    <div id="tr-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-transporte" viewBox="0 0 960 400"></svg></div>
    <div class="legend-bar">
      <span class="leg-item"><span class="sw" style="background:rgba(124,58,237,0.25);border:1px solid #7C3AED;"></span>Beneficio Bruto Demanda</span>
      <span class="leg-item"><span class="sw" style="background:rgba(234,88,12,0.35);border:1px solid #EA580C;"></span>Banda Externalidad (CmgS vs CmgP)</span>
      <span class="leg-item"><span class="sw-line" style="border-top:2px dashed #94A3B8;"></span>Rastro Fantasma (Referencia anterior)</span>
      <span class="leg-item"><span class="sw-line" style="background:#DC2626;"></span>Flecha Vectorial de Movimiento</span>
    </div>
    <div id="tr-sol" class="sol-box"></div>
    <div id="ped-transporte" class="ped-grid"></div>
    <details class="teo-box">
      <summary>
        <span>Marco Teórico: Beneficio Social por Trapecio y Externalidades Negativas (Fontaine, Cap. VII)</span>
        <span class="enun-badge">Desplegar teoría de apoyo</span>
      </summary>
      <div class="teo-body">
        <ul>
          <li><b>Regla del Trapecio (Disposición a Pagar):</b> cuando un proyecto baja el costo generalizado de viaje de <b>P<sub>0</sub></b> a <b>P<sub>1</sub></b> y aumenta los viajes de <b>X<sub>0</sub></b> a <b>X<sub>1</sub></b>, el beneficio por tráfico generado es el área bajo la demanda: <b>B = ½·(P<sub>0</sub> + P<sub>1</sub>)·(X<sub>1</sub> − X<sub>0</sub>)</b>.</li>
          <li><b>Externalidad Negativa (Costo Social &gt; Costo Privado):</b> si el usuario solo percibe su costo privado <b>C<sub>priv</sub></b> (pasaje/combustible), ignora la congestión, ruido y emisiones que impone a terceros (<b>C<sub>soc</sub> − C<sub>priv</sub></b>). Por eso el costo social total es <b>C<sub>soc</sub>·X<sub>1</sub></b> y el daño externo es <b>(C<sub>soc</sub> − C<sub>priv</sub>)·X<sub>1</sub></b>.</li>
          <li><b>Elasticidad Precio (η<sub>d</sub>):</b> indica cuán sensible es la demanda de viajes ante una caída del costo. Si |η<sub>d</sub>| &gt; 1 (elástica), una rebaja de tarifa genera un fuerte salto en viajes y mayor beneficio social bruto.</li>
        </ul>
      </div>
    </details>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 2: MERCADO DE LA LECHE + EDITOR LIBRE DE ECUACIONES LINEALES     -->
  <!-- ====================================================================== -->
  <div id="panel-leche" class="panel active">
    <div class="sec-title">
      <span>Mercado de la Leche y Editor de Ecuaciones Lineales (VSP = AD + LR)</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarLeche()">Reproducir 0% → 100%</button>
        <button class="act-btn" onclick="presetLecheCaso('apuntes')">Leche Apuntes (-50)</button>
        <button class="act-btn" onclick="presetLecheCaso('positivo')">Leche Variante (+50)</button>
        <button class="act-btn" onclick="presetLecheCaso('carne')">Caso Prueba (500-0,02Q)</button>
        <button class="act-btn" onclick="fijarGhostLeche()">Fijar Fantasma Aquí</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento Oficial del Ejercicio (Clase 2 — Mercado del Producto, Preguntas a–e)</span>
        <span class="enun-badge">Cambia las ecuaciones abajo y se actualiza</span>
      </summary>
      <div class="enun-body" id="lc-enunciado"></div>
    </details>

    <div class="eq-editor-bar">
      <div class="eq-field">
        <label>Ecuación de Demanda (escribe cualquier lineal, ej: 300 - 0.0205*Q):</label>
        <input id="lc-eq-d" class="eq-input" type="text" value="Pd = 300 - 0.0205*Q" onkeydown="if(event.key==='Enter') aplicarEcuacionesLeche()" />
      </div>
      <div class="eq-field">
        <label>Ecuación de Oferta (ej: -50 + 0.025*Q  ó  10 + 0.5*Q):</label>
        <input id="lc-eq-o" class="eq-input" type="text" value="Po = -50 + 0.025*Q" onkeydown="if(event.key==='Enter') aplicarEcuacionesLeche()" />
      </div>
      <div class="eq-field">
        <label>Producción Proyecto (Q_proy):</label>
        <input id="lc-eq-q" class="eq-input" type="number" value="1470" step="10" min="0" onkeydown="if(event.key==='Enter') aplicarEcuacionesLeche()" />
      </div>
      <button class="act-btn primary" style="height:33px;" onclick="aplicarEcuacionesLeche()">Aplicar Ecuaciones</button>
    </div>
    <div id="lc-eq-err" class="eq-err"></div>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>Intercepto Demanda (A)</span><span id="lc-a-v" class="sl-val">300</span></div>
        <input id="lc-a" type="range" min="100" max="600" step="5" value="300" oninput="onSliderLeche()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Pendiente Demanda (B)</span><span id="lc-b-v" class="sl-val">0,0205</span></div>
        <input id="lc-b" type="range" min="0.005" max="0.080" step="0.0005" value="0.0205" oninput="onSliderLeche()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Intercepto Oferta (C)</span><span id="lc-c-v" class="sl-val">-50</span></div>
        <input id="lc-c" type="range" min="-150" max="150" step="5" value="-50" oninput="onSliderLeche()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Pendiente Oferta (D)</span><span id="lc-d-v" class="sl-val">0,0250</span></div>
        <input id="lc-d" type="range" min="0.005" max="0.100" step="0.0005" value="0.0250" oninput="onSliderLeche()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Producción Proyecto (Q_proy)</span><span id="lc-q-v" class="sl-val">1.470 t</span></div>
        <input id="lc-q" type="range" min="0" max="3200" step="10" value="1470" oninput="onSliderLeche()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Equilibrio Inicial (E0)</div><div id="lc-k-e0" class="kpi-val">7.692 t | $142,3</div><div class="kpi-sub">Sin proyecto</div></div>
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Nuevo Equilibrio (E1)</div><div id="lc-k-e1" class="kpi-val">8.500 t | $125,8</div><div id="lc-k-dp" class="kpi-sub">Caída precio ΔP = -$16,6</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Aumento Disponibilidad (AD)</div><div id="lc-k-ad" class="kpi-val">$108.282</div><div id="lc-k-adp" class="kpi-sub">55,0% del VSP</div></div>
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Liberación Recursos (LR)</div><div id="lc-k-lr" class="kpi-val">$88.742</div><div id="lc-k-lrp" class="kpi-sub">45,0% del VSP</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">VSP Total y Precio Social P*</div><div id="lc-k-vsp" class="kpi-val">$197.024</div><div id="lc-k-ps" class="kpi-sub">P* = $134,03 / ton</div></div>
    </div>

    <div id="lc-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-leche" viewBox="0 0 960 410"></svg></div>
    <div class="legend-bar">
      <span class="leg-item"><span class="sw" style="background:rgba(37,99,235,0.28);border:1px solid #1D4ED8;"></span>Liberación de Recursos (LR: Qo1 ← Q0)</span>
      <span class="leg-item"><span class="sw" style="background:rgba(220,38,38,0.28);border:1px solid #DC2626;"></span>Aumento en Disponibilidad (AD: Q0 → Q1)</span>
      <span class="leg-item"><span class="sw-line" style="background:#15803D;"></span>Flecha Verde: Desplazamiento Oferta O → O'</span>
      <span class="leg-item"><span class="sw-line" style="border-top:2px dashed #94A3B8;"></span>Rastro Fantasma (Referencia anterior)</span>
    </div>
    <div id="lc-sol" class="sol-box"></div>
    <div id="ped-leche" class="ped-grid"></div>
    <details class="teo-box">
      <summary>
        <span>Marco Teórico: Valor Social de la Producción — Eficiencia vs. Agencia (Fontaine, Cap. V · Clase 2)</span>
        <span class="enun-badge">Desplegar teoría de apoyo</span>
      </summary>
      <div class="teo-body">
        <ul>
          <li><b>¿Por qué el Valor Social (VSP) supera al Valor Privado (VPP)?</b> El dueño privado solo cobra el precio más bajo <b>P<sub>1</sub></b> por cada unidad producida (<b>VPP = P<sub>1</sub>·Q<sub>proy</sub></b>). La sociedad, en cambio, gana además el triángulo de excedente del consumidor por el mayor consumo (<b>AD</b>) y el ahorro real de costos de los productores antiguos desplazados (<b>LR</b>).</li>
          <li><b>Identidad Fundamental (Enfoque Eficiencia = Enfoque Agencia):</b> <b>VSP = AD + LR</b> siempre coincide numéricamente con <b>VPP + ΔEC + ΔEP</b>. En un mercado competitivo sin distorsiones, <b>ΔEC &gt; 0</b> (ganan consumidores por menor precio) y <b>ΔEP &lt; 0</b> (pierden antiguos oferentes), pero la ganancia social neta es positiva.</li>
          <li><b>Regla del Precio Social Unitario:</b> cuando oferta y demanda son lineales, el precio social promedio resulta exacto: <b>P<sub>social</sub> = VSP / Q<sub>proy</sub> = (P<sub>0</sub> + P<sub>1</sub>) / 2</b> (en el caso de la leche: ($187,36 + $170,80)/2 = $179,08/ton).</li>
        </ul>
      </div>
    </details>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 3: ELASTICIDADES EXTREMAS                                        -->
  <!-- ====================================================================== -->
  <div id="panel-elasticidad" class="panel">
    <div class="sec-title">
      <span>Análisis de Elasticidades Extremas — Participación de AD frente a LR</span>
      <div class="btn-bar">
        <button class="act-btn" onclick="setElast(0, 55)">ηd = ∞ (100% AD)</button>
        <button class="act-btn" onclick="setElast(55, 0)">ηo = ∞ (100% LR)</button>
        <button class="act-btn" onclick="setElast(100, 45)">ηd = 0 (100% LR)</button>
        <button class="act-btn" onclick="setElast(45, 100)">ηo = 0 (100% AD)</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento Conceptual de Examen (Sensibilidad de AD y LR según Elasticidades de Oferta y Demanda)</span>
        <span class="enun-badge">Regla de pizarra pág. 16</span>
      </summary>
      <div class="enun-body" id="el-enunciado"></div>
    </details>

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

    <div id="el-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-elast" viewBox="0 0 960 390"></svg></div>
    <div id="el-note" class="note-box">Mueve las rigideces suavemente: observa cómo las flechas horizontales <b>← LR</b> y <b>→ AD</b> cambian de tamaño al instante hasta volverse 100% una u otra en los 4 casos extremos de examen.</div>
    <div id="ped-elast" class="ped-grid"></div>
    <details class="teo-box">
      <summary>
        <span>Marco Teórico: Los 4 Casos Extremos de Elasticidad (Fontaine, Cap. V · Regla de Examen)</span>
        <span class="enun-badge">Desplegar teoría de apoyo</span>
      </summary>
      <div class="teo-body">
        <ul>
          <li><b>Demanda Perfectamente Elástica (horizontal, η<sub>d</sub> = ∞):</b> ej. un bien exportable tomador de precio internacional. El precio no cae y el proyecto no desplaza a ningún productor local ⇒ <b>100% AD (Aumento en Disponibilidad)</b>.</li>
          <li><b>Oferta Perfectamente Elástica (horizontal, η<sub>o</sub> = ∞):</b> ej. bien importable o producción a costo marginal constante. El precio y el consumo no cambian; el proyecto solo reemplaza oferta antigua ⇒ <b>100% LR (Liberación de Recursos)</b>.</li>
          <li><b>Demanda Perfectamente Inelástica (vertical, η<sub>d</sub> = 0):</b> ej. agua potable básica o medicina esencial con consumo fijo. Aunque baje el precio nadie consume más ⇒ <b>100% LR</b>.</li>
          <li><b>Oferta Perfectamente Inelástica (vertical, η<sub>o</sub> = 0):</b> los antiguos oferentes no pueden reducir su producción aunque baje el precio ⇒ toda la producción nueva es consumida ⇒ <b>100% AD</b>.</li>
        </ul>
      </div>
    </details>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 4: PUENTE PRIVADO -> SOCIAL (WATERFALL SNI 2026 A 60 FPS)        -->
  <!-- ====================================================================== -->
  <div id="panel-waterfall" class="panel">
    <div class="sec-title">
      <span>Puente de Valoración Privado a Social — Normativa SNI 2026</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarWaterfall()">Reproducir Cascada</button>
        <button class="act-btn" onclick="presetWaterfall('planta')">Planta 480 t/año (Cátedra)</button>
        <button class="act-btn" onclick="presetWaterfall('carton')">Planta PyME Local (15 t/año)</button>
        <button class="act-btn" onclick="fijarGhostWaterfall()">Fijar Fantasma Aquí</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento del Caso (Transición Metodológica Privado → Social SNI 2026)</span>
        <span class="enun-badge">Enunciado y cascada sincronizados en vivo</span>
      </summary>
      <div class="enun-body" id="wf-enunciado"></div>
    </details>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>CAPEX Inicial (MM$)</span><span id="wf-cap-v" class="sl-val">$68,0 MM</span></div>
        <input id="wf-cap" type="range" min="10" max="150" step="1" value="68" oninput="drawWaterfall()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Volumen Año 1 (ton/año)</span><span id="wf-vol-v" class="sl-val">480 t</span></div>
        <input id="wf-vol" type="range" min="15" max="1000" step="5" value="480" oninput="drawWaterfall()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Margen Unitario ($/ton)</span><span id="wf-mar-v" class="sl-val">$165.000</span></div>
        <input id="wf-mar" type="range" min="60000" max="350000" step="5000" value="165000" oninput="drawWaterfall()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>WACC Privado (%)</span><span id="wf-wacc-v" class="sl-val">11,5%</span></div>
        <input id="wf-wacc" type="range" min="6.0" max="20.0" step="0.5" value="11.5" oninput="drawWaterfall()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Planilla Anual MO (MM$)</span><span id="wf-mo-v" class="sl-val">$52,8 MM</span></div>
        <input id="wf-mo" type="range" min="15" max="100" step="1" value="52.8" oninput="drawWaterfall()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>CH4 Evitado (t/año × 28)</span><span id="wf-ch4-v" class="sl-val">8,5 t</span></div>
        <input id="wf-ch4" type="range" min="0" max="25" step="0.5" value="8.5" oninput="drawWaterfall()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#1E3A8A;"><div class="kpi-lbl">1. VAN Privado Puro</div><div id="wf-k-vp" class="kpi-val">$69,2 MM</div><div id="wf-k-vp2" class="kpi-sub">Descontado al WACC</div></div>
      <div class="kpi" style="border-left-color:#059669;"><div class="kpi-lbl">2. Brecha Total (Social − Priv)</div><div id="wf-k-dif" class="kpi-val">+$458,6 MM</div><div id="wf-k-dif2" class="kpi-sub">Suma de 4 ajustes SNI</div></div>
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">3. VANS Social SNI (TSD 5,5%)</div><div id="wf-k-vs" class="kpi-val">$527,8 MM</div><div id="wf-k-vs2" class="kpi-sub">Δ vs Fantasma: $0,0 MM</div></div>
      <div class="kpi" style="border-left-color:#EA580C;"><div class="kpi-lbl">4. Aporte Carbono + GIRS/año</div><div id="wf-k-co2" class="kpi-val">$39,4 MM/año</div><div id="wf-k-co2b" class="kpi-sub">CO2eq × $71.801/t</div></div>
    </div>

    <div id="wf-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-waterfall" viewBox="0 0 960 400"></svg></div>
    <div id="wf-sol" class="sol-box"></div>

    <div class="sec-title" style="margin-top:12px;">
      <span>Análisis de Sensibilidad y Punto de Quiebre (Pruebas de Estrés)</span>
      <div class="btn-bar">
        <button class="act-btn" onclick="resetRadar()">Restaurar 0% Estrés</button>
        <button class="act-btn" onclick="presetRadar(-20, -15, 15)">Estrés Severo (-20% Vol / -15% Pre / +15% Cos)</button>
      </div>
    </div>
    <div class="sliders-grid" style="grid-template-columns: repeat(3, 1fr);">
      <div class="sl-card">
        <div class="sl-head"><span>Shock Volumen (%)</span><span id="rd-vol-v" class="sl-val">0%</span></div>
        <input id="rd-vol" type="range" min="-45" max="30" step="1" value="0" oninput="drawWaterfall()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Shock Precio / Margen (%)</span><span id="rd-pre-v" class="sl-val">0%</span></div>
        <input id="rd-pre" type="range" min="-45" max="30" step="1" value="0" oninput="drawWaterfall()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Shock Costos Planilla (%)</span><span id="rd-cos-v" class="sl-val">0%</span></div>
        <input id="rd-cos" type="range" min="-25" max="45" step="1" value="0" oninput="drawWaterfall()" />
      </div>
    </div>
    <div id="rd-box" class="sol-box" style="margin-top:0;"></div>
    <div id="ped-waterfall" class="ped-grid"></div>
    <details class="teo-box">
      <summary>
        <span>Marco Teórico: Paso de Evaluación Privada a Social — Precios Sociales SNI 2026 (MDSF)</span>
        <span class="enun-badge">Desplegar teoría de apoyo</span>
      </summary>
      <div class="teo-body">
        <ul>
          <li><b>1) Tasa Social de Descuento (TSD = 5,5% vs. WACC privado):</b> el Estado valora más los flujos futuros de largo plazo que un inversionista privado, elevando el valor presente de los beneficios.</li>
          <li><b>2) Eliminación de Transferencias (Impuesto a la Renta, IVA, Aranceles):</b> en evaluación social los impuestos NO son un costo para el país sino una transferencia desde el proyecto hacia el Fisco.</li>
          <li><b>3) Precios Sombra de Mano de Obra (SNI 2026):</b> <b>PSMO = Salario Bruto × FCSMO</b> con <b>MOC = 0,97</b>, <b>MOSC = 0,95</b> (ej. choferes y operadores según CIUO-08) y <b>MONC = 0,91</b>. El PSMO es siempre menor o igual al salario privado.</li>
          <li><b>4) Externalidades Positivas (Carbono y GIRS):</b> cada tonelada de CO<sub>2</sub>eq evitada se valora al <b>Precio Social del Carbono 2026 = $71.801/t</b> (y 1 t de CH<sub>4</sub> equivale a 28 t CO<sub>2</sub>eq según IPCC).</li>
        </ul>
      </div>
    </details>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 5: HORNO DE PAN (FONTAINE CAP I-II) + COSTOS HUNDIDOS A 60 FPS   -->
  <!-- ====================================================================== -->
  <div id="panel-horno" class="panel">
    <div class="sec-title">
      <span>Ernesto Fontaine: El Horno de Pan (Valor Agregado vs. Excedente y Precio Mentiroso)</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarHorno()">Reproducir Trampa del Subsidio</button>
        <button class="act-btn" onclick="resetHorno()">Caso Libro Fontaine ($104 / $133 / $6)</button>
        <button class="act-btn" onclick="fijarGhostHorno()">Fijar Fantasma Aquí</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento Oficial (Ernesto Fontaine, Cap. I págs. 16–35 y Cap. II págs. 43–51)</span>
        <span class="enun-badge">Por qué maximizar Valor Agregado puede empobrecer</span>
      </summary>
      <div class="enun-body" id="hn-enunciado"></div>
    </details>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>Precio Pan Base ($)</span><span id="hn-pb-v" class="sl-val">$104</span></div>
        <input id="hn-pb" type="range" min="92" max="120" step="1" value="104" oninput="drawHorno()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Precio Pan Envasado + Reparto ($)</span><span id="hn-pe-v" class="sl-val">$133</span></div>
        <input id="hn-pe" type="range" min="115" max="155" step="1" value="133" oninput="drawHorno()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Costo Extra Envasado + Reparto ($)</span><span id="hn-ce-v" class="sl-val">$30</span></div>
        <input id="hn-ce" type="range" min="15" max="45" step="1" value="30" oninput="drawHorno()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Subsidio Oculto al Insumo ($)</span><span id="hn-sub-v" class="sl-val">$6</span></div>
        <input id="hn-sub" type="range" min="0" max="20" step="1" value="6" oninput="drawHorno()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#1E293B;"><div class="kpi-lbl">Valor Agregado (Base → Envas.)</div><div id="hn-k-va" class="kpi-val">$24 → $43</div><div id="hn-k-va2" class="kpi-sub">Sube +$19 (¡Trampa!)</div></div>
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Excedente Privado Base</div><div id="hn-k-epb" class="kpi-val">+$4</div><div class="kpi-sub">Costo base = $100</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Excedente Privado Envasado</div><div id="hn-k-epe" class="kpi-val">+$3</div><div id="hn-k-epe2" class="kpi-sub">Cae -$1 vs base</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Excedente Social (c/Subsidio)</div><div id="hn-k-es" class="kpi-val">-$2 | -$3</div><div id="hn-k-es2" class="kpi-sub">Bueno p/Juan, malo p/país</div></div>
    </div>

    <div id="hn-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-horno" viewBox="0 0 960 350"></svg></div>
    <div id="hn-sol" class="sol-box"></div>

    <div class="sec-title" style="margin-top:12px;">
      <span>Costos Hundidos frente a Costos Evitables (Fontaine, Cap. II)</span>
      <div class="btn-bar">
        <button id="ch-btn-a" class="act-btn primary" onclick="setDecisionHundido('formar')">A. Formar o no la fábrica (antes de invertir)</button>
        <button id="ch-btn-b" class="act-btn" onclick="setDecisionHundido('seguir')">B. Seguir operando o cerrar hoy (ya construida)</button>
      </div>
    </div>
    <div class="sliders-grid" style="grid-template-columns: 1fr 1.6fr;">
      <div class="sl-card">
        <div class="sl-head"><span>Valor de Liquidación Hoy (Máquina + Edificio)</span><span id="ch-liq-v" class="sl-val">$2.500</span></div>
        <input id="ch-liq" type="range" min="500" max="6000" step="100" value="2500" oninput="drawHundido()" />
      </div>
      <div id="ch-fstrip" class="fstrip-grid"></div>
    <div id="ch-res-box" class="sol-box" style="margin-top:0;"></div>
    </div>
    <div id="ped-horno" class="ped-grid"></div>
    <details class="teo-box">
      <summary>
        <span>Marco Teórico: Precios Mentirosos, Subsidios Ocultos y Costos Hundidos (Fontaine, Cap. I · Clase 1)</span>
        <span class="enun-badge">Desplegar teoría de apoyo</span>
      </summary>
      <div class="teo-body">
        <ul>
          <li><b>Evaluación Privada vs. Social ante Subsidios:</b> un subsidio estatal a un insumo (agua, energía, combustible) abarata el costo privado y puede volver rentable un proyecto que para el país destruye riqueza (<b>EP &gt; 0</b> pero <b>ES = EP − Sub &lt; 0</b>).</li>
          <li><b>Valor Agregado (VA) ≠ Rentabilidad Social:</b> crear empleo o aumentar el Valor Agregado (en el pan envasado sube el VA) NO garantiza que un proyecto convenga si los recursos adicionales valen más que el valor que aportan.</li>
          <li><b>Regla de Oro de Costos Hundidos (Clase 1, láminas 33–36):</b> todo desembolso ya comprometido e irrecuperable (ej. estudio de factibilidad ya pagado) <b>NO entra al flujo incremental</b>. Con la planta ya construida, el único costo de capital pertinente es el <b>costo de oportunidad del Valor de Liquidación hoy</b>.</li>
        </ul>
      </div>
    </details>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 6: DÉFICIT AGUA POTABLE (10 AÑOS ANIMADO) + TEA Y CAPM A 60 FPS  -->
  <!-- ====================================================================== -->
  <div id="panel-agua" class="panel">
    <div class="sec-title">
      <span>Proyección de Déficit de Agua Potable a 10 Años (CEPAL Serie Manuales N° 39)</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarAgua()">Reproducir 10 Años</button>
        <button class="act-btn" onclick="fijarGhostAgua()">Fijar Fantasma Aquí</button>
        <button class="act-btn" onclick="resetAgua()">Restaurar Caso CEPAL (35.200 hab.)</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento Oficial CEPAL N° 39 (Proyección Geométrica de Población y Déficit Hídrico)</span>
        <span class="enun-badge">Fórmula: Pt = P0·(1+r)^t</span>
      </summary>
      <div class="enun-body" id="ag-enunciado"></div>
    </details>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>Población Base P0 (hab.)</span><span id="ag-p0-v" class="sl-val">35.200</span></div>
        <input id="ag-p0" type="range" min="15000" max="75000" step="200" value="35200" oninput="drawAgua()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Crecimiento Anual r (%)</span><span id="ag-r-v" class="sl-val">3,2%</span></div>
        <input id="ag-r" type="range" min="0.5" max="7.5" step="0.1" value="3.2" oninput="drawAgua()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Consumo (L/día/persona)</span><span id="ag-dot-v" class="sl-val">180 L</span></div>
        <input id="ag-dot" type="range" min="80" max="300" step="10" value="180" oninput="drawAgua()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Oferta Planta Fija (m³/día)</span><span id="ag-ofe-v" class="sl-val">5.000 m³</span></div>
        <input id="ag-ofe" type="range" min="2000" max="12000" step="250" value="5000" oninput="drawAgua()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Demanda Año 1 (t=0)</div><div id="ag-k-d1" class="kpi-val">6.336 m³/d</div><div id="ag-k-def1" class="kpi-sub">Déficit Año 1: 1.336 m³/d</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Demanda Año 10 (t=9)</div><div id="ag-k-d10" class="kpi-val">8.413 m³/d</div><div id="ag-k-def10" class="kpi-sub">Déficit Año 10: 3.413 m³/d</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Población Proyectada Año 10</div><div id="ag-k-p10" class="kpi-val">46.737 hab.</div><div id="ag-k-dp" class="kpi-sub">Δ Déficit vs Fantasma: 0 m³</div></div>
    </div>

    <div id="ag-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-agua" viewBox="0 0 960 330"></svg></div>

    <div class="sec-title" style="margin-top:12px;">
      <span>Compendio Financiero: Tasa Efectiva Anual (TEA) y Modelo CAPM (Línea SML)</span>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1.25fr;gap:12px;">
      <div class="sl-card" style="padding:11px 13px;">
        <div class="sl-head"><span>Tasa Nominal Anual TNA (%)</span><span id="tc-tna-v" class="sl-val">12,0%</span></div>
        <input id="tc-tna" type="range" min="1.0" max="30.0" step="0.5" value="12.0" oninput="drawTeaCapm()" />
        <div class="sl-head" style="margin-top:8px;"><span>Período Capitalización t (días)</span><span id="tc-dias-v" class="sl-val">30 días</span></div>
        <input id="tc-dias" type="range" min="1" max="365" step="1" value="30" oninput="drawTeaCapm()" />
        <div id="tc-fstrip" class="fstrip-grid"></div>
    <div id="tc-tea-box" class="sol-box" style="margin-top:10px;"></div>
      </div>
      <div class="sl-card" style="padding:11px 13px;">
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;">
          <div><div class="sl-head"><span>Rf (%)</span><span id="tc-rf-v" class="sl-val">4,5%</span></div><input id="tc-rf" type="range" min="0.5" max="9.0" step="0.1" value="4.5" oninput="drawTeaCapm()" /></div>
          <div><div class="sl-head"><span>Beta (β)</span><span id="tc-beta-v" class="sl-val">1,15</span></div><input id="tc-beta" type="range" min="0.2" max="2.4" step="0.05" value="1.15" oninput="drawTeaCapm()" /></div>
          <div><div class="sl-head"><span>E(Rm) (%)</span><span id="tc-rm-v" class="sl-val">11,0%</span></div><input id="tc-rm" type="range" min="6.0" max="18.0" step="0.5" value="11.0" oninput="drawTeaCapm()" /></div>
        </div>
        <div class="svg-box" style="margin-top:6px;"><svg id="svg-capm" viewBox="0 0 460 150"></svg></div>
        <div id="tc-capm-box" class="sol-box" style="margin-top:6px;"></div>
      </div>
    </div>
    <div id="ped-agua" class="ped-grid"></div>
    <details class="teo-box">
      <summary>
        <span>Marco Teórico: Proyección de Demanda SNI, VAN/VAC/CAE, TEA y CAPM (SNI 2025 · Clase 1 y 2)</span>
        <span class="enun-badge">Desplegar teoría de apoyo</span>
      </summary>
      <div class="teo-body">
        <ul>
          <li><b>Optimización de la Situación Base y Brecha (Déficit):</b> antes de dimensionar una inversión pública, el SNI exige proyectar la población (<b>P<sub>t</sub> = P<sub>0</sub>·(1+r)<sup>t</sup></b>), multiplicar por la dotación normativa y restar la oferta optimizada actual para hallar el déficit real.</li>
          <li><b>¿Cuándo elegir VAN, VAC o CAE?</b> Usa <b>VAN</b> si los beneficios son medibles y las vidas útiles son iguales; usa <b>VAC</b> si los beneficios son idénticos o difíciles de monetizar con igual horizonte; usa <b>CAE = VAC · [r(1+r)<sup>n</sup> / ((1+r)<sup>n</sup> − 1)]</b> cuando las alternativas tienen <b>distinta vida útil</b>.</li>
          <li><b>TEA vs. TNA y CAPM:</b> capitalizar más frecuente (menor número de días) eleva la TEA por encima de la TNA hasta el límite continuo <b>e<sup>TNA</sup> − 1</b>. En finanzas privadas, el <b>CAPM</b> fija el costo patrimonial <b>k<sub>e</sub> = R<sub>f</sub> + β(R<sub>m</sub> − R<sub>f</sub>)</b> para descontar los flujos.</li>
        </ul>
      </div>
    </details>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 7: AMBIENTAL RA2 (MATRIZ DE LEOPOLD + BARZEV MCV + GEI A 60 FPS) -->
  <!-- ====================================================================== -->
  <div id="panel-ambiental" class="panel">
    <div class="sec-title">
      <span>Evaluación Ambiental (RA2): Matriz de Leopold, Costo de Viaje (Barzev) y Emisiones GEI 2026</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="presetLeopold('mitigado')">Escenario Con Mitigación Circular</button>
        <button class="act-btn" onclick="presetLeopold('sin_mit')">Escenario Sin Mitigación</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento RA2 (Radoslav Barzev 2002 + Precios Sociales SNI 2026)</span>
        <span class="enun-badge">Magnitud M (-10 a +10) × Importancia I (1 a 10)</span>
      </summary>
      <div class="enun-body">
        Ajuste la <b>Magnitud (M)</b> e <b>Importancia (I)</b> de cada cruce acción-factor en la <b>Matriz de Leopold</b> para calcular el puntaje ambiental neto en tiempo real.
        Abajo, simule la valoración económica de un parque/humedal mediante el <b>Método del Costo de Viaje (MCV)</b> usando el VST Recreación oficial 2026 (<b>$2.792/h-pax</b>) y la conversión <b>IPCC a 100 años</b> (<b>CH<sub>4</sub>×28</b>, <b>N<sub>2</sub>O×265</b> a <b>$71.801/t CO<sub>2</sub>eq</b>).
      </div>
    </details>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Impacto Ambiental Neto (∑ M×I)</div><div id="leo-k-tot" class="kpi-val">+145</div><div id="leo-k-diag" class="kpi-sub">Balance Ambiental Positivo</div></div>
      <div class="kpi" style="border-left-color:#059669;"><div class="kpi-lbl">Suma Impactos Positivos</div><div id="leo-k-pos" class="kpi-val">+210</div><div class="kpi-sub">Celdas verdes</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Suma Impactos Negativos</div><div id="leo-k-neg" class="kpi-val">-65</div><div class="kpi-sub">Celdas rojas</div></div>
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Valor Económico Ambiental/año</div><div id="amb-k-val" class="kpi-val">$68,4 MM</div><div id="amb-k-sub" class="kpi-sub">MCV Recreación + Carbono GEI</div></div>
    </div>

    <div id="leo-grid-wrap"></div>

    <div class="sec-title" style="margin-top:12px;">
      <span>Valoración Económica Ambiental (MCV Barzev) y Conversión GEI IPCC 2026 ($71.801 / t CO2eq)</span>
    </div>
    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>Visitas Anuales al Parque</span><span id="amb-vis-v" class="sl-val">12.000</span></div>
        <input id="amb-vis" type="range" min="1000" max="40000" step="500" value="12000" oninput="drawAmbiental()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Horas Viaje + Estadía (VST $2.792)</span><span id="amb-hrs-v" class="sl-val">1,5 h</span></div>
        <input id="amb-hrs" type="range" min="0.5" max="5.0" step="0.25" value="1.5" oninput="drawAmbiental()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Gasto Transporte/Entrada ($/visita)</span><span id="amb-gas-v" class="sl-val">$1.500</span></div>
        <input id="amb-gas" type="range" min="0" max="10000" step="250" value="1500" oninput="drawAmbiental()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>CO2 Directo Evitado (t/año)</span><span id="amb-co2-v" class="sl-val">120 t</span></div>
        <input id="amb-co2" type="range" min="0" max="500" step="10" value="120" oninput="drawAmbiental()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Metano CH4 (t/año × 28)</span><span id="amb-ch4-v" class="sl-val">8,5 t</span></div>
        <input id="amb-ch4" type="range" min="0" max="40" step="0.5" value="8.5" oninput="drawAmbiental()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Óxido Nitroso N2O (t/año × 265)</span><span id="amb-n2o-v" class="sl-val">0,2 t</span></div>
        <input id="amb-n2o" type="range" min="0" max="5" step="0.1" value="0.2" oninput="drawAmbiental()" />
      </div>
    </div>
    <div id="amb-fstrip" class="fstrip-grid"></div>
    <div id="amb-sol" class="sol-box"></div>
    <div id="ped-ambiental" class="ped-grid"></div>
    <details class="teo-box">
      <summary>
        <span>Marco Teórico: Valoración Económica Ambiental RA2 (Barzev 2002 · Precios Sociales SNI 2026)</span>
        <span class="enun-badge">Desplegar teoría de apoyo</span>
      </summary>
      <div class="teo-body">
        <ul>
          <li><b>Bienes vs. Servicios Ambientales (Barzev, 2002):</b> los <b>bienes</b> son tangibles y se consumen o transforman al usarse (agua, madera, leña); los <b>servicios</b> son funciones ecosistémicas intangibles que no se gastan al disfrutarse (belleza escénica, recreación, captura de carbono).</li>
          <li><b>Método de Costo de Viaje (MCV):</b> estima el valor recreativo de un parque o humedal usando el tiempo de traslado (valorado en Chile con el <b>VST Recreativo 2026 = $2.792 CLP/h-pax</b>) más los gastos directos de transporte y entrada.</li>
          <li><b>Gases de Efecto Invernadero (IPCC 100 años + SNI 2026):</b> convierte cada gas a toneladas equivalentes de CO<sub>2</sub> usando su Potencial de Calentamiento Global: <b>CO<sub>2</sub>eq = t<sub>CO2</sub> + 28·t<sub>CH4</sub> + 265·t<sub>N2O</sub></b>, y valoriza cada tonelada a <b>$71.801 CLP/t</b>.</li>
        </ul>
      </div>
    </details>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 8: ÁRBOLES CAUSALES (PROBLEMAS <-> OBJETIVOS) + QUIZ V/F RA1     -->
  <!-- ====================================================================== -->
  <div id="panel-arboles" class="panel">
    <div class="sec-title">
      <span>Metodología del Marco Lógico: Árbol de Problemas y Árbol de Objetivos (SNI / CEPAL N° 39)</span>
      <div class="btn-bar">
        <button id="arb-btn-prob" class="act-btn primary" onclick="setModoArbol(false)">Ver Árbol de Problemas (Negativo)</button>
        <button id="arb-btn-obj" class="act-btn" onclick="setModoArbol(true)">Transformar a Árbol de Objetivos (Positivo)</button>
      </div>
    </div>

    <div class="mec-filters">
      <button class="flt-btn active" onclick="setCasoArbol(0, this)">1. Productores de Berries (Ejercicio Clase)</button>
      <button class="flt-btn" onclick="setCasoArbol(1, this)">2. Nutrición Adulto Mayor (MARCO LOGICO.pdf)</button>
      <button class="flt-btn" onclick="setCasoArbol(2, this)">3. Transporte y Ausentismo (Proceso2 RA1.pdf)</button>
    </div>

    <div class="svg-box"><svg id="svg-arbol" viewBox="0 0 960 365"></svg></div>
    <div id="arb-alt-box" class="note-box"></div>
    <div id="ped-arbol" class="ped-grid"></div>

    <div class="sec-title" style="margin-top:14px;">
      <span>Repaso Verdadero / Falso — Prueba Proceso 2 RA1 (Dra. Luz María Ferrada)</span>
      <div class="btn-bar">
        <span id="vf-score" class="pill-score">Puntaje: 0 / 8</span>
        <button class="act-btn" onclick="resetQuizVF()">Reiniciar Quiz V/F</button>
      </div>
    </div>
    <div id="vf-list"></div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 4: HOJA DE ENTRENAMIENTO MECÁNICO (FÓRMULAS + ESQUELETOS SVG)    -->
  <!-- ====================================================================== -->
  <div id="panel-mecanica" class="panel">
    <div class="sec-title">
      <span>Formulario y Entrenamiento Mecánico — Evaluación Integrada de Proyectos (ULagos 2026)</span>
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
        <span>Esqueletos de Gráficos Clave para Repaso en Cuaderno (6 diagramas)</span>
        <span style="font-size:11px;font-weight:600;color:#334155;">En Modo Ciego, haz clic en cada gráfico para revelar las etiquetas</span>
      </div>
      <div class="skel-grid" id="mec-skel-grid"></div>

      <details class="enun-box" style="margin-top:12px;">
        <summary>
          <span>Tabla Rápida de Referencia: Precios Sociales Oficiales SNI 2026 (MDSF, 31 mar 2026)</span>
          <span class="enun-badge">Desplegar valores oficiales</span>
        </summary>
        <div class="enun-body" style="font-family:Consolas,monospace;font-size:11.5px;line-height:1.55;">
          • <b>TSD 2026:</b> 5,5% &nbsp;|&nbsp; <b>MO:</b> MOC 0,97 · MOSC 0,95 · MONC 0,91 &nbsp;|&nbsp; <b>FCSD (Divisa):</b> 1,00 &nbsp;|&nbsp; <b>UF Ref.:</b> $39.727,96<br/>
          • <b>VST Urbano:</b> Viaje (1x) $3.338/h · Espera/Caminata (2x) $6.676/h · Recreación $2.792/h · Interurbano $10.047/h · Carga $12.954/h-veh<br/>
          • <b>Combustibles:</b> Diésel $805/L · Gas 93 $737/L · Gas 95 $768/L · Gas 97 $822/L &nbsp;|&nbsp; <b>Electricidad BT:</b> $124,8/kWh<br/>
          • <b>Carbono y Seguridad Vial:</b> P_Social CO2 = $71.801/t CO2eq (CH4 × 28 · N2O × 265) &nbsp;|&nbsp; <b>VVE:</b> $2.383.677.600
        </div>
      </details>
    </div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 10: MAPA CAUSAL TEÓRICO, LECTURA EN 3 CAPAS Y QUIZ INTER-PILARES -->
  <!-- ====================================================================== -->
  <div id="panel-lectura" class="panel">
    <div class="sec-title">
      <span>Mapa Conceptual Integrado — Evaluación de Proyectos (Conexión entre los 5 Pilares)</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="activarEscenarioProy('subsidio')">Cadena A: VANP &lt; 0 y VANS &gt; 0</button>
        <button class="act-btn" onclick="activarEscenarioProy('ambiental')">Cadena B: Externalidad RA2 → VANS</button>
        <button class="act-btn" onclick="activarEscenarioProy('marco')">Cadena C: Árbol → Flujo → SNI</button>
        <button class="act-btn" onclick="selectPilarProy('P1')">Ver Todo Libre</button>
      </div>
    </div>

    <div class="svg-box"><svg id="svg-mapa-proy" viewBox="0 0 980 320"></svg></div>
    <div id="mapa-proy-detail" class="map-detail-card"></div>

    <div class="sec-title" style="margin-top:14px;">
      <span>Síntesis Teórica en 3 Capas por Bibliografía Oficial (Fontaine · SNI 2026 · Barzev · CEPAL N° 39)</span>
      <div class="btn-bar">
        <button id="cap-btn-core" class="act-btn primary" onclick="setCapaProy('core')">Capa 1: Idea Central</button>
        <button id="cap-btn-bridge" class="act-btn" onclick="setCapaProy('bridge')">Capa 2: Puentes entre Pilares</button>
        <button id="cap-btn-trap" class="act-btn" onclick="setCapaProy('trap')">Capa 3: Trampas de Prueba</button>
        <button id="cap-btn-all" class="act-btn" onclick="setCapaProy('all')">Ver las 3 Capas</button>
      </div>
    </div>

    <div class="mec-filters">
      <button class="flt-btn active" onclick="filtrarLecturaProy('all', this)">Toda la Bibliografía (6)</button>
      <button class="flt-btn" onclick="filtrarLecturaProy('P1', this)">P1: Bienestar / VSP (1)</button>
      <button class="flt-btn" onclick="filtrarLecturaProy('P2', this)">P2: Flujos / Hundidos / CAPM (1)</button>
      <button class="flt-btn" onclick="filtrarLecturaProy('P3', this)">P3: Precios Sociales SNI 2026 (2)</button>
      <button class="flt-btn" onclick="filtrarLecturaProy('P4', this)">P4: Ambiental RA2 / Leopold (1)</button>
      <button class="flt-btn" onclick="filtrarLecturaProy('P5', this)">P5: Marco Lógico CEPAL 39 (1)</button>
    </div>

    <div class="lec-grid" id="lec-proy-grid"></div>

    <div class="sec-title" style="margin-top:14px;">
      <span>Control de Lectura y Aplicación Cruzada (10 preguntas integradas)</span>
      <div class="btn-bar">
        <span id="qz-proy-score" class="pill-score">Aciertos: 0 / 10</span>
        <button class="act-btn" onclick="toggleSoloErradasProy(this)">Ver Solo Pendientes / Erradas</button>
        <button class="act-btn" onclick="resetQuizProy()">Reiniciar Control</button>
      </div>
    </div>
    <div id="qz-proy-list"></div>
  </div>
</div>

<script>
const NS = "http://www.w3.org/2000/svg";

function drawAxesPizarra(svg, x0, yTop, xRight, yBot, yTitle, xTitle) {
  el("line", { x1: x0, y1: yBot, x2: xRight + 6, y2: yBot, stroke: "#0F172A", "stroke-width": "1.8", "marker-end": "url(#arr-dark)" }, svg);
  el("line", { x1: x0, y1: yBot, x2: x0, y2: yTop - 6, stroke: "#0F172A", "stroke-width": "1.8", "marker-end": "url(#arr-dark)" }, svg);
  if (yTitle) {
    const ty = el("text", { x: x0 + 8, y: yTop - 7, fill: "#0F172A", "font-size": "11", "font-weight": "800", "text-anchor": "start" }, svg);
    ty.textContent = yTitle;
  }
  if (xTitle) {
    const tx = el("text", { x: xRight + 4, y: yBot + 36, fill: "#0F172A", "font-size": "11", "font-weight": "800", "text-anchor": "end" }, svg);
    tx.textContent = xTitle;
  }
}
function drawPill(svg, x, y, text, color, bg="rgba(255,255,255,0.95)", anchor="middle", fs="10.8") {
  const bw = Math.max(26, text.length * 6.3 + 10);
  const rx = anchor === "middle" ? x - bw / 2 : (anchor === "start" ? x - 4 : x - bw + 4);
  el("rect", { x: rx, y: y - 11.5, width: bw, height: 16.5, rx: 4, fill: bg, stroke: color, "stroke-width": "1.1" }, svg);
  const t = el("text", { x, y: y + 0.5, fill: color, "font-size": fs, "font-weight": "800", "text-anchor": anchor }, svg);
  t.textContent = text;
}
function drawAxisBreakX(svg, xPos, yBot) {
  el("rect", { x: xPos - 5, y: yBot - 5, width: 10, height: 10, fill: "#FFFFFF" }, svg);
  el("line", { x1: xPos - 4, y1: yBot + 5, x2: xPos, y2: yBot - 5, stroke: "#0F172A", "stroke-width": "1.5" }, svg);
  el("line", { x1: xPos + 1, y1: yBot + 5, x2: xPos + 5, y2: yBot - 5, stroke: "#0F172A", "stroke-width": "1.5" }, svg);
}

const fstripXrayState = {};
const fstripPrevVals = {};

function mFrac(num, den) {
  return `<span class="frac"><span class="num">${num}</span><span class="den">${den}</span></span>`;
}
function vChip(val, cls="vc-b", tip="", trackKey="") {
  let pop = "";
  if (trackKey) {
    if (fstripPrevVals[trackKey] !== undefined && fstripPrevVals[trackKey] !== String(val)) pop = " v-pop";
    fstripPrevVals[trackKey] = String(val);
  }
  const tAttr = tip ? ` title="${tip.replace(/"/g, '&quot;')}"` : "";
  return `<span class="v-chip ${cls}${pop}"${tAttr}>${val}</span>`;
}
function eChip(displayVal, rawNum, bindKey, step="any", cls="vc-b", tip="") {
  let pop = "";
  if (bindKey) {
    if (fstripPrevVals[bindKey] !== undefined && fstripPrevVals[bindKey] !== String(displayVal)) pop = " v-pop";
    fstripPrevVals[bindKey] = String(displayVal);
  }
  const fullTip = (tip ? tip + " · " : "") + "Clic para editar directo en la fórmula (Enter aplica)";
  const tAttr = ` title="${fullTip.replace(/"/g, '&quot;')}"`;
  return `<span class="v-chip editable ${cls}${pop}"${tAttr} data-bind="${bindKey}" data-raw="${rawNum}" data-step="${step}" onclick="openChipEditor(event, this)">${displayVal}</span>`;
}
function rChip(val, isNeg=false, tip="") {
  const tAttr = tip ? ` title="${tip.replace(/"/g, '&quot;')}"` : "";
  return `<span class="vc-res${isNeg ? ' neg' : ''}"${tAttr}>${val}</span>`;
}
function toggleXrayCard(cardKey, headEl) {
  const cardEl = headEl.closest(".fstrip-card");
  if (!cardEl) return;
  fstripXrayState[cardKey] = !fstripXrayState[cardKey];
  cardEl.classList.toggle("xray-on", !!fstripXrayState[cardKey]);
  const pill = cardEl.querySelector(".xray-pill");
  if (pill) pill.textContent = fstripXrayState[cardKey] ? "Rayos X: ON ⇄" : "f(x) → 123";
}
function setSliderSmart(id, val, hardMin=null, hardMax=null) {
  const sl = document.getElementById(id);
  if (!sl) return val;
  let v = val;
  if (hardMin !== null) v = Math.max(hardMin, v);
  if (hardMax !== null) v = Math.min(hardMax, v);
  if (v > parseFloat(sl.max) && (hardMax === null || v <= hardMax)) sl.max = Math.ceil(v * 1.25);
  if (v < parseFloat(sl.min) && (hardMin === null || v >= hardMin)) sl.min = Math.floor(v * 0.5);
  sl.value = v;
  return v;
}
function applyChipEdit(bindKey, rawStr) {
  const clean = String(rawStr || "").replace(/,/g, ".").trim();
  const val = parseFloat(clean);
  if (!Number.isFinite(val)) return false;

  // 1. Leche / VSP
  if (bindKey === "lc_A") { stateLc.A = Math.max(20, val); setSliderSmart("lc-a", stateLc.A, 20, null); syncEqInputsFromStateLc(); drawLeche(); return true; }
  if (bindKey === "lc_B") { stateLc.B = Math.max(0.001, val); setSliderSmart("lc-b", stateLc.B, 0.001, null); syncEqInputsFromStateLc(); drawLeche(); return true; }
  if (bindKey === "lc_C") { stateLc.C = val; setSliderSmart("lc-c", stateLc.C, null, null); syncEqInputsFromStateLc(); drawLeche(); return true; }
  if (bindKey === "lc_D") { stateLc.D = Math.max(0.001, val); setSliderSmart("lc-d", stateLc.D, 0.001, null); syncEqInputsFromStateLc(); drawLeche(); return true; }
  if (bindKey === "lc_Q") { stateLc.Q = Math.max(0, Math.round(val)); setSliderSmart("lc-q", stateLc.Q, 0, null); syncEqInputsFromStateLc(); drawLeche(); return true; }

  // 2. Transporte y Externalidades
  if (bindKey === "tr_p0") { document.getElementById("tr-p0-in").value = Math.max(500, Math.round(val)); drawTransporte(); return true; }
  if (bindKey === "tr_p1") { document.getElementById("tr-p1-in").value = Math.max(100, Math.round(val)); drawTransporte(); return true; }
  if (bindKey === "tr_x0") { setSliderSmart("tr-x0", Math.max(1000, Math.round(val)), 1000, null); drawTransporte(); return true; }
  if (bindKey === "tr_x1") { setSliderSmart("tr-x1", Math.max(2500, Math.round(val)), 2500, null); drawTransporte(); return true; }
  if (bindKey === "tr_cp") { setSliderSmart("tr-cp", Math.max(0, Math.round(val)), 0, null); drawTransporte(); return true; }
  if (bindKey === "tr_cs") { setSliderSmart("tr-cs", Math.max(0, Math.round(val)), 0, null); drawTransporte(); return true; }

  // 3. Elasticidades Extremas
  if (bindKey === "el_rd") { setSliderSmart("el-rd", Math.round(val), 0, 100); drawElast(); return true; }
  if (bindKey === "el_ro") { setSliderSmart("el-ro", Math.round(val), 0, 100); drawElast(); return true; }
  if (bindKey === "el_dq") { setSliderSmart("el-dq", Math.max(10, Math.round(val)), 10, null); drawElast(); return true; }

  // 4. Waterfall SNI + Radar Quiebre
  if (bindKey === "wf_cap")  { setSliderSmart("wf-cap", Math.max(1, val), 1, null); drawWaterfall(); return true; }
  if (bindKey === "wf_vol")  { setSliderSmart("wf-vol", Math.max(5, Math.round(val)), 5, null); drawWaterfall(); return true; }
  if (bindKey === "wf_mar")  { setSliderSmart("wf-mar", Math.max(1000, Math.round(val)), 1000, null); drawWaterfall(); return true; }
  if (bindKey === "wf_wacc") { setSliderSmart("wf-wacc", val, 1.0, 35.0); drawWaterfall(); return true; }
  if (bindKey === "wf_mo")   { setSliderSmart("wf-mo", Math.max(1, val), 1, null); drawWaterfall(); return true; }
  if (bindKey === "wf_ch4")  { setSliderSmart("wf-ch4", Math.max(0, val), 0, null); drawWaterfall(); return true; }
  if (bindKey === "rd_vol")  { setSliderSmart("rd-vol", Math.round(val), -60, 60); drawWaterfall(); return true; }
  if (bindKey === "rd_pre")  { setSliderSmart("rd-pre", Math.round(val), -60, 60); drawWaterfall(); return true; }
  if (bindKey === "rd_cos")  { setSliderSmart("rd-cos", Math.round(val), -50, 80); drawWaterfall(); return true; }

  // 5. Horno de Pan y Costos Hundidos
  if (bindKey === "hn_pb")  { setSliderSmart("hn-pb", Math.max(50, Math.round(val)), 50, null); drawHorno(); return true; }
  if (bindKey === "hn_pe")  { setSliderSmart("hn-pe", Math.max(60, Math.round(val)), 60, null); drawHorno(); return true; }
  if (bindKey === "hn_ce")  { setSliderSmart("hn-ce", Math.max(1, Math.round(val)), 1, null); drawHorno(); return true; }
  if (bindKey === "hn_sub") { setSliderSmart("hn-sub", Math.max(0, Math.round(val)), 0, null); drawHorno(); return true; }
  if (bindKey === "ch_liq") { setSliderSmart("ch-liq", Math.max(0, Math.round(val)), 0, null); drawHundido(); return true; }

  // 6. Agua 10 Años + TEA / CAPM
  if (bindKey === "ag_p0")   { setSliderSmart("ag-p0", Math.max(1000, Math.round(val)), 1000, null); drawAgua(); return true; }
  if (bindKey === "ag_r")    { setSliderSmart("ag-r", val, 0.0, 15.0); drawAgua(); return true; }
  if (bindKey === "ag_dot")  { setSliderSmart("ag-dot", Math.max(20, Math.round(val)), 20, null); drawAgua(); return true; }
  if (bindKey === "ag_ofe")  { setSliderSmart("ag-ofe", Math.max(200, Math.round(val)), 200, null); drawAgua(); return true; }
  if (bindKey === "tc_tna")  { setSliderSmart("tc-tna", val, 0.5, 60.0); drawTeaCapm(); return true; }
  if (bindKey === "tc_dias") { setSliderSmart("tc-dias", Math.round(val), 1, 365); drawTeaCapm(); return true; }
  if (bindKey === "tc_rf")   { setSliderSmart("tc-rf", val, 0.0, 20.0); drawTeaCapm(); return true; }
  if (bindKey === "tc_beta") { setSliderSmart("tc-beta", val, 0.0, 3.5); drawTeaCapm(); return true; }
  if (bindKey === "tc_rm")   { setSliderSmart("tc-rm", val, 1.0, 35.0); drawTeaCapm(); return true; }

  // 7. Ambiental RA2
  if (bindKey === "amb_vis") { setSliderSmart("amb-vis", Math.max(0, Math.round(val)), 0, null); drawAmbiental(); return true; }
  if (bindKey === "amb_hrs") { setSliderSmart("amb-hrs", Math.max(0, val), 0, null); drawAmbiental(); return true; }
  if (bindKey === "amb_gas") { setSliderSmart("amb-gas", Math.max(0, Math.round(val)), 0, null); drawAmbiental(); return true; }
  if (bindKey === "amb_co2") { setSliderSmart("amb-co2", Math.max(0, Math.round(val)), 0, null); drawAmbiental(); return true; }
  if (bindKey === "amb_ch4") { setSliderSmart("amb-ch4", Math.max(0, val), 0, null); drawAmbiental(); return true; }
  if (bindKey === "amb_n2o") { setSliderSmart("amb-n2o", Math.max(0, val), 0, null); drawAmbiental(); return true; }
  return false;
}
function openChipEditor(ev, chipEl) {
  ev.stopPropagation();
  if (chipEl.dataset.editing === "1") return;
  chipEl.dataset.editing = "1";
  const bindKey = chipEl.dataset.bind;
  const rawVal = chipEl.dataset.raw;
  const stepVal = chipEl.dataset.step || "any";
  const origHtml = chipEl.innerHTML;

  const inp = document.createElement("input");
  inp.type = "number";
  inp.step = stepVal;
  inp.value = rawVal;
  inp.className = "chip-inline-in";
  inp.style.width = Math.max(66, String(rawVal).length * 10 + 30) + "px";

  let finished = false;
  const commit = () => {
    if (finished) return;
    finished = true;
    const ok = applyChipEdit(bindKey, inp.value);
    if (!ok) {
      chipEl.innerHTML = origHtml;
      chipEl.dataset.editing = "0";
    }
  };
  const cancel = () => {
    if (finished) return;
    finished = true;
    chipEl.innerHTML = origHtml;
    chipEl.dataset.editing = "0";
  };

  inp.addEventListener("keydown", e => {
    if (e.key === "Enter") { e.preventDefault(); commit(); }
    else if (e.key === "Escape") { e.preventDefault(); cancel(); }
  });
  inp.addEventListener("blur", () => commit());
  inp.addEventListener("click", e => e.stopPropagation());

  chipEl.innerHTML = "";
  chipEl.appendChild(inp);
  inp.focus();
  inp.select();
}
function renderFormulaStrip(id, cards) {
  const box = document.getElementById(id);
  if (!box) return;
  box.innerHTML = cards.map((c, idx) => {
    const k = `${id}_${idx}`;
    const isOn = !!fstripXrayState[k];
    const noteHtml = c.note ? `<div class="fstrip-note">${c.note}</div>` : "";
    return `
      <div class="fstrip-card${isOn ? ' xray-on' : ''}" style="border-left-color:${c.col || '#1E3A8A'};">
        <div class="fstrip-head" onclick="toggleXrayCard('${k}', this)" title="Clic aquí para alternar Modo Rayos X">
          <span class="fstrip-lbl" style="color:${c.col || '#1E3A8A'};">${c.lbl}</span>
          <span class="xray-pill">${isOn ? "Rayos X: ON ⇄" : "f(x) → 123"}</span>
        </div>
        <div class="fstrip-eq">${c.eq}</div>
        <div class="fstrip-sub">${c.sub || ""}</div>
        ${noteHtml}
      </div>`;
  }).join("");
}

function renderPedBox(id, lectura, paradoja, defensa) {
  const box = document.getElementById(id);
  if (!box) return;
  box.innerHTML = `
    <div class="ped-card">
      <div class="ped-hd">Lectura Dinámica del Escenario</div>
      <div>${lectura}</div>
    </div>
    <div class="ped-card p-cur">
      <div class="ped-hd">Dato Curioso y Paradoja Teórica</div>
      <div>${paradoja}</div>
    </div>
    <div class="ped-card p-def">
      <div class="ped-hd">Aplicación Real y Defensa en Prueba</div>
      <div>${defensa}</div>
    </div>`;
}

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
  if (name === "waterfall") drawWaterfall();
  if (name === "horno") { drawHorno(); drawHundido(); }
  if (name === "agua") { drawAgua(); drawTeaCapm(); }
  if (name === "ambiental") drawAmbiental();
  if (name === "arboles") { drawArbol(); renderQuizVF(); }
  if (name === "mecanica") renderMecanica();
  if (name === "lectura") { drawMapaProy(); renderLecturaProy(); renderQuizProy(); }
}
function jumpToTab(name) {
  const btns = Array.from(document.querySelectorAll(".top-tabs .tab-btn"));
  const target = btns.find(b => (b.getAttribute("onclick") || "").includes("'" + name + "'"));
  if (target) {
    openTab(name, target);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

// ============================================================================
// 1. SIMULADOR TRANSPORTE Y EXTERNALIDADES (ENUNCIADO VIVO + AUTOESCALA)
// ============================================================================
let ghostTr = { x0: 70000, x1: 100030, cp: 1300, cs: 1700, p0: 5000, p1: 3500 };
let animTrId = null;

function fijarGhostTransporte() {
  ghostTr = {
    x0: +document.getElementById("tr-x0").value,
    x1: +document.getElementById("tr-x1").value,
    cp: +document.getElementById("tr-cp").value,
    cs: +document.getElementById("tr-cs").value,
    p0: +document.getElementById("tr-p0-in").value || 5000,
    p1: +document.getElementById("tr-p1-in").value || 3500,
  };
  drawTransporte();
}
function resetTransporte() {
  if (animTrId) cancelAnimationFrame(animTrId);
  document.getElementById("tr-x0").value = 70000;
  document.getElementById("tr-x1").value = 100030;
  document.getElementById("tr-cp").value = 1300;
  document.getElementById("tr-cs").value = 1700;
  document.getElementById("tr-p0-in").value = 5000;
  document.getElementById("tr-p1-in").value = 3500;
  ghostTr = { x0: 70000, x1: 100030, cp: 1300, cs: 1700, p0: 5000, p1: 3500 };
  drawTransporte();
}
function presetTransporteExt() {
  fijarGhostTransporte();
  document.getElementById("tr-cp").value = 500;
  document.getElementById("tr-cs").value = 700;
  drawTransporte();
}
function animarTransporte() {
  if (animTrId) cancelAnimationFrame(animTrId);
  const x0 = +document.getElementById("tr-x0").value;
  const targetX1 = 100030;
  const startX1 = Math.max(72000, x0 + 2000);
  ghostTr = {
    x0, x1: startX1,
    cp: +document.getElementById("tr-cp").value,
    cs: +document.getElementById("tr-cs").value,
    p0: +document.getElementById("tr-p0-in").value || 5000,
    p1: +document.getElementById("tr-p1-in").value || 3500,
  };
  const t0 = performance.now(), dur = 1600;
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
  const p0 = Math.max(500, +document.getElementById("tr-p0-in").value || 5000);
  let p1 = Math.max(100, +document.getElementById("tr-p1-in").value || 3500);
  if (p1 >= p0 - 100) p1 = Math.max(100, p0 - 200);

  document.getElementById("tr-x0-v").textContent = fmtInt(x0);
  document.getElementById("tr-x1-v").textContent = fmtInt(x1);
  document.getElementById("tr-cp-v").textContent = "$" + fmtInt(cp);
  document.getElementById("tr-cs-v").textContent = "$" + fmtInt(cs);
  setDeltaBadge("tr-x0-d", x0 - ghostTr.x0);
  setDeltaBadge("tr-x1-d", x1 - ghostTr.x1);
  setDeltaBadge("tr-cp-d", cp - ghostTr.cp, "", true);
  setDeltaBadge("tr-cs-d", cs - ghostTr.cs, "", true);

  const dx = x1 - x0;
  const pend = (p0 - p1) / dx;
  const aDem = p0 + pend * x0;
  const ed = ((x1 - x0) / x0) / ((p1 - p0) / p0);
  const ben = 0.5 * (p0 + p1) * dx;
  const brecha = cs - cp;
  const ext = brecha * x1;
  const csTotal = cs * x1;

  document.getElementById("tr-eq-display").value = `Pd = ${fmtInt(aDem)} - ${fmtDec(pend, 4)}·X`;

  document.getElementById("tr-enunciado").innerHTML =
    `Un proyecto de transporte público busca ampliar el servicio en un corredor urbano con capacidad máxima de <b>120.000 pasajes</b>. ` +
    `En la situación sin proyecto se demandan <b>X<sub>0</sub> = ${fmtInt(x0)} pasajes</b> a una tarifa de <b>P<sub>0</sub> = $${fmtInt(p0)}</b>. ` +
    `Al ejecutar la inversión (I<sub>0</sub> = $800.000.000), la tarifa baja a <b>P<sub>1</sub> = $${fmtInt(p1)}</b> y la demanda sube a <b>X<sub>1</sub> = ${fmtInt(x1)} pasajes</b>. ` +
    `El costo marginal privado de operación es <b>CmgP = $${fmtInt(cp)}/pasaje</b>, mientras que por congestión/emisiones el costo marginal social es <b>CmgS = $${fmtInt(cs)}/pasaje</b>.` +
    `<ol class="enun-list" type="a"><li>Calcule la elasticidad precio de la demanda (E<sub>d</sub>) y la función lineal de demanda implícita.</li>` +
    `<li>Determine el beneficio bruto por aumento en disponibilidad (área bajo D), la externalidad neta (CmgS − CmgP) y el costo social total (CmgS · X<sub>1</sub>).</li></ol>`;

  document.getElementById("tr-sol").innerHTML =
    `<b>Desarrollo en vivo:</b> ` +
    `<b>a)</b> E<sub>d</sub> = [(${fmtInt(x1)} − ${fmtInt(x0)})/${fmtInt(x0)}] / [(${fmtInt(p1)} − ${fmtInt(p0)})/${fmtInt(p0)}] = <b>${fmtDec(ed, 2)}</b> | ` +
    `<b>b)</b> Beneficio Bruto = 0,5·($${fmtInt(p0)}+$${fmtInt(p1)})·${fmtInt(dx)} = <b>$${fmtInt(ben)}</b> | ` +
    `Externalidad = ($${fmtInt(cs)}−$${fmtInt(cp)})·${fmtInt(x1)} = <b>${ext < 0 ? "-$" : "$"}${fmtInt(Math.abs(ext))}</b> | ` +
    `CS<sub>total</sub> = $${fmtInt(cs)}·${fmtInt(x1)} = <b>$${fmtInt(csTotal)}</b>`;

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
  const maxX = Math.max(130000, x1 * 1.15);
  const maxY = Math.max(6200, p0 * 1.24, cs * 1.35);
  const sx = v => M.l + (v / maxX) * (W - M.l - M.r);
  const sy = v => H - M.b - (v / maxY) * (H - M.t - M.b);

  const stepY = Math.max(500, Math.round(maxY / 6 / 500) * 500);
  for (let y = 0; y <= maxY; y += stepY) {
    el("line", { x1: M.l, y1: sy(y), x2: W - M.r, y2: sy(y), stroke: "#E2E8F0", "stroke-width": "1" }, svg);
    const t = el("text", { x: M.l - 8, y: sy(y) + 4, fill: "#475569", "font-size": "11", "text-anchor": "end" }, svg);
    t.textContent = "$" + fmtInt(y);
  }
  for (let x = 0; x <= maxX; x += 20000) {
    el("line", { x1: sx(x), y1: M.t, x2: sx(x), y2: H - M.b, stroke: "#F1F5F9", "stroke-width": "1" }, svg);
    const t = el("text", { x: sx(x), y: H - M.b + 16, fill: "#475569", "font-size": "11", "text-anchor": "middle" }, svg);
    t.textContent = x === 0 ? "0" : (x / 1000) + "k";
  }
  drawAxesPizarra(svg, M.l, M.t, W - M.r, H - M.b, "Tarifa / Costo ($)", "Pasajes (X)");

  if (Math.abs(x1 - ghostTr.x1) >= 250 || Math.abs(x0 - ghostTr.x0) >= 250) {
    const gPts = `${sx(ghostTr.x0)},${sy(0)} ${sx(ghostTr.x1)},${sy(0)} ${sx(ghostTr.x1)},${sy(ghostTr.p1)} ${sx(ghostTr.x0)},${sy(ghostTr.p0)}`;
    el("polygon", { points: gPts, fill: "rgba(148,163,184,0.12)", stroke: "#94A3B8", "stroke-width": "1.6", "stroke-dasharray": "5,4" }, svg);
  }
  if (Math.abs(cs - ghostTr.cs) >= 50) {
    el("line", { x1: M.l, y1: sy(ghostTr.cs), x2: W - M.r, y2: sy(ghostTr.cs), stroke: "#94A3B8", "stroke-width": "1.4", "stroke-dasharray": "4,4" }, svg);
  }

  const dPts = `${sx(x0)},${sy(0)} ${sx(x1)},${sy(0)} ${sx(x1)},${sy(p1)} ${sx(x0)},${sy(p0)}`;
  el("polygon", { points: dPts, fill: "rgba(124,58,237,0.22)", stroke: "#7C3AED", "stroke-width": "1.8" }, svg);

  const yTopExt = Math.max(cp, cs), yBotExt = Math.min(cp, cs);
  el("rect", {
    x: sx(0), y: sy(yTopExt), width: sx(x1) - sx(0), height: Math.max(1, sy(yBotExt) - sy(yTopExt)),
    fill: brecha >= 0 ? "rgba(234,88,12,0.34)" : "rgba(22,163,74,0.28)",
    stroke: brecha >= 0 ? "#EA580C" : "#16A34A", "stroke-width": "1.5"
  }, svg);

  el("line", { x1: M.l, y1: sy(cs), x2: W - M.r, y2: sy(cs), stroke: "#DC2626", "stroke-width": "2", "stroke-dasharray": "6,4" }, svg);
  el("line", { x1: M.l, y1: sy(cp), x2: W - M.r, y2: sy(cp), stroke: "#1D4ED8", "stroke-width": "2", "stroke-dasharray": "3,3" }, svg);
  const tCs = el("text", { x: W - M.r - 4, y: sy(cs) - 5, fill: "#DC2626", "font-size": "11", "font-weight": "700", "text-anchor": "end" }, svg);
  tCs.textContent = `CmgS = $${fmtInt(cs)}`;
  const tCp = el("text", { x: W - M.r - 4, y: sy(cp) + 13, fill: "#1D4ED8", "font-size": "11", "font-weight": "700", "text-anchor": "end" }, svg);
  tCp.textContent = `CmgP = $${fmtInt(cp)}`;

  const xDemIni = Math.max(0, x0 - (maxY - p0) / pend);
  const xDemFin = Math.min(maxX, x1 + p1 / pend);
  const yDemIni = p0 + pend * (x0 - xDemIni);
  const yDemFin = p1 - pend * (xDemFin - x1);
  el("line", { x1: sx(xDemIni), y1: sy(yDemIni), x2: sx(xDemFin), y2: sy(yDemFin), stroke: "#0F172A", "stroke-width": "2.6" }, svg);

  // Proyecciones estilo pizarra P0, P1, X0, X1 + rótulo D
  el("line", { x1: M.l, y1: sy(p0), x2: sx(x0), y2: sy(p0), stroke: "#475569", "stroke-dasharray": "4,3" }, svg);
  el("line", { x1: M.l, y1: sy(p1), x2: sx(x1), y2: sy(p1), stroke: "#7C3AED", "stroke-dasharray": "4,3" }, svg);
  drawPill(svg, sx(xDemFin) - 24, sy(yDemFin) - 16, "D (Demanda)", "#0F172A", "#FFFFFF", "end", "10.5");
  el("circle", { cx: sx(x0), cy: sy(p0), r: 6, fill: "#0F172A", stroke: "#FFFFFF", "stroke-width": "1.6" }, svg);
  drawPill(svg, sx(x0), sy(p0) - 16, `E0 (X0; $${fmtInt(p0)})`, "#0F172A", "#FFFFFF", "middle", "10.2");
  el("circle", { cx: sx(x1), cy: sy(p1), r: 6, fill: "#7C3AED", stroke: "#FFFFFF", "stroke-width": "1.6" }, svg);
  drawPill(svg, sx(x1) + 10, sy(p1) - 12, `E1 (X1; $${fmtInt(p1)})`, "#7C3AED", "#FAF5FF", "start", "10.2");
  const tBenLbl = el("text", { x: (sx(x0) + sx(x1)) / 2, y: sy((p0 + p1) * 0.36), fill: "#5B21B6", "font-size": "11", "font-weight": "800", "text-anchor": "middle" }, svg);
  tBenLbl.textContent = "Beneficio Bruto";

  if (Math.abs(x1 - ghostTr.x1) >= 250) {
    const colArr = x1 > ghostTr.x1 ? "#15803D" : "#DC2626";
    const mk = x1 > ghostTr.x1 ? "arr-green" : "arr-red";
    const lbl = x1 > ghostTr.x1 ? `→ +${fmtInt(x1 - ghostTr.x1)}` : `← -${fmtInt(ghostTr.x1 - x1)}`;
    drawArrow(svg, sx(ghostTr.x1), sy(p1) - 24, sx(x1), sy(p1) - 24, colArr, mk, lbl, (sx(ghostTr.x1) + sx(x1)) / 2, sy(p1) - 32);
  }
  drawArrow(svg, sx(x0) + 4, sy(maxY * 0.06), sx(x1) - 4, sy(maxY * 0.06), "#0F172A", "arr-dark", `ΔX = +${fmtInt(dx)}`, (sx(x0) + sx(x1)) / 2, sy(maxY * 0.11));

  if (Math.abs(brecha) >= 150) {
    const xBre = sx(maxX * 0.18);
    drawArrow(svg, xBre, sy(cp), xBre, sy(cs), brecha > 0 ? "#EA580C" : "#15803D", brecha > 0 ? "arr-orange" : "arr-green",
      `Externalidad $${fmtInt(Math.abs(brecha))}`, xBre + 8, (sy(cp) + sy(cs)) / 2 + 4, "start");
  }

  renderFormulaStrip("tr-fstrip", [
    {
      lbl: "Beneficio Social por Trapecio (B)", col: "#15803D",
      eq: `B = ${mFrac('<span class="sym-b">P<sub>0</sub></span> + <span class="sym-t">P<sub>1</sub></span>', '2')}·(<span class="sym-p">X<sub>1</sub></span> − <span class="sym-o">X<sub>0</sub></span>)`,
      sub: `B = ${mFrac(eChip("$"+fmtInt(p0),p0,"tr_p0","100","vc-b","Precio inicial P0") + " + " + eChip("$"+fmtInt(p1),p1,"tr_p1","100","vc-t","Precio nuevo P1"), "2")}·(${eChip(fmtInt(x1),x1,"tr_x1","500","vc-p","Viajes nuevos X1")} − ${eChip(fmtInt(x0),x0,"tr_x0","500","vc-o","Viajes iniciales X0")}) = ${rChip("$"+fmtDec(ben/1e6,2)+"M")}`,
      note: `ΔX = ${fmtInt(dx)} viajes generados · Clic en P0, P1, X0 o X1 para editar`
    },
    {
      lbl: "Elasticidad Precio de la Demanda (η_d)", col: "#1D4ED8",
      eq: `η<sub>d</sub> = ${mFrac('(X<sub>1</sub> − X<sub>0</sub>) / X<sub>0</sub>', '(P<sub>1</sub> − P<sub>0</sub>) / P<sub>0</sub>')}`,
      sub: `η<sub>d</sub> = ${mFrac(fmtDec(((x1-x0)/x0)*100,1) + "%", fmtDec(((p1-p0)/p0)*100,1) + "%")} = ${rChip(fmtDec(ed,2))}`,
      note: Math.abs(ed) > 1 ? "Demanda elástica (|η_d| > 1): fuerte respuesta de viajes" : "Demanda inelástica (|η_d| ≤ 1)"
    },
    {
      lbl: "Externalidad Negativa Total (Ext)", col: "#DC2626",
      eq: `Ext = (<span class="sym-r">C<sub>soc</sub></span> − <span class="sym-o">C<sub>priv</sub></span>)·<span class="sym-p">X<sub>1</sub></span>`,
      sub: `Ext = (${eChip("$"+fmtInt(cs),cs,"tr_cs","50","vc-r","Costo marginal social")} − ${eChip("$"+fmtInt(cp),cp,"tr_cp","50","vc-o","Costo marginal privado")})·${eChip(fmtInt(x1),x1,"tr_x1","500","vc-p","Viajes X1")} = ${rChip("$"+fmtDec(ext/1e6,2)+"M", ext > 0)}`,
      note: `Brecha unitaria = $${fmtInt(brecha)}/viaje | Costo Social Total = $${fmtDec(csTotal/1e6,1)}M`
    }
  ]);
  renderPedBox("ped-transporte",
    `La rebaja tarifaria de <b>$${fmtInt(p0)}</b> a <b>$${fmtInt(p1)}</b> expande los viajes en <b>+${fmtInt(dx)} pasajes</b> (elasticidad <b>E<sub>d</sub> = ${fmtDec(ed,2)}</b>), generando un beneficio bruto de <b>$${fmtInt(ben)}</b>. Sin embargo, cada viaje genera una brecha de <b>${brecha >= 0 ? "+" : "-"}$${fmtInt(Math.abs(brecha))}</b> entre CmgS y CmgP (externalidad total de <b>${ext < 0 ? "-$" : "$"}${fmtInt(Math.abs(ext))}</b>).`,
    `<b>¿Por qué el privado celebra mientras la ciudad pierde?</b> Un operador privado solo mira su costo directo (CmgP = $${fmtInt(cp)}) y jamás paga la congestión, ruido ni contaminación que impone a terceros. Si CmgS &gt; CmgP, el mercado sobreproduce viajes contaminantes salvo que el Estado internalice la franja naranja (impuesto pigouviano o buses eléctricos).`,
    `En evaluación social SNI (Apuntes págs. 13–14), recuerda siempre comparar el <b>Beneficio Social Bruto</b> (trapecio morado bajo D) contra el <b>Costo Social Total</b> (CmgS · X<sub>1</sub>), no contra el costo privado.`
  );
}

// ============================================================================
// 2. MERCADO DE LA LECHE + PARSER LIBRE DE ECUACIONES LINEALES + AUTOESCALA
// ============================================================================
let stateLc = { A: 300, B: 0.0205, C: -50, D: 0.025, Q: 1470, bien: "la leche en polvo", unidad: "ton/año" };
let ghostLc = { A: 300, B: 0.0205, C: -50, D: 0.025, Q: 1470 };
let animLcId = null;

function parseLinearEq(rawStr) {
  // Parsea expresiones lineales como "Pd = 300 - 0.0205*Q", "-50 + 0,025Q", "0.5*X + 10", etc.
  let s = String(rawStr || "").replace(/,/g, ".").replace(/−/g, "-").replace(/\s+/g, "");
  if (s.includes("=")) s = s.split("=").pop();
  s = s.replace(/\*/g, "");
  // Normalizar variables Qd, Qo, Q, X, x -> Q
  s = s.replace(/(Qd|Qo|qd|qo|q|X|x)/g, "Q");
  // Separar en términos con signo
  const tokens = s.match(/[+-]?[^+-]+/g);
  if (!tokens || tokens.length === 0) return null;
  let intercept = 0, slope = 0, hasQ = false;
  for (const tok of tokens) {
    if (tok.includes("Q")) {
      hasQ = true;
      const coefStr = tok.replace("Q", "");
      if (coefStr === "" || coefStr === "+") slope += 1;
      else if (coefStr === "-") slope -= 1;
      else {
        const v = parseFloat(coefStr);
        if (!Number.isFinite(v)) return null;
        slope += v;
      }
    } else {
      const v = parseFloat(tok);
      if (!Number.isFinite(v)) return null;
      intercept += v;
    }
  }
  if (!hasQ) return null;
  return { intercept, slope };
}

function syncSlidersFromStateLc() {
  const fitSlider = (id, val, minFallback, maxFallback) => {
    const sl = document.getElementById(id);
    if (val < parseFloat(sl.min)) sl.min = Math.floor(val * 0.7);
    if (val > parseFloat(sl.max)) sl.max = Math.ceil(val * 1.4);
    if (Math.abs(val) < 1 && val > 0) {
      sl.min = Math.min(parseFloat(sl.min), val * 0.25);
      sl.max = Math.max(parseFloat(sl.max), val * 3.0);
      sl.step = (val < 0.01) ? 0.0002 : (val < 0.1 ? 0.0005 : 0.01);
    }
    sl.value = val;
  };
  fitSlider("lc-a", stateLc.A, 100, 600);
  fitSlider("lc-b", stateLc.B, 0.005, 0.08);
  fitSlider("lc-c", stateLc.C, -150, 150);
  fitSlider("lc-d", stateLc.D, 0.005, 0.10);
  const slQ = document.getElementById("lc-q");
  if (stateLc.Q > parseFloat(slQ.max)) slQ.max = Math.ceil(stateLc.Q * 1.6);
  slQ.step = stateLc.Q < 200 ? 1 : 10;
  slQ.value = stateLc.Q;
}

function syncEqInputsFromStateLc() {
  document.getElementById("lc-eq-d").value = `Pd = ${stateLc.A} - ${stateLc.B}*Q`;
  const signD = stateLc.D >= 0 ? "+" : "-";
  document.getElementById("lc-eq-o").value = `Po = ${stateLc.C} ${signD} ${Math.abs(stateLc.D)}*Q`;
  document.getElementById("lc-eq-q").value = Math.round(stateLc.Q);
}

function aplicarEcuacionesLeche() {
  const errBox = document.getElementById("lc-eq-err");
  errBox.style.display = "none";
  const parsedD = parseLinearEq(document.getElementById("lc-eq-d").value);
  const parsedO = parseLinearEq(document.getElementById("lc-eq-o").value);
  const qVal = parseFloat(document.getElementById("lc-eq-q").value);

  if (!parsedD || parsedD.slope >= 0) {
    errBox.textContent = "Revisa la Demanda: debe ser lineal con pendiente negativa (ej: Pd = 300 - 0.0205*Q).";
    errBox.style.display = "block";
    return;
  }
  if (!parsedO || parsedO.slope <= 0) {
    errBox.textContent = "Revisa la Oferta: debe ser lineal con pendiente positiva (ej: Po = -50 + 0.025*Q).";
    errBox.style.display = "block";
    return;
  }
  if (!Number.isFinite(qVal) || qVal < 0) {
    errBox.textContent = "Ingresa una producción de proyecto (Q_proy) mayor o igual a 0.";
    errBox.style.display = "block";
    return;
  }

  fijarGhostLeche();
  stateLc.A = parsedD.intercept;
  stateLc.B = Math.abs(parsedD.slope);
  stateLc.C = parsedO.intercept;
  stateLc.D = parsedO.slope;
  stateLc.Q = qVal;
  stateLc.bien = "el bien evaluado (ecuaciones personalizadas)";
  stateLc.unidad = "unid/año";
  syncSlidersFromStateLc();
  drawLeche();
}

function onSliderLeche() {
  stateLc.A = +document.getElementById("lc-a").value;
  stateLc.B = +document.getElementById("lc-b").value;
  stateLc.C = +document.getElementById("lc-c").value;
  stateLc.D = +document.getElementById("lc-d").value;
  stateLc.Q = +document.getElementById("lc-q").value;
  syncEqInputsFromStateLc();
  drawLeche();
}

function fijarGhostLeche() {
  ghostLc = { A: stateLc.A, B: stateLc.B, C: stateLc.C, D: stateLc.D, Q: stateLc.Q };
  drawLeche();
}

function presetLecheCaso(tipo) {
  if (animLcId) cancelAnimationFrame(animLcId);
  fijarGhostLeche();
  if (tipo === "apuntes") {
    stateLc = { A: 300, B: 0.0205, C: -50, D: 0.025, Q: 1470, bien: "la leche en polvo", unidad: "ton/año" };
  } else if (tipo === "positivo") {
    stateLc = { A: 300, B: 0.0205, C: 50, D: 0.025, Q: 1470, bien: "la leche en polvo", unidad: "ton/año" };
  } else {
    stateLc = { A: 500, B: 0.02, C: -100, D: 0.08, Q: 1000, bien: "el mercado de prueba", unidad: "unid/año" };
  }
  document.getElementById("lc-a").min = 100; document.getElementById("lc-a").max = 600;
  document.getElementById("lc-b").min = 0.005; document.getElementById("lc-b").max = 0.08; document.getElementById("lc-b").step = 0.0005;
  document.getElementById("lc-c").min = -150; document.getElementById("lc-c").max = 150;
  document.getElementById("lc-d").min = 0.005; document.getElementById("lc-d").max = 0.10; document.getElementById("lc-d").step = 0.0005;
  document.getElementById("lc-q").max = 3200; document.getElementById("lc-q").step = 10;
  syncSlidersFromStateLc();
  syncEqInputsFromStateLc();
  document.getElementById("lc-eq-err").style.display = "none";
  drawLeche();
}

function animarLeche() {
  if (animLcId) cancelAnimationFrame(animLcId);
  const targetQ = Math.max(10, stateLc.Q || 1470);
  ghostLc = { A: stateLc.A, B: stateLc.B, C: stateLc.C, D: stateLc.D, Q: 0 };
  const t0 = performance.now(), dur = 1800;
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    const ease = 1 - Math.pow(1 - u, 3);
    stateLc.Q = Math.round(targetQ * ease);
    document.getElementById("lc-q").value = stateLc.Q;
    document.getElementById("lc-eq-q").value = stateLc.Q;
    drawLeche();
    if (u < 1) animLcId = requestAnimationFrame(step);
  }
  animLcId = requestAnimationFrame(step);
}

function drawLeche() {
  const { A, B, C, D, Q: Qp } = stateLc;

  document.getElementById("lc-a-v").textContent = fmtDec(A, 1);
  document.getElementById("lc-b-v").textContent = fmtDec(B, 4);
  document.getElementById("lc-c-v").textContent = fmtDec(C, 1);
  document.getElementById("lc-d-v").textContent = fmtDec(D, 4);
  document.getElementById("lc-q-v").textContent = fmtInt(Qp);

  const q0 = (A - C) / (B + D);
  const p0 = A - B * q0;
  const q1 = (A - C + D * Qp) / (B + D);
  const p1 = A - B * q1;
  const qo1 = q1 - Qp;

  const rectAD = p1 * (q1 - q0), triAD = 0.5 * (p0 - p1) * (q1 - q0), ad = rectAD + triAD;
  const rectLR = p1 * (q0 - qo1), triLR = 0.5 * (p0 - p1) * (q0 - qo1), lr = rectLR + triLR;
  const vsp = ad + lr;
  const pSoc = Qp > 0 ? vsp / Qp : p0;
  const vpp = p1 * Qp;

  // Enunciado redactado sincronizado con las ecuaciones actuales
  const signC = C >= 0 ? "" : "−";
  document.getElementById("lc-enunciado").innerHTML =
    `En el mercado nacional de <b>${stateLc.bien}</b>, la demanda y la oferta sin comercio exterior están dadas por: ` +
    `<b>P<sub>d</sub> = ${fmtDec(A, 1)} − ${fmtDec(B, 4)}·Q<sub>d</sub></b> &nbsp;y&nbsp; <b>P<sub>o</sub> = ${signC}${fmtDec(Math.abs(C), 1)} + ${fmtDec(D, 4)}·Q<sub>o</sub></b>, ` +
    `donde P ($) es el precio y Q (${stateLc.unidad}) la cantidad transada. Una nueva planta/cooperativa proyecta producir <b>Q<sub>proy</sub> = ${fmtInt(Qp)} ${stateLc.unidad}</b>.` +
    `<ol class="enun-list" type="a"><li>Calcule el equilibrio inicial sin proyecto (Q<sub>0</sub>, P<sub>0</sub>).</li>` +
    `<li>Determine el nuevo equilibrio nacional (Q<sub>1</sub>, P<sub>1</sub>), la oferta de antiguos productores (Q<sub>o1</sub>) y los ingresos privados de la firma (VPP).</li>` +
    `<li>Estime el Valor Social de la Producción bajo enfoque de eficiencia (VSP = AD + LR), <b>d)</b> distribución por agente y <b>e)</b> Precio Social unitario P*.</li></ol>`;

  document.getElementById("lc-sol").innerHTML =
    `<b>a)</b> ${fmtDec(A,1)}−${fmtDec(B,4)}Q = ${fmtDec(C,1)}+${fmtDec(D,4)}Q ⇒ <b>Q<sub>0</sub>=${fmtDec(q0,1)}</b>; <b>P<sub>0</sub>=$${fmtDec(p0,2)}</b> | ` +
    `<b>b)</b> Q'=Q+${fmtInt(Qp)} ⇒ <b>Q<sub>1</sub>=${fmtDec(q1,1)}</b>; <b>Q<sub>o1</sub>=${fmtDec(qo1,1)}</b>; <b>P<sub>1</sub>=$${fmtDec(p1,2)}</b>; VPP=<b>$${fmtInt(vpp)}</b><br/>` +
    `<b>c)</b> AD = $${fmtInt(rectAD)} + $${fmtInt(triAD)} = <b>$${fmtInt(ad)}</b> | LR = $${fmtInt(rectLR)} + $${fmtInt(triLR)} = <b>$${fmtInt(lr)}</b> ⇒ <b>VSP = $${fmtInt(vsp)}</b> | ` +
    `<b>d-e)</b> Triángulos: ΔCons=$${fmtInt(triAD)}, ΔProd=$${fmtInt(triLR)} | <b>P* = $${fmtDec(pSoc, 2)}</b>`;

  document.getElementById("lc-k-e0").textContent = `${fmtInt(q0)} | $${fmtDec(p0, 1)}`;
  document.getElementById("lc-k-e1").textContent = `${fmtInt(q1)} | $${fmtDec(p1, 1)}`;
  document.getElementById("lc-k-dp").textContent = `Caída ΔP = -$${fmtDec(Math.abs(p0 - p1), 2)}`;
  document.getElementById("lc-k-ad").textContent = "$" + fmtInt(ad);
  document.getElementById("lc-k-adp").textContent = `${vsp > 0 ? fmtDec(ad / vsp * 100, 1) : "0,0"}% del VSP`;
  document.getElementById("lc-k-lr").textContent = "$" + fmtInt(lr);
  document.getElementById("lc-k-lrp").textContent = `${vsp > 0 ? fmtDec(lr / vsp * 100, 1) : "0,0"}% del VSP`;
  document.getElementById("lc-k-vsp").textContent = "$" + fmtInt(vsp);
  document.getElementById("lc-k-ps").textContent = `P* = $${fmtDec(pSoc, 2)} / unid`;

  const svg = document.getElementById("svg-leche");
  svg.innerHTML = "";
  addDefs(svg);

  // AUTOESCALA INTELIGENTE PARA CUALQUIER ECUACIÓN QUE ESCRIBA EL USUARIO
  const M = { l: 78, r: 90, t: 30, b: 56 };
  const W = 960, H = 410;
  const spanQ = Math.max(Math.abs(q1 - qo1) * 1.55, Math.abs(q0) * 0.35, 20);
  const minX = Math.max(0, Math.min(qo1, q0) - spanQ);
  const maxX = Math.max(q1, q0) + spanQ;
  const maxY = Math.max(p0 * 1.72, A * 0.92, 50);

  const sx = v => M.l + ((v - minX) / Math.max(1e-6, maxX - minX)) * (W - M.l - M.r);
  const sy = v => H - M.b - (v / maxY) * (H - M.t - M.b);

  // Grilla sutil de fondo
  for (let i = 1; i <= 4; i++) {
    const yv = (maxY / 4) * i;
    el("line", { x1: M.l, y1: sy(yv), x2: W - M.r, y2: sy(yv), stroke: "#F1F5F9", "stroke-width": "1" }, svg);
  }
  drawAxesPizarra(svg, M.l, M.t, W - M.r, H - M.b, "Precio ($)", "Cantidad (Q)");
  if (minX > 0) drawAxisBreakX(svg, M.l + 18, H - M.b);

  // Rastro fantasma si cambió algo
  const gq1 = (ghostLc.A - ghostLc.C + ghostLc.D * ghostLc.Q) / (ghostLc.B + ghostLc.D);
  const gp1 = ghostLc.A - ghostLc.B * gq1;
  if (Math.abs(Qp - ghostLc.Q) > 0.01 * Math.max(1, Qp) || Math.abs(C - ghostLc.C) > 1 || Math.abs(A - ghostLc.A) > 1) {
    el("line", { x1: sx(minX), y1: sy(ghostLc.C + ghostLc.D * (minX - ghostLc.Q)), x2: sx(maxX), y2: sy(ghostLc.C + ghostLc.D * (maxX - ghostLc.Q)), stroke: "#94A3B8", "stroke-width": "1.5", "stroke-dasharray": "4,4" }, svg);
    if (gq1 >= minX && gq1 <= maxX && gp1 >= 0 && gp1 <= maxY) {
      el("circle", { cx: sx(gq1), cy: sy(gp1), r: 4, fill: "#94A3B8" }, svg);
    }
  }

  // Polígonos LR y AD (rectángulo + triángulo)
  if (Qp > 0 && p0 > 0 && p1 >= 0) {
    const lrPts = `${sx(qo1)},${sy(0)} ${sx(q0)},${sy(0)} ${sx(q0)},${sy(p0)} ${sx(qo1)},${sy(p1)}`;
    el("polygon", { points: lrPts, fill: "rgba(37,99,235,0.22)", stroke: "#1D4ED8", "stroke-width": "1.6" }, svg);
    const adPts = `${sx(q0)},${sy(0)} ${sx(q1)},${sy(0)} ${sx(q1)},${sy(p1)} ${sx(q0)},${sy(p0)}`;
    el("polygon", { points: adPts, fill: "rgba(220,38,38,0.22)", stroke: "#DC2626", "stroke-width": "1.6" }, svg);
    // Realce sutil de los dos triángulos superiores (ΔEP y ΔEC)
    el("polygon", { points: `${sx(qo1)},${sy(p1)} ${sx(q0)},${sy(p1)} ${sx(q0)},${sy(p0)}`, fill: "rgba(37,99,235,0.24)" }, svg);
    el("polygon", { points: `${sx(q0)},${sy(p1)} ${sx(q1)},${sy(p1)} ${sx(q0)},${sy(p0)}`, fill: "rgba(220,38,38,0.24)" }, svg);
  }

  // Curvas D, O y O' recortadas al recuadro [minX, maxX] x [0, maxY]
  const drawClipped = (fnY, color, width, dash="") => {
    const pts = [];
    for (let k = 0; k <= 60; k++) {
      const xv = minX + (maxX - minX) * (k / 60);
      const yv = fnY(xv);
      if (yv >= 0 && yv <= maxY) pts.push({ x: xv, y: yv });
    }
    if (pts.length < 2) return null;
    const attrs = { x1: sx(pts[0].x), y1: sy(pts[0].y), x2: sx(pts[pts.length - 1].x), y2: sy(pts[pts.length - 1].y), stroke: color, "stroke-width": width };
    if (dash) attrs["stroke-dasharray"] = dash;
    el("line", attrs, svg);
    return pts[pts.length - 1];
  };
  const endD = drawClipped(x => A - B * x, "#0F172A", "2.8");
  const endO = drawClipped(x => C + D * x, "#1D4ED8", "2.5");
  const endOp = Qp > 0 ? drawClipped(x => C + D * (x - Qp), "#15803D", "2.8", "7,4") : null;

  // Rótulos de curva estilo pizarra (D, O, O')
  if (endD) drawPill(svg, sx(endD.x) + 16, sy(endD.y), "D", "#0F172A", "#FFFFFF", "start");
  if (endO) drawPill(svg, Math.min(W - M.r + 12, sx(endO.x) + 8), Math.max(M.t + 12, sy(endO.y)), "O", "#1D4ED8", "#EFF6FF", "start");
  if (endOp) drawPill(svg, Math.min(W - M.r + 12, sx(endOp.x) + 8), Math.min(H - M.b - 18, sy(endOp.y) + 6), "O' = O+Q", "#15803D", "#F0FDF4", "start");

  // Proyecciones estilo pizarra hacia ejes (P0, P1 en Y; Qo1, Q0, Q1 en X)
  el("line", { x1: M.l, y1: sy(p0), x2: sx(q0), y2: sy(p0), stroke: "#475569", "stroke-width": "1.3", "stroke-dasharray": "4,3" }, svg);
  const tP0 = el("text", { x: M.l - 7, y: sy(p0) - 2, fill: "#0F172A", "font-size": "10.8", "font-weight": "800", "text-anchor": "end" }, svg);
  tP0.textContent = `P0 $${fmtDec(p0, 1)}`;

  const tQ0 = el("text", { x: sx(q0), y: H - M.b + 17, fill: "#0F172A", "font-size": "10.8", "font-weight": "800", "text-anchor": "middle" }, svg);
  tQ0.textContent = `Q0 (${fmtInt(q0)})`;

  el("circle", { cx: sx(q0), cy: sy(p0), r: 6, fill: "#0F172A", stroke: "#FFFFFF", "stroke-width": "1.8" }, svg);
  drawPill(svg, sx(q0), sy(p0) - 18, `E0`, "#0F172A", "#FFFFFF", "middle", "11");

  if (Qp > 0) {
    el("line", { x1: M.l, y1: sy(p1), x2: sx(q1), y2: sy(p1), stroke: "#15803D", "stroke-width": "1.3", "stroke-dasharray": "4,3" }, svg);
    const yP1Lbl = Math.abs(sy(p1) - sy(p0)) < 16 ? sy(p0) + 15 : sy(p1) + 5;
    const tP1 = el("text", { x: M.l - 7, y: yP1Lbl, fill: "#15803D", "font-size": "10.8", "font-weight": "800", "text-anchor": "end" }, svg);
    tP1.textContent = `P1 $${fmtDec(p1, 1)}`;

    const tQo1 = el("text", { x: sx(qo1) - 4, y: H - M.b + 31, fill: "#1D4ED8", "font-size": "10.3", "font-weight": "800", "text-anchor": "end" }, svg);
    tQo1.textContent = `Qo1 (${fmtInt(qo1)})`;
    const tQ1 = el("text", { x: sx(q1) + 4, y: H - M.b + 31, fill: "#DC2626", "font-size": "10.3", "font-weight": "800", "text-anchor": "start" }, svg);
    tQ1.textContent = `Q1 (${fmtInt(q1)})`;
    el("line", { x1: sx(qo1), y1: H - M.b, x2: sx(qo1), y2: H - M.b + 16, stroke: "#1D4ED8", "stroke-width": "1.2" }, svg);
    el("line", { x1: sx(q1), y1: H - M.b, x2: sx(q1), y2: H - M.b + 16, stroke: "#DC2626", "stroke-width": "1.2" }, svg);

    el("circle", { cx: sx(q1), cy: sy(p1), r: 6, fill: "#15803D", stroke: "#FFFFFF", "stroke-width": "1.8" }, svg);
    drawPill(svg, sx(q1) + 22, sy(p1) - 14, `E1`, "#15803D", "#F0FDF4", "start", "11");

    // Flecha verde SIEMPRE visible O -> O' en zona alta limpia
    const yArrO = Math.min(maxY * 0.80, p0 + (maxY - p0) * 0.42);
    const xO0 = (yArrO - C) / D;
    const xO1 = xO0 + Qp;
    if (xO0 > minX && xO1 < maxX) {
      drawArrow(svg, sx(xO0) + 4, sy(yArrO), sx(xO1) - 4, sy(yArrO), "#15803D", "arr-green", `O → O' (+${fmtInt(Qp)})`, (sx(xO0) + sx(xO1)) / 2, sy(yArrO) - 11);
    }
    drawArrow(svg, M.l + 24, sy(p0), M.l + 24, sy(p1), "#DC2626", "arr-red", `↓ -$${fmtDec(p0 - p1, 1)}`, M.l + 32, (sy(p0) + sy(p1)) / 2 + 4, "start");
    drawArrow(svg, sx(q0) - 2, sy(maxY * 0.10), sx(qo1) + 2, sy(maxY * 0.10), "#1D4ED8", "arr-blue", `← LR`, (sx(q0) + sx(qo1)) / 2, sy(maxY * 0.18));
    drawArrow(svg, sx(q0) + 2, sy(maxY * 0.10), sx(q1) - 2, sy(maxY * 0.10), "#DC2626", "arr-red", `AD →`, (sx(q0) + sx(q1)) / 2, sy(maxY * 0.18));
  }

  const cSign = C >= 0 ? "− " : "+ ";
  renderFormulaStrip("lc-fstrip", [
    {
      lbl: "Equilibrio Inicial sin Proyecto (Q0, P0)", col: "#1D4ED8",
      eq: `Q<sub>0</sub> = ${mFrac('<span class="sym-b">A</span> − <span class="sym-p">C</span>', '<span class="sym-t">B</span> + <span class="sym-o">D</span>')}`,
      sub: `Q<sub>0</sub> = ${mFrac(eChip(fmtDec(A,1),A,"lc_A","5","vc-b","Intercepto Demanda A") + " " + cSign + eChip(fmtDec(Math.abs(C),1),C,"lc_C","5","vc-p","Intercepto Oferta C (con signo)"), eChip(fmtDec(B,4),B,"lc_B","0.0005","vc-t","Pendiente Demanda B") + " + " + eChip(fmtDec(D,4),D,"lc_D","0.0005","vc-o","Pendiente Oferta D"))} = ${rChip(fmtInt(q0))}`,
      note: `Precio inicial P<sub>0</sub> = <b>$${fmtDec(p0,2)}</b> · Clic en A, B, C o D para editar directo`
    },
    {
      lbl: "Equilibrio con Proyecto (Q1, P1)", col: "#0F766E",
      eq: `Q<sub>1</sub> = ${mFrac('A − C + D·<span class="sym-r">Q<sub>proy</sub></span>', 'B + D')}`,
      sub: `Q<sub>1</sub> = ${mFrac(fmtDec(A-C,1) + " + " + fmtDec(D,4) + "·" + eChip(fmtInt(Qp),Qp,"lc_Q","10","vc-r","Producción del proyecto Q_proy"), fmtDec(B+D,4))} = ${rChip(fmtInt(q1))}`,
      note: `Nuevo precio P<sub>1</sub> = <b>$${fmtDec(p1,2)}</b> | Oferta antigua Q<sub>o1</sub> = <b>${fmtInt(qo1)}</b>`
    },
    {
      lbl: "Valor Social de la Producción (VSP = AD + LR)", col: "#15803D",
      eq: `VSP = <span class="sym-b">AD</span> + <span class="sym-t">LR</span> = ${mFrac('P<sub>0</sub> + P<sub>1</sub>', '2')}·<span class="sym-r">Q<sub>proy</sub></span>`,
      sub: `VSP = ${vChip("$"+fmtInt(ad),"vc-b","Aumento Disponibilidad AD")} + ${vChip("$"+fmtInt(lr),"vc-t","Liberación Recursos LR")} = ${rChip("$"+fmtInt(vsp))}`,
      note: `Precio social P<sub>soc</sub> = <b>$${fmtDec(pSoc,2)}</b> vs. VPP privado = $${fmtInt(vpp)}`
    }
  ]);
  renderPedBox("ped-leche",
    `Al entrar el proyecto (<b>+${fmtInt(Qp)}</b>), el precio baja de <b>$${fmtDec(p0,1)}</b> a <b>$${fmtDec(p1,1)}</b>. Del Valor Social de la Producción (<b>$${fmtInt(vsp)}</b>), un <b>${vsp > 0 ? fmtDec(ad/vsp*100,1) : "0"}%</b> proviene de mayor consumo neto (<b>AD</b>) y un <b>${vsp > 0 ? fmtDec(lr/vsp*100,1) : "0"}%</b> de recursos liberados por antiguos productores que reducen su oferta (<b>LR</b>).`,
    `<b>¿Por qué el Estado valora la producción MÁS alto que la empresa privada?</b> La firma solo recauda el nuevo precio más bajo (VPP = P<sub>1</sub>·Q<sub>proy</sub> = <b>$${fmtInt(vpp)}</b>). Pero la sociedad además gana los triángulos de excedente del consumidor y ahorro de costos de productores desplazados, por eso el Precio Social <b>P* = $${fmtDec(pSoc,2)}</b> es siempre superior a P<sub>1</sub>.`,
    `Comprobación de examen (Fontaine): el <b>Enfoque de Eficiencia</b> (AD + LR) y el <b>Enfoque por Agentes</b> (VPP + ΔEC + ΔEP) siempre dan exactamente el mismo peso; además, la demanda se grafica <b>con IVA</b> y la oferta <b>sin IVA</b>.`
  );
}

// ============================================================================
// 3. SIMULADOR ELASTICIDADES EXTREMAS (ENUNCIADO VIVO + 60 FPS)
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

  let diagElast = "Caso Intermedio: el beneficio social se reparte entre mayor consumo (AD) y ahorro de costos de antiguos productores (LR).";
  if (rd <= 2) diagElast = "<b>Caso Extremo 1 (Demanda Perfectamente Elástica η<sub>d</sub> = ∞):</b> El precio P<sub>0</sub> no cae; toda la producción nueva es mayor consumo → <b>VSP = 100% AD</b>.";
  else if (ro <= 2) diagElast = "<b>Caso Extremo 2 (Oferta Perfectamente Elástica η<sub>o</sub> = ∞):</b> El precio P<sub>0</sub> y el consumo total X<sub>0</sub> no cambian; el proyecto solo sustituye oferta antigua → <b>VSP = 100% LR</b>.";
  else if (rd >= 98) diagElast = "<b>Caso Extremo 3 (Demanda Perfectamente Inelástica η<sub>d</sub> = 0):</b> El consumo X<sub>0</sub> es fijo aunque baje el precio → <b>VSP = 100% LR</b>.";
  else if (ro >= 98) diagElast = "<b>Caso Extremo 4 (Oferta Perfectamente Inelástica η<sub>o</sub> = 0):</b> Los antiguos productores no reducen su cantidad ofrecida → <b>VSP = 100% AD</b>.";

  document.getElementById("el-enunciado").innerHTML =
    `Un mercado parte en equilibrio inicial <b>(Q<sub>0</sub> = 1.000; P<sub>0</sub> = $100)</b> e ingresa un proyecto que aporta <b>ΔQ = ${dq} unidades</b>. ` +
    `Determine la proporción del Valor Social de la Producción explicada por <b>Aumento en Disponibilidad (AD)</b> vs. <b>Liberación de Recursos (LR)</b> según la inclinación de las curvas.<br/>` +
    `<span style="color:#1E3A8A;">${diagElast}</span>`;

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

  drawAxesPizarra(svg, M.l, M.t, W - M.r, H - M.b, "Precio (P)", "Cantidad (Q)");
  drawAxisBreakX(svg, M.l + 18, H - M.b);

  if (q0 - qo1 > 2) {
    el("polygon", { points: `${sx(qo1)},${sy(0)} ${sx(q0)},${sy(0)} ${sx(q0)},${sy(p0)} ${sx(qo1)},${sy(p1)}`, fill: "rgba(37,99,235,0.30)", stroke: "#1D4ED8", "stroke-width": "1.5" }, svg);
  }
  if (q1 - q0 > 2) {
    el("polygon", { points: `${sx(q0)},${sy(0)} ${sx(q1)},${sy(0)} ${sx(q1)},${sy(p1)} ${sx(q0)},${sy(p0)}`, fill: "rgba(220,38,38,0.30)", stroke: "#DC2626", "stroke-width": "1.5" }, svg);
  }

  if (rd >= 99) {
    el("line", { x1: sx(q0), y1: sy(0), x2: sx(q0), y2: sy(190), stroke: "#0F172A", "stroke-width": "3" }, svg);
  } else {
    el("line", { x1: sx(minX), y1: sy(p0 - bd * (minX - q0)), x2: sx(maxX), y2: sy(p0 - bd * (maxX - q0)), stroke: "#0F172A", "stroke-width": "2.8" }, svg);
  }
  if (ro >= 99) {
    el("line", { x1: sx(q0), y1: sy(0), x2: sx(q0), y2: sy(190), stroke: "#1D4ED8", "stroke-width": "2.6" }, svg);
    el("line", { x1: sx(q0 + dq), y1: sy(0), x2: sx(q0 + dq), y2: sy(190), stroke: "#15803D", "stroke-width": "2.6", "stroke-dasharray": "6,4" }, svg);
  } else {
    el("line", { x1: sx(minX), y1: sy(p0 + d_o * (minX - q0)), x2: sx(maxX), y2: sy(p0 + d_o * (maxX - q0)), stroke: "#1D4ED8", "stroke-width": "2.6" }, svg);
    el("line", { x1: sx(minX), y1: sy(p0 + d_o * (minX - q0 - dq)), x2: sx(maxX), y2: sy(p0 + d_o * (maxX - q0 - dq)), stroke: "#15803D", "stroke-width": "2.6", "stroke-dasharray": "6,4" }, svg);
  }

  // Proyecciones y rótulos de pizarra E0, E1, P0, P1, D, O, O'
  el("line", { x1: M.l, y1: sy(p0), x2: sx(q0), y2: sy(p0), stroke: "#64748B", "stroke-dasharray": "4,3" }, svg);
  const tEP0 = el("text", { x: M.l - 7, y: sy(p0) + 4, fill: "#0F172A", "font-size": "10.8", "font-weight": "800", "text-anchor": "end" }, svg);
  tEP0.textContent = "P0";
  if (p0 - p1 > 3) {
    el("line", { x1: M.l, y1: sy(p1), x2: sx(q1), y2: sy(p1), stroke: "#15803D", "stroke-dasharray": "4,3" }, svg);
    const tEP1 = el("text", { x: M.l - 7, y: Math.max(sy(p0) + 15, sy(p1) + 4), fill: "#15803D", "font-size": "10.8", "font-weight": "800", "text-anchor": "end" }, svg);
    tEP1.textContent = "P1";
  }
  const tEQ0 = el("text", { x: sx(q0), y: H - M.b + 16, fill: "#0F172A", "font-size": "10.8", "font-weight": "800", "text-anchor": "middle" }, svg);
  tEQ0.textContent = "Q0";
  if (q0 - qo1 > 15) {
    const tEQo = el("text", { x: sx(qo1), y: H - M.b + 16, fill: "#1D4ED8", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, svg);
    tEQo.textContent = "Qo1";
  }
  if (q1 - q0 > 15) {
    const tEQ1 = el("text", { x: sx(q1), y: H - M.b + 16, fill: "#DC2626", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, svg);
    tEQ1.textContent = "Q1";
  }
  el("circle", { cx: sx(q0), cy: sy(p0), r: 5.5, fill: "#0F172A", stroke: "#FFF", "stroke-width": "1.5" }, svg);
  el("circle", { cx: sx(q1), cy: sy(p1), r: 5.5, fill: "#15803D", stroke: "#FFF", "stroke-width": "1.5" }, svg);
  drawPill(svg, sx(q0) - 20, sy(p0) - 16, "E0", "#0F172A", "#FFFFFF", "middle", "10.5");
  if (Math.hypot(sx(q1) - sx(q0), sy(p1) - sy(p0)) > 14) drawPill(svg, sx(q1) + 20, sy(p1) - 12, "E1", "#15803D", "#F0FDF4", "middle", "10.5");
  drawPill(svg, W - M.r - 22, rd >= 99 ? M.t + 16 : Math.min(H - M.b - 16, Math.max(M.t + 16, sy(p0 - bd * (maxX - q0)))), "D", "#0F172A", "#FFFFFF", "middle", "10.8");
  drawPill(svg, ro >= 99 ? sx(q0) : W - M.r - 22, ro >= 99 ? M.t + 16 : Math.min(H - M.b - 28, Math.max(M.t + 16, sy(p0 + d_o * (maxX - q0)))), "O", "#1D4ED8", "#EFF6FF", "middle", "10.8");
  drawPill(svg, ro >= 99 ? sx(q0 + dq) : W - M.r - 22, ro >= 99 ? M.t + 16 : Math.min(H - M.b - 12, Math.max(M.t + 34, sy(p0 + d_o * (maxX - q0 - dq)))), "O'", "#15803D", "#F0FDF4", "middle", "10.8");
  if (q0 - qo1 > 12) drawArrow(svg, sx(q0) - 2, sy(18), sx(qo1) + 2, sy(18), "#1D4ED8", "arr-blue", `← LR`, (sx(q0) + sx(qo1)) / 2, sy(35));
  if (q1 - q0 > 12) drawArrow(svg, sx(q0) + 2, sy(18), sx(q1) - 2, sy(18), "#DC2626", "arr-red", `AD →`, (sx(q0) + sx(q1)) / 2, sy(35));
  if (p0 - p1 > 3) drawArrow(svg, M.l + 22, sy(p0), M.l + 22, sy(p1), "#0F172A", "arr-dark", `↓ -$${fmtDec(p0 - p1, 0)}`, M.l + 30, (sy(p0) + sy(p1)) / 2 + 4, "start");

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

  const dAD = q1 - q0, dLR = q0 - qo1;
  renderFormulaStrip("el-fstrip", [
    {
      lbl: "Peso Aumento en Disponibilidad (%AD)", col: "#1D4ED8",
      eq: `%AD = ${mFrac('d<sub>o</sub>', 'b<sub>d</sub> + d<sub>o</sub>')} × 100%`,
      sub: `%AD = ${mFrac(fmtDec(d_o,3), fmtDec(bd,3) + " + " + fmtDec(d_o,3))} = ${rChip(fmtDec(fracAD*100,1)+"%")}`,
      note: `Rigidez Demanda: ${eChip(rd+"/100",rd,"el_rd","1","vc-b","Rigidez Demanda (0=horiz, 100=vert)")} · Rigidez Oferta: ${eChip(ro+"/100",ro,"el_ro","1","vc-o","Rigidez Oferta (0=horiz, 100=vert)")}`
    },
    {
      lbl: "Peso Liberación de Recursos (%LR)", col: "#059669",
      eq: `%LR = ${mFrac('b<sub>d</sub>', 'b<sub>d</sub> + d<sub>o</sub>')} × 100%`,
      sub: `%LR = ${mFrac(fmtDec(bd,3), fmtDec(bd,3) + " + " + fmtDec(d_o,3))} = ${rChip(fmtDec(fracLR*100,1)+"%")}`,
      note: `Mayor consumo = +${fmtInt(dAD)} u | Sustitución oferta = ${fmtInt(dLR)} u`
    },
    {
      lbl: "Descomposición Física del Aporte (ΔQ)", col: "#7C3AED",
      eq: `<span class="sym-p">ΔQ</span> = ΔQ<sub>AD</sub> + ΔQ<sub>LR</sub>`,
      sub: `${eChip(fmtInt(dq)+" u",dq,"el_dq","10","vc-p","Aporte del proyecto ΔQ")} = ${vChip(fmtInt(dAD)+" u","vc-b","Nuevo consumo AD")} + ${vChip(fmtInt(dLR)+" u","vc-t","Oferta liberada LR")} ⇒ P<sub>1</sub> = ${rChip("$"+fmtDec(p1,1))}`,
      note: `Parte en P<sub>0</sub> = $100, Q<sub>0</sub> = 1.000 u`
    }
  ]);
  renderPedBox("ped-elast",
    `Con rigidez de demanda <b>${rd}</b> y de oferta <b>${ro}</b>, el proyecto reparte su impacto en <b>${fmtDec(fracAD*100,1)}% AD</b> (mayor consumo hacia la derecha) y <b>${fmtDec(fracLR*100,1)}% LR</b> (sustitución de oferta antigua hacia la izquierda), bajando el precio en <b>-$${fmtDec(p0-p1,1)}</b>.`,
    `<b>Curiosidad geométrica de examen:</b> dos situaciones opuestas producen el mismo efecto 100% AD (demanda horizontal o oferta vertical), y las otras dos producen 100% LR (oferta horizontal o demanda vertical). La clave no es memorizar de memoria, sino preguntar: <i>¿quién es capaz de reaccionar al precio?</i> El lado más rígido se queda quieto y el otro absorbe todo el ajuste.`,
    `En bienes transables pequeños abiertos al mundo (demanda externa perfectamente elástica η<sub>d</sub> = ∞), el proyecto no tumba el precio internacional y todo el beneficio es <b>AD = P<sub>0</sub>·ΔQ</b>.`
  );
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


// ============================================================================
// 5. PUENTE PRIVADO -> SOCIAL (WATERFALL SNI 2026 A 60 FPS)
// ============================================================================
let ghostWf = null;
let animWfId = null;

function calcWaterfall(capMM, vol, marUnit, waccPct, moMM, ch4) {
  const N = 10, wacc = waccPct / 100, tsd = 0.055;
  const crec = 0.04, impRenta = 0.25;
  const fcPriv = [-capMM];
  const fcTsdOnly = [-capMM];
  const fcSinImp = [-capMM * 0.90]; // quita IVA/arancel en parte importada
  const fcConMo = [-capMM * 0.90];
  const fcSocFull = [-capMM * 0.90];

  const co2EqTon = (vol * 0.25) + ch4 * 28.0; // CO2 directo + Metano*28
  const benCarbMM = (co2EqTon * 71801 + vol * 32000) / 1e6; // Carbono + ahorro GIRS
  const ahorroMoMM = moMM * (1 - 0.94); // Promedio ponderado MOC/MOSC/MONC SNI 2026 (~6% menor costo social)

  for (let t = 1; t <= N; t++) {
    const g = Math.pow(1 + crec, t - 1);
    const ebitda = ((vol * g * marUnit) / 1e6) - moMM;
    const dep = capMM / N;
    const uai = ebitda - dep;
    const imp = uai > 0 ? uai * impRenta : 0;
    const fPriv = uai - imp + dep;
    const fNoImp = ebitda;
    const fMo = ebitda + ahorroMoMM;
    const fFull = fMo + benCarbMM;

    fcPriv.push(fPriv);
    fcTsdOnly.push(fPriv);
    fcSinImp.push(fNoImp);
    fcConMo.push(fMo);
    fcSocFull.push(fFull);
  }
  const npv = (arr, r) => arr.reduce((acc, v, t) => acc + v / Math.pow(1 + r, t), 0);
  const vanPriv = npv(fcPriv, wacc);
  const vanTsd = npv(fcTsdOnly, tsd);
  const vanSinImp = npv(fcSinImp, tsd);
  const vanConMo = npv(fcConMo, tsd);
  const vanSoc = npv(fcSocFull, tsd);

  return {
    vanPriv,
    dTsd: vanTsd - vanPriv,
    dImp: vanSinImp - vanTsd,
    dMo: vanConMo - vanSinImp,
    dCarb: vanSoc - vanConMo,
    vanSoc,
    benCarbMM,
    co2EqTon,
  };
}

function fijarGhostWaterfall() {
  ghostWf = calcWaterfall(
    +document.getElementById("wf-cap").value,
    +document.getElementById("wf-vol").value,
    +document.getElementById("wf-mar").value,
    +document.getElementById("wf-wacc").value,
    +document.getElementById("wf-mo").value,
    +document.getElementById("wf-ch4").value
  );
  drawWaterfall();
}
function presetWaterfall(tipo) {
  if (animWfId) cancelAnimationFrame(animWfId);
  fijarGhostWaterfall();
  if (tipo === "planta") {
    document.getElementById("wf-cap").value = 68;
    document.getElementById("wf-vol").value = 480;
    document.getElementById("wf-mar").value = 165000;
    document.getElementById("wf-wacc").value = 11.5;
    document.getElementById("wf-mo").value = 52.8;
    document.getElementById("wf-ch4").value = 8.5;
  } else {
    document.getElementById("wf-cap").value = 16;
    document.getElementById("wf-vol").value = 15;
    document.getElementById("wf-mar").value = 350000;
    document.getElementById("wf-wacc").value = 12.0;
    document.getElementById("wf-mo").value = 38.0;
    document.getElementById("wf-ch4").value = 0.5;
  }
  drawWaterfall();
}
function animarWaterfall() {
  if (animWfId) cancelAnimationFrame(animWfId);
  const targetCh4 = Math.max(4, +document.getElementById("wf-ch4").value);
  const targetWacc = +document.getElementById("wf-wacc").value;
  document.getElementById("wf-ch4").value = 0;
  fijarGhostWaterfall();
  const t0 = performance.now(), dur = 1600;
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    const ease = 1 - Math.pow(1 - u, 3);
    document.getElementById("wf-ch4").value = (targetCh4 * ease).toFixed(1);
    drawWaterfall();
    if (u < 1) animWfId = requestAnimationFrame(step);
  }
  animWfId = requestAnimationFrame(step);
}
function drawWaterfall() {
  const cap = +document.getElementById("wf-cap").value;
  const vol = +document.getElementById("wf-vol").value;
  const mar = +document.getElementById("wf-mar").value;
  const wacc = +document.getElementById("wf-wacc").value;
  const mo = +document.getElementById("wf-mo").value;
  const ch4 = +document.getElementById("wf-ch4").value;

  document.getElementById("wf-cap-v").textContent = `$${fmtDec(cap, 1)} MM`;
  document.getElementById("wf-vol-v").textContent = `${fmtInt(vol)} t`;
  document.getElementById("wf-mar-v").textContent = `$${fmtInt(mar)}`;
  document.getElementById("wf-wacc-v").textContent = `${fmtDec(wacc, 1)}%`;
  document.getElementById("wf-mo-v").textContent = `$${fmtDec(mo, 1)} MM`;
  document.getElementById("wf-ch4-v").textContent = `${fmtDec(ch4, 1)} t`;

  const sVol = +document.getElementById("rd-vol").value;
  const sPre = +document.getElementById("rd-pre").value;
  const sCos = +document.getElementById("rd-cos").value;
  document.getElementById("rd-vol-v").textContent = (sVol >= 0 ? "+" : "") + sVol + "%";
  document.getElementById("rd-pre-v").textContent = (sPre >= 0 ? "+" : "") + sPre + "%";
  document.getElementById("rd-cos-v").textContent = (sCos >= 0 ? "+" : "") + sCos + "%";

  const volEff = Math.max(5, vol * (1 + sVol / 100));
  const marEff = Math.max(10000, mar * (1 + sPre / 100));
  const moEff = Math.max(5, mo * (1 + sCos / 100));
  const r = calcWaterfall(cap, volEff, marEff, wacc, moEff, ch4);

  const rdBox = document.getElementById("rd-box");
  if (rdBox) {
    const estP = r.vanPriv > 0 ? "<span style='color:#15803D;font-weight:800;'>VIABLE PRIVADAMENTE</span>" : "<span style='color:#DC2626;font-weight:800;'>QUIEBRE PRIVADO (VAN ≤ 0)</span>";
    const estS = r.vanSoc > 0 ? "<span style='color:#15803D;font-weight:800;'>VIABLE SOCIALMENTE</span>" : "<span style='color:#DC2626;font-weight:800;'>QUIEBRE SOCIAL (VANS ≤ 0)</span>";
    rdBox.innerHTML =
      `<b>Radar de Punto de Quiebre (Vol ${fmtInt(volEff)} t | Margen $${fmtInt(marEff)} | Planilla $${fmtDec(moEff,1)}M):</b> ` +
      `VAN Privado = <b>$${fmtDec(r.vanPriv, 1)} MM</b> (${estP}) &nbsp;|&nbsp; VANS Social = <b>$${fmtDec(r.vanSoc, 1)} MM</b> (${estS})`;
  }
  if (!ghostWf) ghostWf = { ...r };

  document.getElementById("wf-enunciado").innerHTML =
    `Un proyecto de valorización procesa <b>${fmtInt(vol)} ton/año</b> (creciendo 4% anual por 10 años) con CAPEX inicial de <b>$${fmtDec(cap, 1)} MM</b>, ` +
    `margen operativo bruto de <b>$${fmtInt(mar)}/ton</b> y planilla de personal de <b>$${fmtDec(mo, 1)} MM/año</b>. El privado exige un <b>WACC de ${fmtDec(wacc, 1)}%</b> y paga 25% de Impuesto a la Renta. ` +
    `Al evaluar socialmente bajo normativa <b>SNI 2026</b> (TSD = <b>5,5%</b>, corrección MO <b>0,97/0,95/0,91</b>, sin impuestos y evitando <b>${fmtDec(ch4, 1)} t CH<sub>4</sub>/año × 28</b> a <b>$71.801/t CO<sub>2</sub>eq</b>), observe cómo se construye cada peldaño desde el VAN Privado hasta el VANS Social.`;

  document.getElementById("wf-k-vp").textContent = `$${fmtDec(r.vanPriv, 1)} MM`;
  document.getElementById("wf-k-vp2").textContent = `Al ${fmtDec(wacc, 1)}% WACC`;
  const brechaTot = r.vanSoc - r.vanPriv;
  document.getElementById("wf-k-dif").textContent = `${brechaTot >= 0 ? "+" : ""}$${fmtDec(brechaTot, 1)} MM`;
  document.getElementById("wf-k-vs").textContent = `$${fmtDec(r.vanSoc, 1)} MM`;
  const dGhost = r.vanSoc - ghostWf.vanSoc;
  document.getElementById("wf-k-vs2").textContent = `Δ vs Fantasma: ${dGhost >= 0 ? "+" : ""}$${fmtDec(dGhost, 1)} MM`;
  document.getElementById("wf-k-co2").textContent = `$${fmtDec(r.benCarbMM, 1)} MM/año`;
  document.getElementById("wf-k-co2b").textContent = `${fmtDec(r.co2EqTon, 0)} t CO2eq × $71.801`;

  document.getElementById("wf-sol").innerHTML =
    `<b>Puente SNI 2026:</b> VAN Privado (<b>$${fmtDec(r.vanPriv, 1)}M</b>) + Efecto TSD 5,5% (<b>${r.dTsd >= 0 ? "+" : ""}$${fmtDec(r.dTsd, 1)}M</b>) ` +
    `+ Elim. Impuestos (<b>${r.dImp >= 0 ? "+" : ""}$${fmtDec(r.dImp, 1)}M</b>) + Corrección MO (<b>+$${fmtDec(r.dMo, 1)}M</b>) ` +
    `+ Carbono/GIRS (<b>+$${fmtDec(r.dCarb, 1)}M</b>) = <b>VANS Social $${fmtDec(r.vanSoc, 1)} MM</b>`;

  const svg = document.getElementById("svg-waterfall");
  svg.innerHTML = "";
  addDefs(svg);

  const steps = [
    { lbl: "1. VAN Privado", base: 0, val: r.vanPriv, type: "total", col: "#1E3A8A" },
    { lbl: "2. Efecto TSD 5,5%", base: r.vanPriv, val: r.dTsd, type: "delta", col: r.dTsd >= 0 ? "#16A34A" : "#DC2626" },
    { lbl: "3. Sin Impuestos", base: r.vanPriv + r.dTsd, val: r.dImp, type: "delta", col: r.dImp >= 0 ? "#16A34A" : "#DC2626" },
    { lbl: "4. Corrección MO", base: r.vanPriv + r.dTsd + r.dImp, val: r.dMo, type: "delta", col: "#0D9488" },
    { lbl: "5. Carbono + GIRS", base: r.vanPriv + r.dTsd + r.dImp + r.dMo, val: r.dCarb, type: "delta", col: "#EA580C" },
    { lbl: "6. VANS Social", base: 0, val: r.vanSoc, type: "total", col: "#0F172A" },
  ];

  const allY = [0, ghostWf.vanSoc, r.vanSoc, r.vanPriv];
  steps.forEach(s => { allY.push(s.base); allY.push(s.base + s.val); });
  const minY = Math.min(0, ...allY) * 1.15 - 15;
  const maxY = Math.max(80, ...allY) * 1.18 + 15;

  const M = { l: 68, r: 28, t: 32, b: 56 }, W = 960, H = 400;
  const sy = v => H - M.b - ((v - minY) / (maxY - minY)) * (H - M.t - M.b);

  for (let i = 0; i <= 5; i++) {
    const yv = minY + ((maxY - minY) / 5) * i;
    el("line", { x1: M.l, y1: sy(yv), x2: W - M.r, y2: sy(yv), stroke: "#E2E8F0" }, svg);
    const t = el("text", { x: M.l - 8, y: sy(yv) + 4, fill: "#475569", "font-size": "11", "text-anchor": "end" }, svg);
    t.textContent = `$${fmtInt(yv)}M`;
  }
  el("line", { x1: M.l, y1: sy(0), x2: W - M.r, y2: sy(0), stroke: "#334155", "stroke-width": "1.6" }, svg);

  const slotW = (W - M.l - M.r) / steps.length;
  const barW = slotW * 0.56;

  steps.forEach((st, idx) => {
    const x0 = M.l + idx * slotW + (slotW - barW) / 2;
    const yTop = sy(Math.max(st.base, st.base + st.val));
    const yBot = sy(Math.min(st.base, st.base + st.val));
    el("rect", { x: x0, y: yTop, width: barW, height: Math.max(2, yBot - yTop), fill: st.col, rx: 4, opacity: st.type === "total" ? "0.95" : "0.85" }, svg);

    // Conector punteado al siguiente peldaño
    if (idx < steps.length - 1) {
      const yEnd = sy(st.base + st.val);
      const xNext = M.l + (idx + 1) * slotW + (slotW - barW) / 2;
      el("line", { x1: x0 + barW, y1: yEnd, x2: xNext, y2: yEnd, stroke: "#94A3B8", "stroke-dasharray": "4,3" }, svg);
    }

    const txtVal = (st.type === "delta" && st.val >= 0 ? "+" : "") + `$${fmtDec(st.val, 1)}M`;
    const tv = el("text", { x: x0 + barW / 2, y: yTop - 6, fill: "#0F172A", "font-size": "11", "font-weight": "800", "text-anchor": "middle" }, svg);
    tv.textContent = txtVal;

    const tl = el("text", { x: x0 + barW / 2, y: H - M.b + 18, fill: "#1E293B", "font-size": "11", "font-weight": "700", "text-anchor": "middle" }, svg);
    tl.textContent = st.lbl;
  });

  // Rastro fantasma y flecha vertical sobre el último peldaño (VANS Social)
  if (Math.abs(dGhost) >= 2) {
    const xLast = M.l + 5 * slotW + (slotW - barW) / 2;
    const gyTop = sy(Math.max(0, ghostWf.vanSoc)), gyBot = sy(Math.min(0, ghostWf.vanSoc));
    el("rect", { x: xLast - 4, y: gyTop, width: barW + 8, height: Math.max(2, gyBot - gyTop), fill: "none", stroke: "#64748B", "stroke-width": "1.6", "stroke-dasharray": "5,4", rx: 4 }, svg);
    drawArrow(svg, xLast - 16, sy(ghostWf.vanSoc), xLast - 16, sy(r.vanSoc), dGhost > 0 ? "#15803D" : "#DC2626", dGhost > 0 ? "arr-green" : "arr-red",
      `${dGhost > 0 ? "↑ +" : "↓ -"}$${fmtDec(Math.abs(dGhost), 1)}M`, xLast - 24, (sy(ghostWf.vanSoc) + sy(r.vanSoc)) / 2 + 4, "end");
  }

  const quadTxt = (r.vanPriv >= 0 && r.vanSoc >= 0) ? "Cuadrante I (+,+): viable sin subsidio" :
                  (r.vanPriv < 0 && r.vanSoc >= 0) ? "Cuadrante II (−,+): justifica subsidio o ejecución pública" :
                  (r.vanPriv >= 0 && r.vanSoc < 0) ? "Cuadrante III (+,−): requiere impuesto pigouviano o regulación" : "Cuadrante IV (−,−): rechazar en ambos planos";
  renderFormulaStrip("wf-fstrip", [
    {
      lbl: "Puente Privado → Social (SNI 2026)", col: "#1D4ED8",
      eq: `VANS = VAN<sub>priv</sub> + ΔTSD + ΔImp + ΔMO + ΔCarb`,
      sub: `VANS = ${vChip("$"+fmtDec(r.vanPriv,1)+"M","vc-b","VAN Privado al WACC")} + ${vChip("$"+fmtDec(r.dTsd,1)+"M","vc-p","Efecto bajar a TSD 5,5%")} + ${vChip("$"+fmtDec(r.dImp,1)+"M","vc-o","Quitar impuestos")} + ${vChip("$"+fmtDec(r.dMo,1)+"M","vc-t","Precios sombra MO")} + ${vChip("$"+fmtDec(r.dCarb,1)+"M","vc-g","Carbono + GIRS")} = ${rChip("$"+fmtDec(r.vanSoc,1)+"M", r.vanSoc < 0)}`,
      note: `CAPEX ${eChip("$"+fmtDec(cap,1)+"M",cap,"wf_cap","1","vc-r","Inversión inicial CAPEX (MM$)")} · WACC ${eChip(fmtDec(wacc,1)+"%",wacc,"wf_wacc","0.5","vc-p","Tasa descuento privada WACC")}`
    },
    {
      lbl: "Carbono Equivalente IPCC y Beneficio GEI", col: "#15803D",
      eq: `CO<sub>2</sub>eq = 0,25·<span class="sym-b">Vol</span> + 28·<span class="sym-t">CH<sub>4</sub></span>`,
      sub: `CO<sub>2</sub>eq = 0,25·${eChip(fmtInt(vol)+"t",vol,"wf_vol","5","vc-b","Volumen base (t/año)")} + 28·${eChip(fmtDec(ch4,1)+"t",ch4,"wf_ch4","0.5","vc-t","Metano evitado CH4 (t/año)")} = ${rChip(fmtDec(r.co2EqTon,1)+" t")}`,
      note: `A $71.801/t CO<sub>2</sub>eq + ahorro GIRS = <b>$${fmtDec(r.benCarbMM,2)} MM/año</b>`
    },
    {
      lbl: "Parámetros Operativos y Shocks del Radar", col: "#7C3AED",
      eq: `Margen = <span class="sym-b">M<sub>0</sub></span>(1+ΔP) · MO = <span class="sym-o">MO<sub>0</sub></span>(1+ΔC)`,
      sub: `M<sub>0</sub>=${eChip("$"+fmtInt(mar),mar,"wf_mar","5000","vc-b","Margen unitario ($/t)")} (${eChip((sPre>=0?"+":"")+sPre+"%",sPre,"rd_pre","1","vc-p","Shock Precio %")}) · MO=${eChip("$"+fmtDec(mo,1)+"M",mo,"wf_mo","1","vc-o","Planilla MO (MM$/año)")} (${eChip((sCos>=0?"+":"")+sCos+"%",sCos,"rd_cos","1","vc-r","Shock Costos %")})`,
      note: `Shock Volumen: ${eChip((sVol>=0?"+":"")+sVol+"%",sVol,"rd_vol","1","vc-t","Shock Volumen %")} → Vol efectivo = ${fmtInt(volEff)} t/año`
    }
  ]);
  renderPedBox("ped-waterfall",
    `Bajo los parámetros actuales, el salto de <b>VAN Privado ($${fmtDec(r.vanPriv,1)}M)</b> a <b>VANS Social ($${fmtDec(r.vanSoc,1)}M)</b> suma <b>${brechaTot >= 0 ? "+" : ""}$${fmtDec(brechaTot,1)} MM</b> y ubica al proyecto en <b>${quadTxt}</b>.`,
    `<b>¿Por qué "borrar" impuestos hace más rentable a un proyecto social?</b> Porque para el país como un todo, el IVA o el Impuesto a la Renta que paga la empresa es exactamente el mismo dinero que recibe el Fisco: es un cambio de bolsillo interno (transferencia pura), no un consumo real de acero, horas-hombre o energía.`,
    `En defensa ante el SNI / MDSF 2026: si un proyecto cae en el <b>Cuadrante II</b> (como iniciativas de reciclaje municipal), el subsidio máximo que el Estado puede otorgar jamás debe superar el <b>VANS</b>.`
  );
}

// ============================================================================
// 6. HORNO DE PAN (FONTAINE CAP I-II) + COSTOS HUNDIDOS A 60 FPS
// ============================================================================
let ghostHn = { pb: 104, pe: 133, ce: 30, sub: 6 };
let animHnId = null;
let decHundido = "formar";

function fijarGhostHorno() {
  ghostHn = {
    pb: +document.getElementById("hn-pb").value,
    pe: +document.getElementById("hn-pe").value,
    ce: +document.getElementById("hn-ce").value,
    sub: +document.getElementById("hn-sub").value,
  };
  drawHorno();
}
function resetHorno() {
  if (animHnId) cancelAnimationFrame(animHnId);
  document.getElementById("hn-pb").value = 104;
  document.getElementById("hn-pe").value = 133;
  document.getElementById("hn-ce").value = 30;
  document.getElementById("hn-sub").value = 6;
  ghostHn = { pb: 104, pe: 133, ce: 30, sub: 6 };
  drawHorno();
}
function animarHorno() {
  if (animHnId) cancelAnimationFrame(animHnId);
  document.getElementById("hn-sub").value = 0;
  fijarGhostHorno();
  const t0 = performance.now(), dur = 1600;
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    const ease = 1 - Math.pow(1 - u, 2.5);
    document.getElementById("hn-sub").value = Math.round(12 * ease);
    drawHorno();
    if (u < 1) animHnId = requestAnimationFrame(step);
  }
  animHnId = requestAnimationFrame(step);
}
function drawHorno() {
  const pb = +document.getElementById("hn-pb").value;
  const pe = +document.getElementById("hn-pe").value;
  const ce = +document.getElementById("hn-ce").value;
  const sub = +document.getElementById("hn-sub").value;

  document.getElementById("hn-pb-v").textContent = "$" + pb;
  document.getElementById("hn-pe-v").textContent = "$" + pe;
  document.getElementById("hn-ce-v").textContent = "$" + ce;
  document.getElementById("hn-sub-v").textContent = "$" + sub;

  // Base: insumos=80, factores(trabajo+cap)=20 => costo=100; Envasado agrega +20 factores + (ce-20) insumos
  const vaBase = pb - 80;
  const epBase = pb - 100;
  const esBase = epBase - sub;

  const vaEnv = pe - (80 + Math.max(0, ce - 20));
  const epEnv = pe - (100 + ce);
  const esEnv = epEnv - sub;

  const gEsBase = (ghostHn.pb - 100) - ghostHn.sub;
  const gEsEnv = (ghostHn.pe - (100 + ghostHn.ce)) - ghostHn.sub;

  document.getElementById("hn-enunciado").innerHTML =
    `<b>Ejercicio 1.1 (Fontaine, págs. 16–35):</b> Un panadero produce pan con un costo privado total de <b>$100</b> ($80 insumos + $20 trabajo/capital) y lo vende a <b>P<sub>base</sub> = $${pb}</b>. ` +
    `Evalúa agregar envasado y reparto a domicilio con un costo adicional de <b>$${ce}</b> para venderlo a <b>P<sub>env</sub> = $${pe}</b>. ` +
    `Además, existe un <b>subsidio oculto estatal de $${sub}</b> sobre un insumo clave (ej. agua/energía subsidiada — <i>Precio Mentiroso</i>). Compare Valor Agregado, Excedente Privado y Excedente Social.`;

  document.getElementById("hn-k-va").textContent = `$${vaBase} → $${vaEnv}`;
  document.getElementById("hn-k-va2").textContent = `ΔVA = ${vaEnv - vaBase >= 0 ? "+" : ""}$${vaEnv - vaBase}`;
  document.getElementById("hn-k-epb").textContent = `${epBase >= 0 ? "+" : ""}$${epBase}`;
  document.getElementById("hn-k-epe").textContent = `${epEnv >= 0 ? "+" : ""}$${epEnv}`;
  document.getElementById("hn-k-epe2").textContent = `Δ vs base = ${epEnv - epBase >= 0 ? "+" : ""}$${epEnv - epBase}`;
  document.getElementById("hn-k-es").textContent = `$${esBase} | $${esEnv}`;
  document.getElementById("hn-k-es2").textContent = esBase < 0 ? "Bueno p/Juan, malo p/país" : "Excedente social positivo";

  document.getElementById("hn-sol").innerHTML =
    `<b>Trampa del Valor Agregado:</b> Al envasar, el Valor Agregado cambia en <b>${vaEnv - vaBase >= 0 ? "+" : ""}$${vaEnv - vaBase}</b>, pero el Excedente Privado cambia en <b>${epEnv - epBase >= 0 ? "+" : ""}$${epEnv - epBase}</b> (agregar trabajo/capital es COSTO, no beneficio). ` +
    `<b>Precio Mentiroso:</b> Con subsidio oculto de $${sub}, el Excedente Social real pasa de <b>$${esBase}</b> (base) a <b>$${esEnv}</b> (envasado).`;

  const svg = document.getElementById("svg-horno");
  svg.innerHTML = "";
  addDefs(svg);

  const groups = [
    { name: "1. Valor Agregado", b: vaBase, e: vaEnv },
    { name: "2. Excedente Privado", b: epBase, e: epEnv },
    { name: "3. Excedente Social (c/Subsidio)", b: esBase, e: esEnv },
  ];
  const vals = [0, 50, -15, vaBase, vaEnv, epBase, epEnv, esBase, esEnv, gEsBase, gEsEnv];
  const minY = Math.min(-18, ...vals) * 1.15;
  const maxY = Math.max(55, ...vals) * 1.18;

  const M = { l: 60, r: 30, t: 28, b: 48 }, W = 960, H = 350;
  const sy = v => H - M.b - ((v - minY) / (maxY - minY)) * (H - M.t - M.b);

  for (let i = 0; i <= 5; i++) {
    const yv = minY + ((maxY - minY) / 5) * i;
    el("line", { x1: M.l, y1: sy(yv), x2: W - M.r, y2: sy(yv), stroke: "#E2E8F0" }, svg);
    const t = el("text", { x: M.l - 8, y: sy(yv) + 4, fill: "#475569", "font-size": "11", "text-anchor": "end" }, svg);
    t.textContent = "$" + fmtInt(yv);
  }
  el("line", { x1: M.l, y1: sy(0), x2: W - M.r, y2: sy(0), stroke: "#0F172A", "stroke-width": "1.8" }, svg);

  const slotW = (W - M.l - M.r) / 3;
  const bw = 72;
  groups.forEach((g, idx) => {
    const cx = M.l + idx * slotW + slotW / 2;
    const drawB = (x, val, col) => {
      const yT = sy(Math.max(0, val)), yB = sy(Math.min(0, val));
      el("rect", { x, y: yT, width: bw, height: Math.max(2, yB - yT), fill: val < 0 ? "#DC2626" : col, rx: 4 }, svg);
      const t = el("text", { x: x + bw / 2, y: val >= 0 ? yT - 6 : yB + 14, fill: val < 0 ? "#DC2626" : "#0F172A", "font-size": "12", "font-weight": "800", "text-anchor": "middle" }, svg);
      t.textContent = (val < 0 ? "-$" : "$") + Math.abs(val);
    };
    drawB(cx - bw - 8, g.b, "#1E293B");
    drawB(cx + 8, g.e, "#0D9488");

    const tl = el("text", { x: cx, y: H - M.b + 20, fill: "#0F172A", "font-size": "12", "font-weight": "700", "text-anchor": "middle" }, svg);
    tl.textContent = g.name;
  });

  // Flecha en Excedente Social vs Fantasma
  if (Math.abs(esBase - gEsBase) >= 2) {
    const cx3 = M.l + 2 * slotW + slotW / 2;
    drawArrow(svg, cx3 - bw - 26, sy(gEsBase), cx3 - bw - 26, sy(esBase), esBase < gEsBase ? "#DC2626" : "#15803D", esBase < gEsBase ? "arr-red" : "arr-green",
      `${esBase - gEsBase >= 0 ? "↑ +" : "↓ -"}$${Math.abs(esBase - gEsBase)}`, cx3 - bw - 34, (sy(gEsBase) + sy(esBase)) / 2 + 4, "end");
  }

  renderFormulaStrip("hn-fstrip", [
    {
      lbl: "Pan Base: Excedente Privado vs. Social", col: "#1D4ED8",
      eq: `ES<sub>base</sub> = (<span class="sym-b">P<sub>base</sub></span> − 100) − <span class="sym-r">Sub</span>`,
      sub: `ES<sub>base</sub> = (${eChip("$"+pb,pb,"hn_pb","1","vc-b","Precio Pan Base")} − 100) − ${eChip("$"+sub,sub,"hn_sub","1","vc-r","Subsidio oculto estatal")} = ${vChip("$"+epBase,"vc-t","Excedente Privado")} − $${sub} = ${rChip("$"+esBase, esBase < 0)}`,
      note: `Valor Agregado Base = $${vaBase} | ${epBase > 0 && esBase < 0 ? "¡Trampa! Privado gana pero País pierde" : "Signos consistentes"}`
    },
    {
      lbl: "Pan Envasado: Excedente Privado vs. Social", col: "#7C3AED",
      eq: `ES<sub>env</sub> = (<span class="sym-p">P<sub>env</sub></span> − (100 + <span class="sym-o">C<sub>env</sub></span>)) − <span class="sym-r">Sub</span>`,
      sub: `ES<sub>env</sub> = (${eChip("$"+pe,pe,"hn_pe","1","vc-p","Precio Pan Envasado")} − (100 + ${eChip("$"+ce,ce,"hn_ce","1","vc-o","Costo extra envasado")})) − ${eChip("$"+sub,sub,"hn_sub","1","vc-r","Subsidio oculto")} = ${rChip("$"+esEnv, esEnv < 0)}`,
      note: `EP Envasado = $${epEnv} | VA Envasado = $${vaEnv}`
    }
  ]);
  renderPedBox("ped-horno",
    `Al pasar del pan base al envasado, el Valor Agregado cambia en <b>${vaEnv - vaBase >= 0 ? "+" : ""}$${vaEnv - vaBase}</b>, pero el Excedente Privado cambia en <b>${epEnv - epBase >= 0 ? "+" : ""}$${epEnv - epBase}</b>. Al incorporar el subsidio oculto de <b>$${sub}</b>, el Excedente Social real del pan base es <b>$${esBase}</b>.`,
    `<b>La Trampa del "Más Empleo y Más Valor Agregado":</b> en política pública suele venderse un proyecto porque "contrata más gente y agrega valor". Fontaine demuestra con este horno que contratar trabajo y capital cuesta recursos escasos: si el consumidor paga $29 extra por algo que cuesta $30 producir, el Valor Agregado sube en +$19 pero <b>el país se empobrece en -$1</b>.`,
    `Y con el <b>Precio Mentiroso</b> (subsidio de $${sub} a un insumo): el negocio puede darle ganancias a Juan (+$${epBase}) mientras destruye riqueza nacional ($${esBase}). De ahí nace toda la evaluación social de proyectos.`
  );
}

function setDecisionHundido(modo) {
  decHundido = modo;
  document.getElementById("ch-btn-a").classList.toggle("primary", modo === "formar");
  document.getElementById("ch-btn-b").classList.toggle("primary", modo === "seguir");
  drawHundido();
}
function drawHundido() {
  const liq = +document.getElementById("ch-liq").value;
  document.getElementById("ch-liq-v").textContent = "$" + fmtInt(liq);
  const opEvit = 5845; // Mano de obra + patente + impuestos evitables
  const rCosto = 0.10;
  const kPert = decHundido === "formar" ? 13050 : liq;
  const minIngF = opEvit + Math.round(kPert * rCosto);
  renderFormulaStrip("ch-fstrip", [
    {
      lbl: decHundido === "formar" ? "Regla Costos Pertinentes (Antes de Invertir)" : "Regla Costos Hundidos (Fábrica ya Construida)", col: "#0F766E",
      eq: decHundido === "formar" ? `Ing<sub>mín</sub> = C<sub>evit</sub> + 10%·Inv<sub>nueva</sub> + $0<sub>hund</sub>` : `Ing<sub>mín</sub> = C<sub>evit</sub> + 10%·<span class="sym-b">V<sub>Liq</sub></span> + $0<sub>hund</sub>`,
      sub: decHundido === "formar"
        ? `Ing<sub>mín</sub> = ${vChip("$"+fmtInt(opEvit),"vc-o","Costos operativos evitables")} + 10%·${vChip("$13.050","vc-b","Inversión evitable antes de construir")} = ${rChip("$"+fmtInt(minIngF)+"/año")}`
        : `Ing<sub>mín</sub> = ${vChip("$"+fmtInt(opEvit),"vc-o","Costos operativos evitables")} + 10%·${eChip("$"+fmtInt(liq),liq,"ch_liq","100","vc-b","Valor de Liquidación hoy ($)")} = ${rChip("$"+fmtInt(minIngF)+"/año")}`,
      note: `Estudio de factibilidad ($250) = Costo Hundido ($0 entra en ambas decisiones)`
    }
  ]);
  if (decHundido === "formar") {
    const invNueva = 13050; // Equivale a anualidad/costo capital 1.305
    const minIng = opEvit + Math.round(invNueva * rCosto);
    document.getElementById("ch-res-box").innerHTML =
      `<b>A. Decisión ANTES de invertir:</b> El estudio de factibilidad ya pagado ($250) es <b>Costo Hundido ($0 entra)</b>. ` +
      `Son pertinentes todos los costos evitables ($${fmtInt(opEvit)}/año) + costo de oportunidad del capital nuevo ($${fmtInt(invNueva * rCosto)}/año) ⇒ ` +
      `<b>Ingreso anual mínimo exigido = $${fmtInt(minIng)}/año</b>.`;
  } else {
    const minSeguir = opEvit + Math.round(liq * rCosto);
    document.getElementById("ch-res-box").innerHTML =
      `<b>B. Decisión CON FÁBRICA YA CONSTRUIDA:</b> Tanto el estudio ($250) como lo pagado históricamente por la planta son <b>Hundidos</b>. ` +
      `Solo importa lo evitable ($${fmtInt(opEvit)}/año) + rentabilidad alternativa del <b>Valor de Liquidación hoy ($${fmtInt(liq)} × 10% = $${fmtInt(liq * rCosto)}/año)</b> ⇒ ` +
      `<b>Ingreso mínimo para NO cerrar = $${fmtInt(minSeguir)}/año</b>.`;
  }
}

// ============================================================================
// 7. DÉFICIT DE AGUA POTABLE (10 AÑOS ANIMADO) + TEA Y CAPM A 60 FPS
// ============================================================================
let ghostAgDef10 = 3413;
let animAgId = null;

function fijarGhostAgua() {
  const p0 = +document.getElementById("ag-p0").value;
  const r = +document.getElementById("ag-r").value / 100;
  const dot = +document.getElementById("ag-dot").value;
  const ofe = +document.getElementById("ag-ofe").value;
  ghostAgDef10 = (p0 * Math.pow(1 + r, 9) * dot) / 1000 - ofe;
  drawAgua();
}
function resetAgua() {
  if (animAgId) cancelAnimationFrame(animAgId);
  document.getElementById("ag-p0").value = 35200;
  document.getElementById("ag-r").value = 3.2;
  document.getElementById("ag-dot").value = 180;
  document.getElementById("ag-ofe").value = 5000;
  fijarGhostAgua();
}
function animarAgua() {
  if (animAgId) cancelAnimationFrame(animAgId);
  const t0 = performance.now(), dur = 1800;
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    const k = Math.max(1, Math.min(10, Math.ceil(u * 10)));
    drawAgua(k);
    if (u < 1) animAgId = requestAnimationFrame(step);
  }
  animAgId = requestAnimationFrame(step);
}
function drawAgua(maxVisibleYear = 10) {
  const p0 = +document.getElementById("ag-p0").value;
  const rPct = +document.getElementById("ag-r").value;
  const r = rPct / 100;
  const dot = +document.getElementById("ag-dot").value;
  const ofe = +document.getElementById("ag-ofe").value;

  document.getElementById("ag-p0-v").textContent = fmtInt(p0);
  document.getElementById("ag-r-v").textContent = fmtDec(rPct, 1) + "%";
  document.getElementById("ag-dot-v").textContent = dot + " L";
  document.getElementById("ag-ofe-v").textContent = fmtInt(ofe) + " m³";

  const dems = [], defs = [], pobs = [];
  for (let t = 0; t < 10; t++) {
    const pt = p0 * Math.pow(1 + r, t);
    const dm = (pt * dot) / 1000;
    pobs.push(pt);
    dems.push(dm);
    defs.push(dm - ofe);
  }

  document.getElementById("ag-enunciado").innerHTML =
    `Un municipio posee una población actual de <b>P<sub>0</sub> = ${fmtInt(p0)} habitantes</b> que crece geométricamente al <b>r = ${fmtDec(rPct, 1)}% anual</b> ` +
    `(P<sub>t</sub> = P<sub>0</sub>·(1+r)<sup>t</sup>), con consumo normativo de <b>${dot} litros/día/persona</b>. ` +
    `La planta actual tiene capacidad fija de <b>${fmtInt(ofe)} m³/día</b>. Dimensione el déficit proyectado al Año 10 para la ampliación.`;

  document.getElementById("ag-k-d1").textContent = `${fmtInt(dems[0])} m³/d`;
  document.getElementById("ag-k-def1").textContent = `Déficit Año 1: ${fmtInt(Math.max(0, defs[0]))} m³/d`;
  document.getElementById("ag-k-d10").textContent = `${fmtInt(dems[9])} m³/d`;
  document.getElementById("ag-k-def10").textContent = `Déficit Año 10: ${fmtInt(Math.max(0, defs[9]))} m³/d`;
  document.getElementById("ag-k-p10").textContent = `${fmtInt(pobs[9])} hab.`;
  const dDef = defs[9] - ghostAgDef10;
  document.getElementById("ag-k-dp").textContent = `Δ Déficit Año 10 vs Fantasma: ${dDef >= 0 ? "+" : ""}${fmtInt(dDef)} m³`;

  const svg = document.getElementById("svg-agua");
  svg.innerHTML = "";
  addDefs(svg);

  const M = { l: 68, r: 30, t: 26, b: 44 }, W = 960, H = 330;
  const maxY = Math.max(dems[9], ofe, ofe + ghostAgDef10) * 1.18;
  const sy = v => H - M.b - (v / maxY) * (H - M.t - M.b);

  for (let i = 0; i <= 4; i++) {
    const yv = (maxY / 4) * i;
    el("line", { x1: M.l, y1: sy(yv), x2: W - M.r, y2: sy(yv), stroke: "#E2E8F0" }, svg);
    const t = el("text", { x: M.l - 8, y: sy(yv) + 4, fill: "#475569", "font-size": "11", "text-anchor": "end" }, svg);
    t.textContent = fmtInt(yv) + " m³";
  }
  el("line", { x1: M.l, y1: H - M.b, x2: W - M.r, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);

  const slotW = (W - M.l - M.r) / 10;
  const bw = slotW * 0.56;
  const linePts = [];

  for (let t = 0; t < maxVisibleYear; t++) {
    const x0 = M.l + t * slotW + (slotW - bw) / 2;
    const hOfe = Math.min(dems[t], ofe);
    el("rect", { x: x0, y: sy(ofe), width: bw, height: Math.max(1, sy(0) - sy(ofe)), fill: "#1D4ED8", opacity: "0.85", rx: 2 }, svg);
    if (defs[t] > 0) {
      el("rect", { x: x0, y: sy(dems[t]), width: bw, height: Math.max(1, sy(ofe) - sy(dems[t])), fill: "#DC2626", opacity: "0.85", rx: 2 }, svg);
    }
    linePts.push(`${x0 + bw / 2},${sy(dems[t])}`);
    const tl = el("text", { x: x0 + bw / 2, y: H - M.b + 16, fill: "#334155", "font-size": "11", "font-weight": "700", "text-anchor": "middle" }, svg);
    tl.textContent = `Año ${t + 1}`;
  }
  if (linePts.length > 1) {
    el("polyline", { points: linePts.join(" "), fill: "none", stroke: "#0F172A", "stroke-width": "2.6" }, svg);
  }
  // Flecha vertical en Año 10 si cambió respecto al fantasma
  if (maxVisibleYear === 10 && Math.abs(dDef) >= 80) {
    const x10 = M.l + 9 * slotW + slotW / 2;
    const yGhost = sy(ofe + ghostAgDef10);
    el("line", { x1: x10 - bw / 2 - 4, y1: yGhost, x2: x10 + bw / 2 + 4, y2: yGhost, stroke: "#64748B", "stroke-width": "2", "stroke-dasharray": "4,3" }, svg);
    drawArrow(svg, x10 - bw / 2 - 12, yGhost, x10 - bw / 2 - 12, sy(dems[9]), dDef > 0 ? "#DC2626" : "#15803D", dDef > 0 ? "arr-red" : "arr-green",
      `${dDef > 0 ? "↑ +" : "↓ -"}${fmtInt(Math.abs(dDef))} m³`, x10 - bw / 2 - 18, (yGhost + sy(dems[9])) / 2 + 4, "end");
  }

  renderFormulaStrip("ag-fstrip", [
    {
      lbl: "Crecimiento Poblacional al Año 10", col: "#1D4ED8",
      eq: `P<sub>10</sub> = <span class="sym-b">P<sub>0</sub></span> · (1 + <span class="sym-p">r</span>)<sup>9</sup>`,
      sub: `P<sub>10</sub> = ${eChip(fmtInt(p0),p0,"ag_p0","200","vc-b","Población inicial P0")} · (1 + ${eChip(fmtDec(rPct,1)+"%",rPct,"ag_r","0.1","vc-p","Tasa crecimiento r (%)")})<sup>9</sup> = ${rChip(fmtInt(pobs[9])+" hab")}`,
      note: `De Año 1 (t=0) a Año 10 (t=9) hay 9 períodos de crecimiento`
    },
    {
      lbl: "Demanda y Déficit Hídrico Año 10", col: "#DC2626",
      eq: `Déf<sub>10</sub> = ${mFrac('P<sub>10</sub> · <span class="sym-t">Dot</span>', '1.000')} − <span class="sym-o">Ofe</span>`,
      sub: `Déf<sub>10</sub> = ${mFrac(fmtInt(pobs[9]) + " · " + eChip(dot+" L",dot,"ag_dot","10","vc-t","Dotación (L/hab/día)"), "1.000")} − ${eChip(fmtInt(ofe)+" m³",ofe,"ag_ofe","250","vc-o","Oferta actual planta (m³/día)")} = ${rChip(fmtInt(defs[9])+" m³/d", defs[9] > 0)}`,
      note: `Demanda Año 10 = ${fmtInt(dems[9])} m³/día · Clic en P0, r, Dot u Ofe para editar`
    }
  ]);
  renderPedBox("ped-agua",
    `Con crecimiento geométrico del <b>${fmtDec(rPct,1)}%</b> anual, la población llega a <b>${fmtInt(pobs[9])} hab.</b> en el Año 10 y el déficit diario de agua potable se amplía de <b>${fmtInt(Math.max(0,defs[0]))} m³/d</b> a <b>${fmtInt(Math.max(0,defs[9]))} m³/d</b>.`,
    `<b>El error del crecimiento lineal en infraestructura:</b> proyectar población sumando una cantidad fija por año subestima brutalmente el Año 10. Como la población se multiplica por (1+r)<sup>t</sup> (interés compuesto demográfico), una planta subdimensionada colapsa a mitad de su vida útil.`,
    `En el <b>SNI / CEPAL N° 39</b>, antes de construir una planta nueva siempre debes definir primero la <b>Situación Base Optimizada</b> (reparar fugas de red o mejorar gestión) para no atribuir al proyecto beneficios que se lograban a bajo costo.`
  );
}

function drawTeaCapm() {
  const tnaPct = +document.getElementById("tc-tna").value;
  const dias = +document.getElementById("tc-dias").value;
  document.getElementById("tc-tna-v").textContent = fmtDec(tnaPct, 1) + "%";
  document.getElementById("tc-dias-v").textContent = dias + " días";

  const tna = tnaPct / 100;
  const teaD = (Math.pow(1 + (tna * dias) / 365, 365 / dias) - 1) * 100;
  const teaC = (Math.exp(tna) - 1) * 100;
  document.getElementById("tc-tea-box").innerHTML =
    `<b>TEA Discreta:</b> (1 + ${fmtDec(tnaPct,1)}%·${dias}/365)<sup>365/${dias}</sup> − 1 = <b>${fmtDec(teaD, 2)}%</b><br/>` +
    `<b>TEA Continua:</b> e<sup>${fmtDec(tna, 3)}</sup> − 1 = <b>${fmtDec(teaC, 2)}%</b>`;

  const rf = +document.getElementById("tc-rf").value;
  const beta = +document.getElementById("tc-beta").value;
  const rm = +document.getElementById("tc-rm").value;
  document.getElementById("tc-rf-v").textContent = fmtDec(rf, 1) + "%";
  document.getElementById("tc-beta-v").textContent = fmtDec(beta, 2);
  document.getElementById("tc-rm-v").textContent = fmtDec(rm, 1) + "%";

  const ke = rf + beta * (rm - rf);
  document.getElementById("tc-capm-box").innerHTML =
    `<b>CAPM:</b> E(R<sub>i</sub>) = ${fmtDec(rf,1)}% + ${fmtDec(beta,2)}·(${fmtDec(rm,1)}% − ${fmtDec(rf,1)}%) = <b>${fmtDec(ke, 2)}%</b>`;

  renderFormulaStrip("tc-fstrip", [
    {
      lbl: "Tasa Efectiva Anual (TEA Discreta)", col: "#1D4ED8",
      eq: `TEA = (1 + <span class="sym-b">TNA</span>·${mFrac('<span class="sym-p">d</span>', '365')})<sup>365/<span class="sym-p">d</span></sup> − 1`,
      sub: `TEA = (1 + ${eChip(fmtDec(tnaPct,1)+"%",tnaPct,"tc_tna","0.5","vc-b","Tasa Nominal Anual TNA (%)")}·${mFrac(eChip(dias+"d",dias,"tc_dias","1","vc-p","Días de capitalización"), "365")})<sup>${fmtDec(365/dias,1)}</sup> − 1 = ${rChip(fmtDec(teaD,2)+"%")}`,
      note: `Límite continuo e<sup>TNA</sup> − 1 = <b>${fmtDec(teaC,2)}%</b>`
    },
    {
      lbl: "Costo de Capital Patrimonial (CAPM)", col: "#7C3AED",
      eq: `E(R<sub>i</sub>) = <span class="sym-t">R<sub>f</sub></span> + <span class="sym-p">β</span>·(<span class="sym-o">R<sub>m</sub></span> − <span class="sym-t">R<sub>f</sub></span>)`,
      sub: `k<sub>e</sub> = ${eChip(fmtDec(rf,1)+"%",rf,"tc_rf","0.1","vc-t","Tasa libre de riesgo Rf (%)")} + ${eChip(fmtDec(beta,2),beta,"tc_beta","0.05","vc-p","Beta sistemático β")}·(${eChip(fmtDec(rm,1)+"%",rm,"tc_rm","0.5","vc-o","Retorno de mercado Rm (%)")} − ${fmtDec(rf,1)}%) = ${rChip(fmtDec(ke,2)+"%")}`,
      note: `Prima por riesgo de mercado (Rm − Rf) = ${fmtDec(rm-rf,1)}%`
    }
  ]);
  // Mini SVG Línea del Mercado de Valores (SML) a 60 FPS
  const svg = document.getElementById("svg-capm");
  svg.innerHTML = "";
  const M = { l: 44, r: 22, t: 14, b: 26 }, W = 460, H = 150;
  const sx = b => M.l + (b / 2.5) * (W - M.l - M.r);
  const sy = r => H - M.b - (Math.min(32, Math.max(0, r)) / 32) * (H - M.t - M.b);

  el("line", { x1: M.l, y1: H - M.b, x2: W - M.r, y2: H - M.b, stroke: "#334155", "stroke-width": "1.4" }, svg);
  el("line", { x1: M.l, y1: M.t, x2: M.l, y2: H - M.b, stroke: "#334155", "stroke-width": "1.4" }, svg);
  const yEnd = rf + 2.5 * (rm - rf);
  el("line", { x1: sx(0), y1: sy(rf), x2: sx(2.5), y2: sy(yEnd), stroke: "#1D4ED8", "stroke-width": "2.4" }, svg);
  el("line", { x1: M.l, y1: sy(ke), x2: sx(beta), y2: sy(ke), stroke: "#94A3B8", "stroke-dasharray": "3,3" }, svg);
  el("line", { x1: sx(beta), y1: sy(ke), x2: sx(beta), y2: H - M.b, stroke: "#94A3B8", "stroke-dasharray": "3,3" }, svg);
  el("circle", { cx: sx(1.0), cy: sy(rm), r: 4, fill: "#475569" }, svg);
  el("circle", { cx: sx(beta), cy: sy(ke), r: 6, fill: "#DC2626", stroke: "#FFFFFF", "stroke-width": "1.5" }, svg);
  const tl = el("text", { x: sx(beta) + 8, y: sy(ke) + 4, fill: "#DC2626", "font-size": "11", "font-weight": "800" }, svg);
  tl.textContent = `Ke = ${fmtDec(ke, 2)}% (β=${fmtDec(beta, 2)})`;
  const tx = el("text", { x: W - M.r, y: H - 6, fill: "#475569", "font-size": "10", "text-anchor": "end" }, svg);
  tx.textContent = "Riesgo Sistemático (β)";
}


function resetRadar() {
  document.getElementById("rd-vol").value = 0;
  document.getElementById("rd-pre").value = 0;
  document.getElementById("rd-cos").value = 0;
  drawWaterfall();
}
function presetRadar(v, p, c) {
  fijarGhostWaterfall();
  document.getElementById("rd-vol").value = v;
  document.getElementById("rd-pre").value = p;
  document.getElementById("rd-cos").value = c;
  drawWaterfall();
}

// ============================================================================
// 8. AMBIENTAL RA2: MATRIZ DE LEOPOLD INTERACTIVA + BARZEV MCV + GEI 2026
// ============================================================================
const LEO_FACTORES = ["Suelo / Vertedero", "Aire / Ruido / GEI", "Agua y Drenaje", "Empleo y Comunidad"];
const LEO_ACCIONES = ["1. Recolección Logística", "2. Operación Planta", "3. Valorización Circular"];
let leoData = [
  [{ m: 5, i: 6 }, { m: 2, i: 4 }, { m: 9, i: 9 }],
  [{ m: -3, i: 5 }, { m: -2, i: 4 }, { m: 8, i: 8 }],
  [{ m: 2, i: 3 }, { m: -1, i: 3 }, { m: 6, i: 7 }],
  [{ m: 4, i: 5 }, { m: 7, i: 7 }, { m: 6, i: 6 }],
];
let leoBuilt = false;

function presetLeopold(tipo) {
  if (tipo === "mitigado") {
    leoData = [
      [{ m: 5, i: 6 }, { m: 2, i: 4 }, { m: 9, i: 9 }],
      [{ m: -3, i: 5 }, { m: -2, i: 4 }, { m: 8, i: 8 }],
      [{ m: 2, i: 3 }, { m: -1, i: 3 }, { m: 6, i: 7 }],
      [{ m: 4, i: 5 }, { m: 7, i: 7 }, { m: 6, i: 6 }],
    ];
  } else {
    leoData = [
      [{ m: -4, i: 6 }, { m: -5, i: 7 }, { m: 2, i: 4 }],
      [{ m: -6, i: 7 }, { m: -7, i: 8 }, { m: 1, i: 4 }],
      [{ m: -3, i: 5 }, { m: -5, i: 6 }, { m: 0, i: 3 }],
      [{ m: 2, i: 4 }, { m: 3, i: 5 }, { m: 2, i: 4 }],
    ];
  }
  leoBuilt = false;
  drawAmbiental();
}
function updateLeoCell(r, c, field, val) {
  leoData[r][c][field] = +val;
  refreshLeopoldVisual();
}
function buildLeopoldTable() {
  const wrap = document.getElementById("leo-grid-wrap");
  if (!wrap) return;
  let html = `<table class="leo-table"><thead><tr><th>Factor Ambiental / Acción</th>`;
  for (const acc of LEO_ACCIONES) html += `<th>${acc}</th>`;
  html += `</tr></thead><tbody>`;
  for (let r = 0; r < LEO_FACTORES.length; r++) {
    html += `<tr><td>${LEO_FACTORES[r]}</td>`;
    for (let c = 0; c < LEO_ACCIONES.length; c++) {
      const cell = leoData[r][c];
      html += `<td id="leo-td-${r}-${c}">
        <div id="leo-sc-${r}-${c}" class="leo-cell-score">0</div>
        <div class="leo-mini-lbl"><span>M:</span><span id="leo-mv-${r}-${c}">${cell.m}</span></div>
        <input class="leo-mini-rng" type="range" min="-10" max="10" step="1" value="${cell.m}" oninput="updateLeoCell(${r},${c},'m',this.value)"/>
        <div class="leo-mini-lbl"><span>I:</span><span id="leo-iv-${r}-${c}">${cell.i}</span></div>
        <input class="leo-mini-rng" type="range" min="1" max="10" step="1" value="${cell.i}" oninput="updateLeoCell(${r},${c},'i',this.value)"/>
      </td>`;
    }
    html += `</tr>`;
  }
  html += `</tbody></table>`;
  wrap.innerHTML = html;
  leoBuilt = true;
}
function refreshLeopoldVisual() {
  let tot = 0, pos = 0, neg = 0;
  for (let r = 0; r < LEO_FACTORES.length; r++) {
    for (let c = 0; c < LEO_ACCIONES.length; c++) {
      const cell = leoData[r][c];
      const sc = cell.m * cell.i;
      tot += sc;
      if (sc > 0) pos += sc; else neg += sc;
      const td = document.getElementById(`leo-td-${r}-${c}`);
      const scEl = document.getElementById(`leo-sc-${r}-${c}`);
      document.getElementById(`leo-mv-${r}-${c}`).textContent = (cell.m > 0 ? "+" : "") + cell.m;
      document.getElementById(`leo-iv-${r}-${c}`).textContent = cell.i;
      scEl.textContent = (sc > 0 ? "+" : "") + sc;
      if (sc > 0) {
        const a = Math.min(0.45, 0.08 + (sc / 100) * 0.45);
        td.style.background = `rgba(22,163,74,${a.toFixed(2)})`;
        scEl.style.color = "#14532D";
      } else if (sc < 0) {
        const a = Math.min(0.45, 0.08 + (Math.abs(sc) / 100) * 0.45);
        td.style.background = `rgba(220,38,38,${a.toFixed(2)})`;
        scEl.style.color = "#7F1D1D";
      } else {
        td.style.background = "#FFFFFF";
        scEl.style.color = "#475569";
      }
    }
  }
  document.getElementById("leo-k-tot").textContent = (tot > 0 ? "+" : "") + tot;
  document.getElementById("leo-k-diag").textContent = tot >= 0 ? "Balance Ambiental Favorable" : "Impacto Negativo — Exige Mitigación";
  document.getElementById("leo-k-pos").textContent = "+" + pos;
  document.getElementById("leo-k-neg").textContent = "" + neg;
}
function drawAmbiental() {
  if (!leoBuilt) buildLeopoldTable();
  refreshLeopoldVisual();

  const vis = +document.getElementById("amb-vis").value;
  const hrs = +document.getElementById("amb-hrs").value;
  const gas = +document.getElementById("amb-gas").value;
  const co2 = +document.getElementById("amb-co2").value;
  const ch4 = +document.getElementById("amb-ch4").value;
  const n2o = +document.getElementById("amb-n2o").value;

  document.getElementById("amb-vis-v").textContent = fmtInt(vis);
  document.getElementById("amb-hrs-v").textContent = fmtDec(hrs, 2) + " h";
  document.getElementById("amb-gas-v").textContent = "$" + fmtInt(gas);
  document.getElementById("amb-co2-v").textContent = fmtInt(co2) + " t";
  document.getElementById("amb-ch4-v").textContent = fmtDec(ch4, 1) + " t";
  document.getElementById("amb-n2o-v").textContent = fmtDec(n2o, 1) + " t";

  const valRec = vis * (hrs * 2792 + gas);
  const co2Eq = co2 + 28 * ch4 + 265 * n2o;
  const valGei = co2Eq * 71801;
  const valTot = valRec + valGei;

  document.getElementById("amb-k-val").textContent = `$${fmtDec(valTot / 1e6, 1)} MM`;
  document.getElementById("amb-k-sub").textContent = `MCV $${fmtDec(valRec / 1e6, 1)}M + GEI $${fmtDec(valGei / 1e6, 1)}M`;
  document.getElementById("amb-sol").innerHTML =
    `<b>Costo de Viaje (MCV):</b> ${fmtInt(vis)} visitas × (${fmtDec(hrs,2)}h × $2.792 + $${fmtInt(gas)}) = <b>$${fmtInt(valRec)}/año</b> | ` +
    `<b>Carbono Equivalente (IPCC):</b> ${fmtInt(co2)} + 28·(${fmtDec(ch4,1)}) + 265·(${fmtDec(n2o,1)}) = <b>${fmtDec(co2Eq,1)} t CO<sub>2</sub>eq</b> × $71.801 = <b>$${fmtInt(valGei)}/año</b>`;

  renderFormulaStrip("amb-fstrip", [
    {
      lbl: "Valoración Recreativa — Costo de Viaje (MCV)", col: "#1D4ED8",
      eq: `MCV = <span class="sym-b">Vis</span> · (<span class="sym-t">h</span> · $2.792 + <span class="sym-o">Gasto</span>)`,
      sub: `MCV = ${eChip(fmtInt(vis),vis,"amb_vis","500","vc-b","Visitas anuales")} · (${eChip(fmtDec(hrs,2)+"h",hrs,"amb_hrs","0.25","vc-t","Horas viaje (VST=$2.792/h)")} · $2.792 + ${eChip("$"+fmtInt(gas),gas,"amb_gas","250","vc-o","Gasto directo viaje ($)")}) = ${rChip("$"+fmtDec(valRec/1e6,2)+"M")}`,
      note: `Valor unitario por visita = $${fmtInt(hrs*2792 + gas)}`
    },
    {
      lbl: "Carbono Equivalente IPCC (100 Años)", col: "#15803D",
      eq: `CO<sub>2</sub>eq = <span class="sym-b">CO<sub>2</sub></span> + 28·<span class="sym-t">CH<sub>4</sub></span> + 265·<span class="sym-p">N<sub>2</sub>O</span>`,
      sub: `CO<sub>2</sub>eq = ${eChip(fmtInt(co2)+"t",co2,"amb_co2","10","vc-b","CO2 directo (t/año)")} + 28·${eChip(fmtDec(ch4,1)+"t",ch4,"amb_ch4","0.5","vc-t","Metano CH4 (t/año)")} + 265·${eChip(fmtDec(n2o,1)+"t",n2o,"amb_n2o","0.1","vc-p","Óxido nitroso N2O (t/año)")} = ${rChip(fmtDec(co2Eq,1)+" t")}`,
      note: `A Precio Social del Carbono 2026 ($71.801/t) = <b>$${fmtDec(valGei/1e6,2)} MM/año</b>`
    },
    {
      lbl: "Beneficio Ambiental Anual Total (RA2)", col: "#7C3AED",
      eq: `B<sub>amb</sub> = MCV + CO<sub>2</sub>eq · $71.801`,
      sub: `B<sub>amb</sub> = ${vChip("$"+fmtDec(valRec/1e6,2)+"M","vc-b","MCV Recreación")} + ${vChip("$"+fmtDec(valGei/1e6,2)+"M","vc-g","GEI Carbono")} = ${rChip("$"+fmtDec(valTot/1e6,2)+" MM/año")}`,
      note: `Clic en cualquier cápsula punteada para simular otro escenario`
    }
  ]);
  renderPedBox("ped-ambiental",
    `La valoración económica ambiental alcanza <b>$${fmtDec(valTot/1e6,1)} MM/año</b> (<b>$${fmtDec(valRec/1e6,1)}M</b> por recreación MCV y <b>$${fmtDec(valGei/1e6,1)}M</b> por <b>${fmtDec(co2Eq,1)} t CO<sub>2</sub>eq</b> evitadas a $71.801/t).`,
    `<b>¿Por qué 1 tonelada de metano vale 28 veces más que 1 tonelada de CO<sub>2</sub>?</b> Porque el CH<sub>4</sub> atrapa mucho más calor en la atmósfera en un horizonte de 100 años (y el N<sub>2</sub>O ¡265 veces más!). Por eso evitar que materia orgánica o cartón se pudra en un vertedero tiene un impacto climático desproporcionadamente alto.`,
    `Recuerda para <b>RA2 / Ley 19.300</b>: en Leopold la <b>Magnitud</b> lleva signo (+ o −) y la <b>Importancia</b> siempre es positiva (1 a 10). Si se activa cualquier causal del <b>art. 11</b>, el proyecto entra al SEIA como <b>EIA</b> y no como simple DIA.`
  );
}

// ============================================================================
// 9. ÁRBOLES CAUSALES (PROBLEMAS <-> OBJETIVOS) + QUIZ V/F PROCESO 2 RA1
// ============================================================================
const CASOS_ARBOL = [
  {
    prob: "Deficiente gestión en organización y logística\npara la comercialización externa de berries",
    obj: "Eficiente gestión en organización y logística\npara la comercialización externa de berries",
    c1: ["Ausencia de asociatividad\ny cooperación sectorial", "Baja capacidad instalada y\nbajo valor agregado", "Ineficiente distribución y\ndesconocimiento de exportación"],
    e1: ["Sin iniciativas de exportación\nni estándares externos", "Bajo nivel competitivo de\npequeños productores", "Escasa participación en\nmercado internacional"],
    m1: ["Asociatividad activa y\ncooperación sectorial", "Mayor capacidad instalada y\nproductos con valor agregado", "Cadenas de distribución y\ndominio logístico exportador"],
    f1: ["Iniciativas de exportación\nestandarizadas y activas", "Mejora sustantiva del nivel\ncompetitivo local", "Mayor participación en el\nmercado internacional"],
    alt: "Alternativa óptima: Centro de Apoyo a Productores de Berries con cooperativa, capacitación en TLC/logística y giras tecnológicas."
  },
  {
    prob: "Altas tasas de malnutrición y déficit proteico\nen adultos mayores vulnerables de la comuna",
    obj: "Adecuado estado nutricional y bienestar integral\nen adultos mayores vulnerables de la comuna",
    c1: ["Ingresos insuficientes para\ncanasta alimentaria adecuada", "Desconocimiento nutricional\nde cuidadores y familias", "Baja cobertura de control\nnutricional preventivo"],
    e1: ["Mayor morbilidad crónica y\nhospitalizaciones evitables", "Pérdida de autonomía física\ny deterioro cognitivo", "Mayor gasto público en\natención de urgencia"],
    m1: ["Entrega mensual focalizada\nde suplementos nutricionales", "Talleres educativos para\nadultos mayores y cuidadores", "Control periódico de salud\ny seguimiento nutricional"],
    f1: ["Disminución de morbilidad\ny hospitalizaciones evitables", "Preservación de autonomía y\ncalidad de vida", "Uso eficiente del presupuesto\nde salud comunal"],
    alt: "Regla MML: Un único Propósito (mejora nutricional); indicadores de Eficacia, Eficiencia, Calidad y Economía; sin supuestos en Actividades."
  },
  {
    prob: "Elevada tasa de ausentismo y atrasos laborales\nen planta industrial periférica",
    obj: "Reducción sostenida del ausentismo y atrasos\nlaborales en planta industrial periférica",
    c1: ["Baja frecuencia de transporte\npúblico en horarios de turno", "Largos tiempos de espera y\ncaminata expuestos a lluvia", "Falta de coordinación de\nhorarios de ingreso"],
    e1: ["Pérdida de horas productivas\ny paradas de línea", "Aumento de rotación de\npersonal capacitado", "Caída en calidad de vida y\ningreso del trabajador"],
    m1: ["Servicio de buses de\nacercamiento por turno", "Paraderos protegidos y\nrutas optimizadas", "Turnos sincronizados con\ntransporte contratado"],
    f1: ["Continuidad operacional y\nmayor productividad", "Retención de mano de obra\nsemicalificada (MOSC 0,95)", "Ahorro de Tiempo Social\n(VST 1x $3.338 / 2x $6.676)"],
    alt: "Clave de examen (Proceso2 RA1): Los choferes de buses son MOSC = 0,95 (NO MONC) y el ahorro de espera/caminata se valora al doble (2x)."
  }
];

let arbCasoIdx = 0;
let arbEsPositivo = false;

function setCasoArbol(idx, btn) {
  arbCasoIdx = idx;
  btn.parentElement.querySelectorAll(".flt-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  drawArbol();
}
function setModoArbol(esPos) {
  arbEsPositivo = esPos;
  document.getElementById("arb-btn-prob").classList.toggle("primary", !esPos);
  document.getElementById("arb-btn-obj").classList.toggle("primary", esPos);
  drawArbol();
}
function drawArbol() {
  const c = CASOS_ARBOL[arbCasoIdx];
  const svg = document.getElementById("svg-arbol");
  if (!svg) return;
  svg.innerHTML = "";
  const pos = arbEsPositivo;

  const colTopBg = pos ? "#DCFCE7" : "#FEE2E2", colTopBd = pos ? "#15803D" : "#DC2626";
  const colMidBg = pos ? "#15803D" : "#B91C1C";
  const colBotBg = pos ? "#DBEAFE" : "#FEF3C7", colBotBd = pos ? "#1D4ED8" : "#D97706";

  const drawBox = (xc, yc, w, h, text, bg, bd, txtCol="#0F172A", bold=false) => {
    el("rect", { x: xc - w / 2, y: yc - h / 2, width: w, height: h, rx: 7, fill: bg, stroke: bd, "stroke-width": "1.8" }, svg);
    const lines = text.split("\n");
    lines.forEach((ln, k) => {
      const yOff = (k - (lines.length - 1) / 2) * 15;
      const t = el("text", { x: xc, y: yc + yOff + 4, fill: txtCol, "font-size": "11.5", "font-weight": bold ? "800" : "700", "text-anchor": "middle" }, svg);
      t.textContent = ln;
    });
  };

  // Conectores ortogonales limpios
  const xs = [175, 480, 785];
  el("line", { x1: 175, y1: 120, x2: 785, y2: 120, stroke: "#64748B", "stroke-width": "1.8" }, svg);
  el("line", { x1: 175, y1: 245, x2: 785, y2: 245, stroke: "#64748B", "stroke-width": "1.8" }, svg);
  el("line", { x1: 480, y1: 120, x2: 480, y2: 146, stroke: "#64748B", "stroke-width": "2" }, svg);
  el("line", { x1: 480, y1: 218, x2: 480, y2: 245, stroke: "#64748B", "stroke-width": "2" }, svg);
  xs.forEach(x => {
    el("line", { x1: x, y1: 96, x2: x, y2: 120, stroke: "#64748B", "stroke-width": "1.8" }, svg);
    el("line", { x1: x, y1: 245, x2: x, y2: 270, stroke: "#64748B", "stroke-width": "1.8" }, svg);
  });

  // Etiquetas de nivel a la izquierda
  const mkLbl = (y, txt, col) => {
    const t = el("text", { x: 18, y, fill: col, "font-size": "10.5", "font-weight": "800" }, svg);
    t.textContent = txt;
  };
  mkLbl(24, pos ? "FINES (ARRIBA)" : "EFECTOS (ARRIBA)", colTopBd);
  mkLbl(356, pos ? "MEDIOS (ABAJO)" : "CAUSAS (ABAJO)", colBotBd);

  const topArr = pos ? c.f1 : c.e1;
  const botArr = pos ? c.m1 : c.c1;
  xs.forEach((x, i) => {
    drawBox(x, 62, 265, 66, topArr[i], colTopBg, colTopBd);
    drawBox(x, 304, 265, 66, botArr[i], colBotBg, colBotBd);
  });
  drawBox(480, 182, 540, 72, pos ? c.obj : c.prob, colMidBg, "#0F172A", "#FFFFFF", true);

  document.getElementById("arb-alt-box").innerHTML = `<b>Criterio Metodológico SNI:</b> ${c.alt}`;

  renderPedBox("ped-arbol",
    `Estás visualizando el <b>${pos ? "Árbol de Objetivos (estados positivos alcanzables)" : "Árbol de Problemas (relaciones causa-efecto negativas)"}</b> del caso seleccionado. Cada causa de la base se convierte en un medio concreto de intervención al invertir el árbol.`,
    `<b>La Trampa del "Falta un...":</b> redactar un problema como "falta un camión" o "falta una planta" es el error más castigado en CEPAL N° 39, porque disfraza una única solución como si fuera el problema e impide comparar alternativas más baratas o eficientes.`,
    `Al pasar del Árbol de Objetivos a la <b>Matriz de Marco Lógico (MML 4×4)</b>: el tronco pasa a ser el <b>Propósito único</b>, las ramas superiores nutren el <b>Fin</b> y las raíces se convierten en <b>Componentes y Actividades</b> (recordando que en Actividades no se redactan supuestos).`
  );
}

const QUIZ_VF_DATA = [
  { n: 1, q: "El principio de proporcionalidad establece que el alcance y detalle del análisis deben guardar relación con la complejidad, magnitud y costo de la iniciativa.", ans: "V", why: "Verdadero (Metodología General SNI 2025, cap. II.1.3)." },
  { n: 2, q: "Un perfil que postula a ejecución solicita recursos para el diseño de la inversión.", ans: "F", why: "Falso: Un proyecto que postula a ejecución solicita financiar las obras; el diseño ya existe." },
  { n: 8, q: "En la mayoría de los casos no hay diferencia entre los conceptos externalidad y efectos indirectos.", ans: "F", why: "Falso: Externalidades recaen sobre terceros fuera del mercado directo; efectos indirectos ocurren en mercados sustitutos o complementarios." },
  { n: 9, q: "Cuando dos alternativas difieren en su nivel de producción con beneficio unitario equivalente, la selección proviene del CAE por producto o solución entregada.", ans: "V", why: "Verdadero: Criterio Costo-Eficiencia por unidad producida o tonelada dispuesta." },
  { n: 11, q: "Es más conveniente cuando los terrenos son de propiedad del municipio, dado que el costo de inversión se reduce en lo que cuesta el terreno.", ans: "F", why: "Falso: Los terrenos públicos o municipales siempre deben valorarse a su costo de oportunidad social." },
  { n: 13, q: "En un Marco Lógico, a nivel de actividades no se definen supuestos.", ans: "V", why: "Verdadero: Los supuestos se definen en Actividades→Componentes, Componentes→Propósito y Propósito→Fin." },
  { n: 14, q: "La obtención de un RS (Recomendado Satisfactoriamente) significa que el proyecto se realizará.", ans: "F", why: "Falso: El RS acredita viabilidad técnico-económica, pero no garantiza priorización ni asignación presupuestaria." },
  { n: 15, q: "El precio social de la mano de obra es siempre menor o igual que su precio privado.", ans: "V", why: "Verdadero: FCSMO 2026 = 0,97 (MOC), 0,95 (MOSC) y 0,91 (MONC)." },
];
let vfAnswers = {};

function renderQuizVF() {
  const wrap = document.getElementById("vf-list");
  if (!wrap) return;
  wrap.innerHTML = "";
  let okCount = 0;
  QUIZ_VF_DATA.forEach((item, idx) => {
    const userAns = vfAnswers[idx];
    const isAnswered = userAns !== undefined;
    const isOk = isAnswered && userAns === item.ans;
    if (isOk) okCount++;
    const card = document.createElement("div");
    card.className = "vf-card" + (isAnswered ? (" answered " + (isOk ? "ok" : "bad")) : "");
    card.innerHTML = `
      <div class="vf-q">P.${item.n}: ${item.q}</div>
      <div class="vf-btns">
        <button class="vf-btn" onclick="responderVF(${idx}, 'V')" style="${userAns==='V'?'background:#0F172A;color:#FFF;':''}">Verdadero (V)</button>
        <button class="vf-btn" onclick="responderVF(${idx}, 'F')" style="${userAns==='F'?'background:#0F172A;color:#FFF;':''}">Falso (F)</button>
        ${isAnswered ? `<span style="font-size:11.5px;font-weight:800;color:${isOk?'#15803D':'#DC2626'};">${isOk ? '✓ Correcto' : '✗ Incorrecto (Era ' + item.ans + ')'}</span>` : ''}
      </div>
      <div class="vf-fb"><b>Justificación oficial:</b> ${item.why}</div>`;
    wrap.appendChild(card);
  });
  document.getElementById("vf-score").textContent = `Puntaje: ${okCount} / ${QUIZ_VF_DATA.length}`;
}
function responderVF(idx, ans) {
  vfAnswers[idx] = ans;
  renderQuizVF();
}
function resetQuizVF() {
  vfAnswers = {};
  renderQuizVF();
}

drawLeche();
drawTransporte();
drawWaterfall();
drawHorno();
drawHundido();
drawAgua();
drawTeaCapm();
drawAmbiental();
drawArbol();

// ============================================================================
// 10. MAPA CAUSAL INTEGRADO, LECTURA EN 3 CAPAS Y QUIZ CRUZADO (FDIC26 / SNI)
// ============================================================================
const MAPA_PILARES = {
  P1: {
    id: "P1", x: 135, y: 95, w: 215, h: 76, col: "#1D4ED8",
    lbl: "P1. BIENESTAR Y VSP",
    sub: "Fontaine · Demanda y Oferta\nVSP · Distorsiones · Externalidades",
    explica: "Establece el fundamento económico de la evaluación social: los beneficios sociales se miden por la disposición a pagar bajo la curva de demanda (VSP) y los costos sociales por los recursos reales liberados bajo la curva de oferta (CMgS), distinguiendo precios privados de precios sombra cuando hay impuestos, subsidios, monopolio o externalidades.",
    puentes: "<b>→ Hacia P3 (SNI 2026):</b> las distorsiones en mercados de insumos y productos explican por qué el MDSF publica factores de corrección (MO, Divisa, VST) y elimina IVA/transferencias. <b>→ Hacia P4 (Ambiental):</b> la brecha entre CMgP y CMgS formaliza las externalidades negativas (emisiones, ruido, residuos).",
    jumps: [["leche", "Abrir Leche y VSP"], ["transporte", "Abrir Transporte/Externalidades"], ["elasticidad", "Abrir Elasticidades Extremas"]]
  },
  P2: {
    id: "P2", x: 490, y: 78, w: 220, h: 76, col: "#0F766E",
    lbl: "P2. FLUJOS Y TASA",
    sub: "Con vs. Sin Proyecto · Hundidos\nHorno Pan · TEA · CAPM · VAN",
    explica: "Define la arquitectura del flujo de caja incremental: se evalúa únicamente la diferencia entre la Situación Con Proyecto y la Situación Base Optimizada (Sin Proyecto), excluyendo costos hundidos, incorporando valor residual y descontando a una tasa coherente con el riesgo (CAPM / TEA) antes de pasar a la tasa social.",
    puentes: "<b>← Desde P5 (Marco Lógico):</b> los Componentes y Actividades del proyecto definen el calendario de inversión y OPEX del flujo. <b>→ Hacia P3 (SNI):</b> el flujo privado (VANP) es el punto de partida exacto del Puente Waterfall hacia el flujo social (VANS).",
    jumps: [["horno", "Abrir Horno y Costos Hundidos"], ["agua", "Abrir Agua 10 Años + TEA/CAPM"]]
  },
  P3: {
    id: "P3", x: 845, y: 95, w: 215, h: 76, col: "#B91C1C",
    lbl: "P3. PRECIOS SOCIALES SNI",
    sub: "MDSF 2026 · TSD 5,5% · MO/FCSD\nPuente VANP → VANS · 4 Cuadrantes",
    explica: "Aplica los parámetros oficiales del Sistema Nacional de Inversiones (MDSF, marzo 2026): corrige mano de obra (MOC 0,97 · MOSC 0,95 · MONC 0,91), divisa (FCSD 1,00), elimina transferencias (IVA/impuestos), valoriza ahorros de tiempo (VST) y carbono ($71.801/t CO2eq) y descuenta a la TSD de 5,5% para decidir en el Semáforo de 4 Cuadrantes.",
    puentes: "<b>← Desde P1 y P2:</b> traduce las distorsiones teóricas y el flujo privado en el VANS oficial. <b>← Desde P4:</b> internaliza los impactos ambientales valorizados en dinero dentro del flujo social.",
    jumps: [["waterfall", "Abrir Puente SNI + Radar Quiebre"], ["mecanica", "Ver Tabla Precios SNI 2026"]]
  },
  P4: {
    id: "P4", x: 300, y: 248, w: 235, h: 76, col: "#15803D",
    lbl: "P4. AMBIENTAL RA2 / SEIA",
    sub: "Barzev (VET) · Matriz de Leopold\nGEI (CO2eq) · Ley 19.300 (DIA/EIA)",
    explica: "Identifica, pondera y valoriza los impactos socioambientales: utiliza la Matriz de Leopold (Magnitud ±1..10 × Importancia 1..10), distingue Valor Económico Total (Uso + No Uso), convierte gases a t CO2eq (CH4 × 28, N2O × 265) y determina la vía de ingreso al SEIA (DIA vs. EIA según art. 11 Ley 19.300).",
    puentes: "<b>→ Hacia P3 (SNI 2026):</b> cada tonelada evitada o emitida de CO2eq entra al Puente Waterfall multiplicada por $71.801/t CO2eq. <b>→ Hacia P5 (MML):</b> las medidas de mitigación/compensación pasan a ser Actividades y Supuestos obligatorios en la Matriz de Marco Lógico.",
    jumps: [["ambiental", "Abrir Ambiental RA2 (Leopold + GEI)"], ["waterfall", "Ver Impacto en VANS"]]
  },
  P5: {
    id: "P5", x: 685, y: 248, w: 235, h: 76, col: "#7C3AED",
    lbl: "P5. MARCO LÓGICO CEPAL 39",
    sub: "Ortegón, Pacheco y Prieto\nÁrboles Causales · MML 4×4",
    explica: "Asegura coherencia entre el diagnóstico del territorio y el diseño del proyecto: transforma causas y efectos del Árbol de Problemas en medios y fines del Árbol de Objetivos, estructurando la Matriz de Marco Lógico (Fin, Propósito, Componentes, Actividades) con indicadores verificables, medios de verificación y supuestos críticos.",
    puentes: "<b>→ Hacia P2 (Flujos):</b> las Actividades y Componentes definen el presupuesto real de inversión y operación. <b>→ Hacia P3 (SNI):</b> evita diseñar proyectos sin demanda o mal formulados (sin pertinencia SNI no existe RS aunque el VANS parezca alto).",
    jumps: [["arboles", "Abrir Árboles Causales + Quiz V/F"], ["mecanica", "Abrir Hoja Mecánica"]]
  }
};

const MAPA_PROY_EDGES = [
  { a: "P1", b: "P3", lbl: "Precios Sombra" },
  { a: "P2", b: "P3", lbl: "Puente VANP→VANS" },
  { a: "P1", b: "P4", lbl: "CMgS vs CMgP" },
  { a: "P4", b: "P3", lbl: "GEI × $71.801/t" },
  { a: "P5", b: "P2", lbl: "Activid. → CAPEX" },
  { a: "P5", b: "P3", lbl: "Pertinencia RS" },
  { a: "P4", b: "P5", lbl: "Mitigación MML" },
  { a: "P1", b: "P2", lbl: "Incrementalidad" }
];

const ESCENARIOS_PROY = {
  subsidio: {
    titulo: "Cadena A: Proyecto Socialmente Rentable pero Privadamente Negativo (VANP < 0 y VANS > 0)",
    nodes: ["P1", "P2", "P3"],
    edges: [["P1", "P3"], ["P2", "P3"], ["P1", "P2"]],
    texto: "<b>1) En P2 (Flujo Privado):</b> el privado paga IVA, salarios brutos, descuenta a una tasa privada alta (ej. 12%) y no cobra por beneficios externos, arrojando <b>VANP &lt; 0</b>. " +
           "<b>2) En P1 y P3 (Corrección SNI 2026):</b> al descontar a la <b>TSD = 5,5%</b>, ajustar mano de obra (0,91–0,97), descontar impuestos/transferencias y sumar ahorros de tiempo o beneficios ambientales, el flujo social salta a <b>VANS &gt; 0</b> (ej. caso Cartón Vivo Osorno: VANS $154,99 MM). " +
           "<b>3) Decisión de Política Pública (Cuadrante II):</b> el Estado debe subsidiar hasta el monto mínimo que vuelva viable al privado, siempre que el subsidio sea menor que el VANS.",
    jumps: [["waterfall", "Ver Puente Waterfall VANP→VANS"], ["transporte", "Probar Externalidades"]]
  },
  ambiental: {
    titulo: "Cadena B: De la Externalidad Ambiental (Leopold + GEI) al VANS Oficial",
    nodes: ["P1", "P4", "P3"],
    edges: [["P1", "P4"], ["P4", "P3"], ["P1", "P3"]],
    texto: "<b>1) En P1 (Bienestar):</b> una externalidad existe cuando el Costo Marginal Social (CMgS) difiere del Costo Marginal Privado (CMgP). " +
           "<b>2) En P4 (RA2 / Barzev / Leopold):</b> se evalúan los impactos por componente (Magnitud × Importancia) y se convierten las emisiones evitadas o generadas a toneladas equivalentes (CH<sub>4</sub> × 28; N<sub>2</sub>O × 265). " +
           "<b>3) En P3 (SNI 2026):</b> esas toneladas se multiplican por el Precio Social del Carbono (<b>$71.801/t CO<sub>2</sub>eq</b>) y se descuentan al 5,5% para reflejar el beneficio o daño ambiental real en el VANS.",
    jumps: [["ambiental", "Probar Leopold + GEI"], ["waterfall", "Ver Impacto en VANS"]]
  },
  marco: {
    titulo: "Cadena C: Del Diagnóstico del Problema (CEPAL 39) a la Decisión SNI",
    nodes: ["P5", "P2", "P3"],
    edges: [["P5", "P2"], ["P2", "P3"], ["P5", "P3"]],
    texto: "<b>1) En P5 (Marco Lógico):</b> se identifica un problema real en el territorio (nunca redactado como 'falta de solución'), sus causas-raíz y alternativas técnicas. " +
           "<b>2) En P2 (Flujo Incremental):</b> cada Componente y Actividad se costea comparando Situación Con Proyecto vs. Situación Base Optimizada, sin incluir costos hundidos. " +
           "<b>3) En P3 (Evaluación SNI):</b> se corrigen precios a valores sociales y se somete a análisis de sensibilidad (Radar de Quiebre) para asegurar robustez antes de postular a RS.",
    jumps: [["arboles", "Abrir Árboles Causales"], ["horno", "Repasar Costos Hundidos"]]
  }
};

let proyPilarActivo = "P1";
let proyEscenarioKey = null;

function selectPilarProy(pKey) {
  proyEscenarioKey = null;
  proyPilarActivo = pKey;
  drawMapaProy();
}
function activarEscenarioProy(eKey) {
  proyEscenarioKey = eKey;
  drawMapaProy();
}
function drawMapaProy() {
  const svg = document.getElementById("svg-mapa-proy");
  const box = document.getElementById("mapa-proy-detail");
  if (!svg || !box) return;
  svg.innerHTML = "";
  addDefs(svg);

  const esc = proyEscenarioKey ? ESCENARIOS_PROY[proyEscenarioKey] : null;
  const activeNodes = new Set(esc ? esc.nodes : [proyPilarActivo]);

  MAPA_PROY_EDGES.forEach(ed => {
    const na = MAPA_PILARES[ed.a], nb = MAPA_PILARES[ed.b];
    let isHot = false;
    if (esc) {
      isHot = esc.edges.some(([x, y]) => (x === ed.a && y === ed.b) || (x === ed.b && y === ed.a));
    } else {
      isHot = (ed.a === proyPilarActivo || ed.b === proyPilarActivo);
    }
    const dx = nb.x - na.x, dy = nb.y - na.y, dist = Math.hypot(dx, dy) || 1;
    const x1 = na.x + (dx / dist) * 60, y1 = na.y + (dy / dist) * 34;
    const x2 = nb.x - (dx / dist) * 64, y2 = nb.y - (dy / dist) * 36;

    el("line", {
      x1, y1, x2, y2,
      stroke: isHot ? "#DC2626" : "#CBD5E1",
      "stroke-width": isHot ? "2.8" : "1.5",
      "stroke-dasharray": isHot ? "" : "4,3",
      "marker-end": isHot ? "url(#arr-red)" : ""
    }, svg);

    if (isHot) {
      const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
      const bw = Math.max(76, ed.lbl.length * 6.2 + 10);
      el("rect", { x: mx - bw / 2, y: my - 9, width: bw, height: 16, rx: 4, fill: "#FFFFFF", stroke: "#DC2626", "stroke-width": "1" }, svg);
      const tl = el("text", { x: mx, y: my + 3, fill: "#991B1B", "font-size": "9.8", "font-weight": "700", "text-anchor": "middle" }, svg);
      tl.textContent = ed.lbl;
    }
  });

  Object.values(MAPA_PILARES).forEach(nd => {
    const isSel = activeNodes.has(nd.id);
    const g = el("g", { style: "cursor:pointer;", onclick: `selectPilarProy('${nd.id}')` }, svg);
    el("rect", {
      x: nd.x - nd.w / 2, y: nd.y - nd.h / 2, width: nd.w, height: nd.h, rx: 9,
      fill: isSel ? nd.col : "#FFFFFF",
      stroke: isSel ? "#0F172A" : nd.col,
      "stroke-width": isSel ? "2.6" : "1.8",
      opacity: esc && !isSel ? "0.45" : "1"
    }, g);

    const t1 = el("text", { x: nd.x, y: nd.y - 13, fill: isSel ? "#FFFFFF" : nd.col, "font-size": "11.5", "font-weight": "800", "text-anchor": "middle" }, g);
    t1.textContent = nd.lbl;
    nd.sub.split("\n").forEach((ln, k) => {
      const ts = el("text", { x: nd.x, y: nd.y + 6 + k * 14, fill: isSel ? "#F1F5F9" : "#334155", "font-size": "10", "font-weight": "600", "text-anchor": "middle" }, g);
      ts.textContent = ln;
    });
  });

  if (esc) {
    const btnsHtml = esc.jumps.map(([tb, lbl]) => `<button class="jump-btn" onclick="jumpToTab('${tb}')">${lbl} →</button>`).join(" ");
    box.innerHTML = `
      <div class="map-detail-head">
        <span class="map-detail-title">${esc.titulo}</span>
        <div class="btn-bar">${btnsHtml}</div>
      </div>
      <div>${esc.texto}</div>`;
  } else {
    const p = MAPA_PILARES[proyPilarActivo];
    const btnsHtml = p.jumps.map(([tb, lbl]) => `<button class="jump-btn" onclick="jumpToTab('${tb}')">${lbl} →</button>`).join(" ");
    box.innerHTML = `
      <div class="map-detail-head">
        <span class="map-detail-title">${p.lbl} (Haz clic en cualquier otro pilar del diagrama para cambiar el foco)</span>
        <div class="btn-bar">${btnsHtml}</div>
      </div>
      <div><b>Lógica central:</b> ${p.explica}</div>
      <div style="margin-top:5px;"><b>Interrelación con el resto del ramo:</b> ${p.puentes}</div>`;
  }
}

const FICHAS_PROY = [
  {
    unit: "P1", src: "Ernesto Fontaine — Evaluación Social de Proyectos (Caps. 1–4)",
    title: "1. Microeconomía del Bienestar: VSP, Excedentes, Distorsiones y Elasticidades",
    core: "<b>Idea central:</b> El beneficio social de producir más unidades (ΔQ) no es simplemente P·ΔQ, sino la suma del <b>Valor Social del mayor consumo</b> (área bajo la curva de demanda entre Q<sub>0</sub> y Q<sub>1</sub>) más los <b>recursos liberados</b> por otros productores que dejan de producir (área bajo la curva de oferta). En mercados con impuestos, subsidios o monopolio, el precio de mercado se separa del precio sombra.",
    bridge: "<b>Puente entre pilares:</b> Fundamenta por qué en P3 (SNI) se ajustan los precios de mercado con factores de corrección y por qué en los ejercicios de Leche y Transporte se miden trapecios bajo Demanda y Oferta.",
    trap: "<b>Trampas de prueba:</b> (1) Si la oferta es <i>perfectamente inelástica</i> (vertical), toda la nueva producción se convierte en mayor consumo y el VSP se calcula solo bajo la Demanda. (2) Si la demanda es <i>perfectamente inelástica</i>, todo el proyecto sustituye producción existente y el beneficio son solo los costos liberados bajo la Oferta."
  },
  {
    unit: "P2", src: "Ernesto Fontaine · Brealey & Myers (TEA / CAPM / Flujos)",
    title: "2. Flujos Incrementales, Costos Hundidos (Horno de Pan), TEA y CAPM",
    core: "<b>Idea central:</b> Todo proyecto se evalúa en forma <b>incremental</b> (Con Proyecto menos Situación Base Optimizada). Los <b>costos hundidos</b> (gastos ya incurridos e irrecuperables, como un estudio previo o una maquinaria vieja sin valor de reventa) jamás entran en la decisión; sí entra el <b>costo de oportunidad</b> (ej. lo que podría venderse hoy del equipo actual). La tasa debe coincidir con la periodicidad del flujo (TEA) y reflejar el riesgo sistemático (CAPM).",
    bridge: "<b>Puente entre pilares:</b> El flujo incremental privado bien armado es el insumo exacto que entra al Puente Waterfall (P3) para corregir hacia precios sociales.",
    trap: "<b>Trampas de prueba:</b> (1) En el clásico 'Horno de Pan', el precio pagado hace años por el horno antiguo es costo hundido, pero su <i>valor comercial de venta hoy</i> sí es relevante como costo de oportunidad. (2) Confundir tasa nominal con TEA o descontar flujos reales con tasas nominales con inflación."
  },
  {
    unit: "P3", src: "MDSF — Precios Sociales Vigentes SNI 2026 (31 mar 2026)",
    title: "3. Parámetros Oficiales SNI 2026: TSD 5,5%, Mano de Obra, Divisa y Transferencias",
    core: "<b>Idea central:</b> Para pasar del flujo privado al flujo social en Chile (SNI 2026) se aplica: <b>TSD = 5,5%</b>; corrección de mano de obra (<b>MOC = 0,97</b>, <b>MOSC = 0,95</b>, <b>MONC = 0,91</b>); <b>FCSD (Divisa) = 1,00</b>; exclusión de <b>IVA e impuestos/subsidios</b> (son transferencias dentro del país, no consumo real de recursos); y precios sociales oficiales para tiempo (VST), combustibles, energía y carbono ($71.801/t CO<sub>2</sub>eq).",
    bridge: "<b>Puente entre pilares:</b> Operacionaliza la teoría de distorsiones de Fontaine (P1) y la valoración ambiental de Barzev (P4) en una sola métrica comparable para el Estado: el <b>VANS</b>.",
    trap: "<b>Trampas de prueba:</b> (1) El IVA y el impuesto a la renta son transferencias privadas-Estado: en evaluación social se excluyen (no son costo ni beneficio social neto). (2) En VST urbano, el tiempo de espera/caminata vale el doble (2x = $6.676/h) que el tiempo en vehículo (1x = $3.338/h)."
  },
  {
    unit: "P3", src: "Semáforo de 4 Cuadrantes · Caso Cartón Vivo Osorno (FDIC26)",
    title: "4. Puente Privado → Social (VANP vs. VANS) y Decisión de Política Pública",
    core: "<b>Idea central:</b> Contrastar VANP y VANS define 4 escenarios: <b>I (+,+)</b> ejecutable sin subsidio; <b>II (−,+)</b> socialmente deseable pero inviable para el privado → justifica <b>subsidio o ejecución pública</b>; <b>III (+,−)</b> privado rentable a costa de dañar a la sociedad → requiere <b>impuesto pigouviano o regulación</b>; <b>IV (−,−)</b> rechazar en ambos planos.",
    bridge: "<b>Puente entre pilares:</b> Une el flujo privado (P2), las externalidades ambientales (P4) y el análisis de sensibilidad (Radar de Quiebre) en una sola recomendación ejecutiva.",
    trap: "<b>Trampas de prueba:</b> En el Cuadrante II (VANP &lt; 0 y VANS &gt; 0, ej. Cartón Vivo Osorno con TSD 5,5% y VANS $154,99 MM), el subsidio estatal máximo justificable nunca puede superar al VANS y debe buscar el mínimo que haga VANP ≥ 0."
  },
  {
    unit: "P4", src: "Radoslav Barzev · Matriz de Leopold · Ley 19.300 (SEIA)",
    title: "5. Evaluación Ambiental RA2: VET, Leopold, Carbono Equivalente y SEIA",
    core: "<b>Idea central:</b> El <b>Valor Económico Total (VET)</b> suma Valor de Uso (directo, indirecto y de opción) + Valor de No Uso (existencia y legado). La <b>Matriz de Leopold</b> cruza acciones del proyecto vs. factores ambientales evaluando <b>Magnitud (±1 a 10)</b> e <b>Importancia (1 a 10)</b>. Las emisiones se homogeneizan a CO<sub>2</sub>eq (CH<sub>4</sub> × 28; N<sub>2</sub>O × 265) y se valorizan a $71.801/t CO<sub>2</sub>eq.",
    bridge: "<b>Puente entre pilares:</b> Transforma el impacto físico sobre aire, agua y suelo en flujos monetarios para el VANS (P3) y en medidas concretas de mitigación/compensación dentro del Marco Lógico (P5).",
    trap: "<b>Trampas de prueba:</b> (1) En el SEIA (Ley 19.300), si un proyecto genera alguno de los efectos del <b>art. 11</b> (riesgo a la salud, efectos adversos significativos sobre recursos renovables, reasentamiento, áreas protegidas, patrimonio), debe ingresar como <b>EIA</b> y no como simple DIA. (2) En Leopold, la Magnitud lleva signo (+ beneficio, − impacto negativo), mientras que la Importancia es siempre positiva (1 a 10)."
  },
  {
    unit: "P5", src: "CEPAL Serie Manuales N° 39 (Ortegón, Pacheco y Prieto)",
    title: "6. Metodología del Marco Lógico: Árboles Causales y Matriz 4×4",
    core: "<b>Idea central:</b> El diagnóstico arranca con el <b>Árbol de Problemas</b> (raíces = causas, tronco = problema central, copa = efectos), se invierte a positivo en el <b>Árbol de Objetivos</b> (medios → objetivo central → fines) y se operacionaliza en la <b>Matriz de Marco Lógico (MML 4×4)</b>: Fin, Propósito, Componentes y Actividades en filas; Resumen Narrativo, Indicadores, Medios de Verificación y Supuestos en columnas.",
    bridge: "<b>Puente entre pilares:</b> Garantiza que el proyecto resuelva un problema real antes de calcular el flujo incremental (P2) y que todas las acciones de mitigación ambiental (P4) tengan responsable y presupuesto.",
    trap: "<b>Trampas de prueba:</b> (1) Error clásico N° 1: redactar el Problema Central como 'falta de una solución' (ej. 'falta de planta de reciclaje') en vez de la brecha real ('alta tasa de disposición de cartón en vertedero'). (2) Lógica Vertical: Actividades + Supuestos ⇒ Componentes ⇒ Propósito ⇒ Fin; Lógica Horizontal: cada objetivo debe tener Indicador verificable y Medio de Verificación."
  }
];

let capaProyActiva = "core";
let filtroProyUnit = "all";

function setCapaProy(capa) {
  capaProyActiva = capa;
  ["core", "bridge", "trap", "all"].forEach(k => {
    const b = document.getElementById("cap-btn-" + k);
    if (b) b.classList.toggle("primary", k === capa);
  });
  renderLecturaProy();
}
function filtrarLecturaProy(unit, btn) {
  filtroProyUnit = unit;
  btn.parentElement.querySelectorAll(".flt-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  renderLecturaProy();
}
function renderLecturaProy() {
  const grid = document.getElementById("lec-proy-grid");
  if (!grid) return;
  grid.innerHTML = "";
  FICHAS_PROY.filter(f => filtroProyUnit === "all" || f.unit === filtroProyUnit).forEach(f => {
    const card = document.createElement("div");
    card.className = "lec-card";
    let layersHtml = "";
    if (capaProyActiva === "core" || capaProyActiva === "all") layersHtml += `<div class="lec-layer l-core">${f.core}</div>`;
    if (capaProyActiva === "bridge" || capaProyActiva === "all") layersHtml += `<div class="lec-layer l-bridge">${f.bridge}</div>`;
    if (capaProyActiva === "trap" || capaProyActiva === "all") layersHtml += `<div class="lec-layer l-trap">${f.trap}</div>`;
    card.innerHTML = `
      <div class="lec-meta"><span class="lec-unit">${f.unit}</span><span class="lec-src">${f.src}</span></div>
      <div class="lec-title">${f.title}</div>
      ${layersHtml}`;
    grid.appendChild(card);
  });
}

const QUIZ_PROY_DATA = [
  {
    tag: "P1 Fontaine",
    q: "En un mercado con oferta perfectamente inelástica (vertical) donde un proyecto estatal introduce nueva producción ΔQ, ¿cómo se mide el Valor Social de la Producción (VSP)?",
    opts: ["Solo por los costos liberados bajo la curva de oferta", "Exclusivamente por el área bajo la curva de demanda entre Q0 y Q1 (todo es mayor consumo)", "Multiplicando ΔQ por el precio con IVA incluido"],
    ans: 1,
    why: "Cuando la oferta existente es perfectamente inelástica (vertical), los antiguos productores no reducen su cantidad ofrecida; por tanto toda la producción del proyecto se destina a nuevo consumo y el VSP equivale al área bajo la demanda (Fontaine)."
  },
  {
    tag: "P2 Hundidos",
    q: "Una empresa pagó $15 millones el año pasado por un estudio de suelos y hoy evalúa si reemplazar o no su horno actual (que compró en $40 millones hace 5 años, pero hoy solo puede vender en $8 millones). ¿Qué monto es relevante en el flujo incremental?",
    opts: ["Solo los $8 millones del valor comercial actual del horno (costo de oportunidad)", "Los $15 millones del estudio más los $40 millones históricos del horno", "Los $40 millones contables porque aún figuran en el balance"],
    ans: 0,
    why: "Tanto el estudio ya pagado ($15M) como el precio histórico de compra ($40M) son costos hundidos irrecuperables. Lo único relevante hoy es el valor de liquidación alternativo ($8M) al que se renuncia o que se recupera al reemplazar el horno."
  },
  {
    tag: "P2 ↔ P3 TSD",
    q: "Al pasar un proyecto de largo plazo (10 años) desde evaluación privada (tasa 12%) a evaluación social SNI 2026 (TSD = 5,5%), ¿qué ocurre con el peso relativo de los flujos netos positivos de los años 7 a 10?",
    opts: ["Disminuyen drásticamente al acercarse al año 10", "Se mantienen exactamente iguales porque el VAN no depende de la tasa", "Aumentan significativamente su valor presente, favoreciendo proyectos de infraestructura y ambientales"],
    ans: 2,
    why: "Al bajar la tasa de descuento de 12% a 5,5%, el factor 1/(1+r)^t castiga mucho menos los beneficios futuros, elevando el valor presente de flujos lejanos (ej. proyectos sanitarios, de agua o reciclaje)."
  },
  {
    tag: "P3 SNI 2026",
    q: "En la corrección de precios privados a precios sociales SNI 2026, ¿por qué se descuentan el IVA y el impuesto a la renta del flujo de caja social?",
    opts: ["Porque son transferencias entre privados y el Fisco dentro del mismo país, no consumo real de recursos", "Porque la ley tributaria exime de IVA a todos los proyectos públicos", "Porque aumentan artificialmente el factor de corrección de la divisa (FCSD)"],
    ans: 0,
    why: "Desde el punto de vista de la sociedad completa, un impuesto es lo que paga el privado y recibe el Estado simultáneamente; su efecto neto de recursos reales es cero (transferencia pura), por lo que no se computa como costo ni beneficio social."
  },
  {
    tag: "P3 Cuadrantes",
    q: "Un proyecto industrial privado presenta VANP = +$90 MM pero genera contaminación hídrica severa que lleva su VANS a −$120 MM (Cuadrante III). ¿Cuál es la recomendación económica correcta?",
    opts: ["Otorgarle un subsidio estatal para que mejore su rentabilidad", "Aplicar impuestos pigouvianos, normas de emisión o rechazar su ejecución sin mitigación que internalice el daño", "Aprobarlo automáticamente porque crea empleo privado"],
    ans: 1,
    why: "En el Cuadrante III (VANP > 0 y VANS < 0), el privado lucra trasladando un costo mayor a la sociedad (CMgS > CMgP). La política correcta es regular, exigir mitigación o aplicar un impuesto pigouviano hasta internalizar la externalidad."
  },
  {
    tag: "P3 Mano de Obra",
    q: "Según los precios sociales SNI 2026 del MDSF, ¿cuál categoría de mano de obra recibe el mayor ajuste a la baja respecto al salario de mercado por existir mayor desempleo/subempleo estructural?",
    opts: ["Mano de Obra Calificada (MOC = 0,97)", "Mano de Obra Semicalificada (MOSC = 0,95)", "Mano de Obra No Calificada (MONC = 0,91)"],
    ans: 2,
    why: "En los parámetros SNI 2026 (31 mar 2026), los factores son MOC = 0,97, MOSC = 0,95 y MONC = 0,91; el costo de oportunidad social es proporcionalmente menor en la mano de obra no calificada (MONC)."
  },
  {
    tag: "P4 ↔ P3 GEI",
    q: "Un proyecto de valorización de residuos evita la emisión de 10 toneladas de metano (CH4) al año. Usando el potencial de calentamiento global (GWP = 28) y el Precio Social del Carbono SNI 2026 ($71.801/t CO2eq), ¿qué beneficio social anual genera?",
    opts: ["$718.010 anuales (10 × $71.801)", "$20.104.280 anuales (10 × 28 × $71.801)", "$190.272.650 anuales (10 × 265 × $71.801)"],
    ans: 1,
    why: "Primero se convierte el metano a CO2 equivalente multiplicando por 28 (10 t CH4 = 280 t CO2eq; el factor 265 corresponde a N2O) y luego se multiplica por $71.801/t CO2eq ⇒ $20.104.280/año."
  },
  {
    tag: "P4 Leopold / SEIA",
    q: "En la Matriz de Leopold, una celda registra Magnitud = −8 e Importancia = 9, y el proyecto afecta significativamente un humedal protegido (art. 11 Ley 19.300). ¿Qué implica esto?",
    opts: ["Un impacto ambiental negativo crítico (−72) que exige ingresar al SEIA mediante un Estudio de Impacto Ambiental (EIA)", "Un impacto positivo alto que permite ingresar solo con una Declaración de Impacto Ambiental (DIA)", "Que la importancia debe ingresarse con signo negativo (−9) para cancelar el signo de la magnitud"],
    ans: 0,
    why: "En Leopold la Magnitud lleva signo (−8 = daño severo) y la Importancia es siempre positiva (1 a 10). Al existir efectos adversos significativos del art. 11 de la Ley 19.300, corresponde obligatoriamente un EIA con medidas de mitigación/reparación/compensación."
  },
  {
    tag: "P5 CEPAL N° 39",
    q: "Al formular el Árbol de Problemas bajo la metodología CEPAL N° 39 (Ortegón, Pacheco y Prieto), ¿cuál de los siguientes enunciados está BIEN formulado como Problema Central?",
    opts: ["Falta de un centro de acopio municipal de cartón en Osorno", "Inexistencia de subsidios municipales para recicladores", "Alta tasa de disposición final de cartón reciclable en el vertedero comunal"],
    ans: 2,
    why: "Regla central de CEPAL N° 39: el problema nunca debe redactarse como 'falta de una solución' (eso cierra el análisis a una sola alternativa), sino como un estado negativo real y verificable."
  },
  {
    tag: "P5 ↔ P2 MML",
    q: "En la Matriz de Marco Lógico (MML 4×4), la Lógica Vertical establece que si se ejecutan las Actividades y se cumplen sus Supuestos, se logran los Componentes; y si se entregan los Componentes y se cumplen sus Supuestos, se alcanza:",
    opts: ["El Propósito (efecto directo del proyecto sobre la población objetivo)", "La Tasa Social de Descuento del 5,5%", "Los Medios de Verificación contables únicamente"],
    ans: 0,
    why: "La Lógica Vertical de la MML encadena de abajo hacia arriba: Actividades (+ Supuestos) → Componentes (+ Supuestos) → Propósito (+ Supuestos) → Fin (contribución de largo plazo)."
  }
];

let qzProyAns = {};
let qzProySoloPend = false;

function toggleSoloErradasProy(btn) {
  qzProySoloPend = !qzProySoloPend;
  btn.classList.toggle("primary", qzProySoloPend);
  renderQuizProy();
}
function responderQuizProy(idx, optIdx) {
  qzProyAns[idx] = optIdx;
  renderQuizProy();
}
function resetQuizProy() {
  qzProyAns = {};
  qzProySoloPend = false;
  renderQuizProy();
}
function renderQuizProy() {
  const wrap = document.getElementById("qz-proy-list");
  if (!wrap) return;
  wrap.innerHTML = "";
  let okCount = 0;
  QUIZ_PROY_DATA.forEach((item, idx) => {
    const uAns = qzProyAns[idx];
    const isAns = uAns !== undefined;
    const isOk = isAns && uAns === item.ans;
    if (isOk) okCount++;
    if (qzProySoloPend && isOk) return;

    const card = document.createElement("div");
    card.className = "qz-card" + (isAns ? (" answered " + (isOk ? "ok" : "bad")) : "");
    const btns = item.opts.map((op, oi) =>
      `<button class="qz-btn ${uAns === oi ? "sel" : ""}" onclick="responderQuizProy(${idx}, ${oi})">${op}</button>`
    ).join("");
    const badgeRes = isAns ? `<span style="font-size:11.5px;font-weight:800;color:${isOk ? "#15803D" : "#DC2626"};">${isOk ? "✓ Correcto" : "✗ Revisar"}</span>` : "";
    card.innerHTML = `
      <div><span class="qz-tag">${item.tag}</span> <span style="font-size:11px;color:#475569;font-weight:700;">Pregunta ${idx + 1}</span></div>
      <div class="qz-q">${item.q}</div>
      <div class="qz-opts">${btns}${badgeRes}</div>
      <div class="qz-fb"><b>Fundamento teórico de cátedra:</b> ${item.why}</div>`;
    wrap.appendChild(card);
  });
  document.getElementById("qz-proy-score").textContent = `Aciertos: ${okCount} / ${QUIZ_PROY_DATA.length}`;
}

renderQuizVF();
renderMecanica();
drawMapaProy();
renderLecturaProy();
renderQuizProy();
</script>
</body>
</html>
"""


def renderizar_simuladores_fluidos_60fps():
    """Renderiza el estudio integral a 60 FPS (10 módulos) sin recarga de servidor ni ruido visual."""
    components.html(HTML_SIMULADOR_FLUIDO, height=1280, scrolling=True)
