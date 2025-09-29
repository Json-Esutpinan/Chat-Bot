import os
import time
import redis
from pathlib import Path
from telegram import Update, Bot
from fastapi import Request
from dotenv import load_dotenv
from model.telegram_model import TelegramBot
from model.state_model import SessionManager, State
load_dotenv()


bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
model_url = os.getenv("MODEL_URL")
storage_path = Path(os.getenv("IMAGE_DIR", "public/images"))
storage_path.mkdir(parents=True, exist_ok=True)
redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True)

async def webhook_handler(request: Request):
    
    data = await request.json()
    update = Update.de_json(data)
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    state_session = SessionManager(redis_client, f"session:{user_id}")
    bot_ = TelegramBot(redis_client,state_session, model_url, storage_path, Bot(token=bot_token), chat_id, user_id)
    
    if update.callback_query:
        await bot_.proccess_callback(update.callback_query.data)
    elif update.message:
        if update.message.text and state_session.get_state() in [State.START, State.WAIT_DESCRIPTION]:
            await bot_.proccess_text(update.message.text)
        elif update.message.location and state_session.get_state() == State.WAIT_LOCATION:
            await bot_.proccess_location(update.message.location)
        elif update.message.photo and state_session.get_state() == State.WAIT_PHOTO:
            image_path = await bot_.proccess_photo(update.message.photo)
            response = await bot_.send_to_model(image_path)
            if response["prediction"]["Flooded"] >.6:
                await self.send_telegram_message("¡Gracias! 📸 Foto recibida. Tu reporte se registró correctamente")
            else:
                await self.send_telegram_message("La imagen enviada no parece mostrar una escena de inundación. Por favor, verifica y envía una foto adecuada.")
                return
        else:
            await bot_.send_telegram_message("¡Ups! No era lo que esperaba.\n\nSi deseas iniciar un reporte escribe /start u Hola.")
            return {"status": "ok"} 
    return {"status": "ok"}