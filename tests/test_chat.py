from fastapi.testclient import TestClient

from main import app


def test_chat_endpoint_returns_structured_reflection() -> None:
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
    assert "reflection" in body
    assert "reflection_question" in body
    assert body["reflection_question"].endswith("?")
    assert "verses" in body
    assert len(body["verses"]) <= 2
    verse_keys = set(body["verses"][0].keys())
    assert verse_keys == {"reference", "translation", "themes"}


def test_chat_stream_endpoint_returns_compact_meta() -> None:
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
    assert "retrieval_query" not in body
