"""
Command for setting release version (version <value>).
"""

import re
from typing import List, Optional
from ..base import Command, CommandContext, CommandResult
from ...builders import ProjectBuilderFactory


class VersionCommand(Command):
    """Version command - set release version for project."""
    
    def get_command_name(self) -> str:
        return "/version"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "version",
            "версия",
            "версию",
            "установить версию",
        ]
    
    def get_parameter_patterns(self) -> dict:
        """Pattern to match version number."""
        return {
            "version": [
                r"version\s+([0-9]+\.[0-9]+\.[0-9]+(?:\+[0-9]+)?)",
                r"версия\s+([0-9]+\.[0-9]+\.[0-9]+(?:\+[0-9]+)?)",
            ]
        }
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has access."""
        return await self._check_user_access(ctx.update, require_admin=False)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute version command."""
        version = ctx.params.get("version")
        
        if not version:
            message = (
                "❌ Неверный формат команды.\n\n"
                "Использование: `version <номер>`\n"
                "Пример: `version 1.2.3+45`"
            )
            await ctx.update.effective_message.reply_text(
                message,
                parse_mode='Markdown'
            )
            return CommandResult(success=False, error="Missing version parameter")
        
        # For now, just show confirmation - real implementation would need project context
        await ctx.update.effective_message.reply_text(
            f"✅ Версия распознана: {version}\n\n"
            f"Эта команда работает в контексте подготовки релиза.\n"
            f"Используйте кнопку '📦 Подготовить релиз' для запуска процесса."
        )
        
        return CommandResult(success=True, message=f"Version recognized: {version}")




