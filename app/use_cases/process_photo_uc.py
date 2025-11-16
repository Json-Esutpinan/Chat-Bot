from app.domain.interface.IPhotoSource import IPhotoSource
from app.domain.interface.IModelClassifier import IModelClassifier

class ProcessPhotoUseCase:

    def __init__(self, photo_source:IPhotoSource,model:IModelClassifier):        
        self.model = model
        self.photo_source = photo_source
    
    async def execute(self, photo):
        label = None
        confidence = None
        filename, img_bytes = await self.photo_source.get_photo_file(photo)
        response = await self.model.send_to_model(filename=filename,img_bytes=img_bytes)
        prediction = response.get("prediction")
        
        if prediction.get("flooded",0) >=.7314:
            label = "flooded"
            confidence = prediction["flooded"]
        elif prediction.get("flooded") <.7313 and prediction.get("flooded")>.55:
            label = "uncertain"
            confidence = max(prediction.get("flooded"),prediction.get("non_flooded"))
        else:
            label = "non_flooded"
            confidence = prediction.get("non_flooded")

        return label, confidence