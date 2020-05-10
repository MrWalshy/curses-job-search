import curses
from curses import textpad

def draw_border(stdscr):
    h, w = stdscr.getmaxyx()
    box_ul = [1, 3]
    box_lr = [h-1, w-3]
    textpad.rectangle(stdscr, uly=box_ul[0], ulx=box_ul[1],
                              lry=box_lr[0], lrx=box_lr[1])
    stdscr.refresh()