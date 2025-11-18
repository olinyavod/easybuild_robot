"""
/unblock_user command implementation.
"""

from typing import List, Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel


class UnblockUserCommand(Command):
    """Unblock user command - unblock user by name (admin only)."""

    def get_command_name(self) -> str:
        return "/unblock_user"

    def get_semantic_tags(self) -> List[str]:
        # Команда недоступна для голосового управления
        return []

    def get_parameter_patterns(self) -> Dict[str, List[str]]:
        # Команда недоступна для голосового управления
        return {}

    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна только админу в личном чате."""
        return CommandAccessLevel.ADMIN

    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute unblock user command."""
        # Get user_name from params
        user_name = ctx.params.get("user_name")

        if not user_name:
            # No name specified - show all blocked users for selection
            all_users = self.storage.get_all_users()
            found_users = [u for u in all_users if not u.allowed]  # Only blocked users

            if not found_users:
                message = "ℹ️ Нет заблокированных пользователей для разблокировки."
                await ctx.update.effective_message.reply_text(message)
                return CommandResult(success=False, error=message)
        else:
            # Search for users by display name
            found_users = self.storage.find_users_by_display_name(user_name)
            # Filter to show only blocked users
            found_users = [u for u in found_users if not u.allowed]

            if not found_users:
                message = f"❌ Заблокированный пользователь с именем '{user_name}' не найден в системе."
                await ctx.update.effective_message.reply_text(message)
                return CommandResult(success=False, error=message)

        if len(found_users) == 1 and user_name:
            # Only one user found with specific name - unblock directly
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
            # Multiple users or no name specified - show selection keyboard
            keyboard = []
            for u in found_users:
                button_text = f"🔒 {u.display_name or u.user_name}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"unblock_{u.user_id}")])

            if user_name:
                message = (
                    f"Найдено несколько пользователей с именем '{user_name}'.\n"
                    f"Выберите пользователя для разблокировки:"
                )
            else:
                message = "Выберите пользователя для разблокировки:"

            await ctx.update.effective_message.reply_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            return CommandResult(success=True, message=message)
