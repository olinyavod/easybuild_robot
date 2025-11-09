"""
/release command implementation - build with custom version.
"""

from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel

# Conversation states
WAITING_VERSION = 1


class ReleaseCommand(Command):
    """Release command - build with custom version specification."""
    
    def get_command_name(self) -> str:
        return "/release"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "релиз",
            "сборка с версией",
            "выпустить релиз",
            "создать релиз",
            "релиз версия"
        ]
    
    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна любому авторизованному пользователю."""
        return CommandAccessLevel.USER
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute release command - show projects based on context."""
        chat = ctx.update.effective_chat
        
        # Get projects based on context
        if chat and chat.type in ("group", "supergroup"):
            # In groups, show only projects available for this group
            projects = self.storage.get_projects_for_group(chat.id)
            context_msg = "для этой группы"
        else:
            # In private chat, show all projects
            projects = self.storage.get_all_projects()
            context_msg = "все доступные"
        
        if not projects:
            message = f"📋 Нет доступных проектов для релиза ({context_msg})."
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=True, message=message)
        
        # If only one project - proceed to version input
        if len(projects) == 1:
            project = projects[0]
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
        
        # Sort projects by name
        sorted_projects = sorted(projects, key=lambda p: p.name.lower())
        
        # Build keyboard with projects
        keyboard = []
        for project in sorted_projects:
            # Create button with project name and type emoji
            emoji = {
                "flutter": "🦋",
                "dotnet_maui": "🔷",
                "xamarin": "🔶"
            }.get(project.project_type.value, "📦")
            
            button_text = f"{emoji} {project.name}"
            callback_data = f"release_project:{project.id}"
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        message = f"🚀 Выберите проект для релиза ({context_msg}):"
        await ctx.update.effective_message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return CommandResult(success=True, message=message)
    
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

