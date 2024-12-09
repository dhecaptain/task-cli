import unittest
import os
from datetime import datetime, timedelta
from database import (
    create_table,
    create_indexes,
    insert_todos,
    get_all_todos,
    get_todo,
    delete_todos,
    update_todo,
    complete_todos,
    mark_in_progress,
    get_todos_by_status,
    get_todos_by_category,
    get_todos_by_priority,
    DatabaseConnection
)
from models import Todo, TodoStatus, Priority

class TestTodoCLI(unittest.TestCase):
    def setUp(self):
        """Set up test database before each test"""
        # Create a new database for testing
        self.db_name = 'test_todos.db'
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        with DatabaseConnection(self.db_name) as conn:
            create_table()
            create_indexes()
        
        # Create sample todos for testing
        self.test_todos = [
            Todo(
                task="Test Django REST API",
                category="Programming",
                priority=Priority.HIGH,
                due_date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            ),
            Todo(
                task="Study Linear Algebra",
                category="Mathematics",
                priority=Priority.MEDIUM,
                due_date=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            )
        ]
        
        # Insert test todos
        for todo in self.test_todos:
            insert_todos(todo)
            print(f"Inserted todo: {todo.__dict__}")

        # Debug: Print all todos after insertion
        all_todos = get_all_todos()
        print("Todos after insertion:")
        for todo in all_todos:
            print(todo.__dict__)

    def tearDown(self):
        """Clean up after each test"""
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    def test_add_todo(self):
        """Test adding a new todo"""
        initial_count = len(get_all_todos())
        new_todo = Todo(
            task="Learn TensorFlow",
            category="AI",
            priority=Priority.HIGH,
            due_date=(datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
        )
        result = insert_todos(new_todo)
        self.assertTrue(result)
        
        todos = get_all_todos()
        self.assertEqual(len(todos), initial_count + 1)
        self.assertEqual(todos[-1].task, "Learn TensorFlow")

    def test_delete_todo(self):
        """Test deleting a todo"""
        initial_count = len(get_all_todos())
        delete_todos(0)  # Delete first todo
        after_delete = len(get_all_todos())
        self.assertEqual(after_delete, initial_count - 1)

    def test_update_todo(self):
        """Test updating a todo"""
        new_task = "Updated Task"
        new_category = "Updated Category"
        update_todo(0, task=new_task, category=new_category)
        
        updated_todo = get_todo(0)
        self.assertEqual(updated_todo.task, new_task)
        self.assertEqual(updated_todo.category, new_category)

    def test_complete_todo(self):
        """Test marking a todo as complete"""
        complete_todos(0)
        todo = get_todo(0)
        self.assertEqual(todo.status, TodoStatus.COMPLETED)

    def test_mark_in_progress(self):
        """Test marking a todo as in progress"""
        """Clean up after each test"""
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    def test_add_todo(self):
        """Test adding a new todo"""
        initial_count = len(get_all_todos())
        new_todo = Todo(
            task="Learn TensorFlow",
            category="AI",
            priority=Priority.HIGH,
            due_date=(datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
        )
        result = insert_todos(new_todo)
        self.assertTrue(result)
        
        todos = get_all_todos()
        self.assertEqual(len(todos), initial_count + 1)
        self.assertEqual(todos[-1].task, "Learn TensorFlow")

    def test_delete_todo(self):
        """Test deleting a todo"""
        initial_count = len(get_all_todos())
        delete_todos(0)  # Delete first todo
        after_delete = len(get_all_todos())
        self.assertEqual(after_delete, initial_count - 1)

    def test_update_todo(self):
        """Test updating a todo"""
        new_task = "Updated Task"
        new_category = "Updated Category"
        update_todo(0, task=new_task, category=new_category)
        
        updated_todo = get_todo(0)
        self.assertEqual(updated_todo.task, new_task)
        self.assertEqual(updated_todo.category, new_category)

    def test_complete_todo(self):
        """Test marking a todo as complete"""
        complete_todos(0)
        todo = get_todo(0)
        self.assertEqual(todo.status, TodoStatus.COMPLETED)

    def test_mark_in_progress(self):
        """Test marking a todo as in progress"""
        mark_in_progress(0)
        todo = get_todo(0)
        self.assertEqual(todo.status, TodoStatus.IN_PROGRESS)

    def test_get_todos_by_status(self):
        """Test filtering todos by status"""
        mark_in_progress(0)
        in_progress_todos = get_todos_by_status(TodoStatus.IN_PROGRESS)
        self.assertEqual(len(in_progress_todos), 1)

    def test_get_todos_by_category(self):
        """Test filtering todos by category"""
        programming_todos = get_todos_by_category("Programming")
        print(f"Number of programming todos: {len(programming_todos)}")
        self.assertEqual(len(programming_todos), 1)
        self.assertEqual(programming_todos[0].category, "Programming")

    def test_get_todos_by_priority(self):
        """Test filtering todos by priority"""
