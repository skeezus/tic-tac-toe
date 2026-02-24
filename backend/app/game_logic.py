"""
Server-side rule enforcement: turn order, cell validity, win/draw detection.
"""
from __future__ import annotations

from app.models import Board, Symbol, WINNING_COMBOS


def check_winner(board: Board, symbol: Symbol) -> bool:
    """True if symbol occupies all cells of any winning combo."""
    for combo in WINNING_COMBOS:
        if all(board[i] == symbol for i in combo):
            return True
    return False


def is_draw(board: Board) -> bool:
    """Board full and no winner (call after move applied)."""
    return all(c is not None for c in board)


def apply_move(
    board: Board,
    cell: int,
    symbol: Symbol,
    current_turn: Symbol,
) -> tuple[bool, str | None, Board | None, str | None, bool]:
    """
    Validate and apply one move.
    Returns: (ok, error_msg, new_board, winner, is_draw).
    If ok, new_board is updated copy; winner/is_draw for status update.
    """
    if cell < 0 or cell > 8:
        return False, "Invalid cell", None, None, False
    if board[cell] is not None:
        return False, "Cell already occupied", None, None, False
    if symbol != current_turn:
        return False, "Not your turn", None, None, False

    new_board = board.copy()
    new_board[cell] = symbol

    if check_winner(new_board, symbol):
        return True, None, new_board, symbol, False
    if is_draw(new_board):
        return True, None, new_board, None, True
    return True, None, new_board, None, False
