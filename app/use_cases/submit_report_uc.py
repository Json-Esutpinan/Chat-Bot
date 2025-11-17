import io
from app.service.session.ReportDataManager import ReportDataManager
from app.domain.interface.IPhotoSource import IPhotoSource
from app.domain.interface.IReportApi import IReportApi
import json

class SubmitReportUseCase:
    def __init__(
        self, 
        report_data_manager: ReportDataManager,
        photo_source: IPhotoSource,
        report_api: IReportApi
    ):
        self.report_data_manager = report_data_manager
        self.photo_source = photo_source
        self.report_api = report_api

    async def execute(self, chat_id: str):
        
        report_data = await self.report_data_manager.get_final_report_json(chat_id)

        images_meta = report_data.get("images", [])
        if not images_meta:
            old = report_data.get("image", {})
            images_meta = (
                [{"file_id": fid, "label": "flooded", "confidence": report_data.get("photo_confidence", 0.0)} for fid in old.get("flooded", [])] +
                [{"file_id": fid, "label": "uncertain", "confidence": report_data.get("photo_confidence", 0.0)} for fid in old.get("uncertain", [])]
            )

        files_to_upload = []
        ordered_images = []
        for item in images_meta:
            file_id = item.get("file_id")
            if not file_id:
                continue
            filename, img_bytes = await self.photo_source.download_photo_by_id(file_id)
            files_to_upload.append(("imagen", (filename, io.BytesIO(img_bytes), "image/jpeg")))
            ordered_images.append({"label": item.get("label"), "confidence": item.get("confidence", 0.0)})

        clean_payload = {
            "chat_id": report_data.get("chat_id"),
            "user_id": report_data.get("user_id"),
            "username": report_data.get("username"),
            "incident_type": report_data.get("incident_type"),
            "lat": report_data.get("lat"),
            "lon": report_data.get("lon"),
            "description": report_data.get("description"),
            "images": ordered_images
        }
        metadata_json_str = json.dumps(clean_payload)
        data_payload = {"metadata_json": metadata_json_str}
        try:
            await self.report_api.send_report(data_payload, files_to_upload)
            await self.report_data_manager.clear_report_data(chat_id)
        except Exception as e:
            await self.report_data_manager.clear_report_data(chat_id)
            return {"No se pudo guardar la imagen"}