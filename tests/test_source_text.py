from ingestion.books.bhagavad_gita_parser import extract_original_text, is_clean_transliteration
from services.source_quote_service import SourceQuoteService


def test_extract_original_text_prefers_clean_transliteration_suffix() -> None:
    block = """
TEXT 66
SavRDaMaaRNPairTYaJYa MaaMaek&- Xar<a& v]Ja ) Ah& Tva& SavRPaaPae>Yaae Maae+aiYaZYaaiMa Maa éuc" )) 66 )) sarva-dharman parityajya
mam ekaṁ śaraṇaṁ vraja
TRANSLATION
Abandon all varieties of religion and just surrender unto Me.
"""

    original_text = extract_original_text(block)

    assert original_text == "sarva-dharman parityajya mam ekaṁ śaraṇaṁ vraja"


def test_extract_original_text_drops_corrupted_source_text() -> None:
    block = """
TEXT 8
Na ih Pa[PaXYaaiMa MaMaaPaNauÛa‚ ÛC^aek-MauC^aez<aiMaiNd]Yaa<aaMa(
TRANSLATION
I can find no means to drive away this grief.
"""

    assert extract_original_text(block) == ""


def test_source_quote_service_drops_invalid_symbols_without_llm() -> None:
    service = SourceQuoteService(llm_client=None, enabled=False, cache_path="/tmp/source_quote_test.json")

    assert service._fallback_clean("bad [ text ]") == ""
    assert is_clean_transliteration("sarva-dharman parityajya") is True
