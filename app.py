import streamlit as st
import pandas as pd

# Configuración para que se vea bien en celulares
st.set_page_config(page_title="FARBEN - Calculadora de Mezclas", layout="wide")

# 1. TU ID DE GOOGLE SHEETS (Verificado)
ID_HOJA = "1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU" 

# Enlaces directos a las pestañas
URL_DATOS = f"https://docs.google.com/spreadsheets/d/1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU/gviz/tq?tqx=out:csv&sheet=DATOS"
URL_BASES = f"https://docs.google.com/spreadsheets/d/1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU/gviz/tq?tqx=out:csv&sheet=BASES"

@st.cache_data(ttl=5)
def load_data():
    try:
        # Cargamos los datos como texto para evitar errores de formato
        df_q = pd.read_csv(URL_DATOS, dtype=str).fillna("0")
        df_n = pd.read_csv(URL_BASES, dtype=str).fillna("")
        return df_q, df_n
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_q, df_n = load_data()

st.title("🎨 Sistema FARBEN")
st.write("Mezclas calculadas según la cantidad de Litros.")

# --- BUSCADOR ---
busqueda = st.text_input("🔍 Buscar código o marca (ej: ZMT, TOYOTA, 042):").strip().upper()

if busqueda and not df_q.empty:
    # Buscamos en la Columna 0 (Código largo) o Columna 1 (Código corto/Nombre)
    mask = (df_q.iloc[:, 0].str.contains(busqueda, na=False, case=False)) | \
           (df_q.iloc[:, 1].str.contains(busqueda, na=False, case=False))
    
    resultados = df_q[mask]

    if not resultados.empty:
        for i, (idx, fila_q) in enumerate(resultados.iterrows()):
            # Obtenemos el ID de vinculación (Columna 0)
            id_vinculo = str(fila_q.iloc[0]).strip()
            nombre_color = str(fila_q.iloc[1]).strip()
            
            with st.expander(f"📍 {id_vinculo} - {nombre_color}", expanded=True):
                # Selector de Litros
                litros = st.number_input(f"¿Cuántos Litros preparar?", 0.01, 100.0, 1.0, 0.1, key=f"L_{idx}_{i}")
                
                # Buscamos la fila de nombres en la hoja BASES que coincida con el ID
                fila_n = df_n[df_n.iloc[:, 0].str.strip() == id_vinculo]
                
                st.write(f"**Mezcla para {litros} L:**")
                st.write("---")
                
                # Rejilla de resultados (2 columnas para celular)
                cols = st.columns(2)
                item_idx = 0
                
                # Recorremos desde la columna 3 (donde empiezan las Bases) hasta la 20
                for col_idx in range(3, len(fila_q)):
                    # A. Sacar la cantidad de la hoja DATOS
                    valor_cantidad = str(fila_q.iloc[col_idx]).replace(',', '.')
                    try:
                        cant_float = float(valor_cantidad)
                    except:
                        cant_float = 0.0
                    
                    # B. Solo si la cantidad es mayor a 0, buscamos el nombre y mostramos
                    if cant_float > 0:
                        # Buscamos el nombre en la hoja BASES en la misma columna
                        nombre_base = f"Base {col_idx-2}" # Nombre de respaldo
                        if not fila_n.empty:
                            nombre_temp = str(fila_n.iloc[0].iloc[col_idx]).strip()
                            if nombre_temp != "" and nombre_temp != "0":
                                nombre_base = nombre_temp
                        
                        # C. Calcular total
                        total_calculado = round(cant_float * litros, 3)
                        
                        # Mostrar en pantalla
                        with cols[item_idx % 2]:
                            st.metric(label=nombre_base, value=f"{total_calculado} L")
                        item_idx += 1
                
                if item_idx == 0:
                    st.warning("No se encontraron bases con cantidades para este color.")
    else:
        st.warning("No se encontró el color.")

# Sidebar
st.sidebar.markdown(f"### [📂 Abrir Google Sheets](https://docs.google.com/spreadsheets/d/{ID_HOJA}/edit)")
st.sidebar.info("La web se actualiza automáticamente cada 5 segundos después de que guardes en el Excel.")
