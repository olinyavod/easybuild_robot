"""
/start command implementation.
"""

from typing import List, Optional
from ..base import Command, CommandContext, CommandResult


class StartCommand(Command):
    """Start command - greet user and initialize bot interaction."""
    
    def get_command_name(self) -> str:
        return "/start"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "начать",
            "начать работу",
            "начать работу с ботом",
            "привет",
            "приветствие",
            "старт",
            "здравствуй",
            "добрый день"
        ]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has access to bot."""
        return await self._check_user_access(ctx.update, require_admin=False)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute start command."""
        user = ctx.update.effective_user
        if not user:
            return CommandResult(
                success=False,
                error="Не удалось определить пользователя"
            )
        
        message = f"Привет, {user.full_name}!"
        await ctx.update.effective_message.reply_text(message)
        
        return CommandResult(success=True, message=message)

