import pytest
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lifeos.models import Base, Task, Project, TimelineEntry, MoodEntry

@pytest.fixture(scope="function")
def fresh_db():
    """Create a fresh in-memory database for each test."""
    # Create in-memory SQLite engine
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    # Create session factory
    TestSessionLocal = sessionmaker(bind=engine)

    # Patch the lifeos.db module's globals
    import lifeos.db as db_module
    original_engine = db_module.ENGINE
    original_session = db_module.SessionLocal

    db_module.ENGINE = engine
    db_module.SessionLocal = TestSessionLocal

    # Also patch get_session to return our test session
    original_get_session = db_module.get_session

    def test_get_session():
        return TestSessionLocal()

    db_module.get_session = test_get_session

    yield engine

    # Restore originals
    db_module.ENGINE = original_engine
    db_module.SessionLocal = original_session
    db_module.get_session = original_get_session

@pytest.fixture
def session(fresh_db):
    """Get a session for the test database."""
    from sqlalchemy.orm import sessionmaker
    TestSessionLocal = sessionmaker(bind=fresh_db)
    sess = TestSessionLocal()
    yield sess
    sess.close()
