"""
Speech recognition service using Whisper.
"""
import os
import logging
import tempfile
from pathlib import Path
from typing import Optional
import whisper

logger = logging.getLogger(__name__)


class SpeechRecognitionService:
    """Service for speech-to-text conversion using Whisper."""
    
    def __init__(self, model_name: str = "base", language: str = "ru"):
        """
        Initialize the speech recognition service.
        
        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
            language: Language code for transcription (default: ru)
        """
        self.model_name = model_name
        self.language = language
        self._model = None
        logger.info(f"Initializing SpeechRecognitionService with model: {model_name}")
    
    @property
    def model(self):
        """Lazy load the Whisper model."""
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self._model = whisper.load_model(self.model_name)
            logger.info("Model loaded successfully")
        return self._model
    
    async def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            # Transcribe using Whisper
            result = self.model.transcribe(
                audio_file_path,
                language=self.language,
                fp16=False  # Use FP32 for CPU compatibility
            )
            
            text = result["text"].strip()
            logger.info(f"Transcription successful: {text[:100]}...")
            return text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}", exc_info=True)
            return None
    
    async def transcribe_telegram_voice(self, voice_file) -> Optional[str]:
        """
        Transcribe Telegram voice message.
        
        Args:
            voice_file: Telegram voice file object
            
        Returns:
            Transcribed text or None if failed
        """
        temp_file = None
        try:
            # Download voice message to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
                file_path = temp_file.name
                await voice_file.download_to_drive(file_path)
                logger.info(f"Voice message downloaded to: {file_path}")
            
            # Transcribe
            text = await self.transcribe_audio(file_path)
            
            return text
            
        except Exception as e:
            logger.error(f"Error processing voice message: {e}", exc_info=True)
            return None
        finally:
            # Clean up temporary file
            if temp_file:
                try:
                    os.unlink(file_path)
                    logger.debug(f"Temporary file deleted: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {file_path}: {e}")
    
    async def transcribe_telegram_audio(self, audio_file) -> Optional[str]:
        """
        Transcribe Telegram audio message.
        
        Args:
            audio_file: Telegram audio file object
            
        Returns:
            Transcribed text or None if failed
        """
        temp_file = None
        try:
            # Download audio message to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                file_path = temp_file.name
                await audio_file.download_to_drive(file_path)
                logger.info(f"Audio message downloaded to: {file_path}")
            
            # Transcribe
            text = await self.transcribe_audio(file_path)
            
            return text
            
        except Exception as e:
            logger.error(f"Error processing audio message: {e}", exc_info=True)
            return None
        finally:
            # Clean up temporary file
            if temp_file:
                try:
                    os.unlink(file_path)
                    logger.debug(f"Temporary file deleted: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {file_path}: {e}")

