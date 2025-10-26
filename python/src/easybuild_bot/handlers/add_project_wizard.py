"""
Step-by-step wizard for adding a new project.
Implements ConversationHandler with multiple states.
"""

import uuid
import logging
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from ..models import Project, ProjectType
from ..storage import Storage
from ..access_control import AccessControlService

logger = logging.getLogger(__name__)

# Conversation states
(
    WAITING_NAME,
    WAITING_TYPE,
    WAITING_GIT_URL,
    WAITING_PROJECT_FILE_PATH,
    WAITING_LOCAL_PATH,
    WAITING_DEV_BRANCH,
    WAITING_RELEASE_BRANCH,
    CONFIRM
) = range(8)


def escape_md(text: str) -> str:
    """Escape special characters for MarkdownV2."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


class AddProjectWizard:
    """Wizard for step-by-step project creation."""
    
    def __init__(self, storage: Storage, access_control: Optional[AccessControlService] = None):
        """
        Initialize wizard with storage and access control.
        
        Args:
            storage: Database storage instance
            access_control: Access control service instance (optional)
        """
        self.storage = storage
        self.access_control = access_control
    
    async def _check_admin_access(self, update: Update) -> bool:
        """Check if user has admin access."""
        user = update.effective_user
        if not user:
            return False
        
        # If access control is not provided, allow all users
        if not self.access_control:
            return True
        
        # Check if user is registered and is admin
        bot_user = self.storage.get_user_by_user_id(user.id)
        if not bot_user:
            return False
        
        return bot_user.is_admin
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the wizard and ask for project name."""
        # Check admin access
        if not await self._check_admin_access(update):
            await update.effective_message.reply_text(
                "❌ У вас нет прав для создания проектов\\.\n"
                "Эта команда доступна только администраторам\\.",
                parse_mode="MarkdownV2"
            )
            return ConversationHandler.END
        
        # Initialize conversation data
        context.user_data['project_data'] = {}
        
        msg = (
            "📝 *Шаг 1 из 7: Название проекта*\n\n"
            "Введите уникальное название для вашего проекта\\.\n"
            "Например: `MyApp`, `CoolProject`, `EasyBuildBot`\n\n"
            "💡 _Название должно быть уникальным и понятным\\._"
        )
        await update.effective_message.reply_text(msg, parse_mode="MarkdownV2")
        return WAITING_NAME
    
    async def receive_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receive project name and ask for project type."""
        name = update.effective_message.text.strip()
        
        # Validate name
        if not name:
            await update.effective_message.reply_text("❌ Название не может быть пустым. Попробуйте ещё раз:")
            return WAITING_NAME
        
        # Check if project already exists
        existing = self.storage.get_project_by_name(name)
        if existing:
            msg = f"❌ Проект с именем `{escape_md(name)}` уже существует\\!\nВведите другое название:"
            await update.effective_message.reply_text(msg, parse_mode="MarkdownV2")
            return WAITING_NAME
        
        # Save name
        context.user_data['project_data']['name'] = name
        
        # Ask for project type
        keyboard = [
            [InlineKeyboardButton("🦋 Flutter", callback_data="type_flutter")],
            [InlineKeyboardButton("🔷 .NET MAUI", callback_data="type_dotnet_maui")],
            [InlineKeyboardButton("🔶 Xamarin", callback_data="type_xamarin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg = (
            "📦 *Шаг 2 из 7: Тип проекта*\n\n"
            f"Отлично\\! Название: `{escape_md(name)}`\n\n"
            "Теперь выберите тип проекта:"
        )
        await update.effective_message.reply_text(msg, parse_mode="MarkdownV2", reply_markup=reply_markup)
        return WAITING_TYPE
    
    async def receive_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receive project type and ask for Git URL."""
        query = update.callback_query
        await query.answer()
        
        # Parse type from callback data
        type_map = {
            "type_flutter": (ProjectType.FLUTTER, "🦋 Flutter"),
            "type_dotnet_maui": (ProjectType.DOTNET_MAUI, "🔷 .NET MAUI"),
            "type_xamarin": (ProjectType.XAMARIN, "🔶 Xamarin")
        }
        
        project_type, type_display = type_map.get(query.data, (None, None))
        if not project_type:
            await query.message.reply_text("❌ Неизвестный тип проекта. Попробуйте ещё раз.")
            return WAITING_TYPE
        
        # Save type
        context.user_data['project_data']['project_type'] = project_type
        context.user_data['project_data']['type_display'] = type_display
        
        # Ask for Git URL
        msg = (
            "🔗 *Шаг 3 из 7: Git URL*\n\n"
            f"Тип проекта: {escape_md(type_display)}\n\n"
            "Введите URL Git\\-репозитория проекта\\.\n"
            "Например: `https://github.com/user/myapp.git`"
        )
        await query.message.reply_text(msg, parse_mode="MarkdownV2")
        return WAITING_GIT_URL
    
    async def receive_git_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receive Git URL and ask for project file path."""
        git_url = update.effective_message.text.strip()
        
        # Basic validation
        if not git_url:
            await update.effective_message.reply_text("❌ Git URL не может быть пустым. Попробуйте ещё раз:")
            return WAITING_GIT_URL
        
        # Save Git URL
        context.user_data['project_data']['git_url'] = git_url
        
        # Ask for project file path
        msg = (
            "📁 *Шаг 4 из 7: Путь к файлу проекта*\n\n"
            "Введите относительный путь к файлу проекта от корня репозитория\\.\n\n"
            "*Примеры:*\n"
            "• Flutter: `android/app` или `ios/Runner`\n"
            "• \\.NET MAUI: `src/MyApp/MyApp.csproj`\n"
            "• Xamarin: `MyApp/MyApp\\.Android/MyApp\\.Android\\.csproj`"
        )
        await update.effective_message.reply_text(msg, parse_mode="MarkdownV2")
        return WAITING_PROJECT_FILE_PATH
    
    async def receive_project_file_path(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receive project file path and ask for local repository path."""
        project_file_path = update.effective_message.text.strip()
        
        # Validation
        if not project_file_path:
            await update.effective_message.reply_text("❌ Путь не может быть пустым. Попробуйте ещё раз:")
            return WAITING_PROJECT_FILE_PATH
        
        # Save path
        context.user_data['project_data']['project_file_path'] = project_file_path
        
        # Ask for local repo path
        msg = (
            "💾 *Шаг 5 из 7: Локальный путь к репозиторию*\n\n"
            "Введите путь к папке, где будет храниться локальная копия репозитория на сервере\\.\n\n"
            "*Пример:*\n"
            "`/home/repos/myapp`"
        )
        await update.effective_message.reply_text(msg, parse_mode="MarkdownV2")
        return WAITING_LOCAL_PATH
    
    async def receive_local_path(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receive local path and ask for dev branch."""
        local_path = update.effective_message.text.strip()
        
        # Validation
        if not local_path:
            await update.effective_message.reply_text("❌ Путь не может быть пустым. Попробуйте ещё раз:")
            return WAITING_LOCAL_PATH
        
        # Save path
        context.user_data['project_data']['local_repo_path'] = local_path
        
        # Ask for dev branch
        msg = (
            "🌿 *Шаг 6 из 7: Ветка разработки*\n\n"
            "Введите название ветки разработки \\(development branch\\)\\.\n\n"
            "💡 Нажмите /skip, чтобы использовать значение по умолчанию: `develop`"
        )
        await update.effective_message.reply_text(msg, parse_mode="MarkdownV2")
        return WAITING_DEV_BRANCH
    
    async def receive_dev_branch(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receive dev branch and ask for release branch."""
        dev_branch = update.effective_message.text.strip()
        
        # Use default if empty
        if not dev_branch or dev_branch == "/skip":
            dev_branch = "develop"
        
        # Save branch
        context.user_data['project_data']['dev_branch'] = dev_branch
        
        # Ask for release branch
        msg = (
            "🚀 *Шаг 7 из 7: Ветка релиза*\n\n"
            "Введите название ветки релиза \\(release/production branch\\)\\.\n\n"
            "💡 Нажмите /skip, чтобы использовать значение по умолчанию: `main`"
        )
        await update.effective_message.reply_text(msg, parse_mode="MarkdownV2")
        return WAITING_RELEASE_BRANCH
    
    async def receive_release_branch(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receive release branch and show confirmation."""
        release_branch = update.effective_message.text.strip()
        
        # Use default if empty
        if not release_branch or release_branch == "/skip":
            release_branch = "main"
        
        # Save branch
        context.user_data['project_data']['release_branch'] = release_branch
        
        # Show confirmation
        data = context.user_data['project_data']
        
        confirmation_msg = (
            "✅ *Проверьте введённые данные:*\n\n"
            f"📝 *Название:* `{escape_md(data['name'])}`\n"
            f"📦 *Тип:* {escape_md(data['type_display'])}\n"
            f"🔗 *Git URL:* `{escape_md(data['git_url'])}`\n"
            f"📁 *Файл проекта:* `{escape_md(data['project_file_path'])}`\n"
            f"💾 *Локальный путь:* `{escape_md(data['local_repo_path'])}`\n"
            f"🌿 *Ветка разработки:* `{escape_md(data['dev_branch'])}`\n"
            f"🚀 *Ветка релиза:* `{escape_md(data['release_branch'])}`\n\n"
            "Всё верно?"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Да, создать", callback_data="confirm_yes"),
                InlineKeyboardButton("❌ Отменить", callback_data="confirm_no")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_message.reply_text(
            confirmation_msg,
            parse_mode="MarkdownV2",
            reply_markup=reply_markup
        )
        return CONFIRM
    
    async def confirm_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Create the project or cancel."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "confirm_no":
            await query.message.reply_text(
                "❌ Создание проекта отменено\\.\n"
                "Используйте /add\\_project, чтобы начать заново\\.",
                parse_mode="MarkdownV2"
            )
            context.user_data.clear()
            return ConversationHandler.END
        
        # Create project
        data = context.user_data['project_data']
        
        try:
            project = Project(
                id=str(uuid.uuid4()),
                name=data['name'],
                project_type=data['project_type'],
                git_url=data['git_url'],
                project_file_path=data['project_file_path'],
                local_repo_path=data['local_repo_path'],
                dev_branch=data['dev_branch'],
                release_branch=data['release_branch'],
                allowed_group_ids=[],  # Empty means available for all groups
                tags=[],
                description=None
            )
            
            # Save to database
            self.storage.add_project(project)
            
            # Build success message
            type_emoji = {
                ProjectType.FLUTTER: "🦋",
                ProjectType.DOTNET_MAUI: "🔷",
                ProjectType.XAMARIN: "🔶"
            }.get(project.project_type, "📦")
            
            success_msg = (
                f"🎉 *Проект успешно создан\\!*\n\n"
                f"{type_emoji} *Название:* {escape_md(data['name'])}\n"
                f"🆔 *ID:* `{escape_md(project.id)}`\n\n"
                f"Используйте `/edit\\_project {escape_md(data['name'])}` для редактирования проекта\\."
            )
            
            await query.message.reply_text(success_msg, parse_mode="MarkdownV2")
            
            logger.info(f"Project '{data['name']}' created successfully by user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Failed to create project: {str(e)}")
            await query.message.reply_text(
                f"❌ Ошибка при создании проекта: {str(e)}\n"
                "Попробуйте ещё раз позже\\.",
                parse_mode="MarkdownV2"
            )
        finally:
            context.user_data.clear()
        
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the wizard."""
        await update.effective_message.reply_text(
            "❌ Создание проекта отменено\\.\n"
            "Используйте /add\\_project, чтобы начать заново\\.",
            parse_mode="MarkdownV2"
        )
        context.user_data.clear()
        return ConversationHandler.END

