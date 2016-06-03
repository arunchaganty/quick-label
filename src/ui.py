#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The quicklabel UI
"""

import curses

class Canvas(object):
    """
    Contains a generic canvas upon which other windows are drawn.
    """

    def __init__(self):
        # Curses set up
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        self.LINES, self.COLS = self.stdscr.getmaxyx()

    def __enter__(self):
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        return self

    def  __exit__(self, type_, value, traceback):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

class MainApp(object):
    def __init__(self, canvas):
        self.window = curses.newwin(canvas.LINES, canvas.COLS)
        self.LINES = canvas.LINES
        self.COLS = canvas.COLS

        self.MID_COL = int(self.COLS/2)
        self.MID_LINE = int(self.LINES/2)

    def refresh(self):
        self.window.refresh()

    def draw_textlabel(self, y, x, text, center=False, flags=None):
        if center:
            x = x - int(len(text)/2)

        win_ = self.window.derwin(3, len(text)+2, y, x)
        if flags:
            win_.addstr(1, 1, text, flags)
        else:
            win_.addstr(1, 1, text)
        win_.border()

    def init(self):
        """
        Create the initial drawing items.
        """
        # Draw a border
        self.window.border()
        # Draw the tagline.
        self.draw_textlabel(0, self.MID_COL, "QuickLabel", center=True)

    def draw(self):
        pass

    def run(self):
        self.init()
        self.refresh()
        self.window.getkey()


def run():
    with Canvas() as canvas:
        app = MainApp(canvas)
        app.run()

if __name__ == "__main__":
    run()
