import streamlit as st
import hashlib
import hmac
import secrets
import base64
import html
import re
import unicodedata
import io
import pandas as pd
from datetime import datetime, timedelta, time as datetime_time
from zoneinfo import ZoneInfo
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
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stColorPicker"] input,
[data-testid="stTextArea"] textarea {
    border: 1px solid var(--pilates-input-border) !important;
    border-radius: 10px; background: var(--pilates-paper);
    color: var(--pilates-ink) !important; -webkit-text-fill-color: var(--pilates-ink) !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.025);
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
[data-testid="stDateInput"] input:focus, [data-testid="stTimeInput"] input:focus,
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--pilates-sage) !important;
    box-shadow: 0 0 0 2px var(--pilates-sage);
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
    "hora_apertura": "06:00:00",
    "hora_cierre": "22:00:00",
    "duracion_clase_minutos": 50,
    "dias_agenda_anticipacion": 45,
    "corte_turno_manana": "12:00:00",
    "limite_reserva_manana": "19:00:00",
    "limite_reserva_tarde_horas": 4,
}

def color_hex_seguro(valor, alternativo):
    return valor if isinstance(valor, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", valor) else alternativo

def color_texto_contraste(color):
    canales = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lineales = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return "#102019" if sum(lineales[i] * peso for i, peso in enumerate((0.2126, 0.7152, 0.0722))) > 0.42 else "#edf2ed"

def fecha_visible(valor, incluir_hora=False):
    """Formatea fechas de base de datos para mostrarlas como dd-mm-aaaa."""
    if valor is None or valor == "":
        return "—"
    if isinstance(valor, datetime):
        fecha = valor
    else:
        texto = str(valor).strip()
        try:
            fecha = datetime.fromisoformat(texto.replace("Z", "+00:00"))
        except ValueError:
            try:
                fecha = datetime.strptime(texto[:10], "%Y-%m-%d")
            except ValueError:
                return texto
    return fecha.strftime("%d-%m-%Y %H:%M" if incluir_hora else "%d-%m-%Y")

try:
    configuracion_res = supabase.table("configuracion_estudio").select("*").eq("id", 1).limit(1).execute()
    configuracion_estudio = {**CONFIG_ESTUDIO_DEFAULT, **(configuracion_res.data[0] if configuracion_res.data else {})}
    config_estudio_disponible = True
except Exception:
    configuracion_estudio = dict(CONFIG_ESTUDIO_DEFAULT)
    config_estudio_disponible = False

def hora_configuracion(clave):
    valor = configuracion_estudio.get(clave) or CONFIG_ESTUDIO_DEFAULT[clave]
    if isinstance(valor, datetime_time):
        return valor
    return datetime_time.fromisoformat(str(valor)[:8])

hora_apertura_estudio = hora_configuracion("hora_apertura")
hora_cierre_estudio = hora_configuracion("hora_cierre")
duracion_clase_default = int(configuracion_estudio.get("duracion_clase_minutos") or 50)
dias_agenda_anticipacion = int(configuracion_estudio.get("dias_agenda_anticipacion") or 45)
corte_turno_manana = hora_configuracion("corte_turno_manana")
limite_reserva_manana = hora_configuracion("limite_reserva_manana")
limite_reserva_tarde_horas = int(configuracion_estudio.get("limite_reserva_tarde_horas") or 4)

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
color_borde_input = "#8c9a91" if fondo_claro else "#64746b"
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
  --pilates-input-border: {color_borde_input};
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
    "sucursales": "Sedes",
    "alumnos_operacion": "Gestión de alumnos",
    "planes": "Planes y precios",
    "instructoras": "Gestión de instructores",
    "configuracion": "Configuración",
}

def normalizar_permisos_admin(permisos):
    """Migra permisos antiguos de Agenda e integra las ventanas de alumnos."""
    if not isinstance(permisos, list):
        return []
    permisos_alumnos_antiguos = {"inscripciones", "renovaciones", "alumnos"}
    normalizados = [p for p in permisos if p in VENTANAS_ADMIN and p != "instructoras"]
    if "instructoras" in permisos or "agenda" in permisos:
        normalizados.append("instructoras")
    if permisos_alumnos_antiguos.intersection(permisos) or "alumnos_operacion" in permisos:
        normalizados.append("alumnos_operacion")
    return list(dict.fromkeys(normalizados))

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
if "instructor_sesion_id" not in st.session_state:
    st.session_state.instructor_sesion_id = None
if "instructor_sesion_nombre" not in st.session_state:
    st.session_state.instructor_sesion_nombre = ""

# ------------------------------------------------------------------
# FLUJO PRINCIPAL DE ACCESO
# ------------------------------------------------------------------
for llave_limpieza in ("clear_bootstrap", "clear_login", "clear_portal_alumno", "clear_checkin", "clear_portal_reserva"):
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
                st.session_state.mensaje_resultado_app = "Sistema activado. Ya puedes administrar el estudio."
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
    rol_acceso = st.sidebar.radio("Menú de Perfiles:", ["Alumnos", "Instructores", "Tablet Check-in", "Administrador"])
    
    # --- VISTA ALUMNOS ---
    if rol_acceso == "Alumnos":
        st.title(":material/smartphone: Portal del Alumno")
        telefono_alumno = st.text_input("Ingresa tu teléfono registrado para ver tu pase de acceso:", key=f"portal_telefono_{st.session_state.clear_portal_alumno}")
        if st.button("Limpiar búsqueda", key="limpiar_portal_alumno"):
            st.session_state.clear_portal_alumno += 1
            st.rerun()
        if telefono_alumno:
            try:
                ahora_portal = datetime.now(ZoneInfo("America/Lima"))

                def limite_reserva_cancelacion(inicio_clase):
                    """Mañana: 19:00 del día anterior. Tarde: cuatro horas antes."""
                    if inicio_clase.time().replace(tzinfo=None) < corte_turno_manana:
                        fecha_limite = inicio_clase.date() - timedelta(days=1)
                        return datetime.combine(fecha_limite, limite_reserva_manana).replace(tzinfo=ZoneInfo("America/Lima"))
                    return inicio_clase - timedelta(hours=limite_reserva_tarde_horas)

                # Respaldo para instalaciones sin pg_cron; el cron de la BD sigue siendo el proceso automático principal.
                try:
                    supabase.rpc("marcar_inasistencias_vencidas", {}).execute()
                except Exception:
                    pass
                alumno = supabase.table("alumnos").select("id,nombre,apellido").eq("telefono", telefono_alumno.strip()).execute()
                if not alumno.data:
                    st.error("Teléfono no registrado. Por favor, inscríbete con el administrador.")
                    st.stop()
                datos_alumno = alumno.data[0]
                id_alumno_portal = datos_alumno["id"]
                st.success(f"¡Hola, {datos_alumno.get('nombre', '')} {datos_alumno.get('apellido', '')}!")
                if st.session_state.pop("aviso_portal", False):
                    st.success(st.session_state.pop("aviso_portal_mensaje", "La operación se completó correctamente."))

                paquetes_res = (
                    supabase.table("paquetes")
                    .select("id,modalidad_plan,tipo_paquete,clases_restantes,fecha_vencimiento,local_id_fijo,pagado")
                    .eq("alumno_id", id_alumno_portal).eq("estado", "Activo")
                    .eq("pagado", True).gte("fecha_vencimiento", ahora_portal.date().isoformat())
                    .gt("clases_restantes", 0).order("fecha_vencimiento")
                    .execute()
                )
                paquetes_portal = paquetes_res.data or []
                tab_plan_portal, tab_reserva_portal, tab_historial_portal = st.tabs(["1. Mi plan", "2. Reservar clase", "3. Mis clases"], key="tabs_portal_alumno", on_change="rerun")
                with tab_plan_portal:
                    st.subheader("Tu plan")
                    if paquetes_portal:
                        cols_plan = st.columns(min(3, len(paquetes_portal)))
                        for idx_plan, plan in enumerate(paquetes_portal):
                            with cols_plan[idx_plan % len(cols_plan)]:
                                st.metric(f"{plan.get('modalidad_plan', '')} · {plan.get('tipo_paquete', '')}", f"{plan.get('clases_restantes', 0)} clases")
                                st.caption(f"Vence el {fecha_visible(plan.get('fecha_vencimiento'))}")
                    else:
                        st.warning("No tienes planes pagados y vigentes con clases disponibles.")

                limite_agenda = ahora_portal.date() + timedelta(days=dias_agenda_anticipacion)
                sesiones_portal = supabase.table("sesiones_clase").select(
                    "id,local_id,instructora_id,fecha_clase,hora_inicio,hora_fin,tipo_servicio,capacidad,estado"
                ).eq("estado", "Programada").gte("fecha_clase", ahora_portal.date().isoformat()).lte(
                    "fecha_clase", limite_agenda.isoformat()
                ).order("fecha_clase").order("hora_inicio").execute().data or []
                dias_portal = supabase.table("dias_operativos").select("numero_dia").eq("habilitado", True).execute().data or []
                dias_habilitados_portal = {int(d["numero_dia"]) for d in dias_portal}
                feriados_portal_res = supabase.table("feriados").select("fecha").gte(
                    "fecha", ahora_portal.date().isoformat()
                ).lte("fecha", limite_agenda.isoformat()).execute()
                fechas_bloqueadas_portal = {str(f["fecha"]) for f in (feriados_portal_res.data or [])}
                sesiones_futuras = []
                for sesion in sesiones_portal:
                    inicio_sesion = datetime.combine(
                        datetime.fromisoformat(str(sesion["fecha_clase"])).date(),
                        datetime_time.fromisoformat(str(sesion["hora_inicio"]))
                    ).replace(tzinfo=ZoneInfo("America/Lima"))
                    fecha_sesion = inicio_sesion.date()
                    if (inicio_sesion > ahora_portal
                            and fecha_sesion.weekday() in dias_habilitados_portal
                            and fecha_sesion.isoformat() not in fechas_bloqueadas_portal):
                        sesion["_inicio_dt"] = inicio_sesion
                        sesiones_futuras.append(sesion)
                ids_sesiones = [s["id"] for s in sesiones_futuras]
                reservas_agendadas = []
                sesiones_reservadas_alumno = set()
                if ids_sesiones:
                    reservas_agendadas = supabase.table("reservas").select("sesion_id,estado,alumno_id").in_("sesion_id", ids_sesiones).eq("estado", "Programada").execute().data or []
                ocupacion = {}
                for reserva_activa in reservas_agendadas:
                    id_sesion = reserva_activa.get("sesion_id")
                    ocupacion[id_sesion] = ocupacion.get(id_sesion, 0) + 1
                    if str(reserva_activa.get("alumno_id")) == str(id_alumno_portal):
                        sesiones_reservadas_alumno.add(int(id_sesion))
                locales_portal = supabase.table("locales").select("id,nombre").execute().data or []
                instructoras_portal = supabase.table("instructoras").select("id,nombre").execute().data or []
                nombre_local_portal = {x["id"]: x.get("nombre", "Sede") for x in locales_portal}
                nombre_instructora_portal = {x["id"]: x.get("nombre", "Instructora") for x in instructoras_portal}
                sesiones_con_cupo = [
                    s for s in sesiones_futuras
                    if ocupacion.get(s["id"], 0) < int(s.get("capacidad") or 0)
                ]
                sesiones_disponibles = [
                    s for s in sesiones_con_cupo
                    if ahora_portal <= limite_reserva_cancelacion(s["_inicio_dt"])
                ]
                sesiones_reserva_mostrables = [
                    s for s in sesiones_futuras
                    if int(s["id"]) in sesiones_reservadas_alumno
                    or (
                        ocupacion.get(s["id"], 0) < int(s.get("capacidad") or 0)
                        and ahora_portal <= limite_reserva_cancelacion(s["_inicio_dt"])
                    )
                ]
                etiqueta_sesion = lambda s: (
                    f"{fecha_visible(s['fecha_clase'])} · {str(s['hora_inicio'])[:5]} · {s.get('tipo_servicio', 'Clase')} · "
                    f"{nombre_local_portal.get(s.get('local_id'), 'Sede')} · "
                    f"{nombre_instructora_portal.get(s.get('instructora_id'), 'Instructora')} · "
                    f"{int(s.get('capacidad') or 0) - ocupacion.get(s['id'], 0)} cupos"
                )

                with tab_reserva_portal:
                    st.subheader("Reservar una clase")
                    if not paquetes_portal:
                        st.info("Necesitas un plan pagado, vigente y con clases disponibles para reservar.")
                    elif not sesiones_reserva_mostrables:
                        st.info(f"No hay clases con cupos y dentro del plazo de reserva. Las clases de mañana se reservan hasta las {limite_reserva_manana.strftime('%H:%M')} del día anterior; las de tarde, hasta {limite_reserva_tarde_horas} horas antes.")
                    else:
                        opciones_reserva = []
                        for plan in paquetes_portal:
                            for sesion in sesiones_reserva_mostrables:
                                if plan.get("modalidad_plan") != "Fixed" or plan.get("local_id_fijo") == sesion.get("local_id"):
                                    opciones_reserva.append((plan, sesion))
                        if opciones_reserva:
                            planes_por_sesion = {}
                            for plan, sesion in opciones_reserva:
                                planes_por_sesion.setdefault(int(sesion["id"]), []).append(plan)

                            sesiones_con_plan = [s for s in sesiones_reserva_mostrables if int(s["id"]) in planes_por_sesion]
                            fechas_con_clases = sorted({sesion["_inicio_dt"].date() for sesion in sesiones_con_plan})
                            st.caption("Elige un día en el calendario para ver sus clases disponibles. La lista conserva el detalle de horarios, sede, instructor y cupos.")
                            fecha_reserva = st.date_input(
                                "Día de la clase",
                                value=fechas_con_clases[0],
                                min_value=ahora_portal.date(),
                                max_value=limite_agenda,
                                format="DD-MM-YYYY",
                                key=f"filtro_fecha_reserva_portal_{id_alumno_portal}_{st.session_state.clear_portal_reserva}",
                            )
                            sesiones_del_dia = [s for s in sesiones_con_plan if s["_inicio_dt"].date() == fecha_reserva]
                            st.caption(f"Hay horarios reservables en {len(fechas_con_clases)} días dentro del periodo disponible.")
                            if not sesiones_del_dia:
                                st.info("No hay clases disponibles para este día. Elige otra fecha en el calendario.")
                            sesion_portal_key = f"portal_sesion_seleccionada_{id_alumno_portal}"
                            columnas_clases = st.columns(2)
                            dias_semana_portal = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                            for idx_sesion, sesion in enumerate(sesiones_del_dia):
                                fecha_sesion_card = sesion["_inicio_dt"].date()
                                cupos_sesion = int(sesion.get("capacidad") or 0) - ocupacion.get(sesion["id"], 0)
                                with columnas_clases[idx_sesion % 2]:
                                    with st.container(border=True):
                                        st.markdown(f"### {dias_semana_portal[fecha_sesion_card.weekday()]}, {fecha_sesion_card.strftime('%d-%m-%Y')}")
                                        st.markdown(f"**{str(sesion['hora_inicio'])[:5]}–{str(sesion['hora_fin'])[:5]} · {sesion.get('tipo_servicio', 'Clase')}**")
                                        st.write(f"📍 {nombre_local_portal.get(sesion.get('local_id'), 'Sede')}  ·  👤 {nombre_instructora_portal.get(sesion.get('instructora_id'), 'Instructor')}")
                                        plazo_reserva = limite_reserva_cancelacion(sesion["_inicio_dt"])
                                        ya_reservada = int(sesion["id"]) in sesiones_reservadas_alumno
                                        if ya_reservada:
                                            st.info("Ya tienes esta clase reservada.")
                                        else:
                                            st.caption(f"{cupos_sesion} {'cupos disponibles' if cupos_sesion != 1 else 'cupo disponible'} · Reserva hasta {plazo_reserva.strftime('%d-%m-%Y a las %H:%M')}")
                                        seleccionada = not ya_reservada and st.session_state.get(sesion_portal_key) == int(sesion["id"])
                                        if st.button(
                                            "Ya tienes esta clase reservada" if ya_reservada else ("Horario elegido ✓" if seleccionada else "Elegir este horario"),
                                            key=f"elegir_sesion_portal_{id_alumno_portal}_{sesion['id']}_{st.session_state.clear_portal_reserva}",
                                            type="primary" if seleccionada else "secondary",
                                            use_container_width=True,
                                            disabled=ya_reservada,
                                        ):
                                            st.session_state[sesion_portal_key] = int(sesion["id"])
                                            st.rerun()

                            sesion_seleccionada = next(
                                (s for s in sesiones_del_dia if int(s["id"]) == st.session_state.get(sesion_portal_key)),
                                None,
                            )
                            if sesion_seleccionada:
                                st.divider()
                                st.markdown("#### Confirma tu reserva")
                                planes_para_sesion = planes_por_sesion[int(sesion_seleccionada["id"])]
                                plan_seleccionado = st.selectbox(
                                    "Plan que deseas utilizar",
                                    planes_para_sesion,
                                    format_func=lambda p: f"{p.get('tipo_paquete')} · {p.get('clases_restantes')} clases restantes · vence {fecha_visible(p.get('fecha_vencimiento'))}",
                                    key=f"plan_reserva_portal_{id_alumno_portal}_{sesion_seleccionada['id']}_{st.session_state.clear_portal_reserva}",
                                )
                                if st.button("Confirmar y reservar clase", type="primary", key=f"confirmar_reserva_{id_alumno_portal}"):
                                    try:
                                        supabase.rpc("reservar_clase_portal", {
                                            "p_telefono": telefono_alumno.strip(),
                                            "p_sesion_id": int(sesion_seleccionada["id"]),
                                            "p_paquete_id": int(plan_seleccionado["id"]),
                                        }).execute()
                                        st.session_state["aviso_portal_mensaje"] = "Reserva confirmada. La clase ya se descontó de tu plan."
                                        st.session_state["aviso_portal"] = True
                                        st.session_state.clear_portal_reserva += 1
                                        st.session_state.pop(sesion_portal_key, None)
                                        st.rerun()
                                    except Exception as error_reserva:
                                        st.error(f"No se pudo reservar: {error_reserva}")
                        else:
                            st.info("Tus planes de sede fija no coinciden con las sedes de las clases disponibles.")

                with tab_historial_portal:
                    reservas_alumno = supabase.table("reservas").select(
                        "id,sesion_id,paquete_id,local_id,instructora_id,fecha_clase,hora_clase,tipo_servicio,estado,qr_token"
                    ).eq("alumno_id", id_alumno_portal).order("fecha_clase", desc=False).limit(200).execute().data or []
                    st.divider()
                    st.subheader("Mis clases")
                    if reservas_alumno:
                        ids_historial = {r.get("sesion_id") for r in reservas_alumno if r.get("sesion_id")}
                        datos_sesion_historial = {}
                        if ids_historial:
                            filas_sesion_historial = supabase.table("sesiones_clase").select(
                                "id,local_id,instructora_id,fecha_clase,hora_inicio,hora_fin,tipo_servicio,estado"
                            ).in_("id", list(ids_historial)).execute().data or []
                            datos_sesion_historial = {s["id"]: s for s in filas_sesion_historial}
                        filas_historial = []
                        ids_reservas_historial = []
                        orden_filas_historial = []
                        for reserva in reservas_alumno:
                            sesion_hist = datos_sesion_historial.get(reserva.get("sesion_id"), {})
                            fecha_hist = sesion_hist.get("fecha_clase") or reserva.get("fecha_clase", "")
                            hora_hist = sesion_hist.get("hora_inicio") or reserva.get("hora_clase", "")
                            filas_historial.append({
                                "Fecha": fecha_visible(fecha_hist),
                                "Hora": str(hora_hist)[:5] if hora_hist else "—",
                                "Sede": nombre_local_portal.get(sesion_hist.get("local_id", reserva.get("local_id")), "—"),
                                "Clase": sesion_hist.get("tipo_servicio") or reserva.get("tipo_servicio", "—"),
                                "Instructora": nombre_instructora_portal.get(sesion_hist.get("instructora_id", reserva.get("instructora_id")), "—"),
                                "Estado": reserva.get("estado", "—"),
                                "Seleccionar": False,
                            })
                            ids_reservas_historial.append(reserva.get("id"))
                            orden_filas_historial.append((str(fecha_hist or ""), str(hora_hist or ""), len(filas_historial) - 1))
                        orden_indices_historial = [item[2] for item in sorted(orden_filas_historial)]
                        filas_historial = [filas_historial[i] for i in orden_indices_historial]
                        ids_reservas_historial = [ids_reservas_historial[i] for i in orden_indices_historial]
                        selector_mis_clases_key = f"seleccionar_reserva_mis_clases_{id_alumno_portal}_{st.session_state.clear_portal_reserva}"
                        anchos_columnas_historial = [1.0, 0.62, 1.25, 1.1, 1.2, 0.9, 0.82]
                        encabezados_historial = ["Fecha", "Hora", "Sede", "Clase", "Instructor/a", "Estado", "Gestión"]
                        campos_historial = ["Fecha", "Hora", "Sede", "Clase", "Instructora", "Estado"]
                        columnas_encabezado = st.columns(anchos_columnas_historial)
                        for columna, titulo in zip(columnas_encabezado, encabezados_historial):
                            columna.markdown(f"**{titulo}**")

                        ids_seleccionados = []
                        for indice_historial, (fila_historial, id_reserva_historial) in enumerate(zip(filas_historial, ids_reservas_historial)):
                            reserva_fila = next((r for r in reservas_alumno if str(r.get("id")) == str(id_reserva_historial)), {})
                            sesion_fila = datos_sesion_historial.get(reserva_fila.get("sesion_id"), {})
                            puede_gestionar = False
                            motivo_no_gestion = ""
                            if reserva_fila.get("estado") != "Programada":
                                estado_reserva = str(reserva_fila.get("estado") or "sin estado").lower()
                                motivo_no_gestion = f"La reserva está {estado_reserva}."
                            elif sesion_fila.get("estado") != "Programada":
                                motivo_no_gestion = "La clase ya no está programada."
                            else:
                                try:
                                    inicio_fila = datetime.combine(
                                        datetime.fromisoformat(str(sesion_fila["fecha_clase"])).date(),
                                        datetime_time.fromisoformat(str(sesion_fila["hora_inicio"])),
                                    ).replace(tzinfo=ZoneInfo("America/Lima"))
                                    if inicio_fila <= ahora_portal:
                                        motivo_no_gestion = "La clase ya pasó."
                                    elif ahora_portal > limite_reserva_cancelacion(inicio_fila):
                                        motivo_no_gestion = "Venció el plazo para cancelar o reagendar."
                                    else:
                                        puede_gestionar = True
                                except (KeyError, TypeError, ValueError):
                                    motivo_no_gestion = "No se pudo validar la fecha de la clase."

                            clave_checkbox_gestion = f"{selector_mis_clases_key}_{id_reserva_historial}"
                            if not puede_gestionar:
                                st.session_state.pop(clave_checkbox_gestion, None)
                            columnas_fila = st.columns(anchos_columnas_historial)
                            for columna, campo in zip(columnas_fila[:6], campos_historial):
                                columna.write(fila_historial.get(campo, "—"))
                            if motivo_no_gestion:
                                columnas_fila[5].caption(motivo_no_gestion)
                            marcado = columnas_fila[6].checkbox(
                                "Gestionar",
                                key=clave_checkbox_gestion,
                                disabled=not puede_gestionar,
                                label_visibility="collapsed",
                                help=motivo_no_gestion or "Marca para cancelar o reagendar esta reserva.",
                            )
                            if marcado:
                                ids_seleccionados.append(id_reserva_historial)

                        id_reserva_seleccionada = ids_seleccionados[0] if len(ids_seleccionados) == 1 else None
                        if len(ids_seleccionados) > 1:
                            st.warning("Marca solo una reserva a la vez para ver sus opciones.")
                        proximas_reservas = [
                            r for r in reservas_alumno
                            if r.get("estado") == "Programada" and r.get("sesion_id") in datos_sesion_historial
                            and datos_sesion_historial[r["sesion_id"]].get("fecha_clase")
                        ]
                        proximas_reservas = [r for r in proximas_reservas if datetime.combine(
                            datetime.fromisoformat(str(datos_sesion_historial[r["sesion_id"]]["fecha_clase"])).date(),
                            datetime_time.fromisoformat(str(datos_sesion_historial[r["sesion_id"]]["hora_inicio"]))
                        ).replace(tzinfo=ZoneInfo("America/Lima")) > ahora_portal]
                        reservas_cancelables = []
                        for reserva_cancelable in proximas_reservas:
                            sesion_cancelable = datos_sesion_historial[reserva_cancelable["sesion_id"]]
                            inicio_cancelable = datetime.combine(
                                datetime.fromisoformat(str(sesion_cancelable["fecha_clase"])).date(),
                                datetime_time.fromisoformat(str(sesion_cancelable["hora_inicio"]))
                            ).replace(tzinfo=ZoneInfo("America/Lima"))
                            limite_cancelacion = limite_reserva_cancelacion(inicio_cancelable)
                            reserva_cancelable["_limite_cancelacion"] = limite_cancelacion
                            if ahora_portal <= limite_cancelacion:
                                reservas_cancelables.append(reserva_cancelable)
                        reserva_seleccionada_cancelable = next(
                            (r for r in reservas_cancelables if str(r.get("id")) == str(id_reserva_seleccionada)),
                            None,
                        )
                        if reserva_seleccionada_cancelable:
                            pestaña_cancelar, pestaña_reagendar = st.tabs(
                                ["Cancelar una Reserva", "Reagendar una Reserva"],
                                key=f"tabs_gestion_reserva_{id_alumno_portal}_{id_reserva_seleccionada}_{st.session_state.clear_portal_reserva}",
                            )
                            sesion_original = datos_sesion_historial[reserva_seleccionada_cancelable["sesion_id"]]
                            fecha_limite_reserva = reserva_seleccionada_cancelable["_limite_cancelacion"].strftime("%d-%m-%Y %H:%M")

                            with pestaña_cancelar:
                                st.caption("La clase se devolverá a tu saldo si cancelas antes del plazo indicado.")
                                titulo_cancelacion = (
                                    f"{fecha_visible(sesion_original.get('fecha_clase'))} · "
                                    f"{str(sesion_original.get('hora_inicio', ''))[:5]} · "
                                    f"{sesion_original.get('tipo_servicio', 'Clase')} · "
                                    f"{nombre_local_portal.get(sesion_original.get('local_id'), 'Sede')}"
                                )
                                with st.container(border=True):
                                    st.write(titulo_cancelacion)
                                    st.caption(f"Puedes cancelar hasta el {fecha_limite_reserva} (hora de Perú).")
                                    confirmar_cancelacion = st.checkbox(
                                        "Confirmo que deseo cancelar esta reserva y devolver la clase a mi saldo.",
                                        key=f"confirmar_cancelacion_portal_{id_alumno_portal}_{reserva_seleccionada_cancelable['id']}_{st.session_state.clear_portal_reserva}",
                                    )
                                    if st.button(
                                        "Cancelar reserva",
                                        key=f"cancelar_reserva_portal_{id_alumno_portal}_{reserva_seleccionada_cancelable['id']}_{st.session_state.clear_portal_reserva}",
                                        type="primary",
                                    ):
                                        if not confirmar_cancelacion:
                                            st.error("Marca la confirmación para cancelar la reserva.")
                                        else:
                                            try:
                                                supabase.rpc("cancelar_reserva_portal", {
                                                    "p_telefono": telefono_alumno.strip(),
                                                    "p_reserva_id": int(reserva_seleccionada_cancelable["id"]),
                                                }).execute()
                                                st.session_state["aviso_portal_mensaje"] = "Reserva cancelada. La clase se devolvió al saldo de tu plan."
                                                st.session_state["aviso_portal"] = True
                                                st.session_state.clear_portal_reserva += 1
                                                st.rerun()
                                            except Exception as error_cancelacion:
                                                st.error(f"No se pudo cancelar la reserva: {error_cancelacion}")

                            with pestaña_reagendar:
                                st.caption("Elige otro horario disponible. Se conserva la clase ya descontada de tu plan y el plazo se valida según Configuración.")
                                try:
                                    paquete_reserva = (supabase.table("paquetes")
                                        .select("id,modalidad_plan,local_id_fijo")
                                        .eq("id", reserva_seleccionada_cancelable.get("paquete_id"))
                                        .eq("alumno_id", id_alumno_portal)
                                        .limit(1).execute().data or [])
                                    paquete_reagenda = paquete_reserva[0] if paquete_reserva else None
                                    sesiones_reagendables = [
                                        s for s in sesiones_disponibles
                                        if int(s["id"]) != int(reserva_seleccionada_cancelable.get("sesion_id") or 0)
                                        and int(s["id"]) not in sesiones_reservadas_alumno
                                        and paquete_reagenda
                                        and (paquete_reagenda.get("modalidad_plan") != "Fixed"
                                             or paquete_reagenda.get("local_id_fijo") == s.get("local_id"))
                                    ]
                                    if not sesiones_reagendables:
                                        st.info("No hay otros horarios disponibles que cumplan las reglas de tu plan y de Configuración.")
                                    else:
                                        fechas_reagenda = sorted({s["_inicio_dt"].date() for s in sesiones_reagendables})
                                        fecha_reagenda_key = f"fecha_reagenda_portal_{id_alumno_portal}_{reserva_seleccionada_cancelable['id']}_{st.session_state.clear_portal_reserva}"
                                        fecha_reagenda = st.date_input(
                                            "Día de la nueva clase",
                                            value=fechas_reagenda[0],
                                            min_value=ahora_portal.date(),
                                            max_value=limite_agenda,
                                            format="DD-MM-YYYY",
                                            key=fecha_reagenda_key,
                                        )
                                        sesiones_reagenda_dia = [s for s in sesiones_reagendables if s["_inicio_dt"].date() == fecha_reagenda]
                                        sesion_reagenda_key = f"sesion_reagenda_portal_{id_alumno_portal}_{reserva_seleccionada_cancelable['id']}"
                                        for indice_reagenda, sesion_nueva in enumerate(sesiones_reagenda_dia):
                                            seleccion_reagenda = st.session_state.get(sesion_reagenda_key) == int(sesion_nueva["id"])
                                            cupos_reagenda = int(sesion_nueva.get("capacidad") or 0) - ocupacion.get(sesion_nueva["id"], 0)
                                            with st.container(border=True):
                                                st.markdown(f"**{str(sesion_nueva['hora_inicio'])[:5]}–{str(sesion_nueva['hora_fin'])[:5]} · {sesion_nueva.get('tipo_servicio', 'Clase')}**")
                                                st.write(f"📍 {nombre_local_portal.get(sesion_nueva.get('local_id'), 'Sede')} · 👤 {nombre_instructora_portal.get(sesion_nueva.get('instructora_id'), 'Instructor')}")
                                                st.caption(f"{cupos_reagenda} {'cupos disponibles' if cupos_reagenda != 1 else 'cupo disponible'} · Reagenda hasta {limite_reserva_cancelacion(sesion_nueva['_inicio_dt']).strftime('%d-%m-%Y %H:%M')}")
                                                if st.button(
                                                    "Horario elegido ✓" if seleccion_reagenda else "Elegir este horario",
                                                    key=f"elegir_reagenda_{id_alumno_portal}_{reserva_seleccionada_cancelable['id']}_{sesion_nueva['id']}_{st.session_state.clear_portal_reserva}",
                                                    type="primary" if seleccion_reagenda else "secondary",
                                                    use_container_width=True,
                                                ):
                                                    st.session_state[sesion_reagenda_key] = int(sesion_nueva["id"])
                                                    st.rerun()

                                        sesion_nueva_seleccionada = next(
                                            (s for s in sesiones_reagenda_dia if int(s["id"]) == st.session_state.get(sesion_reagenda_key)),
                                            None,
                                        )
                                        if sesion_nueva_seleccionada:
                                            st.info(f"Nueva clase: {etiqueta_sesion(sesion_nueva_seleccionada)}")
                                            if st.button(
                                                "Confirmar cambio de reserva",
                                                key=f"confirmar_reagenda_{id_alumno_portal}_{reserva_seleccionada_cancelable['id']}_{st.session_state.clear_portal_reserva}",
                                                type="primary",
                                            ):
                                                try:
                                                    supabase.rpc("reagendar_clase_portal", {
                                                        "p_telefono": telefono_alumno.strip(),
                                                        "p_reserva_id": int(reserva_seleccionada_cancelable["id"]),
                                                        "p_nueva_sesion_id": int(sesion_nueva_seleccionada["id"]),
                                                    }).execute()
                                                    st.session_state["aviso_portal_mensaje"] = "Reserva reagendada. La clase de tu plan se conservó y ya puedes usar el nuevo QR."
                                                    st.session_state["aviso_portal"] = True
                                                    st.session_state.clear_portal_reserva += 1
                                                    st.rerun()
                                                except Exception as error_reagenda:
                                                    st.error(f"No se pudo reagendar: {error_reagenda}")
                                except Exception as error_carga_reagenda:
                                    st.error(f"No se pudieron cargar los horarios para reagendar: {error_carga_reagenda}")
                        if proximas_reservas:
                            with st.expander("Pases QR para tus próximas clases", expanded=False):
                                for reserva_qr in proximas_reservas:
                                    token_qr = reserva_qr.get("qr_token")
                                    sesion_qr = datos_sesion_historial[reserva_qr["sesion_id"]]
                                    st.caption(f"{fecha_visible(sesion_qr['fecha_clase'])} · {str(sesion_qr['hora_inicio'])[:5]} · {nombre_local_portal.get(sesion_qr.get('local_id'), 'Sede')}")
                                    if token_qr:
                                        try:
                                            import qrcode
                                            imagen_qr = qrcode.make(f"PILATES-CHECKIN:{token_qr}")
                                            salida_qr = io.BytesIO()
                                            imagen_qr.save(salida_qr, format="PNG")
                                            st.image(salida_qr.getvalue(), width=180)
                                        except Exception as error_qr:
                                            st.warning(f"No se pudo generar el QR. Verifica la dependencia qrcode[pil]: {error_qr}")
                                    else:
                                        st.caption("El QR ya fue utilizado o la reserva no tiene pase disponible.")
                    else:
                        st.info("Aún no tienes clases reservadas.")
            except Exception as e:
                st.error(f"Error al consultar el portal: {e}")

    # --- VISTA TABLET ---
    elif rol_acceso == "Instructores":
        st.title(":material/person: Espacio del Instructor")
        if st.session_state.instructor_sesion_id is None:
            st.caption("Ingresa con el usuario y la contraseña que te asignó la administración.")
            with st.form("form_acceso_instructor"):
                usuario_instructor_login = st.text_input("Usuario")
                clave_instructor_login = st.text_input("Contraseña", type="password")
                entrar_instructor = st.form_submit_button("Ingresar", type="primary")
                limpiar_acceso_instructor = st.form_submit_button("Limpiar campos")
            if limpiar_acceso_instructor:
                st.rerun()
            if entrar_instructor:
                try:
                    cuenta_instructor = (supabase.table("usuarios_instructores")
                        .select("id,usuario,contrasena_encriptada,instructora_id,activo,instructoras(nombre,activo)")
                        .eq("usuario", usuario_instructor_login.strip()).eq("activo", True).limit(1).execute().data or [])
                    cuenta = cuenta_instructor[0] if cuenta_instructor else None
                    persona = (cuenta or {}).get("instructoras") or {}
                    coincide_instructor = False
                    if cuenta and persona.get("activo", True):
                        coincide_instructor, _ = verificar_contrasena(clave_instructor_login, cuenta["contrasena_encriptada"])
                    if coincide_instructor:
                        st.session_state.instructor_sesion_id = cuenta["instructora_id"]
                        st.session_state.instructor_sesion_nombre = persona.get("nombre", cuenta["usuario"])
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos, o la cuenta está inactiva. Consulta con la administración.")
                except Exception as error_login_instructor:
                    st.error(f"No se pudo validar el acceso. Ejecuta la migración de cuentas de instructores en Supabase. Detalle: {error_login_instructor}")
        else:
            id_instructor_portal = st.session_state.instructor_sesion_id
            if st.sidebar.button("Cerrar sesión de instructor", key="salir_sesion_instructor", type="primary"):
                st.session_state.instructor_sesion_id = None
                st.session_state.instructor_sesion_nombre = ""
                st.rerun()
            st.success(f"Hola, {st.session_state.instructor_sesion_nombre}.")
            try:
                sesiones_instructor_portal = supabase.table("sesiones_clase").select(
                    "id,local_id,fecha_clase,hora_inicio,hora_fin,tipo_servicio,capacidad,estado,pago_por_clase_aplicado"
                ).eq("instructora_id", id_instructor_portal).order("fecha_clase").order("hora_inicio").limit(1000).execute().data or []
                sedes_instructor_portal = supabase.table("locales").select("id,nombre").execute().data or []
                sedes_instructor_map = {int(x["id"]): x.get("nombre", "Sede") for x in sedes_instructor_portal}
                reservas_instructor_portal = []
                if sesiones_instructor_portal:
                    reservas_instructor_portal = supabase.table("reservas").select(
                        "sesion_id,estado"
                    ).in_("sesion_id", [s["id"] for s in sesiones_instructor_portal]).execute().data or []
                conteo_alumnos_sesion = {}
                for reserva_instructor in reservas_instructor_portal:
                    estado_alumno = unicodedata.normalize("NFKD", str(reserva_instructor.get("estado") or "").lower())
                    estado_alumno = "".join(c for c in estado_alumno if not unicodedata.combining(c)).strip()
                    conteos = conteo_alumnos_sesion.setdefault(reserva_instructor["sesion_id"], {
                        "programados": 0, "asistencias": 0, "inasistencias": 0, "cancelados": 0
                    })
                    if estado_alumno in {"programada", "reservada"}:
                        conteos["programados"] += 1
                    elif estado_alumno in {"asistencia", "asistio", "presente"}:
                        conteos["asistencias"] += 1
                    elif estado_alumno in {"inasistencia", "no asistio", "ausente", "falta", "no show", "no-show"}:
                        conteos["inasistencias"] += 1
                    elif estado_alumno in {"cancelada", "cancelado", "reagendada"}:
                        conteos["cancelados"] += 1

                fecha_hoy_instructor = datetime.now(ZoneInfo("America/Lima")).date().isoformat()
                agenda_futura_instructor = [s for s in sesiones_instructor_portal if str(s["fecha_clase"]) >= fecha_hoy_instructor and s.get("estado") == "Programada"]
                historial_clases_instructor = [s for s in sesiones_instructor_portal if str(s["fecha_clase"]) < fecha_hoy_instructor or s.get("estado") in {"Realizada", "Cancelada"}]
                tab_agenda_instructor, tab_historial_instructor, tab_pagos_instructor = st.tabs([
                    "1. Mi agenda", "2. Clases realizadas", "3. Pagos recibidos"
                ], key="tabs_portal_instructor", on_change="rerun")

                def mostrar_clases_instructor(filas_sesiones):
                    if not filas_sesiones:
                        st.info("No hay clases para mostrar en este periodo.")
                        return
                    filas_agenda_instructor = []
                    for clase_instructor in filas_sesiones:
                        totales = conteo_alumnos_sesion.get(clase_instructor["id"], {})
                        filas_agenda_instructor.append({
                            "Fecha": fecha_visible(clase_instructor["fecha_clase"]),
                            "Horario": f"{str(clase_instructor['hora_inicio'])[:5]}–{str(clase_instructor['hora_fin'])[:5]}",
                            "Sede": sedes_instructor_map.get(int(clase_instructor["local_id"]), "Sede"),
                            "Clase": clase_instructor.get("tipo_servicio", "—"),
                            "Aforo": int(clase_instructor.get("capacidad") or 0),
                            "Alumnos reservados": totales.get("programados", 0),
                            "Asistieron": totales.get("asistencias", 0),
                            "Inasistencias": totales.get("inasistencias", 0),
                            "Cancelaciones": totales.get("cancelados", 0),
                            "Estado": clase_instructor.get("estado", "—"),
                        })
                    st.dataframe(pd.DataFrame(filas_agenda_instructor), hide_index=True, use_container_width=True)

                with tab_agenda_instructor:
                    st.caption("Consulta tus próximas clases y el número de alumnos reservados.")
                    mostrar_clases_instructor(agenda_futura_instructor)
                with tab_historial_instructor:
                    st.caption("Consulta las clases impartidas, las asistencias y las inasistencias registradas.")
                    mostrar_clases_instructor(historial_clases_instructor)
                with tab_pagos_instructor:
                    pagos_instructor_portal = supabase.table("pagos_instructoras").select(
                        "id,sesion_id,fecha_pago,importe,referencia"
                    ).eq("instructora_id", id_instructor_portal).order("fecha_pago", desc=True).limit(1000).execute().data or []
                    if pagos_instructor_portal:
                        sesiones_pago_portal = supabase.table("sesiones_clase").select(
                            "id,local_id,fecha_clase,hora_inicio,tipo_servicio"
                        ).in_("id", [p["sesion_id"] for p in pagos_instructor_portal]).execute().data or []
                        sesiones_pago_map = {s["id"]: s for s in sesiones_pago_portal}
                        filas_pagos_instructor = []
                        for pago_instructor in pagos_instructor_portal:
                            sesion_pago_instructor = sesiones_pago_map.get(pago_instructor["sesion_id"], {})
                            filas_pagos_instructor.append({
                                "Fecha de clase": fecha_visible(sesion_pago_instructor.get("fecha_clase")),
                                "Horario": str(sesion_pago_instructor.get("hora_inicio", ""))[:5],
                                "Fecha de pago": fecha_visible(pago_instructor.get("fecha_pago")),
                                "Sede": sedes_instructor_map.get(int(sesion_pago_instructor["local_id"]), "Sede") if sesion_pago_instructor.get("local_id") is not None else "—",
                                "Clase": sesion_pago_instructor.get("tipo_servicio", "—"),
                                "Importe recibido": f"S/ {float(pago_instructor.get('importe') or 0):.2f}",
                                "Referencia": pago_instructor.get("referencia") or "—",
                            })
                        st.metric("Total recibido", f"S/ {sum(float(p.get('importe') or 0) for p in pagos_instructor_portal):.2f}")
                        st.dataframe(pd.DataFrame(filas_pagos_instructor), hide_index=True, use_container_width=True)
                    else:
                        st.info("Aún no hay pagos registrados a tu nombre.")
            except Exception as error_portal_instructor:
                st.error(f"No se pudo cargar tu agenda o tus pagos. Revisa la migración y los permisos de Supabase. Detalle: {error_portal_instructor}")

    elif rol_acceso == "Tablet Check-in":
        st.title(":material/qr_code_scanner: Estación de Check-in (Tablet del Local)")
        st.write("Escanea el pase QR del alumno para registrar su asistencia.")
        aviso_checkin = st.session_state.pop("aviso_checkin", None)
        if aviso_checkin:
            st.success(aviso_checkin)
        try:
            supabase.rpc("marcar_inasistencias_vencidas", {}).execute()
        except Exception:
            pass
        foto_qr = st.camera_input("Enfoca el código QR del alumno", key=f"camara_checkin_{st.session_state.clear_checkin}")
        if foto_qr is not None and st.button("Registrar asistencia", type="primary", key="procesar_checkin_qr"):
            try:
                import cv2
                import numpy as np
                imagen_bytes = np.frombuffer(foto_qr.getvalue(), dtype=np.uint8)
                imagen = cv2.imdecode(imagen_bytes, cv2.IMREAD_COLOR)
                contenido_qr, _, _ = cv2.QRCodeDetector().detectAndDecode(imagen)
                prefijo_qr = "PILATES-CHECKIN:"
                if not contenido_qr or not contenido_qr.startswith(prefijo_qr):
                    st.error("No se pudo leer un pase QR válido. Vuelve a enfocar el código.")
                else:
                    resultado_checkin = supabase.rpc("registrar_asistencia_qr", {"p_qr_token": contenido_qr[len(prefijo_qr):]}).execute().data or []
                    if resultado_checkin:
                        detalle_checkin = resultado_checkin[0]
                        st.session_state.aviso_checkin = f"Asistencia registrada para {detalle_checkin.get('nombre_alumno')} · {fecha_visible(detalle_checkin.get('fecha_clase'))} {str(detalle_checkin.get('hora_inicio'))[:5]} · {detalle_checkin.get('sede')}."
                        st.session_state.clear_checkin += 1
                        st.rerun()
                    else:
                        st.error("El QR no corresponde a una reserva válida para esta hora.")
            except Exception as error_checkin:
                st.error(f"No se pudo registrar la asistencia: {error_checkin}")
                
    # --- VISTA ADMINISTRADOR ---
    elif rol_acceso == "Administrador":
        if not st.session_state.logged_in:
            st.title(":material/lock: Panel Administrativo Privado")
            with st.form(f"form_login_{st.session_state.clear_login}"):
                user_input = st.text_input("Usuario:", key=f"login_usuario_{st.session_state.clear_login}")
                pass_input = st.text_input("Contraseña:", type="password", key=f"login_clave_{st.session_state.clear_login}")
                ingresar = st.form_submit_button("Ingresar", type="primary")
                limpiar_login = st.form_submit_button("Limpiar campos")

            if limpiar_login:
                st.session_state.clear_login += 1
                st.rerun()
            if ingresar:
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
                            else normalizar_permisos_admin(permisos_guardados)
                        )
                        st.session_state.admin_migracion_pendiente = esquema_antiguo
                        st.session_state.logged_in = True
                        st.session_state.clear_login += 1
                        # Cada sesión administrativa inicia la Gestión de Alumnos en el directorio.
                        st.session_state.kardex_alumno_id = None
                        st.session_state.pop("selector_predictivo_kardex", None)
                        st.session_state.pop("alumno_en_edicion_id", None)
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas.")
                except Exception as e:
                    st.error(f"❌ Error al validar credenciales: {e}")
        else:
            st.title(":material/dashboard: Panel de Control")
            mensaje_resultado_app = st.session_state.pop("mensaje_resultado_app", None)
            if mensaje_resultado_app:
                st.success(mensaje_resultado_app)
            if st.sidebar.button("Cerrar sesión", icon=":material/logout:", type="primary"):
                st.session_state.logged_in = False
                st.session_state.clear_login += 1
                st.session_state.admin_id = None
                st.session_state.admin_usuario = ""
                st.session_state.admin_es_superadmin = False
                st.session_state.admin_permisos = []
                st.session_state.admin_migracion_pendiente = False
                st.session_state.kardex_alumno_id = None
                st.session_state.pop("selector_predictivo_kardex", None)
                st.session_state.pop("alumno_en_edicion_id", None)
                st.rerun()
                
            # Inicializar llaves de control para limpiar formularios si no existen
            if "clear_local" not in st.session_state: st.session_state.clear_local = 0
            if "clear_ins" not in st.session_state: st.session_state.clear_ins = 0
            if "clear_ren" not in st.session_state: st.session_state.clear_ren = 0
            if "clear_search" not in st.session_state: st.session_state.clear_search = 0
            if "clear_plan" not in st.session_state: st.session_state.clear_plan = 0
            for llave_limpieza in ("clear_instructora", "clear_agenda", "clear_feriado", "clear_usuario", "clear_tarifa", "clear_cuenta", "clear_reset_clave", "clear_configuracion", "clear_editar_alumno", "clear_permisos", "clear_eliminar_usuario", "clear_catalogo", "clear_dias_operativos", "clear_feriados_tabla", "clear_paquete_alumno", "clear_gestion_instructoras", "clear_programacion_clases", "clear_estado_sesion", "clear_pago_instructora"):
                if llave_limpieza not in st.session_state:
                    st.session_state[llave_limpieza] = 0

            # LECTURA GLOBAL DE CATÁLOGOS COLECTIVOS (Variables seguras en memoria)
            lista_locales_admin = []
            locales_tiene_baja = True
            try:
                try:
                    locales_res = supabase.table("locales").select("id,nombre,direccion,activo,max_camillas").order("nombre").execute()
                    lista_locales_admin = locales_res.data or []
                except Exception as error_columna_local:
                    if "42703" not in str(error_columna_local) and getattr(error_columna_local, "code", None) != "42703":
                        raise
                    locales_tiene_baja = False
                    try:
                        locales_res = supabase.table("locales").select("id,nombre,direccion,activo,max_camillas").order("nombre").execute()
                        lista_locales_admin = [{**local, "activo": local.get("activo", True)} for local in (locales_res.data or [])]
                    except Exception:
                        locales_res = supabase.table("locales").select("id,nombre,direccion").order("nombre").execute()
                        lista_locales_admin = [{**local, "activo": True, "max_camillas": 8} for local in (locales_res.data or [])]
                lista_locales = [local for local in lista_locales_admin if local.get("activo", True)]
                opciones_locales = {local['nombre']: local['id'] for local in lista_locales}
                
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
                or (clave == "instructoras" and "agenda" in permisos_sesion)
                or (clave == "alumnos_operacion" and bool({"inscripciones", "renovaciones", "alumnos"} & permisos_sesion))
            ]
            claves_pestanas = ventanas_visibles + ["mi_cuenta"]
            if st.session_state.admin_es_superadmin:
                claves_pestanas.append("usuarios")
            nombres_pestanas = {**VENTANAS_ADMIN, "mi_cuenta": "Mi cuenta", "usuarios": "Usuarios y permisos"}
            pestanas = st.tabs([nombres_pestanas[clave] for clave in claves_pestanas], key="tabs_admin_principales", on_change="rerun")
            paneles_admin = dict(zip(claves_pestanas, pestanas))
            # Conserva las cuentas antiguas que tenían un permiso separado llamado "Agenda".
            if "instructoras" in paneles_admin:
                paneles_admin["agenda"] = paneles_admin["instructoras"]
            if "alumnos_operacion" in paneles_admin:
                with paneles_admin["alumnos_operacion"]:
                    st.caption("Elige una pestaña según la tarea que quieras realizar.")
                    tab_alta_alumno, tab_renovar_alumno, tab_directorio_alumno = st.tabs([
                        "1. Inscribir alumno",
                        "2. Renovar o cambiar plan",
                        "3. Buscar y gestionar alumnos",
                    ], key="tabs_gestion_alumnos", on_change="rerun")
                    paneles_admin["inscripciones"] = tab_alta_alumno
                    paneles_admin["renovaciones"] = tab_renovar_alumno
                    paneles_admin["alumnos"] = tab_directorio_alumno

            if not ventanas_visibles:
                st.info("Tu cuenta solo tiene acceso a Mi cuenta. Pide a un superadministrador que te asigne otras secciones si las necesitas.")

            if "sucursales" in paneles_admin:
                with paneles_admin["sucursales"]:
                    st.subheader("Gestión de sedes")
                    st.caption("Modifica los datos de una sede o dale de baja para retirarla de los formularios. Las referencias históricas se conservan.")
                    if not locales_tiene_baja:
                        st.warning("Para habilitar bajas de sedes, ejecuta supabase_locales_migration.sql en Supabase.")
                    tab_nueva_sede, tab_gestion_sede = st.tabs(["1. Registrar sede", "2. Buscar y gestionar sedes"], key="tabs_gestion_sedes", on_change="rerun")
                    with tab_nueva_sede:
                        st.markdown("#### Registrar una sede")
                        nombre_local = st.text_input("Nombre de la sede (ej: Barranco):", key=f"loc_name_{st.session_state.clear_local}")
                        direccion_local = st.text_input("Dirección:", key=f"loc_dir_{st.session_state.clear_local}")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("Guardar Local"):
                                if nombre_local:
                                    try:
                                        supabase.table("locales").insert({"nombre": nombre_local, "direccion": direccion_local}).execute()
                                        st.session_state.mensaje_resultado_app = f"La sede {nombre_local.strip()} quedó registrada."
                                        st.session_state.clear_local += 1
                                        st.rerun()
                                    except Exception as e:
                                        if "23505" in str(e):
                                            st.error("Ya existe una sede con ese nombre.")
                                        else:
                                            st.error(f"❌ Error al guardar el local: {e}")
                                else:
                                    st.error("El nombre de la sede es obligatorio.")
                        with col_btn2:
                            if st.button("Limpiar Pantalla", key="btn_clear_loc"):
                                st.session_state.clear_local += 1
                                st.rerun()
    
                    with tab_gestion_sede:
                        st.divider()
                        st.markdown("#### Modificar o dar de baja una sede")
                        if lista_locales_admin:
                            etiquetas_locales = {
                                f"{local['nombre']} {'(Inactiva)' if not local.get('activo', True) else ''}".strip(): local
                                for local in lista_locales_admin
                            }
                            opciones_locales_editar = [""] + list(etiquetas_locales.keys())
                            local_seleccionado_label = st.selectbox(
                                "Sede",
                                opciones_locales_editar,
                                index=0,
                                key=f"local_seleccionado_editar_{st.session_state.clear_local}",
                                placeholder="Selecciona una sede..."
                            )
                            local_seleccionado = etiquetas_locales.get(local_seleccionado_label) or {
                                "id": "", "nombre": "", "direccion": "", "activo": False
                            }
                            local_id = local_seleccionado["id"]
                            nombre_local_editado = st.text_input(
                                "Nombre",
                                value=local_seleccionado["nombre"],
                                key=f"local_nombre_editar_{local_id}_{st.session_state.clear_local}"
                            )
                            direccion_local_editada = st.text_input(
                                "Dirección",
                                value=local_seleccionado.get("direccion") or "",
                                key=f"local_direccion_editar_{local_id}_{st.session_state.clear_local}"
                            )
                            max_camillas_local = st.number_input(
                                "Máximo de camillas",
                                min_value=1,
                                max_value=50,
                                value=int(local_seleccionado.get("max_camillas") or 8),
                                key=f"local_camillas_editar_{local_id}_{st.session_state.clear_local}"
                            )
                            col_local_guardar, col_local_baja = st.columns(2)
                            with col_local_guardar:
                                if st.button("Guardar cambios", key=f"guardar_local_{local_id}_{st.session_state.clear_local}", type="primary", disabled=not local_id):
                                    if not nombre_local_editado.strip():
                                        st.error("El nombre de la sede es obligatorio.")
                                    else:
                                        try:
                                            supabase.table("locales").update({
                                                "nombre": nombre_local_editado.strip(),
                                                "direccion": direccion_local_editada.strip(),
                                                "max_camillas": int(max_camillas_local)
                                            }).eq("id", local_id).execute()
                                            st.session_state.mensaje_resultado_app = f"Los datos de la sede {nombre_local_editado.strip()} se actualizaron."
                                            st.session_state.clear_local += 1
                                            st.rerun()
                                        except Exception as e:
                                            if "23505" in str(e):
                                                st.error("Ya existe otra sede con ese nombre.")
                                            else:
                                                st.error(f"No se pudieron guardar los cambios: {e}")
                            with col_local_baja:
                                if local_id and local_seleccionado.get("activo", True):
                                    confirmar_baja_local = st.checkbox(
                                        "Confirmo dar de baja esta sede",
                                        key=f"confirmar_baja_local_{local_id}_{st.session_state.clear_local}"
                                    )
                                    if st.button("Dar de baja", key=f"baja_local_{local_id}", disabled=not confirmar_baja_local):
                                        if not locales_tiene_baja:
                                            st.error("Ejecuta primero supabase_locales_migration.sql en Supabase.")
                                        else:
                                            try:
                                                supabase.table("locales").update({"activo": False}).eq("id", local_id).execute()
                                                st.session_state.mensaje_resultado_app = f"La sede {local_seleccionado['nombre']} quedó inactiva."
                                                st.session_state.clear_local += 1
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"No se pudo dar de baja la sede: {e}")
                                elif local_id:
                                    if st.button("Reactivar sede", key=f"reactivar_local_{local_id}_{st.session_state.clear_local}"):
                                        try:
                                            supabase.table("locales").update({"activo": True}).eq("id", local_id).execute()
                                            st.session_state.mensaje_resultado_app = f"La sede {local_seleccionado['nombre']} volvió a estar activa."
                                            st.session_state.clear_local += 1
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"No se pudo reactivar la sede: {e}")
                                else:
                                    st.info("Selecciona una sede para editarla.")
                        else:
                            st.info("Registra una sede para habilitar su edición.")
    
            if "inscripciones" in paneles_admin:
                with paneles_admin["inscripciones"]:
                    st.subheader("Inscribir alumno")
                    st.caption("Registra sus datos y confirma el pago del plan para activar su inscripción.")
                    aviso_inscripcion = st.session_state.pop("aviso_inscripcion", None)
                    if aviso_inscripcion:
                        st.success(aviso_inscripcion)
                        
                    col1, col2 = st.columns(2)
                    with col1:
                        a_nombre = st.text_input("Nombre del Alumno:", key=f"ins_nom_{st.session_state.clear_ins}")
                        a_apellido = st.text_input("Apellido del Alumno:", key=f"ins_ape_{st.session_state.clear_ins}")
                        a_telefono = st.text_input("Teléfono (único para acceso móvil):", key=f"ins_tel_{st.session_state.clear_ins}")
                    with col2:
                        tipo_p = st.selectbox("Selecciona el Paquete:", [""] + list(opciones_planes.keys()), key=f"ins_paq_{st.session_state.clear_ins}", placeholder="Selecciona un plan...")
                        modalidad = st.selectbox("Modalidad de Acceso:", ["", "Fixed", "Flex"], key=f"ins_mod_{st.session_state.clear_ins}", placeholder="Selecciona una modalidad...")
                        sede_assigned = ""
                        if modalidad == "Fixed":
                            sede_assigned = st.selectbox("Sede Base / Asignada:", [""] + list(opciones_locales.keys()), key=f"ins_sed_{st.session_state.clear_ins}", placeholder="Selecciona una sede...")
                        elif modalidad == "Flex":
                            st.write("✨ Plan Flex seleccionado: El alumno tendrá acceso a todas las sedes libres.")
                                
                    if tipo_p in costos_planes and costos_planes[tipo_p] > 0:
                        st.info(f"💵 **Valor comercial del paquete seleccionado:** S/ {costos_planes[tipo_p]:.2f}")

                    inscripcion_completa = bool(
                        a_nombre.strip() and a_apellido.strip() and a_telefono.strip()
                        and tipo_p and modalidad
                        and (modalidad != "Fixed" or sede_assigned in opciones_locales)
                    )
                    if inscripcion_completa:
                        fecha_vencimiento_inscripcion = datetime.now(ZoneInfo("America/Lima")).date() + timedelta(days=30)
                        sede_resumen = f" · Sede: {sede_assigned}" if modalidad == "Fixed" else ""
                        st.info(
                            f"**Resumen de inscripción**  \n"
                            f"Alumno: {a_nombre.strip()} {a_apellido.strip()} · Paquete: {tipo_p} "
                            f"({opciones_planes[tipo_p]} clases) · Acceso: {modalidad}{sede_resumen} · "
                            f"Vencimiento: {fecha_vencimiento_inscripcion.strftime('%d-%m-%Y')} · "
                            f"Total a pagar: S/ {costos_planes.get(tipo_p, 0):.2f}"
                        )
                        confirmar_pago_inscripcion = st.checkbox(
                            "Confirmo que el alumno ya pagó el plan indicado.",
                            key=f"pago_confirmado_ins_{st.session_state.clear_ins}"
                        )
                    else:
                        confirmar_pago_inscripcion = False
                        st.caption("Completa los datos del alumno y del plan para revisar el detalle antes de confirmar el pago.")
                        
                    col_i1, col_i2 = st.columns(2)
                    with col_i1:
                        if st.button("Confirmar pago e inscribir", type="primary", key=f"registrar_alumno_{st.session_state.clear_ins}"):
                            if not a_nombre.strip() or not a_apellido.strip() or not a_telefono.strip():
                                st.error("❌ Completa el nombre, apellido y teléfono del alumno.")
                            elif not opciones_planes:
                                st.error("❌ No puedes registrar alumnos: primero configura al menos un plan vigente en Planes y precios.")
                            elif not tipo_p or tipo_p not in opciones_planes:
                                st.error("❌ Selecciona un plan vigente.")
                            elif modalidad not in ("Fixed", "Flex"):
                                st.error("❌ Selecciona la modalidad de acceso.")
                            elif modalidad == "Fixed" and not opciones_locales:
                                st.error("❌ No hay sedes activas. Registra una sede o elige modalidad Flex.")
                            elif modalidad == "Fixed" and sede_assigned not in opciones_locales:
                                st.error("❌ Selecciona una sede válida para la modalidad Fixed.")
                            elif not confirmar_pago_inscripcion:
                                st.error("❌ Confirma que el alumno ya pagó el plan para continuar con la inscripción.")
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
                                    fecha_vence = (datetime.now(ZoneInfo("America/Lima")).date() + timedelta(days=30)).isoformat()
                                    id_local_fijo = opciones_locales[sede_assigned] if modalidad == "Fixed" else None
                                    id_paquete_creado = None
                                    try:
                                        fecha_pago = datetime.now(ZoneInfo("America/Lima")).isoformat()
                                        nuevo_paquete = supabase.table("paquetes").insert({
                                            "alumno_id": id_alumno,
                                            "tipo_paquete": tipo_p,
                                            "modalidad_plan": modalidad,
                                            "local_id_fijo": id_local_fijo,
                                            "clases_totales": total_c,
                                            "clases_restantes": total_c,
                                            "fecha_vencimiento": fecha_vence,
                                            "estado": "Activo",
                                            "pagado": True,
                                            "fecha_pago": fecha_pago,
                                            "pago_confirmado_por": st.session_state.admin_id
                                        }).select("id").execute()
                                        if not nuevo_paquete.data:
                                            raise RuntimeError("No se recibió el identificador del paquete.")
                                        id_paquete_creado = nuevo_paquete.data[0]["id"]
                                        supabase.table("eventos_paquetes").insert({
                                            "paquete_id": id_paquete_creado,
                                            "alumno_id": id_alumno,
                                            "tipo_evento": "inscripcion",
                                            "realizado_por": st.session_state.admin_id,
                                            "detalles": {
                                                "alumno": f"{a_nombre.strip()} {a_apellido.strip()}",
                                                "tipo_paquete": tipo_p,
                                                "modalidad_plan": modalidad,
                                                "local_id_fijo": id_local_fijo,
                                                "clases_totales": total_c,
                                                "costo": costos_planes.get(tipo_p, 0),
                                                "fecha_vencimiento": fecha_vence,
                                                "fecha_pago": fecha_pago
                                            }
                                        }).execute()
                                    except Exception:
                                        if id_paquete_creado is not None:
                                            supabase.table("paquetes").delete().eq("id", id_paquete_creado).execute()
                                        supabase.table("alumnos").delete().eq("id", id_alumno).execute()
                                        raise
                                    st.session_state.aviso_inscripcion = f"Pago confirmado e inscripción registrada para {a_nombre.strip()} {a_apellido.strip()}."
                                    st.session_state.clear_ins += 1
                                    st.balloons()
                                    st.rerun()
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
                    st.divider()
                    st.subheader("Renovar o cambiar plan")
                    st.caption("Busca al alumno, revisa el plan actual y confirma el pago antes de aplicar la renovación o mejora.")
                    aviso_renovacion = st.session_state.pop("aviso_renovacion", None)
                    if aviso_renovacion:
                        st.success(aviso_renovacion)
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
                            hoy = datetime.now(ZoneInfo("America/Lima")).date().isoformat()
                            paquete_previo = (
                                supabase.table("paquetes")
                                .select("id,clases_restantes,fecha_vencimiento,estado")
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
                                tipo_p_nuevo = st.selectbox("Nuevo Paquete:", [""] + list(opciones_planes.keys()), key=f"ren_p_{st.session_state.clear_ren}", placeholder="Selecciona un plan...")
                                modalidad_nueva = st.selectbox("Nueva Modalidad de Acceso:", ["", "Fixed", "Flex"], key=f"ren_m_{st.session_state.clear_ren}", placeholder="Selecciona una modalidad...")
                            with col_ren2:
                                sede_assigned_new = ""
                                if modalidad_nueva == "Fixed":
                                    sede_assigned_new = st.selectbox("Asignar Sede para este periodo:", [""] + list(opciones_locales.keys()), key=f"ren_s_{st.session_state.clear_ren}", placeholder="Selecciona una sede...")
                                elif modalidad_nueva == "Flex": st.write("✨ Plan Flex seleccionado: Acceso global habilitado.")
                                    
                            if tipo_p_nuevo in costos_planes and costos_planes[tipo_p_nuevo] > 0:
                                st.info(f"💵 **Valor comercial de esta renovación:** S/ {costos_planes[tipo_p_nuevo]:.2f}")

                            renovacion_completa = bool(
                                tipo_p_nuevo in opciones_planes and modalidad_nueva
                                and (modalidad_nueva != "Fixed" or sede_assigned_new in opciones_locales)
                            )
                            fecha_vencimiento_renovacion = datetime.now(ZoneInfo("America/Lima")).date() + timedelta(days=30)
                            if renovacion_completa:
                                base_resumen_renovacion = opciones_planes[tipo_p_nuevo]
                                total_resumen_renovacion = base_resumen_renovacion + clases_flotantes
                                sede_resumen_renovacion = f" · Sede: {sede_assigned_new}" if modalidad_nueva == "Fixed" else ""
                                st.info(
                                    f"**Resumen de renovación**  \n"
                                    f"Alumno: {alumno_sel} · Paquete: {tipo_p_nuevo} · "
                                    f"Clases del plan: {base_resumen_renovacion} · Saldo anterior: {clases_flotantes} · "
                                    f"Saldo total: {total_resumen_renovacion} · Acceso: {modalidad_nueva}{sede_resumen_renovacion} · "
                                    f"Vencimiento: {fecha_vencimiento_renovacion.strftime('%d-%m-%Y')} · "
                                    f"Total a pagar: S/ {costos_planes.get(tipo_p_nuevo, 0):.2f}"
                                )
                                confirmar_pago_renovacion = st.checkbox(
                                    "Confirmo que el alumno ya pagó la renovación.",
                                    key=f"pago_confirmado_ren_{st.session_state.clear_ren}"
                                )
                            else:
                                confirmar_pago_renovacion = False
                                st.caption("Selecciona alumno, paquete y modalidad para revisar el detalle y confirmar el pago.")
                                    
                            col_r1, col_r2 = st.columns(2)
                            with col_r1:
                                if st.button("Confirmar pago y renovar", type="primary", disabled=not (renovacion_completa and confirmar_pago_renovacion), key=f"procesar_renovacion_{st.session_state.clear_ren}"):
                                    try:
                                        if not tipo_p_nuevo or not modalidad_nueva:
                                            st.error("❌ Selecciona un plan y una modalidad antes de renovar.")
                                        elif not opciones_planes or tipo_p_nuevo not in opciones_planes:
                                            st.error("❌ Selecciona un plan vigente antes de renovar.")
                                        elif modalidad_nueva == "Fixed" and (not opciones_locales or sede_assigned_new not in opciones_locales):
                                            st.error("❌ Selecciona una sede válida para el plan Fixed.")
                                        else:
                                            base_nuevas = opciones_planes[tipo_p_nuevo]
                                            total_unificado = base_nuevas + clases_flotantes
                                            fecha_vence_nueva = (datetime.now(ZoneInfo("America/Lima")).date() + timedelta(days=30)).isoformat()
                                            id_local_fijo_nuevo = opciones_locales[sede_assigned_new] if modalidad_nueva == "Fixed" else None
                                            fecha_pago_renovacion = datetime.now(ZoneInfo("America/Lima")).isoformat()
                                            paquete_nuevo = supabase.table("paquetes").insert({
                                                "alumno_id": id_alumno_sel, "tipo_paquete": tipo_p_nuevo, "modalidad_plan": modalidad_nueva,
                                                "local_id_fijo": id_local_fijo_nuevo, "clases_totales": total_unificado, "clases_restantes": total_unificado,
                                                "fecha_vencimiento": fecha_vence_nueva, "estado": "Activo", "pagado": True,
                                                "fecha_pago": fecha_pago_renovacion, "pago_confirmado_por": st.session_state.admin_id
                                            }).select("id").execute()
                                            if not paquete_nuevo.data:
                                                raise RuntimeError("No se recibió el identificador del paquete renovado.")
                                            try:
                                                if paquetes_vigentes:
                                                    supabase.table("paquetes").update({"estado": "Agotado"}).in_(
                                                        "id", [p["id"] for p in paquetes_vigentes]
                                                    ).execute()
                                                supabase.table("eventos_paquetes").insert({
                                                    "paquete_id": paquete_nuevo.data[0]["id"],
                                                    "alumno_id": id_alumno_sel,
                                                    "tipo_evento": "renovacion",
                                                    "realizado_por": st.session_state.admin_id,
                                                    "detalles": {
                                                        "tipo_paquete": tipo_p_nuevo,
                                                        "modalidad_plan": modalidad_nueva,
                                                        "local_id_fijo": id_local_fijo_nuevo,
                                                        "clases_totales": total_unificado,
                                                        "clases_plan": base_nuevas,
                                                        "clases_anteriores_sumadas": clases_flotantes,
                                                        "costo": costos_planes.get(tipo_p_nuevo, 0),
                                                        "fecha_vencimiento": fecha_vence_nueva,
                                                        "fecha_pago": fecha_pago_renovacion,
                                                        "paquetes_anteriores": [{"id": p["id"], "estado": p.get("estado")} for p in paquetes_vigentes]
                                                    }
                                                }).execute()
                                            except Exception:
                                                for paquete_anterior in paquetes_vigentes:
                                                    supabase.table("paquetes").update({"estado": paquete_anterior.get("estado", "Activo")}).eq("id", paquete_anterior["id"]).execute()
                                                supabase.table("paquetes").delete().eq("id", paquete_nuevo.data[0]["id"]).execute()
                                                raise
                                            st.session_state.aviso_renovacion = f"Pago confirmado y renovación registrada para {alumno_sel}: {total_unificado} clases disponibles."
                                            st.session_state.clear_ren += 1
                                            st.balloons()
                                            st.rerun()
                                    except Exception as e: st.error(f"❌ Error al procesar la renovación: {e}")
                            with col_r2:
                                if st.button("Limpiar Pantalla", key="btn_clear_ren"):
                                    st.session_state.clear_ren += 1
                                    st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

            if "planes" in paneles_admin:
                with paneles_admin["planes"]:
                    st.subheader(":material/payments: Catálogo de planes, clases y costos")
                    aviso_planes = st.session_state.pop("aviso_planes", None)
                    if aviso_planes:
                        st.success(aviso_planes)
                    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
                        "1. Crear plan",
                        "2. Actualizar precios",
                        "3. Consultar planes",
                    ], key="tabs_planes", on_change="rerun")
                                
                    with sub_tab1:
                        st.markdown("#### Registro de Nuevas Ofertas Comerciales")
                        p_nombre = st.text_input("Nombre del nuevo paquete (ej: Plan Black 30 clases):", key=f"p_n_{st.session_state.clear_plan}")
                        p_clases = st.number_input("Cantidad exacta de clases asignadas:", min_value=1, max_value=200, value=None, placeholder="Escribe la cantidad", key=f"p_c_{st.session_state.clear_plan}")
                        p_costo = st.number_input("Precio / Costo comercial del plan (S/):", min_value=0.0, max_value=5000.0, value=None, step=10.0, placeholder="Escribe el precio", key=f"p_v_{st.session_state.clear_plan}")
                                    
                        col_p1, col_p2 = st.columns(2)
                        with col_p1:
                            if st.button("Dar de Alta Plan"):
                                if p_nombre.strip() and p_clases is not None and p_costo is not None:
                                    try:
                                        supabase.table("tipos_paquetes").insert({"nombre_paquete": p_nombre, "clases_totales": p_clases, "costo": p_costo}).execute()
                                        st.session_state.aviso_planes = f"Plan '{p_nombre.strip()}' añadido al catálogo."
                                        st.session_state.clear_plan += 1
                                        st.rerun()
                                    except Exception as e: st.error(f"❌ Error al guardar el plan: {e}")
                                else: st.error("Completa el nombre, la cantidad de clases y el precio.")
                        with col_p2:
                            if st.button("Limpiar Pantalla", key="btn_clear_plan"):
                                st.session_state.clear_plan += 1
                                st.rerun()
                                            
                    with sub_tab2:
                        st.markdown("#### Actualizar Precios de Planes Existentes")
                        if opciones_planes:
                            plan_a_modificar = st.selectbox("Selecciona el plan que deseas actualizar:", [""] + list(opciones_planes.keys()), key=f"tarifa_plan_{st.session_state.clear_tarifa}", placeholder="Selecciona un plan...")
                            if plan_a_modificar:
                                nuevo_precio = st.number_input("Establecer nuevo precio (S/):", min_value=0.0, max_value=5000.0, value=costos_planes.get(plan_a_modificar, 0.0), step=5.0, key=f"tarifa_precio_{st.session_state.clear_tarifa}_{plan_a_modificar}")
                            else:
                                nuevo_precio = None
                            col_tarifa_1, col_tarifa_2 = st.columns(2)
                            with col_tarifa_1:
                                if st.button("Actualizar Tarifa Comercial", key=f"actualizar_tarifa_comercial_{st.session_state.clear_tarifa}", disabled=not plan_a_modificar):
                                    try:
                                        supabase.table("tipos_paquetes").update({"costo": nuevo_precio}).eq("nombre_paquete", plan_a_modificar).execute()
                                        st.session_state.aviso_planes = f"Precio de '{plan_a_modificar}' actualizado a S/ {nuevo_precio:.2f}."
                                        st.session_state.clear_tarifa += 1
                                        st.rerun()
                                    except Exception as e: st.error(f"❌ Error al actualizar precio: {e}")
                            with col_tarifa_2:
                                if st.button("Limpiar campos", key="limpiar_tarifa"):
                                    st.session_state.clear_tarifa += 1
                                    st.rerun()
                        else: st.info("No hay planes configurados para modificar.")

                    with sub_tab3:
                        st.markdown("#### Catálogo de planes · precio de menor a mayor")
                        try:
                            todos_planes_res = supabase.table("tipos_paquetes").select("*").order("costo", desc=False).execute()
                            if todos_planes_res.data and len(todos_planes_res.data) > 0:
                                import pandas as pd
                                df_catalogo = pd.DataFrame(todos_planes_res.data)
                                df_catalogo_amigable = df_catalogo[["nombre_paquete", "clases_totales", "costo", "activo"]].rename(columns={
                                    "nombre_paquete": "Nombre del Paquete", "clases_totales": "Clases que Incluye", "costo": "Precio Comercial (S/)", "activo": "Disponible para Venta"
                                })
                                editor_catalogo_key = f"editor_catalogo_planes_{st.session_state.clear_catalogo}"
                                cambios_tabla = st.data_editor(df_catalogo_amigable, hide_index=True, disabled=["Nombre del Paquete", "Clases que Incluye", "Precio Comercial (S/)"], use_container_width=True, key=editor_catalogo_key)
                                if st.session_state.get(editor_catalogo_key) and "edited_rows" in st.session_state[editor_catalogo_key]:
                                    filas_editadas = st.session_state[editor_catalogo_key]["edited_rows"]
                                    for indice_fila, cambios in filas_editadas.items():
                                        if "Disponible para Venta" in cambios:
                                            nuevo_estado = cambios["Disponible para Venta"]
                                            id_registro = int(df_catalogo.iloc[indice_fila]["id"])
                                            supabase.table("tipos_paquetes").update({"activo": nuevo_estado}).eq("id", id_registro).execute()
                                            st.session_state.mensaje_resultado_app = f"La disponibilidad del plan {df_catalogo.iloc[indice_fila]['nombre_paquete']} se actualizó."
                                            st.session_state.clear_catalogo += 1
                                            st.rerun()
                            else: st.info("💡 No se encontraron planes registrados.")
                        except Exception as e: st.error(f"Error: {e}")
                                    
            if "instructoras" in paneles_admin:
                with paneles_admin["instructoras"]:
                    st.subheader(":material/groups: Gestión de instructores")
                    st.caption("Registra al equipo, organiza las clases, consulta sus fichas y lleva el control de pagos.")
                    aviso_instructora = st.session_state.pop("aviso_instructora", None)
                    if aviso_instructora:
                        st.success(aviso_instructora)

                    tab_alta_inst, tab_directorio_inst, tab_agenda_inst, tab_pagos_inst = st.tabs([
                        "1. Registrar instructor",
                        "2. Buscar y gestionar",
                        "3. Agenda de clases",
                        "4. Pagos realizados",
                    ], key="tabs_gestion_instructores", on_change="rerun")
                    try:
                        instructoras_res = supabase.table("instructoras").select("id,nombre,telefono,pago_por_clase,activo").order("nombre").execute()
                        instructoras_db = instructoras_res.data or []
                    except Exception as e:
                        instructoras_db = []
                        st.error(f"No se pudo cargar el directorio de instructores: {e}")

                    with tab_directorio_inst:
                        if instructoras_db:
                            opciones_instructoras = {
                                f"{i['nombre']} · {'Activa' if i.get('activo', True) else 'Inactiva'}": i
                                for i in instructoras_db
                            }
                            etiqueta_instructora = st.selectbox(
                                "Busca y selecciona un instructor:",
                                [""] + list(opciones_instructoras),
                                key=f"buscar_instructora_{st.session_state.clear_gestion_instructoras}",
                                placeholder="Escribe su nombre..."
                            )
                            instructora_actual = opciones_instructoras.get(etiqueta_instructora)
                            if instructora_actual:
                                st.markdown(f"### {instructora_actual['nombre']}")
                                estado_instructora = "Activo" if instructora_actual.get("activo", True) else "Inactivo"
                                st.caption(f"Estado: {estado_instructora} · Teléfono: {instructora_actual.get('telefono') or 'No registrado'} · Pago acordado por clase: S/ {float(instructora_actual.get('pago_por_clase') or 0):.2f}")

                                with st.expander("Modificar datos personales y tarifa", expanded=False):
                                    with st.form(f"form_editar_instructora_{instructora_actual['id']}_{st.session_state.clear_gestion_instructoras}"):
                                        nombre_inst_editado = st.text_input("Nombre completo", value=instructora_actual["nombre"], key=f"nombre_inst_edit_{instructora_actual['id']}_{st.session_state.clear_gestion_instructoras}")
                                        telefono_inst_editado = st.text_input("Teléfono", value=instructora_actual.get("telefono") or "", key=f"telefono_inst_edit_{instructora_actual['id']}_{st.session_state.clear_gestion_instructoras}")
                                        tarifa_inst_editada = st.number_input("Pago fijo por clase (S/)", min_value=0.0, value=float(instructora_actual.get("pago_por_clase") or 0), step=5.0, key=f"tarifa_inst_edit_{instructora_actual['id']}_{st.session_state.clear_gestion_instructoras}")
                                        guardar_inst_editada = st.form_submit_button("Guardar cambios", type="primary")
                                        limpiar_inst_editada = st.form_submit_button("Restaurar datos")
                                    if limpiar_inst_editada:
                                        st.session_state.clear_gestion_instructoras += 1
                                        st.rerun()
                                    elif guardar_inst_editada:
                                        if not nombre_inst_editado.strip():
                                            st.error("El nombre de la persona es obligatorio.")
                                        else:
                                            try:
                                                supabase.table("instructoras").update({
                                                    "nombre": nombre_inst_editado.strip(),
                                                    "telefono": telefono_inst_editado.strip() or None,
                                                    "pago_por_clase": tarifa_inst_editada
                                                }).eq("id", instructora_actual["id"]).execute()
                                                st.session_state.aviso_instructora = "Datos del instructor actualizados. Las sesiones existentes conservan el pago acordado al programarlas."
                                                st.session_state.clear_gestion_instructoras += 1
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"No se pudieron guardar los datos: {e}")

                                col_estado_inst, col_ficha_inst = st.columns([1, 2])
                                with col_estado_inst:
                                    if instructora_actual.get("activo", True):
                                        confirmar_baja_inst = st.checkbox(
                                            "Confirmo dar de baja a este instructor",
                                            key=f"confirmar_baja_inst_{instructora_actual['id']}_{st.session_state.clear_gestion_instructoras}"
                                        )
                                        if st.button("Dar de baja", key=f"baja_inst_{instructora_actual['id']}_{st.session_state.clear_gestion_instructoras}", disabled=not confirmar_baja_inst):
                                            try:
                                                supabase.table("instructoras").update({"activo": False}).eq("id", instructora_actual["id"]).execute()
                                                st.session_state.aviso_instructora = f"{instructora_actual['nombre']} quedó inactivo. Su historial se conserva."
                                                st.session_state.clear_gestion_instructoras += 1
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"No se pudo dar de baja: {e}")
                                    else:
                                        if st.button("Reactivar instructor", key=f"reactivar_inst_{instructora_actual['id']}_{st.session_state.clear_gestion_instructoras}"):
                                            try:
                                                supabase.table("instructoras").update({"activo": True}).eq("id", instructora_actual["id"]).execute()
                                                st.session_state.aviso_instructora = f"{instructora_actual['nombre']} volvió a estar activo."
                                                st.session_state.clear_gestion_instructoras += 1
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"No se pudo reactivar: {e}")

                                try:
                                    sesiones_inst_res = (
                                        supabase.table("sesiones_clase")
                                        .select("id,local_id,fecha_clase,hora_inicio,hora_fin,tipo_servicio,capacidad,estado,pago_por_clase_aplicado")
                                        .eq("instructora_id", instructora_actual["id"])
                                        .order("fecha_clase")
                                        .order("hora_inicio")
                                        .limit(500)
                                        .execute()
                                    )
                                    sesiones_inst = sesiones_inst_res.data or []
                                    pagos_inst_res = (
                                        supabase.table("pagos_instructoras")
                                        .select("id,sesion_id,fecha_pago,importe,referencia")
                                        .eq("instructora_id", instructora_actual["id"])
                                        .order("fecha_pago", desc=True)
                                        .limit(500)
                                        .execute()
                                    )
                                    pagos_inst = pagos_inst_res.data or []
                                    pagos_por_sesion = {p["sesion_id"]: p for p in pagos_inst}
                                    completadas_inst = [s for s in sesiones_inst if s["estado"] == "Realizada"]

                                    # Un pago solo procede si hay al menos un alumno marcado con asistencia o inasistencia.
                                    ids_sesiones_inst = [s["id"] for s in completadas_inst]
                                    reservas_por_sesion = {}
                                    if ids_sesiones_inst:
                                        reservas_inst = (
                                            supabase.table("reservas")
                                            .select("id,sesion_id,alumno_id,estado")
                                            .in_("sesion_id", ids_sesiones_inst)
                                            .execute()
                                        ).data or []
                                        estados_asistencia = {"asistencia", "asistio", "presente"}
                                        estados_inasistencia = {"inasistencia", "no asistio", "ausente", "falta", "no show", "no-show"}
                                        for reserva in reservas_inst:
                                            if reserva.get("alumno_id") is None:
                                                continue
                                            estado_reserva = unicodedata.normalize("NFKD", str(reserva.get("estado") or "").lower())
                                            estado_reserva = "".join(c for c in estado_reserva if not unicodedata.combining(c)).strip()
                                            if estado_reserva in estados_asistencia or estado_reserva in estados_inasistencia:
                                                reservas_por_sesion.setdefault(reserva["sesion_id"], []).append({
                                                    "estado": "Asistencia" if estado_reserva in estados_asistencia else "Inasistencia"
                                                })

                                    def minutos_sesion(sesion):
                                        inicio = datetime_time.fromisoformat(str(sesion["hora_inicio"]))
                                        fin = datetime_time.fromisoformat(str(sesion["hora_fin"]))
                                        return int((datetime.combine(datetime.now(ZoneInfo("America/Lima")).date(), fin) - datetime.combine(datetime.now(ZoneInfo("America/Lima")).date(), inicio)).total_seconds() // 60)

                                    def monto_fijo_sesion(sesion):
                                        # El monto fijo por clase usa la tarifa congelada al programarla.
                                        return float(sesion.get("pago_por_clase_aplicado") or 0)

                                    sesiones_con_evidencia = [s for s in completadas_inst if reservas_por_sesion.get(s["id"])]
                                    sesiones_por_pagar = [s for s in sesiones_con_evidencia if s["id"] not in pagos_por_sesion]
                                    por_pagar_inst = sum(monto_fijo_sesion(s) for s in sesiones_por_pagar)
                                    pagado_inst = sum(float(p.get("importe") or 0) for p in pagos_inst)
                                    horas_inst = sum(minutos_sesion(s) for s in completadas_inst) / 60
                                    met1, met2, met3, met4 = st.columns(4)
                                    met1.metric("Clases realizadas", len(completadas_inst))
                                    met2.metric("Horas dictadas", f"{horas_inst:.1f}")
                                    met3.metric("Pendiente de pago", f"S/ {por_pagar_inst:.2f}")
                                    met4.metric("Pagos registrados", f"S/ {pagado_inst:.2f}")

                                    if sesiones_inst:
                                        st.markdown("#### Horarios, sedes y clases")
                                        locales_por_id_inst = {l["id"]: l["nombre"] for l in lista_locales_admin}
                                        filas_sesiones_inst = []
                                        for sesion in sesiones_inst:
                                            filas_sesiones_inst.append({
                                                "Fecha": fecha_visible(sesion["fecha_clase"]),
                                                "Horario": f"{str(sesion['hora_inicio'])[:5]}–{str(sesion['hora_fin'])[:5]}",
                                                "Sede": locales_por_id_inst.get(sesion["local_id"], "Sede"),
                                                "Clase": sesion["tipo_servicio"],
                                                "Estado": sesion["estado"],
                                                "Asistencia / inasistencia": ", ".join(sorted({r["estado"] for r in reservas_por_sesion.get(sesion["id"], [])})) or "Sin registro",
                                                "Pago": f"S/ {float(pagos_por_sesion[sesion['id']]['importe']):.2f}" if sesion["id"] in pagos_por_sesion else (f"Pendiente · S/ {monto_fijo_sesion(sesion):.2f}" if sesion in sesiones_por_pagar else ("Requiere asistencia o inasistencia" if sesion["estado"] == "Realizada" else "—"))
                                            })
                                        st.dataframe(pd.DataFrame(filas_sesiones_inst), use_container_width=True, hide_index=True)
                                    else:
                                        st.info("Aún no hay clases programadas para este instructor.")

                                    if sesiones_por_pagar:
                                        st.markdown("#### Registrar pago de una clase con asistencia validada")
                                        st.caption("El importe por clase es fijo y corresponde al monto acordado para esta persona; no se multiplica ni se prorratea según la duración.")
                                        pagos_opciones = {
                                            f"{fecha_visible(s['fecha_clase'])} · {str(s['hora_inicio'])[:5]} · {locales_por_id_inst.get(s['local_id'], 'Sede')} · S/ {monto_fijo_sesion(s):.2f}": s
                                            for s in sesiones_por_pagar
                                        }
                                        pago_sesion_label = st.selectbox(
                                            "Clase pendiente de pago:",
                                            [""] + list(pagos_opciones),
                                            key=f"sesion_pago_inst_{instructora_actual['id']}_{st.session_state.clear_pago_instructora}",
                                            placeholder="Selecciona una clase..."
                                        )
                                        pago_referencia = st.text_input("Referencia o nota del pago", key=f"referencia_pago_inst_{instructora_actual['id']}_{st.session_state.clear_pago_instructora}")
                                        if pago_sesion_label:
                                            st.info(f"Importe a registrar: **S/ {monto_fijo_sesion(pagos_opciones[pago_sesion_label]):.2f}**")
                                        if st.button("Registrar pago realizado", key=f"guardar_pago_inst_{instructora_actual['id']}_{st.session_state.clear_pago_instructora}", type="primary", disabled=not pago_sesion_label):
                                            sesion_pagada = pagos_opciones[pago_sesion_label]
                                            try:
                                                # Revalidar inmediatamente antes de registrar el pago.
                                                verificacion_asistencia = supabase.table("reservas").select("id,alumno_id,estado").eq("sesion_id", sesion_pagada["id"]).execute().data or []
                                                estados_validos = {"asistencia", "asistio", "presente", "inasistencia", "no asistio", "ausente", "falta", "no show", "no-show"}
                                                existe_evidencia = False
                                                for reserva in verificacion_asistencia:
                                                    estado_reserva = unicodedata.normalize("NFKD", str(reserva.get("estado") or "").lower())
                                                    estado_reserva = "".join(c for c in estado_reserva if not unicodedata.combining(c)).strip()
                                                    if reserva.get("alumno_id") is not None and estado_reserva in estados_validos:
                                                        existe_evidencia = True
                                                        break
                                                if not existe_evidencia:
                                                    st.error("No se registró el pago: la clase no tiene alumnos con asistencia o inasistencia marcada.")
                                                    st.stop()
                                                supabase.table("pagos_instructoras").insert({
                                                    "sesion_id": sesion_pagada["id"],
                                                    "instructora_id": instructora_actual["id"],
                                                    "fecha_pago": datetime.now(ZoneInfo("America/Lima")).date().isoformat(),
                                                    "pago_por_clase_aplicado": sesion_pagada["pago_por_clase_aplicado"],
                                                    "duracion_minutos": minutos_sesion(sesion_pagada),
                                                    "importe": round(monto_fijo_sesion(sesion_pagada), 2),
                                                    "referencia": pago_referencia.strip() or None,
                                                    "registrado_por": st.session_state.admin_id
                                                }).execute()
                                                st.session_state.aviso_instructora = f"Pago de S/ {monto_fijo_sesion(sesion_pagada):.2f} registrado para {instructora_actual['nombre']}."
                                                st.session_state.clear_pago_instructora += 1
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"No se pudo registrar el pago: {e}")

                                    if pagos_inst:
                                        st.markdown("#### Historial de pagos realizados")
                                        pagos_historial_ordenables = []
                                        ids_sesiones_pagadas = list({p["sesion_id"] for p in pagos_inst})
                                        sesiones_pago_res = supabase.table("sesiones_clase").select(
                                            "id,local_id,fecha_clase,tipo_servicio"
                                        ).in_("id", ids_sesiones_pagadas).execute()
                                        sesiones_por_id = {s["id"]: s for s in (sesiones_pago_res.data or [])}
                                        for pago in pagos_inst:
                                            sesion_pago = sesiones_por_id.get(pago["sesion_id"], {})
                                            fila_pago = {
                                                "Fecha de clase": fecha_visible(sesion_pago.get("fecha_clase")),
                                                "Fecha de pago": fecha_visible(pago["fecha_pago"]),
                                                "Sede": locales_por_id_inst.get(sesion_pago.get("local_id"), "—"),
                                                "Clase": sesion_pago.get("tipo_servicio", "—"),
                                                "Importe": f"S/ {float(pago.get('importe') or 0):.2f}",
                                                "Referencia": pago.get("referencia") or "—"
                                            }
                                            orden_pago = (
                                                str(sesion_pago.get("fecha_clase") or ""),
                                                str(pago.get("fecha_pago") or ""),
                                                fila_pago["Sede"].casefold(),
                                                fila_pago["Clase"].casefold(),
                                                float(pago.get("importe") or 0),
                                                fila_pago["Referencia"].casefold(),
                                            )
                                            pagos_historial_ordenables.append((orden_pago, fila_pago))
                                        pagos_historial = [fila for _, fila in sorted(pagos_historial_ordenables, key=lambda elemento: elemento[0])]
                                        st.dataframe(pd.DataFrame(pagos_historial), use_container_width=True, hide_index=True)
                                except Exception as e:
                                    st.warning(f"Para consultar clases y pagos, ejecuta supabase_gestion_instructoras_migration.sql en Supabase. Detalle: {e}")
                        else:
                            st.info("Registra a una persona del equipo para abrir su ficha y llevar su historial.")

                    with tab_alta_inst:
                        st.markdown("#### Registrar instructor")
                        nombre_inst_nueva = st.text_input("Nombre completo", key=f"alta_inst_nombre_{st.session_state.clear_gestion_instructoras}")
                        telefono_inst_nueva = st.text_input("Teléfono de contacto", key=f"alta_inst_telefono_{st.session_state.clear_gestion_instructoras}")
                        tarifa_inst_nueva = st.number_input("Pago fijo por clase (S/)", min_value=0.0, value=None, step=5.0, placeholder="Escribe el importe", key=f"alta_inst_tarifa_{st.session_state.clear_gestion_instructoras}")
                        col_guardar_inst_nueva, col_limpiar_inst_nueva = st.columns(2)
                        with col_guardar_inst_nueva:
                            if st.button("Guardar instructor", key=f"guardar_inst_nueva_{st.session_state.clear_gestion_instructoras}"):
                                nombre_inst_normalizado = "".join(
                                    c for c in unicodedata.normalize("NFKD", nombre_inst_nueva or "").casefold()
                                    if not unicodedata.combining(c)
                                ).strip()
                                telefono_inst_normalizado = re.sub(r"\D", "", telefono_inst_nueva or "")
                                instructor_existente = next((
                                    instructor for instructor in instructoras_db
                                    if "".join(
                                        c for c in unicodedata.normalize("NFKD", str(instructor.get("nombre") or "")).casefold()
                                        if not unicodedata.combining(c)
                                    ).strip() == nombre_inst_normalizado
                                    or (
                                        telefono_inst_normalizado
                                        and re.sub(r"\D", "", str(instructor.get("telefono") or "")) == telefono_inst_normalizado
                                    )
                                ), None)
                                if not nombre_inst_nueva.strip():
                                    st.error("Ingresa el nombre completo del instructor.")
                                elif instructor_existente:
                                    st.error(f"Ya existe un registro para {instructor_existente.get('nombre', 'esta persona')}. Búscalo en “Buscar y gestionar” para consultar sus datos o reactivarlo.")
                                elif tarifa_inst_nueva is None:
                                    st.error("Ingresa el pago fijo acordado por clase.")
                                else:
                                    try:
                                        supabase.table("instructoras").insert({
                                            "nombre": nombre_inst_nueva.strip(),
                                            "telefono": telefono_inst_nueva.strip() or None,
                                            "pago_por_clase": tarifa_inst_nueva,
                                            "activo": True
                                        }).execute()
                                        st.session_state.aviso_instructora = f"Instructor '{nombre_inst_nueva.strip()}' registrado."
                                        st.session_state.clear_gestion_instructoras += 1
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"No se pudo registrar al instructor: {e}")
                        with col_limpiar_inst_nueva:
                            if st.button("Limpiar campos", key=f"limpiar_inst_nueva_{st.session_state.clear_gestion_instructoras}"):
                                st.session_state.clear_gestion_instructoras += 1
                                st.rerun()

                    with tab_pagos_inst:
                        st.markdown("#### Historial de pagos realizados")
                        st.caption("Cada fila muestra la clase, sede, duración, importe pagado y referencia.")
                        st.info("En Agenda de clases, las sesiones se cierran automáticamente al terminar si tuvieron reservas. Luego, en Buscar y gestionar, podrás registrar el pago correspondiente.")
                        try:
                            pagos_globales = supabase.table("pagos_instructoras").select("*").order("fecha_pago", desc=True).limit(1000).execute().data or []
                            if pagos_globales:
                                sesiones_globales = supabase.table("sesiones_clase").select("id,local_id,fecha_clase,hora_inicio,hora_fin,tipo_servicio").in_("id", list({p["sesion_id"] for p in pagos_globales})).execute().data or []
                                instructora_global = {int(i["id"]): i["nombre"] for i in (supabase.table("instructoras").select("id,nombre").execute().data or [])}
                                usuarios_global = {int(u["id"]): u.get("usuario", "—") for u in (supabase.table("usuarios_admin").select("id,usuario").execute().data or [])}
                                local_global = {int(l["id"]): l["nombre"] for l in lista_locales_admin}
                                sesion_global_por_id = {int(s["id"]): s for s in sesiones_globales}
                                detalle_pagos_global = []
                                for pago in pagos_globales:
                                    sesion_pago_global = sesion_global_por_id.get(int(pago["sesion_id"]), {})
                                    detalle_pagos_global.append({
                                        "Fecha de pago": fecha_visible(pago.get("fecha_pago")),
                                    "Instructor": instructora_global.get(int(pago["instructora_id"]), "—"),
                                        "Fecha de clase": fecha_visible(sesion_pago_global.get("fecha_clase")),
                                        "Horario": f"{str(sesion_pago_global.get('hora_inicio', ''))[:5]}–{str(sesion_pago_global.get('hora_fin', ''))[:5]}",
                                        "Sede": local_global.get(int(sesion_pago_global["local_id"]), "—") if sesion_pago_global.get("local_id") is not None else "—",
                                        "Modalidad": sesion_pago_global.get("tipo_servicio", "—"),
                                        "Duración": f"{int(pago.get('duracion_minutos') or 0)} min",
                                        "Importe pagado": f"S/ {float(pago.get('importe') or 0):.2f}",
                                        "Referencia": pago.get("referencia") or "—",
                                        "Registrado por": usuarios_global.get(int(pago["registrado_por"]), "—") if pago.get("registrado_por") is not None else "—",
                                    })
                                st.dataframe(pd.DataFrame(detalle_pagos_global), hide_index=True, use_container_width=True)
                                st.metric("Total pagado en el listado", f"S/ {sum(float(p.get('importe') or 0) for p in pagos_globales):.2f}")
                            else:
                                st.info("Todavía no hay pagos registrados. Cuando registres el primero, aparecerá en esta lista.")
                        except Exception as e:
                            st.warning(f"No se pudo cargar el historial. Verifica que ejecutaste supabase_gestion_instructoras_migration.sql en Supabase. Detalle: {e}")

            if "agenda" in paneles_admin:
                with tab_agenda_inst:
                    st.subheader(":material/calendar_month: Agenda de clases")
                    sub_agenda1, sub_agenda2 = st.tabs([
                        "1. Programar clases",
                        "2. Consultar por sede",
                    ], key="tabs_agenda_clases", on_change="rerun")

                    with sub_agenda1:
                        st.markdown("#### Programar clases")
                        aviso_agenda = st.session_state.pop("aviso_agenda", None)
                        if aviso_agenda:
                            st.success(aviso_agenda)
                        try:
                            dias_db = supabase.table("dias_operativos").select("nombre_dia", "numero_dia", "habilitado").execute()
                            dias_habilitados = {d['numero_dia']: d['habilitado'] for d in dias_db.data} if dias_db.data else {}
                                            
                            inst_res = supabase.table("instructoras").select("id", "nombre", "pago_por_clase").eq("activo", True).execute()
                            lista_inst = inst_res.data if inst_res.data else []
                            opciones_inst = {f"{ins['nombre']} · S/ {float(ins.get('pago_por_clase') or 0):.2f} por clase": ins for ins in lista_inst}
                                            
                            col_mas1, col_mas2 = st.columns(2)
                            with col_mas1:
                                sede_agenda = st.selectbox("Selecciona Sede:", [""] + list(opciones_locales.keys()), key=f"mas_sede_{st.session_state.clear_agenda}", placeholder="Selecciona una sede...")
                                sede_objeto_agenda = next((l for l in lista_locales if l["nombre"] == sede_agenda), None)
                                fecha_minima_agenda = datetime.now(ZoneInfo("America/Lima")).date()
                                fecha_maxima_agenda = fecha_minima_agenda + timedelta(days=dias_agenda_anticipacion)
                                fecha_inicio = st.date_input("Fecha de Inicio:", value=None, min_value=fecha_minima_agenda, max_value=fecha_maxima_agenda, format="DD-MM-YYYY", key=f"mas_f_ini_{st.session_state.clear_agenda}")
                                fecha_fin = st.date_input("Fecha de Fin:", value=None, min_value=fecha_minima_agenda, max_value=fecha_maxima_agenda, format="DD-MM-YYYY", key=f"mas_f_fin_{st.session_state.clear_agenda}")
                                hora_agenda = st.time_input("Hora de inicio:", value=hora_apertura_estudio, key=f"mas_hora_{st.session_state.clear_agenda}")
                                duracion_agenda = duracion_clase_default
                                st.caption(f"Duración de cada clase: {duracion_agenda} minutos (definida en Configuración).")
                            with col_mas2:
                                inst_agenda = st.selectbox("Asignar instructor:", [""] + list(opciones_inst.keys()), key=f"mas_inst_{st.session_state.clear_agenda}", placeholder="Selecciona un instructor...")
                                tipo_serv_agenda = st.selectbox("Tipo de Sesión:", ["", "Grupal", "Privado"], key=f"mas_tipo_{st.session_state.clear_agenda}", placeholder="Selecciona una modalidad...")
                                if tipo_serv_agenda == "Grupal":
                                    aforo_agenda = int(sede_objeto_agenda.get("max_camillas") or 8) if sede_objeto_agenda else None
                                    st.caption(f"Aforo grupal de esta sede: **{aforo_agenda if aforo_agenda is not None else '—'} camillas** (se toma de Configuración).")
                                elif tipo_serv_agenda == "Privado": aforo_agenda = 1
                                else: aforo_agenda = None
                                            
                            dias_seleccionados = []
                            nombres_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                            cols_dias = st.columns(4)
                            for numero_dia, nombre_dia in enumerate(nombres_dias):
                                with cols_dias[numero_dia % 4]:
                                    habilitado = bool(dias_habilitados.get(numero_dia, False))
                                    if st.checkbox(nombre_dia, value=False, disabled=not habilitado, key=f"dia_{numero_dia}_{st.session_state.clear_agenda}"):
                                        dias_seleccionados.append(numero_dia)
                                            
                            if st.button("Programar clases", type="primary", key=f"guardar_agenda_{st.session_state.clear_agenda}"):
                                if not sede_agenda or not inst_agenda or not tipo_serv_agenda or fecha_inicio is None or fecha_fin is None or hora_agenda is None or (tipo_serv_agenda == "Grupal" and aforo_agenda is None): st.error("Completa sede, fechas, hora, instructor, modalidad y aforo si es grupal.")
                                elif not opciones_locales or not opciones_inst: st.error("Se requieren sedes e instructores para programar clases.")
                                elif fecha_inicio > fecha_fin: st.error("❌ Rango inválido.")
                                elif fecha_fin > fecha_maxima_agenda: st.error(f"El rango no puede superar {dias_agenda_anticipacion} días desde hoy, según Configuración.")
                                elif not hora_apertura_estudio <= hora_agenda < hora_cierre_estudio: st.error(f"La hora de inicio debe estar entre {hora_apertura_estudio.strftime('%H:%M')} y antes de {hora_cierre_estudio.strftime('%H:%M')}.")
                                elif not dias_seleccionados: st.error("❌ Selecciona al menos un día.")
                                else:
                                    feriados_db = supabase.table("feriados").select("fecha").execute()
                                    lista_feriados = [f['fecha'] for f in feriados_db.data] if feriados_db.data else []
                                    instructora = opciones_inst[inst_agenda]
                                    inicio_agenda_dt = datetime.combine(fecha_inicio, hora_agenda)
                                    fin_dt = inicio_agenda_dt + timedelta(minutes=int(duracion_agenda))
                                    if fin_dt.date() != fecha_inicio:
                                        st.error("La sesión debe terminar el mismo día en que empieza.")
                                        st.stop()
                                    if fin_dt.time() > hora_cierre_estudio:
                                        st.error(f"La clase terminaría después del cierre ({hora_cierre_estudio.strftime('%H:%M')}). Ajusta el inicio o la duración.")
                                        st.stop()
                                    creadas = 0
                                    omitidas = 0
                                    fecha_actual = fecha_inicio
                                    while fecha_actual <= fecha_fin:
                                        num_dia = fecha_actual.weekday()
                                        if num_dia in dias_seleccionados and dias_habilitados.get(num_dia, False) and (fecha_actual.isoformat() not in lista_feriados):
                                            nueva_sesion = {
                                                "local_id": opciones_locales[sede_agenda],
                                                "instructora_id": instructora["id"],
                                                "fecha_clase": fecha_actual.isoformat(),
                                                "hora_inicio": hora_agenda.strftime("%H:%M:%S"),
                                                "hora_fin": fin_dt.time().strftime("%H:%M:%S"),
                                                "tipo_servicio": tipo_serv_agenda,
                                                "capacidad": int(aforo_agenda),
                                                "estado": "Programada",
                                                "pago_por_clase_aplicado": float(instructora.get("pago_por_clase") or 0),
                                                "creado_por": st.session_state.get("admin_id"),
                                            }
                                            try:
                                                supabase.table("sesiones_clase").insert(nueva_sesion).execute()
                                                creadas += 1
                                            except Exception as error_sesion:
                                                if "23505" in str(error_sesion) or "duplicate" in str(error_sesion).lower():
                                                    omitidas += 1
                                                else:
                                                    raise error_sesion
                                        fecha_actual += timedelta(days=1)
                                    st.session_state.aviso_agenda = f"Se programaron {creadas} clases. {omitidas} fechas se omitieron porque el horario ya estaba ocupado."
                                    st.session_state.clear_agenda += 1
                                    st.rerun()
                            if st.button("Limpiar campos", key="limpiar_generador_agenda"):
                                st.session_state.clear_agenda += 1
                                st.rerun()
                        except Exception as e: st.error(f"Error: {e}")

                    with sub_agenda2:
                        st.markdown("#### Clases por sede y turno")
                        st.caption(f"El turno mañana termina a las {corte_turno_manana.strftime('%H:%M')}; desde esa hora se considera turno tarde, según Configuración.")
                        st.caption("Si una clase vencida no se cerró automáticamente, puedes volver a ejecutar el proceso aquí. El sistema actualizará las reservas y cerrará únicamente las clases vencidas que tengan alumnos reservados.")
                        if st.button("Reintentar cierre de clases vencidas", key="reintentar_cierre_clases_vencidas"):
                            try:
                                resultado_cierre = supabase.rpc(
                                    "reintentar_cierre_clases",
                                    {"p_admin_id": st.session_state.admin_id},
                                ).execute()
                                total_inasistencias = resultado_cierre.data or 0
                                st.success(f"Reintento completado. Se registraron {total_inasistencias} inasistencias. Las clases vencidas con reservas y asistencia o inasistencia quedaron cerradas automáticamente.")
                            except Exception as error_cierre:
                                st.error(f"No se pudo reintentar el cierre automático. Verifica que ejecutaste supabase_validar_estado_clases.sql en Supabase. Detalle: {error_cierre}")
                        try:
                            col_desde, col_hasta = st.columns(2)
                            with col_desde:
                                desde = st.date_input("Desde", value=datetime.now(ZoneInfo("America/Lima")).date(), format="DD-MM-YYYY", key="agenda_reporte_desde")
                            with col_hasta:
                                hasta = st.date_input("Hasta", value=datetime.now(ZoneInfo("America/Lima")).date() + timedelta(days=6), format="DD-MM-YYYY", key="agenda_reporte_hasta")
                            sesiones_reporte = supabase.table("sesiones_clase").select("*").gte("fecha_clase", desde.isoformat()).lte("fecha_clase", hasta.isoformat()).order("hora_inicio").order("fecha_clase").execute().data or []
                            if desde > hasta:
                                st.warning("El rango de fechas no es válido.")
                            elif sesiones_reporte:
                                locales_nombres = {int(v): k for k, v in opciones_locales.items()}
                                nombres_instructoras = {int(i["id"]): i["nombre"] for i in (supabase.table("instructoras").select("id,nombre").execute().data or [])}
                                for sesion in sesiones_reporte:
                                    sesion["Sede"] = locales_nombres.get(int(sesion["local_id"]), "Sede")
                                    sesion["Instructor"] = nombres_instructoras.get(int(sesion["instructora_id"]), "—")
                                    sesion["Turno"] = "Mañana" if datetime_time.fromisoformat(str(sesion["hora_inicio"])) < corte_turno_manana else "Tarde"
                                for sede in sorted({s["Sede"] for s in sesiones_reporte}):
                                    st.markdown(f"##### {sede}")
                                    tab_manana, tab_tarde = st.tabs(["Turno mañana", "Turno tarde"])
                                    for turno, pestaña_turno in (("Mañana", tab_manana), ("Tarde", tab_tarde)):
                                        with pestaña_turno:
                                            filas = [s for s in sesiones_reporte if s["Sede"] == sede and s["Turno"] == turno]
                                            filas.sort(key=lambda s: (s["fecha_clase"], str(s["hora_inicio"])))
                                            if filas:
                                                st.dataframe(pd.DataFrame([{"Fecha": fecha_visible(s["fecha_clase"]), "Hora": f"{str(s['hora_inicio'])[:5]}–{str(s['hora_fin'])[:5]}", "Clase": s["tipo_servicio"], "Instructor": s["Instructor"], "Aforo": s["capacidad"], "Estado": s["estado"]} for s in filas]), hide_index=True, use_container_width=True)
                                            else:
                                                st.caption("Sin clases para este turno.")
                                st.divider()
                                st.markdown("#### Cancelar una clase")
                                sesion_etiquetas = {f"{fecha_visible(s['fecha_clase'])} · {str(s['hora_inicio'])[:5]} · {s['Sede']} · {s['Instructor']} ({s['estado']})": s for s in sesiones_reporte}
                                etiqueta_sesion = st.selectbox("Selecciona una clase", [""] + list(sesion_etiquetas), key=f"estado_sesion_sel_{st.session_state.clear_estado_sesion}")
                                sesion_estado = sesion_etiquetas.get(etiqueta_sesion)
                                if sesion_estado and sesion_estado.get("estado") in {"Realizada", "Cancelada"}:
                                    st.info(f"Esta clase ya está {str(sesion_estado['estado']).lower()}. Es un estado final y no se puede reabrir desde la aplicación.")
                                elif sesion_estado:
                                    st.caption("Las clases pasan a Realizada automáticamente al terminar y procesarse sus reservas. Solo se pueden cancelar antes de su hora de inicio.")
                                if st.button("Cancelar clase seleccionada", key=f"cancelar_sesion_{st.session_state.clear_estado_sesion}", disabled=sesion_estado is None or sesion_estado.get("estado") != "Programada"):
                                    try:
                                        estado_actual = str(sesion_estado.get("estado") or "")
                                        fecha_sesion = sesion_estado["fecha_clase"]
                                        if isinstance(fecha_sesion, str):
                                            fecha_sesion = datetime.fromisoformat(fecha_sesion[:10]).date()
                                        hora_inicio = sesion_estado["hora_inicio"]
                                        if isinstance(hora_inicio, str):
                                            hora_inicio = datetime_time.fromisoformat(hora_inicio)
                                        inicio_sesion = datetime.combine(fecha_sesion, hora_inicio).replace(tzinfo=ZoneInfo("America/Lima"))
                                        pago_existente = supabase.table("pagos_instructoras").select("id").eq("sesion_id", sesion_estado["id"]).limit(1).execute().data or []
                                        if estado_actual != "Programada":
                                            st.error("Solo se pueden cancelar clases que sigan programadas.")
                                        elif datetime.now(ZoneInfo("America/Lima")) >= inicio_sesion:
                                            st.error("Solo se puede cancelar una clase antes de su hora de inicio. Para una clase vencida, usa el reintento de cierre automático.")
                                        elif pago_existente:
                                            st.error("No se puede cambiar una clase cuyo pago ya fue registrado.")
                                        else:
                                            supabase.table("sesiones_clase").update({"estado": "Cancelada"}).eq("id", sesion_estado["id"]).execute()
                                            st.session_state.aviso_agenda = f"La clase del {fecha_visible(sesion_estado['fecha_clase'])} a las {str(sesion_estado['hora_inicio'])[:5]} quedó cancelada."
                                            st.session_state.clear_estado_sesion += 1
                                            st.rerun()
                                    except Exception as error_estado:
                                        st.error(f"No se pudo actualizar el estado de la clase: {error_estado}")
                            else:
                                st.info("No hay clases programadas para este rango.")
                        except Exception as e:
                            st.warning(f"Para usar el calendario de sesiones, ejecuta la migración de Gestión de Instructoras en Supabase. Detalle: {e}")

                # --- CONSULTA PREDICTIVA DE ALUMNOS Y KÁRDEX ---
            if "alumnos" in paneles_admin:
                with paneles_admin["alumnos"]:
                    st.divider()
                    st.subheader("Buscar y gestionar alumnos")
                    st.caption("Consulta su historial y actualiza sus datos de contacto o plan.")
                    mensaje_gestion_alumno = st.session_state.pop("mensaje_gestion_alumno", None)
                    if mensaje_gestion_alumno:
                        st.success(mensaje_gestion_alumno)

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

                                if st.session_state.get("alumno_en_edicion_id") != data_al["id"]:
                                    if st.button("Editar datos del alumno", key=f"abrir_edicion_alumno_{data_al['id']}"):
                                        st.session_state.alumno_en_edicion_id = data_al["id"]
                                        st.rerun()
                                else:
                                    with st.form(f"form_editar_alumno_{data_al['id']}_{st.session_state.clear_editar_alumno}"):
                                        nombre_alumno_editado = st.text_input(
                                            "Nombre",
                                            value=data_al["nombre"],
                                            key=f"editar_alumno_nombre_{data_al['id']}_{st.session_state.clear_editar_alumno}"
                                        )
                                        apellido_alumno_editado = st.text_input(
                                            "Apellido",
                                            value=data_al["apellido"],
                                            key=f"editar_alumno_apellido_{data_al['id']}_{st.session_state.clear_editar_alumno}"
                                        )
                                        telefono_alumno_editado = st.text_input(
                                            "Teléfono",
                                            value=data_al["telefono"],
                                            key=f"editar_alumno_telefono_{data_al['id']}_{st.session_state.clear_editar_alumno}"
                                        )
                                        col_guardar_alumno, col_limpiar_alumno, col_cancelar_alumno = st.columns(3)
                                        with col_guardar_alumno:
                                            guardar_datos_alumno = st.form_submit_button("Guardar cambios", type="primary")
                                        with col_limpiar_alumno:
                                            limpiar_datos_alumno = st.form_submit_button("Restaurar datos")
                                        with col_cancelar_alumno:
                                            cancelar_edicion_alumno = st.form_submit_button("Cancelar")

                                    if limpiar_datos_alumno:
                                        st.session_state.clear_editar_alumno += 1
                                        st.rerun()
                                    elif cancelar_edicion_alumno:
                                        st.session_state.alumno_en_edicion_id = None
                                        st.rerun()
                                    elif guardar_datos_alumno:
                                        if not nombre_alumno_editado.strip() or not apellido_alumno_editado.strip() or not telefono_alumno_editado.strip():
                                            st.error("Nombre, apellido y teléfono son obligatorios.")
                                        else:
                                            try:
                                                supabase.table("alumnos").update({
                                                    "nombre": nombre_alumno_editado.strip(),
                                                    "apellido": apellido_alumno_editado.strip(),
                                                    "telefono": telefono_alumno_editado.strip()
                                                }).eq("id", data_al["id"]).execute()
                                                st.session_state.mensaje_gestion_alumno = "Datos del alumno actualizados correctamente."
                                                st.session_state.alumno_en_edicion_id = None
                                                st.session_state.clear_editar_alumno += 1
                                                st.rerun()
                                            except Exception as e:
                                                if "23505" in str(e):
                                                    st.error("Ese teléfono ya está registrado para otro alumno.")
                                                else:
                                                    st.error(f"No se pudieron actualizar los datos: {e}")

                                # Permite cambiar la modalidad o hacer upgrade del paquete vigente.
                                st.markdown("#### :material/swap_horiz: Paquete y modalidad de acceso")
                                st.caption("El paquete solo puede cambiarse por uno de mayor nivel. Al subir de plan se conserva el consumo y se suman al saldo las clases de diferencia.")
                                try:
                                    paquetes_activos_res = (
                                        supabase.table("paquetes")
                                        .select("id,tipo_paquete,modalidad_plan,local_id_fijo,clases_totales,clases_restantes,fecha_vencimiento,estado,pagado,fecha_pago,pago_confirmado_por,pago_revertido_en,pago_revertido_por")
                                        .eq("alumno_id", data_al["id"])
                                        .eq("estado", "Activo")
                                        .gte("fecha_vencimiento", datetime.now(ZoneInfo("America/Lima")).date().isoformat())
                                        .order("fecha_compra", desc=True)
                                        .execute()
                                    )
                                    paquetes_activos = paquetes_activos_res.data or []
                                    if not paquetes_activos:
                                        st.info("El alumno no tiene un paquete activo que se pueda modificar.")
                                    else:
                                        paquetes_etiquetas = {
                                            f"{p['tipo_paquete']} · {p['modalidad_plan']} · {p['clases_restantes']} clases · vence {fecha_visible(p['fecha_vencimiento'])}": p
                                            for p in paquetes_activos
                                        }
                                        paquete_elegido_label = st.selectbox(
                                            "Paquete activo a modificar:",
                                            [""] + list(paquetes_etiquetas.keys()),
                                            key=f"seleccionar_paquete_alumno_{data_al['id']}_{st.session_state.clear_paquete_alumno}",
                                            placeholder="Selecciona un paquete..."
                                        )
                                        if paquete_elegido_label:
                                            paquete_actual = paquetes_etiquetas[paquete_elegido_label]
                                            planes_superiores = {
                                                p["nombre_paquete"]: int(p["clases_totales"])
                                                for p in lista_p_db
                                                if int(p["clases_totales"]) > int(paquete_actual.get("clases_totales") or 0)
                                            }
                                            opciones_upgrade = ["Sin cambio"] + list(planes_superiores.keys())
                                            with st.form(f"form_actualizar_paquete_alumno_{paquete_actual['id']}_{st.session_state.clear_paquete_alumno}"):
                                                paquete_nuevo_alumno = st.selectbox(
                                                    "Cambiar a un paquete superior (opcional):",
                                                    [""] + opciones_upgrade,
                                                    key=f"upgrade_paquete_alumno_{paquete_actual['id']}_{st.session_state.clear_paquete_alumno}",
                                                    placeholder="Sin cambio de paquete..."
                                                )
                                                confirmar_pago_upgrade = False
                                                if paquete_nuevo_alumno and paquete_nuevo_alumno != "Sin cambio":
                                                    diferencia_upgrade = planes_superiores[paquete_nuevo_alumno] - int(paquete_actual.get("clases_totales") or 0)
                                                    st.info(
                                                        f"**Resumen del cambio de plan:** {paquete_actual['tipo_paquete']} → {paquete_nuevo_alumno} · "
                                                        f"Se añadirán {diferencia_upgrade} clases al saldo actual · "
                                                        f"Total a pagar: S/ {costos_planes.get(paquete_nuevo_alumno, 0):.2f}"
                                                    )
                                                    confirmar_pago_upgrade = st.checkbox(
                                                        "Confirmo que el alumno ya pagó el cambio de plan.",
                                                        key=f"pago_confirmado_upgrade_{paquete_actual['id']}_{st.session_state.clear_paquete_alumno}"
                                                    )
                                                modalidad_nueva_alumno = st.selectbox(
                                                    "Modalidad de acceso:",
                                                    ["", "Fixed", "Flex"],
                                                    key=f"modalidad_paquete_alumno_{paquete_actual['id']}_{st.session_state.clear_paquete_alumno}",
                                                    placeholder="Selecciona una modalidad..."
                                                )
                                                sede_nueva_alumno = ""
                                                if modalidad_nueva_alumno == "Fixed":
                                                    sede_nueva_alumno = st.selectbox(
                                                        "Sede base:",
                                                        [""] + list(opciones_locales.keys()),
                                                        key=f"sede_paquete_alumno_{paquete_actual['id']}_{st.session_state.clear_paquete_alumno}",
                                                        placeholder="Selecciona una sede..."
                                                    )
                                                guardar_paquete_alumno = st.form_submit_button("Guardar paquete y modalidad", type="primary")
                                                limpiar_paquete_alumno = st.form_submit_button("Limpiar campos")
                                            if limpiar_paquete_alumno:
                                                st.session_state.clear_paquete_alumno += 1
                                                st.rerun()
                                            elif guardar_paquete_alumno:
                                                if not modalidad_nueva_alumno:
                                                    st.error("Selecciona la modalidad de acceso.")
                                                elif modalidad_nueva_alumno == "Fixed" and not sede_nueva_alumno:
                                                    st.error("Selecciona la sede base para la modalidad Fixed.")
                                                elif paquete_nuevo_alumno and paquete_nuevo_alumno != "Sin cambio" and not confirmar_pago_upgrade:
                                                    st.error("Confirma que el cambio de plan ya fue pagado para proceder.")
                                                else:
                                                    try:
                                                        paquete_anterior_snapshot = {
                                                            campo: paquete_actual.get(campo)
                                                            for campo in (
                                                                "tipo_paquete", "modalidad_plan", "local_id_fijo", "clases_totales",
                                                                "clases_restantes", "fecha_vencimiento", "estado", "pagado", "fecha_pago",
                                                                "pago_confirmado_por", "pago_revertido_en", "pago_revertido_por"
                                                            )
                                                        }
                                                        actualizacion_paquete = {
                                                            "modalidad_plan": modalidad_nueva_alumno,
                                                            "local_id_fijo": opciones_locales[sede_nueva_alumno] if modalidad_nueva_alumno == "Fixed" else None,
                                                        }
                                                        tipo_evento_paquete = "cambio_modalidad"
                                                        fecha_pago_upgrade = None
                                                        if paquete_nuevo_alumno and paquete_nuevo_alumno != "Sin cambio":
                                                            clases_nuevo_plan = planes_superiores[paquete_nuevo_alumno]
                                                            diferencia_clases = clases_nuevo_plan - int(paquete_actual.get("clases_totales") or 0)
                                                            fecha_pago_upgrade = datetime.now(ZoneInfo("America/Lima")).isoformat()
                                                            actualizacion_paquete.update({
                                                                "tipo_paquete": paquete_nuevo_alumno,
                                                                "clases_totales": clases_nuevo_plan,
                                                                "clases_restantes": int(paquete_actual.get("clases_restantes") or 0) + diferencia_clases,
                                                                "pagado": True,
                                                                "fecha_pago": fecha_pago_upgrade,
                                                                "pago_confirmado_por": st.session_state.admin_id,
                                                                "pago_revertido_en": None,
                                                                "pago_revertido_por": None,
                                                            })
                                                            tipo_evento_paquete = "cambio_plan"
                                                        try:
                                                            supabase.table("paquetes").update(actualizacion_paquete).eq("id", paquete_actual["id"]).execute()
                                                            detalles_evento = {
                                                                "paquete_anterior": paquete_anterior_snapshot,
                                                                "tipo_paquete_nuevo": paquete_nuevo_alumno if tipo_evento_paquete == "cambio_plan" else paquete_actual["tipo_paquete"],
                                                                "modalidad_nueva": modalidad_nueva_alumno,
                                                                "local_id_fijo_nuevo": actualizacion_paquete["local_id_fijo"],
                                                                "costo": costos_planes.get(paquete_nuevo_alumno, 0) if tipo_evento_paquete == "cambio_plan" else 0,
                                                                "fecha_pago": fecha_pago_upgrade
                                                            }
                                                            supabase.table("eventos_paquetes").insert({
                                                                "paquete_id": paquete_actual["id"],
                                                                "alumno_id": data_al["id"],
                                                                "tipo_evento": tipo_evento_paquete,
                                                                "realizado_por": st.session_state.admin_id,
                                                                "detalles": detalles_evento
                                                            }).execute()
                                                        except Exception:
                                                            supabase.table("paquetes").update(paquete_anterior_snapshot).eq("id", paquete_actual["id"]).execute()
                                                            raise
                                                        st.session_state.mensaje_gestion_alumno = "Pago confirmado y paquete actualizado." if tipo_evento_paquete == "cambio_plan" else "Modalidad de acceso actualizada."
                                                        st.session_state.clear_paquete_alumno += 1
                                                        st.rerun()
                                                    except Exception as e:
                                                        st.error(f"No se pudo actualizar el paquete: {e}")
                                except Exception as e:
                                    st.error(f"No se pudieron cargar los paquetes activos: {e}")

                                paq_res = (
                                    supabase.table("paquetes")
                                    .select("id,tipo_paquete,modalidad_plan,clases_totales,clases_restantes,fecha_vencimiento,estado,pagado,fecha_pago,pago_revertido_en")
                                    .eq("alumno_id", data_al["id"])
                                    .order("fecha_compra", desc=True)
                                    .execute()
                                )
                                if paq_res.data:
                                    st.markdown("#### :material/loyalty: Historial de paquetes y membresías")
                                    df_paq = pd.DataFrame(paq_res.data)
                                    df_paq["fecha_vencimiento"] = df_paq["fecha_vencimiento"].map(fecha_visible)
                                    df_paq["fecha_pago"] = df_paq["fecha_pago"].map(fecha_visible)
                                    df_paq["Clases Consumidas"] = df_paq["clases_totales"] - df_paq["clases_restantes"]
                                    df_paq["Pago confirmado"] = df_paq["pagado"].map({True: "Sí", False: "No"}).fillna("Sin registro histórico")
                                    df_reporte_paq = df_paq[[
                                        "tipo_paquete", "modalidad_plan", "clases_totales", "Clases Consumidas",
                                        "clases_restantes", "fecha_vencimiento", "estado", "Pago confirmado", "fecha_pago"
                                    ]].rename(columns={
                                        "tipo_paquete": "Paquete Contratado",
                                        "modalidad_plan": "Tipo Plan",
                                        "clases_totales": "Clases Totales",
                                        "clases_restantes": "Clases Pendientes (Saldo)",
                                        "fecha_vencimiento": "Caduca El",
                                        "estado": "Estado Plan",
                                        "fecha_pago": "Fecha de pago"
                                    })
                                    st.dataframe(df_reporte_paq, use_container_width=True, hide_index=True)
                                    for paquete_historial in paq_res.data:
                                        if paquete_historial.get("pagado") and not paquete_historial.get("pago_revertido_en"):
                                            if st.button(
                                                f"Revertir pago confirmado · {paquete_historial['tipo_paquete']}",
                                                key=f"revertir_pago_{paquete_historial['id']}_{st.session_state.clear_paquete_alumno}"
                                            ):
                                                try:
                                                    supabase.rpc("revertir_pago_paquete", {
                                                        "p_paquete_id": paquete_historial["id"],
                                                        "p_usuario_id": st.session_state.admin_id
                                                    }).execute()
                                                    st.session_state.mensaje_gestion_alumno = "Se revirtió la confirmación de pago. La operación quedó registrada en auditoría."
                                                    st.session_state.clear_paquete_alumno += 1
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"No se pudo revertir el pago. Verifica que supabase_pagos_migration.sql esté aplicado y que el paquete no tenga reservas: {e}")
                                else:
                                    st.info("Este alumno aún no tiene paquetes registrados.")

                                try:
                                    eventos_alumno_res = (
                                        supabase.table("eventos_paquetes")
                                        .select("id,tipo_evento,fecha_evento,realizado_por,detalles")
                                        .eq("alumno_id", data_al["id"])
                                        .order("fecha_evento", desc=True)
                                        .execute()
                                    )
                                    if eventos_alumno_res.data:
                                        st.markdown("#### :material/history: Auditoría de pagos y cambios")
                                        nombres_eventos = {
                                            "inscripcion": "Inscripción registrada",
                                            "renovacion": "Renovación de paquete",
                                            "cambio_plan": "Cambio a paquete superior",
                                            "cambio_modalidad": "Cambio de modalidad",
                                            "reversion_pago": "Reversión de pago"
                                        }
                                        eventos_por_id = {str(ev["id"]): ev for ev in eventos_alumno_res.data}
                                        try:
                                            admins_eventos = supabase.table("usuarios_admin").select("id,usuario").execute().data or []
                                            nombres_admin_eventos = {str(admin["id"]): admin["usuario"] for admin in admins_eventos}
                                        except Exception:
                                            nombres_admin_eventos = {}
                                        locales_por_id = {str(local["id"]): local["nombre"] for local in lista_locales_admin}

                                        filas_auditoria = []
                                        for evento in eventos_alumno_res.data:
                                            detalle = evento.get("detalles") or {}
                                            tipo_evento = evento.get("tipo_evento", "")
                                            movimiento = nombres_eventos.get(tipo_evento, "Actualización")
                                            importe = "—"
                                            if tipo_evento == "inscripcion":
                                                modalidad_detalle = detalle.get("modalidad_plan", "")
                                                sede_detalle = locales_por_id.get(str(detalle.get("local_id_fijo")), "")
                                                texto_detalle = (
                                                    f"Inscripción de {detalle.get('alumno', 'alumno')}: paquete "
                                                    f"{detalle.get('tipo_paquete', '—')} con {detalle.get('clases_totales', '—')} clases, "
                                                    f"acceso {modalidad_detalle}"
                                                )
                                                if sede_detalle:
                                                    texto_detalle += f" en {sede_detalle}"
                                                importe = f"S/ {float(detalle.get('costo') or 0):.2f}"
                                            elif tipo_evento == "renovacion":
                                                texto_detalle = (
                                                    f"Paquete {detalle.get('tipo_paquete', '—')}: "
                                                    f"{detalle.get('clases_plan', '—')} clases nuevas + "
                                                    f"{detalle.get('clases_anteriores_sumadas', 0)} clases anteriores "
                                                    f"(saldo total: {detalle.get('clases_totales', '—')}); "
                                                    f"acceso {detalle.get('modalidad_plan', '—')}"
                                                )
                                                importe = f"S/ {float(detalle.get('costo') or 0):.2f}"
                                            elif tipo_evento == "cambio_plan":
                                                anterior = detalle.get("paquete_anterior") or {}
                                                texto_detalle = (
                                                    f"De {anterior.get('tipo_paquete', 'paquete anterior')} a "
                                                    f"{detalle.get('tipo_paquete_nuevo', 'paquete superior')}; "
                                                    f"modalidad {detalle.get('modalidad_nueva', '—')}"
                                                )
                                                importe = f"S/ {float(detalle.get('costo') or 0):.2f}"
                                            elif tipo_evento == "cambio_modalidad":
                                                local_detalle = locales_por_id.get(str(detalle.get("local_id_fijo_nuevo")), "")
                                                texto_detalle = f"Modalidad actualizada a {detalle.get('modalidad_nueva', '—')}"
                                                if local_detalle:
                                                    texto_detalle += f" en {local_detalle}"
                                            elif tipo_evento == "reversion_pago":
                                                evento_original = eventos_por_id.get(str(detalle.get("evento_original_id")), {})
                                                tipo_original = (evento_original or {}).get("tipo_evento", detalle.get("evento_original", ""))
                                                movimiento = f"Pago revertido · {nombres_eventos.get(tipo_original, 'operación anterior')}"
                                                detalle_original = (evento_original or {}).get("detalles") or {}
                                                paquete_original = detalle_original.get("tipo_paquete_nuevo") or detalle_original.get("tipo_paquete")
                                                texto_detalle = "Se restauró el estado anterior del paquete y se registró la reversión."
                                                if paquete_original:
                                                    texto_detalle = f"Se revirtió el pago asociado al paquete {paquete_original} y se restauró el estado anterior."
                                                if detalle_original.get("costo") is not None:
                                                    importe = f"S/ {float(detalle_original.get('costo') or 0):.2f} (revertido)"
                                            else:
                                                texto_detalle = "Se actualizaron los datos del paquete."

                                            fecha_evento = str(evento.get("fecha_evento") or "")
                                            try:
                                                fecha_evento = datetime.fromisoformat(fecha_evento.replace("Z", "+00:00")).astimezone(ZoneInfo("America/Lima")).strftime("%d-%m-%Y %H:%M")
                                            except (TypeError, ValueError):
                                                pass
                                            admin_id_evento = evento.get("realizado_por")
                                            responsable = nombres_admin_eventos.get(str(admin_id_evento), "Administrador")
                                            filas_auditoria.append({
                                                "Fecha y hora": fecha_evento,
                                                "Movimiento": movimiento,
                                                "Detalle": texto_detalle,
                                                "Importe": importe,
                                                "Responsable": responsable
                                            })
                                        df_eventos = pd.DataFrame(filas_auditoria)
                                        st.dataframe(df_eventos, use_container_width=True, hide_index=True)
                                except Exception:
                                    st.caption("La auditoría estará disponible después de ejecutar supabase_pagos_migration.sql en Supabase.")

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
                                    df_res["Fecha de Clase"] = df_res["Fecha de Clase"].map(fecha_visible)
                                    st.dataframe(df_res, use_container_width=True, hide_index=True)
                                else:
                                    st.info("💡 El alumno aún no tiene historial de clases en la agenda.")
                        except Exception:
                            st.error("No se pudo cargar la ficha del alumno. Revisa la conexión y los permisos.")

            with paneles_admin["mi_cuenta"]:
                st.subheader(":material/key: Cambiar mi contraseña")
                st.caption(f"Sesión iniciada como **{st.session_state.admin_usuario}**")
                aviso_clave_cuenta = st.session_state.pop("aviso_clave_cuenta", None)
                if aviso_clave_cuenta:
                    st.success(aviso_clave_cuenta)
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
                                st.session_state.aviso_clave_cuenta = "Contraseña actualizada correctamente."
                                st.session_state.clear_cuenta += 1
                                st.rerun()
                        except Exception:
                            st.error("No se pudo actualizar la contraseña. Revisa la conexión y los permisos de Supabase.")

            if st.session_state.admin_es_superadmin and "usuarios" in paneles_admin:
                with paneles_admin["usuarios"]:
                    st.subheader(":material/manage_accounts: Crear Usuario y permisos de acceso")
                    st.caption("Cada usuario solo verá las secciones asignadas. Todos pueden cambiar su contraseña desde Mi cuenta.")
                    tab_crear_usuario, tab_clave_usuario, tab_permisos_usuario, tab_eliminar_usuario = st.tabs(["1. Crear usuario", "2. Cambiar contraseña", "3. Asignar permisos", "4. Eliminar usuario"], key="tabs_usuarios_admin", on_change="rerun")

                    with tab_crear_usuario:
                        with st.form(f"form_crear_usuario_admin_{st.session_state.clear_usuario}"):
                            nuevo_usuario_admin = st.text_input("Nombre de usuario", key=f"nuevo_usuario_admin_{st.session_state.clear_usuario}")
                            nueva_clave_admin = st.text_input("Contraseña inicial (mínimo 12 caracteres)", type="password", key=f"nueva_clave_admin_{st.session_state.clear_usuario}")
                            confirmar_clave_admin = st.text_input("Confirmar contraseña", type="password", key=f"confirmar_clave_admin_{st.session_state.clear_usuario}")
                            permisos_nuevos = st.multiselect(
                                "Secciones que podrá administrar",
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
                                    st.session_state.mensaje_resultado_app = f"Usuario {nuevo_usuario_admin.strip()} creado correctamente."
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
                        st.markdown("#### Crear acceso para un instructor")
                        st.caption("Este acceso es solo para consultar la agenda y el historial de pagos de la persona seleccionada.")
                        try:
                            instructores_sin_cuenta = supabase.table("instructoras").select("id,nombre,activo").eq("activo", True).order("nombre").execute().data or []
                            cuentas_existentes_instructor = supabase.table("usuarios_instructores").select("instructora_id,usuario").execute().data or []
                            ids_con_cuenta = {int(c["instructora_id"]) for c in cuentas_existentes_instructor}
                            opciones_instructor = {f"{i['nombre']}" : i["id"] for i in instructores_sin_cuenta if int(i["id"]) not in ids_con_cuenta}
                            if opciones_instructor:
                                with st.form(f"form_crear_cuenta_instructor_{st.session_state.clear_usuario}"):
                                    instructor_cuenta_sel = st.selectbox("Instructor", [""] + list(opciones_instructor), key=f"cuenta_instructor_sel_{st.session_state.clear_usuario}", placeholder="Selecciona un instructor...")
                                    usuario_nuevo_instructor = st.text_input("Nombre de usuario", key=f"usuario_nuevo_instructor_{st.session_state.clear_usuario}")
                                    clave_nueva_instructor = st.text_input("Contraseña inicial (mínimo 12 caracteres)", type="password", key=f"clave_nueva_instructor_{st.session_state.clear_usuario}")
                                    confirmar_nueva_instructor = st.text_input("Confirmar contraseña", type="password", key=f"confirmar_nueva_instructor_{st.session_state.clear_usuario}")
                                    crear_cuenta_instructor = st.form_submit_button("Crear acceso del instructor", type="primary")
                                if crear_cuenta_instructor:
                                    if not instructor_cuenta_sel:
                                        st.error("Selecciona a qué instructor pertenece esta cuenta.")
                                    elif not usuario_nuevo_instructor.strip():
                                        st.error("Escribe un nombre de usuario.")
                                    elif len(clave_nueva_instructor) < 12:
                                        st.error("La contraseña debe tener al menos 12 caracteres.")
                                    elif clave_nueva_instructor != confirmar_nueva_instructor:
                                        st.error("Las contraseñas no coinciden.")
                                    else:
                                        usuario_candidato = usuario_nuevo_instructor.strip()
                                        try:
                                            en_admin = supabase.table("usuarios_admin").select("id").ilike("usuario", usuario_candidato).limit(1).execute().data
                                            en_instructores = supabase.table("usuarios_instructores").select("id").ilike("usuario", usuario_candidato).limit(1).execute().data
                                            if en_admin or en_instructores:
                                                st.error("Ese nombre de usuario ya está en uso.")
                                            else:
                                                supabase.table("usuarios_instructores").insert({
                                                    "usuario": usuario_candidato,
                                                    "contrasena_encriptada": encriptar_contrasena(clave_nueva_instructor),
                                                    "instructora_id": opciones_instructor[instructor_cuenta_sel],
                                                    "activo": True,
                                                    "creado_por": st.session_state.admin_id
                                                }).execute()
                                                st.session_state.mensaje_resultado_app = f"Acceso creado para {instructor_cuenta_sel}."
                                                st.session_state.clear_usuario += 1
                                                st.rerun()
                                        except Exception as error_cuenta_instructor:
                                            if "23505" in str(error_cuenta_instructor):
                                                st.error("Ya existe un usuario con ese nombre o el instructor ya tiene una cuenta.")
                                            else:
                                                st.error(f"No se pudo crear la cuenta. Ejecuta la migración de usuarios instructores. Detalle: {error_cuenta_instructor}")
                            else:
                                st.info("No hay instructores activos sin una cuenta asignada.")
                        except Exception as error_lista_cuentas:
                            st.error(f"No se pudieron cargar las cuentas de instructores. Ejecuta la migración de usuarios instructores. Detalle: {error_lista_cuentas}")
                    with tab_clave_usuario:
                        st.divider()
                        st.markdown("#### Restablecer contraseña de un usuario")
                        aviso_clave_restablecida = st.session_state.pop("aviso_clave_restablecida", None)
                        if aviso_clave_restablecida:
                            st.success(aviso_clave_restablecida)
                        try:
                            usuarios_claves_res = supabase.table("usuarios_admin").select("id,usuario").order("usuario").execute()
                            usuarios_claves = usuarios_claves_res.data or []
                            if usuarios_claves:
                                usuarios_clave_labels = {f"{u['usuario']}" : u["id"] for u in usuarios_claves}
                                usuario_clave_sel = st.selectbox(
                                    "Usuario al que cambiar la contraseña",
                                    [""] + list(usuarios_clave_labels.keys()),
                                    key=f"usuario_restablecer_clave_{st.session_state.clear_reset_clave}",
                                    placeholder="Selecciona un usuario..."
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
                                    cambiar_clave_usuario = st.form_submit_button("Cambiar contraseña", type="primary", disabled=not usuario_clave_sel)
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
                                        st.session_state.aviso_clave_restablecida = f"Contraseña de {usuario_clave_sel} cambiada correctamente."
                                        st.session_state.clear_reset_clave += 1
                                        st.rerun()
                            else:
                                st.info("No hay usuarios administradores registrados.")
                        except Exception:
                            st.error("No se pudo restablecer la contraseña. Revisa la conexión y los permisos de Supabase.")
    
                        st.divider()
                        st.markdown("#### Cambiar contraseña de un instructor")
                        try:
                            cuentas_inst_reset = supabase.table("usuarios_instructores").select("id,usuario,instructora_id,instructoras(nombre)").order("usuario").execute().data or []
                            mapa_inst_reset = {f"{cuenta.get('instructoras', {}).get('nombre', 'Instructor')} — {cuenta['usuario']}": cuenta for cuenta in cuentas_inst_reset}
                            if mapa_inst_reset:
                                etiqueta_inst_reset = st.selectbox("Cuenta de instructor", [""] + list(mapa_inst_reset), key=f"seleccion_reset_cuenta_inst_{st.session_state.clear_reset_clave}", placeholder="Selecciona una cuenta...")
                                with st.form(f"form_reset_clave_inst_{st.session_state.clear_reset_clave}"):
                                    nueva_clave_inst_admin = st.text_input("Nueva contraseña (mínimo 12 caracteres)", type="password")
                                    confirmar_clave_inst_admin = st.text_input("Confirmar contraseña", type="password")
                                    guardar_reset_inst = st.form_submit_button("Cambiar contraseña del instructor", type="primary", disabled=not etiqueta_inst_reset)
                                if guardar_reset_inst:
                                    if len(nueva_clave_inst_admin) < 12:
                                        st.error("La contraseña debe tener al menos 12 caracteres.")
                                    elif nueva_clave_inst_admin != confirmar_clave_inst_admin:
                                        st.error("Las contraseñas no coinciden.")
                                    else:
                                        cuenta_reset = mapa_inst_reset[etiqueta_inst_reset]
                                        supabase.table("usuarios_instructores").update({"contrasena_encriptada": encriptar_contrasena(nueva_clave_inst_admin)}).eq("id", cuenta_reset["id"]).execute()
                                        st.session_state.mensaje_resultado_app = f"Contraseña de {etiqueta_inst_reset} actualizada correctamente."
                                        st.session_state.clear_reset_clave += 1
                                        st.rerun()
                            else:
                                st.info("Aún no hay cuentas de instructores.")
                        except Exception as error_reset_inst:
                            st.error(f"No se pudieron administrar las contraseñas de instructores. Detalle: {error_reset_inst}")
                    with tab_permisos_usuario:
                        st.divider()
                        st.markdown("#### Editar permisos de un usuario existente")
                        aviso_permisos = st.session_state.pop("aviso_permisos", None)
                        if aviso_permisos:
                            st.success(aviso_permisos)
                        try:
                            usuarios_res = supabase.table("usuarios_admin").select(
                                "id,usuario,es_superadmin,permisos"
                            ).order("usuario").execute()
                            usuarios_db = usuarios_res.data or []
                            usuarios_normales = [u for u in usuarios_db if not u.get("es_superadmin", False)]
                            if usuarios_normales:
                                etiqueta_a_id = {u["usuario"]: u["id"] for u in usuarios_normales}
                                usuario_editar = st.selectbox(
                                    "Usuario",
                                    [""] + list(etiqueta_a_id.keys()),
                                    key=f"usuario_permisos_editar_{st.session_state.clear_permisos}",
                                    placeholder="Selecciona un usuario..."
                                )
                                if usuario_editar:
                                    usuario_obj = next(u for u in usuarios_normales if u["id"] == etiqueta_a_id[usuario_editar])
                                    permisos_actuales = usuario_obj.get("permisos") or []
                                    permisos_editados = st.multiselect(
                                "Secciones a las que puede acceder",
                                        options=list(VENTANAS_ADMIN.keys()),
                                default=normalizar_permisos_admin(permisos_actuales),
                                        format_func=lambda permiso: VENTANAS_ADMIN[permiso],
                                        key=f"permisos_editar_{usuario_obj['id']}_{st.session_state.clear_permisos}"
                                    )
                                    if st.button("Guardar permisos", key=f"guardar_permisos_usuario_{st.session_state.clear_permisos}", type="primary"):
                                        supabase.table("usuarios_admin").update({
                                            "permisos": permisos_editados
                                        }).eq("id", usuario_obj["id"]).execute()
                                        st.session_state.aviso_permisos = f"Permisos de {usuario_editar} actualizados."
                                        st.session_state.clear_permisos += 1
                                        st.rerun()
                                else:
                                    st.info("Selecciona un usuario para revisar y editar sus permisos.")
                            else:
                                st.info("Aún no hay otros usuarios administradores para editar.")
                        except Exception:
                            st.error("No se pudieron cargar los usuarios. Ejecuta la migración SQL y revisa los permisos de Supabase.")
    
                    with tab_eliminar_usuario:
                        st.divider()
                        st.markdown("#### Eliminar usuario")
                        aviso_usuario_eliminado = st.session_state.pop("aviso_usuario_eliminado", None)
                        if aviso_usuario_eliminado:
                            st.success(aviso_usuario_eliminado)
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
                                    [""] + list(etiquetas_borrar.keys()),
                                    key=f"usuario_admin_seleccionar_eliminar_{st.session_state.clear_eliminar_usuario}",
                                    placeholder="Selecciona un usuario..."
                                )
                                usuario_borrar = etiquetas_borrar.get(usuario_borrar_etiqueta)
                                confirmar_borrado = st.checkbox(
                                    f"Confirmo que deseo eliminar permanentemente a {usuario_borrar['usuario']}" if usuario_borrar else "Confirmo la eliminación de la cuenta seleccionada",
                                    key=f"confirmar_eliminar_usuario_{st.session_state.clear_eliminar_usuario}",
                                    disabled=not usuario_borrar
                                )
                                if st.button(
                                    "Eliminar usuario",
                                    key=f"eliminar_usuario_admin_{st.session_state.clear_eliminar_usuario}",
                                    type="secondary",
                                    disabled=not usuario_borrar or not confirmar_borrado
                                ):
                                    superusuarios = [u for u in usuarios_borrar if u.get("es_superadmin")]
                                    if usuario_borrar.get("es_superadmin") and len(superusuarios) <= 1:
                                        st.error("No se puede eliminar el último superusuario.")
                                    else:
                                        supabase.table("usuarios_admin").delete().eq("id", usuario_borrar["id"]).execute()
                                        st.session_state.aviso_usuario_eliminado = f"La cuenta {usuario_borrar['usuario']} fue eliminada."
                                        st.session_state.clear_eliminar_usuario += 1
                                        st.rerun()
                            else:
                                st.info("No hay otras cuentas que puedas eliminar.")
                        except Exception:
                            st.error("No se pudo cargar o eliminar la cuenta. Verifica la migración SQL y los permisos de Supabase.")
    
            if "configuracion" in paneles_admin:
                with paneles_admin["configuracion"]:
                    tab_identidad_configuracion, calendario_dias, calendario_feriados, calendario_capacidad, calendario_horarios = st.tabs(["1. Identidad y apariencia", "2. Días laborales", "3. Feriados y festivos", "4. Aforo por sede", "5. Horarios y reservas"], key="tabs_configuracion", on_change="rerun")
                    with tab_identidad_configuracion:
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
    
                    with calendario_dias:
                        st.caption("Indica los días de la semana en que el estudio abre.")
                        try:
                            dias_consulta = supabase.table("dias_operativos").select("*").order("numero_dia").execute()
                            if dias_consulta.data:
                                df_dias = pd.DataFrame(dias_consulta.data)
                                df_dias_amigable = df_dias[["nombre_dia", "habilitado"]].rename(columns={"nombre_dia": "Día de la semana", "habilitado": "Estudio abierto"})
                                editor_dias_key = f"editor_dias_operativos_{st.session_state.clear_dias_operativos}"
                                st.data_editor(df_dias_amigable, hide_index=True, disabled=["Día de la semana"], use_container_width=True, key=editor_dias_key)
                                cambios_dias = st.session_state.get(editor_dias_key, {}).get("edited_rows", {})
                                for idx_fila, cambio_dia in cambios_dias.items():
                                    if "Estudio abierto" in cambio_dia:
                                        supabase.table("dias_operativos").update({"habilitado": cambio_dia["Estudio abierto"]}).eq("id", int(df_dias.iloc[idx_fila]["id"])).execute()
                                        st.session_state.mensaje_resultado_app = f"La disponibilidad de {df_dias.iloc[idx_fila]['nombre_dia']} se actualizó."
                                        st.session_state.clear_dias_operativos += 1
                                        st.rerun()
                            else:
                                st.info("No hay días operativos configurados.")
                        except Exception as e:
                            st.error(f"No se pudo cargar la configuración de días: {e}")
                    with calendario_feriados:
                        st.caption("Registra fechas sin actividad o elimina feriados ingresados por error.")
                        aviso_feriado = st.session_state.pop("aviso_feriado", None)
                        if aviso_feriado:
                            st.success(aviso_feriado)
                        col_f1, col_f2 = st.columns(2)
                        with col_f1:
                            fecha_f = st.date_input("Fecha del feriado", value=None, format="DD-MM-YYYY", key=f"input_fecha_feriado_{st.session_state.clear_feriado}")
                            desc_f = st.text_input("Descripción", key=f"input_desc_feriado_{st.session_state.clear_feriado}")
                            if st.button("Registrar feriado", key=f"guardar_feriado_{st.session_state.clear_feriado}"):
                                if fecha_f is not None and desc_f.strip():
                                    try:
                                        supabase.table("feriados").insert({"fecha": fecha_f.isoformat(), "descripcion": desc_f.strip()}).execute()
                                        st.session_state.aviso_feriado = f"Feriado del {fecha_f.strftime('%d-%m-%Y')} guardado."
                                        st.session_state.clear_feriado += 1
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Ya está registrado o no se pudo guardar: {e}")
                            if st.button("Limpiar campos", key=f"limpiar_feriado_{st.session_state.clear_feriado}"):
                                st.session_state.clear_feriado += 1
                                st.rerun()
                        with col_f2:
                            try:
                                feriados_res = supabase.table("feriados").select("*").order("fecha").execute()
                                if feriados_res.data:
                                    df_fer = pd.DataFrame(feriados_res.data)
                                    df_fer["Eliminar"] = False
                                    df_fer_amigable = df_fer[["fecha", "descripcion", "Eliminar"]].copy()
                                    df_fer_amigable["fecha"] = df_fer_amigable["fecha"].map(fecha_visible)
                                    df_fer_amigable = df_fer_amigable.rename(columns={"fecha": "Fecha bloqueada", "descripcion": "Motivo"})
                                    editor_feriados_key = f"editor_tabla_feriados_{st.session_state.clear_feriados_tabla}"
                                    st.data_editor(df_fer_amigable, hide_index=True, disabled=["Fecha bloqueada", "Motivo"], use_container_width=True, key=editor_feriados_key)
                                    filas_edit_fer = st.session_state.get(editor_feriados_key, {}).get("edited_rows", {})
                                    for idx_f, cambio_f in filas_edit_fer.items():
                                        if cambio_f.get("Eliminar") is True:
                                            supabase.table("feriados").delete().eq("id", int(df_fer.iloc[idx_f]["id"])).execute()
                                            st.session_state.mensaje_resultado_app = f"Se eliminó el feriado del {fecha_visible(df_fer.iloc[idx_f]['fecha'])}."
                                            st.session_state.clear_feriados_tabla += 1
                                            st.rerun()
                                else:
                                    st.info("No hay feriados registrados.")
                            except Exception as e:
                                st.error(f"No se pudo cargar la lista de feriados: {e}")
                    with calendario_horarios:
                        if st.session_state.pop("aviso_horarios_restaurados", False):
                            st.success("Se descartaron los cambios sin guardar. Se muestran los valores actuales de la configuración.")
                        st.caption("Define el horario de atención y las reglas de programación y reserva. Agenda y el portal del alumno tomarán estos valores automáticamente.")
                        with st.form(f"form_config_horarios_{st.session_state.clear_configuracion}"):
                            col_h1, col_h2, col_h3 = st.columns(3)
                            with col_h1:
                                hora_apertura_nueva = st.time_input("Apertura del estudio", value=hora_apertura_estudio, key=f"config_hora_apertura_{st.session_state.clear_configuracion}")
                                corte_manana_nuevo = st.time_input("Turno mañana hasta", value=corte_turno_manana, key=f"config_corte_manana_{st.session_state.clear_configuracion}")
                                limite_manana_nuevo = st.time_input("Reserva/cancelación de mañana hasta", value=limite_reserva_manana, key=f"config_limite_manana_{st.session_state.clear_configuracion}", help="Se aplica el día anterior a la clase.")
                            with col_h2:
                                hora_cierre_nueva = st.time_input("Cierre del estudio", value=hora_cierre_estudio, key=f"config_hora_cierre_{st.session_state.clear_configuracion}")
                                duracion_clase_nueva = st.number_input("Duración de clase (minutos)", min_value=15, max_value=240, value=duracion_clase_default, step=5, key=f"config_duracion_clase_{st.session_state.clear_configuracion}")
                                limite_tarde_nuevo = st.number_input("Anticipación para reservar/cancelar clases de tarde (horas)", min_value=1, max_value=24, value=limite_reserva_tarde_horas, step=1, key=f"config_limite_tarde_{st.session_state.clear_configuracion}")
                            with col_h3:
                                dias_agenda_nuevos = st.number_input("Programar y mostrar agenda hasta (días)", min_value=1, max_value=180, value=dias_agenda_anticipacion, step=1, key=f"config_dias_agenda_{st.session_state.clear_configuracion}")
                            guardar_horario_config = st.form_submit_button("Guardar configuración de horarios", type="primary")
                            limpiar_horario_config = st.form_submit_button("Restaurar valores guardados")
                        if limpiar_horario_config:
                            st.session_state.aviso_horarios_restaurados = True
                            st.session_state.clear_configuracion += 1
                            st.rerun()
                        if guardar_horario_config:
                            if hora_apertura_nueva >= hora_cierre_nueva:
                                st.error("La hora de cierre debe ser posterior a la hora de apertura.")
                            elif not hora_apertura_nueva < corte_manana_nuevo < hora_cierre_nueva:
                                st.error("El límite entre mañana y tarde debe quedar dentro del horario del estudio.")
                            else:
                                try:
                                    supabase.table("configuracion_estudio").update({
                                        "hora_apertura": hora_apertura_nueva.strftime("%H:%M:%S"),
                                        "hora_cierre": hora_cierre_nueva.strftime("%H:%M:%S"),
                                        "duracion_clase_minutos": int(duracion_clase_nueva),
                                        "dias_agenda_anticipacion": int(dias_agenda_nuevos),
                                        "corte_turno_manana": corte_manana_nuevo.strftime("%H:%M:%S"),
                                        "limite_reserva_manana": limite_manana_nuevo.strftime("%H:%M:%S"),
                                        "limite_reserva_tarde_horas": int(limite_tarde_nuevo),
                                    }).eq("id", 1).execute()
                                    st.session_state.mensaje_resultado_app = "La configuración de horarios se guardó y se aplicará a la programación y al portal."
                                    st.session_state.clear_configuracion += 1
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"No se pudo guardar la configuración. Ejecuta la migración supabase_configuracion_horarios_instructores.sql en Supabase. Detalle: {e}")

                    with calendario_capacidad:
                        st.caption("Define cuántas camillas grupales puede utilizar cada sede. Agenda tomará este valor automáticamente.")
                        if lista_locales_admin:
                            sedes_config = {f"{l['nombre']} {'(Inactiva)' if not l.get('activo', True) else ''}".strip(): l for l in lista_locales_admin}
                            sede_config_label = st.selectbox("Sede", [""] + list(sedes_config), key=f"sede_capacidad_{st.session_state.clear_configuracion}", placeholder="Selecciona una sede...")
                            sede_config = sedes_config.get(sede_config_label)
                            if sede_config:
                                maximo_sede_config = st.number_input("Máximo de camillas", min_value=1, max_value=50, value=int(sede_config.get("max_camillas") or 8), key=f"max_camillas_config_{sede_config['id']}_{st.session_state.clear_configuracion}")
                                if st.button("Guardar capacidad de la sede", key=f"guardar_capacidad_sede_{sede_config['id']}_{st.session_state.clear_configuracion}", type="primary"):
                                    try:
                                        supabase.table("locales").update({"max_camillas": int(maximo_sede_config)}).eq("id", sede_config["id"]).execute()
                                        st.session_state.mensaje_resultado_app = f"Aforo de {sede_config['nombre']} actualizado a {int(maximo_sede_config)} camillas."
                                        st.session_state.clear_configuracion += 1
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"No se pudo guardar. Ejecuta la migración de capacidad por sede en Supabase. Detalle: {e}")
                        else:
                            st.info("Registra una sede antes de configurar su aforo.")
