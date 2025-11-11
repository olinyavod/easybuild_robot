# Исправление обновления версий в Xamarin проектах с XML namespace

## Дата: 11 ноября 2025 (обновление №3)

## Проблема

После добавления тегов версий в файлы проектов бот всё ещё не мог обновить версии, выдавая ошибку:

```
❌ Не удалось обновить версию ни в одном файле

Ошибки:
  • Fintech/Fintech.iOS/Fintech.iOS.csproj: Не найдены теги версии для платформы ios
  • Fintech/Fintech.Android/Fintech.Android.csproj: Не найдены теги версии для платформы android
```

### Причина

Метод `_update_version_in_csproj` имел **две критические проблемы**:

1. **Не учитывался XML namespace** при поиске и обновлении тегов
   - Метод `_get_version_from_csproj` (чтение) поддерживал namespace
   - Метод `_update_version_in_csproj` (запись) НЕ поддерживал namespace

2. **`ET.write()` полностью переформатировал XML файлы**
   - Добавлял префиксы `ns0:` ко всем тегам
   - Менял кавычки в XML declaration
   - Полностью перестраивал структуру файла
   - Это делало git diff нечитаемым и ломало структуру проектов

## Решение

### 1. Добавлена поддержка XML namespace в метод обновления

Метод теперь ищет теги **с учётом namespace и без него**, аналогично методу чтения:

```python
# Проверяем namespace в корневом элементе
namespace = ''
if root.tag.startswith('{'):
    namespace = root.tag[root.tag.find('{'):root.tag.find('}') + 1]
    logger.debug(f"Обнаружен XML namespace при обновлении: {namespace}")

# Ищем PropertyGroup с учётом namespace и без него
property_group_paths = [
    './/PropertyGroup',  # Без namespace
    f'.//{namespace}PropertyGroup' if namespace else None  # С namespace
]

for path in property_group_paths:
    if path is None:
        continue

    for prop_group in root.findall(path):
        # Обновляем ApplicationVersion
        app_version_elem = prop_group.find('ApplicationVersion')
        if app_version_elem is None and namespace:
            app_version_elem = prop_group.find(f'{namespace}ApplicationVersion')

        if app_version_elem is not None:
            # Обновляем значение
```

### 2. Заменён способ записи на regex-замену в тексте

Вместо `ET.write()` используется **regex-замена значений напрямую в тексте файла**:

```python
# Сохраняем изменения напрямую в текст файла, чтобы сохранить форматирование
import re

# Читаем содержимое файла
with open(csproj_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Обновляем теги в тексте с помощью регулярных выражений
if platform == 'android':
    # Обновляем ApplicationVersion
    content = re.sub(
        r'(<ApplicationVersion>)[^<]+(</ApplicationVersion>)',
        rf'\g<1>{new_version}\g<2>',
        content
    )
    # Обновляем AndroidVersionCode
    parts = new_version.split('.')
    if len(parts) >= 3:
        version_code = int(parts[0]) * 10000 + int(parts[1]) * 100 + int(parts[2])
        content = re.sub(
            r'(<AndroidVersionCode>)[^<]+(</AndroidVersionCode>)',
            rf'\g<1>{version_code}\g<2>',
            content
        )

# Записываем обратно с сохранением BOM
with open(csproj_path, 'w', encoding='utf-8-sig') as f:
    f.write(content)
```

### Преимущества нового подхода:

✅ **Сохраняется всё форматирование файла**
✅ **Сохраняется UTF-8 BOM** (если был)
✅ **Минимальные изменения в git diff** (только значения тегов)
✅ **Не добавляются namespace префиксы**
✅ **Не меняется структура XML**

## Результат

### До исправления:

```
❌ Не удалось обновить версию ни в одном файле
```

### После исправления:

```
✅ Версия успешно обновлена на 1.11.6

Платформы: Android (1), iOS (1)

Обновлённые файлы:
  • Fintech.Android/Fintech.Android.csproj
  • Fintech.iOS/Fintech.iOS.csproj
```

### Git diff после обновления:

Только минимальные изменения в значениях тегов:

```diff
-    <ApplicationVersion>1.11.5</ApplicationVersion>
+    <ApplicationVersion>1.11.6</ApplicationVersion>
-    <AndroidVersionCode>11105</AndroidVersionCode>
+    <AndroidVersionCode>11106</AndroidVersionCode>
-    <CFBundleVersion>1.11.5</CFBundleVersion>
+    <CFBundleVersion>1.11.6</CFBundleVersion>
```

## Тестирование

Проведено успешное тестирование на реальном проекте Fintech:

```bash
cd /home/olinyavod/projects/easybuild_bot
python3 python/scripts/test_csproj_update.py
```

Результат:
- ✅ iOS проект: обновлены ApplicationVersion, CFBundleVersion, CFBundleShortVersionString
- ✅ Android проект: обновлены ApplicationVersion, AndroidVersionCode
- ✅ Форматирование файлов сохранено
- ✅ Git diff показывает только изменения значений тегов

## Файлы изменены

- `python/src/easybuild_bot/version_services/xamarin_version_service.py`
  - Метод `_update_version_in_csproj` полностью переработан

## Связанные документы

- `docs/XAMARIN_PLATFORM_FIX.md` - Исправление №1 (поиск платформенных файлов)
- `docs/XAMARIN_VERSION_LOGGING_FIX.md` - Исправление №2 (улучшение логирования)
- `docs/XAMARIN_QUICK_FIX_V2.md` - Краткое руководство по добавлению тегов версий
