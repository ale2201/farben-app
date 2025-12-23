import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página
st.set_page_config(page_title="FARBEN - Sistema Litros", layout="wide")

# URL de tu Google Sheet (REEMPLAZA ESTO CON TU LINK)
url = "https://docs.google.com/spreadsheets/d/1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU/edit?usp=sharing"

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5) # Se actualiza cada 5 segundos
def load_data():
    df_q = conn.read(spreadsheet=url, worksheet="DATOS")
    df_n = conn.read(spreadsheet=url, worksheet="BASES")
    return df_q.fillna(0), df_n.fillna("")

df_q, df_n = load_data()

# --- MENÚ ---
menu = st.sidebar.radio("Menú", ["🔍 Buscador (L)", "➕ Agregar Nuevo"])

if menu == "🔍 Buscador (L)":
    st.title("🎨 Buscador en Litros")
    query = st.text_input("Buscar código o color:").strip().upper()

    if query:
        # Buscador flexible
        mask = (df_q.iloc[:, 0].astype(str).str.contains(query)) | (df_q.iloc[:, 1].astype(str).str.contains(query))
        res = df_q[mask]

        for _, fila in res.iterrows():
            with st.expander(f"📍 {fila.iloc[0]} - {fila.iloc[1]}"):
                # El multiplicador ahora representa CUÁNTOS LITROS quieres preparar
                cant_litros = st.number_input(f"¿Cuántos Litros quieres preparar?", 0.1, 100.0, 1.0, 0.5, key=f"L_{fila.iloc[0]}")
                
                st.write(f"### Mezcla para {cant_litros} L")
                
                # Buscamos nombres de bases
                fila_n = df_n[df_n.iloc[:, 0] == fila.iloc[0]]
                
                cols = st.columns(2)
                idx = 0
                for i in range(1, 18):
                    col_name = f"BASE {i}"
                    val_base = float(str(fila[col_name]).replace(',', '.'))
                    
                    if val_base > 0:
                        nombre_b = fila_n.iloc[0][col_name] if not fila_n.empty else f"Base {i}"
                        # CÁLCULO EN LITROS
                        resultado = round(val_base * cant_litros, 3)
                        
                        with cols[idx % 2]:
                            st.metric(label=f"{nombre_b}", value=f"{resultado} L")
                        idx += 1

elif menu == "➕ Agregar Nuevo":
    st.title("📝 Agregar y Guardar Automático")
    
    with st.form("form_registro"):
        st.subheader("1. Datos del Color")
        c1, c2 = st.columns(2)
        nuevo_cod = c1.text_input("Código")
        nuevo_nom = c2.text_input("Nombre")
        
        st.subheader("2. Bases y Cantidades (por cada 1 Litro)")
        st.info("Ingresa la cantidad base para 1 Litro. El sistema calculará el resto.")
        
        nuevos_datos = {}
        nuevos_nombres = {}
        
        for i in range(1, 11): # Primeras 10 bases
            col1, col2 = st.columns([2, 1])
            nb = col1.text_input(f"Nombre Base {i}", key=f"nb_{i}")
            cb = col2.number_input(f"Litros {i}", 0.0, 10.0, 0.0, format="%.3f", key=f"cb_{i}")
            nuevos_nombres[f"BASE {i}"] = nb
            nuevos_datos[f"BASE {i}"] = cb

        if st.form_submit_button("💾 GUARDAR TODO AUTOMÁTICAMENTE"):
            if nuevo_cod:
                # Crear nuevas filas
                new_q_row = pd.DataFrame([{**{df_q.columns[0]: nuevo_cod, df_q.columns[1]: nuevo_nom}, **nuevos_datos}])
                new_n_row = pd.DataFrame([{**{df_n.columns[0]: nuevo_cod, df_n.columns[1]: nuevo_nom}, **nuevos_nombres}])
                
                # Unir y Guardar en Google Sheets
                df_q_updated = pd.concat([df_q, new_q_row], ignore_index=True)
                df_n_updated = pd.concat([df_n, new_n_row], ignore_index=True)
                
                conn.update(spreadsheet=url, worksheet="DATOS", data=df_q_updated)
                conn.update(spreadsheet=url, worksheet="BASES", data=df_n_updated)
                
                st.success("✅ ¡Guardado en Google Sheets con éxito! Ya puedes buscarlo.")
                st.cache_data.clear()
            else:
                st.error("Falta el código del color.")
