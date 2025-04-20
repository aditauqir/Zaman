import curses
import json
import hashlib
import os
from pathlib import Path

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
STATS_DIR = DATA_DIR / "stats"

def initialize_data_dir():
    """Create necessary directories and files with proper initialization"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(STATS_DIR, exist_ok=True)
    
    # Initialize users file if empty or invalid
    if not USERS_FILE.exists():
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    else:
        # Validate existing file
        try:
            with open(USERS_FILE, 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            with open(USERS_FILE, 'w') as f:
                json.dump({}, f)

def hash_password(password):
    """SHA-256 hashing with salt"""
    salt = "zaman_salt_"
    return hashlib.sha256((salt + password).encode()).hexdigest()

def register_user(stdscr, username, password):
    """Register new user with proper file locking"""
    try:
        # Read existing users
        with open(USERS_FILE, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = {}
        
        # Check if user exists
        if username in users:
            return False
            
        # Add new user
        users[username] = hash_password(password)
        
        # Write back to file
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        
        # Create user stats
        user_stats = {
            "toki_balance": 10,
            "eddie_balance": 500,
            "tasks_completed": 0
        }
        stats_path = STATS_DIR / f"{username}.json"
        with open(stats_path, 'w') as f:
            json.dump(user_stats, f)
            
        return True
        
    except Exception as e:
        with open('auth_errors.log', 'a') as f:
            f.write(f"Registration error: {str(e)}\n")
        return False

def verify_user(username, password):
    """Verify user credentials with error handling"""
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            return users.get(username) == hash_password(password)
    except:
        return False

class LoginUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(1)
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    
    def clear_screen(self):
        self.stdscr.clear()
        self.height, self.width = self.stdscr.getmaxyx()
    
    def show_login_screen(self):
        self.clear_screen()
        self.stdscr.addstr(0, 0, "ZAMAN NETWORK", curses.A_BOLD | curses.color_pair(1))
        self.stdscr.addstr(2, 0, "1. Login", curses.color_pair(1))
        self.stdscr.addstr(3, 0, "2. Register", curses.color_pair(1))
        self.stdscr.addstr(4, 0, "3. Exit", curses.color_pair(1))
        self.stdscr.refresh()
        
        while True:
            key = self.stdscr.getch()
            if key == ord('1'): return "login"
            if key == ord('2'): return "register"
            if key == ord('3'): return "exit"
    
    def get_credentials(self):
        self.clear_screen()
        self.stdscr.addstr(0, 0, "Username: ", curses.color_pair(1))
        curses.echo()
        username = self.stdscr.getstr(0, 10, 20).decode().strip()
        self.stdscr.addstr(1, 0, "Password: ", curses.color_pair(1))
        password = self.stdscr.getstr(1, 10, 20).decode().strip()
        curses.noecho()
        return username, password
    
    def show_message(self, msg, is_error=True):
        self.stdscr.addstr(5, 0, msg, curses.color_pair(2 if is_error else 1))
        self.stdscr.refresh()
        self.stdscr.getch()

def authenticate_user(stdscr):
    """Main authentication flow with error recovery"""
    initialize_data_dir()
    ui = LoginUI(stdscr)
    
    while True:
        try:
            choice = ui.show_login_screen()
            
            if choice == "exit":
                return False
                
            username, password = ui.get_credentials()
            
            if not username or not password:
                ui.show_message("Username/password cannot be empty!")
                continue
                
            if choice == "login":
                if verify_user(username, password):
                    return username
                ui.show_message("Invalid credentials!")
            elif choice == "register":
                if register_user(stdscr, username, password):
                    ui.show_message("Registration successful!", False)
                    return username
                ui.show_message("Username exists or registration failed!")
                
        except Exception as e:
            with open('auth_errors.log', 'a') as f:
                f.write(f"Auth error: {str(e)}\n")
            ui.show_message("System error - try again")