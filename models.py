from enum import Enum
from datetime import datetime
from typing import Optional, Union
from dataclasses import dataclass

class TodoStatus(Enum):
    """Enum for todo status with clear string representations"""
    TODO = 1
    IN_PROGRESS = 2
    COMPLETED = 3

    def __str__(self) -> str:
        return self.name.replace('_', ' ').title()


class Priority(Enum):
    """Enum for priority levels"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3

    @classmethod
    def from_value(cls, value: Union[int, str]) -> 'Priority':
        """Convert int or str to Priority"""
        try:
            if isinstance(value, str):
                value = int(value)
            if value not in [1, 2, 3]:
                raise ValueError("Priority must be 1 (High), 2 (Medium), or 3 (Low)")
            return cls(value)
        except (ValueError, TypeError):
            raise ValueError("Priority must be 1 (High), 2 (Medium), or 3 (Low)")


@dataclass
class Todo:
    task: str
    category: str
    date_added: Optional[str] = None
    date_completed: Optional[str] = None
    status: Optional[TodoStatus] = None
    position: Optional[int] = None
    due_date: Optional[str] = None
    priority: Optional[Priority] = None
    id: Optional[int] = None  # Add this line

    def __post_init__(self):
        """Validate and set default values after initialization"""
        if not self.task or not self.task.strip():
            raise ValueError("Task cannot be empty")

        # Set default values
        self.date_added = self.date_added or datetime.now().isoformat()
        self.status = TodoStatus.TODO if self.status is None else self.status

        # Handle priority conversion
        if isinstance(self.priority, (int, str)):
            try:
                priority_value = int(self.priority)
                if priority_value not in [1, 2, 3]:
                    raise ValueError("Priority must be 1 (High), 2 (Medium), or 3 (Low)")
                self.priority = Priority(priority_value)
            except (ValueError, TypeError):
                raise ValueError("Priority must be 1 (High), 2 (Medium), or 3 (Low)")
        elif self.priority is None:
            self.priority = Priority.LOW
   
    @property
    def is_completed(self) -> bool:
        """Check if todo is completed"""
        return self.status == TodoStatus.COMPLETED

    @property
    def is_overdue(self) -> bool:
        """Check if todo is overdue"""
        if not self.due_date:
            return False
        try:
            due = datetime.fromisoformat(self.due_date)
            return due < datetime.now() and not self.is_completed
        except ValueError:
            return False

    def mark_completed(self) -> None:
        """Mark todo as completed"""
        self.status = TodoStatus.COMPLETED
        self.date_completed = datetime.now().isoformat()

    def mark_in_progress(self) -> None:
        """Mark todo as in progress"""
        self.status = TodoStatus.IN_PROGRESS

    def update_priority(self, priority: Union[Priority, int, str]) -> None:
        """Update todo priority"""
        if isinstance(priority, int):
            try:
                self.priority = Priority(priority)
            except ValueError:
                raise ValueError(f"Invalid priority value: {priority}")
        elif isinstance(priority, str) and priority.isdigit():
            self.priority = Priority(int(priority))
        elif isinstance(priority, Priority):
            self.priority = priority
        else:
            raise TypeError("Priority must be an integer, string (digit), or Priority enum")

    def __str__(self) -> str:
        """String representation of todo item"""
        status_str = str(self.status)
        priority_str = self.priority.name if self.priority else 'LOW'
        return f"{self.task} ({self.category}) - {status_str} - Priority: {priority_str}"

    def to_dict(self) -> dict:
        """Convert todo to dictionary (useful for serialization)"""
        return {
            'task': self.task,
            'category': self.category,
            'date_added': self.date_added,
            'date_completed': self.date_completed,
            'status': self.status.value if self.status else None,
            'position': self.position,
            'due_date': self.due_date,
            'priority': self.priority.value if self.priority else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Todo':
        """Create todo from dictionary (useful for deserialization)"""
        return cls(**data)
