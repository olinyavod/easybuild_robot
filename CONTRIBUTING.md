# Contributing to EasyBuild Bot

Thank you for your interest in contributing to EasyBuild Bot! This document provides guidelines and instructions for contributing to the project.

## Code Style Guidelines

### Language Requirements

**IMPORTANT:** All code documentation, comments, docstrings, and technical documentation must be written in **English**.

- ✅ **Comments:** Write all code comments in English
- ✅ **Docstrings:** Write all function/class documentation in English
- ✅ **Documentation Files:** Write all `.md` documentation files in English
- ✅ **Commit Messages:** Write commit messages in English
- ✅ **Variable/Function Names:** Use English for naming
- ⚠️ **User-Facing Messages:** Bot messages to users should remain in **Russian** (as the bot is designed for Russian-speaking users)
- ⚠️ **Semantic Tags:** Semantic tags in commands should remain in **Russian** (for natural language recognition)

### Examples

#### Good ✅

```python
class StartCommand(Command):
    """Start command - greet user and initialize bot interaction."""
    
    def get_command_name(self) -> str:
        return "/start"
    
    def get_semantic_tags(self) -> List[str]:
        # Semantic tags remain in Russian for natural language recognition
        return [
            "начать",
            "привет",
            "старт"
        ]
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Execute start command."""
        user = ctx.update.effective_user
        if not user:
            return CommandResult(
                success=False,
                error="Не удалось определить пользователя"  # User message in Russian
            )
        
        # User-facing message in Russian
        message = f"Привет, {user.full_name}!"
        await ctx.update.effective_message.reply_text(message)
        
        return CommandResult(success=True, message=message)
```

#### Bad ❌

```python
class StartCommand(Command):
    """Команда старт - приветствие пользователя."""  # Docstring in Russian - BAD
    
    def get_command_name(self) -> str:
        return "/start"
    
    def get_semantic_tags(self) -> List[str]:
        # Семантические теги
        return [
            "start",  # Semantic tags in English - BAD (should be Russian)
            "hello",
            "begin"
        ]
    
    async def execute(self, ctx: CommandContext) -> CommandResult:
        """Выполнить команду старт."""  # Docstring in Russian - BAD
        user = ctx.update.effective_user
        if not user:
            return CommandResult(
                success=False,
                error="Failed to identify user"  # User message in English - BAD (should be Russian)
            )
        
        # Пользовательское сообщение
        message = f"Hello, {user.full_name}!"  # User message in English - BAD (should be Russian)
        await ctx.update.effective_message.reply_text(message)
        
        return CommandResult(success=True, message=message)
```

### Summary

**What should be in English:**
- Code comments (`# This is a comment`)
- Docstrings (`"""This is a docstring"""`)
- Documentation files (`.md` files)
- Variable and function names
- Commit messages

**What should be in Russian:**
- User-facing messages (error messages, success messages, etc.)
- Semantic tags for command recognition
- Bot responses to users

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Maximum line length: 120 characters
- Use 4 spaces for indentation

### Documentation Structure

```
docs/
├── README.md                   # Documentation index
├── QUICKSTART.md              # Quick start guide
├── guides/                    # User guides
├── architecture/              # Architecture documentation
└── api/                       # API documentation
```

All documentation files should be:
- Written in English
- Use clear, concise language
- Include code examples where appropriate
- Follow markdown best practices

## How to Contribute

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/easybuild_bot.git
cd easybuild_bot
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Write code following the style guidelines above
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
cd python
pytest tests/ -v
```

### 5. Commit Changes

Write clear commit messages in English:

```bash
git commit -m "Add feature: semantic command recognition"
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Review Process

All contributions will be reviewed for:
- Code quality and style compliance
- Test coverage
- Documentation completeness
- Adherence to language guidelines (English for code/docs)

## Questions?

If you have questions about contributing, please open an issue on GitHub.

## License

By contributing to EasyBuild Bot, you agree that your contributions will be licensed under the MIT License.

