#!/usr/bin/env python3
"""
Script to check project database content.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from easybuild_bot.storage import Storage

def main():
    """Check project database content."""
    storage = Storage()
    
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
    if os.path.exists(full_project_file_path):
        print(f"  ✅ Файл проекта существует: {full_project_file_path}")
    else:
        print(f"  ❌ Файл проекта не найден: {full_project_file_path}")
        print(f"\n🔍 Содержимое директории {project.local_repo_path}:")
        if os.path.exists(project.local_repo_path):
            for item in os.listdir(project.local_repo_path):
                print(f"      - {item}")

if __name__ == "__main__":
    main()

