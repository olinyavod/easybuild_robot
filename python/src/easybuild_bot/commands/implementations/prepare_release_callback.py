"""
Callback command for simplified release preparation.
"""

import os
import subprocess
import logging
from typing import Optional
from ..callback_base import CallbackCommand
from ..base import CommandContext, CommandResult, CommandAccessLevel
from ...models import Project
from ...version_services import VersionServiceFactory

logger = logging.getLogger(__name__)


class PrepareReleaseCallbackCommand(CallbackCommand):
    """Handle release preparation with simplified algorithm."""

    def get_command_name(self) -> str:
        return "callback:prepare_release"

    def get_callback_pattern(self) -> str:
        return r"^prepare_release:.*$"

    def get_access_level(self) -> CommandAccessLevel:
        """Callback доступен авторизованным пользователям."""
        return CommandAccessLevel.USER

    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """
        Переопределяем стандартную проверку доступа.
        Нужна дополнительная проверка, что проект разрешен для группы.
        """
        # Сначала базовая проверка доступа
        has_access, error_msg = await super().can_execute(ctx)

        if not has_access:
            return False, error_msg

        # Проверка разрешений на проект для группы
        query = ctx.update.callback_query
        if query and query.data:
            # Extract project ID from callback data
            parts = query.data.split(":", 1)
            if len(parts) == 2:
                project_id = parts[1]
                project = self.storage.get_project_by_id(project_id)

                # Check if called from group
                chat = ctx.update.effective_chat
                if chat and chat.type in ("group", "supergroup"):
                    # Verify project is allowed for this group
                    if project and chat.id not in project.allowed_group_ids:
                        return False, "Этот проект недоступен для данной группы"

        return True, None

    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute release preparation."""
        query = ctx.update.callback_query
        if not query or not query.data:
            return CommandResult(success=False, error="Invalid callback query")

        parts = query.data.split(":", 1)
        if len(parts) != 2:
            await query.answer(text="Неверный формат данных", show_alert=True)
            return CommandResult(success=False, error="Invalid callback data format")

        project_id = parts[1]
        project = self.storage.get_project_by_id(project_id)
        if not project:
            await query.answer(text="Проект не найден", show_alert=True)
            return CommandResult(success=False, error="Project not found")

        await query.answer()

        # Start release preparation
        async def send_message(msg: str):
            await ctx.update.effective_message.reply_text(msg, parse_mode='Markdown')

        success, message = await self.prepare_release_direct(project, send_message)

        return CommandResult(success=success, message=message)

    async def prepare_release_direct(self, project: Project, send_message, show_start_message: bool = True) -> tuple[bool, str]:
        """Direct method for release preparation (callable without callback context)."""
        # Get version service for this project type
        version_service = VersionServiceFactory.create(project)
        if not version_service:
            error_msg = f"❌ Тип проекта {project.project_type.value} не поддерживается для автоматического версионирования"
            await send_message(error_msg)
            return False, error_msg

        # Get current version from release branch
        current_version = await self._get_current_version_from_release_branch(project, version_service)
        if not current_version:
            # Формируем сообщение об ошибке в зависимости от типа проекта
            if project.project_type.value == "xamarin":
                # Получаем детальную диагностическую информацию
                diagnostic_info = ""
                if hasattr(version_service, 'get_version_diagnostic_info'):
                    diagnostic_info = version_service.get_version_diagnostic_info(project)

                error_msg = (
                    f"❌ Не удалось определить текущую версию проекта **{project.name}**\n\n"
                    f"📋 **Информация о проекте:**\n"
                    f"   • Ветка релиза: `{project.release_branch}`\n"
                    f"   • Файл проекта: `{project.project_file_path}`\n"
                )

                if diagnostic_info:
                    error_msg += f"\n🔍 **Диагностика:**\n{diagnostic_info}\n"
                else:
                    # Fallback на старое сообщение, если диагностика недоступна
                    error_msg += (
                        f"\nДля проектов Xamarin версия ищется в платформенных файлах:\n"
                        f"  • `*.Android.csproj` или `*.Droid.csproj`\n"
                        f"  • `*.iOS.csproj`\n\n"
                        f"Убедитесь, что в платформенных файлах есть теги версий:\n\n"
                        f"**Для Android:**\n"
                        f"  • `<ApplicationVersion>X.Y.Z</ApplicationVersion>`\n"
                        f"  • `<AndroidVersionCode>N</AndroidVersionCode>`\n\n"
                        f"**Для iOS:**\n"
                        f"  • `<ApplicationVersion>X.Y.Z</ApplicationVersion>`\n"
                        f"  • `<CFBundleVersion>X.Y.Z</CFBundleVersion>`"
                    )
            elif project.project_type.value == "dotnet_maui":
                error_msg = (
                    f"❌ Не удалось определить текущую версию проекта {project.name}\n"
                    f"Ветка релиза: `{project.release_branch}`\n"
                    f"Файл проекта: `{project.project_file_path}`\n\n"
                    f"Убедитесь, что в файле проекта есть тег версии:\n"
                    f"  - Для MAUI: `<ApplicationDisplayVersion>X.Y.Z</ApplicationDisplayVersion>`"
                )
            elif project.project_type.value == "flutter":
                error_msg = (
                    f"❌ Не удалось определить текущую версию проекта {project.name}\n"
                    f"Ветка релиза: `{project.release_branch}`\n"
                    f"Файл проекта: `{project.project_file_path}`\n\n"
                    f"Убедитесь, что в файле проекта есть тег версии:\n"
                    f"  - Для Flutter: `version: X.Y.Z` в pubspec.yaml"
                )
            else:
                error_msg = (
                    f"❌ Не удалось определить текущую версию проекта {project.name}\n"
                    f"Ветка релиза: `{project.release_branch}`\n"
                    f"Файл проекта: `{project.project_file_path}`"
                )
            await send_message(error_msg)
            return False, error_msg

        # Auto-increment version (patch)
        new_version = version_service.increment_version(current_version, increment_type='patch')

        # Only show start message if requested (for backward compatibility)
        if show_start_message:
            await send_message(
                f"🚀 Начинаем подготовку релиза для проекта: **{project.name}**\n"
                f"📦 Текущая версия: `{current_version}`\n"
                f"🆕 Новая версия: `{new_version}`",
            )

        success, message = await self.prepare_release(project, new_version, send_message, current_version, version_service)

        return success, message

    async def prepare_release(self, project: Project, new_version: str, send_message, current_version: str = None, version_service = None) -> tuple[bool, str]:
        """Execute the simplified release preparation algorithm (10 steps)."""
        repo_path = project.local_repo_path

        # Get version service if not provided
        if version_service is None:
            version_service = VersionServiceFactory.create(project)
            if not version_service:
                error_msg = f"❌ Тип проекта {project.project_type.value} не поддерживается"
                await send_message(error_msg)
                return False, error_msg

        try:
            # Step 1: Clone/check repository (WITHOUT submodules)
            if not os.path.exists(repo_path):
                parent_dir = os.path.dirname(repo_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)

                # Extract the directory name for cloning
                repo_name = os.path.basename(repo_path)

                # Clone repository WITHOUT submodules
                result = subprocess.run(
                    ["git", "clone", project.git_url, repo_name],
                    cwd=parent_dir,
                    capture_output=True, text=True, timeout=300
                )
                if result.returncode != 0:
                    error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                    error_msg = f"❌ Ошибка клонирования репозитория:\n```\n{error_details}\n```"
                    await send_message(error_msg)
                    return False, error_msg

            # Step 2: Switch to dev branch
            result = subprocess.run(["git", "-C", repo_path, "checkout", project.dev_branch], capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                error_msg = f"❌ Не удалось переключиться на ветку {project.dev_branch}:\n```\n{error_details}\n```"
                await send_message(error_msg)
                return False, error_msg

            # Step 3: Update changes in dev branch (WITHOUT submodules)
            result = subprocess.run(["git", "-C", repo_path, "pull", "origin", project.dev_branch], capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                error_msg = f"❌ Не удалось обновить ветку разработки:\n```\n{error_details}\n```"
                await send_message(error_msg)
                return False, error_msg

            # Step 4: Switch to release branch
            result = subprocess.run(["git", "-C", repo_path, "checkout", project.release_branch], capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                error_msg = f"❌ Не удалось переключиться на ветку {project.release_branch}:\n```\n{error_details}\n```"
                await send_message(error_msg)
                return False, error_msg

            # Step 5: Pull changes for release branch
            result = subprocess.run(["git", "-C", repo_path, "pull", "origin", project.release_branch], capture_output=True, text=True, timeout=120)
            # Non-critical if fails

            # Step 6: Merge dev branch into release branch
            result = subprocess.run(["git", "-C", repo_path, "merge", project.dev_branch, "-m", f"Merge {project.dev_branch} into {project.release_branch}"], capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                error_msg = f"❌ Ошибка при мердже веток:\n```\n{error_details}\n```"
                await send_message(error_msg)
                return False, error_msg

            # Step 7: Update version using version service
            success, version_msg = await version_service.update_version(project, new_version)
            if not success:
                error_msg = f"❌ {version_msg}"
                await send_message(error_msg)
                return False, version_msg

            # Step 8: Create commit with "#Release <version>"
            result = subprocess.run(["git", "-C", repo_path, "add", "."], capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                error_msg = f"❌ Ошибка при добавлении файлов:\n```\n{error_details}\n```"
                await send_message(error_msg)
                return False, error_msg

            commit_message = f"#Release {new_version}"
            result = subprocess.run(["git", "-C", repo_path, "commit", "-m", commit_message], capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                error_msg = f"❌ Ошибка при создании коммита:\n```\n{error_details}\n```"
                await send_message(error_msg)
                return False, error_msg

            # Step 9: Push to repository
            result = subprocess.run(["git", "-C", repo_path, "push", "origin", project.release_branch], capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                error_msg = f"❌ Ошибка при отправке изменений в репозиторий:\n```\n{error_details}\n```"
                await send_message(error_msg)
                return False, error_msg

            # Step 10: Get last commits and show final summary
            last_commits = ""
            try:
                result = subprocess.run(
                    ["git", "-C", repo_path, "log", "-5", "--pretty=format:%h - %s (%an)"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout:
                    last_commits = "\n\n📜 **Последние коммиты:**\n```\n" + result.stdout + "\n```"
            except Exception:
                pass

            # Build success message
            version_info = f"🏷 Версия: **{new_version}**"
            if current_version:
                version_info = f"🏷 Версия: **{current_version}** → **{new_version}**"

            success_msg = (
                f"✅ **Релиз успешно подготовлен!**\n\n"
                f"📦 Проект: **{project.name}**\n"
                f"{version_info}"
                f"{last_commits}\n\n"
                f"Сборка начнется автоматически в репозитории (GitHub Actions)."
            )
            await send_message(success_msg)
            return True, success_msg

        except subprocess.TimeoutExpired as e:
            error_msg = f"❌ Превышено время ожидания операции"
            await send_message(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Неожиданная ошибка: {str(e)}"
            await send_message(error_msg)
            return False, error_msg

    async def _get_current_version_from_release_branch(self, project: Project, version_service) -> Optional[str]:
        """Get current version from release branch."""
        repo_path = project.local_repo_path

        # Save current branch
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                logger.error(f"Failed to get current branch for {project.name}: {result.stderr}")
                return None
            current_branch = result.stdout.strip()
            logger.info(f"Current branch for {project.name}: {current_branch}")

            # Switch to release branch
            logger.info(f"Switching to release branch '{project.release_branch}' for {project.name}")
            result = subprocess.run(
                ["git", "-C", repo_path, "checkout", project.release_branch],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                logger.error(f"Failed to checkout release branch '{project.release_branch}': {result.stderr}")
                return None

            # Pull latest changes
            logger.info(f"Pulling latest changes from '{project.release_branch}'")
            result = subprocess.run(
                ["git", "-C", repo_path, "pull", "origin", project.release_branch],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode != 0:
                logger.warning(f"Failed to pull from release branch (continuing anyway): {result.stderr}")

            # Get version from release branch using version service
            logger.info(f"Getting version from release branch for {project.name}")
            version = await version_service.get_current_version(project)

            if version:
                logger.info(f"Found version in release branch: {version}")
            else:
                logger.error(f"Failed to get version from release branch for {project.name}")

            # Switch back to original branch (usually dev branch will be set later)
            # We don't need to switch back as the prepare_release will switch to release anyway

            return version
        except Exception as e:
            logger.exception(f"Exception in _get_current_version_from_release_branch for {project.name}: {e}")
            return None
