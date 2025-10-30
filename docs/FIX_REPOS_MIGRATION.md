# Исправление сохранения репозиториев в поддиректорию repos

## Дата: 30 октября 2025

## Проблема

Для уже созданных проектов пути к репозиториям сохранялись неправильно:
- Старые репозитории клонировались в корень проекта (`/python/checklist_app`, `/python/TechnouprApp.Client`)
- Вместо этого они должны сохраняться в поддиректорию `repos/`

## Причина

В файле `storage.py` метод `_doc_to_project()` использовал `os.path.abspath()` для преобразования относительных путей. Это приводило к тому, что относительный путь преобразовывался относительно текущей рабочей директории, а не относительно директории `repos/`.

## Решение

### 1. Исправлен `storage.py`

Добавлена константа `REPOS_DIR` и изменена логика преобразования путей:

```python
# Get project root directory (parent of src directory)
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.dirname(_CURRENT_DIR)  # src/easybuild_bot -> src
_PYTHON_DIR = os.path.dirname(_SRC_DIR)    # src -> python
PROJECT_ROOT = os.path.dirname(_PYTHON_DIR)  # python -> project root
REPOS_DIR = os.path.join(PROJECT_ROOT, "repos")
```

В методе `_doc_to_project()`:

```python
# Get local_repo_path and ensure it's absolute
local_repo_path = str(doc.get("local_repo_path", ""))
if local_repo_path and not os.path.isabs(local_repo_path):
    # Convert relative path to absolute, placing it in repos/ directory
    local_repo_path = os.path.join(REPOS_DIR, local_repo_path)
```

**Было:**
- Относительный путь `checklist_app` → `os.path.abspath()` → `/current/working/dir/checklist_app`

**Стало:**
- Относительный путь `checklist_app` → `os.path.join(REPOS_DIR, ...)` → `/project/repos/checklist_app`

### 2. Добавлено свойство `db` в класс `Storage`

Для работы скрипта миграции добавлено публичное свойство:

```python
@property
def db(self):
    """Get database instance for direct access."""
    return self._db
```

## Запуск миграции

### Шаг 1: Установите зависимости (если не установлены)

```bash
cd /home/olinyavod/projects/easybuild_bot/python
pip3 install -r requirements.txt
```

### Шаг 2: Запустите скрипт миграции

```bash
cd /home/olinyavod/projects/easybuild_bot/python
python3 scripts/migrate_repos.py
```

Скрипт:
1. ✅ Загрузит все проекты из БД
2. ✅ Проверит, какие проекты нуждаются в обновлении путей
3. ✅ Обновит пути в БД (добавит `repos/` в начало)
4. ❓ Предложит переместить существующие репозитории

### Шаг 3: Переместите старые репозитории (опционально)

Если у вас есть старые репозитории в корне `/python`:

```bash
# Создайте директорию repos, если её нет
mkdir -p /home/olinyavod/projects/easybuild_bot/repos

# Переместите репозитории
mv /home/olinyavod/projects/easybuild_bot/python/checklist_app \
   /home/olinyavod/projects/easybuild_bot/repos/checklist_app

mv /home/olinyavod/projects/easybuild_bot/python/TechnouprApp.Client \
   /home/olinyavod/projects/easybuild_bot/repos/technouprapp.client
```

**Примечание:** Имена директорий в `repos/` должны совпадать с тем, что было сгенерировано при создании проекта (обычно lowercase с подчёркиваниями).

## Результат

После исправления:
- ✅ Все новые проекты будут автоматически создаваться в `repos/`
- ✅ Старые проекты с относительными путями будут корректно преобразованы
- ✅ При следующем выборе проекта репозитории будут клонироваться в правильное место

## Дополнительная информация

Если вы не переместили старые репозитории вручную, при следующем выборе проекта:
1. Бот обнаружит, что репозитория нет по новому пути
2. Автоматически склонирует репозиторий в `repos/`
3. Старый репозиторий в корне `/python` можно будет удалить вручную


