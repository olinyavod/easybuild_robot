"""
/build command implementation.
"""

from typing import List, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..base import Command, CommandContext, CommandResult


class BuildCommand(Command):
    """Build command - show build options."""
    
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
        """Execute build command."""
        keyboard = [
            [InlineKeyboardButton("Сборка APK Autolab - Checklist для Prod-среды", callback_data="build_apk_checklist_prod")],
            [InlineKeyboardButton("Сборка APK Autolab - Checklist для Dev-среды", callback_data="build_apk_checklist_dev")],
            [InlineKeyboardButton("Сборка APK TehnouprApp - Клиент для Prod-среды", callback_data="build_apk_tehnoupr_client_prod")],
            [InlineKeyboardButton("Сборка APK TehnouprApp - Клиент для Dev-среды", callback_data="build_apk_tehnoupr_client_dev")],
            [InlineKeyboardButton("Сборка APK TehnouprApp - Сотрудник для Prod-среды", callback_data="build_apk_tehnoupr_employee_prod")],
            [InlineKeyboardButton("Сборка APK TehnouprApp - Сотрудник для Dev-среды", callback_data="build_apk_tehnoupr_employee_dev")],
        ]
        
        message = "Выберите сборку:"
        await ctx.update.effective_message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return CommandResult(success=True, message=message)

