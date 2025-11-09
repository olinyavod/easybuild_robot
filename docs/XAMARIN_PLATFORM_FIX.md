# Исправление версионирования Xamarin проектов - платформенные файлы

## Дата: 9 ноября 2025 (обновление №2)

## Проблема

После первого исправления бот всё ещё не мог определить версию, потому что искал версии в **любых** `.csproj` файлах, а не в **платформенных** файлах с **специфичными** тегами.

### Как должно работать

Для Xamarin проектов версия хранится в **платформенных** файлах:
- `*.Android.csproj` или `*.Droid.csproj` - для Android
- `*.iOS.csproj` - для iOS

И в этих файлах используются **специфичные для платформы** теги версий.

## Решение №2

### Обновлённая логика

1. **Поиск только платформенных файлов**
   Бот теперь ищет **только** `*.Android.csproj` и `*.iOS.csproj` файлы

2. **Специфичные теги для каждой платформы**

   **Android** (`*.Android.csproj`):
   - `<ApplicationVersion>X.Y.Z</ApplicationVersion>` - версия приложения
   - `<AndroidVersionCode>N</AndroidVersionCode>` - код версии (автоматически генерируется из версии: 1.2.3 → 10203)

   **iOS** (`*.iOS.csproj`):
   - `<ApplicationVersion>X.Y.Z</ApplicationVersion>` - версия приложения
   - `<CFBundleVersion>X.Y.Z</CFBundleVersion>` - версия bundle
   - `<CFBundleShortVersionString>X.Y.Z</CFBundleShortVersionString>` - короткая версия

3. **Сообщения о недостающих платформах**
   Если не найдено ни одного файла Android или iOS - бот сообщает об этом

## Изменения в коде

### 1. Добавлен метод `_get_platform_type()`

Определяет тип платформы по имени файла:

```python
def _get_platform_type(self, csproj_filename: str) -> Optional[str]:
    filename_lower = csproj_filename.lower()
    if '.android.csproj' in filename_lower or '.droid.csproj' in filename_lower:
        return 'android'
    elif '.ios.csproj' in filename_lower:
        return 'ios'
    return None
```

### 2. Обновлён метод `_get_version_from_csproj()`

Ищет версию с учётом типа платформы:

```python
# Для Android ищет ApplicationVersion
# Для iOS ищет ApplicationVersion или CFBundleShortVersionString
```

### 3. Обновлён метод `_update_version_in_csproj()`

Обновляет платформенные теги:

**Android:**
- `ApplicationVersion` → версия (1.2.3)
- `AndroidVersionCode` → код (10203)

**iOS:**
- `ApplicationVersion` → версия (1.2.3)
- `CFBundleShortVersionString` → версия (1.2.3)
- `CFBundleVersion` → версия (1.2.3)

### 4. Обновлён метод `get_current_version()`

- Ищет **только** в платформенных файлах
- Проверяет наличие Android и iOS проектов
- Сообщает, если платформы не найдены

### 5. Обновлён метод `update_version()`

- Обновляет версию **только** в платформенных файлах
- Показывает, сколько файлов каждой платформы обновлено
- Сообщает о недостающих платформах

### 6. Удалён метод `_find_all_csproj_files()`

Больше не нужен, так как работаем только с платформенными файлами.

## Инструкция для разработчиков

### Для Android проекта

Откройте файл `*.Android.csproj` и добавьте:

```xml
<Project>
  <PropertyGroup>
    <!-- Другие настройки -->
    <ApplicationVersion>1.0.0</ApplicationVersion>
    <AndroidVersionCode>10000</AndroidVersionCode>
  </PropertyGroup>
</Project>
```

### Для iOS проекта

Откройте файл `*.iOS.csproj` и добавьте:

```xml
<Project>
  <PropertyGroup>
    <!-- Другие настройки -->
    <ApplicationVersion>1.0.0</ApplicationVersion>
    <CFBundleVersion>1.0.0</CFBundleVersion>
  </PropertyGroup>
</Project>
```

### Примеры файлов

**Fintech.Android/Fintech.Android.csproj:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<Project>
  <PropertyGroup>
    <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration>
    <Platform Condition=" '$(Platform)' == '' ">AnyCPU</Platform>
    <ApplicationVersion>1.0.0</ApplicationVersion>
    <AndroidVersionCode>10000</AndroidVersionCode>
    <!-- Другие настройки -->
  </PropertyGroup>
</Project>
```

**Fintech.iOS/Fintech.iOS.csproj:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<Project>
  <PropertyGroup>
    <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration>
    <Platform Condition=" '$(Platform)' == '' ">iPhoneSimulator</Platform>
    <ApplicationVersion>1.0.0</ApplicationVersion>
    <CFBundleVersion>1.0.0</CFBundleVersion>
    <CFBundleShortVersionString>1.0.0</CFBundleShortVersionString>
    <!-- Другие настройки -->
  </PropertyGroup>
</Project>
```

## Новые сообщения об ошибках

### Если не найдено платформенных файлов

```
❌ Не удалось определить текущую версию проекта Fintech

Ветка релиза: master

Файл проекта: Fintech/Fintech.sln

Для проектов Xamarin версия ищется в платформенных файлах:
  • *.Android.csproj или *.Droid.csproj
  • *.iOS.csproj

Убедитесь, что в платформенных файлах есть теги версий:

**Для Android:**
  • <ApplicationVersion>X.Y.Z</ApplicationVersion>
  • <AndroidVersionCode>N</AndroidVersionCode>

**Для iOS:**
  • <ApplicationVersion>X.Y.Z</ApplicationVersion>
  • <CFBundleVersion>X.Y.Z</CFBundleVersion>
```

### При успешном обновлении

```
✅ Версия успешно обновлена на 1.0.1

Платформы: Android (1), iOS (1)

Обновлённые файлы:
  • Fintech.Android/Fintech.Android.csproj
  • Fintech.iOS/Fintech.iOS.csproj
```

## Автоматическая генерация AndroidVersionCode

Код версии для Android генерируется автоматически из версии:

| Версия | AndroidVersionCode |
|--------|-------------------|
| 1.0.0  | 10000             |
| 1.0.1  | 10001             |
| 1.2.3  | 10203             |
| 2.5.10 | 20510             |

**Формула:** `Major * 10000 + Minor * 100 + Patch`

## Тестирование

После добавления тегов версий:

1. Закоммитьте изменения:
   ```bash
   git add .
   git commit -m "Добавлены теги версий в платформенные проекты"
   git push
   ```

2. Запустите сборку через бота

3. Бот должен успешно найти и обновить версию во всех платформенных файлах

## Преимущества нового подхода

✅ **Правильная работа с Xamarin** - используются платформенные теги
✅ **Автоматическая генерация кодов версий** - AndroidVersionCode вычисляется автоматически
✅ **Информативные сообщения** - показывает, какие платформы найдены
✅ **Поддержка iOS** - правильные теги CFBundleVersion
✅ **Надёжность** - работает только с нужными файлами

## Связанные документы

- `docs/XAMARIN_VERSION_FIX.md` - первое исправление (устарело)
- `docs/XAMARIN_MULTI_PLATFORM_SUPPORT.md` - общая информация
- `python/src/easybuild_bot/version_services/xamarin_version_service.py` - исходный код
