# Исправление: AttributeError в edit_project при работе с группами

## Дата: 9 ноября 2025

## Описание проблемы

После добавления функционала выбора групп через кнопки команда `/edit_project` падала с ошибкой при попытке отобразить меню редактирования:

```
AttributeError: 'BotGroup' object has no attribute 'name'
```

## Причина

В нескольких местах кода использовался неправильный атрибут для объекта `BotGroup`:

```python
# ❌ НЕПРАВИЛЬНО
group.name  # У BotGroup нет атрибута 'name'
```

Правильное название атрибута в модели `BotGroup`:

```python
@dataclass
class BotGroup:
    id: str
    group_id: int
    group_name: str  # ← Правильное название атрибута
```

## Затронутые места

### 1. Функция `format_value` (строка 55)

**До:**
```python
return group.name or f"Группа {value[0]}"
```

**После:**
```python
return group.group_name or f"Группа {value[0]}"
```

### 2. Метод `show_group_selection` (строка 348 и 364)

**До:**
```python
button_text = f"{prefix}{group.name or f'Группа {group.group_id}'}"
# ...
current_value_text = escape_md(group.name or f"Группа {group.group_id}")
```

**После:**
```python
button_text = f"{prefix}{group.group_name or f'Группа {group.group_id}'}"
# ...
current_value_text = escape_md(group.group_name or f"Группа {group.group_id}")
```

### 3. Метод `handle_group_selection` (строка 405)

**До:**
```python
group_name = group.name if group else f"ID: {new_value[0]}"
```

**После:**
```python
group_name = group.group_name if group else f"ID: {new_value[0]}"
```

## Решение

Заменены все использования `group.name` на `group.group_name` в файле `edit_project_wizard.py`.

## Затронутые файлы

- `python/src/easybuild_bot/handlers/edit_project_wizard.py`

## Тестирование

После исправления:
1. ✅ `/edit_project` → Показывается список проектов
2. ✅ Выбор проекта → Меню редактирования отображается корректно
3. ✅ Выбор поля "Группы" → Названия групп отображаются правильно
4. ✅ Выбор группы → Подтверждение с правильным названием
5. ✅ Сохранение → Успешно сохраняется с правильным названием группы

## Стектрейс ошибки

```
Traceback (most recent call last):
  File ".../telegram/ext/_application.py", line 1335, in process_update
    await coroutine
  File ".../telegram/ext/_handlers/conversationhandler.py", line 857, in handle_update
    new_state: object = await handler.handle_update(
  File ".../telegram/ext/_handlers/basehandler.py", line 158, in handle_update
    return await self.callback(update, context)
  File ".../handlers/edit_project_wizard.py", line 188, in select_project
    return await self.show_field_menu_new_message(update, context)
  File ".../handlers/edit_project_wizard.py", line 217, in show_field_menu_new_message
    msg, keyboard = self._build_field_menu_content(project)
  File ".../handlers/edit_project_wizard.py", line 259, in _build_field_menu_content
    formatted_value = format_value(field_name, value, self.storage)
  File ".../handlers/edit_project_wizard.py", line 55, in format_value
    return group.name or f"Группа {value[0]}"
           ^^^^^^^^^^
AttributeError: 'BotGroup' object has no attribute 'name'
```

## Уроки

При работе с dataclass моделями:
- Всегда проверять правильность названий атрибутов
- Использовать IDE с автодополнением для избежания опечаток
- Добавить type hints для лучшей проверки типов
- Писать unit-тесты для проверки работы с моделями

## Тип проблемы

- Категория: **Багфикс**
- Серьёзность: **Критическая** (команда не работала)
- Затронутая функциональность: Редактирование проектов, отображение групп

## Связанные изменения

Этот багфикс связан с предыдущими изменениями:
- Добавление выбора групп через кнопки в `/edit_project`
- Отображение названий групп вместо ID

## Commit message (пример)

```
fix: исправлен AttributeError при работе с BotGroup

Проблема: использовался неправильный атрибут group.name вместо group.group_name
Затронуто: format_value, show_group_selection, handle_group_selection
Результат: команда /edit_project теперь корректно отображает группы
```





