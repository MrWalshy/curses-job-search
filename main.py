# CLI styling
import curses
from curses import textpad
from curses.textpad import Textbox, rectangle

# HTTP & Web Scraper
import requests
from bs4 import BeautifulSoup

from module_pkg import search
from module_pkg.utilities import draw_border

menu = ['Search', 'Saved', 'Exit']
logo_lines = ['''   ___         _       _____                          _     ''',
'''  |_  |       | |     /  ___|                        | |    ''',
'''    | |  ___  | |__   \ `--.   ___   __ _  _ __  ___ | |__  ''',
'''    | | / _ \ | '_ \   `--. \ / _ \ / _` || '__|/ __|| '_ \ ''',
'''/\__/ /| (_) || |_) | /\__/ /|  __/| (_| || |  | (__ | | | |''',
'''\____/  \___/ |_.__/  \____/  \___| \__,_||_|   \___||_| |_|'''
]

def print_menu(stdscr, current_item):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    draw_border(stdscr)

    # Draw logo
    logo_x, logo_y = 2, 4
    stdscr.attron(curses.color_pair(2))
    for logo_line in logo_lines:
        stdscr.addstr(logo_x, logo_y, logo_line)
        logo_x += 1
    stdscr.attroff(curses.color_pair(2))

    for i, row in enumerate(menu):
        # Get menu positions
        x = len(logo_lines[0]) + 6
        y = 5 + i

        if i == current_item:
            # Highlight current menu item
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            # Add menu item to stdscr without highlighting
            stdscr.addstr(y, x, row)
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    
    current_row = 0

    # Menu
    while True:
        print_menu(stdscr, current_row)

        key = stdscr.getch()
        stdscr.clear()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # Exit if last item 'Exit' is pressed
            if menu[current_row].lower() == 'exit':
                return False
            elif menu[current_row].lower() == 'search':
                search.open_search(stdscr)

curses.wrapper(main)
