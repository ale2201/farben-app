import streamlit as st
import pandas as pd

# Configuración para que se vea perfecto en el celular
st.set_page_config(page_title="FARBEN - Sistema de Mezclas", layout="wide")

# 1. TU ID DE GOOGLE SHEETS (Verificado)
ID_HOJA = "1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU" 

# Enlaces de lectura para las dos pestañas
URL_DATOS = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/gviz/tq?tqx=out:csv&sheet=DATOS"
URL_BASES = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/gviz/tq?tqx=out:csv&sheet=BASES"

@st.cache_data(ttl=5) # Actualiza cada 5 segundos si hay cambios en Google Sheets
def load_data():
    try:
        # Cargamos todo como texto para evitar que se pierdan ceros o decimales
        df_q = pd.read_csv(URL_DATOS, dtype=str).fillna("0") # Cantidades
        df_n = pd.read_csv(URL_BASES, dtype=str).fillna("")  # Nombres de bases
        return df_q, df_n
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_q, df_n = load_data()

st.title("🎨 Sistema FARBEN")
st.write("Mezclas calculadas en **Litros (L)**")

# --- BUSCADOR ---
busqueda = st.text_input("🔍 Buscar por Código o Color (ej: ZMT, 042, TOYOTA):").strip().upper()

if busqueda and not df_q.empty:
    # El programa busca en la primera (COLOR) y segunda columna (CODIGO)
    mask = (df_q.iloc[:, 0].str.contains(busqueda, na=False, case=False)) | \
           (df_q.iloc[:, 1].str.contains(busqueda, na=False, case=False))
    
    resultados = df_q[mask]

    if not resultados.empty:
        for i, (idx, fila_q) in enumerate(resultados.iterrows()):
            # Usamos el nombre de la primera columna para vincular las dos tablas
            id_vinculo = str(fila_q.iloc[0]).strip()
            nombre_tabla = str(fila_q.iloc[1]).strip()
            
            with st.expander(f"📍 {id_vinculo} - {nombre_tabla}", expanded=True):
                # Selector de Litros
                litros = st.number_input(f"¿Cuántos Litros preparar?", 0.01, 100.0, 1.0, 0.1, key=f"L_{idx}_{i}")
                
                # Buscamos la fila de nombres en la hoja BASES que coincida con el nombre de la columna COLOR
                fila_n = df_n[df_n.iloc[:, 0].str.strip() == id_vinculo]
                
                st.write(f"#### Mezcla para {litros} L:")
                
                # Diseño de tarjetas para celular (2 columnas)
                cols = st.columns(2)
                item_idx = 0
                
                # Las bases siempre empiezan en la columna 3 (después de Color, Código y Tipo)
                for col_idx in range(3, len(fila_q)):
                    # 1. Obtenemos la cantidad de la hoja DATOS
                    cantidad_texto = str(fila_q.iloc[col_idx]).replace(',', '.')
                    try:
                        cant_1L = float(cantidad_texto)
                    except:
                        cant_1L = 0.0
                    
                    # 2. SOLO SI LA CANTIDAD ES MAYOR A 0, buscamos el nombre y mostramos
                    if cant_1L > 0:
                        # Buscamos el nombre de la base en la hoja BASES en la misma columna
                        nombre_base = f"Base {col_idx-2}" # Nombre de seguridad
                        
                        if not fila_n.empty:
                            nombre_temp = str(fila_n.iloc[0].iloc[col_idx]).strip()
                            # Si el nombre no está vacío, lo usamos
                            if nombre_temp != "" and nombre_temp != "0":
                                nombre_base = nombre_temp
                        
                        # 3. Calcular total (Cantidad x Litros seleccionados)
                        total_final = round(cant_1L * litros, 3)
                        
                        # Mostrar en pantalla con diseño de tarjeta
                        with cols[item_idx % 2]:
                            st.metric(label=nombre_base, value=f"{total_final} L")
                        item_idx += 1
                
                if item_idx == 0:
                    st.warning("Este color no tiene mezcla registrada en la base de datos.")
    else:
        st.warning("No se encontró ningún resultado para esa búsqueda.")

# Sidebar
st.sidebar.markdown(f"### [📂 Abrir Google Sheets](https://docs.google.com/spreadsheets/d/{ID_HOJA}/edit)")
st.sidebar.info("La web se actualiza sola. Solo edita el Excel y espera 5 segundos.")
