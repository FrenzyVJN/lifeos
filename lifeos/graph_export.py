"""Export LifeOS data as JSON for the web graph UI."""
import json
import sys
from datetime import datetime, timedelta

from lifeos.db import init_db, get_session
from lifeos.models import Task, Project, TimelineEntry, MoodEntry
from lifeos.actions import get_streak


def get_all_tasks(session):
    return session.query(Task).filter(Task.status != "deleted").all()


def get_all_projects(session):
    return session.query(Project).filter(Project.status == "active").all()


def get_timeline(session, limit=100):
    return session.query(TimelineEntry).order_by(
        TimelineEntry.timestamp.desc()
    ).limit(limit).all()


def get_mood_entries(session, days=7):
    now = datetime.utcnow()
    start = now - timedelta(days=days)
    return session.query(MoodEntry).filter(
        MoodEntry.timestamp >= start
    ).order_by(MoodEntry.timestamp.asc()).all()


def export_lifeos_data():
    init_db()
    session = get_session()
    session.expire_on_commit = False

    try:
        # Get projects
        projects_data = []
        projects = get_all_projects(session)
        for p in projects:
            task_count = session.query(Task).filter(
                Task.project_id == p.id,
                Task.status != "deleted"
            ).count()
            projects_data.append({
                "id": p.id,
                "name": p.name,
                "lastActive": p.last_active.isoformat() if p.last_active else None,
                "status": p.status,
                "taskCount": task_count
            })

        # Get tasks
        tasks_data = []
        tasks = get_all_tasks(session)
        for t in tasks:
            tasks_data.append({
                "id": t.id,
                "title": t.title,
                "normalizedTitle": t.normalized_title,
                "dueDate": t.due_date.isoformat() if t.due_date else None,
                "status": t.status,
                "priority": t.priority,
                "recurrence": t.recurrence,
                "nextDue": t.next_due.isoformat() if t.next_due else None,
                "projectId": t.project_id,
                "createdAt": t.created_at.isoformat() if t.created_at else None,
                "updatedAt": t.updated_at.isoformat() if t.updated_at else None
            })

        # Get timeline
        timeline_data = []
        timeline = get_timeline(session)
        for e in timeline:
            timeline_data.append({
                "id": e.id,
                "content": e.content,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None
            })

        # Get mood
        mood_data = []
        mood_entries = get_mood_entries(session)
        for m in mood_entries:
            mood_data.append({
                "id": m.id,
                "mood": m.mood,
                "score": m.score,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None
            })

        # Calculate stats
        total_tasks = len(tasks_data)
        completed_tasks = len([t for t in tasks_data if t["status"] == "done"])
        pending_tasks = len([t for t in tasks_data if t["status"] == "pending"])
        streak = get_streak()
        avg_mood = sum(m["score"] for m in mood_data) / len(mood_data) if mood_data else 0
        active_projects = len(projects_data)

        stats = {
            "totalTasks": total_tasks,
            "pendingTasks": pending_tasks,
            "completedTasks": completed_tasks,
            "currentStreak": streak,
            "avgMood7Days": round(avg_mood, 1),
            "activeProjects": active_projects
        }

        return {
            "projects": projects_data,
            "tasks": tasks_data,
            "timeline": timeline_data,
            "mood": mood_data,
            "stats": stats
        }

    finally:
        session.close()


if __name__ == "__main__":
    data = export_lifeos_data()
    print(json.dumps(data, indent=2))
