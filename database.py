import sqlite3
from typing import List, Optional
import datetime
from functools import wraps
from models import Todo, TodoStatus,Priority
from rich.console import Console

console = Console()

class DatabaseConnection:
    """Context manager for database connections"""
    def __init__(self, db_name='todos.db'):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

def safe_database_operation(func):
    """Decorator for safe database operations with error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                return func(cursor, *args, **kwargs)
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    return wrapper

def validate_todo(todo: Todo) -> bool:
    """Validate todo item data before database operations"""
    if not todo.task or len(todo.task.strip()) == 0:
        raise ValueError("Task cannot be empty")
    if not isinstance(todo.status, TodoStatus):
        raise ValueError("Invalid status")
    if not isinstance(todo.priority, Priority):
        raise ValueError("Invalid priority")
    return True

def create_table():
    """Create the todos table if it doesn't exist"""
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        # Remove the DROP TABLE line
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                category TEXT NOT NULL,
                date_added TEXT NOT NULL,
                date_completed TEXT,
                status INTEGER NOT NULL,
                position INTEGER,
                due_date TEXT,
                priority INTEGER NOT NULL,
                CONSTRAINT status_check CHECK (status IN (1,2,3)),
                CONSTRAINT priority_check CHECK (priority IN (1,2,3))
            )
        """)
        conn.commit()

def create_indexes():
    """Create indexes for frequently queried columns"""
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON todos(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON todos(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_position ON todos(position)')
        conn.commit()

@safe_database_operation
def insert_todos(cursor, todo: Todo):
    """Insert a new todo item into the database"""
    try:
        if not validate_todo(todo):
            return False
        
        cursor.execute('SELECT COUNT(*) FROM todos')
        count = cursor.fetchone()[0]
        todo.position = count if count else 0

        # Store the enum's value instead of the enum itself
        priority_value = todo.priority.value if todo.priority else Priority.LOW.value

        cursor.execute('''
            INSERT INTO todos 
            (task, category, date_added, date_completed, status, position, due_date, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            todo.task,
            todo.category,
            todo.date_added,
            todo.date_completed,
            todo.status.value,  # Already using .value here, which is good
            todo.position,
            todo.due_date,
            priority_value  # Use the integer value instead of the enum
        ))
        cursor.connection.commit()
        return True
    except Exception as e:
        console.print(f"[red]Error inserting todo: {str(e)}[/red]")
        return False


@safe_database_operation
def get_all_todos(cursor) -> List[Todo]:
    """Retrieve all todos ordered by position"""
    try:
        cursor.execute('SELECT * FROM todos ORDER BY position')
        rows = cursor.fetchall()
        todos = []
        for row in rows:
            todo = Todo(
                task=row[1],
                category=row[2],
                date_added=row[3],
                date_completed=row[4],
                status=TodoStatus(row[5]),
                position=row[6],
                due_date=row[7],
                priority=Priority(row[8])
            )
            todos.append(todo)
        return todos
    except Exception as e:
        console.print(f"[red]Error fetching todos: {str(e)}[/red]")
        return []

@safe_database_operation
def delete_todos(cursor, position: int):
    """Delete a todo item and reorder remaining items"""
    cursor.execute('DELETE FROM todos WHERE position = ?', (position,))
    
    # Reorder remaining items
    cursor.execute('SELECT position FROM todos ORDER BY position')
    rows = cursor.fetchall()
    for i, (pos,) in enumerate(rows):
        cursor.execute('''
            UPDATE todos 
            SET position = ? 
            WHERE position = ?
        ''', (i, pos))
    cursor.connection.commit()

@safe_database_operation
def update_todo(cursor, position: int, task: Optional[str] = None, 
                category: Optional[str] = None, priority: Optional[int] = None,
                due_date: Optional[str] = None, status: Optional[int] = None):
    """Update todo item details"""
    updates = []
    params = {'position': position}

    if task is not None:
        updates.append('task = :task')
        params['task'] = task
    if category is not None:
        updates.append('category = :category')
        params['category'] = category
    if priority is not None:
        updates.append('priority = :priority')
        params['priority'] = priority
    if due_date is not None:
        updates.append('due_date = :due_date')
        params['due_date'] = due_date
    if status is not None:
        updates.append('status = :status')
        params['status'] = status

    if updates:
        query = f"UPDATE todos SET {', '.join(updates)} WHERE position = :position"
        cursor.execute(query, params)
        cursor.connection.commit()

@safe_database_operation
def complete_todos(cursor, position: int):
    """Mark a todo item as completed"""
    try:
        cursor.execute('''
            UPDATE todos 
            SET status = ?, date_completed = ? 
            WHERE position = ?
        ''', (TodoStatus.COMPLETED.value, 
              datetime.datetime.now().isoformat(), 
              position))
        cursor.connection.commit()
        # Add debug print
        print(f"Updated todo at position {position} to completed status")
        return True
    except Exception as e:
        print(f"Error completing todo: {e}")
        return False


@safe_database_operation
def mark_in_progress(cursor, position: int):
    """Mark a todo item as in progress"""
    cursor.execute('''
        UPDATE todos 
        SET status = ? 
        WHERE position = ?
    ''', (TodoStatus.IN_PROGRESS.value, position))
    cursor.connection.commit()

@safe_database_operation
def get_todos_by_status(cursor, status: TodoStatus) -> List[Todo]:
    """Retrieve todos filtered by status"""
    cursor.execute('SELECT * FROM todos WHERE status = ?', (status.value,))
    rows = cursor.fetchall()
    return [Todo(
        task=row[1],
        category=row[2],
        date_added=row[3],
        date_completed=row[4],
        status=TodoStatus(row[5]),
        position=row[6],
        due_date=row[7],
        priority=Priority(row[8])
    ) for row in rows]

@safe_database_operation
def get_todos_by_category(cursor, category: str) -> List[Todo]:
    """Retrieve todos filtered by category"""
    cursor.execute('SELECT * FROM todos WHERE category = ?', (category,))
    rows = cursor.fetchall()
    return [Todo(
        task=row[1],
        category=row[2],
        date_added=row[3],
        date_completed=row[4],
        status=TodoStatus(row[5]),
        position=row[6],
        due_date=row[7],
        priority=Priority(row[8])
    ) for row in rows]

@safe_database_operation
def get_todo(cursor, position: int) -> Optional[Todo]:
    """Retrieve a specific todo by position"""
    cursor.execute('SELECT * FROM todos WHERE position = ?', (position,))
    row = cursor.fetchone()
    if row:
        return Todo(
            task=row[1],
            category=row[2],
            date_added=row[3],
            date_completed=row[4],
            status=TodoStatus(row[5]),
            position=row[6],
            due_date=row[7],
            priority=Priority(row[8])
        )
    return None

@safe_database_operation
def get_todos_by_priority(cursor, priority: Priority) -> List[Todo]:
    """Retrieve todos filtered by priority level"""
    cursor.execute('SELECT * FROM todos WHERE priority = ?', (priority.value,))
    rows = cursor.fetchall()
    return [Todo(
        task=row[1],
        category=row[2],
        date_added=row[3],
        date_completed=row[4],
        status=TodoStatus(row[5]),
        position=row[6],
        due_date=row[7],
        priority=Priority(row[8])
    ) for row in rows]

def test_connection():
    try:
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

