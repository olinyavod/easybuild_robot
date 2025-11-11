# 📚 Документация EasyBuild Bot

Вся документация проекта организована в этой папке.

## 📂 Структура

### 🏗️ Архитектура
- [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) - Общая архитектура системы
- [`architecture/COMPARISON.md`](architecture/COMPARISON.md) - Сравнение старой и новой архитектуры

### 📖 Руководства
- [`guides/COMMAND_PATTERN_GUIDE.md`](guides/COMMAND_PATTERN_GUIDE.md) - Паттерн Command
- [`guides/COMMAND_PATTERN_SUMMARY.md`](guides/COMMAND_PATTERN_SUMMARY.md) - Краткое описание паттерна
- [`guides/DI_CONTAINER_GUIDE.md`](guides/DI_CONTAINER_GUIDE.md) - Dependency Injection контейнер
- [`QUICKSTART.md`](QUICKSTART.md) - Быстрый старт

### 🔧 Python-специфичная документация
- [`python/ARCHITECTURE.md`](python/ARCHITECTURE.md) - Архитектура Python части
- [`python/START_BOT.md`](python/START_BOT.md) - Запуск бота
- [`python/VOICE_COMMANDS.md`](python/VOICE_COMMANDS.md) - Голосовые команды
- [`python/TTS_GUIDE.md`](python/TTS_GUIDE.md) - Text-to-Speech
- [`python/TROUBLESHOOTING.md`](python/TROUBLESHOOTING.md) - Решение проблем
- И другие...

### 🐛 Исправления Xamarin
**Последние исправления (11 ноября 2025):**
- [`XAMARIN_RECURSIVE_SEARCH_FIX.md`](XAMARIN_RECURSIVE_SEARCH_FIX.md) - Исправлен рекурсивный поиск файлов
- [`XAMARIN_ERROR_MESSAGES_IMPROVEMENT.md`](XAMARIN_ERROR_MESSAGES_IMPROVEMENT.md) - Улучшены сообщения об ошибках
- [`XAMARIN_VERSION_LOGGING_FIX.md`](XAMARIN_VERSION_LOGGING_FIX.md) - Улучшено логирование
- [`QUICK_FIX_XAMARIN_VERSION.md`](QUICK_FIX_XAMARIN_VERSION.md) - Быстрое решение проблем

**Предыдущие исправления:**
- [`XAMARIN_PLATFORM_FIX.md`](XAMARIN_PLATFORM_FIX.md) - Исправление платформенных файлов
- [`XAMARIN_VERSION_FIX.md`](XAMARIN_VERSION_FIX.md) - Исправление версионирования
- [`XAMARIN_MULTI_PLATFORM_SUPPORT.md`](XAMARIN_MULTI_PLATFORM_SUPPORT.md) - Поддержка нескольких платформ

### 🔄 Рефакторинг
- [`REFACTORING_GIT_SERVICE.md`](REFACTORING_GIT_SERVICE.md) - Общий GitService вместо дублирования кода
- [`python/REFACTORING_SUMMARY.md`](python/REFACTORING_SUMMARY.md) - Общее резюме рефакторинга
- [`python/DI_IMPROVEMENTS.md`](python/DI_IMPROVEMENTS.md) - Улучшения DI контейнера

### 📝 Changelog
- [`CHANGELOG_XAMARIN_FIX.md`](CHANGELOG_XAMARIN_FIX.md) - Изменения в Xamarin
- [`CHANGELOG_2025_11_09.md`](CHANGELOG_2025_11_09.md) - Изменения от 9 ноября
- [`CHANGELOG_DELETE_PROJECT.md`](CHANGELOG_DELETE_PROJECT.md) - Удаление проектов
- [`python/CHANGELOG_VOICE.md`](python/CHANGELOG_VOICE.md) - Голосовые команды
- И другие...

### 🛠️ Управление проектами
- [`PROJECTS_MANAGEMENT.md`](PROJECTS_MANAGEMENT.md) - Управление проектами
- [`ADD_PROJECT_WIZARD.md`](ADD_PROJECT_WIZARD.md) - Мастер добавления проекта
- [`EDIT_PROJECT_WIZARD.md`](EDIT_PROJECT_WIZARD.md) - Мастер редактирования проекта
- [`ADD_PROJECT_CHEATSHEET.md`](ADD_PROJECT_CHEATSHEET.md) - Шпаргалка по добавлению
- [`EDIT_PROJECT_CHEATSHEET.md`](EDIT_PROJECT_CHEATSHEET.md) - Шпаргалка по редактированию

### 🔍 Поиск и матчинг
- [`PROJECT_SEMANTIC_MATCHING.md`](PROJECT_SEMANTIC_MATCHING.md) - Семантический поиск
- [`PROJECT_MATCHING_QUICKSTART.md`](PROJECT_MATCHING_QUICKSTART.md) - Быстрый старт

### 🏗️ Сборка и релизы
- [`BUILDERS_SYSTEM.md`](BUILDERS_SYSTEM.md) - Система сборки
- [`SIMPLIFIED_RELEASE_PROCESS.md`](SIMPLIFIED_RELEASE_PROCESS.md) - Упрощённый процесс релиза
- [`FLUTTER_RELEASE_PREPARATION.md`](FLUTTER_RELEASE_PREPARATION.md) - Подготовка релиза Flutter

### 🔧 Исправления и улучшения
- [`FIX_VERSION_DETECTION.md`](FIX_VERSION_DETECTION.md) - Определение версии
- [`FIX_REPOS_MIGRATION.md`](FIX_REPOS_MIGRATION.md) - Миграция репозиториев
- [`FIX_CLONE_ERROR.md`](FIX_CLONE_ERROR.md) - Ошибки клонирования
- [`WIZARD_CANCEL_FIX.md`](WIZARD_CANCEL_FIX.md) - Отмена мастеров
- И другие...

### 📋 Тестирование
- [`TESTING_INSTRUCTIONS.md`](TESTING_INSTRUCTIONS.md) - Инструкции по тестированию
- [`QUICK_TEST_GUIDE.md`](QUICK_TEST_GUIDE.md) - Быстрое руководство по тестированию

### 🎨 Разное
- [`CODE_STYLE_TRANSLATION.md`](CODE_STYLE_TRANSLATION.md) - Перевод стиля кода
- [`LINTING.md`](LINTING.md) - Линтинг
- [`CI_CD_EXAMPLES.md`](CI_CD_EXAMPLES.md) - Примеры CI/CD
- [`CONTRIBUTING.md`](CONTRIBUTING.md) - Как внести вклад
- [`DOCUMENTATION_STRUCTURE.md`](DOCUMENTATION_STRUCTURE.md) - Структура документации

## 🔄 Миграция
- [`migration/MIGRATION_COMPLETE.md`](migration/MIGRATION_COMPLETE.md) - Завершение миграции
- [`migration/IMPLEMENTATION_COMPLETE.md`](migration/IMPLEMENTATION_COMPLETE.md) - Завершение реализации
- [`migration/FINAL_SUMMARY.md`](migration/FINAL_SUMMARY.md) - Итоговая сводка
- [`migration/LEGACY_REMOVAL_COMPLETE.md`](migration/LEGACY_REMOVAL_COMPLETE.md) - Удаление legacy кода

## 🔍 Поиск документации

### По теме:
- **Xamarin проблемы**: `XAMARIN_*.md`, `QUICK_FIX_XAMARIN_VERSION.md`
- **Архитектура**: `architecture/`, `python/ARCHITECTURE.md`
- **Команды**: `guides/COMMAND_PATTERN_*.md`, `python/VOICE_COMMANDS.md`
- **Проекты**: `*PROJECT*.md`, `ADD_PROJECT_*.md`, `EDIT_PROJECT_*.md`
- **Версии**: `*VERSION*.md`, `FIX_VERSION_*.md`
- **Git**: `REFACTORING_GIT_SERVICE.md`, `FIX_CLONE_*.md`, `FIX_REPOS_*.md`

### По дате:
- **11 ноября 2025**: Xamarin исправления, GitService рефакторинг
- **9 ноября 2025**: `CHANGELOG_2025_11_09.md`
- **30 октября 2025**: Исправления версий, миграция репозиториев

## 📚 Рекомендуемый порядок чтения

Для новых разработчиков:
1. [`QUICKSTART.md`](QUICKSTART.md) - Начните здесь
2. [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) - Понимание архитектуры
3. [`guides/COMMAND_PATTERN_GUIDE.md`](guides/COMMAND_PATTERN_GUIDE.md) - Паттерны
4. [`python/START_BOT.md`](python/START_BOT.md) - Запуск
5. [`PROJECTS_MANAGEMENT.md`](PROJECTS_MANAGEMENT.md) - Управление проектами

Для решения проблем:
1. [`python/TROUBLESHOOTING.md`](python/TROUBLESHOOTING.md) - Общие проблемы
2. [`QUICK_FIX_XAMARIN_VERSION.md`](QUICK_FIX_XAMARIN_VERSION.md) - Xamarin
3. [`FIX_VERSION_DETECTION.md`](FIX_VERSION_DETECTION.md) - Версии
4. [`TESTING_INSTRUCTIONS.md`](TESTING_INSTRUCTIONS.md) - Тестирование

---

**Последнее обновление:** 11 ноября 2025
**Всего файлов документации:** 100+
