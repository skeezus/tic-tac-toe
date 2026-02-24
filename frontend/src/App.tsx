import { useState } from "react";

type GameState = {
  game_id: string;
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
  const [joinGameId, setJoinGameId] = useState("");
  const [ws, setWs] = useState<WebSocket | null>(null);

  const connect = () => {
    setErrorMessage(null);
    setConnectionStatus("connecting");
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws`);
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
      if (msg.type === "game_created" || msg.type === "game_joined") {
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

  const handleCreateGame = () => {
    send({ type: "create" });
  };

  const handleJoinGame = () => {
    if (!joinGameId.trim()) return;
    send({ type: "join", game_id: joinGameId.trim() });
  };

  const handleMove = (cell: number) => {
    if (!gameState?.game_id) return;
    send({ type: "move", game_id: gameState.game_id, cell });
  };

  return (
    <div style={{ padding: 24, maxWidth: 400 }}>
      <h1 style={{ marginTop: 0 }}>Tic-Tac-Toe</h1>

      <p>
        Status: <strong>{connectionStatus}</strong>
      </p>

      {connectionStatus === "disconnected" && (
        <button type="button" onClick={connect}>
          Connect
        </button>
      )}
      {connectionStatus === "connected" && !gameState && (
        <>
          <button type="button" onClick={handleCreateGame}>
            Create game
          </button>
          <div style={{ marginTop: 8 }}>
            <input
              type="text"
              placeholder="Game ID to join"
              value={joinGameId}
              onChange={(e) => setJoinGameId(e.target.value)}
            />
            <button type="button" onClick={handleJoinGame} style={{ marginLeft: 8 }}>
              Join game
            </button>
          </div>
          <button type="button" onClick={disconnect} style={{ marginLeft: 8 }}>
            Disconnect
          </button>
        </>
      )}

      {gameState && (
        <>
          <p>
            {gameState.status === "waiting" && "Waiting for opponent..."}
            {gameState.status === "in_progress" && `Turn: ${gameState.current_turn}`}
            {gameState.status === "finished" &&
              (gameState.winner
                ? `Winner: ${gameState.winner}`
                : "Draw")}
          </p>
          {playerSymbol && <p>You are: {playerSymbol}</p>}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: 4,
              width: "min(280px, 100%)",
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
                style={{
                  aspectRatio: "1",
                  fontSize: 24,
                  cursor: cell === null && gameState.status === "in_progress" ? "pointer" : "default",
                }}
              >
                {cell ?? ""}
              </button>
            ))}
          </div>
          <button type="button" onClick={disconnect} style={{ marginTop: 16 }}>
            Leave / Disconnect
          </button>
        </>
      )}

      {errorMessage && (
        <p style={{ color: "crimson", marginTop: 16 }}>{errorMessage}</p>
      )}
    </div>
  );
}
