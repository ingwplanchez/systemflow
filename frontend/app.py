import streamlit as st
import pandas as pd
import numpy as np
import datetime
import io
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(
    page_title="SystemFlow | Productivity Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inyección de CSS (Mantiene tus indicadores idénticos a las capturas)
st.markdown("""
    <style>
        div[data-testid="stMetricValue"] {
            font-size: 2.2rem;
            font-weight: 700;
            color: #00FFA3;
        }
        div[data-testid="metric-container"] {
            background-color: #1E293B;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #334155;
        }
        /* Botones Primarios (Verde Neón) */
        div.stButton > button[kind="primary"] {
            background-color: #00FFA3 !important;
            color: #000000 !important;
            border: none !important;
            font-weight: 600 !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #00CC82 !important;
            color: #000000 !important;
        }
        /* Botones Secundarios en Sidebar (Rojo) */
        div[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
            background-color: #FF4B4B !important;
            color: white !important;
            border: none !important;
            font-weight: 600 !important;
        }
        div[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
            background-color: #D32F2F !important;
            color: white !important;
        }
        .main .block-container {
            padding-top: 2rem;
        }


    </style>
""", unsafe_allow_html=True)

# 3. Inicialización del Estado de la Sesión
if 'proyectos' not in st.session_state:
    st.session_state['proyectos'] = ["Todos los Proyectos", "Ultra Enfoque", "Nexus Flow", "Vendedor Digital"]

if 'session_active' not in st.session_state:
    st.session_state['session_active'] = False

if 'session_start_time' not in st.session_state:
    st.session_state['session_start_time'] = None

if 'df_tareas' not in st.session_state:
    st.session_state['df_tareas'] = pd.DataFrame([
        {"timestamp": "2026-06-25 09:00", "task_id": "T-001", "project": "Ultra Enfoque", "module_task": "Refactorización Backend", "category": "deep_work", "priority": "high", "est_hours": 2.0, "real_hours": 0.75, "difficulty": 3, "status": "Completed"},
        {"timestamp": "2026-06-26 11:30", "task_id": "T-002", "project": "Nexus Flow", "module_task": "Diseño de PCB en KiCad", "category": "collaboration", "priority": "medium", "est_hours": 1.0, "real_hours": 0.75, "difficulty": 2, "status": "Interrupted"},
        {"timestamp": "2026-06-27 14:00", "task_id": "T-003", "project": "Vendedor Digital", "module_task": "Configuración de Webhooks n8n", "category": "strategy", "priority": "critical", "est_hours": 4.0, "real_hours": 0.5, "difficulty": 4, "status": "Completed"}
    ])

# 4. Pipeline de Limpieza ETL con Esquema Estricto
def procesar_datos_etl(df):
    df_clean = df.copy()
    
    # Definición del esquema estricto de columnas requerido por el motor ETL
    columnas_estrictas = [
        'timestamp', 'task_id', 'project', 'category', 'priority', 
        'est_hours', 'real_hours', 'difficulty', 'status'
    ]
    
    # Filtrar solo las columnas del esquema estricto para la ingesta del motor ETL
    df_clean = df_clean[[col for col in columnas_estrictas if col in df_clean.columns]]
    
    # Limpieza de Datos: Eliminar nulos en columnas críticas
    columnas_criticas = ['timestamp', 'task_id', 'project', 'category', 'status']
    columnas_criticas_existentes = [col for col in columnas_criticas if col in df_clean.columns]
    df_clean = df_clean.dropna(subset=columnas_criticas_existentes)
    
    # Normalización de Texto: Minúsculas y quitar espacios en blanco
    for col in ['category', 'priority', 'status']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.lower().str.strip()
            
    # Limpieza Numérica: Forzar horas negativas a 0.0
    if 'est_hours' in df_clean.columns:
        df_clean['est_hours'] = df_clean['est_hours'].clip(lower=0.0)
    if 'real_hours' in df_clean.columns:
        df_clean['real_hours'] = df_clean['real_hours'].clip(lower=0.0)
    
    # Control de Rango: Forzar dificultad entre 1 y 5
    if 'difficulty' in df_clean.columns:
        df_clean['difficulty'] = df_clean['difficulty'].clip(1, 5)
        
    # Garantizar presencia de todas las columnas del esquema estricto (rellenar con nan si falta alguna)
    for col in columnas_estrictas:
        if col not in df_clean.columns:
            df_clean[col] = np.nan
            
    # Reordenamiento estricto final
    df_clean = df_clean[columnas_estrictas]
    return df_clean

# 5. BARRA LATERAL (Ingreso de datos)
with st.sidebar:
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 30px;'>
            <img src='https://cdn-icons-png.flaticon.com/512/1055/1055644.png' width='80' style='filter: hue-rotate(120deg);'>
            <h1 style='color: #00FFA3; font-size: 2.2rem; margin-bottom: 0; font-weight: 800; letter-spacing: -1px;'>SystemFlow</h1>
            <p style='color: #94A3B8; font-size: 0.9rem; margin-top: 0; font-weight: 400;'>Deep Work Analytics</p>
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown("### ⏱️ Control de Enfoque")
    if not st.session_state['session_active']:
        if st.button("🚀 Iniciar Sesión de Enfoque", use_container_width=True, type="primary"):
            st.session_state['session_active'] = True
            st.session_state['session_start_time'] = datetime.datetime.now()
            st.rerun()
    else:
        # Calcular tiempo transcurrido
        elapsed = datetime.datetime.now() - st.session_state['session_start_time']
        st.info(f"⏳ Sesión activa: {elapsed.total_seconds() // 60:.0f} min")
        if st.button("🛑 Finalizar Sesión", use_container_width=True, type="secondary"):
            # Finalizar sesión y registrar automáticamente como 'deep_work'
            real_h = elapsed.total_seconds() / 3600
            nueva_fila = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "task_id": f"SESS-{datetime.datetime.now().strftime('%Y%m%d%H%M')}",
                "project": proyecto_seleccionado if proyecto_seleccionado != "Todos los Proyectos" else st.session_state['proyectos'][1],
                "module_task": "Sesión de Enfoque Automática",
                "category": "deep_work",
                "priority": "medium",
                "est_hours": real_h,
                "real_hours": real_h,
                "difficulty": 3,
                "status": "completed"
            }
            st.session_state['df_tareas'] = pd.concat([st.session_state['df_tareas'], pd.DataFrame([nueva_fila])], ignore_index=True)
            st.session_state['session_active'] = False
            st.session_state['session_start_time'] = None
            st.success("✅ Sesión guardada automáticamente.")
            st.rerun()

    st.divider()

    st.subheader("📁 Gestión de Proyectos")
    nuevo_proyecto = st.text_input("Nombre del nuevo proyecto:", placeholder="Ej: Proyecto Gamma")
    if st.button("➕ Crear Proyecto", use_container_width=True, type="primary"):
        if nuevo_proyecto and nuevo_proyecto not in st.session_state['proyectos']:
            st.session_state['proyectos'].append(nuevo_proyecto)
            st.success(f"Proyecto '{nuevo_proyecto}' creado.")
            st.rerun()
            
    st.divider()
    proyecto_seleccionado = st.selectbox("Filtrar Dashboard por:", st.session_state['proyectos'])
    st.divider()
    
    st.subheader("📝 Registrar Nueva Tarea")
    with st.form("form_tarea", clear_on_submit=True):
        proj_asociado = st.selectbox("Asociar al proyecto:", [p for p in st.session_state['proyectos'] if p != "Todos los Proyectos"])
        task_id_input = st.text_input("Identificador / Tarea:", placeholder="Ej: T-004")
        
        # Descripción de la tarea debajo de Identificador (Se usará para la visualización simplificada)
        module_task_input = st.text_input("Módulo / Descripción de Tarea:", placeholder="Ej: Refactorización Backend")
        
        categoria = st.selectbox("Categoría:", [" deep_work ", " collaboration ", " strategy ", " reactive "])
        prioridad = st.selectbox("Prioridad:", [" High ", " Medium ", " Low ", " Critical "])
        est_h = st.number_input("Horas Estimadas:", min_value=0.0, value=1.0, step=0.5)
        real_h = st.number_input("Horas Reales (Duración):", min_value=0.0, value=0.75, step=0.25)
        dificultad = st.slider("Dificultad (1-5):", 1, 5, 3)
        estado_t = st.selectbox("Estado:", [" Completed ", " Interrupted ", " In Progress "])
        
        submitted = st.form_submit_button("Registrar Bloque")
        if submitted:
            # INTEGRACIÓN: Si hay una sesión activa, usar ese tiempo automáticamente
            if st.session_state['session_active']:
                elapsed = datetime.datetime.now() - st.session_state['session_start_time']
                real_h_final = elapsed.total_seconds() / 3600
                # Resetear sesión ya que estamos registrando el bloque
                st.session_state['session_active'] = False
                st.session_state['session_start_time'] = None
                st.toast(f"⏱️ Tiempo de sesión aplicado: {real_h_final:.2f} hrs")
            else:
                real_h_final = real_h

            nueva_fila = {
                # CORRECCIÓN: Ahora guardamos con la estructura de hora "%Y-%m-%d %H:%M" para mantener homogeneidad
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "task_id": task_id_input,
                "project": proj_asociado,
                "module_task": module_task_input,
                "category": categoria,
                "priority": prioridad,  # Corrección de variable mapeada
                "est_hours": est_h,
                "real_hours": real_h_final,
                "difficulty": dificultad,
                "status": estado_t
            }
            st.session_state['df_tareas'] = pd.concat([st.session_state['df_tareas'], pd.DataFrame([nueva_fila])], ignore_index=True)
            st.toast("✅ Tarea registrada con éxito.")
            st.rerun()

# 6. FILTRADO DE DATOS PARA EL DASHBOARD
df_master = st.session_state['df_tareas']
df_filtrado = df_master if proyecto_seleccionado == "Todos los Proyectos" else df_master[df_master['project'] == proyecto_seleccionado]

# 7. INDICADORES SUPERIORES
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Puntuación de Enfoque", value="88 / 100", delta="+5% esta semana")
with col2:
    st.metric(label="Ciclos Completados (Hoy)", value="4 / 6", delta="Meta: 6")
with col3:
    st.metric(label="Tiempo Total Enfocado", value=f"{df_filtrado['real_hours'].sum():.1f} hrs", delta=None)
with col4:
    st.metric(label="Eficiencia Promedio", value="92%", delta="+2% vs mes anterior")

st.write("---")

# 8. PESTAÑAS DE CONTENIDO
tab_tendencias, tab_historial, tab_etl = st.tabs(["📊 Tendencias Temporales", "📋 Historial de Tareas", "🚀 Motor de Exportación ETL"])

with tab_tendencias:
    st.subheader("Análisis de Productividad y Enfoque")

    if len(df_filtrado) == 0:
        st.info("No hay suficientes datos para generar gráficos para este proyecto.")
    else:
        df_trends = df_filtrado.copy()
        df_trends['fecha_dt'] = pd.to_datetime(df_trends['timestamp'], errors='coerce')

        # --- GRÁFICO 1: EFICIENCIA POR DÍA (Ciclos Completados) ---
        # Filtrar solo tareas completadas
        df_completed = df_trends[df_trends['status'].str.lower().str.strip() == 'completed'].copy()

        if not df_completed.empty:
            # Mapeo de días al español
            dias_map = {
                'Monday': 'Lunes',
                'Tuesday': 'Martes',
                'Wednesday': 'Miércoles',
                'Thursday': 'Jueves',
                'Friday': 'Viernes',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
            }
            df_completed['Día'] = df_completed['fecha_dt'].dt.day_name().map(dias_map)

            # Ordenar días de la semana en español
            dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

            # Contar ciclos completados por día
            day_counts = df_completed['Día'].value_counts().reindex(dias_orden).fillna(0).reset_index()
            day_counts.columns = ['Día', 'Ciclos']

            fig_day = px.bar(
                day_counts,
                x='Ciclos',
                y='Día',
                orientation='h',
                color_discrete_sequence=['#00FFA3'],
                title="<b>¿En qué día soy más eficiente?</b> (Ciclos Completados)",
                template="plotly_dark"
            )
            fig_day.update_layout(
                yaxis=dict(autorange="reversed"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="#CBD5E1"
            )
            st.plotly_chart(fig_day, use_container_width=True)
        else:
            st.warning("No hay tareas marcadas como 'completed' para mostrar el gráfico de eficiencia.")

        st.write("---")

        # --- GRÁFICO 2: PRODUCTIVIDAD POR HORA ---
        df_trends['Hora'] = df_trends['fecha_dt'].dt.hour
        hour_counts = df_trends['Hora'].value_counts().sort_index().reset_index()
        hour_counts.columns = ['Hora', 'Bloques']

        # Definir segmentos del día
        def get_segment(h):
            if 6 <= h < 12: return 'Mañana'
            if 12 <= h < 18: return 'Tarde'
            return 'Noche'

        hour_counts['Segmento'] = hour_counts['Hora'].apply(get_segment)

        fig_hour = px.line(
            hour_counts,
            x='Hora',
            y='Bloques',
            markers=True,
            color_discrete_sequence=['#00FFA3'],
            title="<b>¿A qué horas soy más productivo?</b> (Intensidad de Bloques)",
            template="plotly_dark"
            )
        fig_hour.update_layout(
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="#CBD5E1"
        )
        # Añadir anotaciones de segmentos
        fig_hour.add_vrect(x0=6, x1=12, fillcolor="green", opacity=0.1, annotation_text="Mañana", annotation_position="top left")
        fig_hour.add_vrect(x0=12, x1=18, fillcolor="blue", opacity=0.1, annotation_text="Tarde", annotation_position="top left")
        fig_hour.add_vrect(x0=18, x1=23, fillcolor="purple", opacity=0.1, annotation_text="Noche", annotation_position="top left")

        st.plotly_chart(fig_hour, use_container_width=True)

with tab_historial:
    st.subheader("Registro de Bloques de Trabajo")
    if len(df_filtrado) == 0:
        st.info("No hay tareas registradas.")
    else:
        # Vista simplificada para el usuario final en la interfaz
        df_vista_cliente = df_filtrado[[
            'task_id', 'timestamp', 'project', 'module_task', 'real_hours', 'status'
        ]].rename(columns={
            'task_id': 'ID',
            'timestamp': 'Fecha',
            'project': 'Proyecto',
            'module_task': 'Módulo / Tarea',
            'real_hours': 'Duración (Horas)',
            'status': 'Resultado'
        })
        
        st.dataframe(df_vista_cliente, use_container_width=True, hide_index=True)

with tab_etl:
    st.subheader("Preprocesamiento e Ingesta de Datos (Esquema ETL Estricto)")
    st.write("Esta tabla contiene únicamente las columnas requeridas por el pipeline del motor ETL:")
    
    # Procesar el DataFrame para cumplir con el esquema riguroso
    df_procesado_etl = procesar_datos_etl(df_master)
    
    # Se renderiza la tabla estrictamente limpia y mapeada
    st.dataframe(df_procesado_etl, use_container_width=True, hide_index=True)
    
    csv_buffer = io.StringIO()
    df_procesado_etl.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    
    st.write("---")
    st.download_button(
        label="📥 Exportar Data limpia para ETL (.csv)",
        data=csv_bytes,
        file_name=f"systemflow_etl_{datetime.date.today()}.csv",
        mime="text/csv",
        help="Descarga el archivo CSV con el esquema exacto de 9 columnas para evitar fallas de ingesta en el motor."
    )