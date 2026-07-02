# SystemFlow ⚙️

**SystemFlow** es una plataforma de análisis de productividad diseñada para medir y optimizar el tiempo de trabajo profundo (*deep work*). El sistema registra sesiones de trabajo, calcula métricas de enfoque mediante lógica de negocio personalizada y visualiza tendencias mediante análisis de datos en tiempo real.

## 🛠️ Stack Tecnológico
- **Frontend:** Streamlit para la visualización de datos y el dashboard interactivo.
- **Backend:** FastAPI (Python) para la gestión de APIs y persistencia de datos.
- **Data Science:** Pandas y Plotly para el procesamiento, limpieza y análisis de tendencias.
- **Base de Datos:** SQLite para despliegue local sencillo.

## 📂 Estructura del Proyecto
La aplicación sigue una arquitectura modular basada en la separación de responsabilidades:

```text
systemflow/
├── app.py              # Punto de entrada principal de la aplicación
├── core/               # Lógica de negocio y procesamiento de datos
│   ├── state.py        # Gestión del estado de la sesión (Transicionando a API)
│   ├── etl.py          # Pipeline de limpieza y normalización de datos (Esquema ETL)
│   └── api_client.py   # Cliente singleton para comunicación con el Backend
├── ui/                 # Diseño y presentación de la interfaz
│   ├── styles.py       # Definiciones de CSS y estilos visuales
│   └── layout.py       # Estructura de la página, sidebar y componentes del dashboard
├── backend/            # API REST y persistencia de datos
│   ├── main.py         # Punto de entrada de FastAPI y CORS
│   ├── database.py     # Configuración de SQLAlchemy y sesión de DB
│   ├── models.py       # Modelos ORM (Project, Task, FocusSession, UserSettings)
│   ├── schemas.py      # Modelos de validación Pydantic
│   ├── crud.py         # Lógica de acceso a datos (Create, Read, Update, Delete)
│   └── api/            # Definiciones de rutas por entidad
│       ├── projects.py # Endpoints de gestión de proyectos
│       ├── tasks.py    # Endpoints de gestión de tareas
│       ├── focus.py    # Ciclo de vida de sesiones de enfoque
│       └── settings.py # Gestión de preferencias de usuario
├── data_analysis/      # Motor de cálculo de métricas y Focus Score (Sprints futuros)
└── requirements.txt    # Dependencias del proyecto
```

## 🚀 Ejecución Local (IMPORTANTE)

Debido a la arquitectura desacoplada, **debes ejecutar el Backend y el Frontend simultáneamente en dos terminales separadas**.

### Paso 1: Lanzar el Backend (API)
Abre una terminal y ejecuta:
```bash
uvicorn backend.main:app --reload
```
*El servidor debe quedar corriendo en `http://localhost:8000`. No cierres esta terminal.*

### Paso 2: Lanzar el Dashboard (Frontend)
Abre una **segunda terminal** y ejecuta:
```bash
streamlit run app.py
```

## 📅 Hoja de Ruta (Roadmap)
El desarrollo está dividido en sprints técnicos para asegurar la escalabilidad:

### Sprint 1: Backend & Persistencia (En Progreso)
- [x] Implementación de FastAPI y estructura modular.
- [x] Definición de modelos de datos con SQLAlchemy (Sincronizados con `DATA_SCHEMA.md`).
- [x] Creación de endpoints CRUD para Proyectos, Tareas y Preferencias.
- [x] Lógica de ciclo de vida de Sesiones de Enfoque (Backend-owned).
- [ ] Integración total del frontend con la API mediante `APIClient`.

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
- **Lógica de Indicadores (KPIs)**:
  - **Focus Score**: Cálculo basado en la precisión de estimación (Diferencia entre `est_hours` y `real_hours`).
  - **Ciclos Completados**: Conteo de tareas `completed` del día actual frente a una meta configurable en el Sidebar.
  - **Tiempo Total**: Suma de `real_hours` del proyecto, con indicador de progreso diario.
  - **Eficiencia Promedio**: Ratio de rendimiento ($\frac{\sum \text{est\_hours}}{\sum \text{real\_hours}}$) capado al 120%.
- **Configuraciones de Usuario**:
  - **Meta Diaria**: Control ajustable en la interfaz para definir el objetivo de bloques diarios (predeterminado: 4 bloques/estilo Pomodoro).
