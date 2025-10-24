"""
Telegram Bot handlers and main bot logic with Dependency Injection.
"""
import os
import logging
from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from .storage import Storage
from .models import BotUser, BotGroup
from .command_matcher import CommandMatcher
from .speech_recognition import SpeechRecognitionService
from .text_to_speech import TextToSpeechService

logger = logging.getLogger(__name__)

ADMIN_WAIT_TOKEN = 1


class EasyBuildBot:
    """Main bot class with dependency injection."""
    
    def __init__(
        self, 
        storage: Storage, 
        command_matcher: CommandMatcher, 
        admin_token: str,
        speech_service: Optional[SpeechRecognitionService] = None,
        tts_service: Optional[TextToSpeechService] = None
    ):
        """
        Initialize bot with dependencies.
        
        Args:
            storage: Database storage instance
            command_matcher: Command matcher instance
            admin_token: Admin token for authorization
            speech_service: Speech recognition service instance (optional)
            tts_service: Text-to-speech service instance (optional)
        """
        self.storage = storage
        self.command_matcher = command_matcher
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
        
        # Update message to show result
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
        
        # Update message to show result
        await query.edit_message_text(
            f"🔒 Пользователь {existing.display_name or existing.user_name} заблокирован!"
        )

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
    
    async def cmd_unblock_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, params: dict):
        """Handle /unblock_user command with dynamic user name extraction (admin only)."""
        if not await self.request_admin_access(update, context):
            return
        
        # Get user_name from params
        user_name = params.get("user_name")
        if not user_name:
            await update.effective_message.reply_text(
                "❌ Не удалось определить имя пользователя.\n\n"
                "Используйте формат: 'Разблокировать пользователя <Имя>'"
            )
            return
        
        # Search for users by display name
        found_users = self.storage.find_users_by_display_name(user_name)
        
        if not found_users:
            await update.effective_message.reply_text(
                f"❌ Пользователь с именем '{user_name}' не найден в системе."
            )
            return
        
        if len(found_users) == 1:
            # Only one user found - unblock directly
            user = found_users[0]
            if user.allowed:
                await update.effective_message.reply_text(
                    f"ℹ️ Пользователь {user.display_name or user.user_name} уже имеет доступ."
                )
            else:
                self.storage.update_user_allowed(user.user_id, True)
                await update.effective_message.reply_text(
                    f"✅ Пользователь {user.display_name or user.user_name} разблокирован!"
                )
        else:
            # Multiple users found - show selection keyboard
            keyboard = []
            for u in found_users:
                status = "🔓" if u.allowed else "🔒"
                button_text = f"{status} {u.display_name or u.user_name}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"unblock_{u.user_id}")])
            
            await update.effective_message.reply_text(
                f"Найдено несколько пользователей с именем '{user_name}'.\n"
                f"Выберите пользователя для разблокировки:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def cmd_block_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, params: dict):
        """Handle /block_user command with dynamic user name extraction (admin only)."""
        if not await self.request_admin_access(update, context):
            return
        
        # Get user_name from params
        user_name = params.get("user_name")
        if not user_name:
            await update.effective_message.reply_text(
                "❌ Не удалось определить имя пользователя.\n\n"
                "Используйте формат: 'Заблокировать пользователя <Имя>'"
            )
            return
        
        # Search for users by display name
        found_users = self.storage.find_users_by_display_name(user_name)
        
        if not found_users:
            await update.effective_message.reply_text(
                f"❌ Пользователь с именем '{user_name}' не найден в системе."
            )
            return
        
        if len(found_users) == 1:
            # Only one user found - block directly
            user = found_users[0]
            if not user.allowed:
                await update.effective_message.reply_text(
                    f"ℹ️ Пользователь {user.display_name or user.user_name} уже заблокирован."
                )
            else:
                self.storage.update_user_allowed(user.user_id, False)
                await update.effective_message.reply_text(
                    f"🔒 Пользователь {user.display_name or user.user_name} заблокирован!"
                )
        else:
            # Multiple users found - show selection keyboard
            keyboard = []
            for u in found_users:
                status = "🔓" if u.allowed else "🔒"
                button_text = f"{status} {u.display_name or u.user_name}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"block_{u.user_id}")])
            
            await update.effective_message.reply_text(
                f"Найдено несколько пользователей с именем '{user_name}'.\n"
                f"Выберите пользователя для блокировки:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

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
    
    async def send_voice_reply(self, message, text: str) -> bool:
        """
        Send text as voice message.
        
        Args:
            message: Message to reply to
            text: Text to convert to speech
            
        Returns:
            True if successful, False otherwise
        """
        if not self.tts_service:
            logger.warning("TTS service not available, sending text instead")
            await message.reply_text(text)
            return False
        
        try:
            # Generate audio
            audio_path = await self.tts_service.synthesize_to_temp_file(text)
            
            if audio_path:
                # Send voice message
                with open(audio_path, 'rb') as audio_file:
                    await message.reply_voice(voice=audio_file)
                
                # Clean up audio file
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
        """Handle /voice command to generate voice message from text."""
        if not await self.request_access(update, context):
            return
        
        if not self.tts_service:
            await update.effective_message.reply_text("❌ Сервис генерации речи недоступен.")
            return
        
        # Get text from command arguments
        if not context.args:
            await update.effective_message.reply_text(
                "📢 Используйте: /voice <текст>\n\n"
                "Пример: /voice Привет, это голосовое сообщение!"
            )
            return
        
        text = " ".join(context.args)
        
        # Send "processing" message
        status_msg = await update.effective_message.reply_text("🎙️ Генерирую голосовое сообщение...")
        
        try:
            # Generate audio
            audio_path = await self.tts_service.synthesize_to_temp_file(text)
            
            if audio_path:
                # Send voice message
                with open(audio_path, 'rb') as audio_file:
                    await update.effective_message.reply_voice(
                        voice=audio_file,
                        caption=f"📝 Текст: {text}"
                    )
                
                # Delete status message
                await status_msg.delete()
                
                # Clean up audio file
                try:
                    os.unlink(audio_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary audio file: {e}")
            else:
                await status_msg.edit_text("❌ Не удалось сгенерировать голосовое сообщение.")
        
        except Exception as e:
            logger.error(f"Error generating voice message: {e}", exc_info=True)
            await status_msg.edit_text("❌ Произошла ошибка при генерации голосового сообщения.")

    async def cb_build_apk_checklist_prod(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle build APK checklist prod callback."""
        if not await self.request_access(update, context):
            return
        await update.effective_message.reply_text("Сборка APK Autolab - Checklist для Prod-среды")
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Скачать", url="http://144.31.213.13/downloads/checklis_app/app-release.apk")]])
        await update.effective_message.reply_text("Скачайте сборку APK Autolab - Checklist для Prod-среды по ссылке:", reply_markup=keyboard)

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages - convert voice to text and process as command."""
        message = update.effective_message
        chat = update.effective_chat
        if not message or not message.voice or not chat:
            return
        
        # In groups respond only if bot is addressed: @username mention or reply to bot message
        if chat.type in ("group", "supergroup"):
            addressed = False
            
            # Check if it's a reply to bot message
            if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == context.bot.id:
                addressed = True
            
            # Check caption for bot mention
            if not addressed and message.caption:
                bot_username = context.bot.username
                if bot_username and f"@{bot_username.lower()}" in message.caption.lower():
                    addressed = True
            
            if not addressed:
                return
            
            # In groups when addressed, show access denied message
            if not await self.request_access(update, context, is_replay=True):
                return
        else:
            # Private chats — regular access check with response
            if not await self.request_access(update, context, is_replay=True):
                return
        
        if not self.speech_service:
            await update.effective_message.reply_text("❌ Сервис распознавания речи недоступен.")
            return
        
        # Send "processing" message
        status_msg = await message.reply_text("🎤 Распознаю голосовое сообщение...")
        
        try:
            # Get voice file
            voice_file = await context.bot.get_file(message.voice.file_id)
            
            # Transcribe voice to text
            text = await self.speech_service.transcribe_telegram_voice(voice_file)
            
            if text:
                logger.info(f"Transcribed voice message: {text}")
                
                # Delete status message
                await status_msg.delete()
                
                # Show recognized text
                await message.reply_text(f"🎤 Распознано: \"{text}\"")
                
                # Process text as command using semantic matcher
                try:
                    match_result = self.command_matcher.match_command(text)
                    
                    if match_result:
                        command, similarity, params = match_result
                        logger.info(f"Voice command recognized: {command} (similarity: {similarity:.2f}, params: {params})")
                        
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
                        elif command == "/unblock_user":
                            await self.cmd_unblock_user(update, context, params)
                        elif command == "/block_user":
                            await self.cmd_block_user(update, context, params)
                        else:
                            await message.reply_text(f"Я понял, что вы хотели выполнить команду {command}, но она пока не реализована.")
                    else:
                        await message.reply_text("❌ Не удалось распознать команду. Попробуйте использовать /help для просмотра доступных команд.")
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
        
        # In groups respond only if bot is addressed: @username mention or reply to bot message
        if chat.type in ("group", "supergroup"):
            addressed = False
            
            # Check if it's a reply to bot message
            if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == context.bot.id:
                addressed = True
            
            # Check caption for bot mention
            if not addressed and message.caption:
                bot_username = context.bot.username
                if bot_username and f"@{bot_username.lower()}" in message.caption.lower():
                    addressed = True
            
            if not addressed:
                return
            
            # In groups when addressed, show access denied message
            if not await self.request_access(update, context, is_replay=True):
                return
        else:
            # Private chats — regular access check with response
            if not await self.request_access(update, context, is_replay=True):
                return
        
        if not self.speech_service:
            await update.effective_message.reply_text("❌ Сервис распознавания речи недоступен.")
            return
        
        # Send "processing" message
        status_msg = await message.reply_text("🎵 Обрабатываю аудиосообщение...")
        
        try:
            # Get audio file
            audio_file = await context.bot.get_file(message.audio.file_id)
            
            # Transcribe
            text = await self.speech_service.transcribe_telegram_audio(audio_file)
            
            if text:
                # Delete status message
                await status_msg.delete()
                
                # Send transcribed text
                await message.reply_text(f"📝 Распознанный текст:\n\n{text}")
                
                # Process the text as a regular message
                if text.strip():
                    message.text = text
                    await self.msg_echo(update, context)
            else:
                await status_msg.edit_text("❌ Не удалось распознать речь. Попробуйте ещё раз.")
                
        except Exception as e:
            logger.error(f"Error handling audio message: {e}", exc_info=True)
            await status_msg.edit_text("❌ Произошла ошибка при обработке аудиосообщения.")


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
                command, similarity, params = match_result
                logger.info(f"Recognized command: {command} (similarity: {similarity:.2f}, params: {params})")
                
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
                elif command == "/unblock_user":
                    await self.cmd_unblock_user(update, context, params)
                elif command == "/block_user":
                    await self.cmd_block_user(update, context, params)
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

        # Echo handler for any text messages outside commands and active dialogs
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.msg_echo))


async def post_init(app: Application):
    """Post initialization hook for setting bot commands."""
    # Commands for private chats
    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Показать справку"),
        BotCommand("build", "Выбрать сборку"),
        BotCommand("voice", "🎙️ Создать голосовое сообщение"),
        BotCommand("admin", "Получить права администратора"),
        BotCommand("users", "👤 Управление пользователями (админ)"),
        BotCommand("groups", "👥 Список групп (админ)"),
    ], scope=BotCommandScopeAllPrivateChats())
    # Commands for groups
    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Показать справку"),
        BotCommand("build", "Выбрать сборку"),
        BotCommand("voice", "🎙️ Создать голосовое сообщение"),
        BotCommand("register_group", "📝 Зарегистрировать группу"),
    ], scope=BotCommandScopeAllGroupChats())

