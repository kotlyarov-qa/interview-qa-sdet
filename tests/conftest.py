import os
import json
import pytest
import httpx

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

AGENT_PORT = os.getenv("PORT", "8092")
AGENT_URL = os.getenv("AGENT_URL", f"http://localhost:{AGENT_PORT}")
UI_URL = os.getenv("UI_PORT", "3082")
if not UI_URL.startswith("http"):
    UI_URL = f"http://localhost:{UI_URL}"

@pytest.fixture(scope="session")
def agent_client():
    """Синхронный HTTP-клиент для вызовов Agent Bridge API."""
    with httpx.Client(base_url=AGENT_URL, timeout=60.0) as client:
        yield client

@pytest.fixture
def alice_headers():
    return {
        "Authorization": "Bearer demo-alice",
        "Content-Type": "application/json",
    }

@pytest.fixture
def bob_headers():
    return {
        "Authorization": "Bearer demo-bob",
        "Content-Type": "application/json",
    }

def send_agent_run(client: httpx.Client, token: str, message: str, mode: str = "mock", tool_mode: str = "success") -> httpx.Response:
    """Вспомогательная функция для отправки запроса в /run."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "message": message,
        "mode": mode,
        "tool_mode": tool_mode,
    }
    return client.post("/run", headers=headers, json=payload)
