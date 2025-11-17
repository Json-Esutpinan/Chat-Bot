from app.service.session.StateManager import StateManager, State
from app.domain.interface.IMessageSender import IMessageSender
from app.use_cases.submit_report_uc import SubmitReportUseCase

class ProcessCallbackUseCase:
    def __init__(self, state_manager:StateManager, bot_repo: IMessageSender, submit_report: SubmitReportUseCase):
        self.state_manager = state_manager
        self.bot = bot_repo
        self.submit_report = submit_report
    
    async def execute(self, data, chat_id:str):
        state = await self.state_manager.get_state(chat_id)
        if state == State.WAIT_CONFIRMATION:
            if data == "confirm_report":
                await self.bot.send(
                    message="¡Genial! Por favor, envíame una breve descripción de la inundación.",
                    chat_id=chat_id,
                    reply_markup=self.bot.remove_keyboard()
                )
                await self.state_manager.advance(chat_id)
                return
            elif data == "cancel_report":
                await self.bot.send(message="Entendido. Si cambias de opinión, solo escribe /start para iniciar un nuevo reporte.", chat_id=chat_id)
                await self.state_manager.clear_state(chat_id)
                return
        elif state == State.WAIT_PHOTO:
            if data == "add_photo":
                await self.bot.send(message="Perfecto, por favor envía otra foto de la inundación.", chat_id=chat_id)
                return
            elif data == "finish_report":
                await self.bot.send(message="😜¡Gracias! Tu reporte ha sido guardado con éxito.", chat_id=chat_id)
                await self.submit_report.execute(chat_id)
                await self.state_manager.advance(chat_id)
                return
        else:
            return await self.bot.send(message="Mensaje inesperado. Sigue las instrucciones o escribe /start para reiniciar.", chat_id= chat_id)