import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="FARBEN - Control Litros", layout="wide")

# --- CONFIGURACIÓN DE TU HOJA ---
# REEMPLAZA ESTO CON TU ID DE HOJA
ID_HOJA = "1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU" 

# Estas son las URLs para leer directamente de las pestañas
URL_DATOS = f"https://docs.google.com/spreadsheets/d/1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU/gviz/tq?tqx=out:csv&sheet=DATOS"
URL_BASES = f"https://docs.google.com/spreadsheets/d/1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU/gviz/tq?tqx=out:csv&sheet=BASES"

@st.cache_data(ttl=10)
def load_data():
    try:
        # Cargamos los datos ignorando errores de codificación
        df_q = pd.read_csv(URL_DATOS).fillna(0)
        df_n = pd.read_csv(URL_BASES).fillna("")
        # Limpiar espacios en los nombres
        df_q.columns = df_q.columns.str.strip().str.upper()
        df_n.columns = df_n.columns.str.strip().str.upper()
        return df_q, df_n
    except Exception as e:
        st.error(f"⚠️ Error al conectar: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_q, df_n = load_data()

# --- MENÚ ---
st.sidebar.title("🛠️ FARBEN App")
opcion = st.sidebar.radio("Menú:", ["🔍 Buscador (LITROS)", "➕ Cómo agregar datos"])

if opcion == "🔍 Buscador (LITROS)":
    st.title("🎨 Calculadora de Mezclas (L)")
    busqueda = st.text_input("Código o Nombre del color:").strip().upper()

    if busqueda and not df_q.empty:
        # Buscar en la primera o segunda columna
        mask = (df_q.iloc[:, 0].astype(str).str.contains(busqueda)) | \
               (df_q.iloc[:, 1].astype(str).str.contains(busqueda))
        res = df_q[mask]

        if not res.empty:
            for _, fila in res.iterrows():
                cod = fila.iloc[0]
                nom = fila.iloc[1]
                
                with st.expander(f"📌 {cod} - {nom}", expanded=True):
                    # PREGUNTA POR LITROS
                    litros = st.number_input(f"¿Cuántos Litros (L) preparar?", 0.1, 100.0, 1.0, 0.5, key=f"L_{cod}")
                    
                    st.write(f"**Mezcla final para {litros} Litro(s):**")
                    
                    # Buscar nombres de bases
                    fila_n = df_n[df_n.iloc[:, 0] == cod]
                    
                    cols = st.columns(2)
                    idx = 0
                    # Recorrer las columnas de bases
                    for i in range(1, 18):
                        col_b = f"BASE {i}"
                        if col_b in fila:
                            cant_base = float(str(fila[col_b]).replace(',', '.'))
                            if cant_base > 0:
                                nom_base = fila_n.iloc[0][col_b] if not fila_n.empty else f"B{i}"
                                # CÁLCULO: Base * Litros
                                total = round(cant_base * litros, 3)
                                with cols[idx % 2]:
                                    st.metric(label=f"{nom_base}", value=f"{total} L")
                                idx += 1
        else:
            st.warning("No se encontró ese código.")

elif opcion == "➕ Cómo agregar datos":
    st.title("📝 Agregar Nuevos Colores")
    st.info("Para que el guardado sea **AUTOMÁTICO y GRATIS**, la mejor forma es editar tu Google Sheet desde el celular.")
    
    link_directo = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/edit"
    st.markdown(f"### [👉 Haz clic aquí para abrir tu DB_FARBEN]({link_directo})")
    
    st.write("""
    1. Abre el enlace arriba desde tu celular o PC.
    2. Agrega la nueva fila en la pestaña **DATOS** (las cantidades).
    3. Agrega la misma fila en la pestaña **BASES** (los nombres de las pinturas).
    4. ¡Listo! Vuelve a esta web y el nuevo color aparecerá en segundos.
    """)

