import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Configuración estética de la web
st.set_page_config(page_title="Materiales Aeroespaciales - UVigo", layout="wide")

# Estilo UVigo (CSS inyectado)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; background-color: #004b87; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Sistema de Análisis de Materiales Aeroespaciales")
st.write("### EEAE - Universidade de Vigo")

# --- SIDEBAR: PARÁMETROS TÉCNICOS ---
with st.sidebar:
    st.header("Configuración de Probeta")
    material = st.text_input("Material", value="Aluminio 7075-T6")
    tipo = st.selectbox("Geometría", ["Cilíndrica", "Plana"])
    
    if tipo == "Cilíndrica":
        d0 = st.number_input("Diámetro d₀ (mm)", value=10.0)
        s0 = np.pi * (d0**2) / 4
    else:
        a = st.number_input("Ancho (mm)", value=10.0)
        b = st.number_input("Espesor (mm)", value=2.0)
        s0 = a * b
        
    l0 = st.number_input("Longitud calibrada inicial L₀ (mm)", value=50.0)
    lu = st.number_input("Longitud tras rotura Lᵤ (mm)", value=55.4)
    st.info(f"Sección calculada S₀: {s0:.2f} mm²")

# --- CUERPO PRINCIPAL ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Entrada de Datos")
    uploaded_file = st.file_uploader("Subir CSV de ensayo (Fuerza vs Desplazamiento)", type="csv")
    
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        # Asumimos columnas: Fuerza_N y Despl_mm
        data['Tension_MPa'] = data['Fuerza_N'] / s0
        data['Deformacion_unit'] = data['Despl_mm'] / l0
        st.success("Datos cargados correctamente")

with col2:
    if uploaded_file:
        st.subheader("2. Curva de Tracción")
        # Gráfica interactiva básica
        fig, ax = plt.subplots()
        ax.plot(data['Deformacion_unit'], data['Tension_MPa'], color='#004b87', lw=2)
        ax.set_xlabel("Deformación (mm/mm)")
        ax.set_ylabel("Tensión (MPa)")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

# --- RESULTADOS AUTOMATIZADOS ---
if uploaded_file:
    st.divider()
    st.subheader("3. Resultados del Informe Técnico")
    
    # Cálculo de Rm
    rm = data['Tension_MPa'].max()
    # Cálculo de Alargamiento A%
    a_porc = ((lu - l0) / l0) * 100
    # Cálculo de Young (E) simplificado para la demo
    # Tomamos el primer 10% de los datos para la pendiente
    limite = int(len(data) * 0.1)
    slope, _, _, _, _ = stats.linregress(data['Deformacion_unit'][:limite], data['Tension_MPa'][:limite])
    e_young = slope / 1000 # GPa

    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Módulo de Young (E)", f"{e_young:.1f} GPa")
    res2.metric("Resistencia (Rm)", f"{rm:.1f} MPa")
    res3.metric("Límite Elástico (Rp0.2)", f"{rm*0.8:.1f} MPa") # Estimación
    res4.metric("Alargamiento (A)", f"{a_porc:.1f} %")

    # Botón para descargar resultados
    st.download_button("Descargar Informe de Resultados", 
                       data.to_csv().encode('utf-8'), 
                       "informe_ensayo.csv", "text/csv")
