"""
In-memory single-game store. Two players; third gets "Game is full".
"""
from __future__ import annotations

from typing import Optional

from app.models import Board, Symbol, Status


def _empty_board() -> Board:
    return [None] * 9


class Game:
    """Single game state."""

    def __init__(self) -> None:
        self.board: Board = _empty_board()
        self.current_turn: Symbol = "X"
        self.status: Status = "waiting"
        self.winner: Optional[Symbol] = None
        self.players: dict[str, Symbol] = {}  # connection_id -> symbol

    def to_state(self) -> dict:
        """Serialize for broadcast (no connection IDs)."""
        return {
            "board": self.board,
            "current_turn": self.current_turn,
            "status": self.status,
            "winner": self.winner,
            "player_count": len(self.players),
        }


_game: Optional[Game] = None


def join_or_create(connection_id: str) -> tuple[Optional[Game], Optional[str]]:
    """
    Join the single game. Returns (game, None) on success or (None, error_message).
    If no game or game is finished, start a new game and add connection as X.
    If game has one player, add as O. If game has two players, return "Game is full".
    """
    global _game
    if _game is None or _game.status == "finished":
        _game = Game()
        _game.players[connection_id] = "X"
        return _game, None
    if len(_game.players) >= 2:
        return None, "Game is full"
    if connection_id in _game.players:
        return _game, None  # already in game (reconnect?)
    _game.players[connection_id] = "O"
    _game.status = "in_progress"
    return _game, None


def get_game_for_connection(connection_id: str) -> Optional[Game]:
    """Return the (single) game this connection is in, or None."""
    if _game is None:
        return None
    if connection_id in _game.players:
        return _game
    return None


def get_the_game() -> Optional[Game]:
    """Return the single game, if any."""
    return _game


def remove_connection(connection_id: str) -> Optional[Game]:
    """Remove player from the game; return the game if it was affected."""
    global _game
    if _game is None or connection_id not in _game.players:
        return None
    del _game.players[connection_id]
    _game.status = "finished"
    _game.winner = None
    return _game
