"""
/build command implementation.
"""

from typing import List, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..base import Command, CommandContext, CommandResult


class BuildCommand(Command):
    """Build command - show build options based on available projects."""
    
    def get_command_name(self) -> str:
        return "/build"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "сборка",
            "сборки",
            "покажи сборки",
            "выбрать сборку",
            "собрать",
            "билд",
            "собрать apk",
            "сборка приложения",
            "создать сборку"
        ]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has access to bot."""
        return await self._check_user_access(ctx.update, require_admin=False)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute build command - show projects based on context."""
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
            message = f"📋 Нет доступных проектов для сборки ({context_msg})."
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=True, message=message)
        
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
            callback_data = f"build_project:{project.id}"
            
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        message = f"🔨 Выберите проект для сборки ({context_msg}):"
        await ctx.update.effective_message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return CommandResult(success=True, message=message)

