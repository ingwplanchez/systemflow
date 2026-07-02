import streamlit as st
import pandas as pd
import datetime
import io
import plotly.express as px
from core.etl import procesar_datos_etl
from core.api_client import api

def render_sidebar():
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
                # Obtener ID del proyecto seleccionado (excluyendo la opción "Todos los Proyectos")
                proj_name = st.session_state.get('proyecto_seleccionado', "Ultra Enfoque")
                if proj_name == "Todos los Proyectos":
                    proj_name = "Ultra Enfoque" # Default fallback

                # Buscar el ID del proyecto en la lista de proyectos de la API
                projs = api.get_projects()
                proj_id = next((p['id'] for p in projs if p['name'] == proj_name), 1)

                res = api.start_focus_session(proj_id)
                if res:
                    st.session_state['session_active'] = True
                    st.session_state['session_start_time'] = datetime.datetime.fromisoformat(res['started_at'].replace('Z', '+00:00'))
                    st.session_state['active_session_id'] = res['id']
                    st.rerun()
        else:
            elapsed = datetime.datetime.now() - st.session_state['session_start_time']
            st.info(f"⏳ Sesión activa: {elapsed.total_seconds() // 60:.0f} min")
            if st.button("🛑 Finalizar Sesión", use_container_width=True, type="secondary"):
                session_id = st.session_state.get('active_session_id')
                if session_id:
                    res = api.stop_focus_session(session_id)
                    if res:
                        st.session_state['session_active'] = False
                        st.session_state['session_start_time'] = None
                        st.session_state['active_session_id'] = None
                        # Refrescar cache de tareas
                        st.session_state['df_tareas'] = pd.DataFrame(api.get_tasks())
                        st.success("✅ Sesión guardada automáticamente.")
                        st.rerun()

        # Control de Meta Diaria
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        # Usamos un valor temporal para el input y actualizamos la API al cambiar
        current_goal = st.session_state.get('daily_goal', 4)
        new_goal = st.number_input(
            "🎯 Meta Diaria de Bloques:",
            min_value=1,
            max_value=20,
            value=current_goal,
            step=1
        )
        if new_goal != current_goal:
            api.update_settings(new_goal)
            st.session_state['daily_goal'] = new_goal
            st.rerun()

        st.caption("Sugerencia: 4 bloques (Técnica Pomodoro)")

        st.divider()

        st.subheader("📁 Gestión de Proyectos")
        nuevo_proyecto = st.text_input("Nombre del nuevo proyecto:", placeholder="Ej: Proyecto Gamma")
        if st.button("➕ Crear Proyecto", use_container_width=True, type="primary"):
            if nuevo_proyecto:
                res = api.create_project(nuevo_proyecto)
                if res:
                    # Actualizar lista local de proyectos
                    projs_api = api.get_projects()
                    st.session_state['proyectos'] = ["Todos los Proyectos"] + [p['name'] for p in projs_api]
                    st.success(f"Proyecto '{nuevo_proyecto}' creado.")
                    st.rerun()

        st.divider()
        proyecto_sel = st.selectbox("Filtrar Dashboard por:", st.session_state['proyectos'])
        st.session_state['proyecto_seleccionado'] = proyecto_sel
        st.divider()

        st.subheader("📝 Registrar Nueva Tarea")
        with st.form("form_tarea", clear_on_submit=True):
            # Filtrar proyectos para el selectbox (sin el sentinel)
            projs_api = api.get_projects()
            proj_names = [p['name'] for p in projs_api]
            proj_asociado_name = st.selectbox("Asociar al proyecto:", proj_names)

            task_id_input = st.text_input("Identificador / Tarea:", placeholder="Ej: T-004")
            module_task_input = st.text_input("Módulo / Descripción de Tarea:", placeholder="Ej: Refactorización Backend")
            categoria = st.selectbox("Categoría:", ["deep_work", "collaboration", "strategy", "reactive"])
            prioridad = st.selectbox("Prioridad:", ["critical", "high", "medium", "low"])
            est_h = st.number_input("Horas Estimadas:", min_value=0.0, value=1.0, step=0.5)
            real_h = st.number_input("Horas Reales (Duración):", min_value=0.0, value=0.75, step=0.25)
            dificultad = st.slider("Dificultad (1-5):", 1, 5, 3)
            estado_t = st.selectbox("Estado:", ["completed", "in_progress", "pending"])

            submitted = st.form_submit_button("Registrar Bloque")
            if submitted:
                # Buscar el ID del proyecto seleccionado
                proj_id = next((p['id'] for p in projs_api if p['name'] == proj_asociado_name), 1)

                real_h_final = real_h
                if st.session_state['session_active']:
                    # Si hay sesión activa, la cerramos y usamos su tiempo
                    session_id = st.session_state.get('active_session_id')
                    if session_id:
                        res_stop = api.stop_focus_session(session_id)
                        if res_stop:
                            real_h_final = res_stop['real_hours']
                            st.session_state['session_active'] = False
                            st.session_state['session_start_time'] = None
                            st.session_state['active_session_id'] = None
                            st.toast(f"⏱️ Tiempo de sesión aplicado: {real_h_final:.2f} hrs")

                # Preparar payload para API
                task_payload = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "task_id": task_id_input,
                    "project_id": proj_id,
                    "module_task": module_task_input,
                    "category": categoria,
                    "priority": prioridad,
                    "est_hours": est_h,
                    "real_hours": real_h_final,
                    "difficulty": dificultad,
                    "status": estado_t
                }

                if api.create_task(task_payload):
                    # Refrescar cache de tareas
                    st.session_state['df_tareas'] = pd.DataFrame(api.get_tasks())
                    st.toast("✅ Tarea registrada con éxito.")
                    st.rerun()

    return proyecto_sel

def render_dashboard(proyecto_seleccionado):
    df_master = st.session_state['df_tareas']
    df_filtrado = df_master if proyecto_seleccionado == "Todos los Proyectos" else df_master[df_master['project'] == proyecto_seleccionado]

    # --- Cálculos Dinámicos de KPIs ---
    df_completed = df_filtrado[df_filtrado['status'].str.lower().str.strip() == 'completed'].copy()

    # 1. Focus Score (Precisión de Estimación)
    if not df_completed.empty:
        diff_ratio = (df_completed['est_hours'] - df_completed['real_hours']).abs() / df_completed['est_hours'].replace(0, float('nan'))
        avg_diff = diff_ratio.mean()
        focus_score = max(0, int(100 * (1 - (avg_diff if not pd.isna(avg_diff) else 0))))
    else:
        focus_score = 0

    # 2. Ciclos Completados (Hoy)
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    df_today = df_completed[df_completed['timestamp'].str.startswith(today_str)]
    ciclos_hoy = len(df_today)
    meta_diaria = st.session_state.get('daily_goal', 6)

    # 3. Tiempo Total Enfocado (Contextualizado)
    total_horas = df_filtrado['real_hours'].sum()
    # Sumamos horas de hoy independientemente de si están 'completed' (para ver progreso actual)
    horas_hoy = df_filtrado[df_filtrado['timestamp'].str.startswith(today_str)]['real_hours'].sum()

    # 4. Eficiencia Promedio (Rendimiento Real vs Estimado)
    if not df_completed.empty:
        suma_est = df_completed['est_hours'].sum()
        suma_real = df_completed['real_hours'].sum()
        # Si suma_real es 0, la eficiencia es 0 para evitar división por cero
        eficiencia = (suma_est / suma_real * 100) if suma_real > 0 else 0
        eficiencia = min(120, eficiencia) # Capamos en 120% para evitar valores absurdos en el UI
    else:
        eficiencia = 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Puntuación de Enfoque", value=f"{focus_score} / 100", delta="+5% esta semana")
    with col2:
        st.metric(label="Ciclos Completados (Hoy)", value=f"{ciclos_hoy} / {meta_diaria}", delta=f"Meta: {meta_diaria}")
    with col3:
        st.metric(label="Tiempo Total Enfocado", value=f"{total_horas:.1f} hrs", delta=f"Hoy: {horas_hoy:.1f} h")
    with col4:
        st.metric(label="Eficiencia Promedio", value=f"{int(eficiencia)}%", delta="+2% vs mes anterior")

    st.write("---")

    tab_tendencias, tab_historial, tab_etl = st.tabs(["📊 Tendencias Temporales", "📋 Historial de Tareas", "🚀 Motor de Exportación ETL"])

    with tab_tendencias:
        st.subheader("Análisis de Productividad y Enfoque")
        if len(df_filtrado) == 0:
            st.info("No hay suficientes datos para generar gráficos para este proyecto.")
        else:
            df_trends = df_filtrado.copy()
            df_trends['fecha_dt'] = pd.to_datetime(df_trends['timestamp'], errors='coerce')
            df_completed = df_trends[df_trends['status'].str.lower().str.strip() == 'completed'].copy()

            if not df_completed.empty:
                dias_map = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
                df_completed['Día'] = df_completed['fecha_dt'].dt.day_name().map(dias_map)
                dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

                # Lógica de Volumen y Color por Dificultad
                # Usamos dt.weekday (0=Lunes, 6=Domingo) para evitar errores de idioma/locale
                df_completed['day_idx'] = df_completed['fecha_dt'].dt.weekday
                dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

                # Mapeamos el índice numérico al nombre en español
                df_completed['Día'] = df_completed['day_idx'].map(lambda x: dias_orden[int(x)])

                day_stats = df_completed.groupby('Día').agg(
                    bloques=('task_id', 'count'),
                    horas_totales=('real_hours', 'sum'),
                    dificultad_avg=('difficulty', 'mean')
                ).reindex(dias_orden).fillna(0).reset_index()

                def assign_color(val):
                    if val <= 2: return '#1B4332' # Verde oscuro
                    if val <= 3.5: return '#00FFA3' # Verde Neón
                    return '#FACC15' # Ambar Eléctrico para alta dificultad

                day_stats['color'] = day_stats['dificultad_avg'].apply(assign_color)
                # Crear etiqueta combinada: "N bloq. (X.X hrs)"
                day_stats['label_texto'] = day_stats.apply(
                    lambda row: f"{int(row['bloques'])} bloq. ({row['horas_totales']:.1f}h)" if row['bloques'] > 0 else "",
                    axis=1
                )

                # Calcular el límite del eje X para evitar que las etiquetas se corten
                max_bloques = day_stats['bloques'].max()
                x_limit = max_bloques + 1 if max_bloques > 0 else 1

                fig_day = px.bar(
                    day_stats,
                    x='bloques',
                    y='Día',
                    orientation='h',
                    color='color',
                    text='label_texto',
                    color_discrete_map='identity',
                    title="<b>Volumen de Trabajo por Día y Nivel de Dificultad</b>",
                    template="plotly_dark",
                    labels={
                        'bloques': 'Bloques',
                        'horas_totales': 'Tiempo Total',
                        'dificultad_avg': 'Dificultad',
                        'Día': 'Día'
                    },
                    hover_data={
                        'bloques': True,
                        'horas_totales': ':.1f',
                        'dificultad_avg': ':.1f',
                        'label_texto': False # Ocultamos el texto redundante del hover
                    }
                )
                fig_day.update_layout(
                    yaxis=dict(
                        autorange="reversed",
                        categoryorder="array",
                        categoryarray=dias_orden
                    ),
                    xaxis=dict(
                        range=[0, x_limit], # Forzamos un espacio extra al final
                        tickmode='linear',
                        tick0=0,
                        dtick=1,
                        showticklabels=False
                    ),
                    margin=dict(r=120, l=20, t=50, b=50), # Aumentamos ligeramente el margen derecho
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color="#CBD5E1",
                    showlegend=False
                )
                fig_day.update_traces(textposition='outside')
                st.plotly_chart(fig_day, use_container_width=True)
                st.caption("💡 El color indica la dificultad promedio y el texto la cantidad de bloques con su tiempo total.")
            else:
                st.warning("No hay tareas marcadas como 'completed' para mostrar el gráfico de eficiencia.")

            st.write("---")
            # --- Implementación Mapa de Calor de Productividad (GitHub Style) ---
            st.subheader("Mapa de Calor de Intensidad Horaria")

            df_trends['Hora'] = df_trends['fecha_dt'].dt.hour
            # Definimos el mapa de días si no se definieron arriba debido a df_completed vacío
            dias_map = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
            dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            df_trends['Día'] = df_trends['fecha_dt'].dt.day_name().map(dias_map)

            # Crear matriz de volumen: Filas = Días, Columnas = Horas (Suma de real_hours)
            heatmap_data = df_trends.groupby(['Día', 'Hora'])['real_hours'].sum().unstack(fill_value=0)
            heatmap_data = heatmap_data.reindex(dias_orden).fillna(0)

            # Asegurar que todas las horas (0-23) estén presentes
            for h in range(24):
                if h not in heatmap_data.columns:
                    heatmap_data[h] = 0
            heatmap_data = heatmap_data.sort_index(axis=1)

            fig_heatmap = px.imshow(
                heatmap_data,
                labels=dict(x="Hora del Día", y="Día de la Semana", color="Horas"),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale=[[0, '#1E293B'], [0.5, '#065F46'], [1, '#00FFA3']],
                title="<b>Mapa de Calor de Productividad</b> (Volumen de Enfoque por Hora)",
                template="plotly_dark"
            )

            # Crear el efecto de celdas separadas (estilo GitHub) mediante gaps
            fig_heatmap.update_traces(xgap=3, ygap=3)

            fig_heatmap.update_layout(
                xaxis=dict(
                    tickmode='linear',
                    tick0=0,
                    dtick=2,
                    showgrid=False
                ),
                yaxis=dict(
                    showgrid=False
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color="#CBD5E1",
                xaxis_title="Hora (0-23h)",
                yaxis_title=""
            )

            st.plotly_chart(fig_heatmap, use_container_width=True)
            st.caption("💡 Las celdas más brillantes indican el mayor volumen de tiempo enfocado (Suma de horas reales).")

    with tab_historial:
        st.subheader("Registro de Bloques de Trabajo")
        if len(df_filtrado) == 0:
            st.info("No hay tareas registradas.")
        else:
            df_vista_cliente = df_filtrado[['task_id', 'timestamp', 'project', 'module_task', 'real_hours', 'status']].rename(
                columns={'task_id': 'ID', 'timestamp': 'Fecha', 'project': 'Proyecto', 'module_task': 'Módulo / Tarea', 'real_hours': 'Duración (Horas)', 'status': 'Resultado'}
            )
            st.dataframe(df_vista_cliente, use_container_width=True, hide_index=True)

    with tab_etl:
        st.subheader("Preprocesamiento e Ingesta de Datos (Esquema ETL Estricto)")
        st.write("Esta tabla contiene únicamente las columnas requeridas por el pipeline del motor ETL:")
        df_procesado_etl = procesar_datos_etl(df_master)
        st.dataframe(df_procesado_etl, use_container_width=True, hide_index=True)
        csv_buffer = io.StringIO()
        df_procesado_etl.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
        st.write("---")
        st.download_button(label="📥 Exportar Data limpia para ETL (.csv)", data=csv_bytes, file_name=f"systemflow_etl_{datetime.date.today()}.csv", mime="text/csv")
