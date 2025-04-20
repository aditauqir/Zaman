#!/usr/bin/env python3
import curses
from auth import authenticate_user
from modules.ui import ZamanUI
from modules.state import AppState

def main(stdscr):
    while True:
        # Login screen
        username = authenticate_user(stdscr)
        if not username:
            break
            
        # Main application
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