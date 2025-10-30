"""
Base class for version services.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
from ..models import Project


class VersionService(ABC):
    """Base class for version management services."""
    
    @abstractmethod
    async def get_current_version(self, project: Project) -> Optional[str]:
        """
        Get current version from project file.
        
        Args:
            project: Project instance
            
        Returns:
            Current version string or None if not found
        """
        pass
    
    @abstractmethod
    async def update_version(self, project: Project, new_version: str) -> Tuple[bool, str]:
        """
        Update version in project file.
        
        Args:
            project: Project instance
            new_version: New version string
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        pass
    
    def increment_version(self, version: str, increment_type: str = 'patch') -> str:
        """
        Increment version number.
        
        Args:
            version: Current version string (e.g., "1.0.0", "1.0", or "1.0.0+5")
            increment_type: Type of increment - 'major', 'minor', or 'patch'
            
        Returns:
            New incremented version string
        """
        # Remove build number if present (e.g., "1.0.0+5" -> "1.0.0")
        base_version = version.split('+')[0]
        
        # Parse version parts
        parts = base_version.split('.')
        
        # Handle different version formats
        if len(parts) == 2:
            # Version like "1.0" - treat as "1.0.0"
            parts.append('0')
        elif len(parts) != 3:
            # Invalid version format, just return with .1 added
            return f"{version}.1"
        
        try:
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            
            # Increment based on type
            if increment_type == 'major':
                major += 1
                minor = 0
                patch = 0
            elif increment_type == 'minor':
                minor += 1
                patch = 0
            else:  # patch (default)
                patch += 1
            
            new_version = f"{major}.{minor}.{patch}"
            return new_version
        except ValueError:
            # Cannot parse, return original with .1 added
            return f"{version}.1"

