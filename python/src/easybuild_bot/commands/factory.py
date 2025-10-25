"""
Factory for creating and registering all bot commands.
"""

import logging
from typing import TYPE_CHECKING

from .registry import CommandRegistry
from .executor import CommandExecutor
from .implementations import (
    StartCommand,
    HelpCommand,
    BuildCommand,
    UsersCommand,
    GroupsCommand,
    RegisterGroupCommand,
    UnblockUserCommand,
    BlockUserCommand
)

if TYPE_CHECKING:
    from ..storage import Storage

logger = logging.getLogger(__name__)


def create_command_system(
    storage: 'Storage',
    admin_token: str,
    model_name: str = "cointegrated/rubert-tiny",
    threshold: float = 0.5
) -> tuple[CommandRegistry, CommandExecutor]:
    """
    Create and configure the command system with all commands.
    
    Args:
        storage: Database storage instance
        admin_token: Admin token for authorization
        model_name: Model name for semantic matching
        threshold: Similarity threshold for command matching
        
    Returns:
        Tuple of (registry, executor)
    """
    logger.info("Creating command system...")
    
    # Create registry
    registry = CommandRegistry(model_name=model_name, threshold=threshold)
    
    # Create and register all commands
    commands = [
        StartCommand(storage, admin_token),
        HelpCommand(storage, admin_token),
        BuildCommand(storage, admin_token),
        UsersCommand(storage, admin_token),
        GroupsCommand(storage, admin_token),
        RegisterGroupCommand(storage, admin_token),
        UnblockUserCommand(storage, admin_token),
        BlockUserCommand(storage, admin_token),
    ]
    
    for cmd in commands:
        registry.register(cmd)
    
    # Create executor
    executor = CommandExecutor(registry)
    
    logger.info(f"Command system created with {len(commands)} commands")
    
    return registry, executor

