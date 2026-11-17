# -*- coding: utf-8 -*-
"""
motor_explicador_vivo_proyectos.py — PANEL PEDAGÓGICO EN VIVO, RADAR DE QUIEBRE Y MODO DEFENSA
Asignatura: Evaluación Integrada de Proyectos (FDIC26) — Universidad de Los Lagos
Docente: Dra. Luz María Ferrada B.

Conecta en tiempo real las cifras que el estudiante simula en `consola_web.py` con:
1. Cascada explicativa exacta (Waterfall): VAN Privado -> VANS Social (efecto tasa,
   impuestos, precios sombra de mano de obra/divisa y liberación de recursos Curaco/GEI).
2. Radar de Punto de Quiebre (3 deslizadores de estrés + búsqueda exacta de VAN = $0).
3. Modo "Defiende tu Proyecto ante Comisión": 4 preguntas de examen generadas con los
   números actuales en pantalla y respuestas técnicas respaldadas en Fontaine, Sapag Chain y SNI 2026.
"""

import copy
import numpy as np
import numpy_financial as npf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _fmt_clp(valor: float) -> str:
    if valor < 0:
        return f"-${abs(int(round(valor))):,}".replace(",", ".")
    return f"${int(round(valor)):,}".replace(",", ".")


def _fmt_pct(valor: float, dec: int = 2) -> str:
    return f"{valor:.{dec}f}%".replace(".", ",")


def calcular_cascada_privado_a_social(cfg: dict, res_vivo: dict) -> dict:
    """
    Descompone con exactitud matemática al peso la transición entre el VAN Privado
    (a tasa privada) y el VAN Social SNI (a Tasa Social de Descuento).
    """
    tasa_priv = float(cfg["TASA_DESCUENTO_PRIVADA"])
    tasa_soc = float(cfg["TASA_DESCUENTO_SOCIAL"])

    df_fp = res_vivo["df_flujo_privado"]
    df_fs = res_vivo["df_flujo_social"]

    fc_priv = df_fp.loc["(=) FLUJO DE CAJA PRIVADO NETO"].values.astype(float)
    fc_soc = df_fs.loc["(=) FLUJO DE BENEFICIOS SOCIALES NETOS"].values.astype(float)

    van_priv = float(npf.npv(tasa_priv, fc_priv))
    van_soc = float(npf.npv(tasa_soc, fc_soc))

    # 1. Efecto Tasa de Descuento (mismo flujo privado, evaluado ahora a tasa social)
    van_priv_a_tsoc = float(npf.npv(tasa_soc, fc_priv))
    efecto_tasa = van_priv_a_tsoc - van_priv

    # 2. Efecto Eliminación de Impuesto a la Renta (transferencia interna al Estado)
    fila_imp = next((r for r in df_fp.index if "Impuesto a la Renta" in r), None)
    imp_vec = df_fp.loc[fila_imp].values.astype(float) if fila_imp else np.zeros_like(fc_priv)
    # imp_vec es negativo en el flujo privado; al quitarlo se suma -imp_vec
    fc_sin_imp = fc_priv - imp_vec
    van_sin_imp = float(npf.npv(tasa_soc, fc_sin_imp))
    efecto_impuestos = van_sin_imp - van_priv_a_tsoc

    # 3. Efecto Externalidades y Liberación de Recursos (Ahorro Curaco + Otros/GEI)
    ben_muni = df_fs.loc["(+) Liberación de Recursos Municipales (Ahorro Vertedero Curaco)"].values.astype(float)
    ben_otros = df_fs.loc["(+) Otros Beneficios Sociales y Ambientales"].values.astype(float)
    efecto_externalidades = float(npf.npv(tasa_soc, ben_muni + ben_otros))

    # 4. Efecto Precios Sombra (Mano de Obra MOC/MOSC/MONC, Divisa, Aranceles, CT y Valor Residual)
    efecto_precios_sombra = van_soc - (van_priv + efecto_tasa + efecto_impuestos + efecto_externalidades)

    return {
        "van_priv": round(van_priv),
        "efecto_tasa": round(efecto_tasa),
        "efecto_impuestos": round(efecto_impuestos),
        "efecto_precios_sombra": round(efecto_precios_sombra),
        "efecto_externalidades": round(efecto_externalidades),
        "van_soc": round(van_soc),
        "tasa_priv_pct": tasa_priv * 100.0,
        "tasa_soc_pct": tasa_soc * 100.0,
    }


def _evaluar_estres_cfg(
    cfg_base: dict,
    fn_motor,
    solo_ton_inc: bool,
    usar_pro_pyme: bool,
    ben_gei: float,
    delta_precio_pct: float = 0.0,
    delta_volumen_pct: float = 0.0,
    delta_costos_pct: float = 0.0,
) -> dict:
    """Aplica perturbaciones simultáneas sobre una copia de cfg sin alterar el estado principal."""
    cfg_s = copy.deepcopy(cfg_base)
    f_p = max(0.05, 1.0 + delta_precio_pct / 100.0)
    f_v = max(0.05, 1.0 + delta_volumen_pct / 100.0)
    f_c = max(0.10, 1.0 + delta_costos_pct / 100.0)

    cfg_s["P1_PRECIO_BRUTO"] = float(cfg_base["P1_PRECIO_BRUTO"]) * f_p
    cfg_s["P2_PRECIO_BRUTO"] = float(cfg_base["P2_PRECIO_BRUTO"]) * f_p
    cfg_s["P1_UNIDADES"] = max(1, int(round(float(cfg_base["P1_UNIDADES"]) * f_v)))
    cfg_s["P2_UNIDADES"] = max(1, int(round(float(cfg_base["P2_UNIDADES"]) * f_v)))
    cfg_s["RESIDUO_TON_ANIO_1"] = float(cfg_base["RESIDUO_TON_ANIO_1"]) * f_v

    for cv in cfg_s["COSTOS_VAR_LISTA"]:
        cv["costo"] = float(cv["costo"]) * f_c
    for cf in cfg_s["COSTOS_FIJOS_LISTA"]:
        cf["mensual"] = float(cf["mensual"]) * f_c
    for per in cfg_s["PERSONAL_LISTA"]:
        per["sueldo_bruto_mensual"] = float(per["sueldo_bruto_mensual"]) * f_c

    res_s = fn_motor(
        cfg_s,
        solo_ton_incorporadas=solo_ton_inc,
        usar_pro_pyme_escalonado=usar_pro_pyme,
        beneficio_gei_anual=ben_gei * f_v,
    )
    return res_s["metricas"]


def calcular_puntos_de_quiebre(
    cfg_base: dict,
    fn_motor,
    solo_ton_inc: bool,
    usar_pro_pyme: bool,
    ben_gei: float,
) -> dict:
    """
    Encuentra por bisección el porcentaje exacto de variación en Precios, Volumen y Costos
    que lleva el VAN Privado exactamente a $0 (Margen de Seguridad del Proyecto).
    """
    def _buscar_raiz(param_nombre: str, lo: float, hi: float) -> float:
        def _van_en(x: float) -> float:
            kw = {param_nombre: x}
            return float(_evaluar_estres_cfg(cfg_base, fn_motor, solo_ton_inc, usar_pro_pyme, ben_gei, **kw)["van_privado"])

        v_lo = _van_en(lo)
        v_hi = _van_en(hi)
        if v_lo * v_hi > 0:
            return hi if abs(v_hi) < abs(v_lo) else lo
        for _ in range(18):
            mid = 0.5 * (lo + hi)
            v_mid = _van_en(mid)
            if v_lo * v_mid <= 0:
                hi, v_hi = mid, v_mid
            else:
                lo, v_lo = mid, v_mid
        return 0.5 * (lo + hi)

    q_precio = _buscar_raiz("delta_precio_pct", -90.0, 100.0)
    q_volumen = _buscar_raiz("delta_volumen_pct", -90.0, 150.0)
    q_costos = _buscar_raiz("delta_costos_pct", -60.0, 150.0)

    return {
        "quiebre_precio_pct": round(q_precio, 1),
        "quiebre_volumen_pct": round(q_volumen, 1),
        "quiebre_costos_pct": round(q_costos, 1),
    }


def renderizar_panel_inteligente_superior(
    cfg: dict,
    res_vivo: dict,
    fn_motor,
    solo_ton_inc: bool,
    usar_pro_pyme: bool,
    ben_gei: float,
):
    """
    Renderiza el Panel Pedagógico Interactivo conectado en vivo a las cifras del simulador:
      - Sub-vista 1: Explícame Mis Números en Vivo (Cascada VAN Privado -> VANS Social).
      - Sub-vista 2: Radar de Punto de Quiebre (3 Sliders + Margen de Seguridad VAN = $0).
      - Sub-vista 3: Modo Defensa ante Comisión (4 preguntas dinámicas con respuestas modelo).
    """
    m = res_vivo["metricas"]
    casc = calcular_cascada_privado_a_social(cfg, res_vivo)

    st.markdown(
        "<div class='sec-header'>PANEL PEDAGÓGICO EN VIVO: COMPRENDE TUS NÚMEROS, ESTRESA EL PROYECTO Y PREPARA TU DEFENSA</div>",
        unsafe_allow_html=True,
    )

    p_casc, p_radar, p_def = st.tabs([
        "1. Explícame Mis Números en Vivo (Puente VAN -> VANS)",
        "2. Radar de Punto de Quiebre (3 Sliders y Margen de Seguridad)",
        "3. Defiende tu Proyecto ante Comisión (Preguntas con Tus Cifras)",
    ])

    # --------------------------------------------------------------------------
    # VISTA 1: CASCADA EXPLICATIVA VAN PRIVADO -> VANS SOCIAL
    # --------------------------------------------------------------------------
    with p_casc:
        c_g, c_txt = st.columns([1.45, 1.05])
        with c_g:
            fig_wf = go.Figure(
                go.Waterfall(
                    name="Puente Privado a Social",
                    orientation="v",
                    measure=["absolute", "relative", "relative", "relative", "relative", "total"],
                    x=[
                        f"VAN Privado\n({casc['tasa_priv_pct']:.1f}%)",
                        f"Efecto Tasa\n({casc['tasa_priv_pct']:.1f}% -> {casc['tasa_soc_pct']:.1f}%)",
                        "Sin Impuesto\na la Renta",
                        "Precios Sombra\n(MO y Divisa)",
                        "Ahorro Curaco\ny Externalidades",
                        f"VANS Social\n({casc['tasa_soc_pct']:.1f}%)",
                    ],
                    y=[
                        casc["van_priv"],
                        casc["efecto_tasa"],
                        casc["efecto_impuestos"],
                        casc["efecto_precios_sombra"],
                        casc["efecto_externalidades"],
                        casc["van_soc"],
                    ],
                    text=[
                        _fmt_clp(casc["van_priv"]),
                        f"+{_fmt_clp(casc['efecto_tasa'])}" if casc["efecto_tasa"] >= 0 else _fmt_clp(casc["efecto_tasa"]),
                        f"+{_fmt_clp(casc['efecto_impuestos'])}" if casc["efecto_impuestos"] >= 0 else _fmt_clp(casc["efecto_impuestos"]),
                        f"+{_fmt_clp(casc['efecto_precios_sombra'])}" if casc["efecto_precios_sombra"] >= 0 else _fmt_clp(casc["efecto_precios_sombra"]),
                        f"+{_fmt_clp(casc['efecto_externalidades'])}" if casc["efecto_externalidades"] >= 0 else _fmt_clp(casc["efecto_externalidades"]),
                        _fmt_clp(casc["van_soc"]),
                    ],
                    textposition="outside",
                    connector={"line": {"color": "#94A3B8", "width": 1.2}},
                    increasing={"marker": {"color": "#0F766E"}},
                    decreasing={"marker": {"color": "#B91C1C"}},
                    totals={"marker": {"color": "#1E293B"}},
                )
            )
            fig_wf.update_layout(
                title="De Rentabilidad Privada a Bienestar Social (Descomposición Exacta en Vivo)",
                yaxis_title="Valor Presente ($ CLP)",
                height=390,
                margin=dict(l=15, r=15, t=45, b=20),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#F8FAFC",
            )
            st.plotly_chart(fig_wf, use_container_width=True)

        with c_txt:
            st.markdown("##### Qué explica la diferencia entre tus dos VAN hoy")
            brecha_tot = casc["van_soc"] - casc["van_priv"]
            st.info(
                f"Tu **VANS Social ({_fmt_clp(casc['van_soc'])})** supera al **VAN Privado ({_fmt_clp(casc['van_priv'])})** "
                f"en **{_fmt_clp(brecha_tot)}**. Este salto se explica por 4 fundamentos teóricos:"
            )
            st.markdown(
                f"* **1. Tasa de Descuento ({_fmt_clp(casc['efecto_tasa'])}):** Al evaluar el mismo flujo con la TSD del Estado "
                f"({casc['tasa_soc_pct']:.1f}% vs. {casc['tasa_priv_pct']:.1f}% privado), los flujos de los años 5 al {cfg['HORIZONTE_ANIOS']} pesan mucho más.\n"
                f"* **2. Impuestos ({_fmt_clp(casc['efecto_impuestos'])}):** En evaluación social (Fontaine / SNI), el Impuesto a la Renta es una "
                f"**transferencia interna** desde la empresa al Fisco, no un consumo real de recursos del país.\n"
                f"* **3. Precios Sombra ({_fmt_clp(casc['efecto_precios_sombra'])}):** Los sueldos ajustados por factores SNI "
                f"(MOC {cfg['FC_MOC']}, MOSC {cfg['FC_MOSC']}, MONC {cfg['FC_MONC']}) y la eliminación de aranceles reducen el costo de oportunidad social.\n"
                f"* **4. Liberación de Recursos ({_fmt_clp(casc['efecto_externalidades'])}):** Ahorro municipal por desviar cartón del Vertedero de Curaco "
                f"({'criterio conservador 70% incorporado' if solo_ton_inc else 'sobre 100% recolectado'})."
            )

    # --------------------------------------------------------------------------
    # VISTA 2: RADAR DE PUNTO DE QUIEBRE (3 SLIDERS + BISECCIÓN EXACTA)
    # --------------------------------------------------------------------------
    with p_radar:
        st.caption(
            "Mueve estos 3 deslizadores para someter tu proyecto a pruebas de estrés instantáneas "
            "sin sobrescribir tus parámetros guardados abajo."
        )
        s1, s2, s3 = st.columns(3)
        d_precio = s1.slider("Variación Precio de Venta (%):", -40, 30, 0, 1, key="radar_dp")
        d_vol = s2.slider("Variación Volumen / Demanda (%):", -50, 40, 0, 1, key="radar_dv")
        d_cos = s3.slider("Variación Costos y Sueldos (%):", -20, 50, 0, 1, key="radar_dc")

        m_est = _evaluar_estres_cfg(
            cfg, fn_motor, solo_ton_inc, usar_pro_pyme, ben_gei,
            delta_precio_pct=float(d_precio),
            delta_volumen_pct=float(d_vol),
            delta_costos_pct=float(d_cos),
        )

        rk1, rk2, rk3, rk4 = st.columns(4)
        rk1.metric(
            "VAN Privado Estresado",
            _fmt_clp(m_est["van_privado"]),
            f"{_fmt_clp(m_est['van_privado'] - m['van_privado'])} vs base",
        )
        rk2.metric(
            "TIR Privada Estresada",
            _fmt_pct(m_est["tir_privada"], 2),
            "VIABLE" if m_est["van_privado"] > 0 else "INVIABLE (VAN < 0)",
        )
        rk3.metric(
            "VANS Social Estresado",
            _fmt_clp(m_est["van_social"]),
            f"{_fmt_clp(m_est['van_social'] - m['van_social'])} vs base",
        )
        rk4.metric(
            "TIRS Social Estresada",
            _fmt_pct(m_est["tir_social"], 2),
            "RS FAVORABLE" if m_est["van_social"] > 0 else "RECHAZO SOCIAL",
        )

        quiebres = calcular_puntos_de_quiebre(cfg, fn_motor, solo_ton_inc, usar_pro_pyme, ben_gei)

        cq1, cq2 = st.columns([1.25, 1.15])
        with cq1:
            vars_q = ["Caída máxima de Precios", "Caída máxima de Volumen", "Alza máxima de Costos/Sueldos"]
            margenes_abs = [
                abs(quiebres["quiebre_precio_pct"]),
                abs(quiebres["quiebre_volumen_pct"]),
                abs(quiebres["quiebre_costos_pct"]),
            ]
            etiquetas_q = [
                f"{quiebres['quiebre_precio_pct']:+.1f}%",
                f"{quiebres['quiebre_volumen_pct']:+.1f}%",
                f"{quiebres['quiebre_costos_pct']:+.1f}%",
            ]
            fig_q = go.Figure(
                go.Bar(
                    x=margenes_abs,
                    y=vars_q,
                    orientation="h",
                    text=etiquetas_q,
                    textposition="outside",
                    marker_color=["#262626", "#404040", "#0F766E"],
                )
            )
            fig_q.update_layout(
                title="Margen de Seguridad Exacto antes de que VAN Privado = $0",
                xaxis_title="Holgura porcentual soportada (%)",
                height=260,
                margin=dict(l=10, r=40, t=42, b=20),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#F8FAFC",
            )
            st.plotly_chart(fig_q, use_container_width=True)

        with cq2:
            st.markdown("##### Lectura del Punto de Quiebre (Para tu Informe y Defensa)")
            st.markdown(
                f"* **Resistencia a caída de precios:** El proyecto soporta hasta una baja de **{abs(quiebres['quiebre_precio_pct']):.1f}%** "
                f"en los precios de venta antes de llegar a VAN Privado = $0.\n"
                f"* **Resistencia a menor demanda:** Tolera vender hasta **{abs(quiebres['quiebre_volumen_pct']):.1f}% menos unidades** "
                f"sin destruir valor para el inversionista.\n"
                f"* **Resistencia a alza de costos:** Aguanta un aumento simultáneo de hasta **+{abs(quiebres['quiebre_costos_pct']):.1f}%** "
                f"en insumos, arriendos y sueldos manteniendo viabilidad privada."
            )

    # --------------------------------------------------------------------------
    # VISTA 3: MODO DEFIENDE TU PROYECTO ANTE COMISIÓN (CON TUS NÚMEROS REALES)
    # --------------------------------------------------------------------------
    with p_def:
        st.caption(
            "Preguntas reales de comisión evaluadora armadas dinámicamente con las cifras vigentes de tu simulación. "
            "Intenta responder primero mentalmente y luego despliega la pauta técnica."
        )
        dias_ct = int(cfg.get("DIAS_DESFASE_CT", 45))
        ct_ini = m["ct_inicial"]
        inv_ini = m["inv_inicial_priv"]
        quiebres_def = calcular_puntos_de_quiebre(cfg, fn_motor, solo_ton_inc, usar_pro_pyme, ben_gei)

        with st.expander(f"Pregunta 1: Su VANS Social ({_fmt_clp(m['van_social'])}) es muy superior al VAN Privado ({_fmt_clp(m['van_privado'])}). ¿No están inflando beneficios sociales?"):
            st.markdown(
                f"**Respuesta técnica (Fontaine & SNI 2026):** No existe sobreestimación porque la brecha de **{_fmt_clp(m['van_social'] - m['van_privado'])}** "
                f"proviene de ajustes normativos verificables:\n"
                f"1. **Tasa Social ({casc['tasa_soc_pct']:.1f}% vs {casc['tasa_priv_pct']:.1f}%):** Aporta **{_fmt_clp(casc['efecto_tasa'])}** al reflejar el menor costo de oportunidad social del capital.\n"
                f"2. **Eliminación de transferencias (Impuesto a la Renta):** Aporta **{_fmt_clp(casc['efecto_impuestos'])}** porque los impuestos no consumen recursos reales.\n"
                f"3. **Precios sombra de mano de obra y divisa:** Aportan **{_fmt_clp(casc['efecto_precios_sombra'])}** usando factores oficiales SNI 2026 (MOC {cfg['FC_MOC']}, MOSC {cfg['FC_MOSC']}, MONC {cfg['FC_MONC']}).\n"
                f"4. **Liberación de recursos municipales en Curaco:** Aporta **{_fmt_clp(casc['efecto_externalidades'])}** bajo criterio "
                f"{'conservador (solo sobre el 70% efectivamente incorporado en productos y $0 en otros beneficios no cuantificados)' if solo_ton_inc else 'de desviación total del residuo recolectado'}."
            )

        with st.expander(f"Pregunta 2: ¿Por qué exigen {_fmt_clp(ct_ini)} de Capital de Trabajo en el Año 0 si el proyecto factura desde el Año 1?"):
            st.markdown(
                f"**Respuesta técnica (Sapag Chain & Clase 1, láminas 17–18):** Porque en ventas institucionales (DAEM Osorno vía Compra Ágil / fondos SEP y jardines), "
                f"el pago de facturas tarda entre 30 y 45 días mientras el taller debe pagar puntualmente sueldos, arriendo en Ovejería, fletes y pinturas al agua. "
                f"Aplicando el **Método del Período de Desfase** ($CT = \\frac{{\\text{{Costo Operacional Anual}}}}{{365}} \\times {dias_ct}\\text{{ días}}$), "
                f"se inmovilizan **{_fmt_clp(ct_ini)}** en $t=0$ (adicionales a los **{_fmt_clp(inv_ini)}** netos en activos fijos), fondo que se recupera íntegramente al término del Año {cfg['HORIZONTE_ANIOS']}."
            )

        with st.expander("Pregunta 3: ¿Qué pasa si las ventas se estancan o caen los precios? ¿Cuál es su variable más sensible?"):
            st.markdown(
                f"**Respuesta técnica (Sensibilidad y Punto de Quiebre):** La variable más crítica es el **precio de venta**, donde el proyecto mantiene "
                f"VAN Privado positivo hasta una caída de **{abs(quiebres_def['quiebre_precio_pct']):.1f}%**. En volumen soporta una caída de hasta "
                f"**{abs(quiebres_def['quiebre_volumen_pct']):.1f}%** y en costos/sueldos tolera un alza simultánea de **+{abs(quiebres_def['quiebre_costos_pct']):.1f}%**. "
                f"Esto demuestra que la viabilidad no depende exclusivamente del supuesto de crecimiento anual de {float(cfg['TASA_CRECIMIENTO'])*100:.1f}%."
            )

        with st.expander(f"Pregunta 4: Presentaron VANS ({_fmt_clp(m['van_social'])}) y también CAE por tonelada ({_fmt_clp(m['cae_por_ton_social'])}/t). ¿Cuándo manda cada indicador en el SNI?"):
            st.markdown(
                "**Respuesta técnica (Metodología General SNI 2025 & Metodología GIRS):**\n"
                "- **VAN / VANS:** Es el criterio principal cuando los beneficios son medibles y valorables monetariamente y las alternativas tienen igual horizonte.\n"
                "- **VAC:** Se usa cuando los beneficios son idénticos o difíciles de valorar y las alternativas comparten la misma vida útil.\n"
                f"- **CAE y CAE/tonelada ({_fmt_clp(m['cae_por_ton_social'])}/t):** Es obligatorio en el enfoque costo-eficiencia GIRS cuando se comparan alternativas tecnológicas con **distinta vida útil** o **distinto volumen anual procesado**."
            )
