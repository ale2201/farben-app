import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="FARBEN - Sistema Litros", layout="wide")

# CONFIGURACIÓN
ID_HOJA = "1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU" 

URL_DATOS = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/gviz/tq?tqx=out:csv&sheet=DATOS"
URL_BASES = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/gviz/tq?tqx=out:csv&sheet=BASES"

@st.cache_data(ttl=10)
def load_data():
    try:
        df_q = pd.read_csv(URL_DATOS).fillna(0)
        df_n = pd.read_csv(URL_BASES).fillna("")
        df_q.columns = df_q.columns.str.strip().str.upper()
        df_n.columns = df_n.columns.str.strip().str.upper()
        return df_q, df_n
    except Exception as e:
        st.error(f"Error al conectar: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_q, df_n = load_data()

st.title("🎨 Calculadora FARBEN (Litros)")

busqueda = st.text_input("Buscar código o nombre:").strip().upper()

if busqueda and not df_q.empty:
    # Buscamos coincidencias
    mask = (df_q.iloc[:, 0].astype(str).str.contains(busqueda)) | \
           (df_q.iloc[:, 1].astype(str).str.contains(busqueda))
    res = df_q[mask]

    if not res.empty:
        # Usamos 'enumerate' para tener un número de fila (i) y evitar llaves duplicadas
        for i, (idx_fila, fila) in enumerate(res.iterrows()):
            cod = fila.iloc[0]
            nom = fila.iloc[1]
            
            # El secreto está en: key=f"L_{cod}_{i}"
            with st.expander(f"📌 {cod} - {nom}", expanded=True):
                litros_total = st.number_input(
                    f"¿Cuántos Litros (L) preparar?", 
                    min_value=0.1, 
                    max_value=100.0, 
                    value=1.0, 
                    step=0.1, 
                    key=f"L_{cod}_{i}" # <--- ESTO ARREGLA EL ERROR
                )
                
                st.write(f"**Mezcla necesaria para {litros_total} L:**")
                
                # Buscar nombres de bases
                fila_n = df_n[df_n.iloc[:, 0] == cod]
                cols = st.columns(2)
                idx_col = 0
                
                for j in range(1, 18):
                    col_b = f"BASE {j}"
                    if col_b in fila:
                        try:
                            # Convertimos a número y calculamos
                            cant_base_1L = float(str(fila[col_b]).replace(',', '.'))
                        except:
                            cant_base_1L = 0
                            
                        if cant_base_1L > 0:
                            nom_base = fila_n.iloc[0][col_b] if not fila_n.empty else f"B{j}"
                            total_litros = round(cant_base_1L * litros_total, 3)
                            with cols[idx_col % 2]:
                                st.metric(label=f"{nom_base}", value=f"{total_litros} L")
                            idx_col += 1
    else:
        st.warning("No se encontró el color.")

# Sidebar con link directo
st.sidebar.markdown("---")
st.sidebar.markdown(f"### [📂 Abrir Google Sheets](https://docs.google.com/spreadsheets/d/{ID_HOJA}/edit)")
st.sidebar.info("Si agregas un color en el Excel, espera 10 segundos y busca aquí.")
