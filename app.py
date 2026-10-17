import streamlit as st
import hashlib
from datetime import datetime, timedelta
from supabase import create_client, Client

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser la primera línea de Streamlit)
st.set_page_config(page_title="Pilates Studio Cloud", page_icon="🧘", layout="wide")

# 2. CONEXIÓN SEGURA A SUPABASE
@st.cache_resource
def conectar_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = conectar_supabase()
except Exception as e:
    st.error("❌ Error de conexión a la base de datos. Verifica tus Secrets.")
    st.stop()

# 3. FUNCIONES DE SEGURIDAD Y LÓGICA DE NEGOCIO
def encriptar_contrasena(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_primer_inicio():
    try:
        respuesta = supabase.table("usuarios_admin").select("*", count="exact").execute()
        return len(respuesta.data) == 0
    except Exception as e:
        return True

# --- ESTADOS DE LA SESIÓN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------------------------------------------------------
# FLUJO PRINCIPAL DE ACCESO
# ------------------------------------------------------------------

# CASO 1: CONFIGURACIÓN INICIAL (Si la tabla de administradores está vacía)
if verificar_primer_inicio():
    st.title("🛡️ Configuración Inicial del Sistema")
    st.subheader("Configura tu cuenta de Dueño/Administrador por primera vez:")
    st.info("Esta pantalla desaparecerá automáticamente una vez registres tu clave.")
    
    nuevo_usuario = st.text_input("Nombre de usuario o correo de administrador:")
    nueva_clave = st.text_input("Contraseña de acceso:", type="password")
    confirmar_clave = st.text_input("Confirma tu contraseña:", type="password")
    
    if st.button("Activar e Iniciar Sistema"):
        if not nuevo_usuario or not nueva_clave:
            st.error("❌ Por favor completa todos los campos.")
        elif nueva_clave != confirmar_clave:
            st.error("❌ Las contraseñas no coinciden.")
        elif len(nueva_clave) < 6:
            st.error("⚠️ La contraseña debe tener al menos 6 caracteres.")
        else:
            try:
                clave_segura = encriptar_contrasena(nueva_clave)
                supabase.table("usuarios_admin").insert({
                    "usuario": nuevo_usuario,
                    "contrasena_encriptada": clave_segura
                }).execute()
                st.success("¡Sistema activado con éxito! Recargando...")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al guardar el administrador: {e}")

# CASO 2: EL SISTEMA YA TIENE ENLACE SEGURO (Flujo de Operación Normal)
else:
    st.sidebar.title("🧘 Pilates Studio")
    rol_acceso = st.sidebar.radio("Menú de Perfiles:", ["👤 Alumnos", "📲 Tablet Check-in", "💼 Administrador"])
    
    # --- VISTA ALUMNOS ---
    if rol_acceso == "👤 Alumnos":
        st.title("📱 Portal del Alumno")
        telefono_alumno = st.text_input("Ingresa tu teléfono registrado para ver tu pase de acceso:")
        if telefono_alumno:
            try:
                alumno = supabase.table("alumnos").select("*").eq("telefono", telefono_alumno).execute()
                if alumno and hasattr(alumno, 'data') and alumno.data and len(alumno.data) > 0:
                    datos_alumno = alumno.data[0]
                    st.success(f"¡Hola, {datos_alumno.get('nombre', '')} {datos_alumno.get('apellido', '')}!")
                    
                    # Buscar paquetes contratados vigentes
                    paquetes_res = supabase.table("paquetes").select("*").eq("alumno_id", datos_alumno['id']).eq("estado", "Activo").execute()
                    if paquetes_res.data and len(paquetes_res.data) > 0:
                        for p in paquetes_res.data:
                            st.metric(label=f"Plan {p['modalidad_plan']} ({p['tipo_paquete']})", value=f"{p['clases_restantes']} clases")
                            st.caption(f"Vence el: {p['fecha_vencimiento']}")
                    else:
                        st.warning("⚠️ No tienes ningún paquete activo en este momento.")
                else:
                    st.error("❌ Teléfono no registrado. Por favor, inscríbete con el administrador.")
            except Exception as e:
                st.error(f"Error al consultar alumno: {e}")
                
    # --- VISTA TABLET ---
    elif rol_acceso == "📲 Tablet Check-in":
        st.title("📸 Estación de Check-in (Tablet del Local)")
        st.write("Coloca esta pantalla fija en la entrada de tu estudio.")
        st.camera_input("Muestra tu código QR frente a la cámara")
    # --- VISTA ADMINISTRADOR ---
    elif rol_acceso == "💼 Administrador":
        if not st.session_state.logged_in:
            st.title("🔐 Panel Administrativo Privado")
            user_input = st.text_input("Usuario:")
            pass_input = st.text_input("Contraseña:", type="password")
            
            if st.button("Ingresar"):
                try:
                    clave_hash = encriptar_contrasena(pass_input)
                    resultado = supabase.table("usuarios_admin").select("*").eq("usuario", user_input).eq("contrasena_encriptada", clave_hash).execute()
                    if resultado and hasattr(resultado, 'data') and resultado.data and len(resultado.data) > 0:
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas.")
                except Exception as e:
                    st.error(f"❌ Error al validar credenciales: {e}")
        else:
            st.title("💼 Panel de Control Global (Dueño)")
            if st.sidebar.button("Cerrar Sesión"):
                st.session_state.logged_in = False
                st.rerun()
                
            # Inicializar llaves de control para limpiar formularios si no existen
            if "clear_local" not in st.session_state: st.session_state.clear_local = 0
            if "clear_ins" not in st.session_state: st.session_state.clear_ins = 0
            if "clear_ren" not in st.session_state: st.session_state.clear_ren = 0
            if "clear_search" not in st.session_state: st.session_state.clear_search = 0
            if "clear_plan" not in st.session_state: st.session_state.clear_plan = 0
                
            # Definición indexada de las 5 pestañas de gestión
            pestanas = st.tabs(["🏢 Configurar Sucursales", "👥 Inscribir Alumno", "🔄 Renovaciones", "💰 Tarifas y Planes", "🔍 Consulta de Alumno"])
            
            with pestanas[0]:
                st.subheader("Alta de Locales")
                nombre_local = st.text_input("Nombre de la sede (ej: Barranco):", key=f"loc_name_{st.session_state.clear_local}")
                direccion_local = st.text_input("Dirección:", key=f"loc_dir_{st.session_state.clear_local}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Guardar Local"):
                        if nombre_local:
                            try:
                                supabase.table("locales").insert({"nombre": nombre_local, "direccion": direccion_local}).execute()
                                st.success(f"¡Sede {nombre_local} registrada exitosamente!")
                            except Exception as e:
                                st.error(f"❌ Error al guardar el local: {e}")
                        else:
                            st.error("❌ El nombre del local es obligatorio.")
                with col_btn2:
                    if st.button("Limpiar Pantalla", key="btn_clear_loc"):
                        st.session_state.clear_local += 1
                        st.rerun()
            with pestanas[1]:
                st.subheader("Formulario de Inscripción y Venta de Paquete")
                
                try:
                    locales_res = supabase.table("locales").select("id", "nombre").execute()
                    lista_locales = locales_res.data if locales_res.data else []
                    opciones_locales = {l['nombre']: l['id'] for l in lista_locales}
                    
                    planes_res = supabase.table("tipos_paquetes").select("nombre_paquete", "clases_totales", "costo").eq("activo", True).execute()
                    lista_p_db = planes_res.data if planes_res.data else []
                    opciones_planes = {p['nombre_paquete']: p['clases_totales'] for p in lista_p_db}
                    costos_planes = {p['nombre_paquete']: float(p['costo']) for p in lista_p_db}
                except Exception as e:
                    opciones_locales = {}
                    opciones_planes = {}
                    costos_planes = {}
                    st.error(f"Error al cargar catálogos desde la nube: {e}")
                
                col1, col2 = st.columns(2)
                with col1:
                    a_nombre = st.text_input("Nombre del Alumno:", key=f"ins_nom_{st.session_state.clear_ins}")
                    a_apellido = st.text_input("Apellido del Alumno:", key=f"ins_ape_{st.session_state.clear_ins}")
                    a_telefono = st.text_input("Teléfono (único para acceso móvil):", key=f"ins_tel_{st.session_state.clear_ins}")
                with col2:
                    tipo_p = st.selectbox("Selecciona el Paquete:", list(opciones_planes.keys()) if opciones_planes else ["Configura planes en la pestaña Tarifas"], key=f"ins_paq_{st.session_state.clear_ins}")
                    modalidad = st.selectbox("Modalidad de Acceso:", ["Fixed", "Flex"], key=f"ins_mod_{st.session_state.clear_ins}")
                    
                    if modalidad == "Fixed":
                        sede_assigned = st.selectbox("Sede Base / Asignada:", list(opciones_locales.keys()) if opciones_locales else ["Primero registra un local"], key=f"ins_sed_{st.session_state.clear_ins}")
                    else:
                        st.write("✨ Plan Flex seleccionado: El alumno tendrá acceso a todas las sedes libres.")
                        
                if tipo_p in costos_planes and costos_planes[tipo_p] > 0:
                    st.info(f"💵 **Valor comercial del paquete seleccionado:** ${costos_planes[tipo_p]:.2f}")
                
                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    if st.button("Registrar Alumno"):
                        if not a_nombre or not a_telefono:
                            st.error("❌ Nombre y Teléfono son campos obligatorios.")
                        elif not opciones_planes:
                            st.error("❌ No puedes registrar alumnos sin configurar planes vigentes.")
                        elif modalidad == "Fixed" and not opciones_locales:
                            st.error("❌ Debes registrar al menos un local antes de inscribir alumnos Fixed.")
                        else:
                            try:
                                nuevo_alumno = supabase.table("alumnos").insert({
                                    "nombre": a_nombre,
                                    "apellido": a_apellido,
                                    "telefono": a_telefono
                                }).execute()
                                
                                if nuevo_alumno and hasattr(nuevo_alumno, 'data') and nuevo_alumno.data and len(nuevo_alumno.data) > 0:
                                    datos_nuevo_alumno = nuevo_alumno.data[0]
                                    id_alumno = datos_nuevo_alumno['id']
                                    total_c = opciones_planes[tipo_p]
                                    
                                    fecha_vence = (datetime.now() + timedelta(days=30)).date().isoformat()
                                    id_local_fijo = opciones_locales[sede_assigned] if modalidad == "Fixed" and opciones_locales else None
                                    
                                    supabase.table("paquetes").insert({
                                        "alumno_id": id_alumno,
                                        "tipo_paquete": tipo_p,
                                        "modalidad_plan": modalidad,
                                        "local_id_fijo": id_local_fijo,
                                        "clases_totales": total_c,
                                        "clases_restantes": total_c,
                                        "fecha_vencimiento": fecha_vence,
                                        "estado": "Activo"
                                    }).execute()
                                    
                                    st.success(f"🎉 **¡Inscripción Exitosa!** Alumno **{a_nombre} {a_apellido}** dado de alta con plan **{modalidad.upper()}** y **{total_c} clases**.")
                                    st.balloons()
                            except Exception as e:
                                error_msg = str(e)
                                if "23505" in error_msg or "already exists" in error_msg.lower():
                                    st.error(f"⚠️ El alumno con el teléfono **{a_telefono}** ya se encuentra registrado.")
                                else:
                                    st.error(f"❌ Error en la inscripción: {e}")
                with col_i2:
                    if st.button("Limpiar Pantalla", key="btn_clear_ins"):
                        st.session_state.clear_ins += 1
                        st.rerun()
            with pestanas[2]:
                st.subheader("🔄 Renovar Paquete de Alumno Existente")
                
                try:
                    alumnos_res = supabase.table("alumnos").select("id", "nombre", "apellido").order("nombre").execute()
                    lista_alumnos = alumnos_res.data if alumnos_res.data else []
                    
                    opciones_alumnos = [""] + [f"{al['nombre']} {al['apellido']}" for al in lista_alumnos]
                    dicc_alumnos = {f"{al['nombre']} {al['apellido']}": al['id'] for al in lista_alumnos}
                    
                    alumno_sel = st.selectbox("Selecciona el Alumno a renovar:", opciones_alumnos, key=f"ren_sel_{st.session_state.clear_ren}", index=0)
                    
                    if alumno_sel == "":
                        st.info("💡 Por favor, busca y selecciona un alumno en el menú superior para procesar su renovación.")
                    else:
                        id_alumno_sel = dicc_alumnos[alumno_sel]
                        paquete_previo = supabase.table("paquetes").select("id", "clases_restantes", "tipo_paquete", "fecha_vencimiento").eq("alumno_id", id_alumno_sel).eq("estado", "Activo").execute()
                        
                        clases_flotantes = 0
                        if paquete_previo and hasattr(paquete_previo, 'data') and paquete_previo.data and len(paquete_previo.data) > 0:
                            info_p = paquete_previo.data[0]
                            clases_flotantes = info_p.get('clases_restantes', 0)
                            if clases_flotantes > 0:
                                st.warning(f"📢 **Aviso Operativo:** Al alumno **{alumno_sel}** aún le quedan **{clases_flotantes} clases pendientes** de su periodo anterior.")
                            else:
                                st.info(f"✅ El alumno no tiene clases pendientes.")
                        else:
                            st.info(f"✅ El alumno **{alumno_sel}** no tiene ningún paquete activo.")
                        
                        col_ren1, col_ren2 = st.columns(2)
                        with col_ren1:
                            tipo_p_nuevo = st.selectbox("Nuevo Paquete:", list(opciones_planes.keys()) if opciones_planes else ["Sin planes"], key=f"ren_p_{st.session_state.clear_ren}")
                            modalidad_nueva = st.selectbox("Nueva Modalidad de Acceso:", ["Fixed", "Flex"], key=f"ren_m_{st.session_state.clear_ren}")
                        with col_ren2:
                            if modalidad_nueva == "Fixed":
                                sede_assigned_new = st.selectbox("Asignar Sede para este periodo:", list(opciones_locales.keys()) if opciones_locales else ["Primero registra un local"], key=f"ren_s_{st.session_state.clear_ren}")
                            else:
                                st.write("✨ Plan Flex seleccionado: Acceso global habilitado.")
                        
                        if tipo_p_nuevo in costos_planes and costos_planes[tipo_p_nuevo] > 0:
                            st.info(f"💵 **Valor comercial de esta renovación:** ${costos_planes[tipo_p_nuevo]:.2f}")
                        
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            if st.button("Procesar Renovación"):
                                try:
                                    if paquete_previo and hasattr(paquete_previo, 'data') and paquete_previo.data and len(paquete_previo.data) > 0:
                                        supabase.table("paquetes").update({"estado": "Agotado"}).eq("id", paquete_previo.data[0]['id']).execute()
                                    
                                    base_nuevas = opciones_planes[tipo_p_nuevo]
                                    total_unificado = base_nuevas + clases_flotantes
                                    
                                    fecha_vence_nueva = (datetime.now() + timedelta(days=30)).date().isoformat()
                                    id_local_fijo_nuevo = opciones_locales[sede_assigned_new] if modalidad_nueva == "Fixed" and opciones_locales else None
                                    
                                    supabase.table("paquetes").insert({
                                        "alumno_id": id_alumno_sel,
                                        "tipo_paquete": tipo_p_nuevo,
                                        "modalidad_plan": modalidad_nueva,
                                        "local_id_fijo": id_local_fijo_nuevo,
                                        "clases_totales": total_unificado,
                                        "clases_restantes": total_unificado,
                                        "fecha_vencimiento": fecha_vence_nueva,
                                        "estado": "Activo"
                                    }).execute()
                                    
                                    st.success(f"🔄 **¡Renovación Exitosa!** **{alumno_sel}** cuenta con **{total_unificado} clases**.")
                                    st.balloons()
                                except Exception as e:
                                    st.error(f"❌ Error al procesar la renovación: {e}")
                        with col_r2:
                            if st.button("Limpiar Pantalla", key="btn_clear_ren"):
                                st.session_state.clear_ren += 1
                                st.rerun()
                except Exception as e:
                    st.error(f"Error en el módulo de renovación: {e}")
            with pestanas[3]:
                st.subheader("💰 Catálogo de Planes, Clases y Costos")
                
                # ACTUALIZADO: Añadida la tercera sub-pestaña para ver la lista de planes
                sub_tab1, sub_tab2, sub_tab3 = st.tabs(["➕ Crear Nuevo Plan", "📈 Modificar Costos Existentes", "📋 Lista de Planes Vigentes"])
                
                with sub_tab1:
                    st.markdown("#### Registro de Nuevas Ofertas Comerciales")
                    p_nombre = st.text_input("Nombre del nuevo paquete (ej: Plan Black 30 clases):", key=f"p_n_{st.session_state.clear_plan}")
                    p_clases = st.number_input("Cantidad exacta de clases asignadas:", min_value=1, max_value=200, value=10, key=f"p_c_{st.session_state.clear_plan}")
                    p_costo = st.number_input("Precio / Costo comercial del plan ($):", min_value=0.0, max_value=5000.0, value=250.0, step=10.0, key=f"p_v_{st.session_state.clear_plan}")
                    
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        if st.button("Dar de Alta Plan"):
                            if p_nombre:
                                try:
                                    supabase.table("tipos_paquetes").insert({
                                        "nombre_paquete": p_nombre,
                                        "clases_totales": p_clases,
                                        "costo": p_costo
                                    }).execute()
                                    st.success(f"🎉 ¡Plan '{p_nombre}' añadido al catálogo con éxito!")
                                except Exception as e:
                                    st.error(f"❌ Error al guardar el plan: {e}")
                            else:
                                st.error("El nombre del paquete es obligatorio.")
                    with col_p2:
                        if st.button("Limpiar Pantalla", key="btn_clear_plan"):
                            st.session_state.clear_plan += 1
                            st.rerun()
                            
                with sub_tab2:
                    st.markdown("#### Actualizar Precios de Planes Existentes")
                    if opciones_planes:
                        plan_a_modificar = st.selectbox("Selecciona el plan que deseas actualizar:", list(opciones_planes.keys()))
                        nuevo_precio = st.number_input("Establecer nuevo precio ($):", min_value=0.0, max_value=5000.0, value=costos_planes.get(plan_a_modificar, 0.0), step=5.0)
                        
                        if st.button("Actualizar Tarifa Comercial"):
                            try:
                                supabase.table("tipos_paquetes").update({"costo": nuevo_precio}).eq("nombre_paquete", plan_a_modificar).execute()
                                st.success(f"📈 ¡Precio del plan '{plan_a_modificar}' actualizado correctamente a ${nuevo_precio:.2f}!")
                            except Exception as e:
                                st.error(f"❌ Error al actualizar precio: {e}")
                    else:
                        st.info("No hay planes configurados para modificar.")

                # ========================================================
                # SUB-PESTAÑA 3 CORREGIDA: ORDENADA POR NOMBRE DE PLAN
                # ========================================================
                with sub_tab3:
                    st.markdown("#### Lista Completa de Planes y Precios Vigentes")
                    st.caption("💡 Puedes marcar o desmarcar la casilla 'Disponible para Venta' para ocultar o mostrar planes en los formularios.")
                    try:
                        # CORREGIDO: Ahora ordena alfabéticamente por el nombre del paquete
                        todos_planes_res = supabase.table("tipos_paquetes").select("*").order("nombre_paquete").execute()
                        if todos_planes_res.data and len(todos_planes_res.data) > 0:
                            import pandas as pd
                            df_catalogo = pd.DataFrame(todos_planes_res.data)
                            
                            # Preparamos las columnas amigables
                            df_catalogo_amigable = df_catalogo[["id", "nombre_paquete", "clases_totales", "costo", "activo"]].rename(columns={
                                "nombre_paquete": "Nombre del Paquete",
                                "clases_totales": "Clases que Incluye",
                                "costo": "Precio Comercial ($)",
                                "activo": "Disponible para Venta"
                            })
                            
                            # Convertimos la tabla en un Editor Interactivo
                            cambios_tabla = st.data_editor(
                                df_catalogo_amigable,
                                hide_index=True,
                                disabled=["id", "Nombre del Paquete", "Clases que Incluye", "Precio Comercial ($)"],
                                use_container_width=True,
                                key="editor_catalogo_planes"
                            )
                            
                            # Guardar cambios automáticamente en Supabase
                            if st.session_state.get("editor_catalogo_planes") and "edited_rows" in st.session_state.editor_catalogo_planes:
                                filas_editadas = st.session_state.editor_catalogo_planes["edited_rows"]
                                for indice_fila, cambios in filas_editadas.items():
                                    if "Disponible para Venta" in cambios:
                                        nuevo_estado = cambios["Disponible para Venta"]
                                        id_registro = int(df_catalogo_amigable.iloc[indice_fila]["id"])
                                        
                                        supabase.table("tipos_paquetes").update({"activo": nuevo_estado}).eq("id", id_registro).execute()
                                        st.success("🔄 ¡Catálogo de ventas actualizado en la nube!")
                                        st.rerun()
                        else:
                            st.info("💡 No se encontraron planes registrados en el catálogo.")
                    except Exception as e:
                        st.error(f"Error al cargar la lista de tarifas: {e}")
