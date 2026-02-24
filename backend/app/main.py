"""
Tic-Tac-Toe FastAPI backend.
WebSocket-based multiplayer; game state in memory.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.websocket import router as ws_router

app = FastAPI(
    title="Tic-Tac-Toe API",
    description="Multiplayer Tic-Tac-Toe over WebSockets",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router, prefix="/ws", tags=["websocket"])


@app.get("/health")
def health():
    """Health check for deployment."""
    return {"status": "ok"}
