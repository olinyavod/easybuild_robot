#!/bin/bash
# Скрипт для установки зависимостей

echo "Установка зависимостей для EasyBuild Bot..."
echo ""

cd "$(dirname "$0")"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8 или выше."
    exit 1
fi

echo "✓ Python найден: $(python3 --version)"
echo ""

# Установка зависимостей
echo "Установка Python пакетов..."
pip3 install -r requirements.txt

echo ""
echo "✅ Установка завершена!"
echo ""
echo "Для запуска бота:"
echo "  1. Создайте файл .env с вашим BOT_TOKEN"
echo "  2. Запустите: python3 main.py"
echo ""
echo "Для тестирования команд:"
echo "  python3 tests/test_dynamic_commands.py"


