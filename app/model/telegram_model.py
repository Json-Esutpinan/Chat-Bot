import os
import redis
from dotenv import load_dotenv
import httpx
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, Update
from datetime import timedelta

redis_client = redis.Redis(host="192.168.79.176", port=6379, decode_responses=True)
load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
STATE ={
        None: "start",
        "start": "wait_confirmation",
        "wait_confirmation": "wait_description",
        "wait_description": "wait_location",
        "wait_location":"wait_photo",
        "wait_photo": "completed",
        "completed": None 
    }
class TelegramBot:
    def __init__(self, update: Update):
        print(update)
        self.bot = Bot(token=bot_token)
        self.update = update
        self.chat_id= update.effective_chat.id
        self.message_type = None
        self.redis_cache = redis_client
        self.session_key = f"session:{update.effective_user.id}"
        try:
            self.redis_cache.hset(self.session_key, mapping={
                "user_name": update.effective_user.full_name,
                "chat_id": self.chat_id,
                "state": None})
            self.redis_cache.expire(self.session_key, timedelta(minutes=15))
        except Exception as e:
            print(f"Error setting session data: {e}")
        if update.callback_query:
            print("Callback Query detected")
            self.message_type = "callback_query"
        elif update.message:
            print("Message detected")
            self.message_type = "message"
        
    async def process_message(self):
        state = self.redis_cache.hget(self.session_key, "state")
        print(f"Estado actual: {state}")
        if self.message_type == "message":
            if self.update.message.text:
                await self.proccess_text(self.update.message.text)
            elif self.update.message.location:
                await self.proccess_location(self.update.message.location)
            elif self.update.message.photo:
                await self.proccess_photo(self.update.message.photo)
            else:
                await self.send_telegram_message("Hola! 👋.\n\nSi deseas iniciar un reporte escribe /start u Hola para empezar.")
                self.redis_cache.hset(self.session_key, "state", None)
                return
        elif self.message_type == "callback_query":
            await self.proccess_callback(self.update.callback_query.data)
        return
    
    
    async def proccess_text(self, text: str):
        state = self.redis_cache.hget(self.session_key, "state")
        if text.lower() in ["/start","hola"] or state is None:
            self.redis_cache.hset(self.session_key, "state", STATE["start"])
            await self.send_telegram_message("¡Hola! 👋 Soy tu asistente para reportar inundaciones en Bogotá.\n\n¿Deseas iniciar un nuevo reporte?",
                                             self.build_inline_keyboard([("Sí, iniciar reporte 📝","confirm"),("No, gracias ❌","cancel")]))
            print(f"Estado actualizado a : {self.redis_cache.hget(self.session_key, 'state')}")
            return
        print(f"Current state: {state}")
        if state == "wait_description" and text.lower() not in ["/start","hola"]:
            self.redis_cache.hset(self.session_key, "description", text.lower())
            self.redis_cache.hset(self.session_key, "state", STATE["wait_description"])
            await self.send_telegram_message("¡Gracias! Ahora, por favor, envía la *ubicación* de la inundación. Puedes usar el botón de adjuntar y seleccionar 'Ubicación'.")
            return
        else:
            await self.send_telegram_message("¡Hola! 👋.\n\nSi deseas iniciar un reporte escribe /start u Hola para empezar.")
    
    
    async def proccess_callback(self, data: str):
        state = self.redis_cache.hget(self.session_key, "state")
        if state == "wait_confirmation":
            print(f"Este es el estado dentro del callback de wait confirmation: {state}")
            if data == "confirm":
                await self.send_telegram_message("¡Genial! Por favor, envíame una breve descripción de la inundación.")
                self.redis_cache.hset(self.session_key, "state", STATE["wait_confirmation"])
                print(f"Estado actualizado a: {self.redis_cache.hget(self.session_key, 'state')}")
                return
            elif data == "cancel":
                await self.send_telegram_message("Entendido. Si cambias de opinión, solo escribe /start para iniciar un nuevo reporte.")
                self.redis_cache.delete(self.session_key)
                return
            else:
                await self.send_telegram_message("Opción no reconocida. Por favor, elige una opción válida.")
        else:
            await self.send_telegram_message("Por favor, sigue las instrucciones o responde a la pregunta anterior. \n\nSi te perdiste, escribe /start para reiniciar.")
            
            
    async def proccess_location(self, location):
        state = self.redis_cache.hget(self.session_key, "state")
        if state != "wait_location":
            await self.send_telegram_message("Ups, no es lo que esperaba. \n\nPor favor, sigue las instrucciones anteriores.")
            return
        self.redis_cache.hset(self.session_key, "location", f"{location.latitude},{location.longitude}")
        self.redis_cache.hset(self.session_key, "state", STATE["wait_location"])
        await self.send_telegram_message("📝 Ubicación guardada. Ahora, por favor, envía una *foto* de la incidencia.")
        return
    
            
    async def proccess_photo(self, photos):
        state = self.redis_cache.hget(self.session_key, "state")
        if state != "wait_photo":
            await self.send_telegram_message("Ups, no es lo que esperaba. Por favor, sigue las instrucciones anteriores.")
            return
        photo_file_id = photos[-1].file_id
        self.redis_cache.hset(self.session_key, "photo_file_id", photo_file_id)
        self.redis_cache.hset(self.session_key, "state", STATE["wait_photo"])
        await self.send_telegram_message("¡Gracias! 📸 Foto recibida. Tu reporte se registró correctamente")        
        self.redis_cache.delete(self.session_key)
        description = self.redis_cache.hget(self.session_key, "description")
        location = self.redis_cache.hget(self.session_key, "location")
        
        report_data = {
            "user_name": self.redis_cache.hget(self.session_key, "user_name"),
            "chat_id": self.chat_id,
            "description": description,
            "location": location,
            "photo_file_id": photo_file_id
        }
        
    
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