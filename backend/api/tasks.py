from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from ..database import get_db
from .. import crud, schemas

router = APIRouter()

@router.get("/", response_model=List[Any])
def read_tasks(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_tasks(db, project_id=project_id, status=status)

@router.post("/", response_model=schemas.Task, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)

@router.post("/bulk", status_code=201)
def create_tasks_bulk(payload: schemas.TaskBulkCreate, db: Session = Depends(get_db)):
    return crud.create_tasks_bulk(db, payload.tasks)

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    if not crud.delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return None

@router.delete("/", status_code=204)
def delete_all_tasks(db: Session = Depends(get_db)):
    crud.delete_all_tasks(db)
    return None

@router.patch("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, updates: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.update_task(db, task_id, updates)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    from ..models import Task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
