#!/usr/bin/env python3
import curses
from pathlib import Path
import sys
from modules.state import AppState
from modules.ui import ZamanUI
from modules.task_ui import TaskUI
from auth import authenticate_user

# Add project directory to Python path
sys.path.append(str(Path(__file__).parent))

def main(stdscr):
    # Initialize curses properly
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)  # Enable special keys
    curses.curs_set(0)   # Hide cursor
    
    # Color setup
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    
    while True:
        # Login screen
        username = authenticate_user(stdscr)
        if not username:
            break
            
        # Main application
        state = AppState(username)
        ui = ZamanUI(stdscr)
        task_ui = TaskUI(stdscr)
        
        while True:
            try:
                ui.render_main_menu(state)
                key = stdscr.getch()
                
                # Handle key presses
                if key == curses.KEY_UP:
                    state.nav_up()
                elif key == curses.KEY_DOWN:
                    state.nav_down()
                elif key == 10:  # Enter key
                    option = state.menu_options[state.selected_option]
                    
                    if option == "Create Task":
                        desc, eddies, diff = task_ui.get_task_input(state)
                        if desc:  # Only proceed if inputs were valid
                            valid, msg = state.validate_task_input(eddies, diff)
                            if valid:
                                task = state.task_manager.create_task(
                                    description=desc,
                                    creator=state.username,
                                    eddies_value=eddies,
                                    difficulty=diff
                                )
                                ui.show_message(f"Task #{task['id']} created!", True)
                            else:
                                ui.show_message(f"Invalid: {msg}", False)
                    
                    elif option == "Browse Tasks":
                        ui.handle_browse_tasks(state)
                    
                    elif option == "Cash Out Tokis":
                        ui.handle_cash_out(state)
                    
                    elif option == "Buy Tokis":
                        ui.handle_buy_toki(state)
                    
                    elif option == "Logout":
                        break
                
                elif key == curses.KEY_RESIZE:
                    ui.handle_resize()
                    
                elif key == 27:  # ESC key
                    break
                    
            except Exception as e:
                # Write full error to log file
                with open('error.log', 'a') as f:
                    import traceback
                    f.write(f"Error: {str(e)}\n{traceback.format_exc()}\n")
                ui.show_message("System error - check error.log", False)
                break

if __name__ == "__main__":
    curses.wrapper(main)