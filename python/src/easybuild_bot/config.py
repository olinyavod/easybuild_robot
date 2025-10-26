"""
Конфигурация приложения.

Этот модуль содержит класс Settings для централизованного управления настройками,
загружаемыми из переменных окружения с разумными значениями по умолчанию.
"""
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Settings:
    """
    Настройки приложения, загружаемые из переменных окружения.
    
    Все параметры, которые могут быть переопределены через .env файл,
    должны быть определены здесь с разумными значениями по умолчанию.
    """
    
    # ========== Обязательные параметры ==========
    bot_token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    
    # ========== Telegram Bot настройки ==========
    admin_token: Optional[str] = field(
        default_factory=lambda: os.getenv("ADMIN_TOKEN")
    )
    
    # ========== База данных ==========
    data_dir: str = field(
        default_factory=lambda: os.getenv("DATA_DIR", os.path.join(os.getcwd(), "data"))
    )
    montydb_dir: Optional[str] = field(
        default_factory=lambda: os.getenv("MONTYDB_DIR")
    )
    montydb_name: str = field(
        default_factory=lambda: os.getenv("MONTYDB_DB", "easybuild_bot")
    )
    
    # ========== Command Matcher (Semantic Search) ==========
    command_matcher_model: str = field(
        default_factory=lambda: os.getenv("COMMAND_MATCHER_MODEL", "cointegrated/rubert-tiny")
    )
    command_matcher_threshold: float = field(
        default_factory=lambda: float(os.getenv("COMMAND_MATCHER_THRESHOLD", "0.5"))
    )
    
    # ========== Speech Recognition (Whisper) ==========
    whisper_enabled: bool = field(
        default_factory=lambda: os.getenv("WHISPER_ENABLED", "true").lower() == "true"
    )
    whisper_model: str = field(
        default_factory=lambda: os.getenv("WHISPER_MODEL", "base")
    )
    whisper_language: str = field(
        default_factory=lambda: os.getenv("WHISPER_LANGUAGE", "ru")
    )
    
    # ========== Text-to-Speech (Silero TTS) ==========
    tts_enabled: bool = field(
        default_factory=lambda: os.getenv("TTS_ENABLED", "true").lower() == "true"
    )
    tts_language: str = field(
        default_factory=lambda: os.getenv("TTS_LANGUAGE", "ru")
    )
    tts_speaker: str = field(
        default_factory=lambda: os.getenv("TTS_SPEAKER", "baya")
    )
    tts_sample_rate: int = field(
        default_factory=lambda: int(os.getenv("TTS_SAMPLE_RATE", "48000"))
    )
    
    # ========== Логирование ==========
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    log_format: str = field(
        default_factory=lambda: os.getenv(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    
    def __post_init__(self):
        """Валидация и дополнительная обработка настроек после инициализации."""
        # Проверка обязательных параметров
        if not self.bot_token:
            raise ValueError("BOT_TOKEN обязательна для работы бота")
        
        # Если admin_token не указан, используем bot_token
        if not self.admin_token:
            self.admin_token = self.bot_token
        
        # Создаём директорию для данных если не существует
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Если montydb_dir не указан, используем data_dir/monty
        if not self.montydb_dir:
            self.montydb_dir = os.path.join(self.data_dir, "monty")
        
        # Создаём директорию для монти если не существует
        os.makedirs(self.montydb_dir, exist_ok=True)
        
        # Валидация sample rate
        valid_sample_rates = [8000, 16000, 48000]
        if self.tts_sample_rate not in valid_sample_rates:
            raise ValueError(
                f"TTS_SAMPLE_RATE должен быть одним из {valid_sample_rates}, "
                f"получен: {self.tts_sample_rate}"
            )
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """
        Создать экземпляр Settings из переменных окружения.
        
        Этот метод удобен для явного указания источника настроек.
        """
        return cls()
    
    def to_dict(self) -> dict:
        """Преобразовать настройки в словарь для логирования или отладки."""
        return {
            "bot_token": "***" if self.bot_token else None,  # Скрываем токен
            "admin_token": "***" if self.admin_token else None,
            "data_dir": self.data_dir,
            "montydb_dir": self.montydb_dir,
            "montydb_name": self.montydb_name,
            "command_matcher_model": self.command_matcher_model,
            "command_matcher_threshold": self.command_matcher_threshold,
            "whisper_enabled": self.whisper_enabled,
            "whisper_model": self.whisper_model,
            "whisper_language": self.whisper_language,
            "tts_enabled": self.tts_enabled,
            "tts_language": self.tts_language,
            "tts_speaker": self.tts_speaker,
            "tts_sample_rate": self.tts_sample_rate,
            "log_level": self.log_level,
        }

