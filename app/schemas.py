from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class ExerciseImage(BaseModel):
    url: str
    caption: Optional[str] = None


# Exercise schemas
class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_muscles: Optional[str] = None
    image_url: Optional[str] = None
    images: list[Any] = []
    guide_url: Optional[str] = None
    default_rest_sec: int = 90
    gif_url: Optional[str] = None
    form_notes: Optional[str] = None


class ExerciseResponse(ExerciseBase):
    id: int

    class Config:
        from_attributes = True


# Program Exercise schemas
class ProgramExerciseBase(BaseModel):
    exercise_id: int
    day: int
    sets: int
    reps_min: int
    reps_max: Optional[int] = None
    rest_override: Optional[int] = None
    notes: Optional[str] = None
    sort_order: int = 0


class ProgramExerciseResponse(ProgramExerciseBase):
    id: int
    exercise: ExerciseResponse

    class Config:
        from_attributes = True


class DayProgramResponse(BaseModel):
    day: int
    day_name: str
    exercises: list[ProgramExerciseResponse]


class FullProgramResponse(BaseModel):
    days: list[DayProgramResponse]


# Set Log schemas
class SetLogCreate(BaseModel):
    exercise_id: int
    set_number: int
    weight: Optional[float] = None
    reps_completed: Optional[int] = None
    rpe: Optional[float] = None
    is_warmup: bool = False


class SetLogUpdate(BaseModel):
    weight: Optional[float] = None
    reps_completed: Optional[int] = None
    rpe: Optional[float] = None
    is_warmup: Optional[bool] = None
    completed_at: Optional[datetime] = None


class SetLogResponse(BaseModel):
    id: int
    session_id: int
    exercise_id: int
    set_number: int
    weight: Optional[float] = None
    reps_completed: Optional[int] = None
    rpe: Optional[float] = None
    is_warmup: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Workout Session schemas
class SessionCreate(BaseModel):
    day_type: int
    notes: Optional[str] = None


class SessionUpdate(BaseModel):
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class SessionResponse(BaseModel):
    id: int
    date: datetime
    day_type: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class SessionDetailResponse(SessionResponse):
    set_logs: list[SetLogResponse]
    day_name: str


# History schemas
class ExerciseHistoryEntry(BaseModel):
    session_id: int
    date: datetime
    sets: list[SetLogResponse]
    max_weight: Optional[float] = None
    total_volume: Optional[float] = None


class ExerciseHistoryResponse(BaseModel):
    exercise: ExerciseResponse
    history: list[ExerciseHistoryEntry]
    current_pr: Optional[float] = None


# Stats schemas
class PREntry(BaseModel):
    exercise_id: int
    exercise_name: str
    weight: float
    reps: int
    date: datetime


class PRResponse(BaseModel):
    prs: list[PREntry]


# Previous weights for pre-filling
class PreviousWeights(BaseModel):
    exercise_id: int
    weights: list[Optional[float]]
