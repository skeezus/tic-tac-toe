"""
In-memory game store. One game per game_id; connection_id -> symbol mapping per game.
"""
from __future__ import annotations

import uuid
from typing import Optional

from app.models import Board, Symbol, Status, WINNING_COMBOS


def _empty_board() -> Board:
    return [None] * 9


class Game:
    """Single game state."""

    def __init__(self) -> None:
        self.game_id = str(uuid.uuid4())
        self.board: Board = _empty_board()
        self.current_turn: Symbol = "X"
        self.status: Status = "waiting"
        self.winner: Optional[Symbol] = None
        self.players: dict[str, Symbol] = {}  # connection_id -> symbol

    def to_state(self) -> dict:
        """Serialize for broadcast (no connection IDs)."""
        return {
            "game_id": self.game_id,
            "board": self.board,
            "current_turn": self.current_turn,
            "status": self.status,
            "winner": self.winner,
            "player_count": len(self.players),
        }


_store: dict[str, Game] = {}  # game_id -> Game


def create_game(connection_id: str) -> Game:
    """Create a new game; first connection is X."""
    game = Game()
    game.players[connection_id] = "X"
    _store[game.game_id] = game
    return game


def get_game(game_id: str) -> Optional[Game]:
    return _store.get(game_id)


def join_game(game_id: str, connection_id: str) -> Optional[str]:
    """
    Join existing game. Returns error message or None on success.
    Assigns O to second player and sets status to in_progress.
    """
    game = _store.get(game_id)
    if not game:
        return "Game not found"
    if len(game.players) >= 2:
        return "Game is full"
    if connection_id in game.players:
        return "Already in this game"
    game.players[connection_id] = "O"
    game.status = "in_progress"
    return None


def remove_connection(connection_id: str) -> list[Game]:
    """Remove player from any game; return affected games (e.g. to end/broadcast)."""
    affected = []
    for game in list(_store.values()):
        if connection_id in game.players:
            del game.players[connection_id]
            affected.append(game)
    return affected
