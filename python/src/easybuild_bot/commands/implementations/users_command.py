"""
/users command implementation.
"""

from typing import List, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..base import Command, CommandContext, CommandResult


class UsersCommand(Command):
    """Users command - manage users (admin only)."""
    
    def get_command_name(self) -> str:
        return "/users"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "пользователи",
            "список пользователей",
            "управление пользователями",
            "показать пользователей",
            "юзеры"
        ]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has admin access."""
        return await self._check_user_access(ctx.update, require_admin=True)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute users command."""
        users = self.storage.get_all_users()
        not_allowed = [u for u in users if not u.allowed]
        
        if not not_allowed:
            message = "Все пользователи имеют доступ."
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=True, message=message)
        
        keyboard = [
            [InlineKeyboardButton(
                u.display_name or f"User {u.user_id}", 
                callback_data=f"allow_user_{u.user_id}"
            )] 
            for u in not_allowed
        ]
        
        message = "Пользователи без доступа:\nНажмите на кнопку, чтобы предоставить доступ:"
        await ctx.update.effective_message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return CommandResult(success=True, message=message)

