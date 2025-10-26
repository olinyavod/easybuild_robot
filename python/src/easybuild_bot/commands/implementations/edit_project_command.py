"""
/edit_project command implementation.
"""

from typing import List, Optional
from ..base import Command, CommandContext, CommandResult


class EditProjectCommand(Command):
    """Edit project command - edit project settings (admin only)."""
    
    def get_command_name(self) -> str:
        return "/edit_project"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "редактировать проект",
            "изменить проект",
            "настроить проект",
            "обновить проект"
        ]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has admin access."""
        return await self._check_user_access(ctx.update, require_admin=True)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute edit project command."""
        # Parse command arguments
        # Format: /edit_project <name> <field> <value>
        
        if not ctx.context.args or len(ctx.context.args) < 2:
            usage_msg = (
                "📝 **Использование команды /edit_project:**\n\n"
                "```\n"
                "/edit_project <название> <поле> <значение>\n"
                "```\n\n"
                "**Доступные поля:**\n"
                "• `description` - описание проекта\n"
                "• `dev_branch` - ветка разработки\n"
                "• `release_branch` - ветка релиза\n"
                "• `tags` - теги (через запятую)\n"
                "• `groups` - ID групп (через запятую, пусто = все группы)\n"
                "• `git_url` - ссылка на git репозиторий\n"
                "• `project_file_path` - путь к файлу проекта\n"
                "• `local_repo_path` - локальный путь к репозиторию\n\n"
                "**Примеры:**\n"
                "```\n"
                "/edit_project MyApp description Мое приложение для Android\n"
                "/edit_project MyApp tags mobile,android,prod\n"
                "/edit_project MyApp groups -1001234567890,-1009876543210\n"
                "/edit_project MyApp dev_branch feature/new-ui\n"
                "/edit_project MyApp groups  # очистить группы (доступ для всех)\n"
                "```"
            )
            await ctx.update.effective_message.reply_text(usage_msg, parse_mode="Markdown")
            return CommandResult(success=False, error="Недостаточно параметров")
        
        name = ctx.context.args[0]
        field = ctx.context.args[1].lower()
        value = " ".join(ctx.context.args[2:]) if len(ctx.context.args) > 2 else ""
        
        # Get project
        project = self.storage.get_project_by_name(name)
        if not project:
            error_msg = f"❌ Проект `{name}` не найден!"
            await ctx.update.effective_message.reply_text(error_msg, parse_mode="Markdown")
            return CommandResult(success=False, error=f"Проект {name} не найден")
        
        # Update field
        try:
            if field == "description":
                project.description = value if value else None
            elif field == "dev_branch":
                project.dev_branch = value
            elif field == "release_branch":
                project.release_branch = value
            elif field == "tags":
                # Parse comma-separated tags
                project.tags = [tag.strip() for tag in value.split(",") if tag.strip()]
            elif field == "groups":
                # Parse comma-separated group IDs
                if value.strip():
                    try:
                        project.allowed_group_ids = [int(gid.strip()) for gid in value.split(",") if gid.strip()]
                    except ValueError:
                        error_msg = "❌ Неверный формат ID групп. Используйте числа через запятую."
                        await ctx.update.effective_message.reply_text(error_msg)
                        return CommandResult(success=False, error="Неверный формат ID групп")
                else:
                    # Empty value means all groups
                    project.allowed_group_ids = []
            elif field == "git_url":
                project.git_url = value
            elif field == "project_file_path":
                project.project_file_path = value
            elif field == "local_repo_path":
                project.local_repo_path = value
            else:
                error_msg = (
                    f"❌ Неизвестное поле: `{field}`\n\n"
                    "Доступные поля: `description`, `dev_branch`, `release_branch`, `tags`, `groups`, "
                    "`git_url`, `project_file_path`, `local_repo_path`"
                )
                await ctx.update.effective_message.reply_text(error_msg, parse_mode="Markdown")
                return CommandResult(success=False, error=f"Неизвестное поле: {field}")
            
            # Save changes
            self.storage.add_project(project)
            
            # Build success message
            success_msg = (
                f"✅ **Проект `{name}` обновлен!**\n\n"
                f"**Поле:** `{field}`\n"
                f"**Новое значение:**\n"
            )
            
            if field == "tags":
                success_msg += f"`{', '.join(project.tags) if project.tags else 'нет тегов'}`"
            elif field == "groups":
                if project.allowed_group_ids:
                    success_msg += f"`{', '.join(str(gid) for gid in project.allowed_group_ids)}`"
                else:
                    success_msg += "`все группы`"
            else:
                success_msg += f"`{value if value else 'пусто'}`"
            
            await ctx.update.effective_message.reply_text(success_msg, parse_mode="Markdown")
            
            return CommandResult(success=True, message=f"Проект {name} обновлен")
            
        except Exception as e:
            error_msg = f"❌ Ошибка при обновлении проекта: {str(e)}"
            await ctx.update.effective_message.reply_text(error_msg)
            return CommandResult(success=False, error=str(e))

