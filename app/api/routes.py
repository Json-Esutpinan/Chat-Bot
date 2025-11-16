from fastapi import APIRouter, Request
from app.controller.telegram_controller import webhook_handler, router as telegram_router

router = APIRouter(prefix="/api")

router.include_router(telegram_router, tags=["TelegramBot"])