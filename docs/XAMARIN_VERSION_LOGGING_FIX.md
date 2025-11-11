# Исправление определения версии для Xamarin проектов

## Дата: 11 ноября 2025

## Проблема

При попытке создать релиз для Xamarin проекта Fintech бот выдавал ошибку:

```
❌ Не удалось определить текущую версию проекта Fintech

Ветка релиза: master

Файл проекта: Fintech/Fintech.sln

Для проектов Xamarin версия ищется в платформенных файлах:
  • *.Android.csproj или *.Droid.csproj
  • *.iOS.csproj

Убедитесь, что в платформенных файлах есть теги версий:

Для Android:
  • <ApplicationVersion>X.Y.Z</ApplicationVersion>
  • <AndroidVersionCode>N</AndroidVersionCode>

Для iOS:
  • <ApplicationVersion>X.Y.Z</ApplicationVersion>
  • <CFBundleVersion>X.Y.Z</CFBundleVersion>
```

## Причина

Недостаточно подробное логирование в сервисе `XamarinVersionService` затрудняло диагностику проблемы. Не было понятно:
- Какие именно файлы проверяются
- Найдены ли платформенные файлы
- Есть ли в них теги версий
- На каком этапе происходит сбой

## Решение

### 1. Улучшено логирование в методе `_get_version_from_csproj`

Добавлено подробное логирование на каждом этапе:

```python
def _get_version_from_csproj(self, csproj_path: str) -> Optional[str]:
    # Логируем начало проверки
    logger.info(f"Читаем версию из файла: {csproj_path}")

    # Логируем тип платформы
    logger.info(f"Тип платформы для {filename}: {platform}")

    # Логируем каждую PropertyGroup
    logger.debug(f"Проверяем PropertyGroup #{prop_groups_count}")

    # Логируем найденные/ненайденные теги
    if app_version_elem is not None:
        logger.info(f"✓ Найдена версия в ApplicationVersion: {version}")
    else:
        logger.debug("  ApplicationVersion не найден в этой группе")

    # Логируем итоговый результат
    logger.warning(f"✗ Версия не найдена ни в одной из {prop_groups_count} PropertyGroup")
```

### 2. Улучшено логирование в методе `get_current_version`

Добавлена диагностическая информация:

```python
async def get_current_version(self, project: Project) -> Optional[str]:
    logger.info(f"=== Определение версии для проекта Xamarin: {project.name} ===")
    logger.info(f"Локальный путь репозитория: {project.local_repo_path}")

    # Проверка существования репозитория
    if not os.path.exists(project.local_repo_path):
        logger.error(f"Локальный репозиторий не существует: {project.local_repo_path}")
        return None

    # Диагностика при отсутствии платформенных файлов
    if not platform_projects:
        # Выводим список всех .csproj файлов
        all_csproj = [...]
        if all_csproj:
            logger.warning(f"  Найдены .csproj файлы (но не платформенные):")
            for csproj in all_csproj:
                logger.warning(f"    • {csproj}")
        else:
            logger.warning(f"  В директории вообще не найдено .csproj файлов")

    # Подробный лог проверенных файлов
    logger.warning(f"✗ Версия не найдена ни в одном из проверенных файлов:")
    for file, platform in checked_files:
        logger.warning(f"  • {file} (платформа: {platform or 'неизвестно'})")
```

### 3. Создан инструмент диагностики

Создан скрипт `scripts/check_xamarin_structure.py` для проверки структуры Xamarin проекта:

```bash
python3 scripts/check_xamarin_structure.py <путь_к_репозиторию>
```

Скрипт:
- Ищет все .csproj файлы
- Определяет платформенные файлы (Android/iOS)
- Проверяет наличие тегов версий
- Выводит подробный отчёт

## Использование

### Диагностика проблемы

1. Проверьте структуру проекта:
```bash
cd /home/olinyavod/projects/easybuild_bot/python
python3 scripts/check_xamarin_structure.py /home/olinyavod/projects/easybuild_bot/repos/fintech
```

2. Скрипт покажет:
   - Все найденные .csproj файлы
   - Какие из них платформенные (Android/iOS)
   - Наличие тегов версий в каждом файле

### Исправление проблемы

#### Вариант 1: Добавить теги версий в существующие файлы

Откройте платформенные файлы и добавьте теги версий:

**Для Android** (`*.Android.csproj`):
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <ApplicationVersion>1.0.0</ApplicationVersion>
    <AndroidVersionCode>10000</AndroidVersionCode>
  </PropertyGroup>
</Project>
```

**Для iOS** (`*.iOS.csproj`):
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <ApplicationVersion>1.0.0</ApplicationVersion>
    <CFBundleVersion>1.0.0</CFBundleVersion>
  </PropertyGroup>
</Project>
```

#### Вариант 2: Переименовать файлы

Если файлы проекта не названы правильно, переименуйте их:
- `Something.csproj` → `Something.Android.csproj` (для Android)
- `Something.csproj` → `Something.iOS.csproj` (для iOS)

## Что изменилось в коде

### Файлы:
- `python/src/easybuild_bot/version_services/xamarin_version_service.py` - улучшено логирование
- `python/scripts/check_xamarin_structure.py` - новый инструмент диагностики

### Изменения не влияют на:
- Логику определения версии (осталась прежней)
- Логику обновления версии (осталась прежней)
- Поиск платформенных файлов (осталась прежней)

Только добавлено подробное логирование для упрощения диагностики проблем.

## Проверка изменений

После изменений логи будут выглядеть так:

```
2025-11-11 12:00:00 - easybuild_bot.version_services.xamarin_version_service - INFO - === Определение версии для проекта Xamarin: Fintech ===
2025-11-11 12:00:00 - easybuild_bot.version_services.xamarin_version_service - INFO - Локальный путь репозитория: /home/.../repos/fintech
2025-11-11 12:00:00 - easybuild_bot.version_services.xamarin_version_service - INFO - ✓ Найдено 2 платформенных файлов:
2025-11-11 12:00:00 - easybuild_bot.version_services.xamarin_version_service - INFO -   • Fintech.Android/Fintech.Android.csproj
2025-11-11 12:00:00 - easybuild_bot.version_services.xamarin_version_service - INFO -   • Fintech.iOS/Fintech.iOS.csproj
2025-11-11 12:00:00 - easybuild_bot.version_services.xamarin_version_service - INFO - Читаем версию из файла: .../Fintech.Android.csproj
2025-11-11 12:00:00 - easybuild_bot.version_services.xamarin_version_service - INFO - Тип платформы для Fintech.Android.csproj: android
2025-11-11 12:00:00 - easybuild_bot.version_services.xamarin_version_service - WARNING - ✗ Версия не найдена ни в одной из 3 PropertyGroup в файле Fintech.Android.csproj
2025-11-11 12:00:00 - easybuild_bot.version_services.xamarin_version_service - WARNING -   Убедитесь, что в файле есть тег <ApplicationVersion>X.Y.Z</ApplicationVersion>
```

Это позволит точно определить, в чём проблема.
