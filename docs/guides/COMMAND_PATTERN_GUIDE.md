# Пример использования паттерна Command

Этот документ показывает, как работает новая архитектура на основе паттерна Command.

## Преимущества новой архитектуры

### 1. **Инкапсуляция логики команды**
Каждая команда — это отдельный класс со всей своей логикой:
- Проверка прав доступа (`can_execute`)
- Логика выполнения (`execute`)
- Семантические теги для распознавания (`get_semantic_tags`)
- Паттерны для извлечения параметров (`get_parameter_patterns`)

```python
class StartCommand(Command):
    def get_command_name(self) -> str:
        return "/start"
    
    def get_semantic_tags(self) -> List[str]:
        return ["начать", "привет", "старт"]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        return await self._check_user_access(ctx.update, require_admin=False)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        user = ctx.update.effective_user
        message = f"Привет, {user.full_name}!"
        await ctx.update.effective_message.reply_text(message)
        return CommandResult(success=True, message=message)
```

### 2. **Масштабируемость**
Добавление новой команды требует только:
1. Создать класс команды
2. Зарегистрировать в фабрике

Не нужно модифицировать огромные `if/elif` блоки!

### 3. **Упрощение основного кода бота**
Было (в `bot.py`):
```python
async def msg_echo(self, update, context):
    # ... множество проверок ...
    match_result = self.command_matcher.match_command(text)
    if match_result:
        command, similarity, params = match_result
        # Огромный if/elif блок:
        if command == "/start":
            await self.cmd_start(update, context)
        elif command == "/help":
            await self.cmd_help(update, context)
        elif command == "/build":
            await self.cmd_build(update, context)
        # ... еще 10+ команд ...
```

Стало (в `bot_v2.py`):
```python
async def msg_echo(self, update, context):
    # ... проверки ...
    cmd_ctx = CommandContext(update=update, context=context, params={}, user_text=text)
    result = await self.command_executor.match_and_execute(text, cmd_ctx)
    if not result:
        await message.reply_text("Извините, я не понимаю...")
```

### 4. **Единообразная обработка**
Все команды обрабатываются единообразно через `CommandExecutor`, который:
- Проверяет права доступа
- Выполняет команду
- Обрабатывает ошибки
- Логирует действия

## Как добавить новую команду

### Шаг 1: Создать класс команды

```python
# В файле: commands/implementations/my_command.py

from typing import List, Optional
from ..base import Command, CommandContext, CommandResult

class MyCommand(Command):
    """Описание вашей команды."""
    
    def get_command_name(self) -> str:
        return "/mycommand"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "моя команда",
            "выполнить действие",
            "сделать что-то"
        ]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        # Для обычных пользователей:
        return await self._check_user_access(ctx.update, require_admin=False)
        
        # Для админов:
        # return await self._check_user_access(ctx.update, require_admin=True)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Логика выполнения команды."""
        # Ваш код здесь
        await ctx.update.effective_message.reply_text("Команда выполнена!")
        return CommandResult(success=True)
```

### Шаг 2: Добавить в фабрику

```python
# В файле: commands/factory.py

from .implementations import (
    # ... существующие команды ...
    MyCommand  # Добавить импорт
)

def create_command_system(...):
    # ...
    commands = [
        # ... существующие команды ...
        MyCommand(storage, admin_token),  # Добавить в список
    ]
```

### Шаг 3: (Опционально) Добавить обработчик в `bot_v2.py`

```python
# Только если нужна команда /mycommand (не семантическая)
async def cmd_mycommand(self, update, context):
    await self._execute_command_by_name("/mycommand", update, context)

# И в setup_handlers:
app.add_handler(CommandHandler("mycommand", self.cmd_mycommand))
```

## Пример команды с параметрами

```python
class GreetUserCommand(Command):
    """Команда для приветствия пользователя по имени."""
    
    def get_command_name(self) -> str:
        return "/greet"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "поприветствовать",
            "передать привет",
            "скажи привет"
        ]
    
    def get_parameter_patterns(self) -> Dict[str, List[str]]:
        return {
            "user_name": [
                r"(?:поприветствовать|передать привет|скажи привет)\s+([А-Яа-яЁё]+)",
                r"привет\s+для\s+([А-Яа-яЁё]+)"
            ]
        }
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        return await self._check_user_access(ctx.update, require_admin=False)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        user_name = ctx.params.get("user_name")
        if not user_name:
            message = "Укажите имя пользователя!"
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=False, error=message)
        
        message = f"Привет, {user_name}! 👋"
        await ctx.update.effective_message.reply_text(message)
        return CommandResult(success=True, message=message)
```

Использование:
- "Поприветствовать Олега" → "Привет, Олег! 👋"
- "Скажи привет Марине" → "Привет, Марина! 👋"

## Структура файлов

```
commands/
├── __init__.py           # Экспорт публичных классов
├── base.py               # Базовый класс Command
├── registry.py           # CommandRegistry для регистрации и поиска
├── executor.py           # CommandExecutor для выполнения
├── factory.py            # Фабрика для создания системы команд
└── implementations/      # Реализации конкретных команд
    ├── __init__.py
    ├── start_command.py
    ├── help_command.py
    ├── build_command.py
    ├── users_command.py
    ├── groups_command.py
    ├── register_group_command.py
    ├── unblock_user_command.py
    └── block_user_command.py
```

## Использование в main.py

```python
from easybuild_bot.di import Container
from easybuild_bot.bot_v2 import EasyBuildBotV2, post_init

# Настройка DI
container = Container()
container.config.from_yaml('config.yaml')

# Получение зависимостей
storage = container.storage()
registry = container.command_registry()
executor = container.command_executor()

# Создание бота с новой архитектурой
bot = EasyBuildBotV2(
    storage=storage,
    command_registry=registry,
    command_executor=executor,
    admin_token=config['bot']['admin_token']
)

# Настройка приложения
app = ApplicationBuilder().token(token).post_init(post_init).build()
bot.setup_handlers(app)
app.run_polling()
```

