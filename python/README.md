# EasyBuild Bot - Python Backend

Telegram bot for managing builds with semantic command recognition in Russian language.

## Features

- 🤖 **Semantic Command Recognition** - Bot understands natural language
- 🔐 **Access Management** - User and group control
- 📦 **Build Management** - Select and download APK builds
- 🇷🇺 **Russian Language Support** - Uses ruBert-tiny model by Sberbank

## Installation

1. Install dependencies:
```bash
cd python
pip install -r requirements.txt
```

2. Create `.env` file with bot token:
```env
BOT_TOKEN=your_bot_token_here
```

3. Configure Privacy Mode in BotFather:
   - Message @BotFather
   - Run `/mybots`
   - Select your bot
   - Bot Settings → Group Privacy → **Turn off**

## Running

```bash
cd python
python main.py
```

## Testing

Test semantic command recognition:

```bash
cd python
python test_command_matcher.py
```

## Usage Examples

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

## Using in Groups

In groups, the bot responds only when:
- You mention it via `@bot_username`
- You reply to its message

Example:
```
@easy_build_robot покажи сборки
```

The bot will automatically recognize that you want to execute the `/build` command and show the list of available builds.

## Architecture

- `bot.py` - Main bot logic
- `command_matcher.py` - Semantic command recognition using ruBert-tiny
- `storage.py` - Database operations (MontyDB)
- `models.py` - Data models

## Recognition Model

The bot uses the compact **cointegrated/rubert-tiny** model (~45 MB) by a Russian developer for semantic matching of messages with commands.

Parameters:
- Similarity threshold: 0.5 (configurable)
- Method: Cosine similarity of embeddings

## Requirements

- Python 3.8+
- 200+ MB free space (for model and dependencies)
- Internet connection for first model download
