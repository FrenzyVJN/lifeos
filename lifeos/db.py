from sqlalchemy import create_engine
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
