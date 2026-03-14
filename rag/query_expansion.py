from __future__ import annotations

import re


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9']+")

SYNONYM_GROUPS = {
    "career": {"career", "job", "work", "profession", "office"},
    "confusion": {"confusion", "uncertain", "uncertainty", "lost", "stuck", "doubt", "indecision"},
    "anxiety": {"anxiety", "stress", "overthinking", "worry", "fear", "restless", "pressure"},
    "purpose": {"purpose", "meaning", "direction", "calling", "future"},
    "duty": {"duty", "responsibility", "obligation", "role"},
    "detachment": {"detachment", "outcome", "results", "expectation", "attachment", "control"},
    "action": {"action", "act", "effort", "doing", "discipline"},
    "grief": {"grief", "sadness", "sorrow", "pain", "loss"},
    "mind": {"mind", "self-control", "discipline", "focus", "attention"},
    "relationships": {"relationship", "relationships", "family", "friend", "love", "conflict"},
}


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_PATTERN.findall(text)}


def expand_query_terms(text: str) -> set[str]:
    base_terms = tokenize(text)
    expanded = set(base_terms)
    for canonical, synonyms in SYNONYM_GROUPS.items():
        if base_terms & synonyms:
            expanded.add(canonical)
            expanded.update(synonyms)
    return expanded
