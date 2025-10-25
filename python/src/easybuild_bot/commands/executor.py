"""
Command Executor for executing commands with access control.
"""

import logging
from typing import Optional

from .base import Command, CommandContext, CommandResult
from .registry import CommandRegistry

logger = logging.getLogger(__name__)


class CommandExecutor:
    """
    Executor for running commands with proper access control.
    """
    
    def __init__(self, registry: CommandRegistry):
        """
        Initialize command executor.
        
        Args:
            registry: Command registry instance
        """
        self.registry = registry
    
    async def execute_command(
        self, 
        command: Command, 
        ctx: CommandContext
    ) -> CommandResult:
        """
        Execute a command with access control checks.
        
        Args:
            command: Command instance to execute
            ctx: Command context
            
        Returns:
            CommandResult with execution status
        """
        try:
            # Check if command can be executed
            can_execute, error_msg = await command.can_execute(ctx)
            
            if not can_execute:
                logger.warning(
                    f"Command {command.get_command_name()} cannot be executed: {error_msg}"
                )
                return CommandResult(
                    success=False,
                    error=error_msg or "Команда не может быть выполнена"
                )
            
            # Execute the command
            logger.info(f"Executing command {command.get_command_name()}")
            result = await command.execute(ctx)
            
            return result
            
        except Exception as e:
            logger.error(
                f"Error executing command {command.get_command_name()}: {e}",
                exc_info=True
            )
            return CommandResult(
                success=False,
                error="Произошла ошибка при выполнении команды"
            )
    
    async def match_and_execute(self, text: str, ctx: CommandContext) -> Optional[CommandResult]:
        """
        Match text to command and execute it.
        
        Args:
            text: User message text
            ctx: Command context
            
        Returns:
            CommandResult if command was matched and executed, None otherwise
        """
        match_result = self.registry.match_command(text)
        
        if not match_result:
            return None
        
        command, similarity, params = match_result
        
        # Update context with matched parameters
        ctx.params.update(params)
        ctx.user_text = text
        
        # Execute the command
        return await self.execute_command(command, ctx)

