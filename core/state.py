import streamlit as st
import pandas as pd
import numpy as np

def init_session_state():
    if 'proyectos' not in st.session_state:
        st.session_state['proyectos'] = ["Todos los Proyectos", "Ultra Enfoque", "Nexus Flow", "Vendedor Digital"]

    if 'session_active' not in st.session_state:
        st.session_state['session_active'] = False

    if 'session_start_time' not in st.session_state:
        st.session_state['session_start_time'] = None

    if 'df_tareas' not in st.session_state:
        st.session_state['df_tareas'] = pd.DataFrame([
            {"timestamp": "2026-06-22 09:00", "task_id": "T-000", "project": "SystemFlow", "module_task": "Configuración del proyecto", "category": "deep_work", "priority": "high", "est_hours": 2.0, "real_hours": 2.0, "difficulty": 1, "status": "Completed"},
            {"timestamp": "2026-06-22 11:00", "task_id": "T-001", "project": "Ultra Enfoque", "module_task": "Configuración del proyecto", "category": "deep_work", "priority": "high", "est_hours": 2.0, "real_hours": 2.0, "difficulty": 2, "status": "Completed"},
            {"timestamp": "2026-06-22 13:00", "task_id": "T-002", "project": "ZenFlow ", "module_task": "Configuración del proyecto", "category": "deep_work", "priority": "high", "est_hours": 3.0, "real_hours": 3.0, "difficulty": 3, "status": "Completed"},
            {"timestamp": "2026-06-23 09:00", "task_id": "T-003", "project": "Ultra Enfoque", "module_task": "Configuración del proyecto", "category": "deep_work", "priority": "high", "est_hours": 2.0, "real_hours": 1.0, "difficulty": 4, "status": "Completed"},
            {"timestamp": "2026-06-23 10:00", "task_id": "T-004", "project": "Ultra Enfoque", "module_task": "Refactorización Backend", "category": "deep_work", "priority": "high", "est_hours": 2.0, "real_hours": 1, "difficulty": 1, "status": "Completed"},
            {"timestamp": "2026-06-24 11:30", "task_id": "T-005", "project": "Nexus Flow", "module_task": "Diseño de PCB en KiCad", "category": "collaboration", "priority": "medium", "est_hours": 1.0, "real_hours": 1.5, "difficulty": 2, "status": "Interrupted"},
            {"timestamp": "2026-06-24 14:00", "task_id": "T-006", "project": "Vendedor Digital", "module_task": "Configuración de Webhooks n8n", "category": "strategy", "priority": "low", "est_hours": 4.0, "real_hours": 1.5, "difficulty": 3, "status": "Completed"},
            {"timestamp": "2026-06-25 15:00", "task_id": "T-007", "project": "OptiFlow", "module_task": "Despliegue del Chatbot", "category": "deep_work", "priority": "high", "est_hours": 2.0, "real_hours": 2.0, "difficulty": 4.0, "status": "Completed"},
            {"timestamp": "2026-06-26 16:00", "task_id": "T-008", "project": "Ultra Enfoque", "module_task": "Integración API Stripe", "category": "deep_work", "priority": "high", "est_hours": 2.0, "real_hours": 1.5, "difficulty": 5.0, "status": "Completed"}
        ])
