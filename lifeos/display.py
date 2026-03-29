from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

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

def print_tasks(tasks, title="Pending Tasks"):
    if not tasks:
        console.print("[dim]No tasks found.[/dim]")
        return

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", style="cyan")
    table.add_column("Due Date", style="green")
    table.add_column("Status", style="yellow")

    for task in tasks:
        due_str = task.due_date.strftime("%b %d, %Y") if task.due_date else "—"
        table.add_row(task.id[:8], task.title, due_str, task.status)

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