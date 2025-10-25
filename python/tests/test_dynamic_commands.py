#!/usr/bin/env python3
"""
Test script for dynamic command parameter extraction.
Проверка извлечения параметров из команд.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from easybuild_bot.commands.registry import CommandRegistry
from easybuild_bot.commands.implementations.unblock_user_command import UnblockUserCommand
from easybuild_bot.commands.implementations.block_user_command import BlockUserCommand
from easybuild_bot.commands.implementations.start_command import StartCommand
from easybuild_bot.commands.implementations.build_command import BuildCommand
from easybuild_bot.commands.implementations.users_command import UsersCommand
from easybuild_bot.storage import Storage


def test_dynamic_commands():
    """Test dynamic command recognition with parameter extraction."""
    print("🧪 Тестирование динамических команд с извлечением параметров\n")
    
    # Initialize storage (mock)
    storage = Storage(dir_path="/tmp/test_monty", db_name="test_db")
    admin_token = "test_token"
    
    # Initialize registry
    registry = CommandRegistry(model_name="cointegrated/rubert-tiny", threshold=0.5)
    
    # Register commands
    commands_to_register = [
        UnblockUserCommand(storage, admin_token),
        BlockUserCommand(storage, admin_token),
        StartCommand(storage, admin_token),
        BuildCommand(storage, admin_token),
        UsersCommand(storage, admin_token),
    ]
    
    for cmd in commands_to_register:
        registry.register(cmd)
    
    print(f"📋 Зарегистрировано команд: {len(commands_to_register)}\n")
    
    # Test cases
    test_cases = [
        # Unblock user commands - С "пользователя" (разные падежи)
        "Разблокировать пользователя Мирослава",  # родительный падеж
        "Разблокировать пользователю Мирослава",  # дательный падеж
        "Дать доступ пользователя Иван",          # родительный падеж
        "Дать доступ пользователю Иван",          # дательный падеж (НОВОЕ!)
        "Предоставить доступ пользователя Анна",  # родительный падеж
        "Предоставить доступ пользователю Анна",  # дательный падеж (НОВОЕ!)
        "Активировать пользователя Петр",         # родительный падеж
        "Разблокировать пользователь Ольга",      # именительный падеж
        "Разблокировать пользователем Иван",      # творительный падеж
        
        # Unblock user commands - С "юзера" (разные падежи)
        "Разблокировать юзера Мирослава",         # родительный падеж
        "Разблокировать юзеру Мирослава",         # дательный падеж (НОВОЕ!)
        "Дать доступ юзер Иван",                  # именительный падеж
        "Дать доступ юзеру Иван",                 # дательный падеж (НОВОЕ!)
        "Активировать юзера Ольга",               # родительный падеж
        
        # Unblock user commands - БЕЗ "пользователя" (прямо имя)
        "Разблокировать Анну",
        "Разблокировать Мирослава",
        "Активировать Иван",
        "Включить Петр",
        "Дать доступ Ольга",
        "Предоставить доступ Анна",
        
        # Block user commands - С "пользователя" (разные падежи)
        "Заблокировать пользователя Мирослава",   # родительный падеж
        "Заблокировать пользователю Сергей",      # дательный падеж (НОВОЕ!)
        "Отключить пользователя Сергей",          # родительный падеж
        "Отключить пользователю Александр",       # дательный падеж (НОВОЕ!)
        "Запретить доступ пользователя Александр",# родительный падеж
        "Запретить доступ пользователю Владимир", # дательный падеж (НОВОЕ!)
        
        # Block user commands - С "юзера" (разные падежи)
        "Заблокировать юзера Дмитрий",            # родительный падеж
        "Заблокировать юзеру Дмитрий",            # дательный падеж (НОВОЕ!)
        "Отключить юзер Елена",                   # именительный падеж
        "Отключить юзеру Елена",                  # дательный падеж (НОВОЕ!)
        
        # Block user commands - БЕЗ "пользователя" (прямо имя)
        "Заблокировать Сергей",
        "Заблокировать Дмитрия",
        "Отключить Александр",
        "Деактивировать Елена",
        "Запретить доступ Владимир",
        
        # Edge cases
        "разблокировать мирослава",               # lowercase
        "разблокировать анну",                    # lowercase без "пользователя"
        "РАЗБЛОКИРОВАТЬ ВЛАДИМИР",                # uppercase без "пользователя"
        "предоставить доступ пользователю анна",  # дательный падеж lowercase (НОВОЕ!)
        "Разблокировать",                         # no name
        
        # Existing commands (should still work)
        "Привет",
        "покажи сборки",
        "список пользователей",
    ]
    
    for text in test_cases:
        print(f"📝 Тест: \"{text}\"")
        result = registry.match_command(text)
        
        if result:
            command, similarity, params = result
            print(f"  ✅ Команда: {command.get_command_name()}")
            print(f"  📊 Схожесть: {similarity:.3f}")
            if params:
                print(f"  📋 Параметры: {params}")
            else:
                print(f"  📋 Параметры: нет")
        else:
            print(f"  ❌ Команда не распознана")
        print()

if __name__ == "__main__":
    test_dynamic_commands()

