"""
Git service for repository operations.
Provides common git operations to avoid code duplication.
"""

import os
import subprocess
import logging
from typing import Tuple, Optional
from ..models import Project

logger = logging.getLogger(__name__)


class GitService:
    """Service for common git repository operations."""

    @staticmethod
    def clone_repository(project: Project, timeout: int = 300) -> Tuple[bool, str]:
        """
        Клонирует репозиторий проекта, если он ещё не существует.

        Args:
            project: Объект проекта с информацией о репозитории
            timeout: Таймаут операции в секундах (по умолчанию 5 минут)

        Returns:
            Кортеж (успешно, сообщение об ошибке или пустая строка)
        """
        repo_path = project.local_repo_path

        # Проверяем, существует ли репозиторий
        if os.path.exists(repo_path):
            logger.info(f"Репозиторий уже существует: {repo_path}")
            return True, ""

        try:
            # Создаём родительскую директорию
            parent_dir = os.path.dirname(repo_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
                logger.info(f"Создана директория: {parent_dir}")

            # Извлекаем имя директории для клонирования
            repo_name = os.path.basename(repo_path)

            logger.info(f"Клонирование репозитория {project.git_url} в {repo_path}...")

            # Клонируем репозиторий БЕЗ подмодулей
            result = subprocess.run(
                ["git", "clone", project.git_url, repo_name],
                cwd=parent_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                logger.error(f"Ошибка клонирования: {error_details}")
                return False, f"❌ Ошибка клонирования репозитория:\n```\n{error_details}\n```"

            logger.info(f"✓ Репозиторий успешно клонирован: {repo_path}")
            return True, ""

        except subprocess.TimeoutExpired:
            error_msg = f"❌ Превышено время ожидания клонирования репозитория ({timeout} сек)"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Неожиданная ошибка при клонировании: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    @staticmethod
    def checkout_branch(repo_path: str, branch: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        Переключается на указанную ветку в репозитории.

        Args:
            repo_path: Путь к локальному репозиторию
            branch: Название ветки
            timeout: Таймаут операции в секундах

        Returns:
            Кортеж (успешно, сообщение об ошибке или пустая строка)
        """
        if not os.path.exists(repo_path):
            error_msg = f"❌ Репозиторий не существует: {repo_path}"
            logger.error(error_msg)
            return False, error_msg

        try:
            logger.info(f"Переключение на ветку {branch} в {repo_path}...")

            result = subprocess.run(
                ["git", "-C", repo_path, "checkout", branch],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                logger.error(f"Ошибка переключения на ветку: {error_details}")
                return False, f"❌ Не удалось переключиться на ветку {branch}:\n```\n{error_details}\n```"

            logger.info(f"✓ Переключено на ветку: {branch}")
            return True, ""

        except subprocess.TimeoutExpired:
            error_msg = f"❌ Превышено время ожидания переключения на ветку ({timeout} сек)"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Неожиданная ошибка при переключении ветки: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    @staticmethod
    def pull_branch(repo_path: str, branch: str, timeout: int = 120) -> Tuple[bool, str]:
        """
        Обновляет указанную ветку из удалённого репозитория.

        Args:
            repo_path: Путь к локальному репозиторию
            branch: Название ветки
            timeout: Таймаут операции в секундах

        Returns:
            Кортеж (успешно, сообщение об ошибке или пустая строка)
        """
        if not os.path.exists(repo_path):
            error_msg = f"❌ Репозиторий не существует: {repo_path}"
            logger.error(error_msg)
            return False, error_msg

        try:
            logger.info(f"Обновление ветки {branch} в {repo_path}...")

            result = subprocess.run(
                ["git", "-C", repo_path, "pull", "origin", branch],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                # Pull может вернуть ненулевой код, даже если всё ok (например, Already up to date)
                logger.warning(f"Git pull вернул код {result.returncode}: {error_details}")
                # Не считаем это фатальной ошибкой
                return True, ""

            logger.info(f"✓ Ветка {branch} обновлена")
            return True, ""

        except subprocess.TimeoutExpired:
            error_msg = f"❌ Превышено время ожидания обновления ветки ({timeout} сек)"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Неожиданная ошибка при обновлении ветки: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    @staticmethod
    def ensure_repository(project: Project) -> Tuple[bool, str]:
        """
        Гарантирует, что репозиторий существует и находится на нужной ветке.
        Если репозиторий не существует - клонирует его.
        Если существует - переключается на dev ветку и обновляет её.

        Args:
            project: Объект проекта

        Returns:
            Кортеж (успешно, сообщение об ошибке или пустая строка)
        """
        repo_path = project.local_repo_path

        # Если репозиторий не существует - клонируем
        if not os.path.exists(repo_path):
            success, error_msg = GitService.clone_repository(project)
            if not success:
                return False, error_msg

        # Переключаемся на dev ветку
        success, error_msg = GitService.checkout_branch(repo_path, project.dev_branch)
        if not success:
            return False, error_msg

        # Обновляем ветку
        success, error_msg = GitService.pull_branch(repo_path, project.dev_branch)
        if not success:
            return False, error_msg

        return True, ""
