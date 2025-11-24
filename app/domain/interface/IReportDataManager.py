from typing import Any
from abc import ABC, abstractmethod

class IReportDataManager(ABC):
    """Interface for managing report data in cache"""
    
    @abstractmethod
    async def set_report_field(self, chat_id: str, field: str, value: Any):
        """Set a field in the report data"""
        pass
    
    @abstractmethod
    async def add_image_file_id(self, chat_id: str, classification_type: str, file_id: str, confidence: float):
        """Add an image file ID with its classification and confidence"""
        pass
    
    @abstractmethod
    async def get_final_report_json(self, chat_id: str) -> dict:
        """Get the complete report data as a dictionary"""
        pass
    
    @abstractmethod
    async def clear_report_data(self, chat_id: str):
        """Clear all report data for a given chat"""
        pass
