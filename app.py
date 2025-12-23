import streamlit as st
import pandas as pd

# Configuración de página para móviles
st.set_page_config(page_title="FARBEN Mix", layout="wide")

# 1. TU ID DE HOJA (Sacado de tu mensaje anterior)
ID_HOJA = "1dCGpVhDwUO-fcBo33GcjrzZ0T9gsnT4yQjr9EibUkVU" 

# Enlaces de lectura directa
URL_DATOS = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/gviz/tq?tqx=out:csv&sheet=DATOS"
URL_BASES = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/gviz/tq?tqx=out:csv&sheet=BASES"

@st.cache_data(ttl=5) # Se actualiza cada 5 segundos
def load_data():
    try:
        # Cargamos los datos sin importar los nombres de las columnas
        df_q = pd.read_csv(URL_DATOS).fillna(0)
        df_n = pd.read_csv(URL_BASES).fillna("")
        return df_q, df_n
    except Exception as e:
        st.error(f"⚠️ Error al conectar con Google Sheets: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_q, df_n = load_data()

st.title("🎨 Sistema FARBEN - Litros")

# --- BUSCADOR ---
busqueda = st.text_input("🔍 Escribe el código o nombre del color:").strip().upper()

if busqueda and not df_q.empty:
    # Usamos iloc[:, 0] y iloc[:, 1] para evitar errores de nombres (CÓDIGO / NOMBRE)
    mask = (df_q.iloc[:, 0].astype(str).str.contains(busqueda, na=False, case=False)) | \
           (df_q.iloc[:, 1].astype(str).str.contains(busqueda, na=False, case=False))
    
    resultados = df_q[mask]

    if not resultados.empty:
        for i, (idx, fila_datos) in enumerate(resultados.iterrows()):
            # Datos principales
            cod_v = str(fila_datos.iloc[0]) # Primera columna (Código)
            nom_v = str(fila_datos.iloc[1]) # Segunda columna (Nombre)
            
            with st.expander(f"📌 {cod_v} - {nom_v}", expanded=True):
                # Entrada de Litros
                litros_a_preparar = st.number_input(
                    f"¿Cuántos Litros (L) preparar?", 
                    0.05, 100.0, 1.0, 0.1, key=f"L_{idx}_{i}"
                )
                
                st.write(f"**Mezcla necesaria para {litros_a_preparar} Litro(s):**")
                st.write("---")
                
                # Buscamos en la otra hoja (BASES) usando el código
                fila_nombres = df_n[df_n.iloc[:, 0].astype(str) == cod_v]
                
                # Diseño en 2 columnas para el celular
                cols = st.columns(2)
                contador_bases = 0
                
                # Las bases empiezan en la columna 3 (índice 3 en adelante)
                # Recorremos todas las columnas de bases que existan
                for col_idx in range(3, len(df_q.columns)):
                    try:
                        # Valor de la base en el Excel
                        valor_excel = str(fila_datos.iloc[col_idx]).replace(',', '.')
                        cant_1L = float(valor_excel)
                        
                        if cant_1L > 0:
                            # Buscamos el nombre de la base en la misma posición en la otra hoja
                            nombre_pintura = f"Base {col_idx-2}"
                            if not fila_nombres.empty:
                                val_n = fila_nombres.iloc[0].iloc[col_idx]
                                if val_n != "" and val_n != 0:
                                    nombre_pintura = val_n
                            
                            # CÁLCULO FINAL: Cantidad x Litros
                            total_litros = round(cant_1L * litros_a_preparar, 3)
                            
                            with cols[contador_bases % 2]:
                                st.metric(label=f"{nombre_pintura}", value=f"{total_litros} L")
                            contador_bases += 1
                    except:
                        continue
    else:
        st.warning("No se encontró ningún resultado.")

# --- BARRA LATERAL (PARA AGREGAR DATOS) ---
st.sidebar.title("Configuración")
st.sidebar.markdown(f"### [📂 Abrir Google Sheets](https://docs.google.com/spreadsheets/d/{ID_HOJA}/edit)")
st.sidebar.info("""
**Para que el guardado sea automático:**
1. Haz clic en el link de arriba.
2. Agrega el nuevo color al final de la lista.
3. La web se actualizará sola en 5 segundos.
""")
