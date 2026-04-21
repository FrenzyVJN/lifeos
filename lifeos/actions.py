from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Task, TimelineEntry, Project, MoodEntry
from .parser import extract_tasks, call_ollama, call_ollama_text, resolve_date, extract_mood_score
from .db import get_session
from datetime import datetime, timedelta, timezone

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

def next_occurrence(recurrence: str, from_date: datetime = None) -> datetime:
    if not recurrence:
        return None
    from_date = from_date or datetime.now(timezone.utc)
    if recurrence == "daily":
        return from_date + timedelta(days=1)
    elif recurrence == "weekly":
        return from_date + timedelta(weeks=1)
    elif recurrence == "weekday":
        next_day = from_date + timedelta(days=1)
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        return next_day
    elif recurrence == "weekend":
        next_day = from_date + timedelta(days=1)
        while next_day.weekday() < 5:
            next_day += timedelta(days=1)
        return next_day
    return None

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

    parsed = call_ollama(user_input)
    tasks_data = parsed.get("tasks", [])
    if not tasks_data:
        tasks_data = []

    project_name = parsed.get("project")
    project = None

    if project_name:
        norm_project_name = normalize(project_name)
        project = find_duplicate_project(session, norm_project_name)
        if project:
            project.last_active = datetime.now(timezone.utc)
            session.commit()
        else:
            project = Project(
                name=project_name,
                normalized_name=norm_project_name,
                last_active=datetime.now(timezone.utc)
            )
            session.add(project)
            session.commit()

    task_results = []

    for task_data in tasks_data:
        norm_title = normalize(task_data["title"])
        existing = find_duplicate_task(session, norm_title)
        parsed_due_date = resolve_date(task_data.get("due_date"))
        priority = task_data.get("priority", "medium")
        recurrence = task_data.get("recurrence")

        if existing:
            # Always update the project if one was extracted this session
            if project and not existing.project_id:
                existing.project_id = project.id
            if parsed_due_date:
                existing.due_date = parsed_due_date
            existing.updated_at = datetime.now(timezone.utc)
            session.commit()
            task_results.append({"task": existing, "action": "updated"})
        else:
            new_task = Task(
                title=task_data["title"],
                normalized_title=norm_title,
                due_date=parsed_due_date,
                priority=priority,
                recurrence=recurrence,
                next_due=next_occurrence(recurrence, parsed_due_date) if recurrence else parsed_due_date,
                status="pending",
                project_id=project.id if project else None
            )
            session.add(new_task)
            session.commit()
            task_results.append({"task": new_task, "action": "created"})

    session.expunge_all()
    session.close()
    return entry, task_results

def get_pending_tasks(priority: str = None, today: bool = False) -> list[Task]:
    session = get_session()
    session.expire_on_commit = False

    query = session.query(Task).filter(Task.status == "pending")
    if priority:
        query = query.filter(Task.priority == priority)
    if today:
        now = datetime.now(timezone.utc)
        query = query.filter(
            (Task.due_date != None) &
            (Task.due_date <= now)
        )
    tasks = query.order_by(Task.created_at.desc()).all()
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
        task.updated_at = datetime.now(timezone.utc)
        session.commit()

        # Handle recurring task - create next occurrence
        if task.recurrence:
            new_task = Task(
                title=task.title,
                normalized_title=task.normalized_title,
                due_date=task.next_due,
                priority=task.priority,
                recurrence=task.recurrence,
                next_due=next_occurrence(task.recurrence, task.next_due),
                status="pending",
                project_id=task.project_id
            )
            session.add(new_task)
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
    projects = session.query(Project).filter(Project.status == "active").order_by(Project.last_active.desc()).all()
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

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    timeline_today = session.query(TimelineEntry).filter(
        TimelineEntry.timestamp >= today,
        TimelineEntry.timestamp < tomorrow
    ).order_by(TimelineEntry.timestamp.asc()).all()

    tasks_created = session.query(Task).filter(
        Task.created_at >= today,
        Task.created_at < tomorrow
    ).all()

    tasks_done = session.query(Task).filter(
        Task.status == "done",
        Task.updated_at >= today,
        Task.updated_at < tomorrow
    ).all()

    projects_today = session.query(Project).filter(
        Project.last_active >= today,
        Project.status == "active"
    ).all()

    streak = get_streak_internal(session)

    # Get mood today
    mood_today = session.query(MoodEntry).filter(
        MoodEntry.timestamp >= today,
        MoodEntry.timestamp < tomorrow
    ).first()

    # Get mood average (last 7 days)
    week_ago = today - timedelta(days=7)
    mood_week = session.query(MoodEntry).filter(
        MoodEntry.timestamp >= week_ago
    ).all()
    avg_mood = sum(m.score for m in mood_week) / len(mood_week) if mood_week else 0

    session.expunge_all()
    session.close()

    return {
        "timeline": timeline_today,
        "tasks_created": tasks_created,
        "tasks_done": tasks_done,
        "projects": projects_today,
        "streak": streak,
        "mood_today": mood_today,
        "avg_mood": round(avg_mood, 1),
        "date": datetime.now(timezone.utc)
    }

def get_streak_internal(session: Session) -> int:
    entries = session.query(TimelineEntry).order_by(
        TimelineEntry.timestamp.desc()
    ).all()

    if not entries:
        return 0

    dates = sorted(set([e.timestamp.date() for e in entries]), reverse=True)
    streak = 0
    today = datetime.now(timezone.utc).date()

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

    tasks = session.query(Task).filter(Task.status != "deleted").all()
    for task in tasks:
        score = embedding_similarity(query, task.normalized_title)
        if score > 0.5:
            results.append(("task", task, score))

    entries = session.query(TimelineEntry).all()
    for entry in entries:
        score = embedding_similarity(query, entry.content)
        if score > 0.5:
            results.append(("timeline", entry, score))

    results.sort(key=lambda x: x[2], reverse=True)
    results = results[:top_k]

    session.expunge_all()
    session.close()
    return results

def generate_digest() -> str:
    session = get_session()
    session.expire_on_commit = False

    # Use proper UTC datetime bounds instead of func.date()
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    entries = session.query(TimelineEntry).filter(
        TimelineEntry.timestamp >= today,
        TimelineEntry.timestamp < tomorrow
    ).all()

    if not entries:
        session.expunge_all()
        session.close()
        return "Nothing logged today. Run `life log` to start tracking."

    tasks_created = session.query(Task).filter(
        Task.created_at >= today,
        Task.created_at < tomorrow
    ).all()

    tasks_done = session.query(Task).filter(
        Task.status == "done",
        Task.updated_at >= today,
        Task.updated_at < tomorrow
    ).all()

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

    return call_ollama_text(prompt)

def get_weekly_summary() -> dict:
    session = get_session()
    session.expire_on_commit = False

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)

    timeline_week = session.query(TimelineEntry).filter(
        TimelineEntry.timestamp >= week_ago
    ).all()

    tasks_created = session.query(Task).filter(
        Task.created_at >= week_ago
    ).all()

    tasks_done = session.query(Task).filter(
        Task.status == "done",
        Task.updated_at >= week_ago
    ).all()

    projects_week = session.query(Project).filter(
        Project.last_active >= week_ago,
        Project.status == "active"
    ).all()

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
        task.updated_at = datetime.now(timezone.utc)
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
        task.updated_at = datetime.now(timezone.utc)
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

# Mood functions
def log_mood(mood_text: str) -> MoodEntry:
    score = extract_mood_score(mood_text)
    session = get_session()
    session.expire_on_commit = False
    entry = MoodEntry(mood=mood_text, score=score)
    session.add(entry)
    session.commit()
    session.expunge(entry)
    session.close()
    return entry

def get_mood_history(days: int = 7) -> list[dict]:
    session = get_session()
    session.expire_on_commit = False

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)

    entries = session.query(MoodEntry).filter(
        MoodEntry.timestamp >= start
    ).order_by(MoodEntry.timestamp.asc()).all()

    # Group by day
    by_day = {}
    for entry in entries:
        day = entry.timestamp.strftime("%a")
        by_day[day] = entry.score

    session.expunge_all()
    session.close()
    return by_day

def chat(question: str) -> str:
    session = get_session()
    session.expire_on_commit = False

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    entries = session.query(TimelineEntry).filter(
        TimelineEntry.timestamp >= week_ago
    ).order_by(TimelineEntry.timestamp.desc()).all()

    tasks = session.query(Task).filter(Task.status != "deleted").all()
    projects = session.query(Project).filter(Project.status == "active").all()

    context = f"""User's timeline (last 7 days):
{chr(10).join([f"- {e.timestamp.strftime('%b %d %H:%M')}: {e.content}" for e in entries])}

Current tasks:
{chr(10).join([f"- [{t.priority}] {t.title} (due: {t.due_date.strftime('%b %d') if t.due_date else 'none'}, status: {t.status})" for t in tasks])}

Projects:
{chr(10).join([f"- {p.name} (last active: {p.last_active.strftime('%b %d')})" for p in projects])}
"""

    prompt = f"""You are a personal productivity assistant with access to the user's activity log.
Answer their question based only on the data provided. Be specific and honest.
If something isn't in the data, say so.

Data:
{context}

Question: {question}

Respond only with your answer. No preamble."""

    session.expunge_all()
    session.close()

    return call_ollama_text(prompt)

def generate_report(week: bool = False, out_file: str = None) -> str:
    session = get_session()
    session.expire_on_commit = False

    if week:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        start = today - timedelta(days=7)
        entries = session.query(TimelineEntry).filter(
            TimelineEntry.timestamp >= start
        ).order_by(TimelineEntry.timestamp.asc()).all()
        tasks_created = session.query(Task).filter(Task.created_at >= start).all()
        tasks_done = session.query(Task).filter(
            Task.status == "done",
            Task.updated_at >= start
        ).all()
        projects = session.query(Project).filter(
            Project.last_active >= start,
            Project.status == "active"
        ).all()
        date_str = f"{start.strftime('%b %d')} to {today.strftime('%b %d, %Y')}"
    else:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        entries = session.query(TimelineEntry).filter(
            TimelineEntry.timestamp >= today,
            TimelineEntry.timestamp < tomorrow
        ).order_by(TimelineEntry.timestamp.asc()).all()
        tasks_created = session.query(Task).filter(
            Task.created_at >= today,
            Task.created_at < tomorrow
        ).all()
        tasks_done = session.query(Task).filter(
            Task.status == "done",
            Task.updated_at >= today,
            Task.updated_at < tomorrow
        ).all()
        projects = session.query(Project).filter(
            Project.last_active >= today,
            Project.status == "active"
        ).all()
        date_str = today.strftime('%b %d, %Y')

    pending = session.query(Task).filter(Task.status == "pending").all()

    # Build markdown
    md = f"# LifeOS Report — {date_str}\n\n"
    md += "## Summary\n"
    md += f"You logged {len(entries)} entries, completed {len(tasks_done)} tasks, and worked on {len(projects)} projects.\n\n"

    md += "## Tasks Completed\n"
    if tasks_done:
        for t in tasks_done:
            project_name = ""
            if t.project_id:
                p = session.query(Project).filter(Project.id == t.project_id).first()
                if p:
                    project_name = f" ({p.name})"
            md += f"- [x] {t.title}{project_name}\n"
    else:
        md += "- None\n"

    md += "\n## Tasks Pending\n"
    if pending:
        for t in pending:
            project_name = ""
            if t.project_id:
                p = session.query(Project).filter(Project.id == t.project_id).first()
                if p:
                    project_name = f" ({p.name})"
            priority_emoji = {"high": "🔴", "low": "🟢"}.get(t.priority, "🟡")
            due_str = f" — due {t.due_date.strftime('%b %d')}" if t.due_date else ""
            md += f"- [ ] {t.title}{due_str} {priority_emoji} {t.priority}{project_name}\n"
    else:
        md += "- None\n"

    md += "\n## Projects Active\n"
    if projects:
        for p in projects:
            md += f"- {p.name} ({p.last_active.strftime('%b %d')})\n"
    else:
        md += "- None\n"

    md += "\n## Timeline\n"
    if entries:
        for e in entries:
            md += f"- {e.timestamp.strftime('%H:%M')} {e.content}\n"
    else:
        md += "- No entries\n"

    session.expunge_all()
    session.close()

    if out_file:
        with open(out_file, 'w') as f:
            f.write(md)

    return md
