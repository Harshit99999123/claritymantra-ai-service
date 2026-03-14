from pydantic import BaseModel


class BookDefinition(BaseModel):
    slug: str
    title: str
    source_kind: str = "book"
    source_document_path: str
    structured_source_path: str
    output_dataset_path: str
    output_metadata_path: str
    ingestor_key: str


class IngestionBookResponse(BaseModel):
    slug: str
    title: str
    source_kind: str
    source_document_path: str
    output_dataset_path: str
    active_for_retrieval: bool


class IngestionRunRequest(BaseModel):
    book_slug: str
    refresh_active_index: bool = True


class IngestionRunResponse(BaseModel):
    book_slug: str
    title: str
    output_dataset_path: str
    output_metadata_path: str
    records_written: int
    refreshed_active_index: bool
