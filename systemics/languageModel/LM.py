from abc import ABC, abstractmethod


class LM(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def generate_chat(self,
                      messages: list,
                      temperature: float = 1,
                      top_p: float = 1,
                      max_tokens: int | None = None,
                      **kwargs) -> tuple[str, dict]:
        pass
