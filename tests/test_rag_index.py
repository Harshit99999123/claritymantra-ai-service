import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def test_vector_index_persists_on_disk() -> None:
    index_dir = Path("data/vector_store")
    assert index_dir.exists()
    assert any(index_dir.iterdir())


def test_ingestion_metadata_tracks_written_records() -> None:
    client = TestClient(app)
    response = client.post(
        "/ingestion/run",
        json={"book_slug": "bhagavad_gita_as_it_is", "refresh_active_index": True},
    )
    assert response.status_code == 200
    metadata_path = Path(response.json()["output_metadata_path"])
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert payload["book_slug"] == "bhagavad_gita_as_it_is"
    assert payload["records_written"] > 600
