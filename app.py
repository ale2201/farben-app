import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="FARBEN - Fórmulas de Pintura", layout="wide")

st.title("🎨 Buscador de Mezclas FARBEN")
st.markdown("Busca un color y haz clic para ver las bases y cantidades.")

@st.cache_data
def load_data(file_name):
    try:
        # Intentamos detectar el separador (sep=None hace que pandas lo adivine)
        df = pd.read_csv(file_name, encoding='latin-1', sep=None, engine='python', on_bad_lines='skip')
        # Limpiamos filas que estén totalmente vacías
        df = df.dropna(how='all')
        # Quitamos espacios en los nombres de las columnas
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar {file_name}: {e}")
        return None

# Cargamos los datos
df_q = load_data('datos.csv')
df_n = load_data('bases.csv')

if df_q is not None and df_n is not None:
    # Buscador
    query = st.text_input("🔍 Escribe el código, marca o color:", "").strip().upper()

    if query:
        # Buscamos en las columnas principales (CÓDIGO o NOMBRE)
        # Ajustamos los nombres de columnas según tus archivos
        col_busqueda = 'CÓDIGO' if 'CÓDIGO' in df_q.columns else df_q.columns[0]
        col_nombre = 'NOMBRE DEL COLOR' if 'NOMBRE DEL COLOR' in df_q.columns else df_q.columns[1]

        mask = (df_q[col_busqueda].astype(str).str.contains(query, case=False, na=False)) | \
               (df_q[col_nombre].astype(str).str.contains(query, case=False, na=False))
        
        resultados = df_q[mask]

        if not resultados.empty:
            st.write(f"Se encontraron **{len(resultados)}** coincidencias:")
            
            for _, fila_datos in resultados.iterrows():
                cod = fila_datos[col_busqueda]
                nom = fila_datos[col_nombre]
                
                # Crear el acordeón (clic para ver)
                with st.expander(f"📍 {cod} - {nom}"):
                    st.write("**Detalles de la mezcla:**")
                    
                    # Buscamos los nombres de las bases en el otro archivo
                    # En bases.csv la columna se llama 'COLOR'
                    fila_nombres = df_n[df_n.iloc[:, 0] == cod]
                    
                    if not fila_nombres.empty:
                        fn = fila_nombres.iloc[0]
                        
                        # Mostrar en columnas bonitas
                        cols = st.columns(4)
                        idx_col = 0
                        
                        for i in range(1, 18):
                            col_name = f'BASE {i}'
                            if col_name in fila_datos:
                                cant = fila_datos[col_name]
                                nom_base = fn[col_name] if col_name in fn else f"Base {i}"
                                
                                # Solo mostrar si hay cantidad
                                if pd.notna(cant) and str(cant).strip() not in ["0", "0.0", "", "nan"]:
                                    with cols[idx_col % 4]:
                                        st.metric(label=str(nom_base), value=str(cant))
                                    idx_col += 1
                    else:
                        st.warning("No se encontraron los nombres de las bases para este código.")
        else:
            st.info("No se encontraron resultados.")
else:
    st.warning("Por favor, asegúrate de que 'datos.csv' y 'bases.csv' estén en el repositorio.")
