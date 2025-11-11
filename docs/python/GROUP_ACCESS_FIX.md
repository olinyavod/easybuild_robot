# Исправление проблемы доступа к проектам из групп

## Дата: 9 ноября 2025

## Описание проблемы

При вызове команды `/build` из группы, после выбора проекта сборка не начиналась, даже если команда выполнялась из разрешённых групп для проекта.

## Причина

Callback команды `ProjectSelectCallbackCommand` и `PrepareReleaseCallbackCommand` проверяли только общий доступ пользователя к боту (`_check_user_access`), но НЕ проверяли, разрешен ли выбранный проект для группы, из которой пришел callback.

### Последовательность событий (до исправления)

1. Пользователь вызывает `/build` из группы
2. `BuildCommand` корректно показывает только проекты, доступные для этой группы (`get_projects_for_group`)
3. Пользователь нажимает на проект
4. `ProjectSelectCallbackCommand.can_execute()` проверяет только доступ пользователя к боту
5. ❌ Отсутствует проверка: разрешен ли проект для группы

Это позволяло пользователю обойти ограничения, если он знал ID проекта.

## Решение

Добавлена проверка доступа к проекту в методы `can_execute` обоих callback команд:

### 1. ProjectSelectCallbackCommand

**Файл:** `python/src/easybuild_bot/commands/implementations/project_select_callback.py`

**Изменения:**
```python
async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
    """Check if user has access and if project is allowed for the group."""
    # First check user access
    has_access, error_msg = await self._check_user_access(ctx.update, require_admin=False)
    if not has_access:
        return has_access, error_msg
    
    # Check if project is allowed for the group (if called from group)
    query = ctx.update.callback_query
    if query and query.data:
        # Extract project ID from callback data
        parts = query.data.split(":", 1)
        if len(parts) == 2:
            project_id = parts[1]
            project = self.storage.get_project_by_id(project_id)
            
            # Check if called from group
            chat = ctx.update.effective_chat
            if chat and chat.type in ("group", "supergroup"):
                # Verify project is allowed for this group
                if project and chat.id not in project.allowed_group_ids:
                    return False, "Этот проект недоступен для данной группы"
    
    return True, None
```

### 2. PrepareReleaseCallbackCommand

**Файл:** `python/src/easybuild_bot/commands/implementations/prepare_release_callback.py`

Добавлена аналогичная проверка.

## Принцип работы

Теперь callback команды:

1. ✅ Проверяют доступ пользователя к боту
2. ✅ Извлекают ID проекта из callback data
3. ✅ Проверяют тип чата (group/supergroup)
4. ✅ Если вызов из группы - проверяют, что `chat.id` есть в `project.allowed_group_ids`
5. ✅ Возвращают ошибку с понятным сообщением, если доступ запрещен

## Тестирование

Для проверки исправления:

1. Создайте проект с доступом только для определенной группы
2. В этой группе: `/build` → выберите проект → ✅ сборка должна начаться
3. В другой группе (где проект недоступен): `/build` → проект не должен отображаться
4. Если пользователь каким-то образом отправит callback с ID недоступного проекта:
   - ❌ Появится alert: "Этот проект недоступен для данной группы"
   - Сборка не начнется

## Затронутые файлы

- `python/src/easybuild_bot/commands/implementations/project_select_callback.py`
- `python/src/easybuild_bot/commands/implementations/prepare_release_callback.py`

## Следование принципам SOLID

- **Single Responsibility:** Каждый метод отвечает за одну проверку
- **Open/Closed:** Расширили функциональность без изменения базовой логики
- **Liskov Substitution:** Callback команды остаются совместимыми с базовым классом
- **Interface Segregation:** Не добавлены лишние зависимости
- **Dependency Inversion:** Используем существующую абстракцию `can_execute`

## Безопасность

Исправление предотвращает:
- Обход ограничений доступа к проектам
- Несанкционированный запуск сборок
- Доступ к проектам из неразрешенных групп





