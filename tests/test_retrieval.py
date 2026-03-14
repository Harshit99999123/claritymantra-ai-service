from fastapi.testclient import TestClient

from main import app


def test_retrieve_career_reflection_returns_duty_related_verses() -> None:
    client = TestClient(app)

    response = client.post("/ai/retrieve", json={"query": "I feel stuck in my career and uncertain about my future."})

    assert response.status_code == 200
    body = response.json()
    assert body["results"]
    assert body["retrieval_query"]
    assert any(
        {"career", "duty", "purpose", "identity"} & set(item["themes"])
        for item in body["results"]
    )
    assert all(item["source"]["slug"] == "bhagavad_gita_as_it_is" for item in body["results"])


def test_chat_response_is_grounded_with_retrieved_verses() -> None:
    client = TestClient(app)

    response = client.post("/ai/chat", json={"message": "I am overthinking my work and results.", "context": []})

    assert response.status_code == 200
    body = response.json()
    assert body["verses"]
    assert all("reference" in item for item in body["verses"])
    assert all("translation" in item for item in body["verses"])
    assert all("retrieval_reason" not in item for item in body["verses"])
    assert all("original_text" not in item for item in body["verses"])
