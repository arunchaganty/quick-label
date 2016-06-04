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

PAIR_BLUE = 2
V_MARGIN = 2
H_MARGIN = 3
H_LEN = 80
CMD_LEN = 40

class QuitException(BaseException):
    pass

class Action(object):
    """
    Just a container for an action returned by the shell
    """
    def __init__(self, action_type, *args):
        self.type = action_type
        self.args = args

class EditShell(object):
    """
    Shell to make quick edits to a sentence.
    """
    def __init__(self, config):
        # Curses set up
        self.stdscr = self.__setup_curses()

        self.LINES, self.COLS = self.stdscr.getmaxyx()
        self.FLAGS = {
            'underline': curses.A_UNDERLINE,
            'bold': curses.A_BOLD,
            'none': curses.color_pair(1),
            'blue': curses.color_pair(2),
            'red': curses.color_pair(3),
            'yellow': curses.color_pair(4),
            'emph': curses.A_STANDOUT,
            }

        self.tags = [tag.strip() for tag in config['tags']['tags'].split(',')]
        self.default_tag = config['tags']['default']
        assert self.default_tag in self.tags

        self.keybindings = self.__setup_keys(config['keys'])
        self.display_flags = self.__setup_display(config['display'])

    def __setup_curses(self):
        """
        Setup curses options
        """
        stdscr = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        return stdscr

    def __setup_keys(self, config):
        """
        Setup the keys from the options given
        """
        return {config[tag]: tag for tag in self.tags}

    def __setup_display(self, config):
        """
        Setup the display flags from the options given
        """
        flags = {}
        for tag in self.tags:
            props = [prop.strip() for prop in config[tag].split(',')]
            flag = 0
            for prop in props:
                flag |= self.FLAGS[prop]
            flags[tag] = flag

        return flags

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
        """
        Initialize the drawing window
        """
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

        LINES, COLS = win.getmaxyx()
        LINES_ = LINES-V_MARGIN*2
        COLS_ = min(COLS-H_MARGIN*2, H_LEN)

        # Setup window
        win_ = win.subwin(LINES_, COLS_, V_MARGIN, H_MARGIN)
        win_.move(0,0)
        # Split sentence into groups of COLS_
        for i, (word, tag) in enumerate(zip(sentence, tags)):
            assert tag in self.tags
            y, x = win_.getyx()
            # Determine if we want to move to the next line.
            if len(word) + x >= COLS_:
                win_.move(y+1, 0)
                y, x = y+1, 0

            flags = self.display_flags[tag]
            if i == hl:
                flags |= self.FLAGS['emph']
            win_.addstr(word, flags)
            _, x = win_.getyx()
            if len(word) + x < COLS_:
                win_.addstr(" ")
        win_.refresh()

    def render_metadata(self, win, metadata):
        COLS_  = min(H_LEN, self.COLS)
        assert len(metadata) < COLS_ - CMD_LEN
        status_win = win.subwin(1,COLS_,self.LINES-1, 0)
        status_win.addstr(0,COLS_-len(metadata)-1, metadata, curses.A_DIM)

    def run(self, sentence, tags = None, metadata="metadata"):
        """
        Run correction shell on the sentence and tags.
        @return sentence, tags -- corrected versions.
        """
        win = self.init_window()
        text_win = win.subwin(1,CMD_LEN,self.LINES-1,0)
        self.render_metadata(win, metadata)

        i = 0 # Cursor position
        while i < len(sentence):

            self.render_sentence(win, sentence, tags, i)
            # Handle corrections
            # :  means meta-command, e.g. quit.
            cmd = win.getkey()
            text_win.clear()

            # <ENTER> means everything is correct, next example.
            if cmd == '\n':
                return Action("save", sentence, tags)

            # <SPACE> means current element is correct, next token.
            elif cmd == ' ':
                i += 1

            # <BACKSPACE> means move to previous token.
            elif cmd == "KEY_BACKSPACE": # Delete
                # Change to echo mode, allow entering command.
                if i > 0:
                    i -= 1
            # <CHAR>  means update tag for current element, next token.
            elif cmd in self.keybindings:
                tags[i] = self.keybindings[cmd]
                if i < len(sentence) - 1: # Don't auto-advance past the last token, just in case you want to make an edit.
                    i += 1
            elif cmd == ':':
                # Change to echo mode, allow entering command.
                text_win.move(0,0)
                text_win.addstr(":")
                tb = curses.textpad.Textbox(text_win)
                cmd = tb.edit().strip()

                if cmd == ":quit":
                    raise QuitException()
                elif cmd == ":skip" or cmd == ":next" or cmd == ":prev":
                    return Action(cmd)
                elif cmd.startswith(":goto"):
                    cmd, doc_idx = cmd[:5], cmd[5:].strip()
                    assert cmd == ":goto"
                    return Action(cmd, int(doc_idx))
                elif cmd == ":help":
                    text_win.addstr(0,0,"cmds: quit,skip,next,prev,goto,help")
                else:
                    text_win.addstr(0,0, "error", self.FLAGS["red"])
            else:
                text_win.addstr(0,0, "error", self.FLAGS["red"])
        return Action("save", sentence, tags)

def test_shell():
    from configparser import ConfigParser
    config = ConfigParser()
    config.read_file(open('quotes.config'))

    with EditShell(config) as shell:
        sentence = "Mexico 's state-owned oil company Petroleos Mexicanos , or Pemex , was bracing for Dean 's arrival into the oil-rich inlet , spokesman Carlos Ramirez said in an e-mail .".split()
        tags = ["O" for _ in sentence]
        _, tags, note = shell.run(sentence, tags)
    print(tags)
    print(note)

if __name__ == "__main__":
    test_shell()
