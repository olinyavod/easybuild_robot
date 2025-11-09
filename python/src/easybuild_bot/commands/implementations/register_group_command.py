"""
/register_group command implementation.
"""

from typing import List, Optional
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel


class RegisterGroupCommand(Command):
    """Register group command - register current group for notifications."""
    
    def get_command_name(self) -> str:
        return "/register_group"
    
    def get_semantic_tags(self) -> List[str]:
        return [
            "зарегистрировать группу",
            "регистрация группы",
            "добавить группу",
            "зарегистрировать чат",
            "добавить чат"
        ]
    
    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна авторизованным пользователям."""
        return CommandAccessLevel.USER
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """
        Переопределяем стандартную проверку доступа.
        Нужна дополнительная проверка, что команда выполняется в группе.
        """
        # Сначала базовая проверка доступа
        has_access, error_msg = await super().can_execute(ctx)
        
        if not has_access:
            return False, error_msg
        
        # Проверка, что команда в группе
        chat = ctx.update.effective_chat
        if not chat or chat.id > 0:
            return False, "Эта команда работает только в группах."
        
        return True, None
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute register group command."""
        from ...models import BotGroup
        
        chat = ctx.update.effective_chat
        if not chat or not chat.title:
            return CommandResult(
                success=False,
                error="Не удалось получить информацию о чате."
            )
        
        group_id = chat.id
        group_title = chat.title
        
        existing = self.storage.get_group_by_group_id(group_id)
        if existing:
            message = f"Эта группа уже зарегистрирована:\nID: {group_id}\nНазвание: {existing.group_name}"
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=True, message=message)
        
        self.storage.add_group(BotGroup(
            id=str(group_id),
            group_id=group_id,
            group_name=group_title
        ))
        
        message = f"✅ Группа успешно зарегистрирована!\n\nID: {group_id}\nНазвание: {group_title}"
        await ctx.update.effective_message.reply_text(message)
        
        return CommandResult(success=True, message=message)

