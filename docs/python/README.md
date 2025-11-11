# EasyBuild Bot - Python Backend

Telegram bot for managing builds with semantic command recognition and voice transformation in Russian language.

## Features

- 🎙️ **Voice Command Recognition** - Send voice messages and bot will execute them as commands
- 🤖 **Semantic Command Recognition** - Bot understands natural language
- 🎯 **Dynamic Commands** - Extract parameters from natural language (NEW!)
- 🎤 **Voice Message Recognition** - Speech-to-text using OpenAI Whisper
- 🔊 **Text-to-Speech** - Natural Russian voice using Silero TTS (for /voice command)
- 🔐 **Access Management** - User and group control
- 📦 **Build Management** - Select and download APK builds
- 🇷🇺 **Russian Language Support** - Uses ruBert-tiny model by Sberbank

## 🎙️ Voice Documentation

- **[VOICE_COMMANDS.md](VOICE_COMMANDS.md)** - Voice command control guide (NEW! 🎤)
- **[VOICE_RECOGNITION.md](VOICE_RECOGNITION.md)** - Speech-to-text (STT) documentation
- **[TTS_GUIDE.md](TTS_GUIDE.md)** - Text-to-speech (TTS) full guide
- **[TTS_QUICKSTART.md](TTS_QUICKSTART.md)** - TTS quick start

## 🎯 Dynamic Commands Documentation

- **[DYNAMIC_COMMANDS.md](DYNAMIC_COMMANDS.md)** - Dynamic parameter extraction guide (NEW!)

## Installation

1. Create and activate virtual environment:
```bash
cd python
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with bot token:
```env
BOT_TOKEN=your_bot_token_here
WHISPER_MODEL=base     # STT: tiny, base, small, medium, large
TTS_SPEAKER=baya       # TTS: baya, kseniya, xenia, aidar, eugene
```

4. Configure Privacy Mode in BotFather:
   - Message @BotFather
   - Run `/mybots`
   - Select your bot
   - Bot Settings → Group Privacy → **Turn off**

## Running

**⚠️ ВАЖНО: Всегда активируйте виртуальное окружение перед запуском!**

```bash
cd python
source .venv/bin/activate  # Активировать окружение!
python main.py
```

## Testing

**⚠️ ВАЖНО: Активируйте виртуальное окружение перед тестированием!**

Test semantic command recognition:

```bash
cd python
source .venv/bin/activate  # Активировать окружение!
python test_command_matcher.py
```

Test dynamic command parameter extraction:

```bash
cd python
source .venv/bin/activate  # Активировать окружение!
python test_dynamic_commands.py
```

## Usage Examples

The bot understands natural phrases in Russian:

### Voice Messages 🎤 (NEW!)
- Send a voice message with any command in Russian
- The bot will transcribe it to text
- Show you what was recognized
- Execute the command automatically

**Example:**
```
🎤 You (voice): "Разблокировать пользователя Мирослава"
🤖 Bot: 🎤 Распознано: "Разблокировать пользователя Мирослава"
🤖 Bot: ✅ Пользователь Мирослав разблокирован!
```

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

### `/unblock_user` command (admin only, NEW! 🎯)
- "разблокировать пользователя Мирослава" (unblock user Miroslav - родительный падеж)
- "разблокировать пользователю Иван" (unblock user Ivan - дательный падеж) ⭐
- "предоставить доступ пользователю Анна" (grant access to Anna - дательный падеж) ⭐
- "разблокировать юзера Иван" (unblock user Ivan)
- "дать доступ юзеру Петр" (give access to Peter - дательный падеж) ⭐
- "разблокировать Анну" (unblock Anna - БЕЗ "пользователя"!)
- "дать доступ Петр" (give access Peter - БЕЗ "пользователя"!)
- "активировать Ольга" (activate Olga)

### `/block_user` command (admin only, NEW! 🎯)
- "заблокировать пользователя Сергей" (block user Sergey - родительный падеж)
- "заблокировать пользователю Дмитрий" (block user Dmitry - дательный падеж) ⭐
- "отключить пользователю Александр" (disable user Alexander - дательный падеж) ⭐
- "заблокировать юзера Дмитрий" (block user Dmitry)
- "отключить юзеру Елена" (disable user Elena - дательный падеж) ⭐
- "заблокировать Александра" (block Alexander - БЕЗ "пользователя"!)
- "отключить Елена" (disable Elena - БЕЗ "пользователя"!)
- "запретить доступ Владимир" (deny access Vladimir)

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
- `speech_recognition.py` - Voice message recognition using Whisper
- `storage.py` - Database operations (MontyDB)
- `models.py` - Data models

## Recognition Models

### Semantic Command Matching
The bot uses the compact **cointegrated/rubert-tiny** model (~45 MB) by a Russian developer for semantic matching of messages with commands.

Parameters:
- Similarity threshold: 0.5 (configurable)
- Method: Cosine similarity of embeddings

### Speech Recognition
The bot uses **OpenAI Whisper** for speech-to-text conversion.

Available models:
- `tiny` - Fastest, ~39M parameters (~75 MB)
- `base` - Balanced speed/quality, ~74M parameters (~140 MB) - **recommended**
- `small` - Good quality, ~244M parameters (~460 MB)
- `medium` - High quality, ~769M parameters (~1.5 GB)
- `large` - Best quality, ~1550M parameters (~2.9 GB)

Set model in `.env` file via `WHISPER_MODEL` variable.

## Requirements

- Python 3.8+
- 500+ MB free space (for models and dependencies)
- Internet connection for first model download
