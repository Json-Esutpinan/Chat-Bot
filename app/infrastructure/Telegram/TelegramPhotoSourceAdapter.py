from app.infrastructure.Telegram.TelegramBotSingleton import TelegramBotSingleton
from app.domain.interface.IPhotoSource import IPhotoSource

class TelegramPhotoSourceAdapter(IPhotoSource):
    def __init__(self):
        self.bot = TelegramBotSingleton().get_bot()
        
    async def _download_from_telegram(self, file_id:str):
        file = await self.bot.get_file(file_id)
        file_path = file.file_path
        filename = file_path.split("/")[-1]
        img_bytes = await file.download_as_bytearray()
        return filename, img_bytes
        
    async def get_photo_file(self, source):
        file = await self.bot.get_file(source[-1].file_id)
        file_path = file.file_path
        filename = file_path.split("/")[-1]
        img_bytes = await file.download_as_bytearray()
        return filename, img_bytes
    
    async def download_photo_by_id(self, file_id: str) -> tuple[str,bytes]:
        return await self._download_from_telegram(file_id)