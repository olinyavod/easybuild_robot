"""
Test suite for Command Pattern implementation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from telegram import Update, User, Chat, Message
from telegram.ext import ContextTypes

from easybuild_bot.commands import Command, CommandContext, CommandResult, CommandRegistry, CommandExecutor
from easybuild_bot.commands.implementations import HelpCommand
from easybuild_bot.storage import Storage


@pytest.fixture
def mock_storage():
    """Create mock storage."""
    storage = Mock(spec=Storage)
    storage.get_user_by_user_id = Mock(return_value=None)
    storage.add_user = Mock()
    storage.get_all_users = Mock(return_value=[])
    storage.get_all_groups = Mock(return_value=[])
    storage.find_users_by_display_name = Mock(return_value=[])
    return storage


@pytest.fixture
def mock_update():
    """Create mock Telegram update."""
    update = Mock(spec=Update)
    update.effective_user = Mock(spec=User)
    update.effective_user.id = 12345
    update.effective_user.username = "testuser"
    update.effective_user.full_name = "Test User"

    update.effective_message = AsyncMock(spec=Message)
    update.effective_message.reply_text = AsyncMock()

    update.effective_chat = Mock(spec=Chat)
    update.effective_chat.id = 12345
    update.effective_chat.type = "private"

    return update


@pytest.fixture
def mock_context():
    """Create mock Telegram context."""
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = Mock()
    context.bot.id = 999999
    context.bot.username = "testbot"
    return context


class TestCommand:
    """Test Command base class."""

    def test_command_interface(self, mock_storage):
        """Test that commands implement required interface."""
        command = HelpCommand(mock_storage, "admin_token")

        assert command.get_command_name() == "/help"
        assert isinstance(command.get_semantic_tags(), list)
        assert len(command.get_semantic_tags()) > 0
        assert isinstance(command.get_parameter_patterns(), dict)

    @pytest.mark.asyncio
    async def test_can_execute_with_access(self, mock_storage, mock_update, mock_context):
        """Test can_execute with proper access."""
        # Create allowed user
        from easybuild_bot.models import BotUser
        allowed_user = BotUser(
            id="12345",
            user_id=12345,
            user_name="testuser",
            display_name="Test User",
            allowed=True
        )
        mock_storage.get_user_by_user_id.return_value = allowed_user

        command = HelpCommand(mock_storage, "admin_token")
        ctx = CommandContext(update=mock_update, context=mock_context, params={})

        can_exec, error = await command.can_execute(ctx)

        assert can_exec is True
        assert error is None

    @pytest.mark.asyncio
    async def test_can_execute_without_access(self, mock_storage, mock_update, mock_context):
        """Test can_execute without proper access."""
        # Create non-allowed user
        from easybuild_bot.models import BotUser
        non_allowed_user = BotUser(
            id="12345",
            user_id=12345,
            user_name="testuser",
            display_name="Test User",
            allowed=False
        )
        mock_storage.get_user_by_user_id.return_value = non_allowed_user

        command = HelpCommand(mock_storage, "admin_token")
        ctx = CommandContext(update=mock_update, context=mock_context, params={})

        can_exec, error = await command.can_execute(ctx)

        assert can_exec is False
        assert error is not None

    @pytest.mark.asyncio
    async def test_execute_success(self, mock_storage, mock_update, mock_context):
        """Test successful command execution."""
        command = HelpCommand(mock_storage, "admin_token")
        ctx = CommandContext(update=mock_update, context=mock_context, params={})

        result = await command.execute(ctx)

        assert result.success is True
        assert mock_update.effective_message.reply_text.called


class TestCommandRegistry:
    """Test CommandRegistry."""

    def test_register_command(self, mock_storage):
        """Test command registration."""
        registry = CommandRegistry(model_name="cointegrated/rubert-tiny", threshold=0.5)
        command = HelpCommand(mock_storage, "admin_token")

        registry.register(command)

        retrieved = registry.get_command("/help")
        assert retrieved is command

    def test_get_all_commands(self, mock_storage):
        """Test getting all commands."""
        registry = CommandRegistry(model_name="cointegrated/rubert-tiny", threshold=0.5)

        from easybuild_bot.commands.implementations import BuildCommand
        cmd1 = HelpCommand(mock_storage, "admin_token")
        cmd2 = BuildCommand(mock_storage, "admin_token")

        registry.register(cmd1)
        registry.register(cmd2)

        all_commands = registry.get_all_commands()

        assert len(all_commands) == 2
        assert cmd1 in all_commands
        assert cmd2 in all_commands

    def test_match_command_semantic(self, mock_storage):
        """Test semantic command matching."""
        registry = CommandRegistry(model_name="cointegrated/rubert-tiny", threshold=0.5)
        command = HelpCommand(mock_storage, "admin_token")
        registry.register(command)

        # Test various ways to say "help"
        match1 = registry.match_command("помощь")
        match2 = registry.match_command("справка")
        match3 = registry.match_command("помоги")

        assert match1 is not None
        assert match1[0] == command

        assert match2 is not None
        assert match2[0] == command

        assert match3 is not None
        assert match3[0] == command

    def test_match_command_no_match(self, mock_storage):
        """Test semantic matching with no match."""
        registry = CommandRegistry(model_name="cointegrated/rubert-tiny", threshold=0.5)
        command = HelpCommand(mock_storage, "admin_token")
        registry.register(command)

        # Test completely unrelated text
        match = registry.match_command("купить молоко в магазине")

        # Should not match or have very low similarity
        assert match is None or match[1] < 0.5


class TestCommandExecutor:
    """Test CommandExecutor."""

    @pytest.mark.asyncio
    async def test_execute_command_success(self, mock_storage, mock_update, mock_context):
        """Test successful command execution via executor."""
        from easybuild_bot.models import BotUser
        allowed_user = BotUser(
            id="12345",
            user_id=12345,
            user_name="testuser",
            display_name="Test User",
            allowed=True
        )
        mock_storage.get_user_by_user_id.return_value = allowed_user

        registry = CommandRegistry(model_name="cointegrated/rubert-tiny", threshold=0.5)
        executor = CommandExecutor(registry)

        command = HelpCommand(mock_storage, "admin_token")
        ctx = CommandContext(update=mock_update, context=mock_context, params={})

        result = await executor.execute_command(command, ctx)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_command_no_access(self, mock_storage, mock_update, mock_context):
        """Test command execution without access."""
        from easybuild_bot.models import BotUser
        non_allowed_user = BotUser(
            id="12345",
            user_id=12345,
            user_name="testuser",
            display_name="Test User",
            allowed=False
        )
        mock_storage.get_user_by_user_id.return_value = non_allowed_user

        registry = CommandRegistry(model_name="cointegrated/rubert-tiny", threshold=0.5)
        executor = CommandExecutor(registry)

        command = HelpCommand(mock_storage, "admin_token")
        ctx = CommandContext(update=mock_update, context=mock_context, params={})

        result = await executor.execute_command(command, ctx)

        assert result.success is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_match_and_execute(self, mock_storage, mock_update, mock_context):
        """Test match and execute flow."""
        from easybuild_bot.models import BotUser
        allowed_user = BotUser(
            id="12345",
            user_id=12345,
            user_name="testuser",
            display_name="Test User",
            allowed=True
        )
        mock_storage.get_user_by_user_id.return_value = allowed_user

        registry = CommandRegistry(model_name="cointegrated/rubert-tiny", threshold=0.5)
        executor = CommandExecutor(registry)

        command = HelpCommand(mock_storage, "admin_token")
        registry.register(command)

        ctx = CommandContext(update=mock_update, context=mock_context, params={})

        # Test semantic matching + execution
        result = await executor.match_and_execute("помощь", ctx)

        assert result is not None
        assert result.success is True
