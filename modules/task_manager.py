import json
from pathlib import Path
from datetime import datetime

from pathlib import Path
from datetime import datetime

TASKS_FILE = Path("data/tasks.json")


TASKS_FILE = Path("data/tasks.json")

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.initialize_data_dir()

    def initialize_data_dir(self):
        """Ensure data directory exists"""
        TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not TASKS_FILE.exists():
            with open(TASKS_FILE, 'w') as f:
                json.dump([], f)
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from file"""
        try:
            with open(TASKS_FILE, 'r') as f:
                self.tasks = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.tasks = []

    def save_tasks(self):
        """Save tasks to file"""
        with open(TASKS_FILE, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def create_task(self, description, creator, eddies_value, difficulty):
        """Create task with eddie rewards"""
        task = {
            "id": len(self.tasks) + 1,
            "description": description,
            "creator": creator,
            "value": {
                "eddies": eddies_value,
                "difficulty": difficulty
            },
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "completed_by": None
        }
        self.tasks.append(task)
        self.save_tasks()
        return task

    def create_task(self, description, creator, toki_value, eddies_value, difficulty):
        """Create task with user-defined values"""
        task = {
            "id": len(self.tasks) + 1,
            "description": description,
            "creator": creator,
            "value": {
                "toki": toki_value,
                "eddies": eddies_value,
                "difficulty": difficulty
            },
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "completed_by": None
        }
        self.tasks.append(task)
        self.save_tasks()
        return task

    def get_all_tasks(self):
        """Get all open tasks"""
        return [t for t in self.tasks if t['status'] == 'open']

    def complete_task(self, task_id, username):
        """Mark task as completed"""
        for task in self.tasks:
            if task['id'] == task_id and task['status'] == 'open':
                task['status'] = 'completed'
                task['completed_by'] = username
                self.save_tasks()
                return task['value']
        return None