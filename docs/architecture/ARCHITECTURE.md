```mermaid
# Архитектура паттерна Command для EasyBuildBot

## Структура классов

┌─────────────────────────────────────────────────────────────────────┐
│                         Command Pattern Architecture                 │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│      <<abstract>>    │
│       Command        │
├──────────────────────┤
│ + get_command_name() │
│ + get_semantic_tags()│
│ + can_execute()      │
│ + execute()          │
│ + get_parameter_     │
│   patterns()         │
└──────────────────────┘
         ▲
         │ implements
         │
    ┌────┴──────────────────────────────────┐
    │                                        │
┌───┴────────────┐                 ┌────────┴────────┐
│ StartCommand   │                 │  BuildCommand   │
├────────────────┤                 ├─────────────────┤
│ + execute()    │  ...и другие    │ + execute()     │
│ + can_execute()│     команды     │ + can_execute() │
└────────────────┘                 └─────────────────┘


┌─────────────────────┐         ┌──────────────────────┐
│  CommandRegistry    │◄────────│  CommandExecutor     │
├─────────────────────┤         ├──────────────────────┤
│ - commands: Dict    │         │ - registry           │
│ - model             │         ├──────────────────────┤
│ - embeddings        │         │ + execute_command()  │
├─────────────────────┤         │ + match_and_execute()│
│ + register()        │         └──────────────────────┘
│ + get_command()     │
│ + match_command()   │
└─────────────────────┘


## Поток выполнения команды

User Message
    │
    ▼
┌─────────────────┐
│ EasyBuildBotV2  │
│   msg_echo()    │
└────────┬────────┘
         │
         │ 1. Создает CommandContext
         ▼
┌──────────────────────┐
│  CommandExecutor     │
│  match_and_execute() │
└─────────┬────────────┘
          │
          │ 2. Ищет команду
          ▼
┌────────────────────┐
│ CommandRegistry    │
│  match_command()   │
└─────────┬──────────┘
          │
          │ 3. Семантическое сопоставление
          │    используя ruBert-tiny
          │
          │ 4. Возвращает: (Command, similarity, params)
          ▼
┌──────────────────────┐
│  CommandExecutor     │
│  execute_command()   │
└─────────┬────────────┘
          │
          │ 5. Проверяет can_execute()
          ▼
┌────────────────┐
│    Command     │
│ can_execute()  │
└────────┬───────┘
         │
         │ 6. Проверка прав доступа
         ▼
┌────────────────┐        ┌──────────────┐
│    Storage     │◄───────│ _check_user_ │
│                │        │   access()   │
└────────────────┘        └──────────────┘
         │
         │ 7. Если доступ разрешен
         ▼
┌────────────────┐
│    Command     │
│   execute()    │
└────────┬───────┘
         │
         │ 8. Выполнение логики
         ▼
┌────────────────┐
│ CommandResult  │
│ (success, msg) │
└────────────────┘


## Добавление новой команды

[1] Создать класс команды
    │
    └─► commands/implementations/my_command.py
        
            class MyCommand(Command):
                def get_command_name() -> str
                def get_semantic_tags() -> List[str]
                def can_execute() -> tuple[bool, Optional[str]]
                def execute() -> CommandResult

[2] Зарегистрировать в фабрике
    │
    └─► commands/factory.py
        
            commands = [
                ...,
                MyCommand(storage, admin_token)
            ]

[3] Готово! ✅
    │
    └─► Команда автоматически:
        • Регистрируется в реестре
        • Получает семантические теги
        • Обрабатывается через executor
        • Проверяется на права доступа


## Сравнение: До и После

### До (старая архитектура):

bot.py (700+ строк)
    ├─ cmd_start()
    ├─ cmd_help()
    ├─ cmd_build()
    ├─ cmd_users()
    ├─ cmd_unblock_user()    ← Много дублирования кода
    ├─ cmd_block_user()      ← для проверки прав доступа
    └─ msg_echo()
        └─ if command == "/start":
               await self.cmd_start()
            elif command == "/help":      ← Растет с каждой
               await self.cmd_help()         новой командой!
            elif command == "/build":
               await self.cmd_build()
            ...

Добавление команды = изменения в 3-4 местах

### После (Command Pattern):

bot_v2.py (500 строк)               commands/
    └─ msg_echo()                      ├─ base.py
        └─ executor.match_and_execute()├─ registry.py
                                       ├─ executor.py
                                       ├─ factory.py
                                       └─ implementations/
                                           ├─ start_command.py
                                           ├─ help_command.py
                                           ├─ build_command.py
                                           └─ ...

Добавление команды = 1 новый файл + 1 строка в фабрике!


## Преимущества

✅ Инкапсуляция      - каждая команда = отдельный класс
✅ Масштабируемость  - легко добавлять новые команды
✅ Тестируемость     - каждую команду можно тестировать отдельно
✅ Читаемость        - код короче и понятнее
✅ Единообразие      - все команды обрабатываются одинаково
✅ Расширяемость     - легко добавить новые возможности

```

