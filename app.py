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
                
            pestanas = st.tabs(["🏢 Configurar Sucursales", "👥 Inscribir Alumno", "📋 Lista de Alumnos"])
            
            with pestanas[0]:
                st.subheader("Alta de Locales")
                nombre_local = st.text_input("Nombre de la sede (ej: Barranco):", key="new_local_name")
                direccion_local = st.text_input("Dirección:", key="new_local_dir")
                if st.button("Guardar Local"):
                    if nombre_local:
                        try:
                            supabase.table("locales").insert({"nombre": nombre_local, "direccion": direccion_local}).execute()
                            st.success(f"¡Sede {nombre_local} registrada exitosamente!")
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
                        sede_asignada = st.selectbox("Sede Base / Asignada:", list(opciones_locales.keys()) if opciones_locales else ["Primero registra un local"])
                    else:
                        st.write("✨ Plan Flex seleccionado: El alumno tendrá acceso a todas las sedes libres.")
                
                if st.button("Registrar Alumno y Cargar Créditos"):
                    if not a_nombre or not a_telefono:
                        st.error("❌ Nombre y Teléfono son campos obligatorios.")
                    elif modalidad == "Fixed" and not opciones_locales:
                        st.error("❌ Debes registrar al menos un local en la pestaña anterior antes de inscribir alumnos Fixed.")
                    else:
                        try:
                            # 1. Registrar al Alumno en la base de datos
                            nuevo_alumno = supabase.table("alumnos").insert({
                                "nombre": a_nombre,
                                "apellido": a_apellido,
                                "telefono": a_telefono
                            }).execute()
                            
                            if nuevo_alumno and hasattr(nuevo_alumno, 'data') and nuevo_alumno.data and len(nuevo_alumno.data) > 0:
                                datos_nuevo_alumno = nuevo_alumno.data[0]
                                id_alumno = datos_nuevo_alumno['id']
                                
                                # Mapear créditos de clases
                                mapeo_clases = {"4 clases": 4, "8 clases": 8, "12 clases": 12, "Mes completo": 999, "Privado": 8}
                                total_c = mapeo_clases[tipo_p]
                                
                                # Fecha de vencimiento estándar (30 días)
                                fecha_vence = (datetime.now() + timedelta(days=30)).date().isoformat()
                                id_local_fijo = opciones_locales[sede_asignada] if modalidad == "Fixed" and opciones_locales else None
                                
                                # 2. Cargar el paquete a favor del cliente
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
                            st.error(f"❌ Error en la inscripción: {e}")

            with pestanas[2]:
                st.subheader("Alumnos Registrados en el Sistema")
                try:
                    alumnos_list = supabase.table("alumnos").select("*").execute()
                    if alumnos_list.data and len(alumnos_list.data) > 0:
                        import pandas as pd
                        st.dataframe(pd.DataFrame(alumnos_list.data), use_container_width=True)
                    else:
                        st.info("No hay alumnos inscritos en este momento.")
                except Exception as e:
                    st.error(f"Error al cargar la lista: {e}")
