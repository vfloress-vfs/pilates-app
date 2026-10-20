import streamlit as st
import hashlib
import hmac
import secrets
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
# PBKDF2 con sal aleatoria se almacena en la columna text existente.
ITERACIONES_HASH = 600_000

def encriptar_contrasena(password):
    sal = secrets.token_hex(16)
    derivado = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(sal), ITERACIONES_HASH
    ).hex()
    return f"pbkdf2_sha256${ITERACIONES_HASH}${sal}${derivado}"

def verificar_contrasena(password, hash_guardado):
    # Migra los SHA-256 anteriores al formato PBKDF2 al primer inicio de sesión válido.
    if hash_guardado and hash_guardado.startswith("pbkdf2_sha256$"):
        try:
            algoritmo, iteraciones, sal, derivado = hash_guardado.split("$", 3)
            if algoritmo != "pbkdf2_sha256":
                return False, False
            calculado = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), bytes.fromhex(sal), int(iteraciones)
            ).hex()
            return hmac.compare_digest(calculado, derivado), False
        except (ValueError, TypeError):
            return False, False
    anterior = hashlib.sha256(password.encode("utf-8")).hexdigest()
    coincide = bool(hash_guardado) and hmac.compare_digest(anterior, hash_guardado)
    return coincide, coincide

def verificar_primer_inicio():
    # Un error de conexión/permisos nunca debe habilitar el alta inicial.
    respuesta = supabase.table("usuarios_admin").select("id", count="exact").limit(1).execute()
    if respuesta.count is None:
        raise RuntimeError("Supabase no devolvió el conteo de administradores.")
    return respuesta.count == 0

# --- ESTADOS DE LA SESIÓN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------------------------------------------------------
# FLUJO PRINCIPAL DE ACCESO
# ------------------------------------------------------------------

# CASO 1: CONFIGURACIÓN INICIAL (solo si se confirma que no existen administradores)
try:
    primer_inicio = verificar_primer_inicio()
except Exception:
    st.error("No se pudo verificar la cuenta administradora. Revisa la conexión y los permisos de Supabase.")
    st.stop()

if primer_inicio:
    st.title("🛡️ Configuración Inicial del Sistema")
    st.subheader("Configura tu cuenta de Dueño/Administrador por primera vez:")
    st.info("Esta pantalla desaparecerá automáticamente una vez registres tu clave.")
    
    nuevo_usuario = st.text_input("Nombre de usuario o correo de administrador:")
    nueva_clave = st.text_input("Contraseña de acceso:", type="password")
    confirmar_clave = st.text_input("Confirma tu contraseña:", type="password")
    
    if st.button("Activar e Iniciar Sistema"):
        if not nuevo_usuario.strip() or not nueva_clave:
            st.error("❌ Por favor completa todos los campos.")
        elif nueva_clave != confirmar_clave:
            st.error("❌ Las contraseñas no coinciden.")
        elif len(nueva_clave) < 12:
            st.error("⚠️ Usa una contraseña de al menos 12 caracteres.")
        else:
            try:
                clave_segura = encriptar_contrasena(nueva_clave)
                supabase.table("usuarios_admin").insert({
                    "usuario": nuevo_usuario.strip(),
                    "contrasena_encriptada": clave_segura
                }).execute()
                st.session_state.logged_in = True
                st.success("¡Sistema activado con éxito! Abriendo el panel...")
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
                alumno = supabase.table("alumnos").select("id,nombre,apellido").eq("telefono", telefono_alumno.strip()).execute()
                if alumno and hasattr(alumno, 'data') and alumno.data and len(alumno.data) > 0:
                    datos_alumno = alumno.data[0]
                    st.success(f"¡Hola, {datos_alumno.get('nombre', '')} {datos_alumno.get('apellido', '')}!")
                    
                    # Buscar paquetes contratados vigentes
                    paquetes_res = (
                        supabase.table("paquetes")
                        .select("modalidad_plan,tipo_paquete,clases_restantes,fecha_vencimiento")
                        .eq("alumno_id", datos_alumno['id'])
                        .eq("estado", "Activo")
                        .gte("fecha_vencimiento", datetime.now().date().isoformat())
                        .execute()
                    )
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
                    resultado = (
                        supabase.table("usuarios_admin")
                        .select("id,contrasena_encriptada")
                        .eq("usuario", user_input.strip())
                        .limit(1)
                        .execute()
                    )
                    admins = resultado.data or []
                    coincide, migrar_hash = (False, False)
                    if admins:
                        coincide, migrar_hash = verificar_contrasena(
                            pass_input, admins[0]["contrasena_encriptada"]
                        )
                    if coincide:
                        if migrar_hash:
                            supabase.table("usuarios_admin").update({
                                "contrasena_encriptada": encriptar_contrasena(pass_input)
                            }).eq("id", admins[0]["id"]).execute()
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

            # LECTURA GLOBAL DE CATÁLOGOS COLECTIVOS (Variables seguras en memoria)
            try:
                locales_res = supabase.table("locales").select("id", "nombre").execute()
                lista_locales = locales_res.data if locales_res.data else []
                opciones_locales = {l['nombre']: l['id'] for l in lista_locales}
                
                planes_res = supabase.table("tipos_paquetes").select("nombre_paquete", "clases_totales", "costo").eq("activo", True).execute()
                lista_p_db = planes_res.data if planes_res.data else []
                opciones_planes = {p['nombre_paquete']: p['clases_totales'] for p in lista_p_db}
                costos_planes = {p['nombre_paquete']: float(p['costo']) for p in lista_p_db}
            except Exception as e:
                opciones_locales, opciones_planes, costos_planes = {}, {}, {}
                
            # Definición indexada exacta de las 6 pestañas unificadas de gestión
            pestanas = st.tabs(["🏢 Configurar Sucursales", "👥 Inscribir Alumno", "🔄 Renovaciones", "💰 Tarifas y Planes", "🗓️ Agenda y Horarios", "🔍 Consulta de Alumno"])
            
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
                        if not a_nombre.strip() or not a_apellido.strip() or not a_telefono.strip():
                            st.error("❌ Nombre, apellido y teléfono son campos obligatorios.")
                        elif not opciones_planes:
                            st.error("❌ No puedes registrar alumnos sin configurar planes vigentes.")
                        elif modalidad == "Fixed" and not opciones_locales:
                            st.error("❌ Debes registrar al menos un local antes de inscribir alumnos Fixed.")
                        else:
                            try:
                                nuevo_alumno = supabase.table("alumnos").insert({
                                    "nombre": a_nombre.strip(),
                                    "apellido": a_apellido.strip(),
                                    "telefono": a_telefono.strip()
                                }).select("id").execute()
                                if not nuevo_alumno.data:
                                    raise RuntimeError("No se recibió el identificador del alumno.")
                                id_alumno = nuevo_alumno.data[0]["id"]
                                total_c = opciones_planes[tipo_p]
                                fecha_vence = (datetime.now().date() + timedelta(days=30)).isoformat()
                                id_local_fijo = opciones_locales[sede_assigned] if modalidad == "Fixed" else None
                                try:
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
                                except Exception:
                                    # Compensa la primera escritura para no dejar un alumno sin paquete.
                                    supabase.table("alumnos").delete().eq("id", id_alumno).execute()
                                    raise
                                st.success(f"🎉 **¡Inscripción Exitosa!** Alumno **{a_nombre.strip()} {a_apellido.strip()}** dado de alta.")
                                st.balloons()
                            except Exception as e:
                                error_msg = str(e)
                                if "23505" in error_msg or "already exists" in error_msg.lower():
                                    st.error(f"⚠️ El alumno con el teléfono **{a_telefono}** ya se encuentra registrado.")
                                else: st.error(f"❌ Error en la inscripción: {e}")
                with col_i2:
                    if st.button("Limpiar Pantalla", key="btn_clear_ins"):
                        st.session_state.clear_ins += 1
                        st.rerun()
            with pestanas[2]:
                st.subheader("🔄 Renovar Paquete de Alumno Existente")
                try:
                    alumnos_res = supabase.table("alumnos").select("id", "nombre", "apellido", "telefono").order("nombre").execute()
                    lista_alumnos = alumnos_res.data if alumnos_res.data else []
                    etiquetas_alumnos = {
                        al["id"]: f"{al['nombre']} {al['apellido']} — {al['telefono']}"
                        for al in lista_alumnos
                    }
                    opciones_alumnos = [""] + list(etiquetas_alumnos.values())
                    dicc_alumnos = {etiquetas_alumnos[al["id"]]: al["id"] for al in lista_alumnos}
                    
                    alumno_sel = st.selectbox("Selecciona el Alumno a renovar:", opciones_alumnos, key=f"ren_sel_{st.session_state.clear_ren}", index=0)
                    
                    if alumno_sel == "":
                        st.info("💡 Por favor, busca y selecciona un alumno en el menú superior para procesar su renovación.")
                    else:
                        id_alumno_sel = dicc_alumnos[alumno_sel]
                        hoy = datetime.now().date().isoformat()
                        paquete_previo = (
                            supabase.table("paquetes")
                            .select("id,clases_restantes,fecha_vencimiento")
                            .eq("alumno_id", id_alumno_sel)
                            .eq("estado", "Activo")
                            .gte("fecha_vencimiento", hoy)
                            .execute()
                        )
                        paquetes_vigentes = paquete_previo.data or []
                        clases_flotantes = sum(max(0, p.get("clases_restantes") or 0) for p in paquetes_vigentes)
                        if clases_flotantes > 0:
                            st.warning(f"📢 **Aviso Operativo:** Al alumno **{alumno_sel}** le quedan **{clases_flotantes} clases vigentes** que se sumarán al renovar.")
                        
                        col_ren1, col_ren2 = st.columns(2)
                        with col_ren1:
                            tipo_p_nuevo = st.selectbox("Nuevo Paquete:", list(opciones_planes.keys()) if opciones_planes else ["Sin planes"], key=f"ren_p_{st.session_state.clear_ren}")
                            modalidad_nueva = st.selectbox("Nueva Modalidad de Acceso:", ["Fixed", "Flex"], key=f"ren_m_{st.session_state.clear_ren}")
                        with col_ren2:
                            if modalidad_nueva == "Fixed":
                                sede_assigned_new = st.selectbox("Asignar Sede para este periodo:", list(opciones_locales.keys()) if opciones_locales else ["Primero registra un local"], key=f"ren_s_{st.session_state.clear_ren}")
                            else: st.write("✨ Plan Flex seleccionado: Acceso global habilitado.")
                        
                        if tipo_p_nuevo in costos_planes and costos_planes[tipo_p_nuevo] > 0:
                            st.info(f"💵 **Valor comercial de esta renovación:** ${costos_planes[tipo_p_nuevo]:.2f}")
                        
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            if st.button("Procesar Renovación"):
                                try:
                                    if not opciones_planes or tipo_p_nuevo not in opciones_planes:
                                        st.error("❌ Selecciona un plan vigente antes de renovar.")
                                    elif modalidad_nueva == "Fixed" and (not opciones_locales or sede_assigned_new not in opciones_locales):
                                        st.error("❌ Selecciona una sede válida para el plan Fixed.")
                                    else:
                                        base_nuevas = opciones_planes[tipo_p_nuevo]
                                        total_unificado = base_nuevas + clases_flotantes
                                        fecha_vence_nueva = (datetime.now().date() + timedelta(days=30)).isoformat()
                                        id_local_fijo_nuevo = opciones_locales[sede_assigned_new] if modalidad_nueva == "Fixed" else None
                                        paquete_nuevo = supabase.table("paquetes").insert({
                                            "alumno_id": id_alumno_sel, "tipo_paquete": tipo_p_nuevo, "modalidad_plan": modalidad_nueva,
                                            "local_id_fijo": id_local_fijo_nuevo, "clases_totales": total_unificado, "clases_restantes": total_unificado,
                                            "fecha_vencimiento": fecha_vence_nueva, "estado": "Activo"
                                        }).select("id").execute()
                                        if not paquete_nuevo.data:
                                            raise RuntimeError("No se recibió el identificador del paquete renovado.")
                                        try:
                                            if paquetes_vigentes:
                                                supabase.table("paquetes").update({"estado": "Agotado"}).in_(
                                                    "id", [p["id"] for p in paquetes_vigentes]
                                                ).execute()
                                        except Exception:
                                            supabase.table("paquetes").delete().eq("id", paquete_nuevo.data[0]["id"]).execute()
                                            raise
                                        st.success(f"🔄 ¡Renovación Exitosa! **{alumno_sel}** cuenta con **{total_unificado} clases**.")
                                        st.balloons()
                                except Exception as e: st.error(f"❌ Error al procesar la renovación: {e}")
                        with col_r2:
                            if st.button("Limpiar Pantalla", key="btn_clear_ren"):
                                st.session_state.clear_ren += 1
                                st.rerun()
                except Exception as e: st.error(f"Error: {e}")

            with pestanas[3]:
                st.subheader("💰 Catálogo de Planes, Clases y Costos")
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
                                    supabase.table("tipos_paquetes").insert({"nombre_paquete": p_nombre, "clases_totales": p_clases, "costo": p_costo}).execute()
                                    st.success(f"🎉 ¡Plan '{p_nombre}' añadido al catálogo con éxito!")
                                except Exception as e: st.error(f"❌ Error al guardar el plan: {e}")
                            else: st.error("El nombre del paquete es obligatorio.")
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
                            except Exception as e: st.error(f"❌ Error al actualizar precio: {e}")
                    else: st.info("No hay planes configurados para modificar.")

                with sub_tab3:
                    st.markdown("#### Lista de Tarifas Ordenadas de Mayor a Menor Precio")
                    try:
                        todos_planes_res = supabase.table("tipos_paquetes").select("*").order("costo", desc=True).execute()
                        if todos_planes_res.data and len(todos_planes_res.data) > 0:
                            import pandas as pd
                            df_catalogo = pd.DataFrame(todos_planes_res.data)
                            df_catalogo_amigable = df_catalogo[["id", "nombre_paquete", "clases_totales", "costo", "activo"]].rename(columns={
                                "nombre_paquete": "Nombre del Paquete", "clases_totales": "Clases que Incluye", "costo": "Precio Comercial ($)", "activo": "Disponible para Venta"
                            })
                            cambios_tabla = st.data_editor(df_catalogo_amigable, hide_index=True, disabled=["id", "Nombre del Paquete", "Clases que Incluye", "Precio Comercial ($)"], use_container_width=True, key="editor_catalogo_planes")
                            if st.session_state.get("editor_catalogo_planes") and "edited_rows" in st.session_state.editor_catalogo_planes:
                                filas_editadas = st.session_state.editor_catalogo_planes["edited_rows"]
                                for indice_fila, cambios in filas_editadas.items():
                                    if "Disponible para Venta" in cambios:
                                        nuevo_estado = cambios["Disponible para Venta"]
                                        id_registro = int(df_catalogo_amigable.iloc[indice_fila]["id"])
                                        supabase.table("tipos_paquetes").update({"activo": nuevo_estado}).eq("id", id_registro).execute()
                                        st.success("🔄 ¡Catálogo de ventas actualizado en la nube!")
                                        st.rerun()
                        else: st.info("💡 No se encontraron planes registrados.")
                    except Exception as e: st.error(f"Error: {e}")
                    
            with pestanas[4]:
                st.subheader("🗓️ Control de Agenda, Clases e Inactividades")
                sub_agenda1, sub_agenda2, sub_agenda3, sub_agenda4 = st.tabs([
                    "👩 Registrar Instructoras", "📅 Programación Masiva de Horarios", "📅 Días Laborales", "🌴 Feriados / Festivos"
                ])
                
                with sub_agenda1:
                    st.markdown("#### Alta de Profesoras y Tarifas por Hora")
                    inst_nombre = st.text_input("Nombre completo de la Instructora:")
                    inst_telefono = st.text_input("Teléfono de contacto:")
                    inst_costo = st.number_input("Costo / Tarifa por hora dictada ($):", min_value=0.0, value=50.0, step=5.0)
                    if st.button("Guardar Instructora"):
                        if inst_nombre:
                            try:
                                supabase.table("instructoras").insert({"nombre": inst_nombre, "telefono": inst_telefono, "costo_hora": inst_costo}).execute()
                                st.success(f"🎉 Instructora '{inst_nombre}' registrada con éxito.")
                            except Exception as e: st.error(f"❌ Error al guardar instructora: {e}")
                        else: st.error("El nombre es obligatorio.")
                            
                with sub_agenda2:
                    st.markdown("#### 🚀 Generador Automatizado de Calendario Mensual")
                    try:
                        dias_db = supabase.table("dias_operativos").select("nombre_dia", "numero_dia", "habilitado").execute()
                        dias_habilitados = {d['numero_dia']: d['habilitado'] for d in dias_db.data} if dias_db.data else {}
                        
                        inst_res = supabase.table("instructoras").select("id", "nombre").eq("activo", True).execute()
                        lista_inst = inst_res.data if inst_res.data else []
                        opciones_inst = {ins['nombre']: ins['id'] for ins in lista_inst}
                        
                        col_mas1, col_mas2 = st.columns(2)
                        with col_mas1:
                            sede_agenda = st.selectbox("Selecciona Sede:", list(opciones_locales.keys()) if opciones_locales else ["No hay locales"], key="mas_sede")
                            fecha_inicio = st.date_input("Fecha de Inicio:", min_value=datetime.now().date(), key="mas_f_ini")
                            fecha_fin = st.date_input("Fecha de Fin:", value=datetime.now().date() + timedelta(days=30), key="mas_f_fin")
                            hora_agenda = st.time_input("Hora de Inicio:", key="mas_hora")
                        with col_mas2:
                            inst_agenda = st.selectbox("Asignar Instructora:", list(opciones_inst.keys()) if opciones_inst else ["Primero registra una instructora"], key="mas_inst")
                            tipo_serv_agenda = st.selectbox("Tipo de Sesión:", ["Grupal", "Privado"], key="mas_tipo")
                            if tipo_serv_agenda == "Grupal":
                                aforo_agenda = st.number_input("Aforo Máximo Camillas:", min_value=4, max_value=10, value=4, key="mas_aforo")
                            else: aforo_agenda = 1
                        
                        dias_seleccionados = []
                        col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns(5)
                        with col_d1: 
                            if st.checkbox("Lunes", value=True): dias_seleccionados.append(0)
                        with col_d2: 
                            if st.checkbox("Martes", value=True): dias_seleccionados.append(1)
                        with col_d3: 
                            if st.checkbox("Miércoles", value=True): dias_seleccionados.append(2)
                        with col_d4: 
                            if st.checkbox("Jueves", value=True): dias_seleccionados.append(3)
                        with col_d5: 
                            if st.checkbox("Viernes", value=True): dias_seleccionados.append(4)
                        
                        if st.button("⚡ Calcular fechas elegibles"):
                            if not opciones_locales or not opciones_inst: st.error("❌ Se requieren locales e instructoras.")
                            elif fecha_inicio > fecha_fin: st.error("❌ Rango inválido.")
                            elif not dias_seleccionados: st.error("❌ Selecciona al menos un día.")
                            else:
                                feriados_db = supabase.table("feriados").select("fecha").execute()
                                lista_feriados = [f['fecha'] for f in feriados_db.data] if feriados_db.data else []
                                total_creadas = 0
                                fecha_actual = fecha_inicio
                                while fecha_actual <= fecha_fin:
                                    num_dia = fecha_actual.weekday()
                                    if num_dia in dias_seleccionados and dias_habilitados.get(num_dia, False) and (fecha_actual.isoformat() not in lista_feriados):
                                        total_creadas += 1
                                    fecha_actual += timedelta(days=1)
                                st.info(f"Se encontraron **{total_creadas} fechas elegibles**. Este cálculo no crea ni publica clases en la base de datos.")
                    except Exception as e: st.error(f"Error: {e}")

                with sub_agenda3:
                    st.markdown("#### Configuración de Días Laborales del Estudio")
                    try:
                        dias_consulta = supabase.table("dias_operativos").select("*").order("numero_dia").execute()
                        if dias_consulta.data:
                            import pandas as pd
                            df_dias = pd.DataFrame(dias_consulta.data)
                            df_dias_amigable = df_dias[["id", "nombre_dia", "habilitado"]].rename(columns={"nombre_dia": "Día de la Semana", "habilitado": "Estudio Abierto"})
                            cambios_dias = st.data_editor(df_dias_amigable, hide_index=True, disabled=["id", "Día de la Semana"], use_container_width=True, key="editor_dias_operativos")
                            if st.session_state.get("editor_dias_operativos") and "edited_rows" in st.session_state.editor_dias_operativos:
                                filas_edit_dias = st.session_state.editor_dias_operativos["edited_rows"]
                                for idx_fila, cambio_dia in filas_edit_dias.items():
                                    if "Estudio Abierto" in cambio_dia:
                                        supabase.table("dias_operativos").update({"habilitado": cambio_dia["Estudio Abierto"]}).eq("id", int(df_dias_amigable.iloc[idx_fila]["id"])).execute()
                                        st.success("🔄 ¡Calendario laboral actualizado!")
                                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

                with sub_agenda4:
                    st.markdown("#### Registro y Eliminación Interactiva de Días Festivos")
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        fecha_f = st.date_input("Fecha del Feriado:", key="input_fecha_feriado")
                        desc_f = st.text_input("Descripción del Festivo:", key="input_desc_feriado")
                        if st.button("Habilitar Feriado"):
                            if desc_f:
                                try:
                                    supabase.table("feriados").insert({"fecha": fecha_f.isoformat(), "descripcion": desc_f}).execute()
                                    st.success(f"🌴 ¡Fecha {fecha_f} bloqueada!")
                                    st.rerun()
                                except Exception as e: st.error(f"❌ Ya registrado o error: {e}")
                            else: st.error("Agrega una descripción.")
                    with col_f2:
                        try:
                            feriados_res = supabase.table("feriados").select("*").order("fecha").execute()
                            if feriados_res.data:
                                import pandas as pd
                                df_fer = pd.DataFrame(feriados_res.data)
                                df_fer["Eliminar"] = False
                                df_fer_amigable = df_fer[["id", "fecha", "descripcion", "Eliminar"]].rename(columns={"fecha": "Fecha Bloqueada", "descripcion": "Festivo / Motivo"})
                                cambios_feriados = st.data_editor(df_fer_amigable, hide_index=True, disabled=["id", "Fecha Bloqueada", "Festivo / Motivo"], use_container_width=True, key="editor_tabla_feriados")
                                if st.session_state.get("editor_tabla_feriados") and "edited_rows" in st.session_state.editor_tabla_feriados:
                                    filas_edit_fer = st.session_state.editor_tabla_feriados["edited_rows"]
                                    for idx_f, cambio_f in filas_edit_fer.items():
                                        if "Eliminar" in cambio_f and cambio_f["Eliminar"] == True:
                                            id_fer_borrar = int(df_fer_amigable.iloc[idx_f]["id"])
                                            supabase.table("feriados").delete().eq("id", id_fer_borrar).execute()
                                            st.success("🗑️ ¡Feriado eliminado!")
                                            st.rerun()
                            else: st.info("No hay feriados agendados.")
                        except Exception as e: st.error(f"Error: {e}")

            # --- PESTAÑA 5 PROTEGIDA CONTRA CORTES SINTÁCTICOS (ÍNDICE NUMÉRICO 5 ESTABLECIDO) ---
            with pestanas[5]:
                st.subheader("🔍 Kárdex e Historial de Clases de Alumno")
                
                try:
                    todos_al_res = supabase.table("alumnos").select("*").order("nombre").execute()
                    lista_alumnos_all = todos_al_res.data if todos_al_res.data else []
                except Exception as e:
                    lista_alumnos_all = []
                    st.error(f"Error al conectar con el directorio: {e}")
                
                telefono_seleccionado = None
                
                if lista_alumnos_all:
                    import pandas as pd
                    df_dir = pd.DataFrame(lista_alumnos_all)
                    
                    busqueda_nombre = st.text_input("🔍 Escribe el nombre o apellido del alumno para filtrar la lista:", key="input_predictivo_nombre")
                    
                    if busqueda_nombre:
                        df_dir = df_dir[
                            df_dir['nombre'].str.contains(busqueda_nombre, case=False, na=False) | 
                            df_dir['apellido'].str.contains(busqueda_nombre, case=False, na=False)
                        ]
                    if not df_dir.empty:
                        df_dir["Ver Kárdex"] = False
                        df_dir_visual = df_dir[["nombre", "apellido", "telefono", "fecha_registro", "Ver Kárdex"]].rename(columns={
                            "nombre": "Nombre", "apellido": "Apellido", "telefono": "Teléfono", "fecha_registro": "Fecha Registro"
                        })
                        
                        editor_directorio = st.data_editor(
                            df_dir_visual,
                            hide_index=True,
                            disabled=["Nombre", "Apellido", "Teléfono", "Fecha Registro"],
                            use_container_width=True,
                            key="directorio_general_alumnos"
                        )
                        
                        # CAPTURA DE SELECCIÓN INMEDIATA (Funciona con listas completas o filtradas)
                        if st.session_state.get("directorio_general_alumnos") and "edited_rows" in st.session_state.directorio_general_alumnos:
                            filas_tocadas = st.session_state.directorio_general_alumnos["edited_rows"]
                            for fila_idx, estado_casilla in filas_tocadas.items():
                                if estado_casilla.get("Ver Kárdex") == True:
                                    telefono_seleccionado = df_dir_visual.iloc[fila_idx]["Teléfono"]
                        
                        # Despliegue del Kárdex 360° unificado dentro del mismo bloque formal de la pestaña
                        if telefono_seleccionado:
                            st.markdown("---")
                            try:
                                al_res = supabase.table("alumnos").select("*").eq("telefono", telefono_seleccionado).execute()
                                if al_res.data and len(al_res.data) > 0:
                                    data_al = al_res.data[0]
                                    st.markdown(f"### 📊 Ficha de Control: **{data_al['nombre']} {data_al['apellido']}**")
                                    st.markdown(f"📱 **Contacto:** {data_al['telefono']}")
                                    
                                    # Historial de Membresías
                                    paq_res = supabase.table("paquetes").select("*").eq("alumno_id", data_al['id']).order("fecha_compra", desc=True).execute()
                                    if paq_res.data and len(paq_res.data) > 0:
                                        st.markdown("#### 📋 Historial de Paquetes y Membresías")
                                        df_paq = pd.DataFrame(paq_res.data)
                                        df_paq["Clases Consumidas"] = df_paq["clases_totales"] - df_paq["clases_restantes"]
                                        df_reporte_paq = df_paq[["tipo_paquete", "modalidad_plan", "clases_totales", "Clases Consumidas", "clases_restantes", "fecha_vencimiento", "estado"]].rename(columns={
                                            "tipo_paquete": "Paquete Contratado", "modalidad_plan": "Tipo Plan", "clases_totales": "Clases Totales", "clases_restantes": "Clases Pendientes (Saldo)", "fecha_vencimiento": "Caduca El", "estado": "Estado Plan"
                                        })
                                        st.dataframe(df_reporte_paq, use_container_width=True, hide_index=True)
                                        
                                    # Bitácora de Asistencias
                                    res_res = supabase.table("reservas").select("fecha_clase", "hora_clase", "tipo_servicio", "estado").eq("alumno_id", data_al['id']).order("fecha_clase", desc=True).execute()
                                    st.markdown("#### 🗓️ Bitácora de Clases y Asistencia Diaria")
                                    if res_res.data and len(res_res.data) > 0:
                                        df_res = pd.DataFrame(res_res.data).rename(columns={"fecha_clase": "Fecha de Clase", "hora_clase": "Horario", "tipo_servicio": "Modalidad", "estado": "Asistencia"})
                                        st.dataframe(df_res, use_container_width=True, hide_index=True)
                                    else:
                                        st.info("💡 El alumno aún no tiene un historial de asistencias en la agenda.")
                            except Exception as e:
                                st.error(f"Error al cargar la ficha del alumno: {e}")
                    else:
                        st.warning("⚠️ No se encontraron alumnos que coincidan con la búsqueda.")
                else:
                    st.info("💡 Aún no registras ningún alumno en el sistema.")
