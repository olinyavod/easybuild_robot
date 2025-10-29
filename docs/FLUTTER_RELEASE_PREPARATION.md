# Подготовка релиза для Flutter проектов

## Дата: 27 октября 2025

## Обзор

Добавлена функциональность автоматической подготовки релиза для Flutter проектов, которая включает:
1. Мердж ветки разработки в ветку релиза
2. Переключение на ветку релиза
3. Обновление версии в `pubspec.yaml`
4. Коммит изменений

## Workflow

### 1. Выбор проекта и клонирование

```
/build → Выбор Flutter проекта → Клонирование репозитория
```

### 2. Меню действий

Для Flutter проектов теперь доступна дополнительная кнопка:

```
🎯 Проект готов к сборке v1.0.0

Выберите действие:
[🔨 Собрать Debug]
[🚀 Собрать Release]
[📦 Подготовить релиз]    ← НОВАЯ КНОПКА
[🧹 Очистить артефакты]
```

### 3. Подготовка релиза

При нажатии на "📦 Подготовить релиз":

1. Бот просит ввести новую версию:
```
🚀 Подготовка релиза для проекта MyApp

Текущая версия: 1.0.0+1

Введите новую версию в формате: version <версия>
Например: version 1.2.3+45
```

2. Пользователь вводит: `version 1.0.1+2`

3. Бот выполняет последовательность операций:
```
🚀 Начинаем подготовку релиза версии 1.0.1+2...
🔀 Переключение на ветку релиза: main...
⬇️ Получение последних изменений из ветки релиза...
🔄 Мердж изменений из develop в main...
✅ Ветки успешно смерджены
📝 Обновление версии в pubspec.yaml на 1.0.1+2...
✅ Версия обновлена на 1.0.1+2
💾 Коммит изменений...
✅ Изменения закоммичены

🎉 Релиз успешно подготовлен!

✅ Ветка: main
✅ Версия: 1.0.1+2
✅ Изменения из develop смерджены

⚠️ Не забудьте сделать push:
git push origin main
```

## Технические детали

### FlutterBuilder.prepare_release()

Метод выполняет следующие шаги:

1. **Checkout release branch**
   ```bash
   git checkout main
   ```

2. **Pull latest changes**
   ```bash
   git pull origin main
   ```

3. **Merge dev into release**
   ```bash
   git merge develop -m "Merge develop for release 1.0.1+2"
   ```
   - При ошибке выполняется `git merge --abort`

4. **Update version in pubspec.yaml**
   - Использует `FlutterVersionManager.update_version()`
   - Regex замена строки `version: ...`

5. **Commit changes**
   ```bash
   git add pubspec.yaml
   git commit -m "Bump version to 1.0.1+2"
   ```

### FlutterVersionManager

Вспомогательный класс для работы с `pubspec.yaml`:

```python
class FlutterVersionManager:
    @staticmethod
    def update_version(pubspec_path: str, new_version: str) -> bool:
        """Update version in pubspec.yaml."""
        # Regex: ^version:\s*.*$ → version: 1.0.1+2
```

### Команды

#### PrepareReleaseCallbackCommand

- **Pattern:** `build_prepare_release:<project_id>`
- **Действие:** Показывает prompt для ввода версии
- **Проверка:** `builder.supports_release_preparation()`

#### ExecuteReleaseCallbackCommand

- **Pattern:** `execute_release:<project_id>:<version>`
- **Действие:** Выполняет `builder.prepare_release(version)`

#### VersionCommand

- **Pattern:** `version <номер>`
- **Действие:** Распознает версию из текста
- **Regex:** `r"version\s+([0-9]+\.[0-9]+\.[0-9]+(?:\+[0-9]+)?)"`

### Базовый интерфейс ProjectBuilder

Добавлены опциональные методы:

```python
async def supports_release_preparation(self) -> bool:
    """Check if this builder supports release preparation."""
    return False  # По умолчанию

async def prepare_release(self, new_version: str) -> BuildResult:
    """Prepare release (merge, update version, commit)."""
    # Реализация специфична для типа проекта
```

## Поддержка других типов проектов

### Flutter
✅ **Полная поддержка**
- Merge develop → release
- Update pubspec.yaml
- Commit changes

### .NET MAUI и Xamarin
⚠️ **Пока не реализовано**
- `supports_release_preparation()` возвращает `False`
- Кнопка "Подготовить релиз" не показывается

Для добавления поддержки нужно:
1. Переопределить `supports_release_preparation()` → `True`
2. Реализовать `prepare_release()` с обновлением `.csproj`

## Формат версии

**Flutter (pubspec.yaml):**
- Формат: `major.minor.patch+build`
- Примеры: `1.0.0`, `1.2.3+45`, `2.0.0-beta+1`

**Regex:** `[0-9]+\.[0-9]+\.[0-9]+(?:\+[0-9]+)?`

## Обработка ошибок

### Конфликты при merge
```
❌ Ошибка при мердже:
CONFLICT (content): Merge conflict in lib/main.dart
Automatic merge failed
```
- Merge отменяется: `git merge --abort`
- Пользователю предлагается разрешить конфликты вручную

### Недоступная ветка
```
❌ Не удалось переключиться на ветку main:
error: pathspec 'main' did not match any file(s) known to git
```

### Неверный формат версии
```
❌ Неверный формат команды.

Использование: version <номер>
Пример: version 1.2.3+45
```

## Безопасность

- ✅ Проверка доступа пользователя
- ✅ Timeout'ы для git операций (30-120 сек)
- ✅ Откат при ошибках (merge --abort)
- ✅ Валидация формата версии
- ⚠️ **Push НЕ выполняется автоматически** - пользователь должен сделать это вручную

## Будущие улучшения

- [ ] Автоматический push после подтверждения
- [ ] Создание git tag для релиза
- [ ] Автоматический changelog
- [ ] Поддержка для .NET MAUI и Xamarin
- [ ] Проверка unit-тестов перед релизом
- [ ] Интеграция с CI/CD
- [ ] Rollback функциональность

## Примеры использования

### Успешный флоу
```
1. /build
2. Выбрать Flutter проект
3. Нажать "📦 Подготовить релиз"
4. Ввести: version 1.0.1+2
5. Дождаться выполнения
6. Выполнить: git push origin main
```

### С конфликтами
```
1. /build
2. Выбрать проект
3. "📦 Подготовить релиз"
4. version 2.0.0
5. ❌ Конфликт при мердже
6. Вручную: git checkout main, git merge develop
7. Разрешить конфликты
8. git commit, git push
```

## Связанные файлы

```
python/src/easybuild_bot/
├── builders/
│   ├── base.py                              # +prepare_release(), +supports_release_preparation()
│   └── flutter_builder.py                   # +FlutterVersionManager, реализация prepare_release()
└── commands/implementations/
    ├── prepare_release_callback.py          # NEW: PrepareReleaseCallbackCommand
    ├── version_command.py                   # NEW: VersionCommand
    └── project_select_callback.py           # +кнопка "Подготовить релиз"
```




