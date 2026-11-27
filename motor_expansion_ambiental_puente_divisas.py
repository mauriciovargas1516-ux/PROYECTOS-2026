# -*- coding: utf-8 -*-
"""
motor_expansion_ambiental_puente_divisas.py
Módulo de expansión para PROYECTOS-2026 (Evaluación Integrada de Proyectos - FDIC26, ULagos).

Incluye 3 bloques interactivos listos para conectar en consola_web.py o ejecutar standalone:
1. Economía Ambiental, Matriz de Bienes (caso Río Rahue), Taxonomía de Recursos, SEIA (Ley 19.300) y 6 Críticas al ACB.
2. Simulador del Puente en Perpetuidad (Fontaine): corrección de Inversión Social (Is) y CMg Social, AD, LR, VSP y gráfico de áreas.
3. Simulador de Economía Abierta y Ahorro de Divisas (SNI 2026): sustitución de importaciones, arancel, IVA y VANS corregido.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _fmt_clp(valor: float, decimales: int = 0) -> str:
    signo = "-" if valor < 0 else ""
    abs_val = abs(valor)
    if decimales == 0:
        return f"{signo}${int(round(abs_val)):,}".replace(",", ".")
    texto = f"{abs_val:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{signo}${texto}"


def _fmt_usd(valor: float, decimales: int = 2) -> str:
    signo = "-" if valor < 0 else ""
    texto = f"{abs(valor):,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{signo}US${texto}"


def _fmt_num(valor: float, decimales: int = 2) -> str:
    return f"{valor:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _render_bloque_ambiental_seia():
    st.subheader("1. Economía Ambiental, Bienes, SEIA (Ley 19.300) y Críticas al ACB")
    st.caption(
        "El medio ambiente debe considerarse como un activo económico para asignarlo eficientemente. "
        "Los precios de mercado fracasan en reflejar su verdadero valor debido a externalidades, bienes públicos y asimetría de información."
    )

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("#### Matriz de Clasificación de Bienes (Rivalidad vs. Exclusión)")
        df_bienes = pd.DataFrame(
            {
                "Característica": ["Rivalidad (el consumo reduce disponibilidad)", "No Rivalidad (consumo simultáneo)"],
                "Con Exclusión": [
                    "Bienes Privados — Ej.: Pan",
                    "Bienes Club / Tarifables — Ej.: Internet, Gimnasio",
                ],
                "Sin Exclusión": [
                    "Bienes Comunes de Libre Acceso — Ej.: Peces del río Rahue",
                    "Bienes Públicos Puros — Ej.: Alumbrado público",
                ],
            }
        )
        st.dataframe(df_bienes, use_container_width=True, hide_index=True)

    with col_m2:
        st.markdown("#### Taxonomía de Recursos Naturales")
        df_recursos = pd.DataFrame(
            {
                "Tipo de Propiedad": [
                    "Públicos (No excluyentes)",
                    "Propiedad Común (Excluyentes)",
                ],
                "Renovables": [
                    "Energía solar, agua, aire, viento, paisaje",
                    "Tierra, especies acuícolas, bosques, cultivos",
                ],
                "No Renovables": [
                    "Capa de ozono",
                    "Minerales (cobre, plata) y energía fósil (petróleo, gas, carbón)",
                ],
            }
        )
        st.dataframe(df_recursos, use_container_width=True, hide_index=True)

    st.divider()

    col_s1, col_s2 = st.columns([1.05, 1.15])
    with col_s1:
        st.markdown("#### Ley N° 19.300 — Sistema de Evaluación de Impacto Ambiental (SEIA)")
        instrumento = st.radio(
            "Selecciona el instrumento ambiental para revisar su alcance:",
            ["DIA (Declaración de Impacto Ambiental)", "EIA (Estudio de Impacto Ambiental)", "RCA (Resolución de Calificación Ambiental)"],
            horizontal=False,
            key="exp_seia_inst",
        )
        if instrumento.startswith("DIA"):
            st.info(
                "**DIA (Declaración de Impacto Ambiental):** Procede cuando el proyecto cumple la normativa ambiental "
                "y **no genera** efectos, características o circunstancias significativos del Art. 11 de la Ley 19.300 "
                "(como riesgo a la salud, reasentamiento humano o afectación grave de áreas protegidas)."
            )
        elif instrumento.startswith("EIA"):
            st.warning(
                "**EIA (Estudio de Impacto Ambiental):** Obligatorio cuando el proyecto **sí genera** al menos uno de "
                "los impactos significativos del Art. 11. Exige línea base ambiental, predicción de impactos, plan de "
                "medidas de mitigación/reparación/compensación y participación ciudadana formal."
            )
        else:
            st.success(
                "**RCA (Resolución de Calificación Ambiental):** Acto administrativo final que aprueba (con o sin "
                "condiciones) o rechaza ambientalmente el proyecto. Ningún proyecto ingresado al SEIA puede ejecutarse "
                "sin RCA favorable."
            )

        st.markdown(
            "**Economía Circular vs. Neoclásica:** La economía circular cierra el ciclo (*reciclar, reutilizar y valorizar* "
            "residuos para que vuelvan a ser insumos), atacando el origen de los problemas ambientales: "
            "**cuánto producimos y consumimos, y cómo lo hacemos**."
        )

    with col_s2:
        st.markdown("#### Las 6 Críticas Metodológicas al Análisis Costo-Beneficio (ACB / VAN)")
        criticas = {
            "1. Valores antropocéntricos": "El ACB mide valor únicamente según la utilidad humana (disposición a pagar), subestimando el valor intrínseco de los ecosistemas.",
            "2. Valores privados vs. valores ciudadanos": "Lo que una persona paga como consumidor individual puede diferir de lo que valora como ciudadano preocupado por el bien común.",
            "3. Equidad intergeneracional": "Descontar flujos futuros a tasas positivas reduce drásticamente el peso de los costos ambientales que enfrentarán generaciones futuras.",
            "4. Valores agregados (distribución)": "Sumar beneficios y costos netos totales ignora quién gana y quién pierde; un VAN positivo puede concentrar daños en comunidades vulnerables.",
            "5. Reduccionismo y complejidad del sistema": "Expresar sistemas ecológicos no lineales en una sola cifra monetaria simplifica en exceso umbrales críticos e irreversibilidades.",
            "6. Riesgo, incertidumbre e ignorancia": "Muchos impactos ecológicos no tienen probabilidades conocidas; el ACB tradicional asume escenarios previsibles.",
        }
        for titulo, desc in criticas.items():
            with st.expander(titulo, expanded=False):
                st.write(desc)


def _render_bloque_puente_perpetuidad():
    st.subheader("2. Simulador del Puente en Perpetuidad (Fontaine — Precios Sociales)")
    st.caption(
        "Proyecto de infraestructura a 50 años (aproximado como anualidad perpetua) que reduce el costo por viaje "
        "y expande la demanda, descomponiendo el Valor Social de la Producción en Aumento en Disponibilidad (AD) "
        "y Liberación de Recursos (LR)."
    )

    c_p1, c_p2, c_p3, c_p4, c_p5 = st.columns(5)
    q0 = c_p1.number_input("Q0 sin proyecto (viajes/año)", min_value=1000, value=100000, step=10000, key="pte_q0")
    q1 = c_p2.number_input("Q1 con proyecto (viajes/año)", min_value=1000, value=250000, step=10000, key="pte_q1")
    p0 = c_p3.number_input("P0 sin proyecto ($/viaje)", min_value=10.0, value=2000.0, step=100.0, key="pte_p0")
    p1 = c_p4.number_input("P1 con proyecto ($/viaje)", min_value=0.0, value=100.0, step=50.0, key="pte_p1")
    tasa_pct = c_p5.selectbox(
        "Tasa de descuento (%)",
        options=[12.0, 6.0, 5.5],
        index=0,
        help="En el ejercicio clásico se usa 12% en el cálculo final del VAN perpetuo; 6% figura en el encabezado y 5,5% es la TSD SNI 2026.",
        key="pte_tasa",
    )

    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    inv_priv = c_m1.number_input("Inversión Privada Total ($)", min_value=1_000_000.0, value=2_000_000_000.0, step=100_000_000.0, format="%.0f", key="pte_inv")
    cp_viaje = c_m2.number_input("Costo Privado Operativo ($/viaje)", min_value=10.0, value=1000.0, step=50.0, key="pte_cp")
    iva_p = c_m3.number_input("IVA (%)", min_value=0.0, max_value=30.0, value=19.0, step=1.0, key="pte_iva") / 100.0
    arancel_p = c_m4.number_input("Arancel importados (%)", min_value=0.0, max_value=30.0, value=11.0, step=1.0, key="pte_ara") / 100.0

    c_f1, c_f2, c_f3, c_f4 = st.columns(4)
    fc_div_p = c_f1.number_input("Factor divisa (R*/e)", min_value=0.5, max_value=2.0, value=1.06, step=0.01, key="pte_div")
    fc_mosc_p = c_f2.number_input("FC MO Semicalificada", min_value=0.1, max_value=1.5, value=0.80, step=0.05, key="pte_mosc")
    fc_monc_p = c_f3.number_input("FC MO No Calificada", min_value=0.1, max_value=1.5, value=0.70, step=0.05, key="pte_monc")
    horizonte_p = c_f4.number_input("Horizonte finito comp. (años)", min_value=10, max_value=100, value=50, step=5, key="pte_hor")

    fc_imp = fc_div_p / ((1.0 + iva_p) * (1.0 + arancel_p))
    fc_nac = 1.0 / (1.0 + iva_p)

    # Desglose de Inversión (exacto al apunte)
    inv_items = [
        ("MO Calificada", 0.07, 1.00),
        ("MO Semicalificada", 0.09, fc_mosc_p),
        ("MO No Calificada", 0.17, fc_monc_p),
        ("Combustible (importado)", 0.05, fc_imp),
        ("Repuestos Importados", 0.20, fc_imp),
        ("Repuestos Nacionales", 0.15, fc_nac),
        ("Depreciación (no desembolsable)", 0.10, 0.00),
        ("Intereses / Gastos financieros", 0.05, fc_nac),
        ("Gastos Generales", 0.12, fc_nac),
    ]
    rows_inv = []
    for nombre, pct, fc in inv_items:
        cp_m = inv_priv * pct
        cs_m = cp_m * fc
        rows_inv.append(
            {
                "Componente": nombre,
                "%": f"{pct*100:.0f}%",
                "Costo Privado (MM$)": round(cp_m / 1e6, 2),
                "Factor Social": round(fc, 4),
                "Costo Social (MM$)": round(cs_m / 1e6, 2),
            }
        )
    df_inv = pd.DataFrame(rows_inv)
    inv_social = sum(inv_priv * pct * fc for _, pct, fc in inv_items)

    # Desglose de Costo Marginal Operativo (exacto al apunte)
    cmg_items = [
        ("MO Calificada", 0.08, 1.00),
        ("MO Semicalificada", 0.10, fc_mosc_p),
        ("MO No Calificada", 0.05, fc_monc_p),
        ("Combustible (importado)", 0.35, fc_imp),
        ("Repuestos Importados", 0.12, fc_imp),
        ("Repuestos Nacionales", 0.15, fc_nac),
        ("Depreciación (no desembolsable)", 0.05, 0.00),
        ("Intereses / Gastos financieros", 0.03, fc_nac),
        ("Gastos Generales", 0.07, fc_nac),
    ]
    rows_cmg = []
    for nombre, pct, fc in cmg_items:
        cp_u = cp_viaje * pct
        cs_u = cp_u * fc
        rows_cmg.append(
            {
                "Componente": nombre,
                "%": f"{pct*100:.0f}%",
                "Costo Privado ($/viaje)": round(cp_u, 2),
                "Factor Social": round(fc, 4),
                "Costo Social ($/viaje)": round(cs_u, 2),
            }
        )
    df_cmg = pd.DataFrame(rows_cmg)
    cmg_social = sum(cp_viaje * pct * fc for _, pct, fc in cmg_items)

    # Beneficios Sociales Anuales y VANS
    delta_q = max(0, q1 - q0)
    ad = delta_q * ((p0 + p1) / 2.0)
    lr = q0 * cmg_social
    vsp = ad + lr

    r = tasa_pct / 100.0
    va_perpetuo = vsp / r
    vans_perpetuo = -inv_social + va_perpetuo

    factor_finito = (1.0 - (1.0 + r) ** (-horizonte_p)) / r
    vans_finito = -inv_social + vsp * factor_finito

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Inversión Social (Is)", f"{_fmt_num(inv_social / 1e6, 2)} MM$")
    k2.metric("CMg Social (Oferta antigua)", f"{_fmt_clp(cmg_social, 2)}/viaje")
    k3.metric("VSP Anual (AD + LR)", f"{_fmt_num(vsp / 1e6, 3)} MM$/año")
    k4.metric(f"VANS Perpetuo ({tasa_pct:.1f}%)", f"{_fmt_num(vans_perpetuo / 1e6, 3)} MM$")

    st.info(
        f"**Descomposición exacta:** $\\text{{AD}} = {_fmt_clp(ad)}$ + $\\text{{LR}} = {_fmt_clp(lr)}$ "
        f"$\\Rightarrow$ $\\text{{VSP}} = {_fmt_clp(vsp)}/\\text{{año}}$.  \n"
        f"Con perpetuidad al **{tasa_pct:.1f}%**: $\\text{{VANS}} = -{_fmt_clp(inv_social)} + \\frac{{{_fmt_clp(vsp)}}}{{{r:.3f}}} = {_fmt_clp(vans_perpetuo)}$ "
        f"(en horizonte finito de {horizonte_p} años: **{_fmt_clp(vans_finito)}**)."
    )

    # Gráfico de áreas AD y LR (estilo pizarra / Goodnotes)
    pendiente = (p0 - p1) / (q1 - q0) if q1 > q0 else 0.0
    q_max_plot = q1 * 1.15
    q_line = np.linspace(0, q_max_plot, 120)
    p_line = np.maximum(0, p0 - pendiente * (q_line - q0))

    fig = go.Figure()
    # Área LR (rectángulo bajo CMg_s entre 0 y Q0)
    fig.add_trace(
        go.Scatter(
            x=[0, q0, q0, 0, 0],
            y=[0, 0, cmg_social, cmg_social, 0],
            fill="toself",
            fillcolor="rgba(236, 72, 153, 0.25)",
            line=dict(color="rgba(219, 39, 119, 0.9)", dash="dot"),
            name=f"LR = {_fmt_num(lr / 1e6, 2)} MM$",
        )
    )
    # Área AD (trapecio bajo demanda entre Q0 y Q1)
    fig.add_trace(
        go.Scatter(
            x=[q0, q1, q1, q0, q0],
            y=[0, 0, p1, p0, 0],
            fill="toself",
            fillcolor="rgba(59, 130, 246, 0.30)",
            line=dict(color="rgba(37, 99, 235, 0.9)"),
            name=f"AD = {_fmt_num(ad / 1e6, 2)} MM$",
        )
    )
    # Curva de demanda
    fig.add_trace(
        go.Scatter(
            x=q_line,
            y=p_line,
            mode="lines",
            line=dict(color="#0F172A", width=2.5),
            name="Demanda de viajes",
        )
    )
    # Línea horizontal CMg social
    fig.add_hline(
        y=cmg_social,
        line_dash="dash",
        line_color="#DB2777",
        annotation_text=f"CMg Social = {_fmt_clp(cmg_social, 2)}",
        annotation_position="top right",
    )
    fig.update_layout(
        title="Valor Social del Puente: Liberación de Recursos (LR) y Aumento en Disponibilidad (AD)",
        xaxis_title="Cantidad de viajes anuales (Q)",
        yaxis_title="Precio / Costo por viaje ($ CLP)",
        template="plotly_white",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.markdown("**Tabla de Inversión Privada vs. Social (MM$)**")
        st.dataframe(df_inv, use_container_width=True, hide_index=True)
    with t_col2:
        st.markdown("**Tabla de Costo Marginal Operativo ($/viaje)**")
        st.dataframe(df_cmg, use_container_width=True, hide_index=True)


def _render_bloque_economia_abierta_divisas():
    st.subheader("3. Simulador de Economía Abierta y Ahorro de Divisas (SNI 2026)")
    st.caption(
        "Evaluación social de un proyecto de sustitución de importaciones donde el beneficio social proviene del "
        "ahorro de divisas a precio internacional (CIF), aplicando los Precios Sociales SNI 2026."
    )

    c1, c2, c3, c4 = st.columns(4)
    q_ton = c1.number_input("Producción anual (ton/año)", min_value=100.0, value=8000.0, step=500.0, key="div_q")
    p_int = c2.number_input("Precio Internacional CIF (US$/ton)", min_value=10.0, value=450.0, step=10.0, key="div_pint")
    horizonte = c3.number_input("Horizonte del proyecto (años)", min_value=1, max_value=100, value=40, step=5, key="div_hor")
    tsd_pct = c4.number_input("Tasa Social de Descuento (%)", min_value=0.5, max_value=20.0, value=5.5, step=0.5, key="div_tsd")

    c5, c6, c7, c8, c9 = st.columns(5)
    iva = c5.number_input("IVA (%)", min_value=0.0, max_value=30.0, value=19.0, step=1.0, key="div_iva") / 100.0
    arancel = c6.number_input("Arancel (%)", min_value=0.0, max_value=30.0, value=1.0, step=0.5, key="div_ara") / 100.0
    r_star_e = c7.number_input("Razón Divisa (R*/e)", min_value=0.5, max_value=1.5, value=1.00, step=0.01, key="div_fcsd")
    fc_moc = c8.number_input("FC MOC (SNI 2026)", min_value=0.5, max_value=1.2, value=0.97, step=0.01, key="div_moc")
    fc_monc = c9.number_input("FC MONC (SNI 2026)", min_value=0.5, max_value=1.2, value=0.91, step=0.01, key="div_monc")

    st.markdown("#### Estructura de Costos Operativos Unitarios (US$/ton) e Inversión Inicial (US$)")
    cu1, cu2, cu3, cu4 = st.columns(4)
    c_moc_u = cu1.number_input("MOC unitaria (US$/ton)", min_value=0.0, value=50.0, step=5.0, key="div_cmoc")
    c_nac_u = cu2.number_input("Insumo nacional c/IVA (US$/ton)", min_value=0.0, value=100.0, step=5.0, key="div_cnac")
    c_imp_u = cu3.number_input("Insumo importado c/IVA+Ar. (US$/ton)", min_value=0.0, value=100.0, step=5.0, key="div_cimp")
    c_monc_u = cu4.number_input("MONC unitaria (US$/ton)", min_value=0.0, value=150.0, step=5.0, key="div_cmonc")

    ci1, ci2 = st.columns(2)
    inv_imp = ci1.number_input("Inversión Maquinaria Importada c/IVA+Ar. (US$)", min_value=0.0, value=1_000_000.0, step=50_000.0, format="%.0f", key="div_inv_imp")
    inv_moc = ci2.number_input("Inversión Mano de Obra Calificada (US$)", min_value=0.0, value=400_000.0, step=25_000.0, format="%.0f", key="div_inv_moc")

    # Cálculos sociales unitarios
    cs_moc_u = c_moc_u * fc_moc
    cs_nac_u = c_nac_u / (1.0 + iva)
    cs_imp_u = (c_imp_u / ((1.0 + iva) * (1.0 + arancel))) * r_star_e
    cs_monc_u = c_monc_u * fc_monc
    cs_unitario = cs_moc_u + cs_nac_u + cs_imp_u + cs_monc_u

    # Flujos anuales
    vsp_anual = q_ton * p_int * r_star_e
    cs_anual = q_ton * cs_unitario
    bn_anual = vsp_anual - cs_anual

    # Inversión social
    is_imp = (inv_imp / ((1.0 + iva) * (1.0 + arancel))) * r_star_e
    is_moc = inv_moc * fc_moc
    inv_social_total = is_imp + is_moc

    # Valor Actual y VANS
    r_tsd = tsd_pct / 100.0
    factor_va = (1.0 - (1.0 + r_tsd) ** (-horizonte)) / r_tsd
    va_beneficios = bn_anual * factor_va
    vans = -inv_social_total + va_beneficios

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Costo Social Unitario", f"{_fmt_usd(cs_unitario)}/ton")
    m2.metric("Beneficio Neto Anual (BN)", _fmt_usd(bn_anual, 0))
    m3.metric("Inversión Social (Is)", _fmt_usd(inv_social_total, 2))
    m4.metric(f"VANS Corregido ({tsd_pct:.1f}%)", _fmt_usd(vans, 2))

    st.success(
        f"**Fórmula paso a paso:**  \n"
        f"- $\\text{{VSP}} = {_fmt_num(q_ton, 0)} \\times \\text{{US\\$}}{_fmt_num(p_int, 0)} \\times {r_star_e:.2f} = {_fmt_usd(vsp_anual, 0)}$  \n"
        f"- $\\text{{CS}} = {_fmt_num(q_ton, 0)} \\times {_fmt_usd(cs_unitario, 2)} = {_fmt_usd(cs_anual, 0)}$ "
        f"$\\Rightarrow$ $\\text{{BN}} = {_fmt_usd(bn_anual, 0)}/\\text{{año}}$  \n"
        f"- $\\text{{VA(BN)}} = {_fmt_usd(bn_anual, 0)} \\times \\frac{{1 - (1+{r_tsd:.3f})^{{-{int(horizonte)}}}}}{{{r_tsd:.3f}}} = {_fmt_usd(va_beneficios, 2)}$  \n"
        f"- $\\text{{VANS}} = -{_fmt_usd(inv_social_total, 2)} + {_fmt_usd(va_beneficios, 2)} = {_fmt_usd(vans, 2)}$"
    )

    st.warning(
        "**Nota de verificación para certamen:** En el apunte manuscrito se obtuvo US$12.550.636 como resultado final, "
        "lo cual corresponde solo al **Valor Actual de los Beneficios Netos** sin descontar la Inversión Social inicial "
        f"({_fmt_usd(inv_social_total, 2)}). Al restarla, el VANS exacto es **{_fmt_usd(vans, 2)}**."
    )

    df_detalle = pd.DataFrame(
        [
            {"Bloque": "Operación (US$/ton)", "Ítem": "MO Calificada (MOC)", "Privado": c_moc_u, "Factor / Ajuste": f"× {fc_moc:.2f}", "Social": round(cs_moc_u, 2)},
            {"Bloque": "Operación (US$/ton)", "Ítem": "Insumo Nacional", "Privado": c_nac_u, "Factor / Ajuste": f"÷ {1+iva:.2f}", "Social": round(cs_nac_u, 2)},
            {"Bloque": "Operación (US$/ton)", "Ítem": "Insumo Importado", "Privado": c_imp_u, "Factor / Ajuste": f"÷ ({1+iva:.2f}×{1+arancel:.2f}) × {r_star_e:.2f}", "Social": round(cs_imp_u, 2)},
            {"Bloque": "Operación (US$/ton)", "Ítem": "MO No Calificada (MONC)", "Privado": c_monc_u, "Factor / Ajuste": f"× {fc_monc:.2f}", "Social": round(cs_monc_u, 2)},
            {"Bloque": "Inversión (US$)", "Ítem": "Maquinaria Importada", "Privado": inv_imp, "Factor / Ajuste": f"÷ ({1+iva:.2f}×{1+arancel:.2f}) × {r_star_e:.2f}", "Social": round(is_imp, 2)},
            {"Bloque": "Inversión (US$)", "Ítem": "MO Calificada Inversión", "Privado": inv_moc, "Factor / Ajuste": f"× {fc_moc:.2f}", "Social": round(is_moc, 2)},
        ]
    )
    st.dataframe(df_detalle, use_container_width=True, hide_index=True)


def renderizar_expansion_ambiental_puente_divisas():
    """Punto de entrada principal para enchufar como pestaña en consola_web.py."""
    st.markdown("### Módulo de Expansión FDIC26: Economía Ambiental, Puente en Perpetuidad y Ahorro de Divisas")
    t1, t2, t3 = st.tabs(
        [
            "1. Economía Ambiental, Bienes y SEIA",
            "2. Ejercicio Puente (Perpetuidad Fontaine)",
            "3. Ejercicio Economía Abierta (Divisas SNI 2026)",
        ]
    )
    with t1:
        _render_bloque_ambiental_seia()
    with t2:
        _render_bloque_puente_perpetuidad()
    with t3:
        _render_bloque_economia_abierta_divisas()


if __name__ == "__main__":
    st.set_page_config(
        page_title="Expansión FDIC26 — Ambiental, Puente y Divisas",
        layout="wide",
    )
    renderizar_expansion_ambiental_puente_divisas()
