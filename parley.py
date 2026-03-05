import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Tu Parley Coleo", layout="wide")
st.title("🏆 Portal de Control - Sella Tu Parley")

URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1C52oM3yP47tKJrD2_ryxGkxRPh_lf31m/export?format=xlsx"

@st.cache_data(ttl=60)
def cargar_datos():
    try:
        nomina = pd.read_excel(URL_PLANILLA, sheet_name="PLANILLA_CONTROL", header=2)
        cuadros = pd.read_excel(URL_PLANILLA, sheet_name="CUADROS_PARLAY", header=1)
        nomina.columns = [str(c).strip() for c in nomina.columns]
        cuadros.columns = [str(c).strip() for c in cuadros.columns]
        return nomina, cuadros
    except Exception as e:
        st.error(f"❌ Error leyendo Excel: {e}")
        return None, None

# 2. FUNCIÓN PARA GENERAR EL TICKET (FLYER)
def generar_flyer(cuadro_num, usuario, picks):
    try:
        # Abrimos el fondo que subiste a GitHub
        img = Image.open("fondo_flyer.png")
        draw = ImageDraw.Draw(img)
        
        # Intentamos cargar una fuente estándar del servidor
        try:
            # En Linux (Streamlit Cloud) esta suele funcionar
            fuente = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 45)
            fuente_peq = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 35)
        except:
            fuente = ImageFont.load_default()
            fuente_peq = ImageFont.load_default()
        
        # --- ESCRIBIMOS LOS DATOS ---
        # Nro de Cuadro (Amarillo)
        draw.text((435, 335), f"{int(cuadro_num)}", fill="#FFD700", font=fuente)
        # Nombre del Jugador (Blanco)
        draw.text((320, 425), f"{usuario[:20]}", fill="white", font=fuente_peq)
        
        # Los 4 Coleadores
        y_pos = 585
        for i, p in enumerate(picks, 1):
            draw.text((300, y_pos), f"{i}. {str(p)[:25]}", fill="white", font=fuente_peq)
            y_pos += 78 # Espacio entre nombres
            
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        st.error(f"Error al generar imagen: {e}")
        return None

# 3. EJECUCIÓN
nomina, cuadros = cargar_datos()

if nomina is not None and cuadros is not None:
    col_cuadro = 'CUADRO #'
    
    # --- RANKING ---
    st.subheader("📊 Tabla de Posiciones (Leaderboard)")
    df_ranking = cuadros.dropna(subset=[col_cuadro]).copy()
    # Ordenar por Puntos, Nulas y SP
    df_ranking = df_ranking.sort_values(by=['CE', 'CN', 'SP'], ascending=[False, True, False])
    
    st.dataframe(df_ranking[[col_cuadro, 'USUARIO', 'CE', 'CN', 'SP']], use_container_width=True, hide_index=True)

    # --- EL "OJITO" (Buscador de Tickets) ---
    st.divider()
    st.subheader("👁️ Ver Ticket de Cuadro")
    
    # Lista de cuadros para el buscador
    lista_cuadros = df_ranking[col_cuadro].unique().tolist()
    cuadro_a_ver = st.selectbox("🔎 Selecciona o escribe el Nro de Cuadro para ver el ticket:", lista_cuadros)

    if cuadro_a_ver:
        # Buscamos los datos del cuadro elegido
        datos = df_ranking[df_ranking[col_cuadro] == cuadro_a_ver].iloc[0]
        picks_cuadro = [datos['PICK1'], datos['PICK2'], datos['PICK3'], datos['PICK4']]
        
        # Generar imagen
        ticket_img = generar_flyer(cuadro_a_ver, datos['USUARIO'], picks_cuadro)
        
        if ticket_img:
            st.image(ticket_img, caption=f"Ticket Oficial - Cuadro {cuadro_a_ver}", use_container_width=True)
            st.download_button(
                label="💾 Descargar para WhatsApp",
                data=ticket_img,
                file_name=f"Ticket_Cuadro_{cuadro_a_ver}.png",
                mime="image/png"
            )

    # --- VALIDACIÓN DE DISPONIBILIDAD ---
    st.divider()
    st.subheader("🔍 Verificación de Disponibilidad")
    nombres_coleadores = nomina['COLEADOR'].dropna().unique().tolist()
    ids_dict = nomina.set_index('COLEADOR')['NUMERO'].to_dict()

    c1 = st.selectbox("Coleador 1", nombres_coleadores, key="sel1")
    c2 = st.selectbox("Coleador 2", nombres_coleadores, key="sel2")
    c3 = st.selectbox("Coleador 3", nombres_coleadores, key="sel3")
    c4 = st.selectbox("Coleador 4", nombres_coleadores, key="sel4")

    if st.button("Validar Combinación"):
        try:
            ids = sorted([int(ids_dict[c1]), int(ids_dict[c2]), int(ids_dict[c3]), int(ids_dict[c4])])
            id_jugada = "-".join(map(str, ids))
            
            # Chequeamos en la columna SERIAL
            existe = cuadros['SERIAL'].astype(str).str.contains(id_jugada).any()
            if existe:
                st.error(f"❌ OCUPADO: La combinación {id_jugada} ya fue vendida.")
            else:
                st.success(f"✅ DISPONIBLE: Puedes vender la combinación {id_jugada}.")
        except:
            st.warning("Verifica que los coleadores seleccionados tengan número asignado en el Excel.")
