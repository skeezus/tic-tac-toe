"""
In-memory multi-game store. Up to 10 parallel games; new joiners get a waiting game or a new slot.
"""
from __future__ import annotations

from typing import Optional

from app.models import Board, Symbol, Status

MAX_GAMES = 10


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

    def reset(self) -> None:
        """Clear board and state for reuse (e.g. after game finished and 0 players)."""
        self.board = _empty_board()
        self.current_turn = "X"
        self.status = "waiting"
        self.winner = None
        self.players = {}


_games: list[Game] = []


def join_or_create(connection_id: str) -> tuple[Optional[Game], Optional[str]]:
    """
    Join a game. Returns (game, None) on success or (None, error_message).
    1. If any game is waiting with 1 player → join as O.
    2. Else if any game is finished with 0 players → reset it and add connection as X.
    3. Else if fewer than MAX_GAMES → create new game, add as X.
    4. Else → "All games are full. Try again later."
    """
    global _games
    # Already in a game (e.g. duplicate join)
    for g in _games:
        if connection_id in g.players:
            return g, None

    # Find a waiting game with one player
    for g in _games:
        if g.status == "waiting" and len(g.players) == 1:
            g.players[connection_id] = "O"
            g.status = "in_progress"
            return g, None

    # Reuse a finished game with no players
    for g in _games:
        if g.status == "finished" and len(g.players) == 0:
            g.reset()
            g.players[connection_id] = "X"
            return g, None

    # Create new game if under limit
    if len(_games) < MAX_GAMES:
        game = Game()
        game.players[connection_id] = "X"
        _games.append(game)
        return game, None

    return None, "All games are full. Try again later."


def get_game_for_connection(connection_id: str) -> Optional[Game]:
    """Return the game this connection is in, or None."""
    for g in _games:
        if connection_id in g.players:
            return g
    return None


def remove_connection(connection_id: str) -> Optional[Game]:
    """Remove player from their game; return that game if affected (for broadcast)."""
    for g in _games:
        if connection_id in g.players:
            del g.players[connection_id]
            g.status = "finished"
            g.winner = None
            return g
    return None


def reset_store() -> None:
    """Clear all games. For testing only."""
    global _games
    _games = []
