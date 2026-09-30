import os
import json
import pytest
import httpx

AGENT_URL = os.getenv("AGENT_URL", "http://localhost:8092")
UI_URL = os.getenv("UI_URL", "http://localhost:3082")

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
