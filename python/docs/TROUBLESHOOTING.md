# Решение проблемы с добавлением проекта

## Проблема
При попытке добавить проект через команду `/add_project` возникла ошибка.

## Причина
После рефакторинга изменилась внутренняя архитектура бота. Если бот был запущен до рефакторинга и не был перезапущен, он использует старый код.

## Решение

### 1. Перезапустите бот

```bash
cd /home/olinyavod/projects/easybuild_bot/python

# Если бот запущен как сервис
sudo systemctl restart easybuild_bot_py

# Или если запущен вручную
# Остановите старый процесс (Ctrl+C или kill)
# Затем запустите снова:
python3 main.py
```

### 2. Проверьте логи

```bash
# Просмотр логов в реальном времени
tail -f bot.log

# Или последние 50 строк
tail -50 bot.log
```

### 3. Используйте правильный формат команды

```
/add_project <название> <тип> <git_url> <путь_к_файлу_проекта> <локальный_путь> [ветка_dev] [ветка_release]
```

**Типы проектов:**
- `flutter` - Flutter проект
- `dotnet_maui` (или `maui`) - .NET MAUI проект
- `xamarin` - Xamarin проект

**Пример:**
```
/add_project MyApp flutter https://github.com/user/myapp.git android/app /home/repos/myapp develop main
```

## Проверка работоспособности

### Тест 1: Проверьте, что бот запущен
```bash
ps aux | grep "python.*main.py"
```

Если процесс не найден - бот не запущен.

### Тест 2: Проверьте, что команды зарегистрированы
При запуске бот должен показать список зарегистрированных команд:
```
📋 Registered 16 commands:
  • /start
  • /help
  • /build
  • /users
  • /groups
  • /register_group
  • /unblock_user
  • /block_user
  • /projects
  • /add_project      ← Эта команда должна быть в списке
  • /edit_project
  • /delete_project
  • callback:allow_user
  • callback:block_user
  • callback:unblock_user
  • callback:build_apk
```

### Тест 3: Проверьте права доступа
Команда `/add_project` требует прав администратора. Убедитесь, что у вас есть права админа:

1. Отправьте боту команду `/admin`
2. Введите токен администратора
3. Попробуйте `/add_project` снова

## Диагностика ошибок

### Ошибка: "Недостаточно параметров"
**Решение:** Проверьте формат команды. Нужно минимум 5 параметров.

### Ошибка: "Неизвестный тип проекта"
**Решение:** Используйте один из допустимых типов: `flutter`, `dotnet_maui`, `maui`, `xamarin`

### Ошибка: "Проект уже существует"
**Решение:** Проект с таким именем уже есть в базе. Используйте другое имя или удалите существующий проект командой `/delete_project <название>`

### Ошибка: "У вас нет прав администратора"
**Решение:** Получите права администратора через команду `/admin`

## Если проблема не решена

1. **Остановите бот полностью:**
```bash
# Если это сервис
sudo systemctl stop easybuild_bot_py

# Или найдите и остановите процесс
pkill -f "python.*main.py"
```

2. **Проверьте, что нет запущенных экземпляров:**
```bash
ps aux | grep "python.*main.py"
```

3. **Очистите кеш Python:**
```bash
cd /home/olinyavod/projects/easybuild_bot/python
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
```

4. **Запустите бот заново:**
```bash
python3 main.py
```

5. **Отправьте полный текст ошибки:**
Если ошибка повторяется, скопируйте:
- Сообщение об ошибке из Telegram
- Содержимое лога: `tail -100 bot.log`
- Команду, которую вы использовали

## Проверка кода (для разработчиков)

Если нужно убедиться, что код корректен:

```bash
# Проверка синтаксиса всех измененных файлов
cd /home/olinyavod/projects/easybuild_bot/python
python3 -m py_compile \
  src/easybuild_bot/access_control.py \
  src/easybuild_bot/commands/base.py \
  src/easybuild_bot/commands/callback_base.py \
  src/easybuild_bot/commands/factory.py \
  src/easybuild_bot/commands/implementations/add_project_command.py \
  src/easybuild_bot/di.py \
  src/easybuild_bot/bot.py \
  main.py

echo "✅ Все файлы проверены"
```

## Изменения после рефакторинга

После рефакторинга были внесены следующие изменения:

1. ✅ Создан `AccessControlService` для централизованной проверки прав
2. ✅ Все команды обновлены для использования нового сервиса
3. ✅ Callback-обработчики вынесены в отдельные команды
4. ✅ Устранено дублирование кода

**Важно:** После обновления кода нужно обязательно перезапустить бот!

## Контактная информация

Если проблема не решается:
1. Проверьте документацию: `docs/REFACTORING_SUMMARY.md`
2. Посмотрите архитектуру: `docs/ARCHITECTURE.md`
3. Создайте issue с описанием проблемы и логами

