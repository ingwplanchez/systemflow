from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import projects, tasks, focus, settings

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SystemFlow API",
    description="Backend for Deep Work Analytics Platform",
    version="1.0.0"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, limit this to the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(focus.router, prefix="/focus-sessions", tags=["Focus Sessions"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])

@app.get("/")
async def root():
    return {"message": "SystemFlow API is online", "version": "1.0.0"}
