# Поддержка множественных платформенных проектов Xamarin

## Обзор

Xamarin проекты часто состоят из нескольких подпроектов для разных платформ:
- **Android** - файлы с расширением `*.Android.csproj` или `*.Droid.csproj`
- **iOS** - файлы с расширением `*.iOS.csproj`
- **UWP** (Universal Windows Platform) - файлы с расширением `*.UWP.csproj`
- **Windows Phone** - файлы с расширением `*.WinPhone.csproj`

`XamarinVersionService` был обновлён для автоматического поиска и обновления версий во всех этих платформенных проектах.

## Как это работает

### 1. Поиск платформенных проектов

При обновлении версии сервис автоматически сканирует репозиторий на наличие файлов проектов с соответствующими расширениями:

```python
patterns = [
    '*.Android.csproj',
    '*.iOS.csproj',
    '*.UWP.csproj',
    '*.WinPhone.csproj',
    '*.Droid.csproj'
]
```

Поиск выполняется рекурсивно во всех подкаталогах проекта.

### 2. Обновление версий

Сервис обновляет версии в следующих тегах XML:
- `<Version>` - стандартный тег версии
- `<ApplicationVersion>` - версия приложения
- `<ApplicationDisplayVersion>` - отображаемая версия (для совместимости)

### 3. Обработка отсутствующих платформ

**⚠️ Важно:** Система **автоматически пропускает** отсутствующие платформы без ошибок!

Примеры:
- ✅ Если есть только Android проект (без iOS) - обновит только Android
- ✅ Если есть только iOS проект (без Android) - обновит только iOS
- ✅ Если есть Android + UWP (без iOS) - обновит оба найденных проекта
- ✅ Если есть основной + Android (без iOS) - обновит оба файла

**Результат:** Операция считается успешной, если обновлён хотя бы один файл.

### 4. Обработка ошибок

- Если основной файл проекта не содержит версии, это не считается ошибкой
- Если не найдено ни одного платформенного проекта, возвращается ошибка
- Если некоторые проекты обновились, а некоторые нет - возвращается частичный успех с детальным отчётом

## Пример структуры проекта

```
MyXamarinApp/
├── MyXamarinApp.csproj                    # Основной проект (shared)
├── MyXamarinApp.Android/
│   └── MyXamarinApp.Android.csproj       # Android проект
├── MyXamarinApp.iOS/
│   └── MyXamarinApp.iOS.csproj           # iOS проект
└── MyXamarinApp.UWP/
    └── MyXamarinApp.UWP.csproj           # UWP проект
```

## Использование

### Получение текущей версии

```python
from easybuild_bot.version_services.xamarin_version_service import XamarinVersionService
from easybuild_bot.models import Project, ProjectType

# Создаём проект
project = Project(
    id="my-xamarin-app",
    name="MyXamarinApp",
    project_type=ProjectType.XAMARIN,
    git_url="https://github.com/user/MyXamarinApp.git",
    project_file_path="MyXamarinApp.csproj",  # Основной файл проекта
    local_repo_path="/path/to/repo",
    dev_branch="develop",
    release_branch="main"
)

# Создаём сервис и получаем версию
service = XamarinVersionService()
version = await service.get_current_version(project)
print(f"Текущая версия: {version}")
```

### Обновление версии

```python
# Обновляем версию
new_version = "2.0.0"
success, message = await service.update_version(project, new_version)

if success:
    print(f"✅ {message}")
else:
    print(f"❌ {message}")
```

## Примеры вывода

### Успешное обновление всех проектов

```
✅ Версия успешно обновлена на 2.0.0 в следующих файлах:
  • MyXamarinApp.csproj
  • MyXamarinApp.Android/MyXamarinApp.Android.csproj
  • MyXamarinApp.iOS/MyXamarinApp.iOS.csproj
```

### Обновление только части платформ (без ошибок!)

```
✅ Версия успешно обновлена на 2.0.0 в следующих файлах:
  • MyXamarinApp.Android/MyXamarinApp.Android.csproj
```

**Примечание:** iOS проект отсутствует, но это **не ошибка** - система просто обновила найденные проекты.

### Частичное обновление (с ошибками)

```
✅ Версия частично обновлена на 2.0.0.

Успешно:
  • MyXamarinApp.Android/MyXamarinApp.Android.csproj
  • MyXamarinApp.iOS/MyXamarinApp.iOS.csproj

Ошибки:
  • MyXamarinApp.UWP/MyXamarinApp.UWP.csproj: Не найдена строка с версией в файле
```

### Ошибка - проекты не найдены

```
❌ Не найдено ни одного платформенного проекта (.Android.csproj, .iOS.csproj и т.д.) в /path/to/repo
```

## Тестирование

### Базовые тесты

Для тестирования функциональности используйте тестовый скрипт:

```bash
cd python/scripts
python test_xamarin_version_service.py
```

Скрипт создаёт временную структуру проекта Xamarin и проверяет:
1. Получение текущей версии
2. Обновление версии во всех файлах
3. Корректность обновления в каждом файле отдельно

### Тесты для частичного набора платформ

Для тестирования поведения при отсутствующих платформах:

```bash
cd python/scripts
python test_xamarin_partial_platforms.py
```

Этот скрипт проверяет:
1. ✅ Проект только с Android (без iOS)
2. ✅ Проект только с iOS (без Android)
3. ✅ Проект с Android + UWP (без iOS)
4. ✅ Основной проект + Android (без iOS)

**Ожидаемый результат:** Все тесты проходят успешно, демонстрируя что система корректно обрабатывает любую комбинацию платформ.

## Логирование

Сервис подробно логирует все операции:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Примеры логов:

```
INFO:easybuild_bot.version_services.xamarin_version_service:Поиск платформенных проектов Xamarin в /path/to/repo
INFO:easybuild_bot.version_services.xamarin_version_service:Найден платформенный проект: MyXamarinApp.Android/MyXamarinApp.Android.csproj
INFO:easybuild_bot.version_services.xamarin_version_service:Найден платформенный проект: MyXamarinApp.iOS/MyXamarinApp.iOS.csproj
INFO:easybuild_bot.version_services.xamarin_version_service:Версия обновлена в платформенном проекте: MyXamarinApp.Android/MyXamarinApp.Android.csproj
INFO:easybuild_bot.version_services.xamarin_version_service:Версия обновлена в платформенном проекте: MyXamarinApp.iOS/MyXamarinApp.iOS.csproj
```

## Принципы проектирования

### SOLID

- **Single Responsibility**: Каждый метод выполняет одну задачу (поиск, чтение, обновление)
- **Open/Closed**: Легко добавить поддержку новых паттернов файлов проектов
- **Liskov Substitution**: Сервис реализует базовый интерфейс `VersionService`
- **Interface Segregation**: Минималистичный интерфейс с только необходимыми методами
- **Dependency Inversion**: Зависимость от абстракции `VersionService`, а не конкретной реализации

### KISS (Keep It Simple, Stupid)

- Простая и понятная логика
- Минимум зависимостей (только стандартная библиотека Python)
- Понятные названия методов и переменных
- Подробные комментарии и документация

## Возможные расширения

### Поддержка дополнительных паттернов

Если в вашем проекте используются другие расширения файлов, добавьте их в список паттернов:

```python
patterns = [
    '*.Android.csproj',
    '*.iOS.csproj',
    '*.UWP.csproj',
    '*.WinPhone.csproj',
    '*.Droid.csproj',
    '*.YourCustomPlatform.csproj'  # Добавьте свой паттерн
]
```

### Поддержка AndroidManifest.xml и Info.plist

В будущем можно добавить обновление версий в платформенно-специфичных файлах:
- `AndroidManifest.xml` для Android (versionCode и versionName)
- `Info.plist` для iOS (CFBundleShortVersionString и CFBundleVersion)

## Дата создания

9 ноября 2025

