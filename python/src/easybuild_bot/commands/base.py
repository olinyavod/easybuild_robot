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
    
    def __init__(self, storage, admin_token: str):
        """
        Initialize command with dependencies.
        
        Args:
            storage: Database storage instance
            admin_token: Admin token for authorization
        """
        self.storage = storage
        self.admin_token = admin_token
    
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
        Helper method to check user access.
        
        Args:
            update: Telegram update
            require_admin: Whether admin access is required
            
        Returns:
            Tuple (has_access: bool, error_message: Optional[str])
        """
        user = update.effective_user
        if not user:
            return False, "Не удалось определить пользователя"
        
        existing = self.storage.get_user_by_user_id(user.id)
        
        # Auto-create user if doesn't exist
        if existing is None:
            from ..models import BotUser
            self.storage.add_user(BotUser(
                id=str(user.id),
                user_id=user.id,
                user_name=user.username or '',
                display_name=user.full_name
            ))
            existing = self.storage.get_user_by_user_id(user.id)
        
        # Check admin access
        if require_admin:
            if existing and existing.is_admin:
                return True, None
            return False, "У вас нет прав администратора"
        
        # Check regular access
        if existing and (existing.allowed or existing.is_admin):
            return True, None
        
        return False, "Вы не имеете доступа к боту. Пожалуйста, обратитесь к администратору."

