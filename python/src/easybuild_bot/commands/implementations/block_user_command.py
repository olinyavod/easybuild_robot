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
        # Команда недоступна для голосового управления
        return []

    def get_parameter_patterns(self) -> Dict[str, List[str]]:
        # Команда недоступна для голосового управления
        return {}

    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна только админу в личном чате."""
        return CommandAccessLevel.ADMIN

    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute block user command."""
        # Get user_name from params
        user_name = ctx.params.get("user_name")

        if not user_name:
            # No name specified - show all unblocked users for selection
            all_users = self.storage.get_all_users()
            found_users = [u for u in all_users if u.allowed]  # Only unblocked users

            if not found_users:
                message = "ℹ️ Нет разблокированных пользователей для блокировки."
                await ctx.update.effective_message.reply_text(message)
                return CommandResult(success=False, error=message)
        else:
            # Search for users by display name
            found_users = self.storage.find_users_by_display_name(user_name)
            # Filter to show only unblocked users
            found_users = [u for u in found_users if u.allowed]

            if not found_users:
                message = f"❌ Разблокированный пользователь с именем '{user_name}' не найден в системе."
                await ctx.update.effective_message.reply_text(message)
                return CommandResult(success=False, error=message)

        if len(found_users) == 1 and user_name:
            # Only one user found with specific name - block directly
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
            # Multiple users or no name specified - show selection keyboard
            keyboard = []
            for u in found_users:
                button_text = f"🔓 {u.display_name or u.user_name}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"block_{u.user_id}")])

            if user_name:
                message = (
                    f"Найдено несколько пользователей с именем '{user_name}'.\n"
                    f"Выберите пользователя для блокировки:"
                )
            else:
                message = "Выберите пользователя для блокировки:"

            await ctx.update.effective_message.reply_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            return CommandResult(success=True, message=message)
