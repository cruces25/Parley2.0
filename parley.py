import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Tu Parley Coleo", layout="wide")
st.title("🏆 Portal de Control - Sella Tu Parley")

URL_PLANILLA = "https://docs.google.com/spreadsheets/d/1C52oM3yP47tKJrD2_ryxGkxRPh_lf31m/export?format=xlsx"

@st.cache_data(ttl=30)
def cargar_datos():
    try:
        # Cargamos con los headers que vimos en tus fotos
        nomina = pd.read_excel(URL_PLANILLA, sheet_name="PLANILLA_CONTROL", header=2)
        cuadros = pd.read_excel(URL_PLANILLA, sheet_name="CUADROS_PARLAY", header=1)
        
        # Limpieza de nombres de columnas
        nomina.columns = [str(c).strip() for c in nomina.columns]
        cuadros.columns = [str(c).strip() for c in cuadros.columns]
        
        return nomina, cuadros
    except Exception as e:
        st.error(f"❌ Error leyendo Excel: {e}")
        return None, None

# 2. FUNCIÓN PARA GENERAR EL TICKET (FLYER) - VERSION BLINDADA
def generar_flyer(cuadro_num, usuario, picks):
    try:
        img = Image.open("fondo_flyer.png")
        draw = ImageDraw.Draw(img)
        
        # Fuente básica del servidor
        try:
            fuente = ImageFont.load_default()
        except:
            fuente = None
        
        # Convertimos todo a texto para evitar el error de "scalar variable"
        txt_cuadro = str(cuadro_num)
        txt_usuario = str(usuario)
        
        # --- ESCRIBIMOS LOS DATOS ---
        # Coordenadas ajustadas al molde de Leonardo.ai
        draw.text((435, 335), txt_cuadro, fill="yellow", font=fuente)
        draw.text((320, 425), txt_usuario, fill="white", font=fuente)
        
        y_pos = 585
        for i, p in enumerate(picks, 1):
            txt_pick = str(p) if pd.notna(p) else "Vacio"
            draw.text((300, y_pos), f"{i}. {txt_pick}", fill="white", font=fuente)
            y_pos += 78 
            
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        st.error(f"Error técnico en imagen: {e}")
        return None

# 3. EJECUCIÓN
nomina, cuadros = cargar_datos()

if nomina is not None and cuadros is not None:
    col_cuadro = 'CUADRO #'
    
    # --- RANKING ---
    st.subheader("📊 Tabla de Posiciones (Leaderboard)")
    # Limpiamos filas que no tengan numero de cuadro
    df_ranking = cuadros.dropna(subset=[col_cuadro]).copy()
    
    # Intentamos ordenar, si faltan columnas mostramos aviso
    try:
        df_ranking = df_ranking.sort_values(by=['CE', 'CN', 'SP'], ascending=[False, True, False])
        st.dataframe(df_ranking[[col_cuadro, 'USUARIO', 'CE', 'CN', 'SP']], use_container_width=True, hide_index=True)
    except:
        st.dataframe(df_ranking, use_container_width=True)

    # --- EL "OJITO" (Buscador de Tickets) ---
    st.divider()
    st.subheader("👁️ Ver Ticket de Cuadro")
    
    lista_cuadros = df_ranking[col_cuadro].unique().tolist()
    cuadro_a_ver = st.selectbox("🔎 Selecciona el Nro de Cuadro:", lista_cuadros)

    if cuadro_a_ver:
        # Seleccionamos la fila de forma segura
        fila = df_ranking[df_ranking[col_cuadro] == cuadro_a_ver]
        
        if not fila.empty:
            datos = fila.iloc[0]
            # Extraemos los picks asegurándonos de que existan las columnas
            p1 = datos.get('PICK1', 'N/A')
            p2 = datos.get('PICK2', 'N/A')
            p3 = datos.get('PICK3', 'N/A')
            p4 = datos.get('PICK4', 'N/A')
            
            # Generar imagen con los datos limpios
            ticket_img = generar_flyer(cuadro_a_ver, datos.get('USUARIO', 'Anonimo'), [p1, p2, p3, p4])
            
            if ticket_img:
                st.image(ticket_img, caption=f"Ticket Oficial - Cuadro {cuadro_a_ver}", use_container_width=True)
                st.download_button(label="💾 Descargar para WhatsApp", data=ticket_img, file_name=f"Cuadro_{cuadro_a_ver}.png", mime="image/png")

    # --- VALIDACIÓN DE DISPONIBILIDAD ---
    st.divider()
    st.subheader("🔍 Verificación de Disponibilidad")
    if 'COLEADOR' in nomina.columns and 'NUMERO' in nomina.columns:
        nombres_col = nomina['COLEADOR'].dropna().unique().tolist()
        ids_dict = nomina.set_index('COLEADOR')['NUMERO'].to_dict()

        c1 = st.selectbox("Coleador 1", nombres_col, key="sel1")
        c2 = st.selectbox("Coleador 2", nombres_col, key="sel2")
        c3 = st.selectbox("Coleador 3", nombres_col, key="sel3")
        c4 = st.selectbox("Coleador 4", nombres_col, key="sel4")

        if st.button("Validar Combinación"):
            try:
                # Convertimos IDs a texto para comparar con el SERIAL del excel
                ids = sorted([str(int(ids_dict[c1])), str(int(ids_dict[c2])), str(int(ids_dict[c3])), str(int(ids_dict[c4]))])
                id_jugada = "-".join(ids)
                
                existe = cuadros['SERIAL'].astype(str).str.contains(id_jugada).any()
                if existe:
                    st.error(f"❌ OCUPADO: La combinación {id_jugada} ya existe.")
                else:
                    st.success(f"✅ DISPONIBLE: Combinación {id_jugada} libre.")
            except:
                st.warning("Revisa los números de los coleadores en el Excel.")
