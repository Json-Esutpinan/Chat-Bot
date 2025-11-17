import os
from dotenv import load_dotenv
import geopandas as gpd
from typing import Optional

from app.infrastructure.ApiGateway.ReportApiClient import ReportApiClient
from app.infrastructure.Redis.RedisRepository import RedisRepository
from app.infrastructure.Telegram.TelegramPhotoSourceAdapter import TelegramPhotoSourceAdapter
from app.infrastructure.Telegram.TelegramMessagerAdapter import TelegramMessager
from app.infrastructure.InferenceModel.FloodModel import FloodModel

from app.service.session.StateManager import StateManager
from app.service.session.ReportDataManager import ReportDataManager

from app.domain.interface.ICacheRepository import ICacheRepository
from app.domain.interface.IReportApi import IReportApi
from app.domain.interface.IPhotoSource import IPhotoSource
from app.domain.interface.IMessageSender import IMessageSender
from app.domain.interface.IModelClassifier import IModelClassifier 

from app.use_cases.process_callback_uc import ProcessCallbackUseCase
from app.use_cases.process_message_uc import ProcessMessageUseCase
from app.use_cases.process_photo_uc import ProcessPhotoUseCase
from app.use_cases.submit_report_uc import SubmitReportUseCase

load_dotenv(override=True)

# --- Constantes y Carga de Recursos ---
BOGOTA_BOUNDARY = gpd.read_file(str(os.getenv("BOGOTA_GEOJSON_PATH"))).geometry.iloc[0]
GATEWAY_URL = os.getenv("APIGATEWAY")
API_REPORT_URL = f"{GATEWAY_URL}01/reports"
MODEL_URL = f"{GATEWAY_URL}80/api/classify-image"

# --- Singletons de Infraestructura ---
_redis_repo: Optional[ICacheRepository] = None
_report_api: Optional[IReportApi] = None
_photo_source: Optional[IPhotoSource] = None
_bot_sender: Optional[IMessageSender] = None
_flood_model: Optional[IModelClassifier] = None

def get_redis_repo() -> ICacheRepository:
    global _redis_repo
    if _redis_repo is None:
        _redis_repo = RedisRepository()
    return _redis_repo

def get_report_api() -> IReportApi:
    global _report_api
    if _report_api is None:
        _report_api = ReportApiClient(api_url=API_REPORT_URL)
    return _report_api

def get_photo_source() -> IPhotoSource:
    global _photo_source
    if _photo_source is None:
        _photo_source = TelegramPhotoSourceAdapter()
    return _photo_source

def get_bot_sender() -> IMessageSender:
    global _bot_sender
    if _bot_sender is None:
        _bot_sender = TelegramMessager() 
    return _bot_sender

def get_flood_model() -> IModelClassifier:
    global _flood_model
    if _flood_model is None:
        _flood_model = FloodModel(url_model=MODEL_URL)
    return _flood_model

# --- Singletons de Servicios/Managers ---
_state_manager: Optional[StateManager] = None
_report_manager: Optional[ReportDataManager] = None

def get_state_manager() -> StateManager:
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager(cache_repo=get_redis_repo())
    return _state_manager

def get_report_data_manager() -> ReportDataManager:
    global _report_manager
    if _report_manager is None:
        _report_manager = ReportDataManager(cache_repository=get_redis_repo())
    return _report_manager

# --- Proveedores de Casos de Uso ---
def get_process_photo_uc() -> ProcessPhotoUseCase:
    return ProcessPhotoUseCase(
        model=get_flood_model(),
        photo_source=get_photo_source()
    )

def get_process_message_uc() -> ProcessMessageUseCase:
    return ProcessMessageUseCase(
        bot_repo=get_bot_sender(),
        state_manager=get_state_manager(),
        photo_process=get_process_photo_uc(),
        report_manager=get_report_data_manager(),
        boundary=BOGOTA_BOUNDARY
    )

def get_process_callback_uc() -> ProcessCallbackUseCase:
    return ProcessCallbackUseCase(
        bot_repo=get_bot_sender(),
        state_manager=get_state_manager(),
        submit_report=get_submit_report_uc()
    )

def get_submit_report_uc() -> SubmitReportUseCase:
    return SubmitReportUseCase(
        photo_source=get_photo_source(),
        report_data_manager=get_report_data_manager(),
        report_api=get_report_api(),
    )