#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы семантического распознавания команд.
"""
import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from easybuild_bot.command_matcher import CommandMatcher


def test_command_matching():
    """Тестирует различные варианты пользовательских сообщений."""
    
    print("Инициализация CommandMatcher...")
    matcher = CommandMatcher(threshold=0.5)
    print()
    
    # Тестовые фразы
    test_phrases = [
        "привет",
        "начать работу",
        "старт",
        "помощь",
        "помоги мне",
        "что ты умеешь",
        "покажи сборки",
        "сборка",
        "собрать apk",
        "зарегистрировать группу",
        "добавить группу",
        "пользователи",
        "список пользователей",
        "группы",
        "показать группы",
        "как дела",  # Не должно совпасть
        "погода",     # Не должно совпасть
    ]
    
    print("Тестирование распознавания команд:")
    print("=" * 80)
    
    for phrase in test_phrases:
        result = matcher.match_command(phrase)
        if result:
            command, similarity = result
            print(f"✓ '{phrase}' -> {command} (схожесть: {similarity:.3f})")
        else:
            print(f"✗ '{phrase}' -> Не распознано")
    
    print("=" * 80)
    print("\nТестирование завершено!")


if __name__ == "__main__":
    test_command_matching()

