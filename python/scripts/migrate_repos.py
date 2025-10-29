#!/usr/bin/env python3
"""
Migrate existing projects to use repos/ directory.
"""

import os
import sys
import re

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.easybuild_bot.storage import Storage
from src.easybuild_bot.config import Settings

# Project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPOS_DIR = os.path.join(PROJECT_ROOT, "repos")


def clean_project_name(name: str) -> str:
    """Clean project name for use as directory name."""
    clean = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_').lower()
    return clean


def migrate_projects():
    """Migrate all projects to use repos/ directory."""
    print("🔄 Миграция проектов в папку repos/")
    print("=" * 60)
    
    # Load settings
    settings = Settings()
    
    # Initialize storage
    print(f"\n📦 Подключение к БД: {settings.montydb_dir}/{settings.montydb_name}")
    storage = Storage(dir_path=settings.montydb_dir, db_name=settings.montydb_name)
    
    # Get all projects
    projects = storage.get_all_projects()
    
    if not projects:
        print("\n⚠️  Проектов не найдено в базе данных")
        return
    
    print(f"\n✅ Найдено проектов: {len(projects)}")
    print()
    
    # Process each project
    updated_count = 0
    skipped_count = 0
    
    for project in projects:
        print(f"\n📦 Проект: {project.name}")
        print(f"   ID: {project.id}")
        print(f"   Текущий путь: {project.local_repo_path}")
        
        # Check if already in repos/ directory
        if project.local_repo_path.endswith(os.path.join("repos", clean_project_name(project.name))) or \
           "repos/" in project.local_repo_path or \
           "/repos/" in project.local_repo_path:
            print(f"   ✓ Уже в папке repos/, пропускаем")
            skipped_count += 1
            continue
        
        # Generate new path
        clean_name = clean_project_name(project.name)
        new_path = os.path.join(REPOS_DIR, clean_name)
        
        print(f"   → Новый путь: {new_path}")
        
        # Update in database
        try:
            # Access the database directly
            projects_collection = storage.db["projects"]
            result = projects_collection.update_one(
                {"id": project.id},
                {"$set": {"local_repo_path": new_path}}
            )
            
            if result.modified_count > 0:
                print(f"   ✅ Обновлено в БД")
                updated_count += 1
                
                # Check if old repository exists and move it
                if os.path.exists(project.local_repo_path):
                    print(f"   📁 Найден старый репозиторий")
                    
                    # Ask user if they want to move
                    response = input(f"   ❓ Переместить репозиторий в новое место? (y/n): ")
                    
                    if response.lower() == 'y':
                        # Create repos directory if it doesn't exist
                        os.makedirs(REPOS_DIR, exist_ok=True)
                        
                        # Move the repository
                        try:
                            import shutil
                            shutil.move(project.local_repo_path, new_path)
                            print(f"   ✅ Репозиторий перемещён")
                        except Exception as e:
                            print(f"   ❌ Ошибка перемещения: {e}")
                            print(f"   💡 Вы можете переместить вручную:")
                            print(f"      mv {project.local_repo_path} {new_path}")
                    else:
                        print(f"   ⏭️  Пропущено. При следующем выборе проекта репозиторий будет клонирован заново")
                else:
                    print(f"   ℹ️  Старый репозиторий не найден (будет клонирован заново)")
            else:
                print(f"   ⚠️  Не удалось обновить в БД")
                
        except Exception as e:
            print(f"   ❌ Ошибка обновления: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"\n📊 Результаты миграции:")
    print(f"   ✅ Обновлено: {updated_count}")
    print(f"   ⏭️  Пропущено: {skipped_count}")
    print(f"   📁 Всего проектов: {len(projects)}")
    
    if updated_count > 0:
        print(f"\n✨ Миграция завершена!")
        print(f"   Все новые проекты будут создаваться в: {REPOS_DIR}")
    else:
        print(f"\n✅ Все проекты уже используют правильные пути")


if __name__ == "__main__":
    try:
        migrate_projects()
    except KeyboardInterrupt:
        print("\n\n⚠️  Миграция прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

