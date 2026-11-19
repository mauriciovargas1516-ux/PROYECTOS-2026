# -*- coding: utf-8 -*-
"""
motor_pizarra_pedagogica_sni.py — ORQUESTADOR LIMPIO DEL LABORATORIO 60 FPS Y REFERENCIA SNI 2026
Versión optimizada sin duplicaciones Plotly:
  - Mantiene el Semáforo Jerárquico de Indicadores (1° a 5° Prioridad CEPAL N° 39 / SNI) para la Pestaña 1.
  - Conecta directamente las 7 herramientas a 60 FPS de 'motor_fluidez_vectores_sni.py'.
  - Mantiene el Catálogo Oficial de Precios Sociales 2026 y los 6 Casos Clásicos CEPAL N° 39 como consulta rápida.
"""

import os
import sys
import importlib.util
import numpy as np
import pandas as pd
import streamlit as st

try:
    _ruta_fluidez = os.path.join(os.path.dirname(os.path.abspath(__file__)), "motor_fluidez_vectores_sni.py")
    if os.path.exists(_ruta_fluidez):
        _spec_fl = importlib.util.spec_from_file_location("motor_fluidez_vectores_sni", _ruta_fluidez)
        _mod_fl = importlib.util.module_from_spec(_spec_fl)
        sys.modules["motor_fluidez_vectores_sni"] = _mod_fl
        _spec_fl.loader.exec_module(_mod_fl)
        renderizar_simuladores_fluidos_60fps = getattr(_mod_fl, "renderizar_simuladores_fluidos_60fps", None)
    else:
        renderizar_simuladores_fluidos_60fps = None
except Exception:
    renderizar_simuladores_fluidos_60fps = None


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


def renderizar_semaforo_jerarquia_cepal(res_vivo, cfg):
    """Semáforo Jerárquico Estricto de 1° a 5° Prioridad (CEPAL N° 39 / SNI) conectado en vivo."""
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
                        Indicador decisivo. Mide riqueza neta incremental hoy (VAN &gt; 0). Cumple <b>aditividad y separabilidad</b>.
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


def _render_referencia_ps2026_y_casos():
    st.markdown("<div class='sec-header'>CATÁLOGO OFICIAL DE PRECIOS SOCIALES VIGENTES 2026 (MDSF / SNI)</div>", unsafe_allow_html=True)
    df_cat = pd.DataFrame([
        ["Parámetros Nacionales", "TSD / MOC / MOSC / MONC / FCSD", "% o Factor", "5,5% | 0,97 | 0,95 | 0,91 | 1,00"],
        ["VST Urbano", "Viaje en vehículo (1x) / Espera (2x) / Caminata (2x)", "CLP/h-pax", "$3.338 / $6.676 / $6.676"],
        ["VST Recreación e Interurbano", "Deporte-Recreación / Interurbano Terrestre / Aéreo", "CLP/h-pax", "$2.792 / $10.047 / $16.983"],
        ["VST Carga y Seguridad Vial", "Tiempo de la carga / Valor de una Vida Estadística (VVE)", "CLP", "$12.954/h-veh | $2.383.677.600"],
        ["Combustibles (Vehículo)", "Auto ($760) / Camioneta ($787) / Camión 2 ejes y Bus ($805)", "CLP/litro", "$760 / $787 / $805"],
        ["Combustibles (Octanaje)", "Gasolina 93 ($737) / 95 ($768) / 97 ($822) / Diésel ($805)", "CLP/litro", "$737 a $822"],
        ["Neumáticos y Lubricantes", "Auto ($87.543) a Bus ($364.116) | Lubr. $8.740 / $5.176", "CLP", "$87.543 a $364.116"],
        ["Vehículos Nuevos y Mantención", "Auto ($11,36M) a Bus Eléctrico ($225,36M) | Mant. $6.931/h", "CLP", "$11.360.008 a $236.844.841"],
        ["Ambientales y Energía", "Carbono ($71.801/t CO2eq) | CH4=28 | N2O=265 | Elec. BT $124,8", "CLP", "$71.801/t | $124,8/kWh"],
    ], columns=["Categoría SNI 2026", "Parámetro / Insumo", "Unidad", "Valor Oficial 2026"])
    st.dataframe(df_cat, use_container_width=True, hide_index=True)

    st.markdown("<div class='sec-header'>LOS 6 CASOS CLÁSICOS DE EXAMEN (MANUAL CEPAL N° 39 Y APUNTES DE CLASE)</div>", unsafe_allow_html=True)
    df_casos = pd.DataFrame([
        ["1. Salud en Macondo", "Definir el problema como 'Falta de un hospital de alta complejidad'.", "Error típico: redactar el problema como falta de una solución. El problema real es 'Altas tasas de morbilidad infantil por consumo de agua no potable'; la solución óptima es potabilización y educación sanitaria."],
        ["2. Salud Primaria Santa Ana", "Baja cobertura de atención primaria urbana y rural en Santa Ana.", "Causas: infraestructura insuficiente + bajos incentivos RRHH + deficiente gestión municipal. Efectos: mayor morbilidad -> ausentismo laboral/escolar -> menor productividad."],
        ["3. Intersección Vial Peligrosa", "Alta tasa de accidentes en un cruce urbano.", "Separa acciones excluyentes (Pasarela vs. Semáforo vs. Disco PARE) de complementarias (Campaña vial + Prohibir estacionar)."],
        ["4. Empresa Aeronáutica", "Se gastaron US$ 1.000 millones en desarrollar un avión y el mercado cayó.", "Los US$ 1.000 millones son un costo hundido (irrecuperable) y no entran en la decisión; solo se comparan ingresos futuros vs. costos pendientes."],
        ["5. Quesería Rural", "Divergencia entre evaluación privada y social en una planta rural.", "Salarios sobre costo de oportunidad son alto costo privado pero beneficio redistributivo social; impuestos son transferencia neutra; efluentes son externalidad negativa."],
        ["6. Nutrición Adulto Mayor (MML)", "Construcción de Matriz de Marco Lógico con 4 tipos de indicadores.", "Fin: calidad de vida mejorada. Propósito: mejora niveles de nutrición. Componente: entrega suplementos. Actividades: licitación y ejecución presupuestaria (sin supuestos)."],
    ], columns=["Caso Clásico en Apuntes", "Planteamiento / Trampa de Prueba", "Criterio Metodológico para Defensa y Examen"])
    st.dataframe(df_casos, use_container_width=True, hide_index=True)

    with st.expander("Ciclo de Vida SNI (Preinversión -> Inversión -> Operación) y Muestreo Poblacional (PHP + PHC)", expanded=False):
        st.markdown(
            "- **Preinversión:** Idea / Problema -> Perfil (Situación Base Optimizada) -> Prefactibilidad -> Factibilidad.\n"
            "- **Inversión y Operación:** Diseño -> Ejecución -> Puesta en marcha -> Operación en régimen. Iniciativas IDI con Código BIP único.\n"
            "- **Muestreo de campo:** $PHP = V \\cdot (P/V)_m$ y Población Total $PT = PHP + PHC$."
        )


def renderizar_tab_pizarra_pedagogica():
    st.markdown(
        """
        <div style="background-color:#0F172A;color:#FFFFFF;padding:12px 18px;border-radius:8px;margin-bottom:12px;">
            <div style="font-size:15px;font-weight:700;">
                LABORATORIO FLUIDO A 60 FPS — ENUNCIADOS VIVOS, ECUACIONES EDITABLES Y HOJA MECÁNICA (FDIC26)
            </div>
            <div style="font-size:12.5px;color:#CBD5E1;margin-top:3px;">
                7 simuladores sin lag de servidor con rastro fantasma, flechas vectoriales y solucionario en vivo, más el catálogo SNI 2026 y los 6 casos CEPAL N° 39.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sub_60, sub_ref = st.tabs([
        "1. Suite Interactiva 60 FPS (7 Simuladores + Hoja Mecánica)",
        "2. Catálogo Precios Sociales 2026 y 6 Casos CEPAL N° 39",
    ])
    with sub_60:
        if callable(renderizar_simuladores_fluidos_60fps):
            renderizar_simuladores_fluidos_60fps()
        else:
            st.warning("Coloca 'motor_fluidez_vectores_sni.py' en la raíz del repositorio.")
    with sub_ref:
        _render_referencia_ps2026_y_casos()
