"""
/unblock_user command implementation.
"""

from typing import List, Optional, Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..base import Command, CommandContext, CommandResult


class UnblockUserCommand(Command):
    """Unblock user command - unblock user by name (admin only)."""
    
    def get_command_name(self) -> str:
        return "/unblock_user"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "разблокировать пользователя",
            "разблокировать",
            "дать доступ пользователю",
            "предоставить доступ",
            "активировать пользователя",
            "включить пользователя",
            "разблокировать юзера"
        ]
    
    def get_parameter_patterns(self) -> Dict[str, List[str]]:
        return {
            "user_name": [
                # With "пользователь" (any ending) or "юзер" (any ending) specified
                r"(?:разблокировать|дать доступ|предоставить доступ|активировать|включить)\s+(?:пользовател(?:ь|я|ю|ем|и|е)|юзер(?:а|у|ом|е)?)\s+([А-Яа-яЁёA-Za-z0-9\s]+?)(?:\s*$|[.,!?])",
                # Without "пользователя" - name directly after verb
                r"(?:разблокировать|активировать|включить)\s+([А-Яа-яЁёA-Za-z0-9\s]+?)(?:\s*$|[.,!?])",
                # "дать/предоставить доступ" + name (without "пользователя")
                r"(?:дать|предоставить)\s+доступ\s+([А-Яа-яЁёA-Za-z0-9\s]+?)(?:\s*$|[.,!?])",
                # Reverse order: name + verb
                r"([А-Яа-яЁёA-Za-z0-9\s]+?)\s+(?:разблокировать|дать доступ|активировать)"
            ]
        }
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has admin access."""
        return await self._check_user_access(ctx.update, require_admin=True)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute unblock user command."""
        # Get user_name from params
        user_name = ctx.params.get("user_name")
        if not user_name:
            message = (
                "❌ Не удалось определить имя пользователя.\n\n"
                "Используйте формат: 'Разблокировать пользователя <Имя>'"
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
            # Only one user found - unblock directly
            user = found_users[0]
            if user.allowed:
                message = f"ℹ️ Пользователь {user.display_name or user.user_name} уже имеет доступ."
                await ctx.update.effective_message.reply_text(message)
            else:
                self.storage.update_user_allowed(user.user_id, True)
                message = f"✅ Пользователь {user.display_name or user.user_name} разблокирован!"
                await ctx.update.effective_message.reply_text(message)
            
            return CommandResult(success=True, message=message)
        else:
            # Multiple users found - show selection keyboard
            keyboard = []
            for u in found_users:
                status = "🔓" if u.allowed else "🔒"
                button_text = f"{status} {u.display_name or u.user_name}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"unblock_{u.user_id}")])
            
            message = (
                f"Найдено несколько пользователей с именем '{user_name}'.\n"
                f"Выберите пользователя для разблокировки:"
            )
            await ctx.update.effective_message.reply_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            return CommandResult(success=True, message=message)

