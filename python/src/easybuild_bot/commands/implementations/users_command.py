"""
/users command implementation.
"""

from typing import List
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel


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
    
    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна только админу в личном чате."""
        return CommandAccessLevel.ADMIN
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute users command."""
        users = self.storage.get_all_users()
        
        if not users:
            message = "📋 Список пользователей пуст."
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=True, message=message)
        
        # Sort users: admins first, then by access status, then by display name
        sorted_users = sorted(
            users, 
            key=lambda u: (
                not u.is_admin,  # Admins first
                not u.allowed,   # Allowed users next
                u.display_name or u.user_name or ""
            )
        )
        
        # Build message with user list and their statuses
        message_lines = ["📋 **Список пользователей:**\n"]
        
        for user in sorted_users:
            user_name = user.display_name or user.user_name or f"User {user.user_id}"
            
            # Status indicators
            status_icons = []
            if user.is_admin:
                status_icons.append("👑 Администратор")
            if user.allowed:
                status_icons.append("✅ Доступ разрешен")
            else:
                status_icons.append("🔒 Доступ запрещен")
            
            status_text = " | ".join(status_icons)
            message_lines.append(f"• **{user_name}**\n  {status_text}\n")
        
        message = "\n".join(message_lines)
        
        await ctx.update.effective_message.reply_text(
            message,
            parse_mode="Markdown"
        )
        
        return CommandResult(success=True, message=message)

