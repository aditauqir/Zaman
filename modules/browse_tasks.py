# browse_tasks.py
import curses
from datetime import datetime

class BrowseTasks:
    def __init__(self, stdscr, task_manager, user_state):
        self.stdscr = stdscr
        self.task_manager = task_manager
        self.user_state = user_state
        self.init_colors()
        
    def init_colors(self):
        """Initialize color pairs specific to task browsing"""
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Header
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Success
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Instructions
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Task text

    def safe_addstr(self, y, x, text, attr=curses.A_NORMAL):
        """Safe string writing with boundary checking"""
        max_y, max_x = self.stdscr.getmaxyx()
        if y < 0 or x < 0 or y >= max_y or x >= max_x:
            return
        text = text[:max_x - x - 1]
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass

    def display(self):
        """Main entry point - displays task interface"""
        while True:
            self.stdscr.clear()
            max_y, max_x = self.stdscr.getmaxyx()
            
            # Display header
            self.safe_addstr(0, 0, "TASK MARKETPLACE", curses.color_pair(1) | curses.A_BOLD)
            self.safe_addstr(1, 0, f"Your Eddie Balance: {self.user_state['eddie_balance']}", 
                           curses.color_pair(1))
            
            # Get and display tasks
            tasks = self.task_manager.get_all_tasks()
            if not tasks:
                self.safe_addstr(3, 0, "No available tasks - check back later!", curses.color_pair(4))
            else:
                for idx, task in enumerate(tasks[:10]):  # Show first 10 tasks
                    y_pos = 3 + (idx * 2)
                    self.safe_addstr(y_pos, 0, 
                                   f"{task['id']}. {task['description']}",
                                   curses.color_pair(4))
                    self.safe_addstr(y_pos+1, 4,
                                   f"Reward: {task['reward']} eddies | Creator: {task['creator']}",
                                   curses.color_pair(4))
            
            # Footer with instructions
            self.safe_addstr(max_y-3, 0, "Enter task ID to complete (0 to exit):", curses.color_pair(3))
            self.safe_addstr(max_y-2, 0, "> ", curses.color_pair(3))
            
            # Get input
            curses.echo()
            curses.curs_set(1)
            input_str = self.stdscr.getstr(max_y-2, 2, 3).decode().strip()
            curses.noecho()
            curses.curs_set(0)
            
            # Process input
            if not input_str:
                continue
                
            try:
                task_id = int(input_str)
            except ValueError:
                continue
                
            if task_id == 0:
                break
                
            if task_id > 0:
                self._complete_task(task_id)

    def _complete_task(self, task_id):
        """Handle task completion logic"""
        reward = self.task_manager.complete_task(task_id, self.user_state['username'])
        if reward:
            self.user_state['eddie_balance'] += reward
            self.stdscr.clear()
            self.safe_addstr(0, 0, f"Task completed! Earned {reward} eddies", curses.color_pair(2))
            self.safe_addstr(2, 0, "Press any key to continue...", curses.color_pair(3))
            self.stdscr.getch()