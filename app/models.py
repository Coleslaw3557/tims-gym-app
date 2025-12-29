from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    target_muscles = Column(String(200))
    image_url = Column(String(500))
    images = Column(JSON, default=list)  # Array of {url, caption} objects
    guide_url = Column(String(500))
    default_rest_sec = Column(Integer, default=90)
    gif_url = Column(String(500))  # URL to animated GIF demonstration
    form_notes = Column(Text)  # Detailed form instructions

    program_exercises = relationship("ProgramExercise", back_populates="exercise")
    set_logs = relationship("SetLog", back_populates="exercise")


class ProgramExercise(Base):
    __tablename__ = "program_exercises"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    day = Column(Integer, nullable=False)  # 1, 2, or 3
    sets = Column(Integer, nullable=False)
    reps_min = Column(Integer, nullable=False)
    reps_max = Column(Integer)  # nullable for fixed rep schemes
    rest_override = Column(Integer)  # override exercise default rest
    notes = Column(Text)
    sort_order = Column(Integer, default=0)

    exercise = relationship("Exercise", back_populates="program_exercises")


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    day_type = Column(Integer, nullable=False)  # 1, 2, or 3
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    notes = Column(Text)

    set_logs = relationship("SetLog", back_populates="session", cascade="all, delete-orphan")


class SetLog(Base):
    __tablename__ = "set_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    set_number = Column(Integer, nullable=False)
    weight = Column(Float)
    reps_completed = Column(Integer)
    rpe = Column(Float)  # Rate of Perceived Exertion (1-10)
    is_warmup = Column(Boolean, default=False)
    completed_at = Column(DateTime)

    session = relationship("WorkoutSession", back_populates="set_logs")
    exercise = relationship("Exercise", back_populates="set_logs")
