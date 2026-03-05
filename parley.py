import streamlit as st
import pandas as pd
import os

# Configuración de la página
st.set_page_config(page_title="Tu Parley Coleo", layout="wide")
st.title("🏆 Portal de Control - Sella Tu Parley")

# ENLACE DE TU GOOGLE SHEET EN VIVO
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1C52oM3yP47tKJrD2_ryxGkxRPh_lf31m/export?format=xlsx"

# ttl=60 significa que el portal refrescará los datos cada 60 segundos si hay cambios
@st.cache_data(ttl=60)
def cargar_datos():
    try:
        # Cargamos planilla de control (Nombres y IDs)
        nomina = pd.read_excel(URL_PLANILLA, sheet_name="PLANILLA_CONTROL", header=2)
        # Cargamos cuadros (Resultados)
        cuadros = pd.read_excel(URL_PLANILLA, sheet_name="CUADROS_PARLAY", header=1)
        
        # Limpiamos nombres de columnas
        nomina.columns = [str(c).strip() for c in nomina.columns]
        cuadros.columns = [str(c).strip() for c in cuadros.columns]
        
        return nomina, cuadros
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {e}")
        return None, None

nomina, cuadros = cargar_datos()

if nomina is not None and cuadros is not None:
    # Ajuste según los nombres que detectamos en tu archivo
    col_cuadro = 'CUADRO #' 
    columnas_necesarias = [col_cuadro, 'USUARIO', 'CE', 'CN', 'SP']
    
    st.subheader("📊 Tabla de Posiciones (Leaderboard)")
    
    try:
        # Quitamos filas vacías y ordenamos por Puntos (CE), Nulas (CN) y Saque de Puerta (SP)
        ranking = cuadros.dropna(subset=[col_cuadro]).sort_values(by=['CE', 'CN', 'SP'], ascending=[False, True, False])
        
        # Mostramos la tabla profesional
        st.dataframe(ranking[columnas_necesarias], use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ Verifica los datos en el Google Sheet. Error: {e}")

    # 3. SECCIÓN DE VALIDACIÓN
    st.divider()
    st.write("### 🔍 Verificación de Cuadro")
    
    try:
        nombres_coleadores = nomina['COLEADOR'].dropna().unique().tolist()
        # Convertimos NUMERO a entero para que no salgan decimales como 1.0
        ids_coleadores = nomina.set_index('COLEADOR')['NUMERO'].to_dict()

        col1, col2 = st.columns(2)
        with col1:
            c1 = st.selectbox("Coleador 1", nombres_coleadores, key="s1")
            c2 = st.selectbox("Coleador 2", nombres_coleadores, key="s2")
        with col2:
            c3 = st.selectbox("Coleador 3", nombres_coleadores, key="s3")
            c4 = st.selectbox("Coleador 4", nombres_coleadores, key="s4")

        if st.button("Validar Disponibilidad"):
            # Obtenemos los IDs, los convertimos a entero y ordenamos
            ids = sorted([int(ids_coleadores[c1]), int(ids_coleadores[c2]), int(ids_coleadores[c3]), int(ids_coleadores[c4])])
            id_jugada = "-".join(map(str, ids))
            
            # Verificamos si existe en la columna SERIAL
            col_serial = 'SERIAL'
            existe = cuadros[col_serial].astype(str).str.contains(id_jugada).any()

            if existe:
                st.error(f"❌ CUADRO OCUPADO: La combinación {id_jugada} ya existe en el sistema.")
            else:
                st.success(f"✅ DISPONIBLE: La combinación {id_jugada} está libre para ser registrada.")
    except Exception as e:
        st.error(f"Falta información en la planilla: Asegúrate de que todos los coleadores tengan un número asignado.")
