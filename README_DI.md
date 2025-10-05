# Dependency Injection (DI)

В проекте настроен Dependency Injection на основе аннотаций с использованием библиотек `get_it` и `injectable`.

## Структура

### Основные файлы

- **`lib/di/service_locator.dart`** - главная точка входа для DI контейнера
- **`lib/di/external_modules.dart`** - файл для регистрации внешних зависимостей (которые нельзя аннотировать)
- **`lib/di/service_locator.config.dart`** - автогенерируемый файл с конфигурацией (не редактировать вручную)

## Использование аннотаций

### @singleton
Регистрирует класс как singleton (единственный экземпляр на всё приложение):

```dart
import 'package:injectable/injectable.dart';

@singleton
class UsersService {
  UsersService(Dependency dep);
}
```

### @lazySingleton
Singleton, который создается только при первом использовании:

```dart
@lazySingleton
class LazyService {
  LazyService();
}
```

### @injectable
Регистрирует класс как factory (новый экземпляр при каждом запросе):

```dart
@injectable
class TransientService {
  TransientService();
}
```

### @Named
Для именованных зависимостей:

```dart
@singleton
class ApiService {
  ApiService(@Named('apiUrl') String url);
}
```

## Регистрация внешних зависимостей

Используйте файл `lib/di/external_modules.dart` для регистрации зависимостей из сторонних библиотек:

```dart
@module
abstract class ExternalModules {
  @preResolve  // Для async инициализации
  @singleton
  Future<Box<User>> get usersBox async {
    return await Hive.openBox<User>('users');
  }
  
  @singleton
  @Named('apiUrl')
  String get apiUrl => 'https://api.example.com';
}
```

## Инициализация

В `main.dart`:

```dart
import 'package:easybuild_bot/di/service_locator.dart';

void main() async {
  // Регистрация зависимостей, которые нельзя аннотировать
  getIt.registerSingleton<String>(token, instanceName: 'botToken');
  
  // Инициализация DI контейнера
  await configureDependencies();
  
  // Получение зависимостей
  final bot = getIt<EasybuildBot>();
}
```

## Получение зависимостей

```dart
// В коде
final service = getIt<UsersService>();

// Или с именем
final url = getIt<String>(instanceName: 'apiUrl');
```

## Генерация кода

После изменения аннотаций или добавления новых сервисов, запустите:

```bash
dart run build_runner build --delete-conflicting-outputs
```

Или для автоматической перегенерации при изменениях:

```bash
dart run build_runner watch --delete-conflicting-outputs
```

## Примеры

### Сервис с зависимостью

```dart
@singleton
class UserRepository {
  final Box<User> _box;
  final ApiService _api;
  
  UserRepository(this._box, this._api);
}
```

### Условная регистрация (для разных окружений)

```dart
@Environment('dev')
@singleton
class DevApiService implements ApiService {
  // ...
}

@Environment('prod')
@singleton
class ProdApiService implements ApiService {
  // ...
}
```

Использование:

```dart
await configureDependencies(environment: 'dev');
```

