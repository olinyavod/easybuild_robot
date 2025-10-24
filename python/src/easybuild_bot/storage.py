"""
Database storage module using MontyDB.
"""
from typing import List, Optional
from .models import BotUser, BotGroup
from montydb import MontyClient


class Storage:
    """Database storage class for managing users and groups."""
    
    def __init__(self, dir_path: str, db_name: str = "easybuild_bot"):
        """
        Initialize storage with MontyDB.
        
        Args:
            dir_path: Directory path for MontyDB storage
            db_name: Database name
        """
        self._client = MontyClient(dir_path)
        self._db = self._client[db_name]
        self._init_indexes()
    
    def _init_indexes(self) -> None:
        """Create indexes for collections."""
        users = self._db["users"]
        groups = self._db["groups"]
        users.create_index("user_id", unique=True)
        users.create_index("id", unique=True)
        groups.create_index("group_id", unique=True)
        groups.create_index("id", unique=True)
    
    # User operations
    
    def add_user(self, user: BotUser) -> None:
        """
        Add or update user in database.
        
        Args:
            user: User to add or update
        """
        users = self._db["users"]
        doc = {
            "id": user.id,
            "user_id": user.user_id,
            "user_name": user.user_name,
            "display_name": user.display_name,
            "allowed": bool(user.allowed),
            "is_admin": bool(user.is_admin),
        }
        users.update_one({"user_id": user.user_id}, {"$set": doc}, upsert=True)
    
    def get_user_by_user_id(self, user_id: int) -> Optional[BotUser]:
        """
        Get user by Telegram user ID.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User or None if not found
        """
        users = self._db["users"]
        doc = users.find_one({"user_id": user_id})
        if not doc:
            return None
        return BotUser(
            id=str(doc.get("id")),
            user_id=int(doc.get("user_id")),
            user_name=str(doc.get("user_name") or ""),
            display_name=doc.get("display_name"),
            allowed=bool(doc.get("allowed", False)),
            is_admin=bool(doc.get("is_admin", False)),
        )
    
    def get_all_users(self) -> List[BotUser]:
        """
        Get all users from database.
        
        Returns:
            List of all users
        """
        users = self._db["users"]
        result: List[BotUser] = []
        for doc in users.find({}):
            result.append(
                BotUser(
                    id=str(doc.get("id")),
                    user_id=int(doc.get("user_id")),
                    user_name=str(doc.get("user_name") or ""),
                    display_name=doc.get("display_name"),
                    allowed=bool(doc.get("allowed", False)),
                    is_admin=bool(doc.get("is_admin", False)),
                )
            )
        return result
    
    def update_user_allowed(self, user_id: int, allowed: bool) -> None:
        """
        Update user allowed status.
        
        Args:
            user_id: Telegram user ID
            allowed: New allowed status
        """
        users = self._db["users"]
        users.update_one({"user_id": user_id}, {"$set": {"allowed": bool(allowed)}})
    
    def update_user_admin(self, user_id: int, is_admin: bool) -> None:
        """
        Update user admin status.
        
        Args:
            user_id: Telegram user ID
            is_admin: New admin status
        """
        users = self._db["users"]
        users.update_one({"user_id": user_id}, {"$set": {"is_admin": bool(is_admin)}})
    
    # Group operations
    
    def add_group(self, group: BotGroup) -> None:
        """
        Add or update group in database.
        
        Args:
            group: Group to add or update
        """
        groups = self._db["groups"]
        doc = {
            "id": group.id,
            "group_id": group.group_id,
            "group_name": group.group_name,
        }
        groups.update_one({"group_id": group.group_id}, {"$set": doc}, upsert=True)
    
    def get_group_by_group_id(self, group_id: int) -> Optional[BotGroup]:
        """
        Get group by Telegram group ID.
        
        Args:
            group_id: Telegram group ID
            
        Returns:
            Group or None if not found
        """
        groups = self._db["groups"]
        doc = groups.find_one({"group_id": group_id})
        if not doc:
            return None
        return BotGroup(
            id=str(doc.get("id")),
            group_id=int(doc.get("group_id")),
            group_name=str(doc.get("group_name") or "")
        )
    
    def get_all_groups(self) -> List[BotGroup]:
        """
        Get all groups from database.
        
        Returns:
            List of all groups
        """
        groups = self._db["groups"]
        result: List[BotGroup] = []
        for doc in groups.find({}):
            result.append(
                BotGroup(
                    id=str(doc.get("id")),
                    group_id=int(doc.get("group_id")),
                    group_name=str(doc.get("group_name") or "")
                )
            )
        return result

