import typer
from rich.console import Console
from rich.table import Table 
from rich.prompt import Prompt
from rich.panel import Panel
from datetime import datetime
from typing import Optional
from models import Todo, TodoStatus, Priority
from database import (
    get_all_todos, 
    delete_todos, 
    insert_todos, 
    complete_todos, 
    update_todo,
    get_todos_by_status,
    mark_in_progress,
    get_todos_by_category,
    get_todos_by_priority,
    test_connection,
)

console = Console()
app = typer.Typer(help="Todolist CLI application for task management")

def display_error(message: str):
    """Display error message in red"""
    console.print(f"[red]Error:[/red] {message}")

def confirm_action(message: str) -> bool:
    """Confirm user action"""
    return typer.confirm(message)

@app.command()
def add(
    task: str = typer.Argument(..., help="Task description"),
    category: str = typer.Argument(..., help="Task category"),
    priority: int = typer.Option(3, "--priority", "-p", help="Priority: 1=High, 2=Medium, 3=Low"),
    due_date: str = typer.Option(None, "--due", "-d", help="Due date (YYYY-MM-DD)")
):
    """Add a new todo item."""
    try:
        # Validate priority before creating Todo
        if priority not in [1, 2, 3]:
            raise ValueError("Priority must be 1 (High), 2 (Medium), or 3 (Low)")
        
        # Create todo with validated priority
        console.print("[yellow]Adding new task...[/yellow]")
        todo = Todo(
            task=task,
            category=category,
            priority=priority,  # Pass as int
            due_date=due_date
        )
        
        if insert_todos(todo):
            console.print("[green]Task added successfully![/green]")
            show()
        else:
            console.print("[red]Failed to add task[/red]")
            
    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")

@app.command()
def delete(
    position: int = typer.Argument(..., help="Position of the task to delete")
):
    """Delete a todo item by position."""
    if confirm_action(f"Are you sure you want to delete task {position}?"):
        try:
            initial_count = len(get_all_todos())
            delete_todos(position-1)
            after_delete = len(get_all_todos())
            if after_delete == initial_count - 1:
                console.print("[green]Task deleted successfully![/green]")
                show()
            else:
                display_error("Failed to delete task: count mismatch")
        except Exception as e:
            display_error(f"Could not delete task: {str(e)}")

@app.command()
def update(
    position: int = typer.Argument(..., help="Position of the task to update"),
    task: Optional[str] = typer.Option(None, help="New task description"),
    category: Optional[str] = typer.Option(None, help="New category"),
    priority: Optional[int] = typer.Option(None, help="New priority level"),
    due_date: Optional[str] = typer.Option(None, help="New due date (YYYY-MM-DD)")
):
    """Update a todo item's details."""
    try:
        update_todo(position-1, task, category, priority, due_date)
        console.print("[green]Task updated successfully![/green]")
        show()
    except Exception as e:
        display_error(f"Could not update task: {str(e)}")

@app.command()
def complete(position: int):
    """Mark a todo item as complete."""
    try:
        complete_todos(position-1)  # Just call complete_todos directly
        console.print("[green]Task marked as complete![/green]")
        show()
    except Exception as e:
        display_error(str(e))


@app.command()
def progress(position: int):
    """Mark a todo item as in progress."""
    try:
        mark_in_progress(position-1)
        console.print("[green]Task marked as in progress![/green]")
        show()
    except Exception as e:
        display_error(str(e))

@app.command()
def list_by_status(
    status: str = typer.Argument(
        ..., 
        help="Status filter (todo/in-progress/done)"
    )
):
    """List todos filtered by status."""
    status_map = {
        "todo": TodoStatus.TODO,
        "in-progress": TodoStatus.IN_PROGRESS,
        "done": TodoStatus.COMPLETED
    }
    
    if status not in status_map:
        display_error(f"Invalid status. Use: {', '.join(status_map.keys())}")
        return
    
    tasks = get_todos_by_status(status_map[status])
    show_tasks(tasks, f"Tasks - {status.upper()}")

@app.command()
def list_by_category(category: str):
    """List todos filtered by category."""
    tasks = get_todos_by_category(category)
    if tasks is None:
        tasks = []
    show_tasks(tasks, f"Tasks in category: {category}")

@app.command()
def list_by_priority(priority: int):
    """List todos filtered by priority level."""
    try:
        tasks = get_todos_by_priority(Priority(priority))
        if tasks is None:
            tasks = []
        priority_name = Priority(priority).name
        show_tasks(tasks, f"Tasks with {priority_name} priority")
    except ValueError:
        display_error("Invalid priority level. Use 1 (High), 2 (Medium), or 3 (Low)")

def show_tasks(tasks, title="Todos"):
    """Display tasks in a formatted table."""
    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    console.print(f"[bold magenta]{title}[/bold magenta]")

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("#", style='dim', width=6)
    table.add_column("Task", min_width=20)
    table.add_column("Category", min_width=12)
    table.add_column("Priority", min_width=8)
    table.add_column("Status", min_width=12)
    table.add_column("Due Date", min_width=12)

    for idx, task in enumerate(tasks, start=1):
        status_emoji = {
            TodoStatus.TODO: "⏳",
            TodoStatus.IN_PROGRESS: "🔄",
            TodoStatus.COMPLETED: "✅"
        }.get(task.status, "❓")

        priority_color = {
            Priority.HIGH: "red",
            Priority.MEDIUM: "yellow",
            Priority.LOW: "green"
        }.get(task.priority, "white")

        due_date = task.due_date if task.due_date else "No due date"
        
        table.add_row(
            str(idx),
            task.task,
            f"[cyan]{task.category}[/cyan]",
            f"[{priority_color}]{task.priority.name}[/{priority_color}]",
            f"{status_emoji} {task.status.name}",
            due_date
        )
    
    console.print(table)

@app.command()
def show():
    """Display all todo items."""
    console.print("[yellow]Fetching tasks...[/yellow]")
    tasks = get_all_todos()
    console.print(f"[yellow]Found {len(tasks)} tasks[/yellow]")
    show_tasks(tasks)

@app.command()
def stats():
    """Show todo statistics."""
    tasks = get_all_todos()
    
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == TodoStatus.COMPLETED)
    in_progress = sum(1 for t in tasks if t.status == TodoStatus.IN_PROGRESS)
    todo = sum(1 for t in tasks if t.status == TodoStatus.TODO)
    
    console.print(Panel.fit(
        f"""[bold]Todo Statistics[/bold]
        
Total Tasks: {total}
Completed: {completed}
In Progress: {in_progress}
Todo: {todo}
        """,
        title="Statistics",
        border_style="blue"
    ))

@app.command()
def test():
    """Test database connection"""
    if test_connection():
        console.print("[green]Database connection successful![/green]")
    else:
        console.print("[red]Database connection failed![/red]")

if __name__ == "__main__":
    app()
