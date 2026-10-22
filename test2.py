import streamlit as st
import math

# Configuración de la página
st.set_page_config(
    page_title="Simulador por Producto - Ollas UNACEM",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BASE DE DATOS DE RECETAS (DATO POR PLATO) ---
RECETAS_DB = {
    "SOPA DE MOTE": {
        "rendimiento_platos": 70,
        "insumos": [
            {"nombre": "Mote seco", "cantidad_g": 5000, "costo_total": 30.00},  # 5 kg x S/ 6.00
            {"nombre": "Mondongo", "cantidad_g": 1500, "costo_total": 21.00},  # 1.5 kg x S/ 14.00
            {"nombre": "Piltrafa", "cantidad_g": 1500, "costo_total": 22.50},  # 1.5 kg x S/ 15.00
            {"nombre": "Huesos de manzana", "cantidad_g": 4000, "costo_total": 12.00},  # 4 kg x S/ 3.00
            {"nombre": "Pata de vaca", "cantidad_g": 1000, "costo_total": 22.00},  # 1 kg x S/ 22.00
            {"nombre": "Arroz", "cantidad_g": 300, "costo_total": 1.50},  # Estimado
            {"nombre": "Cebolla (1 un)", "cantidad_g": 200, "costo_total": 2.00},
            {"nombre": "Ajo (1 un)", "cantidad_g": 50, "costo_total": 1.00},
            {"nombre": "Perejil", "cantidad_g": 100, "costo_total": 2.00},
            {"nombre": "Orégano", "cantidad_g": 50, "costo_total": 2.00},
            {"nombre": "Hierbabuena", "cantidad_g": 100, "costo_total": 2.00},
            {"nombre": "Limón", "cantidad_g": 500, "costo_total": 2.00},
            {"nombre": "Rocoto", "cantidad_g": 500, "costo_total": 3.50},
            {"nombre": "Sal", "cantidad_g": 500, "costo_total": 2.00},
            {"nombre": "Platos descartables (2 pqt)", "cantidad_g": 0, "costo_total": 8.00},  # 2 pqt x S/ 4.00
            {"nombre": "Servilletas", "cantidad_g": 0, "costo_total": 2.00},
            {"nombre": "Cucharas descartables (2 pqt)", "cantidad_g": 0, "costo_total": 8.00}  # 2 pqt x S/ 4.00
        ]
    },
    "YUCA RELLENA": {
        "rendimiento_platos": 70,
        "insumos": [
            {"nombre": "Yuca amarilla", "cantidad_g": 5000, "costo_total": 20.00},  # 5 kg x S/ 4.00
            {"nombre": "Harina de chuño", "cantidad_g": 1000, "costo_total": 10.00},  # 1 kg x S/ 10.00
            {"nombre": "Carne molida", "cantidad_g": 3000, "costo_total": 66.00},  # 3 kg x S/ 22.00
            {"nombre": "Cebolla", "cantidad_g": 4000, "costo_total": 8.00},  # 4 kg x S/ 2.00
            {"nombre": "Ají panca", "cantidad_g": 100, "costo_total": 2.50},
            {"nombre": "Especias (Pimienta, Orégano, Comino)", "cantidad_g": 50, "costo_total": 2.00},
            {"nombre": "Ajo", "cantidad_g": 100, "costo_total": 2.00},
            {"nombre": "Huevo", "cantidad_g": 500, "costo_total": 4.00}
        ]
    }
}

st.title("🍲 Simulador de Punto de Equilibrio por Producto")
st.subheader("Proyecto Ollas UNACEM")

# --- SELECCIÓN DE PRODUCTO ---
plato_seleccionado = st.selectbox(
    "📌 Selecciona el Plato a Evaluar:",
    options=list(RECETAS_DB.keys())
)

datos_plato = RECETAS_DB[plato_seleccionado]

# --- BARRA LATERAL: COSTOS FIJOS Y PARÁMETROS COMERCIALES ---
with st.sidebar:
    st.header("⚙️ Parámetros Fijos y Ventas")

    st.subheader("👥 Mano de Obra y Costos Fijos")
    horas_trabajo = st.number_input("Tiempo de Trabajo (Horas)", min_value=0.0, value=4.0, step=0.5)
    cocineras = st.number_input("N° de Cocineras", min_value=1, value=4, step=1)
    sueldo_hora = st.number_input("Sueldo por Hora (S/)", min_value=0.0, value=5.0, step=0.5)
    costo_agua = st.number_input("Consumo de Agua (S/)", min_value=0.0, value=10.0, step=1.0)
    costo_lena = st.number_input("Costo de Leña/Gas (S/)", min_value=0.0, value=15.0, step=1.0)

    st.subheader("🎯 Objetivos Comerciales")
    utilidad_deseada = st.number_input("Utilidad Deseada (S/)", min_value=0.0, value=100.0, step=10.0)
    precio_venta = st.number_input("Precio de Venta por Porción (S/)", min_value=0.1, value=6.0, step=0.5)

# --- DETALLE DEL LOTE Y CÁLCULO DE INSUMOS ---
st.header(f"📋 Receta y Costos de Insumos: {plato_seleccionado}")

total_costo_insumos = 0.0
total_gramos_insumos = 0.0

# Formato de tabla para mostrar los insumos cargados
tabla_insumos = []
for item in datos_plato["insumos"]:
    c_total = item["costo_total"]
    g_total = item["cantidad_g"]
    total_costo_insumos += c_total
    total_gramos_insumos += g_total

    tabla_insumos.append({
        "Insumo": item["nombre"],
        "Cantidad (g / un)": f"{g_total} g" if g_total > 0 else "N/A",
        "Costo Total (S/)": f"S/ {c_total:.2f}"
    })

# Mostrar la lista de ingredientes en pantalla
st.dataframe(tabla_insumos, use_container_width=True)

# --- CÁLCULOS CONTABLES AUTOMÁTICOS ---
platos_producidos = datos_plato["rendimiento_platos"]
cvu = total_costo_insumos / platos_producidos if platos_producidos > 0 else 0.0
costos_fijos = (horas_trabajo * cocineras * sueldo_hora) + costo_agua + costo_lena
margen_ganancia = precio_venta - cvu

if margen_ganancia > 0:
    pe_unidades = math.ceil((costos_fijos + utilidad_deseada) / margen_ganancia)
    pe_soles = pe_unidades * precio_venta
else:
    pe_unidades = "MARGEN NEGATIVO"
    pe_soles = 0.0

# --- PANEL DE RESULTADOS ---
st.divider()
st.header("📊 Resultados Contables en Tiempo Real")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Costo Insumos Lote", f"S/ {total_costo_insumos:.2f}")
c2.metric("Rendimiento del Lote", f"{platos_producidos} porciones")
c3.metric("Costo Var. Unitario (CVu)", f"S/ {cvu:.2f}")
c4.metric("Costos Fijos Totales (CF)", f"S/ {costos_fijos:.2f}")

st.subheader("🎯 Punto de Equilibrio y Recaudación")
res1, res2 = st.columns(2)

with res1:
    if isinstance(pe_unidades, int):
        st.success(f"### **{pe_unidades} porciones** a vender")
    else:
        st.error("### **Aumentar precio de venta** (Margen insuficiente)")

with res2:
    if isinstance(pe_unidades, int):
        st.info(f"### **S/ {pe_soles:.2f}** meta de ingresos")
    else:
        st.warning("### **S/ 0.00**")