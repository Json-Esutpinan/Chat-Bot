from abc import ABC, abstractmethod
from typing import Any, Optional

class IMessageSender(ABC):
    @abstractmethod
    def send(self, message:str,chat_id:str,reply_markup:Optional[Any]=None):pass
    @abstractmethod
    def build_inline_keyboard(self, buttons: list) -> Any: pass
        