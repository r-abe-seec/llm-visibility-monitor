import json
import re

from src.services.llm.base import LLMProvider

VALID_SENTIMENTS = {"positive", "neutral", "negative"}

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)

_PROMPT_TEMPLATE = """\
You are a brand-perception analyst.
The following text is an AI-generated answer. Classify how each brand listed
below is portrayed in the text.

Brands: {brands}

Text:
\"\"\"
{text}
\"\"\"

For each brand, choose exactly one of: positive, neutral, negative.
Respond with ONLY a JSON object mapping each brand name to its classification.
Example: {{"BrandA": "positive", "BrandB": "neutral"}}
"""


def build_sentiment_prompt(text: str, brand_names: list[str]) -> str:
    return _PROMPT_TEMPLATE.format(brands=", ".join(brand_names), text=text)


def parse_sentiment_response(
    raw: str,
    brand_names: list[str],
) -> dict[str, str]:
    """Extract a {brand: sentiment} mapping from an LLM response.

    Unknown brands and invalid sentiment values are dropped rather than
    raising, since sentiment is a best-effort enrichment.
    """
    match = _JSON_RE.search(raw)
    if not match:
        return {}

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}

    if not isinstance(data, dict):
        return {}

    result: dict[str, str] = {}
    known = set(brand_names)
    for brand, sentiment in data.items():
        if brand not in known or not isinstance(sentiment, str):
            continue
        normalized = sentiment.strip().lower()
        if normalized in VALID_SENTIMENTS:
            result[brand] = normalized
    return result


def judge_sentiments(
    provider: LLMProvider,
    text: str,
    brand_names: list[str],
) -> dict[str, str]:
    """Ask the executing provider to classify brand sentiment in ``text``."""
    if not brand_names:
        return {}

    prompt = build_sentiment_prompt(text, brand_names)
    response = provider.generate(prompt)
    return parse_sentiment_response(response.response, brand_names)
