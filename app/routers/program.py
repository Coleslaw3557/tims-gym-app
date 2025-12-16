from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from database import get_db
from models import Exercise, ProgramExercise
from schemas import (
    ExerciseResponse,
    ProgramExerciseResponse,
    DayProgramResponse,
    FullProgramResponse,
)

router = APIRouter()

DAY_NAMES = {1: "Lower Body", 2: "Upper Push", 3: "Upper Pull"}


@router.get("", response_model=FullProgramResponse)
def get_full_program(db: Session = Depends(get_db)):
    """Get the full program structure with all days and exercises."""
    days = []
    for day_num in [1, 2, 3]:
        program_exercises = (
            db.query(ProgramExercise)
            .filter(ProgramExercise.day == day_num)
            .order_by(ProgramExercise.sort_order)
            .all()
        )
        days.append(
            DayProgramResponse(
                day=day_num,
                day_name=DAY_NAMES[day_num],
                exercises=program_exercises,
            )
        )
    return FullProgramResponse(days=days)


@router.get("/day/{day}", response_model=DayProgramResponse)
def get_day_program(day: int, db: Session = Depends(get_db)):
    """Get a single day's exercises."""
    if day not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Day must be 1, 2, or 3")

    program_exercises = (
        db.query(ProgramExercise)
        .filter(ProgramExercise.day == day)
        .order_by(ProgramExercise.sort_order)
        .all()
    )

    return DayProgramResponse(
        day=day,
        day_name=DAY_NAMES[day],
        exercises=program_exercises,
    )


@router.get("/exercises", response_model=List[ExerciseResponse])
def get_all_exercises(db: Session = Depends(get_db)):
    """Get all exercises in the database."""
    return db.query(Exercise).all()


@router.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    """Get a single exercise by ID."""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise
