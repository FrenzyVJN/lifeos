from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    normalized_name = Column(String, nullable=False)
    last_active = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="active")

class TimelineEntry(Base):
    __tablename__ = "timeline_entries"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    normalized_title = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")
    priority = Column(String, default="medium")
    recurrence = Column(String, nullable=True)  # daily, weekly, weekday, weekend
    next_due = Column(DateTime, nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class MoodEntry(Base):
    __tablename__ = "mood_entries"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mood = Column(String, nullable=False)
    score = Column(Integer, nullable=False)  # 1-5
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
