"""
Callback command for build APK actions.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..callback_base import CallbackCommand
from ..base import CommandContext, CommandResult, CommandAccessLevel


class BuildApkCallbackCommand(CallbackCommand):
    """Handle build APK callbacks - provide download links for builds."""
    
    def get_command_name(self) -> str:
        return "callback:build_apk"
    
    def get_callback_pattern(self) -> str:
        return r"^build_apk_.*$"
    
    def get_access_level(self) -> CommandAccessLevel:
        """Callback доступен авторизованным пользователям."""
        return CommandAccessLevel.USER
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute build APK callback."""
        query = ctx.update.callback_query
        if not query or not query.data:
            return CommandResult(success=False, error="Invalid callback query")
        
        # Map callback data to build info
        build_configs = {
            "build_apk_checklist_prod": {
                "name": "APK Autolab - Checklist для Prod-среды",
                "url": "http://144.31.213.13/downloads/checklis_app/app-release.apk"
            },
            "build_apk_checklist_dev": {
                "name": "APK Autolab - Checklist для Dev-среды",
                "url": "http://144.31.213.13/downloads/checklis_app/app-debug.apk"
            },
            "build_apk_tehnoupr_client_prod": {
                "name": "APK TehnouprApp - Клиент для Prod-среды",
                "url": "http://144.31.213.13/downloads/tehnoupr_client/app-release.apk"
            },
            "build_apk_tehnoupr_client_dev": {
                "name": "APK TehnouprApp - Клиент для Dev-среды",
                "url": "http://144.31.213.13/downloads/tehnoupr_client/app-debug.apk"
            },
            "build_apk_tehnoupr_employee_prod": {
                "name": "APK TehnouprApp - Сотрудник для Prod-среды",
                "url": "http://144.31.213.13/downloads/tehnoupr_employee/app-release.apk"
            },
            "build_apk_tehnoupr_employee_dev": {
                "name": "APK TehnouprApp - Сотрудник для Dev-среды",
                "url": "http://144.31.213.13/downloads/tehnoupr_employee/app-debug.apk"
            },
        }
        
        build_info = build_configs.get(query.data)
        if not build_info:
            await query.answer(text="Неизвестная сборка", show_alert=True)
            return CommandResult(success=False, error="Unknown build")
        
        # Answer callback to remove loading state
        await query.answer()
        
        # Send build information with download button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Скачать", url=build_info['url'])]
        ])
        
        await ctx.update.effective_message.reply_text(
            f"📦 **{build_info['name']}**\n\nНажмите кнопку ниже, чтобы скачать сборку:",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        return CommandResult(
            success=True,
            message=f"Build info sent: {build_info['name']}"
        )

