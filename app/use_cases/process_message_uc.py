from app.domain.value_objects.format_text import FormatText
from app.domain.value_objects.valid_location import ValidLocation
from app.domain.interface.IMessageSender import IMessageSender
from app.service.session.StateManager import StateManager
from app.service.session.ReportDataManager import ReportDataManager
from app.service.session.State import State
from app.use_cases.process_photo_uc import ProcessPhotoUseCase

class ProcessMessageUseCase:
    def __init__(
        self, bot_repo:IMessageSender, 
        state_manager:StateManager, 
        photo_process:ProcessPhotoUseCase,
        report_manager:ReportDataManager,
        boundary=None):
        self.bot = bot_repo
        self.report_manager = report_manager
        self.state_manager = state_manager
        self.photo_processor= photo_process
        self.boundary = boundary

    async def execute(self, message, chat_id:str):
        state = await self.state_manager.get_state(chat_id)
        if message.text:
            text = FormatText(message.text)._format()
            if text in ['hola','/start']:
                await self.state_manager.clear_state(chat_id)
                await self.state_manager.set_state(chat_id=chat_id,state=State.START)
                await self.state_manager.advance(chat_id=chat_id)
                return await self.bot.send(
                        message="¡Hola! 👋 Soy tu asistente para reportar inundaciones en Bogotá.\n\n¿Deseas iniciar un nuevo reporte?",
                        reply_markup=self.bot.build_inline_keyboard([("Sí, iniciar reporte 📝","confirm_report"),("No, gracias ❌","cancel_report")]),
                        chat_id=chat_id
                    )
            elif text and state == State.WAIT_DESCRIPTION:
                await self.report_manager.set_report_field(chat_id,"description", text)
                await self.state_manager.advance(chat_id)
                return await self.bot.send(message="¡Gracias! Ahora, por favor, envía la *ubicación* de la inundación.📍",chat_id=chat_id)

        elif message.location and state == State.WAIT_LOCATION:
            try:
                lat =float(message.location.latitude)
                lon = float(message.location.longitude)
                location = ValidLocation(lat,lon, self.boundary)
            except ValueError:
                return await self.bot.send(
                    message="La ubicación enviada está fuera de los límites de Bogotá. Por favor, envía una ubicación válida dentro de la ciudad.", 
                    chat_id=chat_id)
            await self.report_manager.set_report_field(chat_id, "lat", lat)
            await self.report_manager.set_report_field(chat_id, "lon", lon)
            await self.state_manager.advance(chat_id)
            return await self.bot.send(message="📝 Ubicación guardada. Ahora, por favor, envía una *foto* de la incidencia.", chat_id=chat_id)

        elif message.photo and state == State.WAIT_PHOTO:
            await self.bot.send(message="Procesando la imagen, por favor espera... ⏳",chat_id= chat_id)
            file_id = message.photo[-1].file_id
            label, confidence = await self.photo_processor.execute(message.photo)
            await self.report_manager.add_image_file_id(chat_id,label, file_id, confidence)
            await self.report_manager.set_report_field(chat_id,"incident_type", "flooded")
            
            if label == "non_flooded":
                return await self.bot.send(
                    message="La imagen no muestra una escena de inundación. Por favor, envía otra foto que muestre claramente la inundación.",
                    chat_id=chat_id)
            elif label == "uncertain":
                await self.bot.send(message="No estoy seguro de que la imagen represente una inundación. El reporte será validado manualmente.",
                                    chat_id=chat_id)
            return await self.bot.send(
                message="¿Deseas agregar otra imagen al reporte?", 
                reply_markup=self.bot.build_inline_keyboard([("Sí, agregar otra imagen 📷","add_photo"),("No, finalizar reporte ✅","finish_report")]), 
                chat_id=chat_id)
        else:
            return await self.bot.send(message="Mensaje inesperado. Sigue las instrucciones o escribe /start para reiniciar.", chat_id= chat_id)