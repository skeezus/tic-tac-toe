Project Overview

This is a multiplayer browser-based Tic-Tac-Toe application built with:

Frontend: React

Backend: FastAPI

Transport: WebSockets (real-time updates)

Deployment target: Any publicly reachable platform (TBD)

The goal is correctness, clarity, and architectural explainability — not UI polish.

Core Requirements
1. Deployment

The app must be deployed and reachable via a public URL.

It must support:

Two different devices

Two different browsers

No manual refresh required for state updates

2. Multiplayer PvP
Required Flow

Player A creates or joins a game.

Player B joins the same game.

Players take alternating turns.

Game continues until win or draw.

Both clients update in real-time via WebSockets.

No polling.
No manual refresh.

3. Game Rules
Board

3×3 grid

Represented as 9 cells

X always goes first

Rule Enforcement (Server-Side Only)

The backend must:

Enforce correct turn order

Reject:

Moves in occupied cells

Moves after game over

Moves from the wrong player

Detect:

Win (rows, columns, diagonals)

Draw (board full, no winner)

Broadcast updated game state after each valid move

The frontend must never be trusted for rule validation.

Architecture
High-Level Design
React Client A  ──┐
                   │
                   │ WebSocket
                   │
React Client B  ──┘
                   │
              FastAPI Server
                   │
              In-memory game store
Backend Design (FastAPI)
Game State Model

Each game contains:

game_id: str
board: list[str | None]  # length 9
current_turn: "X" | "O"
status: "waiting" | "in_progress" | "finished"
winner: Optional["X" | "O"]
players: dict[connection_id → symbol]

Game state lives in memory for MVP.

Future scaling would require:

Redis

Database-backed state

Sticky sessions or centralized state

WebSocket Responsibilities
On Connect

Assign connection ID

Allow:

Create game

Join game

On Move

Client sends:

{
  "type": "move",
  "game_id": "...",
  "cell": 4
}

Server:

Validates game exists

Validates player is part of game

Validates correct turn

Validates cell empty

Applies move

Checks win/draw

Broadcasts updated state

Win Detection Logic

Winning combinations:

[0,1,2]
[3,4,5]
[6,7,8]
[0,3,6]
[1,4,7]
[2,5,8]
[0,4,8]
[2,4,6]

Algorithm:

After each move:

Check if current player occupies all cells of any combo

If yes → status = finished, winner = current player

Else if board full → draw

Else → toggle turn

Frontend Design (React)
State Model

React maintains:

gameState
connectionStatus
playerSymbol
errorMessage

React does NOT:

Determine winner

Enforce turns

Validate legality

It only renders server state.

UI Requirements

Minimal UI:

3×3 clickable grid

Text showing:

Current turn

Winner

Draw

Waiting for opponent

Button:

Create game

Join game (enter game ID)

Styling is intentionally minimal.

Edge Cases to Handle
1. Two players try to join same slot simultaneously

→ Server assigns first two only.

2. Third player attempts to join

→ Reject with error.

3. Player disconnects mid-game

Options:

Immediately end game

Or mark as abandoned

MVP: End game on disconnect.

4. Simultaneous moves

WebSocket server must process sequentially.
Python event loop handles ordering.

5. Invalid input payload

Reject safely.
Never crash server.

Constraints Compliance

No tic-tac-toe libraries used.

All rule logic implemented manually.

WebSockets required (no polling).

Architecture must be explainable.

Scaling Considerations (Explainability Section)

If scaling beyond single instance:

Problem:

In-memory store won’t work across instances.

Solution:

Move state to Redis

Use pub/sub for broadcasting

Or persistent DB with real-time layer

Sticky sessions would also be required without shared state.

Testing Checklist

Before deployment, verify:

Two devices can connect

Moves sync instantly

Illegal moves rejected

Turns enforced

Win detection works

Draw detection works

Game cannot continue after finished

Rejoining existing game works

Server handles refresh gracefully

Non-Goals

Authentication

Spectator mode

Chat

Persistence between restarts

Fancy UI

Why This Architecture

WebSockets enable real-time updates.

Backend authoritative model prevents cheating.

React simplifies UI re-rendering.

FastAPI provides simple async WebSocket support.

In-memory store keeps MVP simple.