# -*- coding: utf-8 -*-
"""
motor_guia_interactiva_bibliografia.py — GUÍA INTERACTIVA, EJERCICIOS Y MODO CUADERNO
Respaldo bibliográfico oficial — Evaluación Integrada de Proyectos (FDIC26), ULagos:
  1. Ernesto R. Fontaine (2008), Evaluación Social de Proyectos (13.ª ed., Pearson).
  2. Edgar Ortegón, Juan Francisco Pacheco y Horacio Roura (2005), Metodología general de
     identificación, preparación y evaluación de proyectos de inversión pública (CEPAL N° 39).
  3. MDSF / SNI (2026), Reporte Anual Precios Sociales Vigentes 2026 (31 marzo 2026).

Enfoque pedagógico: aprender haciendo con simuladores breves, gráficos limpios,
desplegables "Paso a paso y tabla para copiar al cuaderno" con sustitución en vivo
y micro-retos de autoevaluación en 30 segundos.
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


def _clp_md(valor: float, dec: int = 0) -> str:
    r"""Devuelve monto en CLP con el signo $ escapado (\$), evitando que Streamlit active LaTeX por error."""
    return _fmt_clp(valor, dec).replace("$", r"\$")


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
            "Costo Alt. C_i ($)": round(c_alt, 2),
            "Benef. Neto BN_i ($)": round(bn_i, 2),
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


def resolver_mercado_insumo_clase2(
    a_of: float = 20.0,
    b_of: float = 0.05,
    c_dem: float = 200.0,
    d_dem: float = 0.04,
    y_proy: float = 400.0,
) -> dict:
    """
    Espejo exacto de Clase2.pdf (láminas 26–28): Mercado del Insumo sin distorsiones.
    Oferta: P_o = a_of + b_of * Y_o  |  Demanda inicial: P_d = c_dem - d_dem * Y_d
    Al demandar Y_proy unidades adicionales, la demanda se desplaza a la derecha:
      P_d' = c_dem - d_dem * (Y - Y_proy)
    Costo Social Total: CS = DD (Disminución de Demanda) + CP (Costo de Producción).
    """
    y0 = (c_dem - a_of) / (b_of + d_dem)
    p0 = a_of + b_of * y0
    # Nuevo equilibrio con proyecto: a_of + b_of * Y2 = c_dem - d_dem * (Y2 - y_proy)
    y2 = (c_dem - a_of + d_dem * y_proy) / (b_of + d_dem)
    p1 = a_of + b_of * y2
    y1 = y2 - y_proy  # Consumo de antiguos demandantes al precio mayor p1

    delta_dd_q = y0 - y1  # Reducción de consumo de otros demandantes
    delta_cp_q = y2 - y0  # Mayor producción del insumo

    valor_dd = 0.5 * (p0 + p1) * delta_dd_q
    valor_cp = 0.5 * (p0 + p1) * delta_cp_q
    cs_total = valor_dd + valor_cp
    costo_privado = p1 * y_proy
    p_social_ins = (cs_total / y_proy) if y_proy > 0 else p0

    return {
        "y0": y0,
        "p0": p0,
        "y1": y1,
        "y2": y2,
        "p1": p1,
        "y_proy": y_proy,
        "delta_dd_q": delta_dd_q,
        "delta_cp_q": delta_cp_q,
        "valor_dd": valor_dd,
        "valor_cp": valor_cp,
        "cs_total": cs_total,
        "costo_privado": costo_privado,
        "p_social_ins": p_social_ins,
    }


def calcular_tabla_credito_frances_clase1(
    monto_p: float = 1000.0,
    tasa_r: float = 0.10,
    plazo_n: int = 10,
) -> tuple[float, pd.DataFrame]:
    """Replica exactamente la tabla de desarrollo de crédito de Clase1 (láminas 31–32)."""
    if tasa_r > 0:
        cuota = monto_p * (tasa_r / (1.0 - (1.0 + tasa_r) ** (-plazo_n)))
    else:
        cuota = monto_p / max(1, plazo_n)

    filas = [{"Año": 0, "Deuda Saldo": round(monto_p, 2), "Interés": 0.0, "Amortización": 0.0, "Cuota": 0.0}]
    saldo = float(monto_p)
    tot_int = 0.0
    tot_amo = 0.0
    tot_cuo = 0.0
    for t in range(1, int(plazo_n) + 1):
        interes = saldo * tasa_r
        amort = cuota - interes
        if t == int(plazo_n):
            amort = saldo
            cuota_ef = interes + amort
            saldo = 0.0
        else:
            cuota_ef = cuota
            saldo = max(0.0, saldo - amort)
        tot_int += interes
        tot_amo += amort
        tot_cuo += cuota_ef
        filas.append({
            "Año": t,
            "Deuda Saldo": round(saldo, 2),
            "Interés": round(interes, 2),
            "Amortización": round(amort, 2),
            "Cuota": round(cuota_ef, 2),
        })
    filas.append({
        "Año": "TOTAL",
        "Deuda Saldo": 0.0,
        "Interés": round(tot_int, 2),
        "Amortización": round(tot_amo, 2),
        "Cuota": round(tot_cuo, 2),
    })
    return round(cuota, 4), pd.DataFrame(filas)


def calcular_venta_activo_clase1(
    valor_inicial: float = 10000000.0,
    vida_util_legal: int = 10,
    anio_venta: int = 6,
    valor_venta: float = 5500000.0,
    tasa_impuesto: float = 0.25,
) -> dict:
    """Replica el tratamiento tributario de Ganancia/Pérdida de Capital y Valor Libro (Clase1, lámina 22)."""
    dep_anual = valor_inicial / max(1, vida_util_legal)
    dep_acum = min(valor_inicial, dep_anual * min(anio_venta, vida_util_legal))
    valor_libro = max(0.0, valor_inicial - dep_acum)
    ganancia_cap = valor_venta - valor_libro
    efecto_imp = -ganancia_cap * tasa_impuesto  # Si hay ganancia, se paga impuesto (-); si hay pérdida, hay ahorro fiscal (+)
    flujo_neto_venta = valor_venta + efecto_imp
    return {
        "dep_anual": dep_anual,
        "dep_acum": dep_acum,
        "valor_libro": valor_libro,
        "ganancia_cap": ganancia_cap,
        "efecto_imp": efecto_imp,
        "flujo_neto_venta": flujo_neto_venta,
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
        "<div class='sec-header'>GUÍA INTERACTIVA Y MODO CUADERNO — FONTAINE (13.ª ED.), CEPAL MANUAL N° 39 Y SNI 2026</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Cuatro mini-laboratorios visuales con ejercicios paso a paso de la bibliografía oficial: mueve los controles, "
        "abre el desplegable 'Ver paso a paso y tabla para copiar al cuaderno' para revisar la sustitución numérica exacta y valida lo aprendido en 30 segundos."
    )

    m1, m2, m3, m4, m5 = st.tabs([
        "1. Precios Mentirosos, VA y Costos Hundidos (Fontaine I–II)",
        "2. Trampas de la TIR y ¿Cuándo Cortar el Bosque? (Fontaine III–IV)",
        "3. Déficit, NOF, WACC y Elasticidades (CEPAL N° 39)",
        "4. Conversor y Casos Precios Sociales SNI 2026 (MDSF)",
        "5. Ejercicios Oficiales Clases 1, 2 y 3 (Modo Cuaderno)",
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
                f"* **Trampa del Valor Agregado:** Con pan envasado a **{_clp_md(precio_env)}**, el Valor Agregado sube en **{_clp_md(hp['delta_va'])}**, "
                f"pero el Excedente cambia en **{_clp_md(hp['delta_exc'])}** porque agregar más mano de obra y capital también es costo.\n"
                f"* **Precio Mentiroso (pág. 30):** Si el panadero paga un insumo subsidiado en **{_clp_md(distorsion_agua)}**, su excedente privado es "
                f"**{_clp_md(hp['exc_base'])}**, pero el excedente social real es **{_clp_md(hp['exc_soc_base'])}**.\n"
                "* **Situación Base Optimizada (págs. 4–10):** Antes de construir un puerto nuevo o una autopista, optimiza lo actual "
                "(3 turnos, tarifas diferenciadas por horario) para no atribuir al proyecto beneficios que no le corresponden."
            )

        with st.expander("Ver paso a paso y tabla para copiar al cuaderno (Ejercicio 1.1)"):
            st.latex(r"E = P - CTP \qquad | \qquad VA = P - \text{Otros Insumos} = \text{Trabajo} + \text{Capital} + E")
            st.markdown(
                f"**1. Caso Base (Pan sin envasar):**\n"
                f"- **Costo Total Privado (CTP₀):** \\$80 (insumos) + \\$15 (trabajo) + \\$5 (capital) = **\\$100**\n"
                f"- **Excedente Privado (E₀):** {_clp_md(precio_pan)} − \\$100 = **{_clp_md(hp['exc_base'])}**\n"
                f"- **Valor Agregado (VA₀):** {_clp_md(precio_pan)} − \\$80 = **{_clp_md(hp['va_base'])}** (equivale a \\$15 + \\$5 + {_clp_md(hp['exc_base'])})\n\n"
                f"**2. Proyecto de Envasado y Reparto (+\\$30 de costo adicional: \\$10 bolsas/gas + \\$12 trabajo + \\$8 capital):**\n"
                f"- **Costo Total Nuevo (CTP₁):** \\$100 + \\$30 = **\\$130**\n"
                f"- **Excedente Nuevo (E₁):** {_clp_md(precio_env)} − \\$130 = **{_clp_md(hp['exc_amp'])}** (variación ΔE = **{_clp_md(hp['delta_exc'])}**)\n"
                f"- **Valor Agregado Nuevo (VA₁):** {_clp_md(precio_env)} − (\\$80 + \\$10) = **{_clp_md(hp['va_amp'])}** (variación ΔVA = **{_clp_md(hp['delta_va'])}**)\n\n"
                f"**3. Ajuste Social por Precio Mentiroso (subsidio oculto de {_clp_md(distorsion_agua)}):**\n"
                f"- **Costo Social Base (CTS₀):** \\$100 + {_clp_md(distorsion_agua)} = **{_clp_md(hp['cts_base'])}** → **Excedente Social:** {_clp_md(precio_pan)} − {_clp_md(hp['cts_base'])} = **{_clp_md(hp['exc_soc_base'])}**"
            )
            df_c11 = pd.DataFrame([
                ["Pan Base", "$80", "$15", "$5", "$100", _fmt_clp(precio_pan), _fmt_clp(hp["va_base"]), _fmt_clp(hp["exc_base"]), _fmt_clp(hp["exc_soc_base"])],
                ["Pan Envasado", "$90", "$27", "$13", "$130", _fmt_clp(precio_env), _fmt_clp(hp["va_amp"]), _fmt_clp(hp["exc_amp"]), _fmt_clp(hp["exc_amp"] - distorsion_agua)],
                ["Diferencia (Δ)", "+$10", "+$12", "+$8", "+$30", f"{precio_env - precio_pan:+.0f}", f"{hp['delta_va']:+.0f}", f"{hp['delta_exc']:+.0f}", f"{hp['delta_exc']:+.0f}"],
            ], columns=["Alternativa", "Otros Insumos", "Trabajo", "Capital", "CTP", "Precio", "Valor Agregado", "Exc. Privado", "Exc. Social"])
            st.dataframe(df_c11, use_container_width=True, hide_index=True)

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
            nota_dec = "Ingreso anual mínimo exigido para formar la fábrica: **\\$7.150/año** (el estudio de \\$250 es historia)."
            desarrollo_c12 = (
                "- **Costos directos evitables:** \\$5.400 (MO) + \\$350 (patente) + \\$95 (impuesto 1%) + \\$155 (sueldo dueño) = **\\$6.000**\n"
                "- **Capital evitable total:** \\$9.000 (máquina) + \\$500 (edificio) + \\$700 (permiso) + \\$1.300 (capital de trabajo) = **\\$11.500**\n"
                "- **Costo de capital al 10%:** 0,10 × \\$11.500 = **\\$1.150**\n"
                "- **Ingreso mínimo exigido:** \\$6.000 + \\$1.150 = **\\$7.150/año** (se omite el estudio de \\$250 por ser costo hundido)."
            )
        elif decision.startswith("B."):
            int_recup = round(val_liq_maq * 0.10)
            ing_min = 6000 + int_recup + 130
            df_cost = pd.DataFrame([
                ["Estudio ($250) y Permiso construcción ($700)", "Hundidos (NO entran)", "$0", "El permiso era evitable antes de construir, pero ya es irrecuperable."],
                ["Costos directos anuales + sueldo dueño", "Evitables (SÍ entran)", "$6.000", "Si cierras la planta, dejas de pagar sueldos, patente e impuesto."],
                [f"Interés 10% sobre liquidación (${val_liq_maq:,.0f})".replace(",", "."), "Recuperable (SÍ entra)", _fmt_clp(int_recup), "No importa el costo original ($9.500), solo lo que hoy recuperas al vender."],
                ["Interés 10% sobre capital circulante ($1.300)", "Recuperable (SÍ entra)", "$130", "El capital de trabajo se recupera al cerrar y rendiría 10% en el banco."],
            ], columns=["Partida (Fontaine, págs. 48–49)", "Clasificación Económica", "Costo Pertinente", "Por qué entra o sale"])
            nota_dec = f"Ingreso anual mínimo para seguir operando: **{_clp_md(ing_min)}/año** (si ganas más que esto, conviene seguir aunque no recuperes la inversión histórica)."
            desarrollo_c12 = (
                f"- **Costos directos evitables si cierras:** **\\$6.000**\n"
                f"- **Capital recuperable hoy:** {_clp_md(val_liq_maq)} (liquidación) + \\$1.300 (capital de trabajo) = **{_clp_md(val_liq_maq + 1300)}**\n"
                f"- **Costo de oportunidad al 10%:** 0,10 × {_clp_md(val_liq_maq + 1300)} = **{_clp_md(int_recup + 130)}**\n"
                f"- **Ingreso mínimo para continuar operando:** \\$6.000 + {_clp_md(int_recup)} + \\$130 = **{_clp_md(ing_min)}/año** (se omiten el estudio de \\$250, el permiso de \\$700 y el costo histórico de \\$9.500)."
            )
        else:
            ing_min = 4550
            df_cost = pd.DataFrame([
                ["Gastos actuales de la fábrica ($7.150)", "No pertinentes (NO entran)", "$0", "Ya se incurren con o sin la máquina adicional."],
                ["Mano de obra adicional", "Marginal (SÍ entra)", "$3.450", "Solo se contrata si compras la nueva máquina."],
                ["Interés 10% máquina adicional ($10.000)", "Marginal (SÍ entra)", "$1.000", "Costo de oportunidad del capital nuevo comprometido."],
                ["Impuesto anual adicional (1% sobre $10.000)", "Marginal (SÍ entra)", "$100", "Aumento tributario incremental del nuevo equipo."],
            ], columns=["Partida (Fontaine, págs. 50–51)", "Clasificación Económica", "Costo Pertinente", "Por qué entra o sale"])
            nota_dec = "Ingreso adicional mínimo para comprar la máquina: **\\$4.550/año**. Nunca decidas comparando contra el costo medio total (\\$5,85) si el precio marginal (\\$5,00) supera al costo marginal (\\$4,55)."
            desarrollo_c12 = (
                "- **Regla Marginal:** ΔIngreso > ΔCosto\n"
                "- **ΔCosto anual:** \\$3.450 (MO extra) + 0,10 × \\$10.000 (capital) + 0,01 × \\$10.000 (impuesto) = **\\$4.550**\n"
                "- **Comprobación con pedido extra (1.000 unid. a \\$5,00):** ΔIngreso = \\$5.000 > \\$4.550 → **utilidad incremental de +\\$450**, aunque el costo medio total sea \\$5,85."
            )

        st.info(nota_dec)
        st.dataframe(df_cost, use_container_width=True, hide_index=True)
        with st.expander("Ver paso a paso para copiar al cuaderno (Ejercicio 1.2)"):
            st.markdown(desarrollo_c12)

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
        disc = f1 * f1 - 4.0 * f0 * f2
        if abs(f0) > 1e-9:
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
                "En el relleno sanitario (-10, +50, -60), las TIR son **100%** y **200%**, pero a **r = 10%** el VAN es **-\\$14,13**. "
                "La regla del VAN nunca se equivoca porque descuenta a la tasa real del mercado y no supone reinversión a la TIR."
            )

        with st.expander("Ver paso a paso para copiar al cuaderno (Ejercicio 2.1 — VAN y raíces de TIR)"):
            vp1 = f1 / (1.0 + r_eval)
            vp2 = f2 / ((1.0 + r_eval) ** 2)
            st.latex(r"VAN(r) = F_0 + \frac{F_1}{(1+r)^1} + \frac{F_2}{(1+r)^2}")
            st.markdown(
                f"**1. Evaluación exacta del VAN a r = {r_eval*100:.1f}%:**\n"
                f"- **Año 0 (hoy):** {_clp_md(f0, 2)}\n"
                f"- **Año 1 descontado:** {_fmt_num(f1, 2)} ÷ (1 + {r_eval:.2f})¹ = **{_clp_md(vp1, 2)}**\n"
                f"- **Año 2 descontado:** {_fmt_num(f2, 2)} ÷ (1 + {r_eval:.2f})² = **{_clp_md(vp2, 2)}**\n"
                f"- **Resultado VAN:** {_clp_md(f0, 2)} + ({_clp_md(vp1, 2)}) + ({_clp_md(vp2, 2)}) = **{_clp_md(van_actual, 2)}**\n\n"
                f"**2. Ecuación cuadrática de la TIR (sea x = 1 + ρ):**\n"
                f"- F₀·x² + F₁·x + F₂ = 0 → ({f0:.1f})x² + ({f1:.1f})x + ({f2:.1f}) = 0\n"
                f"- Discriminante Δ = ({f1:.1f})² − 4·({f0:.1f})·({f2:.1f}) = **{_fmt_num(disc, 2)}** → **TIR(s):** `{', '.join(raices_txt) if raices_txt else 'Sin raíz real'}`."
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
                f"El beneficio del primer año ({_clp_md(b1_tri)}) aún no cubre el costo de oportunidad neto del capital."
            )
        else:
            st.success(
                f"**TRI = {tri_val*100:.2f}% ≥ (r − α) = {umbral_tri*100:.2f}%** → **EJECUTAR AHORA.** "
                "Postergar un año más hace perder más beneficio que lo ahorrado en costo de capital."
            )

        with st.expander("Ver paso a paso y Cuadro IV.5 completo para copiar al cuaderno (Ejercicio 2.2)"):
            fila_opt = df_bosq[df_bosq["Año"] == opt_1ciclo].iloc[0]
            st.latex(r"K_i = \frac{B_i}{B_{i-1}} - 1 \quad | \quad \rho_i = \left(\frac{B_i}{I_0}\right)^{1/i} - 1 \quad | \quad TRI = \frac{B_1}{C}")
            st.markdown(
                f"**Cálculos clave del Cuadro IV.5 (con inversión inicial I₀ = \\$100 y tasa r = {r_bosque*100:.1f}%):**\n"
                f"- **1 Ciclo (cortar cuando Kᵢ ≈ r):** óptimo en **Año {opt_1ciclo}** → VAN = {_fmt_num(fila_opt['Valor Madera ($)'], 2)} ÷ (1 + {r_bosque:.3f})^{opt_1ciclo} − 100 = **{_clp_md(fila_opt['VAN 1 Ciclo ($)'], 2)}**\n"
                f"- **Reinvertir todo el flujo (máxima TIR promedio ρᵢ):** óptimo en **Año {opt_tir}** (TIR = **{_fmt_num(df_bosq['TIR Promedio (%)'].max(), 2)}%**)\n"
                f"- **Tierra limitada (reinvertir siempre \\$100, máximo VAE):** óptimo en **Año {opt_vae}** (VAE = **{_clp_md(df_bosq['VAE ($/año)'].max(), 2)}/año**)\n"
                f"- **Sustitución TRI (obra vial):** TRI = {b1_tri:.2f} ÷ {inv_tri:.2f} = **{tri_val*100:.2f}%** frente a (r − α) = {r_tri*100:.2f}% − {alpha_tri*100:.2f}% = **{umbral_tri*100:.2f}%**"
            )
            df_bosq_vis = df_bosq.copy()
            for col_n in df_bosq_vis.columns:
                if col_n != "Año":
                    df_bosq_vis[col_n] = df_bosq_vis[col_n].map(lambda x: _fmt_num(x, 2))
            st.dataframe(df_bosq_vis, use_container_width=True, hide_index=True)

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

        with st.expander("Ver paso a paso y Tabla 9 completa para copiar al cuaderno (Ejercicio 3.1)"):
            st.markdown(
                f"**Sustitución de ejemplo (Año 0 y Año 10):**\n"
                f"- **Año 0:** P₀ = {_fmt_num(pob_arr[0], 0)} hab → Demanda₀ = ({_fmt_num(pob_arr[0], 0)} × {cons_pc}) ÷ 1.000 = **{_fmt_num(dem_arr[0], 0)} m³/día** → Déficit₀ = {_fmt_num(dem_arr[0], 0)} − {_fmt_num(oferta_m3, 0)} = **{_fmt_num(def_arr[0], 0)} m³/día**\n"
                f"- **Año 10:** P₁₀ = {_fmt_num(p0_cep, 0)} × (1 + {r_pob:.3f})¹⁰ = {_fmt_num(pob_arr[10], 0)} hab → Demanda₁₀ = **{_fmt_num(dem_arr[10], 0)} m³/día** → Déficit₁₀ = **{_fmt_num(def_arr[10], 0)} m³/día**"
            )
            df_t9 = pd.DataFrame({
                "Año": [f"Año {a}" for a in anios_c],
                "Población (hab)": [_fmt_num(x, 0) for x in pob_arr],
                "Demanda (m³/día)": [_fmt_num(x, 0) for x in dem_arr],
                "Oferta Actual (m³/día)": [_fmt_num(x, 0) for x in ofe_arr],
                "Déficit a Cubrir (m³/día)": [_fmt_num(x, 0) for x in def_arr],
            })
            st.dataframe(df_t9, use_container_width=True, hide_index=True)

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
                f"Deudores ({_clp_md(deudores)}) + Inventarios ({_clp_md(inventarios)}) − Proveedores ({_clp_md(proveedores)}). "
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

        with st.expander("Ver paso a paso para copiar al cuaderno (Ejercicio 3.2 — NOF y WACC)"):
            st.latex(r"NOF = \text{Deudores} + \text{Inventarios} - \text{Proveedores} \qquad | \qquad WACC = k_e\frac{E}{V} + k_d(1-t)\frac{D}{V}")
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                st.markdown(
                    f"**A. Cálculo de NOF (CEPAL pág. 80):**\n"
                    f"1. **Deudores:** ({_clp_md(v_anual)} ÷ 365) × {d_cli} días = **{_clp_md(deudores)}**\n"
                    f"2. **Inventarios:** ({_clp_md(c_anual)} ÷ 365) × {d_inv} días = **{_clp_md(inventarios)}**\n"
                    f"3. **Proveedores:** ({_clp_md(c_anual)} ÷ 365) × {d_pro} días = **{_clp_md(proveedores)}**\n"
                    f"4. **NOF Total:** {_clp_md(deudores)} + {_clp_md(inventarios)} − {_clp_md(proveedores)} = **{_clp_md(nof_tot)}**"
                )
            with c_n2:
                comp_e = ke_w * peso_e * 100.0
                comp_d = kd_w * (1.0 - t_imp) * peso_d * 100.0
                st.markdown(
                    f"**B. Cálculo de WACC (CEPAL págs. 89–90):**\n"
                    f"1. **Aporte Patrimonio:** {ke_w*100:.2f}% × {peso_e:.2f} = **{comp_e:.2f}%**\n"
                    f"2. **Deuda neta de impuesto:** {kd_w*100:.2f}% × (1 − {t_imp:.2f}) = **{kd_w*(1-t_imp)*100:.2f}%**\n"
                    f"3. **Aporte Deuda:** {kd_w*(1-t_imp)*100:.2f}% × {peso_d:.2f} = **{comp_d:.2f}%**\n"
                    f"4. **WACC Resultante:** {comp_e:.2f}% + {comp_d:.2f}% = **{wacc_val*100:.2f}%**"
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

        with st.expander("Ver paso a paso para copiar al cuaderno (Ejercicio 3.3 — Fórmula 27 CEPAL)"):
            st.latex(r"p_d = p_s(1+t) \qquad | \qquad p^* = \frac{\varepsilon}{\varepsilon + |\eta|} p_s + \frac{|\eta|}{\varepsilon + |\eta|} p_d")
            st.markdown(
                f"1. **Precio con impuesto (p_d):** {_clp_md(ps_inp, 2)} × (1 + {t_el/100.0:.2f}) = **{_clp_md(res_el['p_demanda'], 2)}**\n"
                f"2. **Ponderador Oferta (w_s):** {eps_o:.1f} ÷ ({eps_o:.1f} + {eta_d:.1f}) = **{res_el['peso_oferta_pct']/100.0:.4f}** ({res_el['peso_oferta_pct']:.1f}%)\n"
                f"3. **Ponderador Demanda (w_d):** {eta_d:.1f} ÷ ({eps_o:.1f} + {eta_d:.1f}) = **{res_el['peso_demanda_pct']/100.0:.4f}** ({res_el['peso_demanda_pct']:.1f}%)\n"
                f"4. **Precio Social (p*):** ({res_el['peso_oferta_pct']/100.0:.4f} × {_clp_md(ps_inp, 2)}) + ({res_el['peso_demanda_pct']/100.0:.4f} × {_clp_md(res_el['p_demanda'], 2)}) = **{_clp_md(res_el['p_social'], 2)}**"
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

        with st.expander("Ver paso a paso para copiar al cuaderno (Ejercicio 4.1 — PSMO)"):
            st.latex(r"PSMO = \text{Salario Bruto Anual} \times FCSMO")
            st.markdown(
                f"1. **Clasificación CIUO-08:** `{sel_ciuo}` → **{cat_sni}** (FCSMO = {str(fc_sni).replace('.', ',')})\n"
                f"2. **Costo Anual Privado:** {cant_trab} × {_clp_md(sueldo_bruto)} × 12 meses = **{_clp_md(anual_priv)}**\n"
                f"3. **Precio Social Anual (PSMO):** {_clp_md(anual_priv)} × {str(fc_sni).replace('.', ',')} = **{_clp_md(anual_soc)}** (corrección social: **{_clp_md(dif_soc)}**)"
            )

        st.markdown("<div class='sub-header'>Ejercicio 4.2 — Calculadora Integral de Beneficios Sociales SNI 2026 (Transporte, VVE, Energía y GEI)</div>", unsafe_allow_html=True)
        st.caption("Moneda oficial al 31 de diciembre de 2025: **UF = \\$39.727,96 CLP** | **Dólar = \\$911,18 CLP** | **TSD = 5,5%** | **FCSD = 1,00**.")

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

        with st.expander("Ver paso a paso y tabla completa para copiar al cuaderno (Ejercicio 4.2 — SNI 2026)"):
            st.latex(r"CO_2\text{eq} = t_{CO_2} + 28 \cdot t_{CH_4} + 265 \cdot t_{N_2O} \qquad | \qquad \text{Total UF} = \frac{\text{Beneficio CLP}}{39.727,96}")
            st.markdown(
                f"- **Carbono Equivalente (Tabla 5.2):** {_fmt_num(ton_co2, 2)} + 28 × ({_fmt_num(ton_ch4, 2)}) + 265 × ({_fmt_num(ton_n2o, 2)}) = **{_fmt_num(co2_eq_tot, 2)} t CO₂eq** → valorizado a \\$71.801/t = **{_clp_md(val_gei)}**\n"
                f"- **Equivalente BIP en UF:** {_clp_md(total_soc_2026)} ÷ \\$39.727,96 = **{_fmt_num(total_soc_2026 / uf_2026, 2)} UF/año**"
            )
            df_sni_cuad = pd.DataFrame([
                ["Ahorro Tiempo Viaje Urbano", f"{_fmt_num(horas_urb, 0)} h-pax", "$3.338 / h-pax", _fmt_clp(horas_urb * 3338), "Tabla 2.1 (pág. 7)"],
                ["Ahorro Espera / Caminata (×2)", f"{_fmt_num(horas_esp, 0)} h-pax", "$6.676 / h-pax", _fmt_clp(horas_esp * 6676), "Tabla 2.1 (pág. 7)"],
                ["Seguridad Vial (VVE = 60.000 UF)", f"{_fmt_num(vidas_evit, 2)} vidas est.", "$2.383.677.600", _fmt_clp(val_vve), "Tabla 3.1 (pág. 11)"],
                ["Ahorro Electricidad Baja Tensión", f"{_fmt_num(kwh_ahor, 0)} kWh", "$124,8 / kWh", _fmt_clp(val_elec), "Tabla 5.3 (pág. 18)"],
                ["Ahorro Combustible Diésel", f"{_fmt_num(litros_diesel, 0)} litros", "$805 / litro", _fmt_clp(val_comb), "Tabla 4.1 (pág. 12)"],
                ["Emisiones Evitadas GEI (CO2eq)", f"{_fmt_num(co2_eq_tot, 2)} t CO2eq", "$71.801 / t CO2eq", _fmt_clp(val_gei), "Tablas 5.1–5.2 (págs. 16–17)"],
                ["TOTAL BENEFICIO SOCIAL ANUAL", "Suma anual", "UF = $39.727,96", f"{_fmt_clp(total_soc_2026)} ({_fmt_num(total_soc_2026 / uf_2026, 2)} UF)", "Anexo 1 (pág. 19)"],
            ], columns=["Concepto SNI 2026", "Cantidad Física", "Precio Social 2026", "Valor Anual ($ CLP)", "Referencia MDSF"])
            st.dataframe(df_sni_cuad, use_container_width=True, hide_index=True)

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
                "En transporte público urbano en Chile (2026), ahorrar 1 hora de espera o caminata tiene exactamente el doble de valor social (\\$6.676) que ahorrar 1 hora viajando dentro del vehículo (\\$3.338).",
                "Verdadero",
                "La Tabla 2.1 aplica ponderador 1 al viaje en vehículo (\\$3.338/h-pax) y ponderador 2 a las fracciones de espera y caminata (\\$6.676/h-pax).",
                "MDSF (2026), Precios Sociales Vigentes 2026, Tabla 2.1 (pág. 7)",
            )

    # ==========================================================================
    # MÓDULO 5: EJERCICIOS OFICIALES DE CLASES 1, 2, 3, MARCO LÓGICO Y LEY REP
    # ==========================================================================
    with m5:
        st.caption(
            "Ejercicios tomados directamente de las diapositivas de la Dra. Luz María Ferrada (`Clase1`, `Clase2`, `Clase3`, "
            "`MARCO LOGICO` y `Trabajo 1`), con sus incógnitas resueltas y desarrollo listo para copiar al cuaderno."
        )

        # ----------------------------------------------------------------------
        # 5.1 MERCADO DE LA LECHE (-50), MERCADO DEL INSUMO Y 4 CASOS EXTREMOS
        # ----------------------------------------------------------------------
        st.markdown("<div class='sub-header'>Ejercicio 5.1 — Mercado de la Leche (Corregido -50), Mercado del Insumo y 4 Casos Extremos (Clase 2, láminas 16–28)</div>", unsafe_allow_html=True)

        tipo_mkt = st.radio(
            "Selecciona qué mercado de la Clase 2 quieres estudiar:",
            [
                "A. Mercado del Producto — Ejercicio Oficial de la Leche (Po = -50 + 0,025·Qo | Pd = 300 - 0,0205·Qd)",
                "B. Mercado del Insumo — Costo Social CS = DD + CP (Láminas 26–28)",
                "C. Los 4 Casos Extremos de Elasticidad (Láminas 16–19)",
            ],
            key="c5_tipo_mkt",
        )

        if tipo_mkt.startswith("A."):
            cl1, cl2, cl3 = st.columns(3)
            a_lec = cl1.number_input("Intercepto Oferta (a):", value=-50.0, step=10.0, key="c5_alec")
            c_lec = cl2.number_input("Intercepto Demanda (c):", value=300.0, step=10.0, key="c5_clec")
            qp_lec = cl3.number_input("Producción Cooperativa (Q_proy ton/año):", value=1470.0, step=50.0, key="c5_qplec")
            b_lec, d_lec = 0.025, 0.0205

            q0_l = (c_lec - a_lec) / (b_lec + d_lec)
            p0_l = a_lec + b_lec * q0_l
            qo1_l = (c_lec - a_lec - d_lec * qp_lec) / (b_lec + d_lec)
            qd1_l = qo1_l + qp_lec
            p1_l = c_lec - d_lec * qd1_l

            ad_l = 0.5 * (p0_l + p1_l) * (qd1_l - q0_l)
            lr_l = 0.5 * (p0_l + p1_l) * (q0_l - qo1_l)
            vsp_l = ad_l + lr_l
            vpp_l = p1_l * qp_lec
            dec_l = (p0_l - p1_l) * q0_l + 0.5 * (p0_l - p1_l) * (qd1_l - q0_l)
            dep_l = -((p0_l - p1_l) * qo1_l + 0.5 * (p0_l - p1_l) * (q0_l - qo1_l))
            psoc_l = vsp_l / qp_lec if qp_lec > 0 else p0_l

            mk1, mk2, mk3, mk4 = st.columns(4)
            mk1.metric("a) Equilibrio Inicial (Q0, P0)", f"Q0 = {_fmt_num(q0_l, 1)} t", f"P0 = {_fmt_clp(p0_l, 2)}")
            mk2.metric("b) Nuevo Equilibrio (Qd1, P1)", f"Qd1 = {_fmt_num(qd1_l, 1)} t", f"P1 = {_fmt_clp(p1_l, 2)} | Qo1 = {_fmt_num(qo1_l, 0)}")
            mk3.metric("c) VSP = AD + LR", _fmt_clp(vsp_l), f"AD {_fmt_clp(ad_l)} + LR {_fmt_clp(lr_l)}")
            mk4.metric("e) Precio Social P*", f"{_fmt_clp(psoc_l, 2)}/ton", f"VPP privado: {_fmt_clp(vpp_l)}")

            with st.expander("Ver resolución completa de incisos a), b), c), d) y e) para copiar al cuaderno (Láminas 20–25)"):
                st.latex(r"VSP = AD + LR = VPP + \Delta EC + \Delta EP \qquad | \qquad P^* = \frac{VSP}{Q_{\text{proy}}} = \frac{P_0 + P_1}{2}")
                st.markdown(
                    f"**a) Equilibrio inicial sin proyecto:**\n"
                    f"- Igualamos oferta y demanda: {a_lec:.1f} + 0,025·Q₀ = {c_lec:.1f} − 0,0205·Q₀ → 0,0455·Q₀ = {c_lec - a_lec:.1f}\n"
                    f"- Q₀ = {c_lec - a_lec:.1f} ÷ 0,0455 = **{_fmt_num(q0_l, 2)} ton** → P₀ = {c_lec:.1f} − 0,0205 × {_fmt_num(q0_l, 2)} = **{_clp_md(p0_l, 2)}**\n\n"
                    f"**b) Nuevo equilibrio con la cooperativa (Q' = Qₒ + {qp_lec:.0f}):**\n"
                    f"- {a_lec:.1f} + 0,025·(Q' − {qp_lec:.0f}) = {c_lec:.1f} − 0,0205·Q' → 0,0455·Q' = {c_lec - a_lec + b_lec*qp_lec:.2f}\n"
                    f"- Consumo total Q_d1 = **{_fmt_num(qd1_l, 2)} ton**, antiguos productores Q_o1 = **{_fmt_num(qo1_l, 2)} ton**, precio P₁ = **{_clp_md(p1_l, 2)}**\n"
                    f"- Ingresos privados (VPP): {_clp_md(p1_l, 2)} × {qp_lec:.0f} = **{_clp_md(vpp_l)}** *(nota: en pizarra la profesora redondea P₁ ≈ \\$125 → \\$183.750)*.\n\n"
                    f"**c) Enfoque de Eficiencia (VSP = AD + LR):**\n"
                    f"- **AD:** {_clp_md(psoc_l, 2)} × ({_fmt_num(qd1_l, 2)} − {_fmt_num(q0_l, 2)}) = **{_clp_md(ad_l)}**\n"
                    f"- **LR:** {_clp_md(psoc_l, 2)} × ({_fmt_num(q0_l, 2)} − {_fmt_num(qo1_l, 2)}) = **{_clp_md(lr_l)}**\n"
                    f"- **VSP Total = AD + LR = {_clp_md(vsp_l)}**\n\n"
                    f"**d) Enfoque de Agencia (conciliación exacta de las '?' en láminas 23–24):**\n"
                    f"- **ΔEC (ganan consumidores):** **+{_clp_md(dec_l)}**\n"
                    f"- **ΔEP (pierden antiguos productores):** **{_clp_md(dep_l)}**\n"
                    f"- **Suma por Agencia:** {_clp_md(vpp_l)} + {_clp_md(dec_l)} + ({_clp_md(dep_l)}) = **{_clp_md(vpp_l + dec_l + dep_l)}** (idéntico al enfoque de eficiencia).\n\n"
                    f"**e) Precio Social Unitario (lámina 25):**\n"
                    f"- **P*** = {_clp_md(vsp_l)} ÷ {qp_lec:.0f} = **{_clp_md(psoc_l, 2)}/ton** (promedio exacto entre P₀ y P₁)."
                )

        elif tipo_mkt.startswith("B."):
            ci1, ci2, ci3, ci4, ci5 = st.columns(5)
            a_in = ci1.number_input("Intercepto Oferta (a):", value=20.0, step=5.0, key="c5_ain")
            b_in = ci2.number_input("Pendiente Oferta (b):", value=0.05, step=0.01, format="%.3f", key="c5_bin")
            c_in = ci3.number_input("Intercepto Demanda (c):", value=200.0, step=10.0, key="c5_cin")
            d_in = ci4.number_input("Pendiente Demanda (d):", value=0.04, step=0.01, format="%.3f", key="c5_din")
            y_in = ci5.number_input("Insumo Demandado (Y_proy):", value=400.0, step=50.0, key="c5_yin")

            ri = resolver_mercado_insumo_clase2(a_in, b_in, c_in, d_in, y_in)
            ik1, ik2, ik3, ik4 = st.columns(4)
            ik1.metric("Sin Proyecto (Y0, P0)", f"Y0 = {_fmt_num(ri['y0'], 1)}", f"P0 = {_fmt_clp(ri['p0'], 2)}")
            ik2.metric("Con Proyecto (Y2, P1)", f"Y2 = {_fmt_num(ri['y2'], 1)}", f"P1 = {_fmt_clp(ri['p1'], 2)} | Y1 = {_fmt_num(ri['y1'], 1)}")
            ik3.metric("Costo Social (CS = DD + CP)", _fmt_clp(ri["cs_total"]), f"DD {_fmt_clp(ri['valor_dd'])} + CP {_fmt_clp(ri['valor_cp'])}")
            ik4.metric("Precio Social Insumo P*", f"{_fmt_clp(ri['p_social_ins'], 2)}/u", f"Costo Privado: {_fmt_clp(ri['costo_privado'])}")

            y_max_p = max(ri["y2"] * 1.25, 100.0)
            yg = np.linspace(0, y_max_p, 150)
            fig_in = go.Figure()
            fig_in.add_trace(go.Scatter(
                x=[ri["y1"], ri["y0"], ri["y0"], ri["y1"]],
                y=[0, 0, ri["p0"], ri["p1"]],
                fill="toself", fillcolor="rgba(2, 132, 199, 0.25)",
                line=dict(color="rgba(2, 132, 199, 0.7)", width=1),
                name=f"Disminución de Demanda DD ({_fmt_clp(ri['valor_dd'])})",
            ))
            fig_in.add_trace(go.Scatter(
                x=[ri["y0"], ri["y2"], ri["y2"], ri["y0"]],
                y=[0, 0, ri["p1"], ri["p0"]],
                fill="toself", fillcolor="rgba(185, 28, 28, 0.25)",
                line=dict(color="rgba(185, 28, 28, 0.7)", width=1),
                name=f"Costo de Producción CP ({_fmt_clp(ri['valor_cp'])})",
            ))
            fig_in.add_trace(go.Scatter(x=yg, y=np.maximum(0.0, a_in + b_in * yg), mode="lines", name="Oferta del Insumo (O)", line=dict(color="#262626", width=2.5)))
            fig_in.add_trace(go.Scatter(x=yg, y=np.maximum(0.0, c_in - d_in * yg), mode="lines", name="Demanda Sin Proyecto (D)", line=dict(color="#0F766E", width=2.5)))
            fig_in.add_trace(go.Scatter(x=yg, y=np.maximum(0.0, c_in - d_in * (yg - y_in)), mode="lines", name="Demanda Con Proyecto (D + Y)", line=dict(color="#B91C1C", width=2.2, dash="dash")))
            fig_in.update_layout(
                title="Mercado del Insumo: CS = DD (bajo demanda) + CP (bajo oferta) — Clase 2, Lámina 26",
                xaxis_title="Cantidad del Insumo (Y)",
                yaxis_title="Precio del Insumo ($)",
                yaxis_range=[0, max(c_in * 1.05, ri["p1"] * 1.25)],
                height=340,
                margin=dict(l=15, r=15, t=42, b=20),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#F8FAFC",
            )
            st.plotly_chart(fig_in, use_container_width=True)

            with st.expander("Ver paso a paso para copiar al cuaderno (Mercado del Insumo — Láminas 26–28)"):
                st.latex(r"CS = DD + CP = \frac{P_0 + P_1}{2}(Y_0 - Y_1) + \frac{P_0 + P_1}{2}(Y_2 - Y_0) \qquad | \qquad P^*_{\text{ins}} = \frac{CS}{Y_{\text{proy}}}")
                st.markdown(
                    f"1. **Equilibrio inicial:** {a_in:.1f} + {b_in:.3f}·Y₀ = {c_in:.1f} − {d_in:.3f}·Y₀ → **Y₀ = {_fmt_num(ri['y0'], 2)}**, **P₀ = {_clp_md(ri['p0'], 2)}**\n"
                    f"2. **Con demanda del proyecto (Y_proy = {y_in:.0f}):** el precio **sube** a **P₁ = {_clp_md(ri['p1'], 2)}**, la producción sube a **Y₂ = {_fmt_num(ri['y2'], 2)}** y otros usuarios bajan su consumo a **Y₁ = {_fmt_num(ri['y1'], 2)}**.\n"
                    f"3. **Disminución de Demanda (DD, bajo curva D):** {_clp_md(ri['p_social_ins'], 2)} × ({_fmt_num(ri['y0'], 2)} − {_fmt_num(ri['y1'], 2)}) = **{_clp_md(ri['valor_dd'])}**\n"
                    f"4. **Costo de Producción Adicional (CP, bajo curva O):** {_clp_md(ri['p_social_ins'], 2)} × ({_fmt_num(ri['y2'], 2)} − {_fmt_num(ri['y0'], 2)}) = **{_clp_md(ri['valor_cp'])}**\n"
                    f"5. **Costo Social Total:** CS = DD + CP = **{_clp_md(ri['cs_total'])}** vs. Costo Privado P₁·Y = **{_clp_md(ri['costo_privado'])}** → **P* insumo = {_clp_md(ri['p_social_ins'], 2)}**."
                )

        else:
            df_ext = pd.DataFrame([
                ["Mercado del Producto", "Demanda perfectamente elástica (horizontal)", "VSP = AD (todo se consume; precio no cae)", "P* = P0 (Precio Privado = Precio Social)", "Lámina 16"],
                ["Mercado del Producto", "Oferta perfectamente elástica (horizontal)", "VSP = LR (desplaza 100% a antiguos productores)", "P* = P0 (Precio Privado = Precio Social)", "Lámina 17"],
                ["Mercado del Producto", "Demanda perfectamente inelástica (vertical)", "VSP = LR (consumo fijo en X0; libera recursos)", "P* = (P0 + P1)/2 > P1", "Lámina 18"],
                ["Mercado del Producto", "Oferta perfectamente inelástica (vertical)", "VSP = AD (antiguos producen fijo X0; todo es consumo nuevo)", "P* = (P0 + P1)/2 > P1", "Lámina 19"],
                ["Mercado del Insumo", "Oferta del insumo perfectamente inelástica (vertical)", "CS = DD (no se puede producir más; todo se quita a otros usuarios)", "P* = (P0 + P1)/2 < P1", "Lámina 27"],
            ], columns=["Mercado", "Caso de Elasticidad Extrema", "Efecto Dominante", "Relación Precio Social (P*)", "Fuente Clase 2"])
            st.dataframe(df_ext, use_container_width=True, hide_index=True)

        # ----------------------------------------------------------------------
        # 5.2 CRUCE DE TASA DE FISHER (CLASE 1, LÁMINA 40)
        # ----------------------------------------------------------------------
        st.markdown("<div class='sub-header'>Ejercicio 5.2 — Cruce de Tasa de Fisher: Proyecto A vs. Proyecto B (Clase 1, lámina 40)</div>", unsafe_allow_html=True)
        st.caption(
            "Flujos exactos que replican la curva de la lámina 40 (`Clase1`): "
            "**Proyecto A:** `[-12.000, +1.000, +6.500, +10.000]` vs. **Proyecto B:** `[-12.000, +10.000, +4.500, +1.000]`."
        )

        r_fish_ui = st.slider("Elige tu tasa de descuento i (%) para decidir entre A y B:", 0.0, 22.0, 10.0, 0.5, key="c5_rfish") / 100.0
        fa_c1 = np.array([-12000.0, 1000.0, 6500.0, 10000.0])
        fb_c1 = np.array([-12000.0, 10000.0, 4500.0, 1000.0])
        fdiff_c1 = fa_c1 - fb_c1

        r_cruce = float(npf.irr(fdiff_c1))
        tir_a_c1 = float(npf.irr(fa_c1))
        tir_b_c1 = float(npf.irr(fb_c1))
        van_a_sel = float(npf.npv(r_fish_ui, fa_c1))
        van_b_sel = float(npf.npv(r_fish_ui, fb_c1))
        van_cruce = float(npf.npv(r_cruce, fa_c1))

        fk1, fk2, fk3, fk4 = st.columns(4)
        fk1.metric(f"VAN Proyecto A ({r_fish_ui*100:.1f}%)", _fmt_clp(van_a_sel), f"TIR A = {tir_a_c1*100:.2f}%")
        fk2.metric(f"VAN Proyecto B ({r_fish_ui*100:.1f}%)", _fmt_clp(van_b_sel), f"TIR B = {tir_b_c1*100:.2f}%")
        fk3.metric("Tasa de Fisher (Cruce)", f"{r_cruce*100:.2f}%".replace(".", ","), f"VAN igual = {_fmt_clp(van_cruce)}")
        ganador = "Proyecto A" if van_a_sel > van_b_sel and van_a_sel > 0 else ("Proyecto B" if van_b_sel > 0 else "Ninguno (VAN < 0)")
        fk4.metric("Decisión Óptima (Regla VAN)", ganador, "A tiene flujos más lejanos" if r_fish_ui < r_cruce else "B recupera más rápido")

        rg_f = np.linspace(0.0, 0.22, 111)
        fig_f = go.Figure()
        fig_f.add_trace(go.Scatter(x=rg_f * 100, y=[float(npf.npv(rv, fa_c1)) for rv in rg_f], mode="lines", name="Proyecto A (TIR 16,4%)", line=dict(color="#262626", width=2.6)))
        fig_f.add_trace(go.Scatter(x=rg_f * 100, y=[float(npf.npv(rv, fb_c1)) for rv in rg_f], mode="lines", name="Proyecto B (TIR 20,3%)", line=dict(color="#0F766E", width=2.6)))
        fig_f.add_trace(go.Scatter(
            x=[r_cruce * 100], y=[van_cruce], mode="markers+text",
            marker=dict(color="#B91C1C", size=10),
            text=[f"Cruce Fisher: {r_cruce*100:.1f}% ($1.272)"],
            textposition="top right", name="Tasa de Fisher",
        ))
        fig_f.add_vline(x=r_fish_ui * 100, line_color="#1E3A8A", line_dash="dot", annotation_text=f"Tu tasa {r_fish_ui*100:.1f}%")
        fig_f.add_hline(y=0, line_color="#94A3B8", line_dash="dash")
        fig_f.update_layout(
            title="Conflicto VAN vs. TIR en Proyectos Mutuamente Excluyentes (Clase 1, Lámina 40)",
            xaxis_title="Tasa de descuento i (%)",
            yaxis_title="VAN ($)",
            height=320,
            margin=dict(l=15, r=15, t=42, b=20),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#F8FAFC",
        )
        st.plotly_chart(fig_f, use_container_width=True)

        with st.expander("Ver paso a paso y tabla comparativa para copiar al cuaderno (Ejercicio 5.2 — Fisher)"):
            st.markdown(
                f"**¿Por qué ocurre el conflicto?** El Proyecto A entrega más dinero total (+\\$5.500 vs. +\\$3.500), pero concentrado en el Año 3 (+\\$10.000), "
                f"por lo que su curva VAN es más empinada y sensible a la tasa i.\n"
                f"- **Flujo incremental (A − B):** `[0, -9.000, +2.000, +9.000]` → **TIR(A − B) = {r_cruce*100:.2f}%** (Tasa de Fisher).\n"
                f"- **Regla práctica de examen:** Si i < 11,73% → elige **Proyecto A** (mayor VAN aunque tenga menor TIR); si 11,73% < i < 20,27% → elige **Proyecto B**; si i > 20,27% → rechaza ambos."
            )
            df_fish_t = pd.DataFrame([
                [f"{rv*100:.1f}%", _fmt_clp(npf.npv(rv, fa_c1)), _fmt_clp(npf.npv(rv, fb_c1)), "Proyecto A" if npf.npv(rv, fa_c1) > npf.npv(rv, fb_c1) else ("Proyecto B" if npf.npv(rv, fb_c1) > 0 else "Rechazar")]
                for rv in [0.0, 0.05, 0.10, r_cruce, 0.15, 0.1639, 0.2027]
            ], columns=["Tasa i (%)", "VAN Proyecto A", "VAN Proyecto B", "Mejor Decisión"])
            st.dataframe(df_fish_t, use_container_width=True, hide_index=True)

        # ----------------------------------------------------------------------
        # 5.3 PRÉSTAMO 1.000 UF (LÁMINAS 31-32) + GANANCIA DE CAPITAL (LÁMINA 22)
        # ----------------------------------------------------------------------
        st.markdown("<div class='sub-header'>Ejercicio 5.3 — Tabla de Crédito 1.000 UF (10 años, 10%) y Ganancia de Capital (Clase 1, láminas 22 y 31–32)</div>", unsafe_allow_html=True)
        col_cr, col_vc = st.columns(2)
        with col_cr:
            st.markdown("##### A. Crédito Francés en UF (Láminas 31–32)")
            cr1, cr2, cr3 = st.columns(3)
            p_uf = cr1.number_input("Préstamo P (UF):", value=1000.0, step=100.0, key="c5_puf")
            r_uf = cr2.number_input("Tasa anual r (%):", value=10.0, step=0.5, key="c5_ruf") / 100.0
            n_uf = cr3.number_input("Plazo n (años):", min_value=1, max_value=20, value=10, step=1, key="c5_nuf")

            cuota_uf, df_cred_uf = calcular_tabla_credito_frances_clase1(p_uf, r_uf, int(n_uf))
            tot_pagado = float(df_cred_uf.iloc[-1]["Cuota"])
            tot_intereses = float(df_cred_uf.iloc[-1]["Interés"])
            st.metric("Cuota Anual Fija (UF)", f"{_fmt_num(cuota_uf, 2)} UF/año", f"Total {int(n_uf)} cuotas: {_fmt_num(tot_pagado, 1)} UF")
            st.caption(
                f"Ojo con la lámina 31: el valor `1.627,5` escrito al final es el **total acumulado de las 10 cuotas** "
                f"(1.000 UF de capital + {_fmt_num(tot_intereses, 1)} UF de intereses); cada cuota anual es **{_fmt_num(cuota_uf, 2)} UF**."
            )

        with col_vc:
            st.markdown("##### B. Venta de Activo y Valor Libro (Lámina 22)")
            va1, va2 = st.columns(2)
            v_ini = va1.number_input("Valor inicial activo ($):", value=10000000, step=500000, key="c5_vini")
            v_ven = va2.number_input("Precio venta residual ($):", value=5500000, step=250000, key="c5_vven")
            va3, va4, va5 = st.columns(3)
            vu_leg = va3.number_input("Vida útil legal (años):", min_value=1, max_value=30, value=10, step=1, key="c5_vul")
            an_ven = va4.number_input("Año de venta:", min_value=1, max_value=30, value=6, step=1, key="c5_anv")
            t_cap = va5.number_input("Impuesto 1ra Cat (%):", value=25.0, step=1.0, key="c5_tcap") / 100.0

            rv_act = calcular_venta_activo_clase1(float(v_ini), int(vu_leg), int(an_ven), float(v_ven), t_cap)
            st.metric(
                "Flujo Neto de Caja por Venta",
                _fmt_clp(rv_act["flujo_neto_venta"]),
                f"Gan./Pérd. Capital: {_fmt_clp(rv_act['ganancia_cap'])} | Imp.: {_fmt_clp(rv_act['efecto_imp'])}",
            )
            st.caption(
                f"Depreciación acumulada ({int(an_ven)} años): **{_clp_md(rv_act['dep_acum'])}** → "
                f"Valor Libro: **{_clp_md(rv_act['valor_libro'])}**. El impuesto se aplica solo sobre (Venta − Valor Libro)."
            )

        with st.expander("Ver Tabla de Desarrollo del Crédito (10 años) y pasos de Venta de Activo para copiar al cuaderno"):
            st.latex(r"C = P \cdot \frac{r}{1 - (1+r)^{-n}} \qquad | \qquad \text{Flujo Neto Venta} = V_{\text{venta}} - (V_{\text{venta}} - V_{\text{libro}})\cdot t")
            st.markdown(
                f"- **Sustitución cuota:** C = {p_uf:.0f} × {r_uf:.3f} ÷ [1 − (1 + {r_uf:.3f})^(−{int(n_uf)})] = **{_fmt_num(cuota_uf, 2)} UF/año** "
                f"(Intereses van antes de impuestos en Flujo Operacional; Amortización va después de impuestos en Flujo de Capitales).\n"
                f"- **Sustitución venta activo:** Valor Libro = {_clp_md(v_ini)} − {_clp_md(rv_act['dep_acum'])} = **{_clp_md(rv_act['valor_libro'])}** → "
                f"Resultado venta = {_clp_md(v_ven)} − {_clp_md(rv_act['valor_libro'])} = **{_clp_md(rv_act['ganancia_cap'])}** → "
                f"**Flujo Neto Caja:** {_clp_md(v_ven)} + ({_clp_md(rv_act['efecto_imp'])}) = **{_clp_md(rv_act['flujo_neto_venta'])}**."
            )
            st.dataframe(df_cred_uf, use_container_width=True, hide_index=True)

        # ----------------------------------------------------------------------
        # 5.4 PIRÁMIDE LEY REP, POBLACIONES CLASE 3 Y LECTURA EN "Z" DE MML
        # ----------------------------------------------------------------------
        st.markdown("<div class='sub-header'>Ejercicio 5.4 — Pirámide Jerárquica Ley REP 20.920, Poblaciones (Clase 3) y Lógica en 'Z' del Marco Lógico</div>", unsafe_allow_html=True)
        cp1, cp2 = st.columns([1.05, 1.35])
        with cp1:
            fig_pir = go.Figure(go.Funnel(
                y=[
                    "1. Prevención (Máxima prioridad)",
                    "2. Reutilización (Sin proceso productivo)",
                    "3. Reciclaje (Residuo como insumo productivo)",
                    "4. Valorización Energética (Poder calorífico)",
                    "5. Eliminación (Relleno / Última opción)",
                ],
                x=[100, 80, 65, 45, 25],
                textinfo="label",
                marker={"color": ["#0F766E", "#15803D", "#1E3A8A", "#404040", "#991B1B"]},
            ))
            fig_pir.update_layout(
                title="Pirámide Jerárquica de Residuos (Ley 20.920 — Trabajo 1)",
                height=310,
                margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor="#F8FAFC",
            )
            st.plotly_chart(fig_pir, use_container_width=True)

        with cp2:
            st.markdown("##### Los 4 Casos de Población de `Clase3.pdf` (Lámina 8)")
            df_pob_c3 = pd.DataFrame([
                ["Instalación de APR", "Pob. total del AE", "Pob. carente del servicio", "50% de pob. carente"],
                ["Normalización escuela", "Pob. total del AE", "350 niños (6–13 años)", "200 niños 1er ciclo"],
                ["Centro de salud", "Pob. total del AE", "Pob. total del AE", "Pob. total del AE"],
                ["Maternidad étnica", "Pob. total del AE", "Mujeres 14–45 pert. étnica", "Mujeres 14–45 pert. étnica"],
            ], columns=["Proyecto", "Pob. Referencia", "Pob. Afectada", "Pob. Objetivo"])
            st.dataframe(df_pob_c3, use_container_width=True, hide_index=True)
            st.info(
                "**Lectura en 'Z' del Marco Lógico (`MARCO LOGICO.pdf`, láminas 11 y 21):** "
                "Si ejecutamos las **Actividades** y se cumplen sus condiciones → entregamos los **Componentes**; "
                "si entregamos los Componentes y se cumplen sus **Supuestos** → logramos el **Propósito** (único por programa); "
                "si logramos el Propósito y se cumplen sus **Supuestos** → contribuimos al **Fin**."
            )

        with st.expander("Pruébame en 30 segundos — Retos de Clases 1, 2 y 3"):
            _render_micro_reto(
                "c5_q1",
                "En el Flujo de Caja anual de evaluación de proyectos, los Pagos Provisionales Mensuales (PPM) reemplazan al Impuesto de Primera Categoría.",
                "Falso",
                "Según Clase 1 (lámina 20), los PPM afectan el Presupuesto de Caja mensual (corto plazo / capital de trabajo), mientras que el Impuesto a la Renta de 1ª Categoría va en el Flujo de Caja anual.",
                "Dra. Luz María Ferrada, Clase1 (18 ago).pdf, lámina 20",
            )
            st.divider()
            _render_micro_reto(
                "c5_q2",
                "En un proyecto que entra a demandar un insumo cuya oferta es perfectamente inelástica, el Costo Social del insumo equivale a la Disminución de Demanda (CS = DD) y el Precio Social P* es menor que el nuevo precio de mercado P1.",
                "Verdadero",
                "Con oferta fija (vertical), no hay mayor producción (CP = 0); el insumo se reasigna quitándoselo a otros demandantes, valorado bajo la curva de demanda a P* = (P0 + P1)/2 < P1.",
                "Dra. Luz María Ferrada, Clase2.pdf, lámina 27",
            )
