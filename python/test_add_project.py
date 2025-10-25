#!/usr/bin/env python3
"""
Скрипт для тестирования команды AddProjectCommand после рефакторинга.
"""

import sys
import os

# Добавить путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Проверка импортов
print("🔍 Проверка импортов...")
try:
    from easybuild_bot.commands.base import Command
    print("✅ Command импортирован")
    
    from easybuild_bot.commands.implementations.add_project_command import AddProjectCommand
    print("✅ AddProjectCommand импортирован")
    
    from easybuild_bot.access_control import AccessControlService
    print("✅ AccessControlService импортирован")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

print("\n📋 Проверка сигнатуры конструктора Command...")
import inspect

# Проверить сигнатуру базового класса
sig = inspect.signature(Command.__init__)
print(f"Command.__init__ параметры: {list(sig.parameters.keys())}")

expected_params = ['self', 'storage', 'access_control']
actual_params = list(sig.parameters.keys())

if actual_params == expected_params:
    print("✅ Сигнатура конструктора Command правильная")
else:
    print(f"❌ Ожидалось: {expected_params}")
    print(f"   Получено: {actual_params}")
    sys.exit(1)

print("\n📋 Проверка AddProjectCommand...")
# AddProjectCommand не переопределяет __init__, поэтому использует базовый
if not hasattr(AddProjectCommand, '__init__') or AddProjectCommand.__init__ is Command.__init__:
    print("✅ AddProjectCommand использует базовый конструктор")
else:
    print("⚠️  AddProjectCommand переопределяет __init__")
    sig = inspect.signature(AddProjectCommand.__init__)
    print(f"   Параметры: {list(sig.parameters.keys())}")

print("\n✅ Все проверки пройдены!")
print("\n💡 Если вы получили ошибку при добавлении проекта:")
print("   1. Перезапустите бот (если он запущен)")
print("   2. Проверьте логи: tail -f bot.log")
print("   3. Убедитесь, что используете правильный формат команды:")
print("      /add_project <название> <тип> <git_url> <путь_к_файлу> <локальный_путь>")

