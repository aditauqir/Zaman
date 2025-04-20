import curses
from curses import textpad
import json

class ZamanUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = self.stdscr.getmaxyx()
        curses.curs_set(0)  # Hide cursor
        curses.noecho()     # Don't echo key presses
        curses.cbreak()     # React to keys immediately
        self.stdscr.keypad(True)  # Enable special keys
        self.init_colors()
    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    
    def handle_resize(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.stdscr.clear()
        curses.resizeterm(self.height, self.width)
    
    def safe_addstr(self, y, x, text, attr=curses.A_NORMAL):
        """Safe string writing with boundary checking"""
        if y < 0 or x < 0 or y >= self.height or x >= self.width:
            return
        text = text[:self.width - x - 1]
        try:
            self.stdscr.addstr(y, x, text, attr)
        except:
            pass
    
    def render_main_menu(self, state):
        self.stdscr.clear()
        self.height, self.width = self.stdscr.getmaxyx()
        
        # Header with balances
        header = f"⏳ {state.toki_balance} toki  💳 {state.eddie_balance} eddie"
        header_x = max(0, self.width - len(header) - 1)
        self.safe_addstr(0, header_x, header, curses.color_pair(2))
        
        # Menu title
        self.safe_addstr(2, 0, f"ZAMAN NETWORK: {state.username}", curses.color_pair(1))
        
        # Menu options
        for idx, option in enumerate(state.menu_options):
            y = 4 + idx
            if y >= self.height - 2:
                break
                
            color = curses.color_pair(4)  # Green
            if idx == state.selected_option:
                color = curses.color_pair(3) | curses.A_REVERSE
            
            self.safe_addstr(y, 2, f"{idx+1}. {option}", color)
        
        # Instructions at bottom
        instr_y = min(self.height - 1, 10)
        self.safe_addstr(instr_y, 0, "↑↓: Navigate  ENTER: Select", curses.color_pair(2))
        
        self.stdscr.refresh()
    
    def get_numeric_input(self, prompt):
        """Get numeric input from user"""
        self.stdscr.addstr(self.height-3, 0, prompt, curses.color_pair(6))
        curses.echo()
        curses.curs_set(1)
        input_str = self.stdscr.getstr(self.height-2, 0, 10).decode()
        curses.noecho()
        curses.curs_set(0)
        try:
            return int(input_str)
        except ValueError:
            return None
    
    def show_message(self, message, is_success=True):
        """Show status message"""
        color = curses.color_pair(4) if is_success else curses.color_pair(5)
        self.safe_addstr(self.height-4, 0, message, color)
        self.safe_addstr(self.height-2, 0, "Press any key to continue...", curses.color_pair(2))
        self.stdscr.getch()
    
    def handle_menu_selection(self, state):
        option = state.menu_options[state.selected_option]
        
        if option == "Earn Tokis":
            self.handle_earn_toki(state)
        elif option == "Cash Out Tokis":
            self.handle_cash_out(state)
        elif option == "Buy Tokis":
            self.handle_buy_toki(state)
        elif option == "View Ledger":
            self.view_ledger(state)
        elif option == "Logout":
            return "logout"
        return None

    def view_ledger(self, state):
        """Display transaction ledger"""
        self.stdscr.clear()
        try:
            with open(state.ledger_file, 'r') as f:
                ledger = json.load(f)
                
            self.safe_addstr(0, 0, "ZAMAN LEDGER", curses.A_BOLD | curses.color_pair(1))
            self.safe_addstr(2, 0, f"Total Fees Collected: {ledger['total_fees']}", curses.color_pair(2))
            
            row = 4
            for tx in reversed(ledger['transactions'][-10:]):  # Show last 10
                if row >= self.height - 2:
                    break
                
                tx_str = (f"{tx['timestamp'][:16]} | {tx['username']} | {tx['type']} | "
                         f"Amount: {tx['amount']} | Fee: {tx['fee']}")
                self.safe_addstr(row, 0, tx_str, curses.color_pair(3))
                row += 1
                
        except FileNotFoundError:
            self.safe_addstr(2, 0, "No ledger data found", curses.color_pair(5))
            
        self.safe_addstr(self.height-2, 0, "Press any key to continue...", curses.color_pair(2))
        self.stdscr.getch()
    
    def handle_earn_toki(self, state):
        self.stdscr.clear()
        self.render_main_menu(state)
        
        amount = self.get_numeric_input("Enter tokis earned (2-3 per task):")
        if amount is None:
            self.show_message("Invalid amount! Must be a number", False)
            return
        
        success, message = state.earn_toki(amount)
        self.show_message(message, success)
    
    def handle_cash_out(self, state):
        self.stdscr.clear()
        self.render_main_menu(state)
        
        amount = self.get_numeric_input("Enter tokis to cash out (1 toki = 190 eddies):")
        if amount is None:
            self.show_message("Invalid amount! Must be a number", False)
            return
        
        success, message = state.cash_out(amount)
        self.show_message(message, success)
    
    def handle_buy_toki(self, state):
        self.stdscr.clear()
        self.render_main_menu(state)
        
        amount = self.get_numeric_input("Enter tokis to buy (190 eddies = 1 toki):")
        if amount is None:
            self.show_message("Invalid amount! Must be a number", False)
            return
        
        success, message = state.buy_toki(amount)
        self.show_message(message, success)
    
    def handle_create_task(self, state):
        """Handle task creation flow"""
        self.stdscr.clear()
        self.render_main_menu(state)
        
        self.safe_addstr(12, 0, "Enter task description:", curses.color_pair(4))
        curses.echo()
        curses.curs_set(1)
        description = self.stdscr.getstr(13, 0, 100).decode()
        curses.noecho()
        curses.curs_set(0)
        
        if not description:
            self.show_message("Task description cannot be empty!", False)
            return
        
        # Get AI estimation
        self.safe_addstr(15, 0, "Estimating task value with AI...", curses.color_pair(2))
        self.stdscr.refresh()
        
        task = state.create_task(description)
        msg = (
            f"Task created!\n"
            f"Reward: {task['value']['toki']} toki ({task['value']['eddies']} eddies)\n"
            f"Difficulty: {task['value']['difficulty']}"
        )
        self.show_message(msg, True)
    
    def handle_browse_tasks(self, state):
        """Display available tasks"""
        self.stdscr.clear()
        tasks = state.get_available_tasks()
        
        self.safe_addstr(0, 0, "AVAILABLE TASKS", curses.A_BOLD | curses.color_pair(1))
        
        if not tasks:
            self.safe_addstr(2, 0, "No tasks available currently", curses.color_pair(3))
        else:
            for idx, task in enumerate(tasks[:10]):  # Show first 10 tasks
                y = 2 + idx
                task_str = (
                    f"{task['id']}. {task['description']}\n"
                    f"   Reward: {task['value']['toki']} toki | "
                    f"Difficulty: {task['value']['difficulty']} | "
                    f"Posted by: {task['creator']}"
                )
                self.safe_addstr(y, 0, task_str, curses.color_pair(4))
        
        self.safe_addstr(self.height-3, 0, "Enter task ID to complete (or 0 to cancel):", curses.color_pair(6))
        task_id = self.get_numeric_input("Task ID:")
        
        if task_id == 0:
            return
        elif task_id:
            success, message = state.complete_task(task_id)
            self.show_message(message, success)
    
    def handle_menu_selection(self, state):
        option = state.menu_options[state.selected_option]
        
        if option == "Earn Tokis":
            self.handle_browse_tasks(state)  # Changed from direct earning to task completion
        elif option == "Create Task":
            self.handle_create_task(state)
        elif option == "Browse Tasks":
            self.handle_browse_tasks(state)