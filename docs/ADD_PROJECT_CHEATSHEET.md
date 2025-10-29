# Быстрая шпаргалка: Add Project Wizard

## Запуск мастера

```
/add_project
```

## Шаги

| # | Вопрос | Пример ответа | Примечание |
|---|--------|---------------|------------|
| 1 | Название проекта | `MyAwesomeApp` | Должно быть уникальным |
| 2 | Тип проекта | [Нажать кнопку] | 🦋 Flutter / 🔷 .NET MAUI / 🔶 Xamarin |
| 3 | Git URL | `https://github.com/user/myapp.git` | URL репозитория |
| 4 | Путь к файлу проекта | `android/app` (Flutter)<br>`src/App/App.csproj` (.NET) | Относительный путь от корня |
| 5 | Локальный путь | `/home/repos/myapp` | Где будет храниться репозиторий |
| 6 | Ветка разработки | `develop` или `/skip` | По умолчанию: `develop` |
| 7 | Ветка релиза | `main` или `/skip` | По умолчанию: `main` |
| 8 | Подтверждение | [Нажать "✅ Да, создать"] | Финальное подтверждение |

## Отмена

В любой момент:
```
/cancel
```

## Значения по умолчанию

Для шагов 6 и 7 можно использовать `/skip`:
- Ветка разработки: `develop`
- Ветка релиза: `main`

## Примеры путей к проектам

### Flutter
```
android/app           # Android приложение
ios/Runner           # iOS приложение
```

### .NET MAUI
```
src/MyApp/MyApp.csproj
MyApp/MyApp.csproj
```

### Xamarin
```
MyApp/MyApp.Android/MyApp.Android.csproj
MyApp/MyApp.iOS/MyApp.iOS.csproj
```

## Требования

✅ Права администратора  
✅ Уникальное название проекта

## Что происходит после создания?

1. ✅ Проект сохраняется в базе данных
2. 📋 Бот показывает ID проекта
3. 🎉 Проект доступен для всех групп (по умолчанию)
4. 🔧 Можно редактировать через `/edit_project`

## Дальнейшие действия

После создания проекта вы можете:

- Добавить описание: `/edit_project MyApp description "Описание проекта"`
- Добавить теги: `/edit_project MyApp tags "tag1,tag2,tag3"`
- Ограничить доступ: `/edit_project MyApp groups -1001234567890`
- Просмотреть проекты: `/projects`

## Подробная документация

📖 [ADD_PROJECT_WIZARD.md](ADD_PROJECT_WIZARD.md) - Полное руководство  
📖 [PROJECTS_MANAGEMENT.md](PROJECTS_MANAGEMENT.md) - Управление проектами






