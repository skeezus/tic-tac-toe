import { useState } from "react";
import { getWebSocketUrl } from "./config";

type GameState = {
  board: (string | null)[];
  current_turn: "X" | "O";
  status: "waiting" | "in_progress" | "finished";
  winner: "X" | "O" | null;
  player_count: number;
};

type ConnectionStatus = "disconnected" | "connecting" | "connected";

export default function App() {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>("disconnected");
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [playerSymbol, setPlayerSymbol] = useState<"X" | "O" | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const connect = () => {
    setErrorMessage(null);
    setConnectionStatus("connecting");
    const socket = new WebSocket(getWebSocketUrl());
    socket.onopen = () => {
      setConnectionStatus("connected");
      setWs(socket);
    };
    socket.onclose = () => {
      setConnectionStatus("disconnected");
      setWs(null);
      setGameState(null);
      setPlayerSymbol(null);
    };
    socket.onerror = () => setConnectionStatus("disconnected");
    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "game_joined") {
        setGameState(msg.game_state);
        setPlayerSymbol(msg.player_symbol);
        setErrorMessage(null);
      } else if (msg.type === "game_state") {
        setGameState(msg.game_state);
      } else if (msg.type === "error") {
        setErrorMessage(msg.message);
      }
    };
  };

  const disconnect = () => {
    ws?.close();
    setWs(null);
    setConnectionStatus("disconnected");
    setGameState(null);
    setPlayerSymbol(null);
    setErrorMessage(null);
  };

  const send = (payload: object) => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(payload));
    }
  };

  const handleJoin = () => {
    send({ type: "join" });
  };

  const handleMove = (cell: number) => {
    if (!gameState) return;
    send({ type: "move", cell });
  };

  return (
    <div
      style={{
        padding: "clamp(16px, 4vw, 24px)",
        width: "100%",
        maxWidth: "min(400px, 95vw)",
      }}
    >
      <h1 style={{ marginTop: 0, fontSize: "clamp(1.5rem, 5vw, 2rem)", textAlign: "center" }}>
        Tic-Tac-Toe
      </h1>

      {connectionStatus === "disconnected" && (
        <div style={{ display: "flex", justifyContent: "center", marginTop: 24 }}>
          <button
            type="button"
            onClick={connect}
            style={{ padding: "12px 24px", fontSize: "1.125rem" }}
          >
            Connect
          </button>
        </div>
      )}
      {connectionStatus === "connected" && !gameState && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          <button type="button" onClick={handleJoin}>
            Join game
          </button>
          <button type="button" onClick={disconnect}>
            Disconnect
          </button>
        </div>
      )}

      {gameState && (
        <>
          <div className="game-info">
            <p>
              {gameState.status === "waiting" && "Waiting for opponent..."}
              {gameState.status === "in_progress" && (
                <>
                  Turn: <span className={gameState.current_turn === "X" ? "cell-x" : "cell-o"}>{gameState.current_turn}</span>
                </>
              )}
              {gameState.status === "finished" &&
                (gameState.winner ? (
                  <>
                    Winner: <span className={gameState.winner === "X" ? "cell-x" : "cell-o"}>{gameState.winner}</span>
                  </>
                ) : (
                  "Draw"
                ))}
            </p>
            {playerSymbol && (
              <p>
                You are: <span className={playerSymbol === "X" ? "cell-x" : "cell-o"}>{playerSymbol}</span>
              </p>
            )}
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: "clamp(4px, 1.5vw, 12px)",
              width: "min(280px, 85vw, 100%)",
              maxWidth: "100%",
            }}
          >
            {gameState.board.map((cell, i) => (
              <button
                key={i}
                type="button"
                disabled={
                  cell !== null ||
                  gameState.status !== "in_progress" ||
                  gameState.current_turn !== playerSymbol
                }
                onClick={() => handleMove(i)}
                className={cell === "X" ? "cell-x" : cell === "O" ? "cell-o" : undefined}
                style={{
                  aspectRatio: "1",
                  fontSize: "clamp(1.25rem, 6vw, 2rem)",
                  minHeight: 44,
                  cursor: cell === null && gameState.status === "in_progress" ? "pointer" : "default",
                }}
              >
                {cell ?? ""}
              </button>
            ))}
          </div>
          <button type="button" onClick={disconnect} style={{ marginTop: "clamp(12px, 3vw, 16px)" }}>
            Leave / Disconnect
          </button>
        </>
      )}

      {errorMessage && (
        <p style={{ color: "#f87171", marginTop: 16 }}>{errorMessage}</p>
      )}
    </div>
  );
}
