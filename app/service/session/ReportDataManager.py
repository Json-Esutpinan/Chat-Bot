from typing import Any
from app.domain.interface.ICacheRepository import ICacheRepository

class ReportDataManager:
    
    key_sufix = "report_data"
    
    def __init__(self, cache_repository: ICacheRepository):
        self.cache = cache_repository
        
    def _get_session_key(self, chat_id: str) -> str:
        return f"session:{chat_id}"

    def _get_report_key(self, chat_id: str) -> str:
        session_key = self._get_session_key(chat_id)
        return f"{session_key}:{self.key_sufix}"
    
    async def set_report_field(self, chat_id: str, field: str, value: Any):
        report_key = self._get_report_key(chat_id)
        await self.cache.hset(report_key, field, value)

    async def add_image_file_id(self, chat_id: str, classification_type: str, file_id: str, confidence: float):
        session_key = self._get_session_key(chat_id)
        list_key = f"{session_key}:img:{classification_type}"
        payload = f"{file_id}|{confidence:.6f}"
        await self.cache.rpush(list_key, payload)

    async def get_final_report_json(self, chat_id: str) -> dict:
        report_key = self._get_report_key(chat_id)
        session_key = self._get_session_key(chat_id)
        async def get_field(key: str):
            val = await self.cache.hget(report_key, key)
            return val.decode('utf-8') if isinstance(val, bytes) else val
        chat_id_str = chat_id
        try:
            chat_id_num = int(chat_id_str)
        except (ValueError, TypeError):
            chat_id_num = 0
        
        lat_str = await get_field("lat")
        try:
            lat_num = float(lat_str) if lat_str else 0.0
        except (ValueError, TypeError):
            lat_num = 0.0
        
        lon_str = await get_field("lon")
        try:
            lon_num = float(lon_str) if lon_str else 0.0
        except (ValueError, TypeError):
            lon_num = 0.0

        data = {
            "chat_id": chat_id_num,  # Convert to int
            "user_id": await get_field("user_id"),
            "username": await get_field("username"),
            "incident_type": await get_field("incident_type"),
            "lat": lat_num,
            "lon": lon_num,
            "description": await get_field("description"),
        }
        
        async def get_decoded_list(list_key: str):
            items = await self.cache.lrange(list_key, 0, -1)
            return [item.decode('utf-8') if isinstance(item, bytes) else item for item in items]

        flooded_raw = await get_decoded_list(f"{session_key}:img:flooded")
        nonf_raw = await get_decoded_list(f"{session_key}:img:non_flooded")
        uncertain_raw = await get_decoded_list(f"{session_key}:img:uncertain")

        def split_items(items):
            parsed = []
            for it in items:
                if "|" in it:
                    fid, conf = it.rsplit("|", 1)
                    try:
                        parsed.append((fid, float(conf)))
                    except ValueError:
                        parsed.append((fid, 0.0))
                else:
                    parsed.append((it, 0.0))
            return parsed

        flooded = split_items(flooded_raw)
        nonf = split_items(nonf_raw)
        uncert = split_items(uncertain_raw)
        
        data["image"] = {
            "flooded": [fid for fid, _ in flooded],
            "non_flooded": [fid for fid, _ in nonf],
            "uncertain": [fid for fid, _ in uncert]
        }

        images_list = []
        for fid, conf in flooded:
            images_list.append({"file_id": fid, "label": "flooded", "confidence": conf})
        for fid, conf in nonf:
            images_list.append({"file_id": fid, "label": "non_flooded", "confidence": conf})
        for fid, conf in uncert:
            images_list.append({"file_id": fid, "label": "uncertain", "confidence": conf})
        data["images"] = images_list

        return data

    async def clear_report_data(self, chat_id: str):
        report_key = self._get_report_key(chat_id)
        session_key = self._get_session_key(chat_id)
        await self.cache.delete(report_key)
        await self.cache.delete(f"{session_key}:img:flooded")
        await self.cache.delete(f"{session_key}:img:non_flooded")
        await self.cache.delete(f"{session_key}:img:uncertain")