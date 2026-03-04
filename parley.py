
import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Tu Parley Coleo", layout="wide")

# Título y Logo
st.title("🏆 Portal de Control - Copa Cheo Hernández Prisco")

# 1. CARGA DE DATOS
@st.cache_data
def cargar_datos():
    # Cargamos las hojas del Excel
    nomina = pd.read_excel("planilla_coleo.xlsx", sheet_name="PLANILLA_CONTROL")
    cuadros = pd.read_excel("planilla_coleo.xlsx", sheet_name="CUADROS_PARLAY")
    return nomina, cuadros

nomina, cuadros = cargar_datos()

# 2. SECCIÓN DE RANKING (Imagen 1 de tu competencia)
st.subheader("📊 Tabla de Posiciones (Leaderboard)")

# Ordenamos según tus criterios de desempate
ranking = cuadros.sort_values(by=['CE', 'CN', 'SP'], ascending=[False, True, False])

# Mostramos la tabla profesional
st.dataframe(ranking[['CUADRO', 'USUARIO', 'CE', 'CN', 'SP']], use_container_width=True)

# 3. BOTÓN DE VERIFICACIÓN (Imagen 2 de tu competencia)
st.divider()
if st.button('🔍 Verificación de Cuadro'):
    with st.expander("Panel de Validación", expanded=True):
        st.write("### Selecciona los 4 Coleadores")
        
        # Listas de nombres de la planilla de control
        nombres_coleadores = nomina['COLEADOR'].tolist()
        ids_coleadores = nomina.set_index('COLEADOR')['NUMERO'].to_dict()

        col1, col2 = st.columns(2)
        with col1:
            c1 = st.selectbox("Coleador 1", nombres_coleadores)
            c2 = st.selectbox("Coleador 2", nombres_coleadores)
        with col2:
            c3 = st.selectbox("Coleador 3", nombres_coleadores)
            c4 = st.selectbox("Coleador 4", nombres_coleadores)

        if st.button("Validar Disponibilidad"):
            # Obtenemos los IDs y los ordenamos para que el orden no importe
            selección_ids = sorted([ids_coleadores[c1], ids_coleadores[c2], ids_coleadores[c3], ids_coleadores[c4]])
            id_jugada = "-".join(map(str, selección_ids))

            # Revisamos si ese ID ya existe en la columna J del Excel
            # (Asumiendo que la columna J en el Excel se llama 'ID_JUGADA')
            existe = cuadros['ID_JUGADA'].astype(str).str.contains(id_jugada).any()

            if existe:
                st.error(f"❌ CUADRO OCUPADO: La combinación {id_jugada} ya fue vendida.")
            else:
                st.success(f"✅ CUADRO DISPONIBLE: Puedes registrar la combinación {id_jugada}.")
