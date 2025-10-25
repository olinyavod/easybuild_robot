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
    BlockUserCommand,
    ProjectsCommand,
    AddProjectCommand,
    EditProjectCommand,
    DeleteProjectCommand
)
# Import callback commands
from .implementations.allow_user_callback import AllowUserCallbackCommand
from .implementations.block_user_callback import BlockUserCallbackCommand
from .implementations.unblock_user_callback import UnblockUserCallbackCommand
from .implementations.build_apk_callback import BuildApkCallbackCommand

if TYPE_CHECKING:
    from ..storage import Storage
    from ..access_control import AccessControlService

logger = logging.getLogger(__name__)


def create_command_system(
    storage: 'Storage',
    access_control: 'AccessControlService',
    model_name: str = "cointegrated/rubert-tiny",
    threshold: float = 0.5
) -> tuple[CommandRegistry, CommandExecutor]:
    """
    Create and configure the command system with all commands.
    
    Args:
        storage: Database storage instance
        access_control: Access control service instance
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
        StartCommand(storage, access_control),
        HelpCommand(storage, access_control),
        BuildCommand(storage, access_control),
        UsersCommand(storage, access_control),
        GroupsCommand(storage, access_control),
        RegisterGroupCommand(storage, access_control),
        UnblockUserCommand(storage, access_control),
        BlockUserCommand(storage, access_control),
        ProjectsCommand(storage, access_control),
        AddProjectCommand(storage, access_control),
        EditProjectCommand(storage, access_control),
        DeleteProjectCommand(storage, access_control),
        # Callback commands
        AllowUserCallbackCommand(storage, access_control),
        BlockUserCallbackCommand(storage, access_control),
        UnblockUserCallbackCommand(storage, access_control),
        BuildApkCallbackCommand(storage, access_control),
    ]
    
    for cmd in commands:
        registry.register(cmd)
    
    # Create executor
    executor = CommandExecutor(registry)
    
    logger.info(f"Command system created with {len(commands)} commands")
    
    return registry, executor

