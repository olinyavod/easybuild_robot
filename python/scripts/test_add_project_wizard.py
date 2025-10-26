#!/usr/bin/env python3
"""
Простой тест для проверки импортов и создания мастера.
"""

import sys
import os

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Проверка импортов"""
    print("🔍 Проверка импортов...")
    
    try:
        from easybuild_bot.handlers import (
            AddProjectWizard,
            WAITING_NAME,
            WAITING_TYPE,
            WAITING_GIT_URL,
            WAITING_PROJECT_FILE_PATH,
            WAITING_LOCAL_PATH,
            WAITING_DEV_BRANCH,
            WAITING_RELEASE_BRANCH,
            CONFIRM
        )
        print("✅ Импорт handlers - OK")
    except Exception as e:
        print(f"❌ Ошибка импорта handlers: {e}")
        return False
    
    try:
        from easybuild_bot.storage import Storage
        print("✅ Импорт Storage - OK")
    except Exception as e:
        print(f"❌ Ошибка импорта Storage: {e}")
        return False
    
    try:
        from easybuild_bot.models import Project, ProjectType
        print("✅ Импорт models - OK")
    except Exception as e:
        print(f"❌ Ошибка импорта models: {e}")
        return False
    
    return True


def test_wizard_creation():
    """Проверка создания мастера"""
    print("\n🔍 Проверка создания мастера...")
    
    try:
        from easybuild_bot.handlers import AddProjectWizard
        from easybuild_bot.storage import Storage
        
        # Создаём storage с тестовой БД
        storage = Storage("/tmp/test_easybuild.db")
        
        # Создаём мастер
        wizard = AddProjectWizard(storage)
        print("✅ Создание AddProjectWizard - OK")
        
        # Проверяем наличие методов
        methods = ['start', 'receive_name', 'receive_type', 'receive_git_url', 
                   'receive_project_file_path', 'receive_local_path', 
                   'receive_dev_branch', 'receive_release_branch', 
                   'confirm_creation', 'cancel']
        
        for method in methods:
            if hasattr(wizard, method):
                print(f"  ✅ Метод {method} - найден")
            else:
                print(f"  ❌ Метод {method} - НЕ найден")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания мастера: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_states():
    """Проверка состояний"""
    print("\n🔍 Проверка состояний...")
    
    try:
        from easybuild_bot.handlers import (
            WAITING_NAME,
            WAITING_TYPE,
            WAITING_GIT_URL,
            WAITING_PROJECT_FILE_PATH,
            WAITING_LOCAL_PATH,
            WAITING_DEV_BRANCH,
            WAITING_RELEASE_BRANCH,
            CONFIRM
        )
        
        states = {
            'WAITING_NAME': WAITING_NAME,
            'WAITING_TYPE': WAITING_TYPE,
            'WAITING_GIT_URL': WAITING_GIT_URL,
            'WAITING_PROJECT_FILE_PATH': WAITING_PROJECT_FILE_PATH,
            'WAITING_LOCAL_PATH': WAITING_LOCAL_PATH,
            'WAITING_DEV_BRANCH': WAITING_DEV_BRANCH,
            'WAITING_RELEASE_BRANCH': WAITING_RELEASE_BRANCH,
            'CONFIRM': CONFIRM
        }
        
        # Проверяем, что все состояния уникальны
        values = list(states.values())
        if len(values) == len(set(values)):
            print("✅ Все состояния уникальны")
        else:
            print("❌ Есть дубликаты состояний!")
            return False
        
        # Выводим значения
        print("\nЗначения состояний:")
        for name, value in states.items():
            print(f"  {name} = {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки состояний: {e}")
        return False


def main():
    """Главная функция теста"""
    print("=" * 60)
    print("🧪 Тест Add Project Wizard")
    print("=" * 60)
    
    all_ok = True
    
    # Тест 1: Импорты
    if not test_imports():
        all_ok = False
    
    # Тест 2: Создание мастера
    if not test_wizard_creation():
        all_ok = False
    
    # Тест 3: Состояния
    if not test_states():
        all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
        print("=" * 60)
        return 0
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

