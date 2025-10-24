"""
Main entry point for EasyBuild Bot with Dependency Injection.
"""
import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application
from src.easybuild_bot.storage import Storage
from src.easybuild_bot.command_matcher import CommandMatcher
from src.easybuild_bot.speech_recognition import SpeechRecognitionService
from src.easybuild_bot.text_to_speech import TextToSpeechService
from src.easybuild_bot.bot import EasyBuildBot, post_init


def main() -> None:
    """Main function to initialize and run the bot."""
    load_dotenv()
    
    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Get configuration from environment
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN not set")
    
    # Setup data directories
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    monty_dir = os.getenv("MONTYDB_DIR", os.path.join(data_dir, "monty"))
    os.makedirs(monty_dir, exist_ok=True)
    monty_db = os.getenv("MONTYDB_DB", "easybuild_bot")
    
    # Initialize dependencies
    storage = Storage(dir_path=monty_dir, db_name=monty_db)
    command_matcher = CommandMatcher(
        model_name="cointegrated/rubert-tiny",
        threshold=0.5
    )
    
    # Initialize speech recognition service
    whisper_model = os.getenv("WHISPER_MODEL", "base")
    speech_service = None
    try:
        speech_service = SpeechRecognitionService(
            model_name=whisper_model,
            language="ru"
        )
        logging.info(f"Speech recognition service initialized with model: {whisper_model}")
    except Exception as e:
        logging.warning(f"Failed to initialize speech recognition service: {e}")
        logging.warning("Bot will run without speech recognition support")
    
    # Initialize text-to-speech service
    tts_speaker = os.getenv("TTS_SPEAKER", "baya")  # Default female voice
    tts_service = None
    try:
        tts_service = TextToSpeechService(
            language="ru",
            speaker=tts_speaker,
            sample_rate=48000
        )
        logging.info(f"Text-to-speech service initialized with speaker: {tts_speaker}")
    except Exception as e:
        logging.warning(f"Failed to initialize text-to-speech service: {e}")
        logging.warning("Bot will run without text-to-speech support")
    
    # Create bot instance with dependencies
    bot = EasyBuildBot(
        storage=storage,
        command_matcher=command_matcher,
        admin_token=token,
        speech_service=speech_service,
        tts_service=tts_service
    )
    
    # Create Telegram application
    app = Application.builder().token(token).post_init(post_init).build()
    
    # Setup handlers
    bot.setup_handlers(app)
    
    # Run bot
    logging.info("Starting EasyBuild Bot...")
    app.run_polling()


if __name__ == "__main__":
    main()

