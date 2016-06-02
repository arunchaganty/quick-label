#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Shell to edit a sequence.
"""

import csv
import sys
import curses

class EditShell(object):
    """
    Shell to make quick edits to a sentence.
    """
    def __init__(self, keys):
        # Curses set up
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        self.LINES, self.COLS = self.stdscr.getmaxyx()

        self.keys = keys


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

    def init_window(self):
        height, width = self.LINES, self.COLS

        # Create a new window.
        begin_y, begin_x = 0, 0
        win = curses.newwin(height, width, begin_y, begin_x)
        win.keypad(True)
        return win

    def render_sentence(self, win, sentence, tags, hl=None):
        """
        Renders the sentence and tags in the center of the screen, highlighting the word @hl in particular.

        @win - window
        @sentence - list[str]
        @tags - list[str]
        """

        lines, cols = win.getmaxyx()

        spacing = max(map(len, sentence + tags)) + 3
        total_len = spacing * len(sentence)

        l1y, l1x = lines / 2 - 1, cols/2 - total_len/2
        l2y, l2x = lines / 2 + 1, cols/2 - total_len/2

        for i, (word, tag) in enumerate(zip(sentence, tags)):
            # Highlight i

            if hl is not None and i == hl:
                flags = curses.color_pair(2) | curses.A_BOLD
            else:
                flags = curses.color_pair(1)

            win.addstr(l1y, l1x + i * spacing, word, flags)
            win.addstr(l2y, l2x + i * spacing, tag, flags)
        win.refresh()


    def run(self, sentence, tags):
        """
        Run correction shell on the sentence and tags.
        @return sentence, tags -- corrected versions.
        """
        win = self.init_window()

        i = 0 # Cursor position
        while i < len(sentence):
            self.render_sentence(win, sentence, tags, i)
            # Handle corrections
            # :  means meta-command, e.g. quit.
            cmd = win.getkey()

            # <ENTER> means everything is correct, next example.
            if cmd == '\n':
                return sentence, tags

            # <SPACE> means current element is correct, next token.
            elif cmd == ' ':
                i += 1

            # <BACKSPACE> means move to previous token.
            elif cmd == "KEY_BACKSPACE": # Delete
                # Change to echo mode, allow entering command.
                if i > 0:
                    i -= 1
            # <CHAR>  means update tag for current element, next token.
            elif cmd in self.keys:
                tags[i] = self.keys[cmd]
                i += 1
            elif cmd == ':':
                # Change to echo mode, allow entering command.
                pass
            else:
                # print error
                pass
        return sentence, tags

def do_command(args):

    sentence = "Calderon said \" I like cheese, \" on Saturday .".split()
    tags = ["O" for _ in sentence]

    # A config of tag to shortcut.
    keys = {
        's' : 'SPKR',
        'j' : 'CTNT',
        'k' : 'CUE',
        'f' : 'O'
        }

    with EditShell(keys) as shell:
        _, tags = shell.run(sentence, tags)
    print(tags)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser( description='' )
    parser.set_defaults(func=do_command)

    ARGS = parser.parse_args()
    ARGS.func(ARGS)
