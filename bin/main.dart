import 'dart:io';
import 'package:easybuild_bot/hive_registrar.g.dart';
import 'package:hive_ce/hive.dart';
import 'package:hotreloader/hotreloader.dart';
import 'package:dotenv/dotenv.dart';

import 'package:easybuild_bot/easybuild_bot.dart';
import 'package:easybuild_bot/di/service_locator.dart';

// This is a general example of how to use the Televerse library.
void main(List<String> args) async {
  // Загружаем переменные окружения из .env файла
  var env = DotEnv();
  env.load();

  // Initialize Hive
  final hiveDir = Directory('${Directory.current.path}/data/hive');
  if (!await hiveDir.exists()) {
    await hiveDir.create(recursive: true);
  }
  Hive
    ..init(hiveDir.path)
    ..registerAdapters();

  // Регистрируем токен бота как именованную зависимость
  final String token = env['BOT_TOKEN'] ?? Platform.environment["BOT_TOKEN"]!;
  getIt.registerSingleton<String>(token, instanceName: 'botToken');

  // Инициализируем DI контейнер
  await configureDependencies();
  
  // Получаем бота из DI контейнера
  final bot = getIt<EasybuildBot>();
  
  final reloader = await HotReloader.create(
    debounceInterval: const Duration(seconds: 2),
    onAfterReload: (ctx) async => bot.restart(),
  );
  
  await bot.start();

  reloader.stop();
}