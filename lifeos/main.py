import typer
import lifeos.db as db_module
from .db import init_db, run_migrations
from .models import Base, Task, TimelineEntry, Project  # Import models to register them with Base
from . import actions, display

app = typer.Typer()

def ensure_db():
    init_db()
    if db_module.ENGINE:
        Base.metadata.create_all(db_module.ENGINE)
        run_migrations(db_module.ENGINE)

@app.command()
def log(text: str):
    ensure_db()
    if not text.strip():
        display.console.print("[red]Please provide some text[/red]")
        raise typer.Exit(code=1)
    entry, results = actions.log_input(text)
    display.print_log_confirmation(entry, results)

@app.command()
def tasks(done: bool = False, high: bool = False, today: bool = False):
    ensure_db()
    if done:
        task_list = actions.get_done_tasks()
        display.print_tasks(task_list, title="Done Tasks")
    else:
        task_list = actions.get_pending_tasks(priority="high" if high else None, today=today)
        title = "High Priority Tasks" if high else ("Due Today" if today else "Pending Tasks")
        display.print_tasks(task_list, title=title)

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

@app.command()
def projects():
    ensure_db()
    project_list = actions.get_all_projects()
    display.print_projects(project_list)

@app.command()
def project(project_id: str):
    ensure_db()
    project_obj, tasks = actions.get_project_tasks(project_id)
    if project_obj:
        display.print_project_tasks(project_obj, tasks)
    else:
        display.console.print(f"[red]Project {project_id} not found[/red]")
        raise typer.Exit(code=1)

@app.command()
def summary():
    ensure_db()
    data = actions.get_daily_summary()
    display.print_summary(data)

@app.command()
def digest():
    ensure_db()
    from datetime import datetime
    display.console.print("[dim]Generating digest...[/dim]")
    digest_text = actions.generate_digest()
    display.console.print(f"\n[dodger_blue1]Daily Digest — {datetime.utcnow().strftime('%b %d, %Y')}[/dodger_blue1]")
    display.console.print(f"\n{digest_text}")

@app.command()
def weekly():
    ensure_db()
    data = actions.get_weekly_summary()
    display.print_weekly_summary(data)

@app.command()
def search(query: str):
    ensure_db()
    results = actions.search(query)
    display.print_search_results(query, results)

@app.command()
def edit(task_id: str, title: str = None, due: str = None):
    ensure_db()
    if not title and not due:
        display.console.print("[red]Please provide --title or --due[/red]")
        raise typer.Exit(code=1)
    task = actions.edit_task(task_id, title=title, due=due)
    if task:
        display.console.print(f"[green]✓[/green] Task updated: {task.title}")
    else:
        display.console.print(f"[red]Task {task_id} not found[/red]")
        raise typer.Exit(code=1)

@app.command()
def delete(task_id: str):
    ensure_db()
    if actions.delete_task(task_id):
        display.console.print(f"[green]✓[/green] Task deleted")
    else:
        display.console.print(f"[red]Task {task_id} not found[/red]")
        raise typer.Exit(code=1)

@app.command()
def delete_project(project_id: str):
    ensure_db()
    if actions.delete_project(project_id):
        display.console.print(f"[green]✓[/green] Project deleted (tasks unlinked)")
    else:
        display.console.print(f"[red]Project {project_id} not found[/red]")
        raise typer.Exit(code=1)

@app.command()
def streak():
    ensure_db()
    s = actions.get_streak()
    display.console.print(f"[bold]🔥 Current streak:[/bold] {s} days")

@app.command()
def mood(mood_text: str):
    ensure_db()
    entry = actions.log_mood(mood_text)
    display.console.print(f"[green]✓[/green] Mood logged: {entry.mood} ({entry.score}/5)")

@app.command()
def mood_history():
    ensure_db()
    history = actions.get_mood_history()
    display.print_mood_history(history)

@app.command()
def report(week: bool = False, out: str = None):
    ensure_db()
    md = actions.generate_report(week=week, out_file=out)
    display.print_report(md)
    if out:
        display.console.print(f"[green]✓[/green] Report saved to {out}")

@app.command()
def chat(question: str):
    ensure_db()
    answer = actions.chat(question)
    display.print_chat(question, answer)

if __name__ == "__main__":
    app()