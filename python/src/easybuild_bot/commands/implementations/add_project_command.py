"""
/add_project command implementation with step-by-step wizard.
"""

import uuid
from typing import List
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel
from ...models import Project, ProjectType


class AddProjectCommand(Command):
    """Add project command - add a new project (admin only) using step-by-step wizard."""

    def get_command_name(self) -> str:
        return "/add_project"

    def get_semantic_tags(self) -> List[str]:
        return [
            "добавить новый проект",
            "создать новый проект",
            "зарегистрировать новый проект",
            "добавление нового проекта"
        ]

    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна только админу в личном чате."""
        return CommandAccessLevel.ADMIN

    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute add project command - starts the wizard."""
        welcome_msg = (
            "🎯 *Мастер создания проекта*\n\n"
            "Я помогу вам создать новый проект шаг за шагом\\.\n"
            "В любой момент вы можете отменить процесс командой /cancel\\.\n\n"
            "Давайте начнём\\! 📝"
        )
        await ctx.update.effective_message.reply_text(welcome_msg, parse_mode="MarkdownV2")

        return CommandResult(success=True, message="Wizard started")


def escape_md(text: str) -> str:
    """Escape special characters for MarkdownV2."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text
