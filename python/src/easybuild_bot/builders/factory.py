"""
Factory for creating project builders based on project type.
"""

from typing import Optional, Callable
from ..models import Project, ProjectType
from .base import ProjectBuilder
from .flutter_builder import FlutterBuilder
from .dotnet_maui_builder import DotNetMauiBuilder
from .xamarin_builder import XamarinBuilder


class ProjectBuilderFactory:
    """
    Factory for creating project builders.
    
    Uses the Strategy pattern to instantiate the appropriate builder
    based on the project type.
    """
    
    @staticmethod
    def create_builder(
        project: Project,
        message_callback: Optional[Callable] = None
    ) -> ProjectBuilder:
        """
        Create a project builder for the given project.
        
        Args:
            project: Project model instance
            message_callback: Optional async callback for sending progress messages
            
        Returns:
            ProjectBuilder instance for the project type
            
        Raises:
            ValueError: If project type is not supported
        """
        if project.project_type == ProjectType.FLUTTER:
            return FlutterBuilder(project, message_callback)
        elif project.project_type == ProjectType.DOTNET_MAUI:
            return DotNetMauiBuilder(project, message_callback)
        elif project.project_type == ProjectType.XAMARIN:
            return XamarinBuilder(project, message_callback)
        else:
            raise ValueError(f"Unsupported project type: {project.project_type}")
    
    @staticmethod
    def get_supported_types():
        """
        Get list of supported project types.
        
        Returns:
            List of ProjectType enums
        """
        return [
            ProjectType.FLUTTER,
            ProjectType.DOTNET_MAUI,
            ProjectType.XAMARIN
        ]
    
    @staticmethod
    def is_supported(project_type: ProjectType) -> bool:
        """
        Check if project type is supported.
        
        Args:
            project_type: ProjectType enum
            
        Returns:
            True if supported, False otherwise
        """
        return project_type in ProjectBuilderFactory.get_supported_types()




