"""
Dependency Injection container for EasyBuild Bot.

Uses dependency_injector library for managing dependencies.
"""
import logging
from typing import Optional
from dependency_injector import containers, providers
from .config import Settings
from .storage import Storage
from .access_control import AccessControlService
from .commands import create_command_system
from .speech_recognition import SpeechRecognitionService
from .text_to_speech import TextToSpeechService
from .bot import EasyBuildBot

logger = logging.getLogger(__name__)


def create_speech_service(settings: Settings) -> Optional[SpeechRecognitionService]:
    """
    Фабрика для создания сервиса распознавания речи.
    
    Returns:
        SpeechRecognitionService если включено, иначе None
    """
    if not settings.whisper_enabled:
        logger.info("⚠️ Speech recognition disabled in settings")
        return None
    
    try:
        logger.info(f"Initializing speech recognition service with model: {settings.whisper_model}")
        service = SpeechRecognitionService(
            model_name=settings.whisper_model,
            language=settings.whisper_language
        )
        logger.info("✅ Speech recognition service initialized")
        return service
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize speech recognition service: {e}")
        logger.warning("Bot will run without speech recognition support")
        return None


def create_tts_service(settings: Settings) -> Optional[TextToSpeechService]:
    """
    Фабрика для создания сервиса синтеза речи.
    
    Returns:
        TextToSpeechService если включено, иначе None
    """
    if not settings.tts_enabled:
        logger.info("⚠️ Text-to-speech disabled in settings")
        return None
    
    try:
        logger.info(f"Initializing text-to-speech service with speaker: {settings.tts_speaker}")
        service = TextToSpeechService(
            language=settings.tts_language,
            speaker=settings.tts_speaker,
            sample_rate=settings.tts_sample_rate
        )
        logger.info("✅ Text-to-speech service initialized")
        return service
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize text-to-speech service: {e}")
        logger.warning("Bot will run without text-to-speech support")
        return None


class Container(containers.DeclarativeContainer):
    """DI Container для всех зависимостей приложения."""
    
    # ========== Конфигурация ==========
    settings = providers.Singleton(Settings.from_env)
    
    # ========== База данных ==========
    storage = providers.Singleton(
        Storage,
        dir_path=settings.provided.montydb_dir,
        db_name=settings.provided.montydb_name,
    )
    
    # ========== Контроль доступа ==========
    access_control = providers.Singleton(
        AccessControlService,
        storage=storage,
    )
    
    # ========== Command Pattern система ==========
    command_system = providers.Singleton(
        create_command_system,
        storage=storage,
        access_control=access_control,
        model_name=settings.provided.command_matcher_model,
        threshold=settings.provided.command_matcher_threshold,
    )
    
    # Извлечение registry и executor из command_system tuple
    command_registry = providers.Callable(
        lambda system: system[0],
        system=command_system
    )
    
    command_executor = providers.Callable(
        lambda system: system[1],
        system=command_system
    )
    
    # ========== Опциональные сервисы ==========
    speech_service = providers.Singleton(
        create_speech_service,
        settings=settings,
    )
    
    tts_service = providers.Singleton(
        create_tts_service,
        settings=settings,
    )
    
    # ========== Основной бот ==========
    bot = providers.Singleton(
        EasyBuildBot,
        storage=storage,
        access_control=access_control,
        command_registry=command_registry,
        command_executor=command_executor,
        admin_token=settings.provided.admin_token,
        speech_service=speech_service,
        tts_service=tts_service,
    )
