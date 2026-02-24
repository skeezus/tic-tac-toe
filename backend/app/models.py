"""
Game state models. In-memory store for MVP.
"""
from typing import Literal

Board = list[str | None]  # length 9
Symbol = Literal["X", "O"]
Status = Literal["waiting", "in_progress", "finished"]

WINNING_COMBOS = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
]
