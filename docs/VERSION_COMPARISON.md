# Объяснение различий в обработке версий между проектами

## Дата: 30 октября 2025

## Почему checklist_app работал, а TechnouprApp.Client - нет?

### Анализ версий в проектах

#### ChecklistApp (Flutter) - ✅ Работал
```yaml
# Файл: pubspec.yaml
version: 1.0.4
```
- **Формат**: 3 части (X.Y.Z)
- **Результат**: Успешно определяется и инкрементируется

#### TechnouprApp.Client (MAUI) - ❌ Не работал
```xml
<!-- Файл: TechnouprApp.Client.csproj -->
<ApplicationDisplayVersion>1.0</ApplicationDisplayVersion>
```
- **Формат**: 2 части (X.Y)
- **Результат**: Ошибка "Не удалось определить текущую версию проекта" (до исправления)

## Почему бот "удалял" сообщение об ошибке?

Ваше наблюдение было правильным! В коде `project_select_callback.py` есть специальная логика:

```python
async def send_message(msg: str):
    nonlocal final_message_sent
    # Only send the final success/error message
    if not final_message_sent:
        await ctx.update.effective_message.reply_text(msg, parse_mode='Markdown')
        final_message_sent = True
```

Это означает:
1. **Отправляется только ПЕРВОЕ сообщение**
2. Все последующие сообщения игнорируются
3. Если первое сообщение - ошибка, она показывается
4. Если процесс продолжается и появляется успешное сообщение - оно тоже показывается (но не заменяет ошибку)

**Но для checklist_app никакой ошибки не было!** Версия `1.0.4` имеет правильный формат, поэтому бот сразу перешёл к успешному выполнению.

## Что было исправлено

### До исправления

```python
# base.py - метод increment_version
parts = base_version.split('.')
if len(parts) != 3:
    # Invalid version format, just return with .1 added
    return f"{version}.1"
```

Версия `1.0` → `1.0.1` (но fallback логика не всегда работала корректно)

### После исправления

```python
# base.py - метод increment_version
parts = base_version.split('.')

# Handle different version formats
if len(parts) == 2:
    # Version like "1.0" - treat as "1.0.0"
    parts.append('0')
elif len(parts) != 3:
    # Invalid version format, just return with .1 added
    return f"{version}.1"
```

Версия `1.0` → интерпретируется как `1.0.0` → инкрементируется до `1.0.1`

## Рекомендации

### Для MAUI/Xamarin проектов

Используйте полный формат версии в `.csproj`:

```xml
<!-- Рекомендуется -->
<ApplicationDisplayVersion>1.0.0</ApplicationDisplayVersion>
<ApplicationVersion>1</ApplicationVersion>

<!-- Также работает (после исправления) -->
<ApplicationDisplayVersion>1.0</ApplicationDisplayVersion>
<ApplicationVersion>1</ApplicationVersion>
```

### Для Flutter проектов

Используйте формат `major.minor.patch+build` в `pubspec.yaml`:

```yaml
# Рекомендуется
version: 1.0.0+1

# Минимальный формат (после исправления)
version: 1.0
```

## Итог

**До исправления:**
- ✅ `checklist_app` работал, потому что версия была `1.0.4` (3 части)
- ❌ `TechnouprApp.Client` не работал, потому что версия была `1.0` (2 части)

**После исправления:**
- ✅ Оба проекта работают корректно
- ✅ Поддерживаются версии формата `X.Y` и `X.Y.Z`
- ✅ Добавлено подробное логирование для диагностики
- ✅ Улучшены сообщения об ошибках

## Проверка текущего состояния

Чтобы убедиться, что оба проекта работают:

```bash
# Проверить версию checklist_app
cd /home/olinyavod/projects/easybuild_bot/repos/checklist_app
grep "^version:" pubspec.yaml
# Результат: version: 1.0.4

# Проверить версию TechnouprApp.Client
cd /home/olinyavod/projects/easybuild_bot/repos/TechnouprApp.Client
grep -A1 "ApplicationDisplayVersion" TechnouprApp.Client/TechnouprApp.Client.csproj
# Результат: <ApplicationDisplayVersion>1.0</ApplicationDisplayVersion>
```

Оба формата теперь поддерживаются ботом!




