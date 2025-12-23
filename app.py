import streamlit as st
import pandas as pd

# Configuración para móviles y escritorio
st.set_page_config(page_title="FARBEN Mix", layout="wide")

# Estilos visuales para que las bases se vean como etiquetas en el celular
st.markdown("""
    <style>
    .metric-container { background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin: 5px 0; }
    .stMetric { border-left: 5px solid #ff4b4b; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data(file_name):
    try:
        df = pd.read_csv(file_name, encoding='latin-1', sep=None, engine='python')
        df = df.dropna(how='all').fillna('')
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

# Mantener los datos en la memoria de la sesión
if 'df_q' not in st.session_state:
    st.session_state.df_q = load_data('datos.csv')
if 'df_n' not in st.session_state:
    st.session_state.df_n = load_data('bases.csv')

# --- MENÚ LATERAL ---
st.sidebar.title("🎨 Menú FARBEN")
opcion = st.sidebar.radio("Ir a:", ["🔍 Buscar Fórmula", "➕ Crear Nueva Fórmula"])

# --- OPCIÓN 1: BUSCADOR ---
if opcion == "🔍 Buscar Fórmula":
    st.title("Buscador de Mezclas")
    busqueda = st.text_input("Escribe el código o nombre del color:", "").strip().upper()

    if busqueda:
        df_q = st.session_state.df_q
        # Buscamos en las dos primeras columnas
        mask = (df_q.iloc[:, 0].astype(str).str.contains(busqueda)) | (df_q.iloc[:, 1].astype(str).str.contains(busqueda))
        resultados = df_q[mask]

        if not resultados.empty:
            for _, fila in resultados.iterrows():
                codigo = fila.iloc[0]
                nombre = fila.iloc[1]
                
                with st.expander(f"📍 {codigo} - {nombre}"):
                    # Multiplicador para cantidades
                    mult = st.number_input("Multiplicar mezcla por:", 0.1, 20.0, 1.0, 0.5, key=f"btn_{codigo}")
                    
                    # Traer nombres de bases desde bases.csv
                    df_n = st.session_state.df_n
                    fila_n = df_n[df_n.iloc[:, 0] == codigo]
                    
                    st.write("### Composición:")
                    # En celulares usaremos 2 columnas, en PC se verá más amplio
                    cols = st.columns([1, 1])
                    idx_visual = 0
                    
                    for i in range(1, 18):
                        col_name = f"BASE {i}"
                        cant_orig = str(fila[col_name]).replace(',', '.')
                        
                        try:
                            val_float = float(cant_orig) if cant_orig != '' else 0
                            if val_float > 0:
                                nombre_base = fila_n.iloc[0][col_name] if not fila_n.empty else f"Base {i}"
                                with cols[idx_visual % 2]:
                                    st.metric(label=str(nombre_base), value=f"{round(val_float * mult, 2)} g")
                                idx_visual += 1
                        except: continue
        else:
            st.warning("No se encontró el color.")

# --- OPCIÓN 2: AGREGAR NUEVO ---
elif opcion == "➕ Crear Nueva Fórmula":
    st.title("Nueva Fórmula")
    
    # PASO 1: DATOS GENERALES
    st.subheader("1️⃣ Datos Generales")
    col_a, col_b, col_c = st.columns(3)
    nuevo_cod = col_a.text_input("Código del Color")
    nuevo_nom = col_b.text_input("Nombre / Marca")
    nuevo_tipo = col_c.selectbox("Tipo de Pintura", ["DUCO", "PU", "POLIURETANO"])

    st.write("---")
    
    # PASO 2: BASES Y CANTIDADES
    st.subheader("2️⃣ Mezcla (Bases y Gramos)")
    st.info("Escribe el nombre de la base y su peso al lado.")

    nuevos_pesos = {}
    nuevos_nombres_base = {}

    # Generamos 10 filas para empezar (puedes llenar solo las que necesites)
    for i in range(1, 11):
        c1, c2 = st.columns([2, 1])
        n_b = c1.text_input(f"Nombre Base {i}", key=f"nb_{i}", placeholder="Ej: BLANCO, NEGRO...")
        c_b = c2.number_input(f"Gramos {i}", 0.0, 5000.0, 0.0, step=0.1, key=f"cb_{i}")
        
        nuevos_nombres_base[f"BASE {i}"] = n_b
        nuevos_pesos[f"BASE {i}"] = c_b

    # Botón para procesar
    if st.button("💾 Guardar Fórmula en la Lista"):
        if nuevo_cod and nuevo_nom:
            # Preparar fila para DATOS.CSV
            fila_d = {st.session_state.df_q.columns[0]: nuevo_cod, st.session_state.df_q.columns[1]: nuevo_nom, st.session_state.df_q.columns[2]: nuevo_tipo}
            fila_d.update(nuevos_pesos)
            
            # Preparar fila para BASES.CSV
            fila_b = {st.session_state.df_n.columns[0]: nuevo_cod, st.session_state.df_n.columns[1]: nuevo_nom, st.session_state.df_n.columns[2]: nuevo_tipo}
            fila_b.update(nuevos_nombres_base)
            
            # Añadir a la sesión actual
            st.session_state.df_q = pd.concat([st.session_state.df_q, pd.DataFrame([fila_d])], ignore_index=True)
            st.session_state.df_n = pd.concat([st.session_state.df_n, pd.DataFrame([fila_b])], ignore_index=True)
            
            st.success(f"¡Color {nuevo_cod} agregado temporalmente!")
        else:
            st.error("Por favor rellena el Código y el Nombre.")

    st.write("---")
    st.subheader("📥 Finalizar y Descargar")
    st.write("Para que los cambios sean permanentes, descarga los archivos y súbelos a tu GitHub.")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button("Descargar DATOS.CSV", st.session_state.df_q.to_csv(index=False).encode('latin-1'), "datos.csv", "text/csv")
    with col_d2:
        st.download_button("Descargar BASES.CSV", st.session_state.df_n.to_csv(index=False).encode('latin-1'), "bases.csv", "text/csv")
