"""
Version service for Xamarin projects.
"""

import os
import re
import logging
import xml.etree.ElementTree as ET
from typing import Optional, Tuple
from .base import VersionService
from ..models import Project

logger = logging.getLogger(__name__)


class XamarinVersionService(VersionService):
    """Version service for Xamarin projects (.csproj files)."""
    
    async def get_current_version(self, project: Project) -> Optional[str]:
        """Get version from .csproj file for Xamarin project."""
        csproj_path = os.path.join(project.local_repo_path, project.project_file_path)
        if not os.path.exists(csproj_path):
            return None
        
        try:
            # Parse XML
            tree = ET.parse(csproj_path)
            root = tree.getroot()
            
            # Try to find Version or ApplicationVersion in PropertyGroup
            for prop_group in root.findall('.//PropertyGroup'):
                # Check for Version tag
                version_elem = prop_group.find('Version')
                if version_elem is not None and version_elem.text:
                    return version_elem.text.strip()
                
                # Check for ApplicationVersion tag
                app_version_elem = prop_group.find('ApplicationVersion')
                if app_version_elem is not None and app_version_elem.text:
                    return app_version_elem.text.strip()
            
            return None
        except Exception as e:
            logger.error(f"Error getting version from {csproj_path}: {str(e)}", exc_info=True)
            return None
    
    async def update_version(self, project: Project, new_version: str) -> Tuple[bool, str]:
        """Update version in .csproj file for Xamarin project."""
        csproj_path = os.path.join(project.local_repo_path, project.project_file_path)
        if not os.path.exists(csproj_path):
            return False, f"Файл проекта не найден: {csproj_path}"
        
        try:
            # Parse XML
            tree = ET.parse(csproj_path)
            root = tree.getroot()
            
            version_updated = False
            
            # Update Version or ApplicationVersion in PropertyGroup
            for prop_group in root.findall('.//PropertyGroup'):
                # Update Version tag
                version_elem = prop_group.find('Version')
                if version_elem is not None:
                    version_elem.text = new_version
                    version_updated = True
                
                # Update ApplicationVersion tag
                app_version_elem = prop_group.find('ApplicationVersion')
                if app_version_elem is not None:
                    app_version_elem.text = new_version
                    version_updated = True
            
            if not version_updated:
                return False, "Не найдена строка с версией в .csproj файле"
            
            # Write updated XML
            tree.write(csproj_path, encoding='utf-8', xml_declaration=True)
            
            return True, f"Версия обновлена на {new_version} в {project.project_file_path}"
        except Exception as e:
            return False, f"Ошибка при обновлении версии: {str(e)}"

