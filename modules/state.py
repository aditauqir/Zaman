import json
from pathlib import Path
from datetime import datetime

import json
from pathlib import Path
from datetime import datetime

from .task_manager import TaskManager

import json
from pathlib import Path
from datetime import datetime
from .task_manager import TaskManager  # Fixed relative import

class AppState:
    def __init__(self, username):
        self.username = username
        self.stats_file = Path("data") / "stats" / f"{username}.json"
        self.ledger_file = Path("data") / "zaman_ledger.json"
        self.task_manager = TaskManager()
        
        # Initialize balances
        self.toki_balance = 0
        self.eddie_balance = 0
        self.tasks_completed = 0
        self.transaction_history = []
        
        self.selected_option = 0
        self.menu_options = [
            "Cash Out Tokis",
            "Buy Tokis",
            "Create Task",
            "Browse Tasks",
            "Logout"
        ]
        
        self.load_stats()  # Load existing data

    def load_stats(self):
        try:
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
                self.toki_balance = stats.get("toki_balance", 10)  # Default 10 if not exists
                self.eddie_balance = stats.get("eddie_balance", 500)  # Default 500
                self.tasks_completed = stats.get("tasks_completed", 0)
                self.transaction_history = stats.get("transaction_history", [])
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_stats()  # Create new file with defaults

    def save_stats(self):
        stats = {
            "toki_balance": self.toki_balance,
            "eddie_balance": self.eddie_balance,
            "tasks_completed": self.tasks_completed,
            "transaction_history": self.transaction_history[-10:]
        }
        self.stats_file.parent.mkdir(exist_ok=True)
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f)
            
    def record_transaction(self, transaction_type, amount, fee=0):
        """Record transaction in Zaman's ledger"""
        with open(self.ledger_file, 'r+') as f:
            ledger = json.load(f)
            ledger["total_fees"] += fee
            ledger["transactions"].append({
                "username": self.username,
                "type": transaction_type,
                "amount": amount,
                "fee": fee,
                "timestamp": datetime.now().isoformat()
            })
            f.seek(0)
            json.dump(ledger, f)

    def cash_out(self, amount):
        """Convert tokis to eddies with 15% fee"""
        if amount <= 0:
            return False, "Amount must be positive"
        
        if self.toki_balance < amount:
            return False, "Insufficient tokis"
        
        fee = round(amount * 0.15, 2)
        eddies_earned = (amount - fee) * 190
        
        self.toki_balance -= amount
        self.eddie_balance += eddies_earned
        
        self.record_transaction("cash_out", amount, fee)
        self.save_stats()
        
        return True, (
            f"Converted {amount} toki → {eddies_earned} eddies\n"
            f"Fee: {fee} toki (15%)"
        )

    def buy_toki(self, amount):
        """Buy tokis with eddies with 15% fee"""
        if amount <= 0:
            return False, "Amount must be positive"
        
        base_cost = amount * 190
        fee = round(base_cost * 0.15, 2)
        total_cost = base_cost + fee
        
        if self.eddie_balance < total_cost:
            return False, "Insufficient eddies"
        
        self.eddie_balance -= total_cost
        self.toki_balance += amount
        
        self.record_transaction("buy", amount, fee)
        self.save_stats()
        
        return True, (
            f"Bought {amount} toki for {base_cost} eddies\n"
            f"+ {fee} eddies fee (15%)\n"
            f"Total: {total_cost} eddies"
        )

    # ... (keep existing nav_up/nav_down methods) ...
    
    def nav_up(self):
        self.selected_option = max(0, self.selected_option - 1)
    
    def nav_down(self):
        self.selected_option = min(len(self.menu_options) - 1, self.selected_option + 1)
        
    def create_task(self, description):
        """Create a new task"""
        return self.task_manager.create_task(description, self.username)
    
    def get_available_tasks(self):
        """Get list of available tasks"""
        return self.task_manager.get_all_tasks()
    
    def complete_task(self, task_id):
        """Mark task as completed and return reward"""
        task = next((t for t in self.task_manager.tasks 
                if t['id'] == task_id and t['status'] == 'open'), None)
        if task:
            task['status'] = 'completed'
            task['completed_by'] = self.username
            self.task_manager.save_tasks()
            return task['reward']
        return None
    
        # Add these methods to your AppState class
    def get_task_rewards_range(self):
        return {
            'min_eddies': 10,  
            'max_eddies': 950   # 5 toki worth
        }

    def validate_task_input(self, eddies):
        """Validate only eddie amount"""
        if not 10 <= eddies <= 950:
            return False, "Eddies must be between 10-950"
        return True, ""