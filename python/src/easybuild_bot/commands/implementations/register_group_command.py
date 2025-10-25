"""
/register_group command implementation.
"""

from typing import List, Optional
from ..base import Command, CommandContext, CommandResult


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
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has access and command is in a group."""
        has_access, error_msg = await self._check_user_access(ctx.update, require_admin=False)
        
        if not has_access:
            return False, error_msg
        
        # Check if in a group
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

