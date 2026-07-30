import re

# Line prefixes that indicate an ordered/unordered list item, e.g.
# "1.", "1)", "1、", "1位", "- ", "* ", "・".
_NUMBERED_RE = re.compile(r"^\s*(\d+)\s*[.\)、．。位]")
_BULLET_RE = re.compile(r"^\s*(?:[-*・]|•)\s+")


def count_occurrences(text: str, term: str) -> int:
    """Case-insensitive, non-overlapping occurrence count of a term."""
    if not term:
        return 0
    return len(re.findall(re.escape(term), text, flags=re.IGNORECASE))


def first_position(text: str, terms: list[str]) -> int | None:
    """Smallest character index at which any term first appears."""
    lowered = text.lower()
    positions = [
        lowered.find(term.lower()) for term in terms if term and term.lower() in lowered
    ]
    return min(positions) if positions else None


def _ranked_lines(text: str) -> list[tuple[int, str]]:
    """Return (rank, line_text) for lines that look like list items.

    Numbered items use their explicit number; bullet items use a running
    counter so mixed lists still produce a sensible ordering.
    """
    ranked: list[tuple[int, str]] = []
    bullet_counter = 0
    for line in text.splitlines():
        numbered = _NUMBERED_RE.match(line)
        if numbered:
            ranked.append((int(numbered.group(1)), line))
            continue
        if _BULLET_RE.match(line):
            bullet_counter += 1
            ranked.append((bullet_counter, line))
    return ranked


def find_rank(text: str, terms: list[str]) -> int | None:
    """Rank of the first list item mentioning any term, if any."""
    lowered_terms = [t.lower() for t in terms if t]
    best: int | None = None
    for rank, line in _ranked_lines(text):
        lowered_line = line.lower()
        if any(term in lowered_line for term in lowered_terms):
            if best is None or rank < best:
                best = rank
    return best
