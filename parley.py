import streamlit as st
import pandas as pd
import os

# Configuración de la página
st.set_page_config(page_title="Tu Parley Coleo", layout="wide")

# Título y Logo
st.title("🏆 Portal de Control - Sella Tu Parley")

# 1. CARGA DE DATOS
@st.cache_data
def cargar_datos():
    # Estas líneas deben tener exactamente 4 espacios de sangría
    try:
        nomina = pd.read_excel("planilla_coleo.xlsx", sheet_name="PLANILLA_CONTROL")
        cuadros = pd.read_excel("planilla_coleo.xlsx", sheet_name="CUADROS_PARLAY")
        return nomina, cuadros
    except FileNotFoundError:
        st.error("❌ No encontré el archivo 'planilla_coleo.xlsx'. Verifica que esté subido a GitHub con ese nombre exacto.")
        st.write("Archivos en el servidor:", os.listdir("."))
        return None, None

nomina, cuadros = cargar_datos()

# Solo ejecutamos el resto si los datos cargaron bien
if nomina is not None and cuadros is not None:
    
    # 2. SECCIÓN DE RANKING
    st.subheader("📊 Tabla de Posiciones (Leaderboard)")

    # Ordenamos según criterios de desempate (Puntos, Nulas, SP)
    # Nota: Asegúrate que estas columnas existan en tu hoja CUADROS_PARLAY
    ranking = cuadros.sort_values(by=['CE', 'CN', 'SP'], ascending=[False, True, False])

    # Mostramos la tabla profesional
    st.dataframe(ranking[['CUADRO', 'USUARIO', 'CE', 'CN', 'SP']], use_container_width=True)

    # 3. BOTÓN DE VERIFICACIÓN
    st.divider()
    if st.button('🔍 Verificación de Cuadro'):
        st.write("### Selecciona los 4 Coleadores")
        
        # Listas de nombres de la planilla de control
        nombres_coleadores = nomina['COLEADOR'].tolist()
        # Creamos diccionario para buscar el número por el nombre
        ids_coleadores = nomina.set_index('COLEADOR')['NUMERO'].to_dict()

        col1, col2 = st.columns(2)
        with col1:
            c1 = st.selectbox("Coleador 1", nombres_coleadores, key="c1")
            c2 = st.selectbox("Coleador 2", nombres_coleadores, key="c2")
        with col2:
            c3 = st.selectbox("Coleador 3", nombres_coleadores, key="c3")
            c4 = st.selectbox("Coleador 4", nombres_coleadores, key="c4")

        if st.button("Validar Disponibilidad"):
            # Obtenemos los IDs y los ordenamos para que el orden no importe
            ids_seleccionados = sorted([ids_coleadores[c1], ids_coleadores[c2], ids_coleadores[c3], ids_coleadores[c4]])
            id_jugada = "-".join(map(str, ids_seleccionados))

            # Revisamos si ese ID ya existe en la columna J (ID_JUGADA)
            existe = cuadros['SERIE'].astype(str).str.contains(id_jugada).any()

            if existe:
                st.error(f"❌ CUADRO OCUPADO: La combinación {id_jugada} ya fue vendida.")
            else:
                st.success(f"✅ CUADRO DISPONIBLE: Puedes registrar la combinación {id_jugada}.")
