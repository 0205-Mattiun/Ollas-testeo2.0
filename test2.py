import streamlit as st
import math

# Configuración de la página
st.set_page_config(
    page_title="Simulador por Producto - Ollas UNACEM",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BASE DE DATOS INICIAL DE RECETAS ---
RECETAS_DB = {
    "SOPA DE MOTE": {
        "rendimiento_platos": 70,
        "insumos": [
            {"id": "ins_1", "nombre": "Mote seco", "cantidad_g": 5000.0, "costo_total": 30.00},
            {"id": "ins_2", "nombre": "Mondongo", "cantidad_g": 1500.0, "costo_total": 21.00},
            {"id": "ins_3", "nombre": "Piltrafa", "cantidad_g": 1500.0, "costo_total": 22.50},
            {"id": "ins_4", "nombre": "Huesos de manzana", "cantidad_g": 4000.0, "costo_total": 12.00},
            {"id": "ins_5", "nombre": "Pata de vaca", "cantidad_g": 1000.0, "costo_total": 22.00},
            {"id": "ins_6", "nombre": "Arroz", "cantidad_g": 300.0, "costo_total": 1.50},
            {"id": "ins_7", "nombre": "Cebolla (1 un)", "cantidad_g": 200.0, "costo_total": 2.00},
            {"id": "ins_8", "nombre": "Ajo (1 un)", "cantidad_g": 50.0, "costo_total": 1.00},
            {"id": "ins_9", "nombre": "Perejil", "cantidad_g": 100.0, "costo_total": 2.00},
            {"id": "ins_10", "nombre": "Orégano", "cantidad_g": 50.0, "costo_total": 2.00},
            {"id": "ins_11", "nombre": "Hierbabuena", "cantidad_g": 100.0, "costo_total": 2.00},
            {"id": "ins_12", "nombre": "Limón", "cantidad_g": 500.0, "costo_total": 2.00},
            {"id": "ins_13", "nombre": "Rocoto", "cantidad_g": 500.0, "costo_total": 3.50},
            {"id": "ins_14", "nombre": "Sal", "cantidad_g": 500.0, "costo_total": 2.00}
        ],
        "utensilios": [
            {"id": "ut_1", "nombre": "Platos descartables", "costo_total": 8.00},
            {"id": "ut_2", "nombre": "Cucharas descartables", "costo_total": 8.00},
            {"id": "ut_3", "nombre": "Servilletas", "costo_total": 2.00}
        ]
    },
    "YUCA RELLENA": {
        "rendimiento_platos": 70,
        "insumos": [
            {"id": "ins_20", "nombre": "Yuca amarilla", "cantidad_g": 5000.0, "costo_total": 20.00},
            {"id": "ins_21", "nombre": "Harina de chuño", "cantidad_g": 1000.0, "costo_total": 10.00},
            {"id": "ins_22", "nombre": "Carne molida", "cantidad_g": 3000.0, "costo_total": 66.00},
            {"id": "ins_23", "nombre": "Cebolla", "cantidad_g": 4000.0, "costo_total": 8.00},
            {"id": "ins_24", "nombre": "Ají panca", "cantidad_g": 100.0, "costo_total": 2.50},
            {"id": "ins_25", "nombre": "Especias (Pimienta, Orégano, Comino)", "cantidad_g": 50.0, "costo_total": 2.00},
            {"id": "ins_26", "nombre": "Ajo", "cantidad_g": 100.0, "costo_total": 2.00},
            {"id": "ins_27", "nombre": "Huevo", "cantidad_g": 500.0, "costo_total": 4.00}
        ],
        "utensilios": [
            {"id": "ut_20", "nombre": "Platos descartables", "costo_total": 8.00},
            {"id": "ut_21", "nombre": "Servilletas", "costo_total": 2.00}
        ]
    }
}

st.title("🍲 Simulador de Punto de Equilibrio por Producto")
st.subheader("Proyecto Ollas UNACEM")

# --- SELECCIÓN DE PRODUCTO Y CONTROL EN SESSION STATE ---
plato_seleccionado = st.selectbox(
    "📌 Selecciona el Plato a Evaluar:",
    options=list(RECETAS_DB.keys())
)

# Inicializar insumos en session_state con copia profunda
key_plato = f"receta_{plato_seleccionado}"
if key_plato not in st.session_state:
    st.session_state[key_plato] = [dict(ins) for ins in RECETAS_DB[plato_seleccionado]["insumos"]]

# Inicializar utensilios en session_state
key_utensilios = f"utensilios_{plato_seleccionado}"
if key_utensilios not in st.session_state:
    st.session_state[key_utensilios] = [dict(u) for u in RECETAS_DB[plato_seleccionado].get("utensilios", [])]

# Inicializar rendimiento
key_rendimiento = f"rendimiento_{plato_seleccionado}"
if key_rendimiento not in st.session_state:
    st.session_state[key_rendimiento] = RECETAS_DB[plato_seleccionado]["rendimiento_platos"]

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

# --- CONFIGURACIÓN DEL RENDIMIENTO DEL LOTE ---
st.header(f"📋 Configuración de Receta: {plato_seleccionado}")

col_rend, _ = st.columns([1, 2])
with col_rend:
    platos_producidos = st.number_input(
        "🥣 Rendimiento Real del Lote (N° de Porciones que salen):",
        min_value=1,
        value=int(st.session_state[key_rendimiento]),
        step=1,
        help="Ajusta el total de platos/porciones que produce esta olla específica."
    )
    st.session_state[key_rendimiento] = platos_producidos

st.divider()

# --- EDICIÓN E INGRESO DINÁMICO DE INSUMOS ---
st.subheader("⚖️ Insumos e Ingredientes Utilizados")

with st.expander("➕ Añadir Insumo Nuevo a esta Olla"):
    col_n, col_g, col_c, col_b = st.columns([2, 1, 1, 1])
    with col_n:
        nuevo_nombre = st.text_input("Nombre del Insumo (ej. Chuño, Pimiento):", key="nuevo_nom")
    with col_g:
        nuevo_g = st.number_input("Cantidad (g):", min_value=0.0, value=500.0, step=50.0, key="nuevo_g")
    with col_c:
        nuevo_costo = st.number_input("Costo Total Insumo (S/):", min_value=0.0, value=5.0, step=0.5, key="nuevo_costo")
    with col_b:
        st.write(" ")
        st.write(" ")
        if st.button("Guardar Insumo"):
            if nuevo_nombre.strip():
                import time
                nuevo_id = f"ins_{int(time.time()*1000)}"
                st.session_state[key_plato].append({
                    "id": nuevo_id,
                    "nombre": nuevo_nombre.strip(),
                    "cantidad_g": nuevo_g,
                    "costo_total": nuevo_costo
                })
                st.rerun()

insumos_activos = st.session_state[key_plato]
total_costo_insumos = 0.0
total_gramos_insumos = 0.0

eliminar_insumo_id = None

for idx, item in enumerate(insumos_activos):
    item_id = item.get("id", f"ins_idx_{idx}")
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
    
    with c1:
        st.text_input(f"Ingrediente #{idx+1}", value=item["nombre"], key=f"nom_{item_id}", disabled=True)
    with c2:
        g_val = st.number_input(f"Gramos (g)", min_value=0.0, value=float(item["cantidad_g"]), step=50.0, key=f"g_{item_id}")
        item["cantidad_g"] = g_val
    with c3:
        costo_val = st.number_input(f"Costo Total (S/)", min_value=0.0, value=float(item["costo_total"]), step=0.5, key=f"c_{item_id}")
        item["costo_total"] = costo_val
    with c4:
        st.write(" ")
        st.write(" ")
        if st.button("🗑️", key=f"del_ins_{item_id}", help="Quitar este insumo"):
            eliminar_insumo_id = item_id

    total_costo_insumos += item["costo_total"]
    total_gramos_insumos += item["cantidad_g"]

if eliminar_insumo_id is not None:
    st.session_state[key_plato] = [x for x in st.session_state[key_plato] if x.get("id") != eliminar_insumo_id]
    st.rerun()

st.divider()

# --- SECCIÓN DE UTENSILIOS Y OTROS ---
st.subheader("🍽️ Utensilios y otros")

with st.expander("➕ Añadir Utensilio u otro"):
    col_un, col_uc, col_ub = st.columns([3, 2, 1])
    with col_un:
        u_nombre = st.text_input("Nombre:", key="u_nom")
    with col_uc:
        u_costo = st.number_input("Costo Total (S/):", min_value=0.0, value=4.0, step=0.5, key="u_costo")
    with col_ub:
        st.write(" ")
        st.write(" ")
        if st.button("Guardar Item"):
            if u_nombre.strip():
                import time
                u_id = f"ut_{int(time.time()*1000)}"
                st.session_state[key_utensilios].append({
                    "id": u_id,
                    "nombre": u_nombre.strip(),
                    "costo_total": u_costo
                })
                st.rerun()

utensilios_activos = st.session_state[key_utensilios]
total_costo_utensilios = 0.0

eliminar_utensilio_id = None

for idx, u_item in enumerate(utensilios_activos):
    u_id = u_item.get("id", f"ut_idx_{idx}")
    uc1, uc2, uc3 = st.columns([4, 3, 1])
    
    with uc1:
        st.text_input(f"Item #{idx+1}", value=u_item["nombre"], key=f"unom_{u_id}", disabled=True)
    with uc2:
        ucosto_val = st.number_input(f"Costo Total (S/)", min_value=0.0, value=float(u_item["costo_total"]), step=0.5, key=f"uc_{u_id}")
        u_item["costo_total"] = ucosto_val
    with uc3:
        st.write(" ")
        st.write(" ")
        if st.button("🗑️", key=f"del_ut_{u_id}", help="Quitar este item"):
            eliminar_utensilio_id = u_id

    total_costo_utensilios += u_item["costo_total"]

if eliminar_utensilio_id is not None:
    st.session_state[key_utensilios] = [x for x in st.session_state[key_utensilios] if x.get("id") != eliminar_utensilio_id]
    st.rerun()

# --- CÁLCULOS CONTABLES AUTOMÁTICOS ---
costo_variable_total = total_costo_insumos + total_costo_utensilios
cvu = costo_variable_total / platos_producidos if platos_producidos > 0 else 0.0
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

m1, m2, m3, m4 = st.columns(4)
m1.metric("Costo Var. Total (Insumos + Utensilios y otros)", f"S/ {costo_variable_total:.2f}")
m2.metric("Rendimiento del Lote", f"{platos_producidos} porciones")
m3.metric("Costo Var. Unitario (CVu)", f"S/ {cvu:.2f}")
m4.metric("Costos Fijos Totales (CF)", f"S/ {costos_fijos:.2f}")

st.subheader("🎯 Punto de Equilibrio y Recaudación Meta")
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
