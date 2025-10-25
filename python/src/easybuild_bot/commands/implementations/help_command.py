"""
/help command implementation.
"""

from typing import List, Optional
from ..base import Command, CommandContext, CommandResult


class HelpCommand(Command):
    """Help command - show available commands and usage information."""
    
    def get_command_name(self) -> str:
        return "/help"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "помощь",
            "помоги",
            "помоги мне",
            "справка",
            "что ты умеешь",
            "как тебя использовать",
            "инструкция",
            "команды",
            "список команд"
        ]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has access to bot."""
        return await self._check_user_access(ctx.update, require_admin=False)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute help command."""
        message = "Help"
        await ctx.update.effective_message.reply_text(message)
        
        return CommandResult(success=True, message=message)

