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
                
            # Definición de las 4 pestañas de gestión (Añadida la pestaña de Consulta)
            pestanas = st.tabs(["🏢 Configurar Sucursales", "👥 Inscribir Alumno", "🔄 Renovaciones", "🔍 Consulta de Alumno"])
            
            with pestanas[0]:
                st.subheader("Alta de Locales")
                nombre_local = st.text_input("Nombre de la sede (ej: Barranco):", key="new_local_name")
                direccion_local = st.text_input("Dirección:", key="new_local_dir")
                if st.button("Guardar Local"):
                    if nombre_local:
                        try:
                            supabase.table("locales").insert({"nombre": nombre_local, "direccion": direccion_local}).execute()
                            st.success(f"¡Sede {nombre_local} registrada exitosamente!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al guardar el local: {e}")
                    else:
                        st.error("❌ El nombre del local es obligatorio.")
                        
            with pestanas[1]:
                st.subheader("Formulario de Inscripción y Venta de Paquete")
                
                try:
                    locales_res = supabase.table("locales").select("id", "nombre").execute()
                    lista_locales = locales_res.data if locales_res.data else []
                    opciones_locales = {l['nombre']: l['id'] for l in lista_locales}
                except Exception as e:
                    opciones_locales = {}
                    st.error(f"Error al cargar locales: {e}")
                
                col1, col2 = st.columns(2)
                with col1:
                    a_nombre = st.text_input("Nombre del Alumno:")
                    a_apellido = st.text_input("Apellido del Alumno:")
                    a_telefono = st.text_input("Teléfono (único para acceso móvil):")
                with col2:
                    tipo_p = st.selectbox("Selecciona el Paquete:", ["4 clases", "8 clases", "12 clases", "Mes completo", "Privado"])
                    modalidad = st.selectbox("Modalidad de Acceso:", ["Fixed", "Flex"])
                    
                    if modalidad == "Fixed":
                        sede_assigned = st.selectbox("Sede Base / Asignada:", list(opciones_locales.keys()) if opciones_locales else ["Primero registra un local"])
                    else:
                        st.write("✨ Plan Flex seleccionado: El alumno tendrá acceso a todas las sedes libres.")
                
                if st.button("Registrar Alumno y Cargar Créditos"):
                    if not a_nombre or not a_telefono:
                        st.error("❌ Nombre y Teléfono son campos obligatorios.")
                    elif modalidad == "Fixed" and not opciones_locales:
                        st.error("❌ Debes registrar al menos un local en la pestaña anterior antes de inscribir alumnos Fixed.")
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
                                
                                mapeo_clases = {"4 clases": 4, "8 clases": 8, "12 clases": 12, "Mes completo": 999, "Privado": 8}
                                total_c = mapeo_clases[tipo_p]
                                
                                fecha_vence = (datetime.now() + timedelta(days=30)).date().isoformat()
                                id_local_fijo = opciones_locales[sede_assigned] if modalidad == "Fixed" and opciones_locales else None
                                
                                supabase.table("paquetes").insert({
                                    "alumno_id": id_alumno,
                                    "tipo_paquete": tipo_p,
                                    "modalidad_plan": modalidad,
                                    "local_id_fijo": id_local_fijo,
                                    "clases_totales": total_c,
                                    "clases_restantes": total_c,
                                    "fecha_vencimiento": fecha_vence
                                }).execute()
                                
                                st.success(f"🎉 ¡Alumno {a_nombre} {a_apellido} registrado con éxito! Se cargaron sus {total_c} clases.")
                                st.rerun()
                        except Exception as e:
                            error_msg = str(e)
                            if "23505" in error_msg or "already exists" in error_msg.lower():
                                st.error(f"⚠️ El alumno con el teléfono **{a_telefono}** ya se encuentra registrado en el sistema.")
                            else:
                                st.error(f"❌ Error en la inscripción: {e}")
            with pestanas[2]:
                st.subheader("🔄 Renovar Paquete de Alumno Existente")
                
                try:
                    alumnos_res = supabase.table("alumnos").select("id", "nombre", "apellido").order("nombre").execute()
                    lista_alumnos = alumnos_res.data if alumnos_res.data else []
                    dicc_alumnos = {f"{al['nombre']} {al['apellido']}": al['id'] for al in lista_alumnos}
                    
                    if not dicc_alumnos:
                        st.info("Aún no tienes alumnos registrados para poder renovar.")
                    else:
                        alumno_sel = st.selectbox("Selecciona el Alumno a renovar:", list(dicc_alumnos.keys()))
                        id_alumno_sel = dicc_alumnos[alumno_sel]
                        
                        # AVISO DE CLASES PENDIENTES ANTES DE RENOVAR
                        paquete_previo = supabase.table("paquetes").select("id", "clases_restantes", "tipo_paquete", "fecha_vencimiento").eq("alumno_id", id_alumno_sel).eq("estado", "Activo").execute()
                        
                        clases_flotantes = 0
                        if paquete_previo.data and len(paquete_previo.data) > 0:
                            info_p = paquete_previo.data[0]
                            if info_p['clases_restantes'] < 900:  # Evita acumular de Mes Completo
                                clases_flotantes = info_p['clases_restantes']
                                if clases_flotantes > 0:
                                    st.warning(f"📢 **Aviso Operativo:** Al alumno **{alumno_sel}** aún le quedan **{clases_flotantes} clases pendientes** de su paquete '{info_p['tipo_paquete']}' (Vence el {info_p['fecha_vencimiento']}).")
                                else:
                                    st.info(f"✅ El alumno no tiene clases pendientes de su plan anterior.")
                        
                        col_ren1, col_ren2 = st.columns(2)
                        with col_ren1:
                            tipo_p_nuevo = st.selectbox("Nuevo Paquete:", ["4 clases", "8 clases", "12 clases", "Mes completo", "Privado"], key="ren_paquete")
                            modalidad_nueva = st.selectbox("Nueva Modalidad de Acceso:", ["Fixed", "Flex"], key="ren_mod")
                        with col_ren2:
                            if modalidad_nueva == "Fixed":
                                sede_assigned_new = st.selectbox("Asignar Sede para este periodo:", list(opciones_locales.keys()) if opciones_locales else ["Primero registra un local"], key="ren_sede")
                            else:
                                st.write("✨ Plan Flex seleccionado: Acceso global habilitado para este periodo.")
                        
                        if st.button("Procesar Renovación / Cargar Nuevo Plan"):
                            try:
                                # 1. Cerrar paquete anterior si existe
                                if paquete_previo.data and len(paquete_previo.data) > 0:
                                    supabase.table("paquetes").update({"estado": "Agotado"}).eq("id", paquete_previo.data[0]['id']).execute()
                                
                                # 2. Calcular créditos unificados
                                mapeo_clases = {"4 clases": 4, "8 clases": 8, "12 clases": 12, "Mes completo": 999, "Privado": 8}
                                base_nuevas = mapeo_clases[tipo_p_nuevo]
                                total_unificado = base_nuevas + clases_flotantes if base_nuevas < 900 else base_nuevas
                                
                                fecha_vence_nueva = (datetime.now() + timedelta(days=30)).date().isoformat()
                                id_local_fijo_nuevo = opciones_locales[sede_assigned_new] if modalidad_nueva == "Fixed" and opciones_locales else None
                                
                                # 3. Guardar en Supabase
                                supabase.table("paquetes").insert({
                                    "alumno_id": id_alumno_sel,
                                    "tipo_paquete": tipo_p_nuevo,
                                    "modalidad_plan": modalidad_nueva,
                                    "local_id_fijo": id_local_fijo_nuevo,
                                    "clases_totales": total_unificado,
                                    "clases_restantes": total_unificado,
                                    "fecha_vencimiento": fecha_vence_nueva,
                                    "estado": "Active" if total_unificado > 0 else "Agotado"
                                }).execute()
                                
                                # MENSAJE DE CONFIRMACIÓN CON COMPROBANTE DETALLADO
                                st.success(f"🔄 **¡Renovación Exitosa!** Se activó el plan para **{alumno_sel}**. Ahora cuenta con un total de **{total_unificado} clases disponibles** (incluyendo {clases_flotantes} acumuladas). El nuevo periodo vence el **{fecha_vence_nueva}**.")
                                st.balloons()
                                
                            except Exception as e:
                                st.error(f"❌ Error al procesar la renovación: {e}")
                except Exception as e:
                    st.error(f"Error en el módulo de renovación: {e}")

            # ========================================================
            # PESTAÑA 4: CONSULTA HISTORIAL 360° POR ALUMNO
            # ========================================================
            with pestanas[3]:
                st.subheader("🔍 Kárdex e Historial de Clases de Alumno")
                busqueda_tel = st.text_input("Busca al Alumno ingresando su Teléfono de Registro:")
                
                if busqueda_tel:
                    try:
                        al_res = supabase.table("alumnos").select("*").eq("telefono", busqueda_tel).execute()
                        if al_res.data and len(al_res.data) > 0:
                            data_al = al_res.data[0]
                            st.markdown(f"### Alumno: **{data_al['nombre']} {data_al['apellido']}**")
                            
                            # 1. Traer Todos sus paquetes contratados (Vigentes e Históricos)
                            paq_res = supabase.table("paquetes").select("*").eq("alumno_id", data_al['id']).order("fecha_compra", descending=True).execute()
                            
                            if paq_res.data:
                                st.markdown("#### 📋 Historial de Paquetes y Membresías")
                                import pandas as pd
                                df_paq = pd.DataFrame(paq_res.data)
                                
                                # Calcular dinámicamente clases consumidas para el reporte
                                df_paq["Clases Consumidas"] = df_paq["clases_totales"] - df_paq["clases_restantes"]
                                # Renombrar columnas para formato amigable
                                df_reporte_paq = df_paq[["tipo_paquete", "modalidad_plan", "clases_totales", "Clases Consumidas", "clases_restantes", "fecha_vencimiento", "estado"]].rename(columns={
                                    "tipo_paquete": "Paquete Contratado", "modalidad_plan": "Tipo Plan", "clases_totales": "Clases Totales", "clases_restantes": "Clases Pendientes (Saldo)", "fecha_vencimiento": "Caduca El", "estado": "Estado Plan"
                                })
                                st.dataframe(df_reporte_paq, use_container_width=True)
                            else:
                                st.info("El alumno no registra compras de paquetes históricas.")
                                
                            # 2. Consultar Historial Detallado de Asistencias (De la tabla Reservas)
                            res_res = supabase.table("reservas").select("fecha_clase", "hora_clase", "tipo_servicio", "estado").eq("alumno_id", data_al['id']).order("fecha_clase", descending=True).execute()
                            
                            st.markdown("#### 🗓️ Bitácora de Clases y Asistencia Diaria")
                            if res_res.data and len(res_res.data) > 0:
                                df_res = pd.DataFrame(res_res.data).rename(columns={
                                    "fecha_clase": "Fecha de Clase", "hora_clase": "Horario", "tipo_servicio": "Modalidad", "estado": "Asistencia"
                                })
                                st.dataframe(df_res, use_container_width=True)
                            else:
                                st.info("💡 El alumno aún no tiene un historial de clases asistidas o reservadas en la agenda.")
                        else:
                            st.error("❌ No se encontró ningún alumno con ese número de teléfono.")
                    except Exception as e:
                        st.error(f"Error al consultar el Kárdex del alumno: {e}")
