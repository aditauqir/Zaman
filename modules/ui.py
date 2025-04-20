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