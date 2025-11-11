# Исправление: Команда /edit_project перестала работать после выбора проекта

## Дата: 9 ноября 2025

## Описание проблемы

После внесения изменений в логику редактирования групп команда `/edit_project` перестала работать на этапе выбора проекта. После нажатия на проект в списке команда не переходила к меню редактирования полей.

## Причина

В ConversationHandler для `edit_project` оба состояния `SELECT_PROJECT` и `SELECT_FIELD` использовали одинаковый паттерн для обработки callback'ов:

```python
SELECT_PROJECT: [CallbackQueryHandler(..., pattern="^edit_")],
SELECT_FIELD: [CallbackQueryHandler(..., pattern="^edit_")],
```

Это приводило к конфликту, так как callback'и из обоих состояний начинаются с `edit_`:
- SELECT_PROJECT: `edit_select_<project_id>`, `edit_cancel`
- SELECT_FIELD: `edit_field_<field_name>`, `edit_save`, `edit_cancel`

Telegram python-telegram-bot не мог правильно определить, какой обработчик должен обрабатывать callback, что приводило к сбою.

## Решение

Сделаны более **специфичные паттерны** для каждого состояния:

```python
SELECT_PROJECT: [CallbackQueryHandler(..., pattern="^(edit_select_|edit_cancel)")],
SELECT_FIELD: [CallbackQueryHandler(..., pattern="^(edit_field_|edit_save|edit_cancel)")],
SELECT_GROUP: [CallbackQueryHandler(..., pattern="^(select_group_|group_back)")],
```

Теперь каждое состояние обрабатывает только свои специфичные callback'и:
- **SELECT_PROJECT**: `edit_select_*` и `edit_cancel`
- **SELECT_FIELD**: `edit_field_*`, `edit_save`, `edit_cancel`
- **SELECT_GROUP**: `select_group_*`, `group_back`

## Затронутые файлы

- `python/src/easybuild_bot/bot.py` — ConversationHandler для edit_project

## Тестирование

После исправления:
1. ✅ `/edit_project` → Показывается список проектов
2. ✅ Выбор проекта → Переход к меню редактирования полей
3. ✅ Выбор поля → Корректная обработка
4. ✅ Выбор поля "Группы" → Показывается список групп
5. ✅ Выбор группы → Корректное сохранение
6. ✅ Сохранение изменений → Успешно

## Уроки

При работе с ConversationHandler важно:
- Использовать **специфичные паттерны** для каждого состояния
- Избегать перекрытия паттернов между состояниями
- Тестировать все переходы между состояниями после изменений

## Тип проблемы

- Категория: **Багфикс**
- Серьёзность: **Критическая** (команда не работала)
- Затронутая функциональность: Редактирование проектов

## Commit message (пример)

```
fix: исправлен ConversationHandler для /edit_project

Проблема: после выбора проекта команда переставала работать
Причина: конфликт паттернов в SELECT_PROJECT и SELECT_FIELD
Решение: использованы специфичные паттерны для каждого состояния
```





