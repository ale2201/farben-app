import streamlit as st
import pandas as pd

# Configuración para móviles
st.set_page_config(page_title="FARBEN - Mezclas Exactas", layout="wide")

# 1. TU ID DE GOOGLE SHEETS
ID_HOJA = "1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU" 

# Enlaces de lectura directa para las dos pestañas
URL_DATOS = f"https://docs.google.com/spreadsheets/d/1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU/gviz/tq?tqx=out:csv&sheet=DATOS"
URL_BASES = f"https://docs.google.com/spreadsheets/d/1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU/gviz/tq?tqx=out:csv&sheet=BASES"

@st.cache_data(ttl=5) # Se actualiza cada 5 segundos
def load_data():
    try:
        # Cargamos ambas hojas
        df_q = pd.read_csv(URL_DATOS).fillna(0) # Cantidades
        df_n = pd.read_csv(URL_BASES).fillna("") # Nombres de bases
        return df_q, df_n
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_q, df_n = load_data()

st.title("🎨 Calculadora FARBEN")
st.subheader("Fórmulas combinadas en Litros (L)")

# --- BUSCADOR ---
busqueda = st.text_input("🔍 Escribe el código o marca:").strip().upper()

if busqueda and not df_q.empty:
    # Buscamos en las dos primeras columnas (Código o Nombre)
    mask = (df_q.iloc[:, 0].astype(str).str.contains(busqueda, na=False, case=False)) | \
           (df_q.iloc[:, 1].astype(str).str.contains(busqueda, na=False, case=False))
    
    resultados = df_q[mask]

    if not resultados.empty:
        for i, (idx, fila_datos) in enumerate(resultados.iterrows()):
            # Paso A: Obtener el código de vinculación (Columna 0 de DATOS)
            cod_vinculo = str(fila_datos.iloc[0]).strip()
            nombre_color = str(fila_datos.iloc[1]).strip()
            
            with st.expander(f"📌 {cod_vinculo} - {nombre_color}", expanded=True):
                # Selector de litros
                litros_a_preparar = st.number_input(
                    f"¿Cuántos Litros quieres preparar?", 
                    0.01, 100.0, 1.0, 0.1, key=f"L_{idx}_{i}"
                )
                
                st.write(f"**Mezcla final para {litros_a_preparar} Litro(s):**")
                
                # Paso B: Buscar la fila de NOMBRES que coincida con ese código
                fila_nombres = df_n[df_n.iloc[:, 0].astype(str).str.strip() == cod_vinculo]
                
                # Diseño de rejilla para celular
                cols = st.columns(2)
                item_idx = 0
                
                # Paso C: Recorrer las columnas desde la BASE 1 (Columna índice 3 en adelante)
                for col_idx in range(3, len(fila_datos)):
                    try:
                        # 1. Sacar la cantidad (de la tabla DATOS)
                        raw_cant = str(fila_datos.iloc[col_idx]).replace(',', '.')
                        cant_base_1L = float(raw_cant)
                        
                        if cant_base_1L > 0:
                            # 2. Sacar el nombre REAL (de la tabla BASES en la misma posición)
                            # Si no lo encuentra, usamos un nombre genérico
                            nombre_real = f"Base {col_idx-2}"
                            if not fila_nombres.empty:
                                val_n = fila_nombres.iloc[0].iloc[col_idx]
                                if val_n != "" and val_n != 0:
                                    nombre_real = str(val_n)
                            
                            # 3. Calcular la cantidad final
                            total_final = round(cant_base_1L * litros_a_preparar, 3)
                            
                            # Mostrar en la web
                            with cols[item_idx % 2]:
                                st.metric(label=nombre_real, value=f"{total_final} L")
                            item_idx += 1
                    except:
                        continue
                
                if item_idx == 0:
                    st.info("Este color no tiene mezcla registrada.")
    else:
        st.warning("No se encontró el color.")

# --- SECCIÓN PARA AGREGAR DATOS ---
st.sidebar.markdown("---")
st.sidebar.write("### ➕ Agregar Datos")
st.sidebar.info("Para que los cambios sean automáticos y se guarden para siempre:")
st.sidebar.markdown(f"[👉 Abre tu Google Sheets aquí](https://docs.google.com/spreadsheets/d/{ID_HOJA}/edit)")
st.sidebar.write("1. Escribe el color y cantidades en la hoja **DATOS**.\n2. Escribe el color y los nombres en la hoja **BASES**.\n3. ¡La web se actualiza sola!")
