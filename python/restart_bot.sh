#!/bin/bash
# Скрипт для запуска/перезапуска бота EasyBuild

cd /home/olinyavod/projects/easybuild_bot/python

echo "🔄 Перезапуск бота EasyBuild..."
echo ""

# Проверка статуса
echo "📊 Текущий статус:"
systemctl --user status easybuild_bot_py 2>/dev/null || sudo systemctl status easybuild_bot_py | head -10

echo ""
echo "🔄 Перезапуск сервиса..."

# Попытка перезапуска без sudo (пользовательский сервис)
systemctl --user restart easybuild_bot_py 2>/dev/null && echo "✅ Бот перезапущен (пользовательский сервис)" && exit 0

# Если не получилось, пробуем через sudo
sudo systemctl restart easybuild_bot_py && echo "✅ Бот перезапущен (системный сервис)" || {
    echo "❌ Не удалось перезапустить через systemctl"
    echo ""
    echo "📝 Попытка запуска вручную..."
    
    # Остановить старые процессы
    pkill -f "python.*main.py" 2>/dev/null
    sleep 2
    
    # Запустить в фоне
    nohup .venv/bin/python main.py > bot.log 2>&1 &
    
    echo "✅ Бот запущен вручную (PID: $!)"
    echo "📋 Логи: tail -f bot.log"
}

echo ""
sleep 2
echo "📊 Новый статус:"
systemctl --user status easybuild_bot_py 2>/dev/null || sudo systemctl status easybuild_bot_py | head -10

