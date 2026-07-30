from src.services.analysis.sentiment import (
    build_sentiment_prompt,
    judge_sentiments,
    parse_sentiment_response,
)
from src.services.llm.base import LLMProvider


def test_prompt_contains_brands_and_text():
    prompt = build_sentiment_prompt("電通は最大手です。", ["電通", "博報堂"])
    assert "電通, 博報堂" in prompt
    assert "電通は最大手です。" in prompt


def test_parse_plain_json():
    raw = '{"電通": "positive", "博報堂": "neutral"}'
    assert parse_sentiment_response(raw, ["電通", "博報堂"]) == {
        "電通": "positive",
        "博報堂": "neutral",
    }


def test_parse_json_with_surrounding_text():
    raw = 'Here is the result:\n{"電通": "Negative"}\nDone.'
    assert parse_sentiment_response(raw, ["電通"]) == {"電通": "negative"}


def test_parse_drops_unknown_brands_and_invalid_values():
    raw = '{"電通": "great", "謎の会社": "positive", "博報堂": "neutral"}'
    assert parse_sentiment_response(raw, ["電通", "博報堂"]) == {"博報堂": "neutral"}


def test_parse_returns_empty_on_garbage():
    assert parse_sentiment_response("no json here", ["電通"]) == {}
    assert parse_sentiment_response("{broken json", ["電通"]) == {}


class _FakeProvider(LLMProvider):
    provider_name = "fake"

    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.prompts: list[str] = []

    def generate(self, prompt: str):
        from src.models.llm_response import LLMResponse

        self.prompts.append(prompt)
        return LLMResponse(
            provider="fake",
            model="fake",
            prompt=prompt,
            response=self.reply,
            input_tokens=1,
            output_tokens=1,
            latency_ms=1,
        )


def test_judge_sentiments_calls_provider():
    provider = _FakeProvider('{"電通": "positive"}')
    result = judge_sentiments(provider, "電通が1位。", ["電通"])
    assert result == {"電通": "positive"}
    assert len(provider.prompts) == 1


def test_judge_sentiments_skips_when_no_brands():
    provider = _FakeProvider("{}")
    assert judge_sentiments(provider, "text", []) == {}
    assert provider.prompts == []
