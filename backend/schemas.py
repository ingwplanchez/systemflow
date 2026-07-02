from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# ---------- Enums (Matching models) ----------

class Category(str, Enum):
    DEEP_WORK = "deep_work"
    COLLABORATION = "collaboration"
    REACTIVE = "reactive"
    STRATEGY = "strategy"

class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Status(str, Enum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"

# ---------- Project Schemas ----------

class ProjectBase(BaseModel):
    name: str = Field(..., max_length=120)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=16)

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------- Task Schemas ----------

class TaskBase(BaseModel):
    timestamp: datetime
    task_id: str = Field(..., max_length=64)
    project_id: int
    category: Category
    priority: Priority
    est_hours: float = Field(..., ge=0)
    real_hours: float = Field(..., ge=0)
    difficulty: int = Field(..., ge=1, le=5)
    status: Status
    module_task: Optional[str] = Field(None, max_length=255)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    timestamp: Optional[datetime] = None
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    est_hours: Optional[float] = Field(None, ge=0)
    real_hours: Optional[float] = Field(None, ge=0)
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[Status] = None
    module_task: Optional[str] = None

class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------- Focus Session Schemas ----------

class FocusSessionBase(BaseModel):
    project_id: int

class FocusSessionCreate(FocusSessionBase):
    pass

class FocusSession(BaseModel):
    id: int
    project_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    real_hours: Optional[float] = None
    cancelled: bool

    model_config = ConfigDict(from_attributes=True)

# ---------- User Settings Schemas ----------

class UserSettingsBase(BaseModel):
    daily_goal: int = Field(..., ge=1, le=20)

class UserSettingsUpdate(UserSettingsBase):
    pass

class UserSettings(UserSettingsBase):
    id: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------- Analytics Schemas ----------

class KPIResponse(BaseModel):
    focus_score: int
    ciclos_hoy: int
    total_horas: float
    horas_hoy: float
    eficiencia: int
