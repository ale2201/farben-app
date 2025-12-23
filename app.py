import streamlit as st
import pandas as pd

# Configuración profesional
st.set_page_config(page_title="FARBEN - Sistema de Mezclas", layout="wide")

# 1. TU ID DE HOJA (Verificado)
ID_HOJA = "1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU" 

URL_DATOS = f"https://docs.google.com/spreadsheets/d/1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU/gviz/tq?tqx=out:csv&sheet=DATOS"
URL_BASES = f"https://docs.google.com/spreadsheets/d/1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU/gviz/tq?tqx=out:csv&sheet=BASES"

@st.cache_data(ttl=5)
def load_data():
    try:
        # Cargamos los datos forzando que todo sea texto al inicio para no perder decimales
        df_q = pd.read_csv(URL_DATOS, dtype=str).fillna("0")
        df_n = pd.read_csv(URL_BASES, dtype=str).fillna("")
        return df_q, df_n
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_q, df_n = load_data()

st.title("🎨 Sistema FARBEN - Mezclas en Litros")

# --- BUSCADOR ---
busqueda = st.text_input("🔍 Busca por Código (ej: ZMT) o Nombre:").strip().upper()

if busqueda and not df_q.empty:
    # Buscamos en la Columna 0 (CÓDIGO) o Columna 1 (NOMBRE)
    mask = (df_q.iloc[:, 0].str.contains(busqueda, na=False, case=False)) | \
           (df_q.iloc[:, 1].str.contains(busqueda, na=False, case=False))
    
    resultados = df_q[mask]

    if not resultados.empty:
        for i, (idx, fila_datos) in enumerate(resultados.iterrows()):
            # Usamos el CÓDIGO exacto (Columna 0) para unir las dos tablas
            codigo_principal = str(fila_datos.iloc[0]).strip()
            nombre_color = str(fila_datos.iloc[1]).strip()
            
            with st.expander(f"📍 {codigo_principal} - {nombre_color}", expanded=True):
                # Selector de Litros
                litros_total = st.number_input(
                    f"¿Cuántos Litros quieres preparar?", 
                    min_value=0.01, max_value=100.0, value=1.0, step=0.1, 
                    key=f"L_{idx}_{i}"
                )
                
                # Buscamos la fila de nombres en BASES que coincida exactamente con el CÓDIGO principal
                fila_nombres = df_n[df_n.iloc[:, 0].str.strip() == codigo_principal]
                
                st.write(f"**Fórmula para {litros_total} L:**")
                
                cols = st.columns(2)
                item_idx = 0
                
                # Las bases y cantidades SIEMPRE empiezan en la columna índice 3 (Base 1)
                for col_idx in range(3, len(fila_datos)):
                    # 1. Obtener cantidad y limpiar coma/punto
                    dato_cantidad = str(fila_datos.iloc[col_idx]).replace(',', '.')
                    
                    try:
                        cant_base_1L = float(dato_cantidad)
                    except ValueError:
                        cant_base_1L = 0.0
                    
                    if cant_base_1L > 0:
                        # 2. Obtener nombre real de la base desde la tabla BASES
                        nombre_base_real = f"Base {col_idx-2}"
                        if not fila_nombres.empty:
                            nombre_base_real = str(fila_nombres.iloc[0].iloc[col_idx]).strip()
                        
                        # Si por alguna razón el nombre está vacío en BASES
                        if nombre_base_real == "" or nombre_base_real == "0":
                            nombre_base_real = f"Base {col_idx-2}"

                        # 3. Calcular cantidad final
                        cantidad_final = round(cant_base_1L * litros_total, 3)
                        
                        with cols[item_idx % 2]:
                            st.metric(label=nombre_base_real, value=f"{cantidad_final} L")
                        item_idx += 1
                
                if item_idx == 0:
                    st.warning("No se encontraron bases con cantidades para este código.")
    else:
        st.warning("No se encontró el color en la base de datos.")

# Sidebar
st.sidebar.markdown(f"### [📂 Abrir Google Sheets](https://docs.google.com/spreadsheets/d/{ID_HOJA}/edit)")
st.sidebar.info("Asegúrate de que 'ZMT' esté escrito igual en la columna 0 de ambas hojas (DATOS y BASES).")
