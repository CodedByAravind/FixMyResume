import re
from typing import Iterable


def normalize(text: str) -> str:
    """Lowercase and collapse whitespace for predictable matching."""
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def term_pattern(term: str) -> re.Pattern:
    """Build a word-boundary regex for a normalized term.

    Short terms like "c" or "go" are anchored so they only match as whole
    words/phrases (not letters inside other words). Multi-word phrases are
    joined by flexible whitespace.
    """
    words = [re.escape(w) for w in term.split()]
    inner = r"\s+".join(words)
    # Negative lookbehind/ahead of a word character prevents substring matches.
    return re.compile(r"(?<![a-z0-9]){}(?![a-z0-9])".format(inner))


def find_terms(normalized_text: str, terms: Iterable[str]) -> set[str]:
    """Return which of the given normalized terms occur in normalized_text."""
    found: set[str] = set()
    for term in terms:
        if term_pattern(term).search(normalized_text):
            found.add(term)
    return found
