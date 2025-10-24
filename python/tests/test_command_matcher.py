#!/usr/bin/env python3
"""
Test script for checking semantic command recognition.
"""
import sys
import os

# Add path to module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from easybuild_bot.command_matcher import CommandMatcher


def test_command_matching():
    """Tests various variants of user messages."""
    
    print("Initializing CommandMatcher...")
    matcher = CommandMatcher(threshold=0.5)
    print()
    
    # Test phrases
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
        "как дела",  # Should not match
        "погода",     # Should not match
    ]
    
    print("Testing command recognition:")
    print("=" * 80)
    
    for phrase in test_phrases:
        result = matcher.match_command(phrase)
        if result:
            command, similarity = result
            print(f"✓ '{phrase}' -> {command} (similarity: {similarity:.3f})")
        else:
            print(f"✗ '{phrase}' -> Not recognized")
    
    print("=" * 80)
    print("\nTesting completed!")


if __name__ == "__main__":
    test_command_matching()

