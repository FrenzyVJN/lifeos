from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from .models import Task, TimelineEntry, Project
from .parser import extract_tasks, call_ollama, resolve_date
from .db import get_session
from datetime import datetime, timedelta

SYNONYMS = {
    "exam": "test",
    "assessment": "test",
    "assignment": "task",
    "homework": "task",
    "project": "task",
    "meeting": "meet",
    "call": "meet",
    "check": "review",
    "look": "review",
}

STOPWORDS = {"a", "an", "the", "to", "for", "in", "on", "at", "my", "i", "and"}

def normalize(text: str) -> str:
    tokens = text.lower().split()
    tokens = [SYNONYMS.get(t, t) for t in tokens]
    return " ".join(t for t in tokens if t not in STOPWORDS)

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def find_duplicate(session: Session, normalized_title: str) -> Task | None:
    tasks = session.query(Task).filter(Task.status == "pending").all()
    for task in tasks:
        if similarity(task.normalized_title, normalized_title) > 0.8:
            return task
    return None

def find_duplicate_project(session: Session, normalized_name: str) -> Project | None:
    projects = session.query(Project).all()
    for project in projects:
        if similarity(project.normalized_name, normalized_name) > 0.75:
            return project
    return None

def log_input(user_input: str) -> tuple[TimelineEntry, list[dict]]:
    session = get_session()
    session.expire_on_commit = False
    entry = TimelineEntry(content=user_input)
    session.add(entry)
    session.commit()

    # Parse with LLM (now returns tasks + project)
    parsed = call_ollama(user_input)
    tasks_data = parsed.get("tasks", [])
    if not tasks_data:
        tasks_data = []

    project_name = parsed.get("project")
    project = None

    # Handle project
    if project_name:
        norm_project_name = normalize(project_name)
        project = find_duplicate_project(session, norm_project_name)
        if project:
            project.last_active = datetime.utcnow()
            session.commit()
        else:
            project = Project(
                name=project_name,
                normalized_name=norm_project_name,
                last_active=datetime.utcnow()
            )
            session.add(project)
            session.commit()

    task_results = []

    for task_data in tasks_data:
        norm_title = normalize(task_data["title"])
        existing = find_duplicate(session, norm_title)
        parsed_due_date = resolve_date(task_data.get("due_date"))
        if existing:
            if parsed_due_date:
                existing.due_date = parsed_due_date
            existing.updated_at = datetime.utcnow()
            if project and not existing.project_id:
                existing.project_id = project.id
            session.commit()
            task_results.append({"task": existing, "action": "updated"})
        else:
            new_task = Task(
                title=task_data["title"],
                normalized_title=norm_title,
                due_date=parsed_due_date,
                status="pending",
                project_id=project.id if project else None
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

def get_all_projects() -> list[Project]:
    session = get_session()
    session.expire_on_commit = False
    projects = session.query(Project).order_by(Project.last_active.desc()).all()
    session.expunge_all()
    session.close()
    return projects

def get_project_tasks(project_id: str) -> tuple[Project | None, list[Task]]:
    session = get_session()
    session.expire_on_commit = False
    project = session.query(Project).filter(Project.id == project_id).first()
    if not project:
        session.close()
        return None, []
    tasks = session.query(Task).filter(
        Task.project_id == project_id,
        Task.status == "pending"
    ).order_by(Task.created_at.desc()).all()
    session.expunge_all()
    session.close()
    return project, tasks

def get_daily_summary() -> dict:
    session = get_session()
    session.expire_on_commit = False

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    # Timeline entries today
    timeline_today = session.query(TimelineEntry).filter(
        TimelineEntry.timestamp >= today,
        TimelineEntry.timestamp < tomorrow
    ).order_by(TimelineEntry.timestamp.asc()).all()

    # Tasks created today
    tasks_created = session.query(Task).filter(
        Task.created_at >= today,
        Task.created_at < tomorrow
    ).all()

    # Projects active today
    projects_today = session.query(Project).filter(
        Project.last_active >= today
    ).all()

    session.expunge_all()
    session.close()

    return {
        "timeline": timeline_today,
        "tasks_created": tasks_created,
        "projects": projects_today,
        "date": datetime.utcnow()
    }
