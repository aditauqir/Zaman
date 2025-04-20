import curses
from curses import textpad

class BrowseTasks:
    def __init__(self, stdscr, task_manager, state):
        self.stdscr = stdscr
        self.task_manager = task_manager
        self.state = state  # Store the full AppState object
        self.scroll_pos = 0
        self.init_colors()

    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)

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
        tasks = self.task_manager.get_all_tasks()
        max_y, max_x = self.stdscr.getmaxyx()
        task_limit = max_y - 5  # Space for header/footer

        while True:
            self.stdscr.clear()
            
            # Header
            self.safe_addstr(0, 0, "TASK MARKETPLACE (↑/↓ Scroll, Enter: Select, Q: Quit)", 
                           curses.color_pair(1) | curses.A_BOLD)
            self.safe_addstr(1, 0, f"Your Balance: {self.state.eddie_balance} eddies", 
                           curses.color_pair(1))

            # Display tasks
            for i in range(task_limit):
                task_idx = i + self.scroll_pos
                if task_idx >= len(tasks):
                    break

                task = tasks[task_idx]
                y_pos = 3 + i
                self.safe_addstr(y_pos, 0, 
                               f"{task['id']}. {task['description']}",
                               curses.color_pair(4))
                self.safe_addstr(y_pos, max_x//2,
                               f"Reward: {task['reward']} eddies | {task['creator']}",
                               curses.color_pair(4))

            # Footer
            self.safe_addstr(max_y-2, 0, 
                           f"Showing {min(len(tasks), self.scroll_pos+1)}-{min(len(tasks), self.scroll_pos+task_limit)} of {len(tasks)}",
                           curses.color_pair(3))
            self.safe_addstr(max_y-1, 0, "↑/↓: Scroll | Enter: Select | Q: Quit", 
                           curses.color_pair(3))

            key = self.stdscr.getch()

            if key == curses.KEY_UP and self.scroll_pos > 0:
                self.scroll_pos -= 1
            elif key == curses.KEY_DOWN and self.scroll_pos < max(0, len(tasks)-task_limit):
                self.scroll_pos += 1
            elif key == ord('q'):
                break
            elif key == 10:  # Enter key
                self._handle_task_selection(tasks)
            elif key == curses.KEY_RESIZE:
                max_y, max_x = self.stdscr.getmaxyx()
                curses.resizeterm(max_y, max_x)

    
    def _handle_task_selection(self, tasks):
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Clear the input line
        self.safe_addstr(max_y-1, 0, " " * max_x, curses.color_pair(3))
        self.safe_addstr(max_y-1, 0, "Enter task ID to complete: ", curses.color_pair(3))
        
        curses.echo()
        task_id_str = self.stdscr.getstr(max_y-1, 24, 3).decode().strip()
        curses.noecho()

        if not task_id_str:
            return

        try:
            task_id = int(task_id_str)
            selected_task = next((t for t in tasks if t['id'] == task_id), None)
            
            if not selected_task:
                self.safe_addstr(max_y-2, 0, "Task not found!", curses.color_pair(5))
                self.stdscr.getch()
                return
                
            if selected_task['creator'] == self.state.username:
                # User is trying to complete their own task
                self.safe_addstr(max_y-2, 0, "Cannot complete your own task!", curses.color_pair(5))
                self.safe_addstr(max_y-3, 0, "Find tasks created by others", curses.color_pair(3))
                self.stdscr.getch()
                return
                
            reward = self.task_manager.complete_task(task_id, self.state.username)
            
            if reward:
                self.state.eddie_balance += reward
                self.state.save_stats()
                msg = f"Completed! Earned {reward} eddies (Press any key)"
                self.safe_addstr(max_y-2, 0, msg, curses.color_pair(2))
                self.stdscr.getch()
                
        except ValueError:
            self.safe_addstr(max_y-2, 0, "Invalid task ID!", curses.color_pair(5))
            self.stdscr.getch()