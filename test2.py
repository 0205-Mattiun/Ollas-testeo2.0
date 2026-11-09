import streamlit as st
import math
import json
import os
import time
import shutil

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

st.title("🍲 Simulador de Punto de Equilibrio - Ollas UNACEM")

# --- GESTIÓN DINÁMICA DE OLLAS Y MULTI-CARPETAS ---
CARPETA_BASE = "historial_registros"
if not os.path.exists(CARPETA_BASE):
    os.makedirs(CARPETA_BASE)

# Obtener lista de Ollas registradas actualmente
ollas_existentes = [d for d in os.listdir(CARPETA_BASE) if os.path.isdir(os.path.join(CARPETA_BASE, d))]
if not ollas_existentes:
    os.makedirs(os.path.join(CARPETA_BASE, "Olla_1"))
    ollas_existentes = ["Olla_1"]

with st.sidebar:
    st.header("🏠 Selección de Olla Común")
    
    opciones_olla = ollas_existentes + ["➕ Registrar Nueva Olla..."]
    olla_seleccionada_menu = st.selectbox("Selecciona la Olla a trabajar:", options=opciones_olla)
    
    if olla_seleccionada_menu == "➕ Registrar Nueva Olla...":
        nueva_olla_nombre = st.text_input("Escribe el Nombre/ID de la Nueva Olla:")
        if st.button("➕ Crear Olla"):
            if nueva_olla_nombre.strip():
                clean_nom = "".join(c for c in nueva_olla_nombre if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
                ruta_nueva = os.path.join(CARPETA_BASE, clean_nom)
                if not os.path.exists(ruta_nueva):
                    os.makedirs(ruta_nueva)
                st.success(f"¡Olla '{clean_nom}' creada con éxito!")
                st.rerun()
            else:
                st.warning("Escribe un nombre válido.")
        nombre_olla_clean = "Olla_Temporal"
    else:
        nombre_olla_clean = olla_seleccionada_menu
        
        # ELIMINAR OLLA CON CONFIRMACIÓN PREVIA
        with st.expander("⚠️ Opciones de Olla"):
            st.warning(f"¿Deseas eliminar '{nombre_olla_clean.replace('_', ' ')}'?")
            confirmar_del_olla = st.checkbox("Sí, estoy seguro de eliminar esta Olla y todos sus datos", key=f"conf_del_{nombre_olla_clean}")
            
            if st.button("🗑️ Confirmar y Eliminar Olla"):
                if confirmar_del_olla:
                    ruta_olla_eliminar = os.path.join(CARPETA_BASE, nombre_olla_clean)
                    if os.path.exists(ruta_olla_eliminar):
                        shutil.rmtree(ruta_olla_eliminar)
                        st.success(f"¡Olla '{nombre_olla_clean}' y sus registros fueron eliminados!")
                        st.rerun()
                else:
                    st.error("Debes marcar la casilla 'Sí, estoy seguro' para poder eliminar.")

    # --- SECCIÓN DE RESPALDO Y CARGA DE REGISTROS ---
    st.divider()
    st.header("💾 Respaldo Anti-Suspensión")
    
    # Cargar respaldo en JSON
    archivo_subido = st.file_uploader("📤 Cargar Respaldo (.json)", type=["json"])
    if archivo_subido is not None:
        try:
            contenido = json.load(archivo_subido)
            nombre_olla_respaldo = contenido.get("olla", "Olla_Restaurada")
            ruta_restaurar = os.path.join(CARPETA_BASE, nombre_olla_respaldo)
            if not os.path.exists(ruta_restaurar):
                os.makedirs(ruta_restaurar)
            
            filename = f"{ruta_restaurar}/{int(time.time())}_{contenido.get('plato', 'Receta')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(contenido, f, ensure_ascii=False, indent=4)
            st.success("✅ ¡Registro restaurado con éxito!")
            st.rerun()
        except Exception as e:
            st.error("Error al procesar el archivo de respaldo.")

# Ruta de almacenamiento activa para la Olla seleccionada
CARPETA_OLLA = os.path.join(CARPETA_BASE, nombre_olla_clean)
if not os.path.exists(CARPETA_OLLA):
    os.makedirs(CARPETA_OLLA)

# MENÚ PRINCIPAL
modo_app = st.sidebar.radio("📌 Menú Principal", ["✏️ Crear Nueva Configuración", "📁 Ver Registros Guardados (Lectura)"])

if modo_app == "✏️ Crear Nueva Configuración":

    st.info(f"📍 Olla activa actual: **{nombre_olla_clean.replace('_', ' ')}**")
    plato_seleccionado = st.selectbox("📌 Selecciona el Plato a Evaluar:", options=list(RECETAS_DB.keys()))

    key_plato = f"receta_{plato_seleccionado}"
    if key_plato not in st.session_state:
        st.session_state[key_plato] = [dict(ins) for ins in RECETAS_DB[plato_seleccionado]["insumos"]]

    key_utensilios = f"utensilios_{plato_seleccionado}"
    if key_utensilios not in st.session_state:
        st.session_state[key_utensilios] = [dict(u) for u in RECETAS_DB[plato_seleccionado].get("utensilios", [])]

    key_rendimiento = f"rendimiento_{plato_seleccionado}"
    if key_rendimiento not in st.session_state:
        st.session_state[key_rendimiento] = RECETAS_DB[plato_seleccionado]["rendimiento_platos"]

    # BARRA LATERAL: PARÁMETROS CONTABLES
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

    st.header(f"📋 Configuración de Receta: {plato_seleccionado}")

    col_rend, _ = st.columns([1, 2])
    with col_rend:
        platos_producidos = st.number_input(
            "🥣 Rendimiento Real del Lote (N° de Porciones):",
            min_value=1,
            value=int(st.session_state[key_rendimiento]),
            step=1
        )
        st.session_state[key_rendimiento] = platos_producidos

    st.divider()

    # INSUMOS
    st.subheader("⚖️ Insumos e Ingredientes Utilizados")
    with st.expander("➕ Añadir Insumo Nuevo"):
        col_n, col_g, col_c, col_b = st.columns([2, 1, 1, 1])
        with col_n:
            nuevo_nombre = st.text_input("Nombre del Insumo:", key="nuevo_nom")
        with col_g:
            nuevo_g = st.number_input("Cantidad (g):", min_value=0.0, value=500.0, step=50.0, key="nuevo_g")
        with col_c:
            nuevo_costo = st.number_input("Costo Total (S/):", min_value=0.0, value=5.0, step=0.5, key="nuevo_costo")
        with col_b:
            st.write(" ")
            st.write(" ")
            if st.button("Guardar Insumo"):
                if nuevo_nombre.strip():
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
            if st.button("🗑️", key=f"del_ins_{item_id}"):
                eliminar_insumo_id = item_id

        total_costo_insumos += item["costo_total"]

    if eliminar_insumo_id is not None:
        st.session_state[key_plato] = [x for x in st.session_state[key_plato] if x.get("id") != eliminar_insumo_id]
        st.rerun()

    st.divider()

    # UTENSILIOS
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
            if st.button("🗑️", key=f"del_ut_{u_id}"):
                eliminar_utensilio_id = u_id

        total_costo_utensilios += u_item["costo_total"]

    if eliminar_utensilio_id is not None:
        st.session_state[key_utensilios] = [x for x in st.session_state[key_utensilios] if x.get("id") != eliminar_utensilio_id]
        st.rerun()

    # CÁLCULOS
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

    # RESULTADOS
    st.divider()
    st.header("📊 Resultados Contables en Tiempo Real")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Costo Var. Total", f"S/ {costo_variable_total:.2f}")
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

    # BOTÓN GUARDAR Y DESCARGAR
    st.divider()
    st.subheader(f"💾 Guardar Registro en: {nombre_olla_clean.replace('_', ' ')}")
    col_reg_nom, col_reg_btn = st.columns([3, 1])
    with col_reg_nom:
        nombre_registro = st.text_input("Nombre para este guardado (ej: Olla San Martin - Lote 1):", key="nom_guardado")
    with col_reg_btn:
        st.write(" ")
        st.write(" ")
        if st.button("💾 Guardar en Registro"):
            if nombre_registro.strip():
                datos_guardar = {
                    "olla": nombre_olla_clean,
                    "plato": plato_seleccionado,
                    "nombre_registro": nombre_registro.strip(),
                    "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "platos_producidos": platos_producidos,
                    "horas_trabajo": horas_trabajo,
                    "cocineras": cocineras,
                    "sueldo_hora": sueldo_hora,
                    "costo_agua": costo_agua,
                    "costo_lena": costo_lena,
                    "utilidad_deseada": utilidad_deseada,
                    "precio_venta": precio_venta,
                    "insumos": insumos_activos,
                    "utensilios": utensilios_activos,
                    "resultados": {
                        "costo_variable_total": costo_variable_total,
                        "cvu": cvu,
                        "costos_fijos": costos_fijos,
                        "pe_unidades": pe_unidades,
                        "pe_soles": pe_soles
                    }
                }
                filename = f"{CARPETA_OLLA}/{int(time.time())}_{plato_seleccionado}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(datos_guardar, f, ensure_ascii=False, indent=4)
                
                st.session_state["ultimo_guardado"] = datos_guardar
                st.success(f"✅ ¡Registro '{nombre_registro}' guardado dentro de {nombre_olla_clean.replace('_', ' ')}!")
            else:
                st.warning("Escribe un nombre para guardar.")

    if "ultimo_guardado" in st.session_state:
        json_str = json.dumps(st.session_state["ultimo_guardado"], ensure_ascii=False, indent=4)
        st.download_button(
            label="📥 Descargar copia de seguridad (.json)",
            data=json_str,
            file_name=f"Respaldo_{st.session_state['ultimo_guardado']['nombre_registro']}.json",
            mime="application/json",
            help="Descarga este archivo a tu PC/celular para restaurarlo si la página se reinicia."
        )

elif modo_app == "📁 Ver Registros Guardados (Lectura)":
    st.header(f"📂 Historial de Registros de: {nombre_olla_clean.replace('_', ' ')}")
    
    archivos = [f for f in os.listdir(CARPETA_OLLA) if f.endswith(".json")]
    
    if not archivos:
        st.info(f"No hay ninguna configuración guardada en el historial de **{nombre_olla_clean.replace('_', ' ')}**.")
    else:
        opciones_registros = {}
        for archivo in archivos:
            filepath = os.path.join(CARPETA_OLLA, archivo)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                nombre_display = f"{data.get('nombre_registro', 'Sin Nombre')} | {data.get('plato')} ({data.get('fecha')})"
                opciones_registros[nombre_display] = (archivo, data)

        reg_seleccionado = st.selectbox("🔍 Selecciona un registro para ver sus datos:", options=list(opciones_registros.keys()))
        
        if reg_seleccionado:
            archivo_actual, reg = opciones_registros[reg_seleccionado]
            
            # ELIMINAR REGISTRO CON CONFIRMACIÓN PREVIA
            with st.expander("🗑️ Eliminar este Registro Guardado"):
                st.warning(f"¿Estás seguro de eliminar el registro '{reg['nombre_registro']}'?")
                confirmar_del_reg = st.checkbox("Sí, deseo eliminar este registro permanentemente", key=f"conf_reg_{archivo_actual}")
                
                if st.button("🗑️ Confirmar Eliminación de Registro"):
                    if confirmar_del_reg:
                        filepath_borrar = os.path.join(CARPETA_OLLA, archivo_actual)
                        if os.path.exists(filepath_borrar):
                            os.remove(filepath_borrar)
                            st.success("¡Registro eliminado con éxito!")
                            st.rerun()
                    else:
                        st.error("Debes marcar la casilla 'Sí, deseo eliminar' para confirmar.")

            st.divider()
            st.subheader(f"📄 Reporte Guardado: {reg['nombre_registro']}")
            st.caption(f"Olla: **{reg.get('olla', nombre_olla_clean)}** | Plato: **{reg['plato']}** | Fecha: **{reg['fecha']}**")

            # Muestra de Resultados (Solo Lectura)
            st.subheader("📊 Resultados de la Configuración Guardada")
            res = reg["resultados"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Costo Var. Total", f"S/ {res['costo_variable_total']:.2f}")
            c2.metric("Rendimiento Lote", f"{reg['platos_producidos']} porciones")
            c3.metric("CVu", f"S/ {res['cvu']:.2f}")
            c4.metric("Costos Fijos", f"S/ {res['costos_fijos']:.2f}")

            r1, r2 = st.columns(2)
            r1.info(f"**Punto Equilibrio (Porciones a vender):** {res['pe_unidades']}")
            r2.info(f"**Punto Equilibrio (Recaudación Meta):** S/ {res['pe_soles']:.2f}")

            st.divider()
            st.subheader("🛒 Ingredientes Guardados")
            st.dataframe(reg["insumos"], use_container_width=True)

            st.subheader("🍽️ Utensilios Guardados")
            st.dataframe(reg["utensilios"], use_container_width=True)

            st.subheader("⚙️ Parámetros Fijos Registrados")
            st.json({
                "Precio de Venta Unitario": f"S/ {reg['precio_venta']}",
                "Utilidad Deseada Meta": f"S/ {reg['utilidad_deseada']}",
                "Costo Mano de Obra": f"{reg['cocineras']} cocineras x {reg['horas_trabajo']} hrs a S/ {reg['sueldo_hora']}/hr",
                "Consumo Agua": f"S/ {reg['costo_agua']}",
                "Consumo Leña/Gas": f"S/ {reg['costo_lena']}"
            })

            # Botón de descarga directa desde la vista de lectura
            json_lectura = json.dumps(reg, ensure_ascii=False, indent=4)
            st.download_button(
                label="📥 Descargar este registro (.json)",
                data=json_lectura,
                file_name=f"Registro_{reg['nombre_registro']}.json",
                mime="application/json"
            )
