# Исправление определения версии для проектов Xamarin

## Дата: 9 ноября 2025

## Проблема

При сборке проекта типа Xamarin бот выдавал ошибку:
```
❌ Не удалось определить текущую версию проекта Fintech

Ветка релиза: master

Файл проекта: Fintech/Fintech.sln

Убедитесь, что в файле проекта есть тег версии:
  - Для MAUI: <ApplicationDisplayVersion>X.Y.Z</ApplicationDisplayVersion>
  - Для Flutter: version: X.Y.Z в pubspec.yaml
```

## Причина

Бот пытался искать версию в `.sln` файле, который указан в поле `project_file_path`. Однако версия в Xamarin проектах хранится в `.csproj` файлах, а не в `.sln` файлах.

Старая логика:
1. Проверял основной файл проекта (`project_file_path`) — мог быть `.sln` файлом
2. Если версия не найдена, искал только платформенные проекты (`.Android.csproj`, `.iOS.csproj`)
3. Не находил версию, если она была в обычных `.csproj` файлах

## Решение

### 1. Добавлен метод `_find_all_csproj_files()`

Новый метод находит **все** `.csproj` файлы в папке проекта и подпапках:

```python
def _find_all_csproj_files(self, project: Project) -> List[str]:
    """
    Находит все .csproj файлы в проекте Xamarin.

    Логика:
    - Если project_file_path указывает на файл (например, .sln),
      берется его директория
    - Поиск выполняется рекурсивно во всех подпапках
    - Возвращается список всех найденных .csproj файлов
    """
```

### 2. Обновлен метод `get_current_version()`

Новая логика поиска версии:

1. **Проверка основного файла** (только если это `.csproj`, а не `.sln`):
   - Если `project_file_path` заканчивается на `.csproj`, проверяется этот файл

2. **Поиск во всех .csproj файлах**:
   - Вызывается `_find_all_csproj_files()` для поиска всех `.csproj` файлов
   - Проверяется каждый найденный файл
   - Возвращается первая найденная версия

**Преимущества:**
- ✅ Игнорирует `.sln` файлы
- ✅ Находит версию в любом `.csproj` файле
- ✅ Работает с проектами любой структуры

### 3. Обновлен метод `update_version()`

Новая логика обновления версии:

1. Находит все `.csproj` файлы через `_find_all_csproj_files()`
2. Пытается обновить версию в каждом файле
3. Не считает ошибкой, если в некоторых файлах нет версии (могут быть тестовые проекты или библиотеки)
4. Возвращает успех, если хотя бы в одном файле версия обновлена

**Преимущества:**
- ✅ Обновляет версию во всех `.csproj` файлах проекта
- ✅ Работает с платформенными проектами (Android, iOS, UWP)
- ✅ Работает с обычными проектами

### 4. Улучшено сообщение об ошибке

В `prepare_release_callback.py` добавлено специфичное для Xamarin сообщение об ошибке:

```
❌ Не удалось определить текущую версию проекта Fintech

Ветка релиза: master

Файл проекта: Fintech/Fintech.sln

Для проектов Xamarin версия ищется во всех .csproj файлах в папке проекта и подпапках.
Убедитесь, что хотя бы в одном .csproj файле есть тег версии:
  - <Version>X.Y.Z</Version>
  - <ApplicationVersion>X.Y.Z</ApplicationVersion>
  - <ApplicationDisplayVersion>X.Y.Z</ApplicationDisplayVersion>
```

## Поддерживаемые теги версий в .csproj

Бот ищет и обновляет следующие теги в секции `<PropertyGroup>`:

1. **`<Version>`** — стандартный тег версии .NET
   ```xml
   <PropertyGroup>
     <Version>1.2.3</Version>
   </PropertyGroup>
   ```

2. **`<ApplicationVersion>`** — версия приложения
   ```xml
   <PropertyGroup>
     <ApplicationVersion>1.2.3</ApplicationVersion>
   </PropertyGroup>
   ```

3. **`<ApplicationDisplayVersion>`** — отображаемая версия (для совместимости с MAUI)
   ```xml
   <PropertyGroup>
     <ApplicationDisplayVersion>1.2.3</ApplicationDisplayVersion>
   </PropertyGroup>
   ```

## Пример структуры проекта

### До исправления (не работало)

```
Fintech/
├── Fintech.sln                    ← project_file_path указывал сюда
├── Fintech/
│   └── Fintech.csproj             ← Версия здесь НЕ искалась
├── Fintech.Android/
│   └── Fintech.Android.csproj     ← Только платформенные проекты проверялись
└── Fintech.iOS/
    └── Fintech.iOS.csproj
```

### После исправления (работает)

```
Fintech/
├── Fintech.sln                    ← project_file_path указывает сюда
├── Fintech/
│   └── Fintech.csproj             ← ✅ Теперь ищется здесь
├── Fintech.Android/
│   └── Fintech.Android.csproj     ← ✅ И здесь
└── Fintech.iOS/
    └── Fintech.iOS.csproj         ← ✅ И здесь
```

Бот найдет версию в любом из `.csproj` файлов!

## Что нужно сделать разработчику

### Вариант 1: Добавить версию в .csproj (рекомендуется)

Откройте любой `.csproj` файл проекта (например, `Fintech/Fintech.csproj`) и добавьте тег версии:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <!-- Другие настройки -->
    <Version>1.0.0</Version>
  </PropertyGroup>
</Project>
```

Или:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <!-- Другие настройки -->
    <ApplicationVersion>1.0.0</ApplicationVersion>
  </PropertyGroup>
</Project>
```

### Вариант 2: Изменить project_file_path (если нужно)

В настройках проекта в боте можно изменить `project_file_path` с `Fintech/Fintech.sln` на `Fintech/Fintech.csproj`:

```python
# До
project_file_path = "Fintech/Fintech.sln"

# После
project_file_path = "Fintech/Fintech.csproj"
```

**Но это необязательно!** Бот теперь автоматически найдет все `.csproj` файлы в папке.

## Тестирование

После внесения изменений:

1. Закоммитьте и запушьте изменения в репозиторий
2. Попробуйте снова запустить сборку через бота
3. Бот должен успешно найти версию в `.csproj` файлах

## Связанные файлы

- `python/src/easybuild_bot/version_services/xamarin_version_service.py` — основная логика
- `python/src/easybuild_bot/commands/implementations/prepare_release_callback.py` — сообщения об ошибках
- `docs/XAMARIN_MULTI_PLATFORM_SUPPORT.md` — документация по платформенным проектам
