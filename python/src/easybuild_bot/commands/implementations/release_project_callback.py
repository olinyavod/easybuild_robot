"""
Callback command for release project selection.
"""

from typing import Optional
from ..callback_base import CallbackCommand
from ..base import CommandContext, CommandResult, CommandAccessLevel


class ReleaseProjectCallbackCommand(CallbackCommand):
    """Handle release project selection callbacks."""
    
    def get_command_name(self) -> str:
        return "callback:release_project"
    
    def get_callback_pattern(self) -> str:
        return r"^release_project:.*$"
    
    def get_access_level(self) -> CommandAccessLevel:
        """Callback доступен авторизованным пользователям."""
        return CommandAccessLevel.USER
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """
        Переопределяем стандартную проверку доступа.
        Нужна дополнительная проверка, что проект разрешен для группы.
        """
        # Сначала базовая проверка доступа
        has_access, error_msg = await super().can_execute(ctx)
        
        if not has_access:
            return False, error_msg
        
        # Проверка разрешений на проект для группы
        query = ctx.update.callback_query
        if query and query.data:
            # Extract project ID from callback data
            parts = query.data.split(":", 1)
            if len(parts) == 2:
                project_id = parts[1]
                project = self.storage.get_project_by_id(project_id)
                
                # Check if called from group
                chat = ctx.update.effective_chat
                if chat and chat.type in ("group", "supergroup"):
                    # Verify project is allowed for this group
                    if project and chat.id not in project.allowed_group_ids:
                        return False, "Этот проект недоступен для данной группы"
        
        return True, None
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute release project selection callback."""
        query = ctx.update.callback_query
        if not query or not query.data:
            return CommandResult(success=False, error="Invalid callback query")
        
        # Extract project ID from callback data
        parts = query.data.split(":", 1)
        if len(parts) != 2:
            await query.answer(text="Неверный формат данных", show_alert=True)
            return CommandResult(success=False, error="Invalid callback data format")
        
        project_id = parts[1]
        
        # Get project from database
        project = self.storage.get_project_by_id(project_id)
        if not project:
            await query.answer(text="Проект не найден", show_alert=True)
            return CommandResult(success=False, error="Project not found")
        
        # Answer callback to remove loading state
        await query.answer()
        
        # Delete the message with project selection
        try:
            await query.message.delete()
        except Exception:
            pass
        
        # Store project in context for version input step
        ctx.context.user_data['release_project'] = project
        
        # Get current version
        from ...version_services import VersionServiceFactory
        version_service = VersionServiceFactory.create(project)
        
        if not version_service:
            error_msg = f"❌ Тип проекта {project.project_type.value} не поддерживается"
            await ctx.update.effective_message.reply_text(error_msg)
            return CommandResult(success=False, error=error_msg)
        
        # Get current version from release branch
        current_version = await self._get_current_version_from_release(project, version_service)
        
        emoji = {
            "flutter": "🦋",
            "dotnet_maui": "🔷",
            "xamarin": "🔶"
        }.get(project.project_type.value, "📦")
        
        if current_version:
            # Auto-calculate next version
            next_version = version_service.increment_version(current_version, increment_type='patch')
            
            message = (
                f"🚀 **Релиз проекта:** {emoji} {project.name}\n\n"
                f"📦 **Текущая версия:** `{current_version}`\n"
                f"🆕 **Рекомендуемая версия:** `{next_version}`\n\n"
                f"💡 Введите новую версию в формате `X.Y.Z`\n"
                f"_(например: `1.2.3`)_\n\n"
                f"Или отправьте `/cancel` для отмены."
            )
        else:
            message = (
                f"🚀 **Релиз проекта:** {emoji} {project.name}\n\n"
                f"⚠️ Не удалось определить текущую версию\n\n"
                f"💡 Введите версию в формате `X.Y.Z`\n"
                f"_(например: `1.0.0`)_\n\n"
                f"Или отправьте `/cancel` для отмены."
            )
        
        await ctx.update.effective_message.reply_text(message, parse_mode='Markdown')
        
        return CommandResult(success=True, message="Waiting for version input")
    
    async def _get_current_version_from_release(self, project, version_service):
        """Get current version from release branch."""
        import subprocess
        
        repo_path = project.local_repo_path
        
        try:
            # Switch to release branch
            result = subprocess.run(
                ["git", "-C", repo_path, "checkout", project.release_branch],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                return None
            
            # Pull latest changes
            subprocess.run(
                ["git", "-C", repo_path, "pull", "origin", project.release_branch],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Get version
            version = await version_service.get_current_version(project)
            return version
        except Exception:
            return None

