"""
Telegram Bot handlers and main bot logic with Dependency Injection.
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from .storage import Storage
from .models import BotUser, BotGroup
from .command_matcher import CommandMatcher

logger = logging.getLogger(__name__)

ADMIN_WAIT_TOKEN = 1


class EasyBuildBot:
    """Main bot class with dependency injection."""
    
    def __init__(self, storage: Storage, command_matcher: CommandMatcher, admin_token: str):
        """
        Initialize bot with dependencies.
        
        Args:
            storage: Database storage instance
            command_matcher: Command matcher instance
            admin_token: Admin token for authorization
        """
        self.storage = storage
        self.command_matcher = command_matcher
        self.admin_token = admin_token
    
    async def request_access(self, update: Update, context: ContextTypes.DEFAULT_TYPE, is_replay: bool = True) -> bool:
        """Check user access to bot."""
        user = update.effective_user
        if not user:
            return False

        existing = self.storage.get_user_by_user_id(user.id)
        if existing is None:
            self.storage.add_user(BotUser(
                id=str(user.id),
                user_id=user.id,
                user_name=user.username or '',
                display_name=user.full_name
            ))
            existing = self.storage.get_user_by_user_id(user.id)

        if existing and existing.is_admin:
            return True

        if not existing or not existing.allowed:
            if is_replay:
                await update.effective_message.reply_text("Вы не имеете доступа к боту. Пожалуйста, обратитесь к администратору.")
            return False

        return True

    async def request_admin_access(self, update: Update, context: ContextTypes.DEFAULT_TYPE, is_replay: bool = True) -> bool:
        """Check admin access."""
        user = update.effective_user
        if not user:
            return False
        existing = self.storage.get_user_by_user_id(user.id)
        if existing and existing.is_admin:
            return True
        if is_replay:
            await update.effective_message.reply_text("Вы не имеете доступа к боту. Пожалуйста, обратитесь к администратору.")
        return False

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        if not await self.request_access(update, context):
            return
        user = update.effective_user
        await update.effective_message.reply_text(f"Привет, {user.full_name}!")

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        if not await self.request_access(update, context):
            return
        await update.effective_message.reply_text("Help")

    async def cmd_build(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /build command."""
        if not await self.request_access(update, context):
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

    async def cmd_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /users command (admin only)."""
        if not await self.request_admin_access(update, context):
            return
        users = self.storage.get_all_users()
        not_allowed = [u for u in users if not u.allowed]
        if not not_allowed:
            await update.effective_message.reply_text("Все пользователи имеют доступ.")
            return
        keyboard = [[InlineKeyboardButton(u.display_name or f"User {u.user_id}", callback_data=f"allow_user_{u.user_id}")] for u in not_allowed]
        await update.effective_message.reply_text("Пользователи без доступа:\nНажмите на кнопку, чтобы предоставить доступ:", reply_markup=InlineKeyboardMarkup(keyboard))

    async def cb_allow_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle allow user callback."""
        query = update.callback_query
        if not query or not query.data:
            return
        if not await self.request_admin_access(update, context, is_replay=False):
            await query.answer(text="У вас нет прав администратора", show_alert=False)
            return
        if not query.data.startswith("allow_user_"):
            return
        user_id = int(query.data.split("_")[-1])
        existing = self.storage.get_user_by_user_id(user_id)
        if not existing:
            await query.answer(text="Пользователь не найден", show_alert=False)
            return
        self.storage.update_user_allowed(user_id, True)
        await query.answer(text="Доступ предоставлен ✅", show_alert=False)
        users = self.storage.get_all_users()
        not_allowed = [u for u in users if not u.allowed]
        if not not_allowed:
            await query.edit_message_text("Все пользователи имеют доступ.")
        else:
            keyboard = [[InlineKeyboardButton(u.display_name or f"User {u.user_id}", callback_data=f"allow_user_{u.user_id}")] for u in not_allowed]
            await query.edit_message_text("Пользователи без доступа:\nНажмите на кнопку, чтобы предоставить доступ:", reply_markup=InlineKeyboardMarkup(keyboard))

    async def cmd_groups(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /groups command (admin only)."""
        if not await self.request_admin_access(update, context):
            return
        groups = self.storage.get_all_groups()
        if not groups:
            await update.effective_message.reply_text("Нет зарегистрированных групп.")
            return
        lines = ["📋 Зарегистрированные группы:\n"]
        for i, g in enumerate(groups, start=1):
            lines.append(f"{i}. {g.group_name}")
            lines.append(f"   ID: {g.group_id}\n")
        await update.effective_message.reply_text("\n".join(lines))

    async def cmd_register_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /register_group command."""
        if not await self.request_access(update, context):
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
        existing = self.storage.get_group_by_group_id(group_id)
        if existing:
            await update.effective_message.reply_text(f"Эта группа уже зарегистрирована:\nID: {group_id}\nНазвание: {existing.group_name}")
            return
        self.storage.add_group(BotGroup(id=str(group_id), group_id=group_id, group_name=group_title))
        await update.effective_message.reply_text(f"✅ Группа успешно зарегистрирована!\n\nID: {group_id}\nНазвание: {group_title}")

    async def admin_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command."""
        if await self.request_admin_access(update, context):
            return ConversationHandler.END
        await update.effective_message.reply_text("Ввведите токен от чат-бота для администратора")
        return ADMIN_WAIT_TOKEN

    async def admin_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin token input."""
        user = update.effective_user
        if not user:
            return ConversationHandler.END
        token_input = update.effective_message.text or ""
        existing = self.storage.get_user_by_user_id(user.id)
        if not existing:
            await update.effective_message.reply_text("Пользователь не найден!")
            return ConversationHandler.END
        if token_input != self.admin_token:
            await update.effective_message.reply_text("Неверный токен!")
            return ConversationHandler.END
        self.storage.update_user_admin(user.id, True)
        await update.effective_message.reply_text("Вы успешно добавлены в администраторы!")
        return ConversationHandler.END

    async def admin_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin cancel."""
        await update.effective_message.reply_text("Попробуйте ещё раз!")
        return ConversationHandler.END

    async def cb_build_apk_checklist_prod(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle build APK checklist prod callback."""
        if not await self.request_access(update, context):
            return
        await update.effective_message.reply_text("Сборка APK Autolab - Checklist для Prod-среды")
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Скачать", url="http://144.31.213.13/downloads/checklis_app/app-release.apk")]])
        await update.effective_message.reply_text("Скачайте сборку APK Autolab - Checklist для Prod-среды по ссылке:", reply_markup=keyboard)

    async def msg_echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with semantic command recognition."""
        message = update.effective_message
        chat = update.effective_chat
        if not message or not message.text or not chat:
            return
        
        # In groups respond only if bot is addressed: @username mention or reply to bot message
        if chat.type in ("group", "supergroup"):
            addressed = False
            
            # Check if it's a reply to bot message
            if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == context.bot.id:
                addressed = True
            
            # Check mention by username
            if not addressed:
                bot_username = context.bot.username
                if bot_username:
                    if f"@{bot_username.lower()}" in message.text.lower():
                        addressed = True
            
            # Check entities (mentions via @mention)
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
            
            # In groups when addressed, show access denied message
            if not await self.request_access(update, context, is_replay=True):
                return
        else:
            # Private chats — regular access check with response
            if not await self.request_access(update, context, is_replay=True):
                return

        # Clean text from bot mention for analysis
        text = message.text
        bot_username = context.bot.username
        if bot_username:
            # Remove bot mention from text
            text = text.replace(f"@{bot_username}", "").strip()
        
        # Try to recognize command semantically
        try:
            match_result = self.command_matcher.match_command(text)
            
            if match_result:
                command, similarity = match_result
                logger.info(f"Recognized command: {command} (similarity: {similarity:.2f})")
                
                # Execute corresponding command
                if command == "/start":
                    await self.cmd_start(update, context)
                elif command == "/help":
                    await self.cmd_help(update, context)
                elif command == "/build":
                    await self.cmd_build(update, context)
                elif command == "/register_group":
                    await self.cmd_register_group(update, context)
                elif command == "/users":
                    await self.cmd_users(update, context)
                elif command == "/groups":
                    await self.cmd_groups(update, context)
                else:
                    # If command recognized but not implemented
                    await message.reply_text(f"Я понял, что вы хотели выполнить команду {command}, но она пока не реализована.")
            else:
                # If failed to recognize command
                await message.reply_text("Извините, я не понимаю вашего сообщения. Попробуйте использовать /help для просмотра доступных команд.")
        except Exception as e:
            logger.error(f"Error recognizing command: {e}", exc_info=True)
            # In case of error, report misunderstanding
            await message.reply_text("Извините, я не понимаю вашего сообщения. Попробуйте использовать /help для просмотра доступных команд.")

    def setup_handlers(self, app: Application) -> None:
        """Setup all handlers for the application."""
        app.add_handler(CommandHandler("start", self.cmd_start))
        app.add_handler(CommandHandler("help", self.cmd_help))
        app.add_handler(CommandHandler("build", self.cmd_build))
        app.add_handler(CommandHandler("users", self.cmd_users))
        app.add_handler(CommandHandler("groups", self.cmd_groups))
        app.add_handler(CommandHandler("register_group", self.cmd_register_group))

        app.add_handler(CallbackQueryHandler(self.cb_allow_user, pattern=r"^allow_user_\d+$"))
        app.add_handler(CallbackQueryHandler(self.cb_build_apk_checklist_prod, pattern=r"^build_apk_checklist_prod$"))

        admin_conv = ConversationHandler(
            entry_points=[CommandHandler("admin", self.admin_start)],
            states={
                ADMIN_WAIT_TOKEN: [MessageHandler(filters.TEXT & (~filters.COMMAND), self.admin_token)]
            },
            fallbacks=[MessageHandler(filters.ALL, self.admin_cancel)],
            allow_reentry=True,
        )
        app.add_handler(admin_conv)

        # Echo handler for any text messages outside commands and active dialogs
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.msg_echo))


async def post_init(app: Application):
    """Post initialization hook for setting bot commands."""
    # Commands for private chats
    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Показать справку"),
        BotCommand("build", "Выбрать сборку"),
        BotCommand("admin", "Получить права администратора"),
        BotCommand("users", "👤 Управление пользователями (админ)"),
        BotCommand("groups", "👥 Список групп (админ)"),
    ], scope=BotCommandScopeAllPrivateChats())
    # Commands for groups
    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Показать справку"),
        BotCommand("build", "Выбрать сборку"),
        BotCommand("register_group", "📝 Зарегистрировать группу"),
    ], scope=BotCommandScopeAllGroupChats())

