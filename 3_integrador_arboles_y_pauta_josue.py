# -*- coding: utf-8 -*-
"""
3_integrador_arboles_y_pauta_josue.py — INTEGRADOR VISUAL, MAPA DE LOCALIZACIÓN OSORNO, ÁRBOLES Y MML (VERSIÓN CORREGIDA)
Atiende las observaciones de retroalimentación docente (24 nov 2026):
  - Árbol de Problemas y Objetivos centrados en el residuo (sin forzar productos didácticos en el problema/causas).
  - Sección 1.3 dedicada estrictamente al residuo + justificación de crecimiento (3% conservador) y balance de masa 70%/30%.
  - Alternativas (2.1) derivadas explícitamente de los Medios del Árbol de Objetivos.
  - Mapa de Localización real de Osorno (Eje Eleuterio Ramírez -> Galpón Ovejería) + tabla de Macro/Microlocalización.
  - Matriz de Marco Lógico (11) derivada del Árbol de Objetivos, sin Indicadores/MV/Supuestos en FIN, con presupuesto
    exacto en Indicadores de Actividades y sin Supuestos en Actividades.
  - Numeración correlativa exacta (Figuras 1 a 8) y cifras 100% dinámicas SNI 2026 (TSD 5,5%).
"""

import os
import sys
import zipfile
import subprocess
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _fmt_clp(v):
    v = float(v)
    if v < 0:
        return f"-${abs(int(round(v))):,}".replace(",", ".")
    return f"${int(round(v)):,}".replace(",", ".")


def _fmt_dec(v, d=2):
    return f"{float(v):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _dibujar_caja_redondeada(ax, xc, yc, w, h, texto, facecolor, edgecolor, fontsize=8.3, bold=False, textcolor="#0F172A"):
    box = FancyBboxPatch(
        (xc - w / 2, yc - h / 2), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        facecolor=facecolor, edgecolor=edgecolor, linewidth=1.3
    )
    ax.add_patch(box)
    ax.text(
        xc, yc, texto, ha="center", va="center", fontsize=fontsize,
        fontweight="bold" if bold else "normal", color=textcolor,
        family="Arial", linespacing=1.18
    )


def generar_diagramas_josue(carpeta_destino, resultados_vivos=None, escenarios_sens=None):
    os.makedirs(carpeta_destino, exist_ok=True)
    rutas = {}

    # --------------------------------------------------------------------------
    # FIGURA 1: ÁRBOL DE PROBLEMAS (CENTRADO EN EL RESIDUO — SIN FORZAR PRODUCTOS)
    # --------------------------------------------------------------------------
    r_prob = os.path.join(carpeta_destino, "josue_fig1_arbol_problemas.png")
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=220)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    ax.text(0.5, 0.96, "ÁRBOL DE PROBLEMAS - GESTIÓN DEL CARTÓN COMERCIAL EN OSORNO", ha="center", va="center", fontsize=13.5, fontweight="bold", color="#1E293B", family="Arial")
    ax.text(0.5, 0.92, "Efectos arriba, problema central del residuo al medio y causas raíz abajo.", ha="center", va="center", fontsize=9.3, color="#475569", family="Arial")

    sub_efectos = [
        (0.095, "Acortamiento de la\nvida útil del Vertedero\nde Curaco."),
        (0.245, "Mayor gasto municipal\nen recolección y\ndisposición final."),
        (0.425, "Desperdicio de fibra\ncelulósica limpia\nreutilizable."),
        (0.575, "Menores encadenamientos\nproductivos y empleo\nlocal."),
        (0.755, "Mayor dependencia de\nbienes y embalajes\nconvencionales."),
        (0.905, "Baja cultura práctica\nde economía circular\nen el comercio."),
    ]
    for x_se, txt_se in sub_efectos:
        _dibujar_caja_redondeada(ax, x_se, 0.80, 0.14, 0.12, txt_se, "#F9EBEB", "#78716C", fontsize=7.6)

    efectos_dir = [
        (0.17, "Sobrecarga del relleno sanitario\ny mayores costos municipales."),
        (0.50, "Pérdida de valor económico y\nmaterial recuperable en Osorno."),
        (0.83, "Escasa presencia de iniciativas\nlocales de economía circular."),
    ]
    for x_ef, txt_ef in efectos_dir:
        _dibujar_caja_redondeada(ax, x_ef, 0.63, 0.29, 0.11, txt_ef, "#F2D7D5", "#64748B", fontsize=8.4, bold=True)

    _dibujar_caja_redondeada(
        ax, 0.50, 0.45, 0.62, 0.14,
        "Bajo aprovechamiento local y alta disposición\nen vertedero del cartón corrugado comercial\nrecuperable generado en el eje céntrico\nde Osorno.",
        "#E0ECF8", "#334155", fontsize=9.8, bold=True
    )

    causas_dir = [
        (0.17, "Recolección municipal mixta sin\nsegregación comercial matutina."),
        (0.50, "Baja capacidad local de valorización\ny transformación del cartón."),
        (0.83, "Escasa articulación entre comercios,\ngestores y mercados sustentables."),
    ]
    for x_ca, txt_ca in causas_dir:
        _dibujar_caja_redondeada(ax, x_ca, 0.27, 0.29, 0.11, txt_ca, "#FDEBD0", "#64748B", fontsize=8.3, bold=True)

    sub_causas = [
        (0.095, "Ausencia de convenios\nde retiro selectivo\nen eje comercial."),
        (0.245, "Exposición de cajas a\nhumedad y mezcla en\nla vía pública."),
        (0.425, "Falta de talleres con\nequipamiento industrial\ny control de calidad."),
        (0.575, "Desconocimiento de\nusos alternativos de\nmayor valor agregado."),
        (0.755, "Inexistencia de canales\nde enlace entre oferta\nde residuo y demanda."),
        (0.905, "Falta de trazabilidad\ny registros formales\nbajo Ley REP."),
    ]
    for x_sc, txt_sc in sub_causas:
        _dibujar_caja_redondeada(ax, x_sc, 0.10, 0.14, 0.12, txt_sc, "#FEF5E7", "#78716C", fontsize=7.6)

    c_line = "#64748B"
    for xg, xi, xd in [(0.17, 0.095, 0.245), (0.50, 0.425, 0.575), (0.83, 0.755, 0.905)]:
        ax.plot([xi, xd], [0.715, 0.715], color=c_line, lw=1.3)
        ax.plot([xi, xi], [0.715, 0.74], color=c_line, lw=1.3)
        ax.plot([xd, xd], [0.715, 0.74], color=c_line, lw=1.3)
        ax.plot([xg, xg], [0.685, 0.715], color=c_line, lw=1.3)
        ax.plot([xi, xd], [0.185, 0.185], color=c_line, lw=1.3)
        ax.plot([xi, xi], [0.16, 0.185], color=c_line, lw=1.3)
        ax.plot([xd, xd], [0.16, 0.185], color=c_line, lw=1.3)
        ax.plot([xg, xg], [0.185, 0.215], color=c_line, lw=1.3)
    ax.plot([0.17, 0.83], [0.545, 0.545], color=c_line, lw=1.4)
    for xg in [0.17, 0.50, 0.83]:
        ax.plot([xg, xg], [0.545, 0.575], color=c_line, lw=1.4)
    ax.plot([0.50, 0.50], [0.52, 0.545], color=c_line, lw=1.5)
    ax.plot([0.17, 0.83], [0.355, 0.355], color=c_line, lw=1.4)
    for xg in [0.17, 0.50, 0.83]:
        ax.plot([xg, xg], [0.325, 0.355], color=c_line, lw=1.4)
    ax.plot([0.50, 0.50], [0.355, 0.38], color=c_line, lw=1.5)

    fig.tight_layout(); fig.savefig(r_prob, dpi=220); plt.close(fig)
    rutas["arbol_problemas"] = r_prob

    # --------------------------------------------------------------------------
    # FIGURA 2: ÁRBOL DE OBJETIVOS (ESPEJO POSITIVO EXACTO DEL ÁRBOL DE PROBLEMAS)
    # --------------------------------------------------------------------------
    r_obj = os.path.join(carpeta_destino, "josue_fig2_arbol_objetivos.png")
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=220)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    ax.text(0.5, 0.96, "ÁRBOL DE OBJETIVOS - MEDIOS Y FINES (ESPEJO POSITIVO)", ha="center", va="center", fontsize=13.5, fontweight="bold", color="#1E293B", family="Arial")
    ax.text(0.5, 0.92, "De estos medios surgen las alternativas evaluadas (Sección 2.1) y la Matriz de Marco Lógico (Sección 11).", ha="center", va="center", fontsize=9.3, color="#475569", family="Arial")

    sub_fines = [
        (0.095, "Extensión de la vida\nútil del Vertedero\nProvincial de Curaco."),
        (0.245, "Ahorro municipal en\nrecolección y\ndisposición final."),
        (0.425, "Reincorporación de\nfibra limpia al ciclo\nproductivo."),
        (0.575, "Generación de empleo\nformal y valor\nagregado local."),
        (0.755, "Mayor oferta local de\nbienes sustentables\ncompetitivos."),
        (0.905, "Fortalecimiento de la\neconomía circular\nen Osorno."),
    ]
    for x_sf, txt_sf in sub_fines:
        _dibujar_caja_redondeada(ax, x_sf, 0.80, 0.14, 0.12, txt_sf, "#EAFAF1", "#64748B", fontsize=7.6)

    fines_dir = [
        (0.17, "Menor presión sobre el vertedero\ny ahorro de recursos municipales."),
        (0.50, "Mayor retención de valor económico\ny ambiental en la comuna."),
        (0.83, "Consolidación de soluciones locales\nde economía circular en Osorno."),
    ]
    for x_fi, txt_fi in fines_dir:
        _dibujar_caja_redondeada(ax, x_fi, 0.63, 0.29, 0.11, txt_fi, "#D5F5E3", "#475569", fontsize=8.4, bold=True)

    _dibujar_caja_redondeada(
        ax, 0.50, 0.45, 0.62, 0.14,
        "Aumentar el aprovechamiento local y reducir la\ndisposición en vertedero del cartón corrugado\ncomercial recuperable del eje céntrico\nde Osorno.",
        "#E0ECF8", "#334155", fontsize=9.8, bold=True
    )

    medios_dir = [
        (0.17, "M1: Implementar retiro selectivo\ncomercial en horario matutino."),
        (0.50, "M2: Desarrollar capacidad local de\nvalorización con diseño y calidad."),
        (0.83, "M3: Articular comercios, canales\ndiversificados y trazabilidad REP."),
    ]
    for x_me, txt_me in medios_dir:
        _dibujar_caja_redondeada(ax, x_me, 0.27, 0.29, 0.11, txt_me, "#D6EAF8", "#475569", fontsize=8.3, bold=True)

    sub_medios = [
        (0.095, "Convenios de entrega\ncon comercios del eje\nEleuterio Ramírez."),
        (0.245, "Protocolo de acopio\nseco previo al camión\nmunicipal."),
        (0.425, "Equipamiento industrial\n(troquelado/impresión)\ny control de calidad."),
        (0.575, "Diseño continuo y\nrenovación periódica\nde matrices/productos."),
        (0.755, "Canales diversificados:\nprivados, licitaciones\ny retail local."),
        (0.905, "Convenio con gestor\npara el 30% de retazo\n(trazabilidad REP)."),
    ]
    for x_sm, txt_sm in sub_medios:
        _dibujar_caja_redondeada(ax, x_sm, 0.10, 0.14, 0.12, txt_sm, "#EBF5FB", "#64748B", fontsize=7.6)

    for xg, xi, xd in [(0.17, 0.095, 0.245), (0.50, 0.425, 0.575), (0.83, 0.755, 0.905)]:
        ax.plot([xi, xd], [0.715, 0.715], color=c_line, lw=1.3)
        ax.plot([xi, xi], [0.715, 0.74], color=c_line, lw=1.3)
        ax.plot([xd, xd], [0.715, 0.74], color=c_line, lw=1.3)
        ax.plot([xg, xg], [0.685, 0.715], color=c_line, lw=1.3)
        ax.plot([xi, xd], [0.185, 0.185], color=c_line, lw=1.3)
        ax.plot([xi, xi], [0.16, 0.185], color=c_line, lw=1.3)
        ax.plot([xd, xd], [0.16, 0.185], color=c_line, lw=1.3)
        ax.plot([xg, xg], [0.185, 0.215], color=c_line, lw=1.3)
    ax.plot([0.17, 0.83], [0.545, 0.545], color=c_line, lw=1.4)
    for xg in [0.17, 0.50, 0.83]:
        ax.plot([xg, xg], [0.545, 0.575], color=c_line, lw=1.4)
    ax.plot([0.50, 0.50], [0.52, 0.545], color=c_line, lw=1.5)
    ax.plot([0.17, 0.83], [0.355, 0.355], color=c_line, lw=1.4)
    for xg in [0.17, 0.50, 0.83]:
        ax.plot([xg, xg], [0.325, 0.355], color=c_line, lw=1.4)
    ax.plot([0.50, 0.50], [0.355, 0.38], color=c_line, lw=1.5)

    fig.tight_layout(); fig.savefig(r_obj, dpi=220); plt.close(fig)
    rutas["arbol_objetivos"] = r_obj

    # --------------------------------------------------------------------------
    # FIGURA 3: OFERTA DE RESIDUO VS. DEMANDA DE FIBRA Y FRACCIÓN RESIDUAL
    # --------------------------------------------------------------------------
    r_bal = os.path.join(carpeta_destino, "josue_fig3_balance_carton.png")
    fig, ax = plt.subplots(figsize=(9.2, 4.1), dpi=220)
    if resultados_vivos is not None and "df_cantidades" in resultados_vivos:
        df_c_v = resultados_vivos["df_cantidades"]
        anios = list(df_c_v.columns)
        rec = [float(x) for x in df_c_v.loc["Residuo de Cartón Recolectado (Toneladas)"].values]
        inc = [float(x) for x in df_c_v.loc["Cartón Efectivamente Incorporado (Toneladas)"].values]
    else:
        anios = [f"Año {i}" for i in range(1, 11)]
        rec = [round(15.0 * (1.03 ** i), 2) for i in range(10)]
        inc = [round(10.5 * (1.03 ** i), 2) for i in range(10)]

    n_a3 = len(anios)
    ax.plot(anios, rec, marker="o", lw=2.3, color="#1D4ED8", label="Oferta de cartón recuperable (6 locales + expansión conservadora)")
    ax.plot(anios, inc, marker="s", lw=2.3, color="#059669", label="Demanda de fibra incorporada en productos (70%)")
    ax.fill_between(range(n_a3), inc, rec, color="#BFDBFE", alpha=0.38, label="Fracción residual trazable (30%: 12% selección + 18% retazo a reciclador)")

    y_min3 = max(0.0, min(inc) * 0.70)
    y_max3 = max(rec) * 1.20
    dy3 = max((y_max3 - y_min3) * 0.03, 0.25)
    for i in range(n_a3):
        ax.text(i, rec[i] + dy3, f"{rec[i]:.1f} t".replace(".", ","), ha="center", va="bottom", fontsize=7.8, family="Arial", color="#1E3A8A", fontweight="bold")
        ax.text(i, inc[i] - dy3 * 1.4, f"{inc[i]:.1f} t".replace(".", ","), ha="center", va="top", fontsize=7.8, family="Arial", color="#065F46", fontweight="bold")

    ax.set_ylim(y_min3, y_max3)
    ax.set_ylabel("Toneladas / año", fontsize=9, fontweight="bold", family="Arial")
    ax.set_title("Oferta de Residuo Recuperable vs. Demanda de Fibra para Producción (Años 1 al 10)", fontsize=10.5, fontweight="bold", family="Arial")
    ax.grid(True, linestyle="--", alpha=0.45)
    ax.legend(loc="upper left", fontsize=8.0)
    fig.tight_layout(); fig.savefig(r_bal, dpi=220); plt.close(fig)
    rutas["balance_carton"] = r_bal

    # --------------------------------------------------------------------------
    # FIGURA 4: MAPA DE LOCALIZACIÓN REAL EN OSORNO (COMENTARIO #19)
    # --------------------------------------------------------------------------
    r_map = os.path.join(carpeta_destino, "josue_fig4_mapa_osorno.png")
    fig, ax = plt.subplots(figsize=(9.5, 4.9), dpi=220)
    ax.set_facecolor("#F8FAFC")

    # Coordenadas reales aproximadas de Osorno (Longitud Oeste, Latitud Sur)
    # Río Rahue (trazo referencial N-S al oeste del centro)
    rio_lon = [-73.1495, -73.1475, -73.1458, -73.1440, -73.1432, -73.1445]
    rio_lat = [-40.5640, -40.5700, -40.5760, -40.5830, -40.5910, -40.6000]
    ax.plot(rio_lon, rio_lat, color="#38BDF8", lw=7.0, alpha=0.55, solid_capstyle="round", label="Río Rahue (referencia geográfica)")

    # Ruta 5 Sur (trazo referencial al este)
    r5_lon = [-73.1060, -73.1070, -73.1095, -73.1120]
    r5_lat = [-40.5640, -40.5760, -40.5880, -40.6000]
    ax.plot(r5_lon, r5_lat, color="#94A3B8", lw=2.8, ls="--", label="Ruta 5 Sur (acceso macro)")

    # 6 Locales reales en Calle Eleuterio Ramírez (#446 al #1024)
    locales_geo = [
        ("L1 Lynch (446)",        -73.1422, -40.5742, (-12, 10)),
        ("L2 Autoplanet (582)",   -73.1396, -40.5744, (-10, -16)),
        ("L3 La Malagueña (625)", -73.1382, -40.5745, (2, 12)),
        ("L4 El Sabrosón (647)",  -73.1368, -40.5746, (4, -15)),
        ("L5 Centrosorno (977)",  -73.1322, -40.5748, (-6, 12)),
        ("L6 Liquimax (1024)",    -73.1302, -40.5749, (6, -14)),
    ]
    lons_l = [p[1] for p in locales_geo]
    lats_l = [p[2] for p in locales_geo]
    ax.plot(lons_l, lats_l, color="#1D4ED8", lw=2.6, zorder=3, label="Eje Comercial Eleuterio Ramírez (6 locales)")
    ax.scatter(lons_l, lats_l, s=68, color="#1D4ED8", edgecolors="#FFFFFF", linewidths=1.4, zorder=4)
    for nom_l, lo, la, off in locales_geo:
        ax.annotate(nom_l, (lo, la), xytext=off, textcoords="offset points", fontsize=7.6, fontweight="bold", color="#1E3A8A",
                    bbox=dict(boxstyle="round,pad=0.18", fc="#EFF6FF", ec="#93C5FD", lw=0.7))

    # Sector Industrial Ovejería (Galpón 140 m2)
    galp_lon, galp_lat = -73.1398, -40.5948
    # Ruta matutina del furgón (Eje Ramírez -> Puente San Pedro / Av. República -> Ovejería)
    ruta_lon = [-73.1302, -73.1325, -73.1365, -73.1398]
    ruta_lat = [-40.5749, -40.5815, -40.5885, -40.5948]
    ax.plot(ruta_lon, ruta_lat, color="#EA580C", lw=2.3, ls="-.", zorder=3, label="Ruta matutina furgón (~3,2 km · 10 min)")
    ax.annotate("", xy=(galp_lon, galp_lat + 0.0012), xytext=(-73.1375, -40.5905), arrowprops=dict(arrowstyle="->", color="#EA580C", lw=2.2))

    ax.scatter([galp_lon], [galp_lat], s=190, marker="s", color="#15803D", edgecolors="#0F172A", linewidths=1.5, zorder=5, label="Planta Taller 140 m2 (Sector Industrial Ovejería)")
    ax.annotate(
        "GALPÓN TALLER (140 m2)\nSector Industrial Ovejería\n(-40,5948° S; -73,1398° O)",
        (galp_lon, galp_lat), xytext=(14, -6), textcoords="offset points",
        fontsize=8.2, fontweight="bold", color="#14532D",
        bbox=dict(boxstyle="round,pad=0.3", fc="#DCFCE7", ec="#15803D", lw=1.1)
    )

    ax.text(-73.1465, -40.5810, "Río\nRahue", fontsize=8, fontweight="bold", color="#0369A1", ha="center")
    ax.text(-73.1118, -40.5700, "Ruta 5 Sur", fontsize=8, fontweight="bold", color="#475569", rotation=-80)
    ax.text(-73.1355, -40.5678, "CENTRO URBANO OSORNO", fontsize=8.8, fontweight="bold", color="#334155", ha="center")

    ax.set_xlim(-73.153, -73.102)
    ax.set_ylim(-40.601, -40.564)
    ax.set_xlabel("Longitud Oeste (WGS84)", fontsize=8.5, fontweight="bold", family="Arial")
    ax.set_ylabel("Latitud Sur (WGS84)", fontsize=8.5, fontweight="bold", family="Arial")
    ax.set_title("Mapa de Macro y Microlocalización — Eje Eleuterio Ramírez y Planta en Ovejería (Osorno)", fontsize=10.5, fontweight="bold", family="Arial", pad=10)
    ax.grid(True, linestyle=":", alpha=0.5, color="#CBD5E1")
    ax.legend(loc="lower left", fontsize=7.6, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1")
    fig.tight_layout(); fig.savefig(r_map, dpi=220); plt.close(fig)
    rutas["mapa_localizacion"] = r_map

    # --------------------------------------------------------------------------
    # FIGURA 5: CROQUIS CONCEPTUAL GALPÓN 140 M2 (Ovejería)
    # --------------------------------------------------------------------------
    r_croq = os.path.join(carpeta_destino, "josue_fig5_croquis_galpon.png")
    fig, ax = plt.subplots(figsize=(9.0, 4.6), dpi=220)
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.text(5.0, 5.7, "Croquis conceptual de distribución - Galpón 140 m2 en Ovejería (Osorno)", ha="center", va="center", fontsize=11.5, fontweight="bold", color="#000000", family="Arial")
    ax.plot([0.2, 9.8, 9.8, 0.2, 0.2], [0.3, 0.3, 5.3, 5.3, 0.3], color="#1E3A8A", lw=1.8)
    ax.plot([0.2, 9.8], [2.9, 2.9], color="#1E3A8A", lw=1.6)
    ax.plot([3.1, 3.1], [2.9, 5.3], color="#1E3A8A", lw=1.5)
    ax.plot([6.5, 6.5], [2.9, 5.3], color="#1E3A8A", lw=1.5)
    ax.plot([3.7, 3.7], [0.3, 2.9], color="#1E3A8A", lw=1.5)
    ax.plot([6.5, 6.5], [0.3, 2.9], color="#1E3A8A", lw=1.5)
    ax.annotate("", xy=(9.3, 4.95), xytext=(2.1, 4.95), arrowprops=dict(arrowstyle="->", lw=2.0, color="#000000"))
    ax.text(1.3, 4.95, "Flujo material", ha="center", va="center", fontsize=9.8, fontweight="bold", family="Arial")
    for xz, yz, tz in [
        (1.65, 3.9, "Recepción, clasificación\ny acopio seco (35 m2)"),
        (4.80, 4.0, "Corte, troquelado\ny matrices (40 m2)"),
        (8.15, 4.0, "Impresión EN-71,\nbarniz y secado (30 m2)"),
        (1.95, 1.6, "Armado y control\nde calidad (20 m2)"),
        (5.10, 1.6, "Producto terminado\ny despacho (10 m2)"),
        (8.15, 1.6, "Oficina, servicios y\nsegregación 30% (5 m2)"),
    ]:
        ax.text(xz, yz, tz, ha="center", va="center", fontsize=9.4, family="Arial", color="#000000")
    fig.tight_layout(); fig.savefig(r_croq, dpi=220); plt.close(fig)
    rutas["croquis_galpon"] = r_croq

    # --------------------------------------------------------------------------
    # FIGURA 6: FLUJO PRODUCTIVO DE 7 ETAPAS (CON DISEÑO Y CONTROL DE CALIDAD)
    # --------------------------------------------------------------------------
    r_proc = os.path.join(carpeta_destino, "josue_fig6_flujo_proceso.png")
    fig, ax = plt.subplots(figsize=(11.0, 2.5), dpi=220)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    etapas = [
        "1. Retiro\nselectivo\n05:30-06:15",
        "2. Recepción\ny descarte\n(12% merma)",
        "3. Diseño y\nmatrices\nactualizadas",
        "4. Corte y\ntroquelado\n(18% retazo)",
        "5. Impresión\nEN-71 y\nbarnizado",
        "6. Armado y\ncontrol de\ncalidad",
        "7. Empaque\ny despacho\nmulticanal",
    ]
    n_et = len(etapas); w_et = 0.125; esp = (0.96 - n_et * w_et) / (n_et - 1)
    for i, et_txt in enumerate(etapas):
        xc = 0.02 + w_et / 2 + i * (w_et + esp)
        _dibujar_caja_redondeada(ax, xc, 0.58, w_et, 0.50, et_txt, "#EBF5FB", "#1E3A8A", fontsize=8.0, bold=True)
        if i < n_et - 1:
            ax.annotate("", xy=(xc + w_et / 2 + esp, 0.58), xytext=(xc + w_et / 2, 0.58), arrowprops=dict(arrowstyle="->", lw=1.7, color="#000000"))
    ax.text(0.5, 0.12, "Fracción residual (30% = 12% selección + 18% retazo de troquelado): compactada y entregada a reciclador autorizado (Ley REP N° 20.920).",
            ha="center", va="center", fontsize=8.6, style="italic", color="#000000", family="Arial")
    fig.tight_layout(); fig.savefig(r_proc, dpi=220); plt.close(fig)
    rutas["flujo_proceso"] = r_proc

    # --------------------------------------------------------------------------
    # FIGURA 7: FLUJOS COMPARADOS PRIVADO VS. SOCIAL SNI 2026 (100% DINÁMICO)
    # --------------------------------------------------------------------------
    r_flujos = os.path.join(carpeta_destino, "josue_fig7_flujos_comparados.png")
    fig, ax = plt.subplots(figsize=(9.5, 4.1), dpi=220)
    df_fp_v = resultados_vivos["df_flujo_privado"]
    df_fs_v = resultados_vivos["df_flujo_social"]
    etiquetas_f = list(df_fp_v.columns)
    f_priv = [round(float(v) / 1e6, 2) for v in df_fp_v.loc["(=) FLUJO DE CAJA PRIVADO NETO"].values]
    f_soc = [round(float(v) / 1e6, 2) for v in df_fs_v.loc["(=) FLUJO DE BENEFICIOS SOCIALES NETOS"].values]

    x_pos = range(len(etiquetas_f)); w_b = 0.36
    ax.bar([p - w_b / 2 for p in x_pos], f_priv, width=w_b, label="Flujo de caja privado neto (MM$)", color="#1D4ED8")
    ax.bar([p + w_b / 2 for p in x_pos], f_soc, width=w_b, label="Flujo social SNI 2026 (MM$)", color="#059669")
    ax.axhline(0, color="#334155", lw=1.0)
    y_min6 = min(min(f_priv), min(f_soc), 0.0) * 1.25 - 2.0
    y_max6 = max(max(f_priv), max(f_soc), 1.0) * 1.20 + 2.0
    off6 = max((y_max6 - y_min6) * 0.016, 0.5)
    for i in range(len(etiquetas_f)):
        ax.text(i - w_b / 2, f_priv[i] + (off6 if f_priv[i] >= 0 else -off6), f"{f_priv[i]:.1f}".replace(".", ","), ha="center", va="bottom" if f_priv[i] >= 0 else "top", fontsize=7.0, family="Arial")
        ax.text(i + w_b / 2, f_soc[i] + (off6 if f_soc[i] >= 0 else -off6), f"{f_soc[i]:.1f}".replace(".", ","), ha="center", va="bottom" if f_soc[i] >= 0 else "top", fontsize=7.0, family="Arial")
    ax.set_xticks(list(x_pos)); ax.set_xticklabels(etiquetas_f, fontsize=8.5, family="Arial")
    ax.set_ylim(y_min6, y_max6)
    ax.set_ylabel("Millones de pesos (CLP)", fontsize=9, fontweight="bold", family="Arial")
    ax.set_title("Comparación Anual: Flujo de Caja Privado vs. Flujo Social SNI 2026", fontsize=10.5, fontweight="bold", family="Arial")
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    ax.legend(loc="upper left", fontsize=8.4)
    fig.tight_layout(); fig.savefig(r_flujos, dpi=220); plt.close(fig)
    rutas["flujos_comparados"] = r_flujos

    # --------------------------------------------------------------------------
    # FIGURA 8: ANÁLISIS DE SENSIBILIDAD MULTIESCENARIO (100% DINÁMICO)
    # --------------------------------------------------------------------------
    r_sens = os.path.join(carpeta_destino, "josue_fig8_sensibilidad.png")
    fig, ax = plt.subplots(figsize=(8.8, 3.9), dpi=220)
    cfg_v = resultados_vivos["cfg"]
    tp_lbl = _fmt_dec(float(cfg_v["TASA_DESCUENTO_PRIVADA"]) * 100, 1)
    ts_lbl = _fmt_dec(float(cfg_v["TASA_DESCUENTO_SOCIAL"]) * 100, 1)
    crec_lbl = _fmt_dec(float(cfg_v["TASA_CRECIMIENTO"]) * 100, 1)

    escenarios = [
        "Pesimista: -15% precios/ing.",
        "Alza de costos: +10%",
        f"Caso base: +{crec_lbl}% anual",
        "Sin crecimiento: 0% anual",
    ]
    van_p = [round(float(e["van_p"]) / 1e6, 2) for e in escenarios_sens]
    van_s = [round(float(e["van_s"]) / 1e6, 2) for e in escenarios_sens]

    y = range(len(escenarios)); h_bar = 0.35
    ax.barh([i - h_bar / 2 for i in y], van_p, height=h_bar, label=f"VAN privado ({tp_lbl}%)", color="#1D4ED8", edgecolor="#000000", linewidth=0.5)
    ax.barh([i + h_bar / 2 for i in y], van_s, height=h_bar, label=f"VANS social ({ts_lbl}%)", color="#EA580C", edgecolor="#000000", linewidth=0.5)
    ax.axvline(0, color="#0F172A", lw=1.0)
    ax.set_yticks(list(y)); ax.set_yticklabels(escenarios, fontsize=8.8, family="Arial")
    ax.set_xlabel("Valor Actual Neto (MM$ CLP)", fontsize=9, fontweight="bold", family="Arial")
    ax.set_title(f"Análisis de Sensibilidad - VAN Privado ({tp_lbl}%) y VANS Social ({ts_lbl}% SNI 2026)", fontsize=10.2, fontweight="bold", family="Arial", pad=8)
    ax.grid(axis="x", linestyle="--", alpha=0.45)
    ax.legend(loc="lower right", fontsize=8.2)
    fig.tight_layout(); fig.savefig(r_sens, dpi=220); plt.close(fig)
    rutas["sensibilidad"] = r_sens

    return rutas


# ==============================================================================
# UTILIDADES WORD
# ==============================================================================

def _estilizar_run_arial(run, size_pt=10.5, bold=False, italic=False, color_rgb=(0, 0, 0)):
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
    for attr in ("ascii", "hAnsi", "cs"):
        rFonts.set(qn(f"w:{attr}"), "Arial")
    if rPr.find(qn("w:noProof")) is None:
        rPr.append(OxmlElement("w:noProof"))


def _sombrear_celda(celda, color_hex):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)
    celda._tc.get_or_add_tcPr().append(shd)


def _bordes_celda(celda, es_destacada=False):
    tcPr = celda._tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement("w:tcBorders")
        tcPr.append(tcBorders)
    for edge in ["top", "bottom", "left", "right"]:
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6" if es_destacada else "4")
        el.set(qn("w:color"), "000000" if es_destacada else "64748B")
        tcBorders.append(el)


def _crear_tabla_en_doc(doc, df, anchos_pulgadas, fuente_pt=7.8):
    filas, cols = df.shape
    tabla = doc.add_table(rows=filas + 1, cols=cols)
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabla.autofit = False
    trPr_h = tabla.rows[0]._tr.get_or_add_trPr()
    trPr_h.append(OxmlElement("w:tblHeader"))
    trPr_h.append(OxmlElement("w:cantSplit"))

    for c_idx, col_nom in enumerate(df.columns):
        cell = tabla.rows[0].cells[c_idx]
        cell.width = Inches(anchos_pulgadas[c_idx])
        _sombrear_celda(cell, "D9E2F3")
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(2.5), Pt(2.5)
        _estilizar_run_arial(p.add_run(str(col_nom)), size_pt=fuente_pt, bold=True, color_rgb=(0, 0, 0))
        _bordes_celda(cell, es_destacada=True)

    for r_idx in range(filas):
        row = tabla.rows[r_idx + 1]
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for c_idx in range(cols):
            cell = row.cells[c_idx]
            cell.width = Inches(anchos_pulgadas[c_idx])
            _sombrear_celda(cell, "FFFFFF")
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(2), Pt(2)
            _estilizar_run_arial(p.add_run(str(df.iloc[r_idx, c_idx])), size_pt=fuente_pt, bold=(c_idx == 0), color_rgb=(0, 0, 0))
            _bordes_celda(cell, es_destacada=False)
    return tabla


def _insertar_antes(p_ref, elem):
    p_ref._p.addprevious(elem)


def _crear_parrafo_flotante(doc, texto="", size_pt=10.5, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=5, anchor_name=None, bm_id=900, outline_lvl=0):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(space_before), Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold:
        p.paragraph_format.keep_with_next = True
    if texto:
        _estilizar_run_arial(p.add_run(texto), size_pt=size_pt, bold=bold, italic=italic)
    if anchor_name:
        pPr = p._p.get_or_add_pPr()
        ol = OxmlElement("w:outlineLvl")
        ol.set(qn("w:val"), str(outline_lvl))
        pPr.append(ol)
        bm_s = OxmlElement("w:bookmarkStart"); bm_s.set(qn("w:id"), str(bm_id)); bm_s.set(qn("w:name"), anchor_name)
        bm_e = OxmlElement("w:bookmarkEnd"); bm_e.set(qn("w:id"), str(bm_id))
        p._p.insert(0, bm_s); p._p.append(bm_e)
    return p


def _crear_parrafo_imagen(doc, ruta_img, ancho_pulgadas=6.2, leyenda=None):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before, p_img.paragraph_format.space_after = Pt(4), Pt(2)
    p_img.add_run().add_picture(ruta_img, width=Inches(ancho_pulgadas))
    els = [p_img._p]
    if leyenda:
        p_ley = doc.add_paragraph()
        p_ley.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_ley.paragraph_format.space_before, p_ley.paragraph_format.space_after = Pt(1), Pt(6)
        _estilizar_run_arial(p_ley.add_run(leyenda), size_pt=8.5, italic=True)
        els.append(p_ley._p)
    return els


def _es_parrafo_de_toc(p):
    return len(p._p.findall(qn("w:hyperlink"))) > 0 or len(p._p.findall(qn("w:fldSimple"))) > 0


def _crear_linea_toc_xml(doc, texto_sec, anchor_name, pag_default="10", nivel=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3.5 if nivel == 1 else 1.5)
    p.paragraph_format.space_after = Pt(3.5 if nivel == 1 else 1.5)
    p.paragraph_format.left_indent = Inches(0.0 if nivel == 1 else 0.25)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.65), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

    hl = OxmlElement("w:hyperlink"); hl.set(qn("w:anchor"), anchor_name); hl.set(qn("w:history"), "1")
    def mk_r(txt, bold=True, pt=10):
        r_el = OxmlElement("w:r"); rPr = OxmlElement("w:rPr"); rF = OxmlElement("w:rFonts")
        for attr in ("ascii", "hAnsi", "cs"): rF.set(qn(f"w:{attr}"), "Arial")
        rPr.append(rF); rPr.append(OxmlElement("w:noProof"))
        if bold: rPr.append(OxmlElement("w:b")); rPr.append(OxmlElement("w:bCs"))
        c_el = OxmlElement("w:color"); c_el.set(qn("w:val"), "000000"); rPr.append(c_el)
        sz = OxmlElement("w:sz"); sz.set(qn("w:val"), str(int(pt * 2))); rPr.append(sz)
        szC = OxmlElement("w:szCs"); szC.set(qn("w:val"), str(int(pt * 2))); rPr.append(szC)
        r_el.append(rPr); t_el = OxmlElement("w:t"); t_el.text = txt; r_el.append(t_el)
        return r_el
    hl.append(mk_r(texto_sec, bold=(nivel == 1), pt=10 if nivel == 1 else 9.5))
    rt = OxmlElement("w:r"); rt.append(OxmlElement("w:tab")); hl.append(rt)
    hl.append(mk_r(f"Pág. {pag_default}", bold=True, pt=10 if nivel == 1 else 9.5))
    p._p.append(hl)
    return p


def _actualizar_indice_p2(doc):
    p_toc_sec2 = p_toc_sec3 = p_toc_sec4 = p_toc_sec9 = p_toc_anx1 = None
    for p in doc.paragraphs:
        if not _es_parrafo_de_toc(p):
            continue
        t = p.text.strip().upper()
        if t.startswith("2. ESTUDIO DE MERCADO") and p_toc_sec2 is None: p_toc_sec2 = p
        elif t.startswith("3. CONFIGURACIÓN DEL TALLER") and p_toc_sec3 is None: p_toc_sec3 = p
        elif t.startswith("4. DOTACIÓN DE PERSONAL") and p_toc_sec4 is None: p_toc_sec4 = p
        elif t.startswith("9. CONCLUSIONES") and p_toc_sec9 is None: p_toc_sec9 = p
        elif t.startswith("ANEXO 1:") and p_toc_anx1 is None: p_toc_anx1 = p

    if p_toc_sec2 is not None:
        _insertar_antes(p_toc_sec2, _crear_linea_toc_xml(doc, "1.2 Árbol de Problemas y Árbol de Objetivos (Enfoque Residuo)", "_Toc_Sub_12", "5", 2)._p)
        _insertar_antes(p_toc_sec2, _crear_linea_toc_xml(doc, "1.3 Diagnóstico Integral del Residuo: Áreas, Oferta y Demanda de Fibra", "_Toc_Sub_13", "6", 2)._p)
    if p_toc_sec3 is not None:
        _insertar_antes(p_toc_sec3, _crear_linea_toc_xml(doc, "2.4 Evaluación y Selección de Alternativas (A partir del Árbol de Objetivos)", "_Toc_Sub_24", "9", 2)._p)
    if p_toc_sec4 is not None:
        _insertar_antes(p_toc_sec4, _crear_linea_toc_xml(doc, "3.1 Macro y Microlocalización (Mapa Osorno), Croquis 140 m2 y Normativa", "_Toc_Sub_31", "11", 2)._p)
    if p_toc_sec9 is not None:
        _insertar_antes(p_toc_sec9, _crear_linea_toc_xml(doc, "8.2 Comparación Gráfica Privado vs. Social SNI 2026", "_Toc_Sub_82", "18", 2)._p)
        _insertar_antes(p_toc_sec9, _crear_linea_toc_xml(doc, "8.3 Análisis de Sensibilidad Multiescenario", "_Toc_Sub_83", "18", 2)._p)
    if p_toc_anx1 is not None:
        _insertar_antes(p_toc_anx1, _crear_linea_toc_xml(doc, "10. MODELO DE GESTIÓN ESTRATÉGICA - BUSINESS MODEL CANVAS", "_Toc_Canvas", "20", 1)._p)
        _insertar_antes(p_toc_anx1, _crear_linea_toc_xml(doc, "11. MODELO DE SEGUIMIENTO - MATRIZ DE MARCO LÓGICO", "_Toc_MML", "21", 1)._p)


# ==============================================================================
# INTEGRADOR PRINCIPAL EN EL CUERPO DEL WORD
# ==============================================================================

def integrar_trabajo_josue_en_word(ruta_word, carpeta_entrega, resultados_vivos=None, escenarios_sens=None):
    if not os.path.exists(ruta_word):
        raise FileNotFoundError(f"No se encontró '{ruta_word}'.")

    rutas_img = generar_diagramas_josue(carpeta_entrega, resultados_vivos=resultados_vivos, escenarios_sens=escenarios_sens)
    doc = Document(ruta_word)

    cfg = resultados_vivos["cfg"]
    m = resultados_vivos["metricas"]
    tp_s = _fmt_dec(float(cfg["TASA_DESCUENTO_PRIVADA"]) * 100, 1)
    ts_s = _fmt_dec(float(cfg["TASA_DESCUENTO_SOCIAL"]) * 100, 1)
    crec_s = _fmt_dec(float(cfg["TASA_CRECIMIENTO"]) * 100, 1)

    p_sec2 = p_sec3 = p_sec4 = p_sec9 = p_anx1 = None
    for p in doc.paragraphs:
        if _es_parrafo_de_toc(p):
            continue
        t = p.text.strip().upper()
        if t.startswith("2. ESTUDIO DE MERCADO"): p_sec2 = p
        elif t.startswith("3. CONFIGURACIÓN DEL TALLER"): p_sec3 = p
        elif t.startswith("4. DOTACIÓN DE PERSONAL"): p_sec4 = p
        elif t.startswith("9. CONCLUSIONES PRINCIPALES"): p_sec9 = p
        elif t.startswith("ANEXO 1:"): p_anx1 = p

    # A) SECCIONES 1.2 (ÁRBOLES CORREGIDOS SIN PRODUCTOS EN CAUSAS) Y 1.3 (ESTRICTAMENTE RESIDUO)
    if p_sec2 is not None:
        p_12 = _crear_parrafo_flotante(doc, "1.2 Árbol de Problemas y Árbol de Objetivos (Enfoque Residuo)", size_pt=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=4, anchor_name="_Toc_Sub_12", bm_id=902, outline_lvl=1)
        p_12_txt = _crear_parrafo_flotante(
            doc,
            "Siguiendo la metodología del Marco Lógico (CEPAL N° 39), el problema central se define estrictamente en torno al residuo y no a la ausencia de una solución específica: «Bajo aprovechamiento local y alta disposición en vertedero del cartón corrugado comercial recuperable generado en el eje céntrico de Osorno». Las causas y efectos directos se sintetizan a continuación y se grafican en las Figuras 1 y 2:"
        )
        df_ce = pd.DataFrame([
            ["Causa 1", "Recolección municipal mixta sin segregación comercial matutina.", "Los 6 comercios de Eleuterio Ramírez sacan cajas a la vereda sin convenio de retiro selectivo previo al camión municipal."],
            ["Causa 2", "Baja capacidad local de valorización y transformación del cartón.", "Faltan talleres locales con equipamiento industrial y control de calidad que aprovechen fibra limpia en la misma comuna."],
            ["Causa 3", "Escasa articulación entre comercios, gestores y mercados sustentables.", "No existe trazabilidad formal bajo Ley REP ni canales que conecten la oferta de cartón con demandas locales."],
            ["Efecto 1", "Sobrecarga del Vertedero Provincial de Curaco y mayor gasto municipal.", "Cada tonelada enterrada acorta la vida útil del relleno e implica $48.000 c/IVA en recolección y disposición."],
            ["Efecto 2", "Pérdida de valor económico y material valorizable en Osorno.", "Fibra celulósica limpia se entierra en vez de generar empleo local y encadenamientos productivos."],
            ["Efecto 3", "Escasa presencia de soluciones locales de economía circular.", "Persiste la dependencia de productos convencionales externos con menor cultura práctica de valorización."],
        ], columns=["Elemento", "Diagnóstico Causal del Residuo", "Evidencia Territorial en Osorno"])
        t_ce = _crear_tabla_en_doc(doc, df_ce, [0.95, 2.35, 3.40], fuente_pt=7.7)
        els_fig1 = _crear_parrafo_imagen(doc, rutas_img["arbol_problemas"], ancho_pulgadas=6.4, leyenda="Figura 1. Árbol de problemas centrado en el bajo aprovechamiento del cartón comercial en Osorno. Fuente: Elaboración propia.")
        els_fig2 = _crear_parrafo_imagen(doc, rutas_img["arbol_objetivos"], ancho_pulgadas=6.4, leyenda="Figura 2. Árbol de objetivos (medios y fines) derivado como espejo positivo del Árbol de Problemas. Fuente: Elaboración propia.")

        p_13 = _crear_parrafo_flotante(doc, "1.3 Diagnóstico Integral del Residuo: Áreas, Oferta y Demanda de Fibra", size_pt=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=4, anchor_name="_Toc_Sub_13", bm_id=903, outline_lvl=1)
        p_13_txt = _crear_parrafo_flotante(
            doc,
            f"Este apartado delimita exclusivamente el diagnóstico del residuo (cartón corrugado comercial seco y limpio; la demanda de juegos se desarrolla en la Sección 2). La tasa de crecimiento proyectada de {crec_s}% anual se fundamenta en un criterio conservador acorde a la evolución del comercio/PIB regional de Los Lagos (Banco Central de Chile) y la adhesión progresiva de 1 a 2 comercios vecinos por año (evaluándose además el escenario de 0% crecimiento en Sensibilidad):"
        )
        df_residuo = pd.DataFrame([
            ["Caracterización del residuo", "Cartón corrugado comercial (embalajes secos de ferretería, repuestos, calzado, abarrotes y mayoristas)."],
            ["Área de estudio del residuo", "Zona urbana de la comuna de Osorno (casco céntrico comercial y zona industrial Ovejería)."],
            ["Área de influencia inicial", "Tramo comercial calle Eleuterio Ramírez (#446 al #1024) y ruta matutina hacia galpón en Ovejería (3,2 km)."],
            ["Población generadora referencia / objetivo", "Comercios minoristas y mayoristas del centro de Osorno / 6 locales piloto catastrados en E. Ramírez (50 kg/día = 15,00 t/año)."],
            ["Oferta vs. Demanda de fibra y brecha", "Oferta inicial: 15,00 t/año actualmente enviadas a vertedero (0% valorización local en el tramo). Demanda de fibra del taller: 10,50 t/año netas (70%) + 4,50 t/año de fracción residual (30%) derivadas a reciclador autorizado (Ley REP)."],
        ], columns=["Dimensión del Residuo", "Definición Técnica Aplicada en Osorno"])
        t_res = _crear_tabla_en_doc(doc, df_residuo, [2.25, 4.45], fuente_pt=7.7)
        els_fig3 = _crear_parrafo_imagen(doc, rutas_img["balance_carton"], ancho_pulgadas=6.2, leyenda="Figura 3. Oferta de cartón comercial recuperable frente a demanda de fibra incorporada (70%) y fracción residual trazable (30%). Fuente: Elaboración propia.")

        for el in [p_12._p, p_12_txt._p, t_ce._tbl] + els_fig1 + els_fig2 + [p_13._p, p_13_txt._p, t_res._tbl] + els_fig3:
            _insertar_antes(p_sec2, el)

    # B) SECCIÓN 2.4: EVALUACIÓN DE ALTERNATIVAS A PARTIR DEL ÁRBOL DE OBJETIVOS (COMENTARIO #14)
    if p_sec3 is not None:
        p_24 = _crear_parrafo_flotante(doc, "2.4 Evaluación y Selección de Alternativas (A partir del Árbol de Objetivos)", size_pt=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=4, anchor_name="_Toc_Sub_24", bm_id=904, outline_lvl=1)
        p_24_txt = _crear_parrafo_flotante(
            doc,
            "Las alternativas de solución se construyen combinando los tres Medios Directos identificados en el Árbol de Objetivos (M1: Retiro selectivo matutino; M2: Capacidad local de valorización con diseño y calidad; M3: Articulación comercial diversificada y trazabilidad REP). La Tabla 2.5 compara las cuatro configuraciones:"
        )
        df_alt = pd.DataFrame([
            ["Alt. A: Acopio y reciclaje convencional", "Solo M1 + M3 (parcial)", "Acopio, enfardado y venta del cartón a recicladores mayoristas.", "Baja inversión inicial, pero mínimo margen y escasa retención de valor local. Se integra como complemento para el 30% de recortes."],
            ["Alt. B: Talleres manuales comunitarios", "M1 + M2 artesanal", "Uso de cajas en talleres escolares/vecinales sin industrialización.", "Bajo costo de partida, pero sin estandarización ni calidad visual/funcional sostenible."],
            ["Alt. C: Manufactura local integrada con diseño (Seleccionada)", "M1 + M2 industrial + M3 completo", "Troquelado industrial de sets escolares y kits adulto mayor con asesoría de diseño continuo, canales diversificados y trazabilidad del 30% de recortes.", "Maximiza el valor agregado y empleo local, garantiza calidad EN-71 / D.S. 114 y es financieramente viable sin depender de un solo comprador."],
            ["Alt. D: Desfibrado industrial de pulpa", "M1 + M2 alta escala", "Planta de reciclaje húmedo para fabricar nuevo cartón industrial.", "Requiere CAPEX, consumo hídrico/energético y volumen de residuos muy superiores a la escala de Osorno."],
        ], columns=["Alternativa", "Medios Árbol de Objetivos", "Descripción Técnica", "Evaluación y Selección"])
        t_alt = _crear_tabla_en_doc(doc, df_alt, [1.35, 1.15, 1.95, 2.25], fuente_pt=7.6)
        for el in [p_24._p, p_24_txt._p, t_alt._tbl]:
            _insertar_antes(p_sec3, el)

    # C) SECCIÓN 3.1: LOCALIZACIÓN + MAPA OSORNO + CROQUIS + FLUJO + NORMATIVA (COMENTARIO #19)
    if p_sec4 is not None:
        p_31 = _crear_parrafo_flotante(doc, "3.1 Macro y Microlocalización (Mapa Osorno), Croquis 140 m2 y Normativa", size_pt=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=4, anchor_name="_Toc_Sub_31", bm_id=905, outline_lvl=1)
        p_31_txt = _crear_parrafo_flotante(
            doc,
            "Macrolocalización: comuna de Osorno (Región de Los Lagos), polo de servicios comerciales y educacionales con acceso directo a la Ruta 5 Sur y al eje generador de cartón. Microlocalización: galpón industrial de 140 m2 en el Sector Industrial de Ovejería (ubicado a 3,2 km —aprox. 10 minutos— de calle Eleuterio Ramírez), seleccionado frente al centro urbano por compatibilidad de uso de suelo industrial (PRC Osorno), disponibilidad de energía trifásica Saesa, facilidad de carga/descarga y menor canon de arriendo ($450.000/mes vs. >$950.000/mes en zona céntrica)."
        )
        df_loc = pd.DataFrame([
            ["Cercanía a generadores (Eje E. Ramírez)", "25%", "Alta (3,2 km / 10 min en furgón)", "Muy alta (0,5 km)", "Ovejería mantiene flete acotado sin congestión céntrica."],
            ["Valor de arriendo y superficie (140 m2)", "25%", "Óptimo ($450.000/mes exento)", "Alto (> $950.000/mes)", "Permite flujo lineal de producción y bodega seca."],
            ["Uso de suelo industrial y permisos", "20%", "Compatible (Zona Industrial PRC)", "Restringido (ruido/carga)", "Facilita patente industrial y resolución sanitaria SEREMI."],
            ["Energía trifásica y acceso camiones", "15%", "Disponible (red Saesa industrial)", "Limitado / horarios carga", "Indispensable para troqueladora de rodillos 1200 mm."],
            ["Accesibilidad a compradores y Ruta 5", "15%", "Buena (conexión directa urbana/R5)", "Buena con congestión", "Facilita despacho a colegios, librerías y provincia."],
        ], columns=["Factor de Localización", "Peso", "Sector Ovejería (Elegido)", "Centro Urbano", "Justificación Técnica"])
        t_loc = _crear_tabla_en_doc(doc, df_loc, [1.50, 0.50, 1.55, 1.25, 1.90], fuente_pt=7.5)
        els_map = _crear_parrafo_imagen(doc, rutas_img["mapa_localizacion"], ancho_pulgadas=6.2, leyenda="Figura 4. Mapa de localización en Osorno: 6 locales generadores en calle Eleuterio Ramírez, ruta matutina y planta taller en Sector Industrial Ovejería. Fuente: Elaboración propia.")
        els_croq = _crear_parrafo_imagen(doc, rutas_img["croquis_galpon"], ancho_pulgadas=5.8, leyenda="Figura 5. Croquis conceptual de distribución del recinto de 140 m2 en Ovejería (Osorno). Fuente: Elaboración propia.")
        els_proc = _crear_parrafo_imagen(doc, rutas_img["flujo_proceso"], ancho_pulgadas=6.4, leyenda="Figura 6. Flujo productivo de 7 etapas incorporando diseño continuo, renovación de matrices y control de calidad. Fuente: Elaboración propia.")
        p_leg = _crear_parrafo_flotante(
            doc,
            "Marco Legal y Normativo: (1) Constitución SpA, inicio de actividades SII (Régimen Pro Pyme General, Circular N° 53/2025) y patente industrial en Municipalidad de Osorno; (2) Cumplimiento obligatorio del D.S. N° 114/2005 del MINSAL (Reglamento de Seguridad de los Juguetes) y tintas certificadas EN-71; (3) Trazabilidad de la fracción residual (30% de recortes) bajo Ley N° 20.920 (Ley REP) con certificado de recepción de gestor autorizado; (4) Contrato laboral regido por Código del Trabajo con sueldo mínimo legal vigente ($553.553) y cobertura íntegra de leyes sociales del empleador (Seguro de Cesantía, SIS, Mutualidad Ley 16.744 y aporte previsional)."
        )
        for el in [p_31._p, p_31_txt._p, t_loc._tbl] + els_map + els_croq + els_proc + [p_leg._p]:
            _insertar_antes(p_sec4, el)

    # D) SECCIONES 8.2 (GRÁFICO FLUJOS SNI 2026) Y 8.3 (SENSIBILIDAD 100% DINÁMICA)
    if p_sec9 is not None:
        p_82 = _crear_parrafo_flotante(doc, "8.2 Comparación Gráfica Privado vs. Social SNI 2026", size_pt=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=4, anchor_name="_Toc_Sub_82", bm_id=906, outline_lvl=1)
        p_82_txt = _crear_parrafo_flotante(
            doc,
            f"La Figura 7 contrasta la evolución anual del Flujo de Caja Privado Neto ({tp_s}%) frente al Flujo Social SNI 2026 ({ts_s}%). La brecha positiva a favor de la evaluación social (VANS = {_fmt_clp(m['van_social'])} vs. VAN Privado = {_fmt_clp(m['van_privado'])}) se explica por la menor tasa social de descuento, la exclusión de impuestos (transferencias internas), los precios sombra de la mano de obra y el ahorro municipal en el Vertedero de Curaco sobre las toneladas incorporadas:"
        )
        els_flujos = _crear_parrafo_imagen(doc, rutas_img["flujos_comparados"], ancho_pulgadas=6.2, leyenda=f"Figura 7. Comparación anual entre flujo privado ({tp_s}%) y flujo social SNI 2026 ({ts_s}%). Fuente: Elaboración propia.")

        p_83 = _crear_parrafo_flotante(doc, f"8.3 Análisis de Sensibilidad Multiescenario (Privado {tp_s}% y Social {ts_s}%)", size_pt=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=4, anchor_name="_Toc_Sub_83", bm_id=907, outline_lvl=1)
        nombres_esc = [
            "Pesimista: -15% precios/ingresos",
            "Incremento de costos: +10% costos",
            f"Caso base: +{crec_s}% crecimiento anual",
            "Sin crecimiento: 0% anual fijo",
        ]
        filas_s = [
            [nombres_esc[idx], _fmt_clp(e["van_p"]), f"{_fmt_dec(e['tir_p'],2)}%", _fmt_clp(e["van_s"]), f"{_fmt_dec(e['tir_s'],2)}%"]
            for idx, e in enumerate(escenarios_sens)
        ]
        df_sens = pd.DataFrame(filas_s, columns=["Escenario Evaluado", f"VAN Privado ({tp_s}%)", "TIR Privada", f"VANS Social ({ts_s}%)", "TIRS Social"])
        t_sens = _crear_tabla_en_doc(doc, df_sens, [2.30, 1.15, 1.00, 1.25, 1.00], fuente_pt=7.8)
        els_sens = _crear_parrafo_imagen(doc, rutas_img["sensibilidad"], ancho_pulgadas=6.0, leyenda="Figura 8. Análisis de sensibilidad del VAN privado y VANS social SNI 2026 ante escenarios de estrés. Fuente: Elaboración propia.")
        for el in [p_82._p, p_82_txt._p] + els_flujos + [p_83._p, t_sens._tbl] + els_sens:
            _insertar_antes(p_sec9, el)

    # E) SECCIÓN 10 (CANVAS) Y SECCIÓN 11 (MARCO LÓGICO ESTRICTO — COMENTARIO #39)
    if p_anx1 is not None:
        p_10 = _crear_parrafo_flotante(doc, "10. MODELO DE GESTIÓN ESTRATÉGICA - BUSINESS MODEL CANVAS", size_pt=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=6, anchor_name="_Toc_Canvas", bm_id=910, outline_lvl=0)
        df_canvas = pd.DataFrame([
            ["1. Socios Clave", "6 comercios generadores en eje Eleuterio Ramírez; gestor autorizado de reciclaje (Ley REP para 30% recortes); diseñador gráfico/pedagógico externo; proveedores de tintas EN-71 y matrices; librerías locales y asociaciones de adulto mayor."],
            ["2. Actividades Clave", "Retiro selectivo matutino (furgón contratado), clasificación y control de humedad, actualización anual de diseños y matrices, troquelado industrial, impresión EN-71/barnizado, control de calidad visual/funcional y gestión comercial multicanal."],
            ["3. Recursos Clave", "Cartón corrugado limpio (15,00 t/año Año 1), galpón industrial 140 m2 en Ovejería, troqueladora, guillotina, matrices renovables, equipo serigráfico, 5 trabajadores con cobertura legal completa y protocolos de calidad."],
            ["4. Propuesta de Valor", f"Juegos didácticos infantiles ({cfg['P1_NOMBRE']}) y kits cognitivos ({cfg['P2_NOMBRE']}) de cartón multicapa lavable, diseño actualizado, seguros (D.S. 114 / EN-71) y 20%-30% más accesibles que madera, con trazabilidad ambiental en Osorno."],
            ["5. Relación con Clientes", "Validación con prototipos junto a educadoras y terapeutas, renovación anual de colecciones, reposición de piezas y soporte postventa."],
            ["6. Canales (Diversificados)", "1) Venta B2B directa a jardines y colegios particulares (45% P1); 2) Licitaciones y Compra Ágil en Mercado Público (30% P1); 3) Retail local, librerías educativas y venta directa a familias (25% P1 y 45% P2); 4) Convenios con ELEAM/cajas/fundaciones."],
            ["7. Segmentos de Clientes", "Jardines y colegios privados/subvencionados, establecimientos públicos vía licitación, familias y librerías educativas de Osorno; ELEAM, fundaciones, clubes y cuidadores de adultos mayores."],
            ["8. Estructura de Costos", f"Planilla de 5 trabajadores con sueldo mínimo $553.553 + leyes sociales ({_fmt_clp(m['personal_anual_priv'])}/año privado; {_fmt_clp(m['personal_anual_soc'])}/año social), diseño/matrices ($250.000/mes c/IVA), arriendo Ovejería, insumos EN-71, flete contratado y reinversión Año 5."],
            ["9. Fuentes de Ingreso", f"Venta de {cfg['P1_UNIDADES']:,} sets escolares ({_fmt_clp(cfg['P1_PRECIO_BRUTO'])} c/IVA) y {cfg['P2_UNIDADES']:,} kits cognitivos ({_fmt_clp(cfg['P2_PRECIO_BRUTO'])} c/IVA), generando {_fmt_clp(m['ingresos_anio_1'])} netos en Año 1.".replace(",", ".")],
        ], columns=["Bloque del Modelo CANVAS", "Aplicación Estratégica en Cartón Vivo Osorno"])
        t_canv = _crear_tabla_en_doc(doc, df_canvas, [1.75, 4.95], fuente_pt=7.7)

        # SECCIÓN 11: MML ESTRICTA (DERIVADA DEL ÁRBOL DE OBJETIVOS, SIN IND/MV/SUP EN FIN, PRESUPUESTO EN ACTIVIDADES Y SIN SUPUESTOS EN ACTIVIDADES)
        p_11 = _crear_parrafo_flotante(doc, "11. MODELO DE SEGUIMIENTO - MATRIZ DE MARCO LÓGICO", size_pt=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=4, anchor_name="_Toc_MML", bm_id=911, outline_lvl=0)
        p_11_txt = _crear_parrafo_flotante(
            doc,
            "La Matriz de Marco Lógico (Tabla 11.1) se deriva directamente del Árbol de Objetivos (Figura 2). Conforme a las reglas metodológicas de la cátedra: (1) a nivel de FIN no se definen indicadores, medios de verificación ni supuestos; (2) a nivel de ACTIVIDADES la columna de indicadores registra exclusivamente el presupuesto desglosado del proyecto y no se definen supuestos:"
        )

        inv_maqs = sum(float(x["monto_bruto"]) for x in cfg["INVERSIONES_LISTA"][:3]) / (1.0 + float(cfg["IVA"]))
        inv_galp = float(cfg["INVERSIONES_LISTA"][3]["monto_bruto"]) / (1.0 + float(cfg["IVA"])) if len(cfg["INVERSIONES_LISTA"]) > 3 else 0.0
        diseno_anual_neto = round((250000.0 * 12.0) / (1.0 + float(cfg["IVA"])))
        df_mml = pd.DataFrame([
            [
                "FIN (Fines del Árbol de Objetivos)\nContribuir a reducir la presión sobre el Vertedero Provincial de Curaco, retener valor económico/ambiental y fortalecer la economía circular en la comuna de Osorno.",
                "No aplica (en nivel Fin no se definen indicadores).",
                "No aplica (en nivel Fin no se definen medios de verificación).",
                "No aplica (en nivel Fin no se definen supuestos)."
            ],
            [
                "PROPÓSITO (Objetivo Central Único)\nAumentar el aprovechamiento local y reducir la disposición en vertedero del cartón corrugado comercial recuperable del eje céntrico de Osorno.",
                f"1) Eficacia: >= 15,00 t/año de cartón recuperadas en Año 1 (70% incorporado en 4.500 juegos y 30% reciclado con trazabilidad).\n2) Calidad: tasa de rechazo de productos < 3% y satisfacción de usuarios >= 90%.\n3) Eficiencia: cumplimiento del costo unitario proyectado.",
                "Registros mensuales de pesaje en planta; facturas de venta SII; certificados de recepción de gestor autorizado (Ley REP); encuestas de satisfacción a clientes.",
                "El comercio céntrico mantiene estabilidad en su flujo de embalajes y el mercado local sostiene la demanda de productos sustentables."
            ],
            [
                "COMPONENTES (Medios Directos del Árbol)\nC1: Retiro selectivo matutino formalizado (M1).\nC2: Capacidad productiva industrial con diseño continuo y control de calidad implementada (M2).\nC3: Canales comerciales diversificados (privados, licitaciones y retail) operativos (M3).\nC4: Trazabilidad del 30% de fracción residual activa (M3).",
                "C1: 6 acuerdos activos de retiro en E. Ramírez.\nC2: Galpón 140 m2 habilitado, catálogo renovado anualmente y protocolo D.S. 114/EN-71.\nC3: Cartera activa en >= 3 canales distintos (sin superar 35% de dependencia en un solo comprador).\nC4: 100% de recortes (4,50 t/año) con certificado de gestor.",
                "Convenios firmados con locales; resolución sanitaria/patente; fichas técnicas de diseño y calidad; órdenes de compra y comprobantes de licitación; certificados Ley REP.",
                "Proveedores entregan cartón seco antes de 06:00 AM; equipos industriales operan sin detenciones prolongadas; procesos de licitación pública mantienen regularidad."
            ],
            [
                "ACTIVIDADES (Acciones por Componente)\nA1: Firma de convenios y operación de retiro matutino.\nA2: Acondicionamiento galpón Ovejería, compra de maquinaria/matrices y contratación de diseño continuo.\nA3: Encuesta/entrevistas de validación, gestión comercial multicanal y licitaciones.\nA4: Segregación y despacho de recortes a gestor autorizado.",
                f"PRESUPUESTO DESGLOSADO (Valores Netos s/IVA):\n- Maquinaria, matrices y serigrafía: {_fmt_clp(inv_maqs)}\n- Habilitación galpón SEC/SEREMI: {_fmt_clp(inv_galp)}\n- Capital de Trabajo inicial ({int(cfg['DIAS_DESFASE_CT'])} días): {_fmt_clp(m['ct_inicial'])}\n- Total Desembolso Año 0: {_fmt_clp(m['inv_inicial_priv'] + m['ct_inicial'])}\n- Presupuesto Operación Año 1 (incl. personal con leyes soc. y diseño {_fmt_clp(diseno_anual_neto)}/año): {_fmt_clp(m['costos_anio_1'])}",
                "Facturas de compra de maquinaria y habilitación; libros contables SII; liquidaciones de sueldo y comprobantes Previred (leyes sociales); boletas/facturas de diseño y flete.",
                "No aplica (a nivel de actividades no se definen supuestos)."
            ],
        ], columns=["Resumen Narrativo de Objetivos", "Indicadores Verificables / Presupuesto", "Medios de Verificación", "Supuestos Críticos"])
        t_mml = _crear_tabla_en_doc(doc, df_mml, [1.80, 1.80, 1.55, 1.55], fuente_pt=7.4)

        for el in [p_10._p, t_canv._tbl, p_11._p, p_11_txt._p, t_mml._tbl]:
            _insertar_antes(p_anx1, el)

    _actualizar_indice_p2(doc)
    doc.save(ruta_word)

    for r_im in rutas_img.values():
        if os.path.exists(r_im):
            try:
                os.remove(r_im)
            except Exception:
                pass
    return ruta_word


def actualizar_pdf_y_zip_final(ruta_word):
    ruta_pdf = os.path.splitext(ruta_word)[0] + ".pdf"
    carpeta_entrega = os.path.dirname(os.path.abspath(ruta_word))
    apellidos = os.path.basename(carpeta_entrega)
    directorio_padre = os.path.dirname(carpeta_entrega)
    ruta_zip = os.path.join(directorio_padre, f"{apellidos}.zip")

    pdf_ok = False
    if sys.platform.startswith("win"):
        abs_docx = os.path.abspath(ruta_word).replace("'", "''")
        abs_pdf = os.path.abspath(ruta_pdf).replace("'", "''")
        ps_cmd = (
            "$ErrorActionPreference = 'Stop'; "
            "$word = New-Object -ComObject Word.Application; "
            "$word.Visible = $false; $word.DisplayAlerts = 0; "
            f"$doc = $word.Documents.Open('{abs_docx}'); "
            "$doc.Repaginate(); $doc.Fields.Update() | Out-Null; "
            "$doc.SpellingChecked = $true; $doc.ShowSpellingErrors = $false; "
            f"$doc.Save(); $doc.SaveAs([ref]'{abs_pdf}', [ref]17); $doc.Close(); $word.Quit();"
        )
        try:
            subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], check=True, timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            pdf_ok = os.path.exists(ruta_pdf)
        except Exception:
            pdf_ok = False

    if os.path.exists(ruta_zip):
        try:
            os.remove(ruta_zip)
        except Exception:
            pass

    with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for arch in os.listdir(carpeta_entrega):
            r_full = os.path.join(carpeta_entrega, arch)
            if os.path.isfile(r_full):
                zf.write(r_full, arcname=os.path.join(apellidos, arch))

    return ruta_pdf, ruta_zip, pdf_ok
