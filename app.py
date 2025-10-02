import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Calculadora de rentabilidad", layout="wide")

# CSS personalizado estilo agrícola
st.markdown("""
<style>
    .main { padding: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f7faf5; }

    .stButton>button {
        width: 100%; 
        border-radius: 12px; 
        height: 45px; 
        font-size: 16px; 
        background-color: #3a6a32;
        color: #f1f1dc;            
        border: 2px solid #557a3b;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #557a3b;
        color: #f9f7f1;
    }

    .product-box {
        background: #d4e6c6;
        padding: 15px; 
        border-radius: 12px; 
        margin: 10px 0;
        box-shadow: 1px 1px 6px rgba(67, 103, 38, 0.3);
        color: #3a4a20;
    }

    .total-box {
        background: #f9d976;
        color: #5b3a00;
        padding: 20px; 
        border-radius: 12px; 
        margin: 20px 0;
        box-shadow: 1px 1px 8px rgba(154, 117, 0, 0.4);
    }

    .edit-box {
        background: #e8f5e8;
        padding: 10px; 
        border-radius: 10px; 
        margin: 5px 0;
        border: 1px solid #c4d9b6;
        color: #3a4a20;
    }

    .result-positive {
        color: #2f6f2f;
        font-weight: bold; 
        font-size: 18px;
    }

    .result-warning {
        color: #b38600;
        font-weight: bold;
        font-size: 18px;
    }

    .result-negative {
        color: #a03434;
        font-weight: bold; 
        font-size: 18px;
    }

    .margen-no-aceptable {
        color: #a03434;
        font-weight: bold;
        background: #fce4e4;
        padding: 5px 10px;
        border-radius: 8px;
    }
    .margen-aceptable {
        color: #8a6d00;
        font-weight: bold;
        background: #fff9c4;
        padding: 5px 10px;
        border-radius: 8px;
    }
    .margen-optimo {
        color: #2f6f2f;
        font-weight: bold;
        background: #e8f5e8;
        padding: 5px 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar para subir archivo
st.sidebar.header("📂 Cargar Archivo de Productos ")
archivo = st.sidebar.file_uploader("Sube un archivo CSV o Excel", type=["csv", "xlsx"])

# Inicializar variables globales
PRODUCTOS = {}
df_productos = None

if archivo is not None:
    try:
        if archivo.name.endswith('.csv'):
            df_productos = pd.read_csv(archivo)
        else:
            df_productos = pd.read_excel(archivo)

        columnas_necesarias = {'ID', 'producto', 'precio_venta', 'costo', 'stock'}
        if not columnas_necesarias.issubset(df_productos.columns):
            st.error("❌ El archivo debe contener: ID, producto, precio_venta, costo, stock")
            st.stop()

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

# Función para calcular precio final
def calcular_precio_final(producto_id, descuento):
    producto = PRODUCTOS[producto_id]
    precio_final = producto['precio'] * (1 - descuento / 100)
    return precio_final

# Función para clasificar margen (dummy, se usa para semáforo)
def clasificar_margen(margen):
    if margen <= 10:
        return "margen-no-aceptable", "No Aceptable"
    elif 11 <= margen <= 15:
        return "margen-aceptable", "Aceptable"
    else:
        return "margen-optimo", "Óptimo"

# Interfaz principal
if PRODUCTOS and df_productos is not None:
    st.title("📊 Calculadora de Rentabilidad")
    st.write("Sistema para optimizar ventas")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📦 Agregar/Editar Producto")

        if st.session_state.edit_index is not None:
            item_editando = st.session_state.venta_actual[st.session_state.edit_index]
            producto_default = item_editando['producto_id']
            st.info(f"✏️ Editando: {item_editando['producto']}")
        else:
            producto_default = list(PRODUCTOS.keys())[0] if PRODUCTOS else None

        producto_option = st.selectbox(
            "Seleccionar Producto:",
            options=list(PRODUCTOS.keys()),
            index=list(PRODUCTOS.keys()).index(producto_default) if producto_default in PRODUCTOS else 0,
            format_func=lambda x: f"{PRODUCTOS[x]['nombre']} - ${PRODUCTOS[x]['precio']}"
        )

        stock_disponible = 100
        if PRODUCTOS and producto_option in PRODUCTOS:
            try:
                stock_fila = df_productos[df_productos['ID'] == producto_option]
                if not stock_fila.empty:
                    stock_disponible = int(stock_fila['stock'].values[0])
            except:
                stock_disponible = 100

        if st.session_state.edit_index is not None:
            cantidad_default = st.session_state.venta_actual[st.session_state.edit_index]['cantidad']
            descuento_default = st.session_state.venta_actual[st.session_state.edit_index]['descuento']
        else:
            cantidad_default = 1
            descuento_default = 0

        cantidad = st.number_input("Cantidad:", min_value=1, max_value=stock_disponible, step=1, value=cantidad_default)
        descuento = st.number_input("Descuento (%):", min_value=0, max_value=100, step=1, value=descuento_default)

        # Información del producto seleccionado
        if producto_option in PRODUCTOS:
            producto_info = PRODUCTOS[producto_option]
            precio_original = producto_info['precio']
            precio_con_descuento = calcular_precio_final(producto_option, descuento)

            st.markdown(f"""
            <div class='edit-box'>
                <b>Información del Producto:</b><br>
                Precio con descuento: <b>${precio_con_descuento:,.2f}</b>
            </div>
            """, unsafe_allow_html=True)

        # Botones
        if st.session_state.edit_index is not None:
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💾 Guardar Cambios", type="primary"):
                    precio_final = calcular_precio_final(producto_option, descuento)
                    st.session_state.venta_actual[st.session_state.edit_index] = {
                        'producto': PRODUCTOS[producto_option]['nombre'],
                        'producto_id': producto_option,
                        'cantidad': cantidad,
                        'descuento': descuento,
                        'precio_final': precio_final,
                    }
                    st.session_state.edit_index = None
                    st.success("✅ Cambios guardados!")
                    st.rerun()
            with col_btn2:
                if st.button("❌ Cancelar"):
                    st.session_state.edit_index = None
                    st.rerun()
        else:
            if st.button("➕ Agregar a Venta", type="primary"):
                precio_final = calcular_precio_final(producto_option, descuento)
                st.session_state.venta_actual.append({
                    'producto': PRODUCTOS[producto_option]['nombre'],
                    'producto_id': producto_option,
                    'cantidad': cantidad,
                    'descuento': descuento,
                    'precio_final': precio_final,
                })
                st.success(f"✅ {PRODUCTOS[producto_option]['nombre']} agregado!")
                st.rerun()

    with col2:
        st.markdown("### 📋 Venta Actual - Editable")

        if st.session_state.venta_actual:
            total_ingresos = sum(item['precio_final'] * item['cantidad'] for item in st.session_state.venta_actual)
            total_cantidad = sum(item['cantidad'] for item in st.session_state.venta_actual)

            # Calcular ganancia real por producto
            for item in st.session_state.venta_actual:
                costo_unitario = PRODUCTOS[item['producto_id']]['costo']
                item['ganancia'] = (item['precio_final'] - costo_unitario) * item['cantidad']

            total_ganancia = sum(item['ganancia'] for item in st.session_state.venta_actual)

            # Semáforo basado en margen real
            margen = (total_ganancia / total_ingresos * 100) if total_ingresos > 0 else 0
            if margen >= 20:
                color_class = "result-positive"
                color_emoji = "🟢"
            elif margen >= 0:
                color_class = "margen-aceptable"
                color_emoji = "🟡"
            else:
                color_class = "margen-no-aceptable"
                color_emoji = "🔴"

            for i, item in enumerate(st.session_state.venta_actual):
                col_info, col_action = st.columns([3, 1])
                with col_info:
                    precio_original_producto = PRODUCTOS[item['producto_id']]['precio']
                    precio_unit_descuento = item['precio_final']

                    st.markdown(f"""
                    <div class='product-box'>
                        <b>{i+1}. {item['producto']} x{item['cantidad']}</b><br>
                        Precio Original : ${precio_original_producto:,.2f}<br>
                        Descuento: <b>{item['descuento']}%</b><br>
                        Precio Final : <b>${precio_unit_descuento:,.2f}</b>
                    </div>
                    """, unsafe_allow_html=True)
                with col_action:
                    if st.button("✏️", key=f"edit_{i}"):
                        st.session_state.edit_index = i
                        st.rerun()
                    if st.button("🗑️", key=f"delete_{i}"):
                        st.session_state.venta_actual.pop(i)
                        st.success("Producto eliminado!")
                        st.rerun()

            # Totales con semáforo
            st.markdown(f"""
            <div class='total-box'>
                <h3>💰 TOTALES DE VENTA</h3>
                <p><b>Productos en venta:</b> {len(st.session_state.venta_actual)}</p>
                <p><b>Cantidad Total:</b> {total_cantidad} unidades</p>
                <p><b>Venta Total:</b> <span class='result-positive'>${total_ingresos:,.2f}</span></p>
                <p><b>Margen:</b> <span class='{color_class}'>{color_emoji} </span></p>
            </div>
            """, unsafe_allow_html=True)

            # Resumen tipo factura
            factura_data = []
            for item in st.session_state.venta_actual:
                total_item = item['precio_final'] * item['cantidad']
                factura_data.append({
                    "Producto": item['producto'],
                    "Cantidad": item['cantidad'],
                    "Precio Final Unitario": f"${item['precio_final']:,.2f}",
                    "Total": f"${total_item:,.2f}"
                })
            df_factura = pd.DataFrame(factura_data)
            st.markdown("### 📄 Resumen")
            st.table(df_factura)

        else:
            st.info("No hay productos agregados a la venta aún.")
else:
    st.warning("⚠️ Esperando la carga de datos del archivo...")
