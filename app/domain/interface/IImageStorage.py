from abc import ABC, abstractmethod
from typing import Any, Optional

class IImageStorage(ABC):
    @abstractmethod
    def save_image(self, image_bytes: bytes, filename: str,url_server_storage:str , dir:str ) -> str:pass