#!/bin/bash
# Полная перезагрузка бота

cd /home/olinyavod/projects/easybuild_bot/python

echo "🛑 Остановка бота..."
pkill -9 -f "python.*main.py" 2>/dev/null || true
sleep 2

echo "🧹 Очистка кеша Python..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Проверка кода..."
.venv/bin/python -m py_compile src/easybuild_bot/commands/implementations/add_project_command.py || {
    echo "❌ Ошибка компиляции!"
    exit 1
}

echo "🚀 Запуск бота..."
nohup .venv/bin/python main.py > bot.log 2>&1 &
BOT_PID=$!

echo "✅ Бот запущен (PID: $BOT_PID)"
echo "📋 Ожидание инициализации..."
sleep 5

echo ""
echo "📊 Последние логи:"
tail -20 bot.log

echo ""
echo "✅ Готово! Проверьте бот в Telegram"

