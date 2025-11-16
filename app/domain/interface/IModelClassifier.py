from abc import ABC, abstractmethod
from typing import Any

class IModelClassifier(ABC):
    def __init__(self, url_model: str):
        self.url_model = url_model
        super().__init__()
    @abstractmethod
    async def send_to_model(self, source: bytes, filename: str) -> Any: pass