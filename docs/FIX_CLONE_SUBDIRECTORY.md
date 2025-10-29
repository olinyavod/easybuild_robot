# Исправление клонирования репозиториев в подкаталоги

## Дата: 29 октября 2025

## Проблема

Команда `git clone` клонировала репозитории неправильно при указании полного пути. Вместо создания подкаталога, git пытался клонировать напрямую в указанный путь, что приводило к ошибкам.

### Изначальный код:

```python
result = subprocess.run(
    ["git", "clone", "--recurse-submodules", project.git_url, repo_path],
    capture_output=True,
    text=True,
    timeout=300
)
```

**Проблема:** Когда `repo_path` = `/path/to/repos/my_project`, git пытается клонировать содержимое напрямую в этот каталог, а не создать его как подкаталог.

## Решение

Изменён подход к клонированию:

1. Извлекается имя подкаталога из полного пути
2. Клонирование выполняется в родительском каталоге
3. Git автоматически создаёт подкаталог с нужным именем

### Исправленный код:

```python
# Extract the directory name for cloning
repo_name = os.path.basename(repo_path)

# Clone repository with submodules into parent directory
# Git will automatically create a subdirectory with repo_name
result = subprocess.run(
    ["git", "clone", "--recurse-submodules", project.git_url, repo_name],
    cwd=parent_dir,
    capture_output=True,
    text=True,
    timeout=300
)
```

**Результат:** При `repo_path` = `/path/to/repos/my_project`:
- `parent_dir` = `/path/to/repos`
- `repo_name` = `my_project`
- Команда: `git clone <url> my_project` (выполняется в `/path/to/repos`)
- Git создаёт `/path/to/repos/my_project` автоматически ✅

## Изменённые файлы

### 1. `python/src/easybuild_bot/commands/implementations/project_select_callback.py`

**Строки 53-73:**

Изменено клонирование при выборе проекта.

### 2. `python/src/easybuild_bot/commands/implementations/prepare_release_callback.py`

**Строки 78-94:**

Изменено клонирование в процессе подготовки релиза (Шаг 1/8).

## Тестирование

Создан и успешно выполнен тестовый скрипт, подтверждающий правильность работы:

```
✅ Клонирование успешно!
✅ /tmp/tmp9qh1o52f/repos/test_repo существует
✅ .git каталог найден - это валидный git репозиторий
```

## Преимущества исправления

1. ✅ Репозитории теперь корректно клонируются в подкаталоги
2. ✅ Использование стандартного поведения git
3. ✅ Более надёжная работа с путями
4. ✅ Сохранена обратная совместимость
5. ✅ Нет изменений в логике создания родительских каталогов

## Совместимость

Исправление полностью обратно совместимо:
- Родительские каталоги создаются как раньше (`os.makedirs(parent_dir, exist_ok=True)`)
- Структура путей не меняется
- Логика проверки существования репозитория не изменена

