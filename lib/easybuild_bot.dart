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
    _bot.use(createConversation("requestAdmin", _admin));
    _bot.command('admin', (ctx) async {
      await ctx.conversation.enter('requestAdmin');
    });
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

  Future<void> _users(Context ctx) async {
    if (!await _requestAdminAccess(ctx)) return;

    for (final user in await _usersService.getAllUsers()) {
      await ctx.reply("${user.displayName} - ${user.allowed}");
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

  Future<void> restart() async {
    _bot.clear();
    _setup();
  }

  Future<void> start() async {
    await _bot.start();
  }
}