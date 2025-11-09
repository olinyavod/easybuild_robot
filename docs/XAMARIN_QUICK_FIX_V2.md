# БЫСТРОЕ ИСПРАВЛЕНИЕ: Версионирование Xamarin (обновление №2)

## 🔴 Проблема
Бот всё ещё не может определить версию в проектах Xamarin.

## ✅ Решение (2 минуты)

### Шаг 1: Откройте файл Android

Найдите файл `*.Android.csproj` (например, `Fintech.Android/Fintech.Android.csproj`)

### Шаг 2: Добавьте теги версий

```xml
<Project>
  <PropertyGroup>
    <ApplicationVersion>1.0.0</ApplicationVersion>
    <AndroidVersionCode>10000</AndroidVersionCode>
  </PropertyGroup>
</Project>
```

### Шаг 3: Откройте файл iOS

Найдите файл `*.iOS.csproj` (например, `Fintech.iOS/Fintech.iOS.csproj`)

### Шаг 4: Добавьте теги версий

```xml
<Project>
  <PropertyGroup>
    <ApplicationVersion>1.0.0</ApplicationVersion>
    <CFBundleVersion>1.0.0</CFBundleVersion>
  </PropertyGroup>
</Project>
```

### Шаг 5: Сохраните и запушьте

```bash
git add .
git commit -m "Добавлены версии в платформенные проекты"
git push
```

### Шаг 6: Запустите сборку

Готово! Бот найдёт версии в платформенных файлах ✅

---

## 📝 Важно

- Версия должна быть в **платформенных** файлах (`*.Android.csproj`, `*.iOS.csproj`)
- Для Android используется `ApplicationVersion` + `AndroidVersionCode`
- Для iOS используется `ApplicationVersion` + `CFBundleVersion`
- `AndroidVersionCode` будет автоматически обновляться (1.0.0 → 10000, 1.0.1 → 10001)

---

## 📚 Подробная документация

См. `docs/XAMARIN_PLATFORM_FIX.md`
