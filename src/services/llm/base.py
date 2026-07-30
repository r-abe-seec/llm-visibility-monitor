from abc import ABC, abstractmethod

from src.models.llm_response import LLMResponse


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> LLMResponse:
        """プロンプトを実行し、共通形式の結果を返す。"""
        raise NotImplementedError
