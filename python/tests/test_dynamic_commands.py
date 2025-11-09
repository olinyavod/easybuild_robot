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
from easybuild_bot.commands.implementations.help_command import HelpCommand
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
        HelpCommand(storage, admin_token),
        BuildCommand(storage, admin_token),
        UsersCommand(storage, admin_token),
    ]

    for cmd in commands_to_register:
        registry.register(cmd)

    print(f"📋 Зарегистрировано команд: {len(commands_to_register)}\n")

    # Test cases
    test_cases = [
        # Unblock user commands - With "пользователя" (different cases)
        "Разблокировать пользователя Мирослава",  # genitive case
        "Разблокировать пользователю Мирослава",  # dative case
        "Дать доступ пользователя Иван",          # genitive case
        "Дать доступ пользователю Иван",          # dative case (NEW!)
        "Предоставить доступ пользователя Анна",  # genitive case
        "Предоставить доступ пользователю Анна",  # dative case (NEW!)
        "Активировать пользователя Петр",         # genitive case
        "Разблокировать пользователь Ольга",      # nominative case
        "Разблокировать пользователем Иван",      # instrumental case

        # Unblock user commands - With "юзера" (different cases)
        "Разблокировать юзера Мирослава",         # genitive case
        "Разблокировать юзеру Мирослава",         # dative case (NEW!)
        "Дать доступ юзер Иван",                  # nominative case
        "Дать доступ юзеру Иван",                 # dative case (NEW!)
        "Активировать юзера Ольга",               # genitive case

        # Unblock user commands - WITHOUT "пользователя" (name directly)
        "Разблокировать Анну",
        "Разблокировать Мирослава",
        "Активировать Иван",
        "Включить Петр",
        "Дать доступ Ольга",
        "Предоставить доступ Анна",

        # Block user commands - With "пользователя" (different cases)
        "Заблокировать пользователя Мирослава",   # genitive case
        "Заблокировать пользователю Сергей",      # dative case (NEW!)
        "Отключить пользователя Сергей",          # genitive case
        "Отключить пользователю Александр",       # dative case (NEW!)
        "Запретить доступ пользователя Александр",# genitive case
        "Запретить доступ пользователю Владимир", # dative case (NEW!)

        # Block user commands - With "юзера" (different cases)
        "Заблокировать юзера Дмитрий",            # genitive case
        "Заблокировать юзеру Дмитрий",            # dative case (NEW!)
        "Отключить юзер Елена",                   # nominative case
        "Отключить юзеру Елена",                  # dative case (NEW!)

        # Block user commands - WITHOUT "пользователя" (name directly)
        "Заблокировать Сергей",
        "Заблокировать Дмитрия",
        "Отключить Александр",
        "Деактивировать Елена",
        "Запретить доступ Владимир",

        # Edge cases
        "разблокировать мирослава",               # lowercase
        "разблокировать анну",                    # lowercase without "пользователя"
        "РАЗБЛОКИРОВАТЬ ВЛАДИМИР",                # uppercase without "пользователя"
        "предоставить доступ пользователю анна",  # dative case lowercase (NEW!)
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
