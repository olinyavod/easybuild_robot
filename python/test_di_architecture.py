#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новой архитектуры DI.

Этот скрипт проверяет базовую структуру без запуска бота.
"""
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_config():
    """Тест класса Settings."""
    print("=" * 60)
    print("Тест 1: Класс Settings")
    print("=" * 60)
    
    try:
        from easybuild_bot.config import Settings
        
        # Создаём минимальные настройки для теста
        settings = Settings(bot_token="test_token_123")
        
        print("✅ Settings успешно создан")
        print("\nНастройки:")
        for key, value in settings.to_dict().items():
            print(f"  • {key}: {value}")
        
        print("\n✅ to_dict() работает")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_di_structure():
    """Тест структуры DI контейнера."""
    print("\n" + "=" * 60)
    print("Тест 2: Структура DI контейнера")
    print("=" * 60)
    
    try:
        import easybuild_bot.di as di_module
        
        # Проверяем наличие фабричных функций
        assert hasattr(di_module, 'create_speech_service'), "create_speech_service отсутствует"
        assert hasattr(di_module, 'create_tts_service'), "create_tts_service отсутствует"
        assert hasattr(di_module, 'Container'), "Container отсутствует"
        
        print("✅ Все компоненты DI контейнера присутствуют:")
        print("  • create_speech_service")
        print("  • create_tts_service")
        print("  • Container")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_structure():
    """Тест структуры main.py."""
    print("\n" + "=" * 60)
    print("Тест 3: Структура main.py")
    print("=" * 60)
    
    try:
        # Читаем main.py
        main_path = Path(__file__).parent / "main.py"
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Проверяем наличие ключевых элементов
        checks = [
            ("Settings", "from src.easybuild_bot.config import Settings" in content or "container.settings()" in content),
            ("Container", "from src.easybuild_bot.di import Container" in content),
            ("Автоматический DI", "container.bot()" in content),
            ("load_dotenv", "load_dotenv()" in content),
        ]
        
        all_ok = True
        for name, check in checks:
            status = "✅" if check else "❌"
            print(f"  {status} {name}")
            all_ok = all_ok and check
        
        if all_ok:
            print("\n✅ main.py использует новую архитектуру")
        else:
            print("\n⚠️ main.py требует доработки")
        
        # Подсчитываем строки кода (без пустых и комментариев)
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
        print(f"\n📊 Статистика main.py:")
        print(f"  • Строк кода: {len(lines)}")
        
        return all_ok
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_env_example():
    """Тест наличия .env.example."""
    print("\n" + "=" * 60)
    print("Тест 4: Файл .env.example")
    print("=" * 60)
    
    try:
        env_path = Path(__file__).parent / ".env.example"
        
        if not env_path.exists():
            print("❌ .env.example не найден")
            return False
        
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Проверяем наличие ключевых параметров
        required_params = [
            "BOT_TOKEN",
            "ADMIN_TOKEN",
            "WHISPER_MODEL",
            "TTS_SPEAKER",
            "COMMAND_MATCHER_MODEL",
        ]
        
        all_ok = True
        for param in required_params:
            present = param in content
            status = "✅" if present else "❌"
            print(f"  {status} {param}")
            all_ok = all_ok and present
        
        if all_ok:
            print("\n✅ .env.example содержит все необходимые параметры")
        
        return all_ok
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Запуск всех тестов."""
    print("\n" + "🚀" * 30)
    print("ТЕСТИРОВАНИЕ НОВОЙ АРХИТЕКТУРЫ DI")
    print("🚀" * 30 + "\n")
    
    results = []
    
    # Запускаем тесты
    results.append(("Settings", test_config()))
    results.append(("DI Container", test_di_structure()))
    results.append(("main.py", test_main_structure()))
    results.append((".env.example", test_env_example()))
    
    # Итоговый отчёт
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЁТ")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r for _, r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("\nНовая архитектура готова к использованию:")
        print("  1. Создайте .env файл: cp .env.example .env")
        print("  2. Заполните BOT_TOKEN в .env")
        print("  3. Запустите: python main.py")
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("Проверьте вывод выше для деталей")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

