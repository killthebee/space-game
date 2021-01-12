import time
import asyncio
import curses
import random


TIC = 0.1
SYMBOLS = "'+*.:'"


async def blink(canvas, coord, symbol='*'):
    row, column = coord
    for _ in range(0, random.randint(1, 20)):
        await asyncio.sleep(0)
    while True:
        for _ in range(0, 20):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)
        for _ in range(0, 3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)
        for _ in range(0, 5):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)
        for _ in range(0, 3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)


def draw_blinking_star(canvas, timeout: float, mode=None):
    row, column = (5, 20)
    if mode:
        canvas.addstr(row, column, '*', mode)
    else:
        canvas.addstr(row, column, '*')
    canvas.border()
    canvas.refresh()
    time.sleep(timeout)


def gen_coords(max_coords):
    max_row = max_coords[1]
    max_column = max_coords[0]
    possible_coords = []
    for i in range(1, max_column - 2):
        for j in range(1, max_row - 2):
            possible_coords.append((i, j))
    for i in random.sample(possible_coords, len(possible_coords)):
        yield i

def gen_symbol(symbols="'+*.:'"):
    while True:
        yield symbols[random.randint(0, len(symbols) - 1)]


def draw(canvas):
    curses.curs_set(False)
    window = curses.initscr()
    coord = gen_coords(window.getmaxyx())
    symbol = gen_symbol()
    coroutines = [blink(canvas, next(coord), next(symbol)) for _ in range(1, 150)]

    while True:
        for coroutine in coroutines:
            coroutine.send(None)

        canvas.border()
        canvas.refresh()
        time.sleep(TIC)

if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)

#python main.py