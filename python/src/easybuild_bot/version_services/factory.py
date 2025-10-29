"""
Factory for creating version services based on project type.
"""

from typing import Optional
from .base import VersionService
from .flutter_version_service import FlutterVersionService
from .xamarin_version_service import XamarinVersionService
from .dotnet_maui_version_service import DotNetMauiVersionService
from ..models import Project, ProjectType


class VersionServiceFactory:
    """Factory for creating version services based on project type."""
    
    @staticmethod
    def create(project: Project) -> Optional[VersionService]:
        """
        Create appropriate version service for the project.
        
        Args:
            project: Project instance
            
        Returns:
            VersionService instance or None if project type is not supported
        """
        if project.project_type == ProjectType.FLUTTER:
            return FlutterVersionService()
        elif project.project_type == ProjectType.XAMARIN:
            return XamarinVersionService()
        elif project.project_type == ProjectType.DOTNET_MAUI:
            return DotNetMauiVersionService()
        else:
            return None
    
    @staticmethod
    def get_supported_types() -> list[ProjectType]:
        """Get list of supported project types."""
        return [
            ProjectType.FLUTTER,
            ProjectType.XAMARIN,
            ProjectType.DOTNET_MAUI
        ]

