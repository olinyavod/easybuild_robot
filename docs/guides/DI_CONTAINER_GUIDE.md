# Руководство по использованию DI Container

## Что такое DI Container?

Dependency Injection Container — это паттерн, который автоматически управляет созданием и внедрением зависимостей.

## Преимущества

✅ **Автоматическое создание объектов** — не нужно вручную создавать зависимости  
✅ **Singleton управление** — объекты создаются один раз и переиспользуются  
✅ **Централизованная конфигурация** — все настройки в одном месте  
✅ **Легкое тестирование** — можно легко подменять зависимости в тестах  

---

## Использование в проекте

### 1. Инициализация контейнера

```python
from src.easybuild_bot.di import Container

# Создание контейнера
container = Container()

# Конфигурация
container.config.set("database.dir_path", "./data/monty")
container.config.set("database.db_name", "easybuild_bot")
container.config.set("command_matcher.model_name", "cointegrated/rubert-tiny")
container.config.set("command_matcher.threshold", 0.5)
container.config.set("bot.admin_token", "your_admin_token")
```

### 2. Получение зависимостей

```python
# Получение storage (Singleton — создается один раз)
storage = container.storage()

# Получение command_registry
registry = container.command_registry()

# Получение command_executor
executor = container.command_executor()
```

### 3. Использование в боте

```python
# Создание бота с зависимостями из контейнера
bot = EasyBuildBot(
    storage=storage,
    command_registry=registry,
    command_executor=executor,
    admin_token=admin_token
)
```

---

## Структура Container

```python
class Container(containers.DeclarativeContainer):
    """DI Container для зависимостей приложения."""
    
    # Конфигурация
    config = providers.Configuration()
    
    # Storage (Singleton)
    storage = providers.Singleton(
        Storage,
        dir_path=config.database.dir_path,
        db_name=config.database.db_name,
    )
    
    # Legacy: Command matcher
    command_matcher = providers.Singleton(
        CommandMatcher,
        model_name=config.command_matcher.model_name,
        threshold=config.command_matcher.threshold,
    )
    
    # New: Command system
    command_system = providers.Singleton(
        create_command_system,
        storage=storage,
        admin_token=config.bot.admin_token,
        model_name=config.command_matcher.model_name,
        threshold=config.command_matcher.threshold,
    )
    
    # Extract registry and executor
    command_registry = providers.Callable(
        lambda system: system[0],
        system=command_system
    )
    
    command_executor = providers.Callable(
        lambda system: system[1],
        system=command_system
    )
```

---

## Как добавить новую зависимость

### Шаг 1: Добавить в Container

```python
# В файле di.py
class Container(containers.DeclarativeContainer):
    # ... существующие провайдеры ...
    
    # Новая зависимость
    my_service = providers.Singleton(
        MyService,
        some_param=config.my_service.param,
    )
```

### Шаг 2: Настроить конфигурацию

```python
# В main.py
container.config.set("my_service.param", "value")
```

### Шаг 3: Использовать

```python
# Получение из контейнера
my_service = container.my_service()

# Передача в бота или другие сервисы
bot = EasyBuildBot(..., my_service=my_service)
```

---

## Паттерны использования

### Singleton (создается один раз)

```python
storage = providers.Singleton(
    Storage,
    dir_path=config.database.dir_path,
)
```

**Когда использовать:** для сервисов, которые должны быть единственными в приложении (storage, кеши, connection pools)

### Factory (создается каждый раз)

```python
worker = providers.Factory(
    Worker,
    storage=storage,
)
```

**Когда использовать:** для объектов, которые создаются многократно

### Callable (вызов функции)

```python
result = providers.Callable(
    my_function,
    param1=value1,
)
```

**Когда использовать:** для вызова функций или извлечения значений

---

## Конфигурация через environment variables

```python
import os

# Метод 1: Прямая установка
container.config.set("database.dir_path", os.getenv("DB_PATH", "./data"))

# Метод 2: Из словаря
config_dict = {
    "database": {
        "dir_path": os.getenv("DB_PATH", "./data"),
        "db_name": os.getenv("DB_NAME", "bot.db"),
    },
    "bot": {
        "admin_token": os.getenv("ADMIN_TOKEN"),
    }
}

for section, values in config_dict.items():
    for key, value in values.items():
        container.config.set(f"{section}.{key}", value)

# Метод 3: Из YAML файла
container.config.from_yaml("config.yaml")
```

---

## Пример конфигурационного файла (config.yaml)

```yaml
database:
  dir_path: "./data/monty"
  db_name: "easybuild_bot"

command_matcher:
  model_name: "cointegrated/rubert-tiny"
  threshold: 0.5

bot:
  admin_token: "${ADMIN_TOKEN}"  # Из environment variable
```

Использование:
```python
container = Container()
container.config.from_yaml("config.yaml")
```

---

## Тестирование с DI Container

```python
import pytest
from src.easybuild_bot.di import Container

@pytest.fixture
def container():
    """Fixture для создания тестового контейнера."""
    container = Container()
    
    # Тестовая конфигурация
    container.config.set("database.dir_path", ":memory:")
    container.config.set("database.db_name", "test_db")
    container.config.set("command_matcher.threshold", 0.3)
    container.config.set("bot.admin_token", "test_token")
    
    return container

def test_storage(container):
    """Тест storage из контейнера."""
    storage = container.storage()
    
    # Проверяем что storage работает
    assert storage is not None
    
    # Проверяем что это Singleton
    storage2 = container.storage()
    assert storage is storage2

def test_command_system(container):
    """Тест command system из контейнера."""
    registry = container.command_registry()
    executor = container.command_executor()
    
    assert registry is not None
    assert executor is not None
    
    # Проверяем что команды зарегистрированы
    commands = registry.get_all_commands()
    assert len(commands) > 0
```

---

## Переопределение зависимостей для тестирования

```python
from unittest.mock import Mock

# Создание контейнера
container = Container()

# Переопределение storage на mock
mock_storage = Mock()
container.storage.override(mock_storage)

# Теперь все, кто запрашивает storage, получат mock
storage = container.storage()
assert storage is mock_storage

# Сброс переопределения
container.storage.reset_override()
```

---

## Полный пример использования

```python
import os
import logging
from dotenv import load_dotenv
from src.easybuild_bot.di import Container
from src.easybuild_bot.bot import EasyBuildBot

def main():
    # Загрузка переменных окружения
    load_dotenv()
    
    # Создание и конфигурация контейнера
    container = Container()
    container.config.set("database.dir_path", os.getenv("DB_PATH", "./data/monty"))
    container.config.set("database.db_name", os.getenv("DB_NAME", "easybuild_bot"))
    container.config.set("command_matcher.model_name", "cointegrated/rubert-tiny")
    container.config.set("command_matcher.threshold", 0.5)
    container.config.set("bot.admin_token", os.getenv("ADMIN_TOKEN"))
    
    # Получение зависимостей
    storage = container.storage()
    registry = container.command_registry()
    executor = container.command_executor()
    
    # Создание бота
    bot = EasyBuildBot(
        storage=storage,
        command_registry=registry,
        command_executor=executor,
        admin_token=os.getenv("ADMIN_TOKEN")
    )
    
    # Запуск бота
    logging.info("Bot started successfully!")
    # ...

if __name__ == "__main__":
    main()
```

---

## Debugging

### Проверка конфигурации

```python
# Вывод всей конфигурации
print(dict(container.config))

# Вывод конкретного значения
print(container.config.database.dir_path())
```

### Проверка провайдеров

```python
# Проверка что провайдер работает
try:
    storage = container.storage()
    print(f"Storage created: {storage}")
except Exception as e:
    print(f"Error creating storage: {e}")
```

---

## Частые проблемы и решения

### Проблема: "Provider returns None"

**Причина:** Не установлена конфигурация

**Решение:**
```python
# Убедитесь что все required параметры настроены
container.config.set("database.dir_path", "./data")
container.config.set("database.db_name", "bot.db")
```

### Проблема: "Circular dependency"

**Причина:** Два провайдера зависят друг от друга

**Решение:** Используйте паттерн Lazy Injection или рефакторинг зависимостей

### Проблема: "Provider called multiple times"

**Причина:** Используется Factory вместо Singleton

**Решение:**
```python
# Замените Factory на Singleton
storage = providers.Singleton(Storage, ...)  # ← не Factory
```

---

## Дополнительные ресурсы

- [Dependency Injector Documentation](https://python-dependency-injector.ets-labs.org/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Dependency Injection Pattern](https://en.wikipedia.org/wiki/Dependency_injection)

---

## Заключение

DI Container делает код:
- ✅ Более тестируемым
- ✅ Более модульным
- ✅ Более поддерживаемым
- ✅ Более гибким

Используйте его для всех крупных зависимостей в вашем приложении!

