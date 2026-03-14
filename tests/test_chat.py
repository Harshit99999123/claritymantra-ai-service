from fastapi.testclient import TestClient

from main import app


def test_chat_endpoint() -> None:
    client = TestClient(app)

    response = client.post(
        "/ai/chat",
        json={
            "message": "I feel stuck in my career.",
            "context": [],
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert "response" in body
    assert "verses" in body
