import json
from pathlib import Path
from datetime import datetime

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

    def create_task(self, description, creator, eddie_cost, user_balance):
        """Returns (success: bool, message: str, task: dict)"""
        if not isinstance(eddie_cost, int) or eddie_cost <= 0:
            return False, "Eddie cost must be a positive number", None
            
        if user_balance < eddie_cost:
            return False, f"Not enough eddies (Need {eddie_cost}, have {user_balance})", None
            
        task = {
            "id": len(self.tasks) + 1,
            "description": description,
            "creator": creator,
            "reward": eddie_cost,  # Using reward instead of eddies_value
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "completed_by": None
        }
    
        self.tasks.append(task)
        self.save_tasks()
        return True, f"Task created for {eddie_cost} eddies", task

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
                return task['reward']
        return None