#!/usr/bin/env python3
"""
Скрипт для тестирования определения версии в Xamarin проектах.
"""
import asyncio
import sys
import os
import logging

# Добавляем путь к модулям проекта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from easybuild_bot.storage import Storage
from easybuild_bot.version_services.xamarin_version_service import XamarinVersionService
from easybuild_bot.models import ProjectType

# Настраиваем логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_xamarin_version(project_name: str):
    """
    Тестирует определение версии для указанного Xamarin проекта.

    Args:
        project_name: Имя проекта для тестирования
    """
    logger.info(f"=== Тестирование определения версии для проекта: {project_name} ===\n")

    # Инициализируем хранилище
    storage = Storage()

    # Получаем проект из базы данных
    project = storage.get_project(project_name)

    if not project:
        logger.error(f"❌ Проект '{project_name}' не найден в базе данных")
        logger.info("\nДоступные проекты:")
        projects = storage.list_projects()
        for p in projects:
            logger.info(f"  • {p.name} (тип: {p.project_type.value})")
        return

    if project.project_type != ProjectType.XAMARIN:
        logger.error(f"❌ Проект '{project_name}' не является Xamarin проектом (тип: {project.project_type.value})")
        return

    logger.info(f"✓ Проект найден:")
    logger.info(f"  Имя: {project.name}")
    logger.info(f"  Тип: {project.project_type.value}")
    logger.info(f"  Git URL: {project.git_url}")
    logger.info(f"  Локальный путь: {project.local_repo_path}")
    logger.info(f"  Ветка релиза: {project.release_branch}")
    logger.info(f"  Файл проекта: {project.project_file_path}")
    logger.info("")

    # Проверяем, существует ли локальный репозиторий
    if not os.path.exists(project.local_repo_path):
        logger.error(f"❌ Локальный репозиторий не существует: {project.local_repo_path}")
        logger.info("Клонируйте репозиторий или выполните первую сборку")
        return

    logger.info(f"✓ Локальный репозиторий существует\n")

    # Создаем сервис версий
    version_service = XamarinVersionService()

    # Пытаемся получить версию
    logger.info("Попытка определить версию...\n")
    version = await version_service.get_current_version(project)

    logger.info("\n" + "="*60)
    if version:
        logger.info(f"✅ РЕЗУЛЬТАТ: Версия успешно определена: {version}")
    else:
        logger.error(f"❌ РЕЗУЛЬТАТ: Не удалось определить версию")
        logger.info("\nПроверьте логи выше для диагностики проблемы")
    logger.info("="*60)


async def main():
    """Главная функция."""
    if len(sys.argv) < 2:
        print("Использование: python test_xamarin_version.py <имя_проекта>")
        print("\nПример: python test_xamarin_version.py Fintech")
        sys.exit(1)

    project_name = sys.argv[1]
    await test_xamarin_version(project_name)


if __name__ == "__main__":
    asyncio.run(main())
