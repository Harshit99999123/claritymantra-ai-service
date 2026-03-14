from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def test_list_ingestion_books() -> None:
    client = TestClient(app)

    response = client.get("/ingestion/books")

    assert response.status_code == 200
    body = response.json()
    assert body
    assert body[0]["slug"] == "bhagavad_gita_as_it_is"
    assert body[0]["source_kind"] == "book"


def test_run_ingestion_for_specific_book() -> None:
    client = TestClient(app)

    response = client.post(
        "/ingestion/run",
        json={"book_slug": "bhagavad_gita_as_it_is", "refresh_active_index": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["book_slug"] == "bhagavad_gita_as_it_is"
    assert body["records_written"] > 600
    assert body["refreshed_active_index"] is True
    assert Path(body["output_dataset_path"]).exists()
    assert Path(body["output_metadata_path"]).exists()
