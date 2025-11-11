"""
Callback command for project deletion with confirmation.
"""

from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..callback_base import CallbackCommand
from ..base import CommandContext, CommandResult, CommandAccessLevel


class DeleteProjectCallbackCommand(CallbackCommand):
    """Handle delete project callbacks with confirmation."""

    def get_command_name(self) -> str:
        return "delete_project_callback"

    def get_callback_pattern(self) -> str:
        """Pattern for delete project callbacks."""
        return r"^(delete_project:|delete_project_confirm:|delete_project_cancel).*"

    def get_access_level(self) -> CommandAccessLevel:
        """Callback доступен только админу."""
        return CommandAccessLevel.ADMIN

    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user can execute this callback."""
        # Check admin access
        can_exec, error_msg = await self._check_user_access(ctx.update, require_admin=True)
        if not can_exec:
            return False, error_msg

        return True, None

    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute delete project callback."""
        query = ctx.update.callback_query
        if not query or not query.data:
            return CommandResult(success=False, error="Invalid callback query")

        # Handle cancel
        if query.data == "delete_project_cancel":
            await query.answer()
            try:
                await query.message.delete()
            except Exception:
                pass
            await ctx.update.effective_message.reply_text("❌ Удаление отменено.")
            return CommandResult(success=True, message="Deletion cancelled")

        # Handle project selection (show confirmation)
        if query.data.startswith("delete_project:") and not query.data.startswith("delete_project_confirm:"):
            # Extract project ID
            project_id = query.data.split(":", 1)[1]

            # Get project from database
            project = self.storage.get_project_by_id(project_id)
            if not project:
                await query.answer(text="Проект не найден", show_alert=True)
                return CommandResult(success=False, error="Project not found")

            await query.answer()

            # Show confirmation message
            confirmation_msg = (
                f"⚠️ **Подтверждение удаления**\n\n"
                f"Вы уверены, что хотите удалить проект?\n\n"
                f"📝 **Название:** `{project.name}`\n"
                f"📦 **Тип:** {project.project_type.value.replace('_', ' ').title()}\n"
                f"🔗 **Git URL:** `{project.git_url}`\n"
                f"📁 **Файл проекта:** `{project.project_file_path}`\n"
                f"💾 **Локальный путь:** `{project.local_repo_path}`\n\n"
                f"⚠️ **Это действие нельзя отменить!**"
            )

            keyboard = [
                [
                    InlineKeyboardButton("✅ Да, удалить", callback_data=f"delete_project_confirm:{project_id}"),
                    InlineKeyboardButton("❌ Отмена", callback_data="delete_project_cancel")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            try:
                await query.message.edit_text(
                    confirmation_msg,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
            except Exception:
                # If edit fails, send new message
                await ctx.update.effective_message.reply_text(
                    confirmation_msg,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )

            return CommandResult(success=True, message="Confirmation shown")

        # Handle confirmation (delete project)
        if query.data.startswith("delete_project_confirm:"):
            # Extract project ID
            project_id = query.data.split(":", 1)[1]

            # Get project from database
            project = self.storage.get_project_by_id(project_id)
            if not project:
                await query.answer(text="Проект не найден", show_alert=True)
                return CommandResult(success=False, error="Project not found")

            # Delete project
            success = self.storage.delete_project(project_id)

            await query.answer()

            # Delete the confirmation message
            try:
                await query.message.delete()
            except Exception:
                pass

            if success:
                success_msg = (
                    f"🗑️ **Проект `{project.name}` успешно удален!**\n\n"
                    f"**Тип:** {project.project_type.value.replace('_', ' ').title()}\n"
                    f"**Git URL:** `{project.git_url}`\n"
                    f"**ID:** `{project.id}`"
                )
                await ctx.update.effective_message.reply_text(success_msg, parse_mode="Markdown")
                return CommandResult(success=True, message=f"Проект {project.name} удален")
            else:
                error_msg = f"❌ Не удалось удалить проект `{project.name}`!"
                await ctx.update.effective_message.reply_text(error_msg, parse_mode="Markdown")
                return CommandResult(success=False, error=f"Не удалось удалить проект {project.name}")

        return CommandResult(success=False, error="Unknown callback action")



