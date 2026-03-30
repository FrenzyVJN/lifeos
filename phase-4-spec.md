# LifeOS — Phase 4 Build Spec
> Hand this to Claude Code after Phase 3 is fully working.
> All previous phases must be complete before starting this.

---

## What Phase 4 Adds

- Claude API integration (replaces Ollama, better parsing)
- Recurring tasks
- Priority levels on tasks
- `life report` command (markdown export for sharing)
- Mood/energy tracking
- `life chat` — ask questions about your own data

---

## 1. Upgrade to Qwen 7B

Switch from llama3.2 to Qwen 7B for better structured JSON extraction.

### Why switch:
- Qwen 7B follows JSON format instructions more reliably than llama3.2
- Better at extracting priority, recurrence, and structured fields
- Still fully local and free via Ollama

### Setup:

```bash
ollama pull qwen2.5:7b
```

### Update model reference in parser.py:

```python
OLLAMA_MODEL = "qwen2.5:7b"  # replace wherever llama3.2 was hardcoded

def call_ollama(prompt: str) -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    )
    return response.json()["response"]
```

### Guard for empty timeline in digest:

```python
def generate_digest(session) -> str:
    today = datetime.utcnow().date()
    entries = session.query(TimelineEntry).filter(
        func.date(TimelineEntry.timestamp) == today
    ).all()
    
    if not entries:
        return "Nothing logged today. Run `life log` to start tracking."
    
    # ... rest of digest logic
```

---

## 2. Priority Levels

Add priority to tasks: `high`, `medium`, `low` (default: `medium`)

### Update Task model:

```python
priority: str  # "high" / "medium" / "low", default "medium"
```

### Update LLM prompt to extract priority:

```json
{
  "tasks": [
    {
      "title": "math test",
      "due_date": "in 3 days",
      "priority": "high"
    }
  ]
}
```

### LLM priority rules in prompt:
- `high`: exams, deadlines, submissions, urgent
- `low`: someday tasks, no due date, casual mentions
- `medium`: everything else

### Updated tasks view:

```
 📌 Pending Tasks
┌──────────┬──────────────────┬──────────────┬──────────┬─────────────┬─────────┐
│ ID       │ Title            │ Due Date     │ Priority │ Project     │ Status  │
├──────────┼──────────────────┼──────────────┼──────────┼─────────────┼─────────┤
│ 56993f63 │ math test        │ Apr 02, 2026 │ 🔴 high  │ Math Course │ pending │
│ 40bbb676 │ finish readme    │ —            │ 🟡 med   │ LifeOS      │ pending │
└──────────┴──────────────────┴──────────────┴──────────┴─────────────┴─────────┘
```

### New filter command:

```bash
life tasks --high     # show only high priority
life tasks --today    # show only tasks due today or overdue
```

---

## 3. Recurring Tasks

```bash
life log "standup meeting every weekday"
life log "review notes every sunday"
```

### Update Task model:

```python
recurrence: str  # null / "daily" / "weekly" / "weekday" / "weekend"
next_due: datetime  # auto-calculated from recurrence
```

### Updated LLM prompt extracts recurrence:

```json
{
  "tasks": [
    {
      "title": "standup meeting",
      "due_date": null,
      "recurrence": "weekday",
      "priority": "medium"
    }
  ]
}
```

### Recurrence engine (actions.py):

```python
from datetime import timedelta

def next_occurrence(recurrence: str, from_date: datetime) -> datetime:
    if recurrence == "daily":
        return from_date + timedelta(days=1)
    elif recurrence == "weekly":
        return from_date + timedelta(weeks=1)
    elif recurrence == "weekday":
        next_day = from_date + timedelta(days=1)
        while next_day.weekday() >= 5:  # skip weekend
            next_day += timedelta(days=1)
        return next_day
    elif recurrence == "weekend":
        next_day = from_date + timedelta(days=1)
        while next_day.weekday() < 5:  # skip weekdays
            next_day += timedelta(days=1)
        return next_day
    return None
```

When a recurring task is marked done → auto-create next occurrence with updated `next_due`.

---

## 4. Mood / Energy Tracking

```bash
life mood good
life mood bad
life mood "tired but focused"
```

### New model:

```python
class MoodEntry(Base):
    __tablename__ = "mood_entries"
    id: str (UUID)
    mood: str  # raw input
    score: int  # 1-5, extracted by LLM
    timestamp: datetime
```

### LLM extracts score from mood text:

- "great", "productive", "amazing" → 5
- "good", "focused" → 4
- "okay", "meh" → 3
- "tired", "distracted" → 2
- "bad", "terrible", "burned out" → 1

### Show in summary:

```
 😊 Mood Today: good (4/5)
 📈 7-day average: 3.4/5
```

### New command:

```bash
life mood-history    # show last 7 days of mood scores
```

Output:
```
 Mood — Last 7 Days
Mon  ████████░░  4/5
Tue  ██████░░░░  3/5
Wed  ██████████  5/5
Thu  ████░░░░░░  2/5
Fri  ████████░░  4/5
```

---

## 5. Markdown Report Export

```bash
life report           # today's report
life report --week    # this week's report
life report --out report.md   # save to file
```

### Output format (markdown):

```markdown
# LifeOS Report — Mar 30, 2026

## Summary
You logged 3 entries, completed 2 tasks, and worked on 2 projects.
Mood average: 4/5.

## Tasks Completed
- [x] finish lifeos readme (LifeOS)
- [x] review paper draft (IITM Research)

## Tasks Pending
- [ ] math test — due Apr 2 🔴 high
- [ ] push phase 4 — due today 🟡 med

## Projects Active
- LifeOS (3 entries)
- IITM Research (1 entry)

## Timeline
- 08:17 worked on lifeos phase 4 spec
- 14:24 back from college, starting phase 4
- 16:00 finished phase 4 implementation
```

This is the file you paste to me as your daily check-in.

---

## 6. `life chat` — Ask Your Data

```bash
life chat "what have I been working on this week?"
life chat "am I making progress on lifeos?"
life chat "what's overdue?"
```

### Implementation:

Pull relevant data from DB, pass as context to Claude API, get natural language answer.

```python
def chat(session, question: str) -> str:
    # Pull all recent data
    entries = get_recent_timeline(session, days=7)
    tasks = get_all_tasks(session)
    projects = get_all_projects(session)
    
    context = f"""
User's timeline (last 7 days):
{format_entries(entries)}

Current tasks:
{format_tasks(tasks)}

Projects:
{format_projects(projects)}
"""
    
    prompt = f"""
You are a personal productivity assistant with access to the user's activity log.
Answer their question based only on the data provided. Be specific and honest.
If something isn't in the data, say so.

Data:
{context}

Question: {question}
"""
    return call_ollama(prompt)
```

> Note: Qwen 7B may give inconsistent answers for complex questions. If responses are poor, try being more specific in your question.

### Output:

```
❯ life chat "what's overdue?"

You have 2 overdue tasks:
- "review code" was due Mar 30 (yesterday)
- "finish python project" was due Mar 30 (yesterday)

Both are unlinked to a project. Want to mark them done or update the due dates?
```

---

## Database Changes

Add columns to existing tables via migration:

```python
def run_migrations(engine):
    inspector = inspect(engine)
    
    task_cols = [c["name"] for c in inspector.get_columns("tasks")]
    with engine.connect() as conn:
        if "priority" not in task_cols:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'medium'"))
        if "recurrence" not in task_cols:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN recurrence TEXT"))
        if "next_due" not in task_cols:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN next_due DATETIME"))
        conn.commit()
    
    # Create mood_entries table if not exists
    MoodEntry.__table__.create(bind=engine, checkfirst=True)
```

---

## Dependencies to Add

No new dependencies needed - Qwen runs via existing Ollama setup.

---

## Definition of Done

Phase 4 is complete when:
- [ ] Qwen 7B is set as default model in parser.py
- [ ] Empty timeline shows "Nothing logged today" instead of hallucinating
- [ ] `life tasks` shows priority column with colored indicators
- [ ] `life tasks --high` filters to high priority only
- [ ] `life tasks --today` shows overdue and due-today tasks
- [ ] `life log "standup every weekday"` creates recurring task
- [ ] Marking recurring task done auto-creates next occurrence
- [ ] `life mood good` logs mood with LLM score
- [ ] `life mood-history` shows 7-day bar chart in terminal
- [ ] `life report` exports clean markdown
- [ ] `life report --out report.md` saves to file
- [ ] `life chat "question"` answers from real data
- [ ] All Phase 1/2/3 commands still work
- [ ] Migration runs cleanly on existing DB