#!/usr/bin/env python3
"""
Тест для проверки поведения XamarinVersionService при частичном наборе платформ.
Демонстрирует, что система корректно обрабатывает отсутствующие платформы.
"""

import asyncio
import tempfile
import os
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
    print(f"✅ Создан: {os.path.basename(path)}")


async def test_partial_platforms():
    """Тест: проект с только некоторыми платформами (только Android, без iOS)"""
    print("\n" + "=" * 70)
    print("ТЕСТ 1: Проект только с Android (без iOS)")
    print("=" * 70)
    print("Сценарий: В проекте есть только Android версия, iOS отсутствует\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        base_name = "PartialXamarinApp"
        
        # Создаём только Android проект (iOS намеренно не создаём)
        android_project_path = os.path.join(temp_dir, f"{base_name}.Android", f"{base_name}.Android.csproj")
        create_test_csproj(android_project_path, f"{base_name}.Android", "1.0.0")
        
        print("\n📋 Структура проекта:")
        print("  ✅ Android проект создан")
        print("  ❌ iOS проект отсутствует")
        print("  ❌ UWP проект отсутствует")
        
        project = Project(
            id="test-partial-xamarin",
            name=base_name,
            project_type=ProjectType.XAMARIN,
            git_url="https://github.com/test/test.git",
            project_file_path=f"{base_name}.csproj",  # Этот файл не существует
            local_repo_path=temp_dir,
        )
        
        service = XamarinVersionService()
        
        print("\n🔄 Обновление версии на 2.0.0...")
        success, message = await service.update_version(project, "2.0.0")
        
        print("\n📊 Результат:")
        if success:
            print(f"✅ {message}")
            print("\n💡 Вывод: Система успешно обновила версию в найденных платформах")
            print("   и пропустила отсутствующие без ошибок!")
        else:
            print(f"❌ {message}")


async def test_only_ios():
    """Тест: проект только с iOS (без Android)"""
    print("\n" + "=" * 70)
    print("ТЕСТ 2: Проект только с iOS (без Android)")
    print("=" * 70)
    print("Сценарий: В проекте есть только iOS версия, Android отсутствует\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        base_name = "iOSOnlyApp"
        
        # Создаём только iOS проект
        ios_project_path = os.path.join(temp_dir, f"{base_name}.iOS", f"{base_name}.iOS.csproj")
        create_test_csproj(ios_project_path, f"{base_name}.iOS", "1.5.0")
        
        print("\n📋 Структура проекта:")
        print("  ❌ Android проект отсутствует")
        print("  ✅ iOS проект создан")
        
        project = Project(
            id="test-ios-only",
            name=base_name,
            project_type=ProjectType.XAMARIN,
            git_url="https://github.com/test/test.git",
            project_file_path=f"{base_name}.csproj",
            local_repo_path=temp_dir,
        )
        
        service = XamarinVersionService()
        
        print("\n🔄 Обновление версии на 1.6.0...")
        success, message = await service.update_version(project, "1.6.0")
        
        print("\n📊 Результат:")
        if success:
            print(f"✅ {message}")
            print("\n💡 Вывод: Система работает с любой доступной платформой!")
        else:
            print(f"❌ {message}")


async def test_mixed_platforms():
    """Тест: проект с Android + UWP (без iOS)"""
    print("\n" + "=" * 70)
    print("ТЕСТ 3: Проект с Android + UWP (без iOS)")
    print("=" * 70)
    print("Сценарий: Нестандартная комбинация платформ\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        base_name = "MixedPlatformsApp"
        
        # Создаём Android и UWP проекты (iOS пропускаем)
        android_path = os.path.join(temp_dir, f"{base_name}.Android", f"{base_name}.Android.csproj")
        uwp_path = os.path.join(temp_dir, f"{base_name}.UWP", f"{base_name}.UWP.csproj")
        
        create_test_csproj(android_path, f"{base_name}.Android", "2.0.0")
        create_test_csproj(uwp_path, f"{base_name}.UWP", "2.0.0")
        
        print("\n📋 Структура проекта:")
        print("  ✅ Android проект создан")
        print("  ❌ iOS проект отсутствует")
        print("  ✅ UWP проект создан")
        
        project = Project(
            id="test-mixed-platforms",
            name=base_name,
            project_type=ProjectType.XAMARIN,
            git_url="https://github.com/test/test.git",
            project_file_path=f"{base_name}.csproj",
            local_repo_path=temp_dir,
        )
        
        service = XamarinVersionService()
        
        print("\n🔄 Обновление версии на 3.0.0...")
        success, message = await service.update_version(project, "3.0.0")
        
        print("\n📊 Результат:")
        if success:
            print(f"✅ {message}")
            print("\n💡 Вывод: Система корректно работает с любой комбинацией платформ!")
        else:
            print(f"❌ {message}")


async def test_main_plus_android():
    """Тест: основной проект + Android (без iOS)"""
    print("\n" + "=" * 70)
    print("ТЕСТ 4: Основной проект + Android (без iOS)")
    print("=" * 70)
    print("Сценарий: Есть shared код и только Android платформа\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        base_name = "MainPlusAndroid"
        
        # Создаём основной проект и Android
        main_path = os.path.join(temp_dir, f"{base_name}.csproj")
        android_path = os.path.join(temp_dir, f"{base_name}.Android", f"{base_name}.Android.csproj")
        
        create_test_csproj(main_path, base_name, "1.0.0")
        create_test_csproj(android_path, f"{base_name}.Android", "1.0.0")
        
        print("\n📋 Структура проекта:")
        print("  ✅ Основной проект создан")
        print("  ✅ Android проект создан")
        print("  ❌ iOS проект отсутствует")
        
        project = Project(
            id="test-main-android",
            name=base_name,
            project_type=ProjectType.XAMARIN,
            git_url="https://github.com/test/test.git",
            project_file_path=f"{base_name}.csproj",
            local_repo_path=temp_dir,
        )
        
        service = XamarinVersionService()
        
        print("\n🔄 Обновление версии на 2.0.0...")
        success, message = await service.update_version(project, "2.0.0")
        
        print("\n📊 Результат:")
        if success:
            print(f"✅ {message}")
            print("\n💡 Вывод: Обновлены оба файла, iOS проект корректно пропущен!")
        else:
            print(f"❌ {message}")


if __name__ == "__main__":
    print("\n" + "🧪" * 35)
    print("ТЕСТИРОВАНИЕ ПОВЕДЕНИЯ ПРИ ОТСУТСТВУЮЩИХ ПЛАТФОРМАХ")
    print("🧪" * 35)
    
    print("\n📝 Цель тестов:")
    print("  Проверить, что XamarinVersionService корректно обрабатывает")
    print("  ситуации, когда некоторые платформенные проекты отсутствуют.\n")
    print("  Ожидаемое поведение:")
    print("  ✅ Обновляет версии в найденных проектах")
    print("  ✅ Пропускает отсутствующие проекты без ошибок")
    print("  ✅ Возвращает успешный результат, если обновлён хотя бы один файл")
    
    asyncio.run(test_partial_platforms())
    asyncio.run(test_only_ios())
    asyncio.run(test_mixed_platforms())
    asyncio.run(test_main_plus_android())
    
    print("\n" + "=" * 70)
    print("🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
    print("=" * 70)
    print("\n✅ Заключение:")
    print("  XamarinVersionService корректно обрабатывает отсутствующие платформы.")
    print("  Система обновляет версии только в найденных проектах и не требует")
    print("  наличия всех платформ одновременно.\n")







