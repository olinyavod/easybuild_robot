"""
Text-to-speech service using Silero TTS.
"""
import os
import logging
import tempfile
import torch
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class TextToSpeechService:
    """Service for text-to-speech conversion using Silero TTS."""
    
    def __init__(self, language: str = "ru", speaker: str = "baya", sample_rate: int = 48000):
        """
        Initialize the text-to-speech service.
        
        Args:
            language: Language code (ru, en, de, es, fr)
            speaker: Speaker name for Russian: aidar, baya, kseniya, natasha, ruslan, irina
            sample_rate: Audio sample rate (8000, 16000, 48000)
        """
        self.language = language
        self.speaker = speaker
        self.sample_rate = sample_rate
        self._model = None
        self._device = torch.device('cpu')  # Use CPU for compatibility
        
        # Map sample rate to model suffix
        self._rate_suffix = ""
        if sample_rate == 8000:
            self._rate_suffix = "_8khz"
        elif sample_rate == 16000:
            self._rate_suffix = "_16khz"
        # 48000 uses default (no suffix needed for most speakers)
        
        logger.info(f"Initializing TextToSpeechService with language: {language}, speaker: {speaker}, sample_rate: {sample_rate}")
    
    @property
    def model(self):
        """Lazy load the Silero TTS model."""
        if self._model is None:
            logger.info(f"Loading Silero TTS model for language: {self.language}")
            try:
                # Determine model name based on language
                if self.language == "ru":
                    model_name = "v4_ru"  # Latest Russian model
                elif self.language == "en":
                    model_name = "v3_en"
                elif self.language == "de":
                    model_name = "v3_de"
                elif self.language == "es":
                    model_name = "v3_es"
                elif self.language == "fr":
                    model_name = "v3_fr"
                else:
                    model_name = "v4_ru"  # Default to Russian
                
                # Load Silero TTS model from torch hub
                # Note: torch.hub.load returns (model, example_text, sample_rate, speakers, apply_tts)
                result = torch.hub.load(
                    repo_or_dir='snakers4/silero-models',
                    model='silero_tts',
                    language=self.language,
                    speaker=model_name  # This is the model identifier, not speaker name
                )
                
                # Extract model from tuple if needed
                if isinstance(result, tuple):
                    self._model = result[0]  # First element is the model
                else:
                    self._model = result
                    
                self._model.to(self._device)
                logger.info(f"Silero TTS model loaded successfully: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load Silero TTS model: {e}", exc_info=True)
                raise
        return self._model
    
    def synthesize_to_file(self, text: str, output_path: str) -> bool:
        """
        Synthesize text to audio file.
        
        Args:
            text: Text to synthesize
            output_path: Path to save the audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Synthesizing text to audio: {text[:50]}...")
            
            # Generate audio
            # For v4_ru model, speaker is passed directly to apply_tts
            audio = self.model.apply_tts(
                text=text,
                speaker=self.speaker,  # This is the actual voice name: baya, aidar, etc.
                sample_rate=self.sample_rate
            )
            
            # Save audio to file using soundfile
            import soundfile as sf
            # Convert tensor to numpy if needed
            if hasattr(audio, 'cpu'):
                audio_np = audio.cpu().numpy()
            else:
                audio_np = audio
            
            sf.write(output_path, audio_np, self.sample_rate)
            
            logger.info(f"Audio saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error synthesizing text: {e}", exc_info=True)
            return False
    
    async def synthesize_to_temp_file(self, text: str) -> Optional[str]:
        """
        Synthesize text to a temporary audio file.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Path to temporary audio file or None if failed
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                file_path = temp_file.name
            
            # Synthesize
            if self.synthesize_to_file(text, file_path):
                return file_path
            else:
                # Clean up if failed
                try:
                    os.unlink(file_path)
                except:
                    pass
                return None
                
        except Exception as e:
            logger.error(f"Error creating temporary audio file: {e}", exc_info=True)
            return None
    
    def get_available_speakers(self) -> list:
        """
        Get list of available speakers for current language.
        
        Returns:
            List of speaker names
        """
        speakers_map = {
            'ru': ['aidar', 'baya', 'kseniya', 'xenia', 'eugene'],  # v4_ru model speakers
            'en': ['en_0', 'en_1', 'en_2'],
            'de': ['bernd', 'eva_k', 'karlsson'],
            'es': ['es_0', 'es_1'],
            'fr': ['fr_0', 'fr_1']
        }
        return speakers_map.get(self.language, ['baya'])
    
    def set_speaker(self, speaker: str):
        """
        Change the speaker voice.
        
        Args:
            speaker: Speaker name
        """
        available = self.get_available_speakers()
        if speaker in available:
            self.speaker = speaker
            logger.info(f"Speaker changed to: {speaker}")
        else:
            logger.warning(f"Speaker '{speaker}' not available. Available speakers: {available}")

