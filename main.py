#!/usr/bin/env python3
import curses
from pathlib import Path
import sys
from modules.state import AppState
from modules.ui import ZamanUI
from modules.task_ui import TaskUI
from auth import authenticate_user
from modules.browse_tasks import BrowseTasks



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
                
                # Handle navigation keys
                if key == curses.KEY_UP:
                    state.nav_up()
                    continue
                elif key == curses.KEY_DOWN:
                    state.nav_down()
                    continue
                
                # Handle Enter key
                if key == 10:  # Enter key
                    option = state.menu_options[state.selected_option]
                    
                    if option == "Create Task":
                        if ui.handle_create_task(state):
                            # Only continue if task creation succeeded
                            continue

                    
                    elif option == "Browse Tasks":
                        browse_ui = BrowseTasks(stdscr, state.task_manager, {
                            'username': state.username,
                            'eddie_balance': state.eddie_balance
                        })
                        browse_ui.display()
                        continue
                    # ... handle other menu options ...
                    
                    elif option == "Logout":
                        break
                
                elif key == curses.KEY_RESIZE:
                    ui.handle_resize()
                
            except Exception as e:
                with open('error.log', 'a') as f:
                    import traceback
                    f.write(f"Error: {str(e)}\n{traceback.format_exc()}\n")
                ui.show_message("System error - check error.log", False)
                break

if __name__ == "__main__":
    curses.wrapper(main)