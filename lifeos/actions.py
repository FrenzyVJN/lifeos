from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Task, TimelineEntry, Project
from .parser import extract_tasks, call_ollama, call_ollama_text, resolve_date
from .db import get_session
from datetime import datetime, timedelta

# Embeddings model (lazy loaded, cached)
_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embedding_similarity(a: str, b: str) -> float:
    import numpy as np
    model = get_model()
    embeddings = model.encode([a, b])
    cos_sim = np.dot(embeddings[0], embeddings[1]) / (
        np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
    )
    return float(cos_sim)

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
SIMILARITY_THRESHOLD = 0.82

def normalize(text: str) -> str:
    tokens = text.lower().split()
    tokens = [SYNONYMS.get(t, t) for t in tokens]
    return " ".join(t for t in tokens if t not in STOPWORDS)

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def find_duplicate_task(session: Session, title: str) -> Task | None:
    tasks = session.query(Task).filter(Task.status == "pending").all()
    best_match = None
    best_score = 0
    for task in tasks:
        score = embedding_similarity(title, task.normalized_title)
        if score > SIMILARITY_THRESHOLD and score > best_score:
            best_match = task
            best_score = score
    return best_match

def find_duplicate_project(session: Session, name: str) -> Project | None:
    projects = session.query(Project).all()
    best_match = None
    best_score = 0
    for project in projects:
        score = embedding_similarity(name, project.normalized_name)
        if score > SIMILARITY_THRESHOLD and score > best_score:
            best_match = project
            best_score = score
    return best_match

def log_input(user_input: str) -> tuple[TimelineEntry, list[dict]]:
    session = get_session()
    session.expire_on_commit = False
    entry = TimelineEntry(content=user_input)
    session.add(entry)
    session.commit()

    # Parse with LLM (returns tasks + project)
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
        existing = find_duplicate_task(session, norm_title)
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

    # Tasks completed today
    tasks_done = session.query(Task).filter(
        Task.status == "done",
        Task.updated_at >= today,
        Task.updated_at < tomorrow
    ).all()

    # Projects active today
    projects_today = session.query(Project).filter(
        Project.last_active >= today
    ).all()

    # Streak
    streak = get_streak_internal(session)

    session.expunge_all()
    session.close()

    return {
        "timeline": timeline_today,
        "tasks_created": tasks_created,
        "tasks_done": tasks_done,
        "projects": projects_today,
        "streak": streak,
        "date": datetime.utcnow()
    }

def get_streak_internal(session: Session) -> int:
    entries = session.query(TimelineEntry).order_by(
        TimelineEntry.timestamp.desc()
    ).all()

    if not entries:
        return 0

    dates = sorted(set([e.timestamp.date() for e in entries]), reverse=True)
    streak = 0
    today = datetime.utcnow().date()

    for i, date in enumerate(dates):
        expected = today - timedelta(days=i)
        if date == expected:
            streak += 1
        else:
            break

    return streak

def get_streak() -> int:
    session = get_session()
    session.expire_on_commit = False
    streak = get_streak_internal(session)
    session.close()
    return streak

def search(query: str, top_k: int = 5) -> list[tuple]:
    session = get_session()
    session.expire_on_commit = False

    results = []

    # Search tasks
    tasks = session.query(Task).filter(Task.status != "deleted").all()
    for task in tasks:
        score = embedding_similarity(query, task.normalized_title)
        if score > 0.5:
            results.append(("task", task, score))

    # Search timeline
    entries = session.query(TimelineEntry).all()
    for entry in entries:
        score = embedding_similarity(query, entry.content)
        if score > 0.5:
            results.append(("timeline", entry, score))

    # Sort by score, return top_k
    results.sort(key=lambda x: x[2], reverse=True)
    results = results[:top_k]

    session.expunge_all()
    session.close()
    return results

def generate_digest() -> str:
    session = get_session()
    session.expire_on_commit = False

    today = datetime.utcnow().date()

    # Pull today's data
    entries = session.query(TimelineEntry).filter(
        func.date(TimelineEntry.timestamp) == today
    ).all()

    tasks_created = session.query(Task).filter(
        func.date(Task.created_at) == today
    ).all()

    tasks_done = session.query(Task).filter(
        Task.status == "done",
        func.date(Task.updated_at) == today
    ).all()

    # Build context for LLM
    context = f"""Timeline entries today:
{chr(10).join([e.content for e in entries])}

Tasks created today:
{chr(10).join([t.title for t in tasks_created])}

Tasks completed today:
{chr(10).join([t.title for t in tasks_done])}
"""

    prompt = f"""Based on this person's activity log, write a brief, friendly daily digest.
2-3 sentences max. Be specific. Mention what they worked on and what they completed.
If nothing happened, say so honestly.

Activity data:
{context}

Respond only with the digest text. No preamble.
"""

    session.expunge_all()
    session.close()

    # Call Ollama for digest
    return call_ollama_text(prompt)

def get_weekly_summary() -> dict:
    session = get_session()
    session.expire_on_commit = False

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)

    # Timeline entries this week
    timeline_week = session.query(TimelineEntry).filter(
        TimelineEntry.timestamp >= week_ago
    ).all()

    # Tasks created this week
    tasks_created = session.query(Task).filter(
        Task.created_at >= week_ago
    ).all()

    # Tasks completed this week
    tasks_done = session.query(Task).filter(
        Task.status == "done",
        Task.updated_at >= week_ago
    ).all()

    # Projects active this week
    projects_week = session.query(Project).filter(
        Project.last_active >= week_ago
    ).all()

    # Most active project
    project_counts = {}
    for task in tasks_done:
        if task.project_id:
            project_counts[task.project_id] = project_counts.get(task.project_id, 0) + 1
    most_active_project_id = max(project_counts, key=project_counts.get) if project_counts else None
    most_active_project = None
    if most_active_project_id:
        most_active_project = session.query(Project).filter(Project.id == most_active_project_id).first()

    session.expunge_all()
    session.close()

    return {
        "timeline": timeline_week,
        "tasks_created": tasks_created,
        "tasks_done": tasks_done,
        "projects": projects_week,
        "most_active_project": most_active_project,
        "start_date": week_ago.date(),
        "end_date": today.date()
    }

def edit_task(task_id: str, title: str = None, due: str = None) -> Task | None:
    session = get_session()
    session.expire_on_commit = False
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        if title:
            task.title = title
            task.normalized_title = normalize(title)
        if due:
            task.due_date = resolve_date(due)
        task.updated_at = datetime.utcnow()
        session.commit()
    session.expunge(task) if task else None
    session.close()
    return task

def delete_task(task_id: str) -> bool:
    session = get_session()
    session.expire_on_commit = False
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = "deleted"
        task.updated_at = datetime.utcnow()
        session.commit()
        session.close()
        return True
    session.close()
    return False

def delete_project(project_id: str) -> bool:
    session = get_session()
    session.expire_on_commit = False
    project = session.query(Project).filter(Project.id == project_id).first()
    if project:
        # Unlink tasks
        tasks = session.query(Task).filter(Task.project_id == project_id).all()
        for task in tasks:
            task.project_id = None
        session.commit()
        project.status = "deleted"
        session.commit()
        session.close()
        return True
    session.close()
    return False
