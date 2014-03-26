import argparse
import curses
import logging
import re


logger = logging.getLogger('legex')
handler = logging.FileHandler('legex.log')
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

    def _get_color(self, key):
        return hash(key) % 8

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


def main(win, filename=None, regex=None):
    curses.noecho()
    curses.cbreak()
    win.keypad(1)

    for x in range(1,8):
        curses.init_pair(x, x, 0)

    logger.debug('COLOR_PAIRS={}'.format(curses.COLOR_PAIRS))
    logger.debug('COLORS={}'.format(curses.COLORS))

    lines = open(filename).readlines()

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
        else:
            logger.debug('cmd={}'.format(cmd))
            scroller.scroll_down(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File viewer with regexp colorizing")
    parser.add_argument('file', help='File to view')
    parser.add_argument('--regex', help='Regular expression to match')
    args = parser.parse_args()

    curses.wrapper(main, filename=args.file, regex=args.regex)
