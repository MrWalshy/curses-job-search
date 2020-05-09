import curses
from curses import textpad
from curses.textpad import Textbox, rectangle
import requests
from bs4 import BeautifulSoup

menu = ['Search', 'Saved', 'Exit']
URL_MONSTER = 'https://www.monster.co.uk/jobs/search/'
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

        # Highlight current menu item
        if i == current_item:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            # Add menu item to stdscr without highlighting
            stdscr.addstr(y, x, row)
    stdscr.refresh()

def build_url_string(base_url, keyword, location):
    query = f'?q={keyword}&where={location}'
    query_string = base_url + query
    query_string = query_string.replace(' ', '')
    return query_string

def monster_job_iterator(stdscr, job_elements):
    job_list = []

    for job_element in job_elements:
        title_element = job_element.find('h2', class_='title')
        company_element = job_element.find('div', class_='company')
        location_element = job_element.find('div', class_='location')

        # If job element is 'None', i.e. erroneous data
        if None in (title_element, company_element, location_element):
            # Skip this iteration
            continue

        title = title_element.text.strip()
        company = company_element.text.strip()
        location = location_element.text.strip()
        link = title_element.find('a')['href']

        job_list.append([title, company, location, link])
    return job_list

def open_search(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    draw_border(stdscr)

    # Menu setup
    stdscr.addstr((h//2)-2, w//4, 'Job Search Wizard')
    stdscr.addstr(h//2, w//4, 'Job Keyword: ')
    stdscr.addstr((h//2)+1, w//4, 'Location: ')

    keyword_win = curses.newwin(1, 24, (h//2), w//4+len('Job Keyword: '))
    location_win = curses.newwin(1, 24, (h//2)+1, w//4+len('Location: '))
    stdscr.refresh()

    # Get user input
    curses.curs_set(1)
    keyword_box = Textbox(keyword_win)
    keyword_box.edit()
    keyword = keyword_box.gather()

    location_box = Textbox(location_win)
    location_box.edit()
    location = location_box.gather()
    curses.curs_set(0)

    # Get results from job board
    # 1. Build query url, perform HTTP request
    query_url = build_url_string(URL_MONSTER, keyword, location)
    page = requests.get(query_url)
    
    # 2. Instantiate BS object for HTML, get search results
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id='SearchResults')

    # 3. Get only job postings, find_all() returns an iterable
    job_elements = results.find_all('section', class_='card-content')

    # 4. Iterate over job element BS objects
    job_list = monster_job_iterator(stdscr, job_elements)

    for job in job_list:
        title, company, location, link = job

        stdscr.clear()
        draw_border(stdscr)
        stdscr.addstr(2, 4, f'Role    : {title}')
        stdscr.addstr(3, 4, f'Company : {company}')
        stdscr.addstr(4, 4, f'Location: {location}')
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(5, 4, f'Link    : {link}')
        stdscr.attroff(curses.color_pair(3))
        stdscr.refresh()
        stdscr.getch()

    stdscr.getch()

def draw_border(stdscr):
    h, w = stdscr.getmaxyx()
    box_ul = [1, 3]
    box_lr = [h-1, w-3]
    textpad.rectangle(stdscr, uly=box_ul[0], ulx=box_ul[1],
                              lry=box_lr[0], lrx=box_lr[1])
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
                open_search(stdscr)

curses.wrapper(main)