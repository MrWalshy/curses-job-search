import curses
from curses import textpad
from curses.textpad import Textbox, rectangle
import requests
from bs4 import BeautifulSoup

from . import utilities

URLS = {
    'monster': 'https://www.monster.co.uk/jobs/search/'
}
search_menu = ['Job Keyword: ',
               '   Location: ', '      SEARCH      ']

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

def print_search_menu(stdscr, menu, current_item):
    for i, item in enumerate(menu):
        h, w = stdscr.getmaxyx()
        y = h//2 + i
        x = w//4

        if i == current_item:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, item)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, item)

def open_search(stdscr):
    current_item = 0
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    utilities.draw_border(stdscr)
    
    # Menu setup
    stdscr.addstr((h//2)-2, w//4, 'Job Search Wizard')
    print_search_menu(stdscr, search_menu, current_item)

    keyword_win = curses.newwin(1, 24, (h//2), w//4+len('Job Keyword: '))
    location_win = curses.newwin(1, 24, (h//2)+1, w//4+len('   Location: '))
    stdscr.refresh()

    # Get user input
    while True:
        print_search_menu(stdscr, search_menu, current_item)
        key = stdscr.getch()
        if key == curses.KEY_UP and current_item > 0:
            current_item -= 1
        elif key == curses.KEY_DOWN and current_item < 2:
            current_item += 1
        elif key == curses.KEY_ENTER or key in [10,13]:
            if current_item == 0:
                curses.curs_set(1)
                keyword_box = Textbox(keyword_win)
                keyword_box.edit()
                keyword = keyword_box.gather()
                curses.curs_set(0)
            elif current_item == 1:
                curses.curs_set(1)
                location_box = Textbox(location_win)
                location_box.edit()
                location = location_box.gather()
                curses.curs_set(0)
            elif current_item == 2:
                break

    # Get results from job board
    # 1. Build query url, perform HTTP request
    query_list = []
    for company, url in URLS.items():
        query_list.append(url)
    stdscr.clear()
    for i, query in enumerate(query_list):
        stdscr.addstr(i, 0, query)
    stdscr.refresh()
    stdscr.getch()

    query_url = build_url_string(URLS.get('monster'), keyword, location)
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
        utilities.draw_border(stdscr)
        stdscr.addstr(2, 4, f'Role    : {title}')
        stdscr.addstr(3, 4, f'Company : {company}')
        stdscr.addstr(4, 4, f'Location: {location}')
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(5, 4, f'Link    : {link}')
        stdscr.attroff(curses.color_pair(3))
        stdscr.refresh()
        stdscr.getch()

    stdscr.getch()