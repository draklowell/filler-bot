#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FILLER-BOT
Andrii Kryvyi
Ukrainian Catholic University

Algorithm that uses distance to the enemy to
evaluate the best move:
The lower the distance, the better the move.
"""
import math
from itertools import count
from typing import Any, Generator

from player import debug, mainloop


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


def evaluate_field(field: list[list[int]], fsm_storage: dict[str, Any]) -> None:
    """
    Callback that is called every new frame (field update).

    :param field: list[list[int]]
    :param fsm_storage: dict[str, Any]
    """
    fsm_storage.setdefault("cache", {})
    fsm_storage["cache"].clear()
    debug("EVALUATOR | Successfully invalidated cache")


def get_distance_at(
    position: tuple[int, int], field: list[list[int]], fsm_storage: dict[str, Any]
) -> int:
    """
    Calculate the distance from the given point to the nearest
    enemy cell using quickdist.

    :param position: tuple[int, int], position in the
        (row, col) form
    :param field: list[list[int]]
    :param fsm_storage: dict[str, Any]

    :returns: int, distance to the neares enemy cell
    """
    if position in fsm_storage["cache"]:
        return fsm_storage["cache"][position]

    distance_minimal = None
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

    fsm_storage["cache"][position] = distance_minimal
    return distance_minimal


def evaluate_placement(field: list[list[int]], fsm_storage: dict[str, Any]) -> float:
    """
    Callback that is called every possible placement.

    :param field: list[list[int]]
    :param fsm_storage: dict[str, Any]

    :returns: float, confidence of the placement
    """
    score = 0
    for row_idx, row in enumerate(field):
        for col_idx, col in enumerate(row):
            if col == 1:
                score -= get_distance_at((row_idx, col_idx), field, fsm_storage)

    return score


if __name__ == "__main__":
    mainloop(evaluate_field, evaluate_placement)
