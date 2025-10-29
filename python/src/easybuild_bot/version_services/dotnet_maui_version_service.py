"""
Version service for .NET MAUI projects.
"""

import os
import xml.etree.ElementTree as ET
from typing import Optional, Tuple
from .base import VersionService
from ..models import Project


class DotNetMauiVersionService(VersionService):
    """Version service for .NET MAUI projects (.csproj files)."""
    
    async def get_current_version(self, project: Project) -> Optional[str]:
        """Get version from .csproj file for .NET MAUI project."""
        csproj_path = os.path.join(project.local_repo_path, project.project_file_path)
        if not os.path.exists(csproj_path):
            return None
        
        try:
            # Parse XML
            tree = ET.parse(csproj_path)
            root = tree.getroot()
            
            # Try to find ApplicationDisplayVersion in PropertyGroup (this is the main version)
            for prop_group in root.findall('.//PropertyGroup'):
                # Check for ApplicationDisplayVersion (MAUI specific)
                display_version_elem = prop_group.find('ApplicationDisplayVersion')
                if display_version_elem is not None and display_version_elem.text:
                    return display_version_elem.text.strip()
            
            return None
        except Exception:
            return None
    
    async def update_version(self, project: Project, new_version: str) -> Tuple[bool, str]:
        """
        Update version in .csproj file for .NET MAUI project.
        Updates both ApplicationDisplayVersion (X.Y.Z) and ApplicationVersion (single number).
        """
        csproj_path = os.path.join(project.local_repo_path, project.project_file_path)
        if not os.path.exists(csproj_path):
            return False, f"Файл проекта не найден: {csproj_path}"
        
        try:
            # Parse XML
            tree = ET.parse(csproj_path)
            root = tree.getroot()
            
            display_version_updated = False
            app_version_updated = False
            current_app_version = None
            
            # First pass: find current ApplicationVersion and update ApplicationDisplayVersion
            for prop_group in root.findall('.//PropertyGroup'):
                # Update ApplicationDisplayVersion (X.Y.Z format)
                display_version_elem = prop_group.find('ApplicationDisplayVersion')
                if display_version_elem is not None:
                    display_version_elem.text = new_version
                    display_version_updated = True
                
                # Get current ApplicationVersion (single number)
                app_version_elem = prop_group.find('ApplicationVersion')
                if app_version_elem is not None and app_version_elem.text:
                    try:
                        current_app_version = int(app_version_elem.text.strip())
                    except ValueError:
                        current_app_version = 1
            
            # Second pass: update ApplicationVersion (increment by 1)
            if current_app_version is not None:
                new_app_version = current_app_version + 1
                for prop_group in root.findall('.//PropertyGroup'):
                    app_version_elem = prop_group.find('ApplicationVersion')
                    if app_version_elem is not None:
                        app_version_elem.text = str(new_app_version)
                        app_version_updated = True
            
            if not display_version_updated:
                return False, "Не найдено поле ApplicationDisplayVersion в .csproj файле"
            
            # Write updated XML with proper formatting
            self._indent_xml(root)
            tree.write(csproj_path, encoding='utf-8', xml_declaration=True)
            
            result_msg = f"Версия обновлена на {new_version} в {project.project_file_path}"
            if app_version_updated:
                result_msg += f" (ApplicationVersion: {current_app_version} → {new_app_version})"
            
            return True, result_msg
        except Exception as e:
            return False, f"Ошибка при обновлении версии: {str(e)}"
    
    def _indent_xml(self, elem, level=0):
        """Add pretty-printing to XML by adding whitespace."""
        indent = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent


