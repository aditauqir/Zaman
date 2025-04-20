import curses
from curses import textpad

class TaskUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
    def draw_input_box(self, y, prompt):
        """Draw labeled input box"""
        self.stdscr.addstr(y, 0, prompt)
        textpad.rectangle(self.stdscr, y+1, 0, y+3, self.width-2)
        self.stdscr.refresh()
        return y+2  # Return input line position

    def get_task_input(self, state):
        """Get task details from user"""
        try:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "CREATE NEW TASK", curses.A_BOLD)
            
            # Description
            desc_y = self.draw_input_box(2, "Task Description:")
            curses.echo()
            description = self.stdscr.getstr(desc_y, 1, 50).decode()  # Limit to 50 chars
            curses.noecho()
            if not description.strip():
                return None, None
                
            # Eddie Reward
            eddies_y = self.draw_input_box(5, "Eddie Reward (190-950):")
            curses.echo()
            eddies = int(self.stdscr.getstr(eddies_y, 1).decode())
            curses.noecho()
            
            return description, eddies
            
        except ValueError:
            return None, None
        except Exception:
            return None, None