import 'package:hive_ce/hive.dart';
import 'package:injectable/injectable.dart';

import 'package:easybuild_bot/hive/models.dart';

/// Модуль для регистрации внешних зависимостей,
/// которые не могут быть аннотированы напрямую
@module
abstract class ExternalModules {
  /// Регистрация Box<User> как singleton
  /// Этот метод будет вызван автоматически при инициализации DI
  @preResolve
  @singleton
  Future<Box<BotUser>> get usersBox async {
    return await Hive.openBox<BotUser>('users');
  }

  // Добавьте сюда другие внешние зависимости, например:
  // 
  // @singleton
  // @Named('apiUrl')
  // String get apiUrl => 'https://api.example.com';
  //
  // @singleton
  // HttpClient get httpClient => HttpClient();
}

