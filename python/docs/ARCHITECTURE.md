# Архитектура Command Pattern с AccessControlService

## До рефакторинга ❌

```
┌─────────────────────────────────────────────────┐
│              EasyBuildBot                       │
│                                                 │
│  ❌ request_access() - проверка доступа        │
│  ❌ request_admin_access() - проверка админа   │
│  ❌ cb_allow_user() - бизнес-логика            │
│  ❌ cb_block_user() - бизнес-логика            │
│  ❌ cb_unblock_user() - бизнес-логика          │
│  ❌ cb_build_apk_*() - бизнес-логика           │
│  ✅ cmd_start() - делегирование                │
│  ✅ cmd_help() - делегирование                 │
│                                                 │
└─────────────────────────────────────────────────┘
           │                    │
           │                    │
           ▼                    ▼
    ┌──────────┐         ┌──────────┐
    │ Command  │         │ Storage  │
    │          │         │          │
    │ ❌ Дубль-│         │          │
    │   рование│         │          │
    │   логики │         │          │
    └──────────┘         └──────────┘
```

**Проблемы:**
- Дублирование логики проверки доступа
- Бизнес-логика в bot.py
- Нарушение Single Responsibility Principle
- Сложность тестирования

## После рефакторинга ✅

```
┌─────────────────────────────────────────────────┐
│              EasyBuildBot                       │
│         (Роутинг и координация)                 │
│                                                 │
│  ✅ request_access() → делегирует               │
│  ✅ request_admin_access() → делегирует         │
│  ✅ handle_callback_query() → находит команду   │
│  ✅ cmd_*() → делегирование на команды          │
│                                                 │
└─────────────────────────────────────────────────┘
           │           │            │
           │           │            │
           ▼           ▼            ▼
    ┌──────────┐ ┌─────────────┐ ┌────────────┐
    │ Command  │ │   Access    │ │  Storage   │
    │ Registry │ │   Control   │ │            │
    │          │ │   Service   │ │            │
    └──────────┘ └─────────────┘ └────────────┘
           │           │
           │           │
           ▼           ▼
    ┌─────────────────────────────────┐
    │    Command Executor             │
    │                                 │
    │  ✅ Проверяет права доступа     │
    │  ✅ Выполняет команды           │
    │  ✅ Обрабатывает ошибки         │
    └─────────────────────────────────┘
                  │
                  │
                  ▼
    ┌─────────────────────────────────┐
    │         Commands                │
    │                                 │
    │  • StartCommand                 │
    │  • HelpCommand                  │
    │  • BuildCommand                 │
    │  • ...                          │
    │                                 │
    │  Callback Commands:             │
    │  • AllowUserCallbackCommand     │
    │  • BlockUserCallbackCommand     │
    │  • UnblockUserCallbackCommand   │
    │  • BuildApkCallbackCommand      │
    └─────────────────────────────────┘
```

## Поток выполнения callback-запроса

### До рефакторинга ❌
```
User clicks button
      │
      ▼
bot.cb_allow_user()
      │
      ├── Проверка прав ❌ (в bot.py)
      ├── Логика доступа ❌ (в bot.py)
      ├── Работа с БД ❌ (в bot.py)
      └── Ответ пользователю
```

### После рефакторинга ✅
```
User clicks button (allow_user_123)
      │
      ▼
bot.handle_callback_query()
      │
      ├── Поиск команды по паттерну
      │   (allow_user_\d+ → AllowUserCallbackCommand)
      │
      ▼
CommandExecutor.execute_command()
      │
      ├── Проверка прав через AccessControlService ✅
      │
      ▼
AllowUserCallbackCommand.execute()
      │
      ├── Бизнес-логика ✅
      ├── Работа с БД через Storage ✅
      └── Ответ пользователю ✅
```

## Dependency Injection Container

```
Container
  │
  ├── storage: Storage
  │     └── MongoDB/MontyDB connection
  │
  ├── access_control: AccessControlService
  │     └── depends on: storage
  │
  └── command_system: (Registry, Executor)
        │
        ├── CommandRegistry
        │     └── all registered commands
        │
        └── CommandExecutor
              └── depends on: registry

Bot initialization:
  bot = EasyBuildBot(
      storage=container.storage(),
      access_control=container.access_control(),
      command_registry=container.command_registry(),
      command_executor=container.command_executor(),
      ...
  )
```

## Преимущества новой архитектуры

### 1. Единственная ответственность
```
EasyBuildBot      → Только роутинг
AccessControl     → Только проверка доступа
Commands          → Только бизнес-логика
Storage           → Только работа с БД
```

### 2. Нет дублирования
```
До:  bot.py (90 строк) + base.py (40 строк) = 130 строк
После: access_control.py (одно место для всей логики)
```

### 3. Легко расширять
```
Новая callback-команда:
  1. Создать класс наследник CallbackCommand
  2. Добавить в factory.py
  3. Готово! ✅

Не нужно:
  ❌ Менять bot.py
  ❌ Добавлять отдельный handler
  ❌ Дублировать логику проверки прав
```

### 4. Легко тестировать
```python
# Тест команды изолированно
def test_allow_user_callback():
    mock_storage = Mock()
    mock_access = Mock()
    cmd = AllowUserCallbackCommand(mock_storage, mock_access)
    
    # Тест без зависимостей от Telegram API
    result = await cmd.execute(ctx)
    assert result.success
```

## Диаграмма классов

```
        ┌──────────────────┐
        │     Command      │  (Abstract)
        │──────────────────│
        │ + storage        │
        │ + access_control │
        │──────────────────│
        │ + can_execute()  │
        │ + execute()      │
        └──────────────────┘
                 △
                 │
        ┌────────┴────────┐
        │                 │
┌───────────────┐  ┌──────────────────┐
│ StartCommand  │  │ CallbackCommand  │  (Abstract)
│ HelpCommand   │  │──────────────────│
│ BuildCommand  │  │ + get_callback_  │
│ ...           │  │   pattern()      │
└───────────────┘  └──────────────────┘
                           △
                           │
                    ┌──────┴──────┐
                    │             │
        ┌───────────────────┐  ┌────────────────┐
        │ AllowUserCallback │  │ BlockUserCallback│
        │ UnblockUser...    │  │ BuildApk...      │
        └───────────────────┘  └────────────────┘
```

## Взаимодействие компонентов

```
    User                 Bot              CommandExecutor      Command         AccessControl
     │                    │                      │               │                  │
     │───click button────>│                      │               │                  │
     │                    │                      │               │                  │
     │                    │──find command──────>│               │                  │
     │                    │                      │               │                  │
     │                    │                      │──execute()──>│                  │
     │                    │                      │               │                  │
     │                    │                      │               │──check_access──>│
     │                    │                      │               │                  │
     │                    │                      │               │<─has_access─────│
     │                    │                      │               │                  │
     │                    │                      │<─result───────│                  │
     │                    │                      │               │                  │
     │                    │<─────────────────────│               │                  │
     │                    │                      │               │                  │
     │<──response─────────│                      │               │                  │
```

---

**Архитектура:** Command Pattern + Dependency Injection + Service Layer  
**Паттерны:** Command, Factory, Singleton, Strategy  
**Принципы:** SOLID, DRY, Clean Architecture

