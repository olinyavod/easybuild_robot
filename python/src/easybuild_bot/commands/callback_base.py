"""
Base class for callback query handlers using Command Pattern.
"""

from abc import ABC, abstractmethod
from typing import Optional
from telegram import Update
from .base import Command, CommandContext, CommandResult


class CallbackCommand(Command):
    """
    Base class for commands that handle callback queries.
    
    Callback commands respond to inline keyboard button presses.
    """
    
    @abstractmethod
    def get_callback_pattern(self) -> str:
        """
        Get the callback data pattern this command handles.
        
        Returns:
            Regex pattern for matching callback_query.data
        """
        pass
    
    def get_semantic_tags(self):
        """
        Callback commands don't need semantic tags.
        They are triggered by callback_query.data patterns.
        """
        return []
    
    async def execute_callback(self, query, ctx: CommandContext) -> CommandResult:
        """
        Execute the callback command.
        Override this method instead of execute() for callbacks.
        
        Args:
            query: CallbackQuery object
            ctx: Command context
            
        Returns:
            CommandResult with execution status
        """
        return await self.execute(ctx)

