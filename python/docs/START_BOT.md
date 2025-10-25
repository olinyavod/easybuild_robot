# 🚀 Как запустить бот после рефакторинга

## Проблема
Бот остановлен и нуждается в перезапуске после обновления кода.

## Быстрое решение

### Вариант 1: Автоматический скрипт (рекомендуется)
```bash
cd /home/olinyavod/projects/easybuild_bot/python
chmod +x restart_bot.sh
./restart_bot.sh
```

### Вариант 2: Через systemctl
```bash
# Если сервис пользовательский
systemctl --user restart easybuild_bot_py

# Если сервис системный (требует sudo)
sudo systemctl restart easybuild_bot_py
```

### Вариант 3: Вручную
```bash
cd /home/olinyavod/projects/easybuild_bot/python

# Остановить старый процесс (если есть)
pkill -f "python.*main.py"

# Запустить бот
.venv/bin/python main.py > bot.log 2>&1 &

# Проверить, что запущен
ps aux | grep "[p]ython.*main.py"
```

## Проверка работы

### 1. Проверить статус сервиса
```bash
# Пользовательский сервис
systemctl --user status easybuild_bot_py

# Или системный
sudo systemctl status easybuild_bot_py
```

Должно быть: `Active: active (running)`

### 2. Проверить процесс
```bash
ps aux | grep "[p]ython.*main.py"
```

Вы должны увидеть запущенный процесс Python.

### 3. Проверить логи
```bash
cd /home/olinyavod/projects/easybuild_bot/python
tail -f bot.log
```

Должны появиться строки:
```
🚀 Starting EasyBuild Bot with Command Pattern Architecture
📋 Registered 16 commands:
  • /start
  • /help
  • /build
  ...
  • /add_project
  ...
```

### 4. Проверить в Telegram
Отправьте боту команду `/start` - бот должен ответить.

## Ожидаемый вывод при запуске

```
2025-10-25 12:30:00 - __main__ - INFO - Initializing Dependency Injection Container...
2025-10-25 12:30:00 - __main__ - INFO - Resolving dependencies from container...
2025-10-25 12:30:01 - __main__ - INFO - Creating bot instance with Command Pattern architecture...
2025-10-25 12:30:01 - __main__ - INFO - 📋 Registered 16 commands:
2025-10-25 12:30:01 - __main__ - INFO -   • /start
2025-10-25 12:30:01 - __main__ - INFO -   • /help
2025-10-25 12:30:01 - __main__ - INFO -   • /build
2025-10-25 12:30:01 - __main__ - INFO -   • /users
2025-10-25 12:30:01 - __main__ - INFO -   • /groups
2025-10-25 12:30:01 - __main__ - INFO -   • /register_group
2025-10-25 12:30:01 - __main__ - INFO -   • /unblock_user
2025-10-25 12:30:01 - __main__ - INFO -   • /block_user
2025-10-25 12:30:01 - __main__ - INFO -   • /projects
2025-10-25 12:30:01 - __main__ - INFO -   • /add_project
2025-10-25 12:30:01 - __main__ - INFO -   • /edit_project
2025-10-25 12:30:01 - __main__ - INFO -   • /delete_project
2025-10-25 12:30:01 - __main__ - INFO -   • callback:allow_user
2025-10-25 12:30:01 - __main__ - INFO -   • callback:block_user
2025-10-25 12:30:01 - __main__ - INFO -   • callback:unblock_user
2025-10-25 12:30:01 - __main__ - INFO -   • callback:build_apk
2025-10-25 12:30:01 - __main__ - INFO - Setting up bot handlers...
2025-10-25 12:30:01 - __main__ - INFO - ============================================================
2025-10-25 12:30:01 - __main__ - INFO - 🚀 Starting EasyBuild Bot with Command Pattern Architecture
2025-10-25 12:30:01 - __main__ - INFO - ============================================================
```

## Если бот не запускается

### Проверка 1: Виртуальное окружение
```bash
cd /home/olinyavod/projects/easybuild_bot/python
ls -la .venv/bin/python

# Если не существует, создать:
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### Проверка 2: Зависимости
```bash
cd /home/olinyavod/projects/easybuild_bot/python
.venv/bin/pip install -r requirements.txt
```

### Проверка 3: Переменные окружения
```bash
# Проверить наличие .env файла
ls -la .env

# Проверить содержимое (без вывода токенов)
cat .env | grep -v TOKEN
```

Должны быть установлены:
- `BOT_TOKEN` - токен Telegram бота
- `ADMIN_TOKEN` - токен администратора (опционально)
- `MONTYDB_DIR` - путь к базе данных (опционально)

### Проверка 4: Ошибки импорта
```bash
cd /home/olinyavod/projects/easybuild_bot/python
.venv/bin/python -c "
from src.easybuild_bot.di import Container
from src.easybuild_bot.bot import EasyBuildBot
print('✅ Все импорты работают')
"
```

## Полный перезапуск (если все остальное не помогло)

```bash
cd /home/olinyavod/projects/easybuild_bot/python

# 1. Остановить все
sudo systemctl stop easybuild_bot_py 2>/dev/null || true
pkill -f "python.*main.py"
sleep 2

# 2. Очистить кеш
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

# 3. Проверить код
.venv/bin/python -m py_compile main.py src/easybuild_bot/*.py

# 4. Запустить заново
sudo systemctl start easybuild_bot_py

# 5. Проверить статус
sleep 3
sudo systemctl status easybuild_bot_py
```

## Мониторинг в реальном времени

```bash
# В одном терминале - логи
tail -f /home/olinyavod/projects/easybuild_bot/python/bot.log

# В другом терминале - статус процесса
watch 'ps aux | grep "[p]ython.*main.py"'
```

## Автозапуск при загрузке системы

```bash
# Включить автозапуск
sudo systemctl enable easybuild_bot_py

# Проверить статус автозапуска
systemctl is-enabled easybuild_bot_py
```

Должно вывести: `enabled`

---

**После запуска бота попробуйте команду `/add_project` снова!**

