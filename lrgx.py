import argparse
import curses
import logging
import os
import re
import sys


logger = logging.getLogger(__file__)
handler = logging.FileHandler('lrgx.log')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class Scroller(object):

    def __init__(self, window, lines, regex=None):
        self.window = window
        self.maxy, self.maxx = window.getmaxyx()
        self.lines = lines[:]
        self.first = 0
        self.last = self.maxy - 1
        if regex is not None:
            regex = '(' + regex + ')'
            regex = re.compile(regex)
        self.regex = regex
        self.key_to_color = {}
        self.next_color = 0

    def _assign_color(self, key):
        color = self.next_color
        self.next_color += 1
        self.next_color %= 8
        return color

    def _get_color(self, key):
        if key not in self.key_to_color:
            self.key_to_color[key] = self._assign_color(key)
        return self.key_to_color[key]

    def _paint_line(self, line):
        if self.regex is not None:
            match = self.regex.search(line)
            if match is not None:
                color = self._get_color(match.group(1))
                n = self.maxx
                self.window.addnstr(line[:match.start()], n,
                                    curses.color_pair(color))
                n = self.maxx - match.start()
                if n <= 0:
                    return
                self.window.addnstr(line[match.start():match.end()], n,
                                    curses.A_BOLD| curses.color_pair(color))
                n = self.maxx - match.end()
                if n <= 0:
                    return
                self.window.addnstr(line[match.end():], n,
                                    curses.color_pair(color))
                return
        self.window.addnstr(line, self.maxx)

    def paint(self):
        for line in self.lines[self.first:self.last]:
            try:
                self._paint_line(line)
            except:
                return

    def scroll_down(self, n):
        logger.debug('scroll_down({})'.format(n))
        while n > 0 and self.last < len(self.lines):
            self.last += 1
            self.first += 1
            n -= 1
            
    def scroll_up(self, n):
        logger.debug('scroll_up({})'.format(n))
        while n > 0 and self.first > 0:
            self.first -= 1
            self.last -= 1
            n -= 1

    def page_down(self):
        logger.debug('page_down')
        self.scroll_down(self.maxy)

    def page_up(self):
        logger.debug('page_up')
        self.scroll_up(self.maxy)


def main(win, stream=None, regex=None):
    curses.noecho()
    curses.cbreak()
    win.keypad(1)

    for x in range(1,8):
        curses.init_pair(x, x, 0)

    logger.debug('COLOR_PAIRS={}'.format(curses.COLOR_PAIRS))
    logger.debug('COLORS={}'.format(curses.COLORS))

    lines = stream.readlines()

    scroller = Scroller(win, lines, regex=regex)

    while True:
        win.clear()
        scroller.paint()
        win.refresh()
        cmd = win.getch()
        if cmd == ord('q'):
            return
        elif cmd == curses.KEY_NPAGE:
            scroller.page_down()
        elif cmd == curses.KEY_PPAGE:
            scroller.page_up()
        elif cmd == curses.KEY_UP:
            scroller.scroll_up(1)
        elif cmd == curses.KEY_DOWN:
            scroller.scroll_down(1)
        else:
            logger.debug('cmd={}'.format(cmd))
            scroller.scroll_down(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File viewer with regexp colorizing")
    parser.add_argument('file', help='File to view', nargs='?')
    parser.add_argument('--regex', help='Regular expression to match')
    args = parser.parse_args()

    if args.file:
        stream = open(args.file)
    else:
        # stdin is the input. Clone it to another file, close it, then dup it
        # from stderr so we can get a tty for curses input (saw this trick in
        # the source code for 'less')
        stream = os.fdopen(os.dup(sys.stdin.fileno()))
        os.close(sys.stdin.fileno())
        sys.stdin = os.fdopen(os.dup(2))
    
    try:
        curses.wrapper(main, stream=stream, regex=args.regex)
    except:
        logger.exception('Something bad happened')
