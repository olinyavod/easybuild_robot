# Улучшенная архитектура Dependency Injection

## Обзор изменений

Мы полностью переработали систему DI для устранения ручного создания зависимостей в `main.py`. Теперь все зависимости автоматически разрешаются через DI-контейнер.

## Основные улучшения

### 1. Класс Settings для централизованного управления конфигурацией

**Файл:** `src/easybuild_bot/config.py`

Вместо разрозненных `os.getenv()` вызовов и ручной настройки `container.config.set()`, теперь используется единый класс `Settings`:

```python
@dataclass
class Settings:
    """Настройки приложения, загружаемые из переменных окружения."""
    
    # Обязательные параметры
    bot_token: str
    
    # Опциональные с умными значениями по умолчанию
    admin_token: Optional[str]
    data_dir: str
    whisper_enabled: bool
    tts_enabled: bool
    # ... и другие
```

#### Преимущества:

- ✅ **Валидация при запуске** - все ошибки конфигурации обнаруживаются сразу
- ✅ **Типизация** - IDE подсказывает доступные настройки
- ✅ **Единое место** - вся конфигурация в одном классе
- ✅ **Документированные значения по умолчанию** - не нужно искать по коду
- ✅ **Автоматическое создание директорий** - готово к работе сразу

### 2. Полностью автоматический DI контейнер

**Файл:** `src/easybuild_bot/di.py`

#### Было (старая версия):

```python
# В main.py - ручное создание зависимостей
container = Container()
container.config.set("database.dir_path", monty_dir)
container.config.set("database.db_name", monty_db)
# ... ещё 10 строк настроек

storage = container.storage()
access_control = container.access_control()
# Сервисы создавались вручную!
speech_service = SpeechRecognitionService(model_name=whisper_model, language="ru")
tts_service = TextToSpeechService(language="ru", speaker=tts_speaker, ...)

# И только потом бот
bot = EasyBuildBot(
    storage=storage,
    access_control=access_control,
    # ... 5 аргументов
    speech_service=speech_service,
    tts_service=tts_service
)
```

#### Стало (новая версия):

```python
# В main.py - всё автоматически!
container = Container()
bot = container.bot()  # ВСЁ! Все зависимости разрешаются автоматически
```

### 3. Структура улучшенного контейнера

```python
class Container(containers.DeclarativeContainer):
    """DI Container для всех зависимостей приложения."""
    
    # ========== Конфигурация ==========
    settings = providers.Singleton(Settings.from_env)
    
    # ========== База данных ==========
    storage = providers.Singleton(
        Storage,
        dir_path=settings.provided.montydb_dir,
        db_name=settings.provided.montydb_name,
    )
    
    # ========== Контроль доступа ==========
    access_control = providers.Singleton(
        AccessControlService,
        storage=storage,
    )
    
    # ========== Command Pattern система ==========
    command_system = providers.Singleton(
        create_command_system,
        storage=storage,
        access_control=access_control,
        model_name=settings.provided.command_matcher_model,
        threshold=settings.provided.command_matcher_threshold,
    )
    
    command_registry = providers.Callable(...)
    command_executor = providers.Callable(...)
    
    # ========== Опциональные сервисы ==========
    speech_service = providers.Singleton(
        create_speech_service,
        settings=settings,
    )
    
    tts_service = providers.Singleton(
        create_tts_service,
        settings=settings,
    )
    
    # ========== Основной бот ==========
    bot = providers.Singleton(
        EasyBuildBot,
        storage=storage,
        access_control=access_control,
        command_registry=command_registry,
        command_executor=command_executor,
        admin_token=settings.provided.admin_token,
        speech_service=speech_service,
        tts_service=tts_service,
    )
```

### 4. Фабрики для опциональных сервисов

Сервисы распознавания речи и синтеза речи теперь создаются через фабричные функции:

```python
def create_speech_service(settings: Settings) -> Optional[SpeechRecognitionService]:
    """Фабрика для создания сервиса распознавания речи."""
    if not settings.whisper_enabled:
        return None
    
    try:
        return SpeechRecognitionService(
            model_name=settings.whisper_model,
            language=settings.whisper_language
        )
    except Exception as e:
        logger.warning(f"Failed to initialize: {e}")
        return None
```

Преимущества:
- ✅ Graceful degradation - бот работает даже если сервис не загрузился
- ✅ Централизованная обработка ошибок
- ✅ Логирование в одном месте

## Упрощённый main.py

**Было:** ~125 строк с ручной настройкой  
**Стало:** ~70 строк - только логика запуска

```python
def main() -> None:
    """Главная функция для инициализации и запуска бота с полным DI."""
    load_dotenv()
    
    # Всё!
    container = Container()
    settings = container.settings()
    
    # Настройка логирования из settings
    logging.basicConfig(
        format=settings.log_format,
        level=getattr(logging, settings.log_level.upper())
    )
    
    # Получаем готовый бот
    bot = container.bot()
    
    # Запускаем
    app = Application.builder().token(settings.bot_token).build()
    bot.setup_handlers(app)
    app.run_polling()
```

## Конфигурация через .env

Создан подробный `.env.example` со всеми доступными параметрами:

```bash
# Обязательные
BOT_TOKEN=your_token_here

# Опциональные (с умолчанию)
ADMIN_TOKEN=...
DATA_DIR=./data
MONTYDB_DIR=./data/monty
MONTYDB_DB=easybuild_bot

# Semantic search
COMMAND_MATCHER_MODEL=cointegrated/rubert-tiny
COMMAND_MATCHER_THRESHOLD=0.5

# Speech recognition
WHISPER_ENABLED=true
WHISPER_MODEL=base
WHISPER_LANGUAGE=ru

# Text-to-speech
TTS_ENABLED=true
TTS_LANGUAGE=ru
TTS_SPEAKER=baya
TTS_SAMPLE_RATE=48000

# Логирование
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Ответ на вопрос о пакете DI

**Вопрос:** Являются ли проблемы ограничением `dependency-injector`?

**Ответ:** Нет! Пакет `dependency-injector` - очень мощный и гибкий. Проблемы были в **архитектуре**, а не в инструменте:

### Что было не так (архитектурные проблемы):

1. ❌ **Частичное использование DI** - контейнер использовался только для части зависимостей
2. ❌ **Ручная настройка конфигурации** - множество `container.config.set()` вызовов
3. ❌ **Ручное создание сервисов** - speech и tts сервисы создавались вне контейнера
4. ❌ **Бот создавался вручную** - главный компонент не был в контейнере
5. ❌ **Разрозненные настройки** - `os.getenv()` по всему main.py

### Что стало правильно:

1. ✅ **Полное использование DI** - всё в контейнере
2. ✅ **Класс Settings** - один источник конфигурации
3. ✅ **Фабрики в контейнере** - опциональные сервисы через фабричные функции
4. ✅ **Бот в контейнере** - полная автоматизация
5. ✅ **Централизованная конфигурация** - всё через Settings

## Граф зависимостей

```
Settings (from .env)
    ↓
├─→ Storage ──────────→ AccessControlService
│                            ↓
├─→ CommandMatcher ─────────┤
│                            ↓
│                       CommandSystem
│                       (Registry + Executor)
│                            ↓
├─→ SpeechRecognitionService ┤
│                            ↓
├─→ TextToSpeechService ─────┤
│                            ↓
└──────────────────────→ EasyBuildBot
```

Все зависимости разрешаются автоматически при вызове `container.bot()`!

## Миграция

Если у вас был старый код с ручной настройкой:

### 1. Создайте .env файл
```bash
cp python/.env.example python/.env
# Отредактируйте .env
```

### 2. Удалите старую ручную настройку
Не нужно больше вызывать:
- `container.config.set()`
- Создавать сервисы вручную
- Передавать зависимости в бота

### 3. Используйте новый упрощённый main.py
```python
from src.easybuild_bot.di import Container

container = Container()
bot = container.bot()
```

## Тестирование

### Проверка конфигурации

```python
from src.easybuild_bot.config import Settings

settings = Settings.from_env()
print(settings.to_dict())  # Безопасный вывод (без токенов)
```

### Переопределение настроек для тестов

```python
settings = Settings(
    bot_token="test_token",
    whisper_enabled=False,
    tts_enabled=False,
)
```

### Мокирование в контейнере

```python
container = Container()
container.storage.override(providers.Singleton(MockStorage))
bot = container.bot()  # Использует MockStorage
```

## Заключение

Новая архитектура:
- 📉 **Меньше кода** - main.py сократился на 40%
- 🔒 **Безопаснее** - валидация при запуске
- 📖 **Понятнее** - весь граф зависимостей виден в di.py
- 🧪 **Тестируемее** - легко мокировать через контейнер
- 🚀 **Быстрее разрабатывать** - добавление нового сервиса = добавление в контейнер

Это пример правильного использования Dependency Injection!

