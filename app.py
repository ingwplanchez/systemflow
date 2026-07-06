import streamlit as st
from core.state import init_session_state
from core.api_client import api
from ui.styles import get_styles
from ui.layout import render_sidebar, render_dashboard
import pandas as pd
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(
    page_title="SystemFlow | Productivity Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Aplicar Estilos Visuales
st.markdown(get_styles(), unsafe_allow_html=True)

# 3. Inicializar Estado de la Sesión
init_session_state()

# --- Sincronización Inicial con Backend ---
def sync_with_backend(force=False):
    """Sincroniza el estado de Streamlit con los datos persistentes del Backend."""
    # Evitamos resincronizar todo en cada rerun a menos que sea forzado o la primera vez
    if not force and st.session_state.get('initialized', False):
        # Solo recuperamos la sesión activa si estamos en modo 'focus' para evitar lags en modo análisis
        if st.session_state.get('app_mode') == 'focus':
            active_session = api.get_active_session()
            if active_session:
                st.session_state['session_active'] = True
                st.session_state['session_start_time'] = datetime.fromisoformat(active_session['started_at'].replace('Z', '+00:00'))
                st.session_state['active_session_id'] = active_session['id']
            else:
                st.session_state['session_active'] = False
                st.session_state['session_start_time'] = None
                st.session_state['active_session_id'] = None
                st.session_state['app_mode'] = 'analysis' # Volver a análisis si la sesión desapareció
        return

    try:
        # 1. Sincronizar Proyectos
        proyectos_api = api.get_projects()
        if proyectos_api:
            nombres = [p['name'] for p in proyectos_api]
            st.session_state['proyectos'] = ["Todos los Proyectos"] + nombres
        else:
            st.session_state['proyectos'] = ["Todos los Proyectos"]

        # 2. Sincronizar Meta Diaria
        settings = api.get_settings()
        if settings:
            st.session_state['daily_goal'] = settings.get('daily_goal', 4)

        # 3. Recuperar Sesión de Enfoque Activa
        active_session = api.get_active_session()
        if active_session:
            st.session_state['session_active'] = True
            st.session_state['session_start_time'] = datetime.fromisoformat(active_session['started_at'].replace('Z', '+00:00'))
            st.session_state['active_session_id'] = active_session['id']
            st.session_state['app_mode'] = 'focus'
        else:
            st.session_state['session_active'] = False
            st.session_state['session_start_time'] = None
            st.session_state['active_session_id'] = None
            st.session_state['app_mode'] = 'analysis'

        # 4. Cargar Tareas Iniciales
        tasks_api = api.get_tasks()
        if tasks_api:
            st.session_state['df_tareas'] = pd.DataFrame(tasks_api)
        else:
            st.session_state['df_tareas'] = pd.DataFrame(columns=['project', 'real_hours', 'status', 'timestamp', 'task_id'])

        st.session_state['initialized'] = True

    except Exception as e:
        st.error(f"⚠️ Error de conexión con el servidor: {e}")
        st.info("Asegúrate de que el backend esté corriendo con: `uvicorn backend.main:app --reload` en otra terminal.")
        st.session_state['proyectos'] = ["Todos los Proyectos"]
        st.session_state['df_tareas'] = pd.DataFrame(columns=['project', 'real_hours', 'status', 'timestamp', 'task_id'])

# Ejecutar sincronización al inicio
sync_with_backend()

# 4. Ejecutar Interfaz
proyecto_seleccionado = render_sidebar()
render_dashboard(proyecto_seleccionado)
