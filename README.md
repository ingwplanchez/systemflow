# SystemFlow ⚙️

**SystemFlow** es una plataforma de análisis de productividad diseñada para medir y optimizar el tiempo de trabajo profundo (*deep work*). El sistema registra sesiones de trabajo, calcula métricas de enfoque mediante lógica de negocio personalizada y visualiza tendencias mediante análisis de datos en tiempo real.

## 🛠️ Stack Tecnológico
- **Frontend:** Streamlit para la visualización de datos y el dashboard interactivo.
- **Backend:** FastAPI (Python) para la gestión de APIs y persistencia de datos (en desarrollo).
- **Data Science:** Pandas y Plotly para el procesamiento, limpieza y análisis de tendencias.
- **Base de Datos:** SQLite para despliegue local sencillo.

## 📂 Estructura del Proyecto
La aplicación sigue una arquitectura modular basada en la separación de responsabilidades:

```text
systemflow/
├── app.py              # Punto de entrada principal de la aplicación
├── core/               # Lógica de negocio y procesamiento de datos
│   ├── state.py        # Gestión del estado de la sesión (st.session_state)
│   └── etl.py          # Pipeline de limpieza y normalización de datos (Esquema ETL)
├── ui/                 # Diseño y presentación de la interfaz
│   ├── styles.py       # Definiciones de CSS y estilos visuales
│   └── layout.py       # Estructura de la página, sidebar y componentes del dashboard
├── backend/            # API REST y persistencia de datos (Sprints futuros)
├── data_analysis/      # Motor de cálculo de métricas y Focus Score (Sprints futuros)
└── requirements.txt    # Dependencias del proyecto
```

## 🚀 Ejecución Local
Para ejecutar la aplicación en modo desarrollo:

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Lanzar el Dashboard**:
   ```bash
   streamlit run app.py
   ```

## 📅 Hoja de Ruta (Roadmap)
El desarrollo está dividido en sprints técnicos para asegurar la escalabilidad:

### Sprint 1: Backend & Persistencia
- Implementación de FastAPI para reemplazar el almacenamiento en memoria.
- Definición de modelos de datos (Proyectos, Tareas) con SQLAlchemy.
- Creación de endpoints CRUD para el registro persistente de sesiones.

### Sprint 2: Lógica de Análisis
- Desarrollo del motor de cálculo de la "Puntuación de Enfoque" (*Focus Score*).
- Agregaciones temporales avanzadas para detección de picos de productividad.

### Sprint 3: Integración Final
- Conexión total del frontend con la API mediante clientes HTTP.
- Implementación de visualizaciones avanzadas del Focus Score.

## 🛠️ Especificaciones Técnicas Obligatorias
- **Ingesta de Datos**: Cualquier importación de CSV debe seguir estrictamente el `DATA_SCHEMA.md`.
- **Colores de Interfaz**: Uso de paleta Dark Mode con acentos en Verde Neón (`#00FFA3`) para acciones positivas y Rojo (`#FF4B4B`) para detenciones.
- **Sincronización**: El cronómetro de enfoque debe alimentar automáticamente la duración de las tareas registradas.
- **Visualización de Datos**: 
  - El análisis de eficiencia diaria debe utilizar un código de colores basado en la dificultad promedio: Verde Oscuro (Baja) -> Verde Neón (Media) -> Ambar Eléctrico (Alta).
  - El Mapa de Calor de Productividad (Hourly Heatmap) debe representar el **Volumen de Enfoque** (suma de `real_hours`) con una escala de color: Azul Pizarra (`#1E293B`) -> Verde Bosque (`#065F46`) -> Verde Neón (`#00FFA3`), utilizando celdas separadas (gaps) para un acabado profesional.
