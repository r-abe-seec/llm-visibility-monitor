import re

# Line prefixes that indicate an ordered list item, e.g. "1.", "1)", "1、",
# "1位". Leading markdown decorations (bold markers, headings, quotes) are
# tolerated so that "**1. Brand**" and "## 2. Brand" are still detected.
_NUMBERED_RE = re.compile(r"^\s*[*_#>]*\s*(\d+)\s*[.\)、．。位]")
_BULLET_RE = re.compile(r"^\s*(?:[-*・]|•)\s+")

# Markdown table rows, e.g. "| Brand | description |".
_TABLE_ROW_RE = re.compile(r"^\s*\|")
_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|[\s\-:|]+\|?\s*$")


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
    """Return (rank, line_text) for lines that look like ranked items.

    Three formats are recognized:
    - numbered items ("1.", "1)", "1位", optionally bold/heading-decorated)
      use their explicit number
    - bullet items ("-", "*", "・") use a running counter that resets
      whenever a non-list line interrupts the list
    - markdown table rows use their data-row position; the first row of a
      table is treated as the header and skipped, separator rows ("|---|")
      are ignored
    """
    ranked: list[tuple[int, str]] = []
    bullet_counter = 0
    table_row_counter = 0
    in_table = False

    for line in text.splitlines():
        if _TABLE_ROW_RE.match(line):
            if _TABLE_SEPARATOR_RE.match(line):
                continue
            if not in_table:
                # First row of a table is assumed to be the header.
                in_table = True
                table_row_counter = 0
                continue
            table_row_counter += 1
            ranked.append((table_row_counter, line))
            continue

        in_table = False

        numbered = _NUMBERED_RE.match(line)
        if numbered:
            ranked.append((int(numbered.group(1)), line))
            continue
        if _BULLET_RE.match(line):
            bullet_counter += 1
            ranked.append((bullet_counter, line))
            continue
        # A non-list, non-empty line ends the current bullet list, so the
        # next list starts counting from 1 again.
        if line.strip():
            bullet_counter = 0
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
