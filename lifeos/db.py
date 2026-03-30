from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path

ENGINE = None
SessionLocal = None

def init_db(db_path: str = "~/.lifeos/lifeos.db") -> None:
    global ENGINE, SessionLocal
    resolved = Path(db_path).expanduser()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    ENGINE = create_engine(f"sqlite:///{resolved}", echo=False)
    SessionLocal = sessionmaker(bind=ENGINE)

def get_session() -> Session:
    if SessionLocal is None:
        init_db()
    return SessionLocal()

def run_migrations(engine):
    inspector = inspect(engine)

    # Migrate tasks table
    task_cols = [c["name"] for c in inspector.get_columns("tasks")]
    with engine.connect() as conn:
        if "project_id" not in task_cols:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN project_id TEXT"))
        if "priority" not in task_cols:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'medium'"))
        if "recurrence" not in task_cols:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN recurrence TEXT"))
        if "next_due" not in task_cols:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN next_due DATETIME"))
        conn.commit()

    # Migrate projects table
    project_cols = [c["name"] for c in inspector.get_columns("projects")]
    with engine.connect() as conn:
        if "status" not in project_cols:
            conn.execute(text("ALTER TABLE projects ADD COLUMN status TEXT DEFAULT 'active'"))
        conn.commit()

    # Create mood_entries table if not exists
    table_names = inspector.get_table_names()
    if "mood_entries" not in table_names:
        from .models import Base, MoodEntry
        Base.metadata.create_all(engine, tables=[MoodEntry.__table__])
