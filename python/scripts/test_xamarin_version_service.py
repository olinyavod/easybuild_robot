#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы XamarinVersionService с множественными платформенными проектами.
"""

import asyncio
import tempfile
import os
from pathlib import Path

# Добавляем путь к модулю
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from easybuild_bot.version_services.xamarin_version_service import XamarinVersionService
from easybuild_bot.models import Project, ProjectType


def create_test_csproj(path: str, project_name: str, version: str = "1.0.0"):
    """Создаёт тестовый .csproj файл"""
    content = f"""<?xml version="1.0" encoding="utf-8"?>
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
    <OutputType>Exe</OutputType>
    <Version>{version}</Version>
    <ApplicationVersion>{version}</ApplicationVersion>
    <ApplicationDisplayVersion>{version}</ApplicationDisplayVersion>
  </PropertyGroup>
</Project>
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Создан тестовый проект: {path}")


async def test_xamarin_service():
    """Тестирует работу XamarinVersionService"""
    print("=" * 70)
    print("Тестирование XamarinVersionService для Xamarin проектов")
    print("=" * 70)
    
    # Создаём временную директорию для тестов
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\n📁 Временная директория: {temp_dir}\n")
        
        # Создаём структуру проекта Xamarin
        base_name = "MyXamarinApp"
        
        # Основной проект (может не содержать версии)
        main_project_path = os.path.join(temp_dir, f"{base_name}.csproj")
        create_test_csproj(main_project_path, base_name, "1.2.3")
        
        # Платформенные проекты
        android_project_path = os.path.join(temp_dir, f"{base_name}.Android", f"{base_name}.Android.csproj")
        create_test_csproj(android_project_path, f"{base_name}.Android", "1.2.3")
        
        ios_project_path = os.path.join(temp_dir, f"{base_name}.iOS", f"{base_name}.iOS.csproj")
        create_test_csproj(ios_project_path, f"{base_name}.iOS", "1.2.3")
        
        # Создаём проект
        project = Project(
            id="test-xamarin-project",
            name=base_name,
            project_type=ProjectType.XAMARIN,
            git_url="https://github.com/test/test.git",
            project_file_path=f"{base_name}.csproj",
            local_repo_path=temp_dir,
            dev_branch="develop",
            release_branch="main"
        )
        
        # Создаём сервис
        service = XamarinVersionService()
        
        # Тест 1: Получение текущей версии
        print("\n" + "─" * 70)
        print("ТЕСТ 1: Получение текущей версии")
        print("─" * 70)
        
        current_version = await service.get_current_version(project)
        if current_version:
            print(f"✅ Текущая версия обнаружена: {current_version}")
        else:
            print("❌ Не удалось получить текущую версию")
            return
        
        # Тест 2: Обновление версии
        print("\n" + "─" * 70)
        print("ТЕСТ 2: Обновление версии")
        print("─" * 70)
        
        new_version = "2.0.0"
        print(f"Обновляем версию с {current_version} на {new_version}...\n")
        
        success, message = await service.update_version(project, new_version)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            return
        
        # Тест 3: Проверка, что версия обновилась во всех файлах
        print("\n" + "─" * 70)
        print("ТЕСТ 3: Проверка обновлённых версий")
        print("─" * 70)
        
        updated_version = await service.get_current_version(project)
        if updated_version == new_version:
            print(f"✅ Версия успешно обновлена: {updated_version}")
        else:
            print(f"❌ Версия не обновилась корректно. Ожидалось: {new_version}, получено: {updated_version}")
            return
        
        # Проверяем каждый файл отдельно
        print("\nПроверка отдельных файлов:")
        test_files = [
            (main_project_path, "Основной проект"),
            (android_project_path, "Android проект"),
            (ios_project_path, "iOS проект")
        ]
        
        for file_path, file_desc in test_files:
            file_version = service._get_version_from_csproj(file_path)
            if file_version == new_version:
                print(f"  ✅ {file_desc}: {file_version}")
            else:
                print(f"  ❌ {file_desc}: ожидалось {new_version}, получено {file_version}")
        
        print("\n" + "=" * 70)
        print("Все тесты пройдены успешно! ✅")
        print("=" * 70)


async def test_xamarin_service_no_platform_projects():
    """Тестирует работу с проектом без платформенных подпроектов"""
    print("\n\n" + "=" * 70)
    print("Тестирование XamarinVersionService (проект без платформенных подпроектов)")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\n📁 Временная директория: {temp_dir}\n")
        
        # Создаём только основной проект
        base_name = "SimpleXamarinApp"
        main_project_path = os.path.join(temp_dir, f"{base_name}.csproj")
        create_test_csproj(main_project_path, base_name, "1.0.0")
        
        project = Project(
            id="test-simple-xamarin",
            name=base_name,
            project_type=ProjectType.XAMARIN,
            git_url="https://github.com/test/test.git",
            project_file_path=f"{base_name}.csproj",
            local_repo_path=temp_dir,
            dev_branch="develop",
            release_branch="main"
        )
        
        service = XamarinVersionService()
        
        # Получение версии
        current_version = await service.get_current_version(project)
        print(f"Текущая версия: {current_version}")
        
        # Обновление версии
        success, message = await service.update_version(project, "1.1.0")
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
        
        # Проверка обновлённой версии
        updated_version = await service.get_current_version(project)
        print(f"Обновлённая версия: {updated_version}")
        
        print("\n" + "=" * 70)
        print("Тест завершён! ✅")
        print("=" * 70)


if __name__ == "__main__":
    print("\n🧪 Запуск тестов XamarinVersionService\n")
    
    asyncio.run(test_xamarin_service())
    asyncio.run(test_xamarin_service_no_platform_projects())
    
    print("\n\n🎉 Все тесты завершены!")







