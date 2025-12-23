import streamlit as st
import pandas as pd

# Configuración visual para móvil
st.set_page_config(page_title="FARBEN - Sistema Litros", layout="wide")

# 1. TU ID DE GOOGLE SHEETS
ID_HOJA = "1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU" 

URL_DATOS = f"https://docs.google.com/spreadsheets/d/1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU/gviz/tq?tqx=out:csv&sheet=DATOS"
URL_BASES = f"https://docs.google.com/spreadsheets/d/1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU/gviz/tq?tqx=out:csv&sheet=BASES"

@st.cache_data(ttl=10)
def load_data():
    try:
        # Cargamos los datos
        df_q = pd.read_csv(URL_DATOS)
        df_n = pd.read_csv(URL_BASES)
        
        # Limpiamos nombres de columnas (quitar espacios y poner mayúsculas)
        df_q.columns = [str(c).strip().upper() for c in df_q.columns]
        df_n.columns = [str(c).strip().upper() for c in df_n.columns]
        
        return df_q.fillna(0), df_n.fillna("")
    except Exception as e:
        st.error(f"Error al conectar con Google: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_q, df_n = load_data()

st.title("🎨 Sistema de Mezclas FARBEN")
st.write("Cálculo automático en **Litros (L)**")

# 2. BUSCADOR
busqueda = st.text_input("🔍 Escribe el Código o Nombre (ej: TOYOTA, 042, NAVAL):").strip().upper()

if busqueda and not df_q.empty:
    # Filtramos: Buscamos en 'CÓDIGO' o en 'NOMBRE DEL COLOR'
    mask = (df_q['CODIGO'].astype(str).str.contains(busqueda, na=False)) | \
           (df_q['NOMBRE DEL COLOR'].astype(str).str.contains(busqueda, na=False))
    
    resultados = df_q[mask]

    if not resultados.empty:
        # i es el contador para evitar el error de Duplicate Key
        for i, (idx, fila_datos) in enumerate(resultados.iterrows()):
            cod_vinculo = str(fila_datos['CÓDIGO'])
            nombre_color = str(fila_datos['NOMBRE DEL COLOR'])
            
            with st.expander(f"📍 {cod_vinculo} - {nombre_color}", expanded=True):
                # 3. SELECTOR DE LITROS
                litros_a_preparar = st.number_input(
                    f"¿Cuántos Litros quieres preparar?", 
                    min_value=0.01, max_value=100.0, value=1.0, step=0.1, 
                    key=f"input_{idx}_{i}"
                )
                
                st.write(f"**Fórmula final para {litros_a_preparar} Litro(s):**")
                
                # Buscamos los nombres de las bases en la hoja BASES usando la columna COLOR
                fila_nombres = df_n[df_n['COLOR'].astype(str) == cod_vinculo]
                
                # Mostramos en 2 columnas para que en el celular se vea una debajo de otra
                cols = st.columns(2)
                item_idx = 0
                
                # Recorremos de BASE 1 a BASE 17
                for j in range(1, 18):
                    col_base = f"BASE {j}"
                    
                    if col_base in fila_datos:
                        # Convertir cantidad de la celda a número
                        try:
                            cant_original = float(str(fila_datos[col_base]).replace(',', '.'))
                        except:
                            cant_original = 0
                        
                        if cant_original > 0:
                            # Buscamos el nombre de la base
                            nombre_de_base = f"Base {j}" # Por defecto
                            if not fila_nombres.empty and col_base in fila_nombres.columns:
                                val_n = fila_nombres.iloc[0][col_base]
                                if val_n != "" and val_n != 0:
                                    nombre_de_base = val_n
                            
                            # CÁLCULO EN LITROS
                            resultado_litros = round(cant_original * litros_a_preparar, 3)
                            
                            with cols[item_idx % 2]:
                                # Diseño tipo tarjeta para celular
                                st.metric(label=f"{nombre_de_base}", value=f"{resultado_litros} L")
                            item_idx += 1
                
                if item_idx == 0:
                    st.info("Este color no tiene cantidades registradas.")
    else:
        st.warning("No se encontró ningún color con ese nombre o código.")

# Barra lateral informativa
st.sidebar.markdown("---")
st.sidebar.write("### 📂 Base de Datos")
st.sidebar.markdown(f"[Abrir Google Sheets](https://docs.google.com/spreadsheets/d/{ID_HOJA}/edit)")
st.sidebar.info("Si añades un color nuevo en el Excel, espera 10 segundos y vuelve a buscar aquí.")

