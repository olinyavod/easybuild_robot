import 'dart:io';
import 'package:injectable/injectable.dart';
import 'package:televerse/plugins/conversation.dart';
import 'package:televerse/televerse.dart';

import 'package:easybuild_bot/hive/models.dart';
import 'package:easybuild_bot/services/services.dart';

@singleton
class EasybuildBot {
  // Create a new bot instance
  final Bot _bot;
  final String _token;
  final UsersService _usersService;

  EasybuildBot(
    @Named('botToken') String token,
    this._usersService,
  ) : _bot = Bot(token), _token = token {
    _bot.plugin(ConversationPlugin<Context>());
    _setup();
  }

  void _setup() {    
    _bot.command("start", _start);
    _bot.command("users", _users);
    _bot.callbackQuery(RegExp(r'^allow_user_(\d+)$'), _allowUserCallback);
    _bot.use(createConversation("requestAdmin", _admin));
    _bot.command('admin', (ctx) async {
      await ctx.conversation.enter('requestAdmin');
    });
    _bot.command('build', _build);
    _bot.callbackQuery(RegExp(r"^build_apk_checklist_prod$"), _buildApkChecklistProd);
    _bot.help(_help);
  }

  Future<bool> _requestAccess(Context ctx) async {
    final userId = ctx.getEffectiveUserId();
    var user = await _usersService.getUserByUserId(userId ?? 0);
    
    if (user == null) {
      user = BotUser(
        id: '${ctx.getEffectiveUserId()}',
        userId: userId ?? 0, 
        userName: '',
        displayName: ctx.getUserDisplayName()
      );

      await _usersService.addUser(user);
    }

    if (!user.allowed) {
      await ctx.reply("Вы не имеете доступа к боту. Пожалуйста, обратитесь к администратору.");
      return false;
    }

    return true;
  }

  Future<bool> _requestAdminAccess(Context ctx, {bool isReplay = true}) async {
    final userId = ctx.getEffectiveUserId();
    final user = await _usersService.getUserByUserId(userId ?? 0);

    if (user?.isAdmin ?? false) return true;

    if(user == null) {
      await _usersService.addUser(BotUser(
        id: '${ctx.getEffectiveUserId()}',
        userId: userId ?? 0, 
        userName: '',
        displayName: ctx.getUserDisplayName()
      ));
    }

    if (isReplay) {
      await ctx.reply("Вы не имеете доступа к боту. Пожалуйста, обратитесь к администратору.");
    }

    return false;
  }

  Future<void> _start(Context ctx) async {
    if (!await _requestAccess(ctx)) return;

    await ctx.reply("Привет, ${ctx.getUserDisplayName()}!");
  }

  Future<void> _help(Context ctx) async {
    if (!await _requestAccess(ctx)) return;

    await ctx.reply("Help");
  }

  Future<void> _build(Context ctx) async {
    if (!await _requestAccess(ctx)) return;

    final keyboard = InlineKeyboard()    
    .text("Сборка APK Autolab - Checklist для Prod-среды", "build_apk_checklist_prod").row()
    .text("Сборка APK Autolab - Checklist для Dev-среды", "build_apk_checklist_dev").row()
    
    .text("Сборка APK TehnouprApp - Клиент для Prod-среды", "build_apk_tehnoupr_client_prod").row()
    .text("Сборка APK TehnouprApp - Клиент для Dev-среды", "build_apk_tehnoupr_client_dev").row()

    .text("Сборка APK TehnouprApp - Сотрудник для Prod-среды", "build_apk_tehnoupr_employee_prod").row()
    .text("Сборка APK TehnouprApp - Сотрудник для Dev-среды", "build_apk_tehnoupr_employee_dev").row()
    .row();

    await ctx.reply(
      "Выберите сборку:",
      replyMarkup: keyboard,
    );
  }

  Future<void> _users(Context ctx) async {
    if (!await _requestAdminAccess(ctx)) return;

    final allUsers = await _usersService.getAllUsers();
    final notAllowedUsers = allUsers.where((user) => !user.allowed).toList();

    if (notAllowedUsers.isEmpty) {
      await ctx.reply("Все пользователи имеют доступ.");
      return;
    }

    // Создаем inline keyboard с кнопками для каждого пользователя без доступа
    var keyboard = InlineKeyboard();
    
    for (final user in notAllowedUsers) {
      final displayText = user.displayName ?? 'User ${user.userId}';
      keyboard = keyboard.text(displayText, 'allow_user_${user.userId}').row();
    }

    await ctx.reply(
      "Пользователи без доступа:\nНажмите на кнопку, чтобы предоставить доступ:",
      replyMarkup: keyboard,
    );
  }

  Future<void> _allowUserCallback(Context ctx) async {
    if (!await _requestAdminAccess(ctx, isReplay: false)) {
      await ctx.answerCallbackQuery(text: "У вас нет прав администратора");
      return;
    }

    final callbackQuery = ctx.callbackQuery;
    if (callbackQuery?.data == null) return;

    final match = RegExp(r'^allow_user_(\d+)$').firstMatch(callbackQuery!.data!);
    if (match == null) return;

    final userId = int.parse(match.group(1)!);
    final user = await _usersService.getUserByUserId(userId);

    if (user == null) {
      await ctx.answerCallbackQuery(text: "Пользователь не найден");
      return;
    }

    user.allowed = true;
    await user.save();

    await ctx.answerCallbackQuery(text: "Доступ предоставлен ✅");
    
    // Обновляем сообщение с кнопками
    final allUsers = await _usersService.getAllUsers();
    final notAllowedUsers = allUsers.where((user) => !user.allowed).toList();

    if (notAllowedUsers.isEmpty) {
      await ctx.editMessageText("Все пользователи имеют доступ.");
    } else {
      var keyboard = InlineKeyboard();
      
      for (final user in notAllowedUsers) {
        final displayText = user.displayName ?? 'User ${user.userId}';
        keyboard = keyboard.text(displayText, 'allow_user_${user.userId}').row();
      }

      await ctx.editMessageText(
        "Пользователи без доступа:\nНажмите на кнопку, чтобы предоставить доступ:",
        replyMarkup: keyboard,
      );
    }
  }

  Future<void> _admin(Conversation<Context> conversation, Context ctx) async {
    try {
      if (await _requestAdminAccess(ctx, isReplay: false)) return;

      await ctx.reply("Ввведите токен от чат-бота для администратора");

      final token = await conversation.waitFor(
        _bot.filters.text.matches,
        timeout: Duration(minutes: 2),
      );

      final userId = token.getEffectiveUserId();
      final user = await _usersService.getUserByUserId(userId ?? 0);

      if (user == null) {
        await ctx.reply("Пользователь не найден!");
        return;
      }

      if (token.text != _token) {
        await ctx.reply("Неверный токен!");
        return;
      }

      user.isAdmin = true;
      
      await user.save();

      await token.reply("Вы успешно добавлены в администраторы!");
    } on ConversationTimeoutException {
      await ctx.reply("Попробуйте ещё раз!");
    }
  }

  Future<void> _buildApkChecklistProd(Context ctx) async {
    if (!await _requestAccess(ctx)) return;

    await ctx.reply("Сборка APK Autolab - Checklist для Prod-среды");

    await ctx.reply(
      "Скачайте сборку APK Autolab - Checklist для Prod-среды по ссылке:",
      replyMarkup: InlineKeyboard()
        .url("Скачать", "http://144.31.213.13/downloads/checklis_app/app-release.apk")
        .row()
    );
  }

  Future<void> restart() async {
    _bot.clear();
    _setup();
  }

  Future<void> start() async {
    await _bot.start();
  }
}