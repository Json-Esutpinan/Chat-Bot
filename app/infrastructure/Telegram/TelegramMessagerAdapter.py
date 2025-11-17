from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from app.infrastructure.Telegram.TelegramBotSingleton import TelegramBotSingleton
from app.domain.interface.IMessageSender import IMessageSender

class TelegramMessager(IMessageSender):
    def __init__(self):
        self.bot = TelegramBotSingleton().get_bot()
    
    async def send(self, message: str, chat_id: str, reply_markup=None):
        await self.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
    def build_inline_keyboard(self, buttons: list) -> InlineKeyboardMarkup:
        keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons]
        return InlineKeyboardMarkup(keyboard)
    
    def build_reply_keyboard(self, buttons: list, **kwargs) -> ReplyKeyboardMarkup:

        keyboard = []
        for button in buttons:
            if isinstance(button, tuple):
                text, request_location = button[0], button[1] if len(button) > 1 else False
                keyboard.append([KeyboardButton(text, request_location=request_location)])
            else:
                keyboard.append([KeyboardButton(button)])
        return ReplyKeyboardMarkup(keyboard, **kwargs)
    
    def remove_keyboard(self) -> ReplyKeyboardRemove:
        return ReplyKeyboardRemove()
        