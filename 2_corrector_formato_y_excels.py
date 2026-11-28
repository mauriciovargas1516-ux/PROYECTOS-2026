# -*- coding: utf-8 -*-
"""
2_corrector_formato_y_excels.py — MOTOR FINANCIERO SNI 2026, 3 EXCELS Y WORD ULAGOS (VERSIÓN CORREGIDA)
Incorpora íntegramente las 17 observaciones de retroalimentación docente (24 nov 2026):
  - Sueldo mínimo legal actualizado ($553.553) + Leyes Sociales del Empleador (6,5%: cesantía, SIS, mutualidad y aporte previsional).
  - Costo mensual de Diseño Gráfico/Pedagógico, Renovación de Matrices y Control de Calidad.
  - Unificación total a Precios Sociales SNI 2026 (TSD 5,5%, MOC 0,97, MOSC 0,95, MONC 0,91, Divisa 1,00, ahorro conservador 70% útil).
  - Estudio de Mercado, especificación concreta de productos, canales diversificados (licitaciones públicas + privados + retail)
    y plantillas transparentes [POR COMPLETAR EN TERRENO] para encuesta a demandantes y registro de entrevistas.
"""

import os
import sys
import re
import copy
import zipfile
import subprocess
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np
import numpy_financial as npf

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


# ==============================================================================
# 1. LIMPIADOR DE FORMATO NUMÉRICO Y TEXTO CHILENO
# ==============================================================================

def limpiar_texto_chileno(texto):
    if texto is None:
        return ""
    s = str(texto)
    reemplazos = {
        "«": '"', "»": '"', "“": '"', "”": '"', "‘": "'", "’": "'",
        "—": " - ", "–": "-", "−": "-", "×": "x", "•": "-", "~": "aprox. ",
        "→": "hacia", "->": "hacia", "\u00a0": " ", "\u200b": "",
    }
    for viejo, nuevo in reemplazos.items():
        s = s.replace(viejo, nuevo)
    s = re.sub(r"\b(\d{1,2}),(\d{3})\b", r"\1.\2", s)
    s = re.sub(r"\b(\d+)\.(\d{2})%", r"\1,\2%", s)
    s = re.sub(r"\b(\d+)\.(\d{2})\s+(toneladas|ton|años|kilos|kg)", r"\1,\2 \3", s)
    s = re.sub(r" {2,}", " ", s).strip()
    return s


def fmt_clp(valor):
    if isinstance(valor, (int, float, np.integer, np.floating)):
        if valor < 0:
            return f"-${abs(int(round(valor))):,}".replace(",", ".")
        return f"${int(round(valor)):,}".replace(",", ".")
    return limpiar_texto_chileno(valor)


def fmt_dec_cl(valor, decimales=2):
    if isinstance(valor, (int, float, np.integer, np.floating)):
        fmt = f"{valor:,.{decimales}f}"
        return fmt.replace(",", "X").replace(".", ",").replace("X", ".")
    return limpiar_texto_chileno(valor)


def fmt_int_cl(valor):
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return f"{int(round(valor)):,}".replace(",", ".")
    return limpiar_texto_chileno(valor)


# ==============================================================================
# 2. PARÁMETROS OFICIALES UNIFICADOS SNI 2026 + SUELDO MÍNIMO + DISEÑO
# ==============================================================================

DEFAULTS = {
    "NOMBRE_PROYECTO": "Cartón Vivo Osorno",
    "INTEGRANTES": "MAURICIO ALEJANDRO VARGAS ORTEGA, OLIVER MUÑOZ, JOSUE JOFRE",
    "APELLIDOS_ENTREGA": "Vargas,Muñoz,Jofre",
    "DOCENTE": "Dra. Luz María Ferrada B.",
    "HORIZONTE_ANIOS": 10,
    "IVA": 0.19,
    "IMPUESTO_RENTA": 0.25,
    "TASA_DESCUENTO_PRIVADA": 0.12,
    "TASA_DESCUENTO_SOCIAL": 0.055,  # Oficial SNI 2026 (MDSF)
    "DIAS_DESFASE_CT": 50,           # Ajustado por ciclo de licitaciones públicas (45-60d) + privados (30d) + retail
    "CARGA_PATRONAL_PCT": 0.065,     # 2,40% Cesantía + 1,54% SIS + 0,93% Mutualidad + 1,63% Aporte Previsional Empleador
    "FC_MOC": 0.97,                  # Oficial SNI 2026
    "FC_MOSC": 0.95,                 # Oficial SNI 2026
    "FC_MONC": 0.91,                 # Oficial SNI 2026
    "FC_DIVISA": 1.00,               # Oficial SNI 2026
    "ARANCEL_IMP": 0.06,
    "RESIDUO_TON_ANIO_1": 15.00,
    "TASA_CRECIMIENTO": 0.03,        # Conservador (3% anual: acorde PIB regional Los Lagos + 1 nuevo local/año)
    "P1_NOMBRE": 'Set Didáctico Escolar "Armando Osorno"',
    "P1_UNIDADES": 3000,
    "P1_PRECIO_BRUTO": 17500,        # Competitivo frente a madera ($22.000-$28.000) cubriendo diseño y leyes sociales
    "P1_KG_CARTON": 2.50,
    "P2_NOMBRE": 'Kit Cognitivo Adulto Mayor "Memoria Activa"',
    "P2_UNIDADES": 1500,
    "P2_PRECIO_BRUTO": 20500,
    "P2_KG_CARTON": 2.00,
    "AHORRO_MUNI_TON": 48000,
    "OTROS_BEN_SOC_ANUAL": 0.0,      # Criterio conservador SNI 2026 (sin inflar beneficios no cuantificados)
}

INVERSIONES_DEFAULT = [
    {
        "item": "Máquina Troqueladora Industrial de Rodillos (1200 mm)",
        "monto_bruto": 8500000, "vida_util_contable": 10, "vida_util_economica": 10,
        "valor_residual_pct": 0.10, "origen": "Importado"
    },
    {
        "item": "Guillotina Cortadora, Mesones y Juego Inicial de Matrices/Troqueles",
        "monto_bruto": 3800000, "vida_util_contable": 5, "vida_util_economica": 5,
        "valor_residual_pct": 0.05, "origen": "Nacional"
    },
    {
        "item": "Equipo de Impresión/Serigrafía al Agua y Estantes de Secado",
        "monto_bruto": 2200000, "vida_util_contable": 5, "vida_util_economica": 5,
        "valor_residual_pct": 0.05, "origen": "Importado"
    },
    {
        "item": "Acondicionamiento Galpón Ovejería (Electricidad SEC y Permiso SEREMI)",
        "monto_bruto": 2000000, "vida_util_contable": 10, "vida_util_economica": 10,
        "valor_residual_pct": 0.00, "origen": "Nacional"
    },
]

COSTOS_VAR_DEFAULT = [
    {
        "item": "Tintas ecológicas al agua (EN-71), barniz protector humedad y pegamento",
        "costo": 2000, "base": "Por Unidad", "origen": "Nacional"
    },
    {
        "item": "Caja de presentación microcorrugada, instructivo pedagógico y etiqueta",
        "costo": 650, "base": "Por Unidad", "origen": "Nacional"
    },
    {
        "item": "Servicio de flete furgón contratado retiro eje Eleuterio Ramírez",
        "costo": 30000, "base": "Por Tonelada", "origen": "Nacional"
    },
]

COSTOS_FIJOS_DEFAULT = [
    {"item": "Arriendo de galpón industrial 140 m2 (Sector Ovejería, Osorno)", "mensual": 450000, "afecto_iva": "Exento"},
    {"item": "Energía trifásica (Saesa), agua potable (Suralis) e internet", "mensual": 180000, "afecto_iva": "Con IVA"},
    {"item": "Contabilidad Pro Pyme, patente municipal, seguros y marketing digital", "mensual": 150000, "afecto_iva": "Con IVA"},
    {"item": "Diseño gráfico/pedagógico externo, renovación de matrices y control de calidad", "mensual": 250000, "afecto_iva": "Con IVA"},
]

PERSONAL_DEFAULT = [
    {
        "cargo": "Jefe de Planta, Control de Calidad y Gestión Comercial",
        "cantidad": 1, "sueldo_bruto_mensual": 980000, "calificacion": "MOC",
        "competencias": "Gestión operativa, control de calidad visual/funcional, licitaciones Mercado Público y ventas"
    },
    {
        "cargo": "Operador Técnico de Corte, Troquelado y Terminación",
        "cantidad": 2, "sueldo_bruto_mensual": 650000, "calificacion": "MOSC",
        "competencias": "Operación de troqueladora industrial, guillotina, impresión al agua y sellado protector"
    },
    {
        "cargo": "Operario de Recolección, Selección y Armado (Sueldo Mínimo Legal)",
        "cantidad": 2, "sueldo_bruto_mensual": 553553, "calificacion": "MONC",
        "competencias": "Recepción y clasificación de cartón, limpieza, armado de kits, empaque y despacho"
    },
]

ENTREVISTAS_DEFAULT = [
    {
        "perfil": "1. Generadores comerciales (Eje Eleuterio Ramírez)",
        "actor": "[POR COMPLETAR: Nombre local y encargado entrevistado]",
        "fecha": "[POR COMPLETAR: Fecha y medio]",
        "respuestas": "[POR COMPLETAR: Volumen semanal real de cajas, horario de entrega y disposición a convenio de retiro]"
    },
    {
        "perfil": "2. Demandante educacional privado (Jardín / Colegio Osorno)",
        "actor": "[POR COMPLETAR: Nombre establecimiento y directora/educadora]",
        "fecha": "[POR COMPLETAR: Fecha y medio]",
        "respuestas": "[POR COMPLETAR: Tipos de juegos más útiles, precio máximo aceptable, exigencias de durabilidad y frecuencia de compra]"
    },
    {
        "perfil": "3. Demandante adulto mayor (ELEAM / Club / Terapeuta)",
        "actor": "[POR COMPLETAR: Nombre institución y terapeuta/encargado]",
        "fecha": "[POR COMPLETAR: Fecha y medio]",
        "respuestas": "[POR COMPLETAR: Preferencia por dominó táctil/tangram/memoria, tamaño de piezas, presupuesto y canal de compra]"
    },
    {
        "perfil": "4. Comprador público / Gestor de reciclaje (DAEM / Reciclador)",
        "actor": "[POR COMPLETAR: Unidad de compras públicas o gestor autorizado]",
        "fecha": "[POR COMPLETAR: Fecha y medio]",
        "respuestas": "[POR COMPLETAR: Requisitos de Compra Ágil/licitación, plazos reales de pago y condiciones de retiro del 30% de recortes]"
    },
]

ENCUESTA_DEFAULT = [
    {"pregunta": "1. Interés de compra en material didáctico/cognitivo de cartón reciclado de alta resistencia", "muestra": "Meta: n >= 45 (30 educ./apoderados + 15 adulto mayor)", "resultado": "[POR COMPLETAR CON % REAL DE ENCUESTA]"},
    {"pregunta": "2. Disposición a pagar por Set Didáctico Escolar ($17.500 c/IVA) y Kit Adulto Mayor ($20.500 c/IVA)", "muestra": "Rango evaluado: $14.000 a $24.000", "resultado": "[POR COMPLETAR CON DAP MEDIA Y % ACEPTACIÓN]"},
    {"pregunta": "3. Productos específicos más valorados (tablero silábico, figuras táctiles, puzle local, dominó gigante, tangram)", "muestra": "Selección múltiple", "resultado": "[POR COMPLETAR CON RANKING DE PREFERENCIAS]"},
    {"pregunta": "4. Atributos decisivos de compra (durabilidad/lavable, diseño visual atractivo, seguridad EN-71, precio, sustentabilidad)", "muestra": "Escala Likert 1 a 5", "resultado": "[POR COMPLETAR CON PROMEDIO POR ATRIBUTO]"},
    {"pregunta": "5. Frecuencia de renovación anual y canal preferido (compra directa, librería/retail local, licitación/Compra Ágil)", "muestra": "Opciones cerradas", "resultado": "[POR COMPLETAR CON % POR CANAL Y FRECUENCIA]"},
]


def calcular_payback(flujos):
    acumulado = np.cumsum(flujos)
    anios_positivos = np.where(acumulado >= 0)[0]
    if len(anios_positivos) == 0:
        return None
    idx = anios_positivos[0]
    if idx == 0:
        return 0.0
    faltante = abs(acumulado[idx - 1])
    flujo_anio = flujos[idx]
    if flujo_anio == 0:
        return None
    return round((idx - 1) + (faltante / flujo_anio), 2)


def calcular_payback_descontado(flujos, tasa):
    acum = float(flujos[0])
    if acum >= 0:
        return 0.0
    for t in range(1, len(flujos)):
        vp = float(flujos[t]) / ((1.0 + float(tasa)) ** t)
        prev = acum
        acum += vp
        if acum >= 0 and vp > 0:
            return round((t - 1) + abs(prev) / vp, 2)
    return None


def armar_tablas_modelo(cfg):
    horizonte = int(cfg["HORIZONTE_ANIOS"])
    iva = float(cfg["IVA"])
    imp_renta = float(cfg["IMPUESTO_RENTA"])
    tasa_priv = float(cfg["TASA_DESCUENTO_PRIVADA"])
    tasa_soc = float(cfg["TASA_DESCUENTO_SOCIAL"])
    dias_ct = int(cfg["DIAS_DESFASE_CT"])
    crec = float(cfg["TASA_CRECIMIENTO"])
    ton_a1 = float(cfg["RESIDUO_TON_ANIO_1"])
    carga_pat = float(cfg.get("CARGA_PATRONAL_PCT", 0.065))
    escala_ton = ton_a1 / 15.0 if ton_a1 > 0 else 1.0

    locales_base = [
        ("LOC-01", "Hojalatería Lynch", "Eleuterio Ramírez 446", "Ferretería y hojalatería", "Cajas gruesas de herramientas y tubos; retiro selectivo 05:35 AM antes del camión municipal", 4.0),
        ("LOC-02", "Autoplanet Osorno", "Eleuterio Ramírez 582", "Repuestos automotrices", "Cajas corrugadas dobles de repuestos limpias y secas; retiro selectivo 05:40 AM", 8.0),
        ("LOC-03", "Zapatería La Malagueña", "Eleuterio Ramírez 625", "Calzado", "Cajas maestras secas de lotes de calzado; retiro selectivo 05:45 AM", 4.0),
        ("LOC-04", "Minimarket El Sabrosón", "Eleuterio Ramírez 647", "Abarrotes", "Cajas de embalaje seco separadas en bodega; retiro selectivo 05:50 AM", 6.0),
        ("LOC-05", "Galería Centrosorno", "Eleuterio Ramírez 977", "Galería comercial", "Acopio conjunto de locales interiores de vestuario y óptica; retiro 05:55 AM", 14.0),
        ("LOC-06", "Liquimax Osorno", "Eleuterio Ramírez 1024 L.3", "Mayorista hogar/aseo", "Mayor generador diario de cajas de gran formato en el tramo; retiro 06:00 AM", 14.0),
    ]
    df_catastro_6 = pd.DataFrame([
        [cod, nom, dir_, rub, desc, round(kg * escala_ton, 2), round(kg * escala_ton * 25.0), round((kg * escala_ton * 25.0 * 12.0) / 1000.0, 2)]
        for cod, nom, dir_, rub, desc, kg in locales_base
    ], columns=[
        "Código", "Comercio Generador (Osorno)", "Dirección", "Rubro",
        "Caracterización del Cartón y Horario de Retiro", "Kg/Día", "Kg/Mes", "Ton/Año"
    ])

    u1_tot = int(cfg["P1_UNIDADES"])
    u2_tot = int(cfg["P2_UNIDADES"])
    u1_pub = int(round(u1_tot * 0.30))   # 30% Licitaciones / Compra Ágil (acotado por riesgo licitación)
    u1_priv = int(round(u1_tot * 0.45))  # 45% Jardines y colegios particulares / subvencionados
    u1_ret = u1_tot - u1_pub - u1_priv   # 25% Retail local, librerías educativas y familias
    u2_inst = int(round(u2_tot * 0.55))  # 55% ELEAM privados, cajas compensación, fundaciones y licitación municipal
    u2_fam = u2_tot - u2_inst            # 45% Venta directa familias y centros terapéuticos

    df_demanda_canales = pd.DataFrame([
        [
            "CAN-01", "Establecimientos Privados y Subvencionados (Jardines / 1er Ciclo)",
            cfg["P1_NOMBRE"], u1_priv, "45% P1", int(cfg["P1_PRECIO_BRUTO"]),
            "Venta B2B directa a sostenedores y jardines particulares de Osorno (pago a 30 días). No depende de licitación estatal."
        ],
        [
            "CAN-02", "Establecimientos Públicos vía Mercado Público (DAEM / SLEP / SEP)",
            cfg["P1_NOMBRE"], u1_pub, "30% P1", int(cfg["P1_PRECIO_BRUTO"]),
            "Participación competitiva en Compra Ágil y licitaciones públicas (pago 45-60 días). Meta acotada para mitigar riesgo de adjudicación."
        ],
        [
            "CAN-03", "Retail Local, Librerías Educativas, Ferias y Familias (E-commerce)",
            cfg["P1_NOMBRE"], u1_ret, "25% P1", int(cfg["P1_PRECIO_BRUTO"]),
            "Venta contado / 15 días en librerías locales, ferias educativas y venta directa digital; mejora liquidez y posicionamiento de marca."
        ],
        [
            "CAN-04", "ELEAM Privados, Fundaciones, Cajas de Compensación y Clubes (Licit./Conv.)",
            cfg["P2_NOMBRE"], u2_inst, "55% P2", int(cfg["P2_PRECIO_BRUTO"]),
            "Convenios directos con hogares privados/fundaciones y participación en licitaciones comunales de programas de adulto mayor (30-60 días)."
        ],
        [
            "CAN-05", "Familias y Terapeutas Ocupacionales (Venta Directa y Retail)",
            cfg["P2_NOMBRE"], u2_fam, "45% P2", int(cfg["P2_PRECIO_BRUTO"]),
            "Venta directa a cuidadores y profesionales de terapia ocupacional en Osorno y provincia (pago contado/15 días)."
        ],
    ], columns=[
        "Canal", "Segmento de Mercado Diversificado", "Producto", "Meta Año 1 (u)",
        "% Línea", "Precio c/IVA ($)", "Mecanismo Comercial y Condición de Cobro"
    ])

    df_productos_ficha = pd.DataFrame([
        [
            cfg["P1_NOMBRE"],
            "1) Tablero alfabético/silábico encajable (27 piezas); 2) Set de 12 números y figuras geométricas táctiles; 3) Rompecabezas 24 piezas de flora/fauna de Los Lagos.",
            f"{fmt_dec_cl(cfg['P1_KG_CARTON'], 2)} kg (cartón multicapa prensado 4 mm)",
            f"{fmt_clp(cfg['P1_PRECIO_BRUTO'])} c/IVA ({fmt_clp(cfg['P1_PRECIO_BRUTO']/(1+iva))} neto)",
            "Madera importada ($22.000-$28.000) y plástico ($14.000-$20.000). Ventaja: liviano, seguro (D.S. 114 / EN-71), personalizable y sustentable."
        ],
        [
            cfg["P2_NOMBRE"],
            "1) Dominó táctil gigante (28 fichas 8x4 cm alto contraste); 2) Tangram ergonómico de 14 piezas gruesas para motricidad fina; 3) Juego de pares de memoria con tipografía grande.",
            f"{fmt_dec_cl(cfg['P2_KG_CARTON'], 2)} kg (cartón doble onda laminado)",
            f"{fmt_clp(cfg['P2_PRECIO_BRUTO'])} c/IVA ({fmt_clp(cfg['P2_PRECIO_BRUTO']/(1+iva))} neto)",
            "Kits terapéuticos de madera/acrílico ($26.000-$38.000). Ventaja: menor peso para adultos mayores, alto contraste visual y reposición económica."
        ],
    ], columns=[
        "Línea de Producto", "Ejemplos Concretos de Juegos Incluidos", "Cartón y Materialidad",
        "Precio Objetivo", "Competencia y Propuesta de Valor"
    ])

    ton_inc_a1 = (u1_tot * float(cfg["P1_KG_CARTON"]) + u2_tot * float(cfg["P2_KG_CARTON"])) / 1000.0
    merma_ton_a1 = max(0.0, ton_a1 - ton_inc_a1)
    pct_util = (ton_inc_a1 / ton_a1 * 100.0) if ton_a1 > 0 else 70.0

    df_balance_masa = pd.DataFrame([
        ["1. Cartón corrugado recolectado en 6 locales (Año 1)", "100,0%", f"{fmt_dec_cl(ton_a1, 2)} t", "50 kg/día hábil x 25 días/mes x 12 meses = 15.000 kg/año (catastro eje E. Ramírez)."],
        ["2. (-) Descarte en recepción y limpieza (humedad, cintas, corchetes)", "-12,0%", f"-{fmt_dec_cl(ton_a1*0.12, 2)} t", "Fracción no apta para troquelado estético por humedad matutina o grapas metálicas."],
        ["3. (-) Retazo geométrico de troquelado (aprovechamiento plancha ~80%)", "-18,0%", f"-{fmt_dec_cl(ton_a1*0.18, 2)} t", "Bordes sobrantes al cortar piezas encajables; se compacta y entrega a gestor autorizado (Ley REP)."],
        ["4. (=) Fibra neta incorporada a productos terminados", f"{fmt_dec_cl(pct_util, 1)}%", f"{fmt_dec_cl(ton_inc_a1, 2)} t", f"{fmt_int_cl(u1_tot)} sets x {fmt_dec_cl(cfg['P1_KG_CARTON'],2)} kg ({fmt_dec_cl(u1_tot*cfg['P1_KG_CARTON']/1000,2)} t) + {fmt_int_cl(u2_tot)} kits x {fmt_dec_cl(cfg['P2_KG_CARTON'],2)} kg ({fmt_dec_cl(u2_tot*cfg['P2_KG_CARTON']/1000,2)} t)."],
    ], columns=["Etapa del Balance de Masa", "% Masa", "Toneladas Año 1", "Memoria de Cálculo Técnico"])

    entrevistas_src = cfg.get("ENTREVISTAS_LISTA", ENTREVISTAS_DEFAULT)
    df_entrevistas = pd.DataFrame([
        [e["perfil"], e["actor"], e["fecha"], e["respuestas"]] for e in entrevistas_src
    ], columns=["Perfil / Actor Clave", "Entrevistado (Nombre y Cargo)", "Fecha y Medio", "Síntesis de Respuestas Obtenidas"])

    encuesta_src = cfg.get("ENCUESTA_RESUMEN", ENCUESTA_DEFAULT)
    df_encuesta = pd.DataFrame([
        [e["pregunta"], e["muestra"], e["resultado"]] for e in encuesta_src
    ], columns=["Variable / Pregunta de la Encuesta a Demandantes", "Diseño Muestral / Escala", "Resultado Levantamiento en Terreno"])

    df_supuestos = pd.DataFrame([
        [
            "Balance de masa (70% útil / 30% retazo)",
            f"{fmt_dec_cl(ton_a1,2)} t -> {fmt_dec_cl(ton_inc_a1,2)} t útiles",
            "12% descarte en recepción + 18% retazo geométrico de troquelado = 30% fracción residual segregada y entregada a reciclador autorizado (trazabilidad Ley 20.920).",
            "Cálculo de rendimiento de plancha en troquelado plano."
        ],
        [
            "Crecimiento anual proyectado",
            f"{fmt_dec_cl(crec*100,1)}% anual (Horizonte {horizonte} años)",
            "Crecimiento conservador respaldado por dinamismo del PIB/comercio regional de Los Lagos (Banco Central) y suma gradual de 1 a 2 locales proveedores/año; contrastado con escenario 0% en sensibilidad.",
            "Banco Central de Chile / Supuesto conservador de expansión."
        ],
        [
            "Remuneraciones y Leyes Sociales",
            f"Sueldo mín. $553.553 + {fmt_dec_cl(carga_pat*100,1)}% empleador",
            "Los operarios parten en el sueldo mínimo legal ($553.553 bruto) y a toda la planilla se suma el aporte patronal: Seguro Cesantía (2,40%), SIS (1,54%), Mutualidad Ley 16.744 (0,93%) y aporte previsional empleador (1,63%).",
            "Código del Trabajo, Ley 16.744 y normativa previsional vigente."
        ],
        [
            "Diseño continuo y aseguramiento de calidad",
            "$250.000/mes c/IVA + matrices",
            "Incorpora asesoría externa de diseño gráfico/pedagógico para renovar colecciones cada año, renovación periódica de matrices/troqueles y tintas/barnices EN-71 lavables.",
            "D.S. N° 114/2005 MINSAL y norma europea EN-71."
        ],
        [
            "Capital de Trabajo y Diversificación",
            f"{dias_ct} días de costos operativos",
            "Refleja la mezcla real de cobros: licitaciones públicas (45-60 días, 30% escolar), establecimientos privados (30 días) y venta directa/retail (contado-15 días).",
            "Método del Período de Desfase (Sapag Chain, 2014)."
        ],
        [
            "Parámetros Sociales SNI 2026",
            f"TSD {fmt_dec_cl(tasa_soc*100,1)}% | MOC {fmt_dec_cl(cfg['FC_MOC'],2)} | MOSC {fmt_dec_cl(cfg['FC_MOSC'],2)} | MONC {fmt_dec_cl(cfg['FC_MONC'],2)}",
            "Unificación total al estándar SNI 2026: sin IVA ni impuesto a la renta, divisa 1,00, ahorro municipal Curaco contabilizado solo sobre toneladas incorporadas (70%) y $0 en beneficios no cuantificados.",
            "MDSF / SNI (2026), Precios Sociales Vigentes."
        ],
    ], columns=["Concepto / Supuesto", "Valor Adoptado", "Justificación Técnica y Metodológica", "Respaldo / Fuente"])

    df_cotizaciones = pd.DataFrame([
        ["Nota 2", "Máquina Principal", "Máquina Troqueladora Industrial de Rodillos (1200 mm)", "Importado", 8500000, round(8500000 / (1 + iva)), "Cotización Maquinaria Gráfica Industrial Chile (2026)"],
        ["Nota 2", "Corte y Matrices", "Guillotina Cortadora, Mesones y Juego Inicial de Matrices/Troqueles", "Nacional", 3800000, round(3800000 / (1 + iva)), "Cotización Fabricante Nacional de Matrices y Troqueles"],
        ["Nota 2", "Impresión y Secado", "Equipo de Impresión/Serigrafía al Agua y Estantes de Secado", "Importado", 2200000, round(2200000 / (1 + iva)), "Cotización Proveedor Equipos Serigráficos Chile"],
        ["Nota 2", "Habilitación Local", "Acondicionamiento Galpón Ovejería (Electricidad SEC y SEREMI)", "Nacional", 2000000, round(2000000 / (1 + iva)), "Presupuesto Instalador Eléctrico SEC y Obras Menores Osorno"],
        ["Nota 2", "Insumo Terminación", "Tintas EN-71 al agua, barniz protector contra humedad y pegamento", "Nacional", 2000, round(2000 / (1 + iva)), "Lista Mayorista Insumos Gráficos Certificados EN-71"],
        ["Nota 2", "Empaque y Guía", "Caja microcorrugada, instructivo pedagógico impreso y etiqueta", "Nacional", 650, round(650 / (1 + iva)), "Cotización Imprenta y Envases Zona Sur Osorno"],
        ["Nota 3", "Logística Retiro", "Flete furgón contratado ruta Eleuterio Ramírez hacia Ovejería", "Nacional", 30000, round(30000 / (1 + iva)), "Tarifa Flete Local Osorno (por tonelada retirada)"],
        ["Nota 4", "Gasto Fijo Mensual", "Arriendo galpón industrial 140 m2 (Sector Ovejería)", "Exento", 450000, 450000, "Corredoras de Propiedades Sector Industrial Ovejería"],
        ["Nota 4", "Gasto Fijo Mensual", "Electricidad trifásica (Saesa), agua (Suralis) e internet", "Con IVA", 180000, round(180000 / (1 + iva)), "Tarifas Comerciales Saesa / Suralis Osorno"],
        ["Nota 4", "Gasto Fijo Mensual", "Contabilidad Pro Pyme, patente municipal, seguros y marketing", "Con IVA", 150000, round(150000 / (1 + iva)), "Honorarios Contables PyME y Patente Municipalidad Osorno"],
        ["Nota 4", "Diseño y Calidad", "Diseño gráfico/pedagógico externo, renovación matrices y control calidad", "Con IVA", 250000, round(250000 / (1 + iva)), "Honorarios Diseñador Industrial/Gráfico + Reposición Troqueles"],
        ["Nota 5", "Ahorro Municipal", "Costo municipal evitado por tonelada desviada del Vertedero Curaco", "Con IVA", int(cfg["AHORRO_MUNI_TON"]), round(float(cfg["AHORRO_MUNI_TON"]) / (1 + iva)), "Contratos de Aseo Municipalidad de Osorno / SINADER"],
    ], columns=["Referencia", "Categoría", "Descripción del Ítem", "Origen / IVA", "Valor c/IVA ($)", "Valor Neto s/IVA ($)", "Fuente de Respaldo"])

    df_porque = pd.DataFrame([
        ["1. ¿Por qué 15,00 t/año recolectadas y 10,50 t útiles?", "50 kg/día -> 70% útil / 30% retazo", "6 locales de E. Ramírez aportan 50 kg/día (15 t/año). El 12% se descarta por humedad/corchetes y el 18% corresponde a retazo geométrico de troquelado (entregado a reciclador Ley REP), dejando 10,50 t netas para 4.500 juegos."],
        ["2. ¿Cómo se calcula el costo real de personal?", "Sueldo mín. $553.553 + 6,5% emp.", "Ningún cargo está bajo el sueldo mínimo legal ($553.553) y sobre toda la planilla se agregan leyes sociales del empleador (cesantía, SIS, mutualidad y aporte previsional = 6,5%)."],
        ["3. ¿Cómo se resguarda el diseño y la calidad visual?", "$250.000/mes diseño + EN-71", "El proyecto no depende de manufactura artesanal: usa troqueladora industrial, matrices actualizadas periódicamente, asesoría externa de diseño pedagógico/gráfico y barniz protector certificado EN-71."],
        ["4. ¿Por qué se diversifican los canales de venta?", "30% público / 45% priv. / 25% retail", "En demandantes públicos (DAEM/SLEP) se debe licitar en Mercado Público con pagos a 45-60 días; diversificar hacia colegios/jardines privados, librerías locales y familias reduce el riesgo comercial y estabiliza caja."],
        ["5. ¿Por qué VANS (5,5%) supera al VAN Privado (12%)?", "TSD 5,5% + sin impuestos + Curaco", "Evaluación unificada SNI 2026: descuenta a TSD 5,5%, excluye IVA e impuesto a la renta (transferencias), aplica factores sombra MO (0,97/0,95/0,91) y suma ahorro municipal en Curaco solo sobre toneladas incorporadas (sin beneficios inflados)."],
        ["6. ¿Cuál es el Payback simple y el Payback descontado?", "Simple vs. Descontado", "En la tabla comparativa se informa el Payback simple (recuperación nominal del capital inicial); al aplicar descuento intertemporal a las tasas del proyecto (12,0% privado y 5,5% social), la recuperación descontada sigue ocurriendo ampliamente dentro del horizonte de 10 años."],
    ], columns=["Pregunta Clave", "Regla / Cifra", "Justificación Técnica"])

    return df_entrevistas, df_encuesta, df_supuestos, df_catastro_6, df_demanda_canales, df_productos_ficha, df_balance_masa, df_cotizaciones, df_porque


def ejecutar_motor_financiero(cfg):
    horizonte = int(cfg["HORIZONTE_ANIOS"])
    iva = float(cfg["IVA"])
    imp_renta = float(cfg["IMPUESTO_RENTA"])
    tasa_priv = float(cfg["TASA_DESCUENTO_PRIVADA"])
    tasa_soc = float(cfg["TASA_DESCUENTO_SOCIAL"])
    dias_ct = float(cfg["DIAS_DESFASE_CT"])
    carga_pat = float(cfg.get("CARGA_PATRONAL_PCT", 0.065))
    fc_moc, fc_mosc, fc_monc = float(cfg["FC_MOC"]), float(cfg["FC_MOSC"]), float(cfg["FC_MONC"])
    fc_div, arancel = float(cfg["FC_DIVISA"]), float(cfg["ARANCEL_IMP"])

    def factor_social_bien(origen):
        neto = 1.0 / (1.0 + iva)
        if str(origen).strip().lower() == "importado":
            return (neto / (1.0 + arancel)) * fc_div
        return neto

    anios_op = list(range(1, horizonte + 1))
    anios_tot = list(range(0, horizonte + 1))
    cols_op = [f"Año {a}" for a in anios_op]
    cols_tot = [f"Año {a}" for a in anios_tot]

    lineas_productos = [
        {"nombre": cfg["P1_NOMBRE"], "unidades_anio_1": float(cfg["P1_UNIDADES"]), "precio_venta_bruto": float(cfg["P1_PRECIO_BRUTO"]), "kg_carton_por_unidad": float(cfg["P1_KG_CARTON"])},
        {"nombre": cfg["P2_NOMBRE"], "unidades_anio_1": float(cfg["P2_UNIDADES"]), "precio_venta_bruto": float(cfg["P2_PRECIO_BRUTO"]), "kg_carton_por_unidad": float(cfg["P2_KG_CARTON"])},
    ]

    mapa_fc_mo = {"MOC": fc_moc, "MOSC": fc_mosc, "MONC": fc_monc}
    filas_personal = []
    costo_anual_personal_privado = 0.0
    costo_anual_personal_social = 0.0

    for p in cfg["PERSONAL_LISTA"]:
        bruto_mes = float(p["sueldo_bruto_mensual"])
        leyes_mes = round(bruto_mes * carga_pat)
        costo_emp_mes = bruto_mes + leyes_mes
        anual_priv = p["cantidad"] * costo_emp_mes * 12.0
        fc = mapa_fc_mo.get(p["calificacion"], 1.0)
        anual_soc = anual_priv * fc
        costo_anual_personal_privado += anual_priv
        costo_anual_personal_social += anual_soc
        filas_personal.append({
            "Cargo / Puesto": p["cargo"],
            "Cant.": int(p["cantidad"]),
            "Calif. SNI": p["calificacion"],
            "Sueldo Bruto ($)": round(bruto_mes),
            f"Leyes Soc. ({fmt_dec_cl(carga_pat*100,1)}%)": round(leyes_mes),
            "Costo Anual Empresa ($)": round(anual_priv),
            "Factor SNI": fc,
            "Costo Anual Social ($)": round(anual_soc),
        })
    df_personal = pd.DataFrame(filas_personal)

    residuo_1 = float(cfg["RESIDUO_TON_ANIO_1"])
    crec = float(cfg["TASA_CRECIMIENTO"])
    ton_residuo_anual = [residuo_1 * ((1.0 + crec) ** (a - 1)) for a in anios_op]

    dict_cantidades = {"Residuo de Cartón Recolectado (Toneladas)": [round(x, 2) for x in ton_residuo_anual]}
    dict_ingresos_priv = {}
    unidades_totales_anual = np.zeros(horizonte)
    kg_utilizados_anual = np.zeros(horizonte)

    for prod in lineas_productos:
        unids = np.array([round(prod["unidades_anio_1"] * ((1.0 + crec) ** (a - 1))) for a in anios_op])
        unidades_totales_anual += unids
        kg_utilizados_anual += unids * prod["kg_carton_por_unidad"]
        precio_neto = prod["precio_venta_bruto"] / (1.0 + iva)
        ing_neto_anual = np.round(unids * precio_neto)
        dict_cantidades[f"Producción {prod['nombre']} (Unidades)"] = unids.astype(int).tolist()
        dict_ingresos_priv[f"Ventas Netas {prod['nombre']} (Sin IVA)"] = ing_neto_anual.astype(int).tolist()

    dict_cantidades["Total Productos Fabricados (Unidades)"] = unidades_totales_anual.astype(int).tolist()
    ton_inc_arr = np.round(kg_utilizados_anual / 1000.0, 2)
    dict_cantidades["Cartón Efectivamente Incorporado (Toneladas)"] = ton_inc_arr.tolist()
    dict_cantidades["Fracción Residual / Recortes a Reciclador (Toneladas)"] = np.round(np.array(ton_residuo_anual) - ton_inc_arr, 2).tolist()

    df_cantidades = pd.DataFrame.from_dict(dict_cantidades, orient="index", columns=cols_op)
    df_cantidades.index.name = "Ítem Físico"

    # Criterio conservador SNI 2026: ahorro municipal sobre toneladas efectivamente incorporadas
    ahorro_muni_neto_ton = float(cfg["AHORRO_MUNI_TON"]) / (1.0 + iva)
    beneficio_ahorro_muni = np.round(ton_inc_arr * ahorro_muni_neto_ton)
    beneficio_otros_soc = np.round(np.full(horizonte, float(cfg["OTROS_BEN_SOC_ANUAL"])))

    df_ingresos = pd.DataFrame.from_dict(dict_ingresos_priv, orient="index", columns=cols_op)
    df_ingresos.loc["TOTAL INGRESOS PRIVADOS NETOS (SIN IVA)"] = df_ingresos.sum(axis=0)
    df_ingresos.index.name = "Concepto de Ingreso"

    dict_costos_priv, dict_costos_soc = {}, {}
    for cv in cfg["COSTOS_VAR_LISTA"]:
        c_neto = cv["costo"] / (1.0 + iva)
        c_soc = cv["costo"] * factor_social_bien(cv["origen"])
        base_arr = np.array(ton_residuo_anual) if cv["base"] == "Por Tonelada" else unidades_totales_anual
        pref_p = "CV Logístico" if cv["base"] == "Por Tonelada" else "CV"
        pref_s = "CV Logístico Social" if cv["base"] == "Por Tonelada" else "CV Social"
        dict_costos_priv[f"{pref_p}: {cv['item']}"] = np.round(base_arr * c_neto).astype(int).tolist()
        dict_costos_soc[f"{pref_s}: {cv['item']}"] = np.round(base_arr * c_soc).astype(int).tolist()

    for cf in cfg["COSTOS_FIJOS_LISTA"]:
        anual_bruto = cf["mensual"] * 12.0
        anual_neto = (anual_bruto / (1.0 + iva)) if (cf["afecto_iva"] == "Con IVA") else anual_bruto
        dict_costos_priv[f"CF: {cf['item']}"] = np.round(np.full(horizonte, anual_neto)).astype(int).tolist()
        dict_costos_soc[f"CF Social: {cf['item']}"] = np.round(np.full(horizonte, anual_neto)).astype(int).tolist()

    dict_costos_priv["Remuneraciones y Leyes Sociales Empleador (Costo Empresa)"] = np.round(np.full(horizonte, costo_anual_personal_privado)).astype(int).tolist()
    dict_costos_soc["Mano de Obra Valorizada a Precios Sociales (SNI 2026)"] = np.round(np.full(horizonte, costo_anual_personal_social)).astype(int).tolist()

    df_costos_priv = pd.DataFrame.from_dict(dict_costos_priv, orient="index", columns=cols_op)
    df_costos_priv.loc["TOTAL COSTOS OPERATIVOS PRIVADOS (SIN IVA)"] = df_costos_priv.sum(axis=0)
    df_costos_priv.index.name = "Ítem de Costo"

    df_costos_soc = pd.DataFrame.from_dict(dict_costos_soc, orient="index", columns=cols_op)
    df_costos_soc.loc["TOTAL COSTOS OPERATIVOS SOCIALES"] = df_costos_soc.sum(axis=0)

    dict_inv_priv, dict_inv_soc, dict_depreciacion = {}, {}, {}
    valor_desecho_priv_total, valor_desecho_soc_total = 0.0, 0.0

    for inv in cfg["INVERSIONES_LISTA"]:
        fila_p = np.zeros(horizonte + 1)
        fila_s = np.zeros(horizonte + 1)
        fila_d = np.zeros(horizonte)
        monto_neto_priv = inv["monto_bruto"] / (1.0 + iva)
        monto_soc = inv["monto_bruto"] * factor_social_bien(inv["origen"])
        fila_p[0], fila_s[0] = monto_neto_priv, monto_soc

        vida_econ = max(1, int(inv["vida_util_economica"]))
        for anio in range(vida_econ, horizonte, vida_econ):
            fila_p[anio], fila_s[anio] = monto_neto_priv, monto_soc

        vida_cont = max(1, int(inv["vida_util_contable"]))
        dep_anual = (monto_neto_priv * (1.0 - inv["valor_residual_pct"])) / vida_cont
        for a_idx in range(horizonte):
            if ((a_idx % vida_econ) + 1) <= vida_cont:
                fila_d[a_idx] = dep_anual

        valor_desecho_priv_total += monto_neto_priv * inv["valor_residual_pct"]
        valor_desecho_soc_total += monto_soc * inv["valor_residual_pct"]
        dict_inv_priv[inv["item"]] = np.round(fila_p).astype(int).tolist()
        dict_inv_soc[inv["item"]] = np.round(fila_s).astype(int).tolist()
        dict_depreciacion[f"Depreciación: {inv['item']}"] = np.round(fila_d).astype(int).tolist()

    df_inversiones = pd.DataFrame.from_dict(dict_inv_priv, orient="index", columns=cols_tot)
    df_inversiones.loc["TOTAL INVERSIONES Y REINVERSIONES NETAS"] = df_inversiones.sum(axis=0)
    df_inversiones.index.name = "Activo / Ítem de Inversión"

    df_inv_social = pd.DataFrame.from_dict(dict_inv_soc, orient="index", columns=cols_tot)
    df_inv_social.loc["TOTAL INVERSIONES Y REINVERSIONES SOCIALES"] = df_inv_social.sum(axis=0)

    df_depreciacion = pd.DataFrame.from_dict(dict_depreciacion, orient="index", columns=cols_op)
    df_depreciacion.loc["TOTAL DEPRECIACIÓN ANUAL"] = df_depreciacion.sum(axis=0)
    df_depreciacion.index.name = "Ítem de Depreciación"

    fraccion_anual_ct = dias_ct / 365.0
    costos_tot_priv_anual = df_costos_priv.loc["TOTAL COSTOS OPERATIVOS PRIVADOS (SIN IVA)"].values
    costos_tot_soc_anual = df_costos_soc.loc["TOTAL COSTOS OPERATIVOS SOCIALES"].values

    ct_requerido_priv = np.round(costos_tot_priv_anual * fraccion_anual_ct)
    ct_requerido_soc = np.round(costos_tot_soc_anual * fraccion_anual_ct)

    flujo_ct_priv = np.zeros(horizonte + 1)
    flujo_ct_soc = np.zeros(horizonte + 1)
    flujo_ct_priv[0], flujo_ct_soc[0] = -ct_requerido_priv[0], -ct_requerido_soc[0]
    for i in range(1, horizonte):
        flujo_ct_priv[i] = -(ct_requerido_priv[i] - ct_requerido_priv[i - 1])
        flujo_ct_soc[i] = -(ct_requerido_soc[i] - ct_requerido_soc[i - 1])
    flujo_ct_priv[horizonte], flujo_ct_soc[horizonte] = ct_requerido_priv[-1], ct_requerido_soc[-1]

    df_capital_trabajo = pd.DataFrame({
        cols_tot[a]: [
            0 if a == 0 else int(costos_tot_priv_anual[a - 1]),
            0 if a == 0 else int(ct_requerido_priv[a - 1]),
            int(flujo_ct_priv[a]),
        ]
        for a in range(horizonte + 1)
    }, index=[
        "Costos Operativos Anuales Netos ($)",
        f"Capital de Trabajo Requerido ({int(dias_ct)} días)",
        "Flujo de Variación / Recuperación de Capital de Trabajo",
    ])
    df_capital_trabajo.index.name = "Concepto Capital de Trabajo"

    ing_priv_0_10 = np.insert(df_ingresos.loc["TOTAL INGRESOS PRIVADOS NETOS (SIN IVA)"].values, 0, 0)
    costos_priv_0_10 = np.insert(-costos_tot_priv_anual, 0, 0)
    dep_0_10 = np.insert(-df_depreciacion.loc["TOTAL DEPRECIACIÓN ANUAL"].values, 0, 0)

    uai = ing_priv_0_10 + costos_priv_0_10 + dep_0_10
    impuestos = np.where(uai > 0, -np.round(uai * imp_renta), 0)
    udi = uai + impuestos
    reverso_dep = -dep_0_10

    inv_fija_priv = -df_inversiones.loc["TOTAL INVERSIONES Y REINVERSIONES NETAS"].values
    val_desecho_priv_arr = np.zeros(horizonte + 1)
    val_desecho_priv_arr[-1] = round(valor_desecho_priv_total)
    flujo_caja_privado = udi + reverso_dep + inv_fija_priv + flujo_ct_priv + val_desecho_priv_arr

    df_flujo_privado = pd.DataFrame({
        "(+) Ingresos Operacionales Netos (Sin IVA)": ing_priv_0_10,
        "(-) Costos Operativos Totales (Fijos, Variables y Personal)": costos_priv_0_10,
        "(-) Depreciación Legal del Ejercicio": dep_0_10,
        "(=) Utilidad Antes de Impuestos (UAI)": uai,
        f"(-) Impuesto a la Renta ({int(imp_renta * 100)}%)": impuestos,
        "(=) Utilidad Después de Impuestos (UDI)": udi,
        "(+) Ajuste por Depreciación (Gasto No Desembolsable)": reverso_dep,
        "(-) Inversiones y Reinversiones en Activos Fijos": inv_fija_priv,
        "(+/-) Inversión y Recuperación de Capital de Trabajo": flujo_ct_priv,
        "(+) Valor de Desecho de los Activos": val_desecho_priv_arr,
        "(=) FLUJO DE CAJA PRIVADO NETO": flujo_caja_privado,
    }, index=cols_tot).T.astype(int)
    df_flujo_privado.index.name = "Estructura Flujo de Caja Privado"

    van_privado = float(npf.npv(tasa_priv, flujo_caja_privado))
    try:
        tir_privada = float(npf.irr(flujo_caja_privado))
        if np.isnan(tir_privada):
            tir_privada = 0.0
    except Exception:
        tir_privada = 0.0
    payback_privado = calcular_payback(flujo_caja_privado)
    payback_privado_desc = calcular_payback_descontado(flujo_caja_privado, tasa_priv)

    ben_soc_ventas = np.insert(df_ingresos.loc["TOTAL INGRESOS PRIVADOS NETOS (SIN IVA)"].values, 0, 0)
    ben_soc_muni = np.insert(beneficio_ahorro_muni, 0, 0)
    ben_soc_otros = np.insert(beneficio_otros_soc, 0, 0)
    costos_soc_0_10 = np.insert(-costos_tot_soc_anual, 0, 0)
    inv_fija_soc = -df_inv_social.loc["TOTAL INVERSIONES Y REINVERSIONES SOCIALES"].values
    val_desecho_soc_arr = np.zeros(horizonte + 1)
    val_desecho_soc_arr[-1] = round(valor_desecho_soc_total)

    flujo_caja_social = ben_soc_ventas + ben_soc_muni + ben_soc_otros + costos_soc_0_10 + inv_fija_soc + flujo_ct_soc + val_desecho_soc_arr

    df_flujo_social = pd.DataFrame({
        "(+) Beneficio Social por Disponibilidad de Bienes (Ventas s/IVA)": ben_soc_ventas,
        "(+) Liberación de Recursos Municipales (Ahorro Vertedero Curaco)": ben_soc_muni,
        "(+) Otros Beneficios Sociales y Ambientales": ben_soc_otros,
        "(-) Costos Operativos y Mano de Obra a Precios Sociales": costos_soc_0_10,
        "(-) Inversiones y Reinversiones a Precios Sociales": inv_fija_soc,
        "(+/-) Capital de Trabajo a Precios Sociales": flujo_ct_soc,
        "(+) Valor Residual Social de los Activos": val_desecho_soc_arr,
        "(=) FLUJO DE BENEFICIOS SOCIALES NETOS": flujo_caja_social,
    }, index=cols_tot).T.astype(int)
    df_flujo_social.index.name = "Estructura Flujo de Caja Social (SNI 2026)"

    van_social = float(npf.npv(tasa_soc, flujo_caja_social))
    try:
        tir_social = float(npf.irr(flujo_caja_social))
        if np.isnan(tir_social):
            tir_social = 0.0
    except Exception:
        tir_social = 0.0
    payback_social = calcular_payback(flujo_caja_social)
    payback_social_desc = calcular_payback_descontado(flujo_caja_social, tasa_soc)

    df_indicadores = pd.DataFrame([
        {
            "Tipo de Evaluación": "Evaluación Privada",
            "Tasa de Descuento": f"{fmt_dec_cl(tasa_priv * 100, 1)}%",
            "VAN / VANS ($)": fmt_clp(van_privado),
            "TIR / TIRS (%)": f"{fmt_dec_cl(tir_privada * 100, 2)}%",
            "Payback (Años)": f"{fmt_dec_cl(payback_privado, 2)} años" if payback_privado is not None else "No recupera",
            "Decisión": "VIABLE (Rentable)" if van_privado > 0 else "NO VIABLE",
        },
        {
            "Tipo de Evaluación": "Evaluación Social SNI 2026",
            "Tasa de Descuento": f"{fmt_dec_cl(tasa_soc * 100, 1)}%",
            "VAN / VANS ($)": fmt_clp(van_social),
            "TIR / TIRS (%)": f"{fmt_dec_cl(tir_social * 100, 2)}%",
            "Payback (Años)": f"{fmt_dec_cl(payback_social, 2)} años" if payback_social is not None else "No recupera",
            "Decisión": "VIABLE SOCIALMENTE" if van_social > 0 else "NO VIABLE",
        },
    ])

    (
        df_entrevistas, df_encuesta, df_supuestos, df_catastro_6,
        df_demanda_canales, df_productos_ficha, df_balance_masa,
        df_cotizaciones, df_porque,
    ) = armar_tablas_modelo(cfg)
    if len(df_porque) >= 6:
        pb_p_s = fmt_dec_cl(payback_privado, 2) if payback_privado is not None else "N/A"
        pb_p_d = fmt_dec_cl(payback_privado_desc, 2) if payback_privado_desc is not None else "N/A"
        pb_s_s = fmt_dec_cl(payback_social, 2) if payback_social is not None else "N/A"
        pb_s_d = fmt_dec_cl(payback_social_desc, 2) if payback_social_desc is not None else "N/A"
        df_porque.iloc[5, 1] = f"Priv: {pb_p_s}a ({pb_p_d}a desc.) | Soc: {pb_s_s}a ({pb_s_d}a desc.)"
        df_porque.iloc[5, 2] = (
            f"Evaluación Privada ({fmt_dec_cl(tasa_priv*100,1)}%): Payback simple = {pb_p_s} años y Payback descontado = {pb_p_d} años. "
            f"Evaluación Social SNI 2026 ({fmt_dec_cl(tasa_soc*100,1)}%): Payback simple = {pb_s_s} años y Payback descontado = {pb_s_d} años."
        )

    return {
        "cfg": cfg,
        "df_personal": df_personal,
        "df_cantidades": df_cantidades,
        "df_ingresos": df_ingresos,
        "df_costos_priv": df_costos_priv,
        "df_costos_soc": df_costos_soc,
        "df_inversiones": df_inversiones,
        "df_depreciacion": df_depreciacion,
        "df_capital_trabajo": df_capital_trabajo,
        "df_flujo_privado": df_flujo_privado,
        "df_flujo_social": df_flujo_social,
        "df_indicadores": df_indicadores,
        "df_informantes": df_entrevistas,
        "df_encuesta": df_encuesta,
        "df_supuestos": df_supuestos,
        "df_catastro_6": df_catastro_6,
        "df_demanda_3": df_demanda_canales,
        "df_productos_ficha": df_productos_ficha,
        "df_balance_masa": df_balance_masa,
        "df_cotizaciones": df_cotizaciones,
        "df_porque": df_porque,
        "metricas": {
            "van_privado": round(van_privado),
            "tir_privada": round(tir_privada * 100, 2),
            "payback_privado": payback_privado,
            "payback_privado_descontado": payback_privado_desc,
            "van_social": round(van_social),
            "tir_social": round(tir_social * 100, 2),
            "payback_social": payback_social,
            "payback_social_descontado": payback_social_desc,
            "ct_inicial": round(abs(flujo_ct_priv[0])),
            "inv_inicial_priv": round(df_inversiones.loc["TOTAL INVERSIONES Y REINVERSIONES NETAS", "Año 0"]),
            "inv_inicial_bruta": round(sum(float(x["monto_bruto"]) for x in cfg["INVERSIONES_LISTA"])),
            "personal_anual_priv": round(costo_anual_personal_privado),
            "personal_anual_soc": round(costo_anual_personal_social),
            "costos_anio_1": round(costos_tot_priv_anual[0]),
            "ingresos_anio_1": round(df_ingresos.loc["TOTAL INGRESOS PRIVADOS NETOS (SIN IVA)", "Año 1"]),
        },
    }


# ==============================================================================
# 3. EXPORTADOR DE LOS 3 LIBROS EXCEL EDITABLES CON FÓRMULAS VIVAS
# ==============================================================================

def exportar_tres_excels_limpios(resultados, carpeta_destino, usar_pro_pyme_escalonado=False):
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    os.makedirs(carpeta_destino, exist_ok=True)
    r_exc1 = os.path.join(carpeta_destino, "1_Excel_Flujos_Editables.xlsx")
    r_exc2 = os.path.join(carpeta_destino, "2_Excel_Informantes_Encuestas_Osorno.xlsx")
    r_exc3 = os.path.join(carpeta_destino, "3_Excel_Calculos_Proyecciones.xlsx")

    for r_f in [r_exc1, r_exc2, r_exc3]:
        if os.path.exists(r_f):
            try:
                os.remove(r_f)
            except PermissionError:
                raise PermissionError(f"Cierra '{os.path.basename(r_f)}' en Excel antes de continuar.")

    cfg = resultados["cfg"]
    horizonte = int(cfg["HORIZONTE_ANIOS"])
    imp_renta = float(cfg["IMPUESTO_RENTA"])
    tasa_priv = float(cfg["TASA_DESCUENTO_PRIVADA"])
    tasa_soc = float(cfg["TASA_DESCUENTO_SOCIAL"])
    dias_ct = int(cfg["DIAS_DESFASE_CT"])
    ult_let = get_column_letter(horizonte + 2)

    font_tit = Font(name="Calibri", size=12, bold=True, color="000000")
    font_sub = Font(name="Calibri", size=10, italic=True, color="334155")
    font_hdr = Font(name="Calibri", size=10, bold=True, color="000000")
    font_reg = Font(name="Calibri", size=10, bold=False, color="000000")
    font_bold = Font(name="Calibri", size=10, bold=True, color="000000")

    fill_hdr = PatternFill("solid", fgColor="D9E1F2")
    fill_par = PatternFill("solid", fgColor="FFFFFF")
    fill_imp = PatternFill("solid", fgColor="F8FAFC")
    fill_tot = PatternFill("solid", fgColor="EDEDED")
    fill_flu = PatternFill("solid", fgColor="E2EFDA")

    b_fino = Side(style="thin", color="808080")
    b_doble = Side(style="double", color="000000")
    b_top = Side(style="thin", color="000000")
    border_reg = Border(left=b_fino, right=b_fino, top=b_fino, bottom=b_fino)
    border_tot = Border(left=b_fino, right=b_fino, top=b_top, bottom=b_doble)

    def decorar_hoja(ws, titulo, subtitulo, num_filas, num_cols, es_moneda=True, alto_fila=24):
        ws.views.sheetView[0].showGridLines = True
        max_c = max(num_cols, 6)
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_c)
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max_c)
        ws.cell(1, 1, f"Proyecto {cfg['NOMBRE_PROYECTO']} - {limpiar_texto_chileno(titulo)}").font = font_tit
        ws.cell(2, 1, limpiar_texto_chileno(subtitulo)).font = font_sub
        ws.row_dimensions[1].height = 24
        ws.row_dimensions[2].height = 18
        ws.row_dimensions[4].height = 28

        headers = []
        for c in range(1, num_cols + 1):
            ch = ws.cell(4, c)
            ch.value = limpiar_texto_chileno(ch.value)
            headers.append(str(ch.value or ""))
            ch.fill = fill_hdr
            ch.font = font_hdr
            ch.border = border_reg
            ch.alignment = Alignment(horizontal="left" if c == 1 else "center", vertical="center", wrap_text=True)

        for idx_f in range(num_filas):
            r = 5 + idx_f
            ws.row_dimensions[r].height = alto_fila
            t_col1 = str(ws.cell(r, 1).value or "").upper()
            es_flujo = "FLUJO DE CAJA" in t_col1 or "FLUJO DE BENEFICIOS" in t_col1
            es_sub = any(k in t_col1 for k in ["TOTAL", "(=)", "CAPITAL DE TRABAJO REQUERIDO"])

            for c in range(1, num_cols + 1):
                cel = ws.cell(r, c)
                if isinstance(cel.value, str) and not cel.value.startswith("="):
                    cel.value = limpiar_texto_chileno(cel.value)
                val = cel.value
                es_form = isinstance(val, str) and val.startswith("=")
                h_nom = headers[c - 1]

                if es_flujo:
                    cel.fill, cel.font, cel.border = fill_flu, font_bold, border_tot
                elif es_sub:
                    cel.fill, cel.font, cel.border = fill_tot, font_bold, border_tot
                else:
                    cel.fill = fill_par if idx_f % 2 == 0 else fill_imp
                    cel.font = font_bold if c == 1 else font_reg
                    cel.border = border_reg

                if c == 1:
                    cel.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                elif isinstance(val, (int, float, np.integer, np.floating)) or es_form:
                    cel.alignment = Alignment(horizontal="right", vertical="center")
                    if "Tasa" in h_nom or "TIR" in h_nom:
                        cel.number_format = "0.00%"
                    elif "$" in h_nom or (es_moneda and not any(k in h_nom for k in ["Cant.", "Factor", "Payback", "Kg", "Ton", "Meta", "Unidades"])):
                        cel.number_format = '$#,##0;-$#,##0;"$0"'
                    elif "Ton" in h_nom or "Día" in h_nom or "Factor" in h_nom or (isinstance(val, float) and not val.is_integer()):
                        cel.number_format = "#,##0.00"
                    else:
                        cel.number_format = "#,##0"
                else:
                    cel.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

        for col in ws.columns:
            c_idx = col[0].column
            c_let = get_column_letter(c_idx)
            m_len = max((len(str(cel.value or "")) for cel in col if cel.row > 2 and not str(cel.value or "").startswith("=")), default=14)
            ws.column_dimensions[c_let].width = max(min(m_len + 5, 58), 44 if c_idx == 1 else 16)

    # EXCEL 1: Flujos Editables
    with pd.ExcelWriter(r_exc1, engine="openpyxl") as w1:
        df1 = resultados["df_indicadores"].copy()
        df2 = resultados["df_flujo_privado"].copy()
        df3 = resultados["df_flujo_social"].copy()
        df4 = resultados["df_capital_trabajo"].copy()

        df1.to_excel(w1, sheet_name="1. Resumen Rentabilidad", startrow=3, index=False)
        df2.to_excel(w1, sheet_name="2. Flujo Caja Privado", startrow=3, index=True)
        df3.to_excel(w1, sheet_name="3. Flujo Social SNI 2026", startrow=3, index=True)
        df4.to_excel(w1, sheet_name="4. Capital de Trabajo", startrow=3, index=True)

        ws1, ws2, ws3, ws4 = w1.sheets["1. Resumen Rentabilidad"], w1.sheets["2. Flujo Caja Privado"], w1.sheets["3. Flujo Social SNI 2026"], w1.sheets["4. Capital de Trabajo"]

        for col_idx in range(3, horizonte + 3):
            c_let = get_column_letter(col_idx)
            ws4[f"{c_let}6"] = f"=ROUND({c_let}5*({dias_ct}/365), 0)"
        ws4["B7"] = "=-C6"
        for col_idx in range(3, horizonte + 2):
            c_let, n_let = get_column_letter(col_idx), get_column_letter(col_idx + 1)
            ws4[f"{c_let}7"] = f"=-({n_let}6-{c_let}6)"
        ws4[f"{ult_let}7"] = f"={ult_let}6"

        ws2["B13"] = "='4. Capital de Trabajo'!B7"
        ws2["B15"] = "=SUM(B10:B14)"
        for col_idx in range(3, horizonte + 3):
            c_let = get_column_letter(col_idx)
            anio_op = col_idx - 2
            tasa_imp_anio = (0.125 if anio_op == 1 else (0.15 if anio_op == 2 else 0.25)) if usar_pro_pyme_escalonado else imp_renta
            ws2[f"{c_let}8"] = f"=SUM({c_let}5:{c_let}7)"
            ws2[f"{c_let}9"] = f"=IF({c_let}8>0, -ROUND({c_let}8*{tasa_imp_anio}, 0), 0)"
            ws2[f"{c_let}10"] = f"={c_let}8+{c_let}9"
            ws2[f"{c_let}11"] = f"=-{c_let}7"
            ws2[f"{c_let}13"] = f"='4. Capital de Trabajo'!{c_let}7"
            ws2[f"{c_let}15"] = f"=SUM({c_let}10:{c_let}14)"

        for col_idx in range(2, horizonte + 3):
            c_let = get_column_letter(col_idx)
            ws3[f"{c_let}12"] = f"=SUM({c_let}5:{c_let}11)"

        ws1["B5"], ws1["B6"] = tasa_priv, tasa_soc
        ws1["C5"] = f"=ROUND(NPV(B5, '2. Flujo Caja Privado'!C15:{ult_let}15)+'2. Flujo Caja Privado'!B15, 0)"
        ws1["D5"] = f"=IRR('2. Flujo Caja Privado'!B15:{ult_let}15)"
        ws1["F5"] = '=IF(C5>0, "VIABLE (Rentable)", "NO VIABLE")'
        ws1["C6"] = f"=ROUND(NPV(B6, '3. Flujo Social SNI 2026'!C12:{ult_let}12)+'3. Flujo Social SNI 2026'!B12, 0)"
        ws1["D6"] = f"=IRR('3. Flujo Social SNI 2026'!B12:{ult_let}12)"
        ws1["F6"] = '=IF(C6>0, "VIABLE SOCIALMENTE", "NO VIABLE")'

        decorar_hoja(ws1, "Resumen de Rentabilidad (Fórmulas Editables)", f"Privado ({fmt_dec_cl(tasa_priv*100,1)}%) vs. Social SNI 2026 ({fmt_dec_cl(tasa_soc*100,1)}%)", len(df1), df1.shape[1], True)
        decorar_hoja(ws2, "Flujo de Caja Privado (10 Años)", "Valores netos sin IVA con sueldo mínimo $553.553 + 6,5% leyes sociales y diseño continuo", len(df2), df2.shape[1] + 1, True)
        decorar_hoja(ws3, "Flujo de Beneficios Sociales Netos (SNI 2026)", "TSD 5,5%, MOC 0,97, MOSC 0,95, MONC 0,91, Divisa 1,00 y ahorro municipal 70% útil", len(df3), df3.shape[1] + 1, True)
        decorar_hoja(ws4, f"Capital de Trabajo ({dias_ct} Días de Desfase)", "Método del Período de Desfase ajustado a mezcla licitaciones públicas + privados + retail", len(df4), df4.shape[1] + 1, True)

    # EXCEL 2: Terreno, Encuesta, Entrevistas y Canales
    with pd.ExcelWriter(r_exc2, engine="openpyxl") as w2:
        df_cat = resultados["df_catastro_6"].copy()
        df_dem = resultados["df_demanda_3"].copy()
        df_ent = resultados["df_informantes"].copy()
        df_enc = resultados["df_encuesta"].copy()
        df_cot = resultados["df_cotizaciones"].copy()

        df_cat.to_excel(w2, sheet_name="1. Catastro 6 Locales", startrow=3, index=False)
        df_dem.to_excel(w2, sheet_name="2. Canales Diversificados", startrow=3, index=False)
        df_ent.to_excel(w2, sheet_name="3. Registro Entrevistas", startrow=3, index=False)
        df_enc.to_excel(w2, sheet_name="4. Encuesta Demandantes", startrow=3, index=False)
        df_cot.to_excel(w2, sheet_name="5. Cotizaciones Precios", startrow=3, index=False)

        decorar_hoja(w2.sheets["1. Catastro 6 Locales"], "Catastro de 6 Locales Generadores en Calle Eleuterio Ramírez", "Retiro selectivo matutino (05:30 a 06:00 AM antes del camión recolector municipal)", len(df_cat), df_cat.shape[1], False, 30)
        decorar_hoja(w2.sheets["2. Canales Diversificados"], "Canales Comerciales Diversificados (Licitaciones + Privados + Retail)", "Estructura comercial sin dependencia exclusiva de un solo comprador público", len(df_dem), df_dem.shape[1], True, 32)
        decorar_hoja(w2.sheets["3. Registro Entrevistas"], "Plantilla de Registro de Entrevistas en Terreno", "Completar con antecedentes reales (nombre, cargo, fecha y respuestas)", len(df_ent), df_ent.shape[1], False, 36)
        decorar_hoja(w2.sheets["4. Encuesta Demandantes"], "Diseño y Resultados de Encuesta a Demandantes", "Completar con resultados reales de la muestra aplicada en Osorno", len(df_enc), df_enc.shape[1], False, 34)
        decorar_hoja(w2.sheets["5. Cotizaciones Precios"], "Cotizaciones de Maquinaria, Insumos, Diseño y Servicios", "Respaldo de precios con IVA y netos sin IVA", len(df_cot), df_cot.shape[1], True, 28)

    # EXCEL 3: Proyecciones y Cálculos (CON FÓRMULAS VIVAS EN TODAS LAS HOJAS NUMÉRICAS)
    crec_val = float(cfg["TASA_CRECIMIENTO"])
    p1_kg_val = float(cfg["P1_KG_CARTON"])
    p2_kg_val = float(cfg["P2_KG_CARTON"])
    carga_pat_val = float(cfg.get("CARGA_PATRONAL_PCT", 0.065))

    with pd.ExcelWriter(r_exc3, engine="openpyxl") as w3:
        df_p1 = resultados["df_cantidades"].copy()
        df_p2 = resultados["df_ingresos"].copy()
        df_p3 = resultados["df_costos_priv"].copy()
        df_p4 = resultados["df_inversiones"].copy()
        df_p5 = resultados["df_depreciacion"].copy()
        df_p6 = resultados["df_personal"].copy()
        fila_tot_p6 = pd.DataFrame([[
            "TOTAL PLANILLA ANUAL", int(df_p6["Cant."].sum()), "-",
            "-", "-", int(df_p6["Costo Anual Empresa ($)"].sum()),
            "-", int(df_p6["Costo Anual Social ($)"].sum())
        ]], columns=df_p6.columns)
        df_p6_tot = pd.concat([df_p6, fila_tot_p6], ignore_index=True)
        df_p7 = resultados["df_supuestos"].copy()

        df_p1.to_excel(w3, sheet_name="1. Proyeccion Fisica", startrow=3, index=True)
        df_p2.to_excel(w3, sheet_name="2. Proyeccion Ventas", startrow=3, index=True)
        df_p3.to_excel(w3, sheet_name="3. Proyeccion Costos", startrow=3, index=True)
        df_p4.to_excel(w3, sheet_name="4. Inversiones Activos", startrow=3, index=True)
        df_p5.to_excel(w3, sheet_name="5. Depreciacion Lineal", startrow=3, index=True)
        df_p6_tot.to_excel(w3, sheet_name="6. Personal y Leyes Soc", startrow=3, index=False)
        df_p7.to_excel(w3, sheet_name="7. Supuestos SNI 2026", startrow=3, index=False)

        ws_p1 = w3.sheets["1. Proyeccion Fisica"]
        ws_p2 = w3.sheets["2. Proyeccion Ventas"]
        ws_p3 = w3.sheets["3. Proyeccion Costos"]
        ws_p4 = w3.sheets["4. Inversiones Activos"]
        ws_p5 = w3.sheets["5. Depreciacion Lineal"]
        ws_p6 = w3.sheets["6. Personal y Leyes Soc"]

        # Fórmulas vivas en Hoja 1 (Proyección Física)
        for col_idx in range(2, horizonte + 2):
            c_let = get_column_letter(col_idx)
            exp_n = col_idx - 2
            if exp_n > 0:
                ws_p1[f"{c_let}5"] = f"=ROUND($B5*(1+{crec_val})^{exp_n}, 2)"
                ws_p1[f"{c_let}6"] = f"=ROUND($B6*(1+{crec_val})^{exp_n}, 0)"
                ws_p1[f"{c_let}7"] = f"=ROUND($B7*(1+{crec_val})^{exp_n}, 0)"
            ws_p1[f"{c_let}8"] = f"=SUM({c_let}6:{c_let}7)"
            ws_p1[f"{c_let}9"] = f"=ROUND(({c_let}6*{p1_kg_val}+{c_let}7*{p2_kg_val})/1000, 2)"
            ws_p1[f"{c_let}10"] = f"=ROUND({c_let}5-{c_let}9, 2)"

        # Fórmulas vivas en Hojas 2, 3, 4 y 5 (Totales SUM dinámicos)
        r_tot_p2 = 4 + len(df_p2)
        r_tot_p3 = 4 + len(df_p3)
        r_tot_p4 = 4 + len(df_p4)
        r_tot_p5 = 4 + len(df_p5)
        for col_idx in range(2, horizonte + 2):
            c_let = get_column_letter(col_idx)
            ws_p2[f"{c_let}{r_tot_p2}"] = f"=SUM({c_let}5:{c_let}{r_tot_p2 - 1})"
            ws_p3[f"{c_let}{r_tot_p3}"] = f"=SUM({c_let}5:{c_let}{r_tot_p3 - 1})"
            ws_p5[f"{c_let}{r_tot_p5}"] = f"=SUM({c_let}5:{c_let}{r_tot_p5 - 1})"
        for col_idx in range(2, horizonte + 3):
            c_let = get_column_letter(col_idx)
            ws_p4[f"{c_let}{r_tot_p4}"] = f"=SUM({c_let}5:{c_let}{r_tot_p4 - 1})"

        # Fórmulas vivas en Hoja 6 (Personal y Leyes Sociales)
        n_pers = len(df_p6)
        for i_p in range(n_pers):
            rp = 5 + i_p
            ws_p6[f"E{rp}"] = f"=ROUND(D{rp}*{carga_pat_val}, 0)"
            ws_p6[f"F{rp}"] = f"=B{rp}*(D{rp}+E{rp})*12"
            ws_p6[f"H{rp}"] = f"=ROUND(F{rp}*G{rp}, 0)"
        r_tot_p6 = 5 + n_pers
        ws_p6[f"B{r_tot_p6}"] = f"=SUM(B5:B{r_tot_p6 - 1})"
        ws_p6[f"F{r_tot_p6}"] = f"=SUM(F5:F{r_tot_p6 - 1})"
        ws_p6[f"H{r_tot_p6}"] = f"=SUM(H5:H{r_tot_p6 - 1})"

        decorar_hoja(ws_p1, "Proyección Física de Residuo, Producción y Fracción Residual", f"Crecimiento {fmt_dec_cl(cfg['TASA_CRECIMIENTO']*100,1)}% anual | Balance de masa 70% útil / 30% reciclaje autorizado", len(df_p1), df_p1.shape[1] + 1, False)
        decorar_hoja(ws_p2, "Proyección de Ingresos por Ventas (Sin IVA)", "Ambas líneas de productos proyectadas a 10 años (totales con fórmulas vivas)", len(df_p2), df_p2.shape[1] + 1, True)
        decorar_hoja(ws_p3, "Proyección de Costos Operativos (Sin IVA)", "Incluye diseño continuo, renovación de matrices, leyes sociales empleador y terminación EN-71", len(df_p3), df_p3.shape[1] + 1, True)
        decorar_hoja(ws_p4, "Calendario de Inversiones y Reinversiones (Año 0 y Año 5)", "Valores netos sin IVA (totales con fórmulas vivas)", len(df_p4), df_p4.shape[1] + 1, True)
        decorar_hoja(ws_p5, "Depreciación Lineal Anual de Activos Fijos", "Gasto contable no desembolsable (totales con fórmulas vivas)", len(df_p5), df_p5.shape[1] + 1, True)
        decorar_hoja(ws_p6, "Dotación de Personal, Sueldo Mínimo ($553.553), Leyes Sociales y SNI 2026", f"Aporte patronal {fmt_dec_cl(cfg.get('CARGA_PATRONAL_PCT',0.065)*100,1)}% | MOC 0,97 · MOSC 0,95 · MONC 0,91", len(df_p6_tot), df_p6_tot.shape[1], True)
        decorar_hoja(w3.sheets["7. Supuestos SNI 2026"], "Supuestos Técnicos, Comerciales y Normativos", "Criterios consolidados SNI 2026", len(df_p7), df_p7.shape[1], False, 34)

    inyectar_cache_excels_proyecto(r_exc1, r_exc3, resultados, usar_pro_pyme_escalonado=usar_pro_pyme_escalonado)
    return r_exc1, r_exc2, r_exc3


def _inyectar_cache_en_xlsx(ruta_xlsx, cache_por_hoja):
    """
    Inyecta valores calculados (<v>...</v>) directamente en el XML de celdas con fórmula
    sin modificar ningún estilo de openpyxl. Así cualquier visor rápido (Moodle, Drive,
    QuickLook u openpyxl data_only=True) muestra las cifras inmediatamente y Excel
    mantiene todas las fórmulas 100% vivas y editables.
    """
    import xml.etree.ElementTree as ET
    if not os.path.exists(ruta_xlsx) or not cache_por_hoja:
        return

    NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ET.register_namespace("", NS_MAIN)
    ET.register_namespace("r", NS_REL)

    with zipfile.ZipFile(ruta_xlsx, "r") as zin:
        wb_xml = ET.fromstring(zin.read("xl/workbook.xml"))
        rels_xml = ET.fromstring(zin.read("xl/_rels/workbook.xml.rels"))

        rid_to_target = {}
        for rel in rels_xml:
            rid = rel.attrib.get("Id")
            tgt = rel.attrib.get("Target", "").lstrip("/")
            if not tgt.startswith("xl/"):
                tgt = "xl/" + tgt
            rid_to_target[rid] = tgt

        sheet_to_path = {}
        for sh in wb_xml.findall(f".//{{{NS_MAIN}}}sheet"):
            name = sh.attrib.get("name")
            rid = sh.attrib.get(f"{{{NS_REL}}}id")
            if name in cache_por_hoja and rid in rid_to_target:
                sheet_to_path[rid_to_target[rid]] = cache_por_hoja[name]

        if not sheet_to_path:
            return

        archivos_mem = {}
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename in sheet_to_path:
                mapa_celdas = sheet_to_path[item.filename]
                root = ET.fromstring(data)
                for c_el in root.findall(f".//{{{NS_MAIN}}}c"):
                    ref = c_el.attrib.get("r")
                    if ref in mapa_celdas:
                        f_el = c_el.find(f"{{{NS_MAIN}}}f")
                        if f_el is not None:
                            val = mapa_celdas[ref]
                            v_el = c_el.find(f"{{{NS_MAIN}}}v")
                            if v_el is None:
                                v_el = ET.SubElement(c_el, f"{{{NS_MAIN}}}v")
                            if isinstance(val, str):
                                c_el.set("t", "str")
                                v_el.text = val
                            else:
                                if "t" in c_el.attrib:
                                    del c_el.attrib["t"]
                                v_el.text = str(val)
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            archivos_mem[item.filename] = data

    tmp_xlsx = ruta_xlsx + ".tmp_cache"
    with zipfile.ZipFile(tmp_xlsx, "w", zipfile.ZIP_DEFLATED) as zout:
        for fname, fbytes in archivos_mem.items():
            zout.writestr(fname, fbytes)
    os.replace(tmp_xlsx, ruta_xlsx)


def inyectar_cache_excels_proyecto(r_exc1, r_exc3, resultados, usar_pro_pyme_escalonado=False):
    from openpyxl.utils import get_column_letter

    cfg = resultados["cfg"]
    m = resultados["metricas"]
    horizonte = int(cfg["HORIZONTE_ANIOS"])
    df_fp = resultados["df_flujo_privado"]
    df_fs = resultados["df_flujo_social"]
    df_ct = resultados["df_capital_trabajo"]

    # ---- Caché para Excel 1 ----
    cache_1 = {
        "1. Resumen Rentabilidad": {
            "C5": int(round(m["van_privado"])),
            "D5": round(float(m["tir_privada"]) / 100.0, 6),
            "F5": "VIABLE (Rentable)" if m["van_privado"] > 0 else "NO VIABLE",
            "C6": int(round(m["van_social"])),
            "D6": round(float(m["tir_social"]) / 100.0, 6),
            "F6": "VIABLE SOCIALMENTE" if m["van_social"] > 0 else "NO VIABLE",
        },
        "2. Flujo Caja Privado": {},
        "3. Flujo Social SNI 2026": {},
        "4. Capital de Trabajo": {},
    }

    # Hoja 4: Capital de Trabajo
    for col_idx in range(2, horizonte + 3):
        c_let = get_column_letter(col_idx)
        a_idx = col_idx - 2
        if a_idx >= 1:
            cache_1["4. Capital de Trabajo"][f"{c_let}6"] = int(df_ct.iloc[1, a_idx])
        cache_1["4. Capital de Trabajo"][f"{c_let}7"] = int(df_ct.iloc[2, a_idx])

    # Hoja 2: Flujo Caja Privado
    cache_1["2. Flujo Caja Privado"]["B13"] = int(df_fp.iloc[8, 0])
    cache_1["2. Flujo Caja Privado"]["B15"] = int(df_fp.iloc[10, 0])
    for col_idx in range(3, horizonte + 3):
        c_let = get_column_letter(col_idx)
        a_idx = col_idx - 2
        cache_1["2. Flujo Caja Privado"][f"{c_let}8"] = int(df_fp.iloc[3, a_idx])
        cache_1["2. Flujo Caja Privado"][f"{c_let}9"] = int(df_fp.iloc[4, a_idx])
        cache_1["2. Flujo Caja Privado"][f"{c_let}10"] = int(df_fp.iloc[5, a_idx])
        cache_1["2. Flujo Caja Privado"][f"{c_let}11"] = int(df_fp.iloc[6, a_idx])
        cache_1["2. Flujo Caja Privado"][f"{c_let}13"] = int(df_fp.iloc[8, a_idx])
        cache_1["2. Flujo Caja Privado"][f"{c_let}15"] = int(df_fp.iloc[10, a_idx])

    # Hoja 3: Flujo Social SNI 2026
    for col_idx in range(2, horizonte + 3):
        c_let = get_column_letter(col_idx)
        a_idx = col_idx - 2
        cache_1["3. Flujo Social SNI 2026"][f"{c_let}12"] = int(df_fs.iloc[7, a_idx])

    _inyectar_cache_en_xlsx(r_exc1, cache_1)

    # ---- Caché para Excel 3 ----
    df_p1 = resultados["df_cantidades"]
    df_p2 = resultados["df_ingresos"]
    df_p3 = resultados["df_costos_priv"]
    df_p4 = resultados["df_inversiones"]
    df_p5 = resultados["df_depreciacion"]
    df_p6 = resultados["df_personal"]

    cache_3 = {
        "1. Proyeccion Fisica": {},
        "2. Proyeccion Ventas": {},
        "3. Proyeccion Costos": {},
        "4. Inversiones Activos": {},
        "5. Depreciacion Lineal": {},
        "6. Personal y Leyes Soc": {},
    }
    for col_idx in range(2, horizonte + 2):
        c_let = get_column_letter(col_idx)
        j = col_idx - 2
        if j > 0:
            cache_3["1. Proyeccion Fisica"][f"{c_let}5"] = float(df_p1.iloc[0, j])
            cache_3["1. Proyeccion Fisica"][f"{c_let}6"] = int(df_p1.iloc[1, j])
            cache_3["1. Proyeccion Fisica"][f"{c_let}7"] = int(df_p1.iloc[2, j])
        cache_3["1. Proyeccion Fisica"][f"{c_let}8"] = int(df_p1.iloc[3, j])
        cache_3["1. Proyeccion Fisica"][f"{c_let}9"] = float(df_p1.iloc[4, j])
        cache_3["1. Proyeccion Fisica"][f"{c_let}10"] = float(df_p1.iloc[5, j])

        cache_3["2. Proyeccion Ventas"][f"{c_let}{4 + len(df_p2)}"] = int(df_p2.iloc[-1, j])
        cache_3["3. Proyeccion Costos"][f"{c_let}{4 + len(df_p3)}"] = int(df_p3.iloc[-1, j])
        cache_3["5. Depreciacion Lineal"][f"{c_let}{4 + len(df_p5)}"] = int(df_p5.iloc[-1, j])

    for col_idx in range(2, horizonte + 3):
        c_let = get_column_letter(col_idx)
        j = col_idx - 2
        cache_3["4. Inversiones Activos"][f"{c_let}{4 + len(df_p4)}"] = int(df_p4.iloc[-1, j])

    n_pers = len(df_p6)
    for i_p in range(n_pers):
        rp = 5 + i_p
        cache_3["6. Personal y Leyes Soc"][f"E{rp}"] = int(df_p6.iloc[i_p, 4])
        cache_3["6. Personal y Leyes Soc"][f"F{rp}"] = int(df_p6.iloc[i_p, 5])
        cache_3["6. Personal y Leyes Soc"][f"H{rp}"] = int(df_p6.iloc[i_p, 7])
    r_tot_p6 = 5 + n_pers
    cache_3["6. Personal y Leyes Soc"][f"B{r_tot_p6}"] = int(df_p6["Cant."].sum())
    cache_3["6. Personal y Leyes Soc"][f"F{r_tot_p6}"] = int(df_p6["Costo Anual Empresa ($)"].sum())
    cache_3["6. Personal y Leyes Soc"][f"H{r_tot_p6}"] = int(df_p6["Costo Anual Social ($)"].sum())

    _inyectar_cache_en_xlsx(r_exc3, cache_3)


# ==============================================================================
# 4. CONSTRUCTOR WORD ULAGOS (SIN DUPLICACIONES, 100% DINÁMICO SNI 2026)
# ==============================================================================

def configurar_run_arial_limpio(run, size_pt=10.5, bold=False, italic=False, color_rgb=(0, 0, 0), superscript=False):
    run.font.name = "Arial"
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.superscript = superscript
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("ascii", "hAnsi", "cs"):
        rFonts.set(qn(f"w:{attr}"), "Arial")
    if rPr.find(qn("w:noProof")) is None:
        rPr.append(OxmlElement("w:noProof"))
    lang = rPr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        rPr.append(lang)
    lang.set(qn("w:val"), "es-CL")


def buscar_plantilla_en_pc(nombre_archivo="plantilla_hoja_carta_institucional_BLANCO.docx"):
    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    for d in [os.getcwd(), carpeta_script]:
        if os.path.isdir(d):
            cand = os.path.join(d, nombre_archivo)
            if os.path.exists(cand):
                return cand
    return None


def preparar_plantilla_ulagos_fiel():
    ruta_pl = buscar_plantilla_en_pc()
    if ruta_pl is not None:
        doc = Document(ruta_pl)
        usando_plantilla = True
        for anchor in doc.element.iter(qn("wp:anchor")):
            anchor.set("behindDoc", "1")
            anchor.set("layoutInCell", "1")
            reemplazado = False
            for wrap_tag in ["wp:wrapSquare", "wp:wrapTight", "wp:wrapThrough", "wp:wrapTopAndBottom"]:
                for w_el in list(anchor.findall(qn(wrap_tag))):
                    idx_w = list(anchor).index(w_el)
                    anchor.remove(w_el)
                    if not reemplazado and anchor.find(qn("wp:wrapNone")) is None:
                        anchor.insert(idx_w, OxmlElement("wp:wrapNone"))
                        reemplazado = True
        parrafos_dibujo = []
        for p in list(doc.paragraphs):
            tiene_dib = any(True for _ in p._p.iter(qn("w:drawing"))) or any(True for _ in p._p.iter(qn("w:pict")))
            if tiene_dib:
                parrafos_dibujo.append(p)
            else:
                p._element.getparent().remove(p._element)
        if len(parrafos_dibujo) > 0:
            parrafos_dibujo[0].paragraph_format.space_before = Pt(0)
            parrafos_dibujo[0].paragraph_format.space_after = Pt(0)
            parrafos_dibujo[0].paragraph_format.line_spacing = 1.0
            for p_extra in parrafos_dibujo[1:]:
                p_extra._element.getparent().remove(p_extra._element)
        sec0 = doc.sections[0]
        sec0.top_margin = Inches(0.85)
        sec0.bottom_margin = Inches(0.85)
        sec0.left_margin = Inches(0.85)
        sec0.right_margin = Inches(0.85)
    else:
        doc = Document()
        usando_plantilla = False
        sec0 = doc.sections[0]
        sec0.page_width, sec0.page_height = Inches(8.5), Inches(11.0)
        sec0.top_margin, sec0.bottom_margin = Inches(0.95), Inches(0.9)
        sec0.left_margin, sec0.right_margin = Inches(0.9), Inches(0.9)
        sec0.different_first_page_header_footer = True
    return doc, usando_plantilla


def configurar_borde_celda(celda, **kwargs):
    tcPr = celda._tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement("w:tcBorders")
        tcPr.append(tcBorders)
    for edge, val_dict in kwargs.items():
        edge_el = tcBorders.find(qn(f"w:{edge}"))
        if edge_el is None:
            edge_el = OxmlElement(f"w:{edge}")
            tcBorders.append(edge_el)
        for k, v in val_dict.items():
            edge_el.set(qn(f"w:{k}"), str(v))


def sombrear_celda(celda, color_hex):
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), color_hex)
    celda._tc.get_or_add_tcPr().append(shading)


def agregar_tabla_word_proporcionada(doc, df, incluir_indice=False, fuente_pt=8.0, col_izq_indices=(0,), anchos_pulgadas=None, ancho_total_pulgadas=6.7):
    df_work = df.reset_index() if incluir_indice else df.copy()
    filas, cols = df_work.shape
    if anchos_pulgadas is None:
        if cols > 6:
            w_primera = 2.6
            w_resto = (ancho_total_pulgadas - w_primera) / (cols - 1)
            anchos_pulgadas = [w_primera] + [w_resto] * (cols - 1)
        else:
            pesos = [min(max(max(len(str(df_work.columns[c])), max((len(str(df_work.iloc[r, c])) for r in range(filas)), default=8)), 8), 55) for c in range(cols)]
            suma_p = sum(pesos) or 1
            anchos_pulgadas = [(p / suma_p) * ancho_total_pulgadas for p in pesos]

    tabla = doc.add_table(rows=filas + 1, cols=cols)
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabla.autofit = False

    trPr_hdr = tabla.rows[0]._tr.get_or_add_trPr()
    trPr_hdr.append(OxmlElement("w:tblHeader"))
    trPr_hdr.append(OxmlElement("w:cantSplit"))

    for c_idx, col_name in enumerate(df_work.columns):
        cell = tabla.rows[0].cells[c_idx]
        cell.width = Inches(anchos_pulgadas[c_idx])
        sombrear_celda(cell, "D9E2F3")
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx in col_izq_indices else WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2.5)
        p.paragraph_format.space_after = Pt(2.5)
        run = p.add_run(limpiar_texto_chileno(col_name))
        configurar_run_arial_limpio(run, size_pt=fuente_pt, bold=True, color_rgb=(0, 0, 0))
        configurar_borde_celda(
            cell,
            top={"val": "single", "sz": "6", "color": "000000"},
            bottom={"val": "single", "sz": "6", "color": "000000"},
            left={"val": "single", "sz": "4", "color": "64748B"},
            right={"val": "single", "sz": "4", "color": "64748B"},
        )

    for r_idx in range(filas):
        row = tabla.rows[r_idx + 1]
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        texto_primera = limpiar_texto_chileno(df_work.iloc[r_idx, 0]).upper()
        es_destacada = any(k in texto_primera for k in ["TOTAL", "(=)", "FLUJO DE CAJA", "FLUJO DE BENEFICIOS", "CAPITAL DE TRABAJO REQUERIDO"])
        bg_hex = "EEF2F7" if es_destacada else "FFFFFF"

        for c_idx in range(cols):
            cell = row.cells[c_idx]
            cell.width = Inches(anchos_pulgadas[c_idx])
            sombrear_celda(cell, bg_hex)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            val = df_work.iloc[r_idx, c_idx]
            col_nom = str(df_work.columns[c_idx])

            if isinstance(val, (int, float, np.integer, np.floating)):
                if any(k in col_nom for k in ["Cant.", "Meta", "Unidades", "Kg/Mes"]) or ("PRODUCCIÓN" in texto_primera and c_idx > 0) or ("TOTAL PRODUCTOS" in texto_primera and c_idx > 0):
                    txt_val = fmt_int_cl(val)
                elif any(k in col_nom for k in ["Ton", "Día", "Factor"]) or ("TONELADAS" in texto_primera and c_idx > 0):
                    txt_val = fmt_dec_cl(val, 2)
                else:
                    txt_val = fmt_clp(val)
                alineacion = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                txt_val = limpiar_texto_chileno(val)
                alineacion = WD_ALIGN_PARAGRAPH.LEFT if c_idx in col_izq_indices else WD_ALIGN_PARAGRAPH.CENTER

            p = cell.paragraphs[0]
            p.alignment = alineacion
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(txt_val)
            configurar_run_arial_limpio(run, size_pt=fuente_pt, bold=(es_destacada or c_idx == 0), color_rgb=(0, 0, 0))
            configurar_borde_celda(
                cell,
                top={"val": "single", "sz": "6" if es_destacada else "4", "color": "000000" if es_destacada else "64748B"},
                bottom={"val": "double" if es_destacada else "single", "sz": "8" if es_destacada else "4", "color": "000000" if es_destacada else "64748B"},
                left={"val": "single", "sz": "4", "color": "64748B"},
                right={"val": "single", "sz": "4", "color": "64748B"},
            )

    p_esp = doc.add_paragraph()
    p_esp.paragraph_format.space_before = Pt(2)
    p_esp.paragraph_format.space_after = Pt(4)


def agregar_marcador_word(parrafo, nombre_anchor, id_bm):
    bm_start = OxmlElement("w:bookmarkStart")
    bm_start.set(qn("w:id"), str(id_bm))
    bm_start.set(qn("w:name"), nombre_anchor)
    bm_end = OxmlElement("w:bookmarkEnd")
    bm_end.set(qn("w:id"), str(id_bm))
    parrafo._p.insert(0, bm_start)
    parrafo._p.append(bm_end)


def marcar_nivel_esquema_word(parrafo, nivel=0):
    pPr = parrafo._p.get_or_add_pPr()
    outlineLvl = pPr.find(qn("w:outlineLvl"))
    if outlineLvl is None:
        outlineLvl = OxmlElement("w:outlineLvl")
        pPr.append(outlineLvl)
    outlineLvl.set(qn("w:val"), str(nivel))


def insertar_toc_clicable_fijo_pagina_2(doc, items_toc):
    for texto_sec, anchor_name, pag_str, nivel in items_toc:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(3.5 if nivel == 1 else 1.5)
        p.paragraph_format.space_after = Pt(3.5 if nivel == 1 else 1.5)
        p.paragraph_format.left_indent = Inches(0.0 if nivel == 1 else 0.25)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(6.65), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

        hyperlink = OxmlElement("w:hyperlink")
        hyperlink.set(qn("w:anchor"), anchor_name)
        hyperlink.set(qn("w:history"), "1")

        def run_xml_arial(txt, bold=True, pt=10):
            r_el = OxmlElement("w:r")
            rPr = OxmlElement("w:rPr")
            rFonts = OxmlElement("w:rFonts")
            for attr in ("ascii", "hAnsi", "cs"):
                rFonts.set(qn(f"w:{attr}"), "Arial")
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
            t_el.text = limpiar_texto_chileno(txt)
            r_el.append(t_el)
            return r_el

        hyperlink.append(run_xml_arial(texto_sec, bold=(nivel == 1), pt=10 if nivel == 1 else 9.5))
        r_tab = OxmlElement("w:r")
        r_tab.append(OxmlElement("w:tab"))
        hyperlink.append(r_tab)
        hyperlink.append(run_xml_arial(f"Pág. {pag_str}", bold=True, pt=10 if nivel == 1 else 9.5))
        p._p.append(hyperlink)


def exportar_word_a_pdf(ruta_docx, ruta_pdf):
    if not sys.platform.startswith("win"):
        return False
    abs_docx = os.path.abspath(ruta_docx).replace("'", "''")
    abs_pdf = os.path.abspath(ruta_pdf).replace("'", "''")
    ps_script = (
        "$ErrorActionPreference = 'Stop'; "
        "$word = New-Object -ComObject Word.Application; "
        "$word.Visible = $false; $word.DisplayAlerts = 0; "
        f"$doc = $word.Documents.Open('{abs_docx}'); "
        "$doc.SpellingChecked = $true; $doc.GrammarChecked = $true; "
        "$doc.ShowSpellingErrors = $false; $doc.ShowGrammaticalErrors = $false; "
        f"$doc.Save(); $doc.SaveAs([ref]'{abs_pdf}', [ref]17); $doc.Close(); $word.Quit();"
    )
    try:
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script], check=True, timeout=45, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return os.path.exists(ruta_pdf)
    except Exception:
        return False


def generar_informe_word_limpio(resultados, ruta_word, generar_pdf=True):
    if os.path.exists(ruta_word):
        try:
            os.remove(ruta_word)
        except PermissionError:
            raise PermissionError(f"Cierra '{os.path.basename(ruta_word)}' en Word antes de continuar.")

    cfg = resultados["cfg"]
    m = resultados["metricas"]
    iva = float(cfg["IVA"])
    tp = float(cfg["TASA_DESCUENTO_PRIVADA"]) * 100.0
    ts = float(cfg["TASA_DESCUENTO_SOCIAL"]) * 100.0
    crec_pct = float(cfg["TASA_CRECIMIENTO"]) * 100.0
    carga_pct = float(cfg.get("CARGA_PATRONAL_PCT", 0.065)) * 100.0
    dias_ct = int(cfg["DIAS_DESFASE_CT"])
    ton_a1 = float(cfg["RESIDUO_TON_ANIO_1"])
    ton_inc_1 = float(resultados["df_cantidades"].loc["Cartón Efectivamente Incorporado (Toneladas)", "Año 1"])
    ton_mer_1 = max(0.0, ton_a1 - ton_inc_1)

    doc, usando_plantilla = preparar_plantilla_ulagos_fiel()

    # PÁGINA 1: PORTADA ULAGOS
    ind_izq = Inches(2.15) if usando_plantilla else Inches(0.5)
    ind_der = Inches(0.20) if usando_plantilla else Inches(0.5)

    def add_p_portada(texto, size_pt=11, bold=True, italic=False, space_before=0, space_after=4):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.left_indent = ind_izq
        p.paragraph_format.right_indent = ind_der
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(limpiar_texto_chileno(texto))
        configurar_run_arial_limpio(run, size_pt=size_pt, bold=bold, italic=italic)
        return p

    add_p_portada("", size_pt=10, space_before=135 if usando_plantilla else 24, space_after=0)
    add_p_portada("DEPARTAMENTO DE CIENCIAS ADMINISTRATIVAS Y ECONÓMICAS", size_pt=10.5, bold=True, space_after=2)
    add_p_portada("CARRERA DE INGENIERÍA COMERCIAL - CAMPUS OSORNO", size_pt=10, bold=True, space_after=16)
    add_p_portada("EVALUACIÓN PRIVADA Y SOCIAL DE PROYECTO DE ECONOMÍA CIRCULAR:", size_pt=10.5, bold=True, space_after=4)
    add_p_portada(
        f'"{cfg["NOMBRE_PROYECTO"].upper()}: VALORIZACIÓN DE CARTÓN COMERCIAL RECUPERABLE DEL EJE ELEUTERIO RAMÍREZ MEDIANTE MANUFACTURA LOCAL DE MATERIAL DIDÁCTICO Y COGNITIVO EN OSORNO"',
        size_pt=12.8, bold=True, space_after=20
    )
    add_p_portada("ASIGNATURA:", size_pt=9.5, bold=True, space_before=8, space_after=1)
    add_p_portada("Evaluación Integrada de Proyectos", size_pt=10, bold=False, space_after=10)
    add_p_portada("DOCENTE GUÍA:", size_pt=9.5, bold=True, space_after=1)
    add_p_portada(cfg["DOCENTE"], size_pt=10, bold=False, space_after=10)
    add_p_portada("INTEGRANTES:", size_pt=9.5, bold=True, space_after=3)
    for integ in [x.strip() for x in cfg["INTEGRANTES"].split(",") if x.strip()]:
        add_p_portada(f"- {integ}", size_pt=9.5, bold=True, space_after=2)
    add_p_portada("CIUDAD Y FECHA:", size_pt=9.5, bold=True, space_before=10, space_after=1)
    add_p_portada("Osorno, Región de Los Lagos - Noviembre de 2026", size_pt=10, bold=False, space_after=4)

    # PÁGINA 2: ÍNDICE GENERAL
    sec_body = doc.add_section(WD_SECTION.NEW_PAGE)
    sec_body.different_first_page_header_footer = False
    sec_body.header.is_linked_to_previous = True
    sec_body.footer.is_linked_to_previous = True
    sec_body.top_margin, sec_body.bottom_margin = Inches(1.18), Inches(0.85)
    sec_body.left_margin, sec_body.right_margin = Inches(0.9), Inches(0.9)

    p_tit_toc = doc.add_paragraph()
    p_tit_toc.paragraph_format.space_before, p_tit_toc.paragraph_format.space_after = Pt(6), Pt(10)
    configurar_run_arial_limpio(p_tit_toc.add_run("TABLA DE CONTENIDOS (ÍNDICE GENERAL)"), size_pt=13, bold=True)

    items_toc = [
        ("RESUMEN EJECUTIVO", "_Toc_Sec_0", "3", 1),
        ("1. EL PROBLEMA EN OSORNO Y CATASTRO DEL RESIDUO", "_Toc_Sec_1", "4", 1),
        ("2. ESTUDIO DE MERCADO, PRODUCTOS CONCRETOS Y DEMANDA", "_Toc_Sec_2", "7", 1),
        ("3. CONFIGURACIÓN DEL TALLER, BALANCE DE MASA, LOCALIZACIÓN Y CALIDAD", "_Toc_Sec_3", "10", 1),
        ("4. DOTACIÓN DE PERSONAL, LEYES SOCIALES Y PRECIOS SOMBRA SNI 2026", "_Toc_Sec_4", "12", 1),
        ("5. TABLAS DE PRODUCCIÓN, INVERSIONES, COSTOS Y VENTAS (AÑOS 1 AL 10)", "_Toc_Sec_5", "13", 1),
        ("5.a Proyección Física de Residuo, Producción y Fracción Residual", "_Toc_Sub_5a", "13", 2),
        ("5.b Inversiones, Reinversiones y Depreciación Lineal", "_Toc_Sub_5b", "13", 2),
        ("5.c Costos Variables, Gastos Fijos, Diseño y Remuneraciones", "_Toc_Sub_5c", "14", 2),
        ("5.d Ingresos Anuales por Ventas sin IVA (Años 1 al 10)", "_Toc_Sub_5d", "14", 2),
        ("6. CÁLCULO DEL CAPITAL DE TRABAJO (MÉTODO DE DESFASE Y CANALES)", "_Toc_Sec_6", "15", 1),
        ("7. FLUJO DE CAJA PRIVADO A 10 AÑOS Y RENTABILIDAD", "_Toc_Sec_7", "16", 1),
        ("8. EVALUACIÓN SOCIAL DEL PROYECTO (PRECIOS SOCIALES SNI 2026)", "_Toc_Sec_8", "17", 1),
        ("8.1 Resumen Comparativo Privado vs. Social SNI 2026", "_Toc_Sub_81", "17", 2),
        ("9. CONCLUSIONES PRINCIPALES DEL PROYECTO", "_Toc_Sec_9", "19", 1),
        ("ANEXO 1: INSTRUMENTO DE ENCUESTA Y PAUTA DE ENTREVISTAS EN TERRENO", "_Toc_Anx_1", "22", 1),
        ("ANEXO 2: MEMORIA DE CÁLCULO Y PREGUNTAS CLAVE DE DEFENSA", "_Toc_Anx_2", "23", 1),
        ("ANEXO 3: COTIZACIONES DE MÁQUINAS, INSUMOS, DISEÑO Y SERVICIOS", "_Toc_Anx_3", "24", 1),
        ("ANEXO 4: SUPUESTOS TÉCNICOS, TRIBUTARIOS Y NORMATIVOS SNI 2026", "_Toc_Anx_4", "25", 1),
    ]
    insertar_toc_clicable_fijo_pagina_2(doc, items_toc)
    doc.add_page_break()

    bm_counter = [100]

    def add_titulo_seccion(texto, anchor_name=None):
        p = doc.add_paragraph()
        marcar_nivel_esquema_word(p, nivel=0)
        p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(10), Pt(5)
        p.paragraph_format.keep_with_next = True
        configurar_run_arial_limpio(p.add_run(limpiar_texto_chileno(texto)), size_pt=12, bold=True)
        if anchor_name:
            bm_counter[0] += 1
            agregar_marcador_word(p, anchor_name, bm_counter[0])
        return p

    def add_subtitulo(texto, anchor_name=None):
        p = doc.add_paragraph()
        marcar_nivel_esquema_word(p, nivel=1)
        p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(8), Pt(4)
        p.paragraph_format.keep_with_next = True
        configurar_run_arial_limpio(p.add_run(limpiar_texto_chileno(texto)), size_pt=10.5, bold=True)
        if anchor_name:
            bm_counter[0] += 1
            agregar_marcador_word(p, anchor_name, bm_counter[0])
        return p

    def add_parrafo(texto, bold_prefix=None):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(0), Pt(5.5)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            configurar_run_arial_limpio(p.add_run(limpiar_texto_chileno(bold_prefix) + " "), size_pt=10.5, bold=True)
        for parte in re.split(r"(\(Nota \d+\))", limpiar_texto_chileno(texto)):
            if re.match(r"^\(Nota \d+\)$", parte):
                configurar_run_arial_limpio(p.add_run(f" {parte} "), size_pt=8.5, bold=True, superscript=True)
            elif parte:
                configurar_run_arial_limpio(p.add_run(parte), size_pt=10.5, bold=False)
        return p

    # RESUMEN EJECUTIVO (100% dinámico con métricas SNI 2026)
    add_titulo_seccion("RESUMEN EJECUTIVO", "_Toc_Sec_0")
    add_parrafo(
        f'El proyecto "{cfg["NOMBRE_PROYECTO"]}" aborda el bajo aprovechamiento y la alta disposición en vertedero del cartón corrugado comercial recuperable generado en el eje céntrico de Osorno. Evaluado en un horizonte de {cfg["HORIZONTE_ANIOS"]} años, propone instalar un taller de valorización en el Sector Industrial de Ovejería (140 m2) para recuperar cajas limpias antes del paso del camión recolector municipal (06:00 a 07:00 AM) y transformarlas en juegos didácticos infantiles y kits cognitivos para personas mayores.'
    )
    add_parrafo(
        f"El suministro inicial proviene de 6 locales comerciales catastrados en calle Eleuterio Ramírez (50 kg/día hábil = 1.250 kg/mes = {fmt_dec_cl(ton_a1,2)} toneladas/año en Año 1), con un balance de masa técnico de 70% de fibra incorporada ({fmt_dec_cl(ton_inc_1,2)} t/año) y 30% de fracción residual ({fmt_dec_cl(ton_mer_1,2)} t/año entre selección y retazo de troquelado) entregada con trazabilidad a un reciclador autorizado bajo Ley REP. La proyección de crecimiento adopta una tasa conservadora de {fmt_dec_cl(crec_pct,1)}% anual, respaldada por la incorporación gradual de comercios aledaños y contrastada con un escenario estancado (0%)."
    )
    add_parrafo(
        f"Para mitigar el riesgo de licitaciones públicas, la estrategia comercial diversifica las ventas entre establecimientos educacionales privados/subvencionados (45%), licitaciones vía Mercado Público/Compra Ágil (30%), retail local y familias (25%), además de centros de adulto mayor y cuidadores. El modelo financiero incorpora el sueldo mínimo legal vigente ($553.553) más {fmt_dec_cl(carga_pct,1)}% de leyes sociales del empleador en toda la planilla, junto con un presupuesto mensual de diseño gráfico/pedagógico y renovación de matrices ($250.000/mes c/IVA) para asegurar calidad visual y funcional."
    )
    add_parrafo(
        f"Bajo un criterio metodológico unificado SNI 2026, con inversión inicial de {fmt_clp(m['inv_inicial_bruta'])} c/IVA ({fmt_clp(m['inv_inicial_priv'])} netos) y capital de trabajo de {fmt_clp(m['ct_inicial'])} ({dias_ct} días de desfase), la Evaluación Privada ({fmt_dec_cl(tp,1)}%) arroja un VAN de {fmt_clp(m['van_privado'])}, TIR de {fmt_dec_cl(m['tir_privada'],2)}% y payback de {fmt_dec_cl(m['payback_privado'],2) if m['payback_privado'] is not None else 'N/A'} años. En la Evaluación Social SNI 2026 (TSD {fmt_dec_cl(ts,1)}%, factores MO {fmt_dec_cl(cfg['FC_MOC'],2)}/{fmt_dec_cl(cfg['FC_MOSC'],2)}/{fmt_dec_cl(cfg['FC_MONC'],2)} y ahorro municipal en Vertedero Curaco solo sobre las toneladas incorporadas), el VANS alcanza {fmt_clp(m['van_social'])} y la TIRS llega a {fmt_dec_cl(m['tir_social'],2)}%."
    )

    # SECCIÓN 1: PROBLEMA Y CATASTRO DEL RESIDUO
    add_titulo_seccion("1. EL PROBLEMA EN OSORNO Y CATASTRO DEL RESIDUO", "_Toc_Sec_1")
    add_parrafo(
        "El Vertedero Provincial de Curaco en Osorno enfrenta una presión creciente sobre su vida útil debido a la disposición diaria de residuos valorizables, entre ellos cajas de cartón corrugado limpio descartadas por el comercio céntrico. En calle Eleuterio Ramírez, las tiendas sacan temprano sus embalajes a la vereda sin segregación diferenciada, por lo que el camión municipal los mezcla con basura domiciliaria entre las 06:00 y 07:00 AM."
    )
    add_parrafo(
        f"El levantamiento preliminar en terreno sobre 6 locales de calle Eleuterio Ramírez identifica una disponibilidad inicial de 50 kg diarios (1.250 kg/mes en 25 días hábiles = {fmt_dec_cl(ton_a1,2)} toneladas/año), tal como detalla la Tabla 1.1:"
    )
    agregar_tabla_word_proporcionada(
        doc, resultados["df_catastro_6"], incluir_indice=False, fuente_pt=7.8,
        col_izq_indices=(1, 2, 3, 4), anchos_pulgadas=[0.55, 1.15, 1.05, 0.85, 1.75, 0.45, 0.45, 0.45]
    )

    # SECCIÓN 2: ESTUDIO DE MERCADO, PRODUCTOS CONCRETOS, DEMANDA, ENCUESTA Y ENTREVISTAS
    add_titulo_seccion("2. ESTUDIO DE MERCADO, PRODUCTOS CONCRETOS Y DEMANDA", "_Toc_Sec_2")
    add_subtitulo("2.1 Especificación Técnica de Productos Concretos y Análisis Competitivo")
    add_parrafo(
        "La selección de dos líneas de productos concretos responde a dos segmentos complementarios con necesidad de material didáctico y terapéutico liviano, seguro y más económico que las alternativas de madera importada ($22.000 a $28.000). Para garantizar calidad visual y durabilidad frente al uso intensivo, las piezas se fabrican en cartón multicapa prensado con troquelado industrial de precisión, tintas certificadas al agua (norma EN-71) y barniz protector lavable (D.S. N° 114/2005 MINSAL). La Tabla 2.1 especifica los juegos concretos incluidos en cada línea:"
    )
    agregar_tabla_word_proporcionada(
        doc, resultados["df_productos_ficha"], incluir_indice=False, fuente_pt=7.8,
        col_izq_indices=(0, 1, 2, 4), anchos_pulgadas=[1.15, 2.05, 1.05, 0.90, 1.55]
    )

    add_subtitulo("2.2 Estimación de Demanda, Proyección de Juegos y Diversificación de Canales")
    add_parrafo(
        f"El dimensionamiento del mercado objetivo en la comuna de Osorno distingue: (a) mercado escolar y parvulario (jardines infantiles particulares, salas cuna, colegios subvencionados y establecimientos municipales), cuya meta inicial conservadora es de {fmt_int_cl(cfg['P1_UNIDADES'])} sets anuales; y (b) mercado de personas mayores (hogares/ELEAM privados, clubes comunales, fundaciones, cajas de compensación y familias cuidadoras), con meta inicial de {fmt_int_cl(cfg['P2_UNIDADES'])} kits anuales. Dado que el acceso a compradores públicos exige participar en procesos competitivos (Compra Ágil y licitaciones en Mercado Público), la estrategia diversifica los canales de comercialización para no depender de un solo cliente (Tabla 2.2):"
    )
    agregar_tabla_word_proporcionada(
        doc, resultados["df_demanda_3"], incluir_indice=False, fuente_pt=7.7,
        col_izq_indices=(1, 2, 6), anchos_pulgadas=[0.55, 1.45, 1.05, 0.55, 0.50, 0.65, 1.95]
    )
    add_parrafo(
        f"Proyección de demanda de juegos (Años 1 al {cfg['HORIZONTE_ANIOS']}): aplicando una tasa de expansión comercial conservadora de {fmt_dec_cl(crec_pct,1)}% anual (alineada con el crecimiento del comercio regional y apertura gradual de clientes en la provincia), el volumen proyectado evoluciona desde {fmt_int_cl(int(cfg['P1_UNIDADES'])+int(cfg['P2_UNIDADES']))} unidades en el Año 1 hasta {fmt_int_cl(resultados['df_cantidades'].loc['Total Productos Fabricados (Unidades)'].iloc[-1])} unidades en el Año {cfg['HORIZONTE_ANIOS']} (detalle anual en Sección 5.a y escenario de 0% crecimiento evaluado en Sensibilidad 8.3)."
    )

    add_subtitulo("2.3 Diseño de Encuesta a Demandantes y Registro de Entrevistas (Validación en Terreno)")
    add_parrafo(
        "Con el fin de respaldar empíricamente la disposición a pagar, la preferencia por juegos concretos y los requisitos de compra de cada canal, se diseñó un instrumento mixto compuesto por una encuesta estructurada a demandantes y una pauta de entrevista semiestructurada para actores clave. Nota metodológica de transparencia: los campos marcados como [POR COMPLETAR] corresponden al trabajo de campo en ejecución y se completarán con las respuestas verificables antes de la etapa de factibilidad definitiva (pauta completa en Anexo 1):"
    )
    agregar_tabla_word_proporcionada(
        doc, resultados["df_encuesta"], incluir_indice=False, fuente_pt=7.7,
        col_izq_indices=(0, 1, 2), anchos_pulgadas=[2.65, 1.65, 2.40]
    )
    agregar_tabla_word_proporcionada(
        doc, resultados["df_informantes"], incluir_indice=False, fuente_pt=7.6,
        col_izq_indices=(0, 1, 2, 3), anchos_pulgadas=[1.35, 1.50, 1.15, 2.70]
    )

    # SECCIÓN 3: FUNCIONAMIENTO DEL TALLER, BALANCE DE MASA Y DISEÑO/CALIDAD
    add_titulo_seccion("3. CONFIGURACIÓN DEL TALLER, BALANCE DE MASA, LOCALIZACIÓN Y CALIDAD", "_Toc_Sec_3")
    add_parrafo(
        f"De lunes a sábado (05:30 a 06:15 AM), un furgón contratado ($30.000 c/IVA por tonelada (Nota 3) ) retira el cartón en los 6 locales de calle Eleuterio Ramírez y lo traslada al galpón de 140 m2 arrendado en el Sector Industrial de Ovejería ($450.000/mes exento (Nota 4) ). Allí se realiza recepción, clasificación, troquelado industrial con matrices intercambiables, impresión con tintas al agua EN-71, sellado protector contra humedad y control de calidad unitario."
    )
    add_parrafo(
        "Memoria Técnica del Balance de Masa (70% útil / 30% fracción residual): la Tabla 3.1 desglosa paso a paso cómo se llega al aprovechamiento neto del 70% a partir de pérdidas físicas verificables en recepción y corte:"
    )
    agregar_tabla_word_proporcionada(
        doc, resultados["df_balance_masa"], incluir_indice=False, fuente_pt=7.8,
        col_izq_indices=(0, 3), anchos_pulgadas=[2.00, 0.65, 0.85, 3.20]
    )
    add_parrafo(
        "Aseguramiento de Calidad Visual, Funcional y Renovación de Diseños: para evitar que los juegos pierdan vigencia comercial o presenten terminaciones artesanales deficientes, el presupuesto incluye un servicio mensual permanente de diseño gráfico, industrial y pedagógico junto con la renovación anual de matrices y prototipos ($250.000/mes c/IVA (Nota 4) ). Esto asegura actualización periódica de temáticas educativas, ergonomía validada para adultos mayores y terminaciones uniformes de estándar industrial."
    )

    # SECCIÓN 4: DOTACIÓN, SUELDO MÍNIMO $553.553 + LEYES SOCIALES EMPLEADOR + SNI 2026
    add_titulo_seccion("4. DOTACIÓN DE PERSONAL, LEYES SOCIALES Y PRECIOS SOMBRA SNI 2026", "_Toc_Sec_4")
    add_parrafo(
        f"La empresa operará como Sociedad por Acciones (SpA) en Régimen Pro Pyme General ({int(float(cfg['IMPUESTO_RENTA'])*100)}% impuesto a la renta). La dotación de 5 trabajadores (Nota 6) respeta el sueldo mínimo legal vigente ($553.553 bruto en operarios) e incorpora sobre toda la planilla un {fmt_dec_cl(carga_pct,1)}% de leyes sociales de cargo del empleador (Seguro de Cesantía 2,40%, SIS 1,54%, Mutualidad Ley 16.744 0,93% y aporte previsional empleador 1,63%). Para la evaluación social se aplican estrictamente los factores SNI 2026 (MOC 0,97; MOSC 0,95; MONC 0,91), resultando un costo empresa anual de {fmt_clp(m['personal_anual_priv'])} y un costo social de {fmt_clp(m['personal_anual_soc'])} (Tabla 4.1):"
    )
    df_pers_tot = resultados["df_personal"].copy()
    fila_tot_p = pd.DataFrame([[
        "TOTAL PLANILLA ANUAL", int(df_pers_tot["Cant."].sum()), "-",
        "-", "-", int(df_pers_tot["Costo Anual Empresa ($)"].sum()),
        "-", int(df_pers_tot["Costo Anual Social ($)"].sum())
    ]], columns=df_pers_tot.columns)
    df_pers_con_tot = pd.concat([df_pers_tot, fila_tot_p], ignore_index=True)
    agregar_tabla_word_proporcionada(
        doc, df_pers_con_tot, incluir_indice=False, fuente_pt=7.4,
        col_izq_indices=(0,), anchos_pulgadas=[1.80, 0.42, 0.55, 0.78, 0.72, 0.98, 0.52, 0.93]
    )

    p_sep = doc.add_paragraph()
    p_sep.paragraph_format.space_before, p_sep.paragraph_format.space_after = Pt(4), Pt(2)
    configurar_run_arial_limpio(p_sep.add_run("________________________________________"), size_pt=8.5, bold=True)
    p_nt = doc.add_paragraph()
    p_nt.paragraph_format.space_after = Pt(2)
    configurar_run_arial_limpio(p_nt.add_run("NOTAS A PIE DE PÁGINA - REFERENCIAS DE PRECIOS, COSTOS Y PARÁMETROS:"), size_pt=8.5, bold=True)
    for n_txt in [
        f"(Nota 1) Precios objetivo propuestos: {fmt_clp(cfg['P1_PRECIO_BRUTO'])} c/IVA Set Didáctico Escolar y {fmt_clp(cfg['P2_PRECIO_BRUTO'])} c/IVA Kit Cognitivo Adulto Mayor (20% a 30% inferiores a equivalentes en madera), sujetos a ratificación final mediante encuesta a demandantes (Anexo 1).",
        f"(Nota 2) Cotizaciones de maquinaria e insumos gráficos: Inversión inicial {fmt_clp(m['inv_inicial_bruta'])} c/IVA ({fmt_clp(m['inv_inicial_priv'])} netos), tintas al agua EN-71 con barniz protector ($2.000/unid c/IVA) y caja con instructivo ($650/unid c/IVA).",
        "(Nota 3) Servicio de flete contratado en furgón utilitario local para retiro matutino en calle Eleuterio Ramírez hacia Sector Industrial Ovejería: $30.000 c/IVA por tonelada ($25.210 netos).",
        "(Nota 4) Costos fijos mensuales en Osorno: Arriendo galpón 140 m2 Ovejería ($450.000 exento), servicios básicos ($180.000 c/IVA), administración/contabilidad ($150.000 c/IVA) y diseño gráfico/pedagógico + renovación de matrices ($250.000 c/IVA).",
        f"(Nota 5) Ahorro municipal por tonelada desviada del Vertedero Provincial de Curaco: {fmt_clp(cfg['AHORRO_MUNI_TON'])} c/IVA ({fmt_clp(cfg['AHORRO_MUNI_TON']/(1+iva))} netos), contabilizado conservadoramente solo sobre toneladas incorporadas (70%).",
        f"(Nota 6) Remuneraciones actualizadas a sueldo mínimo legal ($553.553) + {fmt_dec_cl(carga_pct,1)}% de leyes sociales del empleador (cesantía, SIS, mutualidad y aporte previsional). Factores sociales oficiales MDSF/SNI 2026: MOC = {fmt_dec_cl(cfg['FC_MOC'],2)}; MOSC = {fmt_dec_cl(cfg['FC_MOSC'],2)}; MONC = {fmt_dec_cl(cfg['FC_MONC'],2)}; Divisa = {fmt_dec_cl(cfg['FC_DIVISA'],2)}.",
    ]:
        pn = doc.add_paragraph()
        pn.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pn.paragraph_format.space_before, pn.paragraph_format.space_after = Pt(1), Pt(1.5)
        configurar_run_arial_limpio(pn.add_run(limpiar_texto_chileno(n_txt)), size_pt=8.0)

    # SECCIÓN HORIZONTAL PARA TABLAS A 10 AÑOS
    sec_land = doc.add_section(WD_SECTION.NEW_PAGE)
    sec_land.orientation = WD_ORIENT.LANDSCAPE
    sec_land.page_width, sec_land.page_height = Inches(11.0), Inches(8.5)
    sec_land.different_first_page_header_footer = False
    sec_land.header.is_linked_to_previous = True
    sec_land.footer.is_linked_to_previous = True
    sec_land.top_margin, sec_land.bottom_margin = Inches(1.12), Inches(0.65)
    sec_land.left_margin, sec_land.right_margin = Inches(0.65), Inches(0.65)

    add_titulo_seccion("5. TABLAS DE PRODUCCIÓN, INVERSIONES, COSTOS Y VENTAS (AÑOS 1 AL 10)", "_Toc_Sec_5")
    add_subtitulo(f"5.a Proyección Física de Residuo, Producción y Fracción Residual (Crecimiento {fmt_dec_cl(crec_pct,1)}% anual)", "_Toc_Sub_5a")
    agregar_tabla_word_proporcionada(doc, resultados["df_cantidades"], incluir_indice=True, fuente_pt=7.3, col_izq_indices=(0,), ancho_total_pulgadas=9.6)

    add_subtitulo(f"5.b Inversiones en Año 0 ({fmt_clp(m['inv_inicial_bruta'])} c/IVA = {fmt_clp(m['inv_inicial_priv'])} netos), Reinversión y Depreciación", "_Toc_Sub_5b")
    agregar_tabla_word_proporcionada(doc, resultados["df_inversiones"], incluir_indice=True, fuente_pt=7.1, col_izq_indices=(0,), ancho_total_pulgadas=9.6)
    agregar_tabla_word_proporcionada(doc, resultados["df_depreciacion"], incluir_indice=True, fuente_pt=7.1, col_izq_indices=(0,), ancho_total_pulgadas=9.6)

    add_subtitulo("5.c Costos Variables, Gastos Fijos, Diseño y Remuneraciones con Leyes Sociales (Sin IVA)", "_Toc_Sub_5c")
    agregar_tabla_word_proporcionada(doc, resultados["df_costos_priv"], incluir_indice=True, fuente_pt=7.0, col_izq_indices=(0,), ancho_total_pulgadas=9.6)

    add_subtitulo("5.d Ingresos Anuales por Ventas sin IVA (Años 1 al 10)", "_Toc_Sub_5d")
    agregar_tabla_word_proporcionada(doc, resultados["df_ingresos"], incluir_indice=True, fuente_pt=7.3, col_izq_indices=(0,), ancho_total_pulgadas=9.6)

    add_titulo_seccion("6. CÁLCULO DEL CAPITAL DE TRABAJO (MÉTODO DE DESFASE Y CANALES)", "_Toc_Sec_6")
    add_parrafo(
        f"Dado que la participación en licitaciones y Compra Ágil con compradores públicos (30% de la línea escolar) implica ciclos de cobro de 45 a 60 días, mientras que el canal privado opera a 30 días y el retail/familias a contado-15 días, se adopta un período de desfase ponderado de {dias_ct} días ((Costos Anuales x {dias_ct}) / 365). El capital de trabajo inicial asciende a {fmt_clp(m['ct_inicial'])} en Año 0 y se recupera íntegramente al finalizar el Año {cfg['HORIZONTE_ANIOS']}:"
    )
    agregar_tabla_word_proporcionada(doc, resultados["df_capital_trabajo"], incluir_indice=True, fuente_pt=7.3, col_izq_indices=(0,), ancho_total_pulgadas=9.6)

    add_titulo_seccion("7. FLUJO DE CAJA PRIVADO A 10 AÑOS Y RENTABILIDAD", "_Toc_Sec_7")
    add_parrafo(
        f"En la Tabla 7.1 se presenta el Flujo de Caja Privado neto de IVA (respaldado con fórmulas editables en el Anexo Excel 1), aplicando {int(float(cfg['IMPUESTO_RENTA'])*100)}% de Impuesto a la Renta y tasa de descuento privada de {fmt_dec_cl(tp,1)}%:"
    )
    agregar_tabla_word_proporcionada(doc, resultados["df_flujo_privado"], incluir_indice=True, fuente_pt=7.0, col_izq_indices=(0,), ancho_total_pulgadas=9.6)

    add_titulo_seccion("8. EVALUACIÓN SOCIAL DEL PROYECTO (PRECIOS SOCIALES SNI 2026)", "_Toc_Sec_8")
    add_parrafo(
        f"El Flujo Social unificado bajo normativa SNI 2026 (Tabla 8.1) elimina el IVA, aranceles e impuesto a la renta (transferencias internas), aplica factores sombra de mano de obra (MOC {fmt_dec_cl(cfg['FC_MOC'],2)}, MOSC {fmt_dec_cl(cfg['FC_MOSC'],2)}, MONC {fmt_dec_cl(cfg['FC_MONC'],2)}) y divisa ({fmt_dec_cl(cfg['FC_DIVISA'],2)}), contabiliza el ahorro municipal en el Vertedero de Curaco ({fmt_clp(cfg['AHORRO_MUNI_TON']/(1+iva))} netos/ton (Nota 5) ) conservadoramente sobre las toneladas efectivamente incorporadas y descuenta a la Tasa Social de Descuento vigente de {fmt_dec_cl(ts,1)}%:"
    )
    agregar_tabla_word_proporcionada(doc, resultados["df_flujo_social"], incluir_indice=True, fuente_pt=7.1, col_izq_indices=(0,), ancho_total_pulgadas=9.6)

    add_subtitulo(f"8.1 Resumen Comparativo Privado ({fmt_dec_cl(tp,1)}%) vs. Social SNI 2026 ({fmt_dec_cl(ts,1)}%)", "_Toc_Sub_81")
    agregar_tabla_word_proporcionada(
        doc, resultados["df_indicadores"], incluir_indice=False, fuente_pt=8.2,
        col_izq_indices=(0,), anchos_pulgadas=[2.4, 1.3, 1.6, 1.3, 1.4, 1.6]
    )

    # RETORNO A VERTICAL PARA GRÁFICOS, CONCLUSIONES, CANVAS, MML Y ANEXOS
    sec_port_final = doc.add_section(WD_SECTION.NEW_PAGE)
    sec_port_final.orientation = WD_ORIENT.PORTRAIT
    sec_port_final.page_width, sec_port_final.page_height = Inches(8.5), Inches(11.0)
    sec_port_final.different_first_page_header_footer = False
    sec_port_final.header.is_linked_to_previous = True
    sec_port_final.footer.is_linked_to_previous = True
    sec_port_final.top_margin, sec_port_final.bottom_margin = Inches(1.18), Inches(0.85)
    sec_port_final.left_margin, sec_port_final.right_margin = Inches(0.9), Inches(0.9)

    add_titulo_seccion("9. CONCLUSIONES PRINCIPALES DEL PROYECTO", "_Toc_Sec_9")
    add_parrafo(
        f"1. Consistencia técnica y territorial: la valorización de {fmt_dec_cl(ton_a1,2)} toneladas/año de cartón limpio del eje Eleuterio Ramírez permite incorporar {fmt_dec_cl(ton_inc_1,2)} toneladas (70%) en 4.500 juegos educativos y cognitivos con estándar industrial y trazabilidad de la fracción residual ({fmt_dec_cl(ton_mer_1,2)} t/año a reciclador Ley REP)."
    )
    add_parrafo(
        f"2. Rentabilidad privada realista y sostenible: incorporando el sueldo mínimo legal vigente ($553.553) con {fmt_dec_cl(carga_pct,1)}% de leyes sociales empleador, un presupuesto permanente de diseño/calidad ($250.000/mes c/IVA) y diversificación de canales, el proyecto alcanza un VAN Privado ({fmt_dec_cl(tp,1)}%) de {fmt_clp(m['van_privado'])}, una TIR de {fmt_dec_cl(m['tir_privada'],2)}% y un período de recuperación de {fmt_dec_cl(m['payback_privado'],2) if m['payback_privado'] is not None else 'N/A'} años."
    )
    add_parrafo(
        f"3. Alto impacto social bajo normativa SNI 2026: descontado a la Tasa Social de Descuento oficial de {fmt_dec_cl(ts,1)}% y bajo criterio conservador sin beneficios no cuantificados, el VANS asciende a {fmt_clp(m['van_social'])} y la TIRS a {fmt_dec_cl(m['tir_social'],2)}%, confirmando la conveniencia económica, social y ambiental para Osorno. Como paso previo a ejecución, el equipo deberá completar la validación empírica de la encuesta y entrevistas registradas en el Anexo 1."
    )

    add_titulo_seccion("ANEXO 1: INSTRUMENTO DE ENCUESTA Y PAUTA DE ENTREVISTAS EN TERRENO", "_Toc_Anx_1")
    add_parrafo(
        "Pauta de entrevista semiestructurada (15 minutos): (1) ¿Qué volumen aproximado de cajas de cartón limpias descarta semanalmente y en qué horario? [generadores]; (2) ¿Qué tipos de material didáctico o terapéutico requieren mayor renovación anual?; (3) ¿Qué atributos valoran más en durabilidad, diseño visual y seguridad?; (4) ¿Cuál es su rango de precio aceptable frente a juegos de madera o plástico?; (5) ¿Qué mecanismo de compra utilizan (compra directa, Compra Ágil, licitación) y cuál es el plazo habitual de pago?; (6) ¿Estarían dispuestos a evaluar un prototipo piloto?"
    )
    agregar_tabla_word_proporcionada(
        doc, resultados["df_encuesta"], incluir_indice=False, fuente_pt=7.7,
        col_izq_indices=(0, 1, 2), anchos_pulgadas=[2.65, 1.65, 2.40]
    )
    agregar_tabla_word_proporcionada(
        doc, resultados["df_informantes"], incluir_indice=False, fuente_pt=7.6,
        col_izq_indices=(0, 1, 2, 3), anchos_pulgadas=[1.35, 1.50, 1.15, 2.70]
    )

    add_titulo_seccion("ANEXO 2: MEMORIA DE CÁLCULO Y PREGUNTAS CLAVE DE DEFENSA", "_Toc_Anx_2")
    agregar_tabla_word_proporcionada(
        doc, resultados["df_porque"], incluir_indice=False, fuente_pt=7.9,
        col_izq_indices=(0, 1, 2), anchos_pulgadas=[1.85, 1.35, 3.50]
    )

    add_titulo_seccion("ANEXO 3: COTIZACIONES DE MÁQUINAS, INSUMOS, DISEÑO Y SERVICIOS", "_Toc_Anx_3")
    agregar_tabla_word_proporcionada(
        doc, resultados["df_cotizaciones"], incluir_indice=False, fuente_pt=7.5,
        col_izq_indices=(0, 1, 2, 6), anchos_pulgadas=[0.58, 0.85, 1.67, 0.65, 0.70, 0.70, 1.55]
    )

    add_titulo_seccion("ANEXO 4: SUPUESTOS TÉCNICOS, TRIBUTARIOS Y NORMATIVOS SNI 2026", "_Toc_Anx_4")
    agregar_tabla_word_proporcionada(
        doc, resultados["df_supuestos"], incluir_indice=False, fuente_pt=7.8,
        col_izq_indices=(0, 1, 2, 3), anchos_pulgadas=[1.35, 1.25, 2.55, 1.55]
    )

    doc.save(ruta_word)
    ruta_pdf = os.path.splitext(ruta_word)[0] + ".pdf"
    pdf_ok = exportar_word_a_pdf(ruta_word, ruta_pdf) if generar_pdf else False
    return ruta_word, ruta_pdf, usando_plantilla, pdf_ok

