"""
Database storage module using MontyDB.
"""
import os
from typing import List, Optional
from .models import BotUser, BotGroup, Project, ProjectType
from montydb import MontyClient

# Get project root directory (parent of src directory)
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.dirname(_CURRENT_DIR)  # src/easybuild_bot -> src
_PYTHON_DIR = os.path.dirname(_SRC_DIR)    # src -> python
PROJECT_ROOT = os.path.dirname(_PYTHON_DIR)  # python -> project root
REPOS_DIR = os.path.join(PROJECT_ROOT, "repos")


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
    
    @property
    def db(self):
        """Get database instance for direct access."""
        return self._db
    
    def _init_indexes(self) -> None:
        """Create indexes for collections."""
        users = self._db["users"]
        groups = self._db["groups"]
        projects = self._db["projects"]
        
        users.create_index("user_id", unique=True)
        users.create_index("id", unique=True)
        groups.create_index("group_id", unique=True)
        groups.create_index("id", unique=True)
        projects.create_index("id", unique=True)
        projects.create_index("name")
    
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
    
    def find_users_by_display_name(self, display_name: str) -> List[BotUser]:
        """
        Find users by display name (partial match).
        
        Args:
            display_name: Display name to search for
            
        Returns:
            List of matching users
        """
        users = self._db["users"]
        result: List[BotUser] = []
        # Search for users with display_name containing the search term (case-insensitive)
        for doc in users.find({}):
            user_display = doc.get("display_name") or ""
            if display_name.lower() in user_display.lower():
                result.append(
                    BotUser(
                        id=str(doc.get("id")),
                        user_id=int(doc.get("user_id")),
                        user_name=str(doc.get("user_name") or ""),
                        display_name=user_display,
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
    
    # Project operations
    
    def add_project(self, project: Project) -> None:
        """
        Add or update project in database.
        
        Args:
            project: Project to add or update
        """
        projects = self._db["projects"]
        doc = {
            "id": project.id,
            "name": project.name,
            "project_type": project.project_type.value,
            "git_url": project.git_url,
            "project_file_path": project.project_file_path,
            "local_repo_path": project.local_repo_path,
            "dev_branch": project.dev_branch,
            "release_branch": project.release_branch,
            "allowed_group_ids": project.allowed_group_ids,
            "tags": project.tags,
            "description": project.description,
        }
        projects.update_one({"id": project.id}, {"$set": doc}, upsert=True)
    
    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """
        Get project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project or None if not found
        """
        projects = self._db["projects"]
        doc = projects.find_one({"id": project_id})
        if not doc:
            return None
        return self._doc_to_project(doc)
    
    def get_project_by_name(self, name: str) -> Optional[Project]:
        """
        Get project by name (case-insensitive).
        
        Args:
            name: Project name
            
        Returns:
            Project or None if not found
        """
        projects = self._db["projects"]
        # Search case-insensitive
        for doc in projects.find({}):
            if doc.get("name", "").lower() == name.lower():
                return self._doc_to_project(doc)
        return None
    
    def get_all_projects(self) -> List[Project]:
        """
        Get all projects from database.
        
        Returns:
            List of all projects
        """
        projects = self._db["projects"]
        result: List[Project] = []
        for doc in projects.find({}):
            result.append(self._doc_to_project(doc))
        return result
    
    def find_projects_by_tag(self, tag: str) -> List[Project]:
        """
        Find projects by tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of matching projects
        """
        projects = self._db["projects"]
        result: List[Project] = []
        # Search for projects with matching tag
        for doc in projects.find({}):
            tags = doc.get("tags", [])
            if tag.lower() in [t.lower() for t in tags]:
                result.append(self._doc_to_project(doc))
        return result
    
    def get_projects_for_group(self, group_id: int) -> List[Project]:
        """
        Get all projects available for a specific group.
        
        Args:
            group_id: Telegram group ID
            
        Returns:
            List of projects available for the group
        """
        projects = self._db["projects"]
        result: List[Project] = []
        for doc in projects.find({}):
            allowed_groups = doc.get("allowed_group_ids", [])
            # If no groups specified, project is available for all groups
            if not allowed_groups or group_id in allowed_groups:
                result.append(self._doc_to_project(doc))
        return result
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if project was deleted, False if not found
        """
        projects = self._db["projects"]
        result = projects.delete_one({"id": project_id})
        return result.deleted_count > 0
    
    def update_project_groups(self, project_id: str, group_ids: List[int]) -> None:
        """
        Update allowed groups for a project.
        
        Args:
            project_id: Project ID
            group_ids: List of allowed group IDs
        """
        projects = self._db["projects"]
        projects.update_one({"id": project_id}, {"$set": {"allowed_group_ids": group_ids}})
    
    def update_project_tags(self, project_id: str, tags: List[str]) -> None:
        """
        Update tags for a project.
        
        Args:
            project_id: Project ID
            tags: List of tags
        """
        projects = self._db["projects"]
        projects.update_one({"id": project_id}, {"$set": {"tags": tags}})
    
    def _doc_to_project(self, doc: dict) -> Project:
        """
        Convert database document to Project object.
        
        Args:
            doc: Database document
            
        Returns:
            Project object
        """
        # Get local_repo_path and ensure it's absolute
        local_repo_path = str(doc.get("local_repo_path", ""))
        if local_repo_path and not os.path.isabs(local_repo_path):
            # Convert relative path to absolute, placing it in repos/ directory
            local_repo_path = os.path.join(REPOS_DIR, local_repo_path)
        
        return Project(
            id=str(doc.get("id")),
            name=str(doc.get("name", "")),
            project_type=ProjectType(doc.get("project_type", "flutter")),
            git_url=str(doc.get("git_url", "")),
            project_file_path=str(doc.get("project_file_path", "")),
            local_repo_path=local_repo_path,
            dev_branch=str(doc.get("dev_branch", "develop")),
            release_branch=str(doc.get("release_branch", "main")),
            allowed_group_ids=list(doc.get("allowed_group_ids", [])),
            tags=list(doc.get("tags", [])),
            description=doc.get("description"),
        )

