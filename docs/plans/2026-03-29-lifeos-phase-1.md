# LifeOS Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a local CLI tool that logs unstructured thoughts to a timeline, extracts tasks using Ollama LLM, stores in SQLite via SQLAlchemy, and displays results cleanly in terminal.

**Architecture:** Python CLI with Typer framework, SQLAlchemy 2.0 ORM to SQLite, Ollama REST API for LLM task extraction, Rich for terminal output, dateparser for natural language date parsing.

**Tech Stack:** Python 3.11+, Typer, SQLAlchemy 2.0, SQLite, Ollama (llama3.2), Rich, dateparser, requests/httpx

---

## Task 1: Create Project Structure and pyproject.toml

**Files:**
- Create: `/Users/frenzyvjn/Documents/personal/lifeos/pyproject.toml`
- Create: `/Users/frenzyvjn/Documents/personal/lifeos/lifeos/__init__.py`
- Create: `/Users/frenzyvjn/Documents/personal/lifeos/lifeos/main.py`
- Create: `/Users/frenzyvjn/Documents/personal/lifeos/lifeos/db.py`
- Create: `/Users/frenzyvjn/Documents/personal/lifeos/lifeos/models.py`
- Create: `/Users/frenzyvjn/Documents/personal/lifeos/lifeos/parser.py`
- Create: `/Users/frenzyvjn/Documents/personal/lifeos/lifeos/actions.py`
- Create: `/Users/frenzyvjn/Documents/personal/lifeos/lifeos/display.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "lifeos"
version = "0.1.0"
dependencies = [
    "typer[all]",
    "sqlalchemy>=2.0.0",
    "rich>=13.0.0",
    "dateparser>=1.0.0",
    "requests>=2.28.0",
    "httpx>=0.24.0",
]

[project.scripts]
life = "lifeos.main:app"
```

**Step 2: Create empty __init__.py**

```python
# LifeOS - Local CLI for life management
```

**Step 3: Create db.py with SQLAlchemy setup**

```python
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
```

**Step 4: Create models.py with ORM models**

```python
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class TimelineEntry(Base):
    __tablename__ = "timeline_entries"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    normalized_title = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Step 5: Create parser.py with LLM and fallback extraction**

```python
import re
import json
import requests
from datetime import datetime
import dateparser
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"

def safe_parse(raw: str) -> dict:
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"tasks": []}

def call_ollama(user_input: str) -> dict:
    prompt = f"""You are a task extraction assistant. Extract structured data from user input. Return ONLY valid JSON. No explanation. No markdown. No extra text. Format: {{"tasks": [{{"title": "short task title", "due_date": "natural language date or null"}}]}} Rules: - Keep titles short (3-6 words max) - Only extract actionable tasks - If no tasks found, return {{"tasks": []}} - Do not hallucinate tasks not mentioned User input: "{user_input}" """
    try:
        response = requests.post(OLLAMA_URL, json={"model": "llama3.2", "prompt": prompt}, timeout=30)
        if response.status_code == 200:
            return safe_parse(response.text)
    except Exception:
        pass
    return {"tasks": []}

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

def resolve_date(raw: str | None) -> Optional[datetime]:
    if not raw:
        return None
    parsed = dateparser.parse(raw, settings={"PREFER_DATES_FROM": "future"})
    return parsed

def extract_tasks(user_input: str) -> list[dict]:
    result = call_ollama(user_input)
    if not result.get("tasks"):
        result = {"tasks": rule_based_extract(user_input)}
    resolved_tasks = []
    for task in result.get("tasks", []):
        resolved_tasks.append({
            "title": task["title"],
            "due_date": resolve_date(task.get("due_date"))
        })
    return resolved_tasks
```

**Step 6: Create actions.py with business logic**

```python
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
            from .models import Task
            new_task = Task(
                title=task_data["title"],
                normalized_title=norm_title,
                due_date=task_data["due_date"],
                status="pending"
            )
            session.add(new_task)
            session.commit()
            task_results.append({"task": new_task, "action": "created"})

    session.close()
    return entry, task_results

def get_pending_tasks() -> list[Task]:
    session = get_session()
    tasks = session.query(Task).filter(Task.status == "pending").order_by(Task.created_at.desc()).all()
    session.close()
    return tasks

def get_done_tasks() -> list[Task]:
    session = get_session()
    tasks = session.query(Task).filter(Task.status == "done").order_by(Task.updated_at.desc()).all()
    session.close()
    return tasks

def mark_task_done(task_id: str) -> Task | None:
    session = get_session()
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        from datetime import datetime
        task.status = "done"
        task.updated_at = datetime.utcnow()
        session.commit()
    session.close()
    return task

def get_timeline() -> list[TimelineEntry]:
    session = get_session()
    entries = session.query(TimelineEntry).order_by(TimelineEntry.timestamp.desc()).all()
    session.close()
    return entries
```

**Step 7: Create display.py with Rich output**

```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

console = Console()

def print_log_confirmation(entry: TimelineEntry, task_results: list[dict]) -> None:
    console.print(f"[green]Logged:[/green] {entry.content}")
    if task_results:
        for result in task_results:
            task = result["task"]
            action = result["action"]
            if action == "updated":
                console.print(f"[yellow]Updated:[/yellow] {task.title}")
            else:
                console.print(f"[blue]Task created:[/blue] {task.title}")

def print_tasks(tasks: list, title: str = "Pending Tasks") -> None:
    if not tasks:
        console.print("[dim]No tasks found.[/dim]")
        return

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Title", style="cyan")
    table.add_column("Due Date", style="green")
    table.add_column("Status", style="yellow")

    for task in tasks:
        due_str = task.due_date.strftime("%b %d, %Y") if task.due_date else "—"
        table.add_row(task.id[:8], task.title, due_str, task.status)

    console.print(table)

def print_timeline(entries: list) -> None:
    if not entries:
        console.print("[dim]No timeline entries.[/dim]")
        return

    console.print(Panel("[bold]Timeline[/bold]", expand=False))
    for entry in entries:
        time_str = entry.timestamp.strftime("%b %d · %H:%M")
        console.print(f"[dim]{time_str}[/dim] {entry.content}")

def print_done_confirmation(task: object) -> None:
    console.print(f"[green]✓[/green] Task marked as done: {getattr(task, 'title', 'Unknown')}")
```

**Step 8: Create main.py with Typer CLI**

```python
import typer
from .db import init_db, ENGINE
from .models import Base
from . import actions, display

app = typer.Typer()

@app.on_startup
def startup():
    init_db()
    if ENGINE:
        Base.metadata.create_all(ENGINE)

@app.command()
def log(text: str):
    if not text.strip():
        console = display.console
        console.print("[red]Please provide some text[/red]")
        raise typer.Exit(code=1)
    entry, results = actions.log_input(text)
    display.print_log_confirmation(entry, results)

@app.command()
def tasks(done: bool = False):
    if done:
        task_list = actions.get_done_tasks()
        display.print_tasks(task_list, title="Done Tasks")
    else:
        task_list = actions.get_pending_tasks()
        display.print_tasks(task_list)

@app.command()
def done(task_id: str):
    task = actions.mark_task_done(task_id)
    if task:
        display.print_done_confirmation(task)
    else:
        console = display.console
        console.print(f"[red]Task {task_id} not found[/red]")
        raise typer.Exit(code=1)

@app.command()
def timeline():
    entries = actions.get_timeline()
    display.print_timeline(entries)

if __name__ == "__main__":
    app()
```

**Step 9: Run tests to verify structure**

Run: `ls -la /Users/frenzyvjn/Documents/personal/lifeos/lifeos/`
Expected: All files created

**Step 10: Commit**

```bash
cd /Users/frenzyvjn/Documents/personal/lifeos && git init && git add pyproject.toml lifeos/ && git commit -m "feat: initial project structure and core modules"
```

---

## Task 2: Install Dependencies and Test Installation

**Files:**
- Modify: `/Users/frenzyvjn/Documents/personal/lifeos/.gitignore`

**Step 1: Create .gitignore**

```
__pycache__/
*.pyc
.pytest_cache/
.lifeos/
```

**Step 2: Install package in editable mode**

Run: `cd /Users/frenzyvjn/Documents/personal/lifeos && pip install -e .`
Expected: Successfully installed lifeos-0.1.0

**Step 3: Verify CLI is available**

Run: `life --help`
Expected: Typer help output showing log, tasks, done, timeline commands

**Step 4: Commit**

```bash
git add .gitignore && git commit -m "chore: add gitignore and install dependencies"
```

---

## Task 3: Verify All CLI Commands Work

**Files:** (no changes)

**Step 1: Test timeline command (empty state)**

Run: `life timeline`
Expected: "No timeline entries." message

**Step 2: Test tasks command (empty state)**

Run: `life tasks`
Expected: "No tasks found." message

**Step 3: Test log command with simple text**

Run: `life log "finish math homework tomorrow"`
Expected: Logged confirmation + task created

**Step 4: Test tasks shows the task**

Run: `life tasks`
Expected: Table showing "finish math homework tomorrow" task

**Step 5: Get the task ID and test done command**

Run: `life tasks` to see tasks, then `life done <id>`
Expected: Task marked as done

**Step 6: Test done tasks view**

Run: `life tasks --done`
Expected: Table showing the completed task

**Step 7: Test timeline command**

Run: `life timeline`
Expected: Shows the logged entry

**Step 8: Commit**

```bash
git add -A && git commit -m "test: verify all CLI commands work"
```

---

## Task 4: Verify Fallback Works (Ollama Offline)

**Files:** (no changes)

**Step 1: Stop Ollama if running**

Run: `pkill -f ollama || true`

**Step 2: Log input with Ollama offline**

Run: `life log "study for exam next week"`
Expected: Logged successfully with fallback parser (rule-based)

**Step 3: Commit**

```bash
git add -A && git commit -m "test: verify fallback parser works when Ollama offline"
```

---

## Task 5: Final Verification Against Spec

**Files:** (no changes)

**Step 1: Verify all spec requirements**

- [ ] `life log "text"` works and saves to DB
- [ ] Tasks are extracted from natural language
- [ ] Duplicate tasks are updated not duplicated
- [ ] `life tasks` shows a clean table
- [ ] `life done <id>` marks task complete
- [ ] `life timeline` shows full log
- [ ] Fallback works when Ollama is offline
- [ ] `pip install -e .` works cleanly

**Step 2: Final commit**

```bash
git add -A && git commit -m "feat: Phase 1 complete - all spec requirements met"
```

---

## Definition of Done Checklist

- [ ] `life log "text"` works and saves to DB
- [ ] Tasks are extracted from natural language
- [ ] Duplicate tasks are updated not duplicated
- [ ] `life tasks` shows a clean table
- [ ] `life done <id>` marks task complete
- [ ] `life timeline` shows full log
- [ ] Fallback works when Ollama is offline
- [ ] `pip install -e .` works cleanly
