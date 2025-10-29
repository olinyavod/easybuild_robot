# Исправление ошибки клонирования репозитория

## Дата: 29 октября 2025

## Проблема

При выполнении команды сборки проекта возникала ошибка:
```
❌ Ошибка при клонировании: [Errno 2] No such file or directory: ''
```

## Причина

В базе данных `local_repo_path` хранился как **относительный путь** (например: `"checklist_app"`, `"TechnouprApp.Client"`).

Когда код пытался создать родительскую директорию для клонирования:
1. `os.path.dirname("checklist_app")` возвращал пустую строку `""`
2. `os.makedirs("")` вызывал ошибку `[Errno 2] No such file or directory: ''`

## Решение

### 1. Исправлен `storage.py`
- Добавлен импорт `os`
- В методе `_doc_to_project()` добавлена нормализация пути:
  - Относительные пути автоматически преобразуются в абсолютные с помощью `os.path.abspath()`
  - Это происходит один раз при загрузке проекта из базы данных

```python
# Get local_repo_path and ensure it's absolute
local_repo_path = str(doc.get("local_repo_path", ""))
if local_repo_path and not os.path.isabs(local_repo_path):
    # Convert relative path to absolute
    local_repo_path = os.path.abspath(local_repo_path)
```

### 2. Исправлен `project_select_callback.py`
- Улучшена обработка создания родительской директории:
  - Добавлена проверка `if parent_dir:` перед `os.makedirs()`
  - Использование переменной `repo_path` вместо прямого обращения к `project.local_repo_path`
  - Все git-команды теперь используют нормализованный путь

```python
# Create parent directory if it doesn't exist
parent_dir = os.path.dirname(repo_path)
if parent_dir:  # Only create if parent_dir is not empty
    os.makedirs(parent_dir, exist_ok=True)
```

## Преимущества решения

1. **Централизованная нормализация**: Путь нормализуется один раз при загрузке из БД
2. **Совместимость**: Работает как с относительными, так и с абсолютными путями
3. **Безопасность**: Предотвращает ошибки с пустыми путями
4. **Универсальность**: Исправление работает для всех билдеров (Flutter, .NET MAUI, Xamarin)

## Измененные файлы

- `python/src/easybuild_bot/storage.py`
  - Добавлен импорт `os`
  - Обновлен метод `_doc_to_project()`

- `python/src/easybuild_bot/commands/implementations/project_select_callback.py`
  - Улучшена обработка путей при клонировании
  - Добавлена проверка родительской директории
  - Использование нормализованного пути во всех git-операциях

## Тестирование

После применения исправлений:
- Относительные пути (`"checklist_app"`) преобразуются в абсолютные (например: `"/home/olinyavod/projects/easybuild_bot/checklist_app"`)
- Родительские директории создаются корректно
- Клонирование репозитория выполняется успешно
- Все git-операции (checkout, pull, fetch) работают корректно

## Совместимость

Исправление обратно совместимо:
- Проекты с абсолютными путями продолжают работать как раньше
- Проекты с относительными путями теперь работают корректно
- Не требуется миграция базы данных

