"""
/block_user command implementation.
"""

from typing import List, Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel


class BlockUserCommand(Command):
    """Block user command - block user by name (admin only)."""
    
    def get_command_name(self) -> str:
        return "/block_user"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "заблокировать пользователя",
            "заблокировать",
            "отключить пользователя",
            "запретить доступ",
            "деактивировать пользователя",
            "заблокировать юзера"
        ]
    
    def get_parameter_patterns(self) -> Dict[str, List[str]]:
        return {
            "user_name": [
                # With "пользователь" (any ending) or "юзер" (any ending) specified
                r"(?:заблокировать|отключить|запретить доступ|деактивировать)\s+(?:пользовател(?:ь|я|ю|ем|и|е)|юзер(?:а|у|ом|е)?)\s+([А-Яа-яЁёA-Za-z0-9\s]+?)(?:\s*$|[.,!?])",
                # Without "пользователя" - name directly after verb
                r"(?:заблокировать|отключить|деактивировать)\s+([А-Яа-яЁёA-Za-z0-9\s]+?)(?:\s*$|[.,!?])",
                # "запретить доступ" + name (without "пользователя")
                r"запретить\s+доступ\s+([А-Яа-яЁёA-Za-z0-9\s]+?)(?:\s*$|[.,!?])",
                # Reverse order: name + verb
                r"([А-Яа-яЁёA-Za-z0-9\s]+?)\s+(?:заблокировать|отключить|деактивировать)"
            ]
        }
    
    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна только админу в личном чате."""
        return CommandAccessLevel.ADMIN
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute block user command."""
        # Get user_name from params
        user_name = ctx.params.get("user_name")
        if not user_name:
            message = (
                "❌ Не удалось определить имя пользователя.\n\n"
                "Используйте формат: 'Заблокировать пользователя <Имя>'"
            )
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=False, error=message)
        
        # Search for users by display name
        found_users = self.storage.find_users_by_display_name(user_name)
        
        if not found_users:
            message = f"❌ Пользователь с именем '{user_name}' не найден в системе."
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=False, error=message)
        
        if len(found_users) == 1:
            # Only one user found - block directly
            user = found_users[0]
            if not user.allowed:
                message = f"ℹ️ Пользователь {user.display_name or user.user_name} уже заблокирован."
                await ctx.update.effective_message.reply_text(message)
            else:
                self.storage.update_user_allowed(user.user_id, False)
                message = f"🔒 Пользователь {user.display_name or user.user_name} заблокирован!"
                await ctx.update.effective_message.reply_text(message)
            
            return CommandResult(success=True, message=message)
        else:
            # Multiple users found - show selection keyboard
            keyboard = []
            for u in found_users:
                status = "🔓" if u.allowed else "🔒"
                button_text = f"{status} {u.display_name or u.user_name}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"block_{u.user_id}")])
            
            message = (
                f"Найдено несколько пользователей с именем '{user_name}'.\n"
                f"Выберите пользователя для блокировки:"
            )
            await ctx.update.effective_message.reply_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            return CommandResult(success=True, message=message)

