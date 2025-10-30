#!/usr/bin/env python3
"""
Debug script to check version detection for TechnouprApp.Client
"""
import os
import sys
import asyncio
import xml.etree.ElementTree as ET

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

async def main():
    """Check version detection."""
    from easybuild_bot.storage import Storage, REPOS_DIR
    from easybuild_bot.version_services import VersionServiceFactory
    
    # Initialize storage
    storage = Storage('/home/olinyavod/projects/easybuild_bot/data/monty', 'easybuild_bot')
    
    # Find TechnouprApp.Client project
    project = storage.get_project_by_name("TechnouprApp.Client")
    
    if not project:
        print("❌ Проект 'TechnouprApp.Client' не найден в базе данных")
        print("\nДоступные проекты:")
        for p in storage.get_all_projects():
            print(f"  - {p.name}")
        return
    
    print(f"✅ Проект найден: {project.name}")
    print(f"\nИнформация о проекте:")
    print(f"  ID: {project.id}")
    print(f"  Имя: {project.name}")
    print(f"  Тип: {project.project_type.value}")
    print(f"  Git URL: {project.git_url}")
    print(f"  Локальный путь: {project.local_repo_path}")
    print(f"  Путь к файлу проекта: {project.project_file_path}")
    print(f"  Ветка разработки: {project.dev_branch}")
    print(f"  Ветка релиза: {project.release_branch}")
    
    # Check if paths exist
    print(f"\n🔍 Проверка путей:")
    if os.path.exists(project.local_repo_path):
        print(f"  ✅ Локальный репозиторий существует: {project.local_repo_path}")
    else:
        print(f"  ❌ Локальный репозиторий не найден: {project.local_repo_path}")
    
    # Check project file path
    full_project_file_path = os.path.join(project.local_repo_path, project.project_file_path)
    print(f"\n  Полный путь к файлу проекта: {full_project_file_path}")
    if os.path.exists(full_project_file_path):
        print(f"  ✅ Файл проекта существует")
    else:
        print(f"  ❌ Файл проекта не найден")
    
    # Try to get version using version service
    version_service = VersionServiceFactory.create(project)
    if version_service:
        print(f"\n✅ Version service создан: {type(version_service).__name__}")
        
        # Try to get version
        print(f"\n🔎 Попытка получить версию...")
        try:
            version = await version_service.get_current_version(project)
            if version:
                print(f"  ✅ Текущая версия обнаружена: {version}")
            else:
                print(f"  ❌ Версия не обнаружена (get_current_version вернул None)")
                
                # Let's try to debug why
                print(f"\n🔧 Диагностика:")
                if os.path.exists(full_project_file_path):
                    try:
                        tree = ET.parse(full_project_file_path)
                        root = tree.getroot()
                        
                        print(f"  ✅ XML файл успешно распарсен")
                        print(f"  Корневой элемент: {root.tag}")
                        
                        # Try to find ApplicationDisplayVersion
                        found = False
                        for prop_group in root.findall('.//PropertyGroup'):
                            display_version_elem = prop_group.find('ApplicationDisplayVersion')
                            if display_version_elem is not None:
                                print(f"  ✅ Найден элемент ApplicationDisplayVersion")
                                print(f"     Значение: '{display_version_elem.text}'")
                                if display_version_elem.text:
                                    stripped = display_version_elem.text.strip()
                                    print(f"     После strip(): '{stripped}'")
                                else:
                                    print(f"     Элемент пустой (text is None или пустая строка)")
                                found = True
                        
                        if not found:
                            print(f"  ❌ Элемент ApplicationDisplayVersion не найден в файле")
                            print(f"\n  Список всех PropertyGroup элементов:")
                            for i, prop_group in enumerate(root.findall('.//PropertyGroup')):
                                print(f"    PropertyGroup {i+1}:")
                                for child in prop_group:
                                    print(f"      - {child.tag}: {child.text}")
                                    
                    except Exception as e:
                        print(f"  ❌ Ошибка при парсинге XML: {e}")
                else:
                    print(f"  ❌ Файл не существует: {full_project_file_path}")
        except Exception as e:
            print(f"  ❌ Ошибка при получении версии: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n❌ Version service не создан")

if __name__ == "__main__":
    asyncio.run(main())

