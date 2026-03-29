import typer
import lifeos.db as db_module
from .db import init_db
from .models import Base, Task, TimelineEntry  # Import models to register them with Base
from . import actions, display

app = typer.Typer()

def ensure_db():
    init_db()
    if db_module.ENGINE:
        Base.metadata.create_all(db_module.ENGINE)

@app.command()
def log(text: str):
    ensure_db()
    if not text.strip():
        display.console.print("[red]Please provide some text[/red]")
        raise typer.Exit(code=1)
    entry, results = actions.log_input(text)
    display.print_log_confirmation(entry, results)

@app.command()
def tasks(done: bool = False):
    ensure_db()
    if done:
        task_list = actions.get_done_tasks()
        display.print_tasks(task_list, title="Done Tasks")
    else:
        task_list = actions.get_pending_tasks()
        display.print_tasks(task_list)

@app.command()
def done(task_id: str):
    ensure_db()
    task = actions.mark_task_done(task_id)
    if task:
        display.print_done_confirmation(task)
    else:
        display.console.print(f"[red]Task {task_id} not found[/red]")
        raise typer.Exit(code=1)

@app.command()
def timeline():
    ensure_db()
    entries = actions.get_timeline()
    display.print_timeline(entries)

if __name__ == "__main__":
    app()