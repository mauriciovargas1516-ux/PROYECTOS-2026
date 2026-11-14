# -*- coding: utf-8 -*-
"""
EXTENSIÓN INTERACTIVA DE CÁTEDRA: EVALUACIÓN INTEGRADA DE PROYECTOS (FDIC26)
Universidad de Los Lagos — Carrera de Ingeniería Comercial
Asignatura: Evaluación Integrada de Proyectos (Prof. Luz María Ferrada)
Archivo: motor_catedra_proyectos_sni.py

Integra los 5 bloques oficiales del curso en UlagosVirtual:
1. Precios Sociales Vigentes 2026 (MDSF/SNI: TSD 5,5%, FCSMO, FCSD, Carbono, VST)
   y Cascada de Evaluación Privada (Puro/Financiado) a Evaluación Social + Capital de Trabajo.
2. Microeconomía del Bienestar de Ernesto Fontaine y resolución interactiva del
   Ejercicio del Mercado de la Leche (Clase 2: VSP = AD + LR y Enfoque de Agencia).
3. Evaluación Ambiental (RA2): Matriz de Leopold interactiva, Valor Económico Total (Barzev),
   Valoración Contingente, Costo de Viaje, Precios Hedónicos y Huella GEI (GIRS 20 años).
4. Formulación SNI 2025: Embudo Poblacional, Optimización de la Situación Base,
   Árbol de Problemas / Objetivos interactivo y Matriz de Marco Lógico (MML).
5. Entrenador Oficial Prueba RA1/RA2, Auditor de los 10 puntos de la Pauta y
   Exportador Excel (.xlsx) de 5 hojas con Fórmulas Vivas.
"""

import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# ==============================================================================
# 1. ESTILOS EJECUTIVOS Y COMPONENTE DE NOTAS METODOLÓGICAS (SIN EMOJIS)
# ==============================================================================
def inyectar_estilos_proyectos():
    st.markdown(
        """
        <style>
        div[data-testid="stPopover"] > button {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            color: #1e3a8a;
            border: 1px solid #93c5fd;
            border-left: 4px solid #2563eb;
            font-weight: 600;
            border-radius: 6px;
        }
        .badge-sni {
            display: inline-block;
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            color: #1e3a8a;
            border: 1px solid #93c5fd;
            border-radius: 18px;
            padding: 6px 14px;
            font-size: 0.86rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .card-ejecutiva {
            background-color: #ffffff;
            border-left: 4px solid #2563eb;
            border-top: 1px solid #e2e8f0;
            border-right: 1px solid #e2e8f0;
            border-bottom: 1px solid #e2e8f0;
            padding: 14px 16px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def renderizar_nota_metodologica(
    titulo_boton: str,
    titulo_interno: str,
    explicacion_md: str,
    formula_latex: str = None,
):
    """
    Despliega una nota metodológica interactiva libre de emojis con estilo técnico azul.
    """
    if hasattr(st, "popover"):
        contenedor = st.popover(f"Nota Metodológica: {titulo_boton}", use_container_width=True)
    else:
        contenedor = st.expander(f"Nota Metodológica: {titulo_boton}")

    with contenedor:
        st.markdown(f"#### {titulo_interno}")
        if formula_latex:
            st.latex(formula_latex)
        st.markdown(explicacion_md)


# ==============================================================================
# 2. CATÁLOGO OFICIAL DE PRECIOS SOCIALES VIGENTES 2026 (MDSF / SNI)
# ==============================================================================
PRECIOS_SOCIALES_2026 = {
    "TSD_anual": 0.055,
    "FCSMO_calificada": 0.97,
    "FCSMO_semicalificada": 0.95,
    "FCSMO_nocalificada": 0.91,
    "FCSD_divisa": 1.00,
    "FCSD_exacto": 1.003450,
    "IVA": 0.19,
    "arancel_ad_valorem": 0.0071,
    "UF_dic2025": 39727.96,
    "dolar_dic2025": 911.18,
    "VST_urbano_viaje": 3338,
    "VST_urbano_espera": 6676,
    "VST_urbano_caminata": 6676,
    "VST_deporte_recreacion": 2792,
    "VST_interurbano_terrestre": 10047,
    "VST_interurbano_aereo": 16983,
    "VST_carga_camion": 12954,
    "VVE_vida_estadistica": 2383677600,
    "comb_automovil": 760,
    "comb_camioneta": 787,
    "comb_camion_bus": 805,
    "mant_vehicular_hora": 6931,
    "carbono_clp_tco2": 71801,
    "factor_metano_ch4": 28,
    "factor_oxido_nitroso_n2o": 265,
    "elec_baja_tension_kwh": 124.8,
    "elec_alta_tension_kwh": 119.8,
}


def obtener_tabla_precios_sociales_2026() -> pd.DataFrame:
    filas = [
        ("Parámetros Nacionales", "Tasa Social de Descuento (TSD)", "% anual real", 5.5, "MDSF Reporte Anual 2026 (Tabla 1.1)"),
        ("Mano de Obra (CIUO-08 G1-G3)", "Factor Corrección MO Calificada (MOC)", "Factor", 0.97, "PSMO = Salario Bruto * 0,97"),
        ("Mano de Obra (CIUO-08 G4-G8)", "Factor Corrección MO Semi Calificada (MOSC)", "Factor", 0.95, "Incluye choferes con licencia profesional"),
        ("Mano de Obra (CIUO-08 G9)", "Factor Corrección MO No Calificada (MONC)", "Factor", 0.91, "Ocupaciones elementales"),
        ("Sector Externo", "Factor Corrección Social de la Divisa (FCSD)", "Factor", 1.00, "Valor exacto 6 dec: 1,003450"),
        ("Valor Social del Tiempo", "Viaje Urbano en Vehículo", "CLP / h-pax", 3338, "Ponderador = 1,0"),
        ("Valor Social del Tiempo", "Espera y Caminata Urbana (TP Mayor)", "CLP / h-pax", 6676, "Ponderador = 2,0 * VST Viaje"),
        ("Valor Social del Tiempo", "Viajes Deporte y Recreación (VTO)", "CLP / h-pax", 2792, "39,08% del Salario Bruto por Hora"),
        ("Valor Social del Tiempo", "Viaje Interurbano Terrestre / Aéreo", "CLP / h-pax", 10047, "Aéreo = 16.983 CLP/h-pax"),
        ("Valor Social del Tiempo", "Transporte de Carga (Camión)", "CLP / h-veh", 12954, "Único para urbano e interurbano"),
        ("Seguridad Vial", "Valor de una Vida Estadística (VVE)", "CLP", 2383677600, "Equivalente a 60.000 UF"),
        ("Operación Vehicular", "Combustible Automóvil / Camioneta / Camión", "CLP / litro", 805, "Auto: 760 | Camioneta: 787 | Camión: 805"),
        ("Operación Vehicular", "Mantenimiento Vehicular (Mano de Obra)", "CLP / hora", 6931, "Salario Bruto Mant. * FCSMO_CAL (0,97)"),
        ("Ambientales y Energía", "Precio Social del Carbono (CO2eq)", "CLP / t CO2eq", 71801, "78,8 USD/t CO2eq (Ruta NDC 2020-2050)"),
        ("Ambientales y Energía", "Factor Conversión Metano (CH4 a CO2eq)", "t CO2eq / t CH4", 28, "Potencial Calentamiento Global IPCC 100 años"),
        ("Ambientales y Energía", "Factor Conversión Óxido Nitroso (N2O a CO2eq)", "t CO2eq / t N2O", 265, "Potencial Calentamiento Global IPCC 100 años"),
        ("Ambientales y Energía", "Precio Social Electricidad Baja Tensión", "CLP / kWh", 124.8, "Alta Tensión = 119,8 CLP/kWh"),
    ]
    return pd.DataFrame(
        filas,
        columns=["Categoría SNI", "Parámetro / Precio Social", "Unidad", "Valor Oficial 2026", "Regla de Aplicación en Cátedra"],
    )


# ==============================================================================
# 3. MOTOR DE EVALUACIÓN PRIVADA, FINANCIADA Y SOCIAL (CASCADA SNI)
# ==============================================================================
def simular_evaluacion_integrada(
    horizonte: int,
    capex_total: float,
    pct_transable_capex: float,
    vida_util_contable: int,
    valor_residual_pct: float,
    toneladas_anuales_base: float,
    crecimiento_anual_demanda: float,
    precio_venta_ton_neto: float,
    costo_var_insumos_ton: float,
    gasto_mo_calificada_anual: float,
    gasto_mo_semicalificada_anual: float,
    gasto_mo_nocalificada_anual: float,
    gasto_energia_kwh_anual: float,
    tarifa_privada_kwh: float,
    litros_diesel_anual: float,
    precio_mercado_diesel: float,
    ton_co2_evitadas_anual: float,
    ton_ch4_evitadas_anual: float,
    ahorro_relleno_ton: float,
    tasa_impuesto_1ra_cat: float,
    wacc_privado: float,
    pct_deuda: float,
    tasa_deuda: float,
    plazo_deuda: int,
    dias_desfase_ct: int,
):
    """
    Construye simultáneamente:
    1. Flujo de Caja Privado Puro (Clase 1, láminas 23-24).
    2. Flujo de Caja Privado Financiado con Tabla de Amortización Francesa (Clase 1, láminas 29-32).
    3. Flujo Social SNI 2026 (Metodología General 2025 + Precios Sociales 2026 + GIRS).
    4. Descomposición en Cascada (Waterfall) de VAN Privado a VAN Social.
    5. Indicadores VAN, TIR, VAC, CAE y CAE por tonelada.
    """
    p = PRECIOS_SOCIALES_2026
    tsd = p["TSD_anual"]
    anios = list(range(0, horizonte + 1))

    # Estimación de Capital de Trabajo por Método de Período de Desfase
    costo_operacional_anual_1 = (
        toneladas_anuales_base * costo_var_insumos_ton
        + gasto_mo_calificada_anual
        + gasto_mo_semicalificada_anual
        + gasto_mo_nocalificada_anual
        + gasto_energia_kwh_anual * tarifa_privada_kwh
        + litros_diesel_anual * precio_mercado_diesel
    )
    cap_trabajo_priv = (costo_operacional_anual_1 / 365.0) * dias_desfase_ct

    # Corrección social de la Inversión Inicial (CAPEX)
    # Parte transable se limpia de IVA y arancel y se multiplica por FCSD; parte nacional se limpia de IVA
    capex_transable = capex_total * (pct_transable_capex / 100.0)
    capex_nacional = capex_total - capex_transable
    capex_social = (
        (capex_transable / (1.0 + p["arancel_ad_valorem"])) * p["FCSD_exacto"]
        + capex_nacional
    )
    cap_trabajo_soc = cap_trabajo_priv * 0.94

    # Tabla de desarrollo del crédito (Amortización Francesa — Clase 1 pág. 31-32)
    monto_prestamo = (capex_total + cap_trabajo_priv) * (pct_deuda / 100.0)
    intereses_deuda = np.zeros(horizonte + 1)
    amortizaciones_deuda = np.zeros(horizonte + 1)
    saldos_deuda = np.zeros(horizonte + 1)
    saldos_deuda[0] = monto_prestamo

    if monto_prestamo > 0 and plazo_deuda > 0 and tasa_deuda > 0:
        n_cred = min(plazo_deuda, horizonte)
        cuota_fija = monto_prestamo * (tasa_deuda / (1.0 - (1.0 + tasa_deuda) ** (-n_cred)))
        saldo = monto_prestamo
        for t in range(1, n_cred + 1):
            int_t = saldo * tasa_deuda
            amort_t = cuota_fija - int_t
            saldo = max(0.0, saldo - amort_t)
            intereses_deuda[t] = int_t
            amortizaciones_deuda[t] = amort_t
            saldos_deuda[t] = saldo

    # Vectores de flujos anuales
    f_priv_puro = np.zeros(horizonte + 1)
    f_priv_fin = np.zeros(horizonte + 1)
    f_social = np.zeros(horizonte + 1)
    costos_sociales_vec = np.zeros(horizonte + 1)
    toneladas_vec = np.zeros(horizonte + 1)

    f_priv_puro[0] = -(capex_total + cap_trabajo_priv)
    f_priv_fin[0] = -(capex_total + cap_trabajo_priv) + monto_prestamo
    f_social[0] = -(capex_social + cap_trabajo_soc)
    costos_sociales_vec[0] = capex_social + cap_trabajo_soc

    dep_anual = capex_total / max(vida_util_contable, 1)
    vr_privado = capex_total * (valor_residual_pct / 100.0)
    vr_social = capex_social * (valor_residual_pct / 100.0)

    filas_flujo = []
    for t in range(1, horizonte + 1):
        q_t = toneladas_anuales_base * ((1.0 + crecimiento_anual_demanda) ** (t - 1))
        toneladas_vec[t] = q_t

        ing_priv = q_t * precio_venta_ton_neto
        c_insumos_priv = q_t * costo_var_insumos_ton
        c_mo_priv = (
            gasto_mo_calificada_anual
            + gasto_mo_semicalificada_anual
            + gasto_mo_nocalificada_anual
        )
        c_energia_priv = gasto_energia_kwh_anual * tarifa_privada_kwh
        c_diesel_priv = litros_diesel_anual * precio_mercado_diesel
        dep_t = dep_anual if t <= vida_util_contable else 0.0

        # Utilidad Antes de Impuestos (Flujo Puro)
        uai_puro = ing_priv - c_insumos_priv - c_mo_priv - c_energia_priv - c_diesel_priv - dep_t
        imp_puro = max(0.0, uai_puro * tasa_impuesto_1ra_cat)
        udi_puro = uai_puro - imp_puro
        fco_puro = udi_puro + dep_t

        recup_final_priv = (vr_privado + cap_trabajo_priv) if t == horizonte else 0.0
        f_priv_puro[t] = fco_puro + recup_final_priv

        # Utilidad Antes de Impuestos (Flujo Financiado)
        uai_fin = uai_puro - intereses_deuda[t]
        imp_fin = max(0.0, uai_fin * tasa_impuesto_1ra_cat)
        udi_fin = uai_fin - imp_fin
        fco_fin = udi_fin + dep_t
        f_priv_fin[t] = fco_fin + recup_final_priv - amortizaciones_deuda[t]

        # Flujo Social SNI 2026
        # Costos corregidos por factores sociales 2026
        c_mo_soc = (
            gasto_mo_calificada_anual * p["FCSMO_calificada"]
            + gasto_mo_semicalificada_anual * p["FCSMO_semicalificada"]
            + gasto_mo_nocalificada_anual * p["FCSMO_nocalificada"]
        )
        c_energia_soc = gasto_energia_kwh_anual * p["elec_baja_tension_kwh"]
        c_diesel_soc = litros_diesel_anual * p["comb_camion_bus"]
        c_insumos_soc = c_insumos_priv * p["FCSD_divisa"]

        # Beneficios sociales directos + externalidades ambientales valorizadas (GIRS / Carbono 2026)
        co2_total_eq = ton_co2_evitadas_anual + (ton_ch4_evitadas_anual * p["factor_metano_ch4"])
        benef_carbono_soc = co2_total_eq * p["carbono_clp_tco2"]
        benef_ahorro_relleno = q_t * ahorro_relleno_ton
        benef_social_total = ing_priv + benef_carbono_soc + benef_ahorro_relleno

        costo_social_op_t = c_insumos_soc + c_mo_soc + c_energia_soc + c_diesel_soc
        recup_final_soc = (vr_social + cap_trabajo_soc) if t == horizonte else 0.0

        f_social[t] = benef_social_total - costo_social_op_t + recup_final_soc
        costos_sociales_vec[t] = costo_social_op_t - recup_final_soc

        filas_flujo.append({
            "Año": t,
            "Toneladas_Valorizadas": round(q_t, 1),
            "Ingresos_Privados": round(ing_priv, 0),
            "Costos_Op_Privados": round(c_insumos_priv + c_mo_priv + c_energia_priv + c_diesel_priv, 0),
            "Impuesto_1ra_Cat": round(imp_puro, 0),
            "Flujo_Privado_Puro": round(f_priv_puro[t], 0),
            "Flujo_Privado_Financiado": round(f_priv_fin[t], 0),
            "Beneficio_Carbono_y_GIRS": round(benef_carbono_soc + benef_ahorro_relleno, 0),
            "Costos_Op_Sociales": round(costo_social_op_t, 0),
            "Flujo_Social_SNI": round(f_social[t], 0),
        })

    # Funciones financieras auxiliares
    def _van(tasa, flujos):
        return float(sum(flujos[t] / ((1.0 + tasa) ** t) for t in range(len(flujos))))

    def _tir(flujos):
        # Búsqueda numérica robusta de TIR entre -50% y +300%
        tasas = np.linspace(-0.45, 3.0, 4000)
        vans = [sum(flujos[t] / ((1.0 + r) ** t) for t in range(len(flujos))) for r in tasas]
        for i in range(len(vans) - 1):
            if vans[i] * vans[i + 1] <= 0:
                return float(tasas[i] + (tasas[i + 1] - tasas[i]) * abs(vans[i]) / (abs(vans[i]) + abs(vans[i + 1]) + 1e-12))
        return np.nan

    van_priv_puro = _van(wacc_privado, f_priv_puro)
    van_priv_fin = _van(wacc_privado, f_priv_fin)
    van_social = _van(tsd, f_social)

    tir_priv_puro = _tir(f_priv_puro)
    tir_social = _tir(f_social)

    # VAC y CAE (Metodología General 2025 / GIRS)
    vac_social = _van(tsd, costos_sociales_vec)
    factor_frc = (tsd * ((1.0 + tsd) ** horizonte)) / (((1.0 + tsd) ** horizonte) - 1.0)
    cae_social = vac_social * factor_frc
    va_toneladas = sum(toneladas_vec[t] / ((1.0 + tsd) ** t) for t in range(1, horizonte + 1))
    cae_por_tonelada = vac_social / max(va_toneladas, 1.0)

    # Descomposición para Gráfico de Cascada (Privado Puro @ WACC -> Social @ TSD)
    van_priv_a_tsd = _van(tsd, f_priv_puro)
    efecto_tasa_descuento = van_priv_a_tsd - van_priv_puro

    # Efecto eliminación de impuestos directos y corrección CAPEX
    f_sin_impuestos = f_priv_puro.copy()
    for idx_t, fila in enumerate(filas_flujo, start=1):
        f_sin_impuestos[idx_t] += fila["Impuesto_1ra_Cat"]
    efecto_impuestos = _van(tsd, f_sin_impuestos) - van_priv_a_tsd

    # Efecto corrección social de Mano de Obra, Energía y Combustibles
    ahorro_mo_anual = (
        gasto_mo_calificada_anual * (1.0 - p["FCSMO_calificada"])
        + gasto_mo_semicalificada_anual * (1.0 - p["FCSMO_semicalificada"])
        + gasto_mo_nocalificada_anual * (1.0 - p["FCSMO_nocalificada"])
    )
    ahorro_energ_comb_anual = (
        gasto_energia_kwh_anual * (tarifa_privada_kwh - p["elec_baja_tension_kwh"])
        + litros_diesel_anual * (precio_mercado_diesel - p["comb_camion_bus"])
    )
    factor_anualidad_tsd = (1.0 - (1.0 + tsd) ** (-horizonte)) / tsd
    efecto_precios_cuenta = (ahorro_mo_anual + ahorro_energ_comb_anual) * factor_anualidad_tsd + (
        (capex_total + cap_trabajo_priv) - (capex_social + cap_trabajo_soc)
    )

    # Efecto beneficios ambientales (Carbono + Ahorro Relleno Sanitario)
    efecto_ambiental_social = van_social - (van_priv_a_tsd + efecto_impuestos + efecto_precios_cuenta)

    resumen = {
        "van_priv_puro": van_priv_puro,
        "van_priv_fin": van_priv_fin,
        "van_social": van_social,
        "tir_priv_puro": tir_priv_puro,
        "tir_social": tir_social,
        "vac_social": vac_social,
        "cae_social": cae_social,
        "cae_por_tonelada": cae_por_tonelada,
        "cap_trabajo_priv": cap_trabajo_priv,
        "capex_social": capex_social,
        "efecto_tasa_descuento": efecto_tasa_descuento,
        "efecto_impuestos": efecto_impuestos,
        "efecto_precios_cuenta": efecto_precios_cuenta,
        "efecto_ambiental_social": efecto_ambiental_social,
        "flujo_priv_puro": f_priv_puro,
        "flujo_priv_fin": f_priv_fin,
        "flujo_social": f_social,
        "df_flujos": pd.DataFrame(filas_flujo),
    }
    return resumen


# ==============================================================================
# 4. MOTOR MICROECONÓMICO DE FONTAINE (CLASE 2: EJERCICIO MERCADO DE LA LECHE)
# ==============================================================================
def resolver_mercado_fontaine_clase2(
    a_oferta: float = 50.0,
    b_oferta: float = 0.025,
    c_demanda: float = 300.0,
    d_demanda: float = 0.0205,
    q_proyecto_total: float = 1470.0,
    fraccion_avance: float = 1.0,
):
    """
    Resuelve exactamente el Ejercicio de la Cooperativa Lechera de la Prof. Luz María Ferrada
    (Clase2.pdf, láminas 20 a 25):
      Oferta Nacional Sin Proyecto: P_o = a_oferta + b_oferta * Q_o
      Demanda Nacional:             P_d = c_demanda - d_demanda * Q_d
      Proyecto introduce:           q_eff = q_proyecto_total * fraccion_avance
    Calcula:
      - Equilibrio inicial (Q0, P0)
      - Equilibrio con proyecto (P1, Qd1, Qo1)
      - Aumento en Disponibilidad (AD) y Liberación de Recursos (LR)
      - Valor Social de la Producción (VSP = AD + LR) y Precio Social Unitario
      - Distribución por Agencia: Inversionista (VPP), Excedente Consumidor (dEC) y Productor (dEP).
    """
    q_proy = q_proyecto_total * fraccion_avance

    # a) Equilibrio sin proyecto: a + b*Q0 = c - d*Q0
    q0 = (c_demanda - a_oferta) / (b_oferta + d_demanda)
    p0 = a_oferta + b_oferta * q0

    # b) Equilibrio con proyecto: Qd1 = Qo1 + q_proy
    # P1 = a + b*Qo1 = c - d*(Qo1 + q_proy)
    qo1 = (c_demanda - a_oferta - d_demanda * q_proy) / (b_oferta + d_demanda)
    qo1 = max(0.0, qo1)
    qd1 = qo1 + q_proy
    p1 = c_demanda - d_demanda * qd1

    # Variaciones físicas
    aumento_disp_q = qd1 - q0       # Delta Qd (mayor consumo nacional)
    liberacion_rec_q = q0 - qo1     # Delta Qo (menor producción de antiguos productores)

    # c) Enfoque de Eficiencia: VSP = AD + LR
    p_medio = 0.5 * (p0 + p1)
    valor_ad = p_medio * aumento_disp_q
    valor_lr = p_medio * liberacion_rec_q
    vsp_eficiencia = valor_ad + valor_lr
    precio_social_unitario = p_medio

    # d) Enfoque de Agencia (Clase 2, láminas 15 y 24)
    ingresos_firma_vpp = p1 * q_proy
    delta_excedente_consumidor = (p0 - p1) * q0 + 0.5 * (p0 - p1) * aumento_disp_q
    delta_excedente_productor = -((p0 - p1) * qo1 + 0.5 * (p0 - p1) * liberacion_rec_q)
    vsp_agencia = ingresos_firma_vpp + delta_excedente_consumidor + delta_excedente_productor

    return {
        "q0": q0,
        "p0": p0,
        "qo1": qo1,
        "qd1": qd1,
        "p1": p1,
        "q_proy": q_proy,
        "aumento_disp_q": aumento_disp_q,
        "liberacion_rec_q": liberacion_rec_q,
        "valor_ad": valor_ad,
        "valor_lr": valor_lr,
        "vsp_eficiencia": vsp_eficiencia,
        "precio_social_unitario": precio_social_unitario,
        "ingresos_firma_vpp": ingresos_firma_vpp,
        "delta_ec": delta_excedente_consumidor,
        "delta_ep": delta_excedente_productor,
        "vsp_agencia": vsp_agencia,
    }


def construir_grafico_fontaine_interactivo(
    a_oferta: float,
    b_oferta: float,
    c_demanda: float,
    d_demanda: float,
    q_proyecto_total: float,
    fraccion_avance: float,
):
    res = resolver_mercado_fontaine_clase2(
        a_oferta, b_oferta, c_demanda, d_demanda, q_proyecto_total, fraccion_avance
    )
    q_max_eje = max(res["qd1"] * 1.25, 8500.0)
    q_grid = np.linspace(0, q_max_eje, 200)

    p_oferta_sin = a_oferta + b_oferta * q_grid
    p_demanda = np.maximum(0.0, c_demanda - d_demanda * q_grid)
    p_oferta_con = a_oferta + b_oferta * np.maximum(0.0, q_grid - res["q_proy"])

    fig = go.Figure()

    # Área sombreada LR (Liberación de Recursos: entre Qo1 y Q0 bajo la curva de oferta)
    if res["q_proy"] > 0:
        fig.add_trace(
            go.Scatter(
                x=[res["qo1"], res["q0"], res["q0"], res["qo1"]],
                y=[0, 0, res["p0"], res["p1"]],
                fill="toself",
                fillcolor="rgba(37, 99, 235, 0.25)",
                line=dict(color="rgba(37, 99, 235, 0.6)", width=1),
                name=f"Liberación de Recursos (LR = ${res['valor_lr']:,.0f})",
            )
        )
        # Área sombreada AD (Aumento en Disponibilidad: entre Q0 y Qd1 bajo la curva de demanda)
        fig.add_trace(
            go.Scatter(
                x=[res["q0"], res["qd1"], res["qd1"], res["q0"]],
                y=[0, 0, res["p1"], res["p0"]],
                fill="toself",
                fillcolor="rgba(5, 150, 105, 0.25)",
                line=dict(color="rgba(5, 150, 105, 0.6)", width=1),
                name=f"Aumento en Disponibilidad (AD = ${res['valor_ad']:,.0f})",
            )
        )

    # Curvas principales
    fig.add_trace(
        go.Scatter(
            x=q_grid,
            y=p_demanda,
            mode="lines",
            line=dict(color="#0f172a", width=3),
            name="Demanda Nacional Pd(Q)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=q_grid,
            y=p_oferta_sin,
            mode="lines",
            line=dict(color="#2563eb", width=3),
            name="Oferta Sin Proyecto Po(Q)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=q_grid,
            y=p_oferta_con,
            mode="lines",
            line=dict(color="#dc2626", width=3, dash="dash"),
            name=f"Oferta Con Proyecto (Q + {res['q_proy']:,.0f})",
        )
    )

    # Puntos de equilibrio E0, E1 y producción antigua Qo1
    fig.add_trace(
        go.Scatter(
            x=[res["q0"], res["qd1"], res["qo1"]],
            y=[res["p0"], res["p1"], res["p1"]],
            mode="markers+text",
            text=[
                f"<b>E0 (Q0={res['q0']:,.0f}, P0=${res['p0']:.1f})</b>",
                f"<b>E1 (Qd1={res['qd1']:,.0f}, P1=${res['p1']:.1f})</b>",
                f"<b>Qo1={res['qo1']:,.0f}</b>",
            ],
            textposition=["top center", "top right", "bottom left"],
            marker=dict(size=11, color=["#1e3a8a", "#dc2626", "#d97706"]),
            name="Equilibrios de Mercado",
        )
    )

    fig.update_layout(
        title=(
            f"Equilibrio de Mercado de Fontaine (Clase 2): "
            f"VSP = AD (${res['valor_ad']:,.0f}) + LR (${res['valor_lr']:,.0f}) = ${res['vsp_eficiencia']:,.0f} | "
            f"Precio Social = ${res['precio_social_unitario']:.2f}/ton"
        ),
        xaxis_title="Cantidad Q (Toneladas / año)",
        yaxis_title="Precio P ($ / Tonelada)",
        xaxis=dict(range=[0, q_max_eje]),
        yaxis=dict(range=[0, max(c_demanda * 1.1, 330)]),
        height=490,
        plot_bgcolor="#f8fafc",
        legend=dict(orientation="h", y=-0.22),
    )
    return fig


# ==============================================================================
# 5. GENERADOR DE ÁRBOL DE PROBLEMAS / OBJETIVOS INTERACTIVO (PLOTLY)
# ==============================================================================
CASOS_ARBOLES_CATEDRA = {
    "1. Caso Oficial Clase: Centro de Apoyo a Productores de Berries (Ejercicio Árbol PDF)": {
        "problema_central": "Deficiente gestión en organización y logística\npara la comercialización externa de berries",
        "objetivo_central": "Eficiente gestión en organización y logística\npara la comercialización externa de berries",
        "causas_n1": [
            "Ausencia de procesos de\nasociatividad y cooperación",
            "Baja capacidad instalada y\nproducción con bajo valor agregado",
            "Ineficiente cadena de distribución\ny desconocimiento de exportación",
        ],
        "causas_n2": [
            "Desconocimiento de potencialidades\nde asociatividad y falta de asesoría",
            "Insuficientes estrategias grupales\ny condiciones fitosanitarias",
            "Desconocimiento de TLC y de\nrutas logísticas internacionales",
        ],
        "efectos_n1": [
            "No hay iniciativas de exportación\nni se cubren estándares externos",
            "Bajo nivel competitivo de\nlos pequeños productores",
            "Escasa participación en el\nmercado internacional",
        ],
        "efectos_n2": [
            "No se aprovechan los beneficios\nde los Tratados de Libre Comercio",
            "Pocas posibilidades de ampliar\ningresos de las familias",
            "Bajo aporte al desarrollo\neconómico de la comuna",
        ],
        "medios_n1": [
            "Presencia de asociatividad\ndirigida a cooperación sectorial",
            "Incremento de capacidad instalada\ny producción con valor agregado",
            "Formación de cadenas de distribución\ny dominio logístico exportador",
        ],
        "medios_n2": [
            "Talleres, giras tecnológicas y\nasesoría de seguimiento en curso",
            "Generación de estrategias grupales\ny cumplimiento de estándares",
            "Capacitación en TLC y en rutas\nde distribución logística",
        ],
        "fines_n1": [
            "Presencia de iniciativas de\nexportación estandarizadas",
            "Mejora sustantiva del nivel\ncompetitivo local",
            "Mejora la participación en el\nmercado internacional",
        ],
        "fines_n2": [
            "Se aprovechan los beneficios\nde los Tratados de Libre Comercio",
            "Se amplían las posibilidades\nde ingresos de los productores",
            "Creciente aporte al desarrollo\neconómico de la comuna",
        ],
        "alternativa_seleccionada": (
            "Construcción y habilitación de un Centro de Apoyo a la Producción y Comercialización de Berries "
            "para mercados externos, que ejecute capacitaciones en TLC/logística, talleres, giras tecnológicas, "
            "seguimiento técnico y constitución de una cooperativa de pequeños productores."
        ),
    },
    "2. Caso Proyecto Curso: Valorización de Residuos Cartón Vivo Osorno (Trabajo 1 / GIRS)": {
        "problema_central": "Baja valorización de residuos de cartón comercial\ne inadecuada disposición en vertedero Curaco (Osorno)",
        "objetivo_central": "Alta valorización circular de residuos de cartón comercial\ny reducción de disposición en vertedero Curaco (Osorno)",
        "causas_n1": [
            "Recolección municipal mixta\nsin segregación en origen comercial",
            "Inexistencia de planta local de\ntransformación con valor agregado",
            "Baja articulación entre comercio\ngenerador y demanda educativa",
        ],
        "causas_n2": [
            "Carencia de ruta logística\ndiferenciada en eje E. Ramírez",
            "Falta de equipamiento de prensado,\ntriturado y moldeo celulósico",
            "Desconocimiento de incentivos Ley REP\nN° 20.920 y educación circular",
        ],
        "efectos_n1": [
            "Saturación acelerada de vida útil\ndel sitio de disposición en Curaco",
            "Aumento de emisiones GEI (CH4 y CO2)\ny costos municipales de transporte",
            "Pérdida de materia prima secundaria\npara mobiliario y material didáctico",
        ],
        "efectos_n2": [
            "Deterioro de calidad ambiental\ny riesgo sanitario comunal",
            "Mayor carga presupuestaria municipal\nen gestión de RSDyA",
            "Desaprovechamiento de economía\ncircular escolar (DAEM / Jardines)",
        ],
        "medios_n1": [
            "Sistema de recolección selectiva\nen comercios del eje céntrico",
            "Planta operativa de valorización y\nsecado/prensado de cartón",
            "Convenios activos con comercio\nlocal y demandantes institucionales",
        ],
        "medios_n2": [
            "Ruta logística programada con\ncontenedores diferenciados (NCh 3322)",
            "Adquisición de prensa hidráulica,\npulper y matrices de moldeo",
            "Programa de sensibilización ambiental\nbajo jerarquía Ley N° 20.920",
        ],
        "fines_n1": [
            "Extensión de la vida útil del\nrelleno sanitario de Osorno",
            "Mitigación de emisiones GEI valorizadas\na Precio Social del Carbono",
            "Provisión local de productos reciclados\npara establecimientos educacionales",
        ],
        "fines_n2": [
            "Mejora de la calidad ambiental\ny cumplimiento del PROT / PLADECO",
            "Ahorro neto de costos municipales\nde transporte y disposición final",
            "Fortalecimiento de la economía\ncircular en la Región de Los Lagos",
        ],
        "alternativa_seleccionada": (
            "Implementación de Planta de Valorización de Cartón Comercial (Cartón Vivo Osorno) con ruta de "
            "recolección selectiva en eje Eleuterio Ramírez y línea de transformación en mobiliario/material "
            "didáctico para DAEM Osorno, jardines infantiles e instituciones locales."
        ),
    },
    "3. Caso Oficial Clase: Programa de Nutrición del Adulto Mayor (MARCO LOGICO.pdf)": {
        "problema_central": "Altos niveles de malnutrición en adultos\nmayores vulnerables de la comuna",
        "objetivo_central": "Mejora de los niveles de nutrición de los\nadultos mayores vulnerables de la comuna",
        "causas_n1": [
            "Alteración del metabolismo y\nenfermedades degenerativas",
            "Inadecuada dieta alimentaria\nen el hogar",
            "Aumento de la soledad y pérdida\nde espacios sociales",
        ],
        "causas_n2": [
            "Alta incidencia de patologías\ncrónicas no controladas",
            "Bajos niveles de ingreso y\nhábitos alimenticios inadecuados",
            "Carencia de redes de apoyo\ny acompañamiento comunitario",
        ],
        "efectos_n1": [
            "Mayor incidencia de enfermedades\ny hospitalizaciones",
            "Disminución del bienestar anímico\ny pérdida de espacio social",
            "Disminución de la capacidad de\nautovalencia funcional",
        ],
        "efectos_n2": [
            "Sobrecarga de la red asistencial\nde salud primaria",
            "Aislamiento severo del\nadulto mayor",
            "Ancianos con calidad de vida\nseveramente deteriorada",
        ],
        "medios_n1": [
            "Regulación del metabolismo y\ncontrol de patologías de base",
            "Adecuada dieta alimentaria con\nsuplemento enriquecido",
            "Disminución de la soledad y\nrecuperación de espacios sociales",
        ],
        "medios_n2": [
            "Baja incidencia de complicaciones\npor enfermedades degenerativas",
            "Entrega de suplemento alimenticio\ny capacitación en hábitos sanos",
            "Conservación de espacios sociales\ny convenios con consultorios",
        ],
        "fines_n1": [
            "Menor incidencia de enfermedades\nasociadas a desnutrición",
            "Mejora en el bienestar anímico\ny participación comunitaria",
            "Recuperación de la capacidad\nde autovalencia",
        ],
        "fines_n2": [
            "Descongestión de consultas de\nmorbilidad en CESFAM",
            "Integración activa del adulto\nmayor en la sociedad",
            "Adultos mayores con calidad de\nvida integralmente mejorada (FIN)",
        ],
        "alternativa_seleccionada": (
            "Programa de Nutrición del Adulto Mayor con 2 Componentes: (1) Entrega de suplemento alimenticio "
            "enriquecido mediante convenios con consultorios municipales y (2) Capacitación nutricional."
        ),
    },
    "4. Caso Prueba Proceso 2 RA1: Transporte de Trabajadores y Ausentismo (Proceso2 RA1.pdf)": {
        "problema_central": "Aumento del ausentismo y atrasos laborales\nen la planta industrial",
        "objetivo_central": "Reducción del ausentismo y atrasos laborales\nen la planta industrial (Propósito)",
        "causas_n1": [
            "No hay servicios de transporte\nconfiables para los trabajadores",
            "Altos tiempos de espera y trasbordo\nen transporte público rural/urbano",
            "Fatiga por largos desplazamientos\nen horarios de entrada de turnos",
        ],
        "causas_n2": [
            "Inexistencia de buses de acercamiento\ncontratados por la empresa",
            "Baja frecuencia de recorridos\nen sectores periféricos",
            "Desconexión horaria entre turnos\nde planta y locomoción colectiva",
        ],
        "efectos_n1": [
            "Pérdida de horas-hombre efectivas\nen las líneas de producción",
            "Interrupciones operativas e\nincumplimiento de metas diarias",
            "Sobrecosto por horas extraordinarias\nde reemplazo de personal",
        ],
        "efectos_n2": [
            "Baja productividad laboral general\nde la fábrica (Efecto Final)",
            "Pérdida de competitividad y\natrasos en entregas a clientes",
            "Deterioro del clima organizacional\ny rotación de operarios",
        ],
        "medios_n1": [
            "Contratación de servicios de transporte\npara trabajadores de la fábrica",
            "Rutas de acercamiento optimizadas\ncon paraderos definidos",
            "Sincronización puntual con los\nhorarios de ingreso y salida de turno",
        ],
        "medios_n2": [
            "Licitación y contrato de flota de\nbuses de acercamiento (Componente)",
            "Cobertura completa de los sectores\nresidenciales del personal",
            "Monitoreo mensual de puntualidad\ny frecuencia del servicio",
        ],
        "fines_n1": [
            "Aumento de los días y horas\nefectivamente trabajadas por mes",
            "Continuidad operacional en todas\nlas líneas de la planta",
            "Reducción de costos por reemplazos\ny horas extras de emergencia",
        ],
        "fines_n2": [
            "Alta productividad laboral en la\nfábrica (Objetivo FIN)",
            "Cumplimiento oportuno de pedidos\ny estándares de calidad",
            "Mejora en bienestar y retención\nde los trabajadores(as)",
        ],
        "alternativa_seleccionada": (
            "Contratación y gestión de un servicio dedicado de transporte de acercamiento para los(as) "
            "trabajadores(as) de la fábrica, monitoreado por indicadores de eficacia, eficiencia y calidad."
        ),
    },
}


def construir_figura_arbol_catedra(caso_dict: dict, modo_positivo: bool = False):
    """
    Construye el diagrama de Árbol de Problemas (modo_positivo=False) o
    Árbol de Objetivos / Medios y Fines (modo_positivo=True) con sus 5 niveles jerárquicos.
    """
    if not modo_positivo:
        titulo_central = f"<b>PROBLEMA CENTRAL:</b><br>{caso_dict['problema_central']}"
        n1_abajo = caso_dict["causas_n1"]
        n2_abajo = caso_dict["causas_n2"]
        n1_arriba = caso_dict["efectos_n1"]
        n2_arriba = caso_dict["efectos_n2"]
        etq_arriba2 = "EFECTOS INDIRECTOS (2° NIVEL)"
        etq_arriba1 = "EFECTOS DIRECTOS (1° NIVEL)"
        etq_abajo1 = "CAUSAS DIRECTAS (1° NIVEL)"
        etq_abajo2 = "CAUSAS DE BASE / RAÍCES (2° NIVEL)"
        color_central = "#dc2626"
        color_arriba = "#d97706"
        color_abajo = "#1e3a8a"
        titulo_graf = "Árbol de Problemas (Negativo Fotográfico: Causas -> Problema Central -> Efectos)"
    else:
        titulo_central = f"<b>PROPÓSITO / OBJETIVO CENTRAL:</b><br>{caso_dict['objetivo_central']}"
        n1_abajo = caso_dict["medios_n1"]
        n2_abajo = caso_dict["medios_n2"]
        n1_arriba = caso_dict["fines_n1"]
        n2_arriba = caso_dict["fines_n2"]
        etq_arriba2 = "FINES ÚLTIMOS / IMPACTO (2° NIVEL)"
        etq_arriba1 = "FINES DIRECTOS (1° NIVEL)"
        etq_abajo1 = "MEDIOS DIRECTOS / COMPONENTES (1° NIVEL)"
        etq_abajo2 = "ACCIONES / MEDIOS OPERATIVOS (2° NIVEL)"
        color_central = "#059669"
        color_arriba = "#0284c7"
        color_abajo = "#2563eb"
        titulo_graf = "Árbol de Objetivos: Medios y Fines (Positivo Fotográfico: Acciones -> Medios -> Propósito -> Fines)"

    xs_cols = [-1.0, 0.0, 1.0]
    fig = go.Figure()

    # Líneas conectoras causales (de abajo hacia arriba)
    line_x, line_y = [], []
    for i, x_pos in enumerate(xs_cols):
        # Raíz nivel 2 -> Causa/Medio nivel 1
        line_x.extend([x_pos, x_pos, None])
        line_y.extend([-2.0, -1.0, None])
        # Causa/Medio nivel 1 -> Problema/Objetivo Central
        line_x.extend([x_pos, 0.0, None])
        line_y.extend([-1.0, 0.0, None])
        # Problema/Objetivo Central -> Efecto/Fin nivel 1
        line_x.extend([0.0, x_pos, None])
        line_y.extend([0.0, 1.0, None])
        # Efecto/Fin nivel 1 -> Efecto/Fin nivel 2
        line_x.extend([x_pos, x_pos, None])
        line_y.extend([1.0, 2.0, None])

    fig.add_trace(
        go.Scatter(
            x=line_x,
            y=line_y,
            mode="lines",
            line=dict(color="#64748b", width=2.5),
            hoverinfo="none",
            showlegend=False,
        )
    )

    # Cajas de nodos mediante anotaciones estilizadas de Plotly
    nodos_info = [(0.0, 0.0, titulo_central, color_central, "#ffffff")]
    for i, x_pos in enumerate(xs_cols):
        nodos_info.append((x_pos, 2.0, n2_arriba[i], color_arriba, "#ffffff"))
        nodos_info.append((x_pos, 1.0, n1_arriba[i], color_arriba, "#ffffff"))
        nodos_info.append((x_pos, -1.0, n1_abajo[i], color_abajo, "#ffffff"))
        nodos_info.append((x_pos, -2.0, n2_abajo[i], "#334155", "#ffffff"))

    annotations = []
    for x_n, y_n, texto_n, bg_col, font_col in nodos_info:
        annotations.append(
            dict(
                x=x_n,
                y=y_n,
                xref="x",
                yref="y",
                text=texto_n.replace("\n", "<br>"),
                showarrow=False,
                font=dict(size=11, color=font_col, family="Arial"),
                align="center",
                bgcolor=bg_col,
                bordercolor="#0f172a",
                borderwidth=1.5,
                borderpad=7,
            )
        )

    # Etiquetas laterales de nivel
    niveles_y = [
        (2.0, etq_arriba2),
        (1.0, etq_arriba1),
        (0.0, "TRONCO CENTRAL"),
        (-1.0, etq_abajo1),
        (-2.0, etq_abajo2),
    ]
    for y_niv, txt_niv in niveles_y:
        annotations.append(
            dict(
                x=-1.68,
                y=y_niv,
                xref="x",
                yref="y",
                text=f"<b>{txt_niv}</b>",
                showarrow=False,
                font=dict(size=10, color="#1e293b"),
                align="left",
                bgcolor="#e2e8f0",
                borderpad=4,
            )
        )

    fig.update_layout(
        title=titulo_graf,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-2.15, 1.55]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-2.55, 2.55]),
        annotations=annotations,
        height=560,
        margin=dict(l=15, r=15, t=50, b=15),
        plot_bgcolor="#f8fafc",
    )
    return fig


# ==============================================================================
# 6. EXPORTADOR EXCEL DE 5 HOJAS CON FÓRMULAS VIVAS (OPENPYXL)
# ==============================================================================
def exportar_excel_proyectos_sni_formulas(
    res_eval: dict,
    res_leche: dict,
    df_leopold: pd.DataFrame,
    parametros_sim: dict,
) -> bytes:
    """
    Genera un libro Excel (.xlsx) con 5 hojas y fórmulas nativas de Excel (=NPV, =IRR, =SUM, =IF):
    1. Precios_Sociales_2026
    2. Flujo_Privado_y_Social
    3. Mercado_Fontaine_Clase2
    4. Matriz_Leopold_y_GEI
    5. Capital_Trabajo_y_CAE
    """
    wb = Workbook()

    fill_azul = PatternFill("solid", fgColor="1E3A8A")
    fill_verde = PatternFill("solid", fgColor="065F46")
    fill_input = PatternFill("solid", fgColor="FEF9C3")
    fill_calc = PatternFill("solid", fgColor="EFF6FF")
    font_h = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_b = Font(name="Calibri", size=10, bold=True)
    borde = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    # ------------------------------------------------------------------
    # HOJA 1: PRECIOS SOCIALES VIGENTES 2026 (MDSF / SNI)
    # ------------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "1_Precios_Sociales_2026"
    ws1["A1"] = "REPORTE OFICIAL DE PRECIOS SOCIALES VIGENTES 2026 — SUBSECRETARÍA DE EVALUACIÓN SOCIAL (MDSF / SNI)"
    ws1["A1"].font = Font(size=12, bold=True, color="1E3A8A")

    df_ps = obtener_tabla_precios_sociales_2026()
    for c_idx, col_name in enumerate(df_ps.columns, start=1):
        c = ws1.cell(row=3, column=c_idx, value=col_name)
        c.fill = fill_azul
        c.font = font_h
        c.border = borde

    for r_idx, row_vals in enumerate(df_ps.itertuples(index=False), start=4):
        for c_idx, val in enumerate(row_vals, start=1):
            c = ws1.cell(row=r_idx, column=c_idx, value=val)
            c.border = borde
            if c_idx == 4:
                c.fill = fill_input
                c.font = font_b

    for col_l, ancho in [("A", 28), ("B", 44), ("C", 18), ("D", 18), ("E", 42)]:
        ws1.column_dimensions[col_l].width = ancho

    # ------------------------------------------------------------------
    # HOJA 2: FLUJO DE CAJA PRIVADO Y SOCIAL CON FÓRMULAS VIVAS
    # ------------------------------------------------------------------
    ws2 = wb.create_sheet("2_Flujo_Privado_y_Social")
    ws2["A1"] = "FLUJO DE CAJA PRIVADO Y EVALUACIÓN SOCIAL SNI 2026 (CON FÓRMULAS NATIVAS DE EXCEL)"
    ws2["A1"].font = Font(size=12, bold=True, color="1E3A8A")

    ws2["A3"] = "WACC Privado Anual"
    ws2["B3"] = parametros_sim["wacc_privado"]
    ws2["B3"].number_format = "0.0%"
    ws2["B3"].fill = fill_input

    ws2["C3"] = "Tasa Social Descuento (TSD 2026)"
    ws2["D3"] = PRECIOS_SOCIALES_2026["TSD_anual"]
    ws2["D3"].number_format = "0.0%"
    ws2["D3"].fill = fill_input

    headers_f = [
        "Período (Año)",
        "Ingresos Privados ($)",
        "Costos Op. Privados ($)",
        "Impuesto 1ra Cat. ($)",
        "Inversión y Recup. Privada ($)",
        "Flujo Caja Privado Puro ($)",
        "Beneficio Carbono y Ahorro GIRS ($)",
        "Costos Op. Sociales Corregidos ($)",
        "Inversión y Recup. Social ($)",
        "Flujo Caja Social SNI ($)",
    ]
    for c_i, h_t in enumerate(headers_f, start=1):
        c = ws2.cell(row=5, column=c_i, value=h_t)
        c.fill = fill_azul
        c.font = font_h
        c.border = borde

    # Año 0
    ws2.cell(row=6, column=1, value=0).border = borde
    for col_zero in [2, 3, 4, 7, 8]:
        ws2.cell(row=6, column=col_zero, value=0).border = borde
    ws2.cell(row=6, column=5, value=float(res_eval["flujo_priv_puro"][0])).fill = fill_input
    ws2.cell(row=6, column=6, value="=B6-C6-D6+E6").fill = fill_calc
    ws2.cell(row=6, column=9, value=float(res_eval["flujo_social"][0])).fill = fill_input
    ws2.cell(row=6, column=10, value="=B6+G6-H6+I6").fill = fill_calc

    df_fl = res_eval["df_flujos"]
    n_h = len(df_fl)
    for idx_r, row_f in df_fl.iterrows():
        r_ex = 7 + idx_r
        es_ultimo = (idx_r == n_h - 1)
        rec_priv = float(row_f["Flujo_Privado_Puro"] - (row_f["Ingresos_Privados"] - row_f["Costos_Op_Privados"] - row_f["Impuesto_1ra_Cat"])) if es_ultimo else 0.0
        rec_soc = float(row_f["Flujo_Social_SNI"] - (row_f["Ingresos_Privados"] + row_f["Beneficio_Carbono_y_GIRS"] - row_f["Costos_Op_Sociales"])) if es_ultimo else 0.0

        ws2.cell(row=r_ex, column=1, value=int(row_f["Año"])).border = borde
        ws2.cell(row=r_ex, column=2, value=float(row_f["Ingresos_Privados"])).fill = fill_input
        ws2.cell(row=r_ex, column=3, value=float(row_f["Costos_Op_Privados"])).fill = fill_input
        ws2.cell(row=r_ex, column=4, value=float(row_f["Impuesto_1ra_Cat"])).fill = fill_input
        ws2.cell(row=r_ex, column=5, value=rec_priv).fill = fill_input
        ws2.cell(row=r_ex, column=6, value=f"=B{r_ex}-C{r_ex}-D{r_ex}+E{r_ex}").fill = fill_calc
        ws2.cell(row=r_ex, column=7, value=float(row_f["Beneficio_Carbono_y_GIRS"])).fill = fill_input
        ws2.cell(row=r_ex, column=8, value=float(row_f["Costos_Op_Sociales"])).fill = fill_input
        ws2.cell(row=r_ex, column=9, value=rec_soc).fill = fill_input
        ws2.cell(row=r_ex, column=10, value=f"=B{r_ex}+G{r_ex}-H{r_ex}+I{r_ex}").fill = fill_calc

        for col_k in range(2, 11):
            celda_k = ws2.cell(row=r_ex, column=col_k)
            celda_k.number_format = "#,##0"
            celda_k.border = borde

    fila_fin_fl = 6 + n_h
    f_kpi = fila_fin_fl + 2
    kpis_excel = [
        ("VAN Privado Puro (=NPV + Inversión 0)", f"=F6+NPV(B3,F7:F{fila_fin_fl})", "#,##0"),
        ("TIR Privada Pura (=IRR)", f"=IRR(F6:F{fila_fin_fl})", "0.00%"),
        ("VAN Social SNI 2026 (=NPV a TSD 5,5% + Inv. 0)", f"=J6+NPV(D3,J7:J{fila_fin_fl})", "#,##0"),
        ("TIR Social SNI (=IRR)", f"=IRR(J6:J{fila_fin_fl})", "0.00%"),
        ("Decisión de Recomendación Favorable (RS)", f'=IF(B{f_kpi+2}>=0,"RECOMENDADO FAVORABLEMENTE (RS)","RECHAZADO (VAN SOCIAL < 0)")', "@"),
    ]
    for off, (nom_k, form_k, fmt_k) in enumerate(kpis_excel):
        rk = f_kpi + off
        c1 = ws2.cell(row=rk, column=1, value=nom_k)
        c1.font = font_b
        c1.border = borde
        c2 = ws2.cell(row=rk, column=2, value=form_k)
        c2.fill = fill_calc
        c2.font = font_b
        c2.number_format = fmt_k
        c2.border = borde

    for col_i in range(1, 11):
        ws2.column_dimensions[get_column_letter(col_i)].width = 24
    ws2.column_dimensions["A"].width = 38

    # ------------------------------------------------------------------
    # HOJA 3: MERCADO DE FONTAINE — EJERCICIO CLASE 2 (LECHE EN POLVO)
    # ------------------------------------------------------------------
    ws3 = wb.create_sheet("3_Mercado_Fontaine_Leche")
    ws3["A1"] = "RESOLUCIÓN CON FÓRMULAS VIVAS: EJERCICIO COOPERATIVA LECHERA (CLASE 2 — PROF. LUZ MARÍA FERRADA)"
    ws3["A1"].font = Font(size=12, bold=True, color="065F46")

    filas_leche = [
        ("Intercepto Oferta (a)", 50.0, "0.00", True),
        ("Pendiente Oferta (b)", 0.025, "0.0000", True),
        ("Intercepto Demanda (c)", 300.0, "0.00", True),
        ("Pendiente Demanda (d)", 0.0205, "0.0000", True),
        ("Producción del Proyecto (Q_proy ton/año)", 1470.0, "#,##0.0", True),
        ("a) Cantidad Equilibrio Sin Proyecto (Q0)", "=(B5-B3)/(B4+B6)", "#,##0.00", False),
        ("a) Precio Equilibrio Sin Proyecto (P0)", "=B3+B4*B8", "#,##0.00", False),
        ("b) Oferta Antiguos Productores Con Proyecto (Qo1)", "=(B5-B3-B6*B7)/(B4+B6)", "#,##0.00", False),
        ("b) Consumo Nacional Con Proyecto (Qd1 = Qo1 + Q_proy)", "=B10+B7", "#,##0.00", False),
        ("b) Nuevo Precio Equilibrio Con Proyecto (P1)", "=B5-B6*B11", "#,##0.00", False),
        ("b) Ingresos Privados de la Cooperativa (VPP = P1 * Q_proy)", "=B12*B7", "#,##0", False),
        ("c) Aumento en Disponibilidad (AD)", "=0.5*(B9+B12)*(B11-B8)", "#,##0", False),
        ("c) Liberación de Recursos (LR)", "=0.5*(B9+B12)*(B8-B10)", "#,##0", False),
        ("c) Valor Social de la Producción (VSP = AD + LR)", "=B14+B15", "#,##0", False),
        ("d) Variación Excedente del Consumidor (Delta EC)", "=(B9-B12)*B8+0.5*(B9-B12)*(B11-B8)", "#,##0", False),
        ("d) Variación Excedente Productores Antiguos (Delta EP)", "=-((B9-B12)*B10+0.5*(B9-B12)*(B8-B10))", "#,##0", False),
        ("d) Verificación por Agencia (VPP + Delta EC + Delta EP)", "=B13+B17+B18", "#,##0", False),
        ("e) Precio Social Unitario de la Leche ($/ton)", "=B16/B7", "#,##0.00", False),
    ]
    for idx_l, (etq_l, val_l, fmt_l, es_in) in enumerate(filas_leche, start=3):
        c1 = ws3.cell(row=idx_l, column=1, value=etq_l)
        c1.font = font_b
        c1.border = borde
        c2 = ws3.cell(row=idx_l, column=2, value=val_l)
        c2.fill = fill_input if es_in else fill_calc
        c2.font = font_b
        c2.number_format = fmt_l
        c2.border = borde

    ws3.column_dimensions["A"].width = 54
    ws3.column_dimensions["B"].width = 22

    # ------------------------------------------------------------------
    # HOJA 4: MATRIZ DE LEOPOLD Y VALORIZACIÓN AMBIENTAL (RA2)
    # ------------------------------------------------------------------
    ws4 = wb.create_sheet("4_Matriz_Leopold_y_GEI")
    ws4["A1"] = "MATRIZ DE IMPACTO AMBIENTAL DE LEOPOLD (RA2) — FÓRMULA = MAGNITUD * IMPORTANCIA"
    ws4["A1"].font = Font(size=12, bold=True, color="065F46")

    headers_leo = ["Factor Ambiental", "Componente", "Magnitud (-10 a +10)", "Importancia (1 a 10)", "Puntaje Ponderado (M * I)"]
    for c_i, h_t in enumerate(headers_leo, start=1):
        c = ws4.cell(row=3, column=c_i, value=h_t)
        c.fill = fill_verde
        c.font = font_h
        c.border = borde

    for idx_m, row_m in df_leopold.iterrows():
        rm = 4 + idx_m
        ws4.cell(row=rm, column=1, value=row_m["Medio"]).border = borde
        ws4.cell(row=rm, column=2, value=row_m["Factor_Ambiental"]).border = borde
        c_mag = ws4.cell(row=rm, column=3, value=int(row_m["Magnitud_M"]))
        c_mag.fill = fill_input
        c_mag.border = borde
        c_imp = ws4.cell(row=rm, column=4, value=int(row_m["Importancia_I"]))
        c_imp.fill = fill_input
        c_imp.border = borde
        c_pon = ws4.cell(row=rm, column=5, value=f"=C{rm}*D{rm}")
        c_pon.fill = fill_calc
        c_pon.font = font_b
        c_pon.border = borde

    r_tot_leo = 4 + len(df_leopold)
    ws4.cell(row=r_tot_leo, column=4, value="Impacto Ambiental Neto Total:").font = font_b
    c_sum_leo = ws4.cell(row=r_tot_leo, column=5, value=f"=SUM(E4:E{r_tot_leo-1})")
    c_sum_leo.fill = fill_calc
    c_sum_leo.font = font_b
    c_sum_leo.border = borde

    for col_l in ["A", "B", "C", "D", "E"]:
        ws4.column_dimensions[col_l].width = 28

    # ------------------------------------------------------------------
    # HOJA 5: CAPITAL DE TRABAJO Y COSTO ANUAL EQUIVALENTE (CAE)
    # ------------------------------------------------------------------
    ws5 = wb.create_sheet("5_Capital_Trabajo_y_CAE")
    ws5["A1"] = "COMPARADOR DE ALTERNATIVAS COSTO-EFICIENCIA (VAC Y CAE — PROCESO 2 RA1)"
    ws5["A1"].font = Font(size=12, bold=True, color="1E3A8A")

    headers_cae = ["Alternativa Tecnológica", "Inversión Inicial ($)", "Costo Operación Anual ($)", "Vida Útil (Años)", "TSD 2026", "VAC Social ($)", "CAE Social Anual ($)"]
    for c_i, h_t in enumerate(headers_cae, start=1):
        c = ws5.cell(row=3, column=c_i, value=h_t)
        c.fill = fill_azul
        c.font = font_h
        c.border = borde

    alts_ej = [
        ("Alternativa A: Planta Semi-Automatizada", 85000000, 24000000, 10, 0.055),
        ("Alternativa B: Planta Compacta Modular", 62000000, 29500000, 7, 0.055),
    ]
    for idx_a, (nom_a, inv_a, cop_a, vu_a, tsd_a) in enumerate(alts_ej, start=4):
        ws5.cell(row=idx_a, column=1, value=nom_a).border = borde
        ws5.cell(row=idx_a, column=2, value=inv_a).fill = fill_input
        ws5.cell(row=idx_a, column=3, value=cop_a).fill = fill_input
        ws5.cell(row=idx_a, column=4, value=vu_a).fill = fill_input
        c_t = ws5.cell(row=idx_a, column=5, value=tsd_a)
        c_t.fill = fill_input
        c_t.number_format = "0.0%"
        c_vac = ws5.cell(row=idx_a, column=6, value=f"=B{idx_a}+PV(E{idx_a},D{idx_a},-C{idx_a})")
        c_vac.fill = fill_calc
        c_vac.number_format = "#,##0"
        c_cae = ws5.cell(row=idx_a, column=7, value=f"=-PMT(E{idx_a},D{idx_a},F{idx_a})")
        c_cae.fill = fill_calc
        c_cae.font = font_b
        c_cae.number_format = "#,##0"
        for col_k in range(2, 8):
            ws5.cell(row=idx_a, column=col_k).border = borde
            if col_k in [2, 3]:
                ws5.cell(row=idx_a, column=col_k).number_format = "#,##0"

    for col_i in range(1, 8):
        ws5.column_dimensions[get_column_letter(col_i)].width = 25

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ==============================================================================
# 7. INTERFAZ PRINCIPAL DE LA EXTENSIÓN EN STREAMLIT
# ==============================================================================
def renderizar_extension_proyectos_sni():
    inyectar_estilos_proyectos()

    st.header("Evaluación Integrada de Proyectos (FDIC26): Simulador SNI 2026, Fontaine, Ambiental y Marco Lógico")
    st.markdown(
        '<span class="badge-sni">Guía Metodológica Activa: Despliega las notas técnicas para consultar las fórmulas oficiales de cátedra y la interpretación de cada indicador</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Módulo integral sincronizado con los documentos de cátedra de la **Prof. Luz María Ferrada** en `ulagosvirtual.cl`: "
        "**Precios Sociales 2026 (MDSF)**, **Metodología General SNI 2025**, **Microeconomía de Ernesto Fontaine (`Clase 2`)**, "
        "**Guía de Valoración Ambiental de Barzev (`RA2`)**, **Metodología GIRS (Ley REP N° 20.920)** y **Marco Lógico (ILPES/CEPAL)**."
    )

    tabs = st.tabs([
        "1. Precios Sociales 2026 y Cascada Privado a Social",
        "2. Microeconomía de Fontaine y Ejercicio Leche (Clase 2)",
        "3. Evaluación Ambiental (RA2): Leopold, Valoración y GIRS",
        "4. Formulación SNI 2025: Población, Árboles y Marco Lógico",
        "5. Examen Proceso 2 RA1, Pauta 10 Puntos y Excel Vivo",
    ])

    # Valores por defecto para la exportación Excel transversal
    df_leopold_default = pd.DataFrame([
        {"Medio": "Físico", "Factor_Ambiental": "Calidad del Aire y Gases (GEI / CO2eq)", "Magnitud_M": 8, "Importancia_I": 9},
        {"Medio": "Físico", "Factor_Ambiental": "Carga sobre Suelo / Relleno Sanitario Curaco", "Magnitud_M": 9, "Importancia_I": 10},
        {"Medio": "Físico", "Factor_Ambiental": "Olores Molestos y Ruido en Planta (NCh 3190)", "Magnitud_M": -2, "Importancia_I": 4},
        {"Medio": "Biótico", "Factor_Ambiental": "Conservación de Recursos Forestales / Árboles", "Magnitud_M": 7, "Importancia_I": 8},
        {"Medio": "Socioeconómico", "Factor_Ambiental": "Empleo Local y Encadenamiento Productivo", "Magnitud_M": 7, "Importancia_I": 8},
        {"Medio": "Socioeconómico", "Factor_Ambiental": "Educación Ambiental y Economía Circular Escolar", "Magnitud_M": 9, "Importancia_I": 9},
    ])

    # ==========================================================================
    # PESTAÑA 1: PRECIOS SOCIALES 2026 Y PUENTE PRIVADO -> SOCIAL
    # ==========================================================================
    with tabs[0]:
        st.subheader("Simulador Integrado: De Flujo de Caja Privado (Puro/Financiado) a Evaluación Social SNI 2026")

        with st.expander("Consultar Catálogo Oficial de Precios Sociales Vigentes 2026 (`Precios-Sociales-2026.pdf` — 31 de marzo de 2026)", expanded=False):
            st.dataframe(obtener_tabla_precios_sociales_2026(), use_container_width=True, hide_index=True)

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            caso_proy = st.selectbox(
                "Plantilla de Proyecto:",
                [
                    "1. Valorización de Cartón Comercial (Cartón Vivo Osorno)",
                    "2. Planta de Compostaje Municipal Orgánico (GIRS)",
                    "3. Centro de Apoyo y Comercialización de Berries",
                ],
            )
            horizonte = st.slider("Horizonte de evaluación (años):", 5, 20, 10 if "2." not in caso_proy else 20)
            capex_total = st.number_input("Inversión Inicial CAPEX ($):", min_value=5000000, value=68000000, step=2000000)
            pct_transable_capex = st.slider("% CAPEX Equipos Importados (Transables):", 0, 100, 40)

        with col_p2:
            toneladas_base = st.number_input("Volumen Procesado Año 1 (ton/año):", min_value=50.0, value=480.0, step=20.0)
            crec_demanda = st.slider("Crecimiento anual de volumen (%):", 0.0, 15.0, 4.0, 0.5) / 100.0
            precio_venta_ton = st.number_input("Ingreso Privado por Tonelada ($/ton):", min_value=10000, value=210000, step=10000)
            costo_insumos_ton = st.number_input("Costo Insumos por Tonelada ($/ton):", min_value=5000, value=45000, step=5000)

        with col_p3:
            gasto_moc = st.number_input("Sueldo Anual MO Calificada (MOC 0,97) ($):", min_value=0, value=16800000, step=1000000)
            gasto_mosc = st.number_input("Sueldo Anual MO Semi Calificada (MOSC 0,95) ($):", min_value=0, value=21600000, step=1000000)
            gasto_monc = st.number_input("Sueldo Anual MO No Calificada (MONC 0,91) ($):", min_value=0, value=14400000, step=1000000)
            dias_desfase = st.slider("Días de desfase Capital de Trabajo:", 15, 90, 45)

        with col_p4:
            wacc_priv = st.slider("Tasa de Descuento Privada WACC (%):", 5.0, 20.0, 11.5, 0.5) / 100.0
            pct_deuda = st.slider("% Financiamiento con Deuda Bancaria:", 0, 80, 40, 5)
            ton_co2_evit = st.number_input("Emisiones Directas CO2 Evitadas (t/año):", min_value=0.0, value=120.0, step=10.0)
            ton_ch4_evit = st.number_input("Metano Evitado en Vertedero CH4 (t/año, Factor x28):", min_value=0.0, value=8.5, step=0.5)

        res_eval = simular_evaluacion_integrada(
            horizonte=horizonte,
            capex_total=float(capex_total),
            pct_transable_capex=float(pct_transable_capex),
            vida_util_contable=10,
            valor_residual_pct=20.0,
            toneladas_anuales_base=float(toneladas_base),
            crecimiento_anual_demanda=float(crec_demanda),
            precio_venta_ton_neto=float(precio_venta_ton),
            costo_var_insumos_ton=float(costo_insumos_ton),
            gasto_mo_calificada_anual=float(gasto_moc),
            gasto_mo_semicalificada_anual=float(gasto_mosc),
            gasto_mo_nocalificada_anual=float(gasto_monc),
            gasto_energia_kwh_anual=28000.0,
            tarifa_privada_kwh=165.0,
            litros_diesel_anual=4200.0,
            precio_mercado_diesel=1060.0,
            ton_co2_evitadas_anual=float(ton_co2_evit),
            ton_ch4_evitadas_anual=float(ton_ch4_evit),
            ahorro_relleno_ton=28500.0,
            tasa_impuesto_1ra_cat=0.25,
            wacc_privado=wacc_priv,
            pct_deuda=float(pct_deuda),
            tasa_deuda=0.085,
            plazo_deuda=min(5, horizonte),
            dias_desfase_ct=dias_desfase,
        )

        # Fila de KPIs con sus Notas Metodológicas
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric(
                f"1. VAN Privado Puro ({wacc_priv*100:.1f}%)",
                f"${res_eval['van_priv_puro']:,.0f}",
                f"TIR Privada: {res_eval['tir_priv_puro']*100:.1f}%" if np.isfinite(res_eval["tir_priv_puro"]) else "TIR N/A",
            )
            renderizar_nota_metodologica(
                titulo_boton="Flujo Puro vs. Financiado",
                titulo_interno="Flujo de Caja Privado Puro y Financiado (`Clase1 (18 ago).pdf`)",
                formula_latex=r"VAN_{Priv} = -I_0 + \sum_{t=1}^{n} \frac{FCO_t + FK_t}{(1 + r_{priv})^t}",
                explicacion_md=(
                    "- **Flujo Puro:** Mide la rentabilidad de los activos del proyecto asumiendo $100\\%$ capital propio.\n"
                    f"- **Flujo Financiado ({pct_deuda}% deuda):** Incorpora el préstamo en $t=0$, deduce los intereses antes de impuesto (escudo fiscal) y descuenta la amortización después de impuesto. Tu **VAN Financiado actual es `${res_eval['van_priv_fin']:,.0f}`**."
                ),
            )

        with k2:
            st.metric(
                "2. VAN Social SNI (TSD = 5,5%)",
                f"${res_eval['van_social']:,.0f}",
                f"TIR Social: {res_eval['tir_social']*100:.1f}%" if np.isfinite(res_eval["tir_social"]) else "RS Favorable",
            )
            renderizar_nota_metodologica(
                titulo_boton="Fórmula VANS y TSD 5,5%",
                titulo_interno="Valor Actual Neto Social (`Clase2.pdf` pág. 11 y `Precios-Sociales-2026.pdf`)",
                formula_latex=r"VANS = -I_{0,soc} + \sum_{t=1}^{n} \frac{BSN_t}{(1 + TSD)^t} \quad ; \quad TSD_{2026} = 5,5\%",
                explicacion_md=(
                    "- **TSD Oficial 2026 (5,5%):** Representa el costo de oportunidad social del capital ($\beta \cdot t_p + \phi \cdot q + \alpha \cdot CMg_x$).\n"
                    "- **Correcciones aplicadas:** Se eliminan impuestos directos (transferencias), se corrige la mano de obra por **0,97 / 0,95 / 0,91**, el diésel a **805 CLP/l**, la electricidad a **124,8 CLP/kWh** y se suma el carbono evitado a **71.801 CLP/t CO2eq**."
                ),
            )

        with k3:
            st.metric(
                "3. VAC y CAE Social (5,5%)",
                f"CAE: ${res_eval['cae_social']:,.0f}/año",
                f"VAC: ${res_eval['vac_social']:,.0f}",
            )
            renderizar_nota_metodologica(
                titulo_boton="¿Cuándo usar VAN, VAC o CAE?",
                titulo_interno="Regla de Decisión de Cátedra (`Proceso2 RA1.pdf`, Pregunta II.1)",
                formula_latex=r"CAE = VAC \cdot \left[\frac{TSD(1+TSD)^n}{(1+TSD)^n - 1}\right]",
                explicacion_md=(
                    "- **VAN:** Cuando se pueden medir y valorar los beneficios y costos y las alternativas tienen igual vida útil.\n"
                    "- **VAC (Valor Actual de Costos):** Cuando los beneficios son difíciles de medir o son idénticos entre alternativas y tienen **igual horizonte de evaluación**.\n"
                    "- **CAE (Costo Anual Equivalente):** Cuando los beneficios son idénticos/difíciles de medir y las alternativas tienen **distintos años de vida útil**."
                ),
            )

        with k4:
            st.metric(
                "4. CAE por Tonelada y Cap. Trabajo",
                f"${res_eval['cae_por_tonelada']:,.0f} / ton",
                f"Cap. Trabajo: ${res_eval['cap_trabajo_priv']:,.0f}",
            )
            renderizar_nota_metodologica(
                titulo_boton="Criterio GIRS y Cap. Trabajo",
                titulo_interno="CAE por Tonelada (`Metodologia_GIRS_vf.pdf` pág. 10) y Capital de Trabajo",
                formula_latex=r"ICT_{desfase} = \frac{\text{Costo Operacional Anual}}{365} \times \text{Días de desfase}",
                explicacion_md=(
                    "- **Criterio GIRS:** En proyectos de residuos bajo enfoque costo-eficiencia, el indicador es el **Costo Anual Equivalente por tonelada dispuesta o valorizada**.\n"
                    "- **Capital de Trabajo (`Clase 1` pág. 17–18):** Es una inversión permanente en $t=0$ que financia el desfase entre egresos e ingresos y se recupera íntegramente en el año final $t=n$."
                ),
            )

        c_graf1, c_graf2 = st.columns([1.35, 1.0])
        with c_graf1:
            fig_cascada = go.Figure(
                go.Waterfall(
                    name="Puente Privado a Social",
                    orientation="v",
                    measure=["absolute", "relative", "relative", "relative", "relative", "total"],
                    x=[
                        f"1. VAN Privado Puro ({wacc_priv*100:.1f}%)",
                        "2. Efecto Tasa Descuento (a TSD 5,5%)",
                        "3. Eliminación Impuestos (Transferencias)",
                        "4. Corrección MO (0,97/0,95/0,91) y Energía",
                        "5. Beneficio Carbono ($71.801/t) y Ahorro GIRS",
                        "6. VAN Social SNI 2026 (5,5%)",
                    ],
                    y=[
                        res_eval["van_priv_puro"],
                        res_eval["efecto_tasa_descuento"],
                        res_eval["efecto_impuestos"],
                        res_eval["efecto_precios_cuenta"],
                        res_eval["efecto_ambiental_social"],
                        res_eval["van_social"],
                    ],
                    connector={"line": {"color": "#64748b"}},
                    decreasing={"marker": {"color": "#dc2626"}},
                    increasing={"marker": {"color": "#059669"}},
                    totals={"marker": {"color": "#1e3a8a"}},
                )
            )
            fig_cascada.update_layout(
                title="Puente de Valoración: ¿Por qué difiere el VAN Privado del VAN Social SNI?",
                yaxis_title="Valor Actual Neto ($ CLP)",
                height=420,
                plot_bgcolor="#f8fafc",
            )
            st.plotly_chart(fig_cascada, use_container_width=True)

        with c_graf2:
            df_comp_fl = res_eval["df_flujos"]
            fig_fl = go.Figure()
            fig_fl.add_trace(
                go.Bar(
                    x=df_comp_fl["Año"],
                    y=df_comp_fl["Flujo_Privado_Puro"],
                    name="Flujo Privado Puro",
                    marker_color="#64748b",
                )
            )
            fig_fl.add_trace(
                go.Bar(
                    x=df_comp_fl["Año"],
                    y=df_comp_fl["Flujo_Social_SNI"],
                    name="Flujo Social SNI 2026",
                    marker_color="#2563eb",
                )
            )
            fig_fl.update_layout(
                title="Comparación Anual: Flujo Privado Puro vs. Flujo Social SNI",
                xaxis_title="Año de Operación",
                yaxis_title="Flujo Neto Anual ($ CLP)",
                barmode="group",
                height=420,
                plot_bgcolor="#f8fafc",
                legend=dict(orientation="h", y=1.12),
            )
            st.plotly_chart(fig_fl, use_container_width=True)

        st.markdown("##### Tabla Detallada de Flujos Anuales (Privado Puro, Privado Financiado y Social SNI)")
        st.dataframe(res_eval["df_flujos"], use_container_width=True, hide_index=True)

    # ==========================================================================
    # PESTAÑA 2: MICROECONOMÍA DE FONTAINE Y EJERCICIO DE LA LECHE (CLASE 2)
    # ==========================================================================
    with tabs[1]:
        st.subheader("Laboratorio Microeconómico de Ernesto Fontaine: Ejercicio Oficial de la Leche (`Clase2.pdf`, págs. 20–25)")
        st.markdown(
            "Resuelve de forma interactiva el ejercicio planteado por la **Prof. Luz María Ferrada** en `Clase2.pdf`: "
            "una cooperativa lechera proyecta instalar una planta para producir **1.470 toneladas/año de leche en polvo** "
            "en un mercado cerrado sin distorsiones. Calcula el equilibrio inicial, el nuevo equilibrio, el **Valor Social de la Producción "
            "por Eficiencia ($VSP = AD + LR$)** y la **Distribución por Agencia (Inversionista, Consumidores y Productores)**."
        )

        col_f1, col_f2, col_f3 = st.columns([1.6, 1.2, 1.2])
        with col_f1:
            modo_leche = st.selectbox(
                "Seleccione Configuración de Parámetros de Clase 2:",
                [
                    "1. Ecuaciones Exactas Lámina 20: Po = 50 + 0,025*Qo | Pd = 300 - 0,0205*Qd (Q_proy = 1.470)",
                    "2. Variante Lámina 21 (Precio Con Proyecto P1 = $125 -> Ingreso Firma = $183.750)",
                    "3. Parámetros Personalizados (Editable para ejercicios de prueba)",
                ],
            )
        with col_f2:
            q_proy_leche = st.number_input("Producción del Proyecto (ton/año):", min_value=100.0, value=1470.0, step=50.0)
        with col_f3:
            pct_intro = st.slider(
                "Control de Secuencia (% de entrada del proyecto al mercado):",
                min_value=0,
                max_value=100,
                value=100,
                step=10,
                help="Desliza de 0% (Sin Proyecto) a 100% (Con Proyecto) para ver cómo se desplaza la curva de oferta y aparecen las áreas AD y LR.",
            )

        if "1." in modo_leche:
            a_of, b_of, c_dem, d_dem = 50.0, 0.025, 300.0, 0.0205
        elif "2." in modo_leche:
            # Calibrado para que con Q_proy = 1470 el precio P1 sea exactamente 125 (Lámina 21: 125 * 1470 = 183.750)
            a_of, b_of, c_dem, d_dem = 50.0, 0.025, 211.75, 0.020
        else:
            c_ed1, c_ed2, c_ed3, c_ed4 = st.columns(4)
            a_of = c_ed1.number_input("Intercepto Oferta (a):", value=50.0)
            b_of = c_ed2.number_input("Pendiente Oferta (b):", value=0.025, format="%.4f")
            c_dem = c_ed3.number_input("Intercepto Demanda (c):", value=300.0)
            d_dem = c_ed4.number_input("Pendiente Demanda (d):", value=0.0205, format="%.4f")

        res_leche = resolver_mercado_fontaine_clase2(
            a_of, b_of, c_dem, d_dem, q_proy_leche, pct_intro / 100.0
        )

        m_f1, m_f2, m_f3, m_f4 = st.columns(4)
        with m_f1:
            st.metric(
                "a) Equilibrio Sin Proyecto",
                f"P0 = ${res_leche['p0']:.2f}",
                f"Q0 = {res_leche['q0']:,.1f} ton/año",
            )
            renderizar_nota_metodologica(
                titulo_boton="Cómo se calcula a) y b)",
                titulo_interno="Equilibrio Inicial y Desplazamiento de Oferta (`Clase2.pdf` págs. 20–21)",
                formula_latex=r"P_o = a + b Q_o = P_d = c - d Q_d \implies Q_0 = \frac{c - a}{b + d}",
                explicacion_md=(
                    f"- **a) Sin Proyecto:** Igualando oferta y demanda se obtiene $Q_0 = {res_leche['q0']:,.2f}$ ton y $P_0 = \\${res_leche['p0']:.2f}$.\n"
                    f"- **b) Con Proyecto ($Q' = Q_o + {res_leche['q_proy']:,.0f}$):** El precio baja a **$P_1 = \\${res_leche['p1']:.2f}$**, el consumo nacional sube a **$Q_d^1 = {res_leche['qd1']:,.1f}$ ton** y los antiguos productores bajan a **$Q_o^1 = {res_leche['qo1']:,.1f}$ ton**."
                ),
            )

        with m_f2:
            st.metric(
                "b) Ingresos Firma (VPP)",
                f"${res_leche['ingresos_firma_vpp']:,.0f}",
                f"P1 = ${res_leche['p1']:.2f} | Qd1 = {res_leche['qd1']:,.1f} ton",
            )
            renderizar_nota_metodologica(
                titulo_boton="Ingresos Privados vs. VSP",
                titulo_interno="¿Por qué el Valor Privado (VPP) es menor que el Valor Social (VSP)?",
                formula_latex=r"VPP = P_1 \times Q_{proy} < VSP = \frac{P_0 + P_1}{2} \times Q_{proy}",
                explicacion_md=(
                    "- La cooperativa vende sus toneladas al nuevo precio de mercado $P_1$ (menor que $P_0$).\n"
                    "- Sin embargo, para el país cada tonelada adicional vale más que $P_1$: la fracción que aumenta el consumo vale según la disposición a pagar sobre la curva de demanda ($AD$) y la fracción que reemplaza producción antigua ahorra recursos por el costo marginal de oferta ($LR$)."
                ),
            )

        with m_f3:
            st.metric(
                "c) Valor Social Producción (VSP)",
                f"${res_leche['vsp_eficiencia']:,.0f}",
                f"AD=${res_leche['valor_ad']:,.0f} + LR=${res_leche['valor_lr']:,.0f}",
            )
            renderizar_nota_metodologica(
                titulo_boton="Enfoque de Eficiencia (AD + LR)",
                titulo_interno="Fórmula de Eficiencia (`Clase2.pdf`, láminas 15 y 22)",
                formula_latex=r"VSP = AD + LR = \frac{P_0 + P_1}{2}(Q_d^1 - Q_0) + \frac{P_0 + P_1}{2}(Q_0 - Q_o^1)",
                explicacion_md=(
                    f"- **Aumento en Disponibilidad ($AD$):** $\\Delta Q_d = +{res_leche['aumento_disp_q']:,.1f}$ ton valoradas bajo la curva de demanda = **`${res_leche['valor_ad']:,.0f}`**.\n"
                    f"- **Liberación de Recursos ($LR$):** $\\Delta Q_o = -{res_leche['liberacion_rec_q']:,.1f}$ ton ahorradas bajo la curva de oferta = **`${res_leche['valor_lr']:,.0f}`**.\n"
                    f"- **Suma $VSP = AD + LR$:** **`${res_leche['vsp_eficiencia']:,.0f}`**."
                ),
            )

        with m_f4:
            st.metric(
                "e) Precio Social Unitario",
                f"${res_leche['precio_social_unitario']:.2f} / ton",
                f"Promedio (P0+P1)/2 = ${res_leche['precio_social_unitario']:.2f}",
            )
            renderizar_nota_metodologica(
                titulo_boton="Enfoque de Agencia (Lámina 24)",
                titulo_interno="Conciliación Exacta por Agentes (`Clase2.pdf`, láminas 15 y 24)",
                formula_latex=r"VSP = VPP_{\text{Inversionista}} + \Delta EC_{\text{Consumidores}} + \Delta EP_{\text{Otros Productores}}",
                explicacion_md=(
                    f"- **1. Inversionista ($VPP$):** `+${res_leche['ingresos_firma_vpp']:,.0f}`\n"
                    f"- **2. Excedente del Consumidor ($\\Delta EC$):** `+${res_leche['delta_ec']:,.0f}` (ganan porque el precio baja de ${res_leche['p0']:.2f} a ${res_leche['p1']:.2f})\n"
                    f"- **3. Excedente de Otros Productores ($\\Delta EP$):** `${res_leche['delta_ep']:,.0f}` (pierden por menor precio)\n"
                    f"- **Suma por Agencia:** **`${res_leche['vsp_agencia']:,.0f}`** (idéntico al VSP por Eficiencia)."
                ),
            )

        col_gf1, col_gf2 = st.columns([1.45, 1.0])
        with col_gf1:
            fig_font = construir_grafico_fontaine_interactivo(
                a_of, b_of, c_dem, d_dem, q_proy_leche, pct_intro / 100.0
            )
            st.plotly_chart(fig_font, use_container_width=True)

        with col_gf2:
            st.markdown("##### Conciliación Enfoque de Eficiencia vs. Enfoque de Agencia (`Clase2.pdf`)")
            df_agencia = pd.DataFrame([
                {"Enfoque": "Eficiencia", "Componente / Agente": "Aumento en Disponibilidad (AD)", "Efecto Físico (ton)": round(res_leche["aumento_disp_q"], 2), "Valor Económico ($)": round(res_leche["valor_ad"], 0)},
                {"Enfoque": "Eficiencia", "Componente / Agente": "Liberación de Recursos (LR)", "Efecto Físico (ton)": round(res_leche["liberacion_rec_q"], 2), "Valor Económico ($)": round(res_leche["valor_lr"], 0)},
                {"Enfoque": "Eficiencia", "Componente / Agente": "TOTAL VSP (AD + LR)", "Efecto Físico (ton)": round(res_leche["q_proy"], 2), "Valor Económico ($)": round(res_leche["vsp_eficiencia"], 0)},
                {"Enfoque": "Agencia", "Componente / Agente": "1. Inversionista / Cooperativa (VPP)", "Efecto Físico (ton)": round(res_leche["q_proy"], 2), "Valor Económico ($)": round(res_leche["ingresos_firma_vpp"], 0)},
                {"Enfoque": "Agencia", "Componente / Agente": "2. Consumidores (Delta Excedente Consumidor)", "Efecto Físico (ton)": round(res_leche["qd1"], 2), "Valor Económico ($)": round(res_leche["delta_ec"], 0)},
                {"Enfoque": "Agencia", "Componente / Agente": "3. Otros Productores (Delta Excedente Productor)", "Efecto Físico (ton)": round(res_leche["qo1"], 2), "Valor Económico ($)": round(res_leche["delta_ep"], 0)},
                {"Enfoque": "Agencia", "Componente / Agente": "TOTAL POR AGENCIA (VPP + dEC + dEP)", "Efecto Físico (ton)": round(res_leche["q_proy"], 2), "Valor Económico ($)": round(res_leche["vsp_agencia"], 0)},
            ])
            st.dataframe(df_agencia, use_container_width=True, hide_index=True)

    # ==========================================================================
    # PESTAÑA 3: EVALUACIÓN AMBIENTAL (RA2): LEOPOLD, BARZEV Y GIRS
    # ==========================================================================
    with tabs[2]:
        st.subheader("Resultado de Aprendizaje 2 (RA2 — 50%): Matriz de Leopold, Valoración de BSA y Metodología GIRS")
        st.markdown(
            "Cubre íntegramente los contenidos del **RA2 del Programa de Asignatura (`FDIC26`)**: "
            "**Matriz de Leopold**, **Valores de Uso, Opción y Existencia (`GuiaVEdelosBSA.pdf` — Radoslav Barzev)**, "
            "**Valoración Contingente, Costo de Viaje y Precios Hedónicos**, y conversión oficial de **Metano ($\text{CH}_4 \times 28$) "
            "y Óxido Nitroso ($\text{N}_2\text{O} \times 265$)** a $\text{CO}_2\text{eq}$."
        )

        col_a1, col_a2 = st.columns([1.3, 1.1])
        with col_a1:
            st.markdown("#### A. Matriz Interactiva de Impacto Ambiental de Leopold")
            st.caption("Edita la Magnitud (-10 = impacto negativo severo a +10 = beneficio ambiental alto) y la Importancia (1 a 10):")
            df_leo_edit = st.data_editor(df_leopold_default, use_container_width=True, hide_index=True, key="editor_leopold")
            df_leo_edit["Puntaje_M_x_I"] = df_leo_edit["Magnitud_M"] * df_leo_edit["Importancia_I"]
            impacto_neto_total = int(df_leo_edit["Puntaje_M_x_I"].sum())

            fig_leo = px.bar(
                df_leo_edit,
                x="Puntaje_M_x_I",
                y="Factor_Ambiental",
                orientation="h",
                color="Puntaje_M_x_I",
                color_continuous_scale="RdYlGn",
                title=f"Índice Ponderado de Leopold por Factor Ambiental (Suma Neta = {impacto_neto_total:+d})",
            )
            fig_leo.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_leo, use_container_width=True)

        with col_a2:
            st.markdown("#### B. Calculadora de los 3 Métodos de Valoración Ambiental (Barzev, 2002)")
            metodo_amb = st.selectbox(
                "Seleccione Método de Valoración de Bienes y Servicios Ambientales (BSA):",
                [
                    "1. Valoración Contingente (MVC — Mercados Hipotéticos / DAP)",
                    "2. Costo de Viaje (MCV — Mercados Sustitutos / Recreación)",
                    "3. Precios Hedónicos (MPH — Diferencial de Valor Inmobiliario)",
                ],
            )
            if "1." in metodo_amb:
                renderizar_nota_metodologica(
                    titulo_boton="Fórmula Valoración Contingente (MVC)",
                    titulo_interno="Método de Valoración Contingente (`GuiaVEdelosBSA.pdf`, pág. 60)",
                    formula_latex=r"BN_{MVC} = DAP_{\text{media}} \times N_{\text{Hogares Objetivo}}",
                    explicacion_md=(
                        "- **¿Cuándo se aplica?:** Único método capaz de estimar tanto **Valores de Uso** como **Valores de No Uso (Opción y Existencia)** mediante encuestas de Disposición a Pagar (DAP) o Disposición a Ser Compensado."
                    ),
                )
                dap_mensual = st.number_input("Disposición a Pagar Media por Hogar ($/mes):", min_value=100, value=2500, step=200)
                n_hogares = st.number_input("Número de Hogares de la Población Objetivo:", min_value=50, value=12500, step=500)
                val_anual_bsa = dap_mensual * 12 * n_hogares
                st.success(f"**Beneficio Ambiental Anual Estimado (MVC):** `${val_anual_bsa:,.0f} CLP / año`")

            elif "2." in metodo_amb:
                renderizar_nota_metodologica(
                    titulo_boton="Fórmula Costo de Viaje (MCV)",
                    titulo_interno="Método del Costo de Viaje (`GuiaVEdelosBSA.pdf`, pág. 68)",
                    formula_latex=r"CV_i = C_{\text{transporte}} + C_{\text{acceso}} + VST_{\text{Deporte}} \cdot t_{\text{viaje}}",
                    explicacion_md=(
                        "- **¿Cuándo se aplica?:** Valora servicios recreativos y belleza escénica de parques, humedales o riberas usando el costo de traslado y el **Valor Social del Tiempo Recreación ($2.792 CLP/h-pax en 2026)**."
                    ),
                )
                visitantes_anio = st.number_input("Visitantes anuales al sitio natural:", min_value=100, value=18000, step=1000)
                horas_viaje_ida_vuelta = st.slider("Horas de viaje promedio (ida y vuelta):", 0.5, 6.0, 2.0, 0.5)
                gasto_transporte_pax = st.number_input("Gasto directo de transporte y acceso ($/persona):", min_value=500, value=4500, step=500)
                costo_tiempo_social = horas_viaje_ida_vuelta * PRECIOS_SOCIALES_2026["VST_deporte_recreacion"]
                val_anual_bsa = visitantes_anio * (gasto_transporte_pax + costo_tiempo_social)
                st.success(
                    f"**Costo de Viaje Unitario (Transporte + VST 2026):** `${gasto_transporte_pax + costo_tiempo_social:,.0f} / visitante`\n\n"
                    f"**Valor Recreativo Anual del Ecosistema (MCV):** `${val_anual_bsa:,.0f} CLP / año`"
                )

            else:
                renderizar_nota_metodologica(
                    titulo_boton="Fórmula Precios Hedónicos (MPH)",
                    titulo_interno="Método de Precios Hedónicos (`GuiaVEdelosBSA.pdf`, pág. 74)",
                    formula_latex=r"P_{\text{vivienda}} = f(S_{\text{estructural}}, N_{\text{vecindario}}, A_{\text{ambiental}}) \implies PMg_A = \frac{\partial P}{\partial A}",
                    explicacion_md=(
                        "- **¿Cuándo se aplica?:** Estima el valor de atributos ambientales locales (calidad del aire, ausencia de olores de vertederos, cercanía a áreas verdes) a través del diferencial de precios de las viviendas."
                    ),
                )
                n_viviendas = st.number_input("Viviendas beneficiadas en el Área de Influencia:", min_value=10, value=850, step=50)
                valor_medio_viv = st.number_input("Valor promedio por vivienda ($ CLP):", min_value=10000000, value=65000000, step=5000000)
                plusvalia_ambiental_pct = st.slider("Prima hedónica por mejora ambiental / cierre microbasural (%):", 0.5, 15.0, 4.5, 0.5)
                val_stock_hedonico = n_viviendas * valor_medio_viv * (plusvalia_ambiental_pct / 100.0)
                st.success(f"**Incremento de Bienestar Patrimonial (Precios Hedónicos):** `${val_stock_hedonico:,.0f} CLP`")

    # ==========================================================================
    # PESTAÑA 4: FORMULACIÓN SNI 2025, ÁRBOLES Y MARCO LÓGICO
    # ==========================================================================
    with tabs[3]:
        st.subheader("Formulación SNI (`METODOLOGIA-GENERAL-2025.pdf`), Árboles Causales y Matriz de Marco Lógico")

        c_ar1, c_ar2 = st.columns([2.2, 1.0])
        with c_ar1:
            caso_arbol_sel = st.selectbox(
                "Seleccione Caso de Estudio Oficial de Cátedra:",
                list(CASOS_ARBOLES_CATEDRA.keys()),
            )
        with c_ar2:
            ver_positivo = st.toggle(
                "Revelar Positivo Fotográfico (Pasar de Árbol de Problemas a Árbol de Objetivos)",
                value=False,
            )

        datos_arbol = CASOS_ARBOLES_CATEDRA[caso_arbol_sel]
        fig_arb = construir_figura_arbol_catedra(datos_arbol, modo_positivo=ver_positivo)
        st.plotly_chart(fig_arb, use_container_width=True)
        st.info(f"**Alternativa de Solución Configurada:** {datos_arbol['alternativa_seleccionada']}")

        st.markdown("---")
        col_em1, col_em2 = st.columns([1.05, 1.35])
        with col_em1:
            st.markdown("#### Embudo de Población SNI (`Clase3.pdf`, págs. 7–8)")
            pob_ref = st.number_input("1. Población de Referencia (Total Área de Influencia):", min_value=100, value=174998, step=1000)
            pct_afectada = st.slider("2. % Población con Problema (Afectada):", 5, 100, 35)
            pct_objetivo = st.slider("3. % de la Población Afectada atendida por el Proyecto (Población Objetivo):", 10, 100, 65)

            pob_afectada = int(round(pob_ref * (pct_afectada / 100.0)))
            pob_sin_prob = pob_ref - pob_afectada
            pob_objetivo = int(round(pob_afectada * (pct_objetivo / 100.0)))
            pob_postergada = pob_afectada - pob_objetivo

            fig_funnel = go.Figure(
                go.Funnel(
                    y=[
                        "1. Población de Referencia (AI)",
                        "2. Población Afectada (Con Problema)",
                        "3. Población Objetivo (Beneficiarios)",
                        "4. Población Postergada (No cubierta)",
                    ],
                    x=[pob_ref, pob_afectada, pob_objetivo, pob_postergada],
                    textinfo="value+percent initial",
                    marker={"color": ["#1e3a8a", "#d97706", "#059669", "#64748b"]},
                )
            )
            fig_funnel.update_layout(height=310, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_funnel, use_container_width=True)

        with col_em2:
            st.markdown("#### Matriz de Marco Lógico (MML) con Indicadores de Eficacia, Eficiencia y Calidad")
            renderizar_nota_metodologica(
                titulo_boton="Reglas de Oro del Marco Lógico en Pruebas",
                titulo_interno="Estructura de la Matriz de Marco Lógico (`MARCO LOGICO.pdf` y `Proceso2 RA1.pdf`)",
                explicacion_md=(
                    "- **Lectura de Abajo hacia Arriba:** *Si se ejecutan las Actividades (y se cumplen los supuestos), entonces se logran los Componentes; si se entregan los Componentes, se logra el Propósito; y si se logra el Propósito, se contribuye al Fin*.\n"
                    "- **Un solo Propósito:** Cada proyecto tiene **un único Propósito** (que corresponde al Objetivo Central del árbol de objetivos).\n"
                    "- **Regla Pregunta 13 (`Proceso2 RA1.pdf`):** A nivel de **Actividades NO se definen supuestos** y en la columna de indicadores se registra el **Presupuesto detallado por actividad**."
                ),
            )
            df_mml = pd.DataFrame([
                {
                    "Nivel de Objetivos": f"FIN (Impacto Largo Plazo): {datos_arbol['fines_n2'][2]}",
                    "Indicadores (Eficacia / Eficiencia / Calidad)": "Eficacia: Variación porcentual del indicador comunal en el año 3 de operación",
                    "Medios de Verificación": "Estadísticas oficiales (SINADER / INE / Reportes Municipales)",
                    "Supuestos Externos": "Sostenibilidad de la política pública sectorial y condiciones macroeconómicas",
                },
                {
                    "Nivel de Objetivos": f"PROPÓSITO (Objetivo Central): {datos_arbol['objetivo_central'].replace(chr(10), ' ')}",
                    "Indicadores (Eficacia / Eficiencia / Calidad)": (
                        "Eficacia: (Población atendida / Población objetivo) * 100 | "
                        "Eficiencia: Costo total / Unidad de resultado | "
                        "Calidad: % de entregas dentro de estándar"
                    ),
                    "Medios de Verificación": "Registros operacionales de la unidad ejecutora e informe de seguimiento anual",
                    "Supuestos Externos": "Adhesión activa de los usuarios/beneficiarios del área de influencia",
                },
                {
                    "Nivel de Objetivos": f"COMPONENTES (Productos/Servicios): 1) {datos_arbol['medios_n1'][0].replace(chr(10), ' ')}; 2) {datos_arbol['medios_n1'][1].replace(chr(10), ' ')}",
                    "Indicadores (Eficacia / Eficiencia / Calidad)": (
                        "Eficacia: N° de prestaciones/toneladas procesadas vs. meta anual | "
                        "Eficiencia: Costo promedio por componente | "
                        "Calidad: Cumplimiento técnico NCh"
                    ),
                    "Medios de Verificación": "Actas de recepción, pesajes en planta y estados financieros auditados",
                    "Supuestos Externos": "Suministro oportuno de insumos y mantención preventiva al día",
                },
                {
                    "Nivel de Objetivos": f"ACTIVIDADES (Insumos y Tareas): {datos_arbol['medios_n2'][0].replace(chr(10), ' ')} + {datos_arbol['medios_n2'][1].replace(chr(10), ' ')}",
                    "Indicadores (Eficacia / Eficiencia / Calidad)": "PRESUPUESTO DETALLADO POR ACTIVIDAD (En $ CLP / UF según Carta Gantt)",
                    "Medios de Verificación": "Informe de ejecución presupuestaria, facturas y contratos visados",
                    "Supuestos Externos": "NO APLICA (A nivel de actividades no se definen supuestos — Regla Cátedra)",
                },
            ])
            st.dataframe(df_mml, use_container_width=True, hide_index=True)

    # ==========================================================================
    # PESTAÑA 5: ENTRENADOR PRUEBA PROCESO 2 RA1, PAUTA 10 PUNTOS Y EXCEL VIVO
    # ==========================================================================
    with tabs[4]:
        st.subheader("Pauta Oficial de `Proceso2 RA1.pdf`, Checklist de Términos de Referencia y Exportador Excel")

        col_ex1, col_ex2 = st.columns([1.35, 1.0])
        with col_ex1:
            st.markdown("#### Banco Oficial Resuelto de `Proceso2 RA1.pdf` (Prof. Luz María Ferrada)")
            df_vf = pd.DataFrame([
                {"N°": 1, "Afirmación de Examen": "El principio de proporcionalidad establece que el alcance y detalle del análisis deben guardar relación con la complejidad, magnitud y costo de la iniciativa.", "Resp.": "V", "Justificación Oficial de Cátedra": "Verdadero (Metodología General SNI 2025, cap. II.1.3)."},
                {"N°": 2, "Afirmación de Examen": "Un perfil que postula a ejecución solicita recursos para el diseño de la inversión.", "Resp.": "F", "Justificación Oficial de Cátedra": "Falso: Un proyecto que postula a ejecución solicita financiar las obras de ejecución; el diseño ya se tiene."},
                {"N°": 8, "Afirmación de Examen": "En la mayoría de los casos no hay diferencia entre los conceptos externalidad y efectos indirectos.", "Resp.": "F", "Justificación Oficial de Cátedra": "Falso: Externalidades son efectos sobre terceros fuera del mercado directo; efectos indirectos ocurren en mercados de bienes sustitutos o complementarios."},
                {"N°": 9, "Afirmación de Examen": "Cuando dos alternativas difieren en su nivel de producción con beneficio unitario equivalente, la selección proviene del CAE por producto o solución entregada.", "Resp.": "V", "Justificación Oficial de Cátedra": "Verdadero (criterio Costo-Eficiencia por unidad producida o tonelada dispuesta)."},
                {"N°": 11, "Afirmación de Examen": "Es más conveniente cuando los terrenos son de propiedad del municipio, dado que el costo de inversión se reduce en lo que cuesta el terreno.", "Resp.": "F", "Justificación Oficial de Cátedra": "Falso: Los terrenos públicos o municipales siempre deben valorarse a su costo de oportunidad social."},
                {"N°": 13, "Afirmación de Examen": "En un Marco Lógico, a nivel de actividades no se definen supuestos.", "Resp.": "V", "Justificación Oficial de Cátedra": "Verdadero: Los supuestos se definen en Actividades->Componentes, Componentes->Propósito y Propósito->Fin."},
                {"N°": 14, "Afirmación de Examen": "La obtención de un RS (Recomendado Satisfactoriamente) significa que el proyecto se realizará.", "Resp.": "F", "Justificación Oficial de Cátedra": "Falso: El RS acredita viabilidad técnico-económica, pero no asegura priorización ni asignación presupuestaria de fondos."},
                {"N°": 15, "Afirmación de Examen": "El precio social de la mano de obra es siempre menor o igual que su precio privado.", "Resp.": "V", "Justificación Oficial de Cátedra": "Verdadero: FCSMO 2026 es 0,97 (Calificada), 0,95 (Semi Calificada) y 0,91 (No Calificada)."},
            ])
            st.dataframe(df_vf, use_container_width=True, hide_index=True)

        with col_ex2:
            st.markdown("#### Checklist de los 10 Puntos (`Pauta para el proyecto.pdf`)")
            df_tdr = pd.DataFrame([
                {"Punto TDR": "1. Planteamiento del problema y objetivo", "Requisito Clave": "Problema central, causas/efectos con evidencia y árbol de medios y fines"},
                {"Punto TDR": "2. Diagnóstico del residuo", "Requisito Clave": "Caracterización, AE/AI, disponibilidad, Pob. Objetivo, Oferta, Demanda y Déficit"},
                {"Punto TDR": "3. Definición de alternativas", "Requisito Clave": "Optimización de situación base y postulación de alternativas comparables"},
                {"Punto TDR": "4. Configuración de la alternativa", "Requisito Clave": "Mercado, Localización, Logística, Croquis, Tecnología, Flujo de proceso, Personal (CIUO-08) y Marco Legal (Ley 20.920 / DS 189)"},
                {"Punto TDR": "5. Cuantificación", "Requisito Clave": "Proyecciones físicas, inversiones/reinversiones, costos e ingresos"},
                {"Punto TDR": "6. Estimación de capital de trabajo", "Requisito Clave": "Cálculo explícito (Déficit acumulado máximo o Período de desfase)"},
                {"Punto TDR": "7. Flujo de caja privado y evaluación", "Requisito Clave": "Flujo privado (Puro/Financiado), VAN Privado y TIR"},
                {"Punto TDR": "8. Beneficios netos y evaluación social", "Requisito Clave": "Precios Sociales 2026 (TSD 5,5%, FCSMO, Carbono $71.801/t), VANS y CAE/ton"},
                {"Punto TDR": "9. Modelo de gestión estratégica", "Requisito Clave": "Lienzo de Modelo de Negocios (CANVAS) de 9 bloques"},
                {"Punto TDR": "10. Modelo de seguimiento", "Requisito Clave": "Matriz de Marco Lógico (Fin, Propósito, Componentes, Actividades e Indicadores)"},
            ])
            st.dataframe(df_tdr, use_container_width=True, hide_index=True, height=310)

        st.markdown("---")
        bytes_excel = exportar_excel_proyectos_sni_formulas(
            res_eval=res_eval,
            res_leche=res_leche,
            df_leopold=df_leo_edit,
            parametros_sim={"wacc_privado": wacc_priv},
        )
        st.download_button(
            label="Exportar Libro Maestro de Evaluación Integrada de Proyectos (.xlsx de 5 Hojas con Fórmulas Vivas =NPV, =IRR, =PMT)",
            data=bytes_excel,
            file_name="Evaluacion_Integrada_Proyectos_SNI_2026_Formulas_Vivas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Evaluación Integrada de Proyectos 2026 — ULagos",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    renderizar_extension_proyectos_sni()
