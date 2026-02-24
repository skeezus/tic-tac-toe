"""Tests for up to 10 games (20 players) connecting and playing (multi-game support)."""
import asyncio
import json

import pytest
import websockets

# Up to 10 games, 2 players per game = 20 players
MAX_GAMES = 10
PLAYERS_PER_GAME = 2
MAX_PLAYERS = MAX_GAMES * PLAYERS_PER_GAME  # 20
TEN_PLAYERS = 10  # 5 games


async def join_player(ws_url: str, index: int) -> dict:
    """Open WebSocket, send join, return first JSON message."""
    ws_base = ws_url.replace("http://", "ws://").replace("https://", "wss://")
    async with websockets.connect(f"{ws_base}/ws") as ws:
        await ws.send(json.dumps({"type": "join"}))
        msg = await ws.recv()
        return json.loads(msg)


@pytest.mark.asyncio
async def test_10_players_join_and_form_5_games(server_url):
    """10 players connect and join; they form exactly 5 games of 2 players each."""
    # Run 10 joins concurrently (simulates 10 players connecting at once)
    tasks = [join_player(server_url, i) for i in range(TEN_PLAYERS)]
    results = await asyncio.gather(*tasks)

    # All 10 should get game_joined (no one got "All games are full")
    for i, msg in enumerate(results):
        assert msg.get("type") == "game_joined", f"Player {i} got: {msg}"
        assert "game_state" in msg
        assert "player_symbol" in msg
        assert msg["player_symbol"] in ("X", "O")

    # Exactly 5 games: 5 players have player_count 1 (X), 5 have player_count 2 (O)
    player_counts = sorted(msg["game_state"]["player_count"] for msg in results)
    assert player_counts == [1, 1, 1, 1, 1, 2, 2, 2, 2, 2]


@pytest.mark.asyncio
async def test_21st_player_gets_all_games_full(server_url):
    """After 20 players have joined (10 full games), the 21st gets an error."""
    ws_base = server_url.replace("http://", "ws://").replace("https://", "wss://")
    # Keep 20 connections open so the server doesn't remove them on disconnect
    open_sockets = []
    for _ in range(MAX_PLAYERS):
        ws = await websockets.connect(f"{ws_base}/ws")
        open_sockets.append(ws)
        await ws.send(json.dumps({"type": "join"}))
        await ws.recv()  # game_joined or game_state

    # All 10 games have 2 players; 21st should get "full"
    async with websockets.connect(f"{ws_base}/ws") as ws_21:
        await ws_21.send(json.dumps({"type": "join"}))
        msg = json.loads(await ws_21.recv())

    for ws in open_sockets:
        await ws.close()

    assert msg["type"] == "error"
    assert "full" in msg["message"].lower()


@pytest.mark.asyncio
async def test_two_players_can_play_a_move_each(server_url):
    """Two players join one game; X plays center (4), O plays corner (0); state updates."""
    ws_base = server_url.replace("http://", "ws://").replace("https://", "wss://")
    recv_x: list[dict] = []
    recv_o: list[dict] = []

    async with websockets.connect(f"{ws_base}/ws") as ws_x:
        await ws_x.send(json.dumps({"type": "join"}))
        recv_x.append(json.loads(await ws_x.recv()))

        async with websockets.connect(f"{ws_base}/ws") as ws_o:
            await ws_o.send(json.dumps({"type": "join"}))
            recv_o.append(json.loads(await ws_o.recv()))
            # X may get a game_state when O joins
            try:
                recv_x.append(json.loads(await asyncio.wait_for(ws_x.recv(), timeout=0.5)))
            except asyncio.TimeoutError:
                pass

            # X plays cell 4 (center)
            await ws_x.send(json.dumps({"type": "move", "cell": 4}))
            recv_x.append(json.loads(await ws_x.recv()))
            recv_o.append(json.loads(await ws_o.recv()))

            # O plays cell 0 (top-left)
            await ws_o.send(json.dumps({"type": "move", "cell": 0}))
            recv_o.append(json.loads(await ws_o.recv()))
            recv_x.append(json.loads(await ws_x.recv()))

    # After X=4, O=0: board[4]=X, board[0]=O
    last_state = recv_x[-1]
    assert last_state["type"] == "game_state"
    board = last_state["game_state"]["board"]
    assert board[4] == "X"
    assert board[0] == "O"
    assert last_state["game_state"]["current_turn"] == "X"
