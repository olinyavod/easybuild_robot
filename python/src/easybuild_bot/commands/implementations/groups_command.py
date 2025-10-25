"""
/groups command implementation.
"""

from typing import List, Optional
from ..base import Command, CommandContext, CommandResult


class GroupsCommand(Command):
    """Groups command - list registered groups (admin only)."""
    
    def get_command_name(self) -> str:
        return "/groups"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "группы",
            "список групп",
            "показать группы",
            "зарегистрированные группы",
            "чаты"
        ]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has admin access."""
        return await self._check_user_access(ctx.update, require_admin=True)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute groups command."""
        groups = self.storage.get_all_groups()
        
        if not groups:
            message = "Нет зарегистрированных групп."
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=True, message=message)
        
        lines = ["📋 Зарегистрированные группы:\n"]
        for i, g in enumerate(groups, start=1):
            lines.append(f"{i}. {g.group_name}")
            lines.append(f"   ID: {g.group_id}\n")
        
        message = "\n".join(lines)
        await ctx.update.effective_message.reply_text(message)
        
        return CommandResult(success=True, message=message)

