#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shell to edit a sequence.
"""

import sys
import math
import curses
import curses.textpad

from util import partition

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
        WORD_SPACING = 1
        TAG_SPACING = 1
        LINE_SPACING = 1
        MARGIN = 4

        LINES, COLS = win.getmaxyx()

        # If sentence has more than the max col size, identify how many
        # columns are required to render it.
        max_tok_len = max(map(len, sentence + tags))
        hskip =  max_tok_len + WORD_SPACING
        vskip = 1 + TAG_SPACING + LINE_SPACING

        COLS_ = min(COLS-MARGIN*2, hskip * len(sentence))
        LINES_ = math.ceil(hskip * len(sentence) / COLS_) * vskip

        # Setup window
        begin_y = int(LINES/2 - LINES_/2)
        begin_x = int(COLS/2  - COLS_/2)
        win_ = win.subwin(LINES_, COLS_, begin_y, begin_x)

        # Split sentence into groups of COLS_
        hlim = int(COLS_ / hskip) # Maximum number of characters we can use in a line.
        for i, (word, tag) in enumerate(zip(sentence, tags)):
            y, x = int(i/hlim) * vskip, (i % hlim) * hskip
            word_ = word + " " * (max_tok_len - len(word))
            tag_ = tag + " " * (max_tok_len - len(tag))

            if hl is not None and i == hl:
                w_flags = curses.color_pair(3) | curses.A_BOLD
                t_flags = curses.color_pair(2) | curses.A_BOLD
            else:
                w_flags = curses.color_pair(1)
                t_flags = curses.color_pair(1)
            win_.addstr(y  , x, word_, w_flags)
            win_.addstr(y+1, x,  tag_, t_flags)
        win_.refresh()

    def run(self, sentence, tags):
        """
        Run correction shell on the sentence and tags.
        @return sentence, tags -- corrected versions.
        """
        win = self.init_window()
        text_win = win.subwin(1,80,0,0)

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
                if i < len(sentence) - 1: # Don't auto-advance past the last token, just in case you want to make an edit.
                    i += 1
            elif cmd == ':':
                # Change to echo mode, allow entering command.
                tb = curses.textpad.Textbox(text_win)
                cmd = tb.edit()
                win.addstr(1,0, cmd, curses.A_BOLD)
            else:
                # print error
                pass
        return sentence, tags

def test_shell():

    sentence = "Mexico 's state-owned oil company Petroleos Mexicanos , or Pemex , was bracing for Dean 's arrival into the oil-rich inlet , spokesman Carlos Ramirez said in an e-mail .".split()
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
    test_shell()
