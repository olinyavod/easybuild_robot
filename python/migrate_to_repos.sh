#!/bin/bash
# Скрипт быстрой миграции репозиториев в поддиректорию repos/

echo "🔄 Миграция репозиториев в поддиректорию repos/"
echo "=============================================="
echo ""

# Переходим в директорию проекта
cd "$(dirname "$0")"

# Проверяем, активировано ли виртуальное окружение
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Виртуальное окружение не активировано!"
    echo "📦 Активируем .venv..."
    
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo "✅ Виртуальное окружение активировано"
    else
        echo "❌ Не найдено виртуальное окружение в .venv/"
        echo "💡 Создайте его командой: python3 -m venv .venv"
        exit 1
    fi
fi

# Проверяем установку montydb
echo ""
echo "🔍 Проверка зависимостей..."
python3 -c "import montydb" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Модуль montydb не установлен"
    echo "📦 Устанавливаем зависимости..."
    pip install montydb
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка установки зависимостей"
        exit 1
    fi
    echo "✅ Зависимости установлены"
fi

# Создаём директорию repos, если её нет
echo ""
echo "📁 Создание директории repos..."
mkdir -p ../repos

# Запускаем скрипт миграции Python
echo ""
echo "🔧 Запуск миграции базы данных..."
python3 scripts/migrate_repos.py

echo ""
echo "✅ Миграция завершена!"
echo ""
echo "💡 Если у вас есть старые репозитории в /python/, их можно удалить:"
echo "   ls -la | grep -E '(checklist_app|TechnouprApp)'"
echo ""


