from telegram import Bot
import os

class TelegramBotSingleton:
    _instance = None
    _telegram_bot = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelegramBotSingleton, cls).__new__(cls)
            cls._instance._initialize_bot()
        return cls._instance

    def _initialize_bot(self):
        if self._telegram_bot is None:
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            self._telegram_bot = Bot(token)
            
    def get_bot(self):
        return self._telegram_bot