# -*- coding: utf-8 -*-
"""
motor_pizarra_pedagogica_sni.py — MÓDULO PEDAGÓGICO Y PIZARRA DE CÁTEDRA (FDIC26 - ULAGOS)
Integra el complemento teórico-práctico del Manual CEPAL N° 39 (Ortegón, Pacheco y Roura),
la anatomía matemática de los Precios Sociales Vigentes SNI 2026 (MDSF) y las resoluciones
de pizarra paso a paso de la Dra. Luz María Ferrada B. (Mercado de la Leche, Elasticidades
Extremas, Externalidades en Transporte, Déficit de Agua Potable y Marco Lógico).
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
# 1. SEMÁFORO SUPERIOR: JERARQUÍA ESTRICTA DE INDICADORES (1° A 5° PRIORIDAD)
# ==============================================================================

def renderizar_semaforo_jerarquia_cepal(res_vivo, cfg):
    """
    Reemplaza la lectura plana de indicadores por la Jerarquía Estricta de 1° a 5° Prioridad
    del Manual CEPAL N° 39 / SNI, conectada en vivo con los resultados de Cartón Vivo Osorno.
    """
    m = res_vivo["metricas"]
    tasa_p = float(cfg.get("TASA_DESCUENTO_PRIVADA", 0.12)) * 100.0
    tasa_s = float(cfg.get("TASA_DESCUENTO_SOCIAL", 0.055)) * 100.0

    with st.expander("🧭 GUÍA PEDAGÓGICA EN VIVO: Jerarquía de Decisión de Indicadores (1° a 5° Prioridad SNI / CEPAL N° 39)", expanded=False):
        st.markdown(
            "En la evaluación de proyectos bajo metodología **SNI / CEPAL**, los indicadores cuantitativos "
            "**no tienen la misma ponderación**. La decisión de inversión sigue un orden jerárquico estricto "
            "encabezado por la creación neta de riqueza ($\\text{VAN}/\\text{VANS}$) y complementado por la "
            "tasa de descuento, la rentabilidad relativa y el riesgo:"
        )

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(
                f"""
                <div style="background:#EFF6FF;border-left:4px solid #1D4ED8;padding:10px;border-radius:6px;min-height:175px;">
                    <div style="font-weight:700;color:#1E3A8A;font-size:12.5px;">1° PRIORIDAD (Criterio Rector)</div>
                    <div style="font-weight:700;color:#0F172A;font-size:13.5px;margin-top:6px;">VAN: {_fmt_clp(m['van_privado'])}</div>
                    <div style="font-weight:700;color:#15803D;font-size:13.5px;">VANS: {_fmt_clp(m['van_social'])}</div>
                    <div style="color:#334155;font-size:11.5px;margin-top:6px;line-height:1.3;">
                        Indicador decisivo. Mide en moneda de hoy la riqueza adicional sobre el costo de oportunidad. Cumple <b>aditividad y separabilidad</b>.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                <div style="background:#F0FDF4;border-left:4px solid #15803D;padding:10px;border-radius:6px;min-height:175px;">
                    <div style="font-weight:700;color:#166534;font-size:12.5px;">2° PRIORIDAD (Tasa Descuento)</div>
                    <div style="font-weight:700;color:#0F172A;font-size:13.5px;margin-top:6px;">WACC / k: {_fmt_dec(tasa_p, 1)}%</div>
                    <div style="font-weight:700;color:#15803D;font-size:13.5px;">TSD (k*): {_fmt_dec(tasa_s, 1)}%</div>
                    <div style="color:#334155;font-size:11.5px;margin-top:6px;line-height:1.3;">
                        Indispensable para el VAN. Refleja costo de oportunidad privado (CAPM/WACC) o preferencia temporal social (TSD 5,5%).
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""
                <div style="background:#FEFCE8;border-left:4px solid #CA8A04;padding:10px;border-radius:6px;min-height:175px;">
                    <div style="font-weight:700;color:#854D0E;font-size:12.5px;">3° PRIORIDAD (Complementario)</div>
                    <div style="font-weight:700;color:#0F172A;font-size:13.5px;margin-top:6px;">TIR: {_fmt_dec(m['tir_privada'], 2)}%</div>
                    <div style="font-weight:700;color:#15803D;font-size:13.5px;">TIRS: {_fmt_dec(m['tir_social'], 2)}%</div>
                    <div style="color:#334155;font-size:11.5px;margin-top:6px;line-height:1.3;">
                        Tasa que hace VAN = 0. <b>Precaución:</b> falla al comparar proyectos con diferente escala, distinta vida útil o flujos no convencionales.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                """
                <div style="background:#FFF7ED;border-left:4px solid #EA580C;padding:10px;border-radius:6px;min-height:175px;">
                    <div style="font-weight:700;color:#9A3412;font-size:12.5px;">4° PRIORIDAD (Riesgo y Beta)</div>
                    <div style="font-weight:700;color:#0F172A;font-size:13.5px;margin-top:6px;">Sensibilidad / E[X]</div>
                    <div style="font-weight:700;color:#9A3412;font-size:13.5px;">Desvío σ y Beta (β)</div>
                    <div style="color:#334155;font-size:11.5px;margin-top:6px;line-height:1.3;">
                        Mide la robustez del VAN ante caídas de ingresos (-15%), alzas de costos (+10%) o crecimiento 0% en condiciones adversas.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c5:
            st.markdown(
                f"""
                <div style="background:#FEF2F2;border-left:4px solid #DC2626;padding:10px;border-radius:6px;min-height:175px;">
                    <div style="font-weight:700;color:#991B1B;font-size:12.5px;">5° PRIORIDAD (Liquidez)</div>
                    <div style="font-weight:700;color:#0F172A;font-size:13.5px;margin-top:6px;">PR Priv: {_fmt_dec(m['payback_privado'], 2)} años</div>
                    <div style="font-weight:700;color:#15803D;font-size:13.5px;">PR Soc: {_fmt_dec(m['payback_social'], 2)} años</div>
                    <div style="color:#334155;font-size:11.5px;margin-top:6px;line-height:1.3;">
                        Criterio auxiliar. <b>Es el menos confiable</b> porque ignora todos los flujos posteriores al corte y castiga proyectos de largo plazo.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==============================================================================
# 2. SUB-PESTAÑA A: PIZARRA MICROECONÓMICA (LECHE, ELASTICIDADES Y TRANSPORTE)
# ==============================================================================

def _render_pizarra_microeconomia():
    st.markdown("### 1. Pizarra Paso a Paso: Ejercicio Oficial del Mercado de la Leche (Clase 2)")
    st.markdown(
        "Resolución algebraica y gráfica línea por línea del ejercicio de la cooperativa lechera "
        "($1.470\\text{ ton/año}$ de leche en polvo). Puedes alternar entre la **ecuación manuscrita de los apuntes "
        "de clase ($P_o = -50 + 0,025Q_o$)** y la **variante con intercepto positivo ($P_o = +50 + 0,025Q_o$)** "
        "para verificar cómo cambian el equilibrio, el Aumento en Disponibilidad ($AD$) y la Liberación de Recursos ($LR$)."
    )

    col_sel1, col_sel2 = st.columns([2.2, 1.3])
    with col_sel1:
        modo_leche = st.selectbox(
            "Selecciona la versión de la ecuación de oferta:",
            options=[
                "1. Apuntes Pizarra (Po = -50 + 0,025·Qo | Redondeo P1 = $126 -> VSP = $196.980 | P* = $134,00)",
                "2. Apuntes Pizarra (Po = -50 + 0,025·Qo | Redondeo P1 = $125 -> VSP = $196.245 | P* = $133,50)",
                "3. Apuntes Pizarra Exacto sin redondeo intermedio (Po = -50 + 0,025·Qo -> P1 = $125,75 | VSP = $197.024)",
                "4. Variante Intercepto Positivo (Po = +50 + 0,025·Qo -> P0 = $187,36 | P1 = $170,80 | VSP = $263.253)",
            ],
        )
    with col_sel2:
        q_coop = st.number_input("Producción del proyecto (ton/año):", min_value=100.0, max_value=5000.0, value=1470.0, step=10.0)

    a_d, b_d = 300.0, 0.0205
    c_o = 50.0 if "Positivo" in modo_leche else -50.0
    d_o = 0.025

    q0_exact = (a_d - c_o) / (b_d + d_o)
    p0_exact = a_d - b_d * q0_exact
    q1_exact = (a_d - c_o + d_o * q_coop) / (b_d + d_o)
    p1_exact = a_d - b_d * q1_exact
    qo1_exact = q1_exact - q_coop

    if modo_leche.startswith("1.") and abs(q_coop - 1470.0) < 1e-3:
        q0, p0, q1, p1, qo1 = 7692.0, 142.0, 8500.0, 126.0, 7030.0
    elif modo_leche.startswith("2.") and abs(q_coop - 1470.0) < 1e-3:
        q0, p0, q1, p1, qo1 = 7692.0, 142.0, 8500.0, 125.0, 7030.0
    else:
        q0, p0, q1, p1, qo1 = q0_exact, p0_exact, q1_exact, p1_exact, qo1_exact

    rect_ad = p1 * (q1 - q0)
    tri_ad = 0.5 * (p0 - p1) * (q1 - q0)
    ad = rect_ad + tri_ad

    rect_lr = p1 * (q0 - qo1)
    tri_lr = 0.5 * (p0 - p1) * (q0 - qo1)
    lr = rect_lr + tri_lr

    vsp = ad + lr
    p_soc = vsp / q_coop
    ing_priv = p1 * q_coop

    # Desarrollo paso a paso en LaTeX como en el cuaderno
    st.markdown("#### Desarrollo Algebraico de Pizarra (Preguntas a, b, c, d, e)")
    st.latex(
        rf"\textbf{{a) Equilibrio inicial sin proyecto ($Q_d = Q_o$):}} \quad "
        rf"300 - 0,0205Q = {c_o:+.0f} + 0,025Q \implies {a_d - c_o:.0f} = 0,0455Q \implies "
        rf"Q_0 = {_fmt_dec(q0, 0)}\text{{ ton/año}} \quad ; \quad P_0 = 300 - 0,0205({_fmt_dec(q0, 0)}) = \${_fmt_dec(p0, 2)}"
    )
    st.latex(
        rf"\textbf{{b) Nueva oferta con cooperativa ($Q' = Q + {_fmt_dec(q_coop, 0)}$):}} \quad "
        rf"{c_o:+.0f} + 0,025(Q_1 - {_fmt_dec(q_coop, 0)}) = 300 - 0,0205Q_1 \implies "
        rf"0,0455Q_1 = {_fmt_dec(a_d - c_o + d_o * q_coop, 2)} \implies "
        rf"Q_1 = {_fmt_dec(q1, 0)}\text{{ ton}} \; ; \; P_1 = \${_fmt_dec(p1, 2)} \; ; \; "
        rf"Q_{{o1}} = {_fmt_dec(q1, 0)} - {_fmt_dec(q_coop, 0)} = {_fmt_dec(qo1, 0)}\text{{ ton}}"
    )
    st.latex(
        rf"\textbf{{c) Valor Social bajo Enfoque de Eficiencia ($\text{{VSP}} = \text{{AD}} + \text{{LR}}$):}} \\ "
        rf"\text{{AD (Aumento Disponibilidad)}} = \underbrace{{{_fmt_dec(p1, 2)} \times ({_fmt_dec(q1, 0)} - {_fmt_dec(q0, 0)})}}_{{\text{{Rectángulo}} = \${_fmt_dec(rect_ad, 0)}}} + "
        rf"\underbrace{{\frac{{({_fmt_dec(p0, 2)} - {_fmt_dec(p1, 2)}) \times ({_fmt_dec(q1, 0)} - {_fmt_dec(q0, 0)})}}{{2}}}}_{{\text{{Triángulo Consumidor}} = \${_fmt_dec(tri_ad, 0)}}} = \${_fmt_dec(ad, 0)} \\ "
        rf"\text{{LR (Liberación de Recursos)}} = \underbrace{{{_fmt_dec(p1, 2)} \times ({_fmt_dec(q0, 0)} - {_fmt_dec(qo1, 0)})}}_{{\text{{Rectángulo}} = \${_fmt_dec(rect_lr, 0)}}} + "
        rf"\underbrace{{\frac{{({_fmt_dec(p0, 2)} - {_fmt_dec(p1, 2)}) \times ({_fmt_dec(q0, 0)} - {_fmt_dec(qo1, 0)})}}{{2}}}}_{{\text{{Triángulo Productor}} = \${_fmt_dec(tri_lr, 0)}}} = \${_fmt_dec(lr, 0)} \\ "
        rf"\implies \mathbf{{\text{{VSP}} = \${_fmt_dec(ad, 0)} + \${_fmt_dec(lr, 0)} = \${_fmt_dec(vsp, 0)}}}"
    )
    st.latex(
        rf"\textbf{{d) Distribución por Agente y e) Precio Social Unitario ($P^*$):}} \quad "
        rf"\text{{Inversionista (Cooperativa)}} = {_fmt_dec(q_coop, 0)} \times \${_fmt_dec(p1, 2)} = \${_fmt_dec(ing_priv, 0)} \quad | \quad "
        rf"\text{{Ganancia Neta Consumidores}} = +\${_fmt_dec(tri_ad, 0)} \quad | \quad "
        rf"\text{{Ahorro Neto Productores}} = +\${_fmt_dec(tri_lr, 0)} \quad | \quad "
        rf"\mathbf{{P^* = \frac{{\text{{VSP}}}}{{X}} = \frac{{\${_fmt_dec(vsp, 0)}}}{{{_fmt_dec(q_coop, 0)}}} = \${_fmt_dec(p_soc, 2)}/\text{{ton}}}}"
    )

    # Gráfico interactivo con las áreas de pizarra
    q_grid = np.linspace(max(0, qo1 - 2500), q1 + 2500, 200)
    pd_line = a_d - b_d * q_grid
    po_line = c_o + d_o * q_grid
    po1_line = c_o + d_o * (q_grid - q_coop)

    fig = go.Figure()
    # Polígono LR (Azul como en los apuntes)
    fig.add_trace(go.Scatter(
        x=[qo1, q0, q0, qo1, qo1],
        y=[0, 0, p0, p1, 0],
        fill="toself",
        fillcolor="rgba(37, 99, 235, 0.30)",
        line=dict(color="#1D4ED8", width=1.5),
        name=f"Liberación de Recursos (LR = ${_fmt_dec(lr, 0)})",
    ))
    # Polígono AD (Rojo/Naranja como en los apuntes)
    fig.add_trace(go.Scatter(
        x=[q0, q1, q1, q0, q0],
        y=[0, 0, p1, p0, 0],
        fill="toself",
        fillcolor="rgba(220, 38, 38, 0.30)",
        line=dict(color="#DC2626", width=1.5),
        name=f"Aumento en Disponibilidad (AD = ${_fmt_dec(ad, 0)})",
    ))
    fig.add_trace(go.Scatter(x=q_grid, y=pd_line, mode="lines", name="Demanda (Pd = 300 - 0,0205·Q)", line=dict(color="#0F172A", width=2.5)))
    fig.add_trace(go.Scatter(x=q_grid, y=po_line, mode="lines", name=f"Oferta Sin Proyecto (Po = {c_o:+.0f} + 0,025·Q)", line=dict(color="#1E40AF", width=2.5)))
    fig.add_trace(go.Scatter(x=q_grid, y=po1_line, mode="lines", name="Oferta Con Proyecto (O' = Q + 1.470)", line=dict(color="#16A34A", width=2.5, dash="dash")))

    fig.update_layout(
        title=f"Gráfico de Pizarra: Equilibrio Mercado de la Leche (VSP = ${_fmt_dec(vsp, 0)} | Precio Social P* = ${_fmt_dec(p_soc, 2)}/ton)",
        xaxis_title="Cantidad de Leche en Polvo Q (ton/año)",
        yaxis_title="Precio P ($/ton)",
        yaxis=dict(range=[0, 310]),
        template="plotly_white",
        height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "📌 **Tip de Examen (Apuntes Pág. 17 y 21 — Regla del IVA en las Curvas):** Si estás valorando socialmente, "
        "**la curva de demanda incluye IVA** (porque mide la disposición total a pagar del consumidor final), mientras que "
        "**la curva de oferta representa el costo marginal de producción y NO considera IVA**."
    )

    st.divider()

    # Sub-sección 2: Los 4 casos extremos de elasticidad
    st.markdown("### 2. Los 4 Casos Extremos de Elasticidad (Apuntes Pág. 16) y Bienes Transables (Harberger)")
    caso_el = st.radio(
        "Inspecciona qué ocurre con el Valor Social de la Producción (VSP = AD + LR) en cada caso extremo:",
        options=[
            "Caso 1: Demanda Perfectamente Elástica (ηp,d = ∞) -> VSP = 100% AD (El precio P0 no baja)",
            "Caso 2: Oferta Perfectamente Elástica (ηp,o = ∞) -> VSP = 100% LR (El precio P0 no baja)",
            "Caso 3: Demanda Perfectamente Inelástica (ηp,d = 0) -> VSP = 100% LR (El consumo total X0 no sube)",
            "Caso 4: Oferta Perfectamente Inelástica (ηp,o = 0) -> VSP = 100% AD (Los antiguos productores no reducen oferta)",
        ],
    )
    if "Caso 1" in caso_el:
        st.success(
            "**Demanda Perfectamente Elástica ($\\eta_{p,d} = \\infty$):** La curva de demanda es horizontal en $P_0$. "
            "Como el consumidor es infinitamente sensible al precio, toda la producción nueva del proyecto ($X_1 - X_0$) "
            "se absorbe como mayor consumo al mismo precio $P_0$. No se desplaza a antiguos productores ($\\text{LR} = 0$), "
            "por lo tanto: **$\\text{VSP} = \\text{AD} = P_0 \\cdot \\Delta X$**."
        )
    elif "Caso 2" in caso_el:
        st.success(
            "**Oferta Perfectamente Elástica ($\\eta_{p,o} = \\infty$):** La curva de oferta es horizontal en $P_0$ (costo marginal constante). "
            "Al entrar el proyecto, el precio sigue siendo $P_0$ y la cantidad total demandada $X_0$ no cambia, pero los antiguos "
            "oferentes dejan de producir $X_0 - X_1$. Todo el beneficio social es ahorro de recursos productivos: **$\\text{VSP} = \\text{LR}$**."
        )
    elif "Caso 3" in caso_el:
        st.success(
            "**Demanda Perfectamente Inelástica ($\\eta_{p,d} = 0$):** La curva de demanda es vertical en $X_0$ (consumo fijo insensible al precio). "
            "La entrada del proyecto hace bajar el precio de $P_0$ a $P_1$, pero no aumenta el consumo total ($\\text{AD} = 0$). "
            "El proyecto sustituye exactamente producción antigua bajo la curva de oferta: **$\\text{VSP} = \\text{LR}$**."
        )
    else:
        st.success(
            "**Oferta Perfectamente Inelástica ($\\eta_{p,o} = 0$):** La curva de oferta antigua es vertical en $X_0$. "
            "Aunque el precio baje de $P_0$ a $P_1$, los antiguos productores siguen ofreciendo exactamente $X_0$ ($\\text{LR} = 0$). "
            "Toda la producción del proyecto incrementa el consumo total de $X_0$ a $X_1$: **$\\text{VSP} = \\text{AD}$**."
        )

    st.divider()

    # Sub-sección 3: Ejercicio de Externalidades y Monopolio en Transporte (Págs. 13 y 14)
    st.markdown("### 3. Ejercicio de Pizarra: Externalidades, Monopolio y Costo Social en Transporte (Págs. 13–14)")
    st.markdown(
        "En los apuntes de clase (págs. 13–14) se analiza un proyecto de transporte donde la cantidad inicial es "
        "$X_0 = 70.000\\text{ pasajes}$ a un precio $P_0 = \\$5.000$, pasando con el proyecto a $X_1 = 100.030\\text{ pasajes}$ "
        "(con capacidad máxima de $120.000$) a un precio $P_1 = \\$3.500$, existiendo divergencia entre el **Costo Marginal Privado ($CmgP$)** "
        "y el **Costo Marginal Social ($CmgS$)** por externalidades:"
    )
    st.latex(
        r"E_d = \frac{\Delta Q / Q_0}{\Delta P / P_0} = \frac{(100.030 - 70.000)/70.000}{(3.500 - 5.000)/5.000} = \frac{0,429}{-0,30} = -1,43"
    )
    st.latex(
        r"\text{Con } CmgP = \$1.300 \text{ y } CmgS = \$1.700 \text{ (o } CmgP = \$500 \text{ y } CmgS = \$700\text{):} \quad "
        r"CS_{\text{total}} = 700 \times 100.030 = \$70.021.000 \quad ; \quad "
        r"\text{VAN}_{12\%} = -800.000.000 + \sum_{t=1}^{n} \frac{\text{Flujo}_t}{(1,12)^t}"
    )


# ==============================================================================
# 3. SUB-PESTAÑA B: ANATOMÍA MATEMÁTICA DE LOS PRECIOS SOCIALES SNI 2026
# ==============================================================================

def _render_anatomia_precios_sociales_2026():
    st.markdown("### Anatomía Matemática de los Precios Sociales Vigentes 2026 (MDSF / SNI)")
    st.markdown(
        "A diferencia de un listado estático, aquí puedes revisar **de dónde sale cada fórmula oficial** "
        "según los apuntes de cátedra (págs. 8–11) y el Reporte Anual de Precios Sociales 2026 del MDSF."
    )

    c_f1, c_f2 = st.columns(2)
    with c_f1:
        st.markdown("#### 1. Tasa Social de Descuento ($\\text{TSD} = 5,5\\%$)")
        st.latex(r"TSD = \beta \cdot t_p + \phi \cdot q + \alpha \cdot C_{mgx} = 5,5\%")
        st.markdown(
            "- **$t_p$:** Tasa de interés del ahorro interno (preferencia intertemporal del consumo).\n"
            "- **$q$:** Productividad marginal / rentabilidad de la inversión privada desplazada.\n"
            "- **$C_{mgx}$:** Costo marginal del endeudamiento externo.\n"
            "- **$\\beta, \\phi, \\alpha$:** Ponderadores del ahorro interno, inversión privada y ahorro externo (Fuentes: Banco Central, INE, CMF, SII, Reserva Federal)."
        )

        st.markdown("#### 2. Precio Social de la Mano de Obra ($\\text{PSMO}$)")
        st.latex(r"PSMO = FCSMO \times Salario_{\text{Bruto Mensual}}")
        st.markdown(
            "- **Mano de Obra Calificada ($\\text{MOC}$):** $0,97$\n"
            "- **Mano de Obra Semicalificada ($\\text{MOSC}$):** $0,95$ *(incluye choferes y operadores de maquinaria según CIUO-08)*\n"
            "- **Mano de Obra No Calificada ($\\text{MONC}$):** $0,91$\n"
            "- Representa el costo de oportunidad para la sociedad al contratar trabajadores (Fuentes: INE, ENE, ESI)."
        )

    with c_f2:
        st.markdown("#### 3. Factor de Corrección Social de la Divisa ($\\text{FCSD} = 1,00$)")
        st.latex(r"FCSD = \frac{\theta X - \mu M(1 + t)}{\theta X - \mu M} = 1,00 \implies PS_{\text{Divisa}} = TC_{\text{obs}} \times 1,00")
        st.markdown(
            "- **$X, M$:** Exportaciones e importaciones.\n"
            "- **$t$:** Arancel efectivo de importación.\n"
            "- **$\\theta, \\mu$:** Ponderaciones que dependen de las elasticidades de oferta de exportaciones y demanda de importaciones (Fuentes: Banco Central y Aduanas)."
        )

        st.markdown("#### 4. Desagregación Tributaria de Combustibles e Insumos Vehiculares")
        st.latex(r"PS_{\text{comb},i} = \left[ \frac{PM_{\text{comb},i} - (IE^F + IE^V)\cdot UTM / 1000}{(1 + IVA)(1 + t_a)} \right] \cdot FCSD")
        st.markdown(
            "- Descuenta del precio de mercado ($PM$) el Impuesto Específico Fijo ($IE^F$) y Variable ($IE^V$), el $\\text{IVA}$ ($19\\%$) y el arancel aduanero ($t_a$), multiplicando por el $\\text{FCSD}$."
        )

    st.divider()

    st.markdown("#### 5. Calculadora Interactiva del Valor Social del Tiempo de Viaje ($\\text{VST}$ Urbano, Interurbano y Recreación)")
    st.latex(
        r"VST_{\text{urb}} = \alpha \cdot VTT + \beta \cdot VTC + \gamma \cdot VTO \quad "
        r"(\alpha = 3,4\%\text{ trabajo} \; ; \; \beta = 27,2\%\text{ commute} \; ; \; \gamma = 69,4\%\text{ otros propósitos})"
    )
    st.markdown(
        "- **Viajes en horario laboral ($VTT$):** Se valoran por su uso alternativo / costo de oportunidad productivo ($\\$8.235/\\text{h}$).\n"
        "- **Viajes personales y recreativos ($VTO$):** Se valoran por disposición a pagar ($39,08\\%$ del salario bruto $= \\$7.143/\\text{h}$ general y $\\$2.792/\\text{h-pax}$ en deporte/recreación).\n"
        "- **Penalización por Espera y Caminata (Factor $2\\times$):** En viajes urbanos, el viaje en vehículo pondera $1\\times$ ($\\$3.338/\\text{h-pax}$), mientras que la **espera** y la **caminata** ponderan $2\\times$ ($\\$6.676/\\text{h-pax}$)."
    )

    df_catalogo_2026 = pd.DataFrame([
        ["Parámetros Nacionales", "Tasa Social de Descuento (TSD)", "% anual", "5,5%"],
        ["Parámetros Nacionales", "Mano de Obra Calificada (MOC) / Semicalificada (MOSC) / No Calificada (MONC)", "Factor", "0,97 / 0,95 / 0,91"],
        ["Parámetros Nacionales", "Factor de Corrección Social de la Divisa (FCSD)", "Factor", "1,00"],
        ["Valor Social del Tiempo (VST)", "Urbano: Viaje en Vehículo (1x) / Espera (2x) / Caminata (2x)", "CLP/h-pax", "$3.338 / $6.676 / $6.676"],
        ["Valor Social del Tiempo (VST)", "Actividades Deportivas y Recreativas (Costo de Viaje)", "CLP/h-pax", "$2.792"],
        ["Valor Social del Tiempo (VST)", "Interurbano Terrestre (39,72% trab. / 60,28% otros) / Aéreo", "CLP/h-pax", "$10.047 / $16.983"],
        ["Valor Social del Tiempo (VST)", "Valor Social del Tiempo de la Carga", "CLP/h-veh", "$12.954"],
        ["Seguridad Vial", "Valor de una Vida Estadística (VVE — Reducción riesgo fatalidad)", "CLP", "$2.383.677.600"],
        ["Combustibles (Operación)", "Automóvil ($760) / Camioneta ($787) / Camión 2 ejes, +2 ejes y Bus Diésel ($805)", "CLP/litro", "$760 / $787 / $805"],
        ["Combustibles (Octanaje)", "Gasolina 93 ($737) / Gasolina 95 ($768) / Gasolina 97 ($822) / Ponderado ($755)", "CLP/litro", "$737 / $768 / $822 / $755"],
        ["Neumáticos", "Automóvil ($87.543) / Camioneta ($198.250) / Camión 2 ejes ($243.542) / Bus ($364.116)", "CLP/unidad", "$87.543 a $364.116"],
        ["Lubricantes y Mantenimiento", "Lubricante Auto/Camioneta ($8.740/L) | Bus/Camión ($5.176/L) | M.O. Mantención ($6.931/h)", "CLP", "$8.740/L | $5.176/L | $6.931/h"],
        ["Vehículos Nuevos (Sin Imp.)", "Auto ($11,36M) | Camioneta ($25,93M) | Camión 2 ejes ($59,60M) | Bus Diésel ($117,55M) | Bus Eléctrico ($225,36M)", "CLP/veh", "$11.360.008 a $236.844.841"],
        ["Ambientales y Energía", "Precio Social Carbono ($71.801/t CO2eq) | CH4 = 28x | N2O = 265x | Elec. BT $124,8 / AT $119,8", "CLP", "$71.801/t | $124,8/kWh"],
    ], columns=["Categoría SNI 2026", "Parámetro / Insumo Valorizado", "Unidad", "Valor Oficial 2026"])
    st.dataframe(df_catalogo_2026, use_container_width=True, hide_index=True)


# ==============================================================================
# 4. SUB-PESTAÑA C: CICLO SNI (IDI/BIP), DÉFICIT DE AGUA Y MUESTREO POBLACIONAL
# ==============================================================================

def _render_ciclo_sni_y_deficit():
    st.markdown("### 1. Ciclo de Vida del Proyecto en el SNI, Ficha IDI y Código BIP (Apuntes Págs. 12 y 19)")
    st.markdown(
        """
        * **Fase 1 — Preinversión:** `Idea / Problema` $\\rightarrow$ `Perfil` (antecedentes preliminares y Situación Base Optimizada) $\\rightarrow$ `Prefactibilidad` (evaluación de alternativas) $\\rightarrow$ `Factibilidad` (estudio detallado de la alternativa seleccionada).
        * **Fase 2 — Inversión:** `Diseño` (ingeniería y especificaciones técnicas) $\\rightarrow$ `Ejecución` (materialización física de la obra).
        * **Fase 3 — Operación:** `Puesta en marcha` $\\rightarrow$ `Operación en régimen` (generación de beneficios sociales durante el horizonte de evaluación).
        * **Tipologías de Iniciativa de Inversión (IDI) con Código BIP único:** (1) **Estudios Básicos**, (2) **Proyectos de Inversión** y (3) **Programas de Inversión**.
        """
    )

    st.divider()

    st.markdown("### 2. Simulador del Caso Práctico CEPAL N° 39: Proyección de Población y Déficit de Agua Potable (Págs. 3–4)")
    st.markdown(
        "En el Capítulo II del Manual CEPAL N° 39 se dimensiona la ampliación de una planta de agua potable "
        "comparando la demanda proyectada geométricamente ($P_t = P_0 \\cdot (1+r)^t$) frente a la oferta instalada:"
    )

    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    with col_d1:
        p0_hab = st.number_input("Población Base Actual (P0 hab.):", min_value=100, value=35200, step=100)
    with col_d2:
        tasa_r = st.number_input("Tasa Crecimiento Anual r (%):", min_value=0.0, max_value=20.0, value=3.2, step=0.1) / 100.0
    with col_d3:
        dotacion_l = st.number_input("Consumo Normativo (L/día/persona):", min_value=10.0, value=180.0, step=10.0)
    with col_d4:
        oferta_m3 = st.number_input("Oferta Planta Actual (m³/día):", min_value=0.0, value=5000.0, step=100.0)

    filas_def = []
    for t in range(0, 10):
        anio_lbl = f"Año {t + 1}"
        pob_t = round(p0_hab * ((1.0 + tasa_r) ** t))
        dem_m3 = round((pob_t * dotacion_l) / 1000.0, 1)
        def_m3 = round(dem_m3 - oferta_m3, 1)
        filas_def.append({
            "Período": anio_lbl,
            "t (años transcurridos)": t,
            "Población Proyectada Pt (hab.)": pob_t,
            "Demanda Requerida (m³/día)": dem_m3,
            "Oferta Actual Fija (m³/día)": oferta_m3,
            "Déficit Proyectado (m³/día)": def_m3,
        })
    df_def = pd.DataFrame(filas_def)
    st.latex(
        rf"P_t = P_0 \cdot (1 + r)^t \implies \text{{Año 1 (t=0): }} \text{{Demanda}} = \frac{{{p0_hab:,} \times {dotacion_l:.0f}}}{{1.000}} = {_fmt_dec(df_def.iloc[0]['Demanda Requerida (m³/día)'], 0)}\text{{ m}}^3/\text{{día}} \implies "
        rf"\text{{Déficit Inicial}} = {_fmt_dec(df_def.iloc[0]['Déficit Proyectado (m³/día)'], 0)}\text{{ m}}^3/\text{{día}} \quad | \quad "
        rf"\text{{Año 10 (t=9): Déficit}} = {_fmt_dec(df_def.iloc[-1]['Déficit Proyectado (m³/día)'], 0)}\text{{ m}}^3/\text{{día}}"
    )
    st.dataframe(df_def, use_container_width=True, hide_index=True)

    with st.expander("🔍 Ver Fórmula de Investigación de Campo por Muestreo (PHP + PHC — Pág. 3)"):
        st.latex(
            r"PHP = V \cdot \left(\frac{P}{V}\right)_m \quad ; \quad PT = PHP + PHC"
        )
        st.markdown(
            "1. **Delimitación y cartografía** del área de influencia.\n"
            "2. **Enumeración** física del total de viviendas particulares ($V$).\n"
            "3. **Muestreo aleatorio** y **Encuesta muestral** para estimar el promedio de personas por vivienda $(P/V)_m$.\n"
            "4. **Cálculo de Población en Hogares Particulares ($PHP$):** $V \\times (P/V)_m$.\n"
            "5. **Conteo en Hogares Colectivos ($PHC$):** Hogares de ancianos (como el Hogar Santa María en Osorno), hospitales, internados.\n"
            "6. **Población Total ($PT$):** $PHP + PHC$."
        )


# ==============================================================================
# 5. SUB-PESTAÑA D: CASOS CLÁSICOS CEPAL N° 39 Y COMPENDIO DE FÓRMULAS
# ==============================================================================

def _render_casos_cepal_y_compendio():
    st.markdown("### 1. Los 6 Casos Prácticos de Examen de los Apuntes (CEPAL N° 39 y Clases ULagos)")
    casos_df = pd.DataFrame([
        [
            "1. Salud en Macondo (Pág. 1)",
            "Definir el problema como 'Falta de un hospital de alta complejidad'.",
            "Nunca redactar el problema como 'falta de una solución'. El problema real es 'Altas tasas de morbilidad infantil por consumo de agua no potable', cuya solución óptima es potabilización y educación sanitaria a mucho menor costo.",
        ],
        [
            "2. Salud Primaria en Santa Ana (Pág. 2)",
            "Baja cobertura de atención primaria urbana y rural en la localidad de Santa Ana.",
            "Causas: Insuficiente infraestructura/equipamiento + inadecuado RRHH (bajos sueldos) + deficiente programación municipal. Efectos: Aumento de morbilidad -> ausentismo laboral/escolar -> caída de productividad y competitividad local.",
        ],
        [
            "3. Intersección Vial Peligrosa (Pág. 2)",
            "Alta tasa de accidentes en un cruce vial urbano.",
            "Distingue Acciones Excluyentes (Pasarela peatonal vs. Semáforo vs. Disco PARE) de Acciones Complementarias (Campaña de educación vial + Prohibición de estacionar). Alternativa A = Pasarela + Campaña; Alternativa B = Semáforo + Campaña + Prohibición.",
        ],
        [
            "4. Empresa Aeronáutica (Pág. 6)",
            "Se invirtieron US$ 1.000 millones en desarrollar un avión y el mercado cayó a mitad de camino.",
            "Los US$ 1.000 millones ya gastados son un Costo Hundido (irrecuperable) y deben ignorarse. La decisión de continuar o cancelar solo compara los ingresos futuros esperados frente a los costos adicionales pendientes de ejecutar.",
        ],
        [
            "5. Quesería Rural (Pág. 6)",
            "Divergencia entre Evaluación Privada y Evaluación Social en una fábrica rural de quesos.",
            "(1) Salarios sobre el costo de oportunidad local: costo alto para el privado, pero beneficio redistributivo social; (2) Impuestos: egreso para la empresa, transferencia neutra para la sociedad; (3) Efluentes: costo cero privado si la norma es laxa, pero externalidad negativa social que debe descontarse.",
        ],
        [
            "6. Programa Nutrición Adulto Mayor (Pág. 12)",
            "Aplicación de Matriz de Marco Lógico (MML) con indicadores de Eficacia, Eficiencia, Calidad y Economía.",
            "Fin: Adultos mayores con calidad de vida mejorada. Propósito: Mejora de los niveles de nutrición de los adultos mayores. Componente 1: Entrega de suplementos alimenticios. Actividades: Licitación y ejecución presupuestaria (sin supuestos en Actividades).",
        ],
    ], columns=["Caso de Estudio en los Apuntes", "Planteamiento / Trampa Conceptual", "Lección Metodológica para Defensa y Examen"])
    st.dataframe(casos_df, use_container_width=True, hide_index=True)

    st.divider()

    st.markdown("### 2. Calculadora de Compendio Matemático: TEA, Anualidades Crecientes y Riesgo ($E[X], \\sigma_x, \\beta, \\text{CAPM}$)")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.markdown("#### Conversión TNA $\\rightarrow$ TEA (Discreta y Continua) y Anualidad Creciente")
        tna_in = st.number_input("Tasa Nominal Anual TNA (%):", min_value=0.1, max_value=100.0, value=12.0, step=0.5) / 100.0
        dias_cap = st.number_input("Período de capitalización t (días):", min_value=1, max_value=365, value=30, step=1)
        tea_disc = ((1.0 + (tna_in * dias_cap / 365.0)) ** (365.0 / dias_cap)) - 1.0
        tea_cont = math.exp(tna_in) - 1.0
        st.latex(
            rf"TEA_{{\text{{Discreta}}}} = \left(1 + TNA \cdot \frac{{t}}{{365}}\right)^{{365/t}} - 1 = {_fmt_dec(tea_disc*100, 2)}\% \quad | \quad "
            rf"TEA_{{\text{{Continua}}}} = e^{{TNA}} - 1 = {_fmt_dec(tea_cont*100, 2)}\%"
        )

    with c_m2:
        st.markdown("#### Valor Esperado $E[X]$, Desvío Estándar $\\sigma_x$ y Modelo CAPM")
        rf_in = st.number_input("Tasa Libre de Riesgo Rf (%):", value=4.5, step=0.1)
        beta_in = st.number_input("Coeficiente Sistemático Beta (β):", value=1.15, step=0.05)
        rm_in = st.number_input("Retorno Esperado del Mercado E(Rm) (%):", value=11.0, step=0.5)
        ke_capm = rf_in + beta_in * (rm_in - rf_in)
        st.latex(
            rf"E(R_i) = R_f + \beta \cdot [E(R_m) - R_f] = {_fmt_dec(rf_in, 1)}\% + {_fmt_dec(beta_in, 2)} \times ({_fmt_dec(rm_in, 1)}\% - {_fmt_dec(rf_in, 1)}\%) = \mathbf{{{_fmt_dec(ke_capm, 2)}\%}}"
        )


# ==============================================================================
# 6. PUNTO DE ENTRADA PRINCIPAL DE LA PESTAÑA PEDAGÓGICA
# ==============================================================================

def renderizar_laboratorio_pedagogico_apuntes(res_vivo=None, cfg=None):
    st.markdown(
        """
        <div style="background-color:#1E3A8A;color:#FFFFFF;padding:12px 18px;border-radius:8px;margin-bottom:12px;">
            <div style="font-size:16px;font-weight:700;">
                🎓 PIZARRA PEDAGÓGICA INTERACTIVA Y APUNTES DE CÁTEDRA (CEPAL N° 39 + SNI 2026 + FONTAINE)
            </div>
            <div style="font-size:12.5px;color:#DBEAFE;margin-top:3px;">
                Resolución algebraica paso a paso del Mercado de la Leche (Po = -50 + 0,025Q y +50), los 4 casos extremos de elasticidad, anatomía matemática de los Precios Sociales 2026, déficit de agua potable y casos de examen.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    t1, t2, t3, t4 = st.tabs([
        "🥛 1. Pizarra Mercado de la Leche, Elasticidades y Transporte",
        "🧮 2. Anatomía Matemática Precios Sociales 2026",
        "🚰 3. Ciclo SNI (IDI/BIP), Población y Déficit Agua Potable",
        "📚 4. Los 6 Casos de Examen CEPAL N° 39 y Compendio Matemático",
    ])

    with t1:
        _render_pizarra_microeconomia()
    with t2:
        _render_anatomia_precios_sociales_2026()
    with t3:
        _render_ciclo_sni_y_deficit()
    with t4:
        _render_casos_cepal_y_compendio()
