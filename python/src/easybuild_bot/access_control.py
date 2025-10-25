"""
Access Control Service for centralized access management.
"""

import logging
from typing import Optional
from telegram import Update
from .storage import Storage
from .models import BotUser

logger = logging.getLogger(__name__)


class AccessControlService:
    """
    Service for managing user access control.
    Centralizes all access checking logic in one place.
    """
    
    def __init__(self, storage: Storage):
        """
        Initialize access control service.
        
        Args:
            storage: Database storage instance
        """
        self.storage = storage
    
    async def ensure_user_exists(self, user_id: int, username: str, full_name: str) -> Optional[BotUser]:
        """
        Ensure user exists in database, create if not.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            full_name: User's full name
            
        Returns:
            BotUser instance or None
        """
        existing = self.storage.get_user_by_user_id(user_id)
        
        if existing is None:
            self.storage.add_user(BotUser(
                id=str(user_id),
                user_id=user_id,
                user_name=username or '',
                display_name=full_name
            ))
            existing = self.storage.get_user_by_user_id(user_id)
            logger.info(f"Created new user: {user_id} ({full_name})")
        
        return existing
    
    async def check_user_access(
        self, 
        update: Update, 
        require_admin: bool = False,
        send_error_message: bool = True
    ) -> tuple[bool, Optional[str]]:
        """
        Check if user has access to bot.
        
        Args:
            update: Telegram update
            require_admin: If True, require admin rights
            send_error_message: If True, send error message to user
            
        Returns:
            Tuple of (has_access, error_message)
        """
        user = update.effective_user
        if not user:
            return False, "Пользователь не найден"
        
        # Ensure user exists in database
        existing = await self.ensure_user_exists(
            user_id=user.id,
            username=user.username or '',
            full_name=user.full_name
        )
        
        if not existing:
            error = "Ошибка при проверке доступа пользователя"
            if send_error_message and update.effective_message:
                await update.effective_message.reply_text(error)
            return False, error
        
        # Check admin access if required
        if require_admin:
            if not existing.is_admin:
                error = "У вас нет прав администратора"
                if send_error_message and update.effective_message:
                    await update.effective_message.reply_text(error)
                return False, error
            return True, None
        
        # Admin always has access
        if existing.is_admin:
            return True, None
        
        # Check if user is allowed
        if not existing.allowed:
            error = "Вы не имеете доступа к боту. Пожалуйста, обратитесь к администратору."
            if send_error_message and update.effective_message:
                await update.effective_message.reply_text(error)
            return False, error
        
        return True, None
    
    async def check_admin_access(
        self, 
        update: Update,
        send_error_message: bool = True
    ) -> tuple[bool, Optional[str]]:
        """
        Check if user has admin access.
        Convenience method that calls check_user_access with require_admin=True.
        
        Args:
            update: Telegram update
            send_error_message: If True, send error message to user
            
        Returns:
            Tuple of (has_access, error_message)
        """
        return await self.check_user_access(
            update=update,
            require_admin=True,
            send_error_message=send_error_message
        )
    
    def is_user_admin(self, user_id: int) -> bool:
        """
        Check if user is admin by user_id.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is admin, False otherwise
        """
        user = self.storage.get_user_by_user_id(user_id)
        return user is not None and user.is_admin
    
    def is_user_allowed(self, user_id: int) -> bool:
        """
        Check if user is allowed by user_id.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is allowed, False otherwise
        """
        user = self.storage.get_user_by_user_id(user_id)
        return user is not None and (user.is_admin or user.allowed)

