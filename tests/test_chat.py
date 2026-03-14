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
    assert "retrieval_query" in body


def test_chat_rewrites_noisy_query_for_retrieval() -> None:
    client = TestClient(app)

    response = client.post(
        "/ai/chat",
        json={
            "message": "i dnt knw wht to do in my life evrything is mess",
            "context": [],
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["retrieval_query"]
    assert body["retrieval_query"] != "i dnt knw wht to do in my life evrything is mess"


def test_chat_stream_endpoint_returns_sse_events() -> None:
    client = TestClient(app)

    with client.stream(
        "POST",
        "/ai/chat/stream",
        json={
            "message": "I feel stuck in my career.",
            "context": [],
        },
    ) as response:
        body = "".join(response.iter_text())

    assert response.status_code == 200
    assert "event: meta" in body
    assert "event: token" in body
    assert "event: done" in body
