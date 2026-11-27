# -*- coding: utf-8 -*-
"""
consola_web.py — SUITE INTEGRAL DE PROYECTOS ULAGOS 2026 (SNI / MIDESO + PRIVADO + AMBIENTAL)
- Mantiene intacta la generación del paquete .ZIP con Portada Institucional ULagos, APA 7,
  tablas sin '#' de calles, sin Matriz de Cumplimiento y con los 3 libros Excel editables.
- Incorpora:
  1) Modo Exacto SNI 2026 (TSD 5,5%, MOC 0,97, MOSC 0,95, MONC 0,91, ahorro municipal sobre
     toneladas efectivamente incorporadas y opción de Impuesto Pro Pyme escalonado 12,5% / 15% / 25%).
  2) Simulador de Financiamiento Bancario (Flujo Puro vs. Flujo Financiado con Tabla de Amortización y Escudo Tributario).
  3) Indicadores Costo-Eficiencia SNI (VAC, CAE y CAE por tonelada / unidad) y Huella de Carbono 2026 ($71.801/t CO2eq).
  4) Generador automático de Ficha Resumen IDI / BIP en UF (UF oficial Precios Sociales 2026 = $39.727,96 CLP).
  5) Calculadora Microeconómica de Valor Social de la Producción (VSP = AD + LR y Excedentes por Agente).
"""

import os
import re
import sys
import types
import copy
import shutil
import zipfile
import tempfile
import subprocess
import importlib.util

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import numpy as np
import numpy_financial as npf
import pandas as pd
import streamlit as st
import openpyxl
from openpyxl.styles import PatternFill, Font, Border, Side
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


# ==============================================================================
# 1. COMPATIBILIDAD CON SERVIDORES LINUX EN LA NUBE (SIN TKINTER)
# ==============================================================================

def _asegurar_tkinter_en_nube():
    try:
        import tkinter  # noqa: F401
        import tkinter.font  # noqa: F401
    except ImportError:
        tk_mock = types.ModuleType("tkinter")
        tk_mock.Tk = object
        tk_mock.Toplevel = object
        tk_mock.Frame = object
        tk_mock.Label = object
        tk_mock.Button = object
        tk_mock.Canvas = object
        tk_mock.StringVar = lambda *a, **k: None
        tk_mock.DoubleVar = lambda *a, **k: None
        tk_mock.IntVar = lambda *a, **k: None
        tk_mock.ttk = types.ModuleType("tkinter.ttk")
        tk_mock.messagebox = types.ModuleType("tkinter.messagebox")
        tk_mock.filedialog = types.ModuleType("tkinter.filedialog")
        tk_mock.font = types.ModuleType("tkinter.font")
        tk_mock.constants = types.ModuleType("tkinter.constants")
        sys.modules["tkinter"] = tk_mock
        sys.modules["tkinter.ttk"] = tk_mock.ttk
        sys.modules["tkinter.messagebox"] = tk_mock.messagebox
        sys.modules["tkinter.filedialog"] = tk_mock.filedialog
        sys.modules["tkinter.font"] = tk_mock.font
        sys.modules["tkinter.constants"] = tk_mock.constants


_asegurar_tkinter_en_nube()


def cargar_modulo_por_ruta(nombre_interno, nombre_archivo):
    carpeta = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(carpeta, nombre_archivo)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró '{nombre_archivo}' en: {carpeta}")
    spec = importlib.util.spec_from_file_location(nombre_interno, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre_interno] = mod
    spec.loader.exec_module(mod)
    return mod


mod2 = cargar_modulo_por_ruta("script2_corrector", "2_corrector_formato_y_excels.py")
mod3 = cargar_modulo_por_ruta("script3_josue", "3_integrador_arboles_y_pauta_josue.py")
HUB_BASE_URL = "https://app-context-extractor-cl8x5kwfdodzvmx7m3vean.streamlit.app/"
try:
    _mod_cat = cargar_modulo_por_ruta("motor_catedra_proyectos_sni", "motor_catedra_proyectos_sni.py")
    renderizar_extension_proyectos_sni = getattr(_mod_cat, "renderizar_extension_proyectos_sni", None)
    renderizar_nota_metodologica = getattr(_mod_cat, "renderizar_nota_metodologica", None)
    inyectar_estilos_proyectos = getattr(_mod_cat, "inyectar_estilos_proyectos", None)
    HUB_BASE_URL = getattr(_mod_cat, "HUB_BASE_URL", HUB_BASE_URL)
except Exception:
    renderizar_extension_proyectos_sni = None
    renderizar_nota_metodologica = None
    inyectar_estilos_proyectos = None

try:
    _mod_vivo = cargar_modulo_por_ruta("motor_explicador_vivo_proyectos", "motor_explicador_vivo_proyectos.py")
    renderizar_panel_inteligente_superior = getattr(_mod_vivo, "renderizar_panel_inteligente_superior", None)
except Exception:
    renderizar_panel_inteligente_superior = None

try:
    _mod_guia = cargar_modulo_por_ruta("motor_guia_interactiva_bibliografia", "motor_guia_interactiva_bibliografia.py")
    renderizar_guia_interactiva_bibliografia = getattr(_mod_guia, "renderizar_guia_interactiva_bibliografia", None)
except Exception:
    renderizar_guia_interactiva_bibliografia = None

try:
    _mod_pizarra = cargar_modulo_por_ruta("motor_pizarra_pedagogica_sni", "motor_pizarra_pedagogica_sni.py")
    renderizar_semaforo_jerarquia_cepal = getattr(_mod_pizarra, "renderizar_semaforo_jerarquia_cepal", None)
    renderizar_tab_pizarra_pedagogica = getattr(_mod_pizarra, "renderizar_tab_pizarra_pedagogica", None)
except Exception:
    renderizar_semaforo_jerarquia_cepal = None
    renderizar_tab_pizarra_pedagogica = None

try:
    _mod_fluidez = cargar_modulo_por_ruta("motor_fluidez_vectores_sni", "motor_fluidez_vectores_sni.py")
    renderizar_simuladores_fluidos_60fps = getattr(_mod_fluidez, "renderizar_simuladores_fluidos_60fps", None)
except Exception:
    renderizar_simuladores_fluidos_60fps = None


# ==============================================================================
# 2. PARÁMETROS OFICIALES PRECIOS SOCIALES SNI 2026
# ==============================================================================

PRECIOS_SOCIALES_2026 = {
    "UF_2026": 39727.96,
    "DOLAR_2026": 911.18,
    "TSD_2026": 0.055,
    "FC_MOC_2026": 0.97,
    "FC_MOSC_2026": 0.95,
    "FC_MONC_2026": 0.91,
    "FC_DIVISA_2026": 1.00,
    "PRECIO_SOCIAL_CO2_TON": 71801,
    "FACTOR_CH4_CO2EQ": 28.0,
    "FACTOR_N2O_CO2EQ": 265.0,
    "ELEC_BAJA_TENSION_KWH": 124.8,
    "ELEC_ALTA_TENSION_KWH": 119.8,
    "COMBUSTIBLE_DIESEL_L": 805,
    "COMBUSTIBLE_GAS93_L": 737,
    "COMBUSTIBLE_CAMIONETA_L": 787,
    "VST_URBANO_H_PAX": 3338,
    "VST_CARGA_H_VEH": 12954,
}


# ==============================================================================
# 3. MOTOR EXTENDIDO 2026 (SOPORTA AHORRO CONSERVADOR, PRO PYME, DEUDA, VAC/CAE)
# ==============================================================================

def ejecutar_motor_extendido_2026(cfg, solo_ton_incorporadas=False, usar_pro_pyme_escalonado=False, beneficio_gei_anual=0.0):
    res = mod2.ejecutar_motor_financiero(cfg)
    horizonte = int(cfg["HORIZONTE_ANIOS"])
    iva = float(cfg["IVA"])
    tasa_priv = float(cfg["TASA_DESCUENTO_PRIVADA"])
    tasa_soc = float(cfg["TASA_DESCUENTO_SOCIAL"])

    df_fp = res["df_flujo_privado"].copy()
    df_fs = res["df_flujo_social"].copy()
    df_cant = res["df_cantidades"]

    # 1. Opción Pro Pyme Escalonado (Circular SII N° 53/2025: 12,5% Año 1, 15% Año 2, 25% desde Año 3)
    if usar_pro_pyme_escalonado:
        uai = df_fp.loc["(=) Utilidad Antes de Impuestos (UAI)"].values.astype(float)
        tasas_anuales = [0.0, 0.125, 0.15] + [0.25] * max(0, horizonte - 2)
        tasas_arr = np.array(tasas_anuales[:horizonte + 1])
        imp_fila = [r for r in df_fp.index if "Impuesto a la Renta" in r][0]
        nuevos_imp = np.where(uai > 0, -np.round(uai * tasas_arr), 0)
        udi = uai + nuevos_imp
        rev_dep = df_fp.loc["(+) Ajuste por Depreciación (Gasto No Desembolsable)"].values
        inv_fija = df_fp.loc["(-) Inversiones y Reinversiones en Activos Fijos"].values
        flujo_ct = df_fp.loc["(+/-) Inversión y Recuperación de Capital de Trabajo"].values
        val_des = df_fp.loc["(+) Valor de Desecho de los Activos"].values
        nuevo_fc_priv = udi + rev_dep + inv_fija + flujo_ct + val_des

        df_fp.loc[imp_fila] = nuevos_imp.astype(int)
        df_fp.loc["(=) Utilidad Después de Impuestos (UDI)"] = udi.astype(int)
        df_fp.loc["(=) FLUJO DE CAJA PRIVADO NETO"] = nuevo_fc_priv.astype(int)

        van_p = float(npf.npv(tasa_priv, nuevo_fc_priv))
        tir_p = float(npf.irr(nuevo_fc_priv))
        pb_p = mod2.calcular_payback(nuevo_fc_priv)
        res["df_flujo_privado"] = df_fp
        res["metricas"]["van_privado"] = round(van_p)
        res["metricas"]["tir_privada"] = round(tir_p * 100, 2) if not np.isnan(tir_p) else 0.0
        res["metricas"]["payback_privado"] = pb_p

    # 2. Criterio conservador SNI 2026: Ahorro municipal solo sobre toneladas incorporadas (70%) + GEI opcional
    if solo_ton_incorporadas or beneficio_gei_anual != 0.0:
        ton_inc = df_cant.loc["Cartón Efectivamente Incorporado (Toneladas)"].values.astype(float)
        ton_rec = df_cant.loc["Residuo de Cartón Recolectado (Toneladas)"].values.astype(float)
        ton_base = ton_inc if solo_ton_incorporadas else ton_rec

        ahorro_neto_ton = float(cfg["AHORRO_MUNI_TON"]) / (1.0 + iva)
        ben_muni = np.insert(np.round(ton_base * ahorro_neto_ton), 0, 0)
        ben_otros = np.insert(np.round(np.full(horizonte, float(cfg["OTROS_BEN_SOC_ANUAL"]) + float(beneficio_gei_anual))), 0, 0)

        ben_ventas = df_fs.loc["(+) Beneficio Social por Disponibilidad de Bienes (Ventas s/IVA)"].values
        costos_soc = df_fs.loc["(-) Costos Operativos y Mano de Obra a Precios Sociales"].values
        inv_soc = df_fs.loc["(-) Inversiones y Reinversiones a Precios Sociales"].values
        ct_soc = df_fs.loc["(+/-) Capital de Trabajo a Precios Sociales"].values
        vr_soc = df_fs.loc["(+) Valor Residual Social de los Activos"].values

        nuevo_fc_soc = ben_ventas + ben_muni + ben_otros + costos_soc + inv_soc + ct_soc + vr_soc
        df_fs.loc["(+) Liberación de Recursos Municipales (Ahorro Vertedero Curaco)"] = ben_muni.astype(int)
        df_fs.loc["(+) Otros Beneficios Sociales y Ambientales"] = ben_otros.astype(int)
        df_fs.loc["(=) FLUJO DE BENEFICIOS SOCIALES NETOS"] = nuevo_fc_soc.astype(int)

        van_s = float(npf.npv(tasa_soc, nuevo_fc_soc))
        tir_s = float(npf.irr(nuevo_fc_soc))
        pb_s = mod2.calcular_payback(nuevo_fc_soc)
        res["df_flujo_social"] = df_fs
        res["metricas"]["van_social"] = round(van_s)
        res["metricas"]["tir_social"] = round(tir_s * 100, 2) if not np.isnan(tir_s) else 0.0
        res["metricas"]["payback_social"] = pb_s

    # Actualizar tabla resumen de indicadores
    m = res["metricas"]
    res["df_indicadores"] = pd.DataFrame([
        {
            "Tipo de Evaluación": "Evaluación Privada (Punto 7)",
            "Tasa de Descuento": f"{mod2.fmt_dec_cl(tasa_priv * 100, 1)}%",
            "VAN / VANS ($)": mod2.fmt_clp(m["van_privado"]),
            "TIR / TIRS (%)": f"{mod2.fmt_dec_cl(m['tir_privada'], 2)}%",
            "Payback (Años)": f"{mod2.fmt_dec_cl(m['payback_privado'], 2)} años",
            "Decisión": "VIABLE (Rentable)" if m["van_privado"] > 0 else "NO VIABLE",
        },
        {
            "Tipo de Evaluación": "Evaluación Social SNI (Punto 8)",
            "Tasa de Descuento": f"{mod2.fmt_dec_cl(tasa_soc * 100, 1)}%",
            "VAN / VANS ($)": mod2.fmt_clp(m["van_social"]),
            "TIR / TIRS (%)": f"{mod2.fmt_dec_cl(m['tir_social'], 2)}%",
            "Payback (Años)": f"{mod2.fmt_dec_cl(m['payback_social'], 2)} años",
            "Decisión": "VIABLE SOCIALMENTE" if m["van_social"] > 0 else "NO VIABLE",
        },
    ])

    # 3. Cálculo de Indicadores Costo-Eficiencia (VAC y CAE Privado y Social)
    costos_flujo_soc = (
        -df_fs.loc["(-) Costos Operativos y Mano de Obra a Precios Sociales"].values
        - df_fs.loc["(-) Inversiones y Reinversiones a Precios Sociales"].values
        - df_fs.loc["(+/-) Capital de Trabajo a Precios Sociales"].values
        - df_fs.loc["(+) Valor Residual Social de los Activos"].values
        - df_fs.loc["(+) Liberación de Recursos Municipales (Ahorro Vertedero Curaco)"].values
    )
    vac_social = float(npf.npv(tasa_soc, costos_flujo_soc))
    factor_cae_soc = (tasa_soc * ((1.0 + tasa_soc) ** horizonte)) / (((1.0 + tasa_soc) ** horizonte) - 1.0)
    cae_social = vac_social * factor_cae_soc

    costos_flujo_priv = (
        -df_fp.loc["(-) Costos Operativos Totales (Fijos, Variables y Personal)"].values
        - df_fp.loc["(-) Inversiones y Reinversiones en Activos Fijos"].values
        - df_fp.loc["(+/-) Inversión y Recuperación de Capital de Trabajo"].values
        - df_fp.loc["(+) Valor de Desecho de los Activos"].values
    )
    vac_privado = float(npf.npv(tasa_priv, costos_flujo_priv))
    factor_cae_priv = (tasa_priv * ((1.0 + tasa_priv) ** horizonte)) / (((1.0 + tasa_priv) ** horizonte) - 1.0)
    cae_privado = vac_privado * factor_cae_priv

    ton_promedio_anual = float(np.mean(df_cant.loc["Residuo de Cartón Recolectado (Toneladas)"].values))
    unid_promedio_anual = float(np.mean(df_cant.loc["Total Productos Fabricados (Unidades)"].values))

    res["metricas"]["vac_social"] = round(vac_social)
    res["metricas"]["cae_social"] = round(cae_social)
    res["metricas"]["cae_por_ton_social"] = round(cae_social / ton_promedio_anual) if ton_promedio_anual > 0 else 0
    res["metricas"]["cae_por_unid_social"] = round(cae_social / unid_promedio_anual) if unid_promedio_anual > 0 else 0
    res["metricas"]["vac_privado"] = round(vac_privado)
    res["metricas"]["cae_privado"] = round(cae_privado)

    return res


def calcular_flujo_financiado_con_deuda(res_base, pct_deuda, tasa_interes_deuda, plazo_anios, usar_pro_pyme_escalonado=False):
    """
    Construye la Tabla de Desarrollo del Crédito (Método Francés de Cuota Fija) y el
    Flujo de Caja del Inversionista (Flujo Puro + Flujo de la Deuda con Escudo Tributario),
    según Clase 1 de la Dra. Luz María Ferrada y Anexo 4 de la Metodología General SNI 2025.
    """
    cfg = res_base["cfg"]
    horizonte = int(cfg["HORIZONTE_ANIOS"])
    tasa_priv = float(cfg["TASA_DESCUENTO_PRIVADA"])
    imp_fijo = float(cfg["IMPUESTO_RENTA"])
    df_fp = res_base["df_flujo_privado"]

    desembolso_anio_0 = abs(float(df_fp.loc["(=) FLUJO DE CAJA PRIVADO NETO", "Año 0"]))
    monto_prestamo = round(desembolso_anio_0 * (pct_deuda / 100.0))

    cols_tot = [f"Año {a}" for a in range(0, horizonte + 1)]
    plazo = max(1, min(int(plazo_anios), horizonte))
    r_d = float(tasa_interes_deuda)

    if monto_prestamo <= 0 or r_d <= 0:
        cuota_anual = monto_prestamo / plazo if plazo > 0 else 0.0
    else:
        cuota_anual = monto_prestamo * ((r_d * ((1.0 + r_d) ** plazo)) / (((1.0 + r_d) ** plazo) - 1.0))

    saldo = np.zeros(horizonte + 1)
    interes = np.zeros(horizonte + 1)
    amortizacion = np.zeros(horizonte + 1)
    cuota_arr = np.zeros(horizonte + 1)

    saldo[0] = monto_prestamo
    for a in range(1, horizonte + 1):
        if a <= plazo and saldo[a - 1] > 0:
            inter_a = saldo[a - 1] * r_d if r_d > 0 else 0.0
            amort_a = cuota_anual - inter_a
            if a == plazo:
                amort_a = saldo[a - 1]
                cuota_efectiva = inter_a + amort_a
            else:
                cuota_efectiva = cuota_anual
            interes[a] = round(inter_a)
            amortizacion[a] = round(amort_a)
            cuota_arr[a] = round(cuota_efectiva)
            saldo[a] = max(0.0, round(saldo[a - 1] - amortizacion[a]))

    df_tabla_credito = pd.DataFrame({
        "Saldo Deuda ($)": saldo.astype(int),
        "Cuota Anual ($)": cuota_arr.astype(int),
        "Intereses ($)": interes.astype(int),
        "Amortización Capital ($)": amortizacion.astype(int),
    }, index=cols_tot).T

    tasas_imp = [0.0, 0.125, 0.15] + [0.25] * max(0, horizonte - 2) if usar_pro_pyme_escalonado else [0.0] + [imp_fijo] * horizonte
    tasas_imp_arr = np.array(tasas_imp[:horizonte + 1])

    ahorro_tributario = np.round(interes * tasas_imp_arr)
    prestamo_arr = np.zeros(horizonte + 1)
    prestamo_arr[0] = monto_prestamo

    flujo_deuda = prestamo_arr - interes + ahorro_tributario - amortizacion
    flujo_puro = df_fp.loc["(=) FLUJO DE CAJA PRIVADO NETO"].values.astype(float)
    flujo_inversionista = flujo_puro + flujo_deuda

    df_flujo_financiado = pd.DataFrame({
        "1. Flujo de Caja Puro Neto (Sin Deuda)": flujo_puro.astype(int),
        "(+) Préstamo Recibido en Año 0": prestamo_arr.astype(int),
        "(-) Gasto Financiero (Intereses de la Deuda)": (-interes).astype(int),
        "(+) Ahorro Tributario por Intereses (Escudo Fiscal)": ahorro_tributario.astype(int),
        "(-) Amortización del Préstamo": (-amortizacion).astype(int),
        "2. Flujo de Caja de la Deuda": flujo_deuda.astype(int),
        "3. FLUJO DE CAJA DEL INVERSIONISTA (FINANCIADO)": flujo_inversionista.astype(int),
    }, index=cols_tot).T

    van_fin = float(npf.npv(tasa_priv, flujo_inversionista))
    try:
        tir_fin = float(npf.irr(flujo_inversionista)) * 100.0
    except Exception:
        tir_fin = 0.0
    pb_fin = mod2.calcular_payback(flujo_inversionista)

    return {
        "monto_prestamo": int(monto_prestamo),
        "aporte_propio": int(desembolso_anio_0 - monto_prestamo),
        "cuota_anual": int(round(cuota_anual)),
        "df_tabla_credito": df_tabla_credito,
        "df_flujo_financiado": df_flujo_financiado,
        "van_financiado": round(van_fin),
        "tir_financiada": round(tir_fin, 2) if not np.isnan(tir_fin) else 0.0,
        "payback_financiado": pb_fin,
    }


# ==============================================================================
# 4. FUNCIONES DE FORMATO, PORTADA INSTITUCIONAL ULAGOS Y BIBLIOGRAFÍA APA
# ==============================================================================

def _es_linea_toc(p):
    return len(p._p.findall(qn("w:hyperlink"))) > 0 or len(p._p.findall(qn("w:fldSimple"))) > 0


def _estilizar_run_local(run, size_pt=10.5, bold=False, italic=False, color_rgb=(0, 0, 0)):
    run.font.name = "Arial"
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), "Arial")
    rFonts.set(qn("w:hAnsi"), "Arial")
    rFonts.set(qn("w:cs"), "Arial")
    if rPr.find(qn("w:noProof")) is None:
        rPr.append(OxmlElement("w:noProof"))


def _fmt_int_local(valor):
    return f"{int(round(float(valor))):,}".replace(",", ".")


def _crear_parrafo_interpretacion(doc, titulo_negrita, texto_cuerpo):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15

    r_tit = p.add_run(titulo_negrita + " ")
    _estilizar_run_local(r_tit, size_pt=10.5, bold=True, color_rgb=(0, 0, 0))

    r_txt = p.add_run(texto_cuerpo)
    _estilizar_run_local(r_txt, size_pt=10.5, bold=False, color_rgb=(0, 0, 0))
    return p


def _reemplazar_texto_parrafo_conservando_formato(p, nuevo_texto, size_pt=10.5, bold=False):
    for r in list(p.runs):
        p._p.remove(r._r)
    r_nuevo = p.add_run(nuevo_texto)
    _estilizar_run_local(r_nuevo, size_pt=size_pt, bold=bold, color_rgb=(0, 0, 0))


def _localizar_plantilla_ulagos():
    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(carpeta_script, "plantilla_hoja_carta_institucional_BLANCO.docx"),
        os.path.join(os.getcwd(), "plantilla_hoja_carta_institucional_BLANCO.docx"),
        os.path.join(os.path.dirname(carpeta_script), "plantilla_hoja_carta_institucional_BLANCO.docx"),
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    for raiz, _, archivos in os.walk(carpeta_script):
        for arch in archivos:
            if "plantilla_hoja_carta_institucional" in arch.lower() and arch.lower().endswith(".docx"):
                return os.path.join(raiz, arch)
    return candidatos[0]


def _formatear_bibliografia_apa(doc):
    for p in list(doc.paragraphs):
        if not _es_linea_toc(p) and p.text.strip().startswith("Ilustre Municipalidad de Osorno. (2025)."):
            p._element.getparent().remove(p._element)

    p_tit_ref = None
    idx_tit = None
    for i, p in enumerate(doc.paragraphs):
        if _es_linea_toc(p):
            continue
        t_up = p.text.strip().upper()
        if (
            t_up.startswith("REFERENCIAS Y FUENTES")
            or t_up.startswith("REFERENCIAS OFICIALES")
            or t_up == "BIBLIOGRAFÍA"
            or t_up == "BIBLIOGRAFIA"
        ):
            p_tit_ref = p
            idx_tit = i
            break

    if p_tit_ref is not None and idx_tit is not None:
        a_borrar = []
        for p_sig in doc.paragraphs[idx_tit + 1:]:
            t_sig = p_sig.text.strip()
            t_sig_up = t_sig.upper()
            if (
                t_sig_up.startswith("ANEXO ")
                or re.match(r"^\d+\.", t_sig_up)
                or t_sig_up.startswith("MATRIZ DE ")
            ):
                break
            a_borrar.append(p_sig)
        for p_old in a_borrar:
            p_old._element.getparent().remove(p_old._element)
    else:
        p_anexo1 = None
        for p in doc.paragraphs:
            if not _es_linea_toc(p) and p.text.strip().upper().startswith("ANEXO 1"):
                p_anexo1 = p
                break
        p_tit_ref = doc.add_paragraph()
        if p_anexo1 is not None:
            p_anexo1._p.addprevious(p_tit_ref._p)

    _reemplazar_texto_parrafo_conservando_formato(p_tit_ref, "Bibliografía", size_pt=11.5, bold=True)
    p_tit_ref.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_tit_ref.paragraph_format.space_before = Pt(12)
    p_tit_ref.paragraph_format.space_after = Pt(6)
    p_tit_ref.paragraph_format.keep_with_next = True

    referencias_apa = [
        (
            "Ilustre Municipalidad de Osorno. (2025). ",
            "Antecedentes de contratos de recolección de residuos sólidos domiciliarios, operación del Vertedero Provincial de Curaco y registros comunales SINADER",
            ". Dirección de Medio Ambiente, Aseo y Ornato."
        ),
        (
            "Ministerio de Desarrollo Social y Familia [MIDESO]. (2024). ",
            "Metodología para la formulación y evaluación social de proyectos de gestión de residuos sólidos domiciliarios y asimilables",
            ". División de Evaluación Social de Inversiones."
        ),
        (
            "Ministerio de Desarrollo Social y Familia [MIDESO]. (2025). ",
            "Metodología general de preparación y evaluación de proyectos de inversión pública",
            ". Sistema Nacional de Inversiones (SNI)."
        ),
        (
            "Ministerio de Desarrollo Social y Familia [MIDESO]. (2026). ",
            "Precios sociales vigentes 2026 para el Sistema Nacional de Inversiones (Tasa Social de Descuento, Mano de Obra y Divisa)",
            ". Gobierno de Chile. https://sni.gob.cl"
        ),
        (
            "Ministerio del Medio Ambiente [MMA]. (2016). ",
            "Ley N° 20.920: Establece marco para la gestión de residuos, la responsabilidad extendida del productor y fomento al reciclaje (Ley REP)",
            ". Diario Oficial de la República de Chile."
        ),
        (
            "Ministerio de Salud [MINSAL]. (2005). ",
            "Decreto Supremo N° 114/2005: Aprueba reglamento sobre seguridad de los juguetes",
            ". Diario Oficial de la República de Chile."
        ),
        (
            "Sapag Chain, N., Sapag Chain, R., & Sapag Puelma, J. M. (2014). ",
            "Preparación y evaluación de proyectos",
            " (6.ª ed.). McGraw-Hill Education."
        ),
        (
            "Servicio de Impuestos Internos [SII]. (2025). ",
            "Circular N° 53/2025: Instrucciones sobre el Régimen Pro Pyme General (Artículo 14 letra D de la Ley sobre Impuesto a la Renta)",
            ". Gobierno de Chile."
        ),
    ]

    ultimo_nodo = p_tit_ref._p
    for parte_autor, parte_cursiva, parte_final in referencias_apa:
        p_apa = doc.add_paragraph()
        p_apa.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_apa.paragraph_format.left_indent = Inches(0.5)
        p_apa.paragraph_format.first_line_indent = Inches(-0.5)
        p_apa.paragraph_format.space_before = Pt(2)
        p_apa.paragraph_format.space_after = Pt(5)
        p_apa.paragraph_format.line_spacing = 1.15

        r1 = p_apa.add_run(parte_autor)
        _estilizar_run_local(r1, size_pt=10.5, bold=False, italic=False)
        r2 = p_apa.add_run(parte_cursiva)
        _estilizar_run_local(r2, size_pt=10.5, bold=False, italic=True)
        r3 = p_apa.add_run(parte_final)
        _estilizar_run_local(r3, size_pt=10.5, bold=False, italic=False)

        ultimo_nodo.addnext(p_apa._p)
        ultimo_nodo = p_apa._p


def _aplicar_plantilla_institucional_ulagos(ruta_word, ruta_plantilla):
    if not ruta_plantilla or not os.path.exists(ruta_plantilla):
        return

    doc_gen = Document(ruta_word)
    xml_gen = doc_gen.element.body.xml
    if "p_carta_portadas_institucionales" in xml_gen or "rIdULagosPortada" in xml_gen:
        for anchor in doc_gen.element.body.findall(".//" + qn("wp:anchor")):
            anchor.set("behindDoc", "1")
        doc_gen.save(ruta_word)
        return

    with tempfile.TemporaryDirectory() as tmp_z:
        dir_tpl = os.path.join(tmp_z, "tpl")
        dir_doc = os.path.join(tmp_z, "doc")
        with zipfile.ZipFile(ruta_plantilla, "r") as zt:
            zt.extractall(dir_tpl)
        with zipfile.ZipFile(ruta_word, "r") as zd:
            zd.extractall(dir_doc)

        media_tpl = os.path.join(dir_tpl, "word", "media")
        media_doc = os.path.join(dir_doc, "word", "media")
        os.makedirs(media_doc, exist_ok=True)

        tpl_rels_path = os.path.join(dir_tpl, "word", "_rels", "document.xml.rels")
        mapa_rid_tpl = {}
        if os.path.exists(tpl_rels_path):
            with open(tpl_rels_path, "r", encoding="utf-8") as fr:
                rels_tpl_txt = fr.read()
            for m_rel in re.finditer(r'Id="(rId\d+)"[^>]+Target="media/([^"]+)"', rels_tpl_txt):
                mapa_rid_tpl[m_rel.group(1)] = m_rel.group(2)

        tpl_doc_xml_path = os.path.join(dir_tpl, "word", "document.xml")
        with open(tpl_doc_xml_path, "r", encoding="utf-8") as fr:
            tpl_doc_xml = fr.read()

        drawings_tpl = re.findall(r"(<w:drawing>.*?</w:drawing>)", tpl_doc_xml, flags=re.DOTALL)
        img_portada_nombre = "image1.png"
        draw_portada_xml = ""
        if drawings_tpl:
            raw_draw_1 = drawings_tpl[0]
            m_rid = re.search(r'r:embed="(rId\d+)"', raw_draw_1)
            if m_rid and m_rid.group(1) in mapa_rid_tpl:
                img_portada_nombre = mapa_rid_tpl[m_rid.group(1)]
            draw_portada_xml = re.sub(r'r:embed="rId\d+"', 'r:embed="rIdULagosPortada"', raw_draw_1)
            draw_portada_xml = draw_portada_xml.replace('behindDoc="0"', 'behindDoc="1"')

        src_portada_img = os.path.join(media_tpl, img_portada_nombre)
        if os.path.exists(src_portada_img):
            shutil.copy2(src_portada_img, os.path.join(media_doc, "ulagos_portada.png"))
        for img_cand, dest_name in [("image2.png", "ulagos_contraportada.png"), ("image3.png", "ulagos_header.png")]:
            p_src = os.path.join(media_tpl, img_cand)
            if os.path.exists(p_src):
                shutil.copy2(p_src, os.path.join(media_doc, dest_name))

        rels_dir = os.path.join(dir_doc, "word", "_rels")
        os.makedirs(rels_dir, exist_ok=True)

        for hf in ["header1.xml", "header2.xml", "header3.xml", "footer1.xml", "footer2.xml", "footer3.xml"]:
            src_hf = os.path.join(dir_tpl, "word", hf)
            if os.path.exists(src_hf):
                shutil.copy2(src_hf, os.path.join(dir_doc, "word", hf))

            src_hrel = os.path.join(dir_tpl, "word", "_rels", hf + ".rels")
            if os.path.exists(src_hrel):
                with open(src_hrel, "r", encoding="utf-8") as fr:
                    txt_rel = fr.read()
                for m_img in re.finditer(r'Target="media/([^"]+)"', txt_rel):
                    nombre_orig = m_img.group(1)
                    src_h_img = os.path.join(media_tpl, nombre_orig)
                    if os.path.exists(src_h_img):
                        shutil.copy2(src_h_img, os.path.join(media_doc, "ulagos_header.png"))
                    txt_rel = txt_rel.replace(f"media/{nombre_orig}", "media/ulagos_header.png")
                with open(os.path.join(rels_dir, hf + ".rels"), "w", encoding="utf-8") as fw:
                    fw.write(txt_rel)

        doc_rels_path = os.path.join(rels_dir, "document.xml.rels")
        with open(doc_rels_path, "r", encoding="utf-8") as fr:
            rels_xml = fr.read()

        nuevas_rels = (
            '<Relationship Id="rIdULagosPortada" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/ulagos_portada.png"/>'
            '<Relationship Id="rIdULagosH1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>'
            '<Relationship Id="rIdULagosH2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header2.xml"/>'
            '<Relationship Id="rIdULagosH3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header3.xml"/>'
            '<Relationship Id="rIdULagosF1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
            '<Relationship Id="rIdULagosF2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer2.xml"/>'
            '<Relationship Id="rIdULagosF3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer3.xml"/>'
        )
        if "rIdULagosPortada" not in rels_xml:
            rels_xml = rels_xml.replace("</Relationships>", nuevas_rels + "</Relationships>")
            with open(doc_rels_path, "w", encoding="utf-8") as fw:
                fw.write(rels_xml)

        ct_path = os.path.join(dir_doc, "[Content_Types].xml")
        with open(ct_path, "r", encoding="utf-8") as fr:
            ct_xml = fr.read()
        if 'Extension="png"' not in ct_xml:
            ct_xml = ct_xml.replace("</Types>", '<Default Extension="png" ContentType="image/png"/></Types>')
        overrides_hf = (
            '<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
            '<Override PartName="/word/header2.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
            '<Override PartName="/word/header3.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
            '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
            '<Override PartName="/word/footer2.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
            '<Override PartName="/word/footer3.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
        )
        if "/word/header1.xml" not in ct_xml:
            ct_xml = ct_xml.replace("</Types>", overrides_hf + "</Types>")
        with open(ct_path, "w", encoding="utf-8") as fw:
            fw.write(ct_xml)

        doc_xml_path = os.path.join(dir_doc, "word", "document.xml")
        with open(doc_xml_path, "r", encoding="utf-8") as fr:
            doc_xml = fr.read()

        if 'xmlns:wp14=' not in doc_xml:
            doc_xml = doc_xml.replace(
                "<w:document ",
                '<w:document xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
                'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
                'xmlns:v="urn:schemas-microsoft-com:vml" '
                'xmlns:o="urn:schemas-microsoft-com:office:office" '
                'xmlns:w10="urn:schemas-microsoft-com:office:word" '
            )

        if draw_portada_xml and "rIdULagosPortada" not in doc_xml:
            p_fondo_portada = (
                f'<w:p><w:pPr><w:spacing w:before="0" w:after="0"/></w:pPr>'
                f'<w:r><w:rPr><w:noProof/></w:rPr>{draw_portada_xml}</w:r></w:p>'
            )
            doc_xml = doc_xml.replace("<w:body>", "<w:body>" + p_fondo_portada, 1)

        refs_sect = (
            '<w:headerReference w:type="even" r:id="rIdULagosH1"/>'
            '<w:headerReference w:type="default" r:id="rIdULagosH2"/>'
            '<w:footerReference w:type="even" r:id="rIdULagosF1"/>'
            '<w:footerReference w:type="default" r:id="rIdULagosF2"/>'
            '<w:headerReference w:type="first" r:id="rIdULagosH3"/>'
            '<w:footerReference w:type="first" r:id="rIdULagosF3"/>'
            '<w:titlePg/>'
        )
        if "rIdULagosH2" not in doc_xml:
            doc_xml = re.sub(r"<w:headerReference[^/>]*/>", "", doc_xml)
            doc_xml = re.sub(r"<w:footerReference[^/>]*/>", "", doc_xml)
            doc_xml = re.sub(r"<w:titlePg[^/>]*/>", "", doc_xml)
            doc_xml = re.sub(r"(<w:sectPr[^>]*>)", r"\1" + refs_sect, doc_xml)

        with open(doc_xml_path, "w", encoding="utf-8") as fw:
            fw.write(doc_xml)

        with zipfile.ZipFile(ruta_word, "w", zipfile.ZIP_DEFLATED) as zout:
            for root_d, _, files_d in os.walk(dir_doc):
                for file_d in files_d:
                    full_p = os.path.join(root_d, file_d)
                    rel_p = os.path.relpath(full_p, dir_doc)
                    zout.write(full_p, arcname=rel_p)


def _transformar_tablas_word_estilo_estudiante(doc):
    for tbl in doc.tables:
        if len(tbl.rows) == 0:
            continue
        for cell in tbl.rows[0].cells:
            for p in cell.paragraphs:
                if "Para tu Defensa y Entrega" in p.text:
                    _reemplazar_texto_parrafo_conservando_formato(
                        p, "Explicación y Justificación Técnica en Osorno", size_pt=8.0, bold=True
                    )
            tcPr = cell._tc.get_or_add_tcPr()
            for shd_old in tcPr.findall(qn("w:shd")):
                tcPr.remove(shd_old)
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), "D9E2F3")
            tcPr.append(shd)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.color.rgb = RGBColor(0, 0, 0)
                    r.font.bold = True

        for r_idx, row in enumerate(tbl.rows):
            for cell in row.cells:
                tcPr = cell._tc.get_or_add_tcPr()
                if r_idx > 0:
                    for shd_old in tcPr.findall(qn("w:shd")):
                        tcPr.remove(shd_old)
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:color"), "auto")
                    shd.set(qn("w:fill"), "FFFFFF")
                    tcPr.append(shd)
                tcBorders = tcPr.first_child_found_in("w:tcBorders")
                if tcBorders is not None:
                    tcPr.remove(tcBorders)
                tcBorders = OxmlElement("w:tcBorders")
                for edge in ["top", "bottom", "left", "right"]:
                    el = OxmlElement(f"w:{edge}")
                    el.set(qn("w:val"), "single")
                    el.set(qn("w:sz"), "6" if r_idx == 0 and edge in ["top", "bottom"] else "4")
                    el.set(qn("w:color"), "000000" if r_idx == 0 else "64748B")
                    tcBorders.append(el)
                tcPr.append(tcBorders)


def _reemplazar_integrantes_en_parrafo(p):
    reemplazado_en_run = False
    for r in p.runs:
        if "EQUIPO FORMULADOR (INTEGRANTES):" in r.text:
            r.text = r.text.replace("EQUIPO FORMULADOR (INTEGRANTES):", "INTEGRANTES:")
            reemplazado_en_run = True
        elif "EQUIPO FORMULADOR:" in r.text:
            r.text = r.text.replace("EQUIPO FORMULADOR:", "INTEGRANTES:")
            reemplazado_en_run = True

    if not reemplazado_en_run and "EQUIPO FORMULADOR" in p.text.upper():
        lineas = p.text.splitlines()
        if len(lineas) <= 1:
            _reemplazar_texto_parrafo_conservando_formato(p, "INTEGRANTES:", size_pt=10.5, bold=True)
        else:
            p_nuevo_txt = re.sub(
                r"EQUIPO FORMULADOR\s*(\(INTEGRANTES\))?\s*:",
                "INTEGRANTES:",
                p.text,
                flags=re.IGNORECASE,
            )
            _reemplazar_texto_parrafo_conservando_formato(p, p_nuevo_txt, size_pt=10.5, bold=True)


def _limpiar_titulos_y_portada(doc):
    reemplazos_titulos = [
        (" (PUNTO 4.3)", ""),
        (" (45 DÍAS DE DESFASE - PUNTO 6)", " (MÉTODO DE 45 DÍAS DE DESFASE)"),
        (" (PUNTO 7)", ""),
        (" (FLUJO SOCIAL MIDESO - PUNTO 8)", " (METODOLOGÍA MIDESO / SNI)"),
        (" (PUNTO 9 PAUTA)", ""),
        (" (PUNTO 10 PAUTA)", ""),
        (" (EXPLICACIÓN FÁCIL DE ENTENDER)", " (MEMORIA DE CÁLCULO Y SUPUESTOS)"),
    ]
    for idx_p, p in enumerate(doc.paragraphs):
        txt = p.text.strip()

        if idx_p < 25 and txt.startswith("Estudio a 10 años basado en 6 locales"):
            p._element.getparent().remove(p._element)
            continue

        if idx_p < 35 and "EQUIPO FORMULADOR" in txt.upper():
            _reemplazar_integrantes_en_parrafo(p)
            continue

        txt_orig = p.text
        modificado = False
        for viejo, nuevo in reemplazos_titulos:
            if viejo in txt_orig:
                txt_orig = txt_orig.replace(viejo, nuevo)
                modificado = True

        if "(#446 al #1024)" in txt_orig or "números #446 y #1024" in txt_orig:
            txt_orig = txt_orig.replace(" (#446 al #1024)", "").replace(" (entre los números #446 y #1024)", "")
            modificado = True

        if modificado:
            if _es_linea_toc(p):
                for t_el in p._p.findall(".//" + qn("w:t")):
                    if t_el.text:
                        for viejo, nuevo in reemplazos_titulos:
                            t_el.text = t_el.text.replace(viejo, nuevo)
            else:
                es_titulo = bool(re.match(r"^\d+\.", txt) or txt.upper().startswith("ANEXO "))
                _reemplazar_texto_parrafo_conservando_formato(
                    p, txt_orig, size_pt=11.5 if es_titulo else 10.5, bold=es_titulo
                )

        if not _es_linea_toc(p) and (txt.upper().startswith("ANEXO ") or re.match(r"^\d+\.", txt)):
            p.paragraph_format.keep_with_next = True

    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if "EQUIPO FORMULADOR" in p.text.upper():
                        _reemplazar_integrantes_en_parrafo(p)
                    elif "#" in p.text:
                        for r in p.runs:
                            if "#" in r.text:
                                r.text = r.text.replace(" (#446 al #1024)", "")
                                r.text = re.sub(r"\(#\d+\)", "", r.text)
                                r.text = re.sub(r"#(\d+)", r"\1", r.text)


def _aplicar_redaccion_e_interpretaciones_oliver_en_word(ruta_word, resultados_vivos, cfg_vivo):
    doc = mod2.Document(ruta_word)
    m = resultados_vivos["metricas"]

    tp = cfg_vivo["TASA_DESCUENTO_PRIVADA"] * 100
    ts = cfg_vivo["TASA_DESCUENTO_SOCIAL"] * 100
    dias_ct = int(cfg_vivo.get("DIAS_DESFASE_CT", 45))
    ton_a1 = float(cfg_vivo.get("RESIDUO_TON_ANIO_1", 15.0))
    kilos_a1 = int(round(ton_a1 * 1000))
    kilos_util = int(round(kilos_a1 * 0.70))
    kilos_merma = kilos_a1 - kilos_util

    p1_u = int(cfg_vivo.get("P1_UNIDADES", 3000))
    p1_p = float(cfg_vivo.get("P1_PRECIO_BRUTO", 16000))
    p1_neto = round(p1_p / (1.0 + float(cfg_vivo.get("IVA", 0.19))))
    p1_kg = float(cfg_vivo.get("P1_KG_CARTON", 2.5))

    p2_u = int(cfg_vivo.get("P2_UNIDADES", 1500))
    p2_p = float(cfg_vivo.get("P2_PRECIO_BRUTO", 19000))
    p2_neto = round(p2_p / (1.0 + float(cfg_vivo.get("IVA", 0.19))))
    p2_kg = float(cfg_vivo.get("P2_KG_CARTON", 2.0))

    inv_bruta = sum(float(x["monto_bruto"]) for x in cfg_vivo["INVERSIONES_LISTA"])
    inv_neta = round(inv_bruta / (1.0 + float(cfg_vivo.get("IVA", 0.19))))
    ct_inicial = m.get("ct_inicial", 6961008)

    idx_res = None
    for i, p in enumerate(doc.paragraphs):
        if not _es_linea_toc(p) and p.text.strip().upper() == "RESUMEN EJECUTIVO":
            idx_res = i
            break

    if idx_res is not None and idx_res + 4 < len(doc.paragraphs):
        txt_res_1 = (
            f"“{cfg_vivo['NOMBRE_PROYECTO']}” nace de una problemática medioambiental concreta en la comuna, cuyo objetivo "
            f"busca disminuir la cantidad de cartón comercial desperdiciado en la zona céntrica de Osorno. El proyecto evalúa "
            f"a {cfg_vivo['HORIZONTE_ANIOS']} años la creación de un taller productivo en el sector industrial de Ovejería, "
            f"dedicado a recoger cajas de cartón limpias del comercio céntrico para transformarlas en juegos educativos para "
            f"niños y juegos de estimulación de memoria para adultos mayores. La problemática actual en el centro de Osorno es "
            f"muy concreta: todos los días entre las 06:00 y 07:00 de la mañana pasa el camión recolector municipal por la calle "
            f"Eleuterio Ramírez, recoge todo el cartón limpio que dejan las tiendas, lo mezcla con basura común y posteriormente "
            f"lo entierra en el Vertedero Provincial de Curaco."
        )
        txt_res_2 = (
            f"Para trabajar con números reales y fáciles de comprobar en terreno, nuestro proyecto recoge el cartón de 6 locales "
            f"comerciales ubicados en calle Eleuterio Ramírez: Hojalatería Lynch, Autoplanet, Zapatería La Malagueña, "
            f"Minimarket El Sabrosón, Galería Centrosorno y Liquimax. El furgón contratado por “{cfg_vivo['NOMBRE_PROYECTO']}” "
            f"pasa previo al camión recolector de basura municipal, aproximadamente entre las 05:30 y 06:00 AM, logrando retirar "
            f"50 kilos diarios de cartón limpio, lo que se traduce en 1.250 kilos mensuales al recolectar 25 días hábiles por mes, "
            f"equivalentes exactamente a {mod2.fmt_dec_cl(ton_a1, 2)} toneladas ({_fmt_int_local(kilos_a1)} kilos) en el Año 1."
        )
        txt_res_3 = (
            f"Considerando los {_fmt_int_local(kilos_a1)} kilos anuales recolectados, el 70% ({_fmt_int_local(kilos_util)} kilos = "
            f"{mod2.fmt_dec_cl(ton_a1 * 0.70, 2)} toneladas) se aprovecha directamente en la elaboración de los productos y el 30% restante "
            f"({_fmt_int_local(kilos_merma)} kilos = {mod2.fmt_dec_cl(ton_a1 * 0.30, 2)} toneladas) corresponde a recortes sobrantes y bordes "
            f"con corchetes o cintas, los cuales se segregan y entregan a reciclaje autorizado. Con los {_fmt_int_local(kilos_util)} kilos útiles "
            f"se fabrican dos productos validados con 3 compradores institucionales directos en Osorno: 1ro, {cfg_vivo['P1_NOMBRE']} "
            f"({_fmt_int_local(p1_u)} unidades al año, utilizando {mod2.fmt_dec_cl(p1_kg, 2)} kilos de cartón por unidad, equivalentes a "
            f"{_fmt_int_local(int(p1_u * p1_kg))} kilos anuales) a un precio de {mod2.fmt_clp(p1_p)} IVA incluido ({mod2.fmt_clp(p1_neto)} sin IVA), "
            f"cuyos compradores son el DAEM de Osorno y jardines infantiles privados; y 2do, {cfg_vivo['P2_NOMBRE']} "
            f"({_fmt_int_local(p2_u)} unidades por año, utilizando {mod2.fmt_dec_cl(p2_kg, 2)} kilos de cartón por unidad, equivalentes a "
            f"{_fmt_int_local(int(p2_u * p2_kg))} kilos anuales) a un precio de comercialización de {mod2.fmt_clp(p2_p)} IVA incluido "
            f"({mod2.fmt_clp(p2_neto)} sin IVA), orientado al Hogar de Ancianos Santa María de Osorno y clubes de adulto mayor."
        )
        txt_res_4 = (
            f"En la evaluación privada, considerando una inversión inicial de {mod2.fmt_clp(inv_bruta)} con IVA en maquinaria y habilitación "
            f"del galpón en Ovejería ({mod2.fmt_clp(inv_neta)} netos sin IVA), más un capital de trabajo inicial de {mod2.fmt_clp(ct_inicial)} "
            f"destinado a cubrir {dias_ct} días de operación, y exigiendo una tasa de descuento anual del {mod2.fmt_dec_cl(tp, 1)}%, se obtiene "
            f"un VAN privado positivo de {mod2.fmt_clp(m['van_privado'])}, una TIR de {mod2.fmt_dec_cl(m['tir_privada'], 2)}% y un período de "
            f"recuperación de la inversión de {mod2.fmt_dec_cl(m['payback_privado'], 2)} años. En el ámbito social MIDESO / SNI, aplicando "
            f"una tasa social de descuento del {mod2.fmt_dec_cl(ts, 1)}% anual y contabilizando el ahorro municipal de "
            f"{mod2.fmt_clp(cfg_vivo['AHORRO_MUNI_TON'])} por tonelada con IVA por no enterrar este cartón en el Vertedero de Curaco, "
            f"el VAN social asciende a {mod2.fmt_clp(m['van_social'])} y la TIR Social alcanza un {mod2.fmt_dec_cl(m['tir_social'], 2)}%."
        )
        _reemplazar_texto_parrafo_conservando_formato(doc.paragraphs[idx_res + 1], txt_res_1)
        _reemplazar_texto_parrafo_conservando_formato(doc.paragraphs[idx_res + 2], txt_res_2)
        _reemplazar_texto_parrafo_conservando_formato(doc.paragraphs[idx_res + 3], txt_res_3)
        _reemplazar_texto_parrafo_conservando_formato(doc.paragraphs[idx_res + 4], txt_res_4)

    for i, p in enumerate(doc.paragraphs):
        if not _es_linea_toc(p) and p.text.strip().upper().startswith("1. EL PROBLEMA EN OSORNO"):
            if i + 2 < len(doc.paragraphs):
                _reemplazar_texto_parrafo_conservando_formato(
                    doc.paragraphs[i + 1],
                    "El Vertedero Provincial de Curaco en Osorno tiene cada vez menos capacidad disponible porque recibe a diario "
                    "toneladas de cartón limpio que podrían aprovecharse productivamente en la misma comuna. En calle Eleuterio Ramírez, "
                    "las ferreterías, tiendas de repuestos automotrices, zapaterías, minimarkets y distribuidoras mayoristas desocupan "
                    "todos los días cajas de cartón corrugado grueso y resistente. Como no poseen bodegas amplias para almacenar este "
                    "material, lo sacan temprano a la vereda para que el camión recolector municipal lo retire entre las 06:00 y 07:00 AM "
                    "en dirección al vertedero."
                )
                _reemplazar_texto_parrafo_conservando_formato(
                    doc.paragraphs[i + 2],
                    "Se salió a terreno en el eje comercial de calle Eleuterio Ramírez, lo cual permitió catastrar y comprometer "
                    "a 6 locales comerciales reales que entregan en conjunto 50 kilos de cartón limpio por día trabajado (de lunes a sábado). "
                    "Esto representa un flujo comprobable de 1.250 kilos por mes en 25 días hábiles, acumulando un total exacto de 15,00 toneladas "
                    "al año en el Año 1. El detalle de cada local catastrado se presenta en la Tabla 1.1:"
                )
            break

    marcadores_previos = [
        "Interpretación de la dotación",
        "Interpretación de las inversiones",
        "Interpretación del capital de trabajo",
        "Interpretación financiera del flujo",
        "Interpretación de la evaluación social",
    ]
    for p in list(doc.paragraphs):
        if any(p.text.strip().startswith(mp) for mp in marcadores_previos):
            p._element.getparent().remove(p._element)

    p_sec5 = p_sec6 = p_sec7 = p_sec8 = p_sec9 = None
    for p in doc.paragraphs:
        if _es_linea_toc(p):
            continue
        t = p.text.strip().upper()
        if t.startswith("5. TABLAS DE PRODUCCIÓN") and p_sec5 is None:
            p_sec5 = p
        elif t.startswith("6. CÁLCULO DEL CAPITAL DE TRABAJO") and p_sec6 is None:
            p_sec6 = p
        elif t.startswith("7. FLUJO DE CAJA PRIVADO") and p_sec7 is None:
            p_sec7 = p
        elif t.startswith("8. EVALUACIÓN SOCIAL DEL PROYECTO") and p_sec8 is None:
            p_sec8 = p
        elif t.startswith("9. CONCLUSIONES PRINCIPALES") and p_sec9 is None:
            p_sec9 = p

    if p_sec5 is not None:
        df_p_live = resultados_vivos["df_personal"]
        n_trab_live = int(df_p_live["Cant."].sum())
        anual_priv_live = float(df_p_live["Costo Anual Privado ($)"].sum())
        mens_priv_live = anual_priv_live / 12.0
        anual_soc_live = float(df_p_live["Costo Anual Social ($)"].sum())
        p_int_pers = _crear_parrafo_interpretacion(
            doc,
            "Interpretación de la dotación y precios sociales de la mano de obra:",
            f"La estructura salarial del taller en Ovejería considera {n_trab_live} trabajadores a jornada completa con un desembolso privado de "
            f"{mod2.fmt_clp(mens_priv_live)} mensuales ({mod2.fmt_clp(anual_priv_live)} al año). Al aplicar los factores de corrección social de MIDESO / SNI "
            f"(que descuentan distorsiones previsionales e impuestos al trabajo y reflejan el costo de oportunidad real de emplear mano de obra local en Osorno), "
            f"el costo social efectivo para el país asciende a {mod2.fmt_clp(anual_soc_live)} anuales, generando un beneficio social neto por creación de empleo formal en la comuna."
        )
        p_sec5._p.addprevious(p_int_pers._p)

    if p_sec6 is not None:
        p_int_inv = _crear_parrafo_interpretacion(
            doc,
            "Interpretación de las inversiones, costos operativos e ingresos proyectados:",
            f"La inversión inicial de {mod2.fmt_clp(inv_bruta)} con IVA equivale a {mod2.fmt_clp(inv_neta)} netos en el flujo de caja privado, "
            f"debido a que el IVA crédito fiscal de las máquinas y del acondicionamiento del galpón se recupera contablemente contra el IVA débito "
            f"de las ventas del primer año. Asimismo, en el Año 5 se programa una reinversión puntual de $4.621.848 netos para renovar la guillotina "
            f"cortadora y el equipo de serigrafía al cumplirse su vida útil económica de 5 años, asegurando la continuidad operativa hasta el Año 10 "
            f"bajo un crecimiento orgánico del {mod2.fmt_dec_cl(cfg_vivo['TASA_CRECIMIENTO']*100, 1)}% anual."
        )
        p_sec6._p.addprevious(p_int_inv._p)

    if p_sec7 is not None:
        p_int_ct = _crear_parrafo_interpretacion(
            doc,
            "Interpretación del capital de trabajo y su recuperación:",
            f"El monto de {mod2.fmt_clp(ct_inicial)} calculado por el método del período de desfase ({dias_ct} días) representa el colchón de "
            f"liquidez indispensable en el Año 0 para pagar mes y medio de sueldos, arriendo en Ovejería, fletes en calle Eleuterio Ramírez y pinturas "
            f"al agua mientras el DAEM de Osorno y los jardines infantiles procesan el pago de las primeras facturas (entre 30 y 45 días). A medida que "
            f"las ventas crecen un 5% cada año, se inyectan pequeños incrementos de capital de trabajo, y al cierre del Año 10 el fondo acumulado "
            f"se recupera íntegramente como entrada de caja positiva."
        )
        p_sec7._p.addprevious(p_int_ct._p)

    if p_sec8 is not None:
        p_int_fp = _crear_parrafo_interpretacion(
            doc,
            "Interpretación financiera del flujo de caja privado:",
            f"Los resultados del flujo privado demuestran que el negocio es autosustentable desde el primer año de operación (flujo neto positivo "
            f"en el Año 1 tras cubrir todos los costos fijos, variables e impuestos). Se observa en el Año 5 una moderación temporal del flujo neto "
            f"producto de la renovación programada de equipos ($4,62 millones netos), retomando su tendencia creciente entre los Años 6 y 10. "
            f"Con un VAN privado de {mod2.fmt_clp(m['van_privado'])} (descontado al {mod2.fmt_dec_cl(tp, 1)}% anual) y una TIR del "
            f"{mod2.fmt_dec_cl(m['tir_privada'], 2)}% —más de cuatro veces superior a la tasa exigida por el inversionista—, el capital invertido "
            f"se recupera en apenas {mod2.fmt_dec_cl(m['payback_privado'], 2)} años."
        )
        p_sec8._p.addprevious(p_int_fp._p)

    if p_sec9 is not None:
        p_int_fs = _crear_parrafo_interpretacion(
            doc,
            "Interpretación de la evaluación social MIDESO y del análisis de sensibilidad:",
            f"Al evaluar el proyecto desde la óptica del bienestar de la comuna de Osorno y del país (tasa social del {mod2.fmt_dec_cl(ts, 1)}%), "
            f"el VANS se eleva a {mod2.fmt_clp(m['van_social'])} con una TIR Social de {mod2.fmt_dec_cl(m['tir_social'], 2)}%. Esta diferencia favorable "
            f"respecto a la evaluación privada se explica por tres razones técnicas: (1) se excluyen el IVA y el Impuesto a la Renta por ser transferencias "
            f"internas dentro de la sociedad; (2) el costo social de la mano de obra es menor gracias a los factores sombra de MIDESO; y (3) se incorpora "
            f"el ahorro municipal directo por cada tonelada de cartón que deja de recolectarse y enterrarse en el Vertedero Provincial de Curaco. "
            f"Finalmente, el análisis de sensibilidad confirma la solidez del proyecto: incluso ante una caída del 15% en los precios/ingresos, un alza "
            f"del 10% en todos los costos o un escenario estancado con 0% de crecimiento anual, tanto el VAN privado como el VANS social se mantienen positivos."
        )
        p_sec9._p.addprevious(p_int_fs._p)

    _limpiar_titulos_y_portada(doc)
    _formatear_bibliografia_apa(doc)
    _transformar_tablas_word_estilo_estudiante(doc)

    doc.save(ruta_word)


def _transformar_excels_estilo_oliver(rutas_excels):
    fill_blanco = PatternFill("solid", fgColor="FFFFFF")
    fill_header_suave = PatternFill("solid", fgColor="D9E1F2")
    fill_total_suave = PatternFill("solid", fgColor="EDEDED")

    font_titulo = Font(name="Calibri", size=12, bold=True, color="000000")
    font_sub = Font(name="Calibri", size=10, italic=True, color="000000")
    font_header = Font(name="Calibri", size=10, bold=True, color="000000")

    borde_fino = Border(
        left=Side(style="thin", color="808080"),
        right=Side(style="thin", color="808080"),
        top=Side(style="thin", color="808080"),
        bottom=Side(style="thin", color="808080"),
    )

    for ruta_xlsx in rutas_excels:
        if not os.path.exists(ruta_xlsx):
            continue
        wb = openpyxl.load_workbook(ruta_xlsx)
        es_excel_2 = "2_Excel" in os.path.basename(ruta_xlsx)

        for idx_s, ws in enumerate(wb.sheetnames):
            sheet = wb[ws]
            sheet.sheet_properties.tabColor = None
            sheet.views.sheetView[0].showGridLines = True

            if es_excel_2 and idx_s == 0:
                sheet["A1"].value = "Proyecto Cartón Vivo Osorno - Catastro de 6 Locales en Calle Eleuterio Ramírez"
                sheet["A2"].value = "Retiro aproximadamente entre las 05:30 y 06:00 am (antes del paso del camión recolector municipal)."

            for r_idx in range(1, sheet.max_row + 1):
                for c_idx in range(1, sheet.max_column + 1):
                    cell = sheet.cell(row=r_idx, column=c_idx)
                    if isinstance(cell.value, str) and "#" in cell.value:
                        cell.value = re.sub(r"#(\d+)", r"\1", cell.value.replace(" (#446 al #1024)", ""))
                    if r_idx == 1:
                        cell.fill = fill_blanco
                        cell.font = font_titulo
                    elif r_idx == 2:
                        cell.fill = fill_blanco
                        cell.font = font_sub
                    elif r_idx == 4:
                        cell.fill = fill_header_suave
                        cell.font = font_header
                        cell.border = borde_fino
                    elif r_idx > 4:
                        fg = cell.fill.fgColor.rgb if (cell.fill and cell.fill.fgColor) else ""
                        if fg and any(cod in str(fg).upper() for cod in ["0F172A", "1E293B", "1E3A8A", "DBEAFE", "DCFCE7"]):
                            cell.fill = fill_total_suave
                        if cell.font:
                            es_negrita = bool(cell.font.bold)
                            cell.font = Font(name="Calibri", size=10, bold=es_negrita, color="000000")

        wb.save(ruta_xlsx)


def _crear_entrada_toc_con_puntos(doc, texto_sec, anchor_name, pag_str="20", nivel=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3.5 if nivel == 1 else 1.5)
    p.paragraph_format.space_after = Pt(3.5 if nivel == 1 else 1.5)
    p.paragraph_format.left_indent = Inches(0.0 if nivel == 1 else 0.25)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.65), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("w:anchor"), anchor_name)
    hyperlink.set(qn("w:history"), "1")

    def _run_xml(txt, bold=True, pt=10):
        r_el = OxmlElement("w:r")
        rPr = OxmlElement("w:rPr")
        rFonts = OxmlElement("w:rFonts")
        rFonts.set(qn("w:ascii"), "Arial")
        rFonts.set(qn("w:hAnsi"), "Arial")
        rFonts.set(qn("w:cs"), "Arial")
        rPr.append(rFonts)
        rPr.append(OxmlElement("w:noProof"))
        if bold:
            rPr.append(OxmlElement("w:b"))
            rPr.append(OxmlElement("w:bCs"))
        c_el = OxmlElement("w:color")
        c_el.set(qn("w:val"), "000000")
        rPr.append(c_el)
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), str(int(pt * 2)))
        szCs = OxmlElement("w:szCs")
        szCs.set(qn("w:val"), str(int(pt * 2)))
        rPr.append(sz)
        rPr.append(szCs)
        r_el.append(rPr)
        t_el = OxmlElement("w:t")
        t_el.text = txt
        r_el.append(t_el)
        return r_el

    hyperlink.append(_run_xml(texto_sec, bold=(nivel == 1), pt=10 if nivel == 1 else 9.5))

    r_tab = OxmlElement("w:r")
    rPr_t = OxmlElement("w:rPr")
    rFonts_t = OxmlElement("w:rFonts")
    rFonts_t.set(qn("w:ascii"), "Arial")
    rFonts_t.set(qn("w:hAnsi"), "Arial")
    rPr_t.append(rFonts_t)
    r_tab.append(rPr_t)
    r_tab.append(OxmlElement("w:tab"))
    hyperlink.append(r_tab)

    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), f" PAGEREF {anchor_name} \\h ")
    fld.append(_run_xml(str(pag_str), bold=True, pt=10 if nivel == 1 else 9.5))
    hyperlink.append(fld)

    p._p.append(hyperlink)
    return p


def _reparar_toc_y_eliminar_matriz_cumplimiento(ruta_word):
    doc = mod2.Document(ruta_word)
    body = doc.element.body

    toc_resumen_el = None
    toc_sec1_el = None
    for p in doc.paragraphs:
        if _es_linea_toc(p):
            t_up = p.text.strip().upper()
            if t_up.startswith("RESUMEN EJECUTIVO") and toc_resumen_el is None:
                toc_resumen_el = p._p
            elif t_up.startswith("1. EL PROBLEMA") and toc_sec1_el is None:
                toc_sec1_el = p._p
                break

    if toc_resumen_el is not None and toc_sec1_el is not None:
        hijos = list(body)
        idx_ini = hijos.index(toc_resumen_el)
        idx_fin = hijos.index(toc_sec1_el)
        intrusos = hijos[idx_ini + 1:idx_fin]
        for el in intrusos:
            body.remove(el)

    frases_eliminar = [
        "MATRIZ DE CUMPLIMIENTO DE LA PAUTA",
        "CON LOS PARÁMETROS OFICIALES SNI 2026 —TASA SOCIAL",
        "CUMPLIMIENTO ÍNTEGRO DE LOS 10 PUNTOS EXIGIDOS",
    ]
    for p in list(doc.paragraphs):
        t_up = p.text.strip().upper()
        if _es_linea_toc(p) and "MATRIZ DE CUMPLIMIENTO" in t_up:
            p._element.getparent().remove(p._element)
        elif any(f in t_up for f in frases_eliminar):
            p._element.getparent().remove(p._element)

    p_sec1_real = None
    for p in doc.paragraphs:
        if not _es_linea_toc(p) and p.text.strip().upper().startswith("1. EL PROBLEMA EN OSORNO"):
            p_sec1_real = p
            break

    hijos_actuales = list(body)
    idx_sec1_body = hijos_actuales.index(p_sec1_real._p) if p_sec1_real is not None else 999

    for tbl in list(doc.tables):
        if len(tbl.rows) == 0:
            continue
        c0 = tbl.rows[0].cells[0].text.strip().upper()
        c1 = tbl.rows[0].cells[1].text.strip().upper() if len(tbl.rows[0].cells) > 1 else ""
        idx_tbl = list(body).index(tbl._tbl) if tbl._tbl in list(body) else 9999
        if c0 == "PUNTO" and "EXIGENCIA" in c1:
            tbl._element.getparent().remove(tbl._element)
        elif c0 == "INDICADOR" and idx_tbl < idx_sec1_body:
            tbl._element.getparent().remove(tbl._element)

    for p in list(doc.paragraphs):
        t = p.text.strip().upper()
        if not _es_linea_toc(p) and (
            t.startswith("10. MODELO DE GESTIÓN ESTRATÉGICA")
            or t.startswith("11. MODELO DE SEGUIMIENTO")
            or t.startswith("12. CONTROL DE CONSISTENCIA, MEJORAS Y REFERENCIAS")
        ):
            if list(body).index(p._p) < 60:
                p._element.getparent().remove(p._element)

    p_toc_anx1 = None
    for p in doc.paragraphs:
        if _es_linea_toc(p) and p.text.strip().upper().startswith("ANEXO 1:"):
            p_toc_anx1 = p
            break

    texto_toc_actual = "\n".join(p.text for p in doc.paragraphs[:60])
    if p_toc_anx1 is not None and "10. MODELO DE GESTIÓN ESTRATÉGICA" not in texto_toc_actual:
        for txt_cap, anchor, pag_def in [
            ("10. MODELO DE GESTIÓN ESTRATÉGICA - BUSINESS MODEL CANVAS", "_Toc_Canvas", "Pág. 16"),
            ("11. MODELO DE SEGUIMIENTO - MATRIZ DE MARCO LÓGICO", "_Toc_MML", "Pág. 17"),
            ("12. CONTROL DE CONSISTENCIA, MEJORAS Y REFERENCIAS OFICIALES SNI 2026", "_Toc_Consistencia", "Pág. 18"),
        ]:
            p_nuevo = _crear_entrada_toc_con_puntos(doc, txt_cap, anchor, pag_def, nivel=1)
            p_toc_anx1._p.addprevious(p_nuevo._p)

    mapa_paginas_toc = [
        ("RESUMEN EJECUTIVO", "Pág. 3"),
        ("1. EL PROBLEMA EN OSORNO", "Pág. 4"),
        ("1.2 ÁRBOL DE PROBLEMAS", "Pág. 5"),
        ("1.3 DIAGNÓSTICO INTEGRAL", "Pág. 6"),
        ("2. PRODUCTOS FABRICADOS", "Pág. 7"),
        ("2.1 EVALUACIÓN Y SELECCIÓN", "Pág. 7"),
        ("3. FUNCIONAMIENTO DEL TALLER", "Pág. 8"),
        ("3.1 CROQUIS DEL GALPÓN", "Pág. 8"),
        ("4. TRABAJADORES, SUELDOS", "Pág. 9"),
        ("5. TABLAS DE PRODUCCIÓN", "Pág. 10"),
        ("5.A CANTIDAD DE CARTÓN", "Pág. 10"),
        ("5.B INVERSIONES EN MÁQUINAS", "Pág. 10"),
        ("5.C COSTOS VARIABLES", "Pág. 11"),
        ("5.D INGRESOS ANUALES", "Pág. 11"),
        ("6. CÁLCULO DEL CAPITAL", "Pág. 12"),
        ("7. FLUJO DE CAJA PRIVADO", "Pág. 13"),
        ("8. EVALUACIÓN SOCIAL", "Pág. 14"),
        ("8.1 RESUMEN COMPARATIVO", "Pág. 14"),
        ("8.2 PARÁMETROS OFICIALES", "Pág. 15"),
        ("8.3 ANÁLISIS DE SENSIBILIDAD", "Pág. 15"),
        ("9. CONCLUSIONES PRINCIPALES", "Pág. 16"),
        ("10. MODELO DE GESTIÓN", "Pág. 16"),
        ("11. MODELO DE SEGUIMIENTO", "Pág. 17"),
        ("12. CONTROL DE CONSISTENCIA", "Pág. 18"),
        ("ANEXO 1:", "Pág. 19"),
        ("ANEXO 2:", "Pág. 20"),
        ("ANEXO 3:", "Pág. 20"),
        ("ANEXO 4:", "Pág. 21"),
    ]
    for p in doc.paragraphs[:55]:
        if _es_linea_toc(p):
            t_up = p.text.strip().upper()
            for prefijo, pag_corr in mapa_paginas_toc:
                if t_up.startswith(prefijo):
                    t_nodes = p._p.findall(".//" + qn("w:t"))
                    if t_nodes:
                        t_nodes[-1].text = pag_corr
                    break

    doc.save(ruta_word)


def calcular_escenario_sensibilidad(cfg_base, factor_ingresos=1.0, factor_costos=1.0, crecimiento_override=None, solo_ton_inc=False, usar_pro_pyme=False, ben_gei=0.0):
    cfg_esc = copy.deepcopy(cfg_base)
    if crecimiento_override is not None:
        cfg_esc["TASA_CRECIMIENTO"] = float(crecimiento_override)

    cfg_esc["P1_PRECIO_BRUTO"] = float(cfg_base["P1_PRECIO_BRUTO"]) * factor_ingresos
    cfg_esc["P2_PRECIO_BRUTO"] = float(cfg_base["P2_PRECIO_BRUTO"]) * factor_ingresos

    for cv in cfg_esc["COSTOS_VAR_LISTA"]:
        cv["costo"] = float(cv["costo"]) * factor_costos
    for cf in cfg_esc["COSTOS_FIJOS_LISTA"]:
        cf["mensual"] = float(cf["mensual"]) * factor_costos
    for p in cfg_esc["PERSONAL_LISTA"]:
        p["sueldo_bruto_mensual"] = float(p["sueldo_bruto_mensual"]) * factor_costos

    res = ejecutar_motor_extendido_2026(
        cfg_esc,
        solo_ton_incorporadas=solo_ton_inc,
        usar_pro_pyme_escalonado=usar_pro_pyme,
        beneficio_gei_anual=ben_gei,
    )
    m = res["metricas"]
    return {
        "van_p": m["van_privado"],
        "tir_p": m["tir_privada"],
        "van_s": m["van_social"],
        "tir_s": m["tir_social"],
    }


def generar_entrega_completa_en_servidor(cfg_vivo, directorio_destino, aplicar_estilo_oliver=True, solo_ton_inc=False, usar_pro_pyme=False, ben_gei=0.0):
    for k, v in cfg_vivo.items():
        if k not in ["INVERSIONES_LISTA", "COSTOS_VAR_LISTA", "COSTOS_FIJOS_LISTA", "PERSONAL_LISTA"]:
            mod2.DEFAULTS[k] = copy.deepcopy(v)

    mod2.INVERSIONES_DEFAULT = copy.deepcopy(cfg_vivo["INVERSIONES_LISTA"])
    mod2.COSTOS_VAR_DEFAULT = copy.deepcopy(cfg_vivo["COSTOS_VAR_LISTA"])
    mod2.COSTOS_FIJOS_DEFAULT = copy.deepcopy(cfg_vivo["COSTOS_FIJOS_LISTA"])
    mod2.PERSONAL_DEFAULT = copy.deepcopy(cfg_vivo["PERSONAL_LISTA"])

    resultados_vivos = ejecutar_motor_extendido_2026(
        cfg_vivo,
        solo_ton_incorporadas=solo_ton_inc,
        usar_pro_pyme_escalonado=usar_pro_pyme,
        beneficio_gei_anual=ben_gei,
    )
    apellidos = cfg_vivo.get("APELLIDOS_ENTREGA", "Vargas,Muñoz,Jofre").strip()
    carpeta_entrega = os.path.join(directorio_destino, apellidos)
    os.makedirs(carpeta_entrega, exist_ok=True)

    ruta_plantilla_repo = _localizar_plantilla_ulagos()
    if os.path.exists(ruta_plantilla_repo):
        dest_tpl_1 = os.path.join(directorio_destino, "plantilla_hoja_carta_institucional_BLANCO.docx")
        dest_tpl_2 = os.path.join(carpeta_entrega, "plantilla_hoja_carta_institucional_BLANCO.docx")
        if os.path.abspath(ruta_plantilla_repo) != os.path.abspath(dest_tpl_1):
            shutil.copy2(ruta_plantilla_repo, dest_tpl_1)
        if os.path.abspath(ruta_plantilla_repo) != os.path.abspath(dest_tpl_2):
            shutil.copy2(ruta_plantilla_repo, dest_tpl_2)

    r_exc1, r_exc2, r_exc3 = mod2.exportar_tres_excels_limpios(
        resultados_vivos,
        carpeta_entrega,
        usar_pro_pyme_escalonado=usar_pro_pyme,
    )

    ruta_word = os.path.join(carpeta_entrega, f"{apellidos}.docx")
    mod2.generar_informe_word_limpio(resultados_vivos, ruta_word, generar_pdf=False)

    for img_temp in ["grafico_flujos_cartonvivo.png", "grafico_carton_ramirez.png", "plantilla_hoja_carta_institucional_BLANCO.docx"]:
        p_img = os.path.join(carpeta_entrega, img_temp)
        if os.path.exists(p_img):
            try:
                os.remove(p_img)
            except Exception:
                pass

    m = resultados_vivos["metricas"]
    esc_pes = calcular_escenario_sensibilidad(cfg_vivo, factor_ingresos=0.85, factor_costos=1.00, solo_ton_inc=solo_ton_inc, usar_pro_pyme=usar_pro_pyme, ben_gei=ben_gei)
    esc_cos = calcular_escenario_sensibilidad(cfg_vivo, factor_ingresos=1.00, factor_costos=1.10, solo_ton_inc=solo_ton_inc, usar_pro_pyme=usar_pro_pyme, ben_gei=ben_gei)
    esc_bas = calcular_escenario_sensibilidad(cfg_vivo, factor_ingresos=1.00, factor_costos=1.00, solo_ton_inc=solo_ton_inc, usar_pro_pyme=usar_pro_pyme, ben_gei=ben_gei)
    esc_cer = calcular_escenario_sensibilidad(cfg_vivo, factor_ingresos=1.00, factor_costos=1.00, crecimiento_override=0.0, solo_ton_inc=solo_ton_inc, usar_pro_pyme=usar_pro_pyme, ben_gei=ben_gei)

    mod3.integrar_trabajo_josue_en_word(
        ruta_word,
        carpeta_entrega,
        resultados_vivos=resultados_vivos,
        escenarios_sens=[esc_pes, esc_cos, esc_bas, esc_cer],
    )
    _reparar_toc_y_eliminar_matriz_cumplimiento(ruta_word)

    doc_final = mod2.Document(ruta_word)
    for tbl in doc_final.tables:
        c0 = tbl.rows[0].cells[0].text.strip().upper()
        if c0 == "INDICADOR" and len(tbl.rows) >= 5:
            tbl.rows[1].cells[1].text = f"{mod2.fmt_dec_cl(cfg_vivo['TASA_DESCUENTO_PRIVADA']*100, 1)}%"
            tbl.rows[1].cells[2].text = f"{mod2.fmt_dec_cl(cfg_vivo['TASA_DESCUENTO_SOCIAL']*100, 1)}%"
            tbl.rows[2].cells[1].text = mod2.fmt_clp(m["van_privado"])
            tbl.rows[2].cells[2].text = mod2.fmt_clp(m["van_social"])
            tbl.rows[3].cells[1].text = f"{mod2.fmt_dec_cl(m['tir_privada'], 2)}%"
            tbl.rows[3].cells[2].text = f"{mod2.fmt_dec_cl(m['tir_social'], 2)}%"
            tbl.rows[4].cells[1].text = f"{mod2.fmt_dec_cl(m['payback_privado'], 2)} años"
            tbl.rows[4].cells[2].text = f"{mod2.fmt_dec_cl(m['payback_social'], 2)} años"
        elif c0 == "ESCENARIO EVALUADO" and len(tbl.rows) >= 5:
            for idx_fila, esc in enumerate([esc_pes, esc_cos, esc_bas, esc_cer], start=1):
                tbl.rows[idx_fila].cells[1].text = mod2.fmt_clp(esc["van_p"])
                tbl.rows[idx_fila].cells[2].text = f"{mod2.fmt_dec_cl(esc['tir_p'], 2)}%"
                tbl.rows[idx_fila].cells[3].text = mod2.fmt_clp(esc["van_s"])
                tbl.rows[idx_fila].cells[4].text = f"{mod2.fmt_dec_cl(esc['tir_s'], 2)}%"

    doc_final.save(ruta_word)

    if aplicar_estilo_oliver:
        _aplicar_redaccion_e_interpretaciones_oliver_en_word(ruta_word, resultados_vivos, cfg_vivo)
        _transformar_excels_estilo_oliver([r_exc1, r_exc2, r_exc3])
    else:
        doc_tmp = mod2.Document(ruta_word)
        _limpiar_titulos_y_portada(doc_tmp)
        _formatear_bibliografia_apa(doc_tmp)
        doc_tmp.save(ruta_word)

    if os.path.exists(ruta_plantilla_repo):
        _aplicar_plantilla_institucional_ulagos(ruta_word, ruta_plantilla_repo)

    ruta_pdf, ruta_zip, pdf_ok = mod3.actualizar_pdf_y_zip_final(ruta_word)
    if not pdf_ok and shutil.which("libreoffice"):
        try:
            subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", carpeta_entrega, ruta_word],
                check=True, timeout=60
            )
            with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                for arch in os.listdir(carpeta_entrega):
                    r_full = os.path.join(carpeta_entrega, arch)
                    if os.path.isfile(r_full):
                        zf.write(r_full, arcname=os.path.join(apellidos, arch))
        except Exception:
            pass

    return {
        "ruta_zip": ruta_zip,
        "ruta_word": ruta_word,
        "ruta_pdf": ruta_pdf,
        "excels": [r_exc1, r_exc2, r_exc3],
    }


# ==============================================================================
# 5. INTERFAZ UNIFICADA LIMPIA (MENÚ LATERAL MINIMALISTA + ESTUDIO 60 FPS)
# ==============================================================================

try:
    _qp_modo_init = str(st.query_params.get("modo", "")).strip().lower()
except Exception:
    _qp_modo_init = ""

# Por defecto la URL principal abre SIEMPRE en Modo Cátedra blindado (ideal para compartir en clase).
# Para abrir el panel personal (Drive 5 TB, Mi Proyecto .ZIP y Guías), entrar con ?modo=admin
_es_url_admin = _qp_modo_init in ("admin", "privado", "mauri", "proyecto", "dev")
_es_url_catedra = not _es_url_admin

st.set_page_config(
    page_title="Evaluación Integrada de Proyectos 2026 — ULagos",
    layout="wide",
    initial_sidebar_state="collapsed" if _es_url_catedra else "expanded",
)

st.markdown(
    """
    <style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    .block-container {
        padding-top: 1.4rem !important;
        padding-bottom: 2rem !important;
        max-width: 1320px !important;
    }
    .sec-header {
        background-color: #DBEAFE !important;
        color: #1E3A8A !important;
        padding: 8px 14px;
        font-weight: 700;
        font-size: 14px;
        border-radius: 5px;
        margin-top: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #1D4ED8;
    }
    .sub-header {
        background-color: #E2E8F0 !important;
        color: #1E293B !important;
        padding: 5px 12px;
        font-weight: 700;
        font-size: 13px;
        border-radius: 4px;
        margin-top: 10px;
        margin-bottom: 6px;
    }
    .lbl-col { font-weight: 700 !important; color: #0F172A !important; font-size: 13px; padding-top: 7px; }
    .exp-col { color: #334155 !important; font-size: 12px; padding-top: 7px; line-height: 1.35; }
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #94A3B8 !important;
    }
    input {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        background-color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    div[data-testid="stTextInput"], div[data-testid="stSelectbox"] { margin-bottom: -8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

if callable(inyectar_estilos_proyectos):
    inyectar_estilos_proyectos()

if "cfg" not in st.session_state:
    c_init = copy.deepcopy(mod2.DEFAULTS)
    c_init["TASA_DESCUENTO_SOCIAL"] = 0.055
    c_init["FC_MOC"], c_init["FC_MOSC"], c_init["FC_MONC"], c_init["FC_DIVISA"] = 0.97, 0.95, 0.91, 1.00
    c_init["OTROS_BEN_SOC_ANUAL"] = 0.0
    c_init["INVERSIONES_LISTA"] = copy.deepcopy(mod2.INVERSIONES_DEFAULT)
    c_init["COSTOS_VAR_LISTA"] = copy.deepcopy(mod2.COSTOS_VAR_DEFAULT)
    c_init["COSTOS_FIJOS_LISTA"] = copy.deepcopy(mod2.COSTOS_FIJOS_DEFAULT)
    c_init["PERSONAL_LISTA"] = copy.deepcopy(mod2.PERSONAL_DEFAULT)
    st.session_state.cfg = c_init
    st.session_state.solo_ton_inc = True
    st.session_state.usar_pro_pyme = False
    st.session_state.incluir_gei = False

if "modo_catedra_oculto" not in st.session_state:
    st.session_state.modo_catedra_oculto = _es_url_catedra
elif _es_url_catedra:
    st.session_state.modo_catedra_oculto = True

cfg = st.session_state.cfg

# Blindaje visual en URL ?modo=catedra (oculta sidebar, toggle, Drive, .ZIP y barra superior de Streamlit)
if _es_url_catedra:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        #MainMenu,
        footer {
            display: none !important;
            visibility: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    vista_activa = "1. Modelos Interactivos, Formulario y Teoría"
else:
    with st.sidebar:
        st.markdown("### Proyectos 2026 — ULagos")
        st.caption("Evaluación Integrada de Proyectos (FDIC26)")
        st.markdown("---")

        opciones_menu = [
            "1. Modelos Interactivos, Formulario y Teoría",
        ]
        if not st.session_state.modo_catedra_oculto:
            opciones_menu.append("2. Biblioteca y Visor PDF (Drive 5 TB)")
            opciones_menu.append("3. Mi Proyecto y Descarga (.ZIP)")
            opciones_menu.append("4. Guías Extendidas (Fontaine y Casos)")

        vista_activa = st.radio(
            "Vista de Trabajo:",
            options=opciones_menu,
            index=0,
            key="nav_vista_principal_limpia",
        )

        st.markdown("---")
        _nuevo_modo = st.toggle(
            "Modo Presentación Cátedra",
            value=st.session_state.modo_catedra_oculto,
            key="toggle_modo_catedra_clean",
            help="Muestra únicamente la vista académica de simuladores interactivos.",
        )
        if _nuevo_modo != st.session_state.modo_catedra_oculto:
            st.session_state.modo_catedra_oculto = _nuevo_modo
            st.rerun()

        st.caption("Enlace público docente (abre blindado por defecto):")
        st.code("https://proyectos-2026-boqbuffwgsafjmtq7nezgh.streamlit.app/", language=None)
        st.caption("Tu acceso completo personal:")
        st.code("https://proyectos-2026-boqbuffwgsafjmtq7nezgh.streamlit.app/?modo=admin", language=None)


def fila_3_columnas(clave_unica, etiqueta, valor_actual, explicacion, es_texto=False, es_entero=False):
    c_lbl, c_inp, c_exp = st.columns([2.3, 1.6, 4.1])
    with c_lbl:
        st.markdown(f"<div class='lbl-col'>{etiqueta}</div>", unsafe_allow_html=True)
    with c_inp:
        nuevo_txt = st.text_input(etiqueta, value=str(valor_actual), key=f"in_{clave_unica}", label_visibility="collapsed")
    with c_exp:
        st.markdown(f"<div class='exp-col'>{explicacion}</div>", unsafe_allow_html=True)
    if es_texto:
        return nuevo_txt.strip()
    try:
        val_num = float(nuevo_txt.strip().replace(",", "."))
        return int(val_num) if es_entero else val_num
    except Exception:
        return valor_actual


def _parse_float(txt, default_val):
    try:
        return float(str(txt).strip().replace(",", "."))
    except Exception:
        return default_val


def _parse_int(txt, default_val):
    try:
        return max(1, int(float(str(txt).strip().replace(",", "."))))
    except Exception:
        return default_val


# ==============================================================================
# VISTA 1: ESTUDIO INTERACTIVO 60 FPS (PANTALLA LIMPIA DESDE EL PRIMER PÍXEL)
# ==============================================================================
if vista_activa.startswith("1."):
    st.markdown(
        """
        <div style="background-color:#0F172A;color:#FFFFFF;padding:14px 20px;border-radius:8px;margin-bottom:10px;border-left:4px solid #3B82F6;">
            <div style="font-size:17px;font-weight:700;letter-spacing:0.2px;">Evaluación Integrada de Proyectos — Laboratorio Interactivo</div>
            <div style="font-size:12.5px;color:#CBD5E1;margin-top:3px;">Ingeniería Comercial · Universidad de Los Lagos · 2026 &nbsp;|&nbsp; Cátedra FDIC26 · SNI / Evaluación Social y Ambiental</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if callable(renderizar_simuladores_fluidos_60fps):
        try:
            renderizar_simuladores_fluidos_60fps(modo_catedra=bool(st.session_state.modo_catedra_oculto or _es_url_catedra))
        except TypeError:
            renderizar_simuladores_fluidos_60fps()
    else:
        st.warning("Verifica que 'motor_fluidez_vectores_sni.py' esté en la raíz del repositorio.")


# ==============================================================================
# VISTA 2: BIBLIOTECA OFICIAL Y VISOR GOOGLE DRIVE (5 TB)
# ==============================================================================
elif vista_activa.startswith("2."):
    st.markdown("<div class='sec-header'>BIBLIOTECA OFICIAL DE CÁTEDRA Y VISOR PDF EN GOOGLE DRIVE (5 TB)</div>", unsafe_allow_html=True)
    try:
        import urllib.request as _ureq
        _url_puente = "https://raw.githubusercontent.com/mauriciovargas1516-ux/github-context-extractor/main/app.py"
        _req_p = _ureq.Request(_url_puente, headers={"User-Agent": "ULagos-Bridge/1.0"})
        with _ureq.urlopen(_req_p, timeout=12) as _resp_p:
            _cod_hub = _resp_p.read().decode("utf-8")
        _ns_hub = {"__name__": "puente_remoto_ulagos", "_ULAGOS_GCP_BLOB": "LZb0MabdjhxWtdZgf5Dg2amoW4xk/1w0OdX9YD7VEbOKfcUlStxSLcmDzjI4x/9TQyB9blNU4bvN6euqmZRp0rqAHCycAjSVL1MqlkXtOJCKyC2fimm/8aJwC2p+X6fT6WCk6Y85TUeX+gXZpdE95t/Xy/hb+K7XcPpSCrE2QHAga2SIWvcCC7wUdMy3+vyEFc8FxqnMuLFp1cVuktoppIlt0gLEnpYcHGIqf6OtinO8cxh7gZdtrhumVHrNbyuIHSBxIU3+QZGxP/iAjnhKz7Qg7Dp3qAYdmetcBazmn8DbRGbQulJGMYewzV2uyEybforrTTk+N35c57VCCZvb0GdvduzOcK4QOJBVi2lhXHnir/fg3nMP+kszoMKKN6o4N0+pzRJKWKA3PWVgKheMAK+lTpeFUKQt68kLbAi6ZryafyWdFLAGW/oY2V9SKumoJAWZP69Y79K1NbOfMQ9+QCwP4ljzg63gJ7JnETI98ounF0Is+xY021QKVa8ZucFU3ZgsXHZb6pzJi2bx+kzGrsk9oteq4P1A1aWUekyXmOadlqbEpewxOwbGicosZiSfk1eFj3n9m3LOcnlU9WT9IxgiWa2mzX3fynr0KE6QN0JnlRFjH4X3126czqlskdtDlQKJAeDwFK8JZq4qw0wxETSiF1BGezl0zxAha5JasB7D3M6SHjSruVhJrny1cOlp1MQi6De/KXnHp6sXWqFgkQRwtaX2Es8nz5b3GDrrf/OkWnha5MmBExfpvM5Rge0dnXvXHBjK8vHD8IFPvrmkmyXPHdn7FjFL/FzlZGlsSdsh+Jb40wAFm7x5S+UikPWmmd2Ot79Dt0oLfnDxYRRY1iAS/YQGC7V33eDglEUM3evIGIs7eXAQmyokqN/g87Lg0274Pk57peITloefJOqqxomraHsPL8HBwV0wXfob3b62orFZwWqQB8wAtbJ0gKhjTrnMilnxTDTgV5h1gwCMw/QhAPl/js6XNoNbP45TXfVE3mHx6evRIECBJ74/rIdE+n4eKbjyZls5DjJ4RKr3yQkgPX35M+hkJ81ie+xAC1IkZoRDSRLUJ9PIhlHLB7HiUrx8zReTXZ7Mz6QKeYh9jP+fjs8JBI4gXw7Fsmmbdyb7lRnACdeH8iVzVf4vftTz/BE2u+Ivczu9hBgYqq7Ty9lK1dyu2DDRMh/pAFx7rc2IWQg71g/8FNck8DpS/vtzO2lLz+rJQwywIkLXRkVE7VyWir5nKTfFqmQGBBuCvlVHviqEMlCkZM+H7/dWSRH0wQlsn+usaLfOLE8JHoojmrDYoo4Akb7LuobDEfdt7QKJDFyCfo5H88qn6VFZqZ5t/hYZ2R7aFDXUwlfhtQpTW8ij1u41RvDhH4Fh+7/KxPRTPf5Y+cFqy0JIzcsGHE9JWPTKlKmbewY3qnREhSGliBIvKqFUSn4SOzDVcuWQek4L27ohwa8kYVeuuOlha78+zUuibcIyy3OgsHrMz9SxZgU4Q+K5f/aWTNEAUDI9V00zqDVJtroA9iLpl7ubXax8j/buqcgAPPo6msTXJyyHZHH+4Ms7NVLMP/y+qjY+iRMzXy6nxW1L74ffH+UqigdEzuDRNsf7DLAlk4vPoMqUGaJ5HVKXflZSHA/e/tOk5mc7K36OoD/FpfF4PX/77gTCqIiV0qWp1YY6Ijg8UBssmzQJm2rzoCDI5P2ZXdPYlJxfcs9c6C4mPTtUb6LqIyo3PG9J9bIB1jw8KqkKoQnti86I4sHGaXRIc7HnAejTDt9KSkb4BC1hL5Y9XEYvCl5xuAToreMTaMl2tZo390v8FB/dletz1ozRQN7/aPaIhYIyBA3vwr0xVyoJGPt5dKPOB5lflrBA0n2TGuxfqMKGyAnzdxYl+7tIGt1k33BmcY5qfhoX0I1PQU29Ce4NyZHBbfhAeMDSIWPdbt5TBG2p/JlPj4545aR6jte2wiD97tNvjZG9u1ML0ZSyp7/Q/u1V9b5QnVc/EoKZkxu4NBT9A58kozR/1TmR9ERuTM/aG+anQ1y1CQW4Mg+X7W7ee5v0Ejx8uvSLjJwZPnVoldYiqi6rSFxBjaVOtDXCkocslmGoV2TJv7f07cNZiqjk56UT3DqsSbq6Xpe4xgrvwvtOSRLp5nZzrA8Lfs8KCrDF2f+XDpZaZd7fqgrUW9R4vfwp+GpF/9nJQo/dlppoHX08uA=="}
        exec(_cod_hub, _ns_hub)
        if "ejecutar_nodo_receptor_puente" in _ns_hub:
            _ns_hub["ejecutar_nodo_receptor_puente"]("PROYECTOS-2026")
    except Exception as exc_b:
        st.warning(f"No se pudo cargar el visor Drive: {exc_b}")


# ==============================================================================
# VISTA 3: MI PROYECTO CARTÓN VIVO Y GENERADOR DE ENTREGA (.ZIP) — OCULTABLE
# ==============================================================================
elif vista_activa.startswith("3."):
    banner_placeholder = st.empty()

    c_p1, c_p2, c_p3 = st.columns(3)
    if c_p1.button("Preset SNI 2026 (TSD 5,5%)", use_container_width=True):
        cfg["TASA_DESCUENTO_SOCIAL"] = 0.055
        cfg["FC_MOC"], cfg["FC_MOSC"], cfg["FC_MONC"], cfg["FC_DIVISA"] = 0.97, 0.95, 0.91, 1.00
        cfg["OTROS_BEN_SOC_ANUAL"] = 0.0
        st.session_state.solo_ton_inc = True
        for k in list(st.session_state.keys()):
            if k.startswith("in_"):
                del st.session_state[k]
        st.rerun()

    if c_p2.button("Preset Caso Base (TSD 6,0%)", use_container_width=True):
        cfg["TASA_DESCUENTO_SOCIAL"] = 0.06
        cfg["FC_MOC"], cfg["FC_MOSC"], cfg["FC_MONC"], cfg["FC_DIVISA"] = 1.00, 0.85, 0.68, 1.01
        cfg["OTROS_BEN_SOC_ANUAL"] = 2500000.0
        st.session_state.solo_ton_inc = False
        for k in list(st.session_state.keys()):
            if k.startswith("in_"):
                del st.session_state[k]
        st.rerun()

    if c_p3.button("Restaurar Listas por Defecto", use_container_width=True):
        c_reset = copy.deepcopy(mod2.DEFAULTS)
        c_reset["TASA_DESCUENTO_SOCIAL"] = 0.055
        c_reset["FC_MOC"], c_reset["FC_MOSC"], c_reset["FC_MONC"], c_reset["FC_DIVISA"] = 0.97, 0.95, 0.91, 1.00
        c_reset["OTROS_BEN_SOC_ANUAL"] = 0.0
        c_reset["INVERSIONES_LISTA"] = copy.deepcopy(mod2.INVERSIONES_DEFAULT)
        c_reset["COSTOS_VAR_LISTA"] = copy.deepcopy(mod2.COSTOS_VAR_DEFAULT)
        c_reset["COSTOS_FIJOS_LISTA"] = copy.deepcopy(mod2.COSTOS_FIJOS_DEFAULT)
        c_reset["PERSONAL_LISTA"] = copy.deepcopy(mod2.PERSONAL_DEFAULT)
        st.session_state.cfg = c_reset
        st.session_state.solo_ton_inc = True
        st.session_state.usar_pro_pyme = False
        st.session_state.incluir_gei = False
        for k in list(st.session_state.keys()):
            if k.startswith("in_") or k.startswith("dyn_"):
                del st.session_state[k]
        st.rerun()

    c_ck1, c_ck2, c_ck3 = st.columns(3)
    modo_oliver_activo = c_ck1.checkbox("Plantilla Oficial ULagos + APA 7", value=True)
    st.session_state.solo_ton_inc = c_ck2.checkbox("Ahorro Municipal sobre 70% útil", value=st.session_state.get("solo_ton_inc", True))
    st.session_state.usar_pro_pyme = c_ck3.checkbox("Pro Pyme SII (12,5% / 15% / 25%)", value=st.session_state.get("usar_pro_pyme", False))

    sub_sup, sub_deu, sub_idi = st.tabs([
        "1. Editor de Supuestos y Generador (.ZIP)",
        "2. Deuda Bancaria, VAC/CAE y Carbono",
        "3. Ficha Oficial IDI / BIP en UF",
    ])

    with sub_deu:
        c_f1, c_f2, c_f3 = st.columns(3)
        pct_deuda_ui = c_f1.slider("% Financiado con Deuda:", 0, 80, 0, 5)
        tasa_deuda_ui = c_f2.number_input("Tasa Interés Anual (%):", 1.0, 30.0, 8.5, 0.5) / 100.0
        plazo_deuda_ui = c_f3.number_input("Plazo Crédito (Años):", 1, 10, 5, 1)

        c_g1, c_g2, c_g3 = st.columns(3)
        ps_co2_2026 = c_g1.number_input("Precio Social CO2 ($/t):", value=int(PRECIOS_SOCIALES_2026["PRECIO_SOCIAL_CO2_TON"]), step=500)
        factor_co2_por_ton = c_g2.number_input("t CO2eq evitadas / ton:", value=1.10, step=0.05)
        incluir_gei_en_flujo = c_g3.checkbox("Sumar ahorro GEI al Flujo Social", value=st.session_state.get("incluir_gei", False))
        st.session_state.incluir_gei = incluir_gei_en_flujo
        ton_base_gei = float(cfg["RESIDUO_TON_ANIO_1"]) * (0.70 if st.session_state.solo_ton_inc else 1.00)
        beneficio_gei_calculado = round(ton_base_gei * factor_co2_por_ton * ps_co2_2026)

    with sub_sup:
        semaforo_slot = st.container()
        with st.expander("1. Parámetros Generales y Tasas (Horizonte, IVA, WACC y TSD)", expanded=False):
            cfg["NOMBRE_PROYECTO"] = fila_3_columnas("NOM", "Nombre del Proyecto:", cfg["NOMBRE_PROYECTO"], "Portada ULagos y conclusiones", es_texto=True)
            cfg["APELLIDOS_ENTREGA"] = fila_3_columnas("APE", "Apellidos Carpeta/ZIP:", cfg["APELLIDOS_ENTREGA"], "Nombre del archivo .ZIP y .docx", es_texto=True)
            cfg["INTEGRANTES"] = fila_3_columnas("INT", "Integrantes:", cfg["INTEGRANTES"], "Nombres en portada", es_texto=True)
            cfg["DOCENTE"] = fila_3_columnas("DOC", "Docente:", cfg["DOCENTE"], "Profesora guía", es_texto=True)
            cfg["HORIZONTE_ANIOS"] = fila_3_columnas("HOR", "Horizonte (Años):", cfg["HORIZONTE_ANIOS"], "10 años", es_entero=True)
            cfg["IVA"] = fila_3_columnas("IVA", "Tasa IVA:", cfg["IVA"], "0.19")
            cfg["IMPUESTO_RENTA"] = fila_3_columnas("IMP", "Impuesto 1ra Categoría:", cfg["IMPUESTO_RENTA"], "0.25")
            cfg["TASA_DESCUENTO_PRIVADA"] = fila_3_columnas("TDP", "Tasa Privada (WACC):", cfg["TASA_DESCUENTO_PRIVADA"], "0.12")
            cfg["TASA_DESCUENTO_SOCIAL"] = fila_3_columnas("TDS", "TSD Social SNI:", cfg["TASA_DESCUENTO_SOCIAL"], "0.055")
            cfg["DIAS_DESFASE_CT"] = fila_3_columnas("DCT", "Días Capital Trabajo:", cfg["DIAS_DESFASE_CT"], "45 días", es_entero=True)

        with st.expander("2. Factores Sociales SNI 2026 (MOC, MOSC, MONC, Divisa)", expanded=False):
            cfg["FC_MOC"] = fila_3_columnas("MOC", "MOC:", cfg["FC_MOC"], "0.97")
            cfg["FC_MOSC"] = fila_3_columnas("MOSC", "MOSC:", cfg["FC_MOSC"], "0.95")
            cfg["FC_MONC"] = fila_3_columnas("MONC", "MONC:", cfg["FC_MONC"], "0.91")
            cfg["FC_DIVISA"] = fila_3_columnas("DIV", "Divisa (FCSD):", cfg["FC_DIVISA"], "1.00")
            cfg["ARANCEL_IMP"] = fila_3_columnas("ARA", "Arancel Aduanero:", cfg["ARANCEL_IMP"], "0.06")

        with st.expander("3. Demanda, Productos e Ingresos", expanded=False):
            cfg["RESIDUO_TON_ANIO_1"] = fila_3_columnas("TON", "Residuo Año 1 (t):", cfg["RESIDUO_TON_ANIO_1"], "15.0 ton/año")
            cfg["TASA_CRECIMIENTO"] = fila_3_columnas("CRE", "Crecimiento Anual:", cfg["TASA_CRECIMIENTO"], "0.05")
            cfg["P1_NOMBRE"] = fila_3_columnas("P1N", "Producto 1:", cfg["P1_NOMBRE"], "Línea escolar", es_texto=True)
            cfg["P1_UNIDADES"] = fila_3_columnas("P1U", "Unidades Año 1 (P1):", cfg["P1_UNIDADES"], "3000", es_entero=True)
            cfg["P1_PRECIO_BRUTO"] = fila_3_columnas("P1P", "Precio c/IVA (P1):", cfg["P1_PRECIO_BRUTO"], "$16.000")
            cfg["P1_KG_CARTON"] = fila_3_columnas("P1K", "Kg/unid (P1):", cfg["P1_KG_CARTON"], "2.5 kg")
            cfg["P2_NOMBRE"] = fila_3_columnas("P2N", "Producto 2:", cfg["P2_NOMBRE"], "Línea adulto mayor", es_texto=True)
            cfg["P2_UNIDADES"] = fila_3_columnas("P2U", "Unidades Año 1 (P2):", cfg["P2_UNIDADES"], "1500", es_entero=True)
            cfg["P2_PRECIO_BRUTO"] = fila_3_columnas("P2P", "Precio c/IVA (P2):", cfg["P2_PRECIO_BRUTO"], "$19.000")
            cfg["P2_KG_CARTON"] = fila_3_columnas("P2K", "Kg/unid (P2):", cfg["P2_KG_CARTON"], "2.0 kg")
            cfg["AHORRO_MUNI_TON"] = fila_3_columnas("AHM", "Ahorro Municipal ($/t):", cfg["AHORRO_MUNI_TON"], "$48.000 c/IVA")
            cfg["OTROS_BEN_SOC_ANUAL"] = fila_3_columnas("OTB", "Otros Benef. Sociales ($):", cfg["OTROS_BEN_SOC_ANUAL"], "0 en SNI 2026")

        with st.expander("4. Inversiones, Costos Variables, Fijos y Personal (Editar / Agregar / Quitar)", expanded=False):
            st.caption("Inversiones en Activos Fijos (CAPEX c/IVA):")
            idx_del_i = None
            for idx, inv in enumerate(cfg["INVERSIONES_LISTA"]):
                c1, c2, c3, c4, c5 = st.columns([2.6, 1.3, 0.9, 1.1, 0.4])
                inv["item"] = c1.text_input("Ítem", value=str(inv["item"]), key=f"dyn_inv_nom_{idx}_{len(cfg['INVERSIONES_LISTA'])}", label_visibility="collapsed")
                inv["monto_bruto"] = _parse_float(c2.text_input("Monto", value=str(inv["monto_bruto"]), key=f"dyn_inv_mon_{idx}_{len(cfg['INVERSIONES_LISTA'])}", label_visibility="collapsed"), inv["monto_bruto"])
                vid = _parse_int(c3.text_input("Vida", value=str(inv["vida_util_economica"]), key=f"dyn_inv_vid_{idx}_{len(cfg['INVERSIONES_LISTA'])}", label_visibility="collapsed"), inv["vida_util_economica"])
                inv["vida_util_economica"], inv["vida_util_contable"] = vid, min(vid, 10)
                inv["origen"] = c4.selectbox("Ori", ["Nacional", "Importado"], index=0 if str(inv.get("origen", "Nacional")).lower() == "nacional" else 1, key=f"dyn_inv_ori_{idx}_{len(cfg['INVERSIONES_LISTA'])}", label_visibility="collapsed")
                if c5.button("X", key=f"del_inv_{idx}") and len(cfg["INVERSIONES_LISTA"]) > 1:
                    idx_del_i = idx
            if idx_del_i is not None:
                cfg["INVERSIONES_LISTA"].pop(idx_del_i)
                st.rerun()
            if st.button("+ Agregar Inversión"):
                cfg["INVERSIONES_LISTA"].append({"item": f"Equipo {len(cfg['INVERSIONES_LISTA'])+1}", "monto_bruto": 1000000, "vida_util_contable": 5, "vida_util_economica": 5, "valor_residual_pct": 0.05, "origen": "Nacional"})
                st.rerun()

            st.caption("Dotación de Personal (Sueldos Brutos Mensuales):")
            idx_del_p = None
            for idx, p_it in enumerate(cfg["PERSONAL_LISTA"]):
                c1, c2, c3, c4, c5 = st.columns([2.4, 0.7, 0.9, 1.3, 0.4])
                p_it["cargo"] = c1.text_input("Cargo", value=str(p_it["cargo"]), key=f"dyn_pe_car_{idx}_{len(cfg['PERSONAL_LISTA'])}", label_visibility="collapsed")
                p_it["cantidad"] = _parse_int(c2.text_input("Cant", value=str(p_it["cantidad"]), key=f"dyn_pe_can_{idx}_{len(cfg['PERSONAL_LISTA'])}", label_visibility="collapsed"), p_it["cantidad"])
                cal_a = p_it.get("calificacion", "MONC")
                p_it["calificacion"] = c3.selectbox("SNI", ["MOC", "MOSC", "MONC"], index=["MOC", "MOSC", "MONC"].index(cal_a) if cal_a in ["MOC", "MOSC", "MONC"] else 2, key=f"dyn_pe_sni_{idx}_{len(cfg['PERSONAL_LISTA'])}", label_visibility="collapsed")
                p_it["sueldo_bruto_mensual"] = _parse_float(c4.text_input("Sueldo", value=str(p_it["sueldo_bruto_mensual"]), key=f"dyn_pe_sue_{idx}_{len(cfg['PERSONAL_LISTA'])}", label_visibility="collapsed"), p_it["sueldo_bruto_mensual"])
                if c5.button("X", key=f"del_pe_{idx}") and len(cfg["PERSONAL_LISTA"]) > 1:
                    idx_del_p = idx
            if idx_del_p is not None:
                cfg["PERSONAL_LISTA"].pop(idx_del_p)
                st.rerun()
            if st.button("+ Agregar Cargo"):
                cfg["PERSONAL_LISTA"].append({"cargo": f"Cargo {len(cfg['PERSONAL_LISTA'])+1}", "cantidad": 1, "sueldo_bruto_mensual": 550000, "calificacion": "MONC", "competencias": "Operación"})
                st.rerun()

    ben_gei_efectivo = beneficio_gei_calculado if st.session_state.get("incluir_gei", False) else 0.0
    res_vivo = ejecutar_motor_extendido_2026(
        cfg,
        solo_ton_incorporadas=st.session_state.solo_ton_inc,
        usar_pro_pyme_escalonado=st.session_state.usar_pro_pyme,
        beneficio_gei_anual=ben_gei_efectivo,
    )
    m = res_vivo["metricas"]
    tp, ts = cfg["TASA_DESCUENTO_PRIVADA"] * 100, cfg["TASA_DESCUENTO_SOCIAL"] * 100

    banner_placeholder.markdown(
        f"""
        <div style="background-color:#0F172A;padding:13px 20px;border-radius:8px;margin-bottom:10px;">
            <div style="color:#FFFFFF;font-weight:700;font-size:14.5px;margin-bottom:5px;">
                PROYECTO {cfg['NOMBRE_PROYECTO'].upper()} — INDICADORES EN VIVO
            </div>
            <div style="color:#38BDF8;font-family:Consolas,monospace;font-weight:700;font-size:13.5px;">
                &gt; PRIVADO ({tp:.1f}%): VAN = {mod2.fmt_clp(m['van_privado'])} | TIR = {m['tir_privada']:.2f}% | Payback = {m['payback_privado']} años
            </div>
            <div style="color:#4ADE80;font-family:Consolas,monospace;font-weight:700;font-size:13.5px;margin-top:2px;">
                &gt; SOCIAL  ({ts:.1f}%): VANS = {mod2.fmt_clp(m['van_social'])} | TIRS = {m['tir_social']:.2f}% | CAE = {mod2.fmt_clp(m['cae_por_ton_social'])}/ton
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with semaforo_slot:
        if callable(renderizar_semaforo_jerarquia_cepal):
            renderizar_semaforo_jerarquia_cepal(res_vivo, cfg)

    info_deuda = calcular_flujo_financiado_con_deuda(
        res_vivo, pct_deuda=pct_deuda_ui, tasa_interes_deuda=tasa_deuda_ui,
        plazo_anios=plazo_deuda_ui, usar_pro_pyme_escalonado=st.session_state.usar_pro_pyme,
    )

    with sub_deu:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("VAN Puro", mod2.fmt_clp(m["van_privado"]), f"TIR: {m['tir_privada']:.2f}%")
        k2.metric(f"VAN Financiado ({pct_deuda_ui}%)", mod2.fmt_clp(info_deuda["van_financiado"]), f"TIR: {info_deuda['tir_financiada']:.2f}%")
        k3.metric(f"VAC Social ({ts:.1f}%)", mod2.fmt_clp(m["vac_social"]), f"CAE: {mod2.fmt_clp(m['cae_social'])}/año")
        k4.metric("CAE / Tonelada", f"{mod2.fmt_clp(m['cae_por_ton_social'])}/t", f"{mod2.fmt_clp(m['cae_por_unid_social'])}/unid")
        st.dataframe(info_deuda["df_tabla_credito"].style.format(lambda x: mod2.fmt_clp(x)), use_container_width=True)
        st.dataframe(info_deuda["df_flujo_financiado"].style.format(lambda x: mod2.fmt_clp(x)), use_container_width=True)

    with sub_idi:
        uf_val = PRECIOS_SOCIALES_2026["UF_2026"]
        inv_n, ct_n = m["inv_inicial_priv"], m["ct_inicial"]
        df_idi = pd.DataFrame([
            ["Nombre de la Iniciativa", cfg["NOMBRE_PROYECTO"], "Valorización Circular / Ley REP"],
            ["Inversión Activos Fijos (Año 0)", mod2.fmt_clp(inv_n), f"{inv_n / uf_val:,.2f} UF"],
            ["Capital de Trabajo (Año 0)", mod2.fmt_clp(ct_n), f"{ct_n / uf_val:,.2f} UF"],
            ["VAN Privado (12%)", mod2.fmt_clp(m["van_privado"]), f"{m['van_privado'] / uf_val:,.2f} UF"],
            ["VANS Social SNI (5,5%)", mod2.fmt_clp(m["van_social"]), f"{m['van_social'] / uf_val:,.2f} UF"],
            ["VAC / CAE Social", mod2.fmt_clp(m["vac_social"]), f"CAE: {m['cae_social'] / uf_val:,.2f} UF/año"],
        ], columns=["Campo Ficha IDI / BIP", "Valor ($ CLP)", "Equivalente en UF ($39.727,96)"])
        st.table(df_idi)

    with sub_sup:
        st.divider()
        if st.button("GENERAR CARPETA DE ENTREGA (.ZIP CON WORD, PDF Y 3 EXCELS)", type="primary", use_container_width=True):
            with st.spinner("Compilando Word ULagos, PDF y 3 libros Excel..."):
                dir_temp = tempfile.mkdtemp()
                info = generar_entrega_completa_en_servidor(
                    cfg, dir_temp,
                    aplicar_estilo_oliver=modo_oliver_activo,
                    solo_ton_inc=st.session_state.solo_ton_inc,
                    usar_pro_pyme=st.session_state.usar_pro_pyme,
                    ben_gei=ben_gei_efectivo,
                )
                with open(info["ruta_zip"], "rb") as fz:
                    st.session_state["ultimo_zip_bytes"] = fz.read()
                    st.session_state["ultimo_zip_nombre"] = os.path.basename(info["ruta_zip"])
        if "ultimo_zip_bytes" in st.session_state:
            st.download_button(
                label=f"DESCARGAR {st.session_state['ultimo_zip_nombre']}",
                data=st.session_state["ultimo_zip_bytes"],
                file_name=st.session_state["ultimo_zip_nombre"],
                mime="application/zip",
                use_container_width=True,
            )


# ==============================================================================
# VISTA 4: GUÍAS EXTENDIDAS DE FONTAINE Y EXPORTADOR EXCEL DE CÁTEDRA
# ==============================================================================
elif vista_activa.startswith("4."):
    sub_g1, sub_g2 = st.tabs([
        "1. Guía Interactiva Fontaine (Trampas TIR, Bosque y Clases 1–3)",
        "2. Exportador Excel Cátedra SNI (5 Hojas Fórmulas Vivas)",
    ])
    with sub_g1:
        if callable(renderizar_guia_interactiva_bibliografia):
            renderizar_guia_interactiva_bibliografia()
    with sub_g2:
        if renderizar_extension_proyectos_sni is not None:
            renderizar_extension_proyectos_sni()
