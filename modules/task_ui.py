import curses
from curses import textpad

class TaskUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
    def draw_selection_menu(self, y, options, selected_idx):
        """Draw a selectable menu"""
        for i, option in enumerate(options):
            attr = curses.A_REVERSE if i == selected_idx else curses.A_NORMAL
            self.stdscr.addstr(y+i, 0, f"{i+1}. {option}", attr)
        self.stdscr.refresh()
    
    def get_eddies_input(self, y, min_eddies, max_eddies):
        """Get validated eddies input"""
        while True:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "CREATE NEW TASK", curses.A_BOLD)
            
            prompt = f"Eddie Reward ({min_eddies}-{max_eddies}):"
            input_y = self.draw_input_box(y, prompt)
            
            curses.echo()
            try:
                value = int(self.stdscr.getstr(input_y, 1).decode())
                if min_eddies <= value <= max_eddies:
                    curses.noecho()
                    return value
                self.stdscr.addstr(y+4, 0, f"Must be between {min_eddies}-{max_eddies}", curses.color_pair(3))
            except ValueError:
                self.stdscr.addstr(y+4, 0, "Must be a number", curses.color_pair(3))
            finally:
                curses.noecho()
            self.stdscr.getch()
    
    def get_difficulty(self, y):
        """Difficulty selection menu"""
        difficulties = ["easy", "medium", "hard"]
        selected = 0
        
        while True:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "CREATE NEW TASK", curses.A_BOLD)
            self.stdscr.addstr(y, 0, "Select difficulty:")
            self.draw_selection_menu(y+1, difficulties, selected)
            
            key = self.stdscr.getch()
            if key == curses.KEY_UP:
                selected = max(0, selected-1)
            elif key == curses.KEY_DOWN:
                selected = min(2, selected+1)
            elif key == 10:  # Enter
                return difficulties[selected]
            elif key == 27:  # ESC
                return None
    
    def get_task_input(self, state):
        """Full task creation dialog"""
        try:
            # Description
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "CREATE NEW TASK", curses.A_BOLD)
            desc_y = self.draw_input_box(2, "Task Description:")
            curses.echo()
            description = self.stdscr.getstr(desc_y, 1).decode()
            curses.noecho()
            if not description:
                return None, None, None
            
            # Eddies
            ranges = state.get_task_rewards_range()
            eddies = self.get_eddies_input(5, ranges['min_eddies'], ranges['max_eddies'])
            
            # Difficulty
            difficulty = self.get_difficulty(8)
            if not difficulty:
                return None, None, None
            
            return description, eddies, difficulty
        except Exception:
            return None, None, None