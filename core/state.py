import streamlit as st
import pandas as pd
import numpy as np

def init_session_state():
    if 'proyectos' not in st.session_state:
        st.session_state['proyectos'] = []

    if 'session_active' not in st.session_state:
        st.session_state['session_active'] = False

    if 'session_start_time' not in st.session_state:
        st.session_state['session_start_time'] = None

    if 'daily_goal' not in st.session_state:
        st.session_state['daily_goal'] = 4

    if 'df_tareas' not in st.session_state:
        st.session_state['df_tareas'] = pd.DataFrame()
