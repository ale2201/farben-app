import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Calculadora de Mezclas FARBEN", layout="wide")

st.title("🎨 Sistema de Mezclas FARBEN (Calculador)")
st.markdown("Busca tu color y ajusta la cantidad para multiplicar la fórmula automáticamente.")

@st.cache_data
def load_data(file_name):
    try:
        # Detectamos el separador y cargamos con latin-1 para evitar errores de acentos
        df = pd.read_csv(file_name, encoding='latin-1', sep=None, engine='python', on_bad_lines='skip')
        df = df.dropna(how='all')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar {file_name}: {e}")
        return None

# Cargamos los datos
df_q = load_data('datos.csv')
df_n = load_data('bases.csv')

if df_q is not None and df_n is not None:
    # 1. Buscador Principal
    query = st.text_input("🔍 Buscar código o marca:", "").strip().upper()

    if query:
        # Identificamos columnas (ajuste según tus archivos)
        col_cod = 'CÓDIGO' if 'CÓDIGO' in df_q.columns else df_q.columns[0]
        col_nom = 'NOMBRE DEL COLOR' if 'NOMBRE DEL COLOR' in df_q.columns else df_q.columns[1]

        mask = (df_q[col_cod].astype(str).str.contains(query, case=False, na=False)) | \
               (df_q[col_nom].astype(str).str.contains(query, case=False, na=False))
        
        resultados = df_q[mask]

        if not resultados.empty:
            st.write(f"Resultados encontrados: {len(resultados)}")
            
            for _, fila_datos in resultados.iterrows():
                codigo_actual = fila_datos[col_cod]
                nombre_actual = fila_datos[col_nom]
                
                # Cada color es un "acordeón" desplegable
                with st.expander(f"📍 {codigo_actual} - {nombre_actual}"):
                    
                    # --- AQUÍ ESTÁ LA MAGIA DEL MULTIPLICADOR ---
                    st.markdown("#### ⚙️ Ajustar Cantidad")
                    multiplicador = st.number_input(
                        f"Multiplicar mezcla para {codigo_actual}:", 
                        min_value=0.1, 
                        value=1.0, 
                        step=0.5,
                        key=f"mult_{codigo_actual}" # Clave única para que no choque con otros
                    )
                    
                    st.write(f"Mostrando cantidades multiplicadas por: **{multiplicador}**")
                    st.write("---")
                    
                    # Buscamos nombres de las bases
                    fila_nombres = df_n[df_n.iloc[:, 0] == codigo_actual]
                    
                    if not fila_nombres.empty:
                        fn = fila_nombres.iloc[0]
                        cols = st.columns(4)
                        idx_col = 0
                        
                        for i in range(1, 18):
                            col_name = f'BASE {i}'
                            if col_name in fila_datos:
                                val_original = fila_datos[col_name]
                                
                                # Verificamos que sea un número para poder multiplicar
                                try:
                                    # Convertimos a número (flotante)
                                    num_base = float(str(val_original).replace(',', '.'))
                                    if num_base > 0:
                                        nombre_base = fn[col_name] if col_name in fn else f"Base {i}"
                                        
                                        # CALCULAMOS EL NUEVO VALOR
                                        resultado_final = round(num_base * multiplicador, 2)
                                        
                                        with cols[idx_col % 4]:
                                            st.metric(
                                                label=str(nombre_base), 
                                                value=f"{resultado_final} gr",
                                                delta=f"Original: {num_base}" if multiplicador != 1.0 else None
                                            )
                                        idx_col += 1
                                except:
                                    continue
                    else:
                        st.warning("No se encontraron nombres de bases para este código.")
        else:
            st.info("No se encontró el color.")
else:
    st.error("No se pudieron cargar los archivos de datos.")
