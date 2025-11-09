"""
Тестовый скрипт для проверки работы XamarinVersionService с новой логикой поиска версий.
"""

import sys
import os
import asyncio

# Добавляем путь к модулям бота
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from easybuild_bot.version_services.xamarin_version_service import XamarinVersionService
from easybuild_bot.models import Project, ProjectType


async def test_find_all_csproj():
    """Тест поиска всех .csproj файлов в проекте."""
    print("=" * 60)
    print("Тест 1: Поиск всех .csproj файлов")
    print("=" * 60)

    # Создаем тестовый проект
    # Укажите путь к вашему Xamarin проекту для тестирования
    test_project = Project(
        id="test-xamarin",
        name="Test Xamarin Project",
        project_type=ProjectType.XAMARIN,
        git_url="https://example.com/test.git",
        local_repo_path="/home/olinyavod/projects/easybuild_bot/repos/Fintech",  # Укажите реальный путь
        project_file_path="Fintech/Fintech.sln",  # Путь к .sln файлу
        dev_branch="develop",
        release_branch="master",
        allowed_group_ids=[]
    )

    service = XamarinVersionService()

    print(f"\nПроект: {test_project.name}")
    print(f"Папка проекта: {test_project.local_repo_path}")
    print(f"Файл проекта: {test_project.project_file_path}")

    # Проверяем, существует ли путь
    if not os.path.exists(test_project.local_repo_path):
        print(f"\n❌ ОШИБКА: Путь не существует: {test_project.local_repo_path}")
        print("Измените путь в скрипте на реальный путь к проекту Xamarin")
        return

    print("\nПоиск .csproj файлов...")
    csproj_files = service._find_all_csproj_files(test_project)

    if csproj_files:
        print(f"\n✅ Найдено {len(csproj_files)} .csproj файлов:")
        for file in csproj_files:
            print(f"  • {file}")
    else:
        print("\n❌ Не найдено ни одного .csproj файла")

    return csproj_files


async def test_get_version():
    """Тест получения версии из проекта."""
    print("\n" + "=" * 60)
    print("Тест 2: Получение версии из проекта")
    print("=" * 60)

    # Создаем тестовый проект
    test_project = Project(
        id="test-xamarin",
        name="Test Xamarin Project",
        project_type=ProjectType.XAMARIN,
        git_url="https://example.com/test.git",
        local_repo_path="/home/olinyavod/projects/easybuild_bot/repos/Fintech",  # Укажите реальный путь
        project_file_path="Fintech/Fintech.sln",  # Путь к .sln файлу
        dev_branch="develop",
        release_branch="master",
        allowed_group_ids=[]
    )

    service = XamarinVersionService()

    print(f"\nПроект: {test_project.name}")
    print(f"Папка проекта: {test_project.local_repo_path}")

    # Проверяем, существует ли путь
    if not os.path.exists(test_project.local_repo_path):
        print(f"\n❌ ОШИБКА: Путь не существует: {test_project.local_repo_path}")
        return

    print("\nПолучение версии...")
    version = await service.get_current_version(test_project)

    if version:
        print(f"\n✅ Версия найдена: {version}")
    else:
        print("\n❌ Версия не найдена")
        print("\nВозможные причины:")
        print("  1. В .csproj файлах нет тегов <Version>, <ApplicationVersion> или <ApplicationDisplayVersion>")
        print("  2. Указан неверный путь к проекту")
        print("\nПроверьте .csproj файлы и добавьте один из тегов:")
        print("  <PropertyGroup>")
        print("    <Version>1.0.0</Version>")
        print("  </PropertyGroup>")


async def test_platform_projects():
    """Тест поиска платформенных проектов."""
    print("\n" + "=" * 60)
    print("Тест 3: Поиск платформенных проектов")
    print("=" * 60)

    test_project = Project(
        id="test-xamarin",
        name="Test Xamarin Project",
        project_type=ProjectType.XAMARIN,
        git_url="https://example.com/test.git",
        local_repo_path="/home/olinyavod/projects/easybuild_bot/repos/Fintech",  # Укажите реальный путь
        project_file_path="Fintech/Fintech.sln",
        dev_branch="develop",
        release_branch="master",
        allowed_group_ids=[]
    )

    service = XamarinVersionService()

    print(f"\nПроект: {test_project.name}")

    # Проверяем, существует ли путь
    if not os.path.exists(test_project.local_repo_path):
        print(f"\n❌ ОШИБКА: Путь не существует: {test_project.local_repo_path}")
        return

    print("\nПоиск платформенных проектов (.Android.csproj, .iOS.csproj и т.д.)...")
    platform_projects = service._find_platform_projects(test_project)

    if platform_projects:
        print(f"\n✅ Найдено {len(platform_projects)} платформенных проектов:")
        for file in platform_projects:
            print(f"  • {file}")
    else:
        print("\n⚠️  Не найдено платформенных проектов")
        print("Это нормально, если проект не использует платформенную структуру")


async def main():
    """Основная функция запуска тестов."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Тестирование XamarinVersionService" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")

    print("\n⚠️  ВАЖНО: Измените путь к проекту в скрипте перед запуском!")
    print("   Текущий путь: /home/olinyavod/projects/easybuild_bot/repos/Fintech")
    print()

    try:
        # Тест 1: Поиск всех .csproj файлов
        csproj_files = await test_find_all_csproj()

        # Тест 2: Получение версии
        await test_get_version()

        # Тест 3: Поиск платформенных проектов
        await test_platform_projects()

        print("\n" + "=" * 60)
        print("Тестирование завершено")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Ошибка при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
