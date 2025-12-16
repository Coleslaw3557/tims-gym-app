from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import List, Optional

from database import get_db
from models import WorkoutSession, SetLog, ProgramExercise
from schemas import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionDetailResponse,
    SetLogCreate,
    SetLogUpdate,
    SetLogResponse,
    PreviousWeights,
)

router = APIRouter()

DAY_NAMES = {1: "Lower Body", 2: "Upper Push", 3: "Upper Pull"}


@router.get("", response_model=List[SessionResponse])
def get_sessions(
    limit: int = 20,
    offset: int = 0,
    day_type: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List past sessions, optionally filtered by day type."""
    query = db.query(WorkoutSession).order_by(desc(WorkoutSession.date))
    if day_type:
        query = query.filter(WorkoutSession.day_type == day_type)
    return query.offset(offset).limit(limit).all()


@router.get("/active", response_model=Optional[SessionDetailResponse])
def get_active_session(db: Session = Depends(get_db)):
    """Get the current active (uncompleted) session if one exists."""
    session = (
        db.query(WorkoutSession)
        .filter(WorkoutSession.completed_at.is_(None))
        .order_by(desc(WorkoutSession.started_at))
        .first()
    )
    if not session:
        return None
    return SessionDetailResponse(
        id=session.id,
        date=session.date,
        day_type=session.day_type,
        started_at=session.started_at,
        completed_at=session.completed_at,
        notes=session.notes,
        set_logs=session.set_logs,
        day_name=DAY_NAMES[session.day_type],
    )


@router.post("", response_model=SessionDetailResponse)
def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    """Start a new workout session."""
    if session_data.day_type not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Day type must be 1, 2, or 3")

    # Check for existing active session
    active = (
        db.query(WorkoutSession)
        .filter(WorkoutSession.completed_at.is_(None))
        .first()
    )
    if active:
        raise HTTPException(
            status_code=400,
            detail="An active session already exists. Complete or delete it first.",
        )

    session = WorkoutSession(
        day_type=session_data.day_type,
        notes=session_data.notes,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionDetailResponse(
        id=session.id,
        date=session.date,
        day_type=session.day_type,
        started_at=session.started_at,
        completed_at=session.completed_at,
        notes=session.notes,
        set_logs=[],
        day_name=DAY_NAMES[session.day_type],
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific session with all set logs."""
    session = db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionDetailResponse(
        id=session.id,
        date=session.date,
        day_type=session.day_type,
        started_at=session.started_at,
        completed_at=session.completed_at,
        notes=session.notes,
        set_logs=session.set_logs,
        day_name=DAY_NAMES[session.day_type],
    )


@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db: Session = Depends(get_db),
):
    """Update a session (e.g., complete it or add notes)."""
    session = db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session_data.notes is not None:
        session.notes = session_data.notes
    if session_data.completed_at is not None:
        session.completed_at = session_data.completed_at

    db.commit()
    db.refresh(session)
    return session


@router.post("/{session_id}/complete", response_model=SessionResponse)
def complete_session(session_id: int, db: Session = Depends(get_db)):
    """Mark a session as completed."""
    session = db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a session and all its set logs."""
    session = db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()
    return {"message": "Session deleted"}


# Set logs
@router.post("/{session_id}/sets", response_model=SetLogResponse)
def log_set(
    session_id: int,
    set_data: SetLogCreate,
    db: Session = Depends(get_db),
):
    """Log a set for a session."""
    session = db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    set_log = SetLog(
        session_id=session_id,
        exercise_id=set_data.exercise_id,
        set_number=set_data.set_number,
        weight=set_data.weight,
        reps_completed=set_data.reps_completed,
        rpe=set_data.rpe,
        is_warmup=set_data.is_warmup,
        completed_at=datetime.utcnow(),
    )
    db.add(set_log)
    db.commit()
    db.refresh(set_log)
    return set_log


@router.patch("/{session_id}/sets/{set_id}", response_model=SetLogResponse)
def update_set(
    session_id: int,
    set_id: int,
    set_data: SetLogUpdate,
    db: Session = Depends(get_db),
):
    """Update a logged set."""
    set_log = (
        db.query(SetLog)
        .filter(SetLog.id == set_id, SetLog.session_id == session_id)
        .first()
    )
    if not set_log:
        raise HTTPException(status_code=404, detail="Set not found")

    if set_data.weight is not None:
        set_log.weight = set_data.weight
    if set_data.reps_completed is not None:
        set_log.reps_completed = set_data.reps_completed
    if set_data.rpe is not None:
        set_log.rpe = set_data.rpe
    if set_data.is_warmup is not None:
        set_log.is_warmup = set_data.is_warmup
    if set_data.completed_at is not None:
        set_log.completed_at = set_data.completed_at

    db.commit()
    db.refresh(set_log)
    return set_log


@router.delete("/{session_id}/sets/{set_id}")
def delete_set(session_id: int, set_id: int, db: Session = Depends(get_db)):
    """Delete a logged set."""
    set_log = (
        db.query(SetLog)
        .filter(SetLog.id == set_id, SetLog.session_id == session_id)
        .first()
    )
    if not set_log:
        raise HTTPException(status_code=404, detail="Set not found")

    db.delete(set_log)
    db.commit()
    return {"message": "Set deleted"}


@router.get("/{session_id}/previous-weights", response_model=List[PreviousWeights])
def get_previous_weights(session_id: int, db: Session = Depends(get_db)):
    """Get the weights used in the previous session for the same day type."""
    session = db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Find the most recent completed session of the same day type
    prev_session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.day_type == session.day_type,
            WorkoutSession.completed_at.isnot(None),
            WorkoutSession.id != session_id,
        )
        .order_by(desc(WorkoutSession.date))
        .first()
    )

    if not prev_session:
        return []

    # Get exercises for this day
    program_exercises = (
        db.query(ProgramExercise)
        .filter(ProgramExercise.day == session.day_type)
        .order_by(ProgramExercise.sort_order)
        .all()
    )

    result = []
    for pe in program_exercises:
        # Get sets from previous session for this exercise
        sets = (
            db.query(SetLog)
            .filter(
                SetLog.session_id == prev_session.id,
                SetLog.exercise_id == pe.exercise_id,
                SetLog.is_warmup == False,
            )
            .order_by(SetLog.set_number)
            .all()
        )
        weights = [s.weight for s in sets]
        result.append(PreviousWeights(exercise_id=pe.exercise_id, weights=weights))

    return result
