import httpx, io
from app.domain.interface.IModelClassifier import IModelClassifier

class FloodModel(IModelClassifier):
    
    def __init__(self, url_model):
        super().__init__(url_model)
    
    async def send_to_model(self, img_bytes:bytes, filename: str)->dict:
        file_stream = io.BytesIO(img_bytes)
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {
                "image": (filename, file_stream, "image/jpeg")
            }
            resp = await client.post(self.url_model, files=files)
            resp.raise_for_status()
        return resp.json()