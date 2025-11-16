from abc import ABC, abstractmethod

class IPhotoSource(ABC):
    @abstractmethod
    async def get_photo_file(self, source) -> tuple[str,bytes]:pass
    @abstractmethod
    async def download_photo_by_id(self, file_id: str) -> tuple[str,bytes]:pass