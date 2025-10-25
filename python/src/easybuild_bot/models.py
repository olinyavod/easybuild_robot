from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class ProjectType(Enum):
    """Тип проекта"""
    FLUTTER = "flutter"
    DOTNET_MAUI = "dotnet_maui"
    XAMARIN = "xamarin"


@dataclass
class BotUser:
    id: str
    user_id: int
    user_name: str
    display_name: Optional[str] = None
    allowed: bool = False
    is_admin: bool = False


@dataclass
class BotGroup:
    id: str
    group_id: int
    group_name: str


@dataclass
class Project:
    """
    Модель проекта для сборки приложений.
    
    Атрибуты:
        id: Уникальный идентификатор проекта
        name: Название проекта
        project_type: Тип проекта (Flutter, .NET MAUI, Xamarin)
        git_url: Ссылка на git репозиторий
        project_file_path: Путь к файлу проекта (относительный от корня репозитория)
        local_repo_path: Локальный путь к репозиторию на сервере
        dev_branch: Git ветка разработки
        release_branch: Git ветка публикации/релиза
        allowed_group_ids: Список ID групп, в которых можно работать с проектом
        tags: Теги для сопоставления с параметрами текстовых команд
        description: Описание проекта (опционально)
    """
    id: str
    name: str
    project_type: ProjectType
    git_url: str
    project_file_path: str
    local_repo_path: str
    dev_branch: str = "develop"
    release_branch: str = "main"
    allowed_group_ids: List[int] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
