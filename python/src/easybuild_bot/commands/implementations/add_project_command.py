"""
/add_project command implementation.
"""

import uuid
from typing import List, Optional
from ..base import Command, CommandContext, CommandResult
from ...models import Project, ProjectType


class AddProjectCommand(Command):
    """Add project command - add a new project (admin only)."""
    
    def get_command_name(self) -> str:
        return "/add_project"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "добавить проект",
            "создать проект",
            "новый проект",
            "добавление проекта"
        ]
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has admin access."""
        return await self._check_user_access(ctx.update, require_admin=True)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute add project command."""
        # Parse command arguments
        # Format: /add_project <name> <type> <git_url> <project_file_path> <local_repo_path> [dev_branch] [release_branch]
        
        if not ctx.context.args or len(ctx.context.args) < 5:
            usage_msg = (
                "📝 *Использование команды /add\\_project:*\n\n"
                "/add\\_project \\[название\\] \\[тип\\] \\[git\\_url\\] \\[путь\\] \\[локальный\\_путь\\] \\[dev\\_ветка\\] \\[release\\_ветка\\]\n\n"
                "*Типы проектов:*\n"
                "• `flutter` \\- Flutter проект\n"
                "• `dotnet_maui` \\- \\.NET MAUI проект\n"
                "• `xamarin` \\- Xamarin проект\n\n"
                "*Пример:*\n"
                "`/add_project MyApp flutter https://github.com/user/myapp.git android/app /home/repos/myapp develop main`\n\n"
                "Если ветки не указаны, будут использованы значения по умолчанию: `develop` и `main`"
            )
            await ctx.update.effective_message.reply_text(usage_msg, parse_mode="MarkdownV2")
            return CommandResult(success=False, error="Недостаточно параметров")
        
        name = ctx.context.args[0]
        project_type_str = ctx.context.args[1].lower()
        git_url = ctx.context.args[2]
        project_file_path = ctx.context.args[3]
        local_repo_path = ctx.context.args[4]
        dev_branch = ctx.context.args[5] if len(ctx.context.args) > 5 else "develop"
        release_branch = ctx.context.args[6] if len(ctx.context.args) > 6 else "main"
        
        # Validate project type
        try:
            if project_type_str == "flutter":
                project_type = ProjectType.FLUTTER
            elif project_type_str in ("dotnet_maui", "maui"):
                project_type = ProjectType.DOTNET_MAUI
            elif project_type_str == "xamarin":
                project_type = ProjectType.XAMARIN
            else:
                error_msg = (
                    f"❌ Неизвестный тип проекта: `{project_type_str}`\n\n"
                    "Допустимые типы: `flutter`, `dotnet_maui` \\(или `maui`\\), `xamarin`"
                )
                await ctx.update.effective_message.reply_text(error_msg, parse_mode="MarkdownV2")
                return CommandResult(success=False, error=f"Неизвестный тип проекта: {project_type_str}")
        except Exception as e:
            error_msg = f"❌ Ошибка при определении типа проекта: {str(e)}"
            await ctx.update.effective_message.reply_text(error_msg)
            return CommandResult(success=False, error=str(e))
        
        # Check if project with this name already exists
        existing = self.storage.get_project_by_name(name)
        if existing:
            error_msg = f"❌ Проект с именем `{name}` уже существует\\!"
            await ctx.update.effective_message.reply_text(error_msg, parse_mode="MarkdownV2")
            return CommandResult(success=False, error=f"Проект {name} уже существует")
        
        # Create new project
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
            project_type=project_type,
            git_url=git_url,
            project_file_path=project_file_path,
            local_repo_path=local_repo_path,
            dev_branch=dev_branch,
            release_branch=release_branch,
            allowed_group_ids=[],  # Empty means available for all groups
            tags=[],
            description=None
        )
        
        # Save to database
        self.storage.add_project(project)
        
        # Build success message
        type_emoji = {
            ProjectType.FLUTTER: "🦋",
            ProjectType.DOTNET_MAUI: "🔷",
            ProjectType.XAMARIN: "🔶"
        }.get(project_type, "📦")
        
        # Escape special characters for MarkdownV2
        def escape_md(text):
            special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for char in special_chars:
                text = text.replace(char, f'\\{char}')
            return text
        
        success_msg = (
            f"✅ *Проект успешно создан\\!*\n\n"
            f"{type_emoji} *Название:* {escape_md(name)}\n"
            f"📦 *Тип:* {escape_md(project_type.value.replace('_', ' ').title())}\n"
            f"🔗 *Git URL:* `{escape_md(git_url)}`\n"
            f"📁 *Файл проекта:* `{escape_md(project_file_path)}`\n"
            f"💾 *Локальный путь:* `{escape_md(local_repo_path)}`\n"
            f"🌿 *Ветка разработки:* `{escape_md(dev_branch)}`\n"
            f"🚀 *Ветка релиза:* `{escape_md(release_branch)}`\n"
            f"🆔 *ID:* `{escape_md(project.id)}`\n\n"
            f"Используйте `/edit\\_project {escape_md(name)}` для редактирования проекта\\."
        )
        
        await ctx.update.effective_message.reply_text(success_msg, parse_mode="MarkdownV2")
        
        return CommandResult(success=True, message=f"Проект {name} создан")

