#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILLER-BOT
Andrii Kryvyi
Ukrainian Catholic University
"""
import math
import sys
from itertools import count
from typing import Any, Generator


def expanding_distance(
    center: tuple[int, int]
) -> Generator[tuple[int, int, int], None, None]:
    """
    Generate coordinates of the outer square around the
    center point in increasing quickdist order.

    quickdist = max(|x0 - x1|, |y0 - y1|).

    :param center: tuple[int, int], center point in the
        (row, col) form

    :yields: tuple[int, int, int], neighbour point in the
        (row, col, quickdist) form
    """
    for offset in count(1):
        # Left to right
        for suboffset in range(-offset, offset + 1):
            yield (center[0] + suboffset, center[1] - offset, offset)

        # Top to bottom
        for suboffset in range(-offset + 1, offset):
            yield (center[0] + offset, center[1] + suboffset, offset)

        # Right to left
        for suboffset in reversed(range(-offset, offset + 1)):
            yield (center[0] + suboffset, center[1] + offset, offset)

        # Bottom to top
        for suboffset in range(-offset + 1, offset):
            yield (center[0] - offset, center[1] + suboffset, offset)


def get_distance_at(
    position: tuple[int, int],
    field: list[list[int]],
    cache: dict[tuple[int, int], float],
) -> float:
    """
    Calculate the distance from the given point to the nearest
    enemy cell using quickdist.

    :param position: tuple[int, int], position in the
        (row, col) form
    :param field: list[list[int]]
    :param cache: dict[tuple[int, int], float]

    :returns: float, distance to the nearest enemy cell
    """
    if position in cache:
        return cache[position]

    distance_minimal = 0
    quickdist_maximal = None
    for row, col, quickdist in expanding_distance(position):
        if quickdist_maximal and quickdist >= quickdist_maximal:
            break

        if not 0 <= row < len(field):
            continue
        if not 0 <= col < len(field[0]):
            continue
        if field[row][col] not in (3, 4):
            continue

        distance = math.sqrt((row - position[0]) ** 2 + (col - position[1]) ** 2)
        if not quickdist_maximal:
            quickdist_maximal = distance
            distance_minimal = distance
        else:
            distance_minimal = min(distance_minimal, distance)

    cache[position] = distance_minimal
    return distance_minimal


def evaluate_placement(
    field: list[list[int]], cache: dict[tuple[int, int], float]
) -> float:
    """
    Callback that is called every possible placement.

    :param field: list[list[int]]
    :param cache: dict[tuple[int, int], float], cache for
        distances to enemy cells

    :returns: float, confidence of the placement
    """
    score = 0
    for row_idx, row in enumerate(field):
        for col_idx, col in enumerate(row):
            if col == 1:
                score -= get_distance_at((row_idx, col_idx), field, cache)

    return score


def debug(message: Any, end: str = "\n", flush: bool = False) -> None:
    """
    Print data to stderr to not interfer with filler vm.

    :param message: Any
    :param end: str, string that will be added to the end of
        the message, default is newline character
    :param flush: bool
    """

    print("DEBUG |", message, end=end, flush=flush, file=sys.stderr)


def read_player_info() -> dict[str, int]:
    """
    Read the player info from the stdin and parse it's character,
    returns char map that could be used in read_field and read_figure
    functions.

    Example of player info:
        $$$ exec p2 : [./player1.py]

    Each value of the char map represent:
        0 - empty cell
        1 - player1, lately placed cell or
        filled cell in the figure
        2 - player 1, oldly placed cell
        3 - player 2, lately placed cell
        4 - player 2, oldly placed cell

    :returns: dict[str, int], char map
    """
    info = input()
    debug(f"Player info: {info}")

    if info.removeprefix("$$$ exec ").startswith("p1"):
        return {
            ".": 0,
            "*": 1,
            "O": 2,
            "o": 1,
            "X": 4,
            "x": 3,
        }

    return {
        ".": 0,
        "*": 1,
        "O": 4,
        "o": 3,
        "X": 2,
        "x": 1,
    }


def read_field(char_map: dict[str, int]) -> list[list[int]]:
    """
    Read the field data from the stdin.

    Example of the field:
        Plateau 15 17:
            01234567890123456
        000 .................
        001 .................
        002 .................
        003 .................
        004 .................
        005 .................
        006 .................
        007 ..O..............
        008 ..OOO............
        009 .................
        010 .................
        011 .................
        012 ..............X..
        013 .................
        014 .................

    :param char_map: dict[str, int], char map from the read_player_info

    :returns: list[list[int]], field as the matrix
    """
    info = input()
    debug(f"READ FIELD | {info}")

    _, height, _ = info.split()
    # Ignore column indicies
    debug(f"READ FIELD | {input()}")

    field = []
    for _ in range(int(height)):
        row = input()
        debug(f"READ FIELD | {row}")

        field.append([char_map[char] for char in row.split(" ", 1)[1]])

    return field


def read_figure(char_map: dict[str, int]) -> list[list[int]]:
    """
    Read the figure from the stdin.

    The input may look like this:
        Piece 2 2:
        **
        ..

    :param char_map: dict[str, int], char map from the read_player_info

    :returns: list[list[int]], figure as the matrix
    """
    info = input()
    debug(f"READ FIGURE | {info}")

    _, height, _ = info.split()

    figure = []
    for _ in range(int(height)):
        row = input()
        debug(f"READ FIGURE | {row}")
        figure.append([char_map[char] for char in row])

    return figure


def crop_figure(figure: list[list[int]]) -> tuple[int, int]:
    """
    Crop the figure inplace.
    Cuts off empty lines and columns on the borders.

    :param figure: list[list[int]], figure as the matrix

    :returns: tuple[int, int], offset of new coordinates in
        the (row, col) form
    """
    discarded_rows = 0
    # Crop upper rows
    while True:
        if any(figure[0]):
            break

        del figure[0]
        discarded_rows += 1

    # Crop lower rows
    while True:
        if any(figure[-1]):
            break

        del figure[-1]

    # Crop left cols
    discarded_cols = 0
    while True:
        if any(map(lambda row: row[0], figure)):
            break

        for row in figure:
            del row[0]
        discarded_cols += 1

    # Crop right cols
    while True:
        if any(map(lambda row: row[-1], figure)):
            break

        for row in figure:
            del row[-1]

    return (discarded_rows, discarded_cols)


def blit_figure(
    position: tuple[int, int], field: list[list[int]], figure: list[list[int]]
) -> list[list[int]] | None:
    """
    Draw figure at the given position on the field (creates new field).

    :param offset: tuple[int, int], coordinates to
        put figure at
    :param field: list[list[int]], field as the matrix
    :param figure: list[list[int]], figure as the matrix

    :returns: list[list[int]] | None, new field as the matrix or None
        if couldn't put figure
    """

    new_field = [row[:] for row in field]
    coincidence_found = False
    for offset_row, row in enumerate(figure):
        for offset_col, col in enumerate(row):
            if not col:
                continue

            field_col = field[position[0] + offset_row][position[1] + offset_col]
            # Can't place there, because enemy is there
            if field_col > 2:
                return None

            # Only 1 coincidence is allowed
            if field_col != 0 and coincidence_found:
                return None

            if field_col != 0:
                coincidence_found = True
            new_field[position[0] + offset_row][position[1] + offset_col] = 1

    if not coincidence_found:
        return None

    return new_field


def update(char_map: dict[str, int]):
    """
    Process forward in the game (process next step).

    :param char_map: dict[str, int], char map from the
        read_player_info function
    """
    field = read_field(char_map)
    cache = {}

    figure = read_figure(char_map)
    discarded_rows, discarded_cols = crop_figure(figure)

    best_placement = ()
    for position_row in range(discarded_rows, len(field) - len(figure) + 1):
        for position_col in range(discarded_cols, len(field[0]) - len(figure[0]) + 1):
            new_field = blit_figure((position_row, position_col), field, figure)
            if not new_field:
                continue

            confidence = evaluate_placement(new_field, cache)
            debug(
                f"PLACEMENT EVALUATION | ({position_row - discarded_rows}, "
                f"{position_col - discarded_cols}) = {confidence}"
            )
            if not best_placement or confidence > best_placement[2]:
                best_placement = (
                    position_row - discarded_rows,
                    position_col - discarded_cols,
                    confidence,
                )

    if not best_placement:
        debug("PLACEMENT EVALUATION | Couldn't find best placement")
        print(0, 0)
        return

    debug(f"PLACEMENT EVALUATION | Best placement: {best_placement}")
    print(*best_placement[:2])


def mainloop():
    """
    Function where main code sits.
    """
    char_map = read_player_info()
    try:
        while True:
            update(char_map)
    except EOFError:
        debug("MAINLOOP | Cannot get input. Looks like we've lost")


if __name__ == "__main__":
    mainloop()
