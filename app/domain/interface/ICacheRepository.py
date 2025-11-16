from abc import ABC, abstractmethod
from typing import Any, Optional

class ICacheRepository(ABC):
    @abstractmethod
    async def hget(self, key:str, field:str) -> Optional[str] : pass
    @abstractmethod
    async def hset(self, key:str, field:str, value:Any)-> int : pass
    @abstractmethod
    async def delete(self, key:str)->int : pass
    @abstractmethod
    async def rpush(self, key:str, value:Any)-> int : pass
    @abstractmethod
    async def lrange(self, key:str, start:int, end:int) -> list[str] : pass