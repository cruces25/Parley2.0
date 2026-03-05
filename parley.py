import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import requests

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
        st.error(f"❌ Error: {e}")
        return None, None

# 2. FUNCIÓN PARA GENERAR EL FLYER
def generar_flyer(cuadro_num, usuario, picks):
    try:
        img = Image.open("fondo_flyer.png")
        draw = ImageDraw.Draw(img)
        # Usamos fuente por defecto (puedes subir una .ttf a GitHub para que sea más bonita)
        f_titulo = ImageFont.load_default() 
        
        # --- ESCRIBIMOS DATOS (Ajusta X, Y según tu imagen) ---
        draw.text((430, 320), f"{int(cuadro_num)}", fill="yellow", font=f_titulo) # Nro Cuadro
        draw.text((350, 420), f"{usuario}", fill="white", font=f_titulo)       # Nombre Jugador
        
        y = 580
        for i, p in enumerate(picks, 1):
            draw.text((320, y), f"{i}. {p}", fill="white", font=f_titulo)
            y += 75 # Espaciado hacia abajo
            
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        return None

# 3. EJECUCIÓN DEL PORTAL
nomina, cuadros = cargar_datos()

if nomina is not None and cuadros is not None:
    col_cuadro = 'CUADRO #'
    
    # Preparamos la tabla de posiciones
    df_ranking = cuadros.dropna(subset=[col_cuadro]).copy()
    
    # Añadimos la columna del "Ojito" visualmente
    df_ranking['Ver Cuadro'] = "👁️ Ver Ticket"

    st.subheader("📊 Tabla de Posiciones (Leaderboard)")
    
    # CONFIGURACIÓN DE LA TABLA INTERACTIVA
    # Al hacer clic en una fila, se seleccionará ese cuadro
    evento_seleccion = st.dataframe(
        df_ranking[[col_cuadro, 'USUARIO', 'CE', 'CN', 'SP', 'Ver Cuadro']],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single"
    )

    # 4. MOSTRAR EL FLYER AL SELECCIONAR UNA FILA (El efecto del "Ojo")
    seleccion = evento_seleccion.selection.rows
    if seleccion:
        fila_index = seleccion[0]
        datos_fila = df_ranking.iloc[fila_index]
        
        with st.expander(f"📥 Ticket del Cuadro {datos_fila[col_cuadro]}", expanded=True):
            # Buscamos los picks del cuadro seleccionado
            picks_cuadro = [str(datos_fila['PICK1']), str(datos_fila['PICK2']), str(datos_fila['PICK3']), str(datos_fila['PICK4'])]
            
            # Generamos la imagen
            img_bin = generar_flyer(datos_fila[col_cuadro], datos_fila['USUARIO'], picks_cuadro)
            
            if img_bin:
                st.image(img_bin, use_container_width=True)
                st.download_button(
                    label="💾 Descargar Imagen para WhatsApp",
                    data=img_bin,
                    file_name=f"Ticket_Cuadro_{datos_fila[col_cuadro]}.png",
                    mime="image/png"
                )

    # 5. VALIDACIÓN DE DISPONIBILIDAD (Abajo del ranking)
    st.divider()
    st.write("### 🔍 Verificación de Cuadro")
    # ... (Aquí va tu código de selectboxes para validar disponibilidad que ya teníamos)
