from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from .models import Task, TimelineEntry
from .parser import extract_tasks
from .db import get_session

STOPWORDS = {"a", "an", "the", "to", "for", "in", "on", "at", "my", "i"}

def normalize(text: str) -> str:
    tokens = text.lower().split()
    return " ".join(t for t in tokens if t not in STOPWORDS)

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def find_duplicate(session: Session, normalized_title: str) -> Task | None:
    tasks = session.query(Task).filter(Task.status == "pending").all()
    for task in tasks:
        if similarity(task.normalized_title, normalized_title) > 0.8:
            return task
    return None

def log_input(user_input: str) -> tuple[TimelineEntry, list[dict]]:
    session = get_session()
    session.expire_on_commit = False
    entry = TimelineEntry(content=user_input)
    session.add(entry)
    session.commit()

    tasks_data = extract_tasks(user_input)
    task_results = []

    for task_data in tasks_data:
        norm_title = normalize(task_data["title"])
        existing = find_duplicate(session, norm_title)
        if existing:
            if task_data["due_date"]:
                existing.due_date = task_data["due_date"]
            from datetime import datetime
            existing.updated_at = datetime.utcnow()
            session.commit()
            task_results.append({"task": existing, "action": "updated"})
        else:
            new_task = Task(
                title=task_data["title"],
                normalized_title=norm_title,
                due_date=task_data["due_date"],
                status="pending"
            )
            session.add(new_task)
            session.commit()
            task_results.append({"task": new_task, "action": "created"})

    session.expunge_all()
    session.close()
    return entry, task_results

def get_pending_tasks() -> list[Task]:
    session = get_session()
    session.expire_on_commit = False
    tasks = session.query(Task).filter(Task.status == "pending").order_by(Task.created_at.desc()).all()
    session.expunge_all()
    session.close()
    return tasks

def get_done_tasks() -> list[Task]:
    session = get_session()
    session.expire_on_commit = False
    tasks = session.query(Task).filter(Task.status == "done").order_by(Task.updated_at.desc()).all()
    session.expunge_all()
    session.close()
    return tasks

def mark_task_done(task_id: str) -> Task | None:
    session = get_session()
    session.expire_on_commit = False
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        from datetime import datetime
        task.status = "done"
        task.updated_at = datetime.utcnow()
        session.commit()
    session.expunge(task) if task else None
    session.close()
    return task

def get_timeline() -> list[TimelineEntry]:
    session = get_session()
    session.expire_on_commit = False
    entries = session.query(TimelineEntry).order_by(TimelineEntry.timestamp.desc()).all()
    session.expunge_all()
    session.close()
    return entries