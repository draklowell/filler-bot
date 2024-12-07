#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILLER-BOT
Andrii Kryvyi
Ukrainian Catholic University
"""
import math
from itertools import count
from logging import DEBUG, debug, getLogger
from typing import Generator

# We use the debugger to print messages to stderr
# You cannot use print as you usually do, the vm would intercept it
# You can hovever do the following:
#
# import sys
# print("HEHEY", file=sys.stderr)

getLogger().setLevel(DEBUG)

### ABSTRACT FUNCTIONS ###


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


### I/O FUNCTIONS ###


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
    debug(f"Field info: {info}")

    _, height, _ = info.split()
    # Ignore column indicies
    debug(f"Field info: {input()}")

    field = []
    for _ in range(int(height)):
        line = input()
        debug(f"Field info: {line}")

        field.append([char_map[char] for char in line.split(" ", 1)[1]])

    return field


def read_figure() -> set[tuple[int, int]]:
    """
    Read the figure from the stdin.

    The input may look like this:
        Piece 2 2:
        **
        ..

    :returns: set[tuple[int, int]], points of the figure
    """
    info = input()
    debug(f"Figure info: {info}")

    _, height, _ = info.split()

    figure = set()
    for row in range(int(height)):
        line = input()
        debug(f"Figure info: {line}")
        for col, char in enumerate(line):
            if char == "*":
                figure.add((row, col))

    return figure


### MAIN CODE ###


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

        if quickdist > max(len(field), len(field[0])):
            return 0

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
    position: tuple[int, int],
    field: list[list[int]],
    figure: set[tuple[int, int]],
    cache: dict[tuple[int, int], float],
    max_confidence: float | None,
) -> float | None:
    """
    Callback that is called every possible placement.

    :param position: tuple[int, int], coordinates to
        put figure at
    :param field: list[list[int]], field as the matrix
    :param figure: set[tuple[int, int]], figure as the set of points
    :param max_confidence: float | None, previous maximum confidence
        or None if not available

    :returns: float | None, confidence of the placement or None
        if confidence is lower then given
    """
    confidence = 0
    for point in figure:
        confidence -= get_distance_at(
            (position[0] + point[0], position[1] + point[1]), field, cache
        )
        if max_confidence is not None and confidence < max_confidence:
            return None

    return confidence


def validate_placement(
    position: tuple[int, int], field: list[list[int]], figure: set[tuple[int, int]]
) -> bool:
    """
    Check wheter figure could be placed at the given position
    on the field.

    :param position: tuple[int, int], coordinates to
        put figure at
    :param field: list[list[int]], field as the matrix
    :param figure: set[tuple[int, int]], figure as the set of points

    :returns: bool, True, if figure could be placed
    """

    coincidence_found = False
    for point in figure:
        row = position[0] + point[0]
        if row >= len(field):
            return False
        col = position[1] + point[1]
        if col >= len(field[0]):
            return False

        value = field[position[0] + point[0]][position[1] + point[1]]
        # Can't place there, because enemy is there
        if value > 2:
            return False

        # Only 1 coincidence is allowed
        if value != 0 and coincidence_found:
            return False

        if value != 0:
            coincidence_found = True

    return coincidence_found


def update(char_map: dict[str, int]):
    """
    Process forward in the game (process next step).

    :param char_map: dict[str, int], char map from the
        read_player_info function
    """
    field = read_field(char_map)
    cache = {}

    figure = read_figure()

    best_placement = ()
    for row in range(len(field)):
        for col in range(len(field[0])):
            if not validate_placement((row, col), field, figure):
                continue

            confidence = evaluate_placement(
                (row, col),
                field,
                figure,
                cache,
                best_placement[2] if best_placement else None,
            )
            if confidence is not None:
                debug(f"Placement evaluation: ({row}, {col}) = {confidence}")
                best_placement = (
                    row,
                    col,
                    confidence,
                )
            else:
                debug(f"Placement evaluation: ({row}, {col}): discarded")

    if not best_placement:
        debug("Placement evaluation: Couldn't find best placement")
        print(0, 0)
        return

    debug(f"Placement evaluation: Best placement: {best_placement}")
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
        debug("Cannot get input. Looks like we've lost")


if __name__ == "__main__":
    mainloop()
