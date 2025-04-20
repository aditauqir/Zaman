#!/usr/bin/env python3
import curses
import sys
from pathlib import Path

# Add project directory to Python path
sys.path.append(str(Path(__file__).parent))

from modules.ui import ZamanUI
from modules.state import AppState
from auth import authenticate_user

def main(stdscr):
    # Initialize curses properly
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)
    
    while True:
        username = authenticate_user(stdscr)
        if not username:
            break
            
        state = AppState(username)
        ui = ZamanUI(stdscr)
        
        while True:
            try:
                ui.render_main_menu(state)
                key = stdscr.getch()
                
                if key == curses.KEY_UP:
                    state.nav_up()
                elif key == curses.KEY_DOWN:
                    state.nav_down()
                elif key == 10:  # Enter key
                    result = ui.handle_menu_selection(state)
                    if result == "logout":
                        break
                elif key == curses.KEY_RESIZE:
                    ui.handle_resize()
                    
            except Exception as e:
                with open('error.log', 'a') as f:
                    f.write(f"Error: {str(e)}\n")
                break

if __name__ == "__main__":
    curses.wrapper(main)