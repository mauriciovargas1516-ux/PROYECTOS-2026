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

  /* === PLANTILLAS VERTICALES DE FLUJOS (MODO CIEGO + CUADERNO) === */
  .flj-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-bottom: 14px; }
  @media (max-width: 900px) { .flj-grid { grid-template-columns: 1fr; } }
  .flj-card {
    border: 1px solid #CBD5E1; border-top: 3.5px solid #1E3A8A; border-radius: 6px;
    background: #FFFFFF; padding: 9px 11px; cursor: pointer; transition: border-color 0.15s ease;
  }
  .flj-card:hover { border-color: #60A5FA; }
  .flj-head { display: flex; justify-content: space-between; align-items: center; gap: 6px; margin-bottom: 6px; }
  .flj-title { font-size: 12px; font-weight: 800; color: #0F172A; }
  .flj-badge { font-size: 10px; font-weight: 800; color: #FFFFFF; background: #1E3A8A; padding: 2px 7px; border-radius: 10px; white-space: nowrap; }
  .flj-rows { display: flex; flex-direction: column; gap: 2.5px; }
  .flj-row {
    display: flex; align-items: baseline; gap: 6px; font-size: 11.2px; line-height: 1.35;
    padding: 2.5px 6px; border-radius: 4px; background: #F8FAFC; color: #1E293B;
  }
  .flj-row.sub { background: #EFF6FF; font-weight: 800; color: #0F172A; border-top: 1px solid #BFDBFE; border-bottom: 1px solid #BFDBFE; }
  .flj-row.tot { background: #DCFCE7; font-weight: 800; color: #14532D; border: 1px solid #4ADE80; }
  .flj-row.hlt { background: #FEF3C7; color: #78350F; font-weight: 700; }
  .flj-sgn { font-family: Consolas, monospace; font-weight: 800; min-width: 28px; display: inline-block; }
  .sg-p { color: #15803D; }
  .sg-m { color: #DC2626; }
  .sg-e { color: #1D4ED8; }
  .flj-foot { font-size: 10.6px; color: #475569; margin-top: 6px; border-top: 1px dashed #CBD5E1; padding-top: 5px; line-height: 1.35; }
  .blind-mode .flj-card:not(.revealed) .flj-rows,
  .blind-mode .flj-card:not(.revealed) .flj-foot { display: none; }
  .blind-mode .flj-card:not(.revealed) .blind-cover { display: block; padding: 24px 8px; }

  /* === TABLAS DE CONVERSIÓN PRIVADO -> SOCIAL (CASOS CLASE) === */
  .cl-subgrid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 11px; margin: 10px 0; align-items: start; }
  @media (max-width: 860px) { .cl-subgrid { grid-template-columns: 1fr; } }
  .cl-tbl-wrap { background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 10px; }
  .cl-tbl-tit { font-size: 11.8px; font-weight: 800; color: #1E3A8A; margin-bottom: 6px; }
  .cl-tbl { width: 100%; border-collapse: collapse; font-size: 11.2px; }
  .cl-tbl th { background: #1E293B; color: #FFFFFF; padding: 4.5px 6px; border: 1px solid #CBD5E1; text-align: center; font-weight: 700; }
  .cl-tbl td { padding: 4px 6px; border: 1px solid #CBD5E1; text-align: right; font-family: Consolas, monospace; color: #0F172A; }
  .cl-tbl td:first-child { text-align: left; font-family: inherit; font-weight: 700; background: #F8FAFC; }
  .cl-tbl tr.row-zero td { background: #FEF2F2; color: #991B1B; }
  .cl-tbl tr.row-tot td { background: #DBEAFE; font-weight: 800; color: #0F172A; border-top: 2px solid #1E3A8A; }
  .cl-verdict {
    margin: 10px 0; padding: 10px 14px; border-radius: 7px; border: 1px solid #CBD5E1;
    border-left: 5px solid #15803D; background: #F0FDF4; font-size: 12.1px; line-height: 1.5; color: #0F172A;
  }
  .cl-verdict.sub-si { border-left-color: #D97706; background: #FFFBEB; }
  .cl-verdict.sub-rej { border-left-color: #DC2626; background: #FEF2F2; }
  .cl-sec { display: none; }
  .cl-sec.active { display: block; }

  /* === ESTUDIO GUIADO EN 4 MODOS (APRENDER · PRACTICAR · FORMULARIO · LAB) === */
  .studio-bar {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
    background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px; padding: 9px 12px;
    margin-bottom: 10px; box-shadow: 0 1px 4px rgba(15, 23, 42, 0.05);
  }
  .mode-pills { display: flex; gap: 6px; flex-wrap: wrap; }
  .mode-btn {
    border: 1.5px solid #CBD5E1; background: #F8FAFC; color: #334155;
    padding: 7px 13px; border-radius: 7px; font-weight: 800; font-size: 12.2px;
    cursor: pointer; transition: all 0.14s ease;
  }
  .mode-btn:hover { border-color: #1D4ED8; color: #1D4ED8; background: #EFF6FF; }
  .mode-btn.active { background: #0F172A; color: #FFFFFF; border-color: #0F172A; }
  .prog-chip {
    background: #ECFDF5; color: #065F46; border: 1px solid #6EE7B7;
    padding: 5px 11px; border-radius: 16px; font-size: 11.5px; font-weight: 800;
    font-family: Consolas, monospace; white-space: nowrap;
  }

  /* Barra de Tema + Paso a Paso (visible solo en Modo Aprender) */
  .learn-shell {
    display: none; background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px;
    padding: 12px 14px; margin-bottom: 10px;
  }
  .wrap.mode-aprender .learn-shell { display: block; }
  .prac-shell { display: none; background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px; padding: 10px 14px; margin-bottom: 10px; }
  .wrap.mode-practicar .prac-shell { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
  .wrap.mode-aprender.step-2 #panel-arboles .svg-box, .wrap.mode-aprender.step-2 #panel-arboles .note-box { display: block; }
  .wrap:not(.mode-lab) .top-tabs { display: none !important; }

  .learn-topic-row {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
    margin-bottom: 10px; padding-bottom: 9px; border-bottom: 1px solid #E2E8F0;
  }
  .learn-select {
    flex: 1; min-width: 260px; max-width: 560px; padding: 7px 10px;
    border: 1.5px solid #1D4ED8; border-radius: 7px; background: #F8FAFC;
    color: #0F172A; font-size: 12.8px; font-weight: 800; cursor: pointer;
  }
  .learn-select:focus { outline: 2px solid #93C5FD; background: #FFFFFF; }
  .step-bar {
    display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; margin-bottom: 10px;
  }
  @media (max-width: 680px) { .step-bar { grid-template-columns: 1fr; } }
  .step-pill {
    border: 1.5px solid #CBD5E1; background: #F8FAFC; color: #475569;
    padding: 8px 10px; border-radius: 7px; font-size: 12px; font-weight: 700;
    cursor: pointer; text-align: left; display: flex; align-items: center; gap: 8px;
    transition: all 0.14s ease;
  }
  .step-pill:hover { border-color: #60A5FA; background: #EFF6FF; }
  .step-pill.active { background: #1D4ED8; color: #FFFFFF; border-color: #1D4ED8; }
  .step-num {
    width: 22px; height: 22px; border-radius: 50%; background: #E2E8F0; color: #0F172A;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 800; flex-shrink: 0;
  }
  .step-pill.active .step-num { background: #FFFFFF; color: #1D4ED8; }

  .guide-card {
    background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 100%);
    border: 1px solid #BFDBFE; border-left: 4.5px solid #1D4ED8; border-radius: 8px;
    padding: 11px 14px; font-size: 12.5px; line-height: 1.5; color: #0F172A;
  }
  .guide-head {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
    margin-bottom: 5px;
  }
  .guide-tag {
    font-size: 10.5px; font-weight: 800; color: #1E3A8A; background: #DBEAFE;
    padding: 2px 8px; border-radius: 10px; text-transform: uppercase;
  }
  .guide-foot {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
    margin-top: 10px; padding-top: 9px; border-top: 1px dashed #CBD5E1;
  }
  .done-btn {
    border: 1.5px solid #15803D; background: #FFFFFF; color: #15803D;
    padding: 5px 10px; border-radius: 6px; font-size: 11.5px; font-weight: 800; cursor: pointer;
  }
  .done-btn.is-done { background: #15803D; color: #FFFFFF; }

  /* Recorte limpio por Paso dentro del Modo Aprender (cero murallas de bloques) */
  .wrap.mode-aprender .panel .sec-title { margin-bottom: 8px; }
  .wrap.mode-aprender .panel .enun-box,
  .wrap.mode-aprender .panel .eq-editor-bar,
  .wrap.mode-aprender .panel .sliders-grid,
  .wrap.mode-aprender .panel .kpis,
  .wrap.mode-aprender .panel .fstrip-grid,
  .wrap.mode-aprender .panel .sol-box,
  .wrap.mode-aprender .panel .ped-grid,
  .wrap.mode-aprender .panel .teo-box,
  .wrap.mode-aprender .panel .cl-subgrid,
  .wrap.mode-aprender #vf-list,
  .wrap.mode-aprender #panel-arboles .sec-title:nth-of-type(2),
  .wrap.mode-aprender #panel-clase > .sec-title,
  .wrap.mode-aprender #panel-waterfall .sec-title:nth-of-type(2),
  .wrap.mode-aprender #panel-horno .sec-title:nth-of-type(2),
  .wrap.mode-aprender #panel-agua .sec-title:nth-of-type(2),
  .wrap.mode-aprender #panel-ambiental .sec-title:nth-of-type(2) { display: none; }

  /* Paso 1: Gráfico / Diagrama limpio (Intuición) */
  .wrap.mode-aprender.step-1 .panel .svg-box,
  .wrap.mode-aprender.step-1 .panel .legend-bar,
  .wrap.mode-aprender.step-1 .panel .cl-verdict,
  .wrap.mode-aprender.step-1 .panel .note-box,
  .wrap.mode-aprender.step-1 #leo-grid-wrap { display: block; }

  /* Paso 2: Fórmulas grandes editables + KPIs + Tablas + Solucionario */
  .wrap.mode-aprender.step-2 .panel .svg-box,
  .wrap.mode-aprender.step-2 .panel .legend-bar,
  .wrap.mode-aprender.step-2 #leo-grid-wrap { display: none; }
  .wrap.mode-aprender.step-2 .panel .kpis { display: grid; }
  .wrap.mode-aprender.step-2 .panel .fstrip-grid { display: grid; }
  .wrap.mode-aprender.step-2 .panel .cl-subgrid { display: grid; }
  .wrap.mode-aprender.step-2 .panel .sol-box,
  .wrap.mode-aprender.step-2 .panel .cl-verdict { display: block; }

  /* Paso 3: Trampas de prueba + 3 Cápsulas Pedagógicas + Marco Teórico */
  .wrap.mode-aprender.step-3 .panel .svg-box,
  .wrap.mode-aprender.step-3 .panel .legend-bar,
  .wrap.mode-aprender.step-3 #leo-grid-wrap,
  .wrap.mode-aprender.step-3 .panel .cl-verdict { display: none; }
  .wrap.mode-aprender.step-3 .panel .ped-grid { display: grid; }
  .wrap.mode-aprender.step-3 .panel .teo-box,
  .wrap.mode-aprender.step-3 .panel .enun-box { display: block; }

  /* Botón opcional "Ajustar variables (sliders)" en Paso 1 y Paso 2 */
  .wrap.mode-aprender.show-vars .panel .sliders-grid { display: grid !important; }
  .wrap.mode-aprender.show-vars .panel .eq-editor-bar { display: grid !important; }

  /* === PANEL MODO PRACTICAR (RETOS ACTIVOS CON RESPUESTAS OCULTAS) === */
  .pr-subtabs { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 11px; }
  .pr-chips { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 11px; }
  .pr-chip {
    border: 1.5px solid #CBD5E1; background: #F8FAFC; color: #334155;
    padding: 5px 10px; border-radius: 16px; font-size: 11.5px; font-weight: 700; cursor: pointer;
  }
  .pr-chip:hover { border-color: #1D4ED8; color: #1D4ED8; }
  .pr-chip.active { background: #1D4ED8; color: #FFFFFF; border-color: #1D4ED8; }
  .pr-chip.solved { background: #DCFCE7; color: #166534; border-color: #15803D; }
  .pr-chip.solved.active { background: #15803D; color: #FFFFFF; border-color: #15803D; }
  .pr-card {
    background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 4px solid #1D4ED8;
    border-radius: 8px; padding: 13px 16px;
  }
  .pr-enun {
    background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px;
    padding: 10px 13px; font-size: 12.6px; line-height: 1.52; color: #0F172A; margin-bottom: 12px;
  }
  .pr-qgrid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 10px; margin-bottom: 12px; }
  .pr-qbox {
    background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 7px; padding: 9px 11px;
  }
  .pr-qbox.ok { border-color: #15803D; background: #F0FDF4; }
  .pr-qbox.bad { border-color: #DC2626; background: #FEF2F2; }
  .pr-qlbl { font-size: 11.8px; font-weight: 800; color: #0F172A; margin-bottom: 5px; display: block; }
  .pr-in {
    width: 100%; padding: 7px 9px; border: 1.5px solid #94A3B8; border-radius: 5px;
    font-family: Consolas, monospace; font-size: 13px; font-weight: 700; background: #FFFFFF; color: #0F172A;
  }
  .pr-in:focus { outline: 2px solid #93C5FD; border-color: #1D4ED8; }
  .pr-qfb { font-size: 11.2px; margin-top: 5px; font-weight: 700; line-height: 1.35; }
  .pr-hint {
    display: none; margin-top: 10px; padding: 9px 12px; border-radius: 6px;
    background: #FFFBEB; border: 1px solid #FCD34D; border-left: 4px solid #D97706;
    font-size: 12px; line-height: 1.48; color: #78350F;
  }
  .pr-sol {
    display: none; margin-top: 10px; padding: 10px 13px; border-radius: 6px;
    background: #F0FDF4; border: 1px solid #86EFAC; border-left: 4px solid #15803D;
    font-size: 12px; line-height: 1.5; color: #14532D; font-family: Consolas, monospace;
  }

  .mec-print-msg {
    display: none; margin-bottom: 9px; padding: 7px 11px; border-radius: 6px;
    background: #EFF6FF; border: 1px solid #93C5FD; border-left: 4px solid #1D4ED8;
    font-size: 11.8px; color: #1E3A8A; font-weight: 600;
  }

  @media print {
    body { background: #FFFFFF !important; }
    .studio-bar, .learn-shell, .prac-shell, .top-tabs, .mec-toolbar, .mec-filters, .btn-bar, .chk-btn, .note-box { display: none !important; }
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
    .blind-mode .flj-card .flj-rows { display: flex !important; }
    .blind-mode .flj-card .flj-foot { display: block !important; }
    .blind-mode .flj-card .blind-cover { display: none !important; }
    .flj-grid { grid-template-columns: repeat(3, 1fr) !important; gap: 6px !important; }
    .skel-grid { grid-template-columns: repeat(3, 1fr) !important; gap: 6px !important; }
    .s-card { break-inside: avoid; border: 1px solid #94A3B8 !important; padding: 5px !important; }
  }
</style>
</head>
<body>
<div id="app-wrap" class="wrap mode-aprender step-1">
  <!-- BARRA MAESTRA DE 4 MODOS DE ESTUDIO -->
  <div class="studio-bar">
    <div class="mode-pills">
      <button id="mbtn-aprender" class="mode-btn active" onclick="setStudioMode('aprender')">1. Aprender (Paso a Paso)</button>
      <button id="mbtn-practicar" class="mode-btn" onclick="setStudioMode('practicar')">2. Practicar (Modo Prueba)</button>
      <button id="mbtn-formulario" class="mode-btn" onclick="setStudioMode('formulario')">3. Formulario e Impresión</button>
      <button id="mbtn-lab" class="mode-btn" onclick="setStudioMode('lab')">4. Laboratorio Completo</button>
    </div>
    <span id="studio-prog-chip" class="prog-chip">Progreso: 0 / 10 temas · 0 / 8 retos</span>
  </div>

  <!-- GUÍA PASO A PASO (SOLO EN MODO APRENDER) -->
  <div class="learn-shell">
    <div class="learn-topic-row">
      <select id="learn-topic-sel" class="learn-select" onchange="selectLearnTopic(+this.value)"></select>
      <div class="btn-bar">
        <button class="act-btn" onclick="stepLearnTopic(-1)">← Tema anterior</button>
        <button class="act-btn" onclick="stepLearnTopic(1)">Tema siguiente →</button>
        <button id="learn-done-btn" class="done-btn" onclick="toggleTopicDone()">Marcar aprendido ✓</button>
      </div>
    </div>

    <div class="step-bar">
      <button id="stp-btn-1" class="step-pill active" onclick="setLearnStep(1)">
        <span class="step-num">1</span><span><b>Ver el Gráfico</b> · Qué te piden</span>
      </button>
      <button id="stp-btn-2" class="step-pill" onclick="setLearnStep(2)">
        <span class="step-num">2</span><span><b>Fórmulas Clave</b> · Cálculo paso a paso</span>
      </button>
      <button id="stp-btn-3" class="step-pill" onclick="setLearnStep(3)">
        <span class="step-num">3</span><span><b>Trampa de Prueba</b> · Teoría y defensa</span>
      </button>
    </div>

    <div class="guide-card">
      <div class="guide-head">
        <span id="guide-step-tag" class="guide-tag">Paso 1 de 3 — Intuición Visual</span>
        <div class="btn-bar">
          <button id="btn-toggle-vars" class="act-btn" onclick="toggleVarsGuided()">Ajustar variables (sliders)</button>
          <button class="act-btn primary" onclick="irAPracticaTemaActual()">Practicar este tema →</button>
        </div>
      </div>
      <div id="guide-step-body"></div>
      <div class="guide-foot">
        <button id="btn-prev-step" class="act-btn" onclick="moveLearnStep(-1)">← Paso anterior</button>
        <span id="guide-step-hint" style="font-size:11.5px;color:#475569;font-weight:700;">Paso 1 de 3</span>
        <button id="btn-next-step" class="act-btn primary" onclick="moveLearnStep(1)">Siguiente paso →</button>
      </div>
    </div>
  </div>


  <!-- SUB-NAVEGACIÓN MODO PRACTICAR (SIEMPRE VISIBLE EN MODO PRACTICAR) -->
  <div class="prac-shell">
    <span style="font-size:12.5px;font-weight:800;color:#1E3A8A;">Modo Prueba Activa — Elige cómo quieres entrenarte:</span>
    <div class="btn-bar">
      <button id="pr-sub-retos" class="act-btn primary" onclick="setPracSub('retos')">Retos Numéricos con Respuesta Oculta (8)</button>
      <button id="pr-sub-vf" class="act-btn" onclick="setPracSub('vf')">Quiz Verdadero / Falso RA1 (8)</button>
      <button id="pr-sub-lec" class="act-btn" onclick="setPracSub('lec')">Control de Lectura y Mapa Teórico (10)</button>
    </div>
  </div>

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
    <button class="tab-btn" onclick="openTab('clase', this)">11. Casos Clase: Precios Sociales y Salmón (SNI 2026)</button>
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
        <button class="act-btn" onclick="imprimirHojaMecanica(false)" title="Abre vista Carta limpia con todas las fórmulas, flujos y etiquetas">Imprimir Completo (Carta)</button>
        <button class="act-btn" onclick="imprimirHojaMecanica(true)" title="Abre hoja Carta en blanco con líneas para escribir de memoria con lápiz">Imprimir En Blanco (Lápiz)</button>
        <button class="act-btn" onclick="descargarHojaMecanica()" title="Descarga archivo HTML listo para imprimir según el modo activo (Copia o Ciego)">Descargar (.html)</button>
      </div>
    </div>

    <div class="mec-toolbar">
      <div style="font-size:12px;color:#334155;">
        <b>Método de cuaderno:</b> copia las 18 fórmulas, las 3 estructuras verticales de Flujos (Privado Puro · Financiado · Social SNI 2026) y los 6 gráficos; luego activa <b>Modo Ciego</b>, escríbelos sin mirar y haz clic en cada bloque para comprobar y marcar <b>✓</b>.
      </div>
      <span id="mec-score" class="pill-score">Dominadas: 0 / 18</span>
    </div>

    <div class="mec-filters">
      <button class="flt-btn active" onclick="filtrarMec('all', this)">Todas (18)</button>
      <button class="flt-btn" onclick="filtrarMec('ps', this)">I. Precios Sociales y Transables (6)</button>
      <button class="flt-btn" onclick="filtrarMec('vsp', this)">II. Microeconomía VSP / Harberger (3)</button>
      <button class="flt-btn" onclick="filtrarMec('eval', this)">III. Privada, VAC/CAE y Subsidio (6)</button>
      <button class="flt-btn" onclick="filtrarMec('dem', this)">IV. Población, Ambiental y MML (3)</button>
    </div>

    <div id="mec-print-msg" class="mec-print-msg"></div>
    <div id="mec-container">
      <div class="mec-grid" id="mec-formulas-grid"></div>

      <div class="sec-title" style="margin-top:6px;">
        <span>Estructuras Verticales de Flujos para Memorizar (Privado Puro · Financiado · Social SNI 2026)</span>
        <span style="font-size:11px;font-weight:600;color:#334155;">En Modo Ciego, haz clic en cada plantilla para comprobar el orden y los signos</span>
      </div>
      <div class="flj-grid" id="mec-flujos-grid"></div>

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

  <!-- ====================================================================== -->
  <!-- PANEL 11: CASOS DE CLASE — CONVERSIÓN SOCIAL ÍTEM A ÍTEM Y SALMÓN SNI  -->
  <!-- ====================================================================== -->
  <div id="panel-clase" class="panel">
    <div class="sec-title">
      <span>Casos de Clase Resueltos — Conversión Privado → Social (Pizarra) y Sustitución de Importaciones (Salmón SNI 2026)</span>
      <div class="btn-bar">
        <button id="cl-btn-ej1" class="act-btn primary" onclick="selCasoClase('ej1', this)">Ejercicio 1: Tabla Social + VSP Perpetuidad ($503,3M)</button>
        <button id="cl-btn-ej2" class="act-btn" onclick="selCasoClase('ej2', this)">Ejercicio 2: Salmón (Sustitución Importaciones + Subsidio)</button>
      </div>
    </div>

    <!-- ================= CASO A: EJERCICIO 1 (PIZARRA / CUADERNO) ================= -->
    <div id="cl-sec-ej1" class="cl-sec active">
      <details class="enun-box" open>
        <summary>
          <span>Ejercicio 1 de Clase — Conversión de Inversión ($2.000 MM) y Costo ($1.000/u) a Precios Sociales + VANS a Perpetuidad</span>
          <span class="enun-badge">Fórmula Importados: CS = CP · (R*/R) / [(1+IVA)(1+t)]</span>
        </summary>
        <div class="enun-body" id="cl1-enun"></div>
      </details>

      <div class="btn-bar" style="margin-bottom:9px;">
        <button class="act-btn primary" onclick="presetCl1('pizarra')">Preset Pizarra Oficial (FCSD 1,06 · t=11% · r=12%)</button>
        <button class="act-btn" onclick="presetCl1('sni2026')">Adaptar a SNI 2026 (MOC 0,97 · FCSD 1,00 · TSD 5,5%)</button>
        <button id="cl1-btn-int" class="act-btn" onclick="toggleInteresCl1()">Intereses: Pizarra (÷1,19) ⇄ Estricto ($0)</button>
      </div>

      <div class="sliders-grid">
        <div class="sl-card"><div class="sl-head"><span>Inversión Privada IP ($MM)</span><span id="cl1-ip-v" class="sl-val">$2.000M</span></div><input id="cl1-ip" type="range" min="500" max="4000" step="100" value="2000" oninput="drawClaseEj1()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Costo Unit. Privado C ($/u)</span><span id="cl1-cp-v" class="sl-val">$1.000</span></div><input id="cl1-cp" type="range" min="400" max="2000" step="50" value="1000" oninput="drawClaseEj1()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Tasa Descuento r (%)</span><span id="cl1-r-v" class="sl-val">12,0%</span></div><input id="cl1-r" type="range" min="4.0" max="18.0" step="0.5" value="12.0" oninput="drawClaseEj1()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Divisa (R*/R)</span><span id="cl1-div-v" class="sl-val">1,06</span></div><input id="cl1-div" type="range" min="1.00" max="1.15" step="0.01" value="1.06" oninput="drawClaseEj1()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Arancel Import. t (%)</span><span id="cl1-ar-v" class="sl-val">11,0%</span></div><input id="cl1-ar" type="range" min="0.0" max="15.0" step="1.0" value="11.0" oninput="drawClaseEj1()" /></div>
      </div>

      <div class="kpis">
        <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Inversión Social (IS)</div><div id="cl1-k-is" class="kpi-val">$1.461,1M</div><div id="cl1-k-is2" class="kpi-sub">vs IP = $2.000M</div></div>
        <div class="kpi" style="border-left-color:#7C3AED;"><div class="kpi-lbl">Costo Social Unitario (CS)</div><div id="cl1-k-cs" class="kpi-val">$782,25/u</div><div id="cl1-k-cs2" class="kpi-sub">Depreciación = $0</div></div>
        <div class="kpi" style="border-left-color:#059669;"><div class="kpi-lbl">Valor Social Prod. (VSP = AD+LR)</div><div id="cl1-k-vsp" class="kpi-val">$235,7M/año</div><div id="cl1-k-adlr" class="kpi-sub">AD $157,5M + LR $78,2M</div></div>
        <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">VANS a Perpetuidad (-IS + VSP/r)</div><div id="cl1-k-vans" class="kpi-val">+$503,3M</div><div id="cl1-k-dec" class="kpi-sub">SOCIALMENTE RENTABLE</div></div>
      </div>

      <div id="cl1-fstrip" class="fstrip-grid"></div>
      <div class="svg-box"><svg id="svg-cl1" viewBox="0 0 980 355"></svg></div>
      <div class="cl-subgrid">
        <div class="cl-tbl-wrap"><div class="cl-tbl-tit">Tabla 1A — Conversión de la Inversión Privada a Inversión Social (IS)</div><div id="cl1-tbl-inv"></div></div>
        <div class="cl-tbl-wrap"><div class="cl-tbl-tit">Tabla 1B — Conversión del Costo Operativo Unitario a Costo Social (CS)</div><div id="cl1-tbl-cos"></div></div>
      </div>
      <div id="ped-cl1" class="ped-grid"></div>
      <details class="teo-box">
        <summary>
          <span>Marco Teórico: Conversión de Presupuestos Privados a Precios Sociales y Perpetuidad (Fontaine Cap. V–VI)</span>
          <span class="enun-badge">Desplegar teoría de apoyo</span>
        </summary>
        <div class="teo-body">
          <ul>
            <li><b>Depreciación Legal = $0 en Flujo Social:</b> la depreciación es una convención tributaria/contable, no un consumo real de recursos físicos de la economía (el consumo real de capital ya se imputó al registrar la inversión social <b>I<sub>S</sub></b> en t=0).</li>
            <li><b>Bienes Importados:</b> cuando el precio privado incluye IVA y arancel, primero se limpia de impuestos dividiendo por <b>(1 + IVA)(1 + t<sub>a</sub>)</b> y luego se ajusta por el precio social de la divisa multiplicando por <b>R*/R</b>.</li>
            <li><b>Cuidado metodológico con Intereses:</b> en evaluación social pura los intereses financieros internos suelen excluirse (transferencia entre residentes); en este ejercicio de pizarra se dividieron por 1,19 como servicio gravado, por lo que el botón superior permite comparar ambos criterios.</li>
          </ul>
        </div>
      </details>
    </div>

    <!-- ================= CASO B: EJERCICIO 2 (SALMÓN — SNI 2026) ================= -->
    <div id="cl-sec-ej2" class="cl-sec">
      <details class="enun-box" open>
        <summary>
          <span>Ejercicio 2 de Clase — Industria del Salmón: Sustitución de Importaciones (8 de 10 ton/año · 40 años · SNI 2026)</span>
          <span class="enun-badge">Preguntas clave: ¿Aporte estatal? · ¿Cuánto subsidiar?</span>
        </summary>
        <div class="enun-body" id="cl2-enun"></div>
      </details>

      <div class="btn-bar" style="margin-bottom:9px;">
        <button class="act-btn primary" onclick="presetCl2('pizarra')">Preset Pizarra Oficial (Arancel 1% · P_int US$ 500)</button>
        <button class="act-btn" onclick="presetCl2('arancel6')">Arancel General Chile 6% (1 / [1,19×1,06])</button>
        <button class="act-btn" onclick="presetCl2('cuadrante2')">Probar Cuadrante II (P_int US$ 410 → Requiere Subsidio)</button>
      </div>

      <div class="sliders-grid">
        <div class="sl-card"><div class="sl-head"><span>Precio CIF Import. (US$/kg)</span><span id="cl2-cif-v" class="sl-val">US$ 450</span></div><input id="cl2-cif" type="range" min="300" max="650" step="10" value="450" oninput="drawClaseEj2()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Precio Venta Interno (US$/kg)</span><span id="cl2-pin-v" class="sl-val">US$ 500</span></div><input id="cl2-pin" type="range" min="360" max="620" step="5" value="500" oninput="drawClaseEj2()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Producción Anual (Ton/año)</span><span id="cl2-q-v" class="sl-val">8,0 ton</span></div><input id="cl2-q" type="range" min="2.0" max="10.0" step="0.5" value="8.0" oninput="drawClaseEj2()" /></div>
        <div class="sl-card"><div class="sl-head"><span>Arancel Efectivo t (%)</span><span id="cl2-ar-v" class="sl-val">1,0%</span></div><input id="cl2-ar" type="range" min="0.0" max="10.0" step="0.5" value="1.0" oninput="drawClaseEj2()" /></div>
        <div class="sl-card"><div class="sl-head"><span>TSD Social (%) / r Priv. (%)</span><span id="cl2-r-v" class="sl-val">5,5% / 12%</span></div><input id="cl2-rp" type="range" min="6.0" max="24.0" step="1.0" value="12.0" oninput="drawClaseEj2()" /></div>
      </div>

      <div class="kpis">
        <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Inversión Social (IS)</div><div id="cl2-k-is" class="kpi-val">US$ 1.220.016</div><div id="cl2-k-is2" class="kpi-sub">AF Imp + MOC (0,97)</div></div>
        <div class="kpi" style="border-left-color:#7C3AED;"><div class="kpi-lbl">Beneficio Neto Social Anual (BN)</div><div id="cl2-k-bn" class="kpi-val">US$ 782.160/año</div><div id="cl2-k-cs" class="kpi-sub">VSP $3,60M − CS $2,82M</div></div>
        <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">VANS (40 años · TSD 5,5%)</div><div id="cl2-k-vans" class="kpi-val">+US$ 11.330.621</div><div id="cl2-k-vsp" class="kpi-sub">Ahorro de divisas CIF</div></div>
        <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">VAN Privado &amp; Subsidio Estatal</div><div id="cl2-k-sub" class="kpi-val">Aporte: US$ 0</div><div id="cl2-k-vp" class="kpi-sub">VAN Priv (12%) +US$ 1,31M</div></div>
      </div>

      <div id="cl2-fstrip" class="fstrip-grid"></div>
      <div id="cl2-verdict" class="cl-verdict"></div>
      <div class="svg-box"><svg id="svg-cl2" viewBox="0 0 980 335"></svg></div>
      <div class="cl-subgrid">
        <div class="cl-tbl-wrap"><div class="cl-tbl-tit">Tabla 2A — Conversión a Precios Sociales SNI 2026 (Inversión y Costo por kg)</div><div id="cl2-tbl-soc"></div></div>
        <div class="cl-tbl-wrap"><div class="cl-tbl-tit">Tabla 2B — Evaluación Privada (27% Renta + Dep. 40a) vs. Evaluación Social</div><div id="cl2-tbl-comp"></div></div>
      </div>
      <div id="ped-cl2" class="ped-grid"></div>
      <details class="teo-box">
        <summary>
          <span>Marco Teórico: Sustitución de Importaciones y Matriz de 4 Cuadrantes del Subsidio Estatal</span>
          <span class="enun-badge">Desplegar teoría de apoyo</span>
        </summary>
        <div class="teo-body">
          <ul>
            <li><b>Valor Social en Sustitución de Importaciones (Bien Importable):</b> mientras la producción nacional del proyecto (<b>8 ton</b>) sea menor que las importaciones totales del país (<b>10 ton</b>), Chile sigue siendo importador neto en el margen. Por eso cada kilogramo producido sustituye una importación y libera divisas por <b>P<sub>CIF</sub> × FCSD = US$ 450/kg</b>.</li>
            <li><b>Regla de los 4 Cuadrantes para el Aporte Estatal:</b> (1) <b>Cuadrante I (VAN<sub>P</sub> &gt; 0 y VANS &gt; 0):</b> el privado invierte solo, <b>Aporte Estatal = $0</b>; (2) <b>Cuadrante II (VAN<sub>P</sub> &lt; 0 y VANS &gt; 0):</b> el Estado <b>SÍ</b> debe subsidiar un monto mínimo igual a <b>|VAN<sub>P</sub>|</b> (para hacer VAN<sub>P</sub> ≥ 0) con tope máximo <b>VANS</b>; (3) <b>Cuadrante III (VAN<sub>P</sub> &lt; 0 y VANS &lt; 0):</b> rechazar; (4) <b>Cuadrante IV (VAN<sub>P</sub> &gt; 0 y VANS &lt; 0):</b> desincentivar / regular.</li>
            <li><b>Nota sobre el factor 1,01 en la pizarra:</b> en Chile el arancel general es 6%, pero el arancel efectivo promedio ponderado por los Tratados de Libre Comercio (TLC) bordea el 1% (por eso <b>1 / (1,19 × 1,01)</b> da exactamente US$ 832.015,97 y US$ 83,20/kg). El control permite cambiar entre 1% y 6%.</li>
          </ul>
        </div>
      </details>
    </div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL MODO PRACTICAR: RETOS CON RESPUESTAS OCULTAS + QUIZ V/F + LECTURA -->
  <!-- ====================================================================== -->
  <div id="panel-practicar" class="panel">

    <div id="pr-view-retos">
      <div id="pr-chips-bar" class="pr-chips"></div>
      <div class="pr-card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px;">
          <div>
            <span id="pr-badge" class="enun-badge">Reto 1 de 8</span>
            <span id="pr-title" style="font-size:14px;font-weight:800;color:#0F172A;margin-left:6px;"></span>
          </div>
          <button class="act-btn" onclick="abrirTemaDesdeReto()">Repasar este tema en Aprender →</button>
        </div>
        <div id="pr-enun" class="pr-enun"></div>
        <div id="pr-qgrid" class="pr-qgrid"></div>
        <div class="btn-bar">
          <button class="act-btn primary" onclick="comprobarReto()">Comprobar Respuestas</button>
          <button class="act-btn" onclick="toggleHintReto()">Ver Pista (Fórmula)</button>
          <button class="act-btn" onclick="toggleSolReto()">Ver Desarrollo Completo</button>
          <button class="act-btn" onclick="limpiarReto()">Limpiar</button>
          <button class="act-btn" onclick="navReto(1)">Siguiente Reto →</button>
        </div>
        <div id="pr-hint" class="pr-hint"></div>
        <div id="pr-sol" class="pr-sol"></div>
      </div>
    </div>

    <div id="pr-view-vf" style="display:none;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:8px;">
        <span style="font-size:12.5px;font-weight:700;color:#1E3A8A;">Repaso Verdadero / Falso — Prueba Proceso 2 RA1 (Dra. Luz María Ferrada)</span>
        <div class="btn-bar">
          <span id="pr-vf-score" class="pill-score">Puntaje: 0 / 8</span>
          <button class="act-btn" onclick="resetQuizVF()">Reiniciar V/F</button>
        </div>
      </div>
      <div id="pr-vf-list"></div>
    </div>
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
  // 11. Casos de Clase (Precios Sociales + Salmón SNI 2026)
  if (bindKey === "cl1_ip")  { setSliderSmart("cl1-ip", Math.max(100, val), 100, null); drawClaseEj1(); return true; }
  if (bindKey === "cl1_cp")  { setSliderSmart("cl1-cp", Math.max(100, val), 100, null); drawClaseEj1(); return true; }
  if (bindKey === "cl1_r")   { setSliderSmart("cl1-r", val, 1.0, 30.0); drawClaseEj1(); return true; }
  if (bindKey === "cl1_div") { setSliderSmart("cl1-div", val, 0.90, 1.30); drawClaseEj1(); return true; }
  if (bindKey === "cl1_ar")  { setSliderSmart("cl1-ar", val, 0.0, 25.0); drawClaseEj1(); return true; }
  if (bindKey === "cl2_cif") { setSliderSmart("cl2-cif", Math.max(100, val), 100, null); drawClaseEj2(); return true; }
  if (bindKey === "cl2_pin") { setSliderSmart("cl2-pin", Math.max(100, val), 100, null); drawClaseEj2(); return true; }
  if (bindKey === "cl2_q")   { setSliderSmart("cl2-q", val, 0.5, 10.0); drawClaseEj2(); return true; }
  if (bindKey === "cl2_ar")  { setSliderSmart("cl2-ar", val, 0.0, 15.0); drawClaseEj2(); return true; }
  if (bindKey === "cl2_rp")  { setSliderSmart("cl2-rp", val, 3.0, 30.0); drawClaseEj2(); return true; }
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
  if (name === "clase") { drawClaseEj1(); drawClaseEj2(); }
  if (name === "lectura") { drawMapaProy(); renderLecturaProy(); renderQuizProy(); }
}
function jumpToTab(name) {
  if (name === "mecanica") { setStudioMode("formulario"); window.scrollTo({ top: 0, behavior: "smooth" }); return; }
  const tIdx = LEARN_TOPICS.findIndex(t => t.tab === name);
  if (tIdx >= 0 && studioMode !== "lab") {
    learnTopicIdx = tIdx;
    learnStep = 1;
    setStudioMode("aprender");
    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }
  setStudioMode("lab");
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
    rule: "Problema nunca es 'falta de solución' (caso Macondo). Un único Propósito; Actividades NO llevan supuestos en la MML." },
  { id: 17, cat: "ps", tag: "Transables", title: "17. Costo Social de Importados y Perpetuidad",
    eq: `CS<sub>imp</sub> = CP · <span class="frac"><span class="num">R* / R</span><span class="den">(1 + IVA)(1 + t<sub>a</sub>)</span></span> &nbsp;|&nbsp; VANS<sub>∞</sub> = −I<sub>S</sub> + <span class="frac"><span class="num">BN</span><span class="den">r</span></span>`,
    rule: "Limpia IVA y arancel (t_a) y ajusta por divisa (R*/R). Depreciación legal = $0 en evaluación social." },
  { id: 18, cat: "eval", tag: "Subsidio", title: "18. Sustitución Importaciones y Subsidio Estatal",
    eq: `VSP<sub>imp</sub> = Q · P<sub>CIF</sub> · FCSD &nbsp;|&nbsp; Subsidio ∈ [ |VAN<sub>P</sub>| , VANS ]`,
    rule: "Si VAN_P ≥ 0 y VANS > 0 (Cuadrante I) ⇒ Aporte Estatal = $0. Solo se subsidia en Cuadrante II (VAN_P < 0 y VANS > 0)." }
];

const FLUJOS_PLANTILLAS_PROY = [
  {
    title: "1. Flujo Privado Puro (Sin Deuda)",
    badge: "Descuenta a r_p / WACC",
    col: "#1D4ED8",
    rows: [
      { s: "(+)", c: "sg-p", t: "Ingresos Operacionales Netos (sin IVA)" },
      { s: "(−)", c: "sg-m", t: "Costos Variables, Fijos y Remuneraciones" },
      { s: "(−)", c: "sg-m", t: "Depreciación Legal (no es salida de caja)" },
      { s: "(=)", c: "sg-e", t: "Utilidad Antes de Impuestos (UAI)", cls: "sub" },
      { s: "(−)", c: "sg-m", t: "Impuesto a la Renta (Pro Pyme 25% / 27%)" },
      { s: "(=)", c: "sg-e", t: "Utilidad Después de Impuestos (UDI)", cls: "sub" },
      { s: "(+)", c: "sg-p", t: "Reverso Depreciación (gasto no desembolsable)" },
      { s: "(−)", c: "sg-m", t: "Inversión Inicial + Capital de Trabajo (Año 0)" },
      { s: "(+)", c: "sg-p", t: "Valor de Desecho + Recup. 100% CT (Año N)" },
      { s: "(=)", c: "sg-e", t: "FLUJO DE CAJA PRIVADO PURO", cls: "tot" }
    ],
    foot: "<b>Regla clave:</b> Todo en valores netos (sin IVA). Costos hundidos = $0. Terreno y Capital de Trabajo NO se deprecian."
  },
  {
    title: "2. Flujo Privado Financiado (Con Deuda)",
    badge: "Flujo Inversionista",
    col: "#059669",
    rows: [
      { s: "(+)", c: "sg-p", t: "Ingresos Operacionales Netos (sin IVA)" },
      { s: "(−)", c: "sg-m", t: "Costos Operativos, Fijos y Depreciación" },
      { s: "(−)", c: "sg-m", t: "Intereses del Crédito (generan Escudo Fiscal)", cls: "hlt" },
      { s: "(=)", c: "sg-e", t: "Utilidad Antes de Impuestos (UAI)", cls: "sub" },
      { s: "(−)", c: "sg-m", t: "Impuesto a la Renta (menor por intereses)" },
      { s: "(=)", c: "sg-e", t: "Utilidad Después de Impuestos (UDI)", cls: "sub" },
      { s: "(+)", c: "sg-p", t: "Reverso Depreciación" },
      { s: "(−)", c: "sg-m", t: "Inversión Inicial + CT (Año 0)" },
      { s: "(+)", c: "sg-p", t: "Préstamo Bancario Recibido (Año 0)", cls: "hlt" },
      { s: "(−)", c: "sg-m", t: "Amortización Capital Deuda (Años 1..n)", cls: "hlt" },
      { s: "(+)", c: "sg-p", t: "Valor de Desecho + Recup. 100% CT (Año N)" },
      { s: "(=)", c: "sg-e", t: "FLUJO DEL INVERSIONISTA (FINANCIADO)", cls: "tot" }
    ],
    foot: "<b>Diferencia clave (en amarillo):</b> Solo los Intereses van ANTES de impuestos; Préstamo (+) y Amortización (−) van DESPUÉS."
  },
  {
    title: "3. Flujo Social SNI 2026 (MIDESO)",
    badge: "Descuenta a TSD 5,5%",
    col: "#7C3AED",
    rows: [
      { s: "(+)", c: "sg-p", t: "VSP (AD + LR, o Q × P_CIF × FCSD si imp.)", cls: "hlt" },
      { s: "(+)", c: "sg-p", t: "Externalidades Positivas (Ahorro Curaco / CO2)", cls: "hlt" },
      { s: "(−)", c: "sg-m", t: "Insumos Nac. (÷1,19) e Imp. (× FCSD ÷ 1,19(1+t))" },
      { s: "(−)", c: "sg-m", t: "Mano de Obra × FCSMO (0,97 · 0,95 · 0,91)", cls: "hlt" },
      { s: "$0",  c: "sg-m", t: "SIN Depreciación · SIN Impuestos · SIN Deuda" },
      { s: "(−)", c: "sg-m", t: "Inversión Social I_S + CT Social (Año 0)" },
      { s: "(+)", c: "sg-p", t: "Valor Residual Social + Recup. CT (Año N)" },
      { s: "(=)", c: "sg-e", t: "BENEFICIO NETO SOCIAL (→ VANS 5,5%)", cls: "tot" }
    ],
    foot: "<b>Regla SNI 2026:</b> Se eliminan transferencias internas (IVA, arancel, renta, subsidios) y se valoran recursos al costo de oportunidad."
  }
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
    const fljGrid = document.getElementById("mec-flujos-grid");
    if (fljGrid) {
      fljGrid.innerHTML = "";
      for (const flj of FLUJOS_PLANTILLAS_PROY) {
        const fc = document.createElement("div");
        fc.className = "flj-card";
        fc.style.borderTopColor = flj.col;
        fc.onclick = function() { this.classList.toggle("revealed"); };
        const rowsHtml = flj.rows.map(r =>
          `<div class="flj-row${r.cls ? ' ' + r.cls : ''}"><span class="flj-sgn ${r.c}">${r.s}</span><span>${r.t}</span></div>`
        ).join("");
        fc.innerHTML = `
          <div class="flj-head">
            <span class="flj-title">${flj.title}</span>
            <span class="flj-badge" style="background:${flj.col};">${flj.badge}</span>
          </div>
          <div class="blind-cover">Haz clic para revelar el orden vertical y signos del flujo</div>
          <div class="flj-rows">${rowsHtml}</div>
          <div class="flj-foot">${flj.foot}</div>`;
        fljGrid.appendChild(fc);
      }
    }
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
  cont.querySelectorAll(".f-card, .flj-card, .s-card").forEach(el => el.classList.remove("revealed"));
}
function filtrarMec(cat, btn) {
  mecFilter = cat;
  btn.parentElement.querySelectorAll(".flt-btn").forEach(b => b.classList.remove("active"));
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

// === MOTOR DE IMPRESIÓN CARTA (COMPLETO + EN BLANCO LÁPIZ + DESCARGA .HTML FUERA DEL IFRAME) ===
function buildHojaMecanicaPrintHtml(esBlanco) {
  const cont = document.getElementById("mec-container");
  if (!cont) return "";
  const clone = cont.cloneNode(true);
  clone.classList.remove("blind-mode");
  clone.querySelectorAll(".chk-btn, .blind-cover").forEach(n => n.remove());
  clone.querySelectorAll(".f-card, .flj-card, .s-card").forEach(n => n.classList.remove("mastered", "revealed"));

  if (esBlanco) {
    clone.querySelectorAll("details").forEach(n => n.remove());
    clone.querySelectorAll(".f-card").forEach(card => {
      const body = card.querySelector(".f-body");
      if (body) {
        body.innerHTML = '<div class="blank-lines"><div class="bline"></div><div class="bline"></div></div>';
      }
    });
    clone.querySelectorAll(".flj-card").forEach(card => {
      const rowsWrap = card.querySelector(".flj-rows");
      if (rowsWrap) {
        const count = Math.max(6, rowsWrap.querySelectorAll(".flj-row").length);
        let h = "";
        for (let i = 0; i < count; i++) {
          h += '<div class="blank-flj-row"><span class="bf-sgn">( &nbsp; )</span><span class="bf-line"></span></div>';
        }
        rowsWrap.innerHTML = h;
      }
      const foot = card.querySelector(".flj-foot");
      if (foot) foot.innerHTML = '<b>Tasa / Regla clave:</b> _________________________________________________';
    });
    clone.querySelectorAll(".s-card").forEach(card => {
      card.querySelectorAll(".sk-lbl").forEach(n => n.remove());
      const sub = card.querySelector(".s-sub");
      if (sub) sub.innerHTML = '<b>Interpretación:</b> ____________________________________';
    });
  } else {
    clone.querySelectorAll("details").forEach(d => d.setAttribute("open", "open"));
  }

  const modoBadge = esBlanco ? "HOJA DE PRÁCTICA EN BLANCO (LÁPIZ)" : "FORMULARIO COMPLETO DE ESTUDIO";
  const metaAlumno = esBlanco
    ? '<div class="pr-student"><span><b>Nombre:</b> ______________________________________</span><span><b>Fecha:</b> ____/____/2026</span><span><b>Autoevaluación:</b> _____ / _____</span></div>'
    : '';
  const tituloDoc = `Hoja Mecánica — Evaluación Integrada de Proyectos (FDIC26) (${esBlanco ? "En Blanco" : "Completa"})`;

  return `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<title>${tituloDoc}</title>
<style>
  @page { size: letter portrait; margin: 10mm 11mm; }
  * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }
  body { margin: 0; padding: 14px; background: #FFFFFF; color: #0F172A; }
  .no-print {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
    background: #0F172A; color: #FFFFFF; padding: 9px 14px; border-radius: 7px; margin-bottom: 12px;
  }
  .no-print button {
    border: 1px solid #93C5FD; background: #1D4ED8; color: #FFFFFF;
    padding: 6px 12px; border-radius: 5px; font-size: 12px; font-weight: 700; cursor: pointer;
  }
  .no-print button.sec { background: #334155; border-color: #64748B; }
  .pr-header {
    display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;
    border-bottom: 2px solid #0F172A; padding-bottom: 7px; margin-bottom: 9px;
  }
  .pr-title { font-size: 14px; font-weight: 800; color: #0F172A; }
  .pr-sub { font-size: 10.5px; color: #334155; margin-top: 2px; }
  .pr-badge {
    font-size: 9.8px; font-weight: 800; color: #FFFFFF; background: ${esBlanco ? "#0F172A" : "#1E3A8A"};
    padding: 4px 9px; border-radius: 4px; white-space: nowrap;
  }
  .pr-student {
    display: flex; justify-content: space-between; gap: 12px; font-size: 10.5px; color: #0F172A;
    margin-bottom: 9px; padding: 5px 8px; background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 4px;
  }
  .sec-title {
    font-size: 11px; font-weight: 800; color: #0F172A; background: #F1F5F9;
    border-left: 3.5px solid #0F172A; padding: 4px 8px; border-radius: 3px;
    margin: 9px 0 6px 0; display: flex; justify-content: space-between; align-items: center;
  }
  .sec-title span:nth-child(2) { display: none; }
  .mec-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 7px; margin-bottom: 10px; }
  .f-card {
    border: 1px solid #94A3B8; border-left: 3px solid #0F172A; border-radius: 4px;
    padding: 6px 8px; background: #FFFFFF; break-inside: avoid; page-break-inside: avoid;
  }
  .f-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
  .f-title { font-size: 10.5px; font-weight: 800; color: #0F172A; }
  .f-cat { font-size: 8.8px; font-weight: 700; color: #334155; background: #E2E8F0; padding: 1px 5px; border-radius: 3px; margin-right: 4px; }
  .f-body { background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 3px; padding: 5px 7px; }
  .f-eq {
    font-family: "Cambria Math", "Times New Roman", Georgia, serif;
    font-size: 12.2px; font-weight: 700; color: #0F172A; display: block; line-height: 1.55;
  }
  .f-eq sup { font-size: 0.72em; vertical-align: super; line-height: 0; }
  .f-eq sub { font-size: 0.72em; vertical-align: sub; line-height: 0; }
  .frac { display: inline-flex; flex-direction: column; align-items: center; vertical-align: middle; margin: 0 2px; font-size: 0.88em; line-height: 1.1; }
  .frac .num { border-bottom: 1.2px solid #0F172A; padding: 0 3px 1px 3px; text-align: center; }
  .frac .den { padding: 1px 3px 0 3px; text-align: center; }
  .f-rule { font-size: 9.2px; color: #334155; margin-top: 3px; line-height: 1.3; }
  .blank-lines { padding: 2px 0; }
  .bline { height: 21px; border-bottom: 1px dashed #94A3B8; }
  .flj-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; margin-bottom: 10px; }
  .flj-card {
    border: 1px solid #94A3B8; border-top: 3px solid #0F172A; border-radius: 4px;
    padding: 6px 8px; background: #FFFFFF; break-inside: avoid; page-break-inside: avoid;
  }
  .flj-head { display: flex; justify-content: space-between; align-items: center; gap: 4px; margin-bottom: 5px; }
  .flj-title { font-size: 10px; font-weight: 800; color: #0F172A; }
  .flj-badge { font-size: 8.5px; font-weight: 800; color: #FFFFFF; background: #1E293B; padding: 1.5px 5px; border-radius: 6px; }
  .flj-rows { display: flex; flex-direction: column; gap: 2px; }
  .flj-row { display: flex; gap: 5px; font-size: 9.2px; padding: 2px 4px; border-radius: 3px; background: #F8FAFC; }
  .flj-row.sub { background: #EFF6FF; font-weight: 800; border-top: 1px solid #93C5FD; border-bottom: 1px solid #93C5FD; }
  .flj-row.tot { background: #DCFCE7; font-weight: 800; border: 1px solid #4ADE80; }
  .flj-row.hlt { background: #FEF3C7; font-weight: 700; }
  .flj-sgn { font-family: Consolas, monospace; font-weight: 800; min-width: 24px; }
  .sg-p { color: #15803D; } .sg-m { color: #DC2626; } .sg-e { color: #1D4ED8; }
  .flj-foot { font-size: 8.8px; color: #334155; margin-top: 4px; border-top: 1px dashed #CBD5E1; padding-top: 4px; line-height: 1.3; }
  .blank-flj-row { display: flex; align-items: flex-end; gap: 5px; height: 18px; }
  .bf-sgn { font-family: Consolas, monospace; font-size: 9.5px; color: #475569; min-width: 26px; }
  .bf-line { flex: 1; border-bottom: 1px dashed #94A3B8; height: 12px; }
  .skel-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 7px; }
  .s-card {
    border: 1px solid #94A3B8; border-radius: 4px; padding: 6px 7px; background: #FFFFFF;
    break-inside: avoid; page-break-inside: avoid;
  }
  .s-title { font-size: 9.8px; font-weight: 800; color: #0F172A; margin-bottom: 3px; }
  .s-card svg { width: 100%; height: auto; display: block; }
  .s-sub { font-size: 8.8px; color: #334155; margin-top: 3px; line-height: 1.28; }
  .enun-box { margin-top: 8px; border: 1px solid #94A3B8; border-left: 3px solid #0F172A; border-radius: 4px; padding: 6px 9px; font-size: 9.5px; break-inside: avoid; }
  .enun-box summary { font-weight: 800; list-style: none; margin-bottom: 4px; }
  .enun-badge { display: none; }
  @media print {
    body { padding: 0; }
    .no-print { display: none !important; }
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  }
</style>
</head>
<body>
  <div class="no-print">
    <div><b>Hoja Mecánica Lista para Impresión Carta</b> — Evaluación Integrada de Proyectos (FDIC26) (${esBlanco ? "Modo En Blanco para Lápiz" : "Formulario Completo"})</div>
    <div style="display:flex;gap:8px;">
      <button onclick="window.print()">Imprimir / Guardar PDF (Carta)</button>
      <button class="sec" onclick="window.close()">Cerrar</button>
    </div>
  </div>
  <div class="pr-header">
    <div>
      <div class="pr-title">HOJA MECÁNICA DE ESTUDIO — Evaluación Integrada de Proyectos (FDIC26)</div>
      <div class="pr-sub">Universidad de Los Lagos · Ingeniería Comercial 2026 · Dra. Luz María Ferrada B.</div>
    </div>
    <div class="pr-badge">${modoBadge}</div>
  </div>
  ${metaAlumno}
  ${clone.innerHTML}
</body>
</html>`;
}

function showMecPrintMsg(txt) {
  const elMsg = document.getElementById("mec-print-msg");
  if (!elMsg) return;
  elMsg.innerHTML = txt;
  elMsg.style.display = "block";
}

function descargarHojaMecanica(esBlancoOverride) {
  const esBlanco = typeof esBlancoOverride === "boolean" ? esBlancoOverride : !!mecBlind;
  const htmlDoc = buildHojaMecanicaPrintHtml(esBlanco);
  const blob = new Blob([htmlDoc], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `Hoja_Mecanica_Proyectos_FDIC26_${esBlanco ? "En_Blanco_Lapiz" : "Completa"}_Carta.html`;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 1200);
  showMecPrintMsg(
    `Archivo descargado (<b>${a.download}</b>). Ábrelo en tu navegador y presiona <b>Ctrl + P → Guardar como PDF</b> (formato Carta limpio, sin recortes).`
  );
}

function imprimirHojaMecanica(esBlanco) {
  const htmlDoc = buildHojaMecanicaPrintHtml(esBlanco);
  try {
    const win = window.open("", "_blank", "width=1020,height=780");
    if (win && win.document) {
      win.document.open();
      win.document.write(htmlDoc);
      win.document.close();
      win.focus();
      setTimeout(() => { try { win.print(); } catch (e) {} }, 350);
      showMecPrintMsg(
        `Se abrió la vista limpia tamaño Carta (${esBlanco ? "<b>En Blanco para Lápiz</b>" : "<b>Formulario Completo</b>"}). Si no aparece el diálogo automáticamente, usa el botón superior de la nueva pestaña.`
      );
      return;
    }
  } catch (err) {}
  descargarHojaMecanica(esBlanco);
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
  const prVf = document.getElementById("pr-vf-list");
  if (prVf) prVf.innerHTML = wrap.innerHTML;
  const prSc = document.getElementById("pr-vf-score");
  if (prSc) prSc.textContent = `Puntaje: ${okCount} / ${QUIZ_VF_DATA.length}`;
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


// ============================================================================
// 11. CASOS DE CLASE: CONVERSIÓN SOCIAL ÍTEM A ÍTEM (EJ. 1) Y SALMÓN (EJ. 2)
// ============================================================================
let cl1State = { moc: 1.0, mosc: 0.8, monc: 0.7, intSocial: true };

function selCasoClase(key, btn) {
  document.querySelectorAll(".cl-sec").forEach(d => d.classList.remove("active"));
  document.getElementById("cl-sec-" + key).classList.add("active");
  btn.parentElement.querySelectorAll(".act-btn").forEach(b => b.classList.remove("primary"));
  btn.classList.add("primary");
  if (key === "ej1") drawClaseEj1();
  if (key === "ej2") drawClaseEj2();
}

function presetCl1(modo) {
  if (modo === "pizarra") {
    cl1State = { moc: 1.0, mosc: 0.8, monc: 0.7, intSocial: true };
    document.getElementById("cl1-ip").value = 2000;
    document.getElementById("cl1-cp").value = 1000;
    document.getElementById("cl1-r").value = 12.0;
    document.getElementById("cl1-div").value = 1.06;
    document.getElementById("cl1-ar").value = 11.0;
  } else {
    cl1State = { moc: 0.97, mosc: 0.95, monc: 0.91, intSocial: false };
    document.getElementById("cl1-ip").value = 2000;
    document.getElementById("cl1-cp").value = 1000;
    document.getElementById("cl1-r").value = 5.5;
    document.getElementById("cl1-div").value = 1.00;
    document.getElementById("cl1-ar").value = 6.0;
  }
  drawClaseEj1();
}

function toggleInteresCl1() {
  cl1State.intSocial = !cl1State.intSocial;
  drawClaseEj1();
}

function drawClaseEj1() {
  const ipMM = +document.getElementById("cl1-ip").value;
  const cpU = +document.getElementById("cl1-cp").value;
  const rPct = +document.getElementById("cl1-r").value, r = rPct / 100;
  const fcsd = +document.getElementById("cl1-div").value;
  const arPct = +document.getElementById("cl1-ar").value, ar = arPct / 100;
  const iva = 0.19;
  const ip = ipMM * 1e6;

  document.getElementById("cl1-ip-v").textContent = "$" + fmtInt(ipMM) + "M";
  document.getElementById("cl1-cp-v").textContent = "$" + fmtInt(cpU);
  document.getElementById("cl1-r-v").textContent = fmtDec(rPct, 1) + "%";
  document.getElementById("cl1-div-v").textContent = fmtDec(fcsd, 2);
  document.getElementById("cl1-ar-v").textContent = fmtDec(arPct, 1) + "%";
  const bInt = document.getElementById("cl1-btn-int");
  if (bInt) bInt.textContent = cl1State.intSocial ? "Intereses: Pizarra (÷1,19) ⇄ Estricto ($0)" : "Intereses: Estricto Social ($0) ⇄ Pizarra";

  const fImp = fcsd / ((1 + iva) * (1 + ar));
  const fNac = 1 / (1 + iva);
  const fInt = cl1State.intSocial ? fNac : 0.0;

  const invSpec = [
    ["MO Calificada", 0.07, cl1State.moc, fmtDec(cl1State.moc, 2)],
    ["MO Semicalificada", 0.09, cl1State.mosc, fmtDec(cl1State.mosc, 2)],
    ["MO No Calificada", 0.17, cl1State.monc, fmtDec(cl1State.monc, 2)],
    ["Combust. y Lubricantes", 0.05, fImp, `${fmtDec(fcsd,2)}/(1,19·${fmtDec(1+ar,2)})`],
    ["Repuestos Importados", 0.20, fImp, `${fmtDec(fcsd,2)}/(1,19·${fmtDec(1+ar,2)})`],
    ["Repuestos Nacionales", 0.15, fNac, "1 / 1,19"],
    ["Depreciación Legal", 0.10, 0.0, "0 (Se excluye)"],
    ["Intereses", 0.05, fInt, cl1State.intSocial ? "1 / 1,19" : "0 (Transferencia)"],
    ["Gastos Varios", 0.12, fNac, "1 / 1,19"]
  ];
  const cosSpec = [
    ["MO Calificada", 0.08, cl1State.moc, fmtDec(cl1State.moc, 2)],
    ["MO Semicalificada", 0.10, cl1State.mosc, fmtDec(cl1State.mosc, 2)],
    ["MO No Calificada", 0.05, cl1State.monc, fmtDec(cl1State.monc, 2)],
    ["Combust. y Lubricantes", 0.35, fImp, `${fmtDec(fcsd,2)}/(1,19·${fmtDec(1+ar,2)})`],
    ["Repuestos Importados", 0.12, fImp, `${fmtDec(fcsd,2)}/(1,19·${fmtDec(1+ar,2)})`],
    ["Repuestos Nacionales", 0.15, fNac, "1 / 1,19"],
    ["Depreciación Legal", 0.05, 0.0, "0 (Se excluye)"],
    ["Intereses", 0.03, fInt, cl1State.intSocial ? "1 / 1,19" : "0 (Transferencia)"],
    ["Gastos Varios", 0.07, fNac, "1 / 1,19"]
  ];

  let isTot = 0, hInv = `<table class="cl-tbl"><thead><tr><th>Ítem Inversión</th><th>%</th><th>CP ($MM)</th><th>Factor FC</th><th>CS ($MM)</th></tr></thead><tbody>`;
  for (const [nm, pct, fc, lbl] of invSpec) {
    const cpV = ip * pct, csV = cpV * fc;
    isTot += csV;
    hInv += `<tr class="${fc === 0 ? 'row-zero' : ''}"><td>${nm}</td><td>${Math.round(pct*100)}%</td><td>$${fmtDec(cpV/1e6,1)}M</td><td>${lbl}</td><td>$${fmtDec(csV/1e6,2)}M</td></tr>`;
  }
  hInv += `<tr class="row-tot"><td>TOTAL INVERSIÓN</td><td>100%</td><td>$${fmtInt(ipMM)}M</td><td>${fmtDec((isTot/ip)*100,1)}%</td><td>$${fmtDec(isTot/1e6,2)}M</td></tr></tbody></table>`;
  document.getElementById("cl1-tbl-inv").innerHTML = hInv;

  let csUnit = 0, hCos = `<table class="cl-tbl"><thead><tr><th>Ítem Costo Unit.</th><th>%</th><th>CP ($/u)</th><th>Factor FC</th><th>CS ($/u)</th></tr></thead><tbody>`;
  for (const [nm, pct, fc, lbl] of cosSpec) {
    const cpV = cpU * pct, csV = cpV * fc;
    csUnit += csV;
    hCos += `<tr class="${fc === 0 ? 'row-zero' : ''}"><td>${nm}</td><td>${Math.round(pct*100)}%</td><td>$${fmtDec(cpV,1)}</td><td>${lbl}</td><td>$${fmtDec(csV,2)}</td></tr>`;
  }
  hCos += `<tr class="row-tot"><td>TOTAL COSTO UNIT.</td><td>100%</td><td>$${fmtInt(cpU)}</td><td>${fmtDec((csUnit/cpU)*100,1)}%</td><td>$${fmtDec(csUnit,2)}</td></tr></tbody></table>`;
  document.getElementById("cl1-tbl-cos").innerHTML = hCos;

  const q0 = 100000, q1 = 250000, p0 = 2000, p1 = 100;
  const ad = (q1 - q0) * (p0 + p1) / 2;
  const lr = q0 * csUnit;
  const vsp = ad + lr;
  const vpVsp = vsp / r;
  const vans = -isTot + vpVsp;

  document.getElementById("cl1-enun").innerHTML =
    `Un proyecto expande la oferta desde <b>q<sub>0</sub> = 100.000 u/año</b> (P<sub>0</sub> = $2.000) hasta <b>q<sub>1</sub> = 250.000 u/año</b> (P<sub>1</sub> = $100), ` +
    `con inversión privada <b>IP = $${fmtInt(ipMM)} MM</b> y costo privado unitario <b>C = $${fmtInt(cpU)}/u</b>. ` +
    `Convirtiendo cada partida con MOC=${fmtDec(cl1State.moc,2)}, MOSC=${fmtDec(cl1State.mosc,2)}, MONC=${fmtDec(cl1State.monc,2)}, FCSD=${fmtDec(fcsd,2)}, arancel ${fmtDec(arPct,1)}% e IVA 19% (y <b>Depreciación Legal = $0</b>), se obtiene <b>I<sub>S</sub> = $${fmtDec(isTot/1e6,2)} MM</b> y <b>CS = $${fmtDec(csUnit,2)}/u</b>.`;

  document.getElementById("cl1-k-is").textContent = `$${fmtDec(isTot/1e6, 2)}M`;
  document.getElementById("cl1-k-is2").textContent = `Ahorro social: $${fmtDec((ip - isTot)/1e6, 1)}M`;
  document.getElementById("cl1-k-cs").textContent = `$${fmtDec(csUnit, 2)}/u`;
  document.getElementById("cl1-k-cs2").textContent = `vs CP = $${fmtInt(cpU)}/u (Dep=$0)`;
  document.getElementById("cl1-k-vsp").textContent = `$${fmtDec(vsp/1e6, 2)}M/año`;
  document.getElementById("cl1-k-adlr").textContent = `AD $${fmtDec(ad/1e6,1)}M + LR $${fmtDec(lr/1e6,1)}M`;
  document.getElementById("cl1-k-vans").textContent = `${vans>=0?"+":"-"}$${fmtDec(Math.abs(vans)/1e6, 2)}M`;
  document.getElementById("cl1-k-dec").textContent = vans >= 0 ? "CONVIENE A LA SOCIEDAD (VANS > 0)" : "NO CONVIENE (VANS < 0)";

  renderFormulaStrip("cl1-fstrip", [
    {
      lbl: "Factor Bienes Importados (Divisa + IVA + Arancel)", col: "#7C3AED",
      eq: `F<sub>imp</sub> = ${mFrac('<span class="sym-p">R* / R</span>', '(1 + IVA)(1 + <span class="sym-o">t<sub>a</sub></span>)')}`,
      sub: `F<sub>imp</sub> = ${mFrac(eChip(fmtDec(fcsd,2),fcsd,"cl1_div","0.01","vc-p","Factor Divisa R*/R"), "1,19 · (1 + " + eChip(fmtDec(arPct,1)+"%",arPct,"cl1_ar","1","vc-o","Arancel Import. (%)") + ")")} = ${rChip(fmtDec(fImp,4))}`,
      note: `Costo priv. base = ${eChip("$"+fmtInt(cpU),cpU,"cl1_cp","50","vc-b","Costo Unitario Privado C")} ⇒ CS = <b>$${fmtDec(csUnit,2)}/u</b>`
    },
    {
      lbl: "Valor Social de la Producción (VSP = AD + LR)", col: "#059669",
      eq: `VSP = (q<sub>1</sub>−q<sub>0</sub>)·${mFrac("P<sub>0</sub>+P<sub>1</sub>","2")} + q<sub>0</sub>·CS`,
      sub: `VSP = 150k·$1.050 + 100k·$${fmtDec(csUnit,2)} = ${rChip("$"+fmtDec(vsp/1e6,2)+"M/año")}`,
      note: `AD (Trapecio Demanda) = $${fmtDec(ad/1e6,2)}M | LR (Rectángulo) = $${fmtDec(lr/1e6,2)}M`
    },
    {
      lbl: "VANS a Perpetuidad (−IS + VSP / r)", col: "#1D4ED8",
      eq: `VANS = −I<sub>S</sub> + ${mFrac("VSP", '<span class="sym-r">r</span>')}`,
      sub: `VANS = −$${fmtDec(isTot/1e6,2)}M + ${mFrac("$"+fmtDec(vsp/1e6,2)+"M", eChip(fmtDec(rPct,1)+"%",rPct,"cl1_r","0.5","vc-r","Tasa descuento r (%)"))} = ${rChip((vans>=0?"+":"-")+"$"+fmtDec(Math.abs(vans)/1e6,2)+"M", vans < 0)}`,
      note: `Inversión privada IP = ${eChip("$"+fmtInt(ipMM)+"M",ipMM,"cl1_ip","100","vc-b","Inversión Privada IP ($MM)")} → I<sub>S</sub> = $${fmtDec(isTot/1e6,2)}M`
    }
  ]);

  // SVG estilo pizarra: réplica fiel del diagrama de la pizarra del cuaderno
  const svg = document.getElementById("svg-cl1");
  svg.innerHTML = "";
  addDefs(svg);
  const M = { l: 74, r: 44, t: 30, b: 50 }, W = 980, H = 355;
  const sx = q => M.l + (q / 290000) * (W - M.l - M.r);
  const sy = p => H - M.b - (p / 2400) * (H - M.t - M.b);

  for (const pv of [0, 500, 1000, 1500, 2000]) {
    el("line", { x1: M.l, y1: sy(pv), x2: W - M.r, y2: sy(pv), stroke: "#E2E8F0" }, svg);
    const ty = el("text", { x: M.l - 8, y: sy(pv) + 4, fill: "#475569", "font-size": "10.5", "text-anchor": "end" }, svg);
    ty.textContent = "$" + fmtInt(pv);
  }
  drawAxesPizarra(svg, M.l, M.t, W - M.r, H - M.b, "Precio / Costo ($)", "Cantidad (q u/año)");

  // Área LR: rectángulo [0..q0] x [0..csUnit]
  el("rect", { x: sx(0), y: sy(csUnit), width: sx(q0) - sx(0), height: sy(0) - sy(csUnit), fill: "rgba(124,58,237,0.22)", stroke: "#7C3AED", "stroke-width": "1.2" }, svg);
  // Área AD: trapecio [q0..q1] bajo Demanda desde P0=2000 hasta P1=100
  const ptsAD = `${sx(q0)},${sy(0)} ${sx(q0)},${sy(p0)} ${sx(q1)},${sy(p1)} ${sx(q1)},${sy(0)}`;
  el("polygon", { points: ptsAD, fill: "rgba(5,150,105,0.22)", stroke: "#059669", "stroke-width": "1.2" }, svg);

  // Curva de Demanda D y Cmg Social horizontal
  el("line", { x1: sx(80000), y1: sy(2253), x2: sx(260000), y2: sy(0), stroke: "#1D4ED8", "stroke-width": "3" }, svg);
  el("line", { x1: sx(0), y1: sy(csUnit), x2: sx(270000), y2: sy(csUnit), stroke: "#DC2626", "stroke-width": "2.4", "stroke-dasharray": "7,4" }, svg);
  el("line", { x1: M.l, y1: sy(p0), x2: sx(q0), y2: sy(p0), stroke: "#64748B", "stroke-dasharray": "4,3" }, svg);
  el("line", { x1: M.l, y1: sy(p1), x2: sx(q1), y2: sy(p1), stroke: "#64748B", "stroke-dasharray": "4,3" }, svg);

  el("circle", { cx: sx(q0), cy: sy(p0), r: 6, fill: "#1D4ED8", stroke: "#FFF", "stroke-width": "1.8" }, svg);
  el("circle", { cx: sx(q1), cy: sy(p1), r: 6, fill: "#059669", stroke: "#FFF", "stroke-width": "1.8" }, svg);

  drawPill(svg, sx(50000), sy(csUnit / 2), `LR = $${fmtDec(lr/1e6,2)}M`, "#6D28D9", "#FAF5FF", "middle", "11");
  drawPill(svg, sx(162000), sy(680), `AD = $${fmtDec(ad/1e6,2)}M`, "#065F46", "#ECFDF5", "middle", "11");
  drawPill(svg, sx(232000), sy(csUnit) - 14, `Cmg Social = $${fmtDec(csUnit,2)}`, "#DC2626", "#FEF2F2", "middle", "10.3");
  drawPill(svg, sx(256000), sy(260), "Demanda (D)", "#1D4ED8", "#EFF6FF", "end", "10.5");

  const tq0 = el("text", { x: sx(q0), y: H - M.b + 17, fill: "#0F172A", "font-size": "11", "font-weight": "800", "text-anchor": "middle" }, svg);
  tq0.textContent = "q0 = 100.000";
  const tq1 = el("text", { x: sx(q1), y: H - M.b + 17, fill: "#0F172A", "font-size": "11", "font-weight": "800", "text-anchor": "middle" }, svg);
  tq1.textContent = "q1 = 250.000";

  renderPedBox("ped-cl1",
    `Al convertir el presupuesto privado a precios sociales, la inversión baja de <b>$${fmtInt(ipMM)} MM</b> a <b>I<sub>S</sub> = $${fmtDec(isTot/1e6,2)} MM</b> y el costo unitario cae de $${fmtInt(cpU)} a <b>$${fmtDec(csUnit,2)}/u</b>. Con VSP = $${fmtDec(vsp/1e6,2)} MM/año en perpetuidad al ${fmtDec(rPct,1)}%, el proyecto logra <b>VANS = ${vans>=0?"+":"-"}$${fmtDec(Math.abs(vans)/1e6,2)} MM</b>.`,
    `<b>¿Por qué la Depreciación desaparece (Factor = 0)?</b> Porque la depreciación contable no consume recursos reales de la sociedad cada año; el sacrificio de recursos reales ocurrió completo en t=0 al construir/comprar el activo (<b>I<sub>S</sub></b>). Restarla de nuevo contaría doble el costo del capital.`,
    `<b>Clave de pizarra para la prueba:</b> revisa siempre la columna de porcentajes (debe sumar 100%). Primero limpia el IVA (÷1,19) y el arancel (÷(1+t)) en los ítems transables, luego aplica el factor divisa (×R*/R), y recuerda que <b>LR = q<sub>0</sub>·CS</b> usa el costo social ($${fmtDec(csUnit,2)}), NO el costo privado ($${fmtInt(cpU)}).`
  );
}

// --- CASO B: EJERCICIO 2 (SALMÓN — SUSTITUCIÓN DE IMPORTACIONES SNI 2026) ---
function presetCl2(modo) {
  if (modo === "pizarra") {
    document.getElementById("cl2-cif").value = 450;
    document.getElementById("cl2-pin").value = 500;
    document.getElementById("cl2-q").value = 8.0;
    document.getElementById("cl2-ar").value = 1.0;
    document.getElementById("cl2-rp").value = 12.0;
  } else if (modo === "arancel6") {
    document.getElementById("cl2-cif").value = 450;
    document.getElementById("cl2-pin").value = 500;
    document.getElementById("cl2-q").value = 8.0;
    document.getElementById("cl2-ar").value = 6.0;
    document.getElementById("cl2-rp").value = 12.0;
  } else {
    document.getElementById("cl2-cif").value = 450;
    document.getElementById("cl2-pin").value = 410;
    document.getElementById("cl2-q").value = 8.0;
    document.getElementById("cl2-ar").value = 1.0;
    document.getElementById("cl2-rp").value = 12.0;
  }
  drawClaseEj2();
}

function drawClaseEj2() {
  const pCif = +document.getElementById("cl2-cif").value;
  const pInt = +document.getElementById("cl2-pin").value;
  const qTon = +document.getElementById("cl2-q").value, qKg = qTon * 1000;
  const arPct = +document.getElementById("cl2-ar").value, ar = arPct / 100;
  const rpPct = +document.getElementById("cl2-rp").value, rp = rpPct / 100;
  const tsd = 0.055, n = 40, iva = 0.19, moc = 0.97, monc = 0.91, fcsd = 1.00;

  document.getElementById("cl2-cif-v").textContent = "US$ " + fmtInt(pCif);
  document.getElementById("cl2-pin-v").textContent = "US$ " + fmtInt(pInt);
  document.getElementById("cl2-q-v").textContent = fmtDec(qTon, 1) + " ton";
  document.getElementById("cl2-ar-v").textContent = fmtDec(arPct, 1) + "%";
  document.getElementById("cl2-r-v").textContent = `5,5% / ${fmtDec(rpPct,0)}%`;

  // Social (SNI 2026)
  const invAfSoc = 1000000 / ((1 + iva) * (1 + ar)) * fcsd;
  const invMocSoc = 400000 * moc;
  const isTot = invAfSoc + invMocSoc;

  const csNac = 100 / (1 + iva);
  const csImp = 100 / ((1 + iva) * (1 + ar)) * fcsd;
  const csMoc = 50 * moc;
  const csMonc = 150 * monc;
  const csKg = csNac + csImp + csMoc + csMonc;

  const vspAnual = qKg * pCif * fcsd;
  const csAnual = qKg * csKg;
  const bnSoc = vspAnual - csAnual;
  const facAnuSoc = (1 - Math.pow(1 + tsd, -n)) / tsd;
  const pvBnSoc = bnSoc * facAnuSoc;
  const vans = -isTot + pvBnSoc;

  // Privado (Neto IVA, 27% Impuesto a la Renta + Depreciación lineal 40 años)
  const invAfPrivNeto = 1000000 / (1 + iva);
  const invPrivNeto = invAfPrivNeto + 400000;
  const depAnual = invAfPrivNeto / n;
  const pIntNeto = pInt / (1 + iva);
  const cKgPrivNeto = (100 / (1 + iva)) + (100 / (1 + iva)) + 50 + 150;
  const ebitdaPriv = qKg * (pIntNeto - cKgPrivNeto);
  const uaiPriv = ebitdaPriv - depAnual;
  const impPriv = uaiPriv > 0 ? uaiPriv * 0.27 : 0;
  const fcPrivAnual = (uaiPriv - impPriv) + depAnual;
  const facAnuPriv = (1 - Math.pow(1 + rp, -n)) / rp;
  const vanPriv = -invPrivNeto + fcPrivAnual * facAnuPriv;
  const pImpChile = pCif * (1 + ar) * (1 + iva);

  // Regla de Subsidio (4 Cuadrantes)
  let cuadrante = "", subEstado = 0, verdCls = "", resp1 = "", resp2 = "";
  if (vanPriv >= 0 && vans > 0) {
    cuadrante = "Cuadrante I (VAN_P ≥ 0 y VANS > 0)";
    subEstado = 0;
    verdCls = "";
    resp1 = "<b>NO corresponde financiamiento estatal.</b> El proyecto ya es privadamente rentable (VAN Privado = +US$ " + fmtInt(vanPriv) + ") y vende a US$ " + fmtInt(pInt) + "/kg, más barato que el producto importado puesto en Chile (US$ " + fmtDec(pImpChile,2) + "/kg).";
    resp2 = "<b>Aporte estatal óptimo = US$ 0.</b> Subsidiar un proyecto rentable para el privado sería una transferencia innecesaria de recursos fiscales.";
  } else if (vanPriv < 0 && vans > 0) {
    cuadrante = "Cuadrante II (VAN_P < 0 y VANS > 0)";
    subEstado = Math.min(Math.abs(vanPriv), vans);
    verdCls = " sub-si";
    resp1 = "<b>SÍ corresponde aporte/subsidio estatal.</b> Aunque el privado pierde dinero (VAN Privado = −US$ " + fmtInt(Math.abs(vanPriv)) + "), la sociedad gana VANS = +US$ " + fmtInt(vans) + " al ahorrar divisas y ocupar mano de obra.";
    resp2 = "<b>Aporte mínimo necesario = US$ " + fmtInt(Math.abs(vanPriv)) + "</b> (para llevar VAN_P a $0) y <b>tope máximo social = US$ " + fmtInt(vans) + "</b>.";
  } else {
    cuadrante = vans <= 0 && vanPriv < 0 ? "Cuadrante III (VAN_P < 0 y VANS ≤ 0)" : "Cuadrante IV (VAN_P ≥ 0 y VANS ≤ 0)";
    subEstado = 0;
    verdCls = " sub-rej";
    resp1 = "<b>NO financiar (VANS ≤ 0).</b> El proyecto no genera riqueza neta para el país bajo estos parámetros.";
    resp2 = "<b>Aporte estatal = US$ 0.</b> No se justifica destinar fondos públicos.";
  }

  document.getElementById("cl2-enun").innerHTML =
    `La industria del salmón importa <b>10 ton/año</b> de un antifúngico a <b>US$ ${fmtInt(pCif)}/kg CIF</b> más arancel (${fmtDec(arPct,1)}%) e IVA (19%), es decir <b>US$ ${fmtDec(pImpChile,2)}/kg</b> puesto en Chile. ` +
    `El proyecto local produce <b>${fmtDec(qTon,1)} ton/año (${fmtInt(qKg)} kg)</b> por <b>40 años</b> con inversión de US$ 1.000.000 (AF importado) + US$ 400.000 (MOC) y vende a <b>US$ ${fmtInt(pInt)}/kg</b>. ` +
    `Como ${fmtDec(qTon,1)} ton ≤ 10 ton importadas, cada kilo producido sustituye importaciones al precio CIF (<b>VSP = US$ ${fmtInt(vspAnual)}/año</b>).`;

  document.getElementById("cl2-k-is").textContent = "US$ " + fmtInt(isTot);
  document.getElementById("cl2-k-is2").textContent = `AF $${fmtInt(invAfSoc)} + MOC $${fmtInt(invMocSoc)}`;
  document.getElementById("cl2-k-bn").textContent = `${bnSoc>=0?"":"-"}US$ ${fmtInt(Math.abs(bnSoc))}/año`;
  document.getElementById("cl2-k-cs").textContent = `CS = US$ ${fmtDec(csKg,2)}/kg ($${fmtInt(csAnual)})`;
  document.getElementById("cl2-k-vans").textContent = `${vans>=0?"+":"-"}US$ ${fmtInt(Math.abs(vans))}`;
  document.getElementById("cl2-k-vsp").textContent = `VSP = US$ ${fmtInt(vspAnual)}/año`;
  document.getElementById("cl2-k-sub").textContent = subEstado > 0 ? "Aporte: US$ " + fmtInt(subEstado) : "Aporte: US$ 0";
  document.getElementById("cl2-k-vp").textContent = `VAN Priv (${fmtDec(rpPct,0)}%): ${vanPriv>=0?"+":"-"}US$ ${fmtInt(Math.abs(vanPriv))}`;

  const vBox = document.getElementById("cl2-verdict");
  vBox.className = "cl-verdict" + verdCls;
  vBox.innerHTML =
    `<div style="font-weight:800;margin-bottom:4px;">Veredicto de Cátedra — ${cuadrante}</div>` +
    `<div><b>1) ¿El Estado debiese aportar financiamiento?</b> ${resp1}</div>` +
    `<div style="margin-top:3px;"><b>2) ¿Cuánto es el aporte necesario para que invierta el privado?</b> ${resp2}</div>`;

  renderFormulaStrip("cl2-fstrip", [
    {
      lbl: "Inversión Social SNI 2026 (IS)", col: "#1D4ED8",
      eq: `I<sub>S</sub> = ${mFrac("1.000.000", '(1,19)(1+<span class="sym-o">t<sub>a</sub></span>)')} + 400.000·0,97`,
      sub: `I<sub>S</sub> = ${mFrac("1.000.000", "1,19·(1+" + eChip(fmtDec(arPct,1)+"%",arPct,"cl2_ar","0.5","vc-o","Arancel efectivo (%)") + ")")} + $388.000 = ${rChip("US$ "+fmtInt(isTot))}`,
      note: `AF Imp. = US$ ${fmtInt(invAfSoc)} · MOC (0,97) = US$ 388.000`
    },
    {
      lbl: "Beneficio Neto Social Anual (BN = VSP − CS)", col: "#7C3AED",
      eq: `BN = <span class="sym-t">Q</span> · (<span class="sym-b">P<sub>CIF</sub></span> − CS<sub>kg</sub>)`,
      sub: `BN = ${eChip(fmtDec(qTon,1)+"t",qTon,"cl2_q","0.5","vc-t","Producción anual (ton)")} · (${eChip("$"+fmtInt(pCif),pCif,"cl2_cif","10","vc-b","Precio CIF importación (US$/kg)")} − $${fmtDec(csKg,2)}) = ${rChip("US$ "+fmtInt(bnSoc)+"/año", bnSoc < 0)}`,
      note: `CS<sub>kg</sub> = 84,03 + ${fmtDec(csImp,2)} + 48,50 + 136,50 = <b>US$ ${fmtDec(csKg,2)}/kg</b>`
    },
    {
      lbl: "VANS (40a · TSD 5,5%) vs. VAN Privado", col: "#15803D",
      eq: `VANS = −I<sub>S</sub> + BN · ${mFrac("1 − (1,055)<sup>−40</sup>", "0,055")}`,
      sub: `VANS = −$${fmtInt(isTot)} + $${fmtInt(pvBnSoc)} = ${rChip((vans>=0?"+":"-")+"$"+fmtInt(Math.abs(vans)), vans < 0)}`,
      note: `Privado: P<sub>int</sub>=${eChip("$"+fmtInt(pInt),pInt,"cl2_pin","5","vc-o","Precio venta interno (US$/kg)")} · r<sub>p</sub>=${eChip(fmtDec(rpPct,0)+"%",rpPct,"cl2_rp","1","vc-r","Tasa privada (%)")} ⇒ VAN<sub>P</sub>=${vanPriv>=0?"+":"-"}$${fmtInt(Math.abs(vanPriv))}`
    }
  ]);

  document.getElementById("cl2-tbl-soc").innerHTML =
    `<table class="cl-tbl"><thead><tr><th>Partida</th><th>Privado (US$)</th><th>Factor SNI 2026</th><th>Social (US$)</th></tr></thead><tbody>` +
    `<tr><td>Inv. AF Importado</td><td>$1.000.000</td><td>1 / (1,19·${fmtDec(1+ar,3)})</td><td>$${fmtDec(invAfSoc,2)}</td></tr>` +
    `<tr><td>Inv. MO Calificada</td><td>$400.000</td><td>0,97 (MOC)</td><td>$${fmtDec(invMocSoc,2)}</td></tr>` +
    `<tr class="row-tot"><td>TOTAL INVERSIÓN (IS)</td><td>$1.400.000</td><td>—</td><td>$${fmtDec(isTot,2)}</td></tr>` +
    `<tr><td>Insumos Nacionales (/kg)</td><td>$100,00</td><td>1 / 1,19</td><td>$${fmtDec(csNac,2)}</td></tr>` +
    `<tr><td>Insumos Importados (/kg)</td><td>$100,00</td><td>1 / (1,19·${fmtDec(1+ar,3)})</td><td>$${fmtDec(csImp,2)}</td></tr>` +
    `<tr><td>MO Calificada (/kg)</td><td>$50,00</td><td>0,97 (MOC)</td><td>$${fmtDec(csMoc,2)}</td></tr>` +
    `<tr><td>MO No Calificada (/kg)</td><td>$150,00</td><td>0,91 (MONC)</td><td>$${fmtDec(csMonc,2)}</td></tr>` +
    `<tr class="row-tot"><td>COSTO UNIT. SOCIAL (/kg)</td><td>$400,00</td><td>× ${fmtInt(qKg)} kg</td><td>$${fmtDec(csKg,2)}</td></tr></tbody></table>`;

  document.getElementById("cl2-tbl-comp").innerHTML =
    `<table class="cl-tbl"><thead><tr><th>Indicador (40 años)</th><th>Privado (${fmtDec(rpPct,0)}%)</th><th>Social (TSD 5,5%)</th></tr></thead><tbody>` +
    `<tr><td>Inversión Año 0</td><td>−$${fmtInt(invPrivNeto)}</td><td>−$${fmtInt(isTot)}</td></tr>` +
    `<tr><td>Ingreso / VSP Anual</td><td>$${fmtInt(qKg*pIntNeto)} (neto)</td><td>$${fmtInt(vspAnual)} (CIF)</td></tr>` +
    `<tr><td>Costo Operativo Anual</td><td>−$${fmtInt(qKg*cKgPrivNeto)}</td><td>−$${fmtInt(csAnual)}</td></tr>` +
    `<tr><td>Impuesto Renta (27%)</td><td>−$${fmtInt(impPriv)}</td><td>$0 (Transferencia)</td></tr>` +
    `<tr><td>Flujo Neto Anual</td><td>$${fmtInt(fcPrivAnual)}</td><td>$${fmtInt(bnSoc)}</td></tr>` +
    `<tr class="row-tot"><td>VAN / VANS Total</td><td>${vanPriv>=0?"+":"-"}$${fmtInt(Math.abs(vanPriv))}</td><td>${vans>=0?"+":"-"}$${fmtInt(Math.abs(vans))}</td></tr>` +
    `<tr class="row-tot"><td>Aporte Estatal Óptimo</td><td colspan="2" style="text-align:center;">${subEstado>0 ? "SUBSIDIAR US$ "+fmtInt(subEstado)+" (Cuadrante II)" : "US$ 0 ("+cuadrante+")"}</td></tr></tbody></table>`;

  // Dual Pizarra SVG: Left = Mercado Importable (Ahorro Divisas), Right = VAN Privado vs VANS
  const svg = document.getElementById("svg-cl2");
  svg.innerHTML = "";
  addDefs(svg);
  const W = 980, H = 335;

  // Izquierda: Sustitución de Importaciones (0..11 ton)
  const L = { l: 64, r: 440, t: 30, b: 48 };
  const sxL = q => L.l + (q / 11.5) * (W - L.l - L.r);
  const syL = p => H - L.b - (p / 660) * (H - L.t - L.b);
  for (const pv of [0, 200, 400, 600]) {
    el("line", { x1: L.l, y1: syL(pv), x2: W - L.r, y2: syL(pv), stroke: "#E2E8F0" }, svg);
    const ty = el("text", { x: L.l - 7, y: syL(pv) + 4, fill: "#475569", "font-size": "10.5", "text-anchor": "end" }, svg);
    ty.textContent = "$" + pv;
  }
  drawAxesPizarra(svg, L.l, L.t, W - L.r, H - L.b, "US$ / kg", "Volumen (ton / año)");
  // Ahorro de divisas (VSP): rectángulo [0..qTon] x [0..pCif] y Costo Social [0..qTon] x [0..csKg]
  el("rect", { x: sxL(0), y: syL(pCif), width: sxL(qTon) - sxL(0), height: syL(csKg) - syL(pCif), fill: "rgba(21,128,61,0.26)", stroke: "#15803D", "stroke-width": "1.3" }, svg);
  el("rect", { x: sxL(0), y: syL(csKg), width: sxL(qTon) - sxL(0), height: syL(0) - syL(csKg), fill: "rgba(148,163,184,0.22)", stroke: "#64748B", "stroke-width": "1" }, svg);
  // Líneas de precios
  el("line", { x1: L.l, y1: syL(pImpChile), x2: sxL(10.8), y2: syL(pImpChile), stroke: "#DC2626", "stroke-width": "1.8", "stroke-dasharray": "5,3" }, svg);
  el("line", { x1: L.l, y1: syL(pInt), x2: sxL(10.8), y2: syL(pInt), stroke: "#EA580C", "stroke-width": "2" }, svg);
  el("line", { x1: L.l, y1: syL(pCif), x2: sxL(10.8), y2: syL(pCif), stroke: "#1D4ED8", "stroke-width": "2.6" }, svg);
  el("line", { x1: sxL(10), y1: L.t, x2: sxL(10), y2: H - L.b, stroke: "#0F172A", "stroke-dasharray": "4,3" }, svg);

  drawPill(svg, sxL(qTon / 2), syL((pCif + csKg) / 2), `BN = $${fmtInt(bnSoc)}/año`, "#166534", "#DCFCE7", "middle", "10.5");
  drawPill(svg, sxL(qTon / 2), syL(csKg / 2), `CS = $${fmtDec(csKg,1)}/kg`, "#334155", "#FFFFFF", "middle", "10");
  drawPill(svg, sxL(10.7), syL(pImpChile) - 10, `Imp. Chile $${fmtDec(pImpChile,0)}`, "#DC2626", "#FEF2F2", "end", "9.6");
  drawPill(svg, sxL(10.7), syL(pCif) + 13, `P_CIF $${pCif}`, "#1D4ED8", "#EFF6FF", "end", "9.8");
  const tQ10 = el("text", { x: sxL(10), y: H - L.b + 17, fill: "#0F172A", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, svg);
  tQ10.textContent = "10t (Imp. Chile)";
  const tQp = el("text", { x: sxL(qTon), y: H - L.b + 17, fill: "#1D4ED8", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, svg);
  tQp.textContent = `${fmtDec(qTon,1)}t (Proy)`;

  // Derecha: Comparación VAN Privado vs VANS (en Millones US$)
  const bxL = 610, bxR = 950, byT = 36, byB = 285;
  const maxBar = Math.max(Math.abs(vans), Math.abs(vanPriv), 2000000) * 1.2;
  const minBar = Math.min(vanPriv, vans, 0) * 1.25 - 500000;
  const syR = v => byB - ((v - minBar) / (maxBar - minBar)) * (byB - byT);
  const tR = el("text", { x: (bxL + bxR) / 2, y: 20, fill: "#0F172A", "font-size": "11.8", "font-weight": "800", "text-anchor": "middle" }, svg);
  tR.textContent = "VAN Privado vs. VANS Social (Millones US$)";
  el("line", { x1: bxL, y1: syR(0), x2: bxR, y2: syR(0), stroke: "#0F172A", "stroke-width": "1.6" }, svg);

  const compBars = [
    { x: 660, v: vanPriv, col: vanPriv >= 0 ? "#1D4ED8" : "#DC2626", lbl: `VAN Priv (${fmtDec(rpPct,0)}%)` },
    { x: 815, v: vans, col: vans >= 0 ? "#15803D" : "#DC2626", lbl: "VANS (TSD 5,5%)" }
  ];
  compBars.forEach(b => {
    const yT = syR(Math.max(0, b.v)), yB = syR(Math.min(0, b.v));
    el("rect", { x: b.x, y: yT, width: 84, height: Math.max(3, yB - yT), fill: b.col, rx: 4 }, svg);
    const tv = el("text", { x: b.x + 42, y: b.v >= 0 ? yT - 7 : yB + 14, fill: b.col, "font-size": "11", "font-weight": "800", "text-anchor": "middle" }, svg);
    tv.textContent = `${b.v>=0?"+":"-"}US$ ${fmtDec(Math.abs(b.v)/1e6,2)}M`;
    const tl = el("text", { x: b.x + 42, y: byB + 22, fill: "#1E293B", "font-size": "10.5", "font-weight": "700", "text-anchor": "middle" }, svg);
    tl.textContent = b.lbl;
  });

  renderPedBox("ped-cl2",
    `Sustituyendo <b>${fmtDec(qTon,1)} ton/año</b> de las 10 ton importadas a US$ ${pCif}/kg CIF, la economía ahorra divisas por <b>US$ ${fmtInt(vspAnual)}/año</b> con un costo social de <b>US$ ${fmtInt(csAnual)}/año</b>, logrando <b>VANS = ${vans>=0?"+":"-"}US$ ${fmtInt(Math.abs(vans))}</b> en 40 años.`,
    `<b>Trampa clásica de evaluación social:</b> aunque el proyecto sea «muy bueno para el país» (VANS &gt; US$ 11 MM), eso <b>NO significa automáticamente que el Estado deba financiarlo</b>. Siempre hay que calcular el VAN Privado primero: si el privado ya gana plata (Cuadrante I), el Estado no pone ni un peso.`,
    `Prueba hacer clic en <b>«Probar Cuadrante II (P_int US$ 410)»</b> arriba: verás cómo el VAN Privado se vuelve negativo mientras el VANS sigue en +US$ 11,3 MM, activándose exactamente el rango de subsidio estatal óptimo [|VAN<sub>P</sub>|, VANS].`
  );
}

renderQuizVF();
renderMecanica();
drawMapaProy();
renderLecturaProy();
renderQuizProy();
drawClaseEj1();
drawClaseEj2();

// ============================================================================
// 12. MOTOR DE ESTUDIO EN 4 MODOS (APRENDER · PRACTICAR · FORMULARIO · LAB)
// ============================================================================
const LEARN_TOPICS = [
  {
    id: "t_leche", tab: "leche", sub: null, retoIdx: 0,
    title: "1. Unidad I · Valor Social de la Producción: Leche (AD + LR)",
    s1: "<b>Qué ocurre aquí:</b> Al entrar un proyecto de 1.470 ton/año, la oferta se desplaza de <b>O → O'</b> y el precio cae de P<sub>0</sub> a P<sub>1</sub>. Mira el gráfico: el bloque izquierdo (azul) es <b>LR</b> (recursos ahorrados por productores antiguos) y el bloque derecho (rojo) es <b>AD</b> (nuevo consumo). <i>Haz clic en «Reproducir 0% → 100%» para verlo moverse.</i>",
    s2: "<b>Cómo se calcula en la prueba:</b> (1) Iguala P<sub>d</sub> = P<sub>o</sub> para hallar Q<sub>0</sub> y P<sub>0</sub>; (2) Desplaza la oferta sumando Q<sub>proy</sub> para hallar Q<sub>1</sub>, Q<sub>o1</sub> y P<sub>1</sub>; (3) Suma los trapecios <b>VSP = AD + LR</b>. Con curvas lineales, el precio social unitario siempre es el punto medio: <b>P* = (P<sub>0</sub> + P<sub>1</sub>)/2</b>. <i>Haz clic en cualquier número punteado para editarlo en vivo.</i>",
    s3: "<b>Trampa clásica de examen:</b> El privado solo valora su producción al nuevo precio más bajo (<b>VPP = P<sub>1</sub>·Q<sub>proy</sub></b>), mientras la sociedad valora a <b>P* &gt; P<sub>1</sub></b> por los excedentes ganados. Además, la curva de Demanda incluye IVA y la Oferta es sin IVA."
  },
  {
    id: "t_transporte", tab: "transporte", sub: null, retoIdx: 1,
    title: "2. Unidad I · Transporte, Elasticidad y Externalidades Negativas",
    s1: "<b>Qué ocurre aquí:</b> Una mejora de transporte baja la tarifa de $5.000 a $3.500 y expande los viajes de 70.000 a 100.030. El trapecio morado es el <b>Beneficio Bruto</b> y la franja naranja es el <b>daño externo</b> (CmgS &gt; CmgP por congestión/emisiones).",
    s2: "<b>Cómo se calcula en la prueba:</b> (1) Beneficio Bruto por regla del trapecio: <b>½·(P<sub>0</sub>+P<sub>1</sub>)·(X<sub>1</sub>−X<sub>0</sub>)</b>; (2) Elasticidad E<sub>d</sub> = (%ΔX)/(%ΔP); (3) Externalidad total = <b>(CmgS − CmgP)·X<sub>1</sub></b>.",
    s3: "<b>Trampa clásica de examen:</b> Un proyecto privado puede parecer muy rentable mirando CmgP ($1.300), pero socialmente debes restar el <b>Costo Social Total (CmgS · X<sub>1</sub>)</b>. Si no se internaliza la franja naranja, el mercado sobreproduce viajes contaminantes."
  },
  {
    id: "t_elast", tab: "elasticidad", sub: null, retoIdx: 2,
    title: "3. Unidad I · Los 4 Casos Extremos de Elasticidad (100% AD vs. 100% LR)",
    s1: "<b>Qué ocurre aquí:</b> Usa los 4 botones de arriba (η<sub>d</sub>=∞, η<sub>o</sub>=∞, η<sub>d</sub>=0, η<sub>o</sub>=0) y mira la barra derecha <b>Peso VSP</b>: dependiendo de qué curva es horizontal o vertical, el beneficio se vuelve 100% AD (rojo) o 100% LR (azul).",
    s2: "<b>Regla rápida sin memorizar:</b> Pregúntate <i>¿qué lado puede reaccionar al precio?</i> Si la demanda es horizontal (exportable) o la oferta es vertical ⇒ <b>100% AD</b>. Si la oferta es horizontal (importable) o la demanda es vertical (agua/medicina) ⇒ <b>100% LR</b>.",
    s3: "<b>Trampa clásica de examen:</b> Dos situaciones opuestas dan el mismo resultado (100% AD con D horizontal u O vertical). Identifica primero si el bien es transable internacionalmente o si tiene consumo fijo."
  },
  {
    id: "t_clase1", tab: "clase", sub: "ej1", retoIdx: 3,
    title: "4. Unidad II · Caso Clase: Conversión Social Ítem a Ítem + Perpetuidad",
    s1: "<b>Qué ocurre aquí:</b> Tienes una inversión privada de $2.000 MM y costo unitario de $1.000/u, y la oferta pasa de 100.000 a 250.000 u/año (P baja de $2.000 a $100). En el gráfico de pizarra, <b>LR</b> es el rectángulo izquierdo (q<sub>0</sub>·CS) y <b>AD</b> el trapecio derecho bajo la demanda.",
    s2: "<b>Cómo se calcula paso a paso:</b> Convierte cada partida porcentual: MO por su factor, nacionales ÷1,19, importados por <b>(R*/R)/[(1+IVA)(1+t)]</b> y <b>Depreciación Legal = 0</b>. Luego suma <b>I<sub>S</sub> ($1.461,1M)</b>, <b>CS ($782,25/u)</b>, <b>VSP ($235,7M/año)</b> y aplica perpetuidad <b>VANS = −I<sub>S</sub> + VSP/r (+$503,3M)</b>.",
    s3: "<b>Trampa clásica de examen:</b> (1) La <b>Depreciación Legal SIEMPRE vale $0</b> en flujo social porque el capital real ya se restó en I<sub>S</sub>; (2) Para calcular LR = q<sub>0</sub>·CS usa el <b>costo social ($782,25)</b>, jamás el privado ($1.000)."
  },
  {
    id: "t_clase2", tab: "clase", sub: "ej2", retoIdx: 4,
    title: "5. Unidad II · Caso Clase Salmón: Sustitución de Importaciones y Subsidio",
    s1: "<b>Qué ocurre aquí:</b> Chile importa 10 ton/año de antifúngico a US$ 450/kg CIF. El proyecto produce 8 ton/año (40 años, SNI 2026) y vende interno a US$ 500/kg. Mira ambos gráficos: el área verde ahorra divisas al precio CIF y las barras comparan <b>VAN Privado vs. VANS</b>.",
    s2: "<b>Cómo se calcula paso a paso:</b> (1) Inversión social I<sub>S</sub> = AF imp. ÷(1,19·1,01) + MOC·0,97 = <b>US$ 1.220.016</b>; (2) Costo social unitario = <b>US$ 352,23/kg</b>; (3) VSP = 8.000 × US$ 450 CIF = <b>US$ 3,60M/año</b> ⇒ BN = <b>US$ 782.160/año</b>; (4) VANS (40a, 5,5%) = <b>+US$ 11,33M</b>.",
    s3: "<b>La pregunta trampa de la diapositiva:</b> Aunque el VANS sea enorme (+US$ 11,3M), <b>¿debe el Estado aportar plata? NO (Aporte = US$ 0)</b> porque el privado ya gana dinero solo (VAN<sub>P</sub> &gt; 0, Cuadrante I). Solo se subsidia en Cuadrante II (VAN<sub>P</sub> &lt; 0 y VANS &gt; 0)."
  },
  {
    id: "t_waterfall", tab: "waterfall", sub: null, retoIdx: 7,
    title: "6. Unidad II · Puente VAN Privado → VANS y Sensibilidad (SNI 2026)",
    s1: "<b>Qué ocurre aquí:</b> La cascada muestra por qué un proyecto que apenas renta para un privado puede ser excelente para el país al aplicar los 4 peldaños SNI 2026: bajar la tasa a TSD 5,5%, quitar impuestos, corregir mano de obra y sumar carbono/GIRS.",
    s2: "<b>Fórmulas que mandan:</b> TSD = <b>5,5%</b>; PSMO = Salario × FCSMO (<b>0,97 / 0,95 / 0,91</b>); Carbono = <b>$71.801/t CO<sub>2</sub>eq</b> (CH<sub>4</sub> × 28). Usa «Ajustar variables» para estresar volumen o costos.",
    s3: "<b>Trampa clásica de examen:</b> El IVA y el impuesto a la renta NO son costos sociales, sino transferencias entre privados y Fisco. Si un proyecto cae en Cuadrante II (VAN<sub>P</sub> &lt; 0, VANS &gt; 0), el subsidio máximo nunca debe superar el VANS."
  },
  {
    id: "t_horno", tab: "horno", sub: null, retoIdx: 5,
    title: "7. Unidad II · Precios Mentirosos (Horno de Pan) y Costos Hundidos",
    s1: "<b>Qué ocurre aquí:</b> Compara las 3 parejas de barras: al envasar el pan, el <b>Valor Agregado sube</b> (+$19) pero la ganancia <b>baja</b> (−$1). Y si hay un subsidio oculto de $6 a un insumo, el panadero gana +$4 mientras el país pierde −$2.",
    s2: "<b>Fórmulas que mandan:</b> Excedente Social = Excedente Privado − Subsidio Oculto. Para decisiones con planta construida, los costos pasados (estudio $250) son <b>Costos Hundidos ($0)</b>; solo importa el costo evitable + 10% del <b>Valor de Liquidación hoy</b>.",
    s3: "<b>Trampa clásica de examen:</b> Que un proyecto genere «más empleo y mayor Valor Agregado» NO prueba que sea bueno. Y todo estudio ya pagado antes de decidir es <b>costo hundido</b> y jamás entra al flujo."
  },
  {
    id: "t_agua", tab: "agua", sub: null, retoIdx: 6,
    title: "8. Unidad III · Proyección de Agua 10 Años (CEPAL), TEA y CAPM",
    s1: "<b>Qué ocurre aquí:</b> Las barras azules son la capacidad fija de la planta (5.000 m³/d) y las rojas el <b>déficit creciente</b> a lo largo de 10 años al proyectar población geométricamente. <i>Pulsa «Reproducir 10 Años» para ver crecer la brecha.</i>",
    s2: "<b>Fórmulas que mandan:</b> Población P<sub>t</sub> = P<sub>0</sub>·(1+r)<sup>t</sup> (Año 10 es t=9); TEA = (1 + TNA·d/365)<sup>365/d</sup> − 1; CAPM: k<sub>e</sub> = R<sub>f</sub> + β(R<sub>m</sub> − R<sub>f</sub>).",
    s3: "<b>Trampa clásica de examen:</b> (1) Antes de construir planta nueva, el SNI exige definir la <b>Situación Base Optimizada</b>; (2) Si comparas proyectos de distinta vida útil, manda el <b>menor CAE</b>, no el VAC."
  },
  {
    id: "t_ambiental", tab: "ambiental", sub: null, retoIdx: 6,
    title: "9. Unidad IV · Valoración Ambiental RA2: Leopold, Costo de Viaje y GEI",
    s1: "<b>Qué ocurre aquí:</b> La <b>Matriz de Leopold</b> cruza acciones del proyecto vs. factores ambientales multiplicando Magnitud (−10 a +10) × Importancia (1 a 10). Mueve cualquier celda para ver si el balance ambiental es positivo o exige mitigación.",
    s2: "<b>Fórmulas que mandan:</b> Costo de Viaje MCV = Visitas × (horas × <b>$2.792</b> + gasto); Carbono equivalente IPCC: <b>CO<sub>2</sub>eq = CO<sub>2</sub> + 28·CH<sub>4</sub> + 265·N<sub>2</sub>O</b> valorizado a <b>$71.801/t</b>.",
    s3: "<b>Trampa clásica de examen:</b> En Leopold, la <b>Importancia nunca es negativa</b> (solo la Magnitud lleva signo). En el SEIA (Ley 19.300), si se activa cualquier causal del art. 11 ingresa obligatoriamente como <b>EIA</b>, no DIA."
  },
  {
    id: "t_arboles", tab: "arboles", sub: null, retoIdx: 7,
    title: "10. Unidad IV · Árboles Causales (Problemas ↔ Objetivos) y Marco Lógico",
    s1: "<b>Qué ocurre aquí:</b> Alterna entre <b>Árbol de Problemas</b> (rojo: causas abajo → efectos arriba) y <b>Árbol de Objetivos</b> (verde: medios abajo → fines arriba) en los 3 casos de cátedra.",
    s2: "<b>Cómo pasa a la Matriz 4×4 (MML):</b> El tronco pasa a ser el <b>Propósito único</b>, los fines nutren el <b>Fin</b> y las raíces pasan a ser <b>Componentes y Actividades</b>.",
    s3: "<b>Trampa clásica de examen:</b> (1) Jamás redactes el problema como «falta un camión» (falta de solución); (2) En la MML, <b>a nivel de Actividades NO se definen supuestos</b>; (3) Obtener RS no garantiza financiamiento."
  }
];

const PRAC_RETOS = [
  {
    id: "r1", topicIdx: 0, short: "1. Leche VSP",
    title: "Valor Social de la Producción — Mercado de la Leche (Clase 2)",
    enun: "En el mercado de la leche, <b>P<sub>d</sub> = 300 − 0,0205·Q</b> y <b>P<sub>o</sub> = −50 + 0,025·Q</b>. Un proyecto aporta <b>Q<sub>proy</sub> = 1.470 ton/año</b> (el equilibrio con proyecto baja a Q<sub>1</sub> = 8.500 t y P<sub>1</sub> = $125,75). Calcula sin mirar el simulador:",
    qs: [
      { lbl: "Equilibrio inicial Q0 (ton/año)", type: "num", ans: 7692.3, tol: 0.02, ph: "ej. 7692" },
      { lbl: "Precio inicial P0 ($/ton)", type: "num", ans: 142.31, tol: 0.02, ph: "ej. 142,3" },
      { lbl: "Precio Social Unitario P* ($/ton)", type: "num", ans: 134.03, tol: 0.02, ph: "ej. 134,0" },
      { lbl: "VSP Total = AD + LR ($)", type: "num", ans: 197022, tol: 0.025, ph: "ej. 197024" }
    ],
    hint: "<b>Pista:</b> Iguala 300 − 0,0205Q = −50 + 0,025Q ⇒ Q<sub>0</sub> = 350 / 0,0455. Con curvas lineales, <b>P* = (P<sub>0</sub> + P<sub>1</sub>) / 2</b> y <b>VSP = P* × Q<sub>proy</sub></b>.",
    sol: "Q0 = 350 / 0,0455 = <b>7.692,3 t</b> | P0 = 300 − 0,0205(7692,3) = <b>$142,31</b> | P* = (142,31 + 125,75)/2 = <b>$134,03/t</b> | VSP = 134,03 × 1.470 = <b>$197.022</b>."
  },
  {
    id: "r2", topicIdx: 1, short: "2. Transporte",
    title: "Transporte Urbano y Externalidad Negativa (Apuntes págs. 13–14)",
    enun: "Un corredor de transporte baja la tarifa de <b>P<sub>0</sub> = $5.000</b> a <b>P<sub>1</sub> = $3.500</b> y los viajes suben de <b>X<sub>0</sub> = 70.000</b> a <b>X<sub>1</sub> = 100.030</b> pasajes. Si <b>CmgP = $1.300</b> y <b>CmgS = $1.700</b> por pasaje, calcula:",
    qs: [
      { lbl: "Beneficio Bruto por Demanda ($ millones)", type: "num", ans: 127.63, tol: 0.02, ph: "ej. 127,6" },
      { lbl: "Externalidad Negativa Total ($ millones)", type: "num", ans: 40.01, tol: 0.02, ph: "ej. 40,0" }
    ],
    hint: "<b>Pista:</b> Beneficio Bruto (trapecio) = ½·(P<sub>0</sub> + P<sub>1</sub>)·(X<sub>1</sub> − X<sub>0</sub>). Externalidad = (CmgS − CmgP) · X<sub>1</sub>. Ingresa el resultado en millones (ej. 127,6).",
    sol: "ΔX = 30.030 pasajes ⇒ B = 0,5·(5.000 + 3.500)·30.030 = $127.627.500 (<b>$127,63 MM</b>). Externalidad = ($1.700 − $1.300)·100.030 = $40.012.000 (<b>$40,01 MM</b>)."
  },
  {
    id: "r3", topicIdx: 2, short: "3. Elasticidades",
    title: "Los 4 Casos Extremos de Elasticidad — ¿100% AD o 100% LR?",
    enun: "Identifica qué componente explica el <b>100% del Valor Social de la Producción (VSP)</b> en cada caso extremo de examen:",
    qs: [
      { lbl: "Demanda horizontal (ηd = ∞, bien exportable)", type: "sel", opts: ["Seleccionar...", "100% AD (Mayor consumo)", "100% LR (Recursos liberados)"], ans: "100% AD (Mayor consumo)" },
      { lbl: "Oferta horizontal (ηo = ∞, costo constante)", type: "sel", opts: ["Seleccionar...", "100% AD (Mayor consumo)", "100% LR (Recursos liberados)"], ans: "100% LR (Recursos liberados)" },
      { lbl: "Demanda vertical (ηd = 0, consumo fijo)", type: "sel", opts: ["Seleccionar...", "100% AD (Mayor consumo)", "100% LR (Recursos liberados)"], ans: "100% LR (Recursos liberados)" },
      { lbl: "Oferta vertical (ηo = 0, oferta antigua fija)", type: "sel", opts: ["Seleccionar...", "100% AD (Mayor consumo)", "100% LR (Recursos liberados)"], ans: "100% AD (Mayor consumo)" }
    ],
    hint: "<b>Pista:</b> Si el consumo total NO cambia (D vertical u O horizontal), todo sustituye oferta antigua ⇒ <b>100% LR</b>. Si la oferta antigua NO baja (D horizontal u O vertical), todo se consume ⇒ <b>100% AD</b>.",
    sol: "ηd=∞ → <b>100% AD</b> | ηo=∞ → <b>100% LR</b> | ηd=0 → <b>100% LR</b> | ηo=0 → <b>100% AD</b>."
  },
  {
    id: "r4", topicIdx: 3, short: "4. Caso Clase 1",
    title: "Caso Clase 1 — Conversión Ítem a Ítem y VANS a Perpetuidad",
    enun: "Con IP = $2.000 MM (ya convertida a <b>I<sub>S</sub> = $1.461,05 MM</b>), q<sub>0</sub> = 100.000 (P<sub>0</sub> = $2.000) → q<sub>1</sub> = 250.000 (P<sub>1</sub> = $100), costo privado C = $1.000/u, r = 12%, FCSD = 1,06, IVA 19% y arancel 11% (MOC 1,0 · MOSC 0,8 · MONC 0,7):",
    qs: [
      { lbl: "Factor social para Depreciación Legal", type: "num", ans: 0, tol: 0.01, ph: "ej. 0" },
      { lbl: "Costo Social Unitario CS ($/u)", type: "num", ans: 782.25, tol: 0.02, ph: "ej. 782,25" },
      { lbl: "VSP anual = AD + LR ($ millones)", type: "num", ans: 235.73, tol: 0.02, ph: "ej. 235,7" },
      { lbl: "VANS a perpetuidad ($ millones)", type: "num", ans: 503.32, tol: 0.025, ph: "ej. 503,3" }
    ],
    hint: "<b>Pista:</b> Depreciación = 0. F<sub>imp</sub> = 1,06 / (1,19×1,11) = 0,8025. AD = 150.000 × (2.000+100)/2 = $157,5M. LR = 100.000 × CS. VANS = −I<sub>S</sub> + VSP / 0,12.",
    sol: "Depreciación = <b>0</b> | CS = <b>$782,25/u</b> | AD = $157,50M + LR = $78,23M ⇒ VSP = <b>$235,73M/año</b> | VANS = −1.461,05 + 235,73/0,12 = <b>+$503,32M</b>."
  },
  {
    id: "r5", topicIdx: 4, short: "5. Caso Salmón",
    title: "Caso Clase 2 — Industria del Salmón (Sustitución Importaciones SNI 2026)",
    enun: "Chile importa 10 ton/año a <b>US$ 450/kg CIF</b>. El proyecto produce <b>8 ton/año (8.000 kg)</b> por <b>40 años</b>, vende interno a US$ 500/kg, invierte US$ 1.000.000 (AF imp., factor 1/[1,19×1,01]) + US$ 400.000 (MOC 0,97). Costos unitarios: $100 nac., $100 imp., $50 MOC, $150 MONC (0,91). TSD = <b>5,5%</b>.",
    qs: [
      { lbl: "Inversión Social IS (US$)", type: "num", ans: 1220016, tol: 0.02, ph: "ej. 1220016" },
      { lbl: "Beneficio Neto Social Anual BN (US$/año)", type: "num", ans: 782160, tol: 0.02, ph: "ej. 782160" },
      { lbl: "VANS a 40 años al 5,5% (millones US$)", type: "num", ans: 11.33, tol: 0.025, ph: "ej. 11,33" },
      { lbl: "¿Cuánto debe aportar el Estado?", type: "sel", opts: ["Seleccionar...", "US$ 0 (Cuadrante I: privado ya es rentable)", "US$ 1.220.016 (toda la inversión social)", "US$ 11.330.621 (todo el VANS)"], ans: "US$ 0 (Cuadrante I: privado ya es rentable)" }
    ],
    hint: "<b>Pista:</b> I<sub>S</sub> = 1.000.000/(1,19×1,01) + 400.000×0,97. CS/kg = 84,03 + 83,20 + 48,50 + 136,50 = US$ 352,23. VSP = 8.000 × 450 = US$ 3.600.000. Factor anualidad 40a al 5,5% = 16,0461. Verifica si el privado ya gana dinero vendiendo a US$ 500.",
    sol: "I_S = <b>US$ 1.220.016</b> | BN = 3.600.000 − 2.817.840 = <b>US$ 782.160/año</b> | VANS = −1,22M + 12,55M = <b>+US$ 11,33M</b> | Como VAN_privado &gt; 0 (Cuadrante I), el Estado aporta <b>US$ 0</b>."
  },
  {
    id: "r6", topicIdx: 6, short: "6. Horno / Hundidos",
    title: "Precios Mentirosos (Fontaine) y Costos Hundidos",
    enun: "Un panadero produce con costo privado $100 y vende a <b>$104</b>, pero recibe un <b>subsidio oculto de $6</b> en un insumo. Por otro lado, antes de construir una fábrica ya pagó <b>$250</b> por un estudio de factibilidad.",
    qs: [
      { lbl: "Excedente Privado del panadero ($)", type: "num", ans: 4, tol: 0.01, ph: "ej. 4" },
      { lbl: "Excedente Social real del país ($)", type: "num", ans: -2, tol: 0.01, ph: "ej. -2" },
      { lbl: "¿Cuánto del estudio ya pagado ($250) entra al flujo?", type: "num", ans: 0, tol: 0.01, ph: "ej. 0" }
    ],
    hint: "<b>Pista:</b> Excedente Privado = Precio − Costo Privado. Excedente Social = Excedente Privado − Subsidio Oculto. Un estudio ya pagado es <b>costo hundido</b>.",
    sol: "EP = 104 − 100 = <b>+$4</b> | ES = 4 − 6 = <b>−$2</b> (bueno para Juan, malo para el país) | Estudio de factibilidad = <b>$0</b> (costo hundido irrecuperable)."
  },
  {
    id: "r7", topicIdx: 8, short: "7. GEI y MCV",
    title: "Valoración Ambiental RA2 — Carbono Equivalente SNI 2026",
    enun: "Un proyecto de reciclaje en Osorno evita emitir <b>10 toneladas de Metano (CH<sub>4</sub>)</b> al año. Usando el potencial IPCC a 100 años (CH<sub>4</sub> = 28) y el Precio Social del Carbono SNI 2026 (<b>$71.801 / t CO<sub>2</sub>eq</b>), calcula:",
    qs: [
      { lbl: "Toneladas de CO2 equivalente evitadas (t CO2eq)", type: "num", ans: 280, tol: 0.01, ph: "ej. 280" },
      { lbl: "Beneficio Social Anual por GEI ($ millones)", type: "num", ans: 20.10, tol: 0.02, ph: "ej. 20,1" }
    ],
    hint: "<b>Pista:</b> CO<sub>2</sub>eq = t<sub>CH4</sub> × 28. Luego multiplica por $71.801 y divide por 1.000.000 para expresarlo en millones ($MM).",
    sol: "CO2eq = 10 × 28 = <b>280 t CO2eq</b> | Beneficio = 280 × $71.801 = $20.104.280 (<b>$20,10 MM/año</b>)."
  },
  {
    id: "r8", topicIdx: 5, short: "8. SNI 2026",
    title: "Parámetros Oficiales SNI 2026 y Reglas de Selección (VAN / VAC / CAE)",
    enun: "Comprueba que dominas de memoria los parámetros oficiales vigentes SNI 2026 (MDSF, 31 mar 2026) y criterios de evaluación:",
    qs: [
      { lbl: "Tasa Social de Descuento TSD 2026 (%)", type: "num", ans: 5.5, tol: 0.01, ph: "ej. 5,5" },
      { lbl: "Factor Mano de Obra Semicalificada (choferes CIUO-08)", type: "num", ans: 0.95, tol: 0.01, ph: "ej. 0,95" },
      { lbl: "Criterio correcto si dos alternativas tienen DISTINTA vida útil", type: "sel", opts: ["Seleccionar...", "Mayor VAN sin ajustar", "Menor VAC", "Menor CAE (Costo Anual Equivalente)"], ans: "Menor CAE (Costo Anual Equivalente)" }
    ],
    hint: "<b>Pista:</b> TSD 2026 bajó de 6% a 5,5%. Los factores MO son MOC=0,97 · MOSC=0,95 · MONC=0,91. Con distinta vida útil se anualiza el costo.",
    sol: "TSD 2026 = <b>5,5%</b> | Choferes (MOSC) = <b>0,95</b> | Distinta vida útil con beneficios equivalentes ⇒ <b>Menor CAE</b>."
  }
];

let studioMode = "aprender";
let learnTopicIdx = 0;
let learnStep = 1;
let learnShowVars = false;
let pracSub = "retos";
let pracRetoIdx = 0;
let doneTopics = new Set();
let solvedRetos = new Set();

try {
  const saved = JSON.parse(localStorage.getItem("ulagos_proy_2026_prog") || "{}");
  if (Array.isArray(saved.t)) doneTopics = new Set(saved.t);
  if (Array.isArray(saved.r)) solvedRetos = new Set(saved.r);
} catch (e) {}

function saveStudioProg() {
  try {
    localStorage.setItem("ulagos_proy_2026_prog", JSON.stringify({
      t: Array.from(doneTopics),
      r: Array.from(solvedRetos)
    }));
  } catch (e) {}
  const chip = document.getElementById("studio-prog-chip");
  if (chip) chip.textContent = `Progreso: ${doneTopics.size} / ${LEARN_TOPICS.length} temas · ${solvedRetos.size} / ${PRAC_RETOS.length} retos`;
}

function initLearnSelector() {
  const sel = document.getElementById("learn-topic-sel");
  if (!sel || sel.options.length > 0) return;
  LEARN_TOPICS.forEach((t, idx) => {
    const opt = document.createElement("option");
    opt.value = idx;
    opt.textContent = t.title;
    sel.appendChild(opt);
  });
}

function activatePanelClean(panelName) {
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  const pEl = document.getElementById("panel-" + panelName);
  if (pEl) pEl.classList.add("active");
  document.querySelectorAll(".top-tabs .tab-btn").forEach(b => {
    const oc = b.getAttribute("onclick") || "";
    b.classList.toggle("active", oc.includes("'" + panelName + "'"));
  });
  if (panelName === "transporte") drawTransporte();
  if (panelName === "leche") drawLeche();
  if (panelName === "elasticidad") drawElast();
  if (panelName === "waterfall") drawWaterfall();
  if (panelName === "horno") { drawHorno(); drawHundido(); }
  if (panelName === "agua") { drawAgua(); drawTeaCapm(); }
  if (panelName === "ambiental") drawAmbiental();
  if (panelName === "arboles") { drawArbol(); renderQuizVF(); }
  if (panelName === "mecanica") renderMecanica();
  if (panelName === "clase") { drawClaseEj1(); drawClaseEj2(); }
  if (panelName === "lectura") { drawMapaProy(); renderLecturaProy(); renderQuizProy(); }
}

function setStudioMode(mode) {
  studioMode = mode;
  const wrap = document.getElementById("app-wrap");
  if (!wrap) return;
  wrap.classList.remove("mode-aprender", "mode-practicar", "mode-formulario", "mode-lab", "step-1", "step-2", "step-3", "show-vars");
  wrap.classList.add("mode-" + mode);

  ["aprender", "practicar", "formulario", "lab"].forEach(m => {
    const b = document.getElementById("mbtn-" + m);
    if (b) b.classList.toggle("active", m === mode);
  });

  if (mode === "aprender") {
    applyLearnView();
  } else if (mode === "practicar") {
    activatePanelClean("practicar");
    setPracSub(pracSub);
  } else if (mode === "formulario") {
    activatePanelClean("mecanica");
  } else {
    const t = LEARN_TOPICS[learnTopicIdx];
    activatePanelClean(t ? t.tab : "leche");
  }
}

function applyLearnView() {
  initLearnSelector();
  const wrap = document.getElementById("app-wrap");
  const topic = LEARN_TOPICS[learnTopicIdx];
  const sel = document.getElementById("learn-topic-sel");
  if (sel) sel.value = String(learnTopicIdx);

  wrap.classList.remove("step-1", "step-2", "step-3", "show-vars");
  wrap.classList.add("step-" + learnStep);
  if (learnShowVars && learnStep !== 3) wrap.classList.add("show-vars");

  activatePanelClean(topic.tab);
  if (topic.tab === "clase" && topic.sub) {
    const btnSub = document.getElementById("cl-btn-" + topic.sub);
    if (btnSub) selCasoClase(topic.sub, btnSub);
  }

  for (let s = 1; s <= 3; s++) {
    const sb = document.getElementById("stp-btn-" + s);
    if (sb) sb.classList.toggle("active", s === learnStep);
  }

  const tags = ["", "Paso 1 de 3 — Intuición Visual y Gráfico", "Paso 2 de 3 — Fórmulas Clave y Cálculos", "Paso 3 de 3 — Trampa de Prueba y Teoría"];
  document.getElementById("guide-step-tag").textContent = tags[learnStep];
  document.getElementById("guide-step-body").innerHTML = learnStep === 1 ? topic.s1 : (learnStep === 2 ? topic.s2 : topic.s3);
  document.getElementById("guide-step-hint").textContent = `Tema ${learnTopicIdx + 1} de ${LEARN_TOPICS.length} · Paso ${learnStep} de 3`;

  const btnVars = document.getElementById("btn-toggle-vars");
  if (btnVars) {
    btnVars.style.display = learnStep === 3 ? "none" : "inline-block";
    btnVars.textContent = learnShowVars ? "Ocultar sliders" : "Ajustar variables (sliders)";
    btnVars.classList.toggle("primary", learnShowVars);
  }

  const bPrev = document.getElementById("btn-prev-step");
  const bNext = document.getElementById("btn-next-step");
  if (bPrev) bPrev.disabled = (learnStep === 1 && learnTopicIdx === 0);
  if (bNext) bNext.textContent = learnStep < 3 ? "Siguiente paso →" : (learnTopicIdx < LEARN_TOPICS.length - 1 ? "Ir al siguiente tema →" : "Ir a Practicar →");

  const dBtn = document.getElementById("learn-done-btn");
  if (dBtn) {
    const isD = doneTopics.has(topic.id);
    dBtn.classList.toggle("is-done", isD);
    dBtn.textContent = isD ? "Aprendido ✓" : "Marcar aprendido ✓";
  }

  // En Paso 3 desplegar Marco Teórico automáticamente para facilitar lectura
  if (learnStep === 3) {
    const pEl = document.getElementById("panel-" + topic.tab);
    if (pEl) pEl.querySelectorAll(".teo-box").forEach(d => d.setAttribute("open", "open"));
  }
}

function selectLearnTopic(idx) {
  learnTopicIdx = Math.max(0, Math.min(LEARN_TOPICS.length - 1, idx));
  learnStep = 1;
  learnShowVars = false;
  applyLearnView();
}
function stepLearnTopic(delta) {
  selectLearnTopic(learnTopicIdx + delta);
}
function setLearnStep(st) {
  learnStep = st;
  if (st === 3) learnShowVars = false;
  applyLearnView();
}
function moveLearnStep(delta) {
  if (delta > 0) {
    if (learnStep < 3) { learnStep++; applyLearnView(); }
    else {
      doneTopics.add(LEARN_TOPICS[learnTopicIdx].id);
      saveStudioProg();
      if (learnTopicIdx < LEARN_TOPICS.length - 1) selectLearnTopic(learnTopicIdx + 1);
      else setStudioMode("practicar");
    }
  } else {
    if (learnStep > 1) { learnStep--; applyLearnView(); }
    else if (learnTopicIdx > 0) { learnTopicIdx--; learnStep = 3; applyLearnView(); }
  }
}
function toggleVarsGuided() {
  learnShowVars = !learnShowVars;
  applyLearnView();
}
function toggleTopicDone() {
  const id = LEARN_TOPICS[learnTopicIdx].id;
  if (doneTopics.has(id)) doneTopics.delete(id); else doneTopics.add(id);
  saveStudioProg();
  applyLearnView();
}
function irAPracticaTemaActual() {
  const topic = LEARN_TOPICS[learnTopicIdx];
  pracRetoIdx = topic.retoIdx || 0;
  pracSub = "retos";
  setStudioMode("practicar");
}

// --- MODO PRACTICAR (RETOS + V/F + CONTROL DE LECTURA) ---
function setPracSub(sub) {
  pracSub = sub;
  ["retos", "vf", "lec"].forEach(k => {
    const b = document.getElementById("pr-sub-" + k);
    if (b) b.classList.toggle("primary", k === sub);
  });
  if (sub === "lec") {
    activatePanelClean("lectura");
    return;
  }
  activatePanelClean("practicar");
  document.getElementById("pr-view-retos").style.display = sub === "retos" ? "block" : "none";
  document.getElementById("pr-view-vf").style.display = sub === "vf" ? "block" : "none";
  if (sub === "retos") renderRetoActual();
  if (sub === "vf") renderQuizVF();
}

function renderRetoActual() {
  const bar = document.getElementById("pr-chips-bar");
  if (bar) {
    bar.innerHTML = PRAC_RETOS.map((r, i) => {
      const ok = solvedRetos.has(r.id);
      return `<button class="pr-chip${i === pracRetoIdx ? ' active' : ''}${ok ? ' solved' : ''}" onclick="selectReto(${i})">${ok ? '✓ ' : ''}${r.short}</button>`;
    }).join("");
  }
  const reto = PRAC_RETOS[pracRetoIdx];
  document.getElementById("pr-badge").textContent = `Reto ${pracRetoIdx + 1} de ${PRAC_RETOS.length}`;
  document.getElementById("pr-title").textContent = reto.title;
  document.getElementById("pr-enun").innerHTML = reto.enun;

  const qg = document.getElementById("pr-qgrid");
  qg.innerHTML = reto.qs.map((q, qi) => {
    if (q.type === "sel") {
      const opts = q.opts.map(op => `<option value="${op.replace(/"/g, '&quot;')}">${op}</option>`).join("");
      return `<div class="pr-qbox" id="pr-qb-${qi}"><label class="pr-qlbl">${q.lbl}</label><select class="pr-in" id="pr-in-${qi}">${opts}</select><div class="pr-qfb" id="pr-fb-${qi}"></div></div>`;
    }
    return `<div class="pr-qbox" id="pr-qb-${qi}"><label class="pr-qlbl">${q.lbl}</label><input class="pr-in" id="pr-in-${qi}" type="text" placeholder="${q.ph || ''}" onkeydown="if(event.key==='Enter') comprobarReto()" /><div class="pr-qfb" id="pr-fb-${qi}"></div></div>`;
  }).join("");

  const hBox = document.getElementById("pr-hint");
  const sBox = document.getElementById("pr-sol");
  hBox.style.display = "none";
  hBox.innerHTML = reto.hint;
  sBox.style.display = "none";
  sBox.innerHTML = `<b>Desarrollo paso a paso:</b> ${reto.sol}`;
}

function selectReto(i) { pracRetoIdx = i; renderRetoActual(); }
function navReto(delta) { pracRetoIdx = (pracRetoIdx + delta + PRAC_RETOS.length) % PRAC_RETOS.length; renderRetoActual(); }
function toggleHintReto() {
  const b = document.getElementById("pr-hint");
  b.style.display = b.style.display === "block" ? "none" : "block";
}
function toggleSolReto() {
  const b = document.getElementById("pr-sol");
  b.style.display = b.style.display === "block" ? "none" : "block";
}
function limpiarReto() { renderRetoActual(); }
function abrirTemaDesdeReto() {
  const reto = PRAC_RETOS[pracRetoIdx];
  learnTopicIdx = reto.topicIdx || 0;
  learnStep = 1;
  setStudioMode("aprender");
}

function parseUserNum(raw) {
  let s = String(raw || "").trim().replace(/\$/g, "").replace(/%/g, "").replace(/US/gi, "").replace(/\s+/g, "");
  if (!s) return NaN;
  // Si trae punto de miles y coma decimal (ej. 1.220.016,5) -> 1220016.5
  if (s.includes(".") && s.includes(",")) {
    s = s.replace(/\./g, "").replace(/,/g, ".");
  } else if (s.includes(",")) {
    s = s.replace(/,/g, ".");
  } else if ((s.match(/\./g) || []).length > 1) {
    s = s.replace(/\./g, "");
  } else if (/^\d{1,3}\.\d{3}$/.test(s)) {
    s = s.replace(/\./g, "");
  }
  return parseFloat(s);
}

function comprobarReto() {
  const reto = PRAC_RETOS[pracRetoIdx];
  let allOk = true;
  reto.qs.forEach((q, qi) => {
    const box = document.getElementById("pr-qb-" + qi);
    const inp = document.getElementById("pr-in-" + qi);
    const fb = document.getElementById("pr-fb-" + qi);
    box.classList.remove("ok", "bad");
    if (q.type === "sel") {
      const ok = inp.value === q.ans;
      box.classList.add(ok ? "ok" : "bad");
      fb.style.color = ok ? "#15803D" : "#DC2626";
      fb.textContent = ok ? "✓ Correcto" : "✗ Revisa la pista e intenta de nuevo";
      if (!ok) allOk = false;
    } else {
      const v = parseUserNum(inp.value);
      const ok = Number.isFinite(v) && (q.ans === 0 ? Math.abs(v) < 0.01 : Math.abs(v - q.ans) <= Math.max(Math.abs(q.ans) * (q.tol || 0.02), 0.15));
      box.classList.add(ok ? "ok" : "bad");
      fb.style.color = ok ? "#15803D" : "#DC2626";
      fb.textContent = ok ? "✓ Correcto" : (Number.isFinite(v) ? "✗ Aún no coincide (usa «Ver Pista»)" : "Ingresa un número");
      if (!ok) allOk = false;
    }
  });
  if (allOk) {
    solvedRetos.add(reto.id);
    saveStudioProg();
    const sBox = document.getElementById("pr-sol");
    sBox.style.display = "block";
    // Actualizar chips verdes
    const bar = document.getElementById("pr-chips-bar");
    if (bar) {
      bar.querySelectorAll(".pr-chip")[pracRetoIdx].classList.add("solved");
      bar.querySelectorAll(".pr-chip")[pracRetoIdx].textContent = "✓ " + reto.short;
    }
  }
}

saveStudioProg();
setStudioMode("aprender");

</script>
</body>
</html>
"""


def renderizar_simuladores_fluidos_60fps(modo_catedra: bool = False):
    """Renderiza el estudio integral a 60 FPS (12 módulos) con conectores vivos y expansión RA2 27 Nov."""
    html_final = HTML_SIMULADOR_FLUIDO
    try:
        from motor_conectores_pedagogicos import inyectar_conectores_pedagogicos
        html_final = inyectar_conectores_pedagogicos(html_final)
    except Exception:
        pass
    try:
        from motor_expansion_ra2_27nov import inyectar_expansion_ra2_27nov
        html_final = inyectar_expansion_ra2_27nov(html_final, modo_catedra=modo_catedra)
    except Exception:
        pass
    components.html(html_final, height=1420, scrolling=True)
