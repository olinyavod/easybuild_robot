"""
Callback command for allowing user access.
"""

from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..callback_base import CallbackCommand
from ..base import CommandContext, CommandResult


class AllowUserCallbackCommand(CallbackCommand):
    """Handle allow_user callback - grant access to blocked user."""
    
    def get_command_name(self) -> str:
        return "callback:allow_user"
    
    def get_callback_pattern(self) -> str:
        return r"^allow_user_\d+$"
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has admin access."""
        return await self._check_user_access(ctx.update, require_admin=True)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute allow user callback."""
        query = ctx.update.callback_query
        if not query or not query.data:
            return CommandResult(success=False, error="Invalid callback query")
        
        # Extract user_id from callback data
        user_id = int(query.data.split("_")[-1])
        
        # Get user from database
        existing = self.storage.get_user_by_user_id(user_id)
        if not existing:
            await query.answer(text="Пользователь не найден", show_alert=False)
            return CommandResult(success=False, error="User not found")
        
        # Grant access
        self.storage.update_user_allowed(user_id, True)
        await query.answer(text="Доступ предоставлен ✅", show_alert=False)
        
        # Update message with new list of blocked users
        users = self.storage.get_all_users()
        not_allowed = [u for u in users if not u.allowed]
        
        if not not_allowed:
            await query.edit_message_text("Все пользователи имеют доступ.")
        else:
            keyboard = [
                [InlineKeyboardButton(
                    u.display_name or f"User {u.user_id}", 
                    callback_data=f"allow_user_{u.user_id}"
                )] 
                for u in not_allowed
            ]
            await query.edit_message_text(
                "Пользователи без доступа:\nНажмите на кнопку, чтобы предоставить доступ:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        return CommandResult(
            success=True, 
            message=f"Access granted to user {existing.display_name or existing.user_name}"
        )

