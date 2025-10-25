"""
/delete_project command implementation.
"""

from typing import List, Optional
from ..base import Command, CommandContext, CommandResult


class DeleteProjectCommand(Command):
    """Delete project command - delete a project (admin only)."""
    
    def get_command_name(self) -> str:
        return "/delete_project"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "удалить проект",
            "удаление проекта",
            "стереть проект",
            "убрать проект"
        ]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has admin access."""
        return await self._check_user_access(ctx.update, require_admin=True)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute delete project command."""
        # Parse command arguments
        # Format: /delete_project <name>
        
        if not ctx.context.args or len(ctx.context.args) < 1:
            usage_msg = (
                "📝 **Использование команды /delete_project:**\n\n"
                "```\n"
                "/delete_project <название>\n"
                "```\n\n"
                "**Пример:**\n"
                "```\n"
                "/delete_project MyApp\n"
                "```\n\n"
                "⚠️ **Внимание:** Это действие нельзя отменить!"
            )
            await ctx.update.effective_message.reply_text(usage_msg, parse_mode="Markdown")
            return CommandResult(success=False, error="Не указано название проекта")
        
        name = " ".join(ctx.context.args)
        
        # Get project
        project = self.storage.get_project_by_name(name)
        if not project:
            error_msg = f"❌ Проект `{name}` не найден!"
            await ctx.update.effective_message.reply_text(error_msg, parse_mode="Markdown")
            return CommandResult(success=False, error=f"Проект {name} не найден")
        
        # Delete project
        success = self.storage.delete_project(project.id)
        
        if success:
            success_msg = (
                f"🗑️ **Проект `{name}` успешно удален!**\n\n"
                f"**Тип:** {project.project_type.value.replace('_', ' ').title()}\n"
                f"**Git URL:** `{project.git_url}`\n"
                f"**ID:** `{project.id}`"
            )
            await ctx.update.effective_message.reply_text(success_msg, parse_mode="Markdown")
            return CommandResult(success=True, message=f"Проект {name} удален")
        else:
            error_msg = f"❌ Не удалось удалить проект `{name}`!"
            await ctx.update.effective_message.reply_text(error_msg, parse_mode="Markdown")
            return CommandResult(success=False, error=f"Не удалось удалить проект {name}")

