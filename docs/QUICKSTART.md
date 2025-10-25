# Быстрый старт: Паттерн Command

## Запуск бота с новой архитектурой

```bash
# Установка зависимостей (если нужно)
pip install python-telegram-bot sentence-transformers torch

# Экспорт переменных окружения
export BOT_TOKEN="your_bot_token"
export ADMIN_TOKEN="your_admin_token"
export DB_PATH="./data"
export DB_NAME="bot.db"

# Запуск бота с новой архитектурой
python python/main_v2.py
```

## Добавление новой команды за 3 шага

### Шаг 1: Создать файл команды

`commands/implementations/weather_command.py`:

```python
from typing import List, Optional
from ..base import Command, CommandContext, CommandResult

class WeatherCommand(Command):
    """Показать погоду."""
    
    def get_command_name(self) -> str:
        return "/weather"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "погода",
            "какая погода",
            "прогноз погоды",
            "температура"
        ]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        # Доступно всем пользователям
        return await self._check_user_access(ctx.update, require_admin=False)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Выполнить команду."""
        message = "🌤️ Погода сегодня: +20°C, солнечно"
        await ctx.update.effective_message.reply_text(message)
        return CommandResult(success=True, message=message)
```

### Шаг 2: Добавить импорт

`commands/implementations/__init__.py`:

```python
from .weather_command import WeatherCommand  # ← Добавить

__all__ = [
    # ...
    'WeatherCommand'  # ← Добавить
]
```

### Шаг 3: Зарегистрировать в фабрике

`commands/factory.py`:

```python
from .implementations import (
    # ...
    WeatherCommand  # ← Добавить
)

def create_command_system(...):
    commands = [
        # ...
        WeatherCommand(storage, admin_token),  # ← Добавить
    ]
```

**Готово!** 🎉

Теперь бот понимает команды:
- "/weather"
- "погода"
- "какая погода"
- "прогноз погоды"

## Команда с параметрами

```python
class GreetCommand(Command):
    """Поприветствовать пользователя."""
    
    def get_command_name(self) -> str:
        return "/greet"
    
    def get_semantic_tags(self) -> List[str]:
        return ["поприветствовать", "передать привет", "скажи привет"]
    
    def get_parameter_patterns(self) -> Dict[str, List[str]]:
        # Извлечение имени из фразы
        return {
            "name": [
                r"(?:поприветствовать|привет|скажи привет)\s+([А-Яа-яЁё]+)",
            ]
        }
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        return await self._check_user_access(ctx.update, require_admin=False)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        name = ctx.params.get("name", "друг")
        message = f"Привет, {name}! 👋"
        await ctx.update.effective_message.reply_text(message)
        return CommandResult(success=True, message=message)
```

Использование:
- "Поприветствовать Олега" → "Привет, Олег! 👋"
- "Скажи привет Марине" → "Привет, Марина! 👋"

## Админ-команда

```python
class DeleteUserCommand(Command):
    """Удалить пользователя (только для админов)."""
    
    def get_command_name(self) -> str:
        return "/delete_user"
    
    def get_semantic_tags(self) -> List[str]:
        return ["удалить пользователя", "удалить юзера"]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        # ← Требуется админ-доступ
        return await self._check_user_access(ctx.update, require_admin=True)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        # Логика удаления пользователя
        message = "✅ Пользователь удален"
        await ctx.update.effective_message.reply_text(message)
        return CommandResult(success=True, message=message)
```

## Тестирование

```bash
# Запустить все тесты
pytest python/tests/test_command_pattern.py -v

# Запустить конкретный тест
pytest python/tests/test_command_pattern.py::TestCommand::test_execute_success -v
```

## Структура проекта

```
easybuild_bot/
├── commands/                      ← Новая система команд
│   ├── __init__.py
│   ├── base.py                    ← Базовый класс Command
│   ├── registry.py                ← Реестр команд
│   ├── executor.py                ← Исполнитель
│   ├── factory.py                 ← Фабрика
│   └── implementations/           ← Реализации команд
│       ├── start_command.py
│       ├── help_command.py
│       └── ...
├── bot.py                         ← Старая версия (для совместимости)
├── bot_v2.py                      ← Новая версия с Command Pattern
├── di.py                          ← DI контейнер (обновлен)
└── ...

tests/
└── test_command_pattern.py        ← Тесты

main.py                            ← Старый запуск
main_v2.py                         ← Новый запуск с Command Pattern

COMMAND_PATTERN_GUIDE.md          ← Подробное руководство
COMMAND_PATTERN_SUMMARY.md        ← Резюме изменений
ARCHITECTURE.md                    ← Диаграммы архитектуры
QUICKSTART.md                      ← Этот файл
```

## Миграция с старой версии

Старая и новая версии могут работать параллельно:

```python
# Старая версия (bot.py)
from easybuild_bot.bot import EasyBuildBot
from easybuild_bot.command_matcher import CommandMatcher

matcher = CommandMatcher()
bot = EasyBuildBot(storage, matcher, admin_token)

# Новая версия (bot_v2.py)
from easybuild_bot.bot_v2 import EasyBuildBotV2
from easybuild_bot.commands import create_command_system

registry, executor = create_command_system(storage, admin_token)
bot = EasyBuildBotV2(storage, registry, executor, admin_token)
```

Рекомендуется постепенная миграция:
1. Запустите новую версию параллельно
2. Протестируйте все команды
3. Убедитесь в корректной работе
4. Переключитесь полностью на новую версию

## Поддержка

Документация:
- `COMMAND_PATTERN_GUIDE.md` - полное руководство
- `ARCHITECTURE.md` - архитектурные диаграммы
- `COMMAND_PATTERN_SUMMARY.md` - резюме изменений

