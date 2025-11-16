from abc import ABC, abstractmethod

class IReportApi(ABC):
    @abstractmethod
    async def send_report(self, report_data: dict, files: list)->dict: pass