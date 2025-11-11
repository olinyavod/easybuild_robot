# Уровни доступа команд

## Обзор

Система команд теперь использует декларативный подход к управлению доступом через enum `CommandAccessLevel`.
Это позволяет избежать дублирования проверок доступа в методе `can_execute()` каждой команды.

## Три уровня доступа

### 1. PUBLIC (Публичный)
- **Описание**: Любой пользователь в любом чате может выполнить команду
- **Использование**: Команды, которые не требуют авторизации (пока не используются в боте)
- **Пример**: Информационные команды, помощь без авторизации

```python
def get_access_level(self) -> CommandAccessLevel:
    """Команда доступна всем без ограничений."""
    return CommandAccessLevel.PUBLIC
```

### 2. USER (Пользовательский)
- **Описание**: Команда видна в группе и личном чате, доступна только если у пользователя есть разрешение
- **Проверка**: Пользователь должен быть авторизован (`user.allowed = True`) или быть администратором
- **Использование**: Основные команды бота для авторизованных пользователей
- **Примеры**: `/start`, `/help`, `/build`, `/release`, `/projects`

```python
def get_access_level(self) -> CommandAccessLevel:
    """Команда доступна любому авторизованному пользователю."""
    return CommandAccessLevel.USER
```

### 3. ADMIN (Администраторский)
- **Описание**: Доступна только админу и только в личном чате с ботом
- **Проверка**: 
  1. Чат должен быть личным (не группа)
  2. Пользователь должен быть администратором (`user.is_admin = True`)
- **Использование**: Команды управления системой
- **Примеры**: `/add_project`, `/edit_project`, `/delete_project`, `/users`, `/block_user`, `/unblock_user`, `/groups`

```python
def get_access_level(self) -> CommandAccessLevel:
    """Команда доступна только админу в личном чате."""
    return CommandAccessLevel.ADMIN
```

## Реализация

### Базовый класс Command

Централизованная проверка доступа реализована в методе `can_execute()` базового класса `Command`:

```python
async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
    """
    Check if command can be executed in current context.
    
    This method implements centralized access control based on command's access level.
    Commands should NOT override this method unless they need custom access logic.
    """
    access_level = self.get_access_level()
    
    # PUBLIC: Любой пользователь в любом чате
    if access_level == CommandAccessLevel.PUBLIC:
        return True, None
    
    # ADMIN: Только админ в личном чате
    if access_level == CommandAccessLevel.ADMIN:
        # Проверка, что это личный чат
        chat = ctx.update.effective_chat
        if chat and chat.type not in ("private",):
            return False, "Эта команда доступна только в личном чате с ботом"
        
        # Проверка прав администратора
        return await self._check_user_access(ctx.update, require_admin=True)
    
    # USER: Требуется разрешение на доступ к боту
    if access_level == CommandAccessLevel.USER:
        return await self._check_user_access(ctx.update, require_admin=False)
    
    # Неизвестный уровень доступа
    return False, "Неизвестный уровень доступа команды"
```

### Переопределение can_execute для специальной логики

Некоторые команды требуют дополнительной логики проверки доступа. В таких случаях они могут переопределить `can_execute()`:

#### Пример 1: RegisterGroupCommand (работает только в группах)

```python
class RegisterGroupCommand(Command):
    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна авторизованным пользователям."""
        return CommandAccessLevel.USER
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """
        Переопределяем стандартную проверку доступа.
        Нужна дополнительная проверка, что команда выполняется в группе.
        """
        # Сначала базовая проверка доступа
        has_access, error_msg = await super().can_execute(ctx)
        
        if not has_access:
            return False, error_msg
        
        # Проверка, что команда в группе
        chat = ctx.update.effective_chat
        if not chat or chat.id > 0:
            return False, "Эта команда работает только в группах."
        
        return True, None
```

#### Пример 2: ProjectSelectCallbackCommand (проверка разрешений на проект)

```python
class ProjectSelectCallbackCommand(CallbackCommand):
    def get_access_level(self) -> CommandAccessLevel:
        """Callback доступен авторизованным пользователям."""
        return CommandAccessLevel.USER
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """
        Переопределяем стандартную проверку доступа.
        Нужна дополнительная проверка, что проект разрешен для группы.
        """
        # Сначала базовая проверка доступа
        has_access, error_msg = await super().can_execute(ctx)
        
        if not has_access:
            return False, error_msg
        
        # Проверка разрешений на проект для группы
        query = ctx.update.callback_query
        if query and query.data:
            parts = query.data.split(":", 1)
            if len(parts) == 2:
                project_id = parts[1]
                project = self.storage.get_project_by_id(project_id)
                
                # Проверка, что вызвано из группы
                chat = ctx.update.effective_chat
                if chat and chat.type in ("group", "supergroup"):
                    # Проверка, что проект разрешен для этой группы
                    if project and chat.id not in project.allowed_group_ids:
                        return False, "Этот проект недоступен для данной группы"
        
        return True, None
```

## Миграция существующих команд

Все существующие команды были обновлены:

### Пользовательские команды (USER)
- StartCommand - `/start`
- HelpCommand - `/help`
- BuildCommand - `/build`
- ReleaseCommand - `/release`
- VersionCommand - `/version`
- ProjectsCommand - `/projects`
- RegisterGroupCommand - `/register_group` (с дополнительной проверкой)

### Админские команды (ADMIN)
- AddProjectCommand - `/add_project`
- EditProjectCommand - `/edit_project`
- DeleteProjectCommand - `/delete_project`
- BlockUserCommand - `/block_user`
- UnblockUserCommand - `/unblock_user`
- UsersCommand - `/users`
- GroupsCommand - `/groups`

### Callback команды

#### Пользовательские (USER)
- BuildApkCallbackCommand
- ProjectSelectCallbackCommand (с дополнительной проверкой на проект)
- PrepareReleaseCallbackCommand (с дополнительной проверкой на проект)
- ReleaseProjectCallbackCommand (с дополнительной проверкой на проект)

#### Админские (ADMIN)
- AllowUserCallbackCommand
- BlockUserCallbackCommand
- UnblockUserCallbackCommand

## Преимущества нового подхода

1. **Устранение дублирования**: Проверка доступа централизована в базовом классе
2. **Декларативность**: Уровень доступа команды явно указывается через `get_access_level()`
3. **Простота**: Большинство команд не нуждаются в переопределении `can_execute()`
4. **Гибкость**: Команды с особой логикой могут переопределить `can_execute()`, вызвав `super().can_execute()`
5. **Читаемость**: Сразу видно, какой уровень доступа требуется для команды
6. **Соответствие SOLID**: Следование принципам единственной ответственности и открытости/закрытости

## Примеры использования

### Создание новой пользовательской команды

```python
from typing import List
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel


class MyCommand(Command):
    """My custom user command."""
    
    def get_command_name(self) -> str:
        return "/mycommand"
    
    def get_semantic_tags(self) -> List[str]:
        return ["моя команда", "выполнить действие"]
    
    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна любому авторизованному пользователю."""
        return CommandAccessLevel.USER
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute command logic."""
        # Ваша логика здесь
        await ctx.update.effective_message.reply_text("Команда выполнена!")
        return CommandResult(success=True, message="Done")
```

### Создание новой админской команды

```python
from typing import List
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel


class AdminCommand(Command):
    """Admin only command."""
    
    def get_command_name(self) -> str:
        return "/admincommand"
    
    def get_semantic_tags(self) -> List[str]:
        return ["административная команда"]
    
    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна только админу в личном чате."""
        return CommandAccessLevel.ADMIN
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute admin command logic."""
        # Ваша логика здесь
        await ctx.update.effective_message.reply_text("Админская команда выполнена!")
        return CommandResult(success=True, message="Done")
```

## Заключение

Новая система уровней доступа делает код команд более чистым, устраняет дублирование и следует принципам SOLID и KISS. 
Она также упрощает добавление новых команд, так как не требует написания одинакового кода проверки доступа в каждой команде.





