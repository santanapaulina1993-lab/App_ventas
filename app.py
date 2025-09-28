import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Calculadora de rentabilidad", layout="wide")

# CSS personalizado estilo agrícola
st.markdown("""
<style>
    /* Contenedor principal con padding */
    .main { padding: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f7faf5; }

    /* Botones con color verde oscuro, borde redondeado y tamaño */
    .stButton>button {
        width: 100%; 
        border-radius: 12px; 
        height: 45px; 
        font-size: 16px; 
        background-color: #3a6a32;  /* Verde bosque */
        color: #f1f1dc;            /* Crema claro */
        border: 2px solid #557a3b;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #557a3b; /* Verde más claro */
        color: #f9f7f1;
    }

    /* Cajas de producto - fondo verde claro con sombra suave */
    .product-box {
        background: #d4e6c6;  /* Verde claro terroso */
        padding: 15px; 
        border-radius: 12px; 
        margin: 10px 0;
        box-shadow: 1px 1px 6px rgba(67, 103, 38, 0.3);
        color: #3a4a20; /* Verde oscuro */
    }

    /* Caja de totales con fondo amarillo cálido */
    .total-box {
        background: #f9d976;  /* Amarillo pálido, cálido */
        color: #5b3a00;      /* Marrón oscuro */
        padding: 20px; 
        border-radius: 12px; 
        margin: 20px 0;
        box-shadow: 1px 1px 8px rgba(154, 117, 0, 0.4);
    }

    /* Cajas de advertencia en rojo suave */
    .warning-box {
        background: #fce4e4; /* Rojo muy claro */
        border: 1px solid #ef6f6f; 
        padding: 15px; 
        border-radius: 12px;
        color: #9b2c2c;
        font-weight: 600;
    }

    /* Resultados positivos en verde oliva */
    .result-positive {
        color: #2f6f2f;
        font-weight: bold; 
        font-size: 18px;
    }

    /* Resultados negativos en rojo terroso */
    .result-negative {
        color: #a03434;
        font-weight: bold; 
        font-size: 18px;
    }

    /* Caja para edición */
    .edit-box {
        background: #e8f5e8; /* Verde muy pálido */
        padding: 10px; 
        border-radius: 10px; 
        margin: 5px 0;
        border: 1px solid #c4d9b6;
        color: #3a4a20;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar para subir archivo
st.sidebar.header("📂 Cargar Archivo de Productos ")
archivo = st.sidebar.file_uploader("Sube un archivo CSV o Excel", type=["csv", "xlsx"])

if archivo is not None:
    try:
        if archivo.name.endswith('.csv'):
            df_productos = pd.read_csv(archivo)
        else:
            df_productos = pd.read_excel(archivo)

        # Validar columnas necesarias
        columnas_necesarias = {'ID', 'producto', 'precio_venta', 'costo', 'stock'}
        if not columnas_necesarias.issubset(df_productos.columns):
            st.error("❌ El archivo debe contener: ID, producto, precio_venta, costo, stock")
            st.stop()

        # Convertir a diccionario usable
        PRODUCTOS = df_productos.set_index('ID')[['producto', 'precio_venta', 'costo']].to_dict(orient='index')
        for k, v in PRODUCTOS.items():
            v['nombre'] = v.pop('producto')
            v['precio'] = v.pop('precio_venta')

        with st.expander("🔍 Ver Productos Cargados"):
            st.dataframe(df_productos)

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
        st.stop()
else:
    st.warning("⚠️ Debes subir un archivo para continuar.")
    st.stop()

# Estado inicial
if 'venta_actual' not in st.session_state:
    st.session_state.venta_actual = []
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# Función de ganancia
def calcular_ganancia(producto_id, cantidad, descuento):
    producto = PRODUCTOS[producto_id]
    precio_final = producto['precio'] * (1 - descuento / 100)
    ganancia = (precio_final - producto['costo']) * cantidad
    return ganancia, precio_final

# Interfaz principal
st.title("📊 Calculadora de Rentabilidad")
st.write("Sistema para optimizar ganancias")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📦 Agregar/Editar Producto")

    # Edición de producto
    if st.session_state.edit_index is not None:
        item = st.session_state.venta_actual[st.session_state.edit_index]
        st.info(f"✏️ Editando: {item['producto']}")

    producto_option = st.selectbox(
        "Seleccionar Producto:",
        options=list(PRODUCTOS.keys()),
        format_func=lambda x: f"{PRODUCTOS[x]['nombre']} - ${PRODUCTOS[x]['precio']}"
    )

    # Obtener stock actual del producto seleccionado
    stock_disponible = int(df_productos[df_productos['ID'] == producto_option]['stock'].values[0])

    cantidad = st.number_input(
        "Cantidad:", min_value=1, max_value=stock_disponible, step=1,
        value=st.session_state.venta_actual[st.session_state.edit_index]['cantidad']
        if st.session_state.edit_index is not None else 1,
        key="cantidad_input"
    )

    descuento = st.number_input(
        "Descuento (%):", min_value=0, max_value=100, step=1,
        value=st.session_state.venta_actual[st.session_state.edit_index]['descuento']
        if st.session_state.edit_index is not None else 0,
        key="descuento_input"
    )

    # Botones
    if st.session_state.edit_index is not None:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 Guardar Cambios", type="primary"):
                ganancia, precio_final = calcular_ganancia(producto_option, cantidad, descuento)
                st.session_state.venta_actual[st.session_state.edit_index] = {
                    'producto': PRODUCTOS[producto_option]['nombre'],
                    'producto_id': producto_option,
                    'cantidad': cantidad,
                    'descuento': descuento,
                    'precio_final': precio_final,
                    'ganancia': ganancia
                }
                st.session_state.edit_index = None
                st.success("✅ Cambios guardados! 🌱")
                st.experimental_rerun()
        with col_btn2:
            if st.button("❌ Cancelar"):
                st.session_state.edit_index = None
                st.experimental_rerun()
    else:
        if st.button("➕ Agregar a Venta", type="primary"):
            ganancia, precio_final = calcular_ganancia(producto_option, cantidad, descuento)
            st.session_state.venta_actual.append({
                'producto': PRODUCTOS[producto_option]['nombre'],
                'producto_id': producto_option,
                'cantidad': cantidad,
                'descuento': descuento,
                'precio_final': precio_final,
                'ganancia': ganancia
            })
            st.success(f"✅ {PRODUCTOS[producto_option]['nombre']} agregado! 🌿")

with col2:
    st.markdown("### 📋 Venta Actual - Editable")

    if st.session_state.venta_actual:
        total_ganancia = sum(item['ganancia'] for item in st.session_state.venta_actual)

        if total_ganancia < 0:
            st.markdown(f"""
            <div class='warning-box'>
                ⚠️ <b>ESTÁS PERDIENDO DINERO!</b><br>
                Ganancia total negativa: <span class='result-negative'>${total_ganancia:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

        for i, item in enumerate(st.session_state.venta_actual):
            col_info, col_action = st.columns([3, 1])
            with col_info:
                ganancia_class = "result-positive" if item['ganancia'] >= 0 else "result-negative"
                st.markdown(f"""
                <div class='product-box'>
                    <b>{i+1}. {item['producto']} x{item['cantidad']}</b><br>
                    Descuento: {item['descuento']}% |
                    Ganancia: <span class='{ganancia_class}'>${item['ganancia']:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_action:
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.experimental_rerun()
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.venta_actual.pop(i)
                    st.success("Producto eliminado! 🍂")
                    st.experimental_rerun()

        total_ingresos = sum(item['precio_final'] * item['cantidad'] for item in st.session_state.venta_actual)
        total_costos = sum(PRODUCTOS[item['producto_id']]['costo'] * item['cantidad'] for item in st.session_state.venta_actual)

        st.markdown(f"""
        <div class='total-box'>
            <h3>💰 TOTALES DE VENTA</h3>
            <p>Ingresos: <b>${total_ingresos:,.2f}</b></p>
            <p>Costos: <b>${total_costos:,.2f}</b></p>
            <p>Ganancia: <span class='{'result-positive' if total_ganancia >= 0 else 'result-negative'}'><b>${total_ganancia:,.2f}</b></span></p>
            <p>Margen: <b>{(total_ganancia / total_ingresos * 100) if total_ingresos > 0 else 0:.1f}%</b></p>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("No hay productos agregados a la venta aún.")