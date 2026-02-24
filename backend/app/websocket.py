"""
WebSocket endpoint: connect, create/join game, move, broadcast.
"""
from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.game_logic import apply_move
from app.game_store import create_game, get_game, join_game, remove_connection

router = APIRouter()

# connection_id -> WebSocket for broadcast
connections: dict[str, WebSocket] = {}


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    connections[connection_id] = websocket

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = msg.get("type")
            if msg_type == "create":
                game = create_game(connection_id)
                await websocket.send_json({
                    "type": "game_created",
                    "game_id": game.game_id,
                    "player_symbol": "X",
                    "game_state": game.to_state(),
                })
            elif msg_type == "join":
                game_id = msg.get("game_id")
                if not game_id:
                    await websocket.send_json({"type": "error", "message": "Missing game_id"})
                    continue
                err = join_game(game_id, connection_id)
                if err:
                    await websocket.send_json({"type": "error", "message": err})
                    continue
                game = get_game(game_id)
                await websocket.send_json({
                    "type": "game_joined",
                    "game_id": game_id,
                    "player_symbol": "O",
                    "game_state": game.to_state(),
                })
                await _broadcast_game(game_id, exclude=connection_id)
            elif msg_type == "move":
                game_id = msg.get("game_id")
                cell = msg.get("cell")
                if game_id is None or cell is None:
                    await websocket.send_json({"type": "error", "message": "Missing game_id or cell"})
                    continue
                game = get_game(game_id)
                if not game:
                    await websocket.send_json({"type": "error", "message": "Game not found"})
                    continue
                if connection_id not in game.players:
                    await websocket.send_json({"type": "error", "message": "Not in this game"})
                    continue
                symbol = game.players[connection_id]
                ok, err, new_board, winner, is_draw = apply_move(
                    game.board, cell, symbol, game.current_turn
                )
                if not ok:
                    await websocket.send_json({"type": "error", "message": err or "Invalid move"})
                    continue
                game.board = new_board
                if winner is not None:
                    game.status = "finished"
                    game.winner = winner
                elif is_draw:
                    game.status = "finished"
                else:
                    game.current_turn = "O" if game.current_turn == "X" else "X"
                await _broadcast_game(game_id)
            else:
                await websocket.send_json({"type": "error", "message": "Unknown message type"})
    except WebSocketDisconnect:
        pass
    finally:
        del connections[connection_id]
        for game in remove_connection(connection_id):
            game.status = "finished"
            game.winner = None
            await _broadcast_game(game.game_id)


async def _broadcast_game(game_id: str, exclude: str | None = None) -> None:
    """Send current game state to all connections in this game."""
    game = get_game(game_id)
    if not game:
        return
    payload = {"type": "game_state", "game_state": game.to_state()}
    for cid, ws in list(connections.items()):
        if cid in game.players and cid != exclude:
            try:
                await ws.send_json(payload)
            except Exception:
                pass
