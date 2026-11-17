# -*- coding: utf-8 -*-
"""
motor_guia_interactiva_bibliografia.py — GUÍA INTERACTIVA Y EJERCICIOS GUIADOS
Respaldo bibliográfico oficial — Evaluación Integrada de Proyectos (FDIC26), ULagos:
  1. Ernesto R. Fontaine (2008), Evaluación Social de Proyectos (13.ª ed., Pearson).
  2. Edgar Ortegón, Juan Francisco Pacheco y Horacio Roura (2005), Metodología general de
     identificación, preparación y evaluación de proyectos de inversión pública (CEPAL N° 39).
  3. MDSF / SNI (2026), Reporte Anual Precios Sociales Vigentes 2026 (31 marzo 2026).

Enfoque pedagógico: aprender haciendo con simuladores breves, gráficos limpios y
micro-retos de autoevaluación en 30 segundos.
"""

import numpy as np
import numpy_financial as npf
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==============================================================================
# UTILIDADES DE FORMATO Y TABLAS OFICIALES DE REFERENCIA
# ==============================================================================

def _fmt_clp(valor: float, dec: int = 0) -> str:
    signo = "-" if valor < 0 else ""
    v = abs(float(valor))
    if dec == 0:
        return f"{signo}${int(round(v)):,}".replace(",", ".")
    s = f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{signo}${s}"


def _fmt_num(valor: float, dec: int = 2) -> str:
    return f"{float(valor):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


CIUO_08_SNI_2026 = [
    ("1. Directores, gerentes y administradores", "MOC", 0.97),
    ("2. Profesionales, científicos e intelectuales", "MOC", 0.97),
    ("3. Técnicos y profesionales de nivel medio", "MOC", 0.97),
    ("4. Personal de apoyo y administrativo", "MOSC", 0.95),
    ("5. Trabajadores de los servicios y vendedores de comercios", "MOSC", 0.95),
    ("6. Agricultores y trabajadores calificados agropecuarios y pesqueros", "MOSC", 0.95),
    ("7. Artesanos y operarios de oficios (excepción justificada: maestro 1ª -> MOC)", "MOSC", 0.95),
    ("8. Operadores de instalaciones, máquinas y montadores (incluye choferes)", "MOSC", 0.95),
    ("9. Ocupaciones elementales", "MONC", 0.91),
]

# Cuadro IV.5 de Fontaine (pág. 146): "¿Cuándo cortar los árboles?"
BOSQUE_FONTAINE = [
    (0, 100.00),
    (1, 105.00),
    (2, 112.35),
    (3, 123.59),
    (4, 139.65),
    (5, 153.85),
    (6, 167.70),
    (7, 181.12),
    (8, 191.98),
    (9, 201.58),
    (10, 210.65),
    (11, 218.79),
    (12, 225.35),
]


# ==============================================================================
# FUNCIONES DE CÁLCULO PURO (TESTEABLES Y REUTILIZABLES)
# ==============================================================================

def calcular_horno_pan_fontaine(
    insumos_base: float = 80.0,
    mo_base: float = 15.0,
    cap_base: float = 5.0,
    precio_base: float = 104.0,
    insumos_extra: float = 10.0,
    mo_extra: float = 12.0,
    cap_extra: float = 8.0,
    precio_nuevo: float = 133.0,
    subsidio_insumo_soc: float = 0.0,
) -> dict:
    """Replica Gráfico I.4 y sección B.8 de Fontaine (págs. 16-17 y 35) más precios mentirosos (pág. 30)."""
    ctp_base = insumos_base + mo_base + cap_base
    exc_base = precio_base - ctp_base
    va_base = precio_base - insumos_base

    ctp_amp = ctp_base + insumos_extra + mo_extra + cap_extra
    exc_amp = precio_nuevo - ctp_amp
    va_amp = precio_nuevo - (insumos_base + insumos_extra)

    # Precio mentiroso: si un insumo (ej. agua en Iquique) cuesta más a la sociedad que al privado
    cts_base = ctp_base + subsidio_insumo_soc
    exc_soc_base = precio_base - cts_base

    return {
        "ctp_base": ctp_base,
        "exc_base": exc_base,
        "va_base": va_base,
        "ctp_amp": ctp_amp,
        "exc_amp": exc_amp,
        "va_amp": va_amp,
        "delta_va": va_amp - va_base,
        "delta_exc": exc_amp - exc_base,
        "cts_base": cts_base,
        "exc_soc_base": exc_soc_base,
    }


def calcular_bosque_fontaine(tasa_r: float = 0.05) -> pd.DataFrame:
    """Calcula la tabla completa del Cuadro IV.5 de Fontaine (pág. 146) para cualquier tasa r."""
    inv0 = BOSQUE_FONTAINE[0][1]
    filas = []
    for idx in range(1, len(BOSQUE_FONTAINE)):
        anio, b_i = BOSQUE_FONTAINE[idx]
        _, b_prev = BOSQUE_FONTAINE[idx - 1]
        k_marg = ((b_i / b_prev) - 1.0) * 100.0
        c_alt = inv0 * ((1.0 + tasa_r) ** anio)
        bn_i = b_i - c_alt
        van_i = (b_i / ((1.0 + tasa_r) ** anio)) - inv0
        tir_prom = (((b_i / inv0) ** (1.0 / anio)) - 1.0) * 100.0
        factor_vae = (tasa_r * ((1.0 + tasa_r) ** anio)) / (((1.0 + tasa_r) ** anio) - 1.0) if tasa_r > 0 else (1.0 / anio)
        vae_i = van_i * factor_vae
        van_perp = (vae_i / tasa_r) if tasa_r > 0 else 0.0
        filas.append({
            "Año": anio,
            "Valor Madera ($)": round(b_i, 2),
            "Tasa Marginal K_i (%)": round(k_marg, 2),
            "VAN 1 Ciclo ($)": round(van_i, 4),
            "TIR Promedio (%)": round(tir_prom, 4),
            "VAE ($/año)": round(vae_i, 4),
            "VAN Perpetuo ($)": round(van_perp, 4),
        })
    return pd.DataFrame(filas)


def calcular_precio_social_impuesto_cepal(
    p_oferta: float,
    tasa_imp_pct: float,
    elast_oferta: float,
    elast_demanda_abs: float,
) -> dict:
    """
    Fórmula 27 (CEPAL Manual N° 39, pág. 128):
    p_d = p_s * (1 + t)
    p* = (eps * p_s + |eta| * p_d) / (eps + |eta|)
    """
    t = tasa_imp_pct / 100.0
    p_demanda = p_oferta * (1.0 + t)
    denom = elast_oferta + elast_demanda_abs
    if denom <= 0:
        w_s, w_d = 0.5, 0.5
    else:
        w_s = elast_oferta / denom
        w_d = elast_demanda_abs / denom
    p_social = w_s * p_oferta + w_d * p_demanda
    return {
        "p_oferta": p_oferta,
        "p_demanda": p_demanda,
        "p_social": p_social,
        "peso_oferta_pct": w_s * 100.0,
        "peso_demanda_pct": w_d * 100.0,
    }


def _render_micro_reto(clave: str, afirmacion: str, respuesta_correcta: str, explicacion: str, referencia: str):
    """Renderiza una tarjeta limpia de Verdadero/Falso en 30 segundos con retroalimentación inmediata."""
    st.markdown(f"**Afirmación:** {afirmacion}")
    c_rad, c_btn = st.columns([2.2, 1.0])
    eleccion = c_rad.radio(
        "Tu respuesta:",
        ["Verdadero", "Falso"],
        horizontal=True,
        key=f"reto_rad_{clave}",
        label_visibility="collapsed",
    )
    if c_btn.button("Verificar", key=f"reto_btn_{clave}", use_container_width=True):
        st.session_state[f"reto_chk_{clave}"] = True

    if st.session_state.get(f"reto_chk_{clave}", False):
        if eleccion == respuesta_correcta:
            st.success(f"Correcto ({respuesta_correcta}). {explicacion} — Fuente: {referencia}.")
        else:
            st.error(f"Incorrecto. La respuesta correcta es {respuesta_correcta}. {explicacion} — Fuente: {referencia}.")


# ==============================================================================
# RENDERIZADOR PRINCIPAL DE LA PESTAÑA 7
# ==============================================================================

def renderizar_guia_interactiva_bibliografia():
    st.markdown(
        "<div class='sec-header'>GUÍA INTERACTIVA Y EJERCICIOS PRÁCTICOS — FONTAINE (13.ª ED.), CEPAL MANUAL N° 39 Y SNI 2026</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Cuatro mini-laboratorios visuales diseñados para aprender paso a paso con los ejercicios clásicos de la bibliografía "
        "de la cátedra: mueve los controles, observa qué cambia en el gráfico y comprueba lo aprendido en 30 segundos."
    )

    m1, m2, m3, m4 = st.tabs([
        "1. Precios Mentirosos, VA y Costos Hundidos (Fontaine I–II)",
        "2. Trampas de la TIR y ¿Cuándo Cortar el Bosque? (Fontaine III–IV)",
        "3. Déficit, NOF, WACC y Elasticidades (CEPAL N° 39)",
        "4. Conversor y Casos Precios Sociales SNI 2026 (MDSF)",
    ])

    # ==========================================================================
    # MÓDULO 1: FONTAINE CAP. I Y II
    # ==========================================================================
    with m1:
        st.markdown("<div class='sub-header'>Ejercicio 1.1 — El Horno de Pan: ¿Por qué maximizar Valor Agregado puede empobrecer? (Fontaine, págs. 16–17 y 35)</div>", unsafe_allow_html=True)
        st.caption(
            "Idea central de Fontaine: producir es costo y consumir es beneficio. El objetivo económico no es inflar el "
            "Valor Agregado (VA = Trabajo + Capital + Excedente), sino maximizar el Excedente neto."
        )

        col_p1, col_p2, col_p3 = st.columns(3)
        precio_pan = col_p1.slider("Precio venta pan base ($):", 90, 120, 104, 1, key="f1_pbase")
        precio_env = col_p2.slider("Precio venta pan envasado + reparto ($):", 120, 145, 133, 1, key="f1_pamp")
        distorsion_agua = col_p3.slider("Subsidio oculto al insumo (ej. agua Iquique, $):", 0, 20, 6, 1, key="f1_agua")

        hp = calcular_horno_pan_fontaine(
            precio_base=float(precio_pan),
            precio_nuevo=float(precio_env),
            subsidio_insumo_soc=float(distorsion_agua),
        )

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Excedente Privado Base", _fmt_clp(hp["exc_base"]), f"VA Base: {_fmt_clp(hp['va_base'])}")
        k2.metric(
            "Excedente con Envasado (+$30 costo)",
            _fmt_clp(hp["exc_amp"]),
            f"{hp['delta_exc']:+.0f} vs base",
        )
        k3.metric(
            "Valor Agregado con Envasado",
            _fmt_clp(hp["va_amp"]),
            f"{hp['delta_va']:+.0f} vs base",
        )
        k4.metric(
            "Excedente Social (con subsidio oculto)",
            _fmt_clp(hp["exc_soc_base"]),
            "Bueno para Juan, malo para el país" if (hp["exc_base"] > 0 and hp["exc_soc_base"] < 0) else "Alineado",
        )

        cg1, ct1 = st.columns([1.35, 1.05])
        with cg1:
            fig_pan = go.Figure()
            fig_pan.add_trace(go.Bar(
                name="Pan Base (Costo $100)",
                x=["Valor Agregado", "Excedente Privado", "Excedente Social"],
                y=[hp["va_base"], hp["exc_base"], hp["exc_soc_base"]],
                marker_color="#262626",
                text=[_fmt_clp(hp["va_base"]), _fmt_clp(hp["exc_base"]), _fmt_clp(hp["exc_soc_base"])],
                textposition="outside",
            ))
            fig_pan.add_trace(go.Bar(
                name="Pan Envasado + Reparto (Costo $130)",
                x=["Valor Agregado", "Excedente Privado", "Excedente Social"],
                y=[hp["va_amp"], hp["exc_amp"], hp["exc_amp"] - distorsion_agua],
                marker_color="#0F766E",
                text=[_fmt_clp(hp["va_amp"]), _fmt_clp(hp["exc_amp"]), _fmt_clp(hp["exc_amp"] - distorsion_agua)],
                textposition="outside",
            ))
            fig_pan.add_hline(y=0, line_color="#64748B", line_width=1)
            fig_pan.update_layout(
                title="Valor Agregado vs. Excedente Económico (Caso Panadero de Fontaine)",
                barmode="group",
                yaxis_title="Pesos por unidad ($)",
                height=320,
                margin=dict(l=15, r=15, t=42, b=20),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#F8FAFC",
            )
            st.plotly_chart(fig_pan, use_container_width=True)

        with ct1:
            st.markdown("##### Qué debes recordar de este ejercicio")
            st.markdown(
                f"* **Trampa del Valor Agregado:** Con pan envasado a **${precio_env}**, el Valor Agregado sube en **{_fmt_clp(hp['delta_va'])}**, "
                f"pero el Excedente cambia en **{_fmt_clp(hp['delta_exc'])}** porque agregar más mano de obra y capital también es costo.\n"
                f"* **Precio Mentiroso (pág. 30):** Si el panadero paga un insumo subsidiado en **${distorsion_agua}**, su excedente privado es "
                f"**{_fmt_clp(hp['exc_base'])}**, pero el excedente social real es **{_fmt_clp(hp['exc_soc_base'])}**.\n"
                "* **Situación Base Optimizada (págs. 4–10):** Antes de construir un puerto nuevo o una autopista, optimiza lo actual "
                "(3 turnos, tarifas diferenciadas por horario) para no atribuir al proyecto beneficios que no le corresponden."
            )

        st.markdown("<div class='sub-header'>Ejercicio 1.2 — Diferentes Costos para Diferentes Decisiones (Fontaine, Cap. II, págs. 43–51)</div>", unsafe_allow_html=True)
        c_dec1, c_dec2 = st.columns([1.6, 1.0])
        decision = c_dec1.selectbox(
            "Elige la decisión gerencial que estás evaluando:",
            [
                "A. Decisión de formar o no la fábrica (antes de invertir)",
                "B. Decisión de continuar operando (fábrica ya construida)",
                "C. Decisión de comprar una máquina adicional (análisis marginal)",
            ],
            key="f1_decision",
        )
        val_liq_maq = c_dec2.number_input(
            "Valor de liquidación hoy de máquina + edificio ($):",
            min_value=0, max_value=12000, value=2500, step=250, key="f1_liq",
        )

        if decision.startswith("A."):
            df_cost = pd.DataFrame([
                ["Estudio de factibilidad ya pagado ($250)", "Hundido (NO entra)", "$0", "Ya se gastó y no se recupera aunque no hagas la fábrica."],
                ["Mano de obra + patente + impuesto activo", "Evitable (SÍ entra)", "$5.845", "Se evita por completo si decides no formar la empresa."],
                ["Sueldo alternativo del dueño ($155)", "Costo de oportunidad (SÍ)", "$155", "Dejas de ganarlo en tu empleo actual aunque no figure en planilla."],
                ["Interés 10% sobre capital total ($11.500)", "Evitable (SÍ entra)", "$1.150", "Incluye máquina ($9.000), edificio ($500), permiso ($700) y CT ($1.300)."],
            ], columns=["Partida (Fontaine, págs. 44–46)", "Clasificación Económica", "Costo Pertinente", "Por qué entra o sale"])
            ing_min = 7150
            nota_dec = "Ingreso anual mínimo exigido para formar la fábrica: **$7.150/año** (el estudio de $250 es historia)."
        elif decision.startswith("B."):
            int_recup = round(val_liq_maq * 0.10)
            ing_min = 6000 + int_recup + 130
            df_cost = pd.DataFrame([
                ["Estudio ($250) y Permiso construcción ($700)", "Hundidos (NO entran)", "$0", "El permiso era evitable antes de construir, pero ya es irrecuperable."],
                ["Costos directos anuales + sueldo dueño", "Evitables (SÍ entran)", "$6.000", "Si cierras la planta, dejas de pagar sueldos, patente e impuesto."],
                [f"Interés 10% sobre liquidación (${val_liq_maq:,.0f})".replace(",", "."), "Recuperable (SÍ entra)", _fmt_clp(int_recup), "No importa el costo original ($9.500), solo lo que hoy recuperas al vender."],
                ["Interés 10% sobre capital circulante ($1.300)", "Recuperable (SÍ entra)", "$130", "El capital de trabajo se recupera al cerrar y rendiría 10% en el banco."],
            ], columns=["Partida (Fontaine, págs. 48–49)", "Clasificación Económica", "Costo Pertinente", "Por qué entra o sale"])
            nota_dec = f"Ingreso anual mínimo para seguir operando: **{_fmt_clp(ing_min)}/año** (si ganas más que esto, conviene seguir aunque no recuperes la inversión histórica)."
        else:
            ing_min = 4550
            df_cost = pd.DataFrame([
                ["Gastos actuales de la fábrica ($7.150)", "No pertinentes (NO entran)", "$0", "Ya se incurren con o sin la máquina adicional."],
                ["Mano de obra adicional", "Marginal (SÍ entra)", "$3.450", "Solo se contrata si compras la nueva máquina."],
                ["Interés 10% máquina adicional ($10.000)", "Marginal (SÍ entra)", "$1.000", "Costo de oportunidad del capital nuevo comprometido."],
                ["Impuesto anual adicional (1% sobre $10.000)", "Marginal (SÍ entra)", "$100", "Aumento tributario incremental del nuevo equipo."],
            ], columns=["Partida (Fontaine, págs. 50–51)", "Clasificación Económica", "Costo Pertinente", "Por qué entra o sale"])
            nota_dec = "Ingreso adicional mínimo para comprar la máquina: **$4.550/año**. Nunca decidas comparando contra el costo medio total ($5,85) si el precio marginal ($5,00) supera al costo marginal ($4,55)."

        st.info(nota_dec)
        st.table(df_cost)

        with st.expander("Pruébame en 30 segundos — Retos de Fontaine (Cap. I y II)"):
            _render_micro_reto(
                "f1_q1",
                "Si el Valor Agregado del proyecto A es mayor que el del proyecto B, entonces el proyecto A es mejor para el país que el proyecto B.",
                "Falso",
                "El Valor Agregado incluye pagos al trabajo y al capital, que son costos para el país; lo que aumenta la riqueza es el excedente social neto.",
                "Fontaine (2008), Cap. I (pág. 34) y Cap. II (pág. 85)",
            )
            st.divider()
            _render_micro_reto(
                "f1_q2",
                "El costo del permiso de construcción ya pagado debe incluirse como costo pertinente al decidir si conviene continuar operando una fábrica existente.",
                "Falso",
                "Una vez pagado y sin valor de reventa, el permiso pasa a ser un costo hundido (inevitable) y no debe afectar la decisión de continuar operando.",
                "Fontaine (2008), Cap. II (pág. 48–49)",
            )

    # ==========================================================================
    # MÓDULO 2: FONTAINE CAP. III Y IV
    # ==========================================================================
    with m2:
        st.markdown("<div class='sub-header'>Ejercicio 2.1 — ¿Por qué la TIR puede mentir? Flujos con Doble TIR (Fontaine, Cap. III, págs. 104–106)</div>", unsafe_allow_html=True)
        st.caption(
            "Cuando un proyecto tiene costos de cierre ambiental al final (como un relleno sanitario o una mina), "
            "el flujo cambia dos veces de signo y puede tener dos TIR o ninguna TIR real."
        )

        caso_tir = st.selectbox(
            "Selecciona un caso clásico de Fontaine (Cap. III):",
            [
                "Caso 1: Relleno Sanitario con cierre ambiental (-10, +50, -60) -> Dos TIR (100% y 200%)",
                "Caso 2: Mina con remediación (-10, +30, -25) -> Sin TIR real (raíces imaginarias)",
                "Caso 3: Proyecto bien comportado (-100, +60, +65) -> Una sola TIR",
            ],
            key="f2_caso_tir",
        )
        if caso_tir.startswith("Caso 1"):
            flujos_def = [-10.0, 50.0, -60.0]
        elif caso_tir.startswith("Caso 2"):
            flujos_def = [-10.0, 30.0, -25.0]
        else:
            flujos_def = [-100.0, 60.0, 65.0]

        cf0, cf1, cf2, cr_sel = st.columns([1, 1, 1, 1.4])
        f0 = cf0.number_input("Flujo Año 0 ($):", value=flujos_def[0], step=5.0, key=f"f2_f0_{caso_tir[:6]}")
        f1 = cf1.number_input("Flujo Año 1 ($):", value=flujos_def[1], step=5.0, key=f"f2_f1_{caso_tir[:6]}")
        f2 = cf2.number_input("Flujo Año 2 ($):", value=flujos_def[2], step=5.0, key=f"f2_f2_{caso_tir[:6]}")
        r_eval = cr_sel.slider("Tasa de descuento r (%):", 0, 240, 10, 5, key="f2_reval") / 100.0

        flujos_vec = np.array([f0, f1, f2], dtype=float)
        r_grid = np.linspace(0.0, 2.5, 251)
        van_grid = [float(npf.npv(rv, flujos_vec)) for rv in r_grid]
        van_actual = float(npf.npv(r_eval, flujos_vec))

        # Calcular raíces exactas de f0*(1+r)^2 + f1*(1+r) + f2 = 0
        raices_txt = []
        if abs(f0) > 1e-9:
            disc = f1 * f1 - 4.0 * f0 * f2
            if disc >= 0:
                for sgn in (-1.0, 1.0):
                    x_root = (-f1 + sgn * np.sqrt(disc)) / (2.0 * f0)
                    if x_root > 0:
                        r_root = (x_root - 1.0) * 100.0
                        if -99.0 <= r_root <= 500.0:
                            raices_txt.append(f"{r_root:.1f}%")
            else:
                raices_txt = ["Imaginaria (no existe TIR real)"]

        cg2, ct2 = st.columns([1.4, 1.0])
        with cg2:
            fig_tir = go.Figure()
            fig_tir.add_trace(go.Scatter(
                x=r_grid * 100.0,
                y=van_grid,
                mode="lines",
                name="Curva VAN(r)",
                line=dict(color="#1E293B", width=2.5),
            ))
            fig_tir.add_trace(go.Scatter(
                x=[r_eval * 100.0],
                y=[van_actual],
                mode="markers+text",
                name="Tu tasa r",
                marker=dict(color="#0F766E" if van_actual >= 0 else "#B91C1C", size=11),
                text=[f"VAN({r_eval*100:.0f}%) = ${van_actual:,.2f}"],
                textposition="top center",
            ))
            fig_tir.add_hline(y=0, line_color="#94A3B8", line_dash="dash")
            fig_tir.update_layout(
                title="Perfil VAN según Tasa de Descuento (Regla a Prueba de Tontos)",
                xaxis_title="Tasa de descuento r (%)",
                yaxis_title="VAN ($)",
                height=320,
                margin=dict(l=15, r=15, t=42, b=20),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#F8FAFC",
            )
            st.plotly_chart(fig_tir, use_container_width=True)

        with ct2:
            st.metric(
                f"VAN evaluado a r = {r_eval*100:.0f}%",
                _fmt_clp(van_actual, 2),
                "CONVIENE (VAN > 0)" if van_actual > 0 else "RECHAZAR (VAN <= 0)",
            )
            st.markdown(f"**TIR(s) matemática(s):** `{', '.join(raices_txt) if raices_txt else 'Sin raíz real'}`")
            st.info(
                "En el relleno sanitario (-10, +50, -60), las TIR son **100%** y **200%**, pero a **r = 10%** el VAN es **-$14,13**. "
                "La regla del VAN nunca se equivoca porque descuenta a la tasa real del mercado y no supone reinversión a la TIR."
            )

        st.markdown("<div class='sub-header'>Ejercicio 2.2 — ¿Cuándo Cortar el Bosque? y Momento Óptimo TRI (Fontaine, Cap. IV, págs. 145–156)</div>", unsafe_allow_html=True)
        cb1, cb2 = st.columns([1.0, 1.4])
        r_bosque = cb1.slider("Tasa alternativa del inversionista r (%):", 2.0, 10.0, 5.0, 0.5, key="f2_rbosq") / 100.0
        df_bosq = calcular_bosque_fontaine(r_bosque)

        opt_1ciclo = int(df_bosq.loc[df_bosq["VAN 1 Ciclo ($)"].idxmax(), "Año"])
        opt_tir = int(df_bosq.loc[df_bosq["TIR Promedio (%)"].idxmax(), "Año"])
        opt_vae = int(df_bosq.loc[df_bosq["VAE ($/año)"].idxmax(), "Año"])

        with cb2:
            bmk1, bmk2, bmk3 = st.columns(3)
            bmk1.metric("1 Ciclo (Salir del negocio)", f"Año {opt_1ciclo}", f"VAN máx: {_fmt_clp(df_bosq['VAN 1 Ciclo ($)'].max(), 2)}")
            bmk2.metric("Tierra limitada (Reinv. $100)", f"Año {opt_vae}", f"VAE máx: {_fmt_clp(df_bosq['VAE ($/año)'].max(), 2)}")
            bmk3.metric("Reinvertir TODO el flujo", f"Año {opt_tir}", f"TIR máx: {_fmt_num(df_bosq['TIR Promedio (%)'].max(), 2)}%")

        fig_b = go.Figure()
        fig_b.add_trace(go.Scatter(
            x=df_bosq["Año"], y=df_bosq["Tasa Marginal K_i (%)"],
            mode="lines+markers", name="Crecimiento marginal del bosque K_i (%)",
            line=dict(color="#262626", width=2.4),
        ))
        fig_b.add_trace(go.Scatter(
            x=df_bosq["Año"], y=df_bosq["TIR Promedio (%)"],
            mode="lines+markers", name="TIR promedio acumulada (%)",
            line=dict(color="#0F766E", width=2.2, dash="dot"),
        ))
        fig_b.add_hline(y=r_bosque * 100.0, line_color="#B91C1C", line_dash="dash", annotation_text=f"Tasa alternativa r = {r_bosque*100:.1f}%")
        fig_b.update_layout(
            title="Regla de Liquidación Óptima: Cortar cuando K_i iguala tu tasa relevante (Cuadro IV.5)",
            xaxis_title="Año de corte",
            yaxis_title="Tasa anual (%)",
            height=300,
            margin=dict(l=15, r=15, t=42, b=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#F8FAFC",
        )
        st.plotly_chart(fig_b, use_container_width=True)

        # Mini-widget TRI (Carretera pág. 155-157)
        st.markdown("##### Regla de Momento Óptimo de Inicio — Tasa de Rentabilidad Instantánea (`TRI = B1 / C`)")
        ctri1, ctri2, ctri3, ctri4 = st.columns(4)
        inv_tri = ctri1.number_input("Inversión obra C ($):", value=200.0, step=20.0, key="f2_ctri")
        b1_tri = ctri2.number_input("Beneficio año 1 B1 ($):", value=15.0, step=1.0, key="f2_b1tri")
        r_tri = ctri3.number_input("Tasa descuento r (%):", value=10.0, step=0.5, key="f2_rtri") / 100.0
        alpha_tri = ctri4.number_input("Alza anual costo construcción/molestias α (%):", value=0.0, step=0.5, key="f2_atri") / 100.0

        tri_val = (b1_tri / inv_tri) if inv_tri > 0 else 0.0
        umbral_tri = r_tri - alpha_tri
        if tri_val < umbral_tri:
            st.warning(
                f"**TRI = {tri_val*100:.2f}% < (r − α) = {umbral_tri*100:.2f}%** → **POSTERGAR la obra.** "
                f"El beneficio del primer año ({_fmt_clp(b1_tri)}) aún no cubre el costo de oportunidad neto del capital."
            )
        else:
            st.success(
                f"**TRI = {tri_val*100:.2f}% ≥ (r − α) = {umbral_tri*100:.2f}%** → **EJECUTAR AHORA.** "
                "Postergar un año más hace perder más beneficio que lo ahorrado en costo de capital."
            )

        with st.expander("Pruébame en 30 segundos — Retos de Fontaine (Cap. III y IV)"):
            _render_micro_reto(
                "f2_q1",
                "Si la TIR del proyecto A es mayor que la TIR del proyecto B (ambos con flujos bien comportados), ejecutar A siempre aumenta más la riqueza que ejecutar B.",
                "Falso",
                "La TIR no compara escalas ni horizontes; entre proyectos mutuamente excluyentes manda el mayor VAN (o mayor VAE si son repetibles).",
                "Fontaine (2008), Cap. III (págs. 107–108 y 130)",
            )
            st.divider()
            _render_micro_reto(
                "f2_q2",
                "Si la Tasa de Rentabilidad Instantánea (TRI = B1 / C) de una carretera cuyos beneficios crecen con el tiempo calendario es menor que r, conviene postergar su inicio.",
                "Verdadero",
                "Cuando B1 < r·C, el proyecto aún no rinde en su primer año el costo de capital de invertir hoy; conviene esperar hasta que TRI alcance r.",
                "Fontaine (2008), Cap. IV (págs. 155–156)",
            )

    # ==========================================================================
    # MÓDULO 3: CEPAL MANUAL N° 39 (ORTEGÓN, PACHECO Y ROURA, 2005)
    # ==========================================================================
    with m3:
        st.markdown("<div class='sub-header'>Ejercicio 3.1 — Proyección Poblacional y Curva de Déficit (CEPAL N° 39, Cap. II, Tabla 9, págs. 48–49)</div>", unsafe_allow_html=True)
        st.latex(r"P_t = P_0 \cdot (1 + r)^t \qquad | \qquad \text{Déficit}_t = \text{Demanda}_t - \text{Oferta}_t")

        cd1, cd2, cd3, cd4 = st.columns(4)
        p0_cep = cd1.number_input("Población inicial P0 (hab):", value=35200, step=1000, key="c3_p0")
        r_pob = cd2.slider("Crecimiento poblacional anual (%):", 0.5, 6.0, 3.2, 0.1, key="c3_rpob") / 100.0
        cons_pc = cd3.number_input("Consumo estándar (litros/hab/día):", value=180, step=10, key="c3_cons")
        oferta_m3 = cd4.number_input("Oferta actual instalada (m³/día):", value=5000, step=250, key="c3_ofe")

        anios_c = np.arange(0, 11)
        pob_arr = np.round(p0_cep * ((1.0 + r_pob) ** anios_c))
        dem_arr = np.round((pob_arr * cons_pc) / 1000.0)
        ofe_arr = np.full_like(dem_arr, float(oferta_m3))
        def_arr = np.maximum(0.0, dem_arr - ofe_arr)

        fig_def = go.Figure()
        fig_def.add_trace(go.Scatter(x=anios_c, y=dem_arr, mode="lines+markers", name="Demanda (m³/día)", line=dict(color="#262626", width=2.4)))
        fig_def.add_trace(go.Scatter(x=anios_c, y=ofe_arr, mode="lines", name="Oferta fija instalada (m³/día)", line=dict(color="#0F766E", width=2.2, dash="dash")))
        fig_def.add_trace(go.Bar(x=anios_c, y=def_arr, name="Déficit a cubrir (m³/día)", marker_color="rgba(185, 28, 28, 0.30)"))
        fig_def.update_layout(
            title="Proyección de Demanda, Oferta y Déficit a 10 Años (Modelo Tabla 9 CEPAL)",
            xaxis_title="Año de proyección",
            yaxis_title="Metros cúbicos por día (m³/día)",
            height=300,
            margin=dict(l=15, r=15, t=42, b=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#F8FAFC",
        )
        st.plotly_chart(fig_def, use_container_width=True)

        st.markdown("<div class='sub-header'>Ejercicio 3.2 — Capital de Trabajo NOF y Tasa WACC / CAPM (CEPAL N° 39, págs. 80 y 89–90)</div>", unsafe_allow_html=True)
        col_nof, col_wacc = st.columns(2)
        with col_nof:
            st.markdown("##### Necesidades Operativas de Fondos (NOF — Fórmulas 10–12)")
            v_anual = st.number_input("Ventas anuales ($):", value=64285714, step=1000000, key="c3_va")
            c_anual = st.number_input("Compras anuales de insumos ($):", value=12000000, step=500000, key="c3_ca")
            d1, d2, d3 = st.columns(3)
            d_cli = d1.number_input("Días clientes:", value=45, step=5, key="c3_dcli")
            d_inv = d2.number_input("Días inventario:", value=20, step=5, key="c3_dinv")
            d_pro = d3.number_input("Días proveedores:", value=30, step=5, key="c3_dpro")

            deudores = (v_anual / 365.0) * d_cli
            inventarios = (c_anual / 365.0) * d_inv
            proveedores = (c_anual / 365.0) * d_pro
            nof_tot = deudores + inventarios - proveedores
            st.metric("NOF (Capital de Trabajo Requerido)", _fmt_clp(nof_tot))
            st.caption(
                f"Deudores ({_fmt_clp(deudores)}) + Inventarios ({_fmt_clp(inventarios)}) − Proveedores ({_fmt_clp(proveedores)}). "
                "Mientras más plazo te dan tus proveedores, menos caja propia inmovilizas."
            )

        with col_wacc:
            st.markdown("##### Costo de Capital Ponderado WACC (Ejemplo 18, pág. 90)")
            w1, w2 = st.columns(2)
            ke_w = w1.number_input("Costo capital propio ke (%):", value=15.0, step=0.5, key="c3_ke") / 100.0
            kd_w = w2.number_input("Costo deuda bancaria kd (%):", value=8.0, step=0.5, key="c3_kd") / 100.0
            w3, w4 = st.columns(2)
            peso_d = w3.slider("Peso Deuda D/V (%):", 0, 80, 40, 5, key="c3_dv") / 100.0
            t_imp = w4.number_input("Impuesto renta t (%):", value=30.0, step=1.0, key="c3_tax") / 100.0

            peso_e = 1.0 - peso_d
            wacc_val = ke_w * peso_e + kd_w * (1.0 - t_imp) * peso_d
            st.metric("WACC Resultante", f"{wacc_val*100:.2f}%".replace(".", ","))
            st.caption(
                f"WACC = {ke_w*100:.1f}%×{peso_e*100:.0f}% + {kd_w*100:.1f}%×(1−{t_imp*100:.0f}%)×{peso_d*100:.0f}%. "
                "El escudo tributario (1−t) abarata el costo efectivo de la deuda."
            )

        st.markdown("<div class='sub-header'>Ejercicio 3.3 — Precio Social con Impuesto según Elasticidades (CEPAL N° 39, Cap. IV, pág. 128)</div>", unsafe_allow_html=True)
        ce1, ce2, ce3, ce4 = st.columns(4)
        ps_inp = ce1.number_input("Precio de Oferta ps ($):", value=100.0, step=10.0, key="c3_ps")
        t_el = ce2.slider("Impuesto ad valorem t (%):", 0, 50, 19, 1, key="c3_tel")
        eps_o = ce3.slider("Elasticidad Oferta ε (positiva):", 0.1, 5.0, 1.0, 0.1, key="c3_eps")
        eta_d = ce4.slider("Elasticidad Demanda |η|:", 0.1, 5.0, 1.0, 0.1, key="c3_eta")

        res_el = calcular_precio_social_impuesto_cepal(ps_inp, float(t_el), float(eps_o), float(eta_d))
        ek1, ek2, ek3 = st.columns(3)
        ek1.metric("Precio Oferta ps (Sin Impuesto)", _fmt_clp(res_el["p_oferta"], 2), f"Peso liberación recursos: {res_el['peso_oferta_pct']:.1f}%")
        ek2.metric("Precio Social p* (Ponderado)", _fmt_clp(res_el["p_social"], 2), "Promedio ponderado por elasticidades")
        ek3.metric("Precio Demanda pd (Con Impuesto)", _fmt_clp(res_el["p_demanda"], 2), f"Peso mayor consumo: {res_el['peso_demanda_pct']:.1f}%")

        st.caption(
            "Regla intuitiva: cuando la demanda es muy elástica (|η| grande), el proyecto genera sobre todo nuevo consumo y p* se acerca a pd (con impuesto); "
            "cuando la oferta es muy elástica (ε grande), desplaza productores antiguos y p* se acerca a ps (sin impuesto)."
        )

        with st.expander("Pruébame en 30 segundos — Retos CEPAL Manual N° 39"):
            _render_micro_reto(
                "c3_q1",
                "Definir el problema central como 'Falta un camión recolector' es metodológicamente correcto porque orienta de inmediato la inversión.",
                "Falso",
                "Es confundir el problema con la falta de una solución; impide evaluar alternativas más eficientes como rediseño de rutas o valorización selectiva.",
                "CEPAL Manual N° 39 (2005), Cap. I (págs. 10 y 14)",
            )
            st.divider()
            _render_micro_reto(
                "c3_q2",
                "Al construir el flujo de fondos del proyecto puro (económico), se deben separar y excluir la toma de créditos, amortizaciones e intereses bancarios.",
                "Verdadero",
                "Primero se evalúa si el proyecto es rentable por sí mismo (100% capital propio) y luego se agrega el flujo de financiamiento con su ahorro tributario.",
                "CEPAL Manual N° 39 (2005), Cap. III (págs. 78 y 84–85)",
            )

    # ==========================================================================
    # MÓDULO 4: PRECIOS SOCIALES VIGENTES SNI 2026 (MDSF, 31 MARZO 2026)
    # ==========================================================================
    with m4:
        st.markdown("<div class='sub-header'>Ejercicio 4.1 — Clasificador CIUO-08 y Precio Social de Mano de Obra 2026 (Tablas 1.2–1.3, pág. 4)</div>", unsafe_allow_html=True)
        cm1, cm2, cm3 = st.columns([2.2, 0.8, 1.1])
        opciones_ciuo = [x[0] for x in CIUO_08_SNI_2026]
        sel_ciuo = cm1.selectbox("Selecciona el Gran Grupo Ocupacional (CIUO-08):", opciones_ciuo, index=7, key="sni_ciuo")
        cant_trab = cm2.number_input("Cantidad:", min_value=1, max_value=100, value=2, step=1, key="sni_cant")
        sueldo_bruto = cm3.number_input("Salario bruto mensual ($):", min_value=300000, max_value=8000000, value=600000, step=20000, key="sni_sueldo")

        _, cat_sni, fc_sni = next(x for x in CIUO_08_SNI_2026 if x[0] == sel_ciuo)
        anual_priv = cant_trab * sueldo_bruto * 12
        anual_soc = round(anual_priv * fc_sni)
        dif_soc = anual_priv - anual_soc

        sk1, sk2, sk3, sk4 = st.columns(4)
        sk1.metric("Categoría Oficial SNI", cat_sni, f"Factor FCSMO = {str(fc_sni).replace('.', ',')}")
        sk2.metric("Costo Anual Privado", _fmt_clp(anual_priv))
        sk3.metric("Costo Anual Social", _fmt_clp(anual_soc))
        sk4.metric("Ahorro / Corrección Social", _fmt_clp(dif_soc), "Menor costo de oportunidad país")

        st.markdown("<div class='sub-header'>Ejercicio 4.2 — Calculadora Integral de Beneficios Sociales SNI 2026 (Transporte, VVE, Energía y GEI)</div>", unsafe_allow_html=True)
        st.caption("Moneda oficial al 31 de diciembre de 2025: **UF = $39.727,96 CLP** | **Dólar = $911,18 CLP** | **TSD = 5,5%** | **FCSD = 1,00**.")

        cs1, cs2, cs3, cs4 = st.columns(4)
        horas_urb = cs1.number_input("Horas ahorradas viaje urbano (h-pax/año):", value=5000, step=500, key="sni_hurb")
        horas_esp = cs2.number_input("Horas ahorradas espera/caminata (h-pax/año):", value=1500, step=250, key="sni_hesp")
        vidas_evit = cs3.number_input("Reducción fatalidades viales (VVE/año):", value=0.05, min_value=0.0, max_value=5.0, step=0.01, key="sni_vve")
        kwh_ahor = cs4.number_input("Ahorro energía Baja Tensión (kWh/año):", value=25000, step=5000, key="sni_kwh")

        cs5, cs6, cs7, cs8 = st.columns(4)
        litros_diesel = cs5.number_input("Ahorro diésel camión/bus (litros/año):", value=3000, step=500, key="sni_dies")
        ton_co2 = cs6.number_input("Emisiones evitadas CO2 (t/año):", value=15.0, step=5.0, key="sni_co2")
        ton_ch4 = cs7.number_input("Emisiones evitadas Metano CH4 (t/año):", value=1.5, step=0.5, key="sni_ch4")
        ton_n2o = cs8.number_input("Emisiones evitadas Óxido Nitroso N2O (t/año):", value=0.1, step=0.05, key="sni_n2o")

        val_tiempo = horas_urb * 3338 + horas_esp * 6676
        val_vve = vidas_evit * 2383677600
        val_elec = kwh_ahor * 124.8
        val_comb = litros_diesel * 805
        co2_eq_tot = ton_co2 + 28.0 * ton_ch4 + 265.0 * ton_n2o
        val_gei = co2_eq_tot * 71801
        total_soc_2026 = val_tiempo + val_vve + val_elec + val_comb + val_gei
        uf_2026 = 39727.96

        tk1, tk2, tk3 = st.columns(3)
        tk1.metric("Beneficio Social Total Anual (CLP)", _fmt_clp(total_soc_2026))
        tk2.metric("Equivalente BIP en UF (2026)", f"{_fmt_num(total_soc_2026 / uf_2026, 2)} UF")
        tk3.metric("Total Emisiones Evitadas", f"{_fmt_num(co2_eq_tot, 2)} t CO2eq", f"Valorizadas en {_fmt_clp(val_gei)}")

        fig_sni = go.Figure(go.Bar(
            x=["Tiempo Viaje/Espera", "Seguridad Vial (VVE)", "Energía Eléctrica BT", "Combustible Diésel", "Carbono y GEI"],
            y=[val_tiempo, val_vve, val_elec, val_comb, val_gei],
            marker_color=["#262626", "#404040", "#0F766E", "#475569", "#1E3A8A"],
            text=[_fmt_clp(x) for x in [val_tiempo, val_vve, val_elec, val_comb, val_gei]],
            textposition="outside",
        ))
        fig_sni.update_layout(
            title="Desglose Anual de Beneficios Valorados a Precios Sociales SNI 2026 ($ CLP)",
            yaxis_title="Pesos chilenos ($ CLP)",
            height=300,
            margin=dict(l=15, r=15, t=42, b=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#F8FAFC",
        )
        st.plotly_chart(fig_sni, use_container_width=True)

        with st.expander("Pruébame en 30 segundos — Retos Precios Sociales SNI 2026"):
            _render_micro_reto(
                "sni_q1",
                "Según la tabla CIUO-08 oficial del SNI 2026, los operadores de máquinas y choferes corresponden a Mano de Obra No Calificada (MONC = 0,91).",
                "Falso",
                "Pertenecen al Gran Grupo 8 (Operadores de instalaciones, máquinas y montadores), clasificado como Mano de Obra Semi-Calificada (MOSC = 0,95).",
                "MDSF (2026), Precios Sociales Vigentes 2026, Tablas 1.2 y 1.3 (pág. 4)",
            )
            st.divider()
            _render_micro_reto(
                "sni_q2",
                "En transporte público urbano en Chile (2026), ahorrar 1 hora de espera o caminata tiene exactamente el doble de valor social ($6.676) que ahorrar 1 hora viajando dentro del vehículo ($3.338).",
                "Verdadero",
                "La Tabla 2.1 aplica ponderador 1 al viaje en vehículo ($3.338/h-pax) y ponderador 2 a las fracciones de espera y caminata ($6.676/h-pax).",
                "MDSF (2026), Precios Sociales Vigentes 2026, Tabla 2.1 (pág. 7)",
            )
