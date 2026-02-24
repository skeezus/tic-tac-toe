"""Pytest fixtures for backend tests."""
import socket
import threading
import time

import pytest
import uvicorn

from app.game_store import reset_store
from app.main import app

# Port for test server (single process, sequential tests)
TEST_PORT = 18765


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server_url():
    """Start ASGI app in a background thread; yield base URL (e.g. http://127.0.0.1:port)."""
    port = _find_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)

    def run():
        server.run()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    # Wait for server to be ready
    for _ in range(50):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                s.connect(("127.0.0.1", port))
            break
        except (OSError, socket.error):
            time.sleep(0.1)
    else:
        pytest.fail("Server did not start in time")

    yield f"http://127.0.0.1:{port}"


@pytest.fixture(autouse=True)
def reset_game_store():
    """Clear game store before each test so tests don't affect each other."""
    reset_store()
    yield
    reset_store()
