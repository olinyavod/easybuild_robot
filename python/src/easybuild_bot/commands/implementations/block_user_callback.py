"""
Callback command for blocking user.
"""

from ..callback_base import CallbackCommand
from ..base import CommandContext, CommandResult, CommandAccessLevel


class BlockUserCallbackCommand(CallbackCommand):
    """Handle block_user callback - block user access."""
    
    def get_command_name(self) -> str:
        return "callback:block_user"
    
    def get_callback_pattern(self) -> str:
        return r"^block_\d+$"
    
    def get_access_level(self) -> CommandAccessLevel:
        """Callback доступен только админу."""
        return CommandAccessLevel.ADMIN
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute block user callback."""
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
        
        # Block user
        if not existing.allowed:
            await query.answer(text="Пользователь уже заблокирован", show_alert=False)
        else:
            self.storage.update_user_allowed(user_id, False)
            await query.answer(text="🔒 Пользователь заблокирован", show_alert=True)
        
        # Update message
        await query.edit_message_text(
            f"🔒 Пользователь {existing.display_name or existing.user_name} заблокирован!"
        )
        
        return CommandResult(
            success=True,
            message=f"User {existing.display_name or existing.user_name} blocked"
        )

