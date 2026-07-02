from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, DateTime, ForeignKey, Enum as SAEnum, Text, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

# ---------- Enums (Strictly following DATA_SCHEMA.md) ----------

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

# ---------- Models ----------

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks: Mapped[List["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    focus_sessions: Mapped[List["FocusSession"]] = relationship(back_populates="project")

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Canonical columns from DATA_SCHEMA.md
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    task_id:   Mapped[str]       = mapped_column(String(64), nullable=False, index=True)
    project_id: Mapped[int]      = mapped_column(ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True)
    category:  Mapped[Category]  = mapped_column(SAEnum(Category), nullable=False)
    priority:  Mapped[Priority]  = mapped_column(SAEnum(Priority), nullable=False)
    est_hours: Mapped[float]     = mapped_column(Float, nullable=False)
    real_hours: Mapped[float]    = mapped_column(Float, nullable=False)
    difficulty: Mapped[int]      = mapped_column(Integer, nullable=False)
    status:    Mapped[Status]    = mapped_column(SAEnum(Status), nullable=False, index=True)

    # UI Extension: human-readable label
    module_task: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Session Link
    source_session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("focus_sessions.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="tasks")
    source_session: Mapped[Optional["FocusSession"]] = relationship(back_populates="tasks")

    __table_args__ = (
        UniqueConstraint("task_id", name="uq_tasks_task_id"),
        CheckConstraint("est_hours >= 0", name="check_est_hours_positive"),
        CheckConstraint("real_hours >= 0", name="check_real_hours_positive"),
        CheckConstraint("difficulty >= 1 AND difficulty <= 5", name="check_difficulty_range"),
        Index("ix_tasks_project_timestamp", "project_id", "timestamp"),
    )

class FocusSession(Base):
    __tablename__ = "focus_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at:   Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    real_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cancelled: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Linked task if session converted to task
    task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="focus_sessions")
    tasks:   Mapped[List["Task"]] = relationship(back_populates="source_session")

class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    daily_goal: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("daily_goal >= 1 AND daily_goal <= 20", name="check_daily_goal_range"),
    )
