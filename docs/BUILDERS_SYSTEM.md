# Система сборки проектов (Builders)

> ⚠️ **УСТАРЕВШИЙ ДОКУМЕНТ**
> 
> Эта система больше не используется. С 29 октября 2025 года бот не выполняет локальную сборку проектов.
> 
> Сборка происходит автоматически в репозитории через CI/CD (например, GitHub Actions).
> 
> См. актуальный документ: [SIMPLIFIED_RELEASE_PROCESS.md](SIMPLIFIED_RELEASE_PROCESS.md)

## Дата: 27 октября 2025

## Обзор

Реализована система builder'ов для различных типов проектов с использованием паттерна **Strategy**. Это позволяет легко добавлять поддержку новых типов проектов без изменения основного кода.

## Архитектура

### Структура файлов

```
python/src/easybuild_bot/builders/
├── __init__.py                 # Экспорт всех классов
├── base.py                     # Базовый интерфейс ProjectBuilder
├── flutter_builder.py          # Реализация для Flutter
├── dotnet_maui_builder.py      # Реализация для .NET MAUI
├── xamarin_builder.py          # Реализация для Xamarin
└── factory.py                  # Factory для создания builder'ов
```

### Диаграмма классов

```
ProjectBuilder (ABC)
├── prepare_environment() -> BuildResult
├── build_debug() -> BuildResult
├── build_release() -> BuildResult
├── get_version_info() -> Optional[str]
└── clean() -> BuildResult

    ↑ implements
    │
    ├── FlutterBuilder
    ├── DotNetMauiBuilder
    └── XamarinBuilder

ProjectBuilderFactory
└── create_builder(project) -> ProjectBuilder
```

## Базовые классы

### `BuildStep` (Enum)

Этапы процесса сборки:
- `PREPARING` - подготовка окружения
- `DEPENDENCIES` - установка зависимостей
- `BUILDING` - сборка проекта
- `SIGNING` - подписание (если требуется)
- `PACKAGING` - упаковка
- `COMPLETED` - успешное завершение
- `FAILED` - ошибка

### `BuildResult` (dataclass)

Результат операции сборки:
```python
@dataclass
class BuildResult:
    success: bool
    step: BuildStep
    message: str
    artifact_path: Optional[str] = None
    error: Optional[str] = None
```

### `ProjectBuilder` (ABC)

Базовый абстрактный класс для всех builder'ов.

**Методы:**
- `prepare_environment()` - подготовка окружения (установка зависимостей)
- `build_debug()` - сборка debug версии
- `build_release()` - сборка release версии
- `get_version_info()` - получение версии из файлов проекта
- `clean()` - очистка артефактов сборки
- `send_message(message)` - отправка прогресс-сообщений через callback

## Реализации Builder'ов

### FlutterBuilder

**Команды:**
- Зависимости: `flutter pub get`
- Debug: `flutter build apk --debug`
- Release: `flutter build apk --release`
- Clean: `flutter clean`

**Путь к APK:**
- Debug: `build/app/outputs/flutter-apk/app-debug.apk`
- Release: `build/app/outputs/flutter-apk/app-release.apk`

**Версия:** извлекается из `pubspec.yaml` (поле `version`)

**Timeout:**
- Зависимости: 5 минут
- Сборка: 30 минут
- Clean: 1 минута

### DotNetMauiBuilder

**Команды:**
- Зависимости: `dotnet restore`
- Debug: `dotnet build -f net8.0-android -c Debug`
- Release: `dotnet publish -f net8.0-android -c Release`
- Clean: `dotnet clean`

**Путь к APK:**
- Debug: `bin/Debug/net8.0-android/*-Signed.apk`
- Release: `bin/Release/net8.0-android/publish/*-Signed.apk`

**Версия:** извлекается из `.csproj` (тег `<ApplicationVersion>` или `<Version>`)

**Timeout:**
- Зависимости: 10 минут
- Сборка: 30 минут
- Clean: 1 минута

### XamarinBuilder

**Команды:**
- Зависимости: `msbuild /t:Restore`
- Debug: `msbuild /p:Configuration=Debug /p:Platform=AnyCPU /t:PackageForAndroid`
- Release: `msbuild /p:Configuration=Release /p:Platform=AnyCPU /t:PackageForAndroid`
- Clean: `msbuild /t:Clean`

**Путь к APK:**
- Debug: `bin/Debug/*.apk`
- Release: `bin/Release/*.apk`

**Версия:** извлекается из `.csproj` (тег `<Version>` или `<ApplicationVersion>`)

**Timeout:**
- Зависимости: 10 минут
- Сборка: 30 минут
- Clean: 1 минута

## ProjectBuilderFactory

Factory для создания нужного builder'а на основе типа проекта.

```python
builder = ProjectBuilderFactory.create_builder(
    project=project,
    message_callback=async_callback_function
)
```

**Методы:**
- `create_builder(project, message_callback)` - создать builder
- `get_supported_types()` - получить список поддерживаемых типов
- `is_supported(project_type)` - проверить поддержку типа

## Интеграция с командами

### ProjectSelectCallbackCommand

После клонирования и переключения на ветку:
1. Создает builder через factory
2. Получает версию проекта
3. Показывает меню с кнопками:
   - 🔨 Собрать Debug
   - 🚀 Собрать Release
   - 🧹 Очистить артефакты

### BuildActionCallbackCommand

Новая команда для обработки действий сборки:
- Обрабатывает callback'и: `build_debug:<project_id>`, `build_release:<project_id>`, `build_clean:<project_id>`
- Создает builder через factory
- Выполняет запрошенное действие
- Отправляет прогресс-сообщения пользователю

**Callback patterns:**
- `build_debug:*` - сборка debug
- `build_release:*` - сборка release
- `build_clean:*` - очистка артефактов

## Workflow использования

1. Пользователь вызывает `/build`
2. Выбирает проект → клонирование → переключение на ветку
3. Бот показывает кнопки действий с версией проекта
4. Пользователь нажимает кнопку (Debug/Release/Clean)
5. BuildActionCallbackCommand:
   - Создает builder для типа проекта
   - Подготавливает окружение
   - Выполняет сборку
   - Отправляет прогресс-сообщения
   - Сообщает о результате с путем к файлу

## Пример использования

```python
# В callback команде
async def send_message(msg: str):
    await update.message.reply_text(msg)

# Создать builder
builder = ProjectBuilderFactory.create_builder(project, send_message)

# Получить версию
version = await builder.get_version_info()
print(f"Version: {version}")

# Подготовить окружение
prep_result = await builder.prepare_environment()
if not prep_result.success:
    print(f"Preparation failed: {prep_result.error}")
    return

# Собрать debug
build_result = await builder.build_debug()
if build_result.success:
    print(f"APK ready: {build_result.artifact_path}")
else:
    print(f"Build failed: {build_result.error}")
```

## Добавление нового типа проекта

1. Создать новый файл `new_type_builder.py` в `builders/`
2. Реализовать класс, наследующий `ProjectBuilder`
3. Добавить новый `ProjectType` в `models.py`
4. Зарегистрировать в `ProjectBuilderFactory.create_builder()`
5. Экспортировать в `builders/__init__.py`

Пример:
```python
class NewTypeBuilder(ProjectBuilder):
    async def prepare_environment(self) -> BuildResult:
        # Установка зависимостей
        pass
    
    async def build_debug(self) -> BuildResult:
        # Сборка debug
        pass
    
    async def build_release(self) -> BuildResult:
        # Сборка release
        pass
    
    async def get_version_info(self) -> Optional[str]:
        # Получение версии
        pass
    
    async def clean(self) -> BuildResult:
        # Очистка
        pass
```

## Обработка ошибок

Все builder'ы обрабатывают:
- **TimeoutExpired** - превышение timeout'а команды
- **FileNotFoundError** - отсутствие файлов проекта/артефактов
- **subprocess errors** - ошибки выполнения команд

Ошибки возвращаются в `BuildResult.error` и отображаются пользователю.

## Прогресс-сообщения

Builder'ы отправляют прогресс через `send_message()`:
- "📦 Установка зависимостей..."
- "✅ Зависимости успешно установлены"
- "🔨 Сборка debug APK..."
- "✅ Debug APK успешно собран"
- "❌ Ошибка сборки: ..."

## Зависимости

**Системные требования:**
- Flutter SDK (для Flutter проектов)
- .NET SDK 8.0+ (для .NET MAUI проектов)
- MSBuild (для Xamarin проектов)
- Git

**Python зависимости:**
- subprocess (стандартная библиотека)
- asyncio (для async операций)

## Безопасность

- Все команды выполняются с timeout'ами
- Проверка существования проекта в БД
- Проверка прав доступа через `_check_user_access()`
- Валидация путей файлов

## Масштабируемость

Система легко расширяется:
- ✅ Добавление новых типов проектов (просто новый builder)
- ✅ Добавление новых действий (добавить метод в интерфейс)
- ✅ Изменение логики для конкретного типа (редактирование одного builder'а)
- ✅ Независимое тестирование каждого builder'а

## TODO (будущие улучшения)

- [ ] Поддержка iOS сборок (IPA)
- [ ] Поддержка Web сборок (Flutter Web)
- [ ] Параллельная сборка нескольких конфигураций
- [ ] Кеширование зависимостей
- [ ] Прогресс-бар для длительных операций
- [ ] Логирование в файл
- [ ] Метрики времени сборки
- [ ] Автоматическое тестирование после сборки
- [ ] Публикация в магазины (Google Play, App Store)




