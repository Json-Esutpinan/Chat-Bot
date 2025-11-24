from app.domain.interface.IReportApi import IReportApi
import httpx

class ReportApiClient(IReportApi):
    def __init__(self, api_url: str):
        self.api_url = api_url

    async def send_report(self, data: dict, files: list) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.api_url,
                    data=data,
                    files=files
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"API Error {e.response.status_code}: {e.response.text}") from e
            except Exception as e:
                raise RuntimeError(f"Network error sending report: {e}") from e