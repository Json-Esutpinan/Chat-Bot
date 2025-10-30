from abc import ABC, abstractmethod
from typing import Any, Optional

class ICacheRepository(ABC):
    @abstractmethod
    def hget(self, key:str, field:str) -> Optional[str] : pass
    @abstractmethod
    def hset(self, key:str, field:str, value:Any)-> None : pass
    @abstractmethod
    def delete(self, key:str)->None : pass
    @abstractmethod
    def rpush(self, key:str, value:Any)-> None : pass
    @abstractmethod
    def lrange(self, key:str, start:int, end:int) -> list : pass