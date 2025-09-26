from fastapi import APIRouter, Request
from controller.telegram_controller import webhook_handler

router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    return await webhook_handler(request)
