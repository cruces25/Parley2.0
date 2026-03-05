import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Tu Parley Coleo", layout="wide")
st.title("🏆 Portal de Control - Sella Tu Parley")

@st.cache_data
def cargar_datos():
    try:
        # Cargamos planilla de control (Nombres y IDs)
        # header=2 porque los títulos están en la fila 3
        nomina = pd.read_excel("planilla_coleo.xlsx", sheet_name="PLANILLA_CONTROL", header=2)
        
        # Cargamos cuadros (Resultados)
        # header=1 porque los títulos están en la fila 2
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
    # Verificamos que las columnas existan antes de mostrar nada
    columnas_necesarias = ['CUADRO', 'USUARIO', 'CE', 'CN', 'SP']
    columnas_presentes = [c for c in columnas_necesarias if c in cuadros.columns]
    
    if len(columnas_presentes) < len(columnas_necesarias):
        st.warning(f"⚠️ Faltan columnas en tu hoja CUADROS_PARLAY. Encontré: {cuadros.columns.tolist()}")
    else:
        st.subheader("📊 Tabla de Posiciones (Leaderboard)")
        
        # Quitamos filas vacías y ordenamos
        ranking = cuadros.dropna(subset=['CUADRO']).sort_values(by=['CE', 'CN', 'SP'], ascending=[False, True, False])
        
        st.dataframe(ranking[columnas_necesarias], use_container_width=True)

    # 3. SECCIÓN DE VALIDACIÓN
    st.divider()
    if st.button('🔍 Verificación de Cuadro'):
        st.write("### Selecciona los 4 Coleadores")
        
        nombres_coleadores = nomina['COLEADOR'].dropna().tolist()
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
                ids = sorted([int(ids_coleadores[c1]), int(ids_coleadores[c2]), int(ids_coleadores[c3]), int(ids_coleadores[c4])])
                id_jugada = "-".join(map(str, ids))
                
                # Buscamos en la columna SERIE (o J)
                # Ajustamos según el nombre de tu columna de IDs en Excel
                columna_id = 'SERIE' if 'SERIE' in cuadros.columns else cuadros.columns[9] 
                existe = cuadros[columna_id].astype(str).str.contains(id_jugada).any()

                if existe:
                    st.error(f"❌ CUADRO OCUPADO: La combinación {id_jugada} ya existe.")
                else:
                    st.success(f"✅ DISPONIBLE: Puedes registrar {id_jugada}.")
            except Exception as e:
                st.error(f"Error en validación: {e}")
