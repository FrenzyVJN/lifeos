# LifeOS — Phase 1 Build Spec
> Hand this entire document to Claude Code. Build Phase 1 only. No scope creep.

---

## Project Overview

A local CLI tool that lets the user dump unstructured thoughts and automatically:
- Logs everything to a timeline
- Extracts tasks using a local LLM (Ollama)
- Stores everything in SQLite via SQLAlchemy ORM
- Displays tasks and timeline cleanly in terminal

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.11+ | Fast to build, rich ecosystem |
| CLI Framework | [Typer](https://typer.tiangolo.com/) | Clean CLI with minimal boilerplate |
| ORM | SQLAlchemy 2.0 | Future-proof for PostgreSQL migration |
| Database | SQLite (local file `~/.lifeos/lifeos.db`) | Zero setup, works offline |
| LLM | Ollama (llama3.2) | Free, local, unlimited |
| Output formatting | [Rich](https://rich.readthedocs.io/) | Beautiful terminal output |
| Date parsing | [dateparser](https://dateparser.readthedocs.io/) | Handles "in 3 days", "tomorrow", etc. |

---

## Folder Structure

```
lifeos/
├── lifeos/
│   ├── __init__.py
│   ├── main.py          # CLI entry point (Typer app)
│   ├── db.py            # SQLAlchemy setup, engine, session
│   ├── models.py        # ORM models
│   ├── parser.py        # LLM extraction + fallback
│   ├── actions.py       # Core business logic
│   └── display.py       # Rich-based terminal output
├── pyproject.toml       # Package config + dependencies
└── README.md
```

---

## Database Models (models.py)

```python
# Two models only for Phase 1

class TimelineEntry(Base):
    __tablename__ = "timeline_entries"
    id: str (UUID, primary key)
    content: str (raw user input)
    timestamp: datetime (UTC, auto)

class Task(Base):
    __tablename__ = "tasks"
    id: str (UUID, primary key)
    title: str
    normalized_title: str (lowercase, stopwords removed)
    due_date: datetime (nullable)
    status: str (default: "pending") # pending / done
    created_at: datetime (UTC, auto)
    updated_at: datetime (UTC, auto)
```

---

## LLM Parser (parser.py)

### Primary: Ollama llama3.2

Call Ollama REST API at `http://localhost:11434/api/generate`

#### Prompt (use this exactly):

```
You are a task extraction assistant. Extract structured data from user input.

Return ONLY valid JSON. No explanation. No markdown. No extra text.

Format:
{
  "tasks": [
    {
      "title": "short task title",
      "due_date": "natural language date or null"
    }
  ]
}

Rules:
- Keep titles short (3-6 words max)
- Only extract actionable tasks
- If no tasks found, return {"tasks": []}
- Do not hallucinate tasks not mentioned

User input: "{user_input}"
```

#### JSON Parsing:

```python
import json, re

def safe_parse(raw: str) -> dict:
    # Strip markdown fences if present
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return empty tasks
        return {"tasks": []}
```

### Fallback: Rule-based extraction

If Ollama is not running or returns invalid JSON, use this fallback:

```python
import re
from datetime import datetime, timedelta

TASK_PATTERNS = [
    r"\b(finish|complete|submit|do|study|prepare|fix|build|write|review)\b.{3,40}",
    r"\b\w+\s+(test|exam|assignment|meeting|deadline|due)\b",
]

def rule_based_extract(text: str) -> list[dict]:
    tasks = []
    for pattern in TASK_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            tasks.append({"title": match.strip(), "due_date": None})
    return tasks
```

---

## Date Resolution (parser.py)

Use `dateparser` library:

```python
import dateparser

def resolve_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    parsed = dateparser.parse(raw, settings={"PREFER_DATES_FROM": "future"})
    return parsed
```

---

## Deduplication Logic (actions.py)

Before creating a task, check for duplicates:

```python
from difflib import SequenceMatcher

def normalize(text: str) -> str:
    STOPWORDS = {"a", "an", "the", "to", "for", "in", "on", "at", "my", "i"}
    tokens = text.lower().split()
    return " ".join(t for t in tokens if t not in STOPWORDS)

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def find_duplicate(session, normalized_title: str) -> Task | None:
    tasks = session.query(Task).filter(Task.status == "pending").all()
    for task in tasks:
        if similarity(task.normalized_title, normalized_title) > 0.8:
            return task
    return None
```

If duplicate found → update `due_date` and `updated_at` only.
If no duplicate → create new task.

---

## CLI Commands (main.py)

### 1. Log input
```bash
life log "worked on backend, math test in 3 days"
```
**Flow:**
1. Save raw input to `timeline_entries`
2. Call LLM parser → extract tasks
3. For each task: resolve date → dedup check → create or update
4. Print confirmation with Rich

---

### 2. View tasks
```bash
life tasks
```
**Output:**
```
 📌 Pending Tasks
┌────┬─────────────────────┬──────────────┬────────────┐
│ ID │ Title               │ Due Date     │ Status     │
├────┼─────────────────────┼──────────────┼────────────┤
│  1 │ Math test           │ Apr 1, 2026  │ pending    │
│  2 │ Finish reel         │ —            │ pending    │
└────┴─────────────────────┴──────────────┴────────────┘
```

---

### 3. Mark task done
```bash
life done <id>
```
Updates `status` to `done`, updates `updated_at`.

---

### 4. View timeline
```bash
life timeline
```
**Output:**
```
 📜 Timeline
[Mar 29 · 12:30]  worked on backend, math test in 3 days
[Mar 29 · 14:00]  need to finish reel
```

---

### 5. View all done tasks
```bash
life tasks --done
```

---

## Setup & Installation

```toml
# pyproject.toml
[project]
name = "lifeos"
version = "0.1.0"
dependencies = [
    "typer[all]",
    "sqlalchemy",
    "rich",
    "dateparser",
    "requests",  # for Ollama API calls
    "httpx",
]

[project.scripts]
life = "lifeos.main:app"
```

Install with:
```bash
pip install -e .
```

---

## Ollama Setup (README section)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull llama3.2

# Start Ollama (runs in background)
ollama serve
```

---

## Error Handling Requirements

| Scenario | Behavior |
|---|---|
| Ollama not running | Fall back to rule-based parser, warn user |
| Invalid JSON from LLM | Fall back to rule-based parser silently |
| No tasks found in input | Log to timeline only, inform user |
| Duplicate task found | Update due date, print "Updated: [task]" |
| Empty input | Show error: "Please provide some text" |

---

## What Phase 1 Does NOT include

- ❌ Projects / project linking
- ❌ Embeddings (uses difflib only)
- ❌ Voice input
- ❌ Web UI
- ❌ Notifications
- ❌ Daily digest / summaries
- ❌ Export features

Build only what's in this doc. Resist scope creep.

---

## Definition of Done

Phase 1 is complete when:
- [ ] `life log "text"` works and saves to DB
- [ ] Tasks are extracted from natural language
- [ ] Duplicate tasks are updated not duplicated
- [ ] `life tasks` shows a clean table
- [ ] `life done <id>` marks task complete
- [ ] `life timeline` shows full log
- [ ] Fallback works when Ollama is offline
- [ ] `pip install -e .` works cleanly