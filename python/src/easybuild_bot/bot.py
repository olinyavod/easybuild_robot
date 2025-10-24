import os
import logging
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats, BotCommandScopeDefault
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from .storage import init_db, add_user, get_user_by_user_id, get_all_users, update_user_allowed, get_all_groups, add_group, get_group_by_group_id, update_user_admin
from .models import BotUser, BotGroup
from .command_matcher import get_command_matcher

logger = logging.getLogger(__name__)

ADMIN_WAIT_TOKEN = 1

async def request_access(update: Update, context: ContextTypes.DEFAULT_TYPE, is_replay: bool = True) -> bool:
    user = update.effective_user
    if not user:
        return False

    existing = get_user_by_user_id(user.id)
    if existing is None:
        add_user(BotUser(id=str(user.id), user_id=user.id, user_name=user.username or '', display_name=user.full_name))
        existing = get_user_by_user_id(user.id)

    if existing and existing.is_admin:
        return True

    if not existing or not existing.allowed:
        if is_replay:
            await update.effective_message.reply_text("Вы не имеете доступа к боту. Пожалуйста, обратитесь к администратору.")
        return False

    return True

async def request_admin_access(update: Update, context: ContextTypes.DEFAULT_TYPE, is_replay: bool = True) -> bool:
    user = update.effective_user
    if not user:
        return False
    existing = get_user_by_user_id(user.id)
    if existing and existing.is_admin:
        return True
    if is_replay:
        await update.effective_message.reply_text("Вы не имеете доступа к боту. Пожалуйста, обратитесь к администратору.")
    return False

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await request_access(update, context):
        return
    user = update.effective_user
    await update.effective_message.reply_text(f"Привет, {user.full_name}!")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await request_access(update, context):
        return
    await update.effective_message.reply_text("Help")

async def cmd_build(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await request_access(update, context):
        return
    keyboard = [
        [InlineKeyboardButton("Сборка APK Autolab - Checklist для Prod-среды", callback_data="build_apk_checklist_prod")],
        [InlineKeyboardButton("Сборка APK Autolab - Checklist для Dev-среды", callback_data="build_apk_checklist_dev")],
        [InlineKeyboardButton("Сборка APK TehnouprApp - Клиент для Prod-среды", callback_data="build_apk_tehnoupr_client_prod")],
        [InlineKeyboardButton("Сборка APK TehnouprApp - Клиент для Dev-среды", callback_data="build_apk_tehnoupr_client_dev")],
        [InlineKeyboardButton("Сборка APK TehnouprApp - Сотрудник для Prod-среды", callback_data="build_apk_tehnoupr_employee_prod")],
        [InlineKeyboardButton("Сборка APK TehnouprApp - Сотрудник для Dev-среды", callback_data="build_apk_tehnoupr_employee_dev")],
    ]
    await update.effective_message.reply_text("Выберите сборку:", reply_markup=InlineKeyboardMarkup(keyboard))

async def cmd_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await request_admin_access(update, context):
        return
    users = get_all_users()
    not_allowed = [u for u in users if not u.allowed]
    if not not_allowed:
        await update.effective_message.reply_text("Все пользователи имеют доступ.")
        return
    keyboard = [[InlineKeyboardButton(u.display_name or f"User {u.user_id}", callback_data=f"allow_user_{u.user_id}")] for u in not_allowed]
    await update.effective_message.reply_text("Пользователи без доступа:\nНажмите на кнопку, чтобы предоставить доступ:", reply_markup=InlineKeyboardMarkup(keyboard))

async def cb_allow_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.data:
        return
    if not await request_admin_access(update, context, is_replay=False):
        await query.answer(text="У вас нет прав администратора", show_alert=False)
        return
    if not query.data.startswith("allow_user_"):
        return
    user_id = int(query.data.split("_")[-1])
    existing = get_user_by_user_id(user_id)
    if not existing:
        await query.answer(text="Пользователь не найден", show_alert=False)
        return
    update_user_allowed(user_id, True)
    await query.answer(text="Доступ предоставлен ✅", show_alert=False)
    users = get_all_users()
    not_allowed = [u for u in users if not u.allowed]
    if not not_allowed:
        await query.edit_message_text("Все пользователи имеют доступ.")
    else:
        keyboard = [[InlineKeyboardButton(u.display_name or f"User {u.user_id}", callback_data=f"allow_user_{u.user_id}")] for u in not_allowed]
        await query.edit_message_text("Пользователи без доступа:\nНажмите на кнопку, чтобы предоставить доступ:", reply_markup=InlineKeyboardMarkup(keyboard))

async def cmd_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await request_admin_access(update, context):
        return
    groups = get_all_groups()
    if not groups:
        await update.effective_message.reply_text("Нет зарегистрированных групп.")
        return
    lines = ["📋 Зарегистрированные группы:\n"]
    for i, g in enumerate(groups, start=1):
        lines.append(f"{i}. {g.group_name}")
        lines.append(f"   ID: {g.group_id}\n")
    await update.effective_message.reply_text("\n".join(lines))

async def cmd_register_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await request_access(update, context):
        return
    chat = update.effective_chat
    if not chat:
        await update.effective_message.reply_text("Не удалось получить информацию о чате.")
        return
    group_id = chat.id
    group_title = chat.title
    if group_title is None or group_id > 0:
        await update.effective_message.reply_text("Эта команда работает только в группах.")
        return
    existing = get_group_by_group_id(group_id)
    if existing:
        await update.effective_message.reply_text(f"Эта группа уже зарегистрирована:\nID: {group_id}\nНазвание: {existing.group_name}")
        return
    add_group(BotGroup(id=str(group_id), group_id=group_id, group_name=group_title))
    await update.effective_message.reply_text(f"✅ Группа успешно зарегистрирована!\n\nID: {group_id}\nНазвание: {group_title}")

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await request_admin_access(update, context):
        return ConversationHandler.END
    await update.effective_message.reply_text("Ввведите токен от чат-бота для администратора")
    return ADMIN_WAIT_TOKEN

async def admin_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return ConversationHandler.END
    token_input = update.effective_message.text or ""
    bot_token = context.application.bot_data.get("admin_token")
    existing = get_user_by_user_id(user.id)
    if not existing:
        await update.effective_message.reply_text("Пользователь не найден!")
        return ConversationHandler.END
    if token_input != bot_token:
        await update.effective_message.reply_text("Неверный токен!")
        return ConversationHandler.END
    update_user_admin(user.id, True)
    await update.effective_message.reply_text("Вы успешно добавлены в администраторы!")
    return ConversationHandler.END

async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text("Попробуйте ещё раз!")
    return ConversationHandler.END

async def cb_build_apk_checklist_prod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await request_access(update, context):
        return
    await update.effective_message.reply_text("Сборка APK Autolab - Checklist для Prod-среды")
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Скачать", url="http://144.31.213.13/downloads/checklis_app/app-release.apk")]])
    await update.effective_message.reply_text("Скачайте сборку APK Autolab - Checklist для Prod-среды по ссылке:", reply_markup=keyboard)

async def msg_echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    if not message or not message.text or not chat:
        return
    
    # В группах отвечаем только если обратились к боту: упоминание @username или ответ на сообщение бота
    if chat.type in ("group", "supergroup"):
        addressed = False
        
        # Проверяем, это ответ на сообщение бота
        if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == context.bot.id:
            addressed = True
        
        # Проверяем упоминание по username
        if not addressed:
            bot_username = context.bot.username
            if bot_username:
                if f"@{bot_username.lower()}" in message.text.lower():
                    addressed = True
        
        # Проверяем entities (упоминания через @mention)
        if not addressed and message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                    bot_username = context.bot.username
                    if bot_username and mentioned_username.lower() == f"@{bot_username.lower()}":
                        addressed = True
                        break
        
        if not addressed:
            return
        
        # В группах при обращении показываем сообщение об отсутствии доступа
        if not await request_access(update, context, is_replay=True):
            return
    else:
        # Приватные чаты — обычная проверка доступа с ответом
        if not await request_access(update, context, is_replay=True):
            return

    # Очищаем текст от упоминания бота для анализа
    text = message.text
    bot_username = context.bot.username
    if bot_username:
        # Убираем упоминание бота из текста
        text = text.replace(f"@{bot_username}", "").strip()
    
    # Пытаемся распознать команду семантически
    try:
        matcher = get_command_matcher()
        match_result = matcher.match_command(text)
        
        if match_result:
            command, similarity = match_result
            logger.info(f"Распознана команда: {command} (схожесть: {similarity:.2f})")
            
            # Выполняем соответствующую команду
            if command == "/start":
                await cmd_start(update, context)
            elif command == "/help":
                await cmd_help(update, context)
            elif command == "/build":
                await cmd_build(update, context)
            elif command == "/register_group":
                await cmd_register_group(update, context)
            elif command == "/users":
                await cmd_users(update, context)
            elif command == "/groups":
                await cmd_groups(update, context)
            else:
                # Если команда распознана, но не реализована
                await message.reply_text(f"Я понял, что вы хотели выполнить команду {command}, но она пока не реализована.")
        else:
            # Если не удалось распознать команду
            await message.reply_text("Извините, я не понимаю вашего сообщения. Попробуйте использовать /help для просмотра доступных команд.")
    except Exception as e:
        logger.error(f"Ошибка при распознавании команды: {e}", exc_info=True)
        # В случае ошибки сообщаем о непонимании
        await message.reply_text("Извините, я не понимаю вашего сообщения. Попробуйте использовать /help для просмотра доступных команд.")

async def post_init(app: Application):
    # Команды для приватных чатов
    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Показать справку"),
        BotCommand("build", "Выбрать сборку"),
        BotCommand("admin", "Получить права администратора"),
        BotCommand("users", "👤 Управление пользователями (админ)"),
        BotCommand("groups", "👥 Список групп (админ)"),
    ], scope=BotCommandScopeAllPrivateChats())
    # Команды для групп
    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Показать справку"),
        BotCommand("build", "Выбрать сборку"),
        BotCommand("register_group", "📝 Зарегистрировать группу"),
    ], scope=BotCommandScopeAllGroupChats())


def run() -> None:
    load_dotenv()
    
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN not set")

    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    monty_dir = os.getenv("MONTYDB_DIR", os.path.join(data_dir, "monty"))
    os.makedirs(monty_dir, exist_ok=True)
    monty_db = os.getenv("MONTYDB_DB", "easybuild_bot")

    init_db(monty_dir, monty_db)

    app = Application.builder().token(token).post_init(post_init).build()
    app.bot_data["admin_token"] = token

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("build", cmd_build))
    app.add_handler(CommandHandler("users", cmd_users))
    app.add_handler(CommandHandler("groups", cmd_groups))
    app.add_handler(CommandHandler("register_group", cmd_register_group))

    app.add_handler(CallbackQueryHandler(cb_allow_user, pattern=r"^allow_user_\d+$"))
    app.add_handler(CallbackQueryHandler(cb_build_apk_checklist_prod, pattern=r"^build_apk_checklist_prod$"))

    admin_conv = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            ADMIN_WAIT_TOKEN: [MessageHandler(filters.TEXT & (~filters.COMMAND), admin_token)]
        },
        fallbacks=[MessageHandler(filters.ALL, admin_cancel)],
        allow_reentry=True,
    )
    app.add_handler(admin_conv)

    # Эхо для любых текстовых сообщений вне команд и вне активного диалога
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), msg_echo))

    app.run_polling()
