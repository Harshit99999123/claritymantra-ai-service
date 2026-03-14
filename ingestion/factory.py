from ingestion.books.bhagavad_gita_as_it_is import BhagavadGitaAsItIsIngestor
from ingestion.models import BookDefinition


def build_ingestor(definition: BookDefinition):
    if definition.ingestor_key == "bhagavad_gita_as_it_is":
        return BhagavadGitaAsItIsIngestor()
    raise ValueError(f"Unsupported ingestor key: {definition.ingestor_key}")
