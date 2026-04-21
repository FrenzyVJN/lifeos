from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime, timezone

console = Console()

def print_log_confirmation(entry, task_results):
    console.print(f"[green]Logged:[/green] {entry.content}")
    if task_results:
        for result in task_results:
            task = result["task"]
            action = result["action"]
            if action == "updated":
                console.print(f"[yellow]Updated:[/yellow] {task.title}")
            else:
                console.print(f"[blue]Task created:[/blue] {task.title}")

def get_project_name(project_id, projects_cache=None):
    if not project_id:
        return "—"
    if projects_cache and project_id in projects_cache:
        return projects_cache[project_id]
    return project_id[:8]

def get_priority_indicator(priority):
    return {"high": "[red]🔴 high[/red]", "low": "[green]🟢 low[/green]", "medium": "[yellow]🟡 med[/yellow]"}.get(priority, "🟡 med")

def print_tasks(tasks, title="Pending Tasks", projects_cache=None):
    if not tasks:
        console.print("[dim]No tasks found.[/dim]")
        return

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", style="cyan")
    table.add_column("Due Date", style="green")
    table.add_column("Priority", style="red")
    table.add_column("Project", style="blue")
    table.add_column("Status", style="yellow")

    for task in tasks:
        due_str = task.due_date.strftime("%b %d, %Y") if task.due_date else "—"
        project_str = get_project_name(task.project_id, projects_cache)
        priority_str = get_priority_indicator(task.priority)
        table.add_row(task.id[:8], task.title, due_str, priority_str, project_str, task.status)

    console.print(table)

def print_timeline(entries):
    if not entries:
        console.print("[dim]No timeline entries.[/dim]")
        return

    console.print(Panel("[bold]Timeline[/bold]", expand=False))
    for entry in entries:
        time_str = entry.timestamp.strftime("%b %d · %H:%M")
        console.print(f"[dim]{time_str}[/dim] {entry.content}")

def print_done_confirmation(task):
    console.print(f"[green]✓[/green] Task marked as done: {getattr(task, 'title', 'Unknown')}")

def print_projects(projects):
    if not projects:
        console.print("[dim]No projects found.[/dim]")
        return

    table = Table(title=" Projects", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Name", style="cyan")
    table.add_column("Last Active", style="green")

    for project in projects:
        last_active = project.last_active.strftime("%b %d, %Y") if project.last_active else "—"
        table.add_row(project.id[:8], project.name, last_active)

    console.print(table)

def print_project_tasks(project, tasks):
    if not project:
        return

    table = Table(title=f" Project: {project.name}", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", style="cyan")
    table.add_column("Due Date", style="green")
    table.add_column("Status", style="yellow")

    for task in tasks:
        due_str = task.due_date.strftime("%b %d, %Y") if task.due_date else "—"
        table.add_row(task.id[:8], task.title, due_str, task.status)

    console.print(table)

def print_summary(data):
    date = data.get("date", datetime.now(timezone.utc))
    streak = data.get("streak", 0)
    mood_today = data.get("mood_today")
    avg_mood = data.get("avg_mood", 0)

    console.print(f"[bold] Today's Summary — {date.strftime('%b %d, %Y')}[/bold]")
    console.print(f"[bold]🔥 Streak:[/bold] {streak} days")

    if mood_today:
        mood_str = mood_today.mood
        console.print(f"[bold]😊 Mood Today:[/bold] {mood_str} ({mood_today.score}/5)")
    if avg_mood > 0:
        console.print(f"[bold]📈 7-day average:[/bold] {avg_mood}/5")

    console.print()

    timeline = data.get("timeline", [])
    console.print(f"[bold]Timeline ({len(timeline)} entries)[/bold]")
    if timeline:
        for entry in timeline:
            time_str = entry.timestamp.strftime("%H:%M")
            console.print(f"  [dim]{time_str}[/dim]  {entry.content}")
    else:
        console.print("  [dim]No entries today[/dim]")
    console.print()

    tasks = data.get("tasks_created", [])
    console.print(f"[bold]Tasks Created Today ({len(tasks)})[/bold]")
    if tasks:
        for task in tasks:
            due_str = f" (due {task.due_date.strftime('%b %d')})" if task.due_date else ""
            console.print(f"  • {task.title}{due_str}")
    else:
        console.print("  [dim]No tasks created today[/dim]")
    console.print()

    tasks_done = data.get("tasks_done", [])
    console.print(f"[bold]Tasks Completed Today ({len(tasks_done)})[/bold]")
    if tasks_done:
        for task in tasks_done:
            console.print(f"  • {task.title}")
    else:
        console.print("  [dim]No tasks completed today[/dim]")
    console.print()

    projects = data.get("projects", [])
    console.print(f"[bold]Projects Active Today ({len(projects)})[/bold]")
    if projects:
        for project in projects:
            console.print(f"  • {project.name}")
    else:
        console.print("  [dim]No projects active today[/dim]")

def print_weekly_summary(data):
    start_date = data.get("start_date", datetime.now(timezone.utc).date())
    end_date = data.get("end_date", datetime.now(timezone.utc).date())
    console.print(f"[bold] Weekly Summary — {start_date} to {end_date}[/bold]")
    console.print()

    timeline = data.get("timeline", [])
    tasks_created = data.get("tasks_created", [])
    tasks_done = data.get("tasks_done", [])
    projects = data.get("projects", [])
    most_active = data.get("most_active_project")

    console.print(f"[bold]Stats:[/bold]")
    console.print(f"  Timeline entries: {len(timeline)}")
    console.print(f"  Tasks created: {len(tasks_created)}")
    console.print(f"  Tasks completed: {len(tasks_done)}")
    console.print(f"  Projects active: {len(projects)}")
    if most_active:
        console.print(f"  Most active project: {most_active.name}")

def print_search_results(query, results):
    console.print(f"[bold]🔍 Search:[/bold] \"{query}\"")
    console.print()

    tasks = [(r[0], r[1]) for r in results if r[0] == "task"]
    timeline = [(r[0], r[1]) for r in results if r[0] == "timeline"]

    if tasks:
        console.print("[bold]Tasks:[/bold]")
        for _, task in tasks:
            project_str = f" (Project: {task.project_id[:8] if task.project_id else '—'})"
            console.print(f"  • {task.title}{project_str}")
    else:
        console.print("[bold]Tasks:[/bold]  [dim]No matches[/dim]")

    if timeline:
        console.print()
        console.print("[bold]Timeline:[/bold]")
        for _, entry in timeline:
            time_str = entry.timestamp.strftime("%b %d · %H:%M")
            console.print(f"  [dim]{time_str}[/dim]  {entry.content}")
    else:
        console.print()
        console.print("[bold]Timeline:[/bold]  [dim]No matches[/dim]")

def print_mood_history(mood_by_day):
    console.print("[bold] Mood — Last 7 Days[/bold]")
    if not mood_by_day:
        console.print("[dim]No mood data yet[/dim]")
        return

    for day, score in mood_by_day.items():
        bar = "█" * score + "░" * (5 - score)
        console.print(f"{day}  {bar}  {score}/5")

def print_report(md):
    console.print(md)

def print_chat(question, answer):
    console.print(f"[bold]❯ life chat[/bold] \"{question}\"")
    console.print()
    console.print(answer)
