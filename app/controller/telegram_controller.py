from telegram import Update
from fastapi import APIRouter, Request, Depends
from app.service.session.ReportDataManager import ReportDataManager
from app.service.session.State import State
from app.service.session.StateManager import StateManager
from app.use_cases.process_message_uc import ProcessMessageUseCase
from app.use_cases.process_callback_uc import ProcessCallbackUseCase
from app.use_cases.submit_report_uc import SubmitReportUseCase
from app.config.dependencies import (
    get_report_data_manager,
    get_state_manager,
    get_process_message_uc,
    get_process_callback_uc,
    get_submit_report_uc
)

router = APIRouter()

@router.post("/webhook")
async def webhook_handler(
    request: Request,
    process_message: ProcessMessageUseCase = Depends(get_process_message_uc),
    process_callback: ProcessCallbackUseCase = Depends(get_process_callback_uc),
    report_manager: ReportDataManager = Depends(get_report_data_manager),
):
    update_data = await request.json()
    update = Update.de_json(update_data, None) 
    
    if not update.effective_chat:
        return {"status": "error", "message": "Invalid update"}

    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.username or f"user_{user_id}"
    await report_manager.set_report_field(chat_id,'username', user_name )
        
    if update.callback_query:
        await process_callback.execute(
            data=update.callback_query.data, 
            chat_id=chat_id
        )
        
    elif update.message:
        await process_message.execute(
            message=update.message,
            chat_id=chat_id
        )
        
    return {"status": "ok"}