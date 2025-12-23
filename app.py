import streamlit as st
import pandas as pd
import unicodedata

# Configuración de página
st.set_page_config(page_title="FARBEN - Sistema Litros", layout="wide")

# 1. CONFIGURACIÓN DEL LINK
ID_HOJA = "1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU" 
URL_DATOS = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/gviz/tq?tqx=out:csv&sheet=DATOS"
URL_BASES = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/gviz/tq?tqx=out:csv&sheet=BASES"

# Función para quitar acentos y dejar todo limpio
def normalizar_texto(texto):
    texto = str(texto).strip().upper()
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

@st.cache_data(ttl=10)
def load_data():
    try:
        df_q = pd.read_csv(URL_DATOS)
        df_n = pd.read_csv(URL_BASES)
        
        # Normalizamos los nombres de las columnas (CÓDIGO -> CODIGO)
        df_q.columns = [normalizar_texto(c) for c in df_q.columns]
        df_n.columns = [normalizar_texto(c) for c in df_n.columns]
        
        return df_q.fillna(0), df_n.fillna("")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_q, df_n = load_data()

st.title("🎨 Sistema FARBEN (Cálculo en Litros)")

# 2. BUSCADOR FLEXIBLE
busqueda = st.text_input("🔍 Buscar por Código o Nombre:").strip().upper()

if busqueda and not df_q.empty:
    # Usamos los nombres normalizados: CODIGO y NOMBRE DEL COLOR
    mask = (df_q['CODIGO'].astype(str).str.contains(busqueda, na=False)) | \
           (df_q['NOMBRE DEL COLOR'].astype(str).str.contains(busqueda, na=False))
    
    resultados = df_q[mask]

    if not resultados.empty:
        for i, (idx, fila_datos) in enumerate(resultados.iterrows()):
            cod_v = str(fila_datos['CODIGO'])
            nom_v = str(fila_datos['NOMBRE DEL COLOR'])
            
            with st.expander(f"📌 {cod_v} - {nom_v}", expanded=True):
                # Selector de litros
                litros_a_preparar = st.number_input(
                    "¿Cuántos Litros (L) preparar?", 
                    0.01, 100.0, 1.0, 0.1, key=f"L_{idx}_{i}"
                )
                
                st.write(f"**Mezcla final para {litros_a_preparar} Litro(s):**")
                
                # Buscamos en la otra hoja usando 'COLOR' (normalizado de CÓDIGO)
                fila_nombres = df_n[df_n['COLOR'].astype(str) == cod_v]
                
                cols = st.columns(2)
                item_idx = 0
                
                # Recorremos las bases del 1 al 17
                for j in range(1, 18):
                    col_b = f"BASE {j}"
                    if col_b in df_q.columns:
                        try:
                            # Convertimos cantidad a número (soporta 0.5 y 0,5)
                            valor_celda = str(fila_datos[col_b]).replace(',', '.')
                            cant_1L = float(valor_celda)
                        except:
                            cant_1L = 0
                        
                        if cant_1L > 0:
                            # Nombre de la base desde la hoja BASES
                            nombre_pintura = f"Base {j}"
                            if not fila_nombres.empty and col_b in df_n.columns:
                                val_n = fila_nombres.iloc[0][col_b]
                                if val_n != "" and val_n != 0:
                                    nombre_pintura = val_n
                            
                            # CÁLCULO: Cantidad x Litros elegidos
                            total_calculado = round(cant_1L * litros_a_preparar, 3)
                            
                            with cols[item_idx % 2]:
                                st.metric(label=f"{nombre_pintura}", value=f"{total_calculado} L")
                            item_idx += 1
    else:
        st.warning("No se encontró el color.")

# Sidebar con ayuda
st.sidebar.markdown(f"### [📂 Abrir Google Sheets](https://docs.google.com/spreadsheets/d/{ID_HOJA}/edit)")
st.sidebar.info("Si no ves datos, verifica que las columnas en tu Excel se llamen BASE 1, BASE 2, etc.")
