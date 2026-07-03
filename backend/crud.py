from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List
from . import models, schemas

# ---------- Project CRUD ----------

def get_projects(db: Session):
    return db.query(models.Project).all()

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        name=project.name,
        description=project.description,
        color=project.color
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# ---------- Task CRUD ----------

def get_tasks(db: Session, project_id: Optional[int] = None, status: Optional[str] = None):
    query = db.query(models.Task, models.Project.name.label("project_name")).join(models.Project)
    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    if status:
        query = query.filter(models.Task.status == status)

    results = query.all()
    tasks_list = []
    for task, project_name in results:
        # We manually build the dict to avoid SQLAlchemy internal state
        task_dict = {
            "id": task.id,
            "timestamp": task.timestamp,
            "task_id": task.task_id,
            "project_id": task.project_id,
            "project": project_name,
            "category": task.category.value if hasattr(task.category, 'value') else task.category,
            "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
            "est_hours": task.est_hours,
            "real_hours": task.real_hours,
            "difficulty": task.difficulty,
            "status": task.status.value if hasattr(task.status, 'value') else task.status,
            "module_task": task.module_task,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }
        tasks_list.append(task_dict)
    return tasks_list

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, updates: schemas.TaskUpdate):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

def delete_all_tasks(db: Session):
    db.query(models.Task).delete()
    db.commit()
    return True

def create_tasks_bulk(db: Session, tasks_data: List[schemas.TaskCreate]):
    created_tasks = []
    for task_in in tasks_data:
        db_task = models.Task(**task_in.model_dump())
        db.add(db_task)
        created_tasks.append(db_task)
    db.commit()
    for task in created_tasks:
        db.refresh(task)
    return created_tasks

# ---------- Focus Session CRUD ----------

def create_focus_session(db: Session, session_data: schemas.FocusSessionCreate):
    db_session = models.FocusSession(project_id=session_data.project_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_active_session(db: Session):
    return db.query(models.FocusSession).filter(
        models.FocusSession.ended_at == None,
        models.FocusSession.cancelled == False
    ).first()

def stop_focus_session(db: Session, session_id: int):
    db_session = db.query(models.FocusSession).filter(models.FocusSession.id == session_id).first()
    if db_session:
        now = datetime.utcnow()
        db_session.ended_at = now

        # Calculate real hours
        duration = (db_session.ended_at - db_session.started_at).total_seconds() / 3600
        db_session.real_hours = duration

        # Auto-create a task if it's a productive session
        # This matches the "Sesión de Enfoque Automática" logic in layout.py
        new_task = models.Task(
            timestamp=now,
            task_id=f"SESS-{now.strftime('%Y%m%d%H%M')}",
            project_id=db_session.project_id,
            category=models.Category.DEEP_WORK,
            priority=models.Priority.MEDIUM,
            est_hours=duration,
            real_hours=duration,
            difficulty=3,
            status=models.Status.COMPLETED,
            module_task="Sesión de Enfoque Automática",
            source_session_id=db_session.id
        )
        db.add(new_task)
        db.commit()
        db.refresh(db_session)
    return db_session

# ---------- Settings CRUD ----------

def get_settings(db: Session):
    setting = db.query(models.UserSettings).first()
    if not setting:
        setting = models.UserSettings(daily_goal=4)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting

def update_settings(db: Session, settings_data: schemas.UserSettingsUpdate):
    db_setting = db.query(models.UserSettings).first()
    if not db_setting:
        db_setting = models.UserSettings(id=1)

    db_setting.daily_goal = settings_data.daily_goal
    db.commit()
    db.refresh(db_setting)
    return db_setting
