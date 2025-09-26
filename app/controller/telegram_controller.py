import os
from telegram import Update, Bot
from fastapi import Request
from dotenv import load_dotenv
from model.telegram_model import TelegramBot
load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

async def webhook_handler(request: Request):
    data = await request.json()
    update = Update.de_json(data)
    bot_ = TelegramBot(update)
    await bot_.process_message()
    return {"status": "ok"}