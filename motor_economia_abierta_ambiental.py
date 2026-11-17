# -*- coding: utf-8 -*-
"""
MOTOR INTERACTIVO: ECONOMÍA ABIERTA (CLASE 16 NOV) Y EVALUACIÓN AMBIENTAL (CLASE EA 1)
Asignatura: Evaluación Integrada de Proyectos (FDIC26) — Universidad de Los Lagos
Docente: Dra. Luz María Ferrada B.
Archivo: motor_economia_abierta_ambiental.py

Integra de forma interactiva y pedagógica:
1. Clse 16 nov.pdf — Evaluación Integrada de Proyectos en Economía Abierta:
   - Mercados transables: Insumos Importables (Pm / Pm*), Insumos Exportables (Pe / Pe*),
     Productos Exportables (VSP = VPP * [R* / (R*(1-T))]) y Sustitutos de Importaciones (VSP = Pm* * X).
   - Gráficos interactivos de equilibrio con áreas sombreadas de Valor Social (VSP) y Costo Social (CSY).
   - Ejercicios rápidos resueltos en vivo (Exportables 100 unds y Importados 5.000 unds).
   - 3 Ejercicios Integradores de Cátedra resueltos e interactivos:
     (1) Puente vs. Barcaza (VANS, CAE y criterios SEA),
     (2) Industria del Salmón — Sustitución de Importaciones y Aporte Estatal mínimo,
     (3) Centro de Reciclaje Turístico con Externalidad Ambiental (mercados de producto e insumo).
2. Clase EA 1.pdf — Evaluación de Proyectos con Impacto Ambiental:
   - Economía Neoclásica vs. Economía Circular (flujos de energía y reciclaje).
   - Matriz 2x2 de Bienes (Rivalidad x Exclusión), Tragedia de los Comunes (Hardin, 1968),
     3 Fallas de Mercado y Taxonomía de Recursos Naturales.
   - Simulador Dinámico del Sistema Circular de Recursos Naturales (CCAD, 2010:12):
     reglas de sostenibilidad (h vs y; W*(1-r) vs A) con proyección a 30 años.
   - Metodología de 8 pasos, Ley 19.300 (DIA vs EIA), Impacto Ambiental (Con vs Sin Proyecto desde Línea Base)
     y las 6 Críticas Estructurales al SEIA y al Análisis Costo-Beneficio (ACB).
"""

import numpy as np
import numpy_financial as npf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _nota_teorica(titulo_boton: str, titulo_interno: str, explicacion_md: str, formula_latex: str = None):
    """Muestra una nota metodológica desplegable con estilo consistente al laboratorio."""
    if hasattr(st, "popover"):
        cont = st.popover(f"Nota Metodológica: {titulo_boton}", use_container_width=True)
    else:
        cont = st.expander(f"Nota Metodológica: {titulo_boton}")
    with cont:
        st.markdown(f"#### {titulo_interno}")
        if formula_latex:
            st.latex(formula_latex)
        st.markdown(explicacion_md)


def _fmt_clp(val: float) -> str:
    if val < 0:
        return f"-${abs(int(round(val))):,}".replace(",", ".")
    return f"${int(round(val)):,}".replace(",", ".")


# ==============================================================================
# 1. GRÁFICOS INTERACTIVOS DE ECONOMÍA ABIERTA (CLASE 16 NOV)
# ==============================================================================

def construir_grafico_economia_abierta(
    modo: str,
    p_priv: float,
    p_soc: float,
    cantidad_proy: float,
    etiqueta_eje_x: str = "Cantidad (Q)",
):
    """
    Construye gráficos interactivos de Oferta y Demanda en Economía Abierta
    (réplica interactiva de las láminas 2, 3, 4, 7 y 10 de 'Clse 16 nov.pdf').
    """
    q_max = max(cantidad_proy * 3.8, 100.0)
    q = np.linspace(0, q_max, 200)
    p_base = max(p_priv, p_soc) * 1.45

    fig = go.Figure()

    if modo == "Insumos Importables":
        # Curvas S y D base
        s_y = p_base * 0.20 + (p_base * 0.85 / q_max) * q
        d_y = p_base * 1.10 - (p_base * 0.85 / q_max) * q
        d_y_new = p_base * 1.10 - (p_base * 0.85 / q_max) * (q - cantidad_proy)

        # Equilibrios a precio Pm
        y1 = max(0.0, (p_priv - p_base * 0.20) / (p_base * 0.85 / q_max))
        y0 = max(0.0, (p_base * 1.10 - p_priv) / (p_base * 0.85 / q_max))
        y2 = y0 + cantidad_proy

        # Área sombreada Costo Social CSY = Pm* * (Y2 - Y0)
        fig.add_trace(go.Scatter(
            x=[y0, y2, y2, y0, y0], y=[0, 0, p_soc, p_soc, 0],
            fill="toself", fillcolor="rgba(220, 38, 38, 0.24)",
            line=dict(color="#DC2626", width=1.5),
            name=f"Costo Social CSY = Pm* · Y ({_fmt_clp(p_soc * cantidad_proy)})",
        ))
        fig.add_trace(go.Scatter(x=q, y=s_y, mode="lines", name="Oferta Nacional (S)", line=dict(color="#0F172A", width=2.4)))
        fig.add_trace(go.Scatter(x=q, y=d_y, mode="lines", name="Demanda Inicial (D)", line=dict(color="#1D4ED8", width=2.4)))
        fig.add_trace(go.Scatter(x=q, y=d_y_new, mode="lines", name="Demanda con Proyecto (D + Y)", line=dict(color="#1D4ED8", width=2.2, dash="dash")))
        fig.add_hline(y=p_priv, line_color="#475569", line_width=1.8, annotation_text=f"Pm privado = {_fmt_clp(p_priv)}")
        fig.add_hline(y=p_soc, line_color="#DC2626", line_dash="dot", line_width=2.0, annotation_text=f"Pm* social = {_fmt_clp(p_soc)}")
        for x_m, lbl_m in [(y1, "Y1 (Oferta Nac.)"), (y0, "Y0"), (y2, "Y2 = Y0 + Y")]:
            fig.add_vline(x=x_m, line_color="#94A3B8", line_dash="dot", line_width=1.2, annotation_text=lbl_m, annotation_position="bottom")
        titulo = "Insumos Importables: Desplazamiento D -> D + Y y Costo Social al Precio CIF Social (Pm*)"

    elif modo == "Insumos Exportables":
        s_y = p_base * 0.15 + (p_base * 0.70 / q_max) * q
        d_y = p_base * 1.15 - (p_base * 0.90 / q_max) * q
        d_y_new = p_base * 1.15 - (p_base * 0.90 / q_max) * (q - cantidad_proy)

        y0 = max(0.0, (p_base * 1.15 - p_priv) / (p_base * 0.90 / q_max))
        y1 = y0 + cantidad_proy
        y2 = max(y1 + 5.0, (p_priv - p_base * 0.15) / (p_base * 0.70 / q_max))

        fig.add_trace(go.Scatter(
            x=[y0, y1, y1, y0, y0], y=[0, 0, p_soc, p_soc, 0],
            fill="toself", fillcolor="rgba(217, 119, 6, 0.25)",
            line=dict(color="#D97706", width=1.5),
            name=f"CS Insumo Exportable = Pe* · Y ({_fmt_clp(p_soc * cantidad_proy)})",
        ))
        fig.add_trace(go.Scatter(x=q, y=s_y, mode="lines", name="Oferta Nacional (S)", line=dict(color="#0F172A", width=2.4)))
        fig.add_trace(go.Scatter(x=q, y=d_y, mode="lines", name="Demanda Inicial (D)", line=dict(color="#1D4ED8", width=2.4)))
        fig.add_trace(go.Scatter(x=q, y=d_y_new, mode="lines", name="Demanda con Proyecto (D + Y)", line=dict(color="#1D4ED8", width=2.2, dash="dash")))
        fig.add_hline(y=p_priv, line_color="#475569", line_width=1.8, annotation_text=f"Pe privado = {_fmt_clp(p_priv)}")
        fig.add_hline(y=p_soc, line_color="#D97706", line_dash="dot", line_width=2.0, annotation_text=f"Pe* social = {_fmt_clp(p_soc)}")
        for x_m, lbl_m in [(y0, "Y0"), (y1, "Y1 (Menor Export.)"), (y2, "Y2 (Oferta Tot.)")]:
            fig.add_vline(x=x_m, line_color="#94A3B8", line_dash="dot", line_width=1.2, annotation_text=lbl_m, annotation_position="bottom")
        titulo = "Costo Social de Insumos Exportables: Demanda del Proyecto Reduce Exportaciones en Y"

    elif modo == "Productos Exportables":
        s_y = p_base * 0.15 + (p_base * 0.75 / q_max) * q
        s_y_new = p_base * 0.15 + (p_base * 0.75 / q_max) * (q - cantidad_proy)
        d_y = p_base * 1.15 - (p_base * 0.90 / q_max) * q

        x0 = max(0.0, (p_priv - p_base * 0.15) / (p_base * 0.75 / q_max))
        x1 = x0 + cantidad_proy

        fig.add_trace(go.Scatter(
            x=[x0, x1, x1, x0, x0], y=[0, 0, p_soc, p_soc, 0],
            fill="toself", fillcolor="rgba(22, 163, 74, 0.25)",
            line=dict(color="#15803D", width=1.5),
            name=f"VSP Exportable = Pe* · X ({_fmt_clp(p_soc * cantidad_proy)})",
        ))
        fig.add_trace(go.Scatter(x=q, y=s_y, mode="lines", name="Oferta Inicial (S)", line=dict(color="#0F172A", width=2.4)))
        fig.add_trace(go.Scatter(x=q, y=s_y_new, mode="lines", name="Oferta con Proyecto (S + X)", line=dict(color="#15803D", width=2.2, dash="dash")))
        fig.add_trace(go.Scatter(x=q, y=d_y, mode="lines", name="Demanda Nacional (D)", line=dict(color="#1D4ED8", width=2.4)))
        fig.add_hline(y=p_priv, line_color="#475569", line_width=1.8, annotation_text=f"Pe privado = {_fmt_clp(p_priv)}")
        fig.add_hline(y=p_soc, line_color="#15803D", line_dash="dot", line_width=2.0, annotation_text=f"Pe* social = {_fmt_clp(p_soc)}")
        for x_m, lbl_m in [(x0, "X0"), (x1, "X1 = X0 + X")]:
            fig.add_vline(x=x_m, line_color="#94A3B8", line_dash="dot", line_width=1.2, annotation_text=lbl_m, annotation_position="bottom")
        titulo = "Productos Exportables: Generación de Divisas Valoradas al Precio FOB Social (Pe*)"

    else:  # Sustitutos de Importaciones
        s_y = p_base * 0.15 + (p_base * 0.85 / q_max) * q
        s_y_new = p_base * 0.15 + (p_base * 0.85 / q_max) * (q - cantidad_proy)
        d_y = p_base * 1.25 - (p_base * 0.70 / q_max) * q

        x0 = max(0.0, (p_priv - p_base * 0.15) / (p_base * 0.85 / q_max))
        x1 = x0 + cantidad_proy
        x2 = max(x1 + 5.0, (p_base * 1.25 - p_priv) / (p_base * 0.70 / q_max))

        fig.add_trace(go.Scatter(
            x=[x0, x1, x1, x0, x0], y=[0, 0, p_soc, p_soc, 0],
            fill="toself", fillcolor="rgba(37, 99, 235, 0.24)",
            line=dict(color="#1D4ED8", width=1.5),
            name=f"VSP Sustitución = Pm* · X ({_fmt_clp(p_soc * cantidad_proy)})",
        ))
        fig.add_trace(go.Scatter(x=q, y=s_y, mode="lines", name="Oferta Inicial (S)", line=dict(color="#0F172A", width=2.4)))
        fig.add_trace(go.Scatter(x=q, y=s_y_new, mode="lines", name="Oferta con Proyecto (S + X)", line=dict(color="#1D4ED8", width=2.2, dash="dash")))
        fig.add_trace(go.Scatter(x=q, y=d_y, mode="lines", name="Demanda Nacional (D)", line=dict(color="#475569", width=2.4)))
        fig.add_hline(y=p_priv, line_color="#475569", line_width=1.8, annotation_text=f"Pm privado = {_fmt_clp(p_priv)}")
        fig.add_hline(y=p_soc, line_color="#1D4ED8", line_dash="dot", line_width=2.0, annotation_text=f"Pm* social = {_fmt_clp(p_soc)}")
        for x_m, lbl_m in [(x0, "X0"), (x1, "X1 (Ahorro Divisas)"), (x2, "X2 (Dem. Total)")]:
            fig.add_vline(x=x_m, line_color="#94A3B8", line_dash="dot", line_width=1.2, annotation_text=lbl_m, annotation_position="bottom")
        titulo = "Proyectos Sustitutos de Importaciones: Ahorro de Divisas al Precio CIF Social (Pm*)"

    fig.update_layout(
        title=titulo,
        xaxis_title=etiqueta_eje_x,
        yaxis_title="Precio ($ CLP)",
        yaxis=dict(range=[0, p_base * 1.18]),
        height=440,
        margin=dict(l=20, r=20, t=55, b=40),
        plot_bgcolor="#F8FAFC",
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="left", x=0),
    )
    return fig


# ==============================================================================
# 2. PESTAÑA 6: ECONOMÍA ABIERTA Y RESOLUCIÓN DE LOS 3 EJERCICIOS (CLASE 16 NOV)
# ==============================================================================

def renderizar_modulo_economia_abierta():
    st.subheader("Economía Abierta: Bienes Transables, Divisa Social y Ejercicios de Cátedra (`Clse 16 nov.pdf`)")
    st.markdown(
        "Laboratorio interactivo de evaluación social en economía abierta: cálculo exacto del **Valor Social de la Producción ($VSP$)** "
        "y **Costo Social de Insumos ($CSY$)** para bienes exportables, importables y sustitutos de importaciones, "
        "más los **2 ejercicios rápidos** y los **3 casos integradores** de la sesión del 16 de noviembre."
    )

    sub_ea = st.tabs([
        "A. Gráficos y Fórmulas (Exportables / Importables)",
        "B. Ejercicios Rápidos de Clase (100 u. y 5.000 u.)",
        "C. Caso 1: Puente vs. Barcaza (y SEA)",
        "D. Caso 2: Salmón Sustituto de Importaciones",
        "E. Caso 3: Centro de Reciclaje Turístico (Externalidad)",
    ])

    # --------------------------------------------------------------------------
    # SUB-TAB A: GRÁFICOS INTERACTIVOS DE LOS 4 MERCADOS TRANSABLES
    # --------------------------------------------------------------------------
    with sub_ea[0]:
        col_g1, col_g2 = st.columns([1.2, 2.2])
        with col_g1:
            modo_mkt = st.radio(
                "Seleccione el Mercado en Economía Abierta:",
                [
                    "Insumos Importables",
                    "Insumos Exportables",
                    "Productos Exportables",
                    "Sustitutos de Importaciones",
                ],
                key="ea_modo_mkt",
            )
            p_intl = st.number_input("Precio Internacional CIF / FOB (US$):", min_value=1.0, value=50.0, step=5.0, key="ea_p_intl")
            tc_priv = st.number_input("Tipo de Cambio Privado R ($/US$):", min_value=100.0, value=800.0, step=10.0, key="ea_tc_p")
            tc_soc = st.number_input("Tipo de Cambio Social R* ($/US$):", min_value=100.0, value=880.0, step=10.0, key="ea_tc_s")
            tasa_imp = st.slider("Arancel (t) o Impuesto Exportación (T) (%):", 0.0, 25.0, 6.0, 0.5, key="ea_tasa_t") / 100.0
            cant_p = st.number_input("Cantidad del Proyecto (X o Y):", min_value=10.0, value=100.0, step=10.0, key="ea_cant_p")

            if modo_mkt in ("Insumos Importables", "Sustitutos de Importaciones"):
                p_priv = p_intl * tc_priv * (1.0 + tasa_imp)
                p_soc = p_intl * tc_soc
                factor_conv = tc_soc / (tc_priv * (1.0 + tasa_imp))
                formula_str = r"P_m = \Pi_m \cdot R(1+t) \quad;\quad P_m^* = \Pi_m \cdot R^* \quad;\quad \text{Factor} = \frac{R^*}{R(1+t)}"
            else:
                p_priv = p_intl * tc_priv * (1.0 - tasa_imp)
                p_soc = p_intl * tc_soc
                factor_conv = tc_soc / max(tc_priv * (1.0 - tasa_imp), 1e-6)
                formula_str = r"P_e = \Pi_e \cdot R(1-T) \quad;\quad P_e^* = \Pi_e \cdot R^* \quad;\quad \text{Factor} = \frac{R^*}{R(1-T)}"

            st.metric("Precio Privado de Mercado", _fmt_clp(p_priv))
            st.metric("Precio Social de Frontera", _fmt_clp(p_soc), f"Factor Social = {factor_conv:.4f}")
            st.metric("Valor Social Total (VSP / CSY)", _fmt_clp(p_soc * cant_p), f"vs Privado {_fmt_clp(p_priv * cant_p)}")

        with col_g2:
            _nota_teorica(
                "Regla de Oro de Bienes Transables (Fontaine / Clase 16 Nov)",
                "¿Por qué no se suman excedentes internos en mercados pequeños abiertos?",
                formula_latex=formula_str,
                explicacion_md=(
                    "- Cuando un país es **tomador de precios internacionales**, el precio interno queda fijado por el precio de frontera ($P_m$ o $P_e$).\n"
                    "- **Insumo Importable:** La mayor demanda $D + \\bar{Y}$ se satisface aumentando importaciones $\\rightarrow$ el costo para el país son las divisas gastadas ($P_m^* \\cdot \\bar{Y}$), sin arancel $t$.\n"
                    "- **Insumo Exportable:** La mayor demanda reduce exportaciones en $\\bar{Y}$ $\\rightarrow$ costo social = divisas dejadas de percibir ($P_e^* \\cdot \\bar{Y}$).\n"
                    "- **Producto Exportable / Sustituto de Importación:** Genera o ahorra divisas netas al país valoradas a $R^*$ ($P_e^* \\cdot \\bar{X}$ o $P_m^* \\cdot \\bar{X}$)."
                ),
            )
            fig_ea = construir_grafico_economia_abierta(modo_mkt, p_priv, p_soc, cant_p)
            st.plotly_chart(fig_ea, use_container_width=True)

    # --------------------------------------------------------------------------
    # SUB-TAB B: EJERCICIOS RÁPIDOS DE LA CLASE (LÁMINAS 6 Y 9)
    # --------------------------------------------------------------------------
    with sub_ea[1]:
        c_e1, c_e2 = st.columns(2)

        with c_e1:
            st.markdown("#### Ejercicio Rápido 1 — Producto Exportable (Lámina 6)")
            st.caption("100 unidades exportables (40 exportadas, 60 nacionales), FOB US$3, R = $800, P doméstico = $5.000, impuesto exp. T = 5%, R* = $880.")
            q_exp = st.number_input("Unidades exportadas:", 0, 1000, 40, key="er1_qe")
            q_nac = st.number_input("Unidades vendidas a nacionales:", 0, 1000, 60, key="er1_qn")
            fob_u = st.number_input("Precio FOB (US$):", 0.5, 500.0, 3.0, 0.5, key="er1_fob")
            r_1 = st.number_input("Tipo de cambio R ($):", 100.0, 2000.0, 800.0, 10.0, key="er1_r")
            r_s1 = st.number_input("Tipo de cambio social R* ($):", 100.0, 2000.0, 880.0, 10.0, key="er1_rs")
            p_dom = st.number_input("Precio doméstico ($):", 100.0, 50000.0, 5000.0, 100.0, key="er1_pdom")
            t_exp = st.number_input("Impuesto a la exportación T (%):", 0.0, 50.0, 5.0, 1.0, key="er1_t") / 100.0

            pe_priv = fob_u * r_1 * (1.0 - t_exp)
            pe_soc = fob_u * r_s1
            vpp_mix = q_exp * pe_priv + q_nac * p_dom
            vpp_puro = (q_exp + q_nac) * pe_priv
            vsp_puro = (q_exp + q_nac) * pe_soc
            vsp_seg = q_exp * pe_soc + q_nac * p_dom

            df_er1 = pd.DataFrame([
                {"Concepto": "Precio privado exportación Pe = FOB · R · (1 - T)", "Cálculo": f"{fob_u} × {r_1:.0f} × (1 - {t_exp:.2f})", "Resultado": _fmt_clp(pe_priv)},
                {"Concepto": "Precio social exportación Pe* = FOB · R*", "Cálculo": f"{fob_u} × {r_s1:.0f}", "Resultado": _fmt_clp(pe_soc)},
                {"Concepto": "VPP (Ventas mixtas: 40 exp. + 60 nac.)", "Cálculo": f"{q_exp}×{pe_priv:,.0f} + {q_nac}×{p_dom:,.0f}", "Resultado": _fmt_clp(vpp_mix)},
                {"Concepto": "VSP (Criterio transable puro: 100 u. a Pe*)", "Cálculo": f"{q_exp + q_nac} × {pe_soc:,.0f}", "Resultado": _fmt_clp(vsp_puro)},
                {"Concepto": "VSP (Si mercado doméstico está segmentado a P_dom)", "Cálculo": f"{q_exp}×{pe_soc:,.0f} + {q_nac}×{p_dom:,.0f}", "Resultado": _fmt_clp(vsp_seg)},
            ])
            st.dataframe(df_er1, use_container_width=True, hide_index=True)
            st.info(
                f"Factor directo sobre ventas exportadas: $R^* / [R(1-T)] = {r_s1:.0f} / ({r_1:.0f} \\times {1-t_exp:.2f}) = {r_s1/(r_1*(1-t_exp)):.4f}$. "
                f"Si toda la producción es perfectamente transable, el costo de oportunidad de vender en Chile también es $P_e^*$ (**VSP = {_fmt_clp(vsp_puro)}**); "
                f"si existe barrera que segmenta el mercado interno a {_fmt_clp(p_dom)}, el VSP mixto asciende a **{_fmt_clp(vsp_seg)}**."
            )

        with c_e2:
            st.markdown("#### Ejercicio Rápido 2 — Insumo Importado (Lámina 9)")
            st.caption("5.000 unidades importadas, CIF US$50, arancel t = 3%, R = $800 y R* = 1,2 · R ($960). Calcular CP y CS.")
            y_imp = st.number_input("Unidades importadas (Y):", 100, 100000, 5000, 100, key="er2_y")
            cif_u = st.number_input("Precio CIF (US$):", 1.0, 1000.0, 50.0, 5.0, key="er2_cif")
            t_ara = st.number_input("Arancel importación t (%):", 0.0, 30.0, 3.0, 0.5, key="er2_t") / 100.0
            r_2 = st.number_input("Tipo de cambio R ($):", 100.0, 2000.0, 800.0, 10.0, key="er2_r")
            ratio_rs = st.number_input("Relación R* / R:", 0.8, 2.0, 1.20, 0.05, key="er2_ratio")

            r_s2 = r_2 * ratio_rs
            pm_priv = cif_u * r_2 * (1.0 + t_ara)
            pm_soc = cif_u * r_s2
            cpy = pm_priv * y_imp
            csy = pm_soc * y_imp
            factor_m = r_s2 / (r_2 * (1.0 + t_ara))

            df_er2 = pd.DataFrame([
                {"Concepto": "Precio Privado Pm = CIF · R · (1 + t)", "Cálculo": f"{cif_u} × {r_2:.0f} × (1 + {t_ara:.2f})", "Resultado": _fmt_clp(pm_priv)},
                {"Concepto": "Costo Privado Total (CPY = Pm · Y)", "Cálculo": f"{pm_priv:,.0f} × {y_imp:,}", "Resultado": _fmt_clp(cpy)},
                {"Concepto": "Precio Social Pm* = CIF · R*", "Cálculo": f"{cif_u} × {r_s2:.0f}", "Resultado": _fmt_clp(pm_soc)},
                {"Concepto": "Costo Social Total (CSY = Pm* · Y)", "Cálculo": f"{pm_soc:,.0f} × {y_imp:,}", "Resultado": _fmt_clp(csy)},
                {"Concepto": "Comprobación CSY = CPY · [R* / R(1+t)]", "Cálculo": f"{cpy:,.0f} × {factor_m:.6f}", "Resultado": _fmt_clp(cpy * factor_m)},
            ])
            st.dataframe(df_er2, use_container_width=True, hide_index=True)
            st.success(
                f"Como la prima social de la divisa ($+{(ratio_rs-1)*100:.0f}\\%$) supera al arancel ($+{t_ara*100:.1f}\\%$), "
                f"el **Costo Social ({_fmt_clp(csy)}) es mayor al Costo Privado ({_fmt_clp(cpy)})** en **{_fmt_clp(csy - cpy)}**."
            )

    # --------------------------------------------------------------------------
    # SUB-TAB C: EJERCICIO 1 — PUENTE VS. BARCAZA (LÁMINAS 11-12)
    # --------------------------------------------------------------------------
    with sub_ea[2]:
        st.markdown("#### Ejercicio 1: Factibilidad Social Puente MOP vs. Línea de Barcaza (`Clse 16 nov.pdf`, págs. 11–12)")
        _nota_teorica(
            "Supuestos Clave del Caso Puente vs. Barcaza",
            "Correcciones Sociales Aplicadas según el Enunciado",
            explicacion_md=(
                "- **Impuestos y Transferencias:** Se elimina el IVA (19%) de insumos afectos (combustibles, repuestos y gastos varios), el arancel del 11% sobre repuestos importados, la depreciación legal y los intereses (transferencias / partidas contables).\n"
                "- **Precios Sombra del Enunciado:** Divisa $+6\\%$ ($1,06$), MOSC $-20\\%$ ($0,80$), MONC $-30\\%$ ($0,70$), MOC $= 1,00$, TSD $= 12\\%$.\n"
                "- **Activos Liberados:** Las embarcaciones tienen uso alternativo: avalúo $\$40\\text{ MM}$ con costo de oportunidad $+25\\% = \$50\\text{ MM}$ liberados en $t=0$.\n"
                "- **Beneficio Social Anual:** (1) Ahorro de costo social de la barcaza para los $100.000$ viajeros actuales, menos el costo de $\$100$/pasajero del puente; (2) Excedente del consumidor por tráfico generado ($150.000$ nuevos viajeros): $\\frac{1}{2}(2.000 - 100)(250.000 - 100.000) = \$142,5\\text{ MM/año}$."
            ),
        )

        cp1, cp2, cp3, cp4 = st.columns(4)
        iva_p = cp1.number_input("IVA implícito en compras (%):", 0.0, 25.0, 19.0, 1.0, key="p1_iva") / 100.0
        arancel_p = cp2.number_input("Arancel repuestos importados (%):", 0.0, 20.0, 11.0, 1.0, key="p1_ara") / 100.0
        tsd_p = cp3.number_input("Tasa Social de Descuento (%):", 4.0, 18.0, 12.0, 0.5, key="p1_tsd") / 100.0
        horiz_comp = cp4.selectbox("Horizonte evaluación:", ["50 años (Vida útil puente)", "30 años (Vida útil barcaza)"], key="p1_hor")

        fc_div_p = 1.06
        fc_mosc_p = 0.80
        fc_monc_p = 0.70
        fc_nac_neto = 1.0 / (1.0 + iva_p)
        fc_imp_soc = (1.0 / ((1.0 + iva_p) * (1.0 + arancel_p))) * fc_div_p

        # Desglose de factores sociales por componente
        comp_puente = [
            ("Mano de Obra Calificada", 0.07, 1.00),
            ("Mano de Obra Semi Calificada", 0.09, fc_mosc_p),
            ("Mano de Obra No Calificada", 0.17, fc_monc_p),
            ("Combustibles y lubricantes (sin IVA)", 0.05, fc_nac_neto),
            ("Repuestos importados (sin IVA/arancel × divisa)", 0.20, fc_imp_soc),
            ("Repuestos nacionales (sin IVA)", 0.15, fc_nac_neto),
            ("Depreciación legal (excluida en flujo social)", 0.10, 0.00),
            ("Intereses (transferencia excluida)", 0.05, 0.00),
            ("Gastos varios (sin IVA)", 0.12, fc_nac_neto),
        ]
        comp_barcaza = [
            ("Mano de Obra Calificada", 0.08, 1.00),
            ("Mano de Obra Semi Calificada", 0.10, fc_mosc_p),
            ("Mano de Obra No Calificada", 0.05, fc_monc_p),
            ("Combustibles y lubricantes (sin IVA)", 0.35, fc_nac_neto),
            ("Repuestos importados (sin IVA/arancel × divisa)", 0.12, fc_imp_soc),
            ("Repuestos nacionales (sin IVA)", 0.15, fc_nac_neto),
            ("Depreciación legal (excluida)", 0.05, 0.00),
            ("Intereses (transferencia excluida)", 0.03, 0.00),
            ("Gastos varios (sin IVA)", 0.07, fc_nac_neto),
        ]

        inv_priv_puente = 2_000_000_000.0
        costo_op_barcaza_priv = 100_000 * 1_000.0

        filas_p = []
        inv_soc_puente = 0.0
        for nom, pct, fc in comp_puente:
            m_p = inv_priv_puente * pct
            m_s = m_p * fc
            inv_soc_puente += m_s
            filas_p.append({"Componente Inversión Puente": nom, "%": f"{pct*100:.0f}%", "Privado ($)": _fmt_clp(m_p), "Factor Social": round(fc, 4), "Social ($)": _fmt_clp(m_s)})

        costo_op_barcaza_soc = sum(costo_op_barcaza_priv * pct * fc for _, pct, fc in comp_barcaza)
        ahorro_barcaza_neto = costo_op_barcaza_soc - (100_000 * 100.0)
        excedente_trafico_nuevo = 0.5 * (2_000.0 - 100.0) * (250_000 - 100_000)
        # Costo de viaje de nuevos usuarios ($100) ya está descontado dentro del triángulo de excedente
        ben_social_anual = ahorro_barcaza_neto + excedente_trafico_nuevo
        valor_barcazas_lib = 40_000_000.0 * 1.25  # $50.000.000

        n_anios = 50 if "50" in horiz_comp else 30
        flujos_puente = np.zeros(n_anios + 1)
        flujos_puente[0] = -inv_soc_puente + valor_barcazas_lib
        flujos_puente[1:] = ben_social_anual
        vans_puente = float(npf.npv(tsd_p, flujos_puente))
        tirs_puente = float(npf.irr(flujos_puente)) * 100.0
        fac_anualidad = (1.0 - (1.0 + tsd_p) ** (-n_anios)) / tsd_p
        vp_beneficios = ben_social_anual * fac_anualidad

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Inversión Social Neta (t=0)", _fmt_clp(inv_soc_puente - valor_barcazas_lib), f"Puente {_fmt_clp(inv_soc_puente)} - Barcazas $50M")
        k2.metric("Beneficio Social Anual", _fmt_clp(ben_social_anual), f"Ahorro {_fmt_clp(ahorro_barcaza_neto)} + EC {_fmt_clp(excedente_trafico_nuevo)}")
        k3.metric(f"VANS ({tsd_p*100:.1f}%, {n_anios} años)", _fmt_clp(vans_puente), "CONVIENE AL PAÍS" if vans_puente > 0 else "NO CONVIENE")
        k4.metric("TIRS del Puente", f"{tirs_puente:.2f}%", f"vs TSD {tsd_p*100:.1f}%")

        c_t1, c_t2 = st.columns([1.4, 1.0])
        with c_t1:
            st.dataframe(pd.DataFrame(filas_p), use_container_width=True, hide_index=True)
        with c_t2:
            st.markdown("##### Pregunta 2: Requisitos ante el SEA (Ley N° 19.300)")
            st.markdown(
                "- **Tipología Art. 10 (Ley 19.300 / D.S. 40):** Infraestructura vial/puente con intervención directa de cauce fluvial.\n"
                "- **Línea Base obligatoria:** Hidrología y calidad de aguas del río, biota acuática/ribera, suelo y patrimonio arqueológico.\n"
                "- **Evaluación DIA vs. EIA (Art. 11):** Exige **EIA** si altera significativamente ecosistemas acuáticos, áreas protegidas o genera reasentamiento/alteración de sistemas de vida (ej. operadores de la barcaza).\n"
                "- **Plan de Mitigación y Seguimiento:** Control de turbidez durante hincado de pilotes, manejo de residuos de obra, ruido y plan de reconversión laboral para tripulación de barcazas."
            )

    # --------------------------------------------------------------------------
    # SUB-TAB D: EJERCICIO 2 — SALMÓN SUSTITUTO DE IMPORTACIONES (LÁMINA 13)
    # --------------------------------------------------------------------------
    with sub_ea[3]:
        st.markdown("#### Ejercicio 2: Industria del Salmón — Sustitución de Importaciones y Aporte Estatal (`Clse 16 nov.pdf`, pág. 13)")
        st.caption("Importación actual: US$450/kg CIF + arancel + IVA (máx 10 ton/año). Proyecto local: 8 ton/año a US$500/kg, inversión US$1,0M activo importado (40 años) + US$400k MOC.")

        cs1, cs2, cs3, cs4 = st.columns(4)
        iva_s = cs1.number_input("IVA (%):", 0.0, 25.0, 19.0, 1.0, key="s2_iva") / 100.0
        ara_s = cs2.number_input("Arancel (%):", 0.0, 20.0, 6.0, 1.0, key="s2_ara") / 100.0
        r_priv_s = cs3.number_input("Tasa descuento privada (%):", 5.0, 25.0, 12.0, 1.0, key="s2_rp") / 100.0
        tsd_s = cs4.number_input("TSD Social (%):", 3.0, 15.0, 5.5, 0.5, key="s2_ts") / 100.0

        cs5, cs6, cs7, cs8 = st.columns(4)
        fc_moc_s = cs5.number_input("Factor MOC:", 0.50, 1.20, 0.97, 0.01, key="s2_moc")
        fc_monc_s = cs6.number_input("Factor MONC:", 0.50, 1.20, 0.91, 0.01, key="s2_monc")
        fc_div_s = cs7.number_input("Factor Divisa (R*/R):", 0.80, 1.50, 1.00, 0.02, key="s2_div")
        imp_renta_s = cs8.number_input("Impuesto Renta Privado (%):", 0.0, 35.0, 25.0, 1.0, key="s2_ir") / 100.0

        q_kg = 8_000.0
        vida_s = 40

        # Privado (neto de IVA porque empresa recupera IVA crédito fiscal; arancel SÍ es costo privado)
        p_venta_priv = 500.0 / (1.0 + iva_s)
        c_nac_priv = 100.0 / (1.0 + iva_s)
        c_imp_priv = 100.0 / (1.0 + iva_s)
        c_moc_priv = 50.0
        c_monc_priv = 150.0
        inv_af_priv = 1_000_000.0 / (1.0 + iva_s)
        inv_moc_priv = 400_000.0
        inv_tot_priv = inv_af_priv + inv_moc_priv
        dep_priv = inv_af_priv / vida_s

        ing_anual_priv = q_kg * p_venta_priv
        cos_anual_priv = q_kg * (c_nac_priv + c_imp_priv + c_moc_priv + c_monc_priv)
        uai_s = ing_anual_priv - cos_anual_priv - dep_priv
        imp_s = max(0.0, uai_s * imp_renta_s)
        fc_anual_priv = (uai_s - imp_s) + dep_priv
        flujos_priv_s = np.array([-inv_tot_priv] + [fc_anual_priv] * vida_s)
        van_priv_s = float(npf.npv(r_priv_s, flujos_priv_s))
        tir_priv_s = float(npf.irr(flujos_priv_s)) * 100.0 if fc_anual_priv > 0 else -100.0

        # Social (Sustitución de importaciones: VSP = CIF * R*/R * Q)
        vsp_anual = q_kg * 450.0 * fc_div_s
        c_nac_soc = 100.0 / (1.0 + iva_s)
        c_imp_soc = (100.0 / ((1.0 + iva_s) * (1.0 + ara_s))) * fc_div_s
        c_moc_soc = 50.0 * fc_moc_s
        c_monc_soc = 150.0 * fc_monc_s
        cos_anual_soc = q_kg * (c_nac_soc + c_imp_soc + c_moc_soc + c_monc_soc)

        inv_af_soc = (1_000_000.0 / ((1.0 + iva_s) * (1.0 + ara_s))) * fc_div_s
        inv_moc_soc = 400_000.0 * fc_moc_s
        inv_tot_soc = inv_af_soc + inv_moc_soc

        fc_anual_soc = vsp_anual - cos_anual_soc
        flujos_soc_s = np.array([-inv_tot_soc] + [fc_anual_soc] * vida_s)
        vans_s = float(npf.npv(tsd_s, flujos_soc_s))
        tirs_s = float(npf.irr(flujos_soc_s)) * 100.0 if fc_anual_soc > 0 else -100.0

        aporte_min_estado = max(0.0, -van_priv_s)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("VAN Privado (US$)", f"US$ {van_priv_s:,.0f}", f"TIR = {tir_priv_s:.2f}%")
        m2.metric("VAN Social — VANS (US$)", f"US$ {vans_s:,.0f}", f"TIRS = {tirs_s:.2f}%")
        m3.metric("Aporte Estatal Mínimo", f"US$ {aporte_min_estado:,.0f}", "No requiere subsidio" if aporte_min_estado == 0 else "Subsidio para VAN_priv = 0")
        if vans_s > 0 and aporte_min_estado <= vans_s:
            veredicto_s = "SÍ conviene socialmente" + (" (sin subsidio)" if aporte_min_estado == 0 else " (subsidio justificable)")
        else:
            veredicto_s = "NO conviene financiar"
        m4.metric("Decisión de Política Pública", veredicto_s)

        df_salm = pd.DataFrame([
            {"Partida (US$)": "Inversión Inicial (t=0)", "Evaluación Privada": f"US$ {inv_tot_priv:,.0f}", "Evaluación Social": f"US$ {inv_tot_soc:,.0f}"},
            {"Partida (US$)": "Ingreso / Beneficio Anual (8.000 kg)", "Evaluación Privada": f"US$ {ing_anual_priv:,.0f}", "Evaluación Social": f"US$ {vsp_anual:,.0f} (Ahorro CIF US$450/kg)"},
            {"Partida (US$)": "Costo Operacional Anual", "Evaluación Privada": f"US$ {cos_anual_priv:,.0f}", "Evaluación Social": f"US$ {cos_anual_soc:,.0f}"},
            {"Partida (US$)": "Flujo Anual Neto (Años 1 a 40)", "Evaluación Privada": f"US$ {fc_anual_priv:,.0f}", "Evaluación Social": f"US$ {fc_anual_soc:,.0f}"},
        ])
        st.dataframe(df_salm, use_container_width=True, hide_index=True)

    # --------------------------------------------------------------------------
    # SUB-TAB E: EJERCICIO 3 — CENTRO DE RECICLAJE TURÍSTICO (LÁMINA 14)
    # --------------------------------------------------------------------------
    with sub_ea[4]:
        st.markdown("#### Ejercicio 3: Centro de Reciclaje Turístico con Externalidad Ambiental (`Clse 16 nov.pdf`, pág. 14)")
        st.caption("Localidad de 800 hab., Q0 = 25.000 turistas/año a $2.500 (exento IVA), precio baja a $2.000 (elasticidad -1,5 -> Q1 = 32.500), CMg baja 20% ($2.000 -> $1.600), externalidad contaminación +10%.")

        ce1, ce2, ce3 = st.columns(3)
        elast_e3 = ce1.slider("Elasticidad precio demanda (ε):", -3.0, -0.5, -1.5, 0.1, key="e3_el")
        inv_escala = ce2.selectbox(
            "Escala inversión del enunciado (nota de texto):",
            ["US$ 500.000 (interpretación realista)", "$500.000.000 CLP (interpretación en pesos)"],
            key="e3_esc",
        )
        tsd_e3 = ce3.selectbox("Tasa Social de Descuento (el enunciado menciona 6% y 10%):", [6.0, 10.0], key="e3_tsd") / 100.0

        p0_t, p1_t = 2500.0, 2000.0
        q0_t = 25000.0
        pct_dp = (p1_t - p0_t) / p0_t  # -0.20
        q1_t = q0_t * (1.0 + elast_e3 * pct_dp)  # 32.500 con elast = -1.5

        cmg_p0 = 2000.0
        cmg_p1 = cmg_p0 * 0.80  # 1600
        cmg_s0 = cmg_p0 * 1.10  # 2200
        cmg_s1 = cmg_p1 * 1.10  # 1760

        # Excedente del consumidor incremental + ahorro de costos sociales - externalidad sobre nuevos turistas
        delta_ec_t = 0.5 * (p0_t - p1_t) * (q0_t + q1_t)
        ahorro_costo_s0 = (cmg_s0 - cmg_s1) * q0_t
        ben_turistas_nuevos = 0.5 * (p0_t + p1_t) * (q1_t - q0_t) - cmg_s1 * (q1_t - q0_t)
        ben_directo_transp = ahorro_costo_s0 + ben_turistas_nuevos
        ing_extra_artesanias = 5.0 * (p1_t * q1_t - p0_t * q0_t)

        # Inversión social (IVA 20%, arancel 5%, R=$650, R*=$700)
        r_e3, rs_e3, iva_e3, ara_e3 = 650.0, 700.0, 0.20, 0.05
        inv_priv_clp = (500_000.0 * r_e3) if "US$" in inv_escala else 500_000_000.0
        fc_imp_e3 = (1.0 / ((1.0 + iva_e3) * (1.0 + ara_e3))) * (rs_e3 / r_e3)
        fc_nac_e3 = 1.0 / (1.0 + iva_e3)

        df_inv_e3 = pd.DataFrame([
            {"Componente Inversión": "Maquinaria importada (40%)", "Privado ($)": inv_priv_clp * 0.40, "Factor Social": fc_imp_e3, "Social ($)": inv_priv_clp * 0.40 * fc_imp_e3},
            {"Componente Inversión": "Maquinaria nacional (30%)", "Privado ($)": inv_priv_clp * 0.30, "Factor Social": fc_nac_e3, "Social ($)": inv_priv_clp * 0.30 * fc_nac_e3},
            {"Componente Inversión": "Insumos importados (20%)", "Privado ($)": inv_priv_clp * 0.20, "Factor Social": fc_imp_e3, "Social ($)": inv_priv_clp * 0.20 * fc_imp_e3},
            {"Componente Inversión": "Insumos sustitución de importaciones (10%)", "Privado ($)": inv_priv_clp * 0.10, "Factor Social": fc_imp_e3, "Social ($)": inv_priv_clp * 0.10 * fc_imp_e3},
        ])
        inv_soc_e3 = float(df_inv_e3["Social ($)"].sum())

        ke1, ke2, ke3, ke4 = st.columns(4)
        ke1.metric("Demanda Con Proyecto (Q1)", f"{q1_t:,.0f} turistas/año", f"+{q1_t - q0_t:,.0f} turistas")
        ke2.metric("Beneficio Social Directo Anual", _fmt_clp(ben_directo_transp), "Ahorro CMg social + Excedente")
        ke3.metric("Efecto Indirecto Artesanía (5× ΔIng)", _fmt_clp(ing_extra_artesanias), "Beneficio económico local")
        ke4.metric("Inversión Social Corregida", _fmt_clp(inv_soc_e3), f"vs Privada {_fmt_clp(inv_priv_clp)}")

        col_ga, col_gb = st.columns(2)
        with col_ga:
            # Gráfico a) Mercado del producto (transporte turístico)
            q_line = np.linspace(10000, max(q1_t * 1.25, 42000), 100)
            pend_d = (p1_t - p0_t) / max(q1_t - q0_t, 1.0)
            p_line = p0_t + pend_d * (q_line - q0_t)

            fig_e3a = go.Figure()
            fig_e3a.add_trace(go.Scatter(
                x=[0, q0_t, q0_t, 0, 0], y=[cmg_s1, cmg_s1, cmg_s0, cmg_s0, cmg_s1],
                fill="toself", fillcolor="rgba(22, 163, 74, 0.20)", line=dict(width=0),
                name=f"Ahorro Costo Social Q0 ({_fmt_clp(ahorro_costo_s0)})",
            ))
            fig_e3a.add_trace(go.Scatter(
                x=[q0_t, q1_t, q1_t, q0_t, q0_t], y=[cmg_s1, cmg_s1, p1_t, p0_t, cmg_s1],
                fill="toself", fillcolor="rgba(37, 99, 235, 0.22)", line=dict(width=0),
                name=f"Beneficio Neto Nuevos Turistas ({_fmt_clp(ben_turistas_nuevos)})",
            ))
            fig_e3a.add_trace(go.Scatter(x=q_line, y=p_line, mode="lines", name="Demanda Turística (D)", line=dict(color="#0F172A", width=2.5)))
            fig_e3a.add_hline(y=cmg_p0, line_color="#64748B", line_dash="dot", annotation_text="CMg Priv. Sin Proy ($2.000)")
            fig_e3a.add_hline(y=cmg_s0, line_color="#DC2626", line_width=2.0, annotation_text="CMg Social Sin Proy ($2.200)")
            fig_e3a.add_hline(y=cmg_p1, line_color="#0284C7", line_dash="dot", annotation_text="CMg Priv. Con Proy ($1.600)")
            fig_e3a.add_hline(y=cmg_s1, line_color="#16A34A", line_width=2.0, annotation_text="CMg Social Con Proy ($1.760)")
            fig_e3a.update_layout(
                title="a) Mercado del Producto (Transporte Turístico + Externalidad +10%)",
                xaxis_title="Turistas / año (Q)", yaxis_title="Precio / Costo Marginal ($ CLP)",
                yaxis=dict(range=[1000, 3200]), height=410,
                legend=dict(orientation="h", y=-0.30),
            )
            st.plotly_chart(fig_e3a, use_container_width=True)

        with col_gb:
            # Gráfico b) Mercado del insumo (Inversión Privada vs Social)
            fig_e3b = go.Figure()
            fig_e3b.add_trace(go.Bar(x=df_inv_e3["Componente Inversión"], y=df_inv_e3["Privado ($)"], name="Inversión Privada c/IVA", marker_color="#475569"))
            fig_e3b.add_trace(go.Bar(x=df_inv_e3["Componente Inversión"], y=df_inv_e3["Social ($)"], name="Inversión Social Corregida", marker_color="#1D4ED8"))
            fig_e3b.update_layout(
                title="b) Mercado de Insumos de Inversión (Privado vs. Social Corregido)",
                barmode="group", yaxis_title="Monto ($ CLP)", height=410,
                legend=dict(orientation="h", y=-0.30),
            )
            st.plotly_chart(fig_e3b, use_container_width=True)


# ==============================================================================
# 3. PESTAÑA 7: EVALUACIÓN AMBIENTAL FUNDAMENTOS (CLASE EA 1.PDF)
# ==============================================================================

def renderizar_modulo_evaluacion_ambiental_ea1():
    st.subheader("Fundamentos de Evaluación de Proyectos con Impacto Ambiental (`Clase EA 1.pdf`)")
    st.markdown(
        "Módulo interactivo basado en las 11 láminas de **`Clase EA 1.pdf`**: transición desde la **Economía Neoclásica a la Economía Circular**, "
        "**Tragedia de los Comunes (Hardin, 1968)**, **Fallas de Mercado y Taxonomía de Recursos**, "
        "**Simulador del Sistema Circular CCAD (2010)**, **Metodología de 8 Pasos / Ley N° 19.300 (DIA vs. EIA)** y **Críticas al SEIA y ACB**."
    )

    sub_amb = st.tabs([
        "1. Economía Circular, Bienes y Tragedia de los Comunes",
        "2. Simulador Sistema Circular CCAD (h vs y; W vs A)",
        "3. Metodología 8 Pasos, Línea Base y Ley 19.300 (DIA/EIA)",
        "4. Críticas al SEIA y al Análisis Costo-Beneficio (ACB)",
    ])

    # --------------------------------------------------------------------------
    # SUB-TAB 1: ECONOMÍA CIRCULAR, MATRIZ DE BIENES Y FALLAS DE MERCADO
    # --------------------------------------------------------------------------
    with sub_amb[0]:
        c_a1, c_a2 = st.columns([1.25, 1.15])
        with c_a1:
            st.markdown("#### Matriz de Clasificación de Bienes (Rivalidad × Exclusión — Lámina 3)")
            df_bienes = pd.DataFrame({
                "Condición de Consumo": ["Rivalidad (si consumo, reduzco disponibilidad)", "No Rivalidad (mi consumo no impide el de otro)"],
                "Con Exclusión (se puede cobrar o impedir acceso)": [
                    "BIENES PRIVADOS (ej. alimentos, maquinaria, ropa)",
                    "BIENES CLUB / PÚBLICOS CON CONGESTIÓN (ej. autopista con peaje, parque con entrada)",
                ],
                "Sin Exclusión (libre acceso)": [
                    "BIENES COMUNES DE LIBRE ACCESO (ej. peces en el mar, acuíferos sin control — Tragedia de los Comunes)",
                    "BIENES PÚBLICOS PUROS (ej. aire limpio, paisaje, defensa nacional, biodiversidad)",
                ],
            })
            st.dataframe(df_bienes, use_container_width=True, hide_index=True)

            _nota_teorica(
                "Tragedia de los Comunes (Hardin, 1968) vs. Propiedad Colectiva",
                "Distinción Clave de Examen (`Clase EA 1.pdf`, lámina 3)",
                explicacion_md=(
                    "- **Error común:** Creer que toda propiedad colectiva fracasa.\n"
                    "- **Lo que realmente señala la lámina 3:** *No es la propiedad colectiva lo que pone en riesgo la conservación del bien (paradoja del prisionero), sino el **LIBRE ACCESO** sin reglas ni información.*\n"
                    "- **Solución económica:** Cuando falta información o hay incentivos perversos individuales, se requiere **REGULACIÓN** (cuotas, derechos de acceso o gobernanza comunitaria)."
                ),
            )

            st.markdown("#### Los 3 Fracasos del Mercado Ambiental (Lámina 4)")
            df_fallas = pd.DataFrame([
                {"Falla de Mercado": "1. Externalidades", "Por qué fracasa el precio": "Efectos indirectos no controlables que afectan a terceros y no entran en el costo privado (ej. contaminación hídrica o atmosférica)."},
                {"Falla de Mercado": "2. Bienes Públicos", "Por qué fracasa el precio": "La no exclusión y no rivalidad inducen libre acceso y comportamiento polizón (free-rider)."},
                {"Falla de Mercado": "3. Asimetría de Información", "Por qué fracasa el precio": "Riesgo moral y selección adversa impiden conocer el daño real y obtener el precio verdadero del medio ambiente."},
            ])
            st.dataframe(df_fallas, use_container_width=True, hide_index=True)

        with c_a2:
            st.markdown("#### Taxonomía de Recursos Naturales (Lámina 5)")
            df_tax = pd.DataFrame({
                "Régimen de Acceso": ["Públicos (No Excluyentes)", "Propiedad Común (Excluyentes)"],
                "Recursos Renovables (y > 0)": [
                    "Energía solar, agua, aire/viento, olas, recursos escénicos y paisajísticos",
                    "Tierra, especies acuícolas, bosques, cultivos, frutales",
                ],
                "Recursos No Renovables (y = 0)": [
                    "(No aplican típicamente como no excluyentes puros)",
                    "Minerales (cobre, plata) y energía fósil (petróleo, gas, carbón)",
                ],
            })
            st.dataframe(df_tax, use_container_width=True, hide_index=True)

            st.markdown("#### De Economía Neoclásica a Economía Circular (Lámina 2)")
            st.info(
                "**Economía Neoclásica tradicional:** Solo modela el circuito cerrado *Empresas $\\leftrightarrow$ Mercado de Bienes/Factores $\\leftrightarrow$ Familias*, ignorando límites físicos.\n\n"
                "**Economía Circular / Termodinámica:** Inserta la economía dentro de la biosfera: recibe **Energía Solar** (energía útil) y **Materias Primas**, reincorpora **Residuos Materiales vía Reciclaje**, pero siempre disipa **Energía Residual (Calor Disipado)** — por eso el reciclaje reduce presión sobre los recursos, pero no viola la entropía."
            )

    # --------------------------------------------------------------------------
    # SUB-TAB 2: SIMULADOR DINÁMICO DEL SISTEMA CIRCULAR CCAD (2010:12 — LÁMINA 6)
    # --------------------------------------------------------------------------
    with sub_amb[1]:
        st.markdown("#### Simulador del Sistema Circular de los Recursos Naturales (`CCAD, 2010:12`, Lámina 6)")
        st.latex(r"\text{Sostenibilidad de Fuente (RR): } h \le y \qquad | \qquad \text{Sostenibilidad de Sumidero: } W_{\text{neto}} = W(1 - r) \le A")

        cc1, cc2, cc3, cc4 = st.columns(4)
        y_reg = cc1.slider("Tasa de regeneración natural (y):", 0.0, 20.0, 10.0, 0.5, key="ccad_y")
        h_ext = cc2.slider("Ritmo de extracción (h):", 0.0, 25.0, 9.0, 0.5, key="ccad_h")
        w_des = cc3.slider("Desechos brutos generados (W):", 0.0, 30.0, 16.0, 1.0, key="ccad_w")
        r_rec = cc4.slider("Tasa de reciclaje (r %):", 0, 90, 40, 5, key="ccad_r") / 100.0

        a_abs = st.slider("Capacidad de absorción del Medio Ambiente (A):", 1.0, 25.0, 12.0, 0.5, key="ccad_a")

        w_neto = w_des * (1.0 - r_rec)
        anios_cc = np.arange(0, 31)
        stock_rr = np.zeros(len(anios_cc))
        contam_ac = np.zeros(len(anios_cc))
        stock_rr[0] = 100.0
        for t in range(1, len(anios_cc)):
            stock_rr[t] = max(0.0, stock_rr[t - 1] + (y_reg - h_ext))
            contam_ac[t] = max(0.0, contam_ac[t - 1] + (w_neto - a_abs))

        ok_fuente = h_ext <= y_reg
        ok_sumidero = w_neto <= a_abs

        k1, k2, k3 = st.columns(3)
        k1.metric("Balance de Recurso Renovable (y - h)", f"{y_reg - h_ext:+.1f} u/año", "SOSTENIBLE (h <= y)" if ok_fuente else "AGOTAMIENTO (h > y)")
        k2.metric("Desechos Netos vs Absorción (W_neto vs A)", f"{w_neto:.1f} vs {a_abs:.1f}", "ASIMILABLE (W_neto <= A)" if ok_sumidero else "CONTAMINACIÓN ACUMULADA (W > A)")
        estado_glob = "SISTEMA SOSTENIBLE" if (ok_fuente and ok_sumidero) else "INSOSTENIBLE (REQUIERE INTERVENCIÓN)"
        k3.metric("Diagnóstico Global CCAD", estado_glob)

        fig_ccad = go.Figure()
        fig_ccad.add_trace(go.Scatter(x=anios_cc, y=stock_rr, mode="lines+markers", name="Stock Recurso Renovable R(t)", line=dict(color="#15803D", width=2.6)))
        fig_ccad.add_trace(go.Scatter(x=anios_cc, y=contam_ac, mode="lines+markers", name="Contaminación Acumulada por sobre A", line=dict(color="#DC2626", width=2.6, dash="dash")))
        fig_ccad.update_layout(
            title="Dinámica a 30 Años del Stock Natural (R) y Contaminación Acumulada (W_neto - A)",
            xaxis_title="Horizonte Temporal (Años)",
            yaxis_title="Unidades Físicas",
            height=380,
            plot_bgcolor="#F8FAFC",
            legend=dict(orientation="h", y=-0.24),
        )
        st.plotly_chart(fig_ccad, use_container_width=True)

    # --------------------------------------------------------------------------
    # SUB-TAB 3: METODOLOGÍA 8 PASOS, LÍNEA BASE Y LEY 19.300 (DIA VS EIA)
    # --------------------------------------------------------------------------
    with sub_amb[2]:
        c_m1, c_m2 = st.columns([1.25, 1.15])
        with c_m1:
            st.markdown("#### Metodología de Evaluación con Impacto Ambiental (8 Pasos — Láminas 8–9)")
            df_pasos = pd.DataFrame([
                {"Paso": "1", "Etapa": "Definición de límites y áreas de influencia", "Foco Técnico": "Estado actual del recurso (Línea Base), diagnóstico de amenazas/causales y alternativas."},
                {"Paso": "2", "Etapa": "Identificación de impactos", "Foco Técnico": "Recursos empleados, impactos dentro y fuera del área, impactos económicos y sociales."},
                {"Paso": "3", "Etapa": "Cuantificación física de impactos importantes", "Foco Técnico": "Medición en unidades físicas y matrices de impactos (ej. Matriz de Leopold)."},
                {"Paso": "4", "Etapa": "Valoración monetaria", "Foco Técnico": "Proyecciones, corrección a precios sombra y cálculo de valores económicos sin precio de mercado."},
                {"Paso": "5", "Etapa": "Tasa de descuento", "Foco Técnico": "Aplicación de TSD vigente (5,5% SNI 2026) y debate de equidad intergeneracional."},
                {"Paso": "6", "Etapa": "Aplicación de criterios de decisión", "Foco Técnico": "VAN Social (VANS), TIRS, VAC / CAE ambientalmente ajustados."},
                {"Paso": "7", "Etapa": "Análisis de sensibilidad", "Foco Técnico": "Evaluación de escenarios ante incertidumbre ambiental y variación de precios/costos."},
                {"Paso": "8", "Etapa": "Restricciones de sostenibilidad", "Foco Técnico": "Resguardo explícito del impacto sobre futuras generaciones (capital natural crítico)."},
            ])
            st.dataframe(df_pasos, use_container_width=True, hide_index=True)

        with c_m2:
            st.markdown("#### Definición de Impacto Ambiental (Lámina 11)")
            st.info(
                "**Fórmula Conceptual:** $\\text{Impacto Ambiental} = \\text{Situación Con Proyecto} - \\text{Situación Sin Proyecto}$ (ambas proyectadas desde la **Situación Inicial o Línea Base**).\n\n"
                "- **Ley N° 19.300 (Chile):** *'La alteración del medio ambiente, provocada directa o indirectamente por un proyecto o actividad en un área determinada.'*\n"
                "- **NCh ISO 14000:** *'Cualquier cambio en el ambiente, sea **adverso o beneficioso**, que es resultado total o parcial de las actividades, productos o servicios de una organización.'*"
            )

            st.markdown("#### Verificador Rápido Ley N° 19.300: ¿DIA o EIA?")
            chk_salud = st.checkbox("¿Genera riesgo para la salud de la población (emisiones, efluentes, residuos)?", key="sea_1")
            chk_rrnn = st.checkbox("¿Efectos adversos significativos sobre recursos naturales renovables (suelo, agua, aire)?", key="sea_2")
            chk_reaset = st.checkbox("¿Reasentamiento de comunidades humanas o alteración significativa de sistemas de vida?", key="sea_3")
            chk_prot = st.checkbox("¿Localización próxima a poblaciones, recursos o áreas protegidas / glaciares / humedales?", key="sea_4")
            chk_pais = st.checkbox("¿Alteración significativa del valor paisajístico o turístico de una zona?", key="sea_5")
            chk_pat = st.checkbox("¿Alteración de monumentos o sitios de patrimonio cultural?", key="sea_6")

            n_art11 = sum([chk_salud, chk_rrnn, chk_reaset, chk_prot, chk_pais, chk_pat])
            if n_art11 > 0:
                st.error(
                    f"Requiere **EIA — Estudio de Impacto Ambiental (Art. 2 letra i, Ley 19.300)** "
                    f"porque activa {n_art11} causal(es) del Art. 11. Exige Línea Base profunda, predicción de impactos y Plan de Mitigación/Reparación/Compensación."
                )
            else:
                st.success(
                    "Si el proyecto está listado en el Art. 10 y no genera los efectos del Art. 11, ingresa vía "
                    "**DIA — Declaración de Impacto Ambiental (Art. 2 letra f, Ley 19.300)** acreditando cumplimiento normativo."
                )

    # --------------------------------------------------------------------------
    # SUB-TAB 4: CRÍTICAS AL SEIA Y AL ANÁLISIS COSTO-BENEFICIO (LÁMINA 10)
    # --------------------------------------------------------------------------
    with sub_amb[3]:
        st.markdown("#### Las 6 Críticas Estructurales al SEIA y al Análisis Costo-Beneficio (Lámina 10)")
        df_criticas = pd.DataFrame([
            {"Crítica (Lámina 10)": "1. Valores antropocéntricos", "Explicación para Defensa Académica": "El ACB solo valora la naturaleza en función de la utilidad humana (disposición a pagar), invisibilizando el valor intrínseco de especies sin uso humano directo."},
            {"Crítica (Lámina 10)": "2. Valores privados vs. de los ciudadanos", "Explicación para Defensa Académica": "Una persona decide distinto como consumidor privado (cortoplacista) que como ciudadano colectivo (preocupado por bienes públicos y justicia ambiental)."},
            {"Crítica (Lámina 10)": "3. Equidad intergeneracional", "Explicación para Defensa Académica": "Descontar beneficios y daños a 50–100 años con tasas altas reduce casi a cero el peso de las generaciones futuras."},
            {"Crítica (Lámina 10)": "4. Valores agregados", "Explicación para Defensa Académica": "El criterio Kaldor-Hicks suma pesos sin ponderar quién gana y quién pierde (ganadores ricos vs. comunidades locales afectadas)."},
            {"Crítica (Lámina 10)": "5. Reduccionismo y complejidad del sistema", "Explicación para Defensa Académica": "Reducir ecosistemas complejos y no lineales a un único número monetario (VAN) puede ocultar umbrales ecológicos irreversibles."},
            {"Crítica (Lámina 10)": "6. Riesgo, incertidumbre e ignorancia", "Explicación para Defensa Académica": "Cuando no se conocen las probabilidades de un daño ambiental irreversible, el cálculo esperado falla y debe aplicarse el principio precautorio."},
        ])
        st.dataframe(df_criticas, use_container_width=True, hide_index=True)
