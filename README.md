# EasyBuild Bot

A Telegram bot for managing builds with semantic command recognition in Russian language.

## 🌟 Features

- 🤖 **Semantic Command Recognition** - Bot understands natural language
- 🎯 **Command Pattern Architecture** - Clean, scalable, maintainable code
- 🔐 **Access Management** - User and group control
- 📦 **Build Management** - Select and download APK builds
- 🏗️ **Project Management** - Manage Flutter, .NET MAUI, and Xamarin projects
  - ✨ **New: Interactive Project Wizard** - Step-by-step project creation
  - ✨ **New: Interactive Edit Menu** - Easy field-by-field project editing
- 🇷🇺 **Russian Language Support** - Uses ruBert-tiny model by Sberbank
- 🔄 **Cross-Platform** - Python backend + Dart/Flutter frontend

## ✨ New: Command Pattern Architecture

The bot now uses the **Command Pattern** for better code organization and scalability.

**Benefits:**
- ✅ Each command is a separate, self-contained class
- ✅ Easy to add new commands (1 file + 1 line registration)
- ✅ Built-in access control per command
- ✅ Semantic tags included with each command
- ✅ Highly testable and maintainable

**Documentation:**
- 📖 [Quick Start Guide](docs/QUICKSTART.md) - Get started in 5 minutes
- 📖 [Detailed Guide](docs/guides/COMMAND_PATTERN_GUIDE.md) - Complete tutorial
- 📊 [Architecture Diagrams](docs/architecture/ARCHITECTURE.md) - Visual overview
- 📊 [Comparison](docs/architecture/COMPARISON.md) - Before/After comparison
- 📚 [Full Documentation Index](docs/README.md) - All documentation

## 📁 Project Structure

```
easybuild_bot/
├── python/          # Telegram Bot Backend
│   ├── src/         # Source code
│   ├── scripts/     # Utility scripts
│   ├── main.py      # Bot entry point
│   └── requirements.txt
│
├── dart/            # Dart/Flutter Application
│   ├── lib/         # Library code
│   ├── bin/         # CLI application
│   └── test/        # Unit tests
│
└── docs/            # 📚 Project Documentation
    ├── README.md                   # Documentation index
    ├── QUICKSTART.md               # Quick start guide
    ├── DOCUMENTATION_STRUCTURE.md  # How to organize docs
    ├── guides/                     # User guides
    ├── architecture/               # Architecture docs
    ├── migration/                  # Migration history
    └── api/                        # API documentation
```

## 🚀 Quick Start

### Python Bot (New Command Pattern Architecture)

1. **Install dependencies:**
   ```bash
   cd python
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export BOT_TOKEN="your_bot_token_here"
   export ADMIN_TOKEN="your_admin_token"
   export DB_PATH="./data"
   ```

3. **Configure Privacy Mode in BotFather:**
   - Message @BotFather
   - Run `/mybots`
   - Select your bot
   - Bot Settings → Group Privacy → **Turn off**

4. **Run the bot:**
   ```bash
   python main.py
   ```

📖 See [docs/QUICKSTART.md](docs/QUICKSTART.md) for detailed instructions.

### Dart Application

1. **Install dependencies:**
   ```bash
   cd dart
   dart pub get
   ```

2. **Run the application:**
   ```bash
   dart run
   ```

## 💬 Usage Examples

The bot understands natural phrases in Russian:

### `/start` command
- "привет" (hello)
- "начать работу" (start working)
- "старт" (start)

### `/help` command
- "помощь" (help)
- "помоги мне" (help me)
- "что ты умеешь" (what can you do)

### `/build` command
- "покажи сборки" (show builds)
- "сборка" (build)
- "собрать apk" (build apk)

### `/register_group` command
- "зарегистрировать группу" (register group)
- "добавить группу" (add group)

### `/users` command (admin only)
- "пользователи" (users)
- "список пользователей" (user list)

### `/groups` command (admin only)
- "группы" (groups)
- "показать группы" (show groups)

### `/projects` command
- "проекты" (projects)
- "список проектов" (project list)
- "показать проекты" (show projects)

### `/add_project` command (admin only)
- "добавить проект" (add project)
- "создать проект" (create project)

### `/edit_project` command (admin only)
- "редактировать проект" (edit project)
- "изменить проект" (modify project)

### `/delete_project` command (admin only)
- "удалить проект" (delete project)
- "стереть проект" (erase project)

## 👥 Using in Groups

In groups, the bot responds only when:
- You mention it via `@bot_username`
- You reply to its message

Example:
```
@easy_build_robot покажи сборки
```

The bot will automatically recognize that you want to execute the `/build` command and show available builds.

## 🏗 Architecture

### Python Backend

**New Architecture (Command Pattern):**
```
commands/
├── base.py              # Abstract Command class
├── registry.py          # Command registry with semantic matching
├── executor.py          # Command executor with access control
├── factory.py           # Command system factory
└── implementations/     # Concrete command implementations
    ├── start_command.py
    ├── help_command.py
    ├── build_command.py
    └── ... (8 commands total)

bot_v2.py               # New bot implementation
```

**Core Components:**
- `bot.py` - Main bot logic with Command Pattern
- `commands/` - Command Pattern implementation
  - `registry.py` - Semantic command matching
  - `executor.py` - Command execution with access control
  - `implementations/` - All command implementations
- `storage.py` - Database operations (MontyDB)
- `models.py` - Data models
- `di.py` - Dependency Injection container
- `main.py` - Entry point with DI Container

### Recognition Model

The bot uses the compact **cointegrated/rubert-tiny** model (~45 MB) for semantic matching.

Parameters:
- Similarity threshold: 0.5 (configurable)
- Method: Cosine similarity of embeddings

📊 See [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) for detailed architecture diagrams.

## 📋 Requirements

### Python
- Python 3.8+
- 200+ MB free space (for model and dependencies)
- Internet connection for first model download

### Dart
- Dart SDK 2.12+
- Flutter SDK (for mobile apps)

## 🗄 Database

The project uses:
- **MontyDB** (MongoDB-like) for Python backend
- **Hive** for Dart/Flutter local storage

Database files are automatically excluded from git via `.gitignore`.

## 🧪 Testing

**Test Command Pattern:**
```bash
cd python
pytest tests/test_command_pattern.py -v
```

**Test Dynamic Commands:**
```bash
cd python
python tests/test_dynamic_commands.py
```

## 🔧 Deployment

### As a systemd service (Linux)

1. Configure the service:
   ```bash
   cd python
   ./install.sh
   ```

2. Manage the service:
   ```bash
   sudo systemctl start easybuild_bot_py
   sudo systemctl enable easybuild_bot_py
   sudo systemctl status easybuild_bot_py
   ```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a Pull Request.

**Code Style:**
- All comments and documentation must be in **English**
- User-facing messages and semantic tags remain in **Russian**
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code

## 📧 Support

For issues and questions, please open an issue in the repository.

