"""
Interactive wizard for editing project fields.
Implements ConversationHandler with field selection menu.
"""

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
    SELECT_PROJECT,
    SELECT_FIELD,
    EDIT_VALUE,
    SELECT_GROUP,
    CONFIRM
) = range(5)


def escape_md(text: str) -> str:
    """Escape special characters for MarkdownV2."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def format_value(field: str, value, storage=None) -> str:
    """Format field value for display."""
    if value is None or value == "":
        return "_не задано_"

    if field == "project_type":
        type_emoji = {
            ProjectType.FLUTTER: "🦋",
            ProjectType.DOTNET_MAUI: "🔷",
            ProjectType.XAMARIN: "🔶"
        }
        return f"{type_emoji.get(value, '📦')} {value.value}"
    elif field == "tags":
        return ", ".join(value) if value else "_нет тегов_"
    elif field == "allowed_group_ids":
        if not value:
            return "_все группы_"
        # Display group name if available
        if storage and len(value) > 0:
            group = next((g for g in storage.get_all_groups() if g.group_id == value[0]), None)
            if group:
                return group.group_name or f"Группа {value[0]}"
        return str(value[0])
    else:
        return str(value)


class EditProjectWizard:
    """Wizard for interactive project editing."""

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

        if not self.access_control:
            return True

        bot_user = self.storage.get_user_by_user_id(user.id)
        if not bot_user:
            return False

        return bot_user.is_admin

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the wizard - show project selection or use provided name."""
        # Check admin access
        if not await self._check_admin_access(update):
            await update.effective_message.reply_text(
                "❌ У вас нет прав для редактирования проектов\\.\n"
                "Эта команда доступна только администраторам\\.",
                parse_mode="MarkdownV2"
            )
            return ConversationHandler.END

        # Check if this is a direct command with field and value arguments
        # Format: /edit_project <name> <field> <value>
        if context.args and len(context.args) >= 2:
            # This looks like a direct command, not wizard
            # Let it be handled by EditProjectCommand instead
            # We should not start the wizard in this case
            await update.effective_message.reply_text(
                "❌ Прямое редактирование через аргументы команды больше не поддерживается\\.\n\n"
                "Используйте интерактивный мастер:\n"
                "• `/edit_project` \\- выбрать проект из списка\n"
                "• `/edit_project <название>` \\- редактировать конкретный проект\n\n"
                "Пример: `/edit_project MyApp`",
                parse_mode="MarkdownV2"
            )
            return ConversationHandler.END

        # Check if project name was provided as argument (wizard with pre-selected project)
        if context.args and len(context.args) == 1:
            project_name = context.args[0]
            project = self.storage.get_project_by_name(project_name)

            if not project:
                await update.effective_message.reply_text(
                    f"❌ Проект `{escape_md(project_name)}` не найден\\!",
                    parse_mode="MarkdownV2"
                )
                return ConversationHandler.END

            # Save project to context
            context.user_data['edit_project'] = project
            context.user_data['edit_data'] = {}

            # Show field selection menu
            return await self.show_field_menu(update, context)
        else:
            # Show project selection
            return await self.show_project_list(update, context)

    async def show_project_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Show list of projects to select from."""
        projects = self.storage.get_all_projects()

        if not projects:
            await update.effective_message.reply_text(
                "📭 Нет доступных проектов для редактирования\\.",
                parse_mode="MarkdownV2"
            )
            return ConversationHandler.END

        # Build keyboard with projects
        keyboard = []
        for project in projects:
            type_emoji = {
                ProjectType.FLUTTER: "🦋",
                ProjectType.DOTNET_MAUI: "🔷",
                ProjectType.XAMARIN: "🔶"
            }.get(project.project_type, "📦")

            button_text = f"{type_emoji} {project.name}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"edit_select_{project.id}")])

        keyboard.append([InlineKeyboardButton("❌ Отменить", callback_data="edit_cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = (
            "📋 *Выберите проект для редактирования:*\n\n"
            "Нажмите на проект, чтобы открыть меню редактирования\\."
        )

        await update.effective_message.reply_text(
            msg,
            parse_mode="MarkdownV2",
            reply_markup=reply_markup
        )

        return SELECT_PROJECT

    async def select_project(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle project selection."""
        query = update.callback_query
        await query.answer()

        if query.data == "edit_cancel":
            await query.message.edit_text("❌ Редактирование отменено\\.", parse_mode="MarkdownV2")
            context.user_data.clear()
            return ConversationHandler.END

        # Extract project ID
        project_id = query.data.replace("edit_select_", "")
        project = self.storage.get_project_by_id(project_id)

        if not project:
            await query.message.edit_text("❌ Проект не найден\\!", parse_mode="MarkdownV2")
            return ConversationHandler.END

        # Save project to context
        context.user_data['edit_project'] = project
        context.user_data['edit_data'] = {}

        # Delete selection message and show field menu
        await query.message.delete()

        # Need to send new message since we deleted the old one
        return await self.show_field_menu_new_message(update, context)

    async def show_field_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Show menu with all editable fields and their current values."""
        project = context.user_data['edit_project']

        msg, keyboard = self._build_field_menu_content(project)
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send or edit message
        if update.callback_query:
            await update.callback_query.message.edit_text(
                msg,
                parse_mode="MarkdownV2",
                reply_markup=reply_markup
            )
        else:
            await update.effective_message.reply_text(
                msg,
                parse_mode="MarkdownV2",
                reply_markup=reply_markup
            )

        return SELECT_FIELD

    async def show_field_menu_new_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Show menu with all editable fields (send as new message)."""
        project = context.user_data['edit_project']

        msg, keyboard = self._build_field_menu_content(project)
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Always send as new message
        await update.effective_message.reply_text(
            msg,
            parse_mode="MarkdownV2",
            reply_markup=reply_markup
        )

        return SELECT_FIELD

    def _build_field_menu_content(self, project: Project) -> tuple[str, list]:
        """Build field menu message content and keyboard."""
        # Build field buttons
        fields = [
            ("✏️ Название проекта", "name", project.name),
            ("📝 Описание", "description", project.description),
            ("🔗 Git URL", "git_url", project.git_url),
            ("📁 Путь к файлу проекта", "project_file_path", project.project_file_path),
            ("🌿 Ветка разработки", "dev_branch", project.dev_branch),
            ("🚀 Ветка релиза", "release_branch", project.release_branch),
            ("🏷️ Теги", "tags", project.tags),
            ("👥 Группы", "allowed_group_ids", project.allowed_group_ids),
        ]

        # Build message with current values
        type_emoji = {
            ProjectType.FLUTTER: "🦋",
            ProjectType.DOTNET_MAUI: "🔷",
            ProjectType.XAMARIN: "🔶"
        }.get(project.project_type, "📦")

        msg = (
            f"✏️ *Редактирование проекта*\n\n"
            f"{type_emoji} *Проект:* `{escape_md(project.name)}`\n"
            f"📦 *Тип:* {escape_md(project.project_type.value)}\n\n"
            f"*Текущие значения:*\n\n"
        )

        keyboard = []
        for label, field_name, value in fields:
            formatted_value = format_value(field_name, value, self.storage)
            msg += f"{label}: {escape_md(str(formatted_value)) if not formatted_value.startswith('_') else formatted_value}\n"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"edit_field_{field_name}")])

        msg += "\n💡 _Выберите поле для редактирования:_"

        keyboard.append([InlineKeyboardButton("✅ Сохранить и выйти", callback_data="edit_save")])
        keyboard.append([InlineKeyboardButton("❌ Отменить", callback_data="edit_cancel")])

        return msg, keyboard

    async def select_field(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle field selection."""
        query = update.callback_query
        await query.answer()

        if query.data == "edit_cancel":
            await query.message.edit_text("❌ Редактирование отменено\\. Изменения не сохранены\\.", parse_mode="MarkdownV2")
            context.user_data.clear()
            return ConversationHandler.END

        if query.data == "edit_save":
            return await self.save_changes(update, context)

        # Extract field name
        field_name = query.data.replace("edit_field_", "")
        context.user_data['editing_field'] = field_name

        # Special handling for allowed_group_ids - show list of registered groups
        if field_name == "allowed_group_ids":
            return await self.show_group_selection(update, context)

        project = context.user_data['edit_project']

        # Get current value
        current_value = getattr(project, field_name)
        formatted_value = format_value(field_name, current_value, self.storage)

        # Field descriptions and hints
        field_info = {
            "name": ("✏️ Название проекта", "уникальное название проекта", "MyApp"),
            "description": ("📝 Описание проекта", "краткое описание проекта", "Мое приложение для Android"),
            "git_url": ("🔗 Git URL", "URL репозитория", "https://github.com/user/myapp.git"),
            "project_file_path": ("📁 Путь к файлу проекта", "относительный путь от корня репозитория", "android/app"),
            "dev_branch": ("🌿 Ветка разработки", "название ветки", "develop"),
            "release_branch": ("🚀 Ветка релиза", "название ветки", "main"),
            "tags": ("🏷️ Теги", "теги через запятую", "mobile,android,prod"),
        }

        label, hint, example = field_info.get(field_name, (field_name, "", ""))

        msg = (
            f"✏️ *Редактирование поля*\n\n"
            f"*Поле:* {escape_md(label)}\n"
            f"*Текущее значение:*\n{escape_md(str(formatted_value)) if not formatted_value.startswith('_') else formatted_value}\n\n"
            f"💡 Введите новое значение:\n"
            f"_{escape_md(hint)}_\n\n"
            f"*Пример:* `{escape_md(example)}`\n\n"
            f"Или введите `/back` для возврата к меню\\.\n"
            f"ℹ️ Используйте /cancel для отмены всех изменений\\."
        )

        await query.message.edit_text(msg, parse_mode="MarkdownV2")

        return EDIT_VALUE

    async def show_group_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Show registered groups as buttons for selection."""
        query = update.callback_query
        project = context.user_data['edit_project']

        # Get all registered groups
        groups = self.storage.get_all_groups()

        if not groups:
            await query.message.edit_text(
                "❌ Нет зарегистрированных групп\\!\n\n"
                "Сначала зарегистрируйте группы через команду `/register_group`\\.",
                parse_mode="MarkdownV2"
            )
            return await self.show_field_menu(update, context)

        # Get current group ID (if any)
        current_group_id = project.allowed_group_ids[0] if project.allowed_group_ids else None

        # Build keyboard with groups
        keyboard = []
        for group in groups:
            # Mark currently selected group
            prefix = "✅ " if current_group_id == group.group_id else ""
            button_text = f"{prefix}{group.group_name or f'Группа {group.group_id}'}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"select_group_{group.group_id}")])

        # Add "no group" option (empty allowed_group_ids = available for all groups)
        prefix = "✅ " if not project.allowed_group_ids else ""
        keyboard.append([InlineKeyboardButton(f"{prefix}🌍 Все группы", callback_data="select_group_all")])

        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="group_back")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Format current value
        current_value_text = "_все группы_"
        if project.allowed_group_ids:
            # Find group name by ID
            group = next((g for g in groups if g.group_id == project.allowed_group_ids[0]), None)
            if group:
                current_value_text = escape_md(group.group_name or f"Группа {group.group_id}")
            else:
                current_value_text = escape_md(f"ID: {project.allowed_group_ids[0]}")

        msg = (
            f"👥 *Выбор группы для проекта*\n\n"
            f"📦 *Проект:* `{escape_md(project.name)}`\n"
            f"*Текущая группа:* {current_value_text}\n\n"
            f"💡 Выберите группу, для которой будет доступен проект:\n"
            f"_\\(только одна группа на проект по бизнес\\-требованиям\\)_"
        )

        await query.message.edit_text(msg, parse_mode="MarkdownV2", reply_markup=reply_markup)

        return SELECT_GROUP

    async def handle_group_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle group selection from buttons."""
        query = update.callback_query
        await query.answer()

        if query.data == "group_back":
            return await self.show_field_menu(update, context)

        project = context.user_data['edit_project']

        if query.data == "select_group_all":
            # Set to empty list (available for all groups)
            new_value = []
        else:
            # Extract group ID and set as single-element list
            group_id = int(query.data.replace("select_group_", ""))
            new_value = [group_id]

        # Save to edit_data (not to project yet)
        context.user_data['edit_data']['allowed_group_ids'] = new_value

        # Get group name for confirmation message
        if new_value:
            groups = self.storage.get_all_groups()
            group = next((g for g in groups if g.group_id == new_value[0]), None)
            group_name = group.group_name if group else f"ID: {new_value[0]}"
            value_text = escape_md(group_name)
        else:
            value_text = "все группы"

        await query.message.edit_text(
            f"✅ Группа изменена на: {value_text}\\!\n\n"
            f"Изменения будут применены после нажатия \"Сохранить и выйти\"\\.",
            parse_mode="MarkdownV2"
        )

        # Return to field menu
        return await self.show_field_menu(update, context)

    async def receive_value(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receive new value for the field."""
        text = update.effective_message.text.strip()

        # Allow cancellation at any point
        if text == "/cancel":
            return await self.cancel(update, context)

        if text == "/back":
            return await self.show_field_menu(update, context)

        field_name = context.user_data['editing_field']
        project = context.user_data['edit_project']

        try:
            # Parse and validate value based on field type
            if field_name == "name":
                # Validate that name is not empty and unique
                if not text or not text.strip():
                    await update.effective_message.reply_text(
                        "❌ Название проекта не может быть пустым\\!",
                        parse_mode="MarkdownV2"
                    )
                    return EDIT_VALUE

                # Check if name already exists (excluding current project)
                existing_project = self.storage.get_project_by_name(text)
                if existing_project and existing_project.id != project.id:
                    await update.effective_message.reply_text(
                        f"❌ Проект с названием `{escape_md(text)}` уже существует\\!\n"
                        f"Выберите другое название\\.",
                        parse_mode="MarkdownV2"
                    )
                    return EDIT_VALUE

                new_value = text.strip()
            elif field_name == "tags":
                new_value = [tag.strip() for tag in text.split(",") if tag.strip()]
            elif field_name == "description":
                new_value = text if text else None
            else:
                new_value = text

            # Save to edit_data (not to project yet)
            context.user_data['edit_data'][field_name] = new_value

            await update.effective_message.reply_text(
                f"✅ Значение сохранено\\!\n\n"
                f"Изменения будут применены после нажатия \"Сохранить и выйти\"\\.",
                parse_mode="MarkdownV2"
            )

            # Return to field menu
            return await self.show_field_menu(update, context)

        except Exception as e:
            logger.error(f"Error updating field: {str(e)}")
            await update.effective_message.reply_text(
                f"❌ Ошибка: {escape_md(str(e))}",
                parse_mode="MarkdownV2"
            )
            return EDIT_VALUE

    async def save_changes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Save all changes to the project."""
        query = update.callback_query

        project = context.user_data['edit_project']
        changes = context.user_data['edit_data']

        if not changes:
            await query.message.edit_text(
                "ℹ️ Изменений не было\\.\nРедактирование завершено\\.",
                parse_mode="MarkdownV2"
            )
            context.user_data.clear()
            return ConversationHandler.END

        # Apply all changes
        for field_name, value in changes.items():
            setattr(project, field_name, value)

        # Save to database
        try:
            self.storage.add_project(project)

            # Build success message
            msg = (
                f"✅ *Проект `{escape_md(project.name)}` обновлен\\!*\n\n"
                f"*Изменено полей:* {len(changes)}\n\n"
            )

            for field_name in changes.keys():
                value = getattr(project, field_name)
                formatted = format_value(field_name, value, self.storage)
                msg += f"• {escape_md(field_name)}: {escape_md(str(formatted)) if not formatted.startswith('_') else formatted}\n"

            await query.message.edit_text(msg, parse_mode="MarkdownV2")

            logger.info(f"Project '{project.name}' updated by user {update.effective_user.id}")

        except Exception as e:
            logger.error(f"Failed to save project: {str(e)}")
            await query.message.edit_text(
                f"❌ Ошибка при сохранении: {escape_md(str(e))}",
                parse_mode="MarkdownV2"
            )
        finally:
            context.user_data.clear()

        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the wizard."""
        await update.effective_message.reply_text(
            "❌ Редактирование отменено\\.\nИзменения не сохранены\\.",
            parse_mode="MarkdownV2"
        )
        context.user_data.clear()
        return ConversationHandler.END
