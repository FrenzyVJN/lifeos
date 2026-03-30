# LifeOS — Phase 2 Build Spec
> Hand this to Claude Code after Phase 1 is fully working.
> Phase 1 must be complete before starting this.

---

## What Phase 2 Adds

- Projects system
- Task → Project linking
- Better normalization (synonym replacement)
- `life summary` command (what did I do today?)

---

## New Database Model

Add to `models.py`:

```python
class Project(Base):
    __tablename__ = "projects"
    id: str (UUID, primary key)
    name: str
    normalized_name: str
    last_active: datetime (UTC, auto-updated)
    created_at: datetime (UTC, auto)
```

Update `Task` model:

```python
# Add this column to Task
project_id: str (nullable, foreign key → projects.id)
```

---

## Updated LLM Prompt (parser.py)

Replace Phase 1 prompt with this:

```
You are a task and project extraction assistant.

Return ONLY valid JSON. No explanation. No markdown. No extra text.

Format:
{
  "tasks": [
    {
      "title": "short task title",
      "due_date": "natural language date or null"
    }
  ],
  "project": "project name or null"
}

Rules:
- Keep task titles short (3-6 words max)
- Only extract actionable tasks
- Project is the broader context (e.g. "SNUC Hacks", "Math Course", "LifeOS")
- If no project context, return null for project
- If no tasks found, return empty list
- Do not hallucinate

User input: "{user_input}"
```

---

## Project Matching Logic (actions.py)

Same pattern as task deduplication:

```python
def find_duplicate_project(session, normalized_name: str) -> Project | None:
    projects = session.query(Project).all()
    for project in projects:
        if similarity(project.normalized_name, normalized_name) > 0.75
            return project
    return None
```

If match → update `last_active`
If no match → create new project

---

## Updated Log Flow (actions.py)

```
life log "text"
  ↓
Save to timeline
  ↓
LLM parse → tasks + project
  ↓
If project extracted:
    → find_duplicate_project()
    → create or update project
  ↓
For each task:
    → resolve date
    → find_duplicate_task()
    → create or update task
    → if project exists: link task.project_id → project.id
  ↓
Print confirmation
```

---

## New CLI Commands

### View projects
```bash
life projects
```

Output:
```
 🗂️  Projects
┌──────────┬─────────────────┬─────────────────────┐
│ ID       │ Name            │ Last Active         │
├──────────┼─────────────────┼─────────────────────┤
│ a1b2c3d4 │ SNUC Hacks      │ today               │
│ e5f6g7h8 │ LifeOS          │ today               │
│ i9j0k1l2 │ Math Course     │ yesterday           │
└──────────┴─────────────────┴─────────────────────┘
```

---

### View tasks for a project
```bash
life project <id>
```

Output:
```
 🗂️  Project: LifeOS
┌──────────┬──────────────────────┬──────────────┬─────────┐
│ ID       │ Title                │ Due Date     │ Status  │
├──────────┼──────────────────────┼──────────────┼─────────┤
│ 40bbb676 │ finish lifeos readme │ —            │ pending │
└──────────┴──────────────────────┴──────────────┴─────────┘
```

---

### Daily summary
```bash
life summary
```

Pulls all timeline entries from today and all tasks created/updated today.

Output:
```
 📊 Today's Summary — Mar 30, 2026

 🕐 Timeline (3 entries)
  02:26  math test in 3 days, finish lifeos readme
  16:56  finish my python project tomorrow
  16:56  study for math exam next week

 📌 Tasks Created Today (2)
  • math test (due Apr 2)
  • finish lifeos readme

 🗂️  Projects Active Today (1)
  • LifeOS
```

---

## Updated tasks view (show project)

Update `life tasks` output to include project column:

```
┌──────────┬──────────────────┬──────────────┬─────────────┬─────────┐
│ ID       │ Title            │ Due Date     │ Project     │ Status  │
├──────────┼──────────────────┼──────────────┼─────────────┼─────────┤
│ 40bbb676 │ finish readme    │ —            │ LifeOS      │ pending │
│ 56993f63 │ math test        │ Apr 02, 2026 │ Math Course │ pending │
└──────────┴──────────────────┴──────────────┴─────────────┴─────────┘
```

---

## Better Normalization (actions.py)

Add synonym replacement to the normalize function:

```python
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

def normalize(text: str) -> str:
    STOPWORDS = {"a", "an", "the", "to", "for", "in", "on", "at", "my", "i", "and"}
    tokens = text.lower().split()
    tokens = [SYNONYMS.get(t, t) for t in tokens]
    return " ".join(t for t in tokens if t not in STOPWORDS)
```

---

## Database Migration

Phase 1 already has `tasks` and `timeline_entries` tables.
Phase 2 adds `projects` table and `project_id` column to `tasks`.

Use SQLAlchemy's `create_all()` with `checkfirst=True` - it will create only missing tables without touching existing data.

For the new `project_id` column on existing tasks table, add this migration in `db.py`:

```python
from sqlalchemy import inspect, text

def run_migrations(engine):
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns("tasks")]
    if "project_id" not in columns:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN project_id TEXT"))
            conn.commit()
```

Call `run_migrations(engine)` before app starts.

---

## What Phase 2 Does NOT Include

- ❌ Embeddings (still using difflib)
- ❌ Voice input
- ❌ Web UI
- ❌ Notifications
- ❌ Export features
- ❌ Edit command
- ❌ Search

---

## Definition of Done

Phase 2 is complete when:
- [ ] `life log "worked on lifeos"` creates a LifeOS project
- [ ] `life log "math exam next week"` links to Math Course project
- [ ] `life projects` shows all projects with last active
- [ ] `life project <id>` shows tasks for that project
- [ ] `life tasks` shows project column
- [ ] `life summary` shows today's activity
- [ ] Existing Phase 1 data is not broken
- [ ] Migration runs cleanly on existing DB