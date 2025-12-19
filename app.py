import streamlit as st
import pandas as pd

# Configuración visual
st.set_page_config(page_title="FARBEN - Base de Datos de Colores", layout="centered")

st.title("🎨 Buscador de Fórmulas FARBEN")
st.info("Escribe el nombre o código del color abajo. Haz clic en el resultado para ver la mezcla.")

# Función para cargar y limpiar datos
# Función para cargar y limpiar datos corregida
@st.cache_data
def load_data():
    # Agregamos encoding='latin-1' para que no de error con los acentos
    df_cantidades = pd.read_csv('datos.csv', encoding='latin-1')
    df_nombres = pd.read_csv('bases.csv', encoding='latin-1')
    
    # Limpieza básica: quitar espacios en blanco de los nombres de columnas
    df_cantidades.columns = df_cantidades.columns.str.strip()
    df_nombres.columns = df_nombres.columns.str.strip()
    
    return df_cantidades, df_nombres

try:
    df_q, df_n = load_data()

    # Buscador central
    query = st.text_input("🔍 Buscar color (ej: TOYOTA, 042, NISSAN...)", "").strip().upper()

    if query:
        # Buscamos en las columnas de CÓDIGO y NOMBRE DEL COLOR
        mask = (df_q['CÓDIGO'].astype(str).str.contains(query, case=False, na=False)) | \
               (df_q['NOMBRE DEL COLOR'].astype(str).str.contains(query, case=False, na=False))
        
        resultados = df_q[mask]

        if not resultados.empty:
            st.write(f"Se encontraron **{len(resultados)}** resultados:")
            
            # Crear un desplegable por cada resultado encontrado
            for index, fila_datos in resultados.iterrows():
                # Título del desplegable: Código + Nombre
                titulo = f"📌 {fila_datos['CÓDIGO']} - {fila_datos['NOMBRE DEL COLOR']}"
                
                with st.expander(titulo):
                    st.markdown(f"**Tipo de Pintura:** {fila_datos['TIPO DE PINTURA']}")
                    st.write("---")
                    
                    # Buscamos la fila correspondiente en el archivo de BASES (nombres)
                    # Usamos el 'CÓDIGO' de DATOS para buscar en 'COLOR' de BASES
                    fila_nombres = df_n[df_n['COLOR'] == fila_datos['CÓDIGO']]
                    
                    if not fila_nombres.empty:
                        fn = fila_nombres.iloc[0]
                        
                        # Creamos columnas para que la lista de bases se vea ordenada
                        col1, col2 = st.columns(2)
                        
                        # Recorremos las 17 bases posibles
                        for i in range(1, 18):
                            col_name = f'BASE {i}'
                            nombre_base = fn[col_name]
                            cantidad = fila_datos[col_name]
                            
                            # Solo mostrar si hay una cantidad válida (distinta de cero o vacía)
                            if pd.notna(cantidad) and str(cantidad).strip() not in ["0", "0.0", "", "nan"]:
                                target_col = col1 if i % 2 != 0 else col2
                                target_col.markdown(f"**{nombre_base}:** `{cantidad}`")
                    else:
                        st.error("No se encontró la definición de nombres para este código.")
        else:
            st.warning("No se encontró ningún color con ese nombre o código.")
    else:
        st.write("Introduce un término para comenzar la búsqueda.")

except Exception as e:
    st.error(f"Error técnico: {e}")

    st.info("Revisa que los archivos 'datos.csv' y 'bases.csv' estén correctamente subidos a GitHub.")
