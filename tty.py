'''
Created by Samvel Khalatyan, Sep 04, 2012
Copyright 2012, All rights reserved
'''

import os
import sys
import subprocess

class Tty(object):
    def __init__(self, dynamic=False):
        self._dynamic = dynamic
        self._isatty = sys.stdout.isatty()

        if self._dynamic:
            self._get_width()

    @property
    def width(self):
        if not self._dynamic:
            self._get_width()

        return self._width

    @property
    def bold(self):
        return self._escape("1")

    @property
    def blue(self):
        return self._bold(34)

    @property
    def white(self):
        return self._bold(39)

    @property
    def red(self):
        return self._color(31)

    @property
    def yellow(self):
        return self._underline(33)

    @property
    def em(self):
        return self._underline(39)

    @property
    def green(self):
        return self._color(92)

    @property
    def reset(self):
        return self._escape(0)

    def bool(self):
        '''Check if it is tty input'''

        return self._isatty

    # Protected
    #
    def _escape(self, code):
        return "\033[{code}m".format(code=code) if self else ""

    def _bold(self, color):
        return self._escape("1;{color}".format(color=color))

    def _underline(self, color):
        return self._escape("4;{color}".format(color=color))

    def _color(self, color):
        return self._escape("0;{color}".format(color=color))

    def _get_width(self):
        process = subprocess.Popen(('/usr/bin/tput', 'cols'),
                                   stdout=subprocess.PIPE,
                                   stderr=os.devnull)
        self._width = (80 if process.wait()
                          else int(process.stdout.readline().strip()))

tty = Tty()
green = tty.green
red = tty.red
bold = tty.bold
reset = tty.reset

boldgreen = green + bold
boldred = red + bold

def makebold(string):
    global bold, reset

    return bold + string + reset

def error(*msg, **karg):
    karg.pop("file", None)
    print(tty.red + 'error' + tty.reset + ':',
          *msg, file=sys.stderr, **karg)

def warning(*msg, **karg):
    print(tty.blue + 'warning' + tty.reset + ':',
          *msg, **karg)

def info(*msg, **karg):
    print(makebold('info') + ':', *msg, **karg)
