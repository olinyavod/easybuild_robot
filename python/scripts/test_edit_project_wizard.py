#!/usr/bin/env python3
"""
Тест для проверки мастера редактирования проектов.
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
            EditProjectWizard,
            SELECT_PROJECT,
            SELECT_FIELD,
            EDIT_VALUE,
            EDIT_PROJECT_CONFIRM
        )
        print("✅ Импорт EditProjectWizard - OK")
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
    print("\n🔍 Проверка создания мастера редактирования...")
    
    try:
        from easybuild_bot.handlers import EditProjectWizard
        from easybuild_bot.storage import Storage
        
        # Создаём storage с тестовой БД
        storage = Storage("/tmp/test_easybuild_edit.db")
        
        # Создаём мастер
        wizard = EditProjectWizard(storage)
        print("✅ Создание EditProjectWizard - OK")
        
        # Проверяем наличие методов
        methods = ['start', 'show_project_list', 'select_project', 'show_field_menu', 
                   'select_field', 'receive_value', 'save_changes', 'cancel']
        
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
            SELECT_PROJECT,
            SELECT_FIELD,
            EDIT_VALUE,
            EDIT_PROJECT_CONFIRM
        )
        
        states = {
            'SELECT_PROJECT': SELECT_PROJECT,
            'SELECT_FIELD': SELECT_FIELD,
            'EDIT_VALUE': EDIT_VALUE,
            'EDIT_PROJECT_CONFIRM': EDIT_PROJECT_CONFIRM
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


def test_format_functions():
    """Проверка вспомогательных функций"""
    print("\n🔍 Проверка вспомогательных функций...")
    
    try:
        from easybuild_bot.handlers.edit_project_wizard import escape_md, format_value
        from easybuild_bot.models import ProjectType
        
        # Тест escape_md
        result = escape_md("Test_string-with.special!")
        if "\\" in result:
            print("✅ Функция escape_md работает")
        else:
            print("❌ Функция escape_md не экранирует символы")
            return False
        
        # Тест format_value
        result = format_value("description", "Test description")
        if result == "Test description":
            print("✅ Функция format_value работает для строк")
        else:
            print(f"❌ Функция format_value вернула неожиданное значение: {result}")
            return False
        
        # Тест format_value для None
        result = format_value("description", None)
        if result == "_не задано_":
            print("✅ Функция format_value работает для None")
        else:
            print(f"❌ Функция format_value для None вернула: {result}")
            return False
        
        # Тест format_value для списка
        result = format_value("tags", ["tag1", "tag2"])
        if result == "tag1, tag2":
            print("✅ Функция format_value работает для списков")
        else:
            print(f"❌ Функция format_value для списка вернула: {result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки функций: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Главная функция теста"""
    print("=" * 60)
    print("🧪 Тест Edit Project Wizard")
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
    
    # Тест 4: Вспомогательные функции
    if not test_format_functions():
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



