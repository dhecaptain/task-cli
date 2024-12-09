# task-cli


```markdown
# Advanced Todo CLI Application

A powerful command-line interface (CLI) todo application built with Python, featuring priority levels, categories, due dates, and status tracking. This project demonstrates clean code architecture, SQLite database management, and modern Python practices.

## Features

- ✨ Task management with priorities (High, Medium, Low)
- 📂 Category organization
- 📅 Due date tracking
- 🔄 Status tracking (Todo, In Progress, Completed)
- 📊 Task statistics
- 🎨 Rich terminal interface with colored output
- 💾 Persistent storage using SQLite

## Requirements

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dhecaptain/task-cli.git
cd task-cli
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Commands

1. **Add a new task:**
```bash
python todocli.py add "Task description" "Category" --priority 1 --due "2024-12-31"
```
Priority levels:
- 1: High
- 2: Medium
- 3: Low (default)

2. **Show all tasks:**
```bash
python todocli.py show
```

3. **Complete a task:**
```bash
python todocli.py complete 1  # Complete task at position 1
```

4. **Mark task as in progress:**
```bash
python todocli.py progress 1  # Mark task 1 as in progress
```

5. **Delete a task:**
```bash
python todocli.py delete 1  # Delete task at position 1
```

### Advanced Commands

1. **Update task details:**
```bash
python todocli.py update 1 --task "New description" --category "New category" --priority 2 --due "2024-12-31"
```

2. **Filter tasks by status:**
```bash
python todocli.py list-by-status todo
python todocli.py list-by-status in-progress
python todocli.py list-by-status done
```

3. **Filter tasks by category:**
```bash
python todocli.py list-by-category "Study"
```

4. **Filter tasks by priority:**
```bash
python todocli.py list-by-priority 1  # Show high priority tasks
```

5. **View statistics:**
```bash
python todocli.py stats
```

## Project Structure

```
todo-cli/
├── todocli.py      # Main CLI application
├── database.py     # Database operations
├── models.py       # Data models and enums
├── requirements.txt
└── todos.db        # SQLite database file
```

## Database Schema

The application uses SQLite with the following table structure:

```sql
CREATE TABLE todos (
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
```

## Error Handling

The application includes comprehensive error handling for:
- Database operations
- Invalid input validation
- Priority and status constraints
- Date format validation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Dependencies

- typer: For creating the CLI interface
- rich: For terminal formatting and colors
- sqlite3: For database management
- python-dateutil: For date handling

## Development

To set up the development environment:

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Your Name
- GitHub: [@dhecaptain](https://github.com/dhecaptain)

## Acknowledgments

- Inspired by modern task management applications
- Built with Python best practices and clean architecture principles
```
