import json
from pathlib import Path
import google.generativeai as genai
from datetime import datetime

TASKS_FILE = Path("data/tasks.json")

class TaskManager:
    def __init__(self):
        self.tasks = []
        self._initialize_files()
        genai.configure(api_key='AIzaSyAS8SpvO6SZa7Bx9gkg9bQCKCnP1Juqywg')  # Replace with your actual API key
        self.model = genai.GenerativeModel('gemini-pro')

    def _initialize_files(self):
        """Ensure data directory and tasks file exist"""
        TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not TASKS_FILE.exists():
            with open(TASKS_FILE, 'w') as f:
                json.dump([], f)
        else:
            self._load_tasks()

    def _load_tasks(self):
        """Load existing tasks from file"""
        with open(TASKS_FILE, 'r') as f:
            self.tasks = json.load(f)

    def _save_tasks(self):
        """Save tasks to file"""
        with open(TASKS_FILE, 'w') as f:
            json.dump(self.tasks, f)

    def estimate_task_value(self, task_description):
        """Use Gemini AI to estimate task value"""
        prompt = f"""
        Estimate the appropriate reward for this task in a time-based economy where:
        - 1 toki = 2 months of life extension
        - 1 toki = 190 eddies (currency)
        - Typical simple tasks earn 1-2 toki
        - Complex tasks earn 3-5 toki
        
        Task: {task_description}
        
        Respond ONLY with JSON format like this:
        {{
            "toki": number,
            "eddies": number,
            "difficulty": "easy/medium/hard"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"AI estimation failed: {e}")
            return {"toki": 1, "eddies": 190, "difficulty": "medium"}

    def create_task(self, task_description, creator):
        """Create a new task with AI-estimated value"""
        value = self.estimate_task_value(task_description)
        
        task = {
            "id": len(self.tasks) + 1,
            "description": task_description,
            "creator": creator,
            "value": value,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "completed_by": None
        }
        
        self.tasks.append(task)
        self._save_tasks()
        return task

    def get_all_tasks(self):
        """Return all available tasks"""
        return [t for t in self.tasks if t['status'] == 'open']

    def complete_task(self, task_id, username):
        """Mark a task as completed"""
        for task in self.tasks:
            if task['id'] == task_id and task['status'] == 'open':
                task['status'] = 'completed'
                task['completed_by'] = username
                self._save_tasks()
                return task['value']
        return None