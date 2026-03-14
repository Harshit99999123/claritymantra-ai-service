from ingestion.models import BookDefinition


BOOK_REGISTRY: dict[str, BookDefinition] = {
    "bhagavad_gita_as_it_is": BookDefinition(
        slug="bhagavad_gita_as_it_is",
        title="Bhagavad Gita As It Is",
        source_kind="book",
        source_document_path="data-resources/hindu/Bhagavad-gita-As-It-Is.pdf",
        structured_source_path="data-resources/hindu/bhagavad_gita_as_it_is.seed.json",
        output_dataset_path="data/books/bhagavad_gita_as_it_is/dataset.json",
        output_metadata_path="data/books/bhagavad_gita_as_it_is/metadata.json",
        ingestor_key="bhagavad_gita_as_it_is",
    )
}


def list_books() -> list[BookDefinition]:
    return list(BOOK_REGISTRY.values())


def get_book_definition(book_slug: str) -> BookDefinition:
    return BOOK_REGISTRY[book_slug]
