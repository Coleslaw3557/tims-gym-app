from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List

from database import get_db
from models import Exercise, SetLog, WorkoutSession
from schemas import (
    ExerciseHistoryResponse,
    ExerciseHistoryEntry,
    ExerciseResponse,
    SetLogResponse,
    PREntry,
    PRResponse,
)

router = APIRouter()


@router.get("/exercises/{exercise_id}/history", response_model=ExerciseHistoryResponse)
def get_exercise_history(
    exercise_id: int,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Get historical data for a specific exercise."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # Get all sessions that have this exercise
    sessions_with_exercise = (
        db.query(WorkoutSession)
        .join(SetLog)
        .filter(
            SetLog.exercise_id == exercise_id,
            WorkoutSession.completed_at.isnot(None),
        )
        .distinct()
        .order_by(desc(WorkoutSession.date))
        .limit(limit)
        .all()
    )

    history = []
    current_pr = None

    for session in sessions_with_exercise:
        sets = (
            db.query(SetLog)
            .filter(
                SetLog.session_id == session.id,
                SetLog.exercise_id == exercise_id,
                SetLog.is_warmup == False,
            )
            .order_by(SetLog.set_number)
            .all()
        )

        if not sets:
            continue

        # Calculate max weight and total volume for this session
        weights = [s.weight for s in sets if s.weight]
        max_weight = max(weights) if weights else None

        total_volume = sum(
            (s.weight or 0) * (s.reps_completed or 0)
            for s in sets
            if not s.is_warmup
        )

        # Track PR
        if max_weight and (current_pr is None or max_weight > current_pr):
            current_pr = max_weight

        history.append(
            ExerciseHistoryEntry(
                session_id=session.id,
                date=session.date,
                sets=sets,
                max_weight=max_weight,
                total_volume=total_volume if total_volume > 0 else None,
            )
        )

    return ExerciseHistoryResponse(
        exercise=exercise,
        history=history,
        current_pr=current_pr,
    )


@router.get("/stats/prs", response_model=PRResponse)
def get_prs(db: Session = Depends(get_db)):
    """Get current PRs for all exercises."""
    exercises = db.query(Exercise).all()
    prs = []

    for exercise in exercises:
        # Get the heaviest non-warmup set for this exercise
        best_set = (
            db.query(SetLog)
            .join(WorkoutSession)
            .filter(
                SetLog.exercise_id == exercise.id,
                SetLog.is_warmup == False,
                SetLog.weight.isnot(None),
                WorkoutSession.completed_at.isnot(None),
            )
            .order_by(desc(SetLog.weight))
            .first()
        )

        if best_set and best_set.weight:
            session = (
                db.query(WorkoutSession)
                .filter(WorkoutSession.id == best_set.session_id)
                .first()
            )
            prs.append(
                PREntry(
                    exercise_id=exercise.id,
                    exercise_name=exercise.name,
                    weight=best_set.weight,
                    reps=best_set.reps_completed or 0,
                    date=session.date,
                )
            )

    # Sort by exercise name
    prs.sort(key=lambda x: x.exercise_name)
    return PRResponse(prs=prs)


@router.get("/stats/volume")
def get_volume_stats(
    days: int = 30,
    db: Session = Depends(get_db),
):
    """Get volume statistics over time."""
    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(days=days)

    sessions = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.completed_at.isnot(None),
            WorkoutSession.date >= cutoff,
        )
        .order_by(WorkoutSession.date)
        .all()
    )

    result = []
    for session in sessions:
        sets = (
            db.query(SetLog)
            .filter(SetLog.session_id == session.id, SetLog.is_warmup == False)
            .all()
        )

        total_volume = sum(
            (s.weight or 0) * (s.reps_completed or 0) for s in sets
        )

        result.append({
            "date": session.date.isoformat(),
            "day_type": session.day_type,
            "total_volume": total_volume,
            "total_sets": len(sets),
        })

    return {"stats": result}
