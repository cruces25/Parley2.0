import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Tu Parley Coleo", layout="wide")
st.title("🏆 Portal de Control - Sella Tu Parley")

@st.cache_data
def cargar_datos():
    try:
        # Cargamos planilla de control (Nombres y IDs)
        nomina = pd.read_excel("planilla_coleo.xlsx", sheet_name="PLANILLA_CONTROL", header=2)
        # Cargamos cuadros (Resultados)
        cuadros = pd.read_excel("planilla_coleo.xlsx", sheet_name="CUADROS_PARLAY", header=1)
        
        # Limpiamos nombres de columnas
        nomina.columns = [str(c).strip() for c in nomina.columns]
        cuadros.columns = [str(c).strip() for c in cuadros.columns]
        
        return nomina, cuadros
    except Exception as e:
        st.error(f"❌ Error al leer el Excel: {e}")
        return None, None

nomina, cuadros = cargar_datos()

if nomina is not None and cuadros is not None:
    # AJUSTE DE NOMBRES SEGÚN TU EXCEL REAL
    # Cambiamos 'CUADRO' por 'CUADRO #' que es como está en tu archivo
    col_cuadro = 'CUADRO #' 
    columnas_necesarias = [col_cuadro, 'USUARIO', 'CE', 'CN', 'SP']
    
    st.subheader("📊 Tabla de Posiciones (Leaderboard)")
    
    # Quitamos filas vacías y ordenamos por Puntos (CE), Nulas (CN) y Saque de Puerta (SP)
    ranking = cuadros.dropna(subset=[col_cuadro]).sort_values(by=['CE', 'CN', 'SP'], ascending=[False, True, False])
    
    # Mostramos la tabla
    st.dataframe(ranking[columnas_necesarias], use_container_width=True)

    # 3. SECCIÓN DE VALIDACIÓN
    st.divider()
    st.write("### 🔍 Verificación de Cuadro")
    
    nombres_coleadores = nomina['COLEADOR'].dropna().unique().tolist()
    ids_coleadores = nomina.set_index('COLEADOR')['NUMERO'].to_dict()

    col1, col2 = st.columns(2)
    with col1:
        c1 = st.selectbox("Coleador 1", nombres_coleadores, key="s1")
        c2 = st.selectbox("Coleador 2", nombres_coleadores, key="s2")
    with col2:
        c3 = st.selectbox("Coleador 3", nombres_coleadores, key="s3")
        c4 = st.selectbox("Coleador 4", nombres_coleadores, key="s4")

    if st.button("Validar Disponibilidad"):
        try:
            # Ordenamos los IDs para que el orden de selección no importe
            ids = sorted([int(ids_coleadores[c1]), int(ids_coleadores[c2]), int(ids_coleadores[c3]), int(ids_coleadores[c4])])
            id_jugada = "-".join(map(str, ids))
            
            # Buscamos en la columna SERIAL que es la que detectó el sistema
            col_serial = 'SERIAL'
            
            # Verificamos si existe la combinación
            existe = cuadros[col_serial].astype(str).str.contains(id_jugada).any()

            if existe:
                st.error(f"❌ CUADRO OCUPADO: La combinación {id_jugada} ya existe en el sistema.")
            else:
                st.success(f"✅ DISPONIBLE: La combinación {id_jugada} está libre para ser registrada.")
        except Exception as e:
            st.error(f"Error en la validación: Asegúrate de que todos los coleadores tengan un número en la Planilla de Control.")
