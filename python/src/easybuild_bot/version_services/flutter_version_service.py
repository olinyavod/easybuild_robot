"""
Version service for Flutter projects.
"""

import os
import re
from typing import Optional, Tuple
from .base import VersionService
from ..models import Project


class FlutterVersionService(VersionService):
    """Version service for Flutter projects (pubspec.yaml)."""
    
    async def get_current_version(self, project: Project) -> Optional[str]:
        """Get version from pubspec.yaml for Flutter project."""
        pubspec_path = os.path.join(project.local_repo_path, project.project_file_path)
        if not os.path.exists(pubspec_path):
            return None
        
        try:
            with open(pubspec_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern matches: version: 1.0.0 or version: 1.0.0+5
            version_pattern = r'^version:\s+([\d]+\.[\d]+\.[\d]+(?:\+\d+)?).*$'
            match = re.search(version_pattern, content, re.MULTILINE)
            
            if match:
                return match.group(1)
            return None
        except Exception:
            return None
    
    async def update_version(self, project: Project, new_version: str) -> Tuple[bool, str]:
        """Update version in pubspec.yaml for Flutter project."""
        pubspec_path = os.path.join(project.local_repo_path, project.project_file_path)
        if not os.path.exists(pubspec_path):
            return False, f"Файл проекта не найден: {pubspec_path}"
        
        try:
            with open(pubspec_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern to find version line
            version_pattern = r'^version:\s+[\d]+\.[\d]+\.[\d]+.*$'
            new_version_line = f'version: {new_version}'
            
            if not re.search(version_pattern, content, re.MULTILINE):
                return False, "Не найдена строка с версией в pubspec.yaml"
            
            # Replace version
            updated_content = re.sub(
                version_pattern, 
                new_version_line, 
                content, 
                count=1, 
                flags=re.MULTILINE
            )
            
            # Write updated content
            with open(pubspec_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return True, f"Версия обновлена на {new_version} в {project.project_file_path}"
        except Exception as e:
            return False, f"Ошибка при обновлении версии: {str(e)}"

