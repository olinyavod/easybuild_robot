"""
/help command implementation.
"""

from typing import List
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel


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
    
    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна любому авторизованному пользователю."""
        return CommandAccessLevel.USER
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute help command."""
        message = "Help"
        await ctx.update.effective_message.reply_text(message)
        
        return CommandResult(success=True, message=message)


