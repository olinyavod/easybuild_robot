"""
Main entry point for EasyBuild Bot with Dependency Injection Container.

This version uses Command Pattern architecture with full DI support.
"""
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application

from src.easybuild_bot.di import Container
from src.easybuild_bot.bot import EasyBuildBot, post_init
from src.easybuild_bot.speech_recognition import SpeechRecognitionService
from src.easybuild_bot.text_to_speech import TextToSpeechService


def main() -> None:
    """Main function to initialize and run the bot with DI Container."""
    load_dotenv()
    
    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    
    # Get bot token from environment
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is required")
    
    admin_token = os.getenv("ADMIN_TOKEN", token)  # Use BOT_TOKEN as fallback
    
    # Setup data directories
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    monty_dir = os.getenv("MONTYDB_DIR", os.path.join(data_dir, "monty"))
    os.makedirs(monty_dir, exist_ok=True)
    monty_db = os.getenv("MONTYDB_DB", "easybuild_bot")
    
    # Initialize DI Container
    logger.info("Initializing Dependency Injection Container...")
    container = Container()
    
    # Configure container
    container.config.set("database.dir_path", monty_dir)
    container.config.set("database.db_name", monty_db)
    container.config.set("command_matcher.model_name", "cointegrated/rubert-tiny")
    container.config.set("command_matcher.threshold", 0.5)
    container.config.set("bot.admin_token", admin_token)
    
    # Get dependencies from container
    logger.info("Resolving dependencies from container...")
    storage = container.storage()
    command_registry = container.command_registry()
    command_executor = container.command_executor()
    
    # Initialize optional services
    whisper_model = os.getenv("WHISPER_MODEL", "base")
    speech_service = None
    try:
        logger.info(f"Initializing speech recognition service with model: {whisper_model}")
        speech_service = SpeechRecognitionService(
            model_name=whisper_model,
            language="ru"
        )
        logger.info("✅ Speech recognition service initialized")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize speech recognition service: {e}")
        logger.warning("Bot will run without speech recognition support")
    
    # Initialize text-to-speech service
    tts_speaker = os.getenv("TTS_SPEAKER", "baya")  # Default female voice
    tts_service = None
    try:
        logger.info(f"Initializing text-to-speech service with speaker: {tts_speaker}")
        tts_service = TextToSpeechService(
            language="ru",
            speaker=tts_speaker,
            sample_rate=48000
        )
        logger.info("✅ Text-to-speech service initialized")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize text-to-speech service: {e}")
        logger.warning("Bot will run without text-to-speech support")
    
    # Create bot instance with Command Pattern architecture
    logger.info("Creating bot instance with Command Pattern architecture...")
    bot = EasyBuildBot(
        storage=storage,
        command_registry=command_registry,
        command_executor=command_executor,
        admin_token=admin_token,
        speech_service=speech_service,
        tts_service=tts_service
    )
    
    # Log registered commands
    all_commands = command_registry.get_all_commands()
    logger.info(f"📋 Registered {len(all_commands)} commands:")
    for cmd in all_commands:
        logger.info(f"  • {cmd.get_command_name()}")
    
    # Create Telegram application
    logger.info("Building Telegram application...")
    app = Application.builder().token(token).post_init(post_init).build()
    
    # Setup handlers
    logger.info("Setting up bot handlers...")
    bot.setup_handlers(app)
    
    # Run bot
    logger.info("=" * 60)
    logger.info("🚀 Starting EasyBuild Bot with Command Pattern Architecture")
    logger.info("=" * 60)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

