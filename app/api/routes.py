from fastapi import APIRouter, Request
from controller.telegram_controller import webhook_handler

router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    try:
        await webhook_handler(request)
    except Exception as e:
        print(f"Error handling webhook: {e}")
    return {"status": "ok"}
