"""
Callback command for project selection and git cloning.
"""

import os
import subprocess
from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ..callback_base import CallbackCommand
from ..base import CommandContext, CommandResult


class ProjectSelectCallbackCommand(CallbackCommand):
    """Handle project selection callbacks - clone git repository and prepare for build."""
    
    def get_command_name(self) -> str:
        return "callback:build_project"
    
    def get_callback_pattern(self) -> str:
        return r"^build_project:.*$"
    
    async def can_execute(self, ctx: CommandContext) -> tuple[bool, Optional[str]]:
        """Check if user has access."""
        return await self._check_user_access(ctx.update, require_admin=False)
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute project selection callback."""
        query = ctx.update.callback_query
        if not query or not query.data:
            return CommandResult(success=False, error="Invalid callback query")
        
        # Extract project ID from callback data
        # Format: build_project:<project_id>
        parts = query.data.split(":", 1)
        if len(parts) != 2:
            await query.answer(text="Неверный формат данных", show_alert=True)
            return CommandResult(success=False, error="Invalid callback data format")
        
        project_id = parts[1]
        
        # Get project from database
        project = self.storage.get_project_by_id(project_id)
        if not project:
            await query.answer(text="Проект не найден", show_alert=True)
            return CommandResult(success=False, error="Project not found")
        
        # Answer callback to remove loading state
        await query.answer()
        
        # Delete the message with project selection
        try:
            await query.message.delete()
        except Exception:
            pass  # Ignore if we can't delete the message
        
        # Send message about repository preparation
        progress_msg = await ctx.update.effective_message.reply_text(
            f"🔄 Подготовка репозитория **{project.name}** к публикации...",
            parse_mode='Markdown'
        )
        
        # Get absolute path for the repository (already normalized in Storage)
        repo_path = project.local_repo_path
        
        # Check if local repository path exists
        if not os.path.exists(repo_path):
            # Repository doesn't exist, need to clone
            try:
                # Create parent directory if it doesn't exist
                parent_dir = os.path.dirname(repo_path)
                if parent_dir:  # Only create if parent_dir is not empty
                    os.makedirs(parent_dir, exist_ok=True)
                
                # Extract the directory name for cloning
                repo_name = os.path.basename(repo_path)
                
                # Clone repository with submodules into parent directory
                # Git will automatically create a subdirectory with repo_name
                result = subprocess.run(
                    ["git", "clone", "--recurse-submodules", project.git_url, repo_name],
                    cwd=parent_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode != 0:
                    error_msg = f"❌ Ошибка клонирования репозитория"
                    # Delete progress message
                    try:
                        await progress_msg.delete()
                    except Exception:
                        pass
                    await ctx.update.effective_message.reply_text(error_msg)
                    return CommandResult(success=False, error="Git clone failed")
                
                # After cloning, checkout dev branch
                result = subprocess.run(
                    ["git", "-C", repo_path, "checkout", project.dev_branch],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    # If checkout fails, it's not critical - might already be on correct branch
                    pass
                
            except subprocess.TimeoutExpired:
                # Delete progress message
                try:
                    await progress_msg.delete()
                except Exception:
                    pass
                await ctx.update.effective_message.reply_text(
                    "❌ Превышено время ожидания клонирования репозитория"
                )
                return CommandResult(success=False, error="Clone timeout")
            except Exception as e:
                # Delete progress message
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
                    error_msg = f"❌ Ошибка обновления репозитория"
                    # Delete progress message
                    try:
                        await progress_msg.delete()
                    except Exception:
                        pass
                    await ctx.update.effective_message.reply_text(error_msg)
                    return CommandResult(success=False, error="Git fetch failed")
                
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
                # Delete progress message
                try:
                    await progress_msg.delete()
                except Exception:
                    pass
                await ctx.update.effective_message.reply_text(
                    "❌ Превышено время ожидания обновления репозитория"
                )
                return CommandResult(success=False, error="Fetch timeout")
            except Exception as e:
                # Delete progress message
                try:
                    await progress_msg.delete()
                except Exception:
                    pass
                await ctx.update.effective_message.reply_text(
                    f"❌ Ошибка при обновлении: {str(e)}"
                )
                return CommandResult(success=False, error=f"Fetch error: {str(e)}")
        
        # Delete progress message
        try:
            await progress_msg.delete()
        except Exception:
            pass
        
        # Automatically start release preparation
        from .prepare_release_callback import PrepareReleaseCallbackCommand
        prepare_cmd = PrepareReleaseCallbackCommand(self.storage, self.access_control)
        
        # We'll send only the final message
        final_message_sent = False
        
        async def send_message(msg: str):
            nonlocal final_message_sent
            # Only send the final success/error message
            if not final_message_sent:
                await ctx.update.effective_message.reply_text(msg, parse_mode='Markdown')
                final_message_sent = True
        
        success, message = await prepare_cmd.prepare_release_direct(project, send_message, show_start_message=False)
        
        return CommandResult(
            success=success,
            message=message
        )

