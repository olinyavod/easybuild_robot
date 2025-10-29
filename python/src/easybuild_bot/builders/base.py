"""
Base interface for project builders.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, AsyncIterator
from enum import Enum


class BuildStep(Enum):
    """Build process steps."""
    PREPARING = "preparing"
    DEPENDENCIES = "dependencies"
    BUILDING = "building"
    SIGNING = "signing"
    PACKAGING = "packaging"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BuildResult:
    """Result of a build operation."""
    success: bool
    step: BuildStep
    message: str
    artifact_path: Optional[str] = None
    error: Optional[str] = None


class ProjectBuilder(ABC):
    """
    Abstract base class for project builders.
    
    Each project type (Flutter, .NET MAUI, Xamarin) implements this interface
    to provide type-specific build functionality.
    """
    
    def __init__(self, project, message_callback=None):
        """
        Initialize builder.
        
        Args:
            project: Project model instance
            message_callback: Optional async callback for sending progress messages
        """
        self.project = project
        self.message_callback = message_callback
    
    async def send_message(self, message: str):
        """Send a progress message if callback is available."""
        if self.message_callback:
            await self.message_callback(message)
    
    @abstractmethod
    async def prepare_environment(self) -> BuildResult:
        """
        Prepare build environment (install dependencies, etc).
        
        Returns:
            BuildResult with preparation status
        """
        pass
    
    @abstractmethod
    async def build_debug(self) -> BuildResult:
        """
        Build debug version of the application.
        
        Returns:
            BuildResult with build status and artifact path
        """
        pass
    
    @abstractmethod
    async def build_release(self) -> BuildResult:
        """
        Build release version of the application.
        
        Returns:
            BuildResult with build status and artifact path
        """
        pass
    
    @abstractmethod
    async def get_version_info(self) -> Optional[str]:
        """
        Get current version of the application from project files.
        
        Returns:
            Version string or None if not found
        """
        pass
    
    @abstractmethod
    async def clean(self) -> BuildResult:
        """
        Clean build artifacts.
        
        Returns:
            BuildResult with clean status
        """
        pass
    
    def get_project_type_name(self) -> str:
        """Get human-readable project type name."""
        return self.project.project_type.value
    
    async def prepare_release(self, new_version: str) -> BuildResult:
        """
        Prepare release: merge dev to release branch and update version.
        This is optional and not all project types may implement it.
        
        Args:
            new_version: New version string to set
            
        Returns:
            BuildResult with preparation status
        """
        return BuildResult(
            success=False,
            step=BuildStep.FAILED,
            message="Release preparation not implemented for this project type",
            error="Not implemented"
        )
    
    async def supports_release_preparation(self) -> bool:
        """
        Check if this builder supports release preparation.
        
        Returns:
            True if prepare_release is implemented
        """
        return False

