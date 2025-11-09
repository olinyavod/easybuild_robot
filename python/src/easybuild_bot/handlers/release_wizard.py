"""
Release wizard handler for version input and build execution.
"""

import os
import subprocess
import logging
import re
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

# Conversation state
WAITING_VERSION = 1


class ReleaseWizard:
    """Wizard for handling release with version input."""
    
    def __init__(self, storage, access_control=None):
        self.storage = storage
        self.access_control = access_control
    
    async def receive_version(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receive version from user and start release."""
        text = update.effective_message.text.strip()
        
        # Get project from context
        project = context.user_data.get('release_project')
        if not project:
            await update.effective_message.reply_text(
                "❌ Ошибка: проект не найден. Пожалуйста, начните заново с /release"
            )
            context.user_data.clear()
            return ConversationHandler.END
        
        # Validate version format (X.Y.Z)
        version_pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(version_pattern, text):
            await update.effective_message.reply_text(
                "❌ Неверный формат версии!\n\n"
                "Пожалуйста, используйте формат `X.Y.Z` (например: `1.2.3`)\n\n"
                "Или отправьте `/cancel` для отмены.",
                parse_mode='Markdown'
            )
            return WAITING_VERSION
        
        new_version = text
        
        # Send progress message
        progress_msg = await update.effective_message.reply_text(
            f"🔄 Подготовка репозитория **{project.name}** к релизу версии `{new_version}`...",
            parse_mode='Markdown'
        )
        
        # Execute the release preparation
        try:
            from ..commands.implementations.prepare_release_callback import PrepareReleaseCallbackCommand
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
                await update.effective_message.reply_text(msg, parse_mode='Markdown')
            
            # Execute repository preparation and release
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
                        await update.effective_message.reply_text(error_msg, parse_mode='Markdown')
                        context.user_data.clear()
                        return ConversationHandler.END
                    
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
                    await update.effective_message.reply_text(
                        "❌ Превышено время ожидания клонирования репозитория"
                    )
                    context.user_data.clear()
                    return ConversationHandler.END
                except Exception as e:
                    try:
                        await progress_msg.delete()
                    except Exception:
                        pass
                    await update.effective_message.reply_text(
                        f"❌ Ошибка при клонировании: {str(e)}"
                    )
                    context.user_data.clear()
                    return ConversationHandler.END
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
                        await update.effective_message.reply_text(error_msg, parse_mode='Markdown')
                        context.user_data.clear()
                        return ConversationHandler.END
                    
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
                    await update.effective_message.reply_text(
                        "❌ Превышено время ожидания обновления репозитория"
                    )
                    context.user_data.clear()
                    return ConversationHandler.END
                except Exception as e:
                    try:
                        await progress_msg.delete()
                    except Exception:
                        pass
                    await update.effective_message.reply_text(
                        f"❌ Ошибка при обновлении: {str(e)}"
                    )
                    context.user_data.clear()
                    return ConversationHandler.END
            
            # Get version service
            from ..version_services import VersionServiceFactory
            version_service = VersionServiceFactory.create(project)
            
            if not version_service:
                error_msg = f"❌ Тип проекта {project.project_type.value} не поддерживается"
                try:
                    await progress_msg.delete()
                except Exception:
                    pass
                await update.effective_message.reply_text(error_msg)
                context.user_data.clear()
                return ConversationHandler.END
            
            # Get current version for display
            current_version = await version_service.get_current_version(project)
            
            # Start release preparation with custom version
            success, result_message = await prepare_cmd.prepare_release(
                project, 
                new_version, 
                send_message, 
                current_version=current_version, 
                version_service=version_service
            )
            
            # Clear context
            context.user_data.clear()
            
            return ConversationHandler.END
            
        except Exception as e:
            # Delete progress message on error
            try:
                await progress_msg.delete()
            except Exception:
                pass
            
            error_msg = f"❌ Ошибка при подготовке релиза: {str(e)}"
            await update.effective_message.reply_text(error_msg)
            logger.exception(f"Error in release wizard: {e}")
            context.user_data.clear()
            return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the release wizard."""
        await update.effective_message.reply_text(
            "❌ Релиз отменён."
        )
        context.user_data.clear()
        return ConversationHandler.END


