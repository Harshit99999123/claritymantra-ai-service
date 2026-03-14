from fastapi.testclient import TestClient

from main import app


def test_insight_response_includes_shloka_field() -> None:
    client = TestClient(app)

    response = client.post(
        "/ai/insight",
        json={
            "conversation": [
                {
                    "role": "user",
                    "message": "I feel stuck and uncertain about results",
                }
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "shloka" in body
