"""
/edit_project command implementation.
"""

from typing import List, Optional, Dict
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
    
    def get_parameter_patterns(self) -> Dict[str, List[str]]:
        """Get regex patterns for parameter extraction from voice commands."""
        return {
            "project_name": [
                r"(?:редактировать|изменить|настроить|обновить)\s+проект\s+([А-Яа-яЁёA-Za-z0-9_\-]+)",
                r"проект\s+([А-Яа-яЁёA-Za-z0-9_\-]+)",
            ]
        }
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has admin access."""
        return await self._check_user_access(ctx.update, require_admin=True)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute edit project command."""
        # Parse command arguments
        # For voice commands, check params first
        # For text commands, use context.args
        
        # Try to get arguments from context.args (for /edit_project command)
        if ctx.context.args and len(ctx.context.args) >= 2:
            name = ctx.context.args[0]
            field = ctx.context.args[1].lower()
            value = " ".join(ctx.context.args[2:]) if len(ctx.context.args) > 2 else ""
        # Try to get from params (for voice commands)
        elif ctx.params.get("project_name"):
            name = ctx.params.get("project_name")
            # For voice commands, show interactive menu (not implemented yet)
            error_msg = (
                "❌ Голосовое редактирование проекта пока не поддерживается.\n\n"
                "Используйте команду:\n"
                "/edit_project <название> <поле> <значение>\n\n"
                f"Найден проект: {name}\n\n"
                "Или используйте интерактивный мастер: /edit_project_wizard"
            )
            await ctx.update.effective_message.reply_text(error_msg)
            return CommandResult(success=False, error="Голосовое редактирование пока не поддерживается")
        else:
            usage_msg = (
                "📝 Использование команды /edit_project:\n\n"
                "/edit_project <название> <поле> <значение>\n\n"
                "Доступные поля:\n"
                "• name - название проекта\n"
                "• description - описание проекта\n"
                "• dev_branch - ветка разработки\n"
                "• release_branch - ветка релиза\n"
                "• tags - теги (через запятую)\n"
                "• groups - ID групп (через запятую, пусто = все группы)\n"
                "• git_url - ссылка на git репозиторий\n"
                "• project_file_path - путь к файлу проекта\n\n"
                "Примеры:\n"
                "/edit_project MyApp name NewAppName\n"
                "/edit_project MyApp description Мое приложение для Android\n"
                "/edit_project MyApp tags mobile,android,prod\n"
                "/edit_project MyApp groups -1001234567890,-1009876543210\n"
                "/edit_project MyApp dev_branch feature/new-ui\n\n"
                "ℹ️ Для удобного редактирования используйте: /edit_project_wizard"
            )
            await ctx.update.effective_message.reply_text(usage_msg)
            return CommandResult(success=False, error="Недостаточно параметров")
        
        # Get project
        project = self.storage.get_project_by_name(name)
        if not project:
            error_msg = f"❌ Проект {name} не найден!"
            await ctx.update.effective_message.reply_text(error_msg)
            return CommandResult(success=False, error=f"Проект {name} не найден")
        
        # Update field
        try:
            if field == "name":
                # Validate that name is not empty
                if not value or not value.strip():
                    error_msg = "❌ Название проекта не может быть пустым!"
                    await ctx.update.effective_message.reply_text(error_msg)
                    return CommandResult(success=False, error="Пустое название проекта")
                
                # Check if name already exists (excluding current project)
                existing_project = self.storage.get_project_by_name(value)
                if existing_project and existing_project.id != project.id:
                    error_msg = f"❌ Проект с названием '{value}' уже существует! Выберите другое название."
                    await ctx.update.effective_message.reply_text(error_msg)
                    return CommandResult(success=False, error=f"Проект {value} уже существует")
                
                project.name = value.strip()
            elif field == "description":
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
                # This is a system-managed field, but we allow it for backward compatibility
                error_msg = (
                    "⚠️ Внимание: local_repo_path - служебное поле, управляемое системой автоматически.\n\n"
                    "Изменение этого поля может привести к проблемам с работой системы. "
                    "Рекомендуется использовать только другие поля для редактирования проекта."
                )
                await ctx.update.effective_message.reply_text(error_msg)
                return CommandResult(success=False, error="local_repo_path - служебное поле")
            else:
                error_msg = (
                    f"❌ Неизвестное поле: {field}\n\n"
                    "Доступные поля: name, description, dev_branch, release_branch, tags, groups, "
                    "git_url, project_file_path\n\n"
                    "ℹ️ Поле local_repo_path является служебным и управляется системой автоматически."
                )
                await ctx.update.effective_message.reply_text(error_msg)
                return CommandResult(success=False, error=f"Неизвестное поле: {field}")
            
            # Save changes
            self.storage.add_project(project)
            
            # Build success message
            success_msg = (
                f"✅ Проект '{name}' обновлен!\n\n"
                f"Поле: {field}\n"
                f"Новое значение:\n"
            )
            
            if field == "tags":
                success_msg += f"{', '.join(project.tags) if project.tags else 'нет тегов'}"
            elif field == "groups":
                if project.allowed_group_ids:
                    success_msg += f"{', '.join(str(gid) for gid in project.allowed_group_ids)}"
                else:
                    success_msg += "все группы"
            else:
                success_msg += f"{value if value else 'пусто'}"
            
            await ctx.update.effective_message.reply_text(success_msg)
            
            return CommandResult(success=True, message=f"Проект {name} обновлен")
            
        except Exception as e:
            error_msg = f"❌ Ошибка при обновлении проекта: {str(e)}"
            await ctx.update.effective_message.reply_text(error_msg)
            return CommandResult(success=False, error=str(e))

