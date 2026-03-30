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
    columns = [c["name"] for c in inspector.get_columns("tasks")]
    if "project_id" not in columns:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN project_id TEXT"))
            conn.commit()
