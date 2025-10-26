"""
Main entry point for EasyBuild Bot with full Dependency Injection.

Эта версия использует полностью автоматический DI - все зависимости
разрешаются контейнером, ничего не создаётся вручную.
"""
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application

from src.easybuild_bot.di import Container
from src.easybuild_bot.bot import post_init


def main() -> None:
    """Главная функция для инициализации и запуска бота с полным DI."""
    # Загружаем переменные окружения из .env файла
    load_dotenv()
    
    # Инициализируем DI Container
    container = Container()
    
    # Получаем настройки для логирования
    settings = container.settings()
    
    # Настройка логирования
    logging.basicConfig(
        format=settings.log_format,
        level=getattr(logging, settings.log_level.upper())
    )
    logger = logging.getLogger(__name__)
    
    # Логируем текущую конфигурацию (без секретов)
    logger.info("=" * 60)
    logger.info("🔧 Конфигурация приложения:")
    for key, value in settings.to_dict().items():
        logger.info(f"  • {key}: {value}")
    logger.info("=" * 60)
    
    # Получаем полностью сконфигурированный бот из контейнера
    # Все зависимости разрешаются автоматически!
    logger.info("Resolving dependencies from DI container...")
    bot = container.bot()
    
    # Логируем зарегистрированные команды
    command_registry = container.command_registry()
    all_commands = command_registry.get_all_commands()
    logger.info(f"📋 Registered {len(all_commands)} commands:")
    for cmd in all_commands:
        logger.info(f"  • {cmd.get_command_name()}")
    
    # Создаём Telegram приложение
    logger.info("Building Telegram application...")
    app = Application.builder().token(settings.bot_token).post_init(post_init).build()
    
    # Настраиваем обработчики
    logger.info("Setting up bot handlers...")
    bot.setup_handlers(app)
    
    # Запускаем бота
    logger.info("=" * 60)
    logger.info("🚀 Starting EasyBuild Bot with Full Dependency Injection")
    logger.info("=" * 60)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

