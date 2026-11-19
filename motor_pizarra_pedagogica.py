# -*- coding: utf-8 -*-
"""
motor_pizarra_pedagogica_sni.py — LABORATORIO ANIMADO Y PIZARRA PEDAGÓGICA (FDIC26 - ULAGOS)
Módulo independiente conectado a consola_web.py con gráficos interactivos paso a paso,
animaciones con Plotly Frames (Reproducir/Pausa) y sliders en tiempo real para:
  1) Semáforo Jerárquico de Indicadores (1° a 5° Prioridad CEPAL N° 39 / SNI).
  2) Mercado de la Leche (Constructor Paso 1-5 + Animación de Desplazamiento + Sliders A, B, C, D, Q_proy).
  3) Laboratorio de los 4 Casos Extremos de Elasticidad (morfología en vivo % AD vs. % LR).
  4) Simulador Gráfico de Externalidades y Monopolio en Transporte (CmgP vs. CmgS).
  5) Anatomía Matemática de Precios Sociales SNI 2026 (TSD, PSMO, FCSD, VST 1x/2x, Combustibles).
  6) Ciclo SNI (IDI/BIP) y Gráfico Animado a 10 años del Déficit de Agua Potable (CEPAL N° 39).
  7) Los 6 Casos Clásicos de Examen y Compendio Matemático Interactivo (TEA y CAPM).
"""

import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _fmt_clp(valor):
    if isinstance(valor, (int, float, np.integer, np.floating)):
        if valor < 0:
            return f"-${abs(int(round(valor))):,}".replace(",", ".")
        return f"${int(round(valor)):,}".replace(",", ".")
    return str(valor)


def _fmt_dec(valor, dec=2):
    if isinstance(valor, (int, float, np.integer, np.floating)):
        s = f"{valor:,.{dec}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    return str(valor)


# ==============================================================================
# 1. SEMÁFORO DE JERARQUÍA ESTRICTA DE INDICADORES (1° A 5° PRIORIDAD CEPAL/SNI)
# ==============================================================================

def renderizar_semaforo_jerarquia_cepal(res_vivo, cfg):
    m = res_vivo["metricas"]
    tasa_p = float(cfg.get("TASA_DESCUENTO_PRIVADA", 0.12)) * 100.0
    tasa_s = float(cfg.get("TASA_DESCUENTO_SOCIAL", 0.055)) * 100.0

    with st.expander("Guía Pedagógica en Vivo: Jerarquía Estricta de Indicadores (1° a 5° Prioridad CEPAL N° 39 / SNI)", expanded=False):
        st.markdown(
            "En evaluación privada y social los indicadores cuantitativos **no tienen la misma ponderación**. "
            "La decisión de inversión sigue este orden jerárquico estricto:"
        )
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(
                f"""
                <div style="background:#EFF6FF;border-left:4px solid #1D4ED8;padding:10px;border-radius:6px;min-height:178px;">
                    <div style="font-weight:700;color:#1E3A8A;font-size:12px;">1° PRIORIDAD (Criterio Rector)</div>
                    <div style="font-weight:700;color:#0F172A;font-size:13px;margin-top:6px;">VAN: {_fmt_clp(m['van_privado'])}</div>
                    <div style="font-weight:700;color:#15803D;font-size:13px;">VANS: {_fmt_clp(m['van_social'])}</div>
                    <div style="color:#334155;font-size:11.5px;margin-top:6px;line-height:1.35;">
                        Indicador decisivo. Mide riqueza neta incremental en moneda de hoy (VAN &gt; 0). Cumple <b>aditividad y separabilidad</b>.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                <div style="background:#F0FDF4;border-left:4px solid #15803D;padding:10px;border-radius:6px;min-height:178px;">
                    <div style="font-weight:700;color:#166534;font-size:12px;">2° PRIORIDAD (Tasa Descuento)</div>
                    <div style="font-weight:700;color:#0F172A;font-size:13px;margin-top:6px;">WACC / k: {_fmt_dec(tasa_p, 1)}%</div>
                    <div style="font-weight:700;color:#15803D;font-size:13px;">TSD (k*): {_fmt_dec(tasa_s, 1)}%</div>
                    <div style="color:#334155;font-size:11.5px;margin-top:6px;line-height:1.35;">
                        Costo de oportunidad ajustado por riesgo (CAPM/WACC) o preferencia temporal social (TSD = 5,5%).
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""
                <div style="background:#FEFCE8;border-left:4px solid #CA8A04;padding:10px;border-radius:6px;min-height:178px;">
                    <div style="font-weight:700;color:#854D0E;font-size:12px;">3° PRIORIDAD (Complementario)</div>
                    <div style="font-weight:700;color:#0F172A;font-size:13px;margin-top:6px;">TIR: {_fmt_dec(m['tir_privada'], 2)}%</div>
                    <div style="font-weight:700;color:#15803D;font-size:13px;">TIRS: {_fmt_dec(m['tir_social'], 2)}%</div>
                    <div style="color:#334155;font-size:11.5px;margin-top:6px;line-height:1.35;">
                        Tasa que iguala VAN = 0. <b>Precaución:</b> falla en proyectos excluyentes de distinta escala, vida útil o flujos no convencionales.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                """
                <div style="background:#FFF7ED;border-left:4px solid #EA580C;padding:10px;border-radius:6px;min-height:178px;">
                    <div style="font-weight:700;color:#9A3412;font-size:12px;">4° PRIORIDAD (Análisis Riesgo)</div>
                    <div style="font-weight:700;color:#0F172A;font-size:13px;margin-top:6px;">Sensibilidad y E[X]</div>
                    <div style="font-weight:700;color:#9A3412;font-size:13px;">Desvío σ y Beta (β)</div>
                    <div style="color:#334155;font-size:11.5px;margin-top:6px;line-height:1.35;">
                        Evalúa robustez del VAN frente a caídas de ingresos (-15%), alzas de costos (+10%) o crecimiento 0%.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c5:
            st.markdown(
                f"""
                <div style="background:#FEF2F2;border-left:4px solid #DC2626;padding:10px;border-radius:6px;min-height:178px;">
                    <div style="font-weight:700;color:#991B1B;font-size:12px;">5° PRIORIDAD (Liquidez)</div>
                    <div style="font-weight:700;color:#0F172A;font-size:13px;margin-top:6px;">PR Priv: {_fmt_dec(m['payback_privado'], 2)} años</div>
                    <div style="font-weight:700;color:#15803D;font-size:13px;">PR Soc: {_fmt_dec(m['payback_social'], 2)} años</div>
                    <div style="color:#334155;font-size:11.5px;margin-top:6px;line-height:1.35;">
                        Criterio auxiliar. <b>Es el menos confiable</b> por ignorar todos los flujos posteriores al recupero.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==============================================================================
# 2. SUB-TAB A: MERCADO DE LA LECHE (ANIMADO + PASO A PASO), ELASTICIDADES Y TRANSPORTE
# ==============================================================================

def _construir_figura_leche_interactiva(a_d, b_d, c_o, d_o, q_coop, modo_viz, paso_actual, usar_redondeo):
    q0_ex = (a_d - c_o) / (b_d + d_o)
    p0_ex = a_d - b_d * q0_ex
    q1_ex = (a_d - c_o + d_o * q_coop) / (b_d + d_o)
    p1_ex = a_d - b_d * q1_ex
    qo1_ex = q1_ex - q_coop

    if usar_redondeo and abs(a_d - 300.0) < 1e-6 and abs(b_d - 0.0205) < 1e-6 and abs(c_o + 50.0) < 1e-6 and abs(d_o - 0.025) < 1e-6 and abs(q_coop - 1470.0) < 1e-3:
        q0, p0, q1, p1, qo1 = 7692.0, 142.0, 8500.0, 126.0, 7030.0
    else:
        q0, p0, q1, p1, qo1 = q0_ex, p0_ex, q1_ex, p1_ex, qo1_ex

    x_min = max(0.0, min(qo1, q0) - max(1500.0, q_coop * 1.1))
    x_max = max(q1, q0) + max(1500.0, q_coop * 1.1)
    y_max = max(a_d * 1.05, p0 * 1.45, 220.0)
    q_grid = np.linspace(x_min, x_max, 120)
    pd_line = a_d - b_d * q_grid
    po_line = c_o + d_o * q_grid

    def _trazas_para_fraccion(frac, mostrar_o1=True, mostrar_ad=True, mostrar_lr=True):
        q_p = q_coop * frac
        q1_f = (a_d - c_o + d_o * q_p) / (b_d + d_o) if frac < 1.0 else q1
        p1_f = (a_d - b_d * q1_f) if frac < 1.0 else p1
        qo1_f = (q1_f - q_p) if frac < 1.0 else qo1

        po1_f = c_o + d_o * (q_grid - q_p) if mostrar_o1 else [None] * len(q_grid)

        # Separar rectángulos y triángulos para máxima claridad pedagógica
        if mostrar_lr and q_p > 1e-3:
            lr_rect_x = [qo1_f, q0, q0, qo1_f, qo1_f]
            lr_rect_y = [0, 0, p1_f, p1_f, 0]
            lr_tri_x = [qo1_f, q0, q0, qo1_f]
            lr_tri_y = [p1_f, p1_f, p0, p1_f]
        else:
            lr_rect_x, lr_rect_y, lr_tri_x, lr_tri_y = [q0], [0], [q0], [p0]

        if mostrar_ad and q_p > 1e-3:
            ad_rect_x = [q0, q1_f, q1_f, q0, q0]
            ad_rect_y = [0, 0, p1_f, p1_f, 0]
            ad_tri_x = [q0, q1_f, q0, q0]
            ad_tri_y = [p1_f, p1_f, p0, p1_f]
        else:
            ad_rect_x, ad_rect_y, ad_tri_x, ad_tri_y = [q0], [0], [q0], [p0]

        pts_x = [q0]
        pts_y = [p0]
        pts_txt = [f"E0 ({_fmt_dec(q0, 0)}; ${_fmt_dec(p0, 1)})"]
        if mostrar_o1 and q_p > 1e-3:
            pts_x.extend([q1_f, qo1_f])
            pts_y.extend([p1_f, p1_f])
            pts_txt.extend([
                f"E1 ({_fmt_dec(q1_f, 0)}; ${_fmt_dec(p1_f, 1)})",
                f"Qo1 ({_fmt_dec(qo1_f, 0)})",
            ])

        return [
            go.Scatter(x=lr_rect_x, y=lr_rect_y, fill="toself", fillcolor="rgba(37, 99, 235, 0.25)", line=dict(color="#1D4ED8", width=1.2), name="LR: Rectángulo (P1·ΔQo)"),
            go.Scatter(x=lr_tri_x, y=lr_tri_y, fill="toself", fillcolor="rgba(30, 64, 175, 0.50)", line=dict(color="#1E3A8A", width=1.2), name="LR: Triángulo Productores"),
            go.Scatter(x=ad_rect_x, y=ad_rect_y, fill="toself", fillcolor="rgba(220, 38, 38, 0.22)", line=dict(color="#DC2626", width=1.2), name="AD: Rectángulo (P1·ΔQd)"),
            go.Scatter(x=ad_tri_x, y=ad_tri_y, fill="toself", fillcolor="rgba(185, 28, 28, 0.50)", line=dict(color="#991B1B", width=1.2), name="AD: Triángulo Consumidores"),
            go.Scatter(x=q_grid, y=pd_line, mode="lines", name=f"Demanda (Pd = {a_d:.0f} - {b_d:.4f}·Q)", line=dict(color="#0F172A", width=2.6)),
            go.Scatter(x=q_grid, y=po_line, mode="lines", name=f"Oferta Inicial (Po = {c_o:+.0f} + {d_o:.4f}·Q)", line=dict(color="#1D4ED8", width=2.4)),
            go.Scatter(x=q_grid, y=po1_f, mode="lines", name="Oferta Con Proyecto (O' = Q + Q_proy)", line=dict(color="#15803D", width=2.6, dash="dash")),
            go.Scatter(
                x=pts_x, y=pts_y, mode="markers+text", text=pts_txt,
                textposition="top center",
                marker=dict(size=9, color="#0F172A", line=dict(color="#FFFFFF", width=1.5)),
                textfont=dict(size=11, color="#0F172A"),
                name="Puntos de Equilibrio",
                showlegend=False,
            ),
        ]

    if modo_viz == "Animación Continua (Botón Reproducir)":
        pasos_anim = np.linspace(0.0, 1.0, 21)
        fig = go.Figure(data=_trazas_para_fraccion(0.0, mostrar_o1=True, mostrar_ad=True, mostrar_lr=True))
        frames = [
            go.Frame(
                data=_trazas_para_fraccion(f, mostrar_o1=True, mostrar_ad=True, mostrar_lr=True),
                name=f"{int(round(f * 100))}%",
            )
            for f in pasos_anim
        ]
        fig.frames = frames
        fig.update_layout(
            updatemenus=[{
                "type": "buttons",
                "showactive": False,
                "x": 0.0,
                "y": 1.16,
                "buttons": [
                    {
                        "label": "▶ Reproducir desplazamiento (0% -> 100%)",
                        "method": "animate",
                        "args": [None, {"frame": {"duration": 140, "redraw": True}, "fromcurrent": True, "transition": {"duration": 60}}],
                    },
                    {
                        "label": "⏸ Pausar",
                        "method": "animate",
                        "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                    },
                ],
            }],
            sliders=[{
                "active": 0,
                "y": -0.14,
                "currentvalue": {"prefix": "Entrada del proyecto al mercado: ", "font": {"size": 12}},
                "steps": [
                    {
                        "label": f"{int(round(f * 100))}%",
                        "method": "animate",
                        "args": [[f"{int(round(f * 100))}%"], {"frame": {"duration": 80, "redraw": True}, "mode": "immediate"}],
                    }
                    for f in pasos_anim
                ],
            }],
            margin=dict(t=95, b=85),
        )
    else:
        # Modo Constructor Pedagógico Paso 1 al 5
        mostrar_o1 = paso_actual >= 2
        mostrar_ad = paso_actual >= 3
        mostrar_lr = paso_actual >= 4
        fig = go.Figure(data=_trazas_para_fraccion(1.0 if mostrar_o1 else 0.0, mostrar_o1=mostrar_o1, mostrar_ad=mostrar_ad, mostrar_lr=mostrar_lr))
        fig.update_layout(margin=dict(t=75, b=50))

    # Líneas punteadas guía hacia los ejes
    fig.add_hline(y=p0, line_dash="dot", line_color="#94A3B8", line_width=1)
    if modo_viz == "Animación Continua (Botón Reproducir)" or paso_actual >= 2:
        fig.add_hline(y=p1, line_dash="dot", line_color="#15803D", line_width=1)

    fig.update_layout(
        xaxis_title="Cantidad Q (ton/año)",
        yaxis_title="Precio P ($/ton)",
        xaxis=dict(range=[x_min, x_max]),
        yaxis=dict(range=[0, y_max]),
        template="plotly_white",
        height=490,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10.5)),
    )
    return fig, (q0, p0, q1, p1, qo1)


def _render_seccion_leche_animada():
    st.markdown("<div class='sec-header'>A. PIZARRA ANIMADA PASO A PASO: MERCADO DE LA LECHE Y VALOR SOCIAL DE LA PRODUCCIÓN (CLASE 2)</div>", unsafe_allow_html=True)

    # Inicializar presets editables en session_state
    if "piz_A" not in st.session_state:
        st.session_state.piz_A = 300.0
        st.session_state.piz_B = 0.0205
        st.session_state.piz_C = -50.0
        st.session_state.piz_D = 0.0250
        st.session_state.piz_Q = 1470.0

    bp1, bp2, bp3 = st.columns(3)
    if bp1.button("Preset 1: Apuntes de Pizarra (Po = -50 + 0,025Q)", use_container_width=True):
        st.session_state.piz_A, st.session_state.piz_B, st.session_state.piz_C, st.session_state.piz_D, st.session_state.piz_Q = 300.0, 0.0205, -50.0, 0.0250, 1470.0
        st.rerun()
    if bp2.button("Preset 2: Variante Intercepto Positivo (Po = +50 + 0,025Q)", use_container_width=True):
        st.session_state.piz_A, st.session_state.piz_B, st.session_state.piz_C, st.session_state.piz_D, st.session_state.piz_Q = 300.0, 0.0205, 50.0, 0.0250, 1470.0
        st.rerun()
    if bp3.button("Preset 3: Demanda Más Inelástica (Pendiente B = 0,045)", use_container_width=True):
        st.session_state.piz_A, st.session_state.piz_B, st.session_state.piz_C, st.session_state.piz_D, st.session_state.piz_Q = 480.0, 0.0450, -50.0, 0.0250, 1470.0
        st.rerun()

    # Sliders en vivo para alterar todas las variables del mercado
    st.markdown("**Controles de Variables en Tiempo Real (Mueve cualquier parámetro para ver el impacto en el gráfico y en las fórmulas):**")
    s1, s2, s3, s4, s5 = st.columns(5)
    a_d = s1.slider("Intercepto Demanda (A)", 150.0, 600.0, float(st.session_state.piz_A), step=10.0)
    b_d = s2.slider("Pendiente Demanda (B)", 0.0050, 0.0600, float(st.session_state.piz_B), step=0.0005, format="%.4f")
    c_o = s3.slider("Intercepto Oferta (C)", -150.0, 150.0, float(st.session_state.piz_C), step=10.0)
    d_o = s4.slider("Pendiente Oferta (D)", 0.0050, 0.0600, float(st.session_state.piz_D), step=0.0005, format="%.4f")
    q_coop = s5.slider("Producción Proyecto (Q_proy)", 200.0, 3500.0, float(st.session_state.piz_Q), step=10.0)

    c_mod1, c_mod2, c_mod3 = st.columns([1.6, 1.8, 1.2])
    with c_mod1:
        modo_viz = st.radio(
            "Modo de visualización pedagógica:",
            options=["Constructor Paso a Paso (Pasos 1 a 5)", "Animación Continua (Botón Reproducir)"],
            horizontal=False,
            key="piz_modo_viz",
        )
    with c_mod2:
        if modo_viz.startswith("Constructor"):
            paso_actual = st.select_slider(
                "Avanza paso a paso la explicación de pizarra:",
                options=[1, 2, 3, 4, 5],
                value=5,
                format_func=lambda x: {
                    1: "Paso 1: Equilibrio Inicial (E0)",
                    2: "Paso 2: Entra Proyecto (O -> O')",
                    3: "Paso 3: Aumento Disponibilidad (AD)",
                    4: "Paso 4: Liberación Recursos (LR)",
                    5: "Paso 5: VSP Total y Agentes",
                }[x],
            )
        else:
            paso_actual = 5
            st.caption("Presiona el botón **Reproducir desplazamiento (0% -> 100%)** encima del gráfico o arrastra la barra inferior.")
    with c_mod3:
        usar_redondeo = st.checkbox("Usar redondeo entero de cuaderno (P0=$142, P1=$126)", value=True)

    fig_leche, (q0, p0, q1, p1, qo1) = _construir_figura_leche_interactiva(a_d, b_d, c_o, d_o, q_coop, modo_viz, paso_actual, usar_redondeo)

    rect_ad = p1 * (q1 - q0)
    tri_ad = 0.5 * (p0 - p1) * (q1 - q0)
    ad = rect_ad + tri_ad
    rect_lr = p1 * (q0 - qo1)
    tri_lr = 0.5 * (p0 - p1) * (q0 - qo1)
    lr = rect_lr + tri_lr
    vsp = ad + lr
    p_soc = vsp / q_coop if q_coop > 0 else 0.0
    ing_priv = p1 * q_coop

    # KPIs rápidos en vivo sobre el gráfico
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Equilibrio Inicial (E0)", f"Q0 = {_fmt_dec(q0, 0)} t", f"P0 = ${_fmt_dec(p0, 2)}")
    k2.metric("Nuevo Equilibrio (E1)", f"Q1 = {_fmt_dec(q1, 0)} t", f"P1 = ${_fmt_dec(p1, 2)} ({p1 - p0:+.2f})")
    k3.metric("Aumento Disponibilidad (AD)", f"${_fmt_dec(ad, 0)}", f"{(ad/vsp*100 if vsp else 0):.1f}% del VSP")
    k4.metric("Liberación de Recursos (LR)", f"${_fmt_dec(lr, 0)}", f"{(lr/vsp*100 if vsp else 0):.1f}% del VSP")
    k5.metric("Valor Social (VSP = AD+LR)", f"${_fmt_dec(vsp, 0)}", f"Precio Social P* = ${_fmt_dec(p_soc, 2)}/t")

    st.plotly_chart(fig_leche, use_container_width=True)

    # Narrativa y fórmula sincronizada con el paso seleccionado
    if modo_viz.startswith("Constructor"):
        if paso_actual == 1:
            st.info(f"**Paso 1 — Situación Sin Proyecto:** Igualamos demanda y oferta ($P_d = P_o$) para hallar el punto de equilibrio inicial $E_0$: $Q_0 = {_fmt_dec(q0, 0)}$ ton/año a un precio de mercado $P_0 = \\${_fmt_dec(p0, 2)}$/ton.")
            st.latex(rf"{a_d:.0f} - {b_d:.4f}Q = {c_o:+.0f} + {d_o:.4f}Q \implies Q_0 = {_fmt_dec(q0, 0)}\text{{ ton}} \; ; \; P_0 = \${_fmt_dec(p0, 2)}")
        elif paso_actual == 2:
            st.info(f"**Paso 2 — Entrada del Proyecto ($Q' = Q + {_fmt_dec(q_coop, 0)}$):** La oferta se desplaza horizontalmente a la derecha. El precio cae de $\\${_fmt_dec(p0, 2)}$ a $\\${_fmt_dec(p1, 2)}$, el consumo total sube a $Q_1 = {_fmt_dec(q1, 0)}$ ton y los antiguos productores reducen su producción a $Q_{{o1}} = {_fmt_dec(qo1, 0)}$ ton.")
            st.latex(rf"{c_o:+.0f} + {d_o:.4f}(Q_1 - {_fmt_dec(q_coop, 0)}) = {a_d:.0f} - {b_d:.4f}Q_1 \implies Q_1 = {_fmt_dec(q1, 0)} \; ; \; Q_{{o1}} = {_fmt_dec(qo1, 0)} \; ; \; P_1 = \${_fmt_dec(p1, 2)}")
        elif paso_actual == 3:
            st.info(f"**Paso 3 — Aumento en Disponibilidad ($AD$, zona roja):** Mide el valor bajo la curva de demanda de las $+{_fmt_dec(q1 - q0, 0)}$ toneladas de mayor consumo. Se compone del rectángulo base ($\\${_fmt_dec(rect_ad, 0)}$) más el triángulo del consumidor ($\\${_fmt_dec(tri_ad, 0)}$).")
            st.latex(rf"AD = \underbrace{{{_fmt_dec(p1, 2)} \times ({_fmt_dec(q1, 0)} - {_fmt_dec(q0, 0)})}}_{{\${_fmt_dec(rect_ad, 0)}}} + \underbrace{{\frac{{({_fmt_dec(p0, 2)} - {_fmt_dec(p1, 2)}) \times ({_fmt_dec(q1, 0)} - {_fmt_dec(q0, 0)})}}{{2}}}}_{{\${_fmt_dec(tri_ad, 0)}}} = \mathbf{{\${_fmt_dec(ad, 0)}}}")
        elif paso_actual == 4:
            st.info(f"**Paso 4 — Liberación de Recursos ($LR$, zona azul):** Mide el ahorro real de costos productivos bajo la curva de oferta antigua cuando otros productores dejan de fabricar ${_fmt_dec(q0 - qo1, 0)}$ toneladas. Rectángulo ($\\${_fmt_dec(rect_lr, 0)}$) más triángulo ($\\${_fmt_dec(tri_lr, 0)}$).")
            st.latex(rf"LR = \underbrace{{{_fmt_dec(p1, 2)} \times ({_fmt_dec(q0, 0)} - {_fmt_dec(qo1, 0)})}}_{{\${_fmt_dec(rect_lr, 0)}}} + \underbrace{{\frac{{({_fmt_dec(p0, 2)} - {_fmt_dec(p1, 2)}) \times ({_fmt_dec(q0, 0)} - {_fmt_dec(qo1, 0)})}}{{2}}}}_{{\${_fmt_dec(tri_lr, 0)}}} = \mathbf{{\${_fmt_dec(lr, 0)}}}")
        else:
            st.success(f"**Paso 5 — Síntesis Completa:** $VSP = AD + LR = \\${_fmt_dec(ad, 0)} + \\${_fmt_dec(lr, 0)} = \\${_fmt_dec(vsp, 0)}$. Equivale exactamente al ingreso privado del proyecto ($\\${_fmt_dec(ing_priv, 0)}$) más los dos triángulos netos de consumidores ($\\${_fmt_dec(tri_ad, 0)}$) y productores ($\\${_fmt_dec(tri_lr, 0)}$). Precio Social unitario $P^* = \\${_fmt_dec(p_soc, 2)}$/ton.")
            st.latex(rf"VSP = AD + LR = \${_fmt_dec(vsp, 0)} \quad | \quad P^* = \frac{{\${_fmt_dec(vsp, 0)}}}{{{_fmt_dec(q_coop, 0)}}} = \mathbf{{\${_fmt_dec(p_soc, 2)}/\text{{ton}}}}")
    else:
        st.latex(rf"VSP = AD\,(\${_fmt_dec(ad, 0)}) + LR\,(\${_fmt_dec(lr, 0)}) = \mathbf{{\${_fmt_dec(vsp, 0)}}} \quad | \quad P^* = \mathbf{{\${_fmt_dec(p_soc, 2)}/\text{{ton}}}}")

    st.caption(
        "Regla de cátedra sobre el IVA en las curvas: la curva de demanda incluye IVA (disposición total a pagar del consumidor), "
        "mientras que la curva de oferta representa el costo marginal de producción y NO considera IVA."
    )


def _render_laboratorio_elasticidades():
    st.markdown("<div class='sec-header'>B. LABORATORIO INTERACTIVO DE ELASTICIDADES: CÓMO SE DEFORMAN AD Y LR (APUNTES PÁG. 16)</div>", unsafe_allow_html=True)
    st.markdown(
        "Mueve la rigidez de la Demanda y de la Oferta —o usa los 4 botones rápidos— para comprobar visualmente "
        "cuándo el Valor Social de la Producción se vuelve **100% Aumento en Disponibilidad (AD)** o **100% Liberación de Recursos (LR)**."
    )

    if "el_rig_d" not in st.session_state:
        st.session_state.el_rig_d = 50
        st.session_state.el_rig_o = 50

    b1, b2, b3, b4 = st.columns(4)
    if b1.button("Caso 1: Demanda Perf. Elástica (ηd = ∞)", use_container_width=True):
        st.session_state.el_rig_d, st.session_state.el_rig_o = 0, 55
        st.rerun()
    if b2.button("Caso 2: Oferta Perf. Elástica (ηo = ∞)", use_container_width=True):
        st.session_state.el_rig_d, st.session_state.el_rig_o = 55, 0
        st.rerun()
    if b3.button("Caso 3: Demanda Perf. Inelástica (ηd = 0)", use_container_width=True):
        st.session_state.el_rig_d, st.session_state.el_rig_o = 100, 45
        st.rerun()
    if b4.button("Caso 4: Oferta Perf. Inelástica (ηo = 0)", use_container_width=True):
        st.session_state.el_rig_d, st.session_state.el_rig_o = 45, 100
        st.rerun()

    ce1, ce2, ce3 = st.columns([1.3, 1.3, 1.1])
    rig_d = ce1.slider("Rigidez (Inelasticidad) de la Demanda (0 = Horizontal / 100 = Vertical):", 0, 100, int(st.session_state.el_rig_d), key="sl_rig_d")
    rig_o = ce2.slider("Rigidez (Inelasticidad) de la Oferta (0 = Horizontal / 100 = Vertical):", 0, 100, int(st.session_state.el_rig_o), key="sl_rig_o")
    dq_el = ce3.slider("Tamaño del Proyecto (ΔQ):", 100, 500, 300, step=25, key="sl_dq_el")

    # Mapear rigidez [0..100] a pendientes en ángulo [0°..88°] escaladas sobre E0=(1000, 100)
    def _slope_from_rig(r):
        if r <= 0:
            return 1e-5
        if r >= 100:
            return 1e5
        rad = math.radians((r / 100.0) * 85.0)
        return math.tan(rad) * 0.12

    bd = _slope_from_rig(rig_d)
    do = _slope_from_rig(rig_o)
    q0_e, p0_e = 1000.0, 100.0

    # Fórmulas cerradas exactas válidas incluso en los 4 límites extremos
    frac_ad = do / (bd + do)
    frac_lr = bd / (bd + do)
    q1_e = q0_e + frac_ad * dq_el
    qo1_e = q0_e - frac_lr * dq_el
    dp_e = (bd * do / (bd + do)) * dq_el
    p1_e = max(5.0, p0_e - dp_e)

    ad_e = 0.5 * (p0_e + p1_e) * (q1_e - q0_e)
    lr_e = 0.5 * (p0_e + p1_e) * (q0_e - qo1_e)
    vsp_e = ad_e + lr_e
    pct_ad = (ad_e / vsp_e * 100.0) if vsp_e > 0 else 50.0
    pct_lr = 100.0 - pct_ad

    cg_izq, cg_der = st.columns([1.8, 1.0])
    with cg_izq:
        fig_e = go.Figure()
        # Áreas LR y AD
        if (q0_e - qo1_e) > 1.0:
            fig_e.add_trace(go.Scatter(
                x=[qo1_e, q0_e, q0_e, qo1_e, qo1_e], y=[0, 0, p0_e, p1_e, 0],
                fill="toself", fillcolor="rgba(37, 99, 235, 0.30)", line=dict(color="#1D4ED8", width=1.5),
                name=f"LR ({pct_lr:.0f}%)",
            ))
        if (q1_e - q0_e) > 1.0:
            fig_e.add_trace(go.Scatter(
                x=[q0_e, q1_e, q1_e, q0_e, q0_e], y=[0, 0, p1_e, p0_e, 0],
                fill="toself", fillcolor="rgba(220, 38, 38, 0.30)", line=dict(color="#DC2626", width=1.5),
                name=f"AD ({pct_ad:.0f}%)",
            ))

        # Curva Demanda
        if rig_d >= 99:
            fig_e.add_trace(go.Scatter(x=[q0_e, q0_e], y=[0, 190], mode="lines", name="Demanda (D)", line=dict(color="#0F172A", width=3)))
        else:
            qx = np.linspace(300, 1700, 80)
            fig_e.add_trace(go.Scatter(x=qx, y=p0_e - bd * (qx - q0_e), mode="lines", name="Demanda (D)", line=dict(color="#0F172A", width=2.8)))

        # Curva Oferta Inicial y Con Proyecto
        if rig_o >= 99:
            fig_e.add_trace(go.Scatter(x=[q0_e, q0_e], y=[0, 190], mode="lines", name="Oferta Inicial (O)", line=dict(color="#1D4ED8", width=2.6)))
            fig_e.add_trace(go.Scatter(x=[q0_e + dq_el, q0_e + dq_el], y=[0, 190], mode="lines", name="Oferta Con Proyecto (O')", line=dict(color="#15803D", width=2.6, dash="dash")))
        else:
            qx = np.linspace(300, 1700, 80)
            fig_e.add_trace(go.Scatter(x=qx, y=p0_e + do * (qx - q0_e), mode="lines", name="Oferta Inicial (O)", line=dict(color="#1D4ED8", width=2.6)))
            fig_e.add_trace(go.Scatter(x=qx, y=p0_e + do * (qx - q0_e - dq_el), mode="lines", name="Oferta Con Proyecto (O')", line=dict(color="#15803D", width=2.6, dash="dash")))

        fig_e.update_layout(
            title=f"Composición del VSP: {pct_ad:.1f}% AD  |  {pct_lr:.1f}% LR  (P0 = ${p0_e:.0f} -> P1 = ${p1_e:.1f})",
            xaxis=dict(title="Cantidad (X)", range=[300, 1700]),
            yaxis=dict(title="Precio (Px)", range=[0, 195]),
            template="plotly_white",
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )
        st.plotly_chart(fig_e, use_container_width=True)

    with cg_der:
        fig_bar = go.Figure(data=[
            go.Bar(name="Aumento Disponibilidad (AD)", x=["Composición VSP"], y=[pct_ad], marker_color="#DC2626", text=f"{pct_ad:.1f}% AD", textposition="inside"),
            go.Bar(name="Liberación de Recursos (LR)", x=["Composición VSP"], y=[pct_lr], marker_color="#1D4ED8", text=f"{pct_lr:.1f}% LR", textposition="inside"),
        ])
        fig_bar.update_layout(
            barmode="stack",
            yaxis=dict(range=[0, 100], title="% del VSP Total"),
            template="plotly_white",
            height=380,
            showlegend=False,
            title="Peso AD vs. LR",
        )
        st.plotly_chart(fig_bar, use_container_width=True)


def _render_simulador_transporte_externalidades():
    st.markdown("<div class='sec-header'>C. SIMULADOR GRÁFICO: EXTERNALIDADES Y COSTO SOCIAL EN TRANSPORTE (APUNTES PÁGS. 13–14)</div>", unsafe_allow_html=True)
    ct1, ct2, ct3, ct4 = st.columns(4)
    x0_t = ct1.slider("Pasajes Iniciales X0:", 30000, 90000, 70000, step=1000)
    x1_t = ct2.slider("Pasajes Con Proyecto X1:", 75000, 120000, 100030, step=1000)
    cmgp_t = ct3.slider("Costo Marginal Privado CmgP ($):", 500, 2500, 1300, step=100)
    cmgs_t = ct4.slider("Costo Marginal Social CmgS ($):", 500, 3000, 1700, step=100)

    p0_t, p1_t = 5000.0, 3500.0
    dx_t = max(1.0, float(x1_t - x0_t))
    ed_t = ((x1_t - x0_t) / x0_t) / ((p1_t - p0_t) / p0_t)
    brecha_ext = cmgs_t - cmgp_t
    costo_ext_total = brecha_ext * x1_t
    ben_bruto_dem = 0.5 * (p0_t + p1_t) * dx_t

    q_arr = np.linspace(0, 130000, 100)
    pend_t = (p0_t - p1_t) / dx_t
    p_dem_t = p0_t - pend_t * (q_arr - x0_t)

    fig_t = go.Figure()
    # Beneficio bruto por mayor consumo bajo la demanda
    fig_t.add_trace(go.Scatter(
        x=[x0_t, x1_t, x1_t, x0_t, x0_t], y=[0, 0, p1_t, p0_t, 0],
        fill="toself", fillcolor="rgba(124, 58, 237, 0.22)", line=dict(color="#7C3AED", width=1.4),
        name=f"Beneficio Bruto Demanda ({_fmt_clp(ben_bruto_dem)})",
    ))
    # Banda de externalidad negativa entre CmgP y CmgS
    fig_t.add_trace(go.Scatter(
        x=[0, x1_t, x1_t, 0, 0], y=[cmgp_t, cmgp_t, cmgs_t, cmgs_t, cmgp_t],
        fill="toself", fillcolor="rgba(234, 88, 12, 0.35)", line=dict(color="#EA580C", width=1.4),
        name=f"Externalidad Negativa ({_fmt_clp(costo_ext_total)})",
    ))
    fig_t.add_trace(go.Scatter(x=q_arr, y=p_dem_t, mode="lines", name="Demanda Transporte (D)", line=dict(color="#0F172A", width=2.5)))
    fig_t.add_hline(y=cmgs_t, line_dash="dash", line_color="#DC2626", annotation_text=f"CmgS = ${_fmt_dec(cmgs_t, 0)}")
    fig_t.add_hline(y=cmgp_t, line_dash="dot", line_color="#1D4ED8", annotation_text=f"CmgP = ${_fmt_dec(cmgp_t, 0)}")

    fig_t.update_layout(
        title=f"Transporte Urbano: Elasticidad Ed = {_fmt_dec(ed_t, 2)} | Brecha Externalidad = {_fmt_clp(brecha_ext)}/pasaje",
        xaxis=dict(title="Pasajes (X)", range=[0, 128000]),
        yaxis=dict(title="Tarifa / Costo Marginal ($)", range=[0, 6200]),
        template="plotly_white",
        height=390,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig_t, use_container_width=True)


# ==============================================================================
# 3. SUB-TAB B: ANATOMÍA MATEMÁTICA DE LOS PRECIOS SOCIALES SNI 2026
# ==============================================================================

def _render_anatomia_precios_sociales():
    st.markdown("<div class='sec-header'>ANATOMÍA MATEMÁTICA INTERACTIVA DE LOS PRECIOS SOCIALES VIGENTES 2026 (MDSF / SNI)</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1. Simulador Estructural de la Tasa Social de Descuento (TSD)**")
        st.latex(r"TSD = \beta \cdot t_p + \phi \cdot q + \alpha \cdot C_{mgx}")
        st.caption("Ajusta los componentes para ver cómo el MDSF llega al 5,5% oficial:")
        tp_s = st.slider("Tasa ahorro interno tp (%):", 1.0, 8.0, 3.8, step=0.1, key="ps_tp")
        q_s = st.slider("Rentabilidad inversión privada desplazada q (%):", 4.0, 15.0, 7.6, step=0.1, key="ps_q")
        cmgx_s = st.slider("Costo marginal ahorro externo Cmgx (%):", 2.0, 10.0, 4.9, step=0.1, key="ps_cmgx")
        tsd_calc = 0.40 * tp_s + 0.40 * q_s + 0.20 * cmgx_s
        st.metric("TSD Ponderada Resultante (Ref. Oficial 2026 = 5,5%)", f"{_fmt_dec(tsd_calc, 2)}%")

    with c2:
        st.markdown("**2. Desagregación Tributaria de Combustibles (PS_comb)**")
        st.latex(r"PS_{\text{comb}} = \left[\frac{PM_{\text{comb}} - (IE^F + IE^V)\cdot UTM/1000}{(1 + IVA)(1 + t_a)}\right] \cdot FCSD")
        pm_comb = st.slider("Precio de Mercado en Bomba ($/litro):", 900, 1600, 1250, step=10, key="ps_pm")
        ie_litro = st.slider("Impuesto Específico equivalente ($/litro):", 0, 500, 330, step=10, key="ps_ie")
        ps_comb_calc = ((pm_comb - ie_litro) / (1.19 * 1.00)) * 1.00
        st.metric("Precio Social Estimado sin IVA ni Imp. Específico", f"{_fmt_clp(ps_comb_calc)}/litro", f"Ref. 2026: Gas93 $737 | Diésel $805")

    st.markdown("**3. Valor Social del Tiempo de Viaje (VST Urbano 1x / 2x) y Factores SNI 2026**")
    st.latex(r"VST_{\text{urb}} = \alpha \cdot VTT + \beta \cdot VTC + \gamma \cdot VTO \quad (\alpha=3,4\%;\; \beta=27,2\%;\; \gamma=69,4\%)")
    st.markdown(
        "- **Viaje en vehículo (ponderador 1x):** **$3.338 CLP/h-pax** | **Espera y Caminata (ponderador 2x):** **$6.676 CLP/h-pax**.\n"
        "- **Deporte y Recreación ($VTO = 39,08\\%$ salario bruto):** **$2.792 CLP/h-pax**.\n"
        "- **Mano de Obra ($PSMO = FCSMO \times Salario$):** MOC = **0,97** | MOSC = **0,95** | MONC = **0,91** | Divisa (**FCSD**) = **1,00**.\n"
        "- **Valor de una Vida Estadística ($VVE$):** **$2.383.677.600 CLP**."
    )

    df_cat_ps2026 = pd.DataFrame([
        ["Parámetros Nacionales", "TSD / MOC / MOSC / MONC / FCSD", "% o Factor", "5,5% | 0,97 | 0,95 | 0,91 | 1,00"],
        ["VST Urbano", "Viaje en vehículo (1x) / Espera (2x) / Caminata (2x)", "CLP/h-pax", "$3.338 / $6.676 / $6.676"],
        ["VST Recreación e Interurbano", "Deporte-Recreación / Interurbano Terrestre / Aéreo", "CLP/h-pax", "$2.792 / $10.047 / $16.983"],
        ["VST Carga y Seguridad Vial", "Tiempo de la carga / Valor de una Vida Estadística (VVE)", "CLP", "$12.954/h-veh | $2.383.677.600"],
        ["Combustibles (Vehículo)", "Auto ($760) / Camioneta ($787) / Camión 2 ejes y Bus ($805)", "CLP/litro", "$760 / $787 / $805"],
        ["Neumáticos y Lubricantes", "Neumático Auto ($87.543) a Bus ($364.116) | Lubr. $8.740 / $5.176", "CLP", "$87.543 a $364.116"],
        ["Vehículos Nuevos y Mantención", "Auto ($11,36M) a Bus Eléctrico ($225,36M) | Mantención $6.931/h", "CLP", "$11.360.008 a $236.844.841"],
        ["Ambientales y Energía", "Carbono ($71.801/t CO2eq) | CH4=28 | N2O=265 | Elec. BT $124,8 / AT $119,8", "CLP", "$71.801/t | $124,8/kWh"],
    ], columns=["Categoría SNI 2026", "Parámetro / Insumo", "Unidad", "Valor Oficial 2026"])
    st.dataframe(df_cat_ps2026, use_container_width=True, hide_index=True)


# ==============================================================================
# 4. SUB-TAB C: CICLO SNI Y GRÁFICO ANIMADO A 10 AÑOS DEL DÉFICIT DE AGUA POTABLE
# ==============================================================================

def _render_ciclo_sni_y_agua_animado():
    st.markdown("<div class='sec-header'>A. CICLO DE VIDA DEL PROYECTO EN EL SNI (PREINVERSIÓN, IDI Y CÓDIGO BIP)</div>", unsafe_allow_html=True)
    st.markdown(
        "1. **Preinversión:** `Idea / Problema` $\\rightarrow$ `Perfil` (Situación Base Optimizada) $\\rightarrow$ `Prefactibilidad` $\\rightarrow$ `Factibilidad`.\n"
        "2. **Inversión:** `Diseño` (aspectos técnicos) $\\rightarrow$ `Ejecución` (materialización física).\n"
        "3. **Operación:** `Puesta en marcha` $\\rightarrow$ `Operación en régimen`.\n"
        "4. **Iniciativa de Inversión (IDI) con Código BIP único:** Agrupa Estudios Básicos, Proyectos de Inversión y Programas de Inversión."
    )

    st.markdown("<div class='sec-header'>B. GRÁFICO ANIMADO A 10 AÑOS: PROYECCIÓN POBLACIONAL Y DÉFICIT DE AGUA POTABLE (CEPAL N° 39)</div>", unsafe_allow_html=True)
    cd1, cd2, cd3, cd4 = st.columns(4)
    p0_hab = cd1.slider("Población Base P0 (hab.):", 10000, 80000, 35200, step=200)
    tasa_r = cd2.slider("Crecimiento Anual r (%):", 0.5, 8.0, 3.2, step=0.1) / 100.0
    dotacion_l = cd3.slider("Consumo (L/día/persona):", 80, 300, 180, step=10)
    oferta_m3 = cd4.slider("Oferta Planta Actual (m³/día):", 2000, 12000, 5000, step=250)

    anios = [f"Año {t + 1}" for t in range(10)]
    pob_arr = [round(p0_hab * ((1.0 + tasa_r) ** t)) for t in range(10)]
    dem_arr = [round((p * dotacion_l) / 1000.0, 1) for p in pob_arr]
    ofe_arr = [float(oferta_m3)] * 10
    def_arr = [round(d - oferta_m3, 1) for d in dem_arr]

    y_top = max(max(dem_arr), oferta_m3) * 1.18
    fig_agua = go.Figure(
        data=[
            go.Bar(x=[anios[0]], y=[ofe_arr[0]], name="Oferta Planta Actual (m³/día)", marker_color="#1D4ED8"),
            go.Bar(x=[anios[0]], y=[max(0.0, def_arr[0])], name="Déficit Proyectado a Cubrir (m³/día)", marker_color="#DC2626"),
            go.Scatter(x=[anios[0]], y=[dem_arr[0]], mode="lines+markers", name="Demanda Total (m³/día)", line=dict(color="#0F172A", width=3)),
        ],
        frames=[
            go.Frame(
                data=[
                    go.Bar(x=anios[:k], y=ofe_arr[:k], marker_color="#1D4ED8"),
                    go.Bar(x=anios[:k], y=[max(0.0, v) for v in def_arr[:k]], marker_color="#DC2626"),
                    go.Scatter(x=anios[:k], y=dem_arr[:k], mode="lines+markers", line=dict(color="#0F172A", width=3)),
                ],
                name=f"Año {k}",
            )
            for k in range(1, 11)
        ],
    )
    fig_agua.update_layout(
        barmode="stack",
        title=f"Evolución del Déficit de Agua Potable (Año 1: {_fmt_dec(def_arr[0], 0)} m³/día -> Año 10: {_fmt_dec(def_arr[-1], 0)} m³/día)",
        xaxis=dict(title="Horizonte de Evaluación (10 Años)", range=[-0.5, 9.5]),
        yaxis=dict(title="Volumen Diario (m³/día)", range=[0, y_top]),
        template="plotly_white",
        height=410,
        updatemenus=[{
            "type": "buttons",
            "x": 0.0,
            "y": 1.16,
            "buttons": [
                {"label": "▶ Reproducir 10 Años", "method": "animate", "args": [None, {"frame": {"duration": 320, "redraw": True}, "fromcurrent": False}]},
                {"label": "⏸ Pausar", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]},
            ],
        }],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_agua, use_container_width=True)

    df_def = pd.DataFrame({
        "Año": anios,
        "Población Pt (hab.)": pob_arr,
        "Demanda (m³/día)": dem_arr,
        "Oferta Fija (m³/día)": ofe_arr,
        "Déficit (m³/día)": def_arr,
    })
    st.dataframe(df_def, use_container_width=True, hide_index=True)

    with st.expander("Investigación de Campo por Muestreo Poblacional (PHP + PHC)", expanded=False):
        st.latex(r"PHP = V \cdot \left(\frac{P}{V}\right)_m \quad ; \quad PT = PHP + PHC")
        st.markdown(
            "1. Delimitación y cartografía. 2. Enumeración de viviendas ($V$). 3. Muestreo y encuesta muestral $(P/V)_m$. "
            "4. Población en hogares particulares ($PHP$). 5. Conteo en hogares colectivos ($PHC$: asilos, hospitales). 6. Población Total ($PT = PHP + PHC$)."
        )


# ==============================================================================
# 5. SUB-TAB D: LOS 6 CASOS CLÁSICOS CEPAL N° 39 Y COMPENDIO MATEMÁTICO
# ==============================================================================

def _render_casos_y_compendio():
    st.markdown("<div class='sec-header'>A. LOS 6 CASOS PRÁCTICOS DE EXAMEN (MANUAL CEPAL N° 39 Y APUNTES DE CLASE)</div>", unsafe_allow_html=True)
    df_casos_piz = pd.DataFrame([
        ["1. Salud en Macondo", "Definir el problema como 'Falta de un hospital de alta complejidad'.", "Error típico: redactar el problema como falta de una solución. El problema real es 'Altas tasas de morbilidad infantil por consumo de agua no potable'; la solución óptima es potabilización y educación sanitaria."],
        ["2. Salud Primaria Santa Ana", "Baja cobertura de atención primaria urbana y rural en Santa Ana.", "Causas: infraestructura insuficiente + bajos incentivos RRHH + deficiente gestión municipal. Efectos: mayor morbilidad -> ausentismo laboral/escolar -> menor productividad y competitividad."],
        ["3. Intersección Vial Peligrosa", "Alta tasa de accidentes en un cruce urbano.", "Separa acciones excluyentes (Pasarela vs. Semáforo vs. Disco PARE) de complementarias (Campaña vial + Prohibir estacionar). Alternativa A = Pasarela + Campaña; Alternativa B = Semáforo + Campaña + Prohibición."],
        ["4. Empresa Aeronáutica", "Se gastaron US$ 1.000 millones en desarrollar un avión y el mercado cayó.", "Los US$ 1.000 millones son un costo hundido (irrecuperable) y no entran en la decisión; solo se comparan ingresos futuros esperados frente a costos adicionales pendientes."],
        ["5. Quesería Rural", "Divergencia entre evaluación privada y social en una planta rural.", "Salarios sobre el costo de oportunidad son alto costo privado pero beneficio redistributivo social; impuestos son egreso privado pero transferencia neutra social; efluentes contaminantes son externalidad negativa social."],
        ["6. Nutrición Adulto Mayor (MML)", "Construcción de Matriz de Marco Lógico con 4 tipos de indicadores.", "Fin: calidad de vida mejorada. Propósito: mejora de niveles de nutrición. Componente: entrega de suplementos. Actividades: licitación y ejecución presupuestaria (Eficacia, Eficiencia, Calidad y Economía)."],
    ], columns=["Caso Clásico en Apuntes", "Planteamiento / Trampa de Prueba", "Criterio Metodológico para Defensa y Examen"])
    st.dataframe(df_casos_piz, use_container_width=True, hide_index=True)

    st.markdown("<div class='sec-header'>B. CALCULADORA INTERACTIVA DE COMPENDIO MATEMÁTICO (TEA Y CAPM)</div>", unsafe_allow_html=True)
    cm_a, cm_b = st.columns(2)
    with cm_a:
        tna_in = st.slider("Tasa Nominal Anual TNA (%):", 1.0, 30.0, 12.0, step=0.5, key="piz_tna") / 100.0
        dias_t = st.slider("Período de capitalización t (días):", 1, 365, 30, step=1, key="piz_dias")
        tea_d = ((1.0 + (tna_in * dias_t / 365.0)) ** (365.0 / dias_t)) - 1.0
        tea_c = math.exp(tna_in) - 1.0
        st.latex(
            rf"TEA_{{\text{{Discreta}}}} = \left(1 + TNA \cdot \frac{{t}}{{365}}\right)^{{365/t}} - 1 = {_fmt_dec(tea_d*100, 2)}\% \quad | \quad "
            rf"TEA_{{\text{{Continua}}}} = e^{{TNA}} - 1 = {_fmt_dec(tea_c*100, 2)}\%"
        )
    with cm_b:
        rf_v = st.slider("Tasa Libre de Riesgo Rf (%):", 0.5, 10.0, 4.5, step=0.1, key="piz_rf")
        beta_v = st.slider("Coeficiente Sistemático Beta (β):", 0.20, 2.50, 1.15, step=0.05, key="piz_beta")
        rm_v = st.slider("Retorno Esperado Mercado E(Rm) (%):", 5.0, 20.0, 11.0, step=0.5, key="piz_rm")
        ke_v = rf_v + beta_v * (rm_v - rf_v)
        st.latex(
            rf"E(R_i) = R_f + \beta \cdot [E(R_m) - R_f] = {_fmt_dec(rf_v, 1)}\% + {_fmt_dec(beta_v, 2)} \times ({_fmt_dec(rm_v, 1)}\% - {_fmt_dec(rf_v, 1)}\%) = \mathbf{{{_fmt_dec(ke_v, 2)}\%}}"
        )


# ==============================================================================
# 6. PUNTO DE ENTRADA PRINCIPAL DE LA PESTAÑA 8
# ==============================================================================

def renderizar_tab_pizarra_pedagogica():
    st.markdown(
        """
        <div style="background-color:#0F172A;color:#FFFFFF;padding:12px 18px;border-radius:8px;margin-bottom:12px;">
            <div style="font-size:15px;font-weight:700;">
                LABORATORIO ANIMADO Y PIZARRA PEDAGÓGICA (CEPAL N° 39 + PRECIOS SOCIALES 2026 + FONTAINE)
            </div>
            <div style="font-size:12.5px;color:#CBD5E1;margin-top:3px;">
                Altera variables en vivo, avanza paso a paso o presiona Reproducir para visualizar desplazamientos de oferta,
                elasticidades extremas, externalidades en transporte y evolución del déficit a 10 años.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pt1, pt2, pt3, pt4 = st.tabs([
        "1. Pizarra Animada: Leche, Elasticidades y Transporte",
        "2. Anatomía Interactiva Precios Sociales 2026",
        "3. Ciclo SNI y Animación Déficit Agua Potable (10 Años)",
        "4. Los 6 Casos de Examen CEPAL N° 39 y Compendio",
    ])

    with pt1:
        _render_seccion_leche_animada()
        st.divider()
        _render_laboratorio_elasticidades()
        st.divider()
        _render_simulador_transporte_externalidades()
    with pt2:
        _render_anatomia_precios_sociales()
    with pt3:
        _render_ciclo_sni_y_agua_animado()
    with pt4:
        _render_casos_y_compendio()