# OxeignBot

OxeignBot is a modular Telegram moderation bot built with [Pyrogram](https://docs.pyrogram.org/). It provides several moderation utilities with a simple inline control panel and stores its configuration in a local SQLite database.

## Features

- Toggleable edit deletion, auto delete, link filter and bio link filter
- Admin commands: `/ban`, `/kick`, `/mute`, `/approve`
- Inline control panel available via `/start`, `/menu`, `/help`, or `/settings`
- Group metadata logging (title, owner ID, photo URL)
- SQLite persistence using `aiosqlite`
- Commands to manage features: `/editmode`, `/linkfilter`, `/setautodelete`

## Setup

The source code is organised into `handlers/` for bot commands and message
handlers, and `utils/` for helper utilities and database access.

### Environment variables

Create a `.env` file with the following keys (see `.env.example`):

```
API_ID=123456
API_HASH=your_api_hash
BOT_TOKEN=123456:ABCDEF
DB_PATH=oxeignbot.db
LOG_LEVEL=INFO
UPDATE_CHANNEL_ID=0
SUPPORT_CHAT_URL=https://t.me/botsyard
DEVELOPER_URL=https://t.me/oxeign
BANNER_URL=
```

1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file based on `.env.example` and fill in your API credentials.
3. Run the bot
   ```bash
   python main.py
   ```

### Commands

Toggle features with:
```
/editmode on|off
/linkfilter on|off
/setautodelete <seconds>
```
Moderation commands:
```
/approve, /unapprove, /viewapproved
/ban, /kick, /mute
```

## License

MIT
