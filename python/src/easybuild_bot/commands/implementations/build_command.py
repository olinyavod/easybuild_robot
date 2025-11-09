"""
/build command implementation.
"""

from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..base import Command, CommandContext, CommandResult, CommandAccessLevel


class BuildCommand(Command):
    """Build command - show build options based on available projects."""

    def get_command_name(self) -> str:
        return "/build"

    def get_semantic_tags(self) -> List[str]:
        return [
            "сборка",
            "сборки",
            "покажи сборки",
            "выбрать сборку",
            "собрать",
            "собери",
            "построй",
            "билд",
            "собрать apk",
            "сборка приложения",
            "создать сборку",
            "собери проект",
            "построй проект",
            "сборка проекта"
        ]

    def get_access_level(self) -> CommandAccessLevel:
        """Команда доступна любому авторизованному пользователю."""
        return CommandAccessLevel.USER

    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute build command - show projects based on context."""
        chat = ctx.update.effective_chat

        # Get projects based on context
        if chat and chat.type in ("group", "supergroup"):
            # In groups, show only projects available for this group
            projects = self.storage.get_projects_for_group(chat.id)
            context_msg = "для этой группы"
        else:
            # In private chat, show all projects
            projects = self.storage.get_all_projects()
            context_msg = "все доступные"

        if not projects:
            message = f"📋 Нет доступных проектов для сборки ({context_msg})."
            await ctx.update.effective_message.reply_text(message)
            return CommandResult(success=True, message=message)

        # If only one project - start build immediately
        if len(projects) == 1:
            project = projects[0]
            emoji = {
                "flutter": "🦋",
                "dotnet_maui": "🔷",
                "xamarin": "🔶"
            }.get(project.project_type.value, "📦")

            message = f"🔨 Запускаю сборку проекта: {emoji} **{project.name}**"
            await ctx.update.effective_message.reply_text(message, parse_mode='Markdown')

            # Import and execute ProjectSelectCallbackCommand directly
            from .project_select_callback import ProjectSelectCallbackCommand

            # Create a mock callback query context
            # We need to simulate the callback to reuse existing logic
            project_select_cmd = ProjectSelectCallbackCommand(self.storage, self.access_control)

            # Create a modified context for direct execution
            # Instead of using callback, we'll call the logic directly
            import asyncio

            # Send progress message
            progress_msg = await ctx.update.effective_message.reply_text(
                f"🔄 Подготовка репозитория **{project.name}** к публикации...",
                parse_mode='Markdown'
            )

            # Execute the project selection logic (cloning, preparation, etc.)
            try:
                # Import prepare_release_callback to execute directly
                from .prepare_release_callback import PrepareReleaseCallbackCommand
                prepare_cmd = PrepareReleaseCallbackCommand(self.storage, self.access_control)

                # Track if progress message was deleted
                progress_deleted = False

                async def send_message(msg: str):
                    nonlocal progress_deleted
                    # Delete progress message on first message
                    if not progress_deleted:
                        try:
                            await progress_msg.delete()
                        except Exception:
                            pass
                        progress_deleted = True

                    # Send all messages to user
                    await ctx.update.effective_message.reply_text(msg, parse_mode='Markdown')

                # Execute repository preparation and release
                import os
                import subprocess

                repo_path = project.local_repo_path

                # Check if local repository path exists
                if not os.path.exists(repo_path):
                    # Repository doesn't exist, need to clone
                    try:
                        # Create parent directory if it doesn't exist
                        parent_dir = os.path.dirname(repo_path)
                        if parent_dir:
                            os.makedirs(parent_dir, exist_ok=True)

                        # Extract the directory name for cloning
                        repo_name = os.path.basename(repo_path)

                        # Clone repository with submodules
                        result = subprocess.run(
                            ["git", "clone", "--recurse-submodules", project.git_url, repo_name],
                            cwd=parent_dir,
                            capture_output=True,
                            text=True,
                            timeout=300  # 5 minutes timeout
                        )

                        if result.returncode != 0:
                            error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                            error_msg = f"❌ Ошибка клонирования репозитория:\n```\n{error_details}\n```"
                            try:
                                await progress_msg.delete()
                            except Exception:
                                pass
                            await ctx.update.effective_message.reply_text(error_msg, parse_mode='Markdown')
                            return CommandResult(success=False, error=f"Git clone failed: {error_details}")

                        # After cloning, checkout dev branch
                        result = subprocess.run(
                            ["git", "-C", repo_path, "checkout", project.dev_branch],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                    except subprocess.TimeoutExpired:
                        try:
                            await progress_msg.delete()
                        except Exception:
                            pass
                        await ctx.update.effective_message.reply_text(
                            "❌ Превышено время ожидания клонирования репозитория"
                        )
                        return CommandResult(success=False, error="Clone timeout")
                    except Exception as e:
                        try:
                            await progress_msg.delete()
                        except Exception:
                            pass
                        await ctx.update.effective_message.reply_text(
                            f"❌ Ошибка при клонировании: {str(e)}"
                        )
                        return CommandResult(success=False, error=f"Clone error: {str(e)}")
                else:
                    # Repository exists, update it
                    try:
                        # Fetch latest changes
                        result = subprocess.run(
                            ["git", "-C", repo_path, "fetch", "--all"],
                            capture_output=True,
                            text=True,
                            timeout=120  # 2 minutes timeout
                        )

                        if result.returncode != 0:
                            error_details = result.stderr if result.stderr else "Неизвестная ошибка"
                            error_msg = f"❌ Ошибка обновления репозитория:\n```\n{error_details}\n```"
                            try:
                                await progress_msg.delete()
                            except Exception:
                                pass
                            await ctx.update.effective_message.reply_text(error_msg, parse_mode='Markdown')
                            return CommandResult(success=False, error=f"Git fetch failed: {error_details}")

                        # Checkout dev branch
                        result = subprocess.run(
                            ["git", "-C", repo_path, "checkout", project.dev_branch],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                        # Pull latest changes from dev branch
                        result = subprocess.run(
                            ["git", "-C", repo_path, "pull", "origin", project.dev_branch],
                            capture_output=True,
                            text=True,
                            timeout=120
                        )

                        # Update submodules
                        subprocess.run(
                            ["git", "-C", repo_path, "submodule", "update", "--init", "--recursive"],
                            capture_output=True,
                            text=True,
                            timeout=120
                        )

                    except subprocess.TimeoutExpired:
                        try:
                            await progress_msg.delete()
                        except Exception:
                            pass
                        await ctx.update.effective_message.reply_text(
                            "❌ Превышено время ожидания обновления репозитория"
                        )
                        return CommandResult(success=False, error="Fetch timeout")
                    except Exception as e:
                        try:
                            await progress_msg.delete()
                        except Exception:
                            pass
                        await ctx.update.effective_message.reply_text(
                            f"❌ Ошибка при обновлении: {str(e)}"
                        )
                        return CommandResult(success=False, error=f"Fetch error: {str(e)}")

                # Start release preparation
                success, result_message = await prepare_cmd.prepare_release_direct(project, send_message, show_start_message=False)

                return CommandResult(
                    success=success,
                    message=result_message
                )
            except Exception as e:
                # Delete progress message on error
                try:
                    await progress_msg.delete()
                except Exception:
                    pass

                error_msg = f"❌ Ошибка при подготовке релиза: {str(e)}"
                await ctx.update.effective_message.reply_text(error_msg)
                return CommandResult(
                    success=False,
                    error=error_msg
                )

        # Sort projects by name
        sorted_projects = sorted(projects, key=lambda p: p.name.lower())

        # Build keyboard with projects
        keyboard = []
        for project in sorted_projects:
            # Create button with project name and type emoji
            emoji = {
                "flutter": "🦋",
                "dotnet_maui": "🔷",
                "xamarin": "🔶"
            }.get(project.project_type.value, "📦")

            button_text = f"{emoji} {project.name}"
            callback_data = f"build_project:{project.id}"

            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        message = f"🔨 Выберите проект для сборки ({context_msg}):"
        await ctx.update.effective_message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return CommandResult(success=True, message=message)
