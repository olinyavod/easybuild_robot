"""
/projects command implementation.
"""

from typing import List
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel


class ProjectsCommand(Command):
    """Projects command - list all projects or projects for current group."""
    
    def get_command_name(self) -> str:
        return "/projects"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "проекты",
            "список проектов",
            "показать проекты",
            "какие проекты",
            "доступные проекты"
        ]
    
    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна любому авторизованному пользователю."""
        return CommandAccessLevel.USER
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute projects command."""
        chat = ctx.update.effective_chat
        user = ctx.update.effective_user
        
        # Check if user is admin
        user_obj = self.storage.get_user_by_user_id(user.id) if user else None
        is_admin = user_obj and user_obj.is_admin
        
        # Get projects based on context
        if chat and chat.type in ("group", "supergroup"):
            # In groups, show only projects available for this group
            projects = self.storage.get_projects_for_group(chat.id)
            context_msg = f"доступные для этой группы"
        elif is_admin:
            # Admins see all projects in private chat
            projects = self.storage.get_all_projects()
            context_msg = "все проекты"
        else:
            # Regular users in private chat see all projects
            projects = self.storage.get_all_projects()
            context_msg = "все проекты"
        
        if not projects:
            message = f"📋 Нет проектов ({context_msg})."
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=True, message=message)
        
        # Sort projects by name
        sorted_projects = sorted(projects, key=lambda p: p.name.lower())
        
        # Build message with project list
        message_lines = [f"📋 **Проекты ({context_msg}):**\n"]
        
        for project in sorted_projects:
            # Project type emoji
            type_emoji = {
                "flutter": "🦋",
                "dotnet_maui": "🔷",
                "xamarin": "🔶"
            }.get(project.project_type.value, "📦")
            
            project_info = [f"{type_emoji} **{project.name}**"]
            project_info.append(f"  • Тип: {project.project_type.value.replace('_', ' ').title()}")
            project_info.append(f"  • Ветка разработки: `{project.dev_branch}`")
            project_info.append(f"  • Ветка релиза: `{project.release_branch}`")
            
            if project.tags:
                project_info.append(f"  • Теги: {', '.join(f'`{tag}`' for tag in project.tags)}")
            
            if project.description:
                project_info.append(f"  • {project.description}")
            
            if is_admin:
                # Show additional info for admins
                project_info.append(f"  • ID: `{project.id}`")
                if project.allowed_group_ids:
                    project_info.append(f"  • Группы: {len(project.allowed_group_ids)} шт.")
                else:
                    project_info.append(f"  • Группы: все")
            
            message_lines.append("\n".join(project_info) + "\n")
        
        message = "\n".join(message_lines)
        
        await ctx.update.effective_message.reply_text(
            message,
            parse_mode="Markdown"
        )
        
        return CommandResult(success=True, message=message)

