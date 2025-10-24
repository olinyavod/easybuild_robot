# EasyBuild Bot

A Telegram bot for managing builds with semantic command recognition in Russian language.

## 🌟 Features

- 🤖 **Semantic Command Recognition** - Bot understands natural language
- 🔐 **Access Management** - User and group control
- 📦 **Build Management** - Select and download APK builds
- 🇷🇺 **Russian Language Support** - Uses ruBert-tiny model by Sberbank
- 🔄 **Cross-Platform** - Python backend + Dart/Flutter frontend

## 📁 Project Structure

```
easybuild_bot/
├── python/          # Telegram Bot Backend
│   ├── src/         # Source code
│   ├── scripts/     # Utility scripts
│   ├── main.py      # Bot entry point
│   └── requirements.txt
│
└── dart/            # Dart/Flutter Application
    ├── lib/         # Library code
    ├── bin/         # CLI application
    └── test/        # Unit tests
```

## 🚀 Quick Start

### Python Bot

1. **Install dependencies:**
   ```bash
   cd python
   pip install -r requirements.txt
   ```

2. **Create `.env` file with bot token:**
   ```env
   BOT_TOKEN=your_bot_token_here
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
- `bot.py` - Main bot logic
- `command_matcher.py` - Semantic command recognition using ruBert-tiny
- `storage.py` - Database operations (MontyDB)
- `models.py` - Data models

### Recognition Model

The bot uses the compact **cointegrated/rubert-tiny** model (~45 MB) for semantic matching of messages with commands.

Parameters:
- Similarity threshold: 0.5 (configurable)
- Method: Cosine similarity of embeddings

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

Test semantic command recognition:

```bash
cd python
python test_command_matcher.py
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

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue in the repository.

