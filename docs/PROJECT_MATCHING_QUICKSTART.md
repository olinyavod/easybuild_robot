# Быстрый старт: Семантический поиск проектов

## Что добавлено

✅ **ProjectMatcher** - класс для семантического поиска проектов по тегам  
✅ **Детальные ошибки** - теперь при ошибках в голосовых командах показываются детали для отладки

## Файлы

1. **`src/easybuild_bot/project_matcher.py`** - основной класс
2. **`scripts/test_project_matcher.py`** - скрипт для тестирования
3. **`docs/PROJECT_SEMANTIC_MATCHING.md`** - полная документация

## Быстрый тест

```bash
# Перейти в директорию проекта
cd /home/olinyavod/projects/easybuild_bot/python

# Активировать виртуальное окружение
source .venv/bin/activate

# Запустить тест
python scripts/test_project_matcher.py
```

## Добавление тегов к проектам

Чтобы семантический поиск работал, добавьте теги к проектам:

```bash
# Через команду бота
/edit_project MyApp tags mobile,android,мобильный,flutter

# Через интерактивный мастер
/edit_project_wizard
```

## Примеры тегов

**Мобильные:**
```
mobile, мобильный, мобильное, android, андроид, ios, айфон
```

**Веб:**
```
web, веб, сайт, react, vue, frontend, backend
```

**Desktop:**
```
desktop, десктоп, windows, linux, wpf, winforms
```

## Следующие шаги (TODO для интеграции)

### 1. Добавить ProjectMatcher в factory.py

```python
from .project_matcher import ProjectMatcher

def create_command_system(...):
    # ...
    project_matcher = ProjectMatcher(threshold=0.5)
    return registry, executor, project_matcher
```

### 2. Обновить команды сборки

Пример для `/build_apk`:

```python
class BuildApkCommand(Command):
    def __init__(self, storage, access_control, project_matcher):
        super().__init__(storage, access_control)
        self.project_matcher = project_matcher
    
    def get_parameter_patterns(self):
        return {
            "project_query": [
                r"(?:собрать|build)\s+(.+?)(?:\s+apk|\s*$)",
            ]
        }
    
    async def execute(self, ctx):
        project_query = ctx.params.get("project_query")
        
        if project_query:
            projects = self.storage.get_all_projects()
            project = self.project_matcher.find_project_by_name_or_tags(
                project_query,
                projects
            )
            
            if project:
                # Начать сборку
                pass
            else:
                await ctx.update.effective_message.reply_text(
                    f"❌ Проект '{project_query}' не найден"
                )
```

### 3. Перезапустить бота

```bash
sudo systemctl restart easybuild_bot_py
```

## Проверка работы

После интеграции попробуйте голосовую команду:

🎤 **"Собрать мобильное приложение"**

Бот должен:
1. Распознать команду `/build_apk`
2. Найти проект с тегами `mobile`, `мобильный`, `android`
3. Начать сборку или показать список проектов для выбора

## Отладка ошибок

Теперь при ошибках бот показывает детали:

```
❌ Произошла ошибка при выполнении команды

🔧 Детали ошибки (для отладки):
AttributeError: 'NoneType' object has no attribute 'name'
```

Это поможет быстро найти и исправить проблемы!

## Дополнительная информация

- **Полная документация:** `docs/PROJECT_SEMANTIC_MATCHING.md`
- **Порог сходства:** 0.5 (можно настроить при инициализации)
- **Модель:** `cointegrated/rubert-tiny` (та же, что для команд)

