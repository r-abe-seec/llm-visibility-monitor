from openai import OpenAI

from src.config import settings

client = OpenAI(api_key=settings.openai_api_key)


def hello_openai():
    response = client.responses.create(
        model=settings.openai_model, input="Say hello in Japanese."
    )

    return response.output_text
