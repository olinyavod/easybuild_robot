"""
/delete_project command implementation.
"""

from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel


class DeleteProjectCommand(Command):
    """Delete project command - delete a project (admin only)."""

    def get_command_name(self) -> str:
        return "/delete_project"

    def get_semantic_tags(self) -> List[str]:
        return [
            "удалить проект из списка",
            "удаление проекта из базы",
            "стереть проект полностью",
            "убрать проект из системы"
        ]

    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна только админу в личном чате."""
        return CommandAccessLevel.ADMIN

    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute delete project command."""
        # Get all projects
        projects = self.storage.get_all_projects()

        if not projects:
            message = "📋 Нет проектов для удаления."
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=True, message=message)

        # Sort projects by name
        sorted_projects = sorted(projects, key=lambda p: p.name.lower())

        # Build inline keyboard with project list
        keyboard = []
        for project in sorted_projects:
            # Project type emoji
            type_emoji = {
                "flutter": "🦋",
                "dotnet_maui": "🔷",
                "xamarin": "🔶"
            }.get(project.project_type.value, "📦")

            button_text = f"{type_emoji} {project.name}"
            callback_data = f"delete_project:{project.id}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        # Add cancel button
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="delete_project_cancel")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            "🗑️ **Удаление проекта**\n\n"
            "Выберите проект для удаления:\n\n"
            "⚠️ **Внимание:** Это действие нельзя отменить!"
        )

        await ctx.update.effective_message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

        return CommandResult(success=True, message="Показан список проектов для удаления")
