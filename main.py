import time
import asyncio
import curses
import random
from itertools import cycle


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258
TIC = 0.1
SYMBOLS = "'+*.:'"


def fetch_spaceship_frames():
    with open('frames/rocket_frame_1.txt') as file1:
        frame1 = file1.read()
    with open('frames/rocket_frame_2.txt') as file2:
        frame2 = file2.read()
    return [frame1, frame2]


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


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column
    for _ in range(0, 3):
        canvas.addstr(round(row), round(column), '*')
        await asyncio.sleep(0)
    for _ in range(0, 3):
        canvas.addstr(round(row), round(column), 'O')
        await asyncio.sleep(0)
    for _ in range(0, 2):
        canvas.addstr(round(row), round(column), ' ')
        await asyncio.sleep(0)

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -3

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 3

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 3

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -3

    return rows_direction, columns_direction


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def gen_frame(frames):
    for i in cycle([0, 0, 1, 1]):
        yield frames[i]


def gen_coords(max_coords):
    max_row = max_coords[1]
    max_column = max_coords[0]
    possible_coords = []
    offset = 2
    for i in range(1, max_column - offset):
        for j in range(1, max_row - offset):
            possible_coords.append((i, j))
    for coord in random.sample(possible_coords, len(possible_coords)):
        yield coord


def fetch_next_coords(current_row, current_column, delta_row, delta_column, max_coords, frame_size):
    frame_rows, frame_columns = frame_size
    max_row, max_column = max_coords
    next_row = current_row + delta_row
    next_column = current_column + delta_column
    if next_row < 1:
        next_row = 1
    if next_row + frame_rows > max_row:
        next_row = max_row - frame_rows - 1
    if next_column < 1:
        next_column = 1
    if next_column + frame_columns > max_column:
        next_column = max_column - frame_columns -1
    return next_row, next_column



def gen_symbol(symbols="'+*.:'"):
    while True:
        yield symbols[random.randint(0, len(symbols) - 1)]


def draw(canvas):
    frames = fetch_spaceship_frames()
    frame = gen_frame(frames)
    curses.curs_set(False)
    window = curses.initscr()
    window.nodelay(True)
    coord = gen_coords(window.getmaxyx())
    symbol = gen_symbol()
    current_row, current_column = 1, 1
    coroutines = [blink(canvas, next(coord), next(symbol)) for _ in range(1, 450)]

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        current_frame = next(frame)
        delta_row, delta_column = read_controls(canvas)
        current_row, current_column = fetch_next_coords(
                current_row,
                current_column,
                delta_row,
                delta_column,
                window.getmaxyx(),
                get_frame_size(current_frame)
        )
        draw_frame(canvas, current_row, current_column, current_frame)

        canvas.border()
        canvas.refresh()
        draw_frame(canvas, current_row, current_column, current_frame, negative=True)
        time.sleep(TIC)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
