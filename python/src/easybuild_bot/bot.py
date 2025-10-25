"""
Telegram Bot with Command Pattern implementation.
"""
import os
import logging
from typing import Optional
from telegram import Update, BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from .storage import Storage
from .models import BotUser
from .commands import CommandContext, CommandRegistry, CommandExecutor
from .speech_recognition import SpeechRecognitionService
from .text_to_speech import TextToSpeechService

logger = logging.getLogger(__name__)

ADMIN_WAIT_TOKEN = 1


class EasyBuildBot:
    """
    Main bot class with Command Pattern and Dependency Injection.
    
    This version uses Command Pattern to organize bot commands,
    making it easier to add new commands and maintain the codebase.
    """
    
    def __init__(
        self, 
        storage: Storage,
        command_registry: CommandRegistry,
        command_executor: CommandExecutor,
        admin_token: str,
        speech_service: Optional[SpeechRecognitionService] = None,
        tts_service: Optional[TextToSpeechService] = None
    ):
        """
        Initialize bot with dependencies.
        
        Args:
            storage: Database storage instance
            command_registry: Command registry for command lookup
            command_executor: Command executor for running commands
            admin_token: Admin token for authorization
            speech_service: Speech recognition service instance (optional)
            tts_service: Text-to-speech service instance (optional)
        """
        self.storage = storage
        self.command_registry = command_registry
        self.command_executor = command_executor
        self.admin_token = admin_token
        self.speech_service = speech_service
        self.tts_service = tts_service
    
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
    
    async def _execute_command_by_name(self, command_name: str, update: Update, context: ContextTypes.DEFAULT_TYPE, params: dict = None) -> None:
        """
        Execute a command by its name.
        
        Args:
            command_name: Command name (e.g. "/start")
            update: Telegram update
            context: Telegram context
            params: Optional parameters dict
        """
        command = self.command_registry.get_command(command_name)
        if not command:
            logger.error(f"Command {command_name} not found in registry")
            await update.effective_message.reply_text(f"Команда {command_name} не найдена.")
            return
        
        # Create command context
        cmd_ctx = CommandContext(
            update=update,
            context=context,
            params=params or {}
        )
        
        # Execute command
        result = await self.command_executor.execute_command(command, cmd_ctx)
        
        # Handle errors
        if not result.success and result.error:
            await update.effective_message.reply_text(result.error)
    
    # Command handlers that delegate to Command Pattern
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        await self._execute_command_by_name("/start", update, context)
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        await self._execute_command_by_name("/help", update, context)
    
    async def cmd_build(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /build command."""
        await self._execute_command_by_name("/build", update, context)
    
    async def cmd_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /users command."""
        await self._execute_command_by_name("/users", update, context)
    
    async def cmd_groups(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /groups command."""
        await self._execute_command_by_name("/groups", update, context)
    
    async def cmd_register_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /register_group command."""
        await self._execute_command_by_name("/register_group", update, context)
    
    # Callback handlers (remain unchanged as they handle UI interactions)
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
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [[InlineKeyboardButton(u.display_name or f"User {u.user_id}", callback_data=f"allow_user_{u.user_id}")] for u in not_allowed]
            await query.edit_message_text("Пользователи без доступа:\nНажмите на кнопку, чтобы предоставить доступ:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def cb_unblock_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unblock user callback."""
        query = update.callback_query
        if not query or not query.data:
            return
        if not await self.request_admin_access(update, context, is_replay=False):
            await query.answer(text="У вас нет прав администратора", show_alert=False)
            return
        if not query.data.startswith("unblock_"):
            return
        
        user_id = int(query.data.split("_")[-1])
        existing = self.storage.get_user_by_user_id(user_id)
        if not existing:
            await query.answer(text="Пользователь не найден", show_alert=False)
            return
        
        if existing.allowed:
            await query.answer(text="Пользователь уже имеет доступ", show_alert=False)
        else:
            self.storage.update_user_allowed(user_id, True)
            await query.answer(text="✅ Пользователь разблокирован", show_alert=True)
        
        await query.edit_message_text(
            f"✅ Пользователь {existing.display_name or existing.user_name} разблокирован!"
        )
    
    async def cb_block_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle block user callback."""
        query = update.callback_query
        if not query or not query.data:
            return
        if not await self.request_admin_access(update, context, is_replay=False):
            await query.answer(text="У вас нет прав администратора", show_alert=False)
            return
        if not query.data.startswith("block_"):
            return
        
        user_id = int(query.data.split("_")[-1])
        existing = self.storage.get_user_by_user_id(user_id)
        if not existing:
            await query.answer(text="Пользователь не найден", show_alert=False)
            return
        
        if not existing.allowed:
            await query.answer(text="Пользователь уже заблокирован", show_alert=False)
        else:
            self.storage.update_user_allowed(user_id, False)
            await query.answer(text="🔒 Пользователь заблокирован", show_alert=True)
        
        await query.edit_message_text(
            f"🔒 Пользователь {existing.display_name or existing.user_name} заблокирован!"
        )
    
    async def cb_build_apk_checklist_prod(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle build APK checklist prod callback."""
        if not await self.request_access(update, context):
            return
        await update.effective_message.reply_text("Сборка APK Autolab - Checklist для Prod-среды")
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Скачать", url="http://144.31.213.13/downloads/checklis_app/app-release.apk")]])
        await update.effective_message.reply_text("Скачайте сборку APK Autolab - Checklist для Prod-среды по ссылке:", reply_markup=keyboard)
    
    async def send_voice_reply(self, message, text: str) -> bool:
        """Send text as voice message."""
        if not self.tts_service:
            logger.warning("TTS service not available, sending text instead")
            await message.reply_text(text)
            return False
        
        try:
            audio_path = await self.tts_service.synthesize_to_temp_file(text)
            
            if audio_path:
                with open(audio_path, 'rb') as audio_file:
                    await message.reply_voice(voice=audio_file)
                
                try:
                    os.unlink(audio_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary audio file: {e}")
                
                return True
            else:
                logger.error("Failed to generate voice message")
                await message.reply_text(text)
                return False
                
        except Exception as e:
            logger.error(f"Error sending voice reply: {e}", exc_info=True)
            await message.reply_text(text)
            return False
    
    async def cmd_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /voice command."""
        if not await self.request_access(update, context):
            return
        
        if not self.tts_service:
            await update.effective_message.reply_text("❌ Сервис генерации речи недоступен.")
            return
        
        if not context.args:
            await update.effective_message.reply_text(
                "📢 Используйте: /voice <текст>\n\n"
                "Пример: /voice Привет, это голосовое сообщение!"
            )
            return
        
        text = " ".join(context.args)
        status_msg = await update.effective_message.reply_text("🎙️ Генерирую голосовое сообщение...")
        
        try:
            audio_path = await self.tts_service.synthesize_to_temp_file(text)
            
            if audio_path:
                with open(audio_path, 'rb') as audio_file:
                    await update.effective_message.reply_voice(
                        voice=audio_file,
                        caption=f"📝 Текст: {text}"
                    )
                
                await status_msg.delete()
                
                try:
                    os.unlink(audio_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary audio file: {e}")
            else:
                await status_msg.edit_text("❌ Не удалось сгенерировать голосовое сообщение.")
        
        except Exception as e:
            logger.error(f"Error generating voice message: {e}", exc_info=True)
            await status_msg.edit_text("❌ Произошла ошибка при генерации голосового сообщения.")
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages - convert voice to text and process as command."""
        message = update.effective_message
        chat = update.effective_chat
        if not message or not message.voice or not chat:
            return
        
        # In groups respond only if bot is addressed
        if chat.type in ("group", "supergroup"):
            addressed = False
            
            if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == context.bot.id:
                addressed = True
            
            if not addressed and message.caption:
                bot_username = context.bot.username
                if bot_username and f"@{bot_username.lower()}" in message.caption.lower():
                    addressed = True
            
            if not addressed:
                return
            
            if not await self.request_access(update, context, is_replay=True):
                return
        else:
            if not await self.request_access(update, context, is_replay=True):
                return
        
        if not self.speech_service:
            await update.effective_message.reply_text("❌ Сервис распознавания речи недоступен.")
            return
        
        status_msg = await message.reply_text("🎤 Распознаю голосовое сообщение...")
        
        try:
            voice_file = await context.bot.get_file(message.voice.file_id)
            text = await self.speech_service.transcribe_telegram_voice(voice_file)
            
            if text:
                logger.info(f"Transcribed voice message: {text}")
                await status_msg.delete()
                await message.reply_text(f"🎤 Распознано: \"{text}\"")
                
                # Process using Command Pattern
                try:
                    cmd_ctx = CommandContext(
                        update=update,
                        context=context,
                        params={},
                        user_text=text
                    )
                    
                    result = await self.command_executor.match_and_execute(text, cmd_ctx)
                    
                    if not result:
                        await message.reply_text("❌ Не удалось распознать команду. Попробуйте использовать /help для просмотра доступных команд.")
                    elif not result.success and result.error:
                        # Show error message to user
                        await message.reply_text(f"❌ {result.error}")
                        
                except Exception as e:
                    logger.error(f"Error processing voice command: {e}", exc_info=True)
                    await message.reply_text("❌ Произошла ошибка при обработке команды.")
            else:
                await status_msg.edit_text("❌ Не удалось распознать речь. Попробуйте ещё раз.")
                
        except Exception as e:
            logger.error(f"Error handling voice message: {e}", exc_info=True)
            await status_msg.edit_text("❌ Произошла ошибка при обработке голосового сообщения.")
    
    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle audio messages."""
        message = update.effective_message
        chat = update.effective_chat
        if not message or not message.audio or not chat:
            return
        
        # Similar logic to handle_voice...
        if chat.type in ("group", "supergroup"):
            addressed = False
            
            if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == context.bot.id:
                addressed = True
            
            if not addressed and message.caption:
                bot_username = context.bot.username
                if bot_username and f"@{bot_username.lower()}" in message.caption.lower():
                    addressed = True
            
            if not addressed:
                return
            
            if not await self.request_access(update, context, is_replay=True):
                return
        else:
            if not await self.request_access(update, context, is_replay=True):
                return
        
        if not self.speech_service:
            await update.effective_message.reply_text("❌ Сервис распознавания речи недоступен.")
            return
        
        status_msg = await message.reply_text("🎵 Обрабатываю аудиосообщение...")
        
        try:
            audio_file = await context.bot.get_file(message.audio.file_id)
            text = await self.speech_service.transcribe_telegram_audio(audio_file)
            
            if text:
                await status_msg.delete()
                await message.reply_text(f"📝 Распознанный текст:\n\n{text}")
                
                if text.strip():
                    message.text = text
                    await self.msg_echo(update, context)
            else:
                await status_msg.edit_text("❌ Не удалось распознать речь. Попробуйте ещё раз.")
                
        except Exception as e:
            logger.error(f"Error handling audio message: {e}", exc_info=True)
            await status_msg.edit_text("❌ Произошла ошибка при обработке аудиосообщения.")
    
    async def msg_echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with semantic command recognition using Command Pattern."""
        message = update.effective_message
        chat = update.effective_chat
        if not message or not message.text or not chat:
            return
        
        # In groups respond only if bot is addressed
        if chat.type in ("group", "supergroup"):
            addressed = False
            
            if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == context.bot.id:
                addressed = True
            
            if not addressed:
                bot_username = context.bot.username
                if bot_username and f"@{bot_username.lower()}" in message.text.lower():
                    addressed = True
            
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
            
            if not await self.request_access(update, context, is_replay=True):
                return
        else:
            if not await self.request_access(update, context, is_replay=True):
                return

        # Clean text from bot mention
        text = message.text
        bot_username = context.bot.username
        if bot_username:
            text = text.replace(f"@{bot_username}", "").strip()
        
        # Use Command Pattern for command matching and execution
        try:
            cmd_ctx = CommandContext(
                update=update,
                context=context,
                params={},
                user_text=text
            )
            
            result = await self.command_executor.match_and_execute(text, cmd_ctx)
            
            if not result:
                await message.reply_text("Извините, я не понимаю вашего сообщения. Попробуйте использовать /help для просмотра доступных команд.")
            elif not result.success and result.error:
                # Show error message to user
                await message.reply_text(f"❌ {result.error}")
                
        except Exception as e:
            logger.error(f"Error recognizing command: {e}", exc_info=True)
            await message.reply_text("Извините, я не понимаю вашего сообщения. Попробуйте использовать /help для просмотра доступных команд.")
    
    # Admin conversation handlers (remain unchanged)
    async def admin_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command."""
        if await self.request_admin_access(update, context):
            return ConversationHandler.END
        await update.effective_message.reply_text("Введите токен от чат-бота для администратора")
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
    
    def setup_handlers(self, app: Application) -> None:
        """Setup all handlers for the application."""
        app.add_handler(CommandHandler("start", self.cmd_start))
        app.add_handler(CommandHandler("help", self.cmd_help))
        app.add_handler(CommandHandler("build", self.cmd_build))
        app.add_handler(CommandHandler("voice", self.cmd_voice))
        app.add_handler(CommandHandler("users", self.cmd_users))
        app.add_handler(CommandHandler("groups", self.cmd_groups))
        app.add_handler(CommandHandler("register_group", self.cmd_register_group))

        app.add_handler(CallbackQueryHandler(self.cb_allow_user, pattern=r"^allow_user_\d+$"))
        app.add_handler(CallbackQueryHandler(self.cb_unblock_user, pattern=r"^unblock_\d+$"))
        app.add_handler(CallbackQueryHandler(self.cb_block_user, pattern=r"^block_\d+$"))
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

        # Voice and audio message handlers
        app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        app.add_handler(MessageHandler(filters.AUDIO, self.handle_audio))

        # Echo handler for text messages
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.msg_echo))


async def post_init(app: Application):
    """Post initialization hook for setting bot commands."""
    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Показать справку"),
        BotCommand("build", "Выбрать сборку"),
        BotCommand("voice", "🎙️ Создать голосовое сообщение"),
        BotCommand("admin", "Получить права администратора"),
        BotCommand("users", "👤 Управление пользователями (админ)"),
        BotCommand("groups", "👥 Список групп (админ)"),
    ], scope=BotCommandScopeAllPrivateChats())
    
    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Показать справку"),
        BotCommand("build", "Выбрать сборку"),
        BotCommand("voice", "🎙️ Создать голосовое сообщение"),
        BotCommand("register_group", "📝 Зарегистрировать группу"),
    ], scope=BotCommandScopeAllGroupChats())

