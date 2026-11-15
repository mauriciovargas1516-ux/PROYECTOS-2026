# Suite de Formulación y Evaluación Privada, Social y Ambiental de Proyectos 2026 — ULagos (FDIC26)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://proyectos-2026-ubfvxgpqmpp5z7dn6wlnn3.streamlit.app/)
[![Lanzar Consola en Streamlit](https://img.shields.io/badge/ABRIR_SUITE_DE_PROYECTOS_EN_STREAMLIT-1E3A8A?style=for-the-badge&logo=streamlit&logoColor=white)](https://proyectos-2026-ubfvxgpqmpp5z7dn6wlnn3.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/mauriciovargas1516-ux/PROYECTOS-2026)

Plataforma interactiva de ingeniería económica, evaluación socioambiental y automatización documental desarrollada en **Python (`Streamlit`, `plotly`, `python-docx`, `openpyxl`, `numpy-financial`, `matplotlib`)** para la formulación, evaluación financiera privada (flujo puro y financiado), evaluación social bajo normativa del **Sistema Nacional de Inversiones (SNI / MIDESO 2026)** y evaluación de impacto ambiental (**RA1 y RA2**), aplicada al proyecto de economía circular **"Cartón Vivo Osorno"** y a los casos oficiales de la cátedra **Evaluación Integrada de Proyectos (`FDIC26`)** (Ingeniería Comercial, Universidad de Los Lagos — Docente: Dra. Luz María Ferrada B.).

**Acceso directo a la plataforma interactiva en vivo:**  
https://proyectos-2026-ubfvxgpqmpp5z7dn6wlnn3.streamlit.app/

---

## Arquitectura Funcional de las 5 Pestañas Interactivas (`consola_web.py`)

### 1. Simulador Principal y Descarga Automatizada de Entregables (`.ZIP`)
* **Presets Normativos Instantáneos:** Permite alternar en un clic entre los **Precios Sociales Vigentes SNI 2026** ($\text{TSD} = 5,5\%$, $\text{MOC} = 0,97$, $\text{MOSC} = 0,95$, $\text{MONC} = 0,91$, $\text{FCSD} = 1,00$) y el **Caso Base Original** ($\text{TSD} = 6,0\%$).
* **Edición Dinámica de Partidas:** Permite agregar o quitar filas en vivo dentro de **Inversiones en Activos Fijos (CAPEX)**, **Costos Variables**, **Gastos Fijos Mensuales** y **Dotación de Personal**, recalculando al instante $\text{VAN}$, $\text{TIR}$, $\text{Payback}$, $\text{VAC}$ y $\text{CAE}$.
* **Compilación Documental en Servidor:** Ejecuta en cadena los motores financieros y de maquetación para empaquetar el archivo `Vargas,Muñoz,Jofre.zip` con el **Informe Word (`.docx`)** sobre plantilla oficial ULagos, el **Informe `.pdf`** y los **3 Libros Excel Anexos (`.xlsx`)** con fórmulas vivas.

### 2. Endeudamiento Bancario, Costo-Eficiencia ($\text{VAC}/\text{CAE}$) y Huella de Carbono 2026
* **Flujo Puro vs. Flujo del Inversionista Financiado:** Construye la tabla de amortización bajo el método francés de cuota fija y cuantifica el escudo tributario de los intereses conforme a la `Clase 1` y al Anexo 4 de la Metodología General SNI 2025.
* **Indicadores Costo-Eficiencia:** Calcula el **Valor Actual de los Costos ($\text{VAC}$)**, el **Costo Anual Equivalente ($\text{CAE}$)** y el **$\text{CAE}$ por tonelada valorizada** bajo la Metodología GIRS (Ley REP N° 20.920).
* **Valorización de Gases de Efecto Invernadero (GEI):** Cuantifica las emisiones evitadas al **Precio Social del Carbono 2026 ($71.801\text{ CLP/t CO}_2\text{eq}$)**.

### 3. Ficha Oficial IDI / BIP en Unidades de Fomento (SNI 2026)
* Convierte automáticamente todas las partidas de inversión, capital de trabajo, costos operacionales e indicadores ($\text{VAN}$, $\text{VANS}$, $\text{VAC}$, $\text{CAE}$) a **Unidades de Fomento ($\text{UF} = \$39.727,96\text{ CLP}$)** y dólares observados (**$\$911,18\text{ CLP}$**) según el Anexo N° 1 del Reporte Anual de Precios Sociales 2026.

### 4. Calculadora Microeconómica del Valor Social de la Producción (Ernesto Fontaine)
* Resuelve y grafica equilibrios de mercado con y sin proyecto para funciones lineales de oferta y demanda, descomponiendo el **Aumento en Disponibilidad ($\text{AD}$)** y la **Liberación de Recursos ($\text{LR}$)**.

### 5. Laboratorio de Cátedra `FDIC26` (`motor_catedra_proyectos_sni.py`)
Módulo académico y pedagógico con **Notas Metodológicas desplegables** en LaTeX que integra los 5 bloques del curso en `ulagosvirtual.cl`:
* **Sub-pestaña 5.1 — Precios Sociales 2026 y Cascada Privado $\rightarrow$ Social:** Catálogo completo del reporte MDSF (31 de marzo de 2026) y gráfico *Waterfall* interactivo que explica paso a paso la transición desde el $\text{VAN Privado}$ al $\text{VAN Social}$.
* **Sub-pestaña 5.2 — Microeconomía de Fontaine y Ejercicio del Mercado de la Leche (`Clase 2`, láminas 20–25):** Control de secuencia ($0\%$ a $100\%$) que desplaza la curva de oferta con las $1.470\text{ ton/año}$ de la cooperativa lechera, sombreando $\text{AD} = \$144.645$ y $\text{LR} = \$118.609$ ($\text{VSP} = \$263.253$, precio social unitario $\$179,08/\text{ton}$) y conciliando el **Enfoque de Eficiencia** con el **Enfoque de Agencia** ($\text{VPP} + \Delta EC + \Delta EP$).
* **Sub-pestaña 5.3 — Evaluación Ambiental RA2 (`GuiaVEdelosBSA.pdf` — Barzev, 2002):** **Matriz de Leopold** interactiva ($\sum M \times I$), calculadoras de **Valoración Contingente ($\text{MVC}$)**, **Costo de Viaje ($\text{MCV}$ con $\text{VST Recreación} = 2.792\text{ CLP/h-pax}$)** y **Precios Hedónicos ($\text{MPH}$)**, más conversión IPCC a 100 años para **Metano ($\text{CH}_4 \times 28$)** y **Óxido Nitroso ($\text{N}_2\text{O} \times 265$)**.
* **Sub-pestaña 5.4 — Formulación SNI 2025, Árboles Causales y Marco Lógico:** Interruptor de revelado negativo/positivo entre **Árbol de Problemas** y **Árbol de Objetivos** para los 4 casos oficiales (*Centro de Berries*, *Cartón Vivo Osorno*, *Programa Adulto Mayor* y *Ausentismo Laboral*), **Embudo de Población SNI** (Referencia $\rightarrow$ Afectada $\rightarrow$ Objetivo vs. Postergada) y **Matriz de Marco Lógico (MML)** con indicadores de Eficacia, Eficiencia y Calidad.
* **Sub-pestaña 5.5 — Entrenador Oficial `Proceso2 RA1.pdf`, Auditor TDR de 10 Puntos y Exportador Excel:** Banco resuelto de preguntas Verdadero/Falso con las justificaciones oficiales de cátedra, verificador de `Pauta para el proyecto.pdf` y descarga del libro `Evaluacion_Integrada_Proyectos_SNI_2026_Formulas_Vivas.xlsx` (5 hojas con fórmulas `=NPV`, `=IRR`, `=PMT`, `=PV`, `=SUM`, `=IF`).

---

## Impacto Cuantitativo y Multiplicadores de Velocidad (Pipeline Cloud vs. Trabajo Manual)

| Etapa de Formulación, Modelamiento o Maquetación | Entregable / Volumen Procesado | Tiempo Manual (Word / Excel) | Tiempo Motor Cloud | Horas Ahorradas | % Mejora (Multiplicador) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **1. Construcción de Flujo Privado ($12\%$) y Flujo Social SNI ($5,5\%$) a 10–20 Años** | Corrección de IVA, Aranceles, Precios Sombra ($\text{MOC}/\text{MOSC}/\text{MONC}/\text{Divisa}$), Carbono y Capital de Trabajo | 12,0 horas | **0,01 hrs** (2 seg) | 11,99 hrs/ciclo | **99,9% ($21.600\times$ más rápido)** |
| **2. Compilación de Libros Excel con Fórmulas Nativas (`openpyxl`)** | 3 Anexos del Proyecto + Libro Maestro de Cátedra (5 hojas con `=NPV`, `=IRR`, `=PMT`) | 11,5 horas | **0,02 hrs** (3 seg) | 11,48 hrs/entrega | **99,8% ($13.800\times$ más rápido)** |
| **3. Redacción, Cuadratura de Tablas y Formato Institucional en Word (`python-docx`)** | Portada oficial ULagos, Tabla de Contenido con puntos líderes, 12 capítulos, Canvas, Marco Lógico y APA 7 | 18,0 horas | **0,03 hrs** (4 seg) | 17,97 hrs/informe | **99,8% ($16.200\times$ más rápido)** |
| **4. Recálculo Total ante Cambio de un Supuesto (Sueldo, Precio, Deuda o $\text{TSD}$)** | Actualizar Excels + más de 15 tablas del Word + 7 gráficos + conclusiones sin descuadres | 4,5 horas (por cambio) | **0,02 hrs** (8 seg) | 4,48 hrs/iteración | **99,6% ($2.025\times$ más rápido)** |
| **TOTAL GENERACIÓN DE ENTREGA OFICIAL COMPLETA (`.ZIP`)** | **1 Word + 1 PDF + 4 Libros Excel + 12 Gráficos Interactivos y de Ingeniería** | **46,0 horas** | **0,20 hrs (12 min)** | **45,80 horas** | **99,6% ($230,0\times$ más rápido)** |

---

## Estructura de Archivos del Repositorio

```text
PROYECTOS-2026/
├── consola_web.py                                  # Punto de entrada principal en Streamlit Cloud (5 Pestañas)
├── 0_consola_maestra_total.py                      # Consola maestra sincronizada (Espejo de respaldo)
├── motor_catedra_proyectos_sni.py                  # Módulo de extensión FDIC26 (SNI 2026, Fontaine, Leopold, Barzev, MML y RA1)
├── 1_simulador_interactivo_cartonvivo.py           # Motor base de evaluación privada/social y simulador local
├── 2_corrector_formato_y_excels.py                 # Compilador de los 3 Libros Excel editables y documento Word base
├── 3_integrador_arboles_y_pauta_josue.py           # Inyector de los 7 diagramas técnicos, Canvas, Marco Lógico y PDF/ZIP
├── plantilla_hoja_carta_institucional_BLANCO.docx  # Plantilla oficial de la Universidad de Los Lagos
├── Vargas,Muñoz,Jofre.zip                          # Paquete precompilado de respaldo con Word, PDF y 3 Excels
├── packages.txt                                    # Dependencia de sistema Linux (libreoffice para conversión PDF)
├── requirements.txt                                # Librerías Python (streamlit, plotly, openpyxl, python-docx, etc.)
└── README.md                                       # Documentación técnica e institucional del repositorio
```

---

## Instalación y Ejecución Local

```bash
git clone https://github.com/mauriciovargas1516-ux/PROYECTOS-2026.git
cd PROYECTOS-2026
pip install -r requirements.txt
streamlit run consola_web.py
```
