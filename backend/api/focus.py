from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.FocusSession, status_code=201)
def start_session(session_data: schemas.FocusSessionCreate, db: Session = Depends(get_db)):
    return crud.create_focus_session(db, session_data)

@router.get("/active", response_model=schemas.FocusSession)
def get_active_session(db: Session = Depends(get_db)):
    active_session = crud.get_active_session(db)
    if not active_session:
        raise HTTPException(status_code=404, detail="No active session found")
    return active_session

@router.patch("/{session_id}/stop", response_model=schemas.FocusSession)
def stop_session(session_id: int, db: Session = Depends(get_db)):
    updated_session = crud.stop_focus_session(db, session_id)
    if not updated_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return updated_session

@router.delete("/{session_id}", status_code=204)
def cancel_session(session_id: int, db: Session = Depends(get_db)):
    from ..models import FocusSession
    session = db.query(FocusSession).filter(FocusSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.cancelled = True
    session.ended_at = None # Effectively cancel
    db.commit()
    return None
