from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas

router = APIRouter()

@router.get("/", response_model=schemas.UserSettings)
def read_settings(db: Session = Depends(get_db)):
    return crud.get_settings(db)

@router.put("/", response_model=schemas.UserSettings)
def update_settings(settings: schemas.UserSettingsUpdate, db: Session = Depends(get_db)):
    return crud.update_settings(db, settings)
