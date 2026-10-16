import streamlit as st
import hashlib
from supabase import create_client, Client

# 1. Configuración de la página de Streamlit
st.set_page_config(page_title="Pilates Studio Cloud", page_icon="🧘", layout="wide")

# 2. Conclusión segura a Supabase usando Secrets
@st.cache_resource
def conectar_supabase() -> Client:
    # Lee los datos ocultos configurados en Streamlit Cloud
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = conectar_supabase()
except Exception as e:
    st.error("❌ Error de conexión a la base de datos. Verifica tus Secrets.")
    st.stop()

# 3. Funciones de Seguridad
def encriptar_contrasena(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_primer_inicio():
    try:
        # En Python se pide el conteo dentro del select pero con un formato limpio
        respuesta = supabase.table("usuarios_admin").select("*", count="exact").execute()
        # Si la lista de datos está vacía, significa que no hay administradores
        return len(respuesta.data) == 0
    except Exception as e:
        # Si la tabla aún no se crea o hay otro problema, asumimos que está vacío por seguridad
        return True

# --- ESTADOS DE LA SESIÓN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------------------------------------------------------
# FLUJO PRINCIPAL DE ACCESO
# ------------------------------------------------------------------

# CASO 1: CONFIGURACIÓN INICIAL (Si no hay administradores en Supabase)
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
            # Guarda el administrador real en Supabase
            clave_segura = encriptar_contrasena(nueva_clave)
            supabase.table("usuarios_admin").insert({
                "usuario": nuevo_usuario,
                "contrasena_encriptada": clave_segura
            }).execute()
            st.success("¡Sistema activado con éxito! Recargando la aplicación...")
            st.rerun()

# CASO 2: EL SISTEMA YA TIENE DUEÑO (Flujo Normal)
else:
    st.sidebar.title("🧘 Pilates Studio")
    rol_acceso = st.sidebar.radio("Menú de Perfiles:", ["👤 Alumnos", "📲 Tablet Check-in", "💼 Administrador"])
    
    # --- VISTA ALUMNOS ---
    if rol_acceso == "👤 Alumnos":
        st.title("📱 Portal del Alumno")
        telefono_alumno = st.text_input("Ingresa tu teléfono registrado para ver tu pase de acceso:")
        if telefono_alumno:
            # Busca al alumno real en la base de datos
            alumno = supabase.table("alumnos").select("*").eq("telefono", telefono_alumno).execute()
    if alumno.data:
        # Seleccionamos el primer alumno encontrado en la lista [0]
        datos_alumno = alumno.data[0]
        st.success(f"¡Hola, {datos_alumno['nombre']} {datos_alumno['apellido']}!")
        st.info("Aquí podrás ver tus clases restantes, reservar según tu Plan y generar tu código QR.")
    else:
        st.error("❌ Teléfono no registrado. Por favor, inscríbete con el administrador.")
                
    # --- VISTA TABLET ---
    elif rol_acceso == "📲 Tablet Check-in":
        st.title("📸 Estación de Check-in (Tablet del Local)")
        st.camera_input("Muestra tu código QR frente a la cámara")
        
    # --- VISTA ADMINISTRADOR (CON LOGIN REAL) ---
    elif rol_acceso == "💼 Administrador":
        if not st.session_state.logged_in:
            st.title("🔐 Panel Administrativo")
            user_input = st.text_input("Usuario:")
            pass_input = st.text_input("Contraseña:", type="password")
            
            if st.button("Ingresar"):
                clave_hash = encriptar_contrasena(pass_input)
                # Compara contra Supabase
                resultado = supabase.table("usuarios_admin").select("*").eq("usuario", user_input).eq("contrasena_encriptada", clave_hash).execute()
                if resultado.data:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas.")
        else:
            st.title("💼 Panel de Control Global")
            if st.sidebar.button("Cerrar Sesión"):
                st.session_state.logged_in = False
                st.rerun()
                
            pestanas = st.tabs(["🏢 Configurar Sucursales", "👥 Inscribir Alumno"])
            
            with pestanas[0]:
                st.subheader("Alta de Locales")
                nombre_local = st.text_input("Nombre de la sede (ej: Barranco):")
                direccion_local = st.text_input("Dirección:")
                if st.button("Guardar Local"):
                    if nombre_local:
                        supabase.table("locales").insert({"nombre": nombre_local, "direccion": direccion_local}).execute()
                        st.success(f"¡Sede {nombre_local} registrada exitosamente!")
