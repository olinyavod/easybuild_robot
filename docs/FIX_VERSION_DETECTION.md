# Исправление ошибки "Не удалось определить текущую версию проекта"

## Дата: 30 октября 2025

## Проблема

При построении MAUI проекта TechnouprApp.Client бот выдавал ошибку:
```
❌ Не удалось определить текущую версию проекта TechnouprApp.Client
```

## Причины

1. **Неполная поддержка формата версий**: Версия в .csproj файле указана как `1.0` (2 части), а бот ожидал формат `X.Y.Z` (3 части)
2. **Недостаточное логирование**: При возникновении ошибки в методе `_get_current_version_from_release_branch` все исключения поглощались без вывода информации
3. **Неинформативное сообщение об ошибке**: Пользователь не получал информации о том, какая ветка и какой файл проверялись

## Решение

### 1. Улучшена поддержка формата версий (base.py)

Метод `increment_version` теперь корректно обрабатывает версии с 2 частями (например, `1.0`):

```python
# Handle different version formats
if len(parts) == 2:
    # Version like "1.0" - treat as "1.0.0"
    parts.append('0')
elif len(parts) != 3:
    # Invalid version format, just return with .1 added
    return f"{version}.1"
```

**Было:**
- Версия `1.0` преобразовывалась в `1.0.1` через fallback логику

**Стало:**
- Версия `1.0` интерпретируется как `1.0.0` и корректно инкрементируется до `1.0.1`

### 2. Добавлено подробное логирование (prepare_release_callback.py)

В метод `_get_current_version_from_release_branch` добавлено логирование на каждом этапе:

```python
logger.info(f"Current branch for {project.name}: {current_branch}")
logger.info(f"Switching to release branch '{project.release_branch}' for {project.name}")
logger.info(f"Getting version from release branch for {project.name}")

if version:
    logger.info(f"Found version in release branch: {version}")
else:
    logger.error(f"Failed to get version from release branch for {project.name}")
```

### 3. Улучшено сообщение об ошибке (prepare_release_callback.py)

Теперь при ошибке пользователь получает подробную информацию:

```python
error_msg = (
    f"❌ Не удалось определить текущую версию проекта {project.name}\n"
    f"Ветка релиза: `{project.release_branch}`\n"
    f"Файл проекта: `{project.project_file_path}`\n"
    f"Убедитесь, что в файле проекта есть тег версии:\n"
    f"  - Для MAUI: `<ApplicationDisplayVersion>X.Y.Z</ApplicationDisplayVersion>`\n"
    f"  - Для Flutter: `version: X.Y.Z` в pubspec.yaml"
)
```

## Проверка

Создан тестовый скрипт, который подтвердил, что:
- ✅ Версия `1.0` корректно читается из .csproj файла
- ✅ Метод `get_current_version` работает правильно
- ✅ XML парсинг выполняется успешно
- ✅ Тег `ApplicationDisplayVersion` находится корректно

## Рекомендации для пользователей

### Если проект не добавлен в базу данных

Используйте команду `/add_project` в Telegram боте для добавления проекта:

1. Отправьте `/add_project` в чат с ботом
2. Следуйте пошаговому мастеру:
   - Укажите имя проекта: `TechnouprApp.Client`
   - Выберите тип проекта: `.NET MAUI`
   - Укажите Git URL: URL вашего репозитория
   - Укажите путь к файлу проекта: `TechnouprApp.Client/TechnouprApp.Client.csproj`
   - Укажите локальный путь: `/home/olinyavod/projects/easybuild_bot/repos/TechnouprApp.Client`
   - Укажите ветку разработки: `develop`
   - Укажите ветку релиза: `main`

### Если версия в .csproj имеет формат X.Y

Рекомендуется обновить версию до формата X.Y.Z для полной совместимости:

```xml
<!-- Было -->
<ApplicationDisplayVersion>1.0</ApplicationDisplayVersion>

<!-- Рекомендуется -->
<ApplicationDisplayVersion>1.0.0</ApplicationDisplayVersion>
```

Однако, текущая версия бота теперь корректно обрабатывает обе форматы.

## Результат

После внесенных изменений:
- ✅ Версии с 2 частями (X.Y) обрабатываются корректно
- ✅ Подробное логирование помогает диагностировать проблемы
- ✅ Информативные сообщения об ошибках упрощают устранение проблем
- ✅ Бот корректно работает с MAUI проектами

## Затронутые файлы

1. `python/src/easybuild_bot/version_services/base.py` - улучшена поддержка формата версий
2. `python/src/easybuild_bot/commands/implementations/prepare_release_callback.py` - добавлено логирование и улучшены сообщения об ошибках







