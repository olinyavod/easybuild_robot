"""
Base Command class and related types for Command Pattern implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes


@dataclass
class CommandContext:
    """Context information for command execution."""
    update: Update
    context: ContextTypes.DEFAULT_TYPE
    params: Dict[str, Any]
    user_text: Optional[str] = None


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class Command(ABC):
    """
    Abstract base class for all commands.
    
    Each command encapsulates:
    - Execution logic
    - Access control logic
    - Semantic tags for matching
    """
    
    def __init__(self, storage, access_control):
        """
        Initialize command with dependencies.
        
        Args:
            storage: Database storage instance
            access_control: Access control service instance
        """
        self.storage = storage
        self.access_control = access_control
    
    @abstractmethod
    def get_command_name(self) -> str:
        """
        Get the command name (e.g. "/start", "/help").
        
        Returns:
            Command name string
        """
        pass
    
    @abstractmethod
    def get_semantic_tags(self) -> List[str]:
        """
        Get semantic tags for command matching.
        
        Returns:
            List of Russian language descriptions/synonyms
        """
        pass
    
    @abstractmethod
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """
        Check if command can be executed in current context.
        
        Args:
            ctx: Command context with update and params
            
        Returns:
            Tuple (can_execute: bool, error_message: Optional[str])
        """
        pass
    
    @abstractmethod
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """
        Execute the command.
        
        Args:
            ctx: Command context with update and params
            
        Returns:
            CommandResult with execution status
        """
        pass
    
    def get_parameter_patterns(self) -> Dict[str, List[str]]:
        """
        Get regex patterns for parameter extraction.
        
        Returns:
            Dictionary mapping parameter names to list of regex patterns
        """
        return {}
    
    async def _check_user_access(self, update: Update, require_admin: bool = False) -> tuple[bool, Optional[str]]:
        """
        Helper method to check user access using AccessControlService.
        
        Args:
            update: Telegram update
            require_admin: Whether admin access is required
            
        Returns:
            Tuple (has_access: bool, error_message: Optional[str])
        """
        return await self.access_control.check_user_access(
            update=update,
            require_admin=require_admin,
            send_error_message=False  # Commands handle error messages themselves
        )

