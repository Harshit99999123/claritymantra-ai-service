from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader

from models.knowledge import KnowledgeChunk, KnowledgeSource


CHAPTER_START_PAGES = {
    1: 39,
    2: 81,
    3: 176,
    4: 231,
    5: 292,
    6: 328,
    7: 386,
    8: 436,
    9: 469,
    10: 524,
    11: 576,
    12: 634,
    13: 660,
    14: 705,
    15: 737,
    16: 767,
    17: 798,
    18: 826,
}

ART_SECTION_START_PAGE = 903
TEXT_HEADER_PATTERN = re.compile(r"(?=(?:^|\n)TEXTS?\s+(\d+)(?:[–-](\d+))?)", re.MULTILINE)

THEME_KEYWORDS = {
    "duty": {"duty", "duties", "responsibility", "obligation", "role"},
    "karma yoga": {"karma", "action", "work", "perform", "prescribed"},
    "detachment": {"detachment", "attached", "attachment", "outcome", "results", "fruits"},
    "action": {"action", "act", "work", "perform", "deed"},
    "discipline": {"discipline", "control", "regulated", "steady"},
    "mind": {"mind", "thought", "thinking", "consciousness"},
    "purpose": {"purpose", "meaning", "future", "path", "nature"},
    "identity": {"self", "nature", "identity", "soul"},
    "relationships": {"family", "friend", "kinsmen", "relationship"},
    "calm": {"peace", "calm", "equanimity", "steady", "balance"},
    "fear": {"fear", "afraid", "terrified", "anxiety"},
    "control": {"control", "power", "choice", "influence"},
}

EMOTION_KEYWORDS = {
    "confusion": {"confused", "confusion", "bewildered", "uncertain", "doubt", "perplexity"},
    "anxiety": {"anxiety", "fear", "worried", "restless", "panic"},
    "stress": {"stress", "pressure", "distress", "agitation"},
    "grief": {"grief", "lamentation", "sorrow", "tears", "loss"},
    "overthinking": {"overthinking", "wanders", "mind", "restless", "thinking"},
    "career": {"work", "duty", "profession", "action", "responsibility"},
    "purpose": {"purpose", "future", "direction", "meaning"},
    "relationship": {"family", "friend", "kinsmen", "teacher"},
}


def parse_bhagavad_gita_pdf(pdf_path: str, source_slug: str, source_title: str, source_kind: str) -> list[KnowledgeChunk]:
    reader = PdfReader(pdf_path)
    source = KnowledgeSource(slug=source_slug, title=source_title, kind=source_kind)
    chunks: list[KnowledgeChunk] = []

    chapter_numbers = sorted(CHAPTER_START_PAGES)
    for index, chapter in enumerate(chapter_numbers):
        start_page = CHAPTER_START_PAGES[chapter]
        end_page = CHAPTER_START_PAGES.get(chapter_numbers[index + 1], ART_SECTION_START_PAGE) if index + 1 < len(chapter_numbers) else ART_SECTION_START_PAGE
        chapter_text = extract_page_range(reader, start_page, end_page)
        chapter_chunks = parse_chapter_text(chapter, chapter_text, source)
        chunks.extend(chapter_chunks)

    return chunks


def extract_page_range(reader: PdfReader, start_page: int, end_page: int) -> str:
    parts: list[str] = []
    for page_index in range(start_page, min(end_page, len(reader.pages))):
        text = reader.pages[page_index].extract_text() or ""
        parts.append(text)
    return "\n".join(parts)


def parse_chapter_text(chapter: int, chapter_text: str, source: KnowledgeSource) -> list[KnowledgeChunk]:
    matches = list(TEXT_HEADER_PATTERN.finditer(chapter_text))
    chunks: list[KnowledgeChunk] = []
    for index, match in enumerate(matches):
        block_start = match.start()
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(chapter_text)
        block = chapter_text[block_start:block_end].strip()
        chunk = parse_verse_block(chapter, block, source)
        if chunk:
            chunks.append(chunk)
    return chunks


def parse_verse_block(chapter: int, block: str, source: KnowledgeSource) -> KnowledgeChunk | None:
    header_match = re.search(r"TEXTS?\s+(\d+)(?:[–-](\d+))?", block)
    if not header_match:
        return None

    verse_start = int(header_match.group(1))
    verse_end = header_match.group(2)
    verse_label = f"{verse_start}-{verse_end}" if verse_end else str(verse_start)
    chunk_id = f"{chapter}_{verse_label.replace('-', '_')}"

    translation = extract_section(block, "TRANSLATION", ["PURPORT"])
    if not translation:
        return None
    purport = extract_section(block, "PURPORT", [])
    meaning = derive_meaning(translation, purport)
    combined_text = f"{translation}\n{purport}".strip()
    themes = infer_tags(combined_text, THEME_KEYWORDS)
    emotions = infer_tags(combined_text, EMOTION_KEYWORDS)

    reference = f"{chapter}.{verse_label}"
    return KnowledgeChunk(
        chunk_id=chunk_id,
        source=source,
        reference=reference,
        chapter=chapter,
        verse=verse_start,
        verse_label=verse_label if verse_end else None,
        translation=normalize_whitespace(translation),
        interpretation=meaning,
        themes=themes,
        emotions=emotions,
    )


def extract_section(block: str, section_name: str, stop_names: list[str]) -> str:
    start_match = re.search(rf"{section_name}\s*", block)
    if not start_match:
        return ""
    section_text = block[start_match.end():]
    end_positions = []
    for stop_name in stop_names:
        stop_match = re.search(rf"\n{stop_name}\s*", section_text)
        if stop_match:
            end_positions.append(stop_match.start())
    if end_positions:
        section_text = section_text[: min(end_positions)]
    return normalize_whitespace(section_text)


def derive_meaning(translation: str, purport: str) -> str:
    source = purport if purport else translation
    sentences = split_sentences(source)
    if not sentences:
        return normalize_whitespace(translation)
    selected = sentences[:2]
    return normalize_whitespace(" ".join(selected))


def split_sentences(text: str) -> list[str]:
    cleaned = normalize_whitespace(text)
    if not cleaned:
        return []
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", cleaned) if sentence.strip()]


def infer_tags(text: str, keyword_map: dict[str, set[str]]) -> list[str]:
    lowered = text.lower()
    matched = [tag for tag, keywords in keyword_map.items() if any(keyword in lowered for keyword in keywords)]
    return matched


def normalize_whitespace(text: str) -> str:
    text = text.replace("\xad", "")
    text = text.replace("-\n", "")
    text = text.replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()
