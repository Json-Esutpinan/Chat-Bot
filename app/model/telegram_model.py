import time
import redis
from pathlib import Path
import httpx
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from datetime import timedelta
from model.state_model import SessionManager, State

class TelegramBot:
    def __init__(self,session: redis.Redis, state: SessionManager, model_url, storage_path: Path, bot: Bot, chat_id, user_id):
        #Init flood model variables
        self.model_url = model_url
        self.storage_dir = storage_path
        self.state = state
        
        #Init telegram bot variables
        self.bot = bot
        
        #Init session variables
        self.chat_id= chat_id
        self.redis_cache = session
        self.session_key = f"session:{user_id}"
        
        try:
            self.redis_cache.hset(self.session_key, mapping={
                "chat_id": self.chat_id})
            self.redis_cache.expire(self.session_key, timedelta(minutes=5))
        except Exception as e:
            print(f"Error setting session data: {e}")
    
    async def proccess_text(self, text: str):
        if text.lower() in ["/start","hola"]:
            self.state.set_state(State.START)
            await self.send_telegram_message("¡Hola! 👋 Soy tu asistente para reportar inundaciones en Bogotá.\n\n¿Deseas iniciar un nuevo reporte?",
                                             self.build_inline_keyboard([("Sí, iniciar reporte 📝","confirm"),("No, gracias ❌","cancel")]))
            self.state.advance()
            return
        
        if self.state.get_state() == State.WAIT_DESCRIPTION and text.lower() not in ["/start","hola"]:
            self.redis_cache.hset(self.session_key, "description", text.lower())
            self.state.advance()
            await self.send_telegram_message("¡Gracias! Ahora, por favor, envía la *ubicación* de la inundación. Puedes usar el botón de adjuntar y seleccionar 📍'Ubicación'.")
            return
        else:
            await self.send_telegram_message("¡Hola! 👋.\n\nSi deseas iniciar un reporte escribe /start u Hola para empezar.")
    
    async def proccess_callback(self, data: str):
        if self.state.get_state() == State.WAIT_CONFIRMATION:
            if data == "confirm":
                await self.send_telegram_message("¡Genial! Por favor, envíame una breve descripción de la inundación.")
                self.state.advance()
                return
            elif data == "cancel":
                await self.send_telegram_message("Entendido. Si cambias de opinión, solo escribe /start para iniciar un nuevo reporte.")
                self.redis_cache.delete(self.session_key)
                return
            else:
                await self.send_telegram_message("Opción no reconocida. Por favor, elige una opción válida.")
        else:
            await self.send_telegram_message("Ups, no es lo que esperaba. \n\nPor favor, sigue las instrucciones. \n\nSi te perdiste, escribe /start para reiniciar.")  
            
    async def proccess_location(self, location):
        if self.state.get_state() != State.WAIT_LOCATION:
            await self.send_telegram_message("Ups, no es lo que esperaba. \n\nPor favor, sigue las instrucciones. \n\nSi te perdiste, escribe /start para reiniciar.")
            return
        self.redis_cache.hset(self.session_key, "location", f"{location.latitude},{location.longitude}")
        self.state.advance()
        await self.send_telegram_message("📝 Ubicación guardada. Ahora, por favor, envía una *foto* de la incidencia.")
        return
            
    async def proccess_photo(self, photos):
        if self.state.get_state() != State.WAIT_PHOTO:
            await self.send_telegram_message("Ups, no es lo que esperaba. \n\nPor favor, sigue las instrucciones. \n\nSi te perdiste, escribe /start para reiniciar.")
            return
        await self.send_telegram_message("Procesando la imagen, por favor espera... ⏳")
        photo_path = await self.download_photo(photos)
        self.redis_cache.hset(self.session_key, "photo_path", photo_path.as_posix())
        self.state.advance()
        return photo_path
        
    async def download_photo(self,photos) -> Path:
        file = await self.bot.get_file(photos[-1].file_id)
        img_bytes = await file.download_as_bytearray()
        filename = f"{self.chat_id}_{int(time.time())}.jpg"
        local_path = self.storage_dir / filename
        local_path.write_bytes(img_bytes)
        return local_path    
    
    async def send_to_model(self, file_path: Path) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(file_path, "rb") as f:
                files = {"image": (file_path.name, f, "image/jpeg")}
                resp = await client.post(self.model_url, files=files)
            resp.raise_for_status()
            return resp.json()
    
    def save_report(self):
        report_data={
            "user_name": self.redis_cache.hget(self.session_key, "user_name"),
            "chat_id": self.chat_id,
            "description": self.redis_cache.hget(self.session_key, "description"),
            "location": self.redis_cache.hget(self.session_key, "location"),
            "photo_path": self.redis_cache.hget(self.session_key, "photo_path")
        }
        self.redis_cache.delete(self.session_key)
        pass
    
    
    async def send_telegram_message(self, text: str, reply_markup=None):
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
            
    def build_inline_keyboard(self, buttons: list):
        keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons]
        return InlineKeyboardMarkup(keyboard)