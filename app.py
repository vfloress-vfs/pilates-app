import streamlit as st
import hashlib
import hmac
import secrets
import base64
import html
import re
from datetime import datetime, timedelta
from supabase import create_client, Client

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser la primera línea de Streamlit)
st.set_page_config(page_title="Panel de Control", page_icon="🧘", layout="wide")

# Identidad visual: calma, movimiento y claridad para una escuela profesional de Pilates.
st.markdown("""
<style>
:root {
    --pilates-forest: #a9c5b2;
    --pilates-forest-dark: #0b1512;
    --pilates-sage: #8fb49d;
    --pilates-sage-light: #263a31;
    --pilates-cream: #0e1714;
    --pilates-paper: #1b2923;
    --pilates-panel: #17231e;
    --pilates-ink: #edf2ed;
    --pilates-muted: #a9b8ae;
    --pilates-clay: #d9aa84;
    --pilates-border: #35463d;
}

.stApp { background: var(--pilates-cream); color: var(--pilates-ink); }
[data-testid="stHeader"] { background: rgba(14,23,20,.96); }
[data-testid="stToolbar"] { right: 1rem; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1500px; }

h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] {
    font-family: "Aptos", "Segoe UI", sans-serif;
}
h1 { color: var(--pilates-forest); font-weight: 700; letter-spacing: -.035em; line-height: 1.15; }
h2, h3 { color: var(--pilates-forest); font-weight: 650; letter-spacing: -.02em; }
[data-testid="stCaptionContainer"] { color: var(--pilates-muted); }

/* Contraste explícito para etiquetas y textos del contenido principal. */
.block-container { color: var(--pilates-ink); }
.block-container label,
.block-container [data-testid="stWidgetLabel"],
.block-container [data-testid="stWidgetLabel"] *,
.block-container [data-testid="stMarkdownContainer"],
.block-container [data-testid="stMarkdownContainer"] p {
    color: var(--pilates-ink) !important;
}
.block-container [data-testid="stCaptionContainer"],
.block-container [data-testid="stCaptionContainer"] * {
    color: var(--pilates-muted) !important;
}

/* Cabecera de marca */
.pilates-brand {
    display: flex; align-items: center; gap: 1rem;
    padding: 1.2rem 1.5rem; margin: 0 0 1.8rem;
    border: 1px solid #35463d; border-radius: 20px;
    background: linear-gradient(115deg, #17231e 0%, #203329 100%);
    box-shadow: 0 12px 32px rgba(0,0,0,.18);
}
.pilates-mark {
    width: 54px; height: 54px; flex: 0 0 54px; border-radius: 17px;
    display: grid; place-items: center; background: linear-gradient(145deg, #9fbea9, #648875);
    color: #102019; box-shadow: inset 0 1px 0 rgba(255,255,255,.3), 0 5px 14px rgba(0,0,0,.18);
}
.pilates-brand-copy { display: flex; flex-direction: column; gap: .12rem; }
.pilates-kicker { color: var(--pilates-clay); text-transform: uppercase; letter-spacing: .16em; font-size: .67rem; font-weight: 750; }
.pilates-brand-title { color: #edf4ee; font: 650 1.3rem "Aptos", "Segoe UI", sans-serif; letter-spacing: -.035em; }
.pilates-brand-subtitle { color: #b7c7bc; font-size: .87rem; }

/* Navegación */
[data-testid="stSidebar"] { background: var(--pilates-forest-dark); border-right: 1px solid rgba(255,255,255,.08); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p { color: #edf3ee; }
[data-testid="stSidebar"] [data-testid="stRadio"] > label { color: #c3d4ca; font-size: .77rem; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; }
[data-testid="stSidebar"] [role="radiogroup"] { gap: .4rem; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: .58rem .72rem; border-radius: 11px; color: #e5eee8;
    transition: background .18s ease, transform .18s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255,255,255,.09); transform: translateX(2px); }
[data-testid="stSidebar"] [data-testid="stButton"] button {
    color: var(--pilates-forest-dark); background: #e8efe8; border: 0; font-weight: 700;
}
.pilates-sidebar-brand { padding: .45rem .25rem 1rem; margin-bottom: 1.2rem; border-bottom: 1px solid rgba(255,255,255,.15); }
.pilates-sidebar-brand strong { display: block; color: #fffefa; font: 650 1.16rem Georgia, serif; }
.pilates-sidebar-brand span { color: #b9cfc2; font-size: .73rem; letter-spacing: .09em; text-transform: uppercase; }

/* Componentes de Streamlit */
.stButton > button, .stFormSubmitButton > button {
    min-height: 2.7rem; border: 1px solid var(--pilates-forest); border-radius: 11px;
    background: var(--pilates-forest); color: #102019; font-weight: 700;
    box-shadow: 0 3px 10px rgba(0,0,0,.2); transition: all .18s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    border-color: #c4d9ca; background: #c4d9ca;
    color: #102019; transform: translateY(-1px); box-shadow: 0 7px 18px rgba(0,0,0,.28);
}
[data-testid="stSidebar"] [data-testid="stButton"] button {
    width: 100%; min-height: 2.8rem !important; padding: .55rem .8rem !important;
    border: 1px solid #b7d0bf !important; border-radius: 11px !important;
    background: #c6d9cb !important; color: #102019 !important;
    -webkit-text-fill-color: #102019 !important; font-weight: 750 !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background: #e0ebe2 !important; color: #0b1512 !important;
    -webkit-text-fill-color: #0b1512 !important; border-color: #e0ebe2 !important;
}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input, [data-testid="stTimeInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stTextArea"] textarea {
    border-radius: 10px; background: var(--pilates-paper); border-color: var(--pilates-border);
    color: var(--pilates-ink) !important; -webkit-text-fill-color: var(--pilates-ink) !important;
}
[data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {
    color: var(--pilates-muted) !important; -webkit-text-fill-color: var(--pilates-muted) !important; opacity: 1;
}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-baseweb="popover"] [role="option"] {
    color: var(--pilates-ink) !important; -webkit-text-fill-color: var(--pilates-ink) !important;
    background: var(--pilates-paper) !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--pilates-sage); box-shadow: 0 0 0 1px var(--pilates-sage);
}
[data-testid="stTabs"] [role="tablist"] {
    display: flex; flex-wrap: wrap; gap: .55rem; padding: .45rem;
    border: 1px solid var(--pilates-border); border-radius: 15px;
    background: #111b17; margin-bottom: .8rem;
}
[data-testid="stTabs"] button[role="tab"] {
    min-height: 2.8rem; margin: 0; padding: .65rem 1rem;
    color: var(--pilates-muted); background: #1b2923;
    border: 1px solid #35463d; border-radius: 10px 10px 6px 6px;
    font-weight: 700; transition: all .18s ease;
}
[data-testid="stTabs"] button[role="tab"]:hover {
    color: #edf2ed; background: #24352c; border-color: #789783;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #102019; background: #a9c5b2; border-color: #a9c5b2;
    box-shadow: 0 4px 14px rgba(0,0,0,.25); font-weight: 800;
}
[data-testid="stTabs"] [role="tabpanel"] {
    padding: 1.25rem 1.35rem; background: var(--pilates-panel);
    border: 1px solid var(--pilates-border); border-radius: 5px 15px 15px 15px;
    box-shadow: 0 8px 24px rgba(0,0,0,.14);
}
[data-testid="stAlert"] { border-radius: 12px; border: 1px solid var(--pilates-border); background: var(--pilates-panel); color: var(--pilates-ink); }
[data-testid="stAlert"] p { color: var(--pilates-ink); }
[data-testid="stDataFrame"], [data-testid="stTable"] { background: var(--pilates-panel); }
.material-icons, .material-symbols-rounded { color: var(--pilates-sage); font-variation-settings: "FILL" 0, "wght" 500, "GRAD" 0, "opsz" 20; }
[data-testid="stMetric"] { padding: 1rem 1.1rem; border: 1px solid var(--pilates-border); border-radius: 15px; background: var(--pilates-paper); box-shadow: 0 4px 14px rgba(34,57,47,.04); }
[data-testid="stMetricLabel"] { color: var(--pilates-muted); }
[data-testid="stMetricValue"] { color: var(--pilates-forest); font-weight: 700; }
[data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid var(--pilates-border); border-radius: 12px; overflow: hidden; }
hr { border-color: var(--pilates-border); }

@media (max-width: 700px) {
    .block-container { padding: 1rem 1rem 2rem; }
    .pilates-brand { padding: 1rem; border-radius: 16px; }
    .pilates-mark { width: 46px; height: 46px; flex-basis: 46px; }
    .pilates-brand-title { font-size: 1.1rem; }
    [data-testid="stTabs"] [role="tablist"] { overflow-x: auto; }
}
</style>
""", unsafe_allow_html=True)

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

CONFIG_ESTUDIO_DEFAULT = {
    "nombre_estudio": "Pilates Studio",
    "color_fondo": "#0e1714",
    "color_acento": "#a9c5b2",
    "color_boton": "#a9c5b2",
    "logo_base64": None,
    "logo_mime": None,
}

def color_hex_seguro(valor, alternativo):
    return valor if isinstance(valor, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", valor) else alternativo

def color_texto_contraste(color):
    canales = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lineales = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return "#102019" if sum(lineales[i] * peso for i, peso in enumerate((0.2126, 0.7152, 0.0722))) > 0.42 else "#edf2ed"

try:
    configuracion_res = supabase.table("configuracion_estudio").select("*").eq("id", 1).limit(1).execute()
    configuracion_estudio = {**CONFIG_ESTUDIO_DEFAULT, **(configuracion_res.data[0] if configuracion_res.data else {})}
    config_estudio_disponible = True
except Exception:
    configuracion_estudio = dict(CONFIG_ESTUDIO_DEFAULT)
    config_estudio_disponible = False

nombre_estudio = str(configuracion_estudio.get("nombre_estudio") or CONFIG_ESTUDIO_DEFAULT["nombre_estudio"]).strip()
color_fondo_app = color_hex_seguro(configuracion_estudio.get("color_fondo"), CONFIG_ESTUDIO_DEFAULT["color_fondo"])
color_acento_app = color_hex_seguro(configuracion_estudio.get("color_acento"), CONFIG_ESTUDIO_DEFAULT["color_acento"])
color_boton_app = color_hex_seguro(configuracion_estudio.get("color_boton"), CONFIG_ESTUDIO_DEFAULT["color_boton"])
color_texto_boton = color_texto_contraste(color_boton_app)
color_texto_fondo = color_texto_contraste(color_fondo_app)
fondo_claro = color_texto_fondo == "#102019"
color_panel_app = "#ffffff" if fondo_claro else "#17231e"
color_papel_app = "#f1f4f2" if fondo_claro else "#1b2923"
color_borde_app = "#c7d0ca" if fondo_claro else "#35463d"
color_muted_app = "#52605a" if fondo_claro else "#a9b8ae"
color_barra_pestanas = "#e5ebe7" if fondo_claro else "#111b17"
st.markdown(f"""
<style>
:root {{
  --pilates-cream: {color_fondo_app};
  --pilates-forest: {color_acento_app};
  --pilates-sage: {color_acento_app};
  --pilates-button: {color_boton_app};
  --pilates-button-ink: {color_texto_boton};
  --pilates-ink: {color_texto_fondo};
  --pilates-panel: {color_panel_app};
  --pilates-paper: {color_papel_app};
  --pilates-border: {color_borde_app};
  --pilates-muted: {color_muted_app};
}}
.stButton > button, .stFormSubmitButton > button {{
  background: var(--pilates-button) !important;
  border-color: var(--pilates-button) !important;
  color: var(--pilates-button-ink) !important;
  -webkit-text-fill-color: var(--pilates-button-ink) !important;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover {{
  filter: brightness(1.12);
}}
[data-testid="stSidebar"] [data-testid="stButton"] button {{
  background: var(--pilates-button) !important;
  border-color: var(--pilates-button) !important;
  color: var(--pilates-button-ink) !important;
  -webkit-text-fill-color: var(--pilates-button-ink) !important;
}}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {{
  background: var(--pilates-button) !important;
  color: var(--pilates-button-ink) !important;
  -webkit-text-fill-color: var(--pilates-button-ink) !important;
  filter: brightness(1.12);
}}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
  color: var(--pilates-button-ink) !important;
  background: var(--pilates-button) !important;
  border-color: var(--pilates-button) !important;
}}
[data-testid="stTabs"] [role="tablist"] {{ background: {color_barra_pestanas} !important; }}
[data-testid="stTabs"] button[role="tab"] {{ background: var(--pilates-paper) !important; }}
</style>
""", unsafe_allow_html=True)

# 3. FUNCIONES DE SEGURIDAD Y LÓGICA DE NEGOCIO
# PBKDF2 con sal aleatoria se almacena en la columna text existente.
ITERACIONES_HASH = 600_000

VENTANAS_ADMIN = {
    "sucursales": "Sucursales",
    "inscripciones": "Inscripciones",
    "renovaciones": "Renovaciones",
    "planes": "Planes y tarifas",
    "agenda": "Agenda",
    "alumnos": "Consulta de alumnos",
    "configuracion": "Configuración",
}

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
if "admin_id" not in st.session_state:
    st.session_state.admin_id = None
if "admin_usuario" not in st.session_state:
    st.session_state.admin_usuario = ""
if "admin_es_superadmin" not in st.session_state:
    st.session_state.admin_es_superadmin = False
if "admin_permisos" not in st.session_state:
    st.session_state.admin_permisos = []
if "admin_migracion_pendiente" not in st.session_state:
    st.session_state.admin_migracion_pendiente = False

# ------------------------------------------------------------------
# FLUJO PRINCIPAL DE ACCESO
# ------------------------------------------------------------------
for llave_limpieza in ("clear_bootstrap", "clear_login", "clear_portal_alumno"):
    if llave_limpieza not in st.session_state:
        st.session_state[llave_limpieza] = 0

# CASO 1: CONFIGURACIÓN INICIAL (solo si se confirma que no existen administradores)
try:
    primer_inicio = verificar_primer_inicio()
except Exception:
    st.error("No se pudo verificar la cuenta administradora. Revisa la conexión y los permisos de Supabase.")
    st.stop()

if primer_inicio:
    st.title(":material/admin_panel_settings: Configuración Inicial del Sistema")
    st.subheader("Configura tu cuenta de Dueño/Administrador por primera vez:")
    st.info("Esta pantalla desaparecerá automáticamente una vez registres tu clave.")
    
    nuevo_usuario = st.text_input("Nombre de usuario o correo de administrador:", key=f"bootstrap_usuario_{st.session_state.clear_bootstrap}")
    nueva_clave = st.text_input("Contraseña de acceso:", type="password", key=f"bootstrap_clave_{st.session_state.clear_bootstrap}")
    confirmar_clave = st.text_input("Confirma tu contraseña:", type="password", key=f"bootstrap_confirmar_{st.session_state.clear_bootstrap}")
    
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
                nuevo_admin = supabase.table("usuarios_admin").insert({
                    "usuario": nuevo_usuario.strip(),
                    "contrasena_encriptada": clave_segura,
                    "es_superadmin": True,
                    "permisos": list(VENTANAS_ADMIN.keys())
                }).select("id,usuario,es_superadmin,permisos").execute()
                if not nuevo_admin.data:
                    raise RuntimeError("No se recibió el nuevo usuario administrador.")
                datos_admin = nuevo_admin.data[0]
                st.session_state.admin_id = datos_admin["id"]
                st.session_state.admin_usuario = datos_admin["usuario"]
                st.session_state.admin_es_superadmin = True
                st.session_state.admin_permisos = list(VENTANAS_ADMIN.keys())
                st.session_state.logged_in = True
                st.success("¡Sistema activado con éxito! Abriendo el panel...")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al guardar el administrador: {e}")
    if st.button("Limpiar campos", key="limpiar_bootstrap"):
        st.session_state.clear_bootstrap += 1
        st.rerun()

# CASO 2: EL SISTEMA YA TIENE ENLACE SEGURO (Flujo de Operación Normal)
else:
    logo_base64 = configuracion_estudio.get("logo_base64")
    if logo_base64:
        try:
            st.sidebar.image(base64.b64decode(logo_base64), width=145)
        except Exception:
            pass
    st.sidebar.markdown(f"""
    <div class="pilates-sidebar-brand">
        <strong>{html.escape(nombre_estudio)}</strong>
        <span>Gestión del estudio</span>
    </div>
    """, unsafe_allow_html=True)
    rol_acceso = st.sidebar.radio("Menú de Perfiles:", ["Alumnos", "Tablet Check-in", "Administrador"])
    
    # --- VISTA ALUMNOS ---
    if rol_acceso == "Alumnos":
        st.title(":material/smartphone: Portal del Alumno")
        telefono_alumno = st.text_input("Ingresa tu teléfono registrado para ver tu pase de acceso:", key=f"portal_telefono_{st.session_state.clear_portal_alumno}")
        if st.button("Limpiar búsqueda", key="limpiar_portal_alumno"):
            st.session_state.clear_portal_alumno += 1
            st.rerun()
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
    elif rol_acceso == "Tablet Check-in":
        st.title(":material/qr_code_scanner: Estación de Check-in (Tablet del Local)")
        st.write("Coloca esta pantalla fija en la entrada de tu estudio.")
        st.camera_input("Muestra tu código QR frente a la cámara")
                
    # --- VISTA ADMINISTRADOR ---
    elif rol_acceso == "Administrador":
        if not st.session_state.logged_in:
            st.title(":material/lock: Panel Administrativo Privado")
            user_input = st.text_input("Usuario:", key=f"login_usuario_{st.session_state.clear_login}")
            pass_input = st.text_input("Contraseña:", type="password", key=f"login_clave_{st.session_state.clear_login}")
            
            if st.button("Ingresar"):
                try:
                    esquema_antiguo = False
                    try:
                        resultado = (
                            supabase.table("usuarios_admin")
                            .select("id,usuario,contrasena_encriptada,es_superadmin,permisos")
                            .eq("usuario", user_input.strip())
                            .limit(1)
                            .execute()
                        )
                    except Exception as error_esquema:
                        if "42703" not in str(error_esquema) and getattr(error_esquema, "code", None) != "42703":
                            raise
                        # Acceso completo temporal para las cuentas existentes mientras se aplica el SQL.
                        esquema_antiguo = True
                        resultado = (
                            supabase.table("usuarios_admin")
                            .select("id,usuario,contrasena_encriptada")
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
                            try:
                                supabase.table("usuarios_admin").update({
                                    "contrasena_encriptada": encriptar_contrasena(pass_input)
                                }).eq("id", admins[0]["id"]).execute()
                            except Exception:
                                # La actualización del formato de hash no debe impedir
                                # que una cuenta válida entre al panel.
                                st.warning("Ingresaste correctamente. No se pudo actualizar el formato de tu contraseña; podrás hacerlo desde Mi cuenta.")
                        st.session_state.admin_id = admins[0]["id"]
                        st.session_state.admin_usuario = admins[0]["usuario"]
                        st.session_state.admin_es_superadmin = esquema_antiguo or bool(admins[0].get("es_superadmin", False))
                        permisos_guardados = admins[0].get("permisos") or []
                        st.session_state.admin_permisos = (
                            list(VENTANAS_ADMIN.keys()) if esquema_antiguo
                            else permisos_guardados if isinstance(permisos_guardados, list) else []
                        )
                        st.session_state.admin_migracion_pendiente = esquema_antiguo
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas.")
                except Exception as e:
                    st.error(f"❌ Error al validar credenciales: {e}")
            if st.button("Limpiar campos", key="limpiar_login"):
                st.session_state.clear_login += 1
                st.rerun()
        else:
            st.title(":material/dashboard: Panel de Control")
            if st.sidebar.button("Cerrar sesión", icon=":material/logout:", type="primary"):
                st.session_state.logged_in = False
                st.session_state.admin_id = None
                st.session_state.admin_usuario = ""
                st.session_state.admin_es_superadmin = False
                st.session_state.admin_permisos = []
                st.session_state.admin_migracion_pendiente = False
                st.rerun()
                
            # Inicializar llaves de control para limpiar formularios si no existen
            if "clear_local" not in st.session_state: st.session_state.clear_local = 0
            if "clear_ins" not in st.session_state: st.session_state.clear_ins = 0
            if "clear_ren" not in st.session_state: st.session_state.clear_ren = 0
            if "clear_search" not in st.session_state: st.session_state.clear_search = 0
            if "clear_plan" not in st.session_state: st.session_state.clear_plan = 0
            for llave_limpieza in ("clear_instructora", "clear_agenda", "clear_feriado", "clear_usuario", "clear_tarifa", "clear_cuenta", "clear_reset_clave", "clear_configuracion"):
                if llave_limpieza not in st.session_state:
                    st.session_state[llave_limpieza] = 0

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
                
            if st.session_state.admin_migracion_pendiente:
                st.warning("Tu cuenta conserva acceso completo. Ejecuta supabase_admin_users_migration.sql en Supabase para habilitar la gestión de usuarios y permisos.")

            # Las ventanas se muestran según los permisos guardados en el perfil del administrador.
            permisos_sesion = set(st.session_state.admin_permisos or [])
            ventanas_disponibles = list(VENTANAS_ADMIN.keys())
            ventanas_visibles = [
                clave for clave in ventanas_disponibles
                if st.session_state.admin_es_superadmin or clave in permisos_sesion
            ]
            claves_pestanas = ventanas_visibles + ["mi_cuenta"]
            if st.session_state.admin_es_superadmin:
                claves_pestanas.append("usuarios")
            nombres_pestanas = {**VENTANAS_ADMIN, "mi_cuenta": "Mi cuenta", "usuarios": "Usuarios y accesos"}
            pestanas = st.tabs([nombres_pestanas[clave] for clave in claves_pestanas])
            paneles_admin = dict(zip(claves_pestanas, pestanas))

            if not ventanas_visibles:
                st.info("Tu cuenta solo tiene acceso a Mi cuenta. Pide a un superadministrador que te asigne otras ventanas si las necesitas.")

            if "sucursales" in paneles_admin:
                with paneles_admin["sucursales"]:
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

            if "inscripciones" in paneles_admin:
                with paneles_admin["inscripciones"]:
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
            if "renovaciones" in paneles_admin:
                with paneles_admin["renovaciones"]:
                    st.subheader(":material/autorenew: Renovar paquete de alumno")
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

            if "planes" in paneles_admin:
                with paneles_admin["planes"]:
                    st.subheader(":material/payments: Catálogo de planes, clases y costos")
                    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Crear plan", "Modificar costos", "Planes vigentes"])
                                
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
                            plan_a_modificar = st.selectbox("Selecciona el plan que deseas actualizar:", list(opciones_planes.keys()), key=f"tarifa_plan_{st.session_state.clear_tarifa}")
                            nuevo_precio = st.number_input("Establecer nuevo precio ($):", min_value=0.0, max_value=5000.0, value=costos_planes.get(plan_a_modificar, 0.0), step=5.0, key=f"tarifa_precio_{st.session_state.clear_tarifa}")
                            col_tarifa_1, col_tarifa_2 = st.columns(2)
                            with col_tarifa_1:
                                if st.button("Actualizar Tarifa Comercial", key="actualizar_tarifa_comercial"):
                                    try:
                                        supabase.table("tipos_paquetes").update({"costo": nuevo_precio}).eq("nombre_paquete", plan_a_modificar).execute()
                                        st.success(f"📈 ¡Precio del plan '{plan_a_modificar}' actualizado correctamente a ${nuevo_precio:.2f}!")
                                    except Exception as e: st.error(f"❌ Error al actualizar precio: {e}")
                            with col_tarifa_2:
                                if st.button("Limpiar campos", key="limpiar_tarifa"):
                                    st.session_state.clear_tarifa += 1
                                    st.rerun()
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
                                    
            if "agenda" in paneles_admin:
                with paneles_admin["agenda"]:
                    st.subheader("🗓️ Control de Agenda, Clases e Inactividades")
                    sub_agenda1, sub_agenda2, sub_agenda3, sub_agenda4 = st.tabs([
                        "Instructoras", "Programación de horarios", "Días laborales", "Feriados y festivos"
                    ])
                                    
                    with sub_agenda1:
                        st.markdown("#### Alta de Profesoras y Tarifas por Hora")
                        inst_nombre = st.text_input("Nombre completo de la Instructora:", key=f"inst_nombre_{st.session_state.clear_instructora}")
                        inst_telefono = st.text_input("Teléfono de contacto:", key=f"inst_telefono_{st.session_state.clear_instructora}")
                        inst_costo = st.number_input("Costo / Tarifa por hora dictada ($):", min_value=0.0, value=50.0, step=5.0, key=f"inst_costo_{st.session_state.clear_instructora}")
                        col_inst_1, col_inst_2 = st.columns(2)
                        with col_inst_1:
                            if st.button("Guardar Instructora"):
                                if inst_nombre:
                                    try:
                                        supabase.table("instructoras").insert({"nombre": inst_nombre, "telefono": inst_telefono, "costo_hora": inst_costo}).execute()
                                        st.success(f"🎉 Instructora '{inst_nombre}' registrada con éxito.")
                                    except Exception as e: st.error(f"❌ Error al guardar instructora: {e}")
                                else: st.error("El nombre es obligatorio.")
                        with col_inst_2:
                            if st.button("Limpiar campos", key="limpiar_instructora"):
                                st.session_state.clear_instructora += 1
                                st.rerun()
                                                
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
                                sede_agenda = st.selectbox("Selecciona Sede:", list(opciones_locales.keys()) if opciones_locales else ["No hay locales"], key=f"mas_sede_{st.session_state.clear_agenda}")
                                fecha_inicio = st.date_input("Fecha de Inicio:", min_value=datetime.now().date(), key=f"mas_f_ini_{st.session_state.clear_agenda}")
                                fecha_fin = st.date_input("Fecha de Fin:", value=datetime.now().date() + timedelta(days=30), key=f"mas_f_fin_{st.session_state.clear_agenda}")
                                hora_agenda = st.time_input("Hora de Inicio:", key=f"mas_hora_{st.session_state.clear_agenda}")
                            with col_mas2:
                                inst_agenda = st.selectbox("Asignar Instructora:", list(opciones_inst.keys()) if opciones_inst else ["Primero registra una instructora"], key=f"mas_inst_{st.session_state.clear_agenda}")
                                tipo_serv_agenda = st.selectbox("Tipo de Sesión:", ["Grupal", "Privado"], key=f"mas_tipo_{st.session_state.clear_agenda}")
                                if tipo_serv_agenda == "Grupal":
                                    aforo_agenda = st.number_input("Aforo Máximo Camillas:", min_value=4, max_value=10, value=4, key=f"mas_aforo_{st.session_state.clear_agenda}")
                                else: aforo_agenda = 1
                                            
                            dias_seleccionados = []
                            col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns(5)
                            with col_d1: 
                                if st.checkbox("Lunes", value=True, key=f"dia_lunes_{st.session_state.clear_agenda}"): dias_seleccionados.append(0)
                            with col_d2: 
                                if st.checkbox("Martes", value=True, key=f"dia_martes_{st.session_state.clear_agenda}"): dias_seleccionados.append(1)
                            with col_d3: 
                                if st.checkbox("Miércoles", value=True, key=f"dia_miercoles_{st.session_state.clear_agenda}"): dias_seleccionados.append(2)
                            with col_d4: 
                                if st.checkbox("Jueves", value=True, key=f"dia_jueves_{st.session_state.clear_agenda}"): dias_seleccionados.append(3)
                            with col_d5: 
                                if st.checkbox("Viernes", value=True, key=f"dia_viernes_{st.session_state.clear_agenda}"): dias_seleccionados.append(4)
                                            
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
                            if st.button("Limpiar campos", key="limpiar_generador_agenda"):
                                st.session_state.clear_agenda += 1
                                st.rerun()
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
                            fecha_f = st.date_input("Fecha del Feriado:", key=f"input_fecha_feriado_{st.session_state.clear_feriado}")
                            desc_f = st.text_input("Descripción del Festivo:", key=f"input_desc_feriado_{st.session_state.clear_feriado}")
                            if st.button("Habilitar Feriado"):
                                if desc_f:
                                    try:
                                        supabase.table("feriados").insert({"fecha": fecha_f.isoformat(), "descripcion": desc_f}).execute()
                                        st.success(f"🌴 ¡Fecha {fecha_f} bloqueada!")
                                        st.rerun()
                                    except Exception as e: st.error(f"❌ Ya registrado o error: {e}")
                                else: st.error("Agrega una descripción.")
                            if st.button("Limpiar campos", key="limpiar_feriado"):
                                st.session_state.clear_feriado += 1
                                st.rerun()
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

                # --- CONSULTA PREDICTIVA DE ALUMNOS Y KÁRDEX ---
            if "alumnos" in paneles_admin:
                with paneles_admin["alumnos"]:
                    st.subheader(":material/clinical_notes: Kárdex e historial de clases")

                    if "kardex_alumno_id" not in st.session_state:
                        st.session_state.kardex_alumno_id = None

                    try:
                        todos_al_res = supabase.table("alumnos").select("id,nombre,apellido,telefono").order("nombre").execute()
                        lista_alumnos_all = todos_al_res.data or []
                    except Exception:
                        lista_alumnos_all = []
                        st.error("No se pudo cargar el directorio de alumnos. Revisa la conexión y los permisos.")

                    if not lista_alumnos_all:
                        st.info("💡 Aún no registras ningún alumno en el sistema.")
                        st.session_state.kardex_alumno_id = None
                        st.session_state.pop("selector_predictivo_kardex", None)
                    elif st.session_state.kardex_alumno_id is None:
                        # El selectbox permite escribir para filtrar sugerencias por nombre, apellido o teléfono.
                        etiquetas_por_id = {
                            al["id"]: f"{al['nombre']} {al['apellido']} — {al['telefono']}"
                            for al in lista_alumnos_all
                        }
                        ids_por_etiqueta = {etiqueta: alumno_id for alumno_id, etiqueta in etiquetas_por_id.items()}
                        opciones_kardex = [""] + list(ids_por_etiqueta.keys())
                        alumno_elegido = st.selectbox(
                            "Busca y selecciona un alumno:",
                            opciones_kardex,
                            index=0,
                            key="selector_predictivo_kardex",
                            placeholder="Escribe nombre, apellido o teléfono..."
                        )
                        if alumno_elegido:
                            st.session_state.kardex_alumno_id = ids_por_etiqueta[alumno_elegido]
                            st.rerun()
                    else:
                        col_ficha, col_accion = st.columns([5, 1])
                        with col_ficha:
                            st.caption("FICHA DEL ALUMNO SELECCIONADO")
                        with col_accion:
                            if st.button("← Directorio", key="volver_directorio_kardex", use_container_width=True):
                                st.session_state.kardex_alumno_id = None
                                st.session_state.pop("selector_predictivo_kardex", None)
                                st.rerun()

                        try:
                            al_res = (
                                supabase.table("alumnos")
                                .select("id,nombre,apellido,telefono")
                                .eq("id", st.session_state.kardex_alumno_id)
                                .limit(1)
                                .execute()
                            )
                            if not al_res.data:
                                st.warning("El alumno seleccionado ya no aparece en el directorio.")
                                st.session_state.kardex_alumno_id = None
                                st.session_state.pop("selector_predictivo_kardex", None)
                            else:
                                import pandas as pd
                                data_al = al_res.data[0]
                                st.markdown(f"### 📊 {data_al['nombre']} {data_al['apellido']}")
                                st.caption(f"📱 Contacto: {data_al['telefono']}")

                                paq_res = (
                                    supabase.table("paquetes")
                                    .select("tipo_paquete,modalidad_plan,clases_totales,clases_restantes,fecha_vencimiento,estado")
                                    .eq("alumno_id", data_al["id"])
                                    .order("fecha_compra", desc=True)
                                    .execute()
                                )
                                if paq_res.data:
                                    st.markdown("#### :material/loyalty: Historial de paquetes y membresías")
                                    df_paq = pd.DataFrame(paq_res.data)
                                    df_paq["Clases Consumidas"] = df_paq["clases_totales"] - df_paq["clases_restantes"]
                                    df_reporte_paq = df_paq[[
                                        "tipo_paquete", "modalidad_plan", "clases_totales", "Clases Consumidas",
                                        "clases_restantes", "fecha_vencimiento", "estado"
                                    ]].rename(columns={
                                        "tipo_paquete": "Paquete Contratado",
                                        "modalidad_plan": "Tipo Plan",
                                        "clases_totales": "Clases Totales",
                                        "clases_restantes": "Clases Pendientes (Saldo)",
                                        "fecha_vencimiento": "Caduca El",
                                        "estado": "Estado Plan"
                                    })
                                    st.dataframe(df_reporte_paq, use_container_width=True, hide_index=True)
                                else:
                                    st.info("Este alumno aún no tiene paquetes registrados.")

                                res_res = (
                                    supabase.table("reservas")
                                    .select("fecha_clase,hora_clase,tipo_servicio,estado")
                                    .eq("alumno_id", data_al["id"])
                                    .order("fecha_clase", desc=True)
                                    .execute()
                                )
                                st.markdown("#### :material/event_note: Historial de clases y asistencia")
                                if res_res.data:
                                    df_res = pd.DataFrame(res_res.data).rename(columns={
                                        "fecha_clase": "Fecha de Clase",
                                        "hora_clase": "Horario",
                                        "tipo_servicio": "Modalidad",
                                        "estado": "Asistencia"
                                    })
                                    st.dataframe(df_res, use_container_width=True, hide_index=True)
                                else:
                                    st.info("💡 El alumno aún no tiene historial de clases en la agenda.")
                        except Exception:
                            st.error("No se pudo cargar la ficha del alumno. Revisa la conexión y los permisos.")

            with paneles_admin["mi_cuenta"]:
                st.subheader(":material/key: Cambiar mi contraseña")
                st.caption(f"Sesión iniciada como **{st.session_state.admin_usuario}**")
                with st.form(f"form_cambiar_clave_admin_{st.session_state.clear_cuenta}"):
                    clave_actual = st.text_input("Contraseña actual", type="password", key=f"cuenta_clave_actual_{st.session_state.clear_cuenta}")
                    clave_nueva = st.text_input("Nueva contraseña (mínimo 12 caracteres)", type="password", key=f"cuenta_clave_nueva_{st.session_state.clear_cuenta}")
                    clave_confirmacion = st.text_input("Confirmar nueva contraseña", type="password", key=f"cuenta_clave_confirmacion_{st.session_state.clear_cuenta}")
                    guardar_clave = st.form_submit_button("Actualizar contraseña", type="primary")
                    limpiar_clave = st.form_submit_button("Limpiar campos")
                if limpiar_clave:
                    st.session_state.clear_cuenta += 1
                    st.rerun()
                if guardar_clave:
                    if len(clave_nueva) < 12:
                        st.error("La nueva contraseña debe tener al menos 12 caracteres.")
                    elif clave_nueva != clave_confirmacion:
                        st.error("Las contraseñas nuevas no coinciden.")
                    else:
                        try:
                            actual_res = supabase.table("usuarios_admin").select("contrasena_encriptada").eq(
                                "id", st.session_state.admin_id
                            ).limit(1).execute()
                            if not actual_res.data or not verificar_contrasena(
                                clave_actual, actual_res.data[0]["contrasena_encriptada"]
                            )[0]:
                                st.error("La contraseña actual no es correcta.")
                            else:
                                supabase.table("usuarios_admin").update({
                                    "contrasena_encriptada": encriptar_contrasena(clave_nueva)
                                }).eq("id", st.session_state.admin_id).execute()
                                st.success("Contraseña actualizada correctamente.")
                        except Exception:
                            st.error("No se pudo actualizar la contraseña. Revisa la conexión y los permisos de Supabase.")

            if st.session_state.admin_es_superadmin and "usuarios" in paneles_admin:
                with paneles_admin["usuarios"]:
                    st.subheader(":material/manage_accounts: Usuarios y permisos de acceso")
                    st.caption("Cada usuario solo verá las ventanas asignadas. Todos pueden cambiar su contraseña desde Mi cuenta.")

                    with st.form(f"form_crear_usuario_admin_{st.session_state.clear_usuario}"):
                        nuevo_usuario_admin = st.text_input("Nombre de usuario", key=f"nuevo_usuario_admin_{st.session_state.clear_usuario}")
                        nueva_clave_admin = st.text_input("Contraseña inicial (mínimo 12 caracteres)", type="password", key=f"nueva_clave_admin_{st.session_state.clear_usuario}")
                        confirmar_clave_admin = st.text_input("Confirmar contraseña", type="password", key=f"confirmar_clave_admin_{st.session_state.clear_usuario}")
                        permisos_nuevos = st.multiselect(
                            "Ventanas que podrá administrar",
                            options=list(VENTANAS_ADMIN.keys()),
                            format_func=lambda permiso: VENTANAS_ADMIN[permiso],
                            key=f"permisos_nuevo_admin_{st.session_state.clear_usuario}"
                        )
                        crear_usuario = st.form_submit_button("Crear usuario administrador", type="primary")
                        limpiar_usuario = st.form_submit_button("Limpiar campos")
                    if limpiar_usuario:
                        st.session_state.clear_usuario += 1
                        st.rerun()
                    if crear_usuario:
                        if not nuevo_usuario_admin.strip():
                            st.error("Escribe un nombre de usuario.")
                        elif len(nueva_clave_admin) < 12:
                            st.error("La contraseña debe tener al menos 12 caracteres.")
                        elif nueva_clave_admin != confirmar_clave_admin:
                            st.error("Las contraseñas no coinciden.")
                        else:
                            try:
                                supabase.table("usuarios_admin").insert({
                                    "usuario": nuevo_usuario_admin.strip(),
                                    "contrasena_encriptada": encriptar_contrasena(nueva_clave_admin),
                                    "es_superadmin": False,
                                    "permisos": permisos_nuevos
                                }).execute()
                                st.success(f"Usuario {nuevo_usuario_admin.strip()} creado.")
                                st.session_state.clear_usuario += 1
                                st.rerun()
                            except Exception as e:
                                if "23505" in str(e) or "already exists" in str(e).lower():
                                    st.error("Ese nombre de usuario ya existe.")
                                elif "42703" in str(e):
                                    st.error("Ejecuta primero supabase_admin_users_migration.sql en Supabase para habilitar los permisos.")
                                else:
                                    st.error("No se pudo crear el usuario. Revisa la conexión y los permisos de Supabase.")

                    st.divider()
                    st.markdown("#### Restablecer contraseña de un usuario")
                    try:
                        usuarios_claves_res = supabase.table("usuarios_admin").select("id,usuario").order("usuario").execute()
                        usuarios_claves = usuarios_claves_res.data or []
                        if usuarios_claves:
                            usuarios_clave_labels = {f"{u['usuario']}" : u["id"] for u in usuarios_claves}
                            usuario_clave_sel = st.selectbox(
                                "Usuario al que cambiar la contraseña",
                                list(usuarios_clave_labels.keys()),
                                key="usuario_restablecer_clave"
                            )
                            with st.form(f"form_restablecer_clave_{st.session_state.clear_reset_clave}"):
                                clave_admin_nueva = st.text_input(
                                    "Nueva contraseña (mínimo 12 caracteres)",
                                    type="password",
                                    key=f"reset_clave_nueva_{st.session_state.clear_reset_clave}"
                                )
                                confirmar_clave_admin_nueva = st.text_input(
                                    "Confirmar nueva contraseña",
                                    type="password",
                                    key=f"reset_clave_confirmar_{st.session_state.clear_reset_clave}"
                                )
                                cambiar_clave_usuario = st.form_submit_button("Cambiar contraseña", type="primary")
                                limpiar_reset_clave = st.form_submit_button("Limpiar campos")
                            if limpiar_reset_clave:
                                st.session_state.clear_reset_clave += 1
                                st.rerun()
                            if cambiar_clave_usuario:
                                if len(clave_admin_nueva) < 12:
                                    st.error("La contraseña debe tener al menos 12 caracteres.")
                                elif clave_admin_nueva != confirmar_clave_admin_nueva:
                                    st.error("Las contraseñas no coinciden.")
                                else:
                                    supabase.table("usuarios_admin").update({
                                        "contrasena_encriptada": encriptar_contrasena(clave_admin_nueva)
                                    }).eq("id", usuarios_clave_labels[usuario_clave_sel]).execute()
                                    st.success(f"Contraseña de {usuario_clave_sel} cambiada correctamente.")
                                    st.session_state.clear_reset_clave += 1
                                    st.rerun()
                        else:
                            st.info("No hay usuarios administradores registrados.")
                    except Exception:
                        st.error("No se pudo restablecer la contraseña. Revisa la conexión y los permisos de Supabase.")

                    st.divider()
                    st.markdown("#### Editar permisos de un usuario existente")
                    try:
                        usuarios_res = supabase.table("usuarios_admin").select(
                            "id,usuario,es_superadmin,permisos"
                        ).order("usuario").execute()
                        usuarios_db = usuarios_res.data or []
                        usuarios_normales = [u for u in usuarios_db if not u.get("es_superadmin", False)]
                        if usuarios_normales:
                            etiqueta_a_id = {u["usuario"]: u["id"] for u in usuarios_normales}
                            usuario_editar = st.selectbox("Usuario", list(etiqueta_a_id.keys()), key="usuario_permisos_editar")
                            usuario_obj = next(u for u in usuarios_normales if u["id"] == etiqueta_a_id[usuario_editar])
                            permisos_actuales = usuario_obj.get("permisos") or []
                            permisos_editados = st.multiselect(
                                "Ventanas asignadas",
                                options=list(VENTANAS_ADMIN.keys()),
                                default=[p for p in permisos_actuales if p in VENTANAS_ADMIN],
                                format_func=lambda permiso: VENTANAS_ADMIN[permiso],
                                key=f"permisos_editar_{usuario_obj['id']}"
                            )
                            if st.button("Guardar permisos", key="guardar_permisos_usuario", type="primary"):
                                supabase.table("usuarios_admin").update({
                                    "permisos": permisos_editados
                                }).eq("id", usuario_obj["id"]).execute()
                                st.success(f"Permisos de {usuario_editar} actualizados.")
                                st.rerun()
                        else:
                            st.info("Aún no hay otros usuarios administradores para editar.")
                    except Exception:
                        st.error("No se pudieron cargar los usuarios. Ejecuta la migración SQL y revisa los permisos de Supabase.")

                    st.divider()
                    st.markdown("#### Eliminar usuario")
                    st.caption("La eliminación es permanente. No puedes eliminar la cuenta con la que tienes la sesión abierta ni el último superusuario.")
                    try:
                        usuarios_borrar_res = supabase.table("usuarios_admin").select(
                            "id,usuario,es_superadmin"
                        ).order("usuario").execute()
                        usuarios_borrar = usuarios_borrar_res.data or []
                        usuarios_eliminables = [
                            usuario for usuario in usuarios_borrar
                            if str(usuario["id"]) != str(st.session_state.admin_id)
                        ]
                        if usuarios_eliminables:
                            etiquetas_borrar = {
                                f"{usuario['usuario']} — {'Superusuario' if usuario.get('es_superadmin') else 'Administrador'}": usuario
                                for usuario in usuarios_eliminables
                            }
                            usuario_borrar_etiqueta = st.selectbox(
                                "Selecciona la cuenta que deseas eliminar",
                                list(etiquetas_borrar.keys()),
                                key="usuario_admin_seleccionar_eliminar"
                            )
                            usuario_borrar = etiquetas_borrar[usuario_borrar_etiqueta]
                            confirmar_borrado = st.checkbox(
                                f"Confirmo que deseo eliminar permanentemente a {usuario_borrar['usuario']}",
                                key=f"confirmar_eliminar_usuario_{usuario_borrar['id']}"
                            )
                            if st.button(
                                "Eliminar usuario",
                                key="eliminar_usuario_admin",
                                type="secondary",
                                disabled=not confirmar_borrado
                            ):
                                superusuarios = [u for u in usuarios_borrar if u.get("es_superadmin")]
                                if usuario_borrar.get("es_superadmin") and len(superusuarios) <= 1:
                                    st.error("No se puede eliminar el último superusuario.")
                                else:
                                    supabase.table("usuarios_admin").delete().eq("id", usuario_borrar["id"]).execute()
                                    st.success(f"La cuenta {usuario_borrar['usuario']} fue eliminada.")
                                    st.rerun()
                        else:
                            st.info("No hay otras cuentas que puedas eliminar.")
                    except Exception:
                        st.error("No se pudo cargar o eliminar la cuenta. Verifica la migración SQL y los permisos de Supabase.")

            if "configuracion" in paneles_admin:
                with paneles_admin["configuracion"]:
                    st.subheader(":material/palette: Identidad visual del estudio")
                    st.caption("El nombre y la apariencia se aplican a todos los perfiles de la aplicación.")
                    if not config_estudio_disponible:
                        st.error("Falta crear la tabla de configuración. Ejecuta supabase_app_config_migration.sql en Supabase y vuelve a cargar la app.")
                    else:
                        if st.session_state.pop("configuracion_guardada", False):
                            st.success("Configuración del estudio guardada.")
                        logo_actual = configuracion_estudio.get("logo_base64")
                        logo_mime_actual = configuracion_estudio.get("logo_mime") or "image/png"
                        logo_subido = st.file_uploader(
                            "Cambiar logo (PNG, JPG o WEBP; máximo 1 MB)",
                            type=["png", "jpg", "jpeg", "webp"],
                            key=f"config_logo_{st.session_state.clear_configuracion}"
                        )
                        if logo_subido is not None:
                            st.image(logo_subido.getvalue(), caption="Vista previa del nuevo logo", width=180)
                        elif logo_actual:
                            try:
                                st.image(base64.b64decode(logo_actual), caption="Logo actual", width=180)
                            except Exception:
                                st.warning("No se pudo mostrar el logo guardado.")

                        nombre_nuevo_estudio = st.text_input(
                            "Nombre del estudio",
                            value=nombre_estudio,
                            key=f"config_nombre_{st.session_state.clear_configuracion}"
                        )
                        col_color_1, col_color_2, col_color_3 = st.columns(3)
                        with col_color_1:
                            fondo_nuevo = st.color_picker(
                                "Fondo principal",
                                value=color_fondo_app,
                                key=f"config_fondo_{st.session_state.clear_configuracion}"
                            )
                        with col_color_2:
                            acento_nuevo = st.color_picker(
                                "Color de acento",
                                value=color_acento_app,
                                key=f"config_acento_{st.session_state.clear_configuracion}"
                            )
                        with col_color_3:
                            boton_nuevo = st.color_picker(
                                "Color de botones",
                                value=color_boton_app,
                                key=f"config_boton_{st.session_state.clear_configuracion}"
                            )
                        quitar_logo = st.checkbox(
                            "Quitar el logo actual",
                            key=f"config_quitar_logo_{st.session_state.clear_configuracion}"
                        )
                        guardar_configuracion = st.button(
                            "Guardar configuración",
                            key=f"guardar_configuracion_{st.session_state.clear_configuracion}",
                            type="primary"
                        )

                        if guardar_configuracion:
                            if not nombre_nuevo_estudio.strip():
                                st.error("Escribe el nombre del estudio.")
                            elif logo_subido is not None and logo_subido.size > 1_048_576:
                                st.error("El logo supera el límite de 1 MB.")
                            else:
                                logo_base64_nuevo = None if quitar_logo else logo_actual
                                logo_mime_nuevo = None if quitar_logo else logo_mime_actual
                                if logo_subido is not None:
                                    logo_base64_nuevo = base64.b64encode(logo_subido.getvalue()).decode("ascii")
                                    logo_mime_nuevo = logo_subido.type or "image/png"
                                try:
                                    supabase.table("configuracion_estudio").upsert({
                                        "id": 1,
                                        "nombre_estudio": nombre_nuevo_estudio.strip(),
                                        "color_fondo": fondo_nuevo,
                                        "color_acento": acento_nuevo,
                                        "color_boton": boton_nuevo,
                                        "logo_base64": logo_base64_nuevo,
                                        "logo_mime": logo_mime_nuevo,
                                    }, on_conflict="id").execute()
                                    st.session_state.configuracion_guardada = True
                                    st.session_state.clear_configuracion += 1
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"No se pudo guardar la configuración. Revisa la migración y los permisos de Supabase: {e}")
